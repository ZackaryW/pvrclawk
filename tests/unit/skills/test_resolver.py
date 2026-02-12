from pathlib import Path

from pvrclawk.skills.core.resolver import resolve_skills
from pvrclawk.skills.models.skill import SkillInfo


def test_resolve_skills_ranks_name_matches_first():
    skills = [
        SkillInfo(
            name="cleanup-memory-bank",
            path=Path("/tmp/a"),
            format="story-driven",
            description="Cleanup and normalize memory bank documents",
            repo="my-skills-v2",
        ),
        SkillInfo(
            name="memory-maintenance",
            path=Path("/tmp/b"),
            format="standard",
            description="Cleanup memory structures and references",
            repo="anthropic-skills",
        ),
    ]
    matches = resolve_skills(skills, ["cleanup"])
    assert matches[0].name == "cleanup-memory-bank"


def test_resolve_skills_matches_description_when_name_misses():
    skills = [
        SkillInfo(
            name="workflow-helper",
            path=Path("/tmp/c"),
            format="standard",
            description="Automates browser testing and QA flows",
            repo="anthropic-skills",
        )
    ]
    matches = resolve_skills(skills, ["browser"])
    assert len(matches) == 1
    assert matches[0].name == "workflow-helper"

