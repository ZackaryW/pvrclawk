from pathlib import Path

import click

from pvrclawk.membank.core.config import load_config, set_config_value
from pvrclawk.membank.core.storage.engine import StorageEngine


def register_config(group: click.Group) -> None:
    @group.group("config")
    @click.pass_context
    def config_group(ctx: click.Context) -> None:
        ctx.ensure_object(dict)

    @config_group.command("set")
    @click.argument("key")
    @click.argument("value")
    @click.pass_context
    def set_command(ctx: click.Context, key: str, value: str) -> None:
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        storage.init_db()
        set_config_value(storage.config_file, key, value)
        click.echo(f"{key}={value}")

    @config_group.command("get")
    @click.argument("key")
    @click.pass_context
    def get_command(ctx: click.Context, key: str) -> None:
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        config = load_config(storage.config_file)
        value = config
        for part in key.split("."):
            value = getattr(value, part)
        click.echo(str(value))

    @config_group.command("list")
    @click.pass_context
    def list_command(ctx: click.Context) -> None:
        root_path = Path(ctx.obj["root_path"])
        storage = StorageEngine(root_path)
        config = load_config(storage.config_file)
        click.echo(config.model_dump_json(indent=2))
