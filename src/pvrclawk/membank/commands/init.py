from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_init(group: click.Group) -> None:
    @group.command("init")
    @click.pass_context
    def init_command(ctx: click.Context) -> None:
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        storage.init_db()
        click.echo(f"Initialized membank at {root_path}")
