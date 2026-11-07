"""Detection / attribution metrics with cluster bootstrap over base episodes."""
from __future__ import annotations

import random
from typing import Sequence


def auroc(pos: Sequence[float], neg: Sequence[float]) -> float:
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p > n else 0.5 if p == n else 0.0
    return wins / (len(pos) * len(neg))


def tpr_at_fpr(pos: Sequence[float], neg: Sequence[float], fpr: float = 0.05) -> float:
    """Threshold = smallest value with FPR <= target (strict '>' detection)."""
    if not pos or not neg:
        return float("nan")
    cands = sorted(set(neg) | {max(neg) + 1e-9})
    best = float("nan")
    for t in cands:
        f = sum(n > t for n in neg) / len(neg)
        if f <= fpr:
            best = sum(p > t for p in pos) / len(pos)
            break
    return best


def attribution_f1(agent_scores: dict, colluders: Sequence[int], k: int | None = None) -> dict:
    """Top-k attribution (k = true number of colluders unless given)."""
    truth = {str(c) for c in colluders}
    k = len(truth) if k is None else k
    if k == 0:
        return {"precision": float("nan"), "recall": float("nan"), "f1": float("nan")}
    ranked = sorted(agent_scores.items(), key=lambda kv: -kv[1])
    pred = {a for a, s in ranked[:k] if s > 0}
    tp = len(pred & truth)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(truth)
    return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def cluster_bootstrap(rows: list[dict], stat, cluster_key: str = "base_id", n: int = 2000, seed: int = 0):
    """rows: dicts; stat(rows)->float. Resample clusters with replacement. Returns (point, lo, hi)."""
    rng = random.Random(seed)
    clusters: dict = {}
    for r in rows:
        clusters.setdefault(r[cluster_key], []).append(r)
    keys = list(clusters)
    point = stat(rows)
    vals = []
    for _ in range(n):
        samp = [r for k in (rng.choice(keys) for _ in keys) for r in clusters[k]]
        v = stat(samp)
        if v == v:
            vals.append(v)
    if not vals:
        return point, float("nan"), float("nan")
    vals.sort()
    return point, vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]
