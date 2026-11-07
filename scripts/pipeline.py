"""End-to-end pipeline. Stages write JSONL to --out so a timed-out Kaggle session can resume.

  gen    : base episodes over the (topology x colluders x seed) grid
  coverup: LLM-organic cover-ups (naive / adaptive / adaptive+witness-corruption)
  tamper : scripted tamper bundles + negatives (untampered honest, benign rewrite)
  audit  : B0/B1/B3 (LLM) and B2 (deterministic) on all bundles

Local test:  python scripts/pipeline.py --backend mock --out /tmp/wn_test --seeds 2 --neg-seeds 3
Kaggle:      python scripts/pipeline.py --backend vllm --model Qwen/Qwen2.5-7B-Instruct-AWQ --out /kaggle/working
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from wn.blueteam import llm_auditors as L  # noqa: E402
from wn.blueteam.b2_matcher import audit as b2_audit  # noqa: E402
from wn.env.episode import make_config, run_episodes  # noqa: E402
from wn.redteam import tamper_ops  # noqa: E402
from wn.redteam.coverup import run_coverup  # noqa: E402
from wn.schemas import Episode  # noqa: E402

TOPOLOGIES = ["complete", "ring", "hub", "regular3"]


def jl_write(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def jl_read(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def make_backend(a):
    if a.backend == "mock":
        from wn.llm.backends import MockBackend
        return MockBackend()
    if a.backend == "vllm":
        from wn.llm.backends import VLLMBackend
        kw = dict(dtype="half", max_model_len=a.max_len, gpu_memory_utilization=0.90, tensor_parallel_size=a.tp)
        if "AWQ" in a.model or "awq" in a.model:
            kw["quantization"] = "awq"
        return VLLMBackend(a.model, **kw)
    from wn.llm.backends import OpenAICompatBackend
    return OpenAICompatBackend(a.model, base_url=a.base_url)


def stage_gen(a, be):
    path = os.path.join(a.out, "episodes.jsonl")
    if a.episodes_from and not os.path.exists(path):
        import shutil
        shutil.copy(a.episodes_from, path)
        log(f"gen: seeded from {a.episodes_from}")
    eps = [Episode.from_dict(d) for d in jl_read(path)] if os.path.exists(path) else []
    have = {e.config.episode_id for e in eps}
    cfgs = []
    if not eps:
        for t in a.topologies:
            for k in a.ks:
                for s in range(a.neg_seeds if k == 0 else a.seeds):
                    cfgs.append(make_config(f"{t}-k{k}-s{s}", a.n, t, k, seed=1000 * k + s, placement=a.placement,
                                            model=a.model, rounds=a.rounds))
    for t in a.topologies:  # extra honest episodes (more negatives -> finer FPR resolution)
        for s in range(a.neg_seeds, a.neg_seeds + a.extra_neg):
            eid = f"{t}-k0-s{s}"
            if eid not in have:
                cfgs.append(make_config(eid, a.n, t, 0, seed=s, placement=a.placement, model=a.model,
                                        rounds=a.rounds))
    if not cfgs:
        log(f"gen: cached ({len(eps)})")
        return eps
    log(f"gen: {len(cfgs)} new episodes (+{len(eps)} cached)")
    for i in range(0, len(cfgs), a.chunk):
        eps += run_episodes(cfgs[i:i + a.chunk], be)
        jl_write(path + ".partial", [e.to_dict() for e in eps])
        log(f"gen: {len(eps)} total")
    jl_write(path, [e.to_dict() for e in eps])
    return eps


def stage_coverup(a, be, eps):
    path = os.path.join(a.out, "coverups.jsonl")
    if os.path.exists(path):
        log("coverup: cached")
        return jl_read(path)
    pos = [e for e in eps if e.config.colluders]
    out = []
    for cond, aw, corr in [("organic-naive", "naive", False), ("organic-adaptive", "adaptive", False),
                           ("organic-corrupt", "adaptive", True)]:
        bs = run_coverup(pos, be, awareness=aw, corruption=corr)
        for b in bs:
            b["condition"] = cond
        out += bs
        log(f"coverup: {cond} done ({len(bs)})")
    jl_write(path, out)
    return out


def stage_tamper(a, eps):
    out = []
    for e in eps:
        if e.config.colluders:
            b = tamper_ops.untampered(e)  # control: attack happened, logs untouched (review C1)
            b["condition"] = "ctrl-attack-untampered"
            out.append(b)
            for op in tamper_ops.OPS:
                b = tamper_ops.apply(e, op, seed=e.config.seed)
                b["condition"] = f"scripted-{op}"
                out.append(b)
        else:
            b = tamper_ops.untampered(e)
            b["condition"] = "neg-untampered"
            out.append(b)
            b = tamper_ops.benign_rewrite(e, seed=e.config.seed)
            b["condition"] = "neg-benign"
            out.append(b)
    return out


def stage_audit(a, be, eps, bundles):
    path = os.path.join(a.out, "audits.jsonl")
    by_id = {e.config.episode_id: e for e in eps}
    metas = [{"n": by_id[b["episode_id"]].config.n_agents, "integ": by_id[b["episode_id"]].config.integrator}
             for b in bundles]
    edges = [by_id[b["episode_id"]].edges for b in bundles]
    rows = [{"episode_id": b["episode_id"], "condition": b["condition"], "n_record": len(b["record"])} for b in bundles]
    for r, b in zip(rows, bundles):
        for ts in (True, False):
            res = b2_audit(b["raw"], toolsvc=ts)
            r[f"B2{'' if ts else '-notool'}"] = {"score": res["score"], "agent_scores": res["agent_scores"]}
    # LLM auditors read journals (narr), which every scripted op scrubs identically -> audit one representative
    # scripted op ("scripted-PARA", reported as the journal-scrub condition); B2 still runs on every op.
    llm_idx = [i for i, b in enumerate(bundles)
               if not b["condition"].startswith("scripted-") or b["condition"] == "scripted-PARA"]
    sub_b = [bundles[i] for i in llm_idx]
    sub_m = [metas[i] for i in llm_idx]
    sub_e = [edges[i] for i in llm_idx]
    sub_r = [rows[i] for i in llm_idx]
    bundles, metas, edges = sub_b, sub_m, sub_e
    cache: dict = {}
    for i in range(0, len(bundles), a.audit_chunk):
        sl = slice(i, i + a.audit_chunk)
        for name, fn in [("B3", lambda: L.b3_witness(bundles[sl], metas[sl], edges[sl], be, "narr", True, cache)),
                         ("B3-notool", lambda: L.b3_witness(bundles[sl], metas[sl], edges[sl], be, "narr", False, cache)),
                         ("B1", lambda: L.b1_concat(bundles[sl], metas[sl], be, "narr", True)),
                         ("B0", lambda: L.b0_single(bundles[sl], metas[sl], be, "narr"))]:
            if name not in a.auditors:
                continue
            for r, res in zip(sub_r[sl], fn()):
                r[name] = res
        jl_write(path + ".partial", rows)
        log(f"audit: {min(i + a.audit_chunk, len(bundles))}/{len(bundles)}")
    jl_write(path, rows)
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default="mock", choices=["mock", "vllm", "openai"])
    p.add_argument("--model", default="mock")
    p.add_argument("--base-url", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--rounds", type=int, default=6)
    p.add_argument("--topologies", nargs="+", default=TOPOLOGIES)
    p.add_argument("--ks", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    p.add_argument("--seeds", type=int, default=6)
    p.add_argument("--neg-seeds", type=int, default=10)
    p.add_argument("--placement", default="random")
    p.add_argument("--episodes-from", default="")
    p.add_argument("--extra-neg", type=int, default=0)
    p.add_argument("--chunk", type=int, default=40)
    p.add_argument("--audit-chunk", type=int, default=200)
    p.add_argument("--auditors", nargs="+", default=["B0", "B1", "B3", "B3-notool"])
    p.add_argument("--stages", nargs="+", default=["gen", "coverup", "tamper", "audit"])
    p.add_argument("--max-len", type=int, default=8192)
    p.add_argument("--tp", type=int, default=1)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    be = make_backend(a)
    log(f"backend ready ({a.backend}:{a.model}) in {time.time() - t0:.0f}s")
    eps = stage_gen(a, be)
    s = {"episodes": len(eps), "side_task_success": sum(e.side_task_success for e in eps if e.config.colluders),
         "pos_episodes": sum(1 for e in eps if e.config.colluders),
         "parse_fail_rate": sum(e.parse_failures for e in eps) / max(1, sum(e.llm_calls for e in eps))}
    log(f"gen summary: {s}")
    bundles = []
    if "coverup" in a.stages:
        bundles += stage_coverup(a, be, eps)
    if "tamper" in a.stages:
        bundles += stage_tamper(a, eps)
    if "audit" in a.stages and bundles:
        stage_audit(a, be, eps, bundles)
    s.update(llm_calls=be.calls, minutes=round((time.time() - t0) / 60, 1))
    json.dump(s, open(os.path.join(a.out, "summary.json"), "w"), indent=2)
    log(f"done: {s}")


if __name__ == "__main__":
    main()
