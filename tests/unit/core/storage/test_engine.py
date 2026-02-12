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
    assert storage.recent_uid_file.exists()
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


def test_resolve_uid_supports_unique_prefix_and_recent_index(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    uid1 = storage.save_node(Memory(content="one"), "memory")
    uid2 = storage.save_node(Memory(content="two"), "memory")

    assert storage.resolve_uid(uid1[:8]) == uid1
    assert storage.resolve_recent_uid(1) == uid2
    assert storage.resolve_recent_uid(2) == uid1
    assert storage.resolve_recent_uid(11) is None


def test_resolve_uid_with_reason_detects_ambiguity(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    storage.save_node(Memory(uid="abcd1111-1111-1111-1111-111111111111", content="one"), "memory")
    storage.save_node(Memory(uid="abcd2222-2222-2222-2222-222222222222", content="two"), "memory")
    resolved, reason = storage.resolve_uid_with_reason("abcd")
    assert resolved is None
    assert reason == "ambiguous"
