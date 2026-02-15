"""Integration tests for membank forctx command."""

from pvrclawk.app import main


def test_forctx_returns_ranked_nodes_by_query(runner, tmp_path):
    """forctx with #tag and [phrase] returns nodes ranked by tag and content match."""
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "task", "--content", "auth flow", "--tags", "task"],
    )
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "task", "--content", "other", "--tags", "misc"],
    )

    result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "forctx", "#task [auth]", "--top", "5"],
    )
    assert result.exit_code == 0
    assert "auth flow" in result.output
    assert "task" in result.output
    # First line should show a score (tag+content ranks higher)
    lines = result.output.strip().split("\n")
    assert any("[0" in line or "[1" in line or "[2" in line or "[3" in line for line in lines)


def test_forctx_session_truncation(runner, tmp_path):
    """With active session, second forctx call returns header-only for already-served nodes."""
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "task", "--content", "session task", "--tags", "t"],
    )
    runner.invoke(main, ["membank", "--path", str(db_path), "session", "up"])

    first = runner.invoke(main, ["membank", "--path", str(db_path), "forctx", "#t", "--top", "5"])
    assert first.exit_code == 0
    assert "session task" in first.output

    second = runner.invoke(main, ["membank", "--path", str(db_path), "forctx", "#t", "--top", "5"])
    assert second.exit_code == 0
    assert "session task" not in second.output
    assert "(Task)" in second.output
