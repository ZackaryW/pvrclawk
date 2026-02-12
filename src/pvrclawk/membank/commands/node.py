from pathlib import Path

import click

from pvrclawk.membank.commands.render import render_node, render_node_detail
from pvrclawk.membank.core.storage.engine import StorageEngine
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
from pvrclawk.membank.models.session import Session


def _parse_tags(raw: str) -> dict[str, float]:
    tags: dict[str, float] = {}
    if not raw:
        return tags
    for item in raw.split(","):
        piece = item.strip()
        if not piece:
            continue
        if ":" in piece:
            name, value = piece.rsplit(":", 1)
            tags[name.strip()] = float(value)
        else:
            tags[piece] = 1.0
    return tags


def _sort_recent(nodes: list[object]) -> list[object]:
    return sorted(nodes, key=lambda n: getattr(n, "updated_at", "") or "", reverse=True)


def _resolve_uid_reference(
    storage: StorageEngine,
    uid: str | None,
    last: int | None,
    allow_unresolved_uid: bool = False,
) -> str:
    if uid and last is not None:
        raise click.ClickException("Use either UID or --last, not both.")
    if not uid and last is None:
        raise click.ClickException("Provide a UID or --last.")
    if last is not None:
        resolved = storage.resolve_recent_uid(last)
        if resolved is None:
            raise click.ClickException(f"No recent UID found for --last {last}.")
        return resolved
    assert uid is not None
    resolved, reason = storage.resolve_uid_with_reason(uid)
    if reason == "ambiguous":
        raise click.ClickException(f"Ambiguous UID prefix: {uid}. Provide a longer prefix or full UID.")
    if resolved is None:
        if allow_unresolved_uid:
            return uid
        raise click.ClickException(f"Could not resolve UID reference: {uid}")
    return resolved


