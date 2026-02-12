"""User-level skills config loader."""

import os
import tomllib
from pathlib import Path

from pvrclawk.skills.models.config import SkillsConfig


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _default_config_path() -> Path:
    return Path.home() / ".config" / "pvrclawk" / "config.toml"


def load_skills_config(config_path: Path | None = None) -> SkillsConfig:
    path = config_path or _default_config_path()
    base = SkillsConfig()
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        base = SkillsConfig(
            skills_repo=data.get("skills_repo", []),
            skills_group=data.get("skills_group", []),
            skills_format=data.get("skills_format", []),
        )

    env_repo = os.environ.get("MY_SKILLS_REPO")
    env_group = os.environ.get("SKILLS_GROUP_DIR")

    repos = list(base.skills_repo)
    groups = list(base.skills_group)
    if env_repo:
        repos.append(env_repo)
    if env_group:
        groups.append(env_group)

    return SkillsConfig(
        skills_repo=_dedupe(repos),
        skills_group=_dedupe(groups),
        skills_format=list(base.skills_format),
    )

