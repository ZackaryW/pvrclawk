from pvrclawk.app import main


def test_prune_command_rebalances(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "A", "--tags", "tcp:1.0,timeout:0.8"],
    )
    runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "B", "--tags", "tcp:1.0,timeout:0.8"],
    )

    result = runner.invoke(main, ["membank", "--path", str(db_path), "prune"])
    assert result.exit_code == 0
    assert "tcp" in result.output
