"""skills update command."""

import click

from pvrclawk.skills.core.config import load_skills_config
from pvrclawk.skills.core.scanner import collect_skill_repos
from pvrclawk.skills.core.updater import update_skill_repos


def register_update(group: click.Group) -> None:
    @group.command("update", help="Update configured skill repositories by pulling git remotes.")
    @click.option("-a", "--all", "update_all", is_flag=True, help="Update all configured skill repos.")
    def update_skills(update_all: bool) -> None:
        """Update configured skill repositories by pulling git remotes."""
        if not update_all:
            raise click.UsageError("Use -a/--all to update all configured skill repositories.")
        cfg = load_skills_config()
        repos = collect_skill_repos(cfg)
        results = update_skill_repos(repos)
        for result in results:
            label = result.status.upper()
            click.echo(f"{label}: {result.repo} - {result.message}")

