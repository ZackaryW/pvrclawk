"""User-level config models for skills resolution."""

from pydantic import BaseModel, Field


class SkillsConfig(BaseModel):
    skills_repo: list[str] = Field(default_factory=list)
    skills_group: list[str] = Field(default_factory=list)
    skills_format: list[str] = Field(default_factory=list)

