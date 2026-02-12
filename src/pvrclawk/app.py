import click

from pvrclawk.membank import membank_group
from pvrclawk.skills import skills_group


@click.group()
def main() -> None:
    """pvrclawk root command."""


main.add_command(membank_group, name="membank")
main.add_command(skills_group, name="skills")
