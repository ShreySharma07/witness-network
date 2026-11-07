"""Communication topologies. Nodes are 0..n-1; edges are undirected."""
from __future__ import annotations

import random


def complete(n: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def ring(n: int) -> list[tuple[int, int]]:
    return sorted({tuple(sorted((i, (i + 1) % n))) for i in range(n)})


def hub(n: int, center: int = 0) -> list[tuple[int, int]]:
    return [(center, j) for j in range(n) if j != center]


def random_regular(n: int, d: int = 3, seed: int = 0) -> list[tuple[int, int]]:
    """Random d-regular graph via repeated pairing (configuration model with rejection)."""
    rng = random.Random(seed)
    for _ in range(1000):
        stubs = [v for v in range(n) for _ in range(d)]
        rng.shuffle(stubs)
        edges = set()
        ok = True
        for a, b in zip(stubs[::2], stubs[1::2]):
            e = tuple(sorted((a, b)))
            if a == b or e in edges:
                ok = False
                break
            edges.add(e)
        if ok and is_connected(n, edges):
            return sorted(edges)
    raise RuntimeError("failed to sample a connected regular graph")


def is_connected(n: int, edges) -> bool:
    adj = neighbors(n, edges)
    seen, stack = {0}, [0]
    while stack:
        for u in adj[stack.pop()]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return len(seen) == n


def neighbors(n: int, edges) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def build(topology: str, n: int, seed: int = 0) -> list[tuple[int, int]]:
    if topology == "complete":
        return complete(n)
    if topology == "ring":
        return ring(n)
    if topology == "hub":
        return hub(n)
    if topology == "regular3":
        return random_regular(n, 3, seed)
    raise ValueError(topology)
