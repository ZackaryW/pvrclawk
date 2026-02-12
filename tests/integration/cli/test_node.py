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


def test_add_task_and_subtask_with_status(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    task_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "task", "--content", "implement api", "--status", "in_progress"],
    )
    subtask_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "subtask", "--content", "write tests", "--status", "todo"],
    )
    assert task_result.exit_code == 0
    assert subtask_result.exit_code == 0
    tasks = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "task"])
    subtasks = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "subtask"])
    assert "implement api" in tasks.output
    assert "write tests" in subtasks.output


def test_add_active_is_deprecated(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "active", "--content", "legacy"])
    assert result.exit_code != 0
    assert "deprecated" in result.output.lower()


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
    new_add = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "New Story", "--summary", "new"])
    new_uid = new_add.output.strip()
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "status", new_uid, "in_progress"])

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list", "story", "--top", "1"])
    assert list_result.exit_code == 0
    assert "New Story" in list_result.output
    assert "Old Story" not in list_result.output


def test_node_list_all_top_most_recent(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    story_add = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "story", "--title", "S1", "--summary", "first"])
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "pattern", "--title", "p2", "--content", "older rule"])
    story_uid = story_add.output.strip()
    runner.invoke(main, ["membank", "--path", str(db_path), "node", "status", story_uid, "in_progress"])

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "node", "list-all", "--top", "1"])
    assert list_result.exit_code == 0
    assert "S1" in list_result.output
