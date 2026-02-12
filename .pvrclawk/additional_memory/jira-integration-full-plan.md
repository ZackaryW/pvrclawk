# Jira Integration Full Implementation Plan

## Goal

Add a new `jira` command group to `pvrclawk` so agents and users can:

1. Read Jira issues and search results from Jira Cloud.
2. Optionally create/update issues.
3. Map Jira issues to membank nodes for workflow traceability.

This plan prioritizes safe, testable incremental delivery with strict TDD.

---

## Scope and Phasing

### Phase 1 (MVP, read-focused)

- `pvrclawk jira search "<jql>"`
- `pvrclawk jira issue <ISSUE_KEY>`
- `pvrclawk jira my-open`
- Config + auth via env and user-level config.
- Human and machine-readable outputs.

### Phase 2 (write actions)

- `pvrclawk jira create`
- `pvrclawk jira transition`
- `pvrclawk jira comment`

### Phase 3 (membank linkage + sync helpers)

- `pvrclawk jira link-node <node_uid> <issue_key>`
- `pvrclawk jira links [--node <uid>] [--issue <key>]`
- Optional status sync suggestions (not automatic mutation by default).

---

## Architecture

Add a new feature package mirroring existing style:

```text
src/pvrclawk/jira/
  __init__.py
  commands/
    __init__.py
    search.py
    issue.py
    my_open.py
    create.py              # phase 2
    transition.py          # phase 2
    comment.py             # phase 2
    link_node.py           # phase 3
    links.py               # phase 3
  core/
    __init__.py
    auth.py
    client.py
    formatter.py
    mappings.py
  models/
    __init__.py
    config.py
    issue.py
    search.py
```

Register in `src/pvrclawk/app.py`:

```python
from pvrclawk.jira import jira_group
main.add_command(jira_group, name="jira")
```

---

## Configuration and Auth

Use both env vars and user-level config (`~/.config/pvrclawk/config.toml`).

### Environment variables

- `JIRA_BASE_URL` (for example `https://your-domain.atlassian.net`)
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

### User config keys

```toml
[jira]
base_url = "https://your-domain.atlassian.net"
email = "user@example.com"
api_token = ""
default_project = "PROJ"
default_jql = "assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC"
timeout_seconds = 20
```

Resolution order:
1. CLI options (if supplied)
2. Env vars
3. `~/.config/pvrclawk/config.toml`

Secrets rules:
- Never print tokens.
- Redact auth in errors/logs.
- Fail with explicit remediation steps.

---

## Command Contracts

### `jira search`

```bash
pvrclawk jira search "project = PROJ ORDER BY updated DESC"
```

Options:
- `--limit N` (default 20)
- `--human` table output
- `--json` raw machine output

Behavior:
- Executes JQL via `/rest/api/3/search`.
- Returns issue key, summary, status, assignee, updated.

### `jira issue`

```bash
pvrclawk jira issue PROJ-123
```

Options:
- `--human`
- `--json`

Behavior:
- Fetches issue via `/rest/api/3/issue/{key}`.
- Includes description and key fields.

### `jira my-open`

```bash
pvrclawk jira my-open
```

Behavior:
- Equivalent to search with default JQL for current user unresolved.

### Phase 2 write contracts

- `jira create --project PROJ --type Story --summary "..." --description "..."`
- `jira transition PROJ-123 --to "In Progress"`
- `jira comment PROJ-123 --text "..."`

### Phase 3 membank mapping contracts

- `jira link-node <node_uid> <issue_key>`
- `jira links --node <uid>`
- `jira links --issue <key>`

Storage file:
- `.pvrclawk/jira_links.json`

Schema:

```json
{
  "by_node": {
    "<node_uid>": ["PROJ-123"]
  },
  "by_issue": {
    "PROJ-123": ["<node_uid>"]
  }
}
```

---

## Error Handling

Normalize errors into user-friendly messages:

- `401/403`: auth failure; tell user to check token/email/base URL.
- `404`: issue not found or URL mismatch.
- `429`: rate limited; suggest retry/backoff.
- network timeout: suggest connectivity check and `timeout_seconds` tuning.

For `--json`, return structured error payload with `code`, `message`, `hint`.

---

## Output Design

Default output should be concise and copy-friendly.

`--human`:
- table-like view for search and my-open.

`--json`:
- deterministic field names.
- no ANSI/control characters.

---

## TDD Plan (Detailed)

### Slice A: config + auth

Tests:
- load config from env/config precedence.
- missing required auth fields yields actionable error.

Code:
- `models/config.py`
- `core/auth.py`

### Slice B: client primitives

Tests:
- request builder creates correct URL/path.
- auth header uses basic auth email:token.
- timeout applied.
- response parse for success/error branches.

Code:
- `core/client.py`

### Slice C: read commands

Tests:
- integration tests for:
  - `jira search`
  - `jira issue`
  - `jira my-open`
- unit tests for formatting (`--human` and `--json`).

Code:
- command modules + formatter.

### Slice D: write commands

Tests:
- transition lookup + transition post.
- create payload correctness.
- comment payload correctness.

Code:
- phase 2 command modules.

### Slice E: membank links

Tests:
- add mapping updates both indexes.
- idempotent add.
- list by node and by issue.

Code:
- `core/mappings.py`, command modules.

### Slice F: docs and examples

Tests:
- CLI help smoke checks.

Docs:
- `AGENTS/skills.md` references if needed.
- README command reference extension.

---

## Dependencies

Preferred:
- Python stdlib `urllib` for HTTP to keep deps minimal.

Optional (if ergonomics preferred):
- `httpx` for timeout/retry ergonomics.

Recommendation:
- Start with stdlib for MVP; add `httpx` only if retries/streaming complexity rises.

---

## Security and Privacy Notes

- Never persist Jira API token in project repo.
- User-level config is allowed but token should prefer env variable.
- Avoid logging full Jira payloads in normal mode.
- In JSON mode, include only requested/necessary fields.

---

## Definition of Done

Phase 1 done when:
- `jira search`, `jira issue`, `jira my-open` fully tested.
- Auth/config precedence tested.
- Clear errors for auth/network/rate-limit.
- README + AGENTS docs updated.

Phase 2 done when write actions tested end-to-end with mocked API.

Phase 3 done when node-issue mapping is persisted and queryable.

---

## Suggested First Sprint

1. Implement config/auth/client + tests.
2. Implement `jira search` + tests.
3. Implement `jira issue` + tests.
4. Implement `jira my-open` + tests.
5. Ship MVP and gather usage feedback before write actions.

