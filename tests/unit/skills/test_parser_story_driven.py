import json
from pathlib import Path

from pvrclawk.skills.core.parsers.story_driven import parse_story_driven_skill, read_optional_skill_markdown


def test_parse_story_driven_skill(tmp_path: Path):
    skill_dir = tmp_path / "use-skill"
    skill_dir.mkdir(parents=True)
    skill_json = {
        "goal": "Resolve and execute skills",
        "acceptance_criteria": ["Supports subskill delegation"],
        "features": [
            {
                "name": "resolve",
                "test_scenario": "Given keyword, when resolve, then chooses matching skill",
                "expected_result": "Returns best matched skill",
                "ext": {"subskill": "find"},
            }
        ],
    }
    (skill_dir / "skill.json").write_text(json.dumps(skill_json), encoding="utf-8")

    parsed = parse_story_driven_skill(skill_dir)
    assert parsed.goal == "Resolve and execute skills"
    assert parsed.features[0].ext is not None
    assert parsed.features[0].ext.subskill == "find"


def test_read_optional_skill_markdown(tmp_path: Path):
    skill_dir = tmp_path / "use-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text("# extra docs", encoding="utf-8")
    assert read_optional_skill_markdown(skill_dir) == "# extra docs"

