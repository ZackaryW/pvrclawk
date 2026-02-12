import json
from pathlib import Path

from pvrclawk.skills.core.scanner import collect_skill_repos, scan_skills
from pvrclawk.skills.models.config import SkillsConfig


def test_collect_skill_repos_from_repo_and_group(tmp_path: Path):
    direct_repo = tmp_path / "repo-a"
    (direct_repo / "skills").mkdir(parents=True)

    group_root = tmp_path / "groups"
    repo_b = group_root / "repo-b"
    (repo_b / "skills").mkdir(parents=True)

    cfg = SkillsConfig(skills_repo=[str(direct_repo)], skills_group=[str(group_root)])
    repos = collect_skill_repos(cfg)
    assert direct_repo in repos
    assert repo_b in repos


def test_scan_skills_detects_standard_and_story_driven(tmp_path: Path):
    repo = tmp_path / "repo"
    standard = repo / "skills" / "web-testing"
    story = repo / "skills" / "use-skill"
    standard.mkdir(parents=True)
    story.mkdir(parents=True)

    (standard / "SKILL.md").write_text(
        "---\nname: web-testing\ndescription: Browser testing helpers\n---\n\n# Web Testing\n",
        encoding="utf-8",
    )
    (story / "skill.json").write_text(
        json.dumps(
            {
                "goal": "Resolve and use skills",
                "acceptance_criteria": ["Loads features from skill.json"],
                "features": [],
            }
        ),
        encoding="utf-8",
    )

    infos = scan_skills([repo])
    by_name = {i.name: i for i in infos}
    assert by_name["web-testing"].format == "standard"
    assert "Browser testing helpers" in by_name["web-testing"].description
    assert by_name["use-skill"].format == "story-driven"
    assert "Resolve and use skills" in by_name["use-skill"].description


def test_scan_skills_story_driven_nested_uses_parent_delimited_name(tmp_path: Path):
    repo = tmp_path / "repo"
    parent = repo / "skills" / "use-skill"
    nested = parent / "find"
    parent.mkdir(parents=True)
    nested.mkdir(parents=True)

    (parent / "skill.json").write_text(
        json.dumps(
            {
                "goal": "Parent skill",
                "acceptance_criteria": ["Parent criteria"],
                "features": [],
            }
        ),
        encoding="utf-8",
    )
    (nested / "skill.json").write_text(
        json.dumps(
            {
                "goal": "Nested resolver",
                "acceptance_criteria": ["Nested criteria"],
                "features": [],
            }
        ),
        encoding="utf-8",
    )

    infos = scan_skills([repo])
    by_name = {i.name: i for i in infos}
    assert "use-skill/find" in by_name
    assert by_name["use-skill/find"].format == "story-driven"

