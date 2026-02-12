import click

from pvrclawk.membank import membank_group


@click.group()
def main() -> None:
    """pvrclawk root command."""


main.add_command(membank_group, name="membank")
