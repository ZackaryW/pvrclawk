"""Forctx command: query-based context retrieval with #tag and [phrase] syntax."""

from pathlib import Path

import click

from pvrclawk.membank.commands.render import render_node
from pvrclawk.membank.core.forctx.parser import parse_forctx_query
from pvrclawk.membank.core.forctx.scorer import score_nodes_forctx
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.session import Session


def register_forctx(group: click.Group) -> None:
    @group.command("forctx", help="Retrieve context by query: #tag for tags, [phrase] for content (tags weighted higher).")
    @click.argument("query", required=True)
    @click.option("--top", type=click.IntRange(min=1), default=50, help="Maximum number of ranked nodes to return (default 50).")
    @click.pass_context
    def forctx_command(ctx: click.Context, query: str, top: int) -> None:
        """Return nodes ranked by tag and content phrase match."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        nodes = storage.all_nodes()
        tag_tokens, content_phrases = parse_forctx_query(query)
        ranked = score_nodes_forctx(nodes, tag_tokens, content_phrases, top=top)

        node_by_uid = {n.uid: n for n in nodes}
        active_session = ctx.obj.get("session")
        active_session = active_session if isinstance(active_session, Session) else None
        served_uids = set(active_session.served_uids) if active_session is not None else set()
        newly_served: list[str] = []

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
