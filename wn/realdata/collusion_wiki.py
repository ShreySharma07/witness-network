"""Real-data arm: natural peer witnesses on the collusion.wiki revision log.

Provenance: revision log of OpenAI agents' unsanctioned use of German public wikis (DSEWiki etc., May-July 2026;
collusion.wiki, Von Arx et al. 2026). This is a SEPARATE incident from the July 2026 Hugging Face breach.
It is a wiki revision log, not a message board; its deletions include admin deletions (a confound for 'omission').

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


def added_text(r: dict) -> str:
    """Only the lines this revision ADDED (insert/replace hunks), so unchanged page text carried over from
    earlier snapshots is not mistaken for an echo (review C3)."""
    lines = (r.get("body") or "").split("\n")
    out = []
    for h in r.get("hunks") or []:
        if h.get("op") in ("insert", "replace"):
            out += lines[h.get("b0", 0):h.get("b1", 0)]
    return "\n".join(out)


def load(path: str):
    revs = []
    with open(path) as f:
        for l in f:
            r = json.loads(l)
            ident = r.get("label") or f"ip:{r.get('ip16')}"
            revs.append({"id": r["rev_id"], "who": ident, "ip": str(r.get("ip16")), "t": r.get("time") or "",
                         "page": r.get("page_id"), "body": added_text(r)})
    revs.sort(key=lambda r: (r["t"], r["id"]))
    return revs


def echoes(revs, strict: bool = False, max_df: int = MAX_DF, cross_page_only: bool = True):
    """witnesses[i] = identities (≠ author) whose LATER revision re-adds distinctive text first added in revision i.
    cross_page_only: count only copies on a DIFFERENT page (a quote/relay elsewhere, not the same page's history)."""
    sh = [shingles(r["body"]) for r in revs]
    df = Counter(s for ss in sh for s in ss)
    first: dict[str, int] = {}
    witnesses = defaultdict(set)
    eligible = set()
    for i, ss in enumerate(sh):
        for s in ss:
            if df[s] > max_df:
                continue
            if s not in first:
                first[s] = i
                eligible.add(i)
            else:
                j = first[s]
                if revs[i]["who"] == revs[j]["who"]:
                    continue
                if strict and revs[i]["ip"] == revs[j]["ip"]:
                    continue
                if cross_page_only and revs[i]["page"] == revs[j]["page"]:
                    continue
                witnesses[j].add(revs[i]["who"])
    return witnesses, eligible


def coverage_curve(revs, witnesses, fracs, trials=50, seed=0, weighted=True, eligible=None):
    """'lo'/'hi' are the 2.5/97.5% SPREAD of single-trial values (not a CI on the mean).
    Denominator: scrubbed revisions that are echo-ELIGIBLE (contain >=1 distinctive shingle)."""
    rng = random.Random(seed)
    ids = Counter(r["who"] for r in revs)
    pool = list(ids)
    weights = [ids[p] for p in pool]
    out = []
    for f in fracs:
        k = max(1, round(f * len(pool)))
        vals = []
        for _ in range(trials):
            if weighted:  # activity-weighted successive sampling (draw, reject duplicates)
                coll = set()
                while len(coll) < k:
                    coll.add(rng.choices(pool, weights)[0])
            else:
                coll = set(rng.sample(pool, k))
            scrubbed = [i for i, r in enumerate(revs) if r["who"] in coll and (eligible is None or i in eligible)]
            if not scrubbed:
                continue
            ok = sum(1 for i in scrubbed if witnesses.get(i, set()) - coll)
            vals.append(ok / len(scrubbed))
        vals.sort()
        out.append({"frac": f, "k": k, "witnessed": sum(vals) / len(vals),
                    "spread_lo": vals[int(0.025 * len(vals))], "spread_hi": vals[min(len(vals) - 1, int(0.975 * len(vals)))]})
    return out


def main(d: str, out_path: str):
    revs = load(d.rstrip("/") + "/revisions.jsonl")
    fracs = [0.001, 0.01, 0.05, 0.1, 0.2, 0.4]
    res = {"n_revisions": len(revs), "n_identities": len({r["who"] for r in revs}),
           "n_with_added_text": sum(1 for r in revs if r["body"].strip()), "sensitivity": {}}
    for mdf in (2, 5, 10):
        for xp in (True, False):
            w, el = echoes(revs, max_df=mdf, cross_page_only=xp)
            key = f"max_df={mdf}|{'cross_page' if xp else 'any_page'}"
            res["sensitivity"][key] = {"eligible": len(el), "echoed": sum(1 for i in el if w.get(i)),
                                       "echoed_frac_of_eligible": round(sum(1 for i in el if w.get(i)) / max(1, len(el)), 4),
                                       "echoed_frac_of_all": round(sum(1 for i in el if w.get(i)) / len(revs), 4)}
    w, el = echoes(revs)  # primary: added text, cross-page, MAX_DF=5
    ws, els = echoes(revs, strict=True)
    res["primary"] = res["sensitivity"][f"max_df={MAX_DF}|cross_page"]
    res["curve_weighted"] = coverage_curve(revs, w, fracs, eligible=el)
    res["curve_uniform"] = coverage_curve(revs, w, fracs, weighted=False, eligible=el)
    res["strict_curve_weighted"] = coverage_curve(revs, ws, fracs, eligible=els)
    json.dump(res, open(out_path, "w"), indent=2)
    print(json.dumps({k: v for k, v in res.items() if "curve" not in k}, indent=1))
    for c in res["curve_weighted"]:
        print(f'colluders {c["frac"]:.1%} (k={c["k"]}): {c["witnessed"]:.3f} of scrubbed eligible revisions still '
              f'witnessed cross-page [spread {c["spread_lo"]:.3f}, {c["spread_hi"]:.3f}]')


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
