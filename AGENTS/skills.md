# Skills Resolution Workflow

This project supports two skill formats and resolves both with keyword matching.

## Formats

1. **Standard (Anthropic)**: marker file `SKILL.md`
2. **Story-driven**: marker file `skill.json` (supports nested subskills via `ext.subskill`)

Format detection is automatic:
- `skill.json` present -> story-driven
- else `SKILL.md` present -> standard

## Sources

Skills are discovered from user-level config and env vars.

### User Config

`~/.config/pvrclawk/config.toml`

```toml
skills_repo = ["C:/path/to/my-skills-v2"]
skills_group = ["C:/path/to/skills-root"]
skills_format = []
```

### Environment Overrides

- `MY_SKILLS_REPO` -> appended to `skills_repo`
- `SKILLS_GROUP_DIR` -> appended to `skills_group`

## Commands

```bash
# List all discovered skills across configured repositories
pvrclawk skills list

# Resolve by keyword(s) against folder name + description/goal
pvrclawk skills resolve browser testing
pvrclawk skills resolve memory bank
```

## Matching Rules

- Case-insensitive keyword matching
- Targets:
  - skill folder name
  - skill description (`SKILL.md` frontmatter description or `skill.json` goal)
- Ranking:
  1. exact folder-name match
  2. partial folder-name match
  3. description-only match

## Story-driven `skill.json` contract

Required fields:
- `goal: string`
- `acceptance_criteria: string[]`
- `features: SkillFeature[]`

`SkillFeature` fields:
- `name: string`
- `test_scenario: string`
- `expected_result: string`
- `optional?: bool` (defaults to false)
- `ext?: { subskill?: string, script?: string, skill_md_ref?: string }`

## Agent Guidance

- Prefer `skills resolve <keywords...>` as first step when user intent suggests a reusable workflow.
- If multiple results appear, pick the highest-ranked match and explain why.
- If no matches appear, broaden keywords and retry once.

