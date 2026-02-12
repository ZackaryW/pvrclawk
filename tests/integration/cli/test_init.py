from pvrclawk.app import main


def test_membank_init_creates_layout(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    result = runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    assert result.exit_code == 0
    assert (db_path / "nodes").exists()
    assert (db_path / "additional_memory").exists()
    assert (db_path / "index.json").exists()
    assert (db_path / "links.json").exists()
    assert (db_path / "rules.json").exists()
    assert (db_path / "mood.json").exists()
    assert (db_path / "recent_uid.json").exists()
    assert (db_path / "config.toml").exists()
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert ".pvrclawk/recent_uid.json" in gitignore.read_text(encoding="utf-8")
