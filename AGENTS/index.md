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
| `update membank` | Record completed work as progress, update status, refresh active |
| `check context` | Run `pvrclawk membank focus --tags "active"` |
| `what's left` | List story/feature nodes and inspect non-done status |
| `resolve skill` | Run `pvrclawk skills resolve <keywords...>` |
| `list skills` | Run `pvrclawk skills list` |
| `log pattern` | Add a pattern node to membank |

## Session Bootstrap

```bash
pvrclawk membank focus --tags "active"
```

Read returned active context and linked nodes before coding.

## Operating Rules

- Keep tags normalized and consistent.
- Prefer updating existing status over creating duplicate nodes.
- Keep status in the `status` field, not as text prefixes inside `content`.
- Link related story/feature/pattern nodes for better context traversal.
- Use `skills resolve` when task intent maps to reusable skills.
- Run tests after changes.

