import click


@click.group()
def skills_group() -> None:
    """Skills commands."""


from pvrclawk.skills.commands.list import register_list  # noqa: E402
from pvrclawk.skills.commands.resolve import register_resolve  # noqa: E402
from pvrclawk.skills.commands.update import register_update  # noqa: E402

register_list(skills_group)
register_resolve(skills_group)
register_update(skills_group)

