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
