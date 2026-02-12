from pvrclawk.app import main
from pathlib import Path


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


def test_membank_init_subpaths_to_dot_pvrclawk_for_existing_source_dir(runner, tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")

    result = runner.invoke(main, ["membank", "--path", str(source_dir), "init"])

    resolved_db_path = source_dir / ".pvrclawk"
    assert result.exit_code == 0
    initialized_path = Path(result.output.strip().replace("Initialized membank at ", ""))
    assert initialized_path.name == ".pvrclawk"
    assert initialized_path.resolve() == resolved_db_path.resolve()
    assert initialized_path.exists()
    assert (initialized_path / "nodes").exists()
    assert (initialized_path / "index.json").exists()
    assert (source_dir / "main.py").exists()


def test_membank_commands_reuse_resolved_subpath_for_existing_source_dir(runner, tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")

    init_result = runner.invoke(main, ["membank", "--path", str(source_dir), "init"])
    assert init_result.exit_code == 0

    add_result = runner.invoke(
        main,
        ["membank", "--path", str(source_dir), "node", "add", "memory", "--content", "hello", "--tags", "test:1.0"],
    )
    assert add_result.exit_code == 0

    list_result = runner.invoke(main, ["membank", "--path", str(source_dir), "node", "list", "memory"])
    assert list_result.exit_code == 0
    assert "hello" in list_result.output
    assert (source_dir / ".pvrclawk" / "index.json").exists()
    assert (source_dir / "index.json").exists() is False
