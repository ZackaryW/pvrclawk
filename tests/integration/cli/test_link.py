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


def test_link_chain_creates_adjacent_links_in_one_command(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    a = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "A"])
    b = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "B"])
    c = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "C"])
    uid_a = a.output.strip()
    uid_b = b.output.strip()
    uid_c = c.output.strip()

    chain = runner.invoke(
        main,
        [
            "membank",
            "--path",
            str(db_path),
            "link",
            "chain",
            uid_a,
            uid_b,
            uid_c,
            "--tags",
            "flow,related",
            "--weight",
            "0.9",
        ],
    )
    assert chain.exit_code == 0
    assert "created 2 links" in chain.output.lower()

    list_a = runner.invoke(main, ["membank", "--path", str(db_path), "link", "list", uid_a])
    list_b = runner.invoke(main, ["membank", "--path", str(db_path), "link", "list", uid_b])
    assert uid_b in list_a.output
    assert uid_c in list_b.output


def test_link_chain_requires_at_least_two_uids(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    a = runner.invoke(main, ["membank", "--path", str(db_path), "node", "add", "memory", "--content", "A"])
    uid_a = a.output.strip()

    chain = runner.invoke(main, ["membank", "--path", str(db_path), "link", "chain", uid_a])
    assert chain.exit_code != 0
    assert "at least two uids" in chain.output.lower()


def test_link_list_federated_reads_remote_source(runner, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host_db = repo / "apps" / "host" / ".pvrclawk"
    remote_db = repo / "libs" / "shared" / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(host_db), "init"])
    runner.invoke(main, ["membank", "--path", str(remote_db), "init"])

    source = runner.invoke(
        main,
        ["membank", "--path", str(remote_db), "node", "add", "memory", "--content", "remote source", "--tags", "federation:1.0"],
    )
    target = runner.invoke(
        main,
        ["membank", "--path", str(remote_db), "node", "add", "memory", "--content", "remote target", "--tags", "federation:1.0"],
    )
    source_uid = source.output.strip().splitlines()[-1]
    target_uid = target.output.strip().splitlines()[-1]
    runner.invoke(
        main,
        ["membank", "--path", str(remote_db), "link", "add", source_uid, target_uid, "--tags", "federation", "--weight", "1.0"],
    )

    result = runner.invoke(
        main,
        ["membank", "--path", str(host_db), "--federated", "link", "list", source_uid],
    )
    assert result.exit_code == 0
    assert target_uid in result.output
