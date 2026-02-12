from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_prune(group: click.Group) -> None:
    @group.command("prune")
    @click.pass_context
    def prune_command(ctx: click.Context) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        name = storage.prune()
        click.echo(name)
