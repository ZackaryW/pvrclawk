from pathlib import Path

import click

from pvrclawk.membank.core.config import load_config, set_config_value
from pvrclawk.membank.core.storage.engine import StorageEngine


def register_config(group: click.Group) -> None:
    @group.group("config", help="Read and update membank configuration values.")
    @click.pass_context
    def config_group(ctx: click.Context) -> None:
        """Read and update membank configuration values."""
        ctx.ensure_object(dict)

    @config_group.command("set", help="Set a configuration key to a value.")
    @click.argument("key")
    @click.argument("value")
    @click.pass_context
    def set_command(ctx: click.Context, key: str, value: str) -> None:
        """Set a configuration key to a value."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        storage.init_db()
        set_config_value(storage.config_file, key, value)
        click.echo(f"{key}={value}")

    @config_group.command("get", help="Get a configuration value by dotted key path.")
    @click.argument("key")
    @click.pass_context
    def get_command(ctx: click.Context, key: str) -> None:
        """Get a configuration value by dotted key path."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        config = load_config(storage.config_file)
        value = config
        for part in key.split("."):
            value = getattr(value, part)
        click.echo(str(value))

    @config_group.command("list", help="Print the full configuration as JSON.")
    @click.pass_context
    def list_command(ctx: click.Context) -> None:
        """Print the full configuration as JSON."""
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        config = load_config(storage.config_file)
        click.echo(config.model_dump_json(indent=2))
