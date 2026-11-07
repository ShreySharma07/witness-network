"""Witness-coverage theory.

An event e is undetectable by cross-witness checking iff every party in its witness set W(e) colludes.
Episode-level: tampering is detectable iff at least one tampered event has an honest witness.
"""
from __future__ import annotations

from math import comb

from ..schemas import TOOLSVC, Episode


def p_undetectable_pairwise(n: int, k: int) -> float:
    """Random placement, pairwise message: P(both endpoints colluders)."""
    return comb(k, 2) / comb(n, 2) if n >= 2 else 0.0


def honest_coverage(ep: Episode, toolsvc: bool = True, only_covert: bool = True) -> float:
    """Fraction of (covert) events with >=1 honest witness."""
    coll = set(ep.config.colluders)
    evs = [e for e in ep.events if e.covert or not only_covert]
    if not evs:
        return float("nan")
    def honest(e):
        return any((w == TOOLSVC) or (w not in coll) for w in e.witnesses(toolsvc))
    return sum(honest(e) for e in evs) / len(evs)


def detectable(ep: Episode, toolsvc: bool = True) -> bool:
    """Theoretical upper bound: some covert event has an honest witness."""
    cov = honest_coverage(ep, toolsvc)
    return cov == cov and cov > 0  # nan-safe
