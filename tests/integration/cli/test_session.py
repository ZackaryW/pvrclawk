import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pvrclawk.app import main


def test_session_up_info_and_tear(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    up = runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])
    assert up.exit_code == 0
    session_id = up.output.strip()
    assert session_id

    session_file = db_path / "session.json"
    assert session_file.exists()
    payload = json.loads(session_file.read_text(encoding="utf-8"))
    assert payload["session_id"] == session_id
    assert payload["served_uids"] == []

    info = runner.invoke(main, ["membank", "--path", str(db_path), "session", "info"])
    assert info.exit_code == 0
    assert f"session_id={session_id}" in info.output
    assert "served_count=0" in info.output

    tear = runner.invoke(main, ["membank", "--path", str(db_path), "session", "tear"])
    assert tear.exit_code == 0
    assert "Session cleared." in tear.output
    assert not session_file.exists()


def test_focus_uses_session_and_truncates_served_nodes(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "tcp setup", "--tags", "tcp:1.0"],
    )
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    first = runner.invoke(main, ["membank", "--path", str(db_path), "focus", "--tags", "tcp", "--limit", "5"])
    assert first.exit_code == 0
    assert "tcp setup" in first.output

    second = runner.invoke(main, ["membank", "--path", str(db_path), "focus", "--tags", "tcp", "--limit", "5"])
    assert second.exit_code == 0
    assert "tcp setup" not in second.output
    assert "(Memory)" in second.output


def test_node_list_uses_session_and_reset_restores_full_output(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "session note", "--tags", "ctx:1.0"],
    )
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    first_list = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert first_list.exit_code == 0
    assert "session note" in first_list.output

    second_list = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert second_list.exit_code == 0
    assert "session note" not in second_list.output
    assert "(Memory)" in second_list.output

    reset = runner.invoke(main, ["membank", "--path", str(db_path), "session", "reset"])
    assert reset.exit_code == 0

    third_list = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert third_list.exit_code == 0
    assert "session note" in third_list.output


def test_expired_session_is_treated_as_absent(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "stale session note", "--tags", "stale:1.0"],
    )
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    session_file = db_path / "session.json"
    payload = json.loads(session_file.read_text(encoding="utf-8"))
    payload["created_at"] = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat().replace("+00:00", "Z")
    session_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    info = runner.invoke(main, ["membank", "--path", str(db_path), "session", "info"])
    assert info.exit_code == 0
    assert "No active session." in info.output

    listing = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert listing.exit_code == 0
    assert "stale session note" in listing.output


def test_session_flag_overrides_env_and_persists_active_session(runner, tmp_path, monkeypatch):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "override note", "--tags", "override:1.0"],
    )
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    env_id = str(uuid4())
    flag_id = str(uuid4())
    monkeypatch.setenv("PVRCLAWK_SESSION", env_id)

    with_flag = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "--session", flag_id, "node", "list", "memory"],
    )
    assert with_flag.exit_code == 0
    assert "override note" in with_flag.output

    payload = json.loads((db_path / "session.json").read_text(encoding="utf-8"))
    assert payload["session_id"] == flag_id

    monkeypatch.delenv("PVRCLAWK_SESSION")
    after_flag = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert after_flag.exit_code == 0
    assert "override note" not in after_flag.output
