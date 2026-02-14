from pvrclawk.membank.core.graph.engine import GraphEngine
from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.models.config import AppConfig, RetrievalConfig
from pvrclawk.membank.models.link import Link
from pvrclawk.membank.models.nodes import Memory


def test_graph_engine_uses_total_frequency_and_neighbors():
    scorer = VectorScorer(AppConfig())
    engine = GraphEngine(scorer)

    n1 = Memory(content="tcp one")
    n2 = Memory(content="tcp two")
    n3 = Memory(content="related")

    l1 = Link(source=n1.uid, target=n2.uid, tags=["tcp"], weight=1.0, usage_count=10)
    l2 = Link(source=n2.uid, target=n3.uid, tags=["misc"], weight=1.0, usage_count=1)

    ranked = engine.retrieve([n1, n2, n3], [l1, l2], ["tcp"], limit=5)
    ids = [uid for uid, _ in ranked]
    assert n2.uid in ids
    # Neighbor expansion should surface n3 even if tag doesn't match directly.
    assert n3.uid in ids


def test_graph_engine_excludes_zero_score_results():
    """Zero-score nodes should not appear in focus output."""
    scorer = VectorScorer(AppConfig())
    engine = GraphEngine(scorer)

    n1 = Memory(content="tcp one")
    n1.add_tag("tcp", 1.0)
    n2 = Memory(content="tcp two")
    n3 = Memory(content="unrelated")
    n3.add_tag("unrelated", 1.0)

    l1 = Link(source=n1.uid, target=n2.uid, tags=["tcp"], weight=1.0, usage_count=5)

    ranked = engine.retrieve([n1, n2, n3], [l1], ["tcp"], limit=10)
    scores = {uid: s for uid, s in ranked}
    # n1 and n2 should be present with positive scores
    assert scores.get(n1.uid, 0) > 0
    assert scores.get(n2.uid, 0) > 0
    # n3 has no tag match and no link -- should NOT appear
    assert n3.uid not in scores


def test_graph_engine_no_zero_score_from_link_misses():
    """Links with non-matching tags should not inject 0-score targets.

    This is the defaultdict(float) bug: accessing scores[link.target]
    with a += 0.0 still creates the key, polluting results.
    """
    scorer = VectorScorer(AppConfig())
    engine = GraphEngine(scorer)

    active_node = Memory(content="current focus")
    active_node.add_tag("active", 1.0)

    feature_node = Memory(content="some feature")
    feature_node.add_tag("architecture", 1.0)

    story_node = Memory(content="a story")
    story_node.add_tag("architecture", 1.0)

    # Story links to feature with tags that DON'T match "active"
    l1 = Link(source=story_node.uid, target=feature_node.uid, tags=["architecture"], weight=1.0, usage_count=5)

    ranked = engine.retrieve(
        [active_node, feature_node, story_node], [l1], ["active"], limit=10
    )
    scores = {uid: s for uid, s in ranked}
    # active_node should appear (direct tag match)
    assert scores.get(active_node.uid, 0) > 0
    # feature_node should NOT appear (link tag "architecture" doesn't match "active")
    assert feature_node.uid not in scores


def test_graph_engine_no_results_for_unknown_tag():
    """Querying a tag that no node has should return empty."""
    scorer = VectorScorer(AppConfig())
    engine = GraphEngine(scorer)

    n1 = Memory(content="stuff")
    n1.add_tag("membank", 1.0)
    ranked = engine.retrieve([n1], [], ["authentication"], limit=5)
    assert len(ranked) == 0


def test_graph_engine_applies_node_multipliers():
    scorer = VectorScorer(AppConfig())
    engine = GraphEngine(scorer)

    n1 = Memory(content="near host")
    n1.add_tag("federation", 1.0)
    n2 = Memory(content="far host")
    n2.add_tag("federation", 1.0)

    ranked = engine.retrieve(
        [n1, n2],
        [],
        ["federation"],
        limit=5,
        node_multipliers={n1.uid: 2.0, n2.uid: 0.5},
    )
    scores = {uid: score for uid, score in ranked}
    assert scores[n1.uid] > scores[n2.uid]


def test_graph_engine_resistance_threshold_filters_low_scores():
    """Nodes with score below retrieval.resistance_threshold are excluded."""
    config = AppConfig(retrieval=RetrievalConfig(resistance_threshold=0.6))
    scorer = VectorScorer(config)
    engine = GraphEngine(scorer)

    high = Memory(content="high")
    high.add_tag("task", 1.0)
    low = Memory(content="low")
    low.add_tag("task", 0.3)

    ranked = engine.retrieve([high, low], [], ["task"], limit=10)
    uids = [uid for uid, _ in ranked]
    assert high.uid in uids
    assert low.uid not in uids
