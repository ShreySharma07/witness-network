"""Replay the frontier colluders' ACTUAL raw-log edits onto witness-by-design logs (CC 1 peer + receipts).
Colluders edit only their own copies; CC'd honest peers keep the originals. Scored by B2, peers only."""
import copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from wn.blueteam.b2_matcher import audit
from wn.redteam.coverup import run_coverup  # noqa: F401 (for reproducibility of bundle format)
from wn.schemas import Episode
from wn.theory.coverage import bundle_detectable
from witness_by_design import with_cc

grid, fr = sys.argv[1], sys.argv[2]
eps = {json.loads(l)["config"]["episode_id"]: Episode.from_dict(json.loads(l)) for l in open(os.path.join(grid, "episodes.jsonl"))}
rows = json.load(open(os.path.join(fr, "colluders.json")))["rows"]
bundles = json.load(open(os.path.join(fr, "colluders_bundles.json")))
out = []
for b in bundles:
    ep = eps[b["episode_id"]]
    coll = {str(c) for c in ep.config.colluders}
    raw_touch = [r for r in b["record"] if r["op"] in ("delete", "edit", "insert") and r["owner"] in coll]
    if not raw_touch:
        continue
    res = {"episode_id": b["episode_id"], "base_B2_notool": audit(b["raw"], toolsvc=False)["score"] > 0}
    for w, rc in [(1, True), (2, True)]:
        e2 = with_cc(ep, w, seed=ep.config.seed, receipts=rc)
        raw = copy.deepcopy(e2.raw_logs)
        for owner in coll:
            new = {e["eid"]: e for e in b["raw"][owner]}
            cc_by_eid = {e["eid"]: e for e in raw[owner]}
            rebuilt = []
            for e in raw[owner]:
                if e["eid"] not in new:          # colluder deleted it
                    continue
                ne = dict(new[e["eid"]])
                if "dst" in e:                   # keep the CC'd party list; only content was forged
                    ne["dst"] = e["dst"]
                rebuilt.append(ne)
            rebuilt += [dict(x) for eid, x in new.items() if eid not in cc_by_eid]  # fabrications
            raw[owner] = sorted(rebuilt, key=lambda e: (e["round"], e["eid"]))
        res[f"CC{w}+receipts_B2_notool"] = audit(raw, toolsvc=False)["score"] > 0
    out.append(res)
summary = {k: f"{sum(r[k] for r in out)}/{len(out)}" for k in out[0] if k != "episode_id"} if out else {}
print(summary)
json.dump({"summary": summary, "rows": out}, open(os.path.join(fr, "colluders_witness_by_design.json"), "w"), indent=1)
