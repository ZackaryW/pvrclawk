from pvrclawk.app import main


def test_node_add_and_list_memory(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])

    add_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "hello", "--tags", "tcp:1.0"],
    )
    assert add_result.exit_code == 0

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memory"])
    assert list_result.exit_code == 0
    assert "hello" in list_result.output


def test_node_add_memorylink_creates_file(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])

    add_result = runner.invoke(
        main,
        [
            "membank",
            "--path",
            str(db_path),
            "node",
            "add",
            "memorylink",
            "--title",
            "TCP Notes",
            "--summary",
            "Long notes",
            "--content",
            "# Markdown",
            "--tags",
            "tcp:1.0",
        ],
    )
    assert add_result.exit_code == 0

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "memorylink"])
    assert list_result.exit_code == 0
    assert "TCP Notes" in list_result.output
    assert "additional_memory/tcp-notes.md" in list_result.output


def test_node_get_by_uid(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "story", "--title", "Build CLI", "--summary", "Ship it", "--tags", "cli:1.0"],
    )
    uid = add_result.output.strip()
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", uid])
    assert get_result.exit_code == 0
    assert "Build CLI" in get_result.output
    assert "Ship it" in get_result.output


def test_node_get_missing_uid(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", "nonexistent"])
    assert get_result.exit_code == 0
    assert "not found" in get_result.output.lower()


def test_node_status_update(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "story", "--title", "Build CLI", "--summary", "Ship it"],
    )
    uid = add_result.output.strip()
    status_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "status", uid, "done"])
    assert status_result.exit_code == 0
    assert "done" in status_result.output.lower()
    # Verify via get
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", uid])
    assert "done" in get_result.output.lower()


def test_node_list_all(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "S1", "--summary", "b"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "pattern", "--title", "arch", "--content", "rule"])
    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list-all"])
    assert list_result.exit_code == 0
    assert "S1" in list_result.output
    assert "rule" in list_result.output


def test_node_add_with_status_flag(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "progress", "--content", "DONE: shipped", "--status", "done", "--tags", "status:1.0"],
    )
    assert add_result.exit_code == 0
    uid = add_result.output.strip()
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", uid])
    assert "done" in get_result.output.lower()


def test_node_add_status_default_is_todo(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "story", "--title", "S1", "--summary", "b"],
    )
    uid = add_result.output.strip()
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", uid])
    assert "todo" in get_result.output.lower()


def test_adding_active_archives_previous(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    # Add first active
    r1 = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "active", "--title", "old-focus", "--content", "old context"])
    uid1 = r1.output.strip()
    # Add second active -- should archive the first
    r2 = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "active", "--title", "new-focus", "--content", "new context"])
    assert r2.exit_code == 0
    # Old active should now be an archive
    archives = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "archive"])
    assert "old context" in archives.output
    # New active should be the only active
    actives = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "active"])
    assert "new context" in actives.output
    assert "old context" not in actives.output


def test_story_with_criteria(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add_result = runner.invoke(
        main,
        [
            "membank", "--path", str(db_path), "node", "add", "story",
            "--title", "Auth flow",
            "--summary", "Users can log in securely",
            "--criteria", "Login form validates email",
            "--criteria", "JWT token issued on success",
            "--criteria", "Failed login returns 401",
        ],
    )
    assert add_result.exit_code == 0
    uid = add_result.output.strip()

    # Criteria should appear in get output
    get_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "get", uid])
    assert "Login form validates email" in get_result.output
    assert "JWT token issued on success" in get_result.output
    assert "Failed login returns 401" in get_result.output

    # Criteria should appear in list output
    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "story"])
    assert "Login form validates email" in list_result.output


def test_node_list_top_most_recent(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "Old Story", "--summary", "old"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "New Story", "--summary", "new"])

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "story", "--top", "1"])
    assert list_result.exit_code == 0
    assert "New Story" in list_result.output
    assert "Old Story" not in list_result.output


def test_node_list_all_top_most_recent(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "S1", "--summary", "first"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "pattern", "--title", "p2", "--content", "newest rule"])

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list-all", "--top", "1"])
    assert list_result.exit_code == 0
    assert "newest rule" in list_result.output
    assert "S1" not in list_result.output
