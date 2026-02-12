from datetime import datetime, timezone
from pathlib import Path

import click

from pvrclawk.membank.core.storage.engine import StorageEngine


def register_session(group: click.Group) -> None:
    @group.group("session", help="Manage session context deduplication state.")
    def session_group() -> None:
        """Manage session context deduplication state."""

    @session_group.command("up", help="Start or reuse an active session and print its UUID.")
    @click.pass_context
    def session_up(ctx: click.Context) -> None:
        """Start or reuse an active session and print its UUID."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        storage.init_db()
        session = storage.activate_session()
        click.echo(session.session_id)

    @session_group.command("tear", help="End the active session and clear session context state.")
    @click.pass_context
    def session_tear(ctx: click.Context) -> None:
        """End the active session and clear session context state."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        if storage.clear_session():
            click.echo("Session cleared.")
            return
        click.echo("No active session.")

    @session_group.command("reset", help="Clear served UID history for the active session.")
    @click.pass_context
    def session_reset(ctx: click.Context) -> None:
        """Clear served UID history for the active session."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        active = storage.load_active_session()
        if active is None:
            click.echo("No active session.")
            return
        storage.reset_session(session_id=active.session_id)
        click.echo(active.session_id)

    @session_group.command("info", help="Show active session UUID, age, and served UID count.")
    @click.pass_context
    def session_info(ctx: click.Context) -> None:
        """Show active session UUID, age, and served UID count."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        active = storage.load_active_session()
        if active is None:
            click.echo("No active session.")
            return
        age_seconds = int((datetime.now(timezone.utc) - active.created_at).total_seconds())
        click.echo(f"session_id={active.session_id}")
        click.echo(f"age_seconds={age_seconds}")
        click.echo(f"served_count={len(active.served_uids)}")
