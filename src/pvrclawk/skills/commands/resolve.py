"""skills resolve command."""

import click

from pvrclawk.skills.core.config import load_skills_config
from pvrclawk.skills.core.resolver import resolve_skills
from pvrclawk.skills.core.scanner import collect_skill_repos, scan_skills


def register_resolve(group: click.Group) -> None:
    @group.command("resolve")
    @click.argument("keywords", nargs=-1, required=True)
    def resolve_skills_command(keywords: tuple[str, ...]) -> None:
        cfg = load_skills_config()
        repos = collect_skill_repos(cfg)
        infos = scan_skills(repos)
        matches = resolve_skills(infos, list(keywords))
        for info in matches:
            click.echo(f"{info.name} [{info.format}] - {info.description}")

