# pvrclawk Agent Instructions

> All project context is managed by the pvrclawk membank CLI.
> There is no `memory-bank/` folder. Do not create one.

## Bootstrap (every session)

```bash
uv run pvrclawk membank --path .pvrclawk focus --tags "active"
```

This returns the current focus and linked context. Read it before doing anything.

## Understand the project

Query by concern:

```bash
# Architecture and boundaries
uv run pvrclawk membank --path .pvrclawk focus --tags "architecture"

# Scoring and decay rules
uv run pvrclawk membank --path .pvrclawk focus --tags "scoring"

# TDD workflow
uv run pvrclawk membank --path .pvrclawk focus --tags "tdd"

# What's done and what's next
uv run pvrclawk membank --path .pvrclawk focus --tags "status"

# Full architecture spec (memorylink)
uv run pvrclawk membank --path .pvrclawk node list memorylink
# Then read the referenced .md file under .pvrclawk/additional_memory/
```

## Story-driven development

Every work item maps to a **story** (goal-level outcome) linked to **features** (testable slices).

```bash
# List all stories
uv run pvrclawk membank --path .pvrclawk node list story

# List all features
uv run pvrclawk membank --path .pvrclawk node list feature
```

Each feature has:
- **component**: what it covers
- **test_scenario**: the given/when/then
- **expected_result**: acceptance criteria

## TDD protocol (mandatory)

1. Write a failing test for the feature slice
2. Implement the minimum code to pass
3. Refactor
4. Run `uv run pytest` to verify
5. Repeat

No code before a failing test. Unit tests for core logic, integration tests for CLI, e2e for full pipeline.

## After completing work

Update the bank to reflect changes:

```bash
# Record progress
uv run pvrclawk membank --path .pvrclawk node add progress --content "DONE: <what you finished>" --tags "status:1.0,done:1.0"

# Update active context
uv run pvrclawk membank --path .pvrclawk node add active --title "current-focus" --content "<current state and next steps>" --tags "active:1.0"

# If you discovered a new pattern
uv run pvrclawk membank --path .pvrclawk node add pattern --title "<type>" --content "<rule>" --tags "<relevant>:1.0"

# If mood needs adjusting (e.g., user keeps correcting something)
uv run pvrclawk membank --path .pvrclawk report mood <tag> <value>
```

## Rules

- **Do NOT create a `memory-bank/` folder.** All context lives in `.pvrclawk/`.
- **Do NOT bulk-import markdown files.** Decompose plans into story/feature/pattern/progress nodes.
- **Keep tags normalized.** Use lowercase, single-word tags (e.g., `architecture`, `tdd`, `scoring`, `storage`).
- **Link related nodes.** `uv run pvrclawk membank --path .pvrclawk link add <source_uid> <target_uid> --tags "tag1,tag2"`
- **Prune periodically.** `uv run pvrclawk membank --path .pvrclawk prune` after adding many nodes.

## Quick reference

| Command | Purpose |
|---------|---------|
| `membank init` | Initialize `.pvrclawk/` |
| `membank config set/get/list` | Manage `config.toml` |
| `membank node add <type>` | Create a node |
| `membank node list <type>` | List nodes by type |
| `membank link add <src> <tgt>` | Create a link |
| `membank link list <uid>` | List links from a node |
| `membank link weight <tags> <delta>` | Adjust link weights |
| `membank focus --tags "t1,t2"` | Retrieve scored context |
| `membank prune` | Rebalance clusters |
| `membank report mood <tag> <val>` | Update mood |
| `membank rule add "<dsl>"` | Add a scoring rule |
| `membank rule list` | List rules |
