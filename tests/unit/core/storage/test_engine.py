from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.link import Link
from pvrclawk.membank.models.nodes import Memory


def test_init_db_creates_layout(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    assert storage.nodes_dir.exists()
    assert storage.additional_memory_dir.exists()
    assert storage.index_file.exists()
    assert storage.config_file.exists()


def test_save_and_load_node_roundtrip(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    node = Memory(content="hello")
    node.add_tag("tcp", 1.0)
    uid = storage.save_node(node, "memory")
    loaded = storage.load_nodes([uid])
    assert len(loaded) == 1
    assert loaded[0].uid == uid


def test_save_and_load_links(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    link = Link(source="s1", target="t1", tags=["tcp"])
    storage.save_link(link)
    loaded = storage.load_links(["s1"])
    assert len(loaded) == 1
    assert loaded[0].target == "t1"
