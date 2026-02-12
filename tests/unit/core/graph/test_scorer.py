from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.link import Link


def test_score_match_positive():
    scorer = VectorScorer(AppConfig())
    link = Link(source="a", target="b", tags=["tcp"], weight=1.0, decay=1.0, usage_count=2)
    assert scorer.score_link(link, ["tcp"], total_frequency=10) > 0


def test_score_no_match_zero():
    scorer = VectorScorer(AppConfig())
    link = Link(source="a", target="b", tags=["auth"])
    assert scorer.score_link(link, ["tcp"], total_frequency=10) == 0.0


def test_decay_relative_to_total_frequency():
    scorer = VectorScorer(AppConfig())
    high = scorer.compute_decay(link_frequency=8, total_frequency=10)
    low = scorer.compute_decay(link_frequency=1, total_frequency=10)
    assert high > low
    assert 0.0 <= low <= 1.0
