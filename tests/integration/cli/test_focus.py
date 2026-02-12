from pvrclawk.app import main


def test_focus_returns_ranked_nodes(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])

    a = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "tcp setup", "--tags", "tcp:1.0"],
    )
    b = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "tcp method", "--tags", "tcp:1.0"],
    )
    source_uid = a.output.strip().splitlines()[-1]
    target_uid = b.output.strip().splitlines()[-1]
    runner.invoke(
        main,
        [
            "membank",
            "--path",
            str(db_path),
            "link",
            "add",
            source_uid,
            target_uid,
            "--tags",
            "tcp,method",
            "--weight",
            "1.0",
        ],
    )

    focus = runner.invoke(main, ["membank", "--path", str(db_path), "focus", "--tags", "tcp", "--limit", "5"])
    assert focus.exit_code == 0
    assert "tcp method" in focus.output
