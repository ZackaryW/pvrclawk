from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.link import Link


def _resolve_uid_reference(storage: StorageEngine, uid_or_prefix: str) -> str:
    resolved, reason = storage.resolve_uid_with_reason(uid_or_prefix)
    if reason == "ambiguous":
        raise click.ClickException(f"Ambiguous UID prefix: {uid_or_prefix}. Provide a longer prefix or full UID.")
    if resolved is None:
        raise click.ClickException(f"Could not resolve UID reference: {uid_or_prefix}")
    return resolved


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
        source_uid = _resolve_uid_reference(storage, source_uid)
        target_uid = _resolve_uid_reference(storage, target_uid)
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        link = Link(source=source_uid, target=target_uid, tags=tag_list, weight=weight)
        storage.save_link(link)
        click.echo(link.uid)

    @link_group.command("list")
    @click.argument("source_uid")
    @click.pass_context
    def list_command(ctx: click.Context, source_uid: str) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        source_uid = _resolve_uid_reference(storage, source_uid)
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

    @link_group.command("chain")
    @click.argument("uids", nargs=-1)
    @click.option("--tags", default="")
    @click.option("--weight", default=1.0, type=float)
    @click.pass_context
    def chain_command(ctx: click.Context, uids: tuple[str, ...], tags: str, weight: float) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        if len(uids) < 2:
            raise click.ClickException("Chain requires at least two UIDs.")
        resolved = [_resolve_uid_reference(storage, uid) for uid in uids]
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

        links = [
            Link(source=resolved[i], target=resolved[i + 1], tags=tag_list, weight=weight)
            for i in range(len(resolved) - 1)
        ]
        created = storage.save_links(links)
        click.echo(f"Created {created} links")
