# pvrclawk Agent Instructions

> All project context is managed by the pvrclawk membank CLI.
> There is no `memory-bank/` folder. Do not create one.

## Installation

How `pvrclawk` is invoked depends on the install method. Examples:

| Method | Invocation |
|--------|------------|
| `uv run` (dev) | `pvrclawk …` |
| `pip install .` | `pvrclawk …` |
| `pipx install .` | `pvrclawk …` |
| Docker | `docker run pvrclawk …` |

All examples below use the bare `pvrclawk` command. Prefix with your environment's runner as needed.

## Bootstrap (every session)

```bash
pvrclawk membank --path .pvrclawk focus --tags "active"
```

This returns the current focus and linked context. Read it before doing anything.

## Understand the project

Query by concern:

```bash
# Architecture and boundaries
pvrclawk membank --path .pvrclawk focus --tags "architecture"

# Scoring and decay rules
pvrclawk membank --path .pvrclawk focus --tags "scoring"

# TDD workflow
pvrclawk membank --path .pvrclawk focus --tags "tdd"

# What's done and what's next
pvrclawk membank --path .pvrclawk focus --tags "status"

# Full architecture spec (memorylink)
pvrclawk membank --path .pvrclawk node list memorylink
# Then read the referenced .md file under .pvrclawk/additional_memory/
```

## Inventory commands

Use these to see everything at a glance or drill into specifics:

```bash
# List ALL nodes across all types
pvrclawk membank --path .pvrclawk node list-all

# List nodes by type
pvrclawk membank --path .pvrclawk node list story
pvrclawk membank --path .pvrclawk node list feature
pvrclawk membank --path .pvrclawk node list pattern
pvrclawk membank --path .pvrclawk node list progress
pvrclawk membank --path .pvrclawk node list active
pvrclawk membank --path .pvrclawk node list memory
pvrclawk membank --path .pvrclawk node list memorylink
pvrclawk membank --path .pvrclawk node list archive

# View full detail for a single node
pvrclawk membank --path .pvrclawk node get <uid>

# List links from a specific node
pvrclawk membank --path .pvrclawk link list <uid>
```

## Status tracking

Stories, features, and progress nodes have a `status` field (todo | in_progress | done | blocked).

```bash
# Check a node's current status
pvrclawk membank --path .pvrclawk node get <uid>

# Update status
pvrclawk membank --path .pvrclawk node status <uid> done
pvrclawk membank --path .pvrclawk node status <uid> in_progress
pvrclawk membank --path .pvrclawk node status <uid> blocked
pvrclawk membank --path .pvrclawk node status <uid> todo
```

## Query (focus)

Focus retrieves and ranks nodes by tag relevance. Nodes are scored by direct tag match + link-based scoring, then expanded to 1-hop neighbors.

```bash
# Retrieve context by tags (returns scored, ranked results)
pvrclawk membank --path .pvrclawk focus --tags "architecture" --limit 10

# Multi-tag query
pvrclawk membank --path .pvrclawk focus --tags "scoring,decay"
```

## Story-driven development

Every work item maps to a **story** (goal-level outcome) linked to **features** (testable slices).

```bash
# List all stories with status
pvrclawk membank --path .pvrclawk node list story

# List all features with status
pvrclawk membank --path .pvrclawk node list feature
```

Each feature has:
- **component**: what it covers
- **test_scenario**: the given/when/then
- **expected_result**: acceptance criteria

## TDD protocol (mandatory)

1. Write a failing test for the feature slice
2. Implement the minimum code to pass
3. Refactor
4. Run tests to verify (e.g. `pytest`, `uv run pytest`)
5. Repeat

No code before a failing test. Unit tests for core logic, integration tests for CLI, e2e for full pipeline.

## After completing work

Update the bank to reflect changes:

```bash
# Mark a feature/story as done
pvrclawk membank --path .pvrclawk node status <uid> done

# Record progress
pvrclawk membank --path .pvrclawk node add progress --content "DONE: <what you finished>" --tags "status:1.0,done:1.0"

# Update active context
pvrclawk membank --path .pvrclawk node add active --title "current-focus" --content "<current state and next steps>" --tags "active:1.0"

# If you discovered a new pattern
pvrclawk membank --path .pvrclawk node add pattern --title "<type>" --content "<rule>" --tags "<relevant>:1.0"

# If mood needs adjusting (e.g., user keeps correcting something)
pvrclawk membank --path .pvrclawk report mood <tag> <value>

# Add a scoring rule
pvrclawk membank --path .pvrclawk rule add "if tag == tcp then boost 1.5"
```

## Configuration

Settings live in `.pvrclawk/config.toml`. Key settings:

```bash
# Toggle auto-archive of active nodes (default: true)
pvrclawk membank --path .pvrclawk config set auto_archive_active true

# Prune inbox threshold
pvrclawk membank --path .pvrclawk config set prune.auto_threshold 20

# Mood smoothing factor
pvrclawk membank --path .pvrclawk config set mood.smoothing 0.1
```

When `auto_archive_active = true`, adding a new active node automatically converts existing active nodes to archive type. Set to `false` to keep multiple active nodes.

## Architecture notes

- **`src/pvrclawk/utils/`**: Universal utilities shared across all feature packages
  - `json_io.py`: `read_json(path, default)`, `write_json(path, data)`
  - `config.py`: `AppConfig` model, `load_config`, `write_config`, `set_config_value`
- **`src/pvrclawk/membank/`**: Feature package for membank. Re-exports utils for backwards compat.
- **`AGENTS.md`**: This file. Root-level instructions for agents.

## Rules

- **Do NOT create a `memory-bank/` folder.** All context lives in `.pvrclawk/`.
- **Do NOT bulk-import markdown files.** Decompose plans into story/feature/pattern/progress nodes.
- **Keep tags normalized.** Use lowercase, single-word tags (e.g., `architecture`, `tdd`, `scoring`, `storage`).
- **Link related nodes.** `pvrclawk membank --path .pvrclawk link add <source_uid> <target_uid> --tags "tag1,tag2"`
- **Prune periodically.** `pvrclawk membank --path .pvrclawk prune` after adding many nodes.
- **MemoryLink no-overwrite.** If a file already exists in `additional_memory/`, linking to it won't overwrite the content.
- **Active auto-archive.** Adding a new active node archives old ones (configurable via `auto_archive_active`).

## Full command reference

| Command | Purpose |
|---------|---------|
| `membank init` | Initialize `.pvrclawk/` directory |
| `membank config set <key> <val>` | Set a config value (supports `section.field` and top-level keys) |
| `membank config get <key>` | Get a config value |
| `membank config list` | List all config values |
| `membank node add <type> [--status]` | Create a node (8 types, optional initial status) |
| `membank node get <uid>` | View full detail for a node |
| `membank node status <uid> <status>` | Update status (todo/in_progress/done/blocked) |
| `membank node list <type>` | List nodes by type with rendered output |
| `membank node list-all` | List all nodes across all types |
| `membank link add <src> <tgt>` | Create a link between nodes |
| `membank link list <uid>` | List links from a node |
| `membank link weight <tags> <delta>` | Adjust link weights by tag match |
| `membank focus --tags "t1,t2"` | Retrieve scored context by tags (zero-score filtered) |
| `membank prune` | Rebalance inbox into named clusters (rebuilds index + links_in) |
| `membank report mood <tag> <val>` | Update per-tag mood (EMA smoothed) |
| `membank rule add "<dsl>"` | Add a DSL scoring rule |
| `membank rule list` | List all scoring rules |
