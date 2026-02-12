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

## Core Commands

```bash
# Query context
pvrclawk membank focus --tags "architecture"
pvrclawk membank focus --tags "task"

# Inspect nodes
pvrclawk membank node list-all
pvrclawk membank node list story
pvrclawk membank node list feature
pvrclawk membank node get <uid>

# Update status
pvrclawk membank node status <uid> in_progress
pvrclawk membank node status <uid> done
```

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

```bash
# Story
pvrclawk membank node add story \
  --title "<role>" \
  --summary "<benefit>" \
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

# Cleanup workflow (run regularly)
pvrclawk membank node list-all --top 50
pvrclawk membank node list progress --top 50
pvrclawk membank node remove <uid>
pvrclawk membank node remove-type <node_type> --all
```

## Policy

- All context belongs in `.pvrclawk/` (no `memory-bank/` folder).
- Do not bulk import markdown; decompose into typed nodes.
- Always update membank first for every new task, then start TDD.
- Add a cleanup pass before implementation: remove stale/superseded entries and deprecated taxonomy artifacts.
- Do not encode status words in `content` (for example: `IN_PROGRESS:`, `DONE:`). Use the `status` field via `node status` or `--status`.
- In team-managed environments, keep `story` and `feature` lean; they are user-to-dev bridge artifacts and often managed via Jira.
- Use `bug` for user-reported defects; use `issue` for tracked execution issues.
- Use `task`/`subtask` for generic work only (subtask must be a child actionable item).
- Most frequent implementation-side nodes should be `pattern`, `memory`, and `progress`, and they should be linked to relevant work.
- Prefer chain link operations for multi-node flows to reduce storage IO and keep updates atomic per command.
- The membank should coexist as a graph for team/project management and developer context, bridging users and agents.
- Keep TDD strict: failing test -> minimal fix -> refactor -> full tests.

