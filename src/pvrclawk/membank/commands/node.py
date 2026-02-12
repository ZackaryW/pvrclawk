from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine
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
    @click.pass_context
    def add_node(
        ctx: click.Context,
        node_type: str,
        content: str,
        title: str,
        summary: str,
        tags: str,
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
            node = Story(role=title, benefit=summary or content)
        elif node_type == "feature":
            node = Feature(component=title or "component", test_scenario=summary or "scenario", expected_result=content or "result")
        elif node_type == "active":
            node = Active(content=content, focus_area=title)
        elif node_type == "archive":
            node = Archive(content=content, archived_from=title, reason=summary)
        elif node_type == "pattern":
            node = Pattern(content=content, pattern_type=title)
        elif node_type == "progress":
            node = Progress(content=content)
        else:
            raise click.ClickException(f"Unknown node type: {node_type}")

        for k, v in parsed_tags.items():
            node.add_tag(k, v)
        uid = storage.save_node(node, node_type)
        click.echo(uid)

    @node_group.command("list")
    @click.argument("node_type")
    @click.pass_context
    def list_nodes(ctx: click.Context, node_type: str) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        nodes = storage.load_nodes_by_type(node_type)
        for node in nodes:
            if isinstance(node, Memory):
                click.echo(node.content)
            elif isinstance(node, MemoryLink):
                click.echo(f"{node.title} [-> {node.file_path}]")
            else:
                click.echo(str(node))

