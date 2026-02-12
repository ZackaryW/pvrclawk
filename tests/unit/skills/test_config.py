from pathlib import Path

from pvrclawk.skills.core.config import load_skills_config


def test_load_skills_config_from_file(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MY_SKILLS_REPO", raising=False)
    monkeypatch.delenv("SKILLS_GROUP_DIR", raising=False)
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        'skills_repo = ["C:/repo/a"]\n'
        'skills_group = ["C:/group"]\n'
        'skills_format = ["story-driven"]\n',
        encoding="utf-8",
    )
    parsed = load_skills_config(config_path=cfg)
    assert parsed.skills_repo == ["C:/repo/a"]
    assert parsed.skills_group == ["C:/group"]
    assert parsed.skills_format == ["story-driven"]


def test_load_skills_config_merges_env(tmp_path: Path, monkeypatch):
    cfg = tmp_path / "config.toml"
    cfg.write_text('skills_repo = ["C:/repo/a"]\n', encoding="utf-8")
    monkeypatch.setenv("MY_SKILLS_REPO", "C:/repo/b")
    monkeypatch.setenv("SKILLS_GROUP_DIR", "C:/groups")
    parsed = load_skills_config(config_path=cfg)
    assert "C:/repo/a" in parsed.skills_repo
    assert "C:/repo/b" in parsed.skills_repo
    assert "C:/groups" in parsed.skills_group

