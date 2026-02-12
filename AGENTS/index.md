# pvrclawk Agent Instructions

> pvrclawk is a CLI context system for AI agents across all project types.
> The command is assumed available in the environment. Setup is user-owned.

## Read Order

1. This file (`AGENTS/index.md`)
2. [`AGENTS/membank.md`](membank.md) for graph memory bank workflows
3. [`AGENTS/skills.md`](skills.md) for dynamic skill resolution workflows

## Trigger Phrases

| Phrase | Action |
|---|---|
| `update membank` | Record completed work as progress, update status, refresh task/subtask context |
| `check context` | Run `pvrclawk membank focus --tags "task"` |
| `what's left` | List story/feature nodes and inspect non-done status |
| `resolve skill` | Run `pvrclawk skills resolve <keywords...>` |
| `list skills` | Run `pvrclawk skills list` |
| `log pattern` | Add a pattern node to membank |

## Session Bootstrap

```bash
pvrclawk membank focus --tags "task"
```

Read returned active context and linked nodes before coding.

## Operating Rules

- Keep tags normalized and consistent.
- Prefer updating existing status over creating duplicate nodes.
- Keep status in the `status` field, not as text prefixes inside `content`.
- Write `story` nodes as user stories (persona + goal + benefit), not technical requirements.
- Prefer `pattern`, `memory`, and `progress` for implementation context; keep `story`/`feature` lean in team-managed workflows.
- Keep node boundaries strict: story/feature (user-dev bridge), bug (user-reported defect), issue/task/subtask (execution), progress/pattern (dev context), memory/memorylink (generic context).
- Link related story/feature/pattern nodes for better context traversal.
- Use `skills resolve` when task intent maps to reusable skills.
- Run tests after changes.

