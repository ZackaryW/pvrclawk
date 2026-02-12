"""Shared node rendering for CLI output."""

from pvrclawk.membank.models.nodes import (
    Active,
    Archive,
    Feature,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
)


def render_node(node, score: float | None = None) -> str:
    tag_str = ",".join(node.tags.keys()) if node.tags else ""
    ntype = node.__class__.__name__
    if score is not None:
        header = f"[{score:.3f}] ({ntype}) {tag_str}"
    else:
        header = f"({ntype}) [{node.uid[:8]}] {tag_str}"

    if isinstance(node, Memory):
        return f"{header}\n  {node.content}"
    if isinstance(node, MemoryLink):
        return f"{header}\n  {node.title}: {node.summary}\n  -> {node.file_path}"
    if isinstance(node, Story):
        status = f" [{node.status.value}]" if hasattr(node, "status") else ""
        crit = ""
        if node.criteria:
            crit = "\n" + "\n".join(f"  - {c}" for c in node.criteria)
        return f"{header}{status}\n  {node.role}: {node.benefit}{crit}"
    if isinstance(node, Feature):
        status = f" [{node.status.value}]" if hasattr(node, "status") else ""
        return f"{header}{status}\n  {node.component}: {node.test_scenario}\n  expect: {node.expected_result}"
    if isinstance(node, Active):
        area = f" [{node.focus_area}]" if node.focus_area else ""
        return f"{header}{area}\n  {node.content}"
    if isinstance(node, Archive):
        return f"{header}\n  {node.content}"
    if isinstance(node, Pattern):
        ptype = f" [{node.pattern_type}]" if node.pattern_type else ""
        return f"{header}{ptype}\n  {node.content}"
    if isinstance(node, Progress):
        status = f" [{node.status.value}]" if hasattr(node, "status") else ""
        return f"{header}{status}\n  {node.content}"
    return f"{header}\n  {node.uid}"


def render_node_detail(node) -> str:
    """Full detail view for node get."""
    lines = [f"uid: {node.uid}"]
    lines.append(f"type: {node.__class__.__name__}")
    lines.append(f"tags: {', '.join(f'{k}:{v}' for k, v in node.tags.items())}")

    if isinstance(node, Memory):
        lines.append(f"content: {node.content}")
    elif isinstance(node, MemoryLink):
        lines.append(f"title: {node.title}")
        lines.append(f"summary: {node.summary}")
        lines.append(f"file: {node.file_path}")
    elif isinstance(node, Story):
        lines.append(f"role: {node.role}")
        lines.append(f"benefit: {node.benefit}")
        if node.criteria:
            lines.append("criteria:")
            for c in node.criteria:
                lines.append(f"  - {c}")
        lines.append(f"status: {node.status.value}")
    elif isinstance(node, Feature):
        lines.append(f"component: {node.component}")
        lines.append(f"scenario: {node.test_scenario}")
        lines.append(f"expected: {node.expected_result}")
        lines.append(f"status: {node.status.value}")
    elif isinstance(node, Active):
        lines.append(f"focus_area: {node.focus_area}")
        lines.append(f"content: {node.content}")
    elif isinstance(node, Archive):
        lines.append(f"archived_from: {node.archived_from}")
        lines.append(f"reason: {node.reason}")
        lines.append(f"content: {node.content}")
    elif isinstance(node, Pattern):
        lines.append(f"pattern_type: {node.pattern_type}")
        lines.append(f"content: {node.content}")
    elif isinstance(node, Progress):
        lines.append(f"content: {node.content}")
        lines.append(f"status: {node.status.value}")

    return "\n".join(lines)
