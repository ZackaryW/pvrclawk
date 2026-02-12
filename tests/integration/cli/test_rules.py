from pvrclawk.app import main


def test_rule_add_and_list(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    add = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "rule", "add", 'if tag("tcp") then weight("tcp") += 0.1'],
    )
    assert add.exit_code == 0

    listed = runner.invoke(main, ["membank", "--path", str(db_path), "rule", "list"])
    assert listed.exit_code == 0
    assert 'tag("tcp")' in listed.output
