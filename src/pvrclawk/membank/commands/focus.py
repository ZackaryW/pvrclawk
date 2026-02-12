from pathlib import Path

import click

from pvrclawk.membank.core.graph.engine import GraphEngine
from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.config import AppConfig
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


def _render_node(node, score: float) -> str:
    tag_str = ",".join(node.tags.keys()) if node.tags else ""
    header = f"[{score:.3f}] ({node.__class__.__name__}) {tag_str}"

    if isinstance(node, Memory):
        return f"{header}\n  {node.content}"
    if isinstance(node, MemoryLink):
        return f"{header}\n  {node.title}: {node.summary}\n  -> {node.file_path}"
    if isinstance(node, Story):
        return f"{header}\n  {node.role}: {node.benefit}"
    if isinstance(node, Feature):
        return f"{header}\n  {node.component}: {node.test_scenario}\n  expect: {node.expected_result}"
    if isinstance(node, Active):
        area = f" [{node.focus_area}]" if node.focus_area else ""
        return f"{header}{area}\n  {node.content}"
    if isinstance(node, Archive):
        return f"{header}\n  {node.content}"
    if isinstance(node, Pattern):
        ptype = f" [{node.pattern_type}]" if node.pattern_type else ""
        return f"{header}{ptype}\n  {node.content}"
    if isinstance(node, Progress):
        return f"{header}\n  {node.content}"
    return f"{header}\n  {node.uid}"


def register_focus(group: click.Group) -> None:
    @group.command("focus")
    @click.option("--tags", required=True, help="Comma separated query tags")
    @click.option("--limit", default=5, type=int)
    @click.pass_context
    def focus_command(ctx: click.Context, tags: str, limit: int) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        nodes = storage.all_nodes()
        links = storage.all_links()
        engine = GraphEngine(VectorScorer(AppConfig()))
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        ranked = engine.retrieve(nodes, links, tag_list, limit=limit)

        node_by_uid = {n.uid: n for n in nodes}
        for uid, score in ranked:
            node = node_by_uid.get(uid)
            if node is not None:
                click.echo(_render_node(node, score))
