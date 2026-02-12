# pvrclawk

> **Experimental** -- this project is built by AI agents, for AI agents. The entire codebase, tests, documentation, and even the project's own context bank were authored through agent-driven development. Treat it as a working prototype, not production software.

A modular Python CLI that gives AI coding agents a graph-based memory bank (`membank`). Instead of flat markdown files that agents dump and re-read wholesale, pvrclawk stores knowledge as typed nodes with weighted links -- so agents can query for scored, relevant context rather than parsing a wall of text.

## Why

Traditional memory-bank approaches (a folder of markdown files) break down when an agent needs to reason about relationships, priority, and staleness. An agent writing to `activeContext.md` has no way to express "this fact is strongly related to that decision" or "this note has decayed in relevance." pvrclawk makes those relationships first-class: nodes have types, links have weights and decay, and queries return ranked results that reflect what actually matters right now.

This tool is designed to be invoked directly by agents via CLI. The agent reads context with `pvrclawk membank focus`, updates status with `pvrclawk membank node status`, and records new knowledge with `pvrclawk membank node add` -- all without needing to parse or generate markdown.

## Install

Requires Python 3.12+. The goal is to make `pvrclawk` available as a command in the agent's environment. How you do that is up to you:

```bash
# Development (uv)
uv sync
uv run pvrclawk --help

# Install globally
pip install .
pvrclawk --help

# Or via pipx, Docker, etc.
```

Once installed, agents interact with it via [`AGENTS/index.md`](AGENTS/index.md) — this instruction folder is the sole protocol an agent needs. It assumes `pvrclawk` is available in the shell.

## Quick start

```bash
# Initialize the bank
pvrclawk membank init

# Add a story with acceptance criteria
pvrclawk membank node add story \
  --title "Auth flow" \
  --summary "Users can log in securely" \
  --criteria "Login form validates email" \
  --criteria "JWT token issued on success" \
  --tags "auth,security"

# Add a feature under that story
pvrclawk membank node add feature \
  --title "JWT issuer" \
  --summary "Given valid credentials, issue a signed JWT" \
  --content "Returns 200 with token in body" \
  --tags "auth,jwt"

# Link them
pvrclawk membank link add <story-uid> <feature-uid> --tags "auth"

# Retrieve context by tags
pvrclawk membank focus --tags "auth"
```

## Concepts

### Node types

| Type | Purpose |
|------|---------|
| `memory` | Free-form text with tags |
| `memorylink` | Reference to a long-form markdown file in `additional_memory/` |
| `story` | Goal-level outcome with role, benefit, and acceptance criteria |
| `feature` | Testable slice with component, scenario, and expected result |
| `active` | Current working context (auto-archives previous on add) |
| `archive` | Archived context |
| `pattern` | Reusable convention or rule |
| `progress` | Status checkpoint |

Stories, features, and progress nodes carry a **status**: `todo` | `in_progress` | `done` | `blocked`.

### Weighted links

Links between nodes carry `tags`, `weight`, `decay`, and `usage_count`. Relevance scoring uses:

```
score = tag_match * link.weight * freq_decay * mood_factor * rule_adjustment
```

where `freq_decay = link.usage_count / total_frequency` (frequency-relative, not time-based).

### Cluster storage

Nodes are stored in named JSON files under `.pvrclawk/nodes/`, grouped by top tags. An `index.json` maps tags and types to node UIDs for fast radiated loading. New nodes land in `_inbox.json` and get merged into clusters on `prune`.

### Mood & rules

- **Mood**: per-tag EMA-smoothed signal. `pvrclawk membank report mood <tag> <value>` adjusts scoring weight.
- **Rules**: DSL-based scoring adjustments. `pvrclawk membank rule add "if tag == tcp then boost 1.5"`

## Command reference

| Command | Purpose |
|---------|---------|
| `membank init` | Initialize `.pvrclawk/` directory |
| `membank node add <type>` | Create a node (`--title`, `--summary`, `--content`, `--tags`, `--status`, `--criteria`) |
| `membank node get <uid>` | View full detail for a node |
| `membank node status <uid> <s>` | Update status |
| `membank node list <type>` | List nodes by type |
| `membank node list-all` | List all nodes |
| `membank link add <src> <tgt>` | Create a weighted link |
| `membank link list <uid>` | List links from a node |
| `membank link weight <tags> <delta>` | Adjust link weights by tag match |
| `membank focus --tags "t1,t2"` | Retrieve scored context |
| `membank prune` | Rebalance clusters (Louvain) |
| `membank report mood <tag> <val>` | Update mood signal |
| `membank rule add "<dsl>"` | Add a scoring rule |
| `membank rule list` | List scoring rules |
| `membank config set/get/list` | Manage `config.toml` settings |

## Configuration

Settings live in `.pvrclawk/config.toml`:

| Key | Default | Description |
|-----|---------|-------------|
| `auto_archive_active` | `true` | Archive existing active nodes when a new one is added |
| `prune.auto_threshold` | `20` | Inbox size that triggers auto-prune |
| `prune.min_cluster` | `3` | Minimum nodes per cluster |
| `decay.base_rate` | `0.95` | Base decay rate |
| `mood.smoothing` | `0.1` | EMA smoothing factor |

## Project structure

```
src/pvrclawk/
  app.py                  # Root Click group
  utils/                  # Universal utilities (json_io, config)
  membank/                # Feature package
    commands/             # CLI commands (node, link, focus, prune, mood, rules, config)
    core/                 # Business logic (storage, graph, mood, rules)
    models/               # Pydantic models (nodes, links, index, types)
```

## Testing

```bash
# All tests
uv run pytest

# By layer
uv run pytest tests/unit/
uv run pytest tests/integration/
```

TDD is mandatory: every feature starts with a failing test.

## For agents

[`AGENTS/index.md`](AGENTS/index.md) is the entry point for AI agents. It links to focused docs for membank and skills workflows, and covers:

- **Trigger phrases** (e.g. "update membank", "check context") and what actions they map to
- Bootstrap protocol (what to run at session start)
- Full command reference with examples
- Tag syntax, node types, story-driven workflow
- Rules for maintaining the bank

Drop the `AGENTS/` folder into any project that uses pvrclawk. The agent reads `index.md`, runs the CLI, and manages context autonomously.

## License

MIT
