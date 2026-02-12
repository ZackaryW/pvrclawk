from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.link import Link


def register_link(group: click.Group) -> None:
    @group.group("link")
    def link_group() -> None:
        """Link commands."""

    @link_group.command("add")
    @click.argument("source_uid")
    @click.argument("target_uid")
    @click.option("--tags", default="")
    @click.option("--weight", default=1.0, type=float)
    @click.pass_context
    def add_command(ctx: click.Context, source_uid: str, target_uid: str, tags: str, weight: float) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        link = Link(source=source_uid, target=target_uid, tags=tag_list, weight=weight)
        storage.save_link(link)
        click.echo(link.uid)

    @link_group.command("list")
    @click.argument("source_uid")
    @click.pass_context
    def list_command(ctx: click.Context, source_uid: str) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        links = storage.load_links([source_uid])
        for link in links:
            click.echo(f"{link.source} -> {link.target} ({','.join(link.tags)}) w={link.weight}")

    @link_group.command("weight")
    @click.argument("tags")
    @click.argument("delta", type=float)
    @click.pass_context
    def weight_command(ctx: click.Context, tags: str, delta: float) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        updated = storage.adjust_link_weights_by_tags([t.strip() for t in tags.split(",") if t.strip()], delta)
        click.echo(str(updated))
