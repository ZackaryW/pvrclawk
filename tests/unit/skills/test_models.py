from pathlib import Path

from pvrclawk.skills.models.config import SkillsConfig
from pvrclawk.skills.models.skill import FeatureExt, SkillFeature, SkillInfo, StandardSkill, StoryDrivenSkill


def test_skill_info_model():
    info = SkillInfo(
        name="cleanup-memory-bank",
        path=Path("/tmp/skills/cleanup-memory-bank"),
        format="story-driven",
        description="Cleanup memory bank docs",
        repo="my-skills-v2",
    )
    assert info.name == "cleanup-memory-bank"
    assert info.format == "story-driven"


def test_standard_skill_model():
    skill = StandardSkill(
        name="web-testing",
        description="Run web testing flows",
        body="# Web Testing\n\nDo steps.",
    )
    assert skill.name == "web-testing"
    assert "Web Testing" in skill.body


def test_story_driven_skill_model():
    feature = SkillFeature(
        name="resolve",
        test_scenario="Given keyword, when resolve, then match by name",
        expected_result="Returns ranked skills",
        optional=False,
        ext=FeatureExt(subskill="find"),
    )
    skill = StoryDrivenSkill(
        goal="Resolve skills from repositories",
        acceptance_criteria=["Supports nested story-driven skills"],
        features=[feature],
    )
    assert skill.goal.startswith("Resolve")
    assert skill.features[0].ext is not None
    assert skill.features[0].ext.subskill == "find"


def test_skills_config_defaults():
    config = SkillsConfig()
    assert config.skills_repo == []
    assert config.skills_group == []
    assert config.skills_format == []
