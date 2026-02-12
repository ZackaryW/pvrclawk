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


def register_node(group: click.Group) -> None:
    @group.group("node")
    def node_group() -> None:
        """Node commands."""

    @node_group.command("add")
    @click.argument("node_type")
    @click.option("--content", default="")
    @click.option("--title", default="")
    @click.option("--summary", default="")
    @click.option("--tags", default="")
    @click.option("--status", "initial_status", default="todo", type=click.Choice(["todo", "in_progress", "done", "blocked"]))
    @click.option("--criteria", multiple=True, help="Acceptance criteria (repeatable)")
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

    @node_group.command("get")
    @click.argument("uid")
    @click.pass_context
    def get_node(ctx: click.Context, uid: str) -> None:
        """Show full detail for a single node by UID."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        node = storage.load_node(uid)
        if node is None:
            click.echo(f"Node not found: {uid}")
            return
        click.echo(render_node_detail(node))

    @node_group.command("status")
    @click.argument("uid")
    @click.argument("new_status", type=click.Choice(["todo", "in_progress", "done", "blocked"]))
    @click.pass_context
    def set_status(ctx: click.Context, uid: str, new_status: str) -> None:
        """Update the status of a story, feature, or progress node."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        ok = storage.update_node_status(uid, new_status)
        if ok:
            click.echo(f"Status updated to {new_status}")
        else:
            click.echo(f"Could not update status for {uid} (node not found or no status field)")

    @node_group.command("list")
    @click.argument("node_type")
    @click.option("--top", type=click.IntRange(min=1), default=None, help="Show only the N most recent nodes.")
    @click.pass_context
    def list_nodes(ctx: click.Context, node_type: str, top: int | None) -> None:
        """List all nodes of a given type."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        nodes = _sort_recent(storage.load_nodes_by_type(node_type))
        if top is not None:
            nodes = nodes[:top]
        for node in nodes:
            click.echo(render_node(node))

    @node_group.command("list-all")
    @click.option("--top", type=click.IntRange(min=1), default=None, help="Show only the N most recent nodes.")
    @click.pass_context
    def list_all_nodes(ctx: click.Context, top: int | None) -> None:
        """List all nodes across all types."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        nodes = _sort_recent(storage.all_nodes())
        if top is not None:
            nodes = nodes[:top]
        for node in nodes:
            click.echo(render_node(node))

