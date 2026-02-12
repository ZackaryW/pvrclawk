"""skills list command."""

import click

from pvrclawk.skills.core.config import load_skills_config
from pvrclawk.skills.core.scanner import collect_skill_repos, scan_skills


def register_list(group: click.Group) -> None:
    @group.command("list", help="List discovered skills across configured repositories.")
    @click.option("--human", is_flag=True, help="Render a human-readable table view.")
    def list_skills(human: bool) -> None:
        """List discovered skills across configured repositories."""
        cfg = load_skills_config()
        repos = collect_skill_repos(cfg)
        infos = scan_skills(repos)
        infos = sorted(infos, key=lambda item: (item.repo, item.name))

        if human:
            click.echo(f"{'NAME':<28} {'FORMAT':<13} {'REPO':<20} DESCRIPTION")
            click.echo(f"{'-' * 28} {'-' * 13} {'-' * 20} {'-' * 40}")
            for info in infos:
                click.echo(f"{info.name:<28} {info.format:<13} {info.repo:<20} {info.description}")
            return

        for info in infos:
            click.echo(f"{info.name} [{info.format}] - {info.description}")

