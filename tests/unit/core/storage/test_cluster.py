from pvrclawk.membank.core.storage.cluster import derive_cluster_name, select_best_cluster
from pvrclawk.membank.models.index import ClusterMeta, IndexData


def test_derive_cluster_name_uses_top_tags():
    name = derive_cluster_name({"tcp": 2.0, "timeout": 1.0})
    assert "tcp" in name


def test_select_best_cluster_falls_back_to_inbox():
    idx = IndexData(clusters={"_inbox": ClusterMeta(top_tags=[], size=0)})
    selected = select_best_cluster(idx, {"newtag": 1.0})
    assert selected == "_inbox"


def test_select_best_cluster_prefers_overlap():
    idx = IndexData(
        clusters={
            "_inbox": ClusterMeta(top_tags=[], size=0),
            "tcp_timeout": ClusterMeta(top_tags=["tcp", "timeout"], size=3),
        }
    )
    selected = select_best_cluster(idx, {"tcp": 1.0})
    assert selected == "tcp_timeout"
