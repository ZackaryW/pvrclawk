"""Score nodes by tag and content phrase occurrence (tags weighted higher)."""

from pvrclawk.membank.models.base import BaseNode
from pvrclawk.membank.models.nodes import (
    Bug,
    Feature,
    Issue,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
    SubTask,
    Task,
)

TAG_WEIGHT = 2.0
CONTENT_WEIGHT = 1.0


def node_to_searchable_text(node: BaseNode) -> str:
    """Concatenate all searchable text fields of a node for content matching."""
    parts: list[str] = [node.uid]
    if isinstance(node, Memory):
        parts.append(node.content)
    elif isinstance(node, MemoryLink):
        parts.extend([node.title, node.summary, node.file_path])
    elif isinstance(node, Story):
        parts.extend([node.role, node.benefit] + node.criteria)
        if hasattr(node, "status"):
            parts.append(node.status.value)
    elif isinstance(node, Feature):
        parts.extend([node.component, node.test_scenario, node.expected_result])
        if hasattr(node, "status"):
            parts.append(node.status.value)
    elif isinstance(node, (Task, SubTask, Issue, Bug)):
        parts.append(node.content)
        if hasattr(node, "status"):
            parts.append(node.status.value)
    elif isinstance(node, Pattern):
        parts.extend([node.pattern_type, node.content])
    elif isinstance(node, Progress):
        parts.append(node.content)
        if hasattr(node, "status"):
            parts.append(node.status.value)
    return " ".join(str(p) for p in parts if p)


def score_nodes_forctx(
    nodes: list[BaseNode],
    tag_tokens: list[str],
    content_phrases: list[str],
    tag_weight: float = TAG_WEIGHT,
    content_weight: float = CONTENT_WEIGHT,
    top: int = 50,
) -> list[tuple[str, float]]:
    """Score nodes by tag and content occurrence; return (uid, score) sorted desc, limited to top."""
    tag_set = set(tag_tokens)
    scored: list[tuple[str, float]] = []

    for node in nodes:
        score = 0.0
        node_tags = set(node.tags.keys()) if node.tags else set()
        tag_matches = len(tag_set & node_tags)
        if tag_matches > 0:
            score += tag_matches * tag_weight

        if content_phrases:
            text = node_to_searchable_text(node).lower()
            for phrase in content_phrases:
                if phrase.lower() in text:
                    score += content_weight

        if score > 0:
            scored.append((node.uid, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top]
