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


def test_focus_federated_reads_other_banks(runner, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host_db = repo / "apps" / "host" / ".pvrclawk"
    remote_db = repo / "libs" / "shared" / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(host_db), "init"])
    runner.invoke(main, ["membank", "--path", str(remote_db), "init"])

    runner.invoke(
        main,
        ["membank", "--path", str(host_db), "node", "add", "memory", "--content", "host federation", "--tags", "federation:1.0"],
    )
    runner.invoke(
        main,
        ["membank", "--path", str(remote_db), "node", "add", "memory", "--content", "remote federation", "--tags", "federation:1.0"],
    )

    focus = runner.invoke(
        main,
        ["membank", "--path", str(host_db), "--federated", "focus", "--tags", "federation", "--limit", "10"],
    )
    assert focus.exit_code == 0
    assert "host federation" in focus.output
    assert "remote federation" in focus.output
