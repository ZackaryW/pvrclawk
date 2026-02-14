# Membank Workflow

## Mandatory Order (Do This First)

Before implementation or tests, update the membank plan context first.

```bash
# 1) Review current context
pvrclawk membank focus --tags "task"
pvrclawk membank node list story
pvrclawk membank node list feature
pvrclawk membank node list task

# 2) Add/update story + feature nodes for the incoming task
# 3) Set relevant node status to in_progress
# 4) Cleanup stale/superseded nodes before implementation
#    (remove obsolete progress snapshots and deprecated taxonomy artifacts)
```

Only after this planning update should coding and TDD begin.

### Default Exclusions (Actionable TODO Tracking)

For repository-maintenance work (documentation, policy wording, environment/setup, tooling housekeeping),
exclude actionable TODO tracking by default unless explicitly requested.

- Do not create or advance actionable execution nodes (`story`, `feature`, `task`, `subtask`, `issue`, `bug`) by default.
- `pattern` and `progress` updates are still allowed when they add durable implementation context.
- If unsure whether actionable tracking is requested, ask one clarification question first.

## Core Commands

```bash
# Session lifecycle (context dedup for repeated retrievals)
pvrclawk membank session up
pvrclawk membank session info
pvrclawk membank session reset
pvrclawk membank session tear

# Query context
pvrclawk membank focus --tags "architecture"
pvrclawk membank focus --tags "task"
pvrclawk membank --federated focus --tags "task"

# Inspect nodes
pvrclawk membank node list-all
pvrclawk membank node list story
pvrclawk membank node list feature
pvrclawk membank --federated node list story
pvrclawk membank node get <uid>
pvrclawk membank --federated node get <uid_or_prefix>

# Update status
pvrclawk membank node status <uid> in_progress
pvrclawk membank node status <uid> done
```

## Federation Mode (`--federated`)

Use federated mode for read-time context synthesis across nearby membanks.

- Trigger: `pvrclawk membank --federated <read-command> ...`
- Supported intent: read/query only (`focus`, `node list`, `node list-all`, `node get`, `link list`).
- Write/mutate commands remain local to `--path` even when `--federated` is set.
- Discovery boundary: walk upward to `.git` root (default max 10 levels).
- Safety default: fail if no `.git` boundary is found unless explicitly allowed in config.
- Candidate default: only `.pvrclawk` directories are scanned.

### Federation Scoring Semantics

- **Root importance**: bank closer to repo root gets higher importance.
- **Host relevance**: bank closer to the host bank gets higher relevance.
- Final score composes base rank with federation multipliers from config.

### Federation Config Keys

```bash
# Discovery
pvrclawk membank config set federation.discovery.only_dot_pvrclawk true
pvrclawk membank config set federation.discovery.max_git_lookup_levels 10
pvrclawk membank config set federation.discovery.allow_no_git_boundary false

# Scoring
pvrclawk membank config set federation.scoring.root_importance_base 1.0
pvrclawk membank config set federation.scoring.host_relevance_base 1.0
pvrclawk membank config set federation.scoring.root_distance_decay 0.35
pvrclawk membank config set federation.scoring.host_distance_decay 0.45
```

For list-valued keys such as `federation.discovery.candidate_paths` and
`federation.discovery.external_roots`, edit `.pvrclawk/config.toml` directly as TOML arrays.

### Recommended Federation Workflow

```bash
# 1) Keep local planning updates local-first
pvrclawk membank session up
pvrclawk membank focus --tags "task"

# 2) Expand context only when needed
pvrclawk membank --federated focus --tags "task,architecture" --limit 10
pvrclawk membank --federated node list story --top 20

# 3) Do writes against local host bank only
pvrclawk membank node add task --content "<local actionable item>" --status in_progress
```

## Session Context Dedupe

Use session-aware retrieval to reduce repeated context payload during active agent work.

### Resolution Priority

Commands resolve session context in this order:

1. `--session <uuid>` override on `membank` group
2. `PVRCLAWK_SESSION` environment variable
3. Active session from session index
4. No active session (full content output)

### Behavior

- `pvrclawk membank session up` creates/reuses active session state and prints UUID.
- `focus`, `node list`, and `node list-all` render header-only for already-served nodes in the active session.
- `node get` remains full detail and is never session-truncated.
- `--last N` UID shortcuts are session-scoped (read from active session recent history only).
- `pvrclawk membank session reset` clears served history for re-fetching complete context.
- `pvrclawk membank session tear` clears active session state.
- Session state expires after 2 days and is treated as absent.

## Node Type Boundaries

Use node types with strict intent boundaries:

- `story`: user-facing outcome mapping to developer requirements bridge
- `feature`: user-to-dev requirement slice (testable implementation bridge)
- `bug`: user-reported defect that developers fix
- `issue`: tracked issue item for development/project execution
- `task`: generic actionable work item
- `subtask`: child actionable item of a task
- `progress`: developer-specific implementation progress/log
- `pattern`: code implementation pattern/convention
- `memory` / `memorylink`: developer-generic context that does not fit other types

Keep these boundaries explicit when creating nodes.

