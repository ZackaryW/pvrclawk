from pathlib import Path
import json
from datetime import datetime, timezone

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
    assert storage.sessions_dir.exists()
    assert storage.session_index_file.exists()


def test_activate_session_creates_index_and_session_files(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    session = storage.activate_session()

    index_payload = json.loads(storage.session_index_file.read_text(encoding="utf-8"))
    assert index_payload["active_session_id"] == session.session_id
    assert session.session_id in index_payload["session_ids"]
    assert (storage.sessions_dir / f"{session.session_id}.json").exists()


def test_clear_session_only_removes_target_and_rehomes_active(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    first = storage.activate_session(session_id="session-a")
    second = storage.activate_session(session_id="session-b")
    assert second.session_id == "session-b"
    assert storage.clear_session("session-b") is True

    index_payload = json.loads(storage.session_index_file.read_text(encoding="utf-8"))
    assert "session-b" not in index_payload["session_ids"]
    assert index_payload["active_session_id"] == "session-a"
    assert (storage.sessions_dir / "session-b.json").exists() is False


def test_migrates_legacy_session_payload_to_multi_layout(tmp_path: Path):
    root = tmp_path / ".pvrclawk"
    root.mkdir(parents=True, exist_ok=True)
    legacy_id = "legacy-session"
    legacy_payload = {
        "session_id": legacy_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "served_uids": ["abc"],
    }
    (root / "session.json").write_text(json.dumps(legacy_payload), encoding="utf-8")

    storage = StorageEngine(root)
    storage.init_db()
    session = storage.load_active_session()
    assert session is not None
    assert session.session_id == legacy_id
    assert session.served_uids == ["abc"]
    assert (storage.sessions_dir / f"{legacy_id}.json").exists()


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
    storage.activate_session(session_id="test-session")
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
