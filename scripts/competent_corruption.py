"""Offline ablation: replay the REAL honest comply/refuse decisions from the organic-corrupt condition, but let each
complying witness make its copies byte-identical to the colluders' (competent execution of the corruption).
'requested'  : only the records the colluder asked about.
'all-held'   : every colluder-changed record the complier holds (upper bound on what corruption can buy).
Usage: python scripts/competent_corruption.py <pipeline out dir>
"""
import collections, copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from wn.schemas import Episode  # noqa: E402
from wn.blueteam.b2_matcher import audit  # noqa: E402


def competent(b, ep, all_held=False):
    b = copy.deepcopy(b)
    coll = {str(c) for c in ep.config.colluders}
    changed = {r["eid"] for r in b["record"] if r.get("eid") and r["owner"] in coll}
    compliers = {}
    for r in b["requests"]:
        if r.get("comply"):
            compliers.setdefault(str(r["to"]), set()).update(r["eids"])
    for h, eids in compliers.items():
        hl = b["raw"][h]
        targets = changed if all_held else eids
        for eid in targets:
            cv = next((e for c in coll for e in b["raw"][c] if e["eid"] == eid), None)
            mine = [e for e in hl if e["eid"] == eid]
            if not mine and not (all_held and cv is not None and h in [str(d) for d in cv.get("dst", [])]):
                continue
            for m in mine:
                hl.remove(m)
            if cv is not None:
                ne = dict(cv)
                ne["dir"] = mine[0]["dir"] if mine else "recv"
                hl.append(ne)
        hl.sort(key=lambda e: (e["round"], e["eid"]))
    return b


def main(d):
    eps = {}
    for l in open(os.path.join(d, "episodes.jsonl")):
        e = Episode.from_dict(json.loads(l))
        eps[e.config.episode_id] = e
    cov = [json.loads(l) for l in open(os.path.join(d, "coverups.jsonl"))]
    res = collections.defaultdict(list)
    for b in cov:
        if b["condition"] != "organic-corrupt" or not b["record"]:
            continue
        ep = eps[b["episode_id"]]
        has = any(r.get("comply") for r in b["requests"])
        for mode, bb in [("as-run", b), ("competent-requested", competent(b, ep)),
                         ("competent-all-held", competent(b, ep, True))]:
            for ts in (True, False):
                res[f"{mode}|{'tool' if ts else 'notool'}"].append(audit(bb["raw"], toolsvc=ts)["score"] > 0)
                if has:
                    res[f"{mode}|{'tool' if ts else 'notool'}|with-compliers"].append(
                        audit(bb["raw"], toolsvc=ts)["score"] > 0)
    out = {k: {"detected": sum(v), "n": len(v), "rate": round(sum(v) / len(v), 3)} for k, v in sorted(res.items())}
    json.dump(out, open(os.path.join(d, "competent_corruption.json"), "w"), indent=2)
    for k, v in out.items():
        print(f"{k:45s} {v['detected']}/{v['n']} = {v['rate']}")


if __name__ == "__main__":
    main(sys.argv[1])
