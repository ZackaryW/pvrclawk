"""Parser for standard (Anthropic) SKILL.md format."""

from pathlib import Path

from pvrclawk.skills.models.skill import StandardSkill


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        raise ValueError("SKILL.md missing YAML frontmatter")
    end_marker = "\n---\n"
    end_idx = content.find(end_marker, 4)
    if end_idx == -1:
        raise ValueError("SKILL.md frontmatter is not closed")

    frontmatter_raw = content[4:end_idx]
    body = content[end_idx + len(end_marker) :]
    data: dict[str, str] = {}
    for line in frontmatter_raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def parse_standard_skill(skill_dir: Path) -> StandardSkill:
    skill_file = skill_dir / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    return StandardSkill(
        name=frontmatter.get("name", skill_dir.name),
        description=frontmatter.get("description", ""),
        body=body,
    )

