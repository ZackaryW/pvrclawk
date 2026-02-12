# pvrclawk Architecture Reference

## CLI Structure

```
pvrclawk (root Click group)
  membank (feature group, --path option)
    init          Initialize .pvrclawk directory
    config        set / get / list settings in config.toml
    node          add / list nodes (8 types)
    link          add / list / weight links between nodes
    focus         Context retrieval with tag-based scoring
    prune         Rebalance inbox into named clusters
    report mood   Update per-tag mood with EMA smoothing
    rule          add / list DSL rules
```

## Models (Pydantic)

### Nodes
- **BaseNode**: uid, tags (dict str->float), created_at, updated_at
  - **Memory**: title, summary, content
  - **MemoryLink**: title, summary, file_path (slug under additional_memory/)
  - **Story**: role (title/goal), benefit (value delivered), criteria, status
  - **Feature**: component, test_scenario (given/when/then), expected_result, status
  - **Active**: content, focus_area
  - **Archive**: content, archived_from, reason
  - **Pattern**: content, pattern_type
  - **Progress**: content, status

### Links
- **Link**: uid, source, target, tags (list[str]), weight, decay, usage_count, created_at, last_accessed

## Storage Layout (.pvrclawk/)

```
config.toml              Prune/decay/mood settings
index.json               tags->uids, types->uids, uid_file, links_in, clusters
links.json               All link objects keyed by source uid
mood.json                Per-tag mood scores (EMA smoothed)
rules.json               DSL rules list
nodes/                   Cluster JSON files
  _inbox.json            Landing zone for new nodes
  {cluster_name}.json    Named clusters derived from top tags
additional_memory/       Markdown files for memorylink nodes
```

## Index Structure (index.json)

```json
{
  "tags":     { "tag_name": ["uid1", "uid2"] },
  "types":    { "story": ["uid1"], "feature": ["uid2"] },
  "uid_file": { "uid1": "cluster_name" },
  "links_in": { "target_uid": ["source_uid"] },
  "clusters": { "cluster_name": { "top_tags": ["t1","t2"], "size": 5 } }
}
```

## Scoring Formula

```
relevance(node) = sum over incoming links:
  tag_match(link.tags, query_tags)
    * link.weight
    * freq_decay
    * mood_factor
    * rule_adjustment

freq_decay = link.usage_count / total_frequency
```

- **tag_match**: 1.0 if any link tag matches query, else 0.0
- **weight**: base weight, adjustable via `link weight <tags> <delta>` or mood/rules
- **freq_decay**: frequency-relative, NOT wall-clock. Higher usage = higher decay value
- **mood_factor**: per-tag EMA value from mood.json
- **rule_adjustment**: multiplier from DSL rule engine evaluation

## Graph Engine

- Uses NetworkX undirected graph
- VectorScorer computes per-link relevance
- GraphEngine.retrieve() scores all links, ranks targets, expands 1-hop neighbors at 0.5x score
- Focus command returns top-N ranked nodes

## Mood System

- `report mood <tag> <value>`: updates mood.json
- EMA smoothing: `new = alpha * reported + (1 - alpha) * old`
- Default alpha from config.toml `[mood] smoothing`
- Mood factor feeds into scoring formula

## DSL Rule Engine

- Rules stored in rules.json as strings
- Format: `if <predicate> then <action>`
- Predicate: `tag <op> <value>` where op is `==`, `>`, `<`
- Action: `boost <factor>` or `suppress <factor>`
- RuleEngine.evaluate_multiplier() returns cumulative multiplier for scoring

## Technology Stack

- Python 3.12+
- Click (CLI framework)
- Pydantic (data validation, model serialization)
- NetworkX (graph operations, Louvain community detection for prune)
- Rich (display formatting)
- pytest (testing)
- uv (package management)

## Development Patterns

- **TDD**: Red-green-refactor for every slice. No code before failing test.
- **Boundary**: All membank code under src/pvrclawk/membank/. Root app.py is registration-only.
- **Storage**: New nodes land in _inbox.json. Prune moves them to named clusters.
- **Modularity**: Feature groups register as Click subcommands. Future groups (utils, etc.) follow same pattern.
