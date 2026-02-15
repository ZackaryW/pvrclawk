# Membank (agent instructions)

## Mandatory order

Before implementation or tests:

0. Start with a new session: run `pvrclawk membank session tear` then `pvrclawk membank session up` (unless reusing is specified).
1. Run: `pvrclawk membank focus --tags "task"` (or `pvrclawk membank forctx "#task" --top 20`). If confidence in context for a tag has shifted, run `report mood <tag> <value>`.
2. Add/update story and feature nodes for the incoming task; set relevant node status to `in_progress`. Link new task/feature/progress to at least one story|pattern|memory; prefer `link chain`.
3. Cleanup: remove obsolete progress nodes and deprecated taxonomy artifacts; relink surviving nodes if needed.
4. Then begin coding/TDD.

## Trigger phrases

When user input matches (case-insensitive) any of:

- membank first | update membank first
- consult/check membank | check context
- sync context | load context

→ Execute mandatory order (steps 0–4 above) before implementation or tests.

## Default exclusions

Repository-maintenance work (docs, policy, env, tooling): do not create or advance `story`|`feature`|`task`|`subtask`|`issue`|`bug` unless explicitly requested. `pattern` and `progress` allowed. If unclear, ask once.

## Commands

Membank group options: `--path` (default `.pvrclawk`), `--session <uuid>` (pin session when reusing).

```bash
# Session
pvrclawk membank session up
pvrclawk membank session info
pvrclawk membank session reset
pvrclawk membank session tear

# Context (planning)
pvrclawk membank focus --tags "task" [--limit N]
pvrclawk membank forctx "#tag [phrase]" --top 50
pvrclawk membank last --top 10

# Context (federated read-only)
pvrclawk membank --federated focus --tags "task"
pvrclawk membank --federated node list story --top 20

# Nodes (node get/status/remove accept [--last N] for session-scoped recent UID, N 1–10)
pvrclawk membank node list-all [--top N]
pvrclawk membank node list <type> [--top N]
pvrclawk membank node get <uid> [--last N]
pvrclawk membank node add <type> --content "..." [--title "..." --summary "..." --tags "..." --status todo|in_progress|done|blocked]
pvrclawk membank node status <uid> <status>  # or --last N <status>
pvrclawk membank node remove <uid> [--last N]
pvrclawk membank node remove-type <type> --all   # explicit confirm

# Links
pvrclawk membank link add <source_uid> <target_uid> --tags "..."
pvrclawk membank link chain <uid_a> <uid_b> [<uid_c> ...] --tags "..."
pvrclawk membank link list <uid>
pvrclawk membank link weight "tag1,tag2" +0.1

# Config / maintenance
pvrclawk membank config get <key>
pvrclawk membank config set <key> <value>
pvrclawk membank prune
pvrclawk membank report mood <tag> <value>
pvrclawk membank rule add "<if predicate then action>"
pvrclawk membank rule list
```

## Focus / forctx behavior

- `focus --tags "t1,t2"`: tag-based ranking; default `--limit 5`; use `--limit N` for more nodes. Nodes below `retrieval.resistance_threshold` (default 0.37) excluded. Config: `pvrclawk membank config get/set retrieval.resistance_threshold`.
- `forctx "query"`: `#tag` = tag match, `[phrase]` = content phrase; tags weighted higher. Default `--top 50`.
- `last`: most recently updated nodes; default `--top 10`.

**When to use:** `focus` for tag-based planning (e.g. `--tags "task"`); `forctx` for query with `#tag` and `[phrase]`; `last` for latest-updated nodes.

## Federation (`--federated`)

- Read-only: `focus`, `node list`, `node list-all`, `node get`, `link list`. Writes stay local to `--path`.
- Discovery: walk up to `.git` (max 10 levels); scan `.pvrclawk` dirs; fail if no `.git` unless config allows.
- Scoring: root importance, host relevance, optional `federation.scoring.bank_path_penalties` (regex + multiplier). List keys in `config.toml`: `federation.discovery.candidate_paths`, `external_roots`, `bank_path_penalties`.

## Session

- Default: use a new session for each run (run `session tear` then `session up`) unless the user or context specifies reusing (e.g. `--session`, `PVRCLAWK_SESSION`, or "reuse session").
- Resolution: `--session <uuid>` > `PVRCLAWK_SESSION` > active session index > no session (full output).
- `session up`: create/reuse session. `focus` / `node list` / `node list-all` / `forctx` / `last`: already-served nodes output header-only. `node get` always full. `--last N` UID is session-scoped. `session reset`: clear served; `session tear`: clear session. Expiry: 2 days.

## Report (mood)

Update mood whenever confidence of current context shifts. After running focus, forctx, or last, if your confidence in the relevance or quality of context for a given tag (or area) changes, run `pvrclawk membank report mood <tag> <value>`. Use a numeric value (float); e.g. 0–1 for confidence, or any scale. Values are EMA-smoothed and affect future scoring for that tag. Example: context for tag `task` felt weak → `report mood task 0.3`; after adding nodes and relinking, context feels strong → `report mood task 0.9`.

## Node types

| type      | intent |
|----------|--------|
| story    | user outcome → requirements bridge |
| feature  | requirement slice (testable bridge) |
| bug      | user-reported defect |
| issue    | tracked execution item |
| task     | generic actionable item |
| subtask  | child of task |
| progress | implementation progress log |
| pattern  | implementation pattern/convention |
| memory   | generic context |
| memorylink | file-backed context |

## Node creation (minimal)

- story: `--title "As a <persona>"` `--summary "I want <goal> so that <benefit>"` `--criteria "..."` (repeatable).
- feature: `--title "<component>"` `--summary "<test scenario>"` `--content "<expected result>"`.
- task/subtask/issue/bug: `--content "..."` `--status todo|in_progress|done|blocked`.
- progress: `--content "..."` `--status done`.
- pattern: `--content "..."` `--title "<pattern_type>"`.
- Link every new task/subtask/bug/issue/feature/progress to at least one story|pattern|memory. Prefer `link chain` for A→B→C.

## Policy (rules)

- Context path: `.pvrclawk/` only. Invoke `pvrclawk` for membank.
- Default to new session; reuse only when specified.
- New task → mandatory order first, then TDD.
- No status in `content`; use `node status` or `--status`.
- Writes local; use `--federated` for read expansion only.
- bug = user defect; issue = execution item. task/subtask = generic; subtask is child of task.
- pattern, memory, progress = main implementation nodes; link to work.
- Use `link chain` for multi-node links. Cleanup: remove stale nodes then relink.
- Update report mood whenever confidence of current context shifts (e.g. after focus/forctx/last).
- TDD: failing test → minimal fix → refactor → tests.
- Stories = user intent; technical requirements refined in implementation.
