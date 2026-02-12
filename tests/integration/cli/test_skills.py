import json
from pathlib import Path

from pvrclawk.app import main


def _seed_standard(repo: Path) -> None:
    skill = repo / "skills" / "web-testing"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: web-testing\n"
        "description: Browser testing helpers\n"
        "---\n\n"
        "# Web Testing\n",
        encoding="utf-8",
    )


def _seed_story(repo: Path) -> None:
    skill = repo / "skills" / "use-skill"
    nested = skill / "find"
    skill.mkdir(parents=True)
    nested.mkdir(parents=True)
    (skill / "skill.json").write_text(
        json.dumps(
            {
                "goal": "Resolve and use skills by keyword",
                "acceptance_criteria": ["Matches by folder and description"],
                "features": [],
            }
        ),
        encoding="utf-8",
    )
    (nested / "skill.json").write_text(
        json.dumps(
            {
                "goal": "Find and match skills by keyword",
                "acceptance_criteria": ["Supports nested skill resolution"],
                "features": [],
            }
        ),
        encoding="utf-8",
    )


def test_skills_list(runner, tmp_path, monkeypatch):
    repo = tmp_path / "my-skills-v2"
    _seed_standard(repo)
    _seed_story(repo)
    monkeypatch.setenv("MY_SKILLS_REPO", str(repo))

    result = runner.invoke(main, ["skills", "list"])
    assert result.exit_code == 0
    assert "web-testing" in result.output
    assert "use-skill" in result.output


def test_skills_list_human_view(runner, tmp_path, monkeypatch):
    repo = tmp_path / "my-skills-v2"
    _seed_standard(repo)
    _seed_story(repo)
    monkeypatch.setenv("MY_SKILLS_REPO", str(repo))

    result = runner.invoke(main, ["skills", "list", "--human"])
    assert result.exit_code == 0
    assert "NAME" in result.output
    assert "FORMAT" in result.output
    assert "web-testing" in result.output
    assert "use-skill" in result.output
    assert "use-skill/find" in result.output


def test_skills_resolve_matches_keywords(runner, tmp_path, monkeypatch):
    repo = tmp_path / "my-skills-v2"
    _seed_standard(repo)
    _seed_story(repo)
    monkeypatch.setenv("MY_SKILLS_REPO", str(repo))

    result = runner.invoke(main, ["skills", "resolve", "browser"])
    assert result.exit_code == 0
    assert "web-testing" in result.output
    assert "Browser testing helpers" in result.output


def test_skills_resolve_full_includes_path_and_format(runner, tmp_path, monkeypatch):
    repo = tmp_path / "my-skills-v2"
    _seed_standard(repo)
    _seed_story(repo)
    monkeypatch.setenv("MY_SKILLS_REPO", str(repo))

    result = runner.invoke(main, ["skills", "resolve", "--full", "browser"])
    assert result.exit_code == 0
    assert "[standard]" in result.output
    assert str((repo / "skills" / "web-testing").resolve()) in result.output


def test_skills_resolve_path_only_outputs_only_paths(runner, tmp_path, monkeypatch):
    repo = tmp_path / "my-skills-v2"
    _seed_standard(repo)
    _seed_story(repo)
    monkeypatch.setenv("MY_SKILLS_REPO", str(repo))

    result = runner.invoke(main, ["skills", "resolve", "--path-only", "browser"])
    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.splitlines() if line.strip()]
    assert lines == [str((repo / "skills" / "web-testing").resolve())]

