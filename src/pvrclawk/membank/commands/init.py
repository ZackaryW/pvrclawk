from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_init(group: click.Group) -> None:
    @group.command("init", help="Initialize membank storage files and directories.")
    @click.pass_context
    def init_command(ctx: click.Context) -> None:
        """Initialize membank storage files and directories."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        storage.init_db()
        click.echo(f"Initialized membank at {root_path}")