## Query Playbook (Everything Must Be Queryable)

```bash
# Planning bridge (user -> dev)
pvrclawk membank node list story --top 20
pvrclawk membank node list feature --top 20

# Execution tracking
pvrclawk membank node list issue --top 20
pvrclawk membank node list bug --top 20
pvrclawk membank node list task --top 20
pvrclawk membank node list subtask --top 20

# Developer context
pvrclawk membank node list progress --top 20
pvrclawk membank node list pattern --top 20
pvrclawk membank node list memory --top 20
pvrclawk membank node list memorylink --top 20
```

## Node Creation

### Story Authoring Standard (Agile User Stories)

- A `story` is an end-user outcome, not a technical requirement or implementation task.
- Use concise, non-technical language centered on user value.
- Recommended shape:
  - `title` (`--title`): persona phrase (the "As a ..." part)
  - `summary` (`--summary`): goal + benefit (the "I want ... so that ..." part)
  - `criteria` (`--criteria`): confirmation checks that define done
- Apply the 3 C's explicitly:
  - Card: concise story statement
  - Conversation: implementation details happen later with the team
  - Confirmation: acceptance criteria are testable and concrete

```bash
# Story
pvrclawk membank node add story \
  --title "As a <persona>" \
  --summary "I want <goal> so that <benefit>" \
  --criteria "<criterion 1>" \
  --criteria "<criterion 2>" \
  --tags "tag1,tag2" \
  --status todo

# Feature
pvrclawk membank node add feature \
  --title "<component>" \
  --summary "<test scenario>" \
  --content "<expected result>" \
  --tags "tag1,tag2" \
  --status todo

# Progress + Task/Subtask
pvrclawk membank node add progress --content "<change summary>" --tags "status,done" --status done
pvrclawk membank node add task --content "<current state>" --tags "task" --status in_progress
pvrclawk membank node add subtask --content "<next granular step>" --tags "subtask" --status todo
```

## Links, Mood, Rules

```bash
# Single link
pvrclawk membank link add <source_uid> <target_uid> --tags "tag1,tag2"

# Chain links (low-IO batch): creates A->B, B->C, C->D
pvrclawk membank link chain <uid_a> <uid_b> <uid_c> <uid_d> --tags "flow,dependency"

# Inspect and tune
pvrclawk membank link list <uid>
pvrclawk membank link weight "tag1,tag2" +0.1
pvrclawk membank report mood <tag> <value>
pvrclawk membank rule add "if tag == tcp then boost 1.5"
```

## Linking Discipline (Required)

- Every new `task`, `subtask`, `bug`, `issue`, `feature`, or `progress` node should be linked to at least one relevant context node (`story`, `pattern`, `memory`, or related execution node).
- Prefer `link chain` when creating multiple sequential links to reduce IO and keep graph updates compact.
- Use UID shorthand only when unambiguous; if a prefix collides, provide a longer prefix or full UID.
- During cleanup, remove stale nodes first, then relink surviving nodes to preserve graph continuity.
- Treat linking as part of the definition of done for membank updates.

## Maintenance

```bash
pvrclawk membank prune
pvrclawk membank config list
pvrclawk membank config get auto_archive_active
pvrclawk membank config set auto_archive_active true
pvrclawk membank session info

# Cleanup workflow (run regularly)
pvrclawk membank node list-all --top 50
pvrclawk membank node list progress --top 50
pvrclawk membank node remove <uid>
pvrclawk membank node remove-type <node_type> --all
pvrclawk membank session tear
```

## Policy

- All context belongs in `.pvrclawk/` (no `memory-bank/` folder).
- Use `pvrclawk` directly for membank workflows in this project.
- For repo-maintenance and documentation/policy/environment tasks, exclude actionable TODO tracking by default unless explicitly requested; `pattern` and `progress` are allowed.
- Do not bulk import markdown; decompose into typed nodes.
- Always update membank first for every new task, then start TDD.
- Add a cleanup pass before implementation: remove stale/superseded entries and deprecated taxonomy artifacts.
- Do not encode status words in `content` (for example: `IN_PROGRESS:`, `DONE:`). Use the `status` field via `node status` or `--status`.
- Prefer local mode for writes and state transitions; use `--federated` for read expansion and ranking.
- In team-managed environments, keep `story` and `feature` lean; they are user-to-dev bridge artifacts and often managed via Jira.
- Use `bug` for user-reported defects; use `issue` for tracked execution issues.
- Use `task`/`subtask` for generic work only (subtask must be a child actionable item).
- Most frequent implementation-side nodes should be `pattern`, `memory`, and `progress`, and they should be linked to relevant work.
- Prefer chain link operations for multi-node flows to reduce storage IO and keep updates atomic per command.
- The membank should coexist as a graph for team/project management and developer context, bridging users and agents.
- Session runtime state is maintained by pvrclawk session storage and should be treated as runtime state (not manual project context).
- Keep TDD strict: failing test -> minimal fix -> refactor -> full tests.
- Do not treat user stories as system requirements; stories capture user intent/value first, while technical requirements are refined during implementation planning.

