"""Core invariants: theory, consistent forgery, matcher behaviour, metrics."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from wn.blueteam.b2_matcher import audit  # noqa: E402
from wn.env import graphs  # noqa: E402
from wn.env.episode import make_config, run_episodes  # noqa: E402
from wn.eval.metrics import auroc, tpr_at_fpr  # noqa: E402
from wn.llm.backends import MockBackend, parse_json  # noqa: E402
from wn.redteam import tamper_ops  # noqa: E402
from wn.theory.coverage import bundle_detectable, honest_coverage, tamper_coverage  # noqa: E402


def _ep(topo="complete", k=2, seed=1):
    return run_episodes([make_config("t", 8, topo, k, seed=seed)], MockBackend())[0]


def test_graphs():
    assert len(graphs.complete(8)) == 28
    assert len(graphs.ring(8)) == 8
    assert len(graphs.hub(8)) == 7
    g = graphs.random_regular(8, 3, seed=0)
    assert len(g) == 12 and graphs.is_connected(8, g)


def test_untampered_is_consistent():
    ep = _ep()
    assert audit(tamper_ops.untampered(ep)["raw"])["score"] == 0


def test_colluder_only_forgery_undetectable_without_toolsvc():
    ep = _ep()
    assert ep.side_task_success
    assert honest_coverage(ep, toolsvc=False) == 0.0
    for op in tamper_ops.OPS:
        assert audit(tamper_ops.apply(ep, op, seed=3)["raw"], toolsvc=False)["score"] == 0


def test_toolsvc_catches_spoof_and_blames_integrator():
    ep = _ep()
    r = audit(tamper_ops.apply(ep, "SPOOF", seed=0)["raw"], toolsvc=True)
    assert r["score"] > 0
    assert max(r["agent_scores"], key=r["agent_scores"].get) == str(ep.config.integrator)


def test_theory_matches_b2_on_scripted_ops():
    """Proposition: for coordinated (scripted) forgery, B2 detects iff some tampered record has a non-coalition party."""
    import itertools
    agree = total = 0
    for topo, k, seed in itertools.product(["complete", "ring", "hub", "regular3"], [1, 2, 3, 4], range(3)):
        ep = _ep(topo, k, seed)
        for op in tamper_ops.OPS:
            b = tamper_ops.apply(ep, op, seed=seed)
            if not any(r["op"] != "journal" for r in b["record"]):
                continue
            for ts in (True, False):
                total += 1
                agree += (audit(b["raw"], toolsvc=ts)["score"] > 0) == bundle_detectable(ep, b, toolsvc=ts)
    assert total > 50 and agree == total, (agree, total)


def test_metrics():
    assert auroc([1, 2, 3], [0, 0, 0]) == 1.0
    assert auroc([0], [0]) == 0.5
    assert tpr_at_fpr([5, 6], [0, 1, 2, 3, 4] * 4, 0.05) == 1.0


def test_parse_json_tolerant():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Sure! {"a": {"b": 2}} done') == {"a": {"b": 2}}
    assert parse_json("nope") is None
