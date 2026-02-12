# Membank Workflow

## Mandatory Order (Do This First)

Before implementation or tests, update the membank plan context first.

```bash
# 1) Review current context
pvrclawk membank focus --tags "active"
pvrclawk membank node list story
pvrclawk membank node list feature

# 2) Add/update story + feature nodes for the incoming task
# 3) Set relevant node status to in_progress
```

Only after this planning update should coding and TDD begin.

## Core Commands

```bash
# Query context
pvrclawk membank focus --tags "architecture"
pvrclawk membank focus --tags "active"

# Inspect nodes
pvrclawk membank node list-all
pvrclawk membank node list story
pvrclawk membank node list feature
pvrclawk membank node get <uid>

# Update status
pvrclawk membank node status <uid> in_progress
pvrclawk membank node status <uid> done
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

# Progress + Active
pvrclawk membank node add progress --content "DONE: <change>" --tags "status,done" --status done
pvrclawk membank node add active --title "current-focus" --content "<current state>" --tags "active"
```

## Links, Mood, Rules

```bash
pvrclawk membank link add <source_uid> <target_uid> --tags "tag1,tag2"
pvrclawk membank link list <uid>
pvrclawk membank link weight "tag1,tag2" +0.1
pvrclawk membank report mood <tag> <value>
pvrclawk membank rule add "if tag == tcp then boost 1.5"
```

## Maintenance

```bash
pvrclawk membank prune
pvrclawk membank config list
pvrclawk membank config get auto_archive_active
pvrclawk membank config set auto_archive_active true
```

## Policy

- All context belongs in `.pvrclawk/` (no `memory-bank/` folder).
- Do not bulk import markdown; decompose into typed nodes.
- Always update membank first for every new task, then start TDD.
- Keep TDD strict: failing test -> minimal fix -> refactor -> full tests.

