from pvrclawk.membank.core.storage.index import add_unique, remove_value


def test_add_unique_deduplicates():
    data = {}
    add_unique(data, "tcp", "u1")
    add_unique(data, "tcp", "u1")
    assert data["tcp"] == ["u1"]


def test_remove_value_cleans_empty_key():
    data = {"tcp": ["u1"]}
    remove_value(data, "tcp", "u1")
    assert "tcp" not in data
