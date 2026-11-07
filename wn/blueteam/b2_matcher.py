"""B2: deterministic cross-log matcher for verbatim raw logs.

For every event id claimed anywhere, every party the entry names (src, dst, toolsvc for tools) should hold an
identical copy. A missing or differing copy is an inconsistency edge between the two log owners.
Attribution: greedy weighted vertex cover over inconsistency edges (each contradiction contains >=1 liar);
toolsvc is trusted, so an edge to toolsvc implicates the other party directly.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

from ..schemas import TOOLSVC


def _key(e: dict) -> str:
    if e["kind"] == "msg":
        return json.dumps([e["src"], sorted(e["dst"]), e["body"]])
    return json.dumps([e["src"], e["tool"], sorted(e["args"].items())])


def _parties(e: dict, toolsvc: bool) -> set[str]:
    p = {str(e["src"])}
    if e["kind"] == "msg":
        p |= {str(d) for d in e["dst"]}
    elif toolsvc:
        p.add(TOOLSVC)
    return p


def audit(raw: dict[str, list[dict]], toolsvc: bool = True) -> dict:
    logs = {o: l for o, l in raw.items() if toolsvc or o != TOOLSVC}
    copies: dict[str, dict[str, str]] = defaultdict(dict)  # eid -> owner -> key
    meta: dict[str, dict] = {}
    for owner, log in logs.items():
        for e in log:
            copies[e["eid"]][owner] = _key(e)
            meta.setdefault(e["eid"], e)
    edges: Counter = Counter()
    incidents = []
    for eid, have in copies.items():
        parties = set().union(*(_parties(json.loads(json.dumps(meta[eid])), toolsvc) for _ in [0]))
        # union of parties named by any copy (a forged copy may name different parties)
        for owner in have:
            e_owner = next(x for x in logs[owner] if x["eid"] == eid)
            parties |= _parties(e_owner, toolsvc)
        parties &= set(logs)
        for a in parties:
            for b in parties:
                if a >= b:
                    continue
                ka, kb = have.get(a), have.get(b)
                if ka != kb:
                    edges[(a, b)] += 1
                    incidents.append({"eid": eid, "a": a, "b": b,
                                      "type": "missing" if (ka is None or kb is None) else "mismatch"})
    suspicion = _vertex_cover_scores(edges, trusted={TOOLSVC})
    return {"score": float(len(incidents)), "incidents": incidents, "agent_scores": suspicion,
            "edges": {f"{a}|{b}": c for (a, b), c in edges.items()}}


def _vertex_cover_scores(edges: Counter, trusted: set[str]) -> dict[str, float]:
    """Greedy weighted vertex cover; returns per-agent blame (weight of edges covered by that agent)."""
    remaining = Counter(edges)
    blame: dict[str, float] = defaultdict(float)
    for (a, b), w in list(remaining.items()):  # edges touching a trusted node implicate the other side
        if a in trusted or b in trusted:
            blame[b if a in trusted else a] += w
            del remaining[(a, b)]
    while remaining:
        deg: Counter = Counter()
        for (a, b), w in remaining.items():
            deg[a] += w
            deg[b] += w
        v, w = deg.most_common(1)[0]
        blame[v] += w
        remaining = Counter({e: c for e, c in remaining.items() if v not in e})
    return dict(blame)
