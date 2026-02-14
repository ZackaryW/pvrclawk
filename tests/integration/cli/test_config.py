from pvrclawk.app import main


def test_membank_config_set_get(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    init_result = runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    assert init_result.exit_code == 0

    set_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "config", "set", "prune.auto_threshold", "30"],
    )
    assert set_result.exit_code == 0

    get_result = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "config", "get", "prune.auto_threshold"],
    )
    assert get_result.exit_code == 0
    assert "30" in get_result.output


def test_membank_config_list(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    init_result = runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    assert init_result.exit_code == 0

    list_result = runner.invoke(main, ["membank", "--path", str(db_path), "config", "list"])
    assert list_result.exit_code == 0
    assert "prune" in list_result.output
    assert "decay" in list_result.output
    assert "mood" in list_result.output
    assert "federation" in list_result.output