def register_node(group: click.Group) -> None:
    @group.group("node", help="Create, inspect, list, and remove membank nodes.")
    def node_group() -> None:
        """Create, inspect, list, and remove membank nodes."""

    @node_group.command("add", help="Create a node for the given node type.")
    @click.argument("node_type")
    @click.option("--content", default="", help="Node content/body text.")
    @click.option(
        "--title",
        default="",
        help="Primary label field. For story nodes, use persona phrasing (for example: 'As a manager').",
    )
    @click.option(
        "--summary",
        default="",
        help="Summary field. For story nodes, use goal+value phrasing (for example: 'I want ... so that ...').",
    )
    @click.option("--tags", default="", help="Comma-separated tags. Optional weights use tag:value syntax.")
    @click.option(
        "--status",
        "initial_status",
        default="todo",
        type=click.Choice(["todo", "in_progress", "done", "blocked"]),
        help="Initial status for node types that support status.",
    )
    @click.option("--criteria", multiple=True, help="Acceptance criteria / confirmation checks (repeatable).")
    @click.pass_context
    def add_node(
        ctx: click.Context,
        node_type: str,
        content: str,
        title: str,
        summary: str,
        tags: str,
        initial_status: str,
        criteria: tuple[str, ...],
    ) -> None:
        """Create a node for the given node type."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        storage.init_db()
        parsed_tags = _parse_tags(tags)

        if node_type == "memory":
            node = Memory(content=content)
        elif node_type == "memorylink":
            file_path = storage.create_memory_file(title, content)
            rel = file_path.relative_to(storage.root).as_posix()
            node = MemoryLink(title=title, summary=summary, file_path=rel)
        elif node_type == "story":
            node = Story(role=title, benefit=summary or content, criteria=list(criteria), status=initial_status)
        elif node_type == "feature":
            node = Feature(component=title or "component", test_scenario=summary or "scenario", expected_result=content or "result", status=initial_status)
        elif node_type == "task":
            node = Task(content=content or summary or title, status=initial_status)
        elif node_type == "subtask":
            node = SubTask(content=content or summary or title, status=initial_status)
        elif node_type == "issue":
            node = Issue(content=content or summary or title, status=initial_status)
        elif node_type == "bug":
            node = Bug(content=content or summary or title, status=initial_status)
        elif node_type in {"active", "archive"}:
            raise click.ClickException(f"'{node_type}' is deprecated. Use 'task' or 'subtask' instead.")
        elif node_type == "pattern":
            node = Pattern(content=content, pattern_type=title)
        elif node_type == "progress":
            node = Progress(content=content, status=initial_status)
        else:
            raise click.ClickException(f"Unknown node type: {node_type}")

        for k, v in parsed_tags.items():
            node.add_tag(k, v)
        uid = storage.save_node(node, node_type)
        click.echo(uid)

    @node_group.command("get", help="Show full details for a node by UID or --last index.")
    @click.argument("uid", required=False)
    @click.option("--last", "last_n", type=click.IntRange(min=1, max=10), default=None, help="Use the Nth most recent UID.")
    @click.pass_context
    def get_node(ctx: click.Context, uid: str | None, last_n: int | None) -> None:
        """Show full detail for a single node by UID."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        resolved_uid = _resolve_uid_reference(storage, uid, last_n, allow_unresolved_uid=True)
        node = storage.load_node(resolved_uid)
        if node is None:
            click.echo(f"Node not found: {resolved_uid}")
            return
        click.echo(render_node_detail(node))

    @node_group.command("status", help="Update the status of a node that supports status.")
    @click.argument("args", nargs=-1)
    @click.option("--last", "last_n", type=click.IntRange(min=1, max=10), default=None, help="Use the Nth most recent UID.")
    @click.pass_context
    def set_status(ctx: click.Context, args: tuple[str, ...], last_n: int | None) -> None:
        """Update the status of a node that supports status."""
        allowed_statuses = {"todo", "in_progress", "done", "blocked"}
        uid: str | None = None
        if last_n is not None:
            if len(args) != 1:
                raise click.ClickException("Usage: node status --last N <new_status>")
            new_status = args[0]
        else:
            if len(args) != 2:
                raise click.ClickException("Usage: node status <uid_or_prefix> <new_status>")
            uid, new_status = args
        if new_status not in allowed_statuses:
            raise click.ClickException(f"Invalid status: {new_status}")

        storage = StorageEngine(Path(ctx.obj["root_path"]))
        resolved_uid = _resolve_uid_reference(storage, uid, last_n, allow_unresolved_uid=True)
        ok = storage.update_node_status(resolved_uid, new_status)
        if ok:
            click.echo(f"Status updated to {new_status}")
        else:
            click.echo(f"Could not update status for {resolved_uid} (node not found or no status field)")

    @node_group.command("list", help="List nodes for a specific node type.")
    @click.argument("node_type")
    @click.option("--top", type=click.IntRange(min=1), default=None, help="Show only the N most recent nodes.")
    @click.pass_context
    def list_nodes(ctx: click.Context, node_type: str, top: int | None) -> None:
        """List all nodes of a given type."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        active_session = ctx.obj.get("session")
        active_session = active_session if isinstance(active_session, Session) else None
        served_uids = set(active_session.served_uids) if active_session is not None else set()
        newly_served: list[str] = []
        nodes = _sort_recent(storage.load_nodes_by_type(node_type))
        if top is not None:
            nodes = nodes[:top]
        for node in nodes:
            already_served = node.uid in served_uids
            click.echo(render_node(node, truncated=already_served))
            if active_session is not None and not already_served:
                newly_served.append(node.uid)
                served_uids.add(node.uid)
        if active_session is not None and newly_served:
            storage.record_session_served(active_session, newly_served)

    @node_group.command("list-all", help="List nodes across all node types.")
    @click.option("--top", type=click.IntRange(min=1), default=None, help="Show only the N most recent nodes.")
    @click.pass_context
    def list_all_nodes(ctx: click.Context, top: int | None) -> None:
        """List all nodes across all types."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        active_session = ctx.obj.get("session")
        active_session = active_session if isinstance(active_session, Session) else None
        served_uids = set(active_session.served_uids) if active_session is not None else set()
        newly_served: list[str] = []
        nodes = _sort_recent(storage.all_nodes())
        if top is not None:
            nodes = nodes[:top]
        for node in nodes:
            already_served = node.uid in served_uids
            click.echo(render_node(node, truncated=already_served))
            if active_session is not None and not already_served:
                newly_served.append(node.uid)
                served_uids.add(node.uid)
        if active_session is not None and newly_served:
            storage.record_session_served(active_session, newly_served)

    @node_group.command("remove", help="Remove one node by UID or --last index.")
    @click.argument("uid", required=False)
    @click.option("--last", "last_n", type=click.IntRange(min=1, max=10), default=None, help="Use the Nth most recent UID.")
    @click.pass_context
    def remove_node(ctx: click.Context, uid: str | None, last_n: int | None) -> None:
        """Remove a single node by UID."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        resolved_uid = _resolve_uid_reference(storage, uid, last_n, allow_unresolved_uid=True)
        ok = storage.remove_node(resolved_uid)
        if ok:
            click.echo(f"Removed node {resolved_uid}")
        else:
            click.echo(f"Node not found: {resolved_uid}")

    @node_group.command("remove-type", help="Remove all nodes of one type (requires --all).")
    @click.argument("node_type")
    @click.option("-a", "--all", "confirm_all", is_flag=True, help="Required: confirm removing all nodes of this type.")
    @click.pass_context
    def remove_nodes_by_type(ctx: click.Context, node_type: str, confirm_all: bool) -> None:
        """Remove all nodes of one type (requires --all)."""
        if not confirm_all:
            raise click.ClickException("Use --all to confirm bulk removal by type.")
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        removed = storage.remove_nodes_by_type(node_type)
        click.echo(f"Removed {removed} node(s) of type {node_type}")

