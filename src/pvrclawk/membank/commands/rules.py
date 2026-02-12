from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_rules(group: click.Group) -> None:
    @group.group("rule")
    def rule_group() -> None:
        """Rule commands."""

    @rule_group.command("add")
    @click.argument("rule")
    @click.pass_context
    def add_command(ctx: click.Context, rule: str) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        storage.init_db()
        storage.add_rule(rule)
        click.echo("ok")

    @rule_group.command("list")
    @click.pass_context
    def list_command(ctx: click.Context) -> None:
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        for rule in storage.list_rules():
            click.echo(rule)
