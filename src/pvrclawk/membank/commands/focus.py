from pathlib import Path

import click

from pvrclawk.membank.commands.render import render_node
from pvrclawk.membank.core.graph.engine import GraphEngine
from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.config import AppConfig


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
                click.echo(render_node(node, score=score))
