"""Skill models for multiple formats."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class SkillInfo(BaseModel):
    name: str
    path: Path
    format: Literal["standard", "story-driven"]
    description: str
    repo: str


class StandardSkill(BaseModel):
    name: str
    description: str
    body: str


class FeatureExt(BaseModel):
    subskill: str | None = None
    script: str | None = None
    skill_md_ref: str | None = None


class SkillFeature(BaseModel):
    name: str
    test_scenario: str
    expected_result: str
    optional: bool = False
    ext: FeatureExt | None = None


class StoryDrivenSkill(BaseModel):
    goal: str
    acceptance_criteria: list[str]
    features: list[SkillFeature]

