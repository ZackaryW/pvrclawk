"""Keyword-based skill matching and ranking."""

from pvrclawk.skills.models.skill import SkillInfo


def _score(skill: SkillInfo, keywords: list[str]) -> int:
    name = skill.name.lower()
    desc = skill.description.lower()
    score = 0
    for kw in keywords:
        token = kw.lower()
        if token == name:
            score += 30
        elif token in name:
            score += 20
        elif token in desc:
            score += 10
    return score


def resolve_skills(skills: list[SkillInfo], keywords: list[str]) -> list[SkillInfo]:
    ranked: list[tuple[int, SkillInfo]] = []
    for skill in skills:
        score = _score(skill, keywords)
        if score > 0:
            ranked.append((score, skill))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked]

