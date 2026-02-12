from pvrclawk.app import main


def test_link_add_list_weight_flow(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    a = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "A", "--tags", "tcp:1.0"],
    )
    b = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "B", "--tags", "tcp:1.0"],
    )
    assert a.exit_code == 0
    assert b.exit_code == 0
    source_uid = a.output.strip().splitlines()[-1]
    target_uid = b.output.strip().splitlines()[-1]

    add_link = runner.invoke(
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
    assert add_link.exit_code == 0

    list_link = runner.invoke(main, ["membank", "--path", str(db_path), "link", "list", source_uid])
    assert list_link.exit_code == 0
    assert target_uid in list_link.output

    weight = runner.invoke(
        main,
        ["membank", "--path", str(db_path), "link", "weight", "tcp,method", "0.1"],
    )
    assert weight.exit_code == 0
    assert "1" in weight.output
