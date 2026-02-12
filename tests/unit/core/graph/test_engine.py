from pvrclawk.membank.core.graph.engine import GraphEngine
from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.models.config import AppConfig
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
