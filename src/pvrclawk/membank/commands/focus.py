from pathlib import Path

import click

from pvrclawk.membank.commands.render import render_node
from pvrclawk.membank.core.graph.engine import GraphEngine
from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.session import Session


def register_focus(group: click.Group) -> None:
    @group.command("focus", help="Retrieve ranked nodes relevant to query tags.")
    @click.option("--tags", required=True, help="Comma-separated query tags.")
    @click.option("--limit", default=5, type=int, help="Maximum number of ranked nodes to return.")
    @click.pass_context
    def focus_command(ctx: click.Context, tags: str, limit: int) -> None:
        """Retrieve ranked nodes relevant to query tags."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        active_session = ctx.obj.get("session")
        active_session = active_session if isinstance(active_session, Session) else None
        served_uids = set(active_session.served_uids) if active_session is not None else set()
        newly_served: list[str] = []
        nodes = storage.all_nodes()
        links = storage.all_links()
        engine = GraphEngine(VectorScorer(AppConfig()))
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        ranked = engine.retrieve(nodes, links, tag_list, limit=limit)

        node_by_uid = {n.uid: n for n in nodes}
        for uid, score in ranked:
            node = node_by_uid.get(uid)
            if node is not None:
                already_served = uid in served_uids
                click.echo(render_node(node, score=score, truncated=already_served))
                if active_session is not None and not already_served:
                    newly_served.append(uid)
                    served_uids.add(uid)

        if active_session is not None and newly_served:
            storage.record_session_served(active_session, newly_served)
