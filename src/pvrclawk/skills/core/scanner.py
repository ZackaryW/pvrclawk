"""Discovery and scanning for skill repositories."""

from pathlib import Path

from pvrclawk.skills.core.parsers.standard import parse_standard_skill
from pvrclawk.skills.core.parsers.story_driven import parse_story_driven_skill
from pvrclawk.skills.models.config import SkillsConfig
from pvrclawk.skills.models.skill import SkillInfo


def collect_skill_repos(config: SkillsConfig) -> list[Path]:
    repos: list[Path] = []
    for raw in config.skills_repo:
        candidate = Path(raw)
        if (candidate / "skills").exists():
            repos.append(candidate)

    for raw in config.skills_group:
        group = Path(raw)
        if not group.exists():
            continue
        for child in group.iterdir():
            if child.is_dir() and (child / "skills").exists():
                repos.append(child)

    deduped: list[Path] = []
    seen: set[Path] = set()
    for repo in repos:
        resolved = repo.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped


def scan_skills(repos: list[Path]) -> list[SkillInfo]:
    results: list[SkillInfo] = []
    for repo in repos:
        skills_root = repo / "skills"
        if not skills_root.exists():
            continue
        for folder in skills_root.rglob("*"):
            if not folder.is_dir():
                continue
            standard_file = folder / "SKILL.md"
            story_file = folder / "skill.json"
            if story_file.exists():
                parsed = parse_story_driven_skill(folder)
                results.append(
                    SkillInfo(
                        name=folder.name,
                        path=folder.resolve(),
                        format="story-driven",
                        description=parsed.goal,
                        repo=repo.name,
                    )
                )
            elif standard_file.exists():
                parsed = parse_standard_skill(folder)
                results.append(
                    SkillInfo(
                        name=folder.name,
                        path=folder.resolve(),
                        format="standard",
                        description=parsed.description,
                        repo=repo.name,
                    )
                )
    return results

