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
