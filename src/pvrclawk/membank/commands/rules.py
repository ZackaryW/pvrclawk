from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_rules(group: click.Group) -> None:
    @group.group("rule", help="Manage scoring rules used during focus retrieval.")
    def rule_group() -> None:
        """Manage scoring rules used during focus retrieval."""

    @rule_group.command("add", help="Add one rule expression to rules storage.")
    @click.argument("rule")
    @click.pass_context
    def add_command(ctx: click.Context, rule: str) -> None:
        """Add one rule expression to rules storage."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        storage.init_db()
        storage.add_rule(rule)
        click.echo("ok")

    @rule_group.command("list", help="List all configured rule expressions.")
    @click.pass_context
    def list_command(ctx: click.Context) -> None:
        """List all configured rule expressions."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        for rule in storage.list_rules():
            click.echo(rule)
