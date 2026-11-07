"""Real-data arm: natural peer witnesses on the collusion.wiki revision log (OpenAI/Hugging Face incident board).

Witness definition: revision R by identity A is "echoed" if a LATER revision by a DIFFERENT identity B contains a
distinctive 8-word shingle first seen in R (rare shingles only, to exclude page templates). An echo is a copy
of A's content that A does not control: if A later deletes or rewrites R, B's copy still exposes it.

Coverage experiment: pick colluder sets of size k (random identities, weighted by activity or uniform). Colluders
scrub their own revisions AND echoes held by other colluders. A scrubbed revision stays detectable iff an honest
identity still holds an echo. Report witnessed fraction vs k/N, the real-data analogue of the synthetic bound.

Identity = self-asserted label (or ip16 bucket if unlabeled). Agents renamed themselves often, so this
OVER-counts identities; we report this as a limitation (renames make some 'witnesses' the same agent).
Usage: python -I wn/realdata/collusion_wiki.py <dir with revisions.jsonl> <out.json>
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict

SHINGLE = 8
MAX_DF = 5            # a shingle in more than this many revisions is a template, not an echo
MIN_ALPHA = 20        # shingle must contain this many letters (skip number tables)


def shingles(text: str) -> set[str]:
    w = re.findall(r"\S+", text.lower())
    out = set()
    for i in range(0, max(0, len(w) - SHINGLE + 1)):
        s = " ".join(w[i:i + SHINGLE])
        if sum(c.isalpha() for c in s) >= MIN_ALPHA:
            out.add(s)
    return out


def load(path: str):
    revs = []
    with open(path) as f:
        for l in f:
            r = json.loads(l)
            ident = r.get("label") or f"ip:{r.get('ip16')}"
            revs.append({"id": r["rev_id"], "who": ident, "ip": str(r.get("ip16")), "t": r.get("time") or "",
                         "body": r.get("body") or ""})
    revs.sort(key=lambda r: r["t"])
    return revs


def echoes(revs, strict: bool = False):
    """Return witnesses[rev_index] = set of identities (≠ author) holding a later copy of the revision's content."""
    sh = [shingles(r["body"]) for r in revs]
    df = Counter(s for ss in sh for s in ss)
    first: dict[str, int] = {}
    witnesses = defaultdict(set)
    for i, ss in enumerate(sh):
        for s in ss:
            if df[s] > MAX_DF:
                continue
            if s not in first:
                first[s] = i
            else:
                j = first[s]
                if revs[i]["who"] != revs[j]["who"] and (not strict or revs[i]["ip"] != revs[j]["ip"]):
                    witnesses[j].add(revs[i]["who"])
    return witnesses


def coverage_curve(revs, witnesses, fracs, trials=50, seed=0, weighted=True):
    rng = random.Random(seed)
    ids = Counter(r["who"] for r in revs)
    pool = list(ids)
    weights = [ids[p] for p in pool]
    out = []
    for f in fracs:
        k = max(1, round(f * len(pool)))
        vals = []
        for _ in range(trials):
            if weighted:  # activity-weighted sample without replacement (active agents are likelier conspirators)
                coll = set()
                while len(coll) < k:
                    coll.add(rng.choices(pool, weights)[0])
            else:
                coll = set(rng.sample(pool, k))
            scrubbed = [i for i, r in enumerate(revs) if r["who"] in coll]
            if not scrubbed:
                continue
            ok = sum(1 for i in scrubbed if witnesses.get(i, set()) - coll)
            vals.append(ok / len(scrubbed))
        vals.sort()
        out.append({"frac": f, "k": k, "witnessed": sum(vals) / len(vals),
                    "lo": vals[int(0.025 * len(vals))], "hi": vals[int(0.975 * len(vals)) - 1]})
    return out


def main(d: str, out_path: str):
    revs = load(d.rstrip("/") + "/revisions.jsonl")
    w = echoes(revs)
    n_w = sum(1 for i in range(len(revs)) if w.get(i))
    res = {"n_revisions": len(revs), "n_identities": len({r["who"] for r in revs}),
           "echoed_fraction": n_w / len(revs),
           "witness_count_hist": Counter(min(len(w.get(i, ())), 5) for i in range(len(revs))),
           "curve_weighted": coverage_curve(revs, w, [0.001, 0.01, 0.05, 0.1, 0.2, 0.4]),
           "curve_uniform": coverage_curve(revs, w, [0.001, 0.01, 0.05, 0.1, 0.2, 0.4], weighted=False)}
    res["witness_count_hist"] = {str(k): v for k, v in sorted(res["witness_count_hist"].items())}
    ws = echoes(revs, strict=True)  # lower bound: echo must also come from a different /16 network
    res["strict_echoed_fraction"] = sum(1 for i in range(len(revs)) if ws.get(i)) / len(revs)
    res["strict_curve_weighted"] = coverage_curve(revs, ws, [0.001, 0.01, 0.05, 0.1, 0.2, 0.4])
    json.dump(res, open(out_path, "w"), indent=2)
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("curve")}, indent=1))
    for c in res["strict_curve_weighted"]:
        print(f'[strict] colluders {c["frac"]:.1%}: {c["witnessed"]:.3f} still witnessed')
    for c in res["curve_weighted"]:
        print(f'colluders {c["frac"]:.1%} (k={c["k"]}): {c["witnessed"]:.3f} of scrubbed revisions still witnessed '
              f'[{c["lo"]:.3f}, {c["hi"]:.3f}]')


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
