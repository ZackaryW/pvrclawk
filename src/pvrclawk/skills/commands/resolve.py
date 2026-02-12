"""skills resolve command."""

import click

from pvrclawk.skills.core.config import load_skills_config
from pvrclawk.skills.core.resolver import resolve_skills
from pvrclawk.skills.core.scanner import collect_skill_repos, scan_skills


def register_resolve(group: click.Group) -> None:
    @group.command("resolve")
    @click.option("--full", "full_view", is_flag=True, help="Show full details including absolute path.")
    @click.option("--path-only", is_flag=True, help="Output absolute path only.")
    @click.argument("keywords", nargs=-1, required=True)
    def resolve_skills_command(full_view: bool, path_only: bool, keywords: tuple[str, ...]) -> None:
        if full_view and path_only:
            raise click.UsageError("--full and --path-only cannot be used together.")
        cfg = load_skills_config()
        repos = collect_skill_repos(cfg)
        infos = scan_skills(repos)
        matches = resolve_skills(infos, list(keywords))
        for info in matches:
            if path_only:
                click.echo(str(info.path))
            elif full_view:
                click.echo(f"{info.name} [{info.format}] - {info.description} -> {info.path}")
            else:
                click.echo(f"{info.name} [{info.format}] - {info.description}")

