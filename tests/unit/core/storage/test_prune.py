from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
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
