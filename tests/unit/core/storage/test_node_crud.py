from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.nodes import (
    Active,
    Archive,
    Feature,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
)


def test_save_load_roundtrip_for_all_node_types(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()

    nodes = [
        ("memory", Memory(content="m")),
        ("memorylink", MemoryLink(title="t", summary="s", file_path=".pvrclawk/additional_memory/t.md")),
        ("story", Story(role="dev", benefit="ship")),
        ("feature", Feature(component="api", test_scenario="Given", expected_result="Then")),
        ("active", Active(content="a", focus_area="f")),
        ("archive", Archive(content="a", archived_from="active", reason="done")),
        ("pattern", Pattern(content="p", pattern_type="arch")),
        ("progress", Progress(content="p")),
    ]
    uids = []
    for node_type, node in nodes:
        node.add_tag("tag1", 1.0)
        uids.append(storage.save_node(node, node_type))

    loaded = storage.load_nodes(uids)
    assert len(loaded) == len(nodes)


def test_load_nodes_by_type(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    m = Memory(content="m")
    s = Story(role="r", benefit="b")
    storage.save_node(m, "memory")
    storage.save_node(s, "story")
    memories = storage.load_nodes_by_type("memory")
    assert len(memories) == 1
    assert isinstance(memories[0], Memory)


def test_memorylink_file_creation(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    path = storage.create_memory_file("TCP Notes", "# long content")
    assert path.name == "tcp-notes.md"
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# long content"


def test_memorylink_no_overwrite_existing(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    path = storage.create_memory_file("TCP Notes", "# original content")
    assert path.read_text(encoding="utf-8") == "# original content"
    # Second call with different content should NOT overwrite
    path2 = storage.create_memory_file("TCP Notes", "# overwritten content")
    assert path2 == path
    assert path.read_text(encoding="utf-8") == "# original content"


def test_load_single_node(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    story = Story(role="Build CLI", benefit="Agents can use it")
    uid = storage.save_node(story, "story")
    loaded = storage.load_node(uid)
    assert loaded is not None
    assert isinstance(loaded, Story)
    assert loaded.role == "Build CLI"


def test_load_single_node_missing(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    assert storage.load_node("nonexistent-uid") is None


def test_update_node_status(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    story = Story(role="Build CLI", benefit="Agents can use it")
    uid = storage.save_node(story, "story")
    assert storage.update_node_status(uid, "done") is True
    loaded = storage.load_node(uid)
    assert loaded is not None
    assert isinstance(loaded, Story)
    assert loaded.status.value == "done"


def test_update_node_status_missing(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    assert storage.update_node_status("nonexistent", "done") is False


def test_auto_archive_active_on_new_active(tmp_path: Path):
    """When auto_archive_active=True, adding a new active node archives existing ones."""
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    old = Active(content="old context", focus_area="old-focus")
    old.add_tag("active", 1.0)
    storage.save_node(old, "active")

    new = Active(content="new context", focus_area="new-focus")
    new.add_tag("active", 1.0)
    storage.save_node(new, "active")

    # Old should be archive now
    archives = storage.load_nodes_by_type("archive")
    assert len(archives) == 1
    assert archives[0].content == "old context"

    # Only new should remain as active
    actives = storage.load_nodes_by_type("active")
    assert len(actives) == 1
    assert actives[0].content == "new context"


def test_auto_archive_disabled_via_config(tmp_path: Path):
    """When auto_archive_active=False, old active nodes are NOT archived."""
    from pvrclawk.utils.config import AppConfig, write_config

    root = tmp_path / ".pvrclawk"
    storage = StorageEngine(root)
    storage.init_db()

    # Disable auto-archive
    write_config(root / "config.toml", AppConfig(auto_archive_active=False))

    old = Active(content="old context", focus_area="old-focus")
    old.add_tag("active", 1.0)
    storage.save_node(old, "active")

    new = Active(content="new context", focus_area="new-focus")
    new.add_tag("active", 1.0)
    storage.save_node(new, "active")

    # Both should remain as active
    actives = storage.load_nodes_by_type("active")
    assert len(actives) == 2
    archives = storage.load_nodes_by_type("archive")
    assert len(archives) == 0
