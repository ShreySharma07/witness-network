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
from wn.theory.coverage import honest_coverage, p_undetectable_pairwise  # noqa: E402


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


def test_theory_pairwise():
    assert p_undetectable_pairwise(8, 0) == 0
    assert p_undetectable_pairwise(8, 8) == 1
    assert abs(p_undetectable_pairwise(8, 2) - 1 / 28) < 1e-9


def test_metrics():
    assert auroc([1, 2, 3], [0, 0, 0]) == 1.0
    assert auroc([0], [0]) == 0.5
    assert tpr_at_fpr([5, 6], [0, 1, 2, 3, 4] * 4, 0.05) == 1.0


def test_parse_json_tolerant():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Sure! {"a": {"b": 2}} done') == {"a": {"b": 2}}
    assert parse_json("nope") is None
