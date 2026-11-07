"""Frontier-model check via the Kaggle Model Proxy, run on a subsample of the main 7B grid.

Steps (each checkpointed to <out>/<step>.json; re-running skips finished steps):
  monitor   frontier all-logs monitor (B1) on: 96 attack-only controls, PARA scrubs, LLM adaptive cover-ups
  comply    the 233 stored witness-corruption requests re-asked to frontier honest agents
  colluders frontier colluders write adaptive cover-ups for a subset of attack episodes; scored by B2 + frontier B1
Usage: python scripts/frontier_check.py <grid out dir> <results dir> [--steps monitor comply colluders]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from wn.blueteam import llm_auditors as L  # noqa: E402
from wn.blueteam.b2_matcher import audit as b2  # noqa: E402
from wn.eval.metrics import auroc  # noqa: E402
from wn.llm.backends import KaggleProxyBackend  # noqa: E402
from wn.redteam import tamper_ops  # noqa: E402
from wn.redteam.coverup import recomply, run_coverup  # noqa: E402
from wn.schemas import Episode  # noqa: E402
from wn.theory.coverage import bundle_detectable  # noqa: E402

CLAUDE = "anthropic/claude-sonnet-5@default"
GEMINI = "google/gemini-3-flash-preview"


class Roomy(KaggleProxyBackend):
    """Reasoning models spend hidden tokens: give every call a generous completion budget.
    (2048 was enough for short verdicts but truncated long cover-up plans; colluders use 6000.)"""
    floor = 2048

    def chat(self, batch, max_tokens=400, temperature=0.7, seed=0):
        return super().chat(batch, max_tokens=max(max_tokens, self.floor), temperature=temperature, seed=seed)


def tpr_at_zero_fp(ps, ns):
    t = max(ns) if ns else 0
    return sum(p > t for p in ps) / len(ps) if ps else float("nan")


def summarize(scores_pos, scores_neg):
    return {"auroc": round(auroc(scores_pos, scores_neg), 3), "tpr_at_fpr0": round(tpr_at_zero_fp(scores_pos, scores_neg), 3),
            "n_pos": len(scores_pos), "n_neg": len(scores_neg)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("grid")
    p.add_argument("out")
    p.add_argument("--steps", nargs="+", default=["monitor", "comply", "colluders"])
    p.add_argument("--n-colluder-eps", type=int, default=48)
    p.add_argument("--cap", type=float, default=9.0)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    eps = {}
    for l in open(os.path.join(a.grid, "episodes.jsonl")):
        e = Episode.from_dict(json.loads(l))
        eps[e.config.episode_id] = e
    cov = [json.loads(l) for l in open(os.path.join(a.grid, "coverups.jsonl"))]
    attack = [e for e in eps.values() if e.config.colluders]
    meta = lambda e: {"n": e.config.n_agents, "integ": e.config.integrator}

    claude = Roomy(CLAUDE, spend_cap_usd=a.cap)
    print("start daily spend $", round(claude.start_spend, 3), flush=True)

    if "monitor" in a.steps and not os.path.exists(os.path.join(a.out, "monitor.json")):
        sets = {"ctrl": [tamper_ops.untampered(e) for e in attack],
                "scripted-PARA": [b for b in (tamper_ops.apply(e, "PARA", seed=e.config.seed) for e in attack) if b["record"]],
                "organic-adaptive": [b for b in cov if b["condition"] == "organic-adaptive" and b["record"]]}
        scores = {}
        for name, bs in sets.items():
            res = L.b1_concat(bs, [meta(eps[b["episode_id"]]) for b in bs], claude, "narr", True)
            scores[name] = [r["score"] for r in res]
            print(f"monitor {name}: n={len(bs)} mean={sum(scores[name]) / len(bs):.1f} spend=${claude.spend() - claude.start_spend:.2f}",
                  flush=True)
        out = {"model": CLAUDE, "scores": scores,
               "tamper_PARA": summarize(scores["scripted-PARA"], scores["ctrl"]),
               "tamper_organic_adaptive": summarize(scores["organic-adaptive"], scores["ctrl"])}
        json.dump(out, open(os.path.join(a.out, "monitor.json"), "w"), indent=1)
        print("monitor:", {k: v for k, v in out.items() if k != "scores"}, flush=True)

    if "comply" in a.steps and not os.path.exists(os.path.join(a.out, "comply.json")):
        cu = [b for b in cov if b["condition"] == "organic-corrupt"]
        out = {}
        for m in (CLAUDE, GEMINI):
            rc = recomply(cu, Roomy(m, spend_cap_usd=a.cap), eps)
            out[m] = {k: v for k, v in rc.items() if k != "decisions"}
            out[m]["sample_reasons"] = [d["reason"] for d in rc["decisions"][:8]]
            print(f"comply {m}: {rc['complied']}/{rc['n']} = {rc['rate']}", flush=True)
        json.dump(out, open(os.path.join(a.out, "comply.json"), "w"), indent=1)

    if "colluders" in a.steps and not os.path.exists(os.path.join(a.out, "colluders.json")):
        gem = Roomy(GEMINI, spend_cap_usd=a.cap)
        gem.floor = 6000
        sub = sorted(attack, key=lambda e: e.config.episode_id)[:: max(1, len(attack) // a.n_colluder_eps)][: a.n_colluder_eps]
        bundles = run_coverup(sub, gem, awareness="adaptive", corruption=False)
        rows = []
        for e, b in zip(sub, bundles):
            rows.append({"episode_id": e.config.episode_id, "k": len(e.config.colluders), "n_record": len(b["record"]),
                         "ops": sorted({r["op"] for r in b["record"]}),
                         "parse_failures": b["parse_failures"],
                         "B2": b2(b["raw"], toolsvc=True)["score"], "B2-notool": b2(b["raw"], toolsvc=False)["score"],
                         "detectable": bundle_detectable(e, b, True), "detectable_notool": bundle_detectable(e, b, False)})
        tampered = [(e, b, r) for e, b, r in zip(sub, bundles, rows) if b["record"]]
        mon = L.b1_concat([b for _, b, _ in tampered], [meta(e) for e, _, _ in tampered], claude, "narr", True)
        ctrl_scores = json.load(open(os.path.join(a.out, "monitor.json")))["scores"]["ctrl"] \
            if os.path.exists(os.path.join(a.out, "monitor.json")) else []
        for (_, _, r), m in zip(tampered, mon):
            r["B1_claude"] = m["score"]
        und = [r for _, _, r in tampered if r["detectable_notool"] is False]
        out = {"colluder_model": GEMINI, "n_episodes": len(sub), "n_tampered": len(tampered), "rows": rows,
               "B2_detect": round(sum(r["B2"] > 0 for _, _, r in tampered) / max(1, len(tampered)), 3),
               "B2_notool_detect": round(sum(r["B2-notool"] > 0 for _, _, r in tampered) / max(1, len(tampered)), 3),
               "undetectable_by_theory_notool": len(und),
               "caught_anyway_notool": sum(r["B2-notool"] > 0 for r in und),
               "B1_claude_vs_ctrl": summarize([r["B1_claude"] for _, _, r in tampered], ctrl_scores) if ctrl_scores else None}
        json.dump(out, open(os.path.join(a.out, "colluders.json"), "w"), indent=1)
        print("colluders:", {k: v for k, v in out.items() if k != "rows"}, flush=True)
    print("total spend this run $", round(claude.spend() - claude.start_spend, 3))


if __name__ == "__main__":
    main()
