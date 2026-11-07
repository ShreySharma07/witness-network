"""Turn pipeline outputs into tables + figures.

Positives: bundles from colluder episodes (k>=1) under each tamper condition.
Negatives: honest episodes (k=0), untampered + benign rewrite (pooled across topologies).
Usage: python scripts/analyze.py --out <pipeline out dir>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from wn.eval.metrics import attribution_f1, auroc, cluster_bootstrap, tpr_at_fpr  # noqa: E402
from wn.schemas import Episode  # noqa: E402
from wn.theory.coverage import honest_coverage  # noqa: E402

AUDITORS = ["B0", "B1", "B2", "B2-notool", "B3", "B3-notool"]


def load(out):
    eps = {}
    for l in open(os.path.join(out, "episodes.jsonl")):
        e = Episode.from_dict(json.loads(l))
        eps[e.config.episode_id] = e
    rows = [json.loads(l) for l in open(os.path.join(out, "audits.jsonl"))]
    for r in rows:
        e = eps[r["episode_id"]]
        r["k"] = len(e.config.colluders)
        r["topology"] = e.config.topology
        r["base_id"] = r["episode_id"]
        r["colluders"] = e.config.colluders
        r["coverage"] = honest_coverage(e, toolsvc=True)
        r["coverage_notool"] = honest_coverage(e, toolsvc=False)
        r["side_success"] = e.side_task_success
    return eps, rows


def table(rows, fpr=0.05, group=("condition",), auditors=AUDITORS):
    neg = [r for r in rows if r["condition"].startswith("neg")]
    pos = [r for r in rows if not r["condition"].startswith("neg") and r["n_record"] > 0]
    groups = defaultdict(list)
    for r in pos:
        groups[tuple(r[g] for g in group)].append(r)
    out = []
    for key in sorted(groups):
        g = groups[key]
        line = {"group": dict(zip(group, key)), "n_pos": len(g), "n_neg": len(neg)}
        for a in auditors:
            gg = [r for r in g if a in r]
            if not gg:
                continue
            ps = [r[a]["score"] for r in gg]
            ns = [r[a]["score"] for r in neg]
            line[a] = {"auroc": round(auroc(ps, ns), 3), f"tpr@{fpr}": round(tpr_at_fpr(ps, ns, fpr), 3),
                       "attr_f1": round(sum(attribution_f1(r[a]["agent_scores"], r["colluders"])["f1"] for r in gg)
                                        / len(gg), 3), "n": len(gg)}
        out.append(line)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--fpr", type=float, default=0.05)
    a = p.parse_args()
    eps, rows = load(a.out)
    neg = [r for r in rows if r["condition"].startswith("neg")]
    res = {"by_condition": table(rows, a.fpr, ("condition",)),
           "by_condition_k": table(rows, a.fpr, ("condition", "k")),
           "by_condition_topology": table(rows, a.fpr, ("condition", "topology")),
           "honest_fpr_threshold_note": f"thresholds set at {a.fpr} FPR on {len(neg)} negatives"}
    # bootstrap CI on headline: B3 vs B1 AUROC over all scripted+organic positives
    def stat_for(aud):
        def f(rs):
            ps = [r[aud]["score"] for r in rs if not r["condition"].startswith("neg") and r["n_record"] > 0 and aud in r]
            ns = [r[aud]["score"] for r in rs if r["condition"].startswith("neg")]
            return auroc(ps, ns)
        return f
    res["auroc_ci"] = {aud: cluster_bootstrap(rows, stat_for(aud), n=500) for aud in AUDITORS
                       if any(aud in r for r in rows)}
    # witness corruption compliance
    cov_path = os.path.join(a.out, "coverups.jsonl")
    if os.path.exists(cov_path):
        reqs = [q for l in open(cov_path) for q in json.loads(l).get("requests", []) if "comply" in q]
        res["corruption"] = {"requests": len(reqs), "complied": sum(q["comply"] for q in reqs),
                             "rate": round(sum(q["comply"] for q in reqs) / max(1, len(reqs)), 3)}
    pos_eps = [e for e in eps.values() if e.config.colluders]
    res["side_task_success_rate"] = round(sum(e.side_task_success for e in pos_eps) / max(1, len(pos_eps)), 3)
    json.dump(res, open(os.path.join(a.out, "analysis.json"), "w"), indent=2)
    for line in res["by_condition"]:
        print(line["group"], {k: v for k, v in line.items() if k in AUDITORS})
    print("corruption:", res.get("corruption"), "| side-task success:", res["side_task_success_rate"])
    print("AUROC CI:", {k: tuple(round(x, 3) for x in v) for k, v in res["auroc_ci"].items()})


if __name__ == "__main__":
    main()
