import click

from pvrclawk.membank import membank_group
from pvrclawk.skills import skills_group


@click.group(help="pvrclawk CLI entrypoint.")
def main() -> None:
    """pvrclawk CLI entrypoint."""


main.add_command(membank_group, name="membank")
main.add_command(skills_group, name="skills")
