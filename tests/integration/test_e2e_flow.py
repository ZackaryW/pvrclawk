from pvrclawk.app import main


def test_full_e2e_flow(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    assert runner.invoke(main, ["membank", "--path", str(db_path), "init"]).exit_code == 0

    n1 = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "tcp setup", "--tags", "tcp:1.0"],
    )
    n2 = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "tcp method", "--tags", "tcp:1.0"],
    )
    uid1 = n1.output.strip().splitlines()[-1]
    uid2 = n2.output.strip().splitlines()[-1]
    assert uid1 and uid2

    assert (
        runner.invoke(
            main,
            [
                "membank",
                "--path",
                str(db_path),
                "link",
                "add",
                uid1,
                uid2,
                "--tags",
                "tcp,method",
                "--weight",
                "1.0",
            ],
        ).exit_code
        == 0
    )

    assert runner.invoke(main, ["membank", "--path", str(db_path), "prune"]).exit_code == 0
    focus_before = runner.invoke(main, ["membank", "--path", str(db_path), "focus", "--tags", "tcp", "--limit", "5"])
    assert focus_before.exit_code == 0
    assert "tcp method" in focus_before.output

    assert runner.invoke(main, ["membank", "--path", str(db_path), "report", "mood", "tcp", "0.2"]).exit_code == 0
    assert (
        runner.invoke(
            main,
            ["membank", "--path", str(db_path), "rule", "add", 'if tag("tcp") then weight("tcp") += 0.1'],
        ).exit_code
        == 0
    )
    focus_after = runner.invoke(main, ["membank", "--path", str(db_path), "focus", "--tags", "tcp", "--limit", "5"])
    assert focus_after.exit_code == 0
