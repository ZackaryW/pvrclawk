from pvrclawk.membank.models.index import ClusterMeta, IndexData


def test_index_defaults():
    idx = IndexData()
    assert idx.tags == {}
    assert idx.clusters == {}


def test_cluster_meta():
    meta = ClusterMeta(top_tags=["tcp"], size=2)
    assert meta.size == 2
