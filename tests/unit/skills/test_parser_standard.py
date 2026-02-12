from pathlib import Path

from pvrclawk.skills.core.parsers.standard import parse_standard_skill


def test_parse_standard_skill(tmp_path: Path):
    skill_dir = tmp_path / "web-testing"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        "name: web-testing\n"
        "description: Test web workflows\n"
        "---\n\n"
        "# Web Testing\n\n"
        "Use this skill for browser automation.\n",
        encoding="utf-8",
    )

    parsed = parse_standard_skill(skill_dir)
    assert parsed.name == "web-testing"
    assert parsed.description == "Test web workflows"
    assert "browser automation" in parsed.body

