"""Integration tests for membank last command."""

from pvrclawk.app import main


def test_last_returns_most_recently_updated_nodes(runner, tmp_path):
    """last --top N returns up to N nodes ordered by updated_at descending."""
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "Older", "--summary", "old"])
    add_new = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "Newer", "--summary", "new"])
    new_uid = add_new.output.strip()
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "status", new_uid, "in_progress"])

    result = runner.invoke(main, ["membank", "--path", str(db_path), "last", "--top", "2"])
    assert result.exit_code == 0
    assert "Newer" in result.output
    assert "Older" in result.output
    # Two nodes, most recent first; output has at least 2 node blocks
    assert result.output.count("(Story)") >= 2


def test_last_empty_bank_returns_no_output(runner, tmp_path):
    """last on empty bank produces no output."""
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])

    result = runner.invoke(main, ["membank", "--path", str(db_path), "last", "--top", "10"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_last_uses_session_truncation(runner, tmp_path):
    """With active session, second last call returns header-only for already-served nodes."""
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "task", "--content", "recent task", "--tags", "t"])
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    first = runner.invoke(main, ["membank", "--path", str(db_path), "last", "--top", "5"])
    assert first.exit_code == 0
    assert "recent task" in first.output

    second = runner.invoke(main, ["membank", "--path", str(db_path), "last", "--top", "5"])
    assert second.exit_code == 0
    assert "recent task" not in second.output
    assert "(Task)" in second.output
