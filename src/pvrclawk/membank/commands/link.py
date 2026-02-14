from pathlib import Path

import click

from pvrclawk.membank.core.federation.service import FederatedMembankService
from pvrclawk.membank.models.config import load_config
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
    @group.group("link", help="Manage directional links between nodes.")
    def link_group() -> None:
        """Manage directional links between nodes."""

    @link_group.command("add", help="Create one link from source UID to target UID.")
    @click.argument("source_uid")
    @click.argument("target_uid")
    @click.option("--tags", default="", help="Comma-separated tags to attach to the link.")
    @click.option("--weight", default=1.0, type=float, help="Initial link weight.")
    @click.pass_context
    def add_command(ctx: click.Context, source_uid: str, target_uid: str, tags: str, weight: float) -> None:
        """Create one link from source UID to target UID."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        source_uid = _resolve_uid_reference(storage, source_uid)
        target_uid = _resolve_uid_reference(storage, target_uid)
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        link = Link(source=source_uid, target=target_uid, tags=tag_list, weight=weight)
        storage.save_link(link)
        click.echo(link.uid)

    @link_group.command("list", help="List outgoing links for a source UID.")
    @click.argument("source_uid")
    @click.pass_context
    def list_command(ctx: click.Context, source_uid: str) -> None:
        """List outgoing links for a source UID."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        federated = bool(ctx.obj.get("federated"))
        if federated:
            config = load_config(storage.config_file)
            service = FederatedMembankService(root_path, config)
            try:
                links = service.aggregate_links_by_source_uid(source_uid)
            except ValueError as exc:
                raise click.ClickException(str(exc)) from exc
        else:
            source_uid = _resolve_uid_reference(storage, source_uid)
            links = storage.load_links([source_uid])
        for link in links:
            click.echo(f"{link.source} -> {link.target} ({','.join(link.tags)}) w={link.weight}")

    @link_group.command("weight", help="Adjust weights for links matching all provided tags.")
    @click.argument("tags")
    @click.argument("delta", type=float)
    @click.pass_context
    def weight_command(ctx: click.Context, tags: str, delta: float) -> None:
        """Adjust weights for links matching all provided tags."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        updated = storage.adjust_link_weights_by_tags([t.strip() for t in tags.split(",") if t.strip()], delta)
        click.echo(str(updated))

    @link_group.command("chain", help="Create sequential links from a list of UIDs.")
    @click.argument("uids", nargs=-1)
    @click.option("--tags", default="", help="Comma-separated tags to attach to all created links.")
    @click.option("--weight", default=1.0, type=float, help="Weight applied to all created links.")
    @click.pass_context
    def chain_command(ctx: click.Context, uids: tuple[str, ...], tags: str, weight: float) -> None:
        """Create sequential links from a list of UIDs."""
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
