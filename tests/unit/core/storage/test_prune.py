from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.link import Link
from pvrclawk.membank.models.nodes import Memory


def test_prune_rebalances_inbox_to_named_cluster(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    for content in ["a", "b", "c"]:
        n = Memory(content=content)
        n.add_tag("tcp", 1.0)
        n.add_tag("timeout", 0.8)
        storage.save_node(n, "memory")

    cluster_name = storage.prune()
    assert "tcp" in cluster_name
    assert (storage.nodes_dir / f"{cluster_name}.json").exists()
    idx = storage.load_index()
    assert cluster_name in idx.clusters


def test_prune_rebuilds_links_in(tmp_path: Path):
    """After prune, links_in should reflect the actual links on disk."""
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    n1 = Memory(content="source")
    n1.add_tag("tcp", 1.0)
    n2 = Memory(content="target")
    n2.add_tag("tcp", 1.0)
    storage.save_node(n1, "memory")
    storage.save_node(n2, "memory")

    link = Link(source=n1.uid, target=n2.uid, tags=["tcp"])
    storage.save_link(link)

    storage.prune()
    idx = storage.load_index()
    # links_in should map target -> [source]
    assert n2.uid in idx.links_in
    assert n1.uid in idx.links_in[n2.uid]
