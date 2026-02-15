"""Last command: return the most recently updated context (small default to save tokens)."""

from pathlib import Path

import click

from pvrclawk.membank.commands.render import render_node
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.session import Session


def _sort_recent(nodes: list) -> list:
    return sorted(nodes, key=lambda n: getattr(n, "updated_at", "") or "", reverse=True)


def register_last(group: click.Group) -> None:
    @group.command("last", help="Return the most recently updated nodes (small default to save tokens).")
    @click.option("--top", type=click.IntRange(min=1), default=10, help="Show only the N most recent nodes (default 10).")
    @click.pass_context
    def last_command(ctx: click.Context, top: int) -> None:
        """Return the N most recently updated nodes."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        nodes = _sort_recent(storage.all_nodes())
        nodes = nodes[:top]

        active_session = ctx.obj.get("session")
        active_session = active_session if isinstance(active_session, Session) else None
        served_uids = set(active_session.served_uids) if active_session is not None else set()
        newly_served: list[str] = []

        for node in nodes:
            already_served = node.uid in served_uids
            click.echo(render_node(node, truncated=already_served))
            if active_session is not None and not already_served:
                newly_served.append(node.uid)
                served_uids.add(node.uid)
        if active_session is not None and newly_served:
            storage.record_session_served(active_session, newly_served)
