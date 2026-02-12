from pathlib import Path

import click

from pvrclawk.membank.core.mood.tracker import MoodTracker
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.config import AppConfig


def register_mood(group: click.Group) -> None:
    @group.group("report", help="Submit observations that influence mood-aware scoring.")
    def report_group() -> None:
        """Submit observations that influence mood-aware scoring."""

    @report_group.command("mood", help="Report a mood value for a tag.")
    @click.argument("tag")
    @click.argument("value", type=float)
    @click.pass_context
    def mood_command(ctx: click.Context, tag: str, value: float) -> None:
        """Report a mood value for a tag."""
        storage = StorageEngine(Path(ctx.obj["root_path"]))
        storage.init_db()
        tracker = MoodTracker(storage.mood_file, AppConfig())
        updated = tracker.report(tag, value)
        click.echo(f"{tag}={updated}")
