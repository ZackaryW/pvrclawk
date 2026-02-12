"""Parser for story-driven skill.json format."""

import json
from pathlib import Path

from pvrclawk.skills.models.skill import StoryDrivenSkill


def parse_story_driven_skill(skill_dir: Path) -> StoryDrivenSkill:
    skill_json = skill_dir / "skill.json"
    payload = json.loads(skill_json.read_text(encoding="utf-8"))
    return StoryDrivenSkill(**payload)


def read_optional_skill_markdown(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "skill.md"
    if not skill_md.exists():
        return None
    return skill_md.read_text(encoding="utf-8")

