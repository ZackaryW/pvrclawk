import click


@click.group()
@click.option("--path", "root_path", default=".pvrclawk", help="Storage root path.")
@click.pass_context
def membank_group(ctx: click.Context, root_path: str) -> None:
    """Membank commands."""
    ctx.ensure_object(dict)
    ctx.obj["root_path"] = root_path


from pvrclawk.membank.commands.config import register_config  # noqa: E402
from pvrclawk.membank.commands.focus import register_focus  # noqa: E402
from pvrclawk.membank.commands.init import register_init  # noqa: E402
from pvrclawk.membank.commands.link import register_link  # noqa: E402
from pvrclawk.membank.commands.mood import register_mood  # noqa: E402
from pvrclawk.membank.commands.node import register_node  # noqa: E402
from pvrclawk.membank.commands.prune import register_prune  # noqa: E402
from pvrclawk.membank.commands.rules import register_rules  # noqa: E402

register_init(membank_group)
register_config(membank_group)
register_node(membank_group)
register_link(membank_group)
register_focus(membank_group)
register_prune(membank_group)
register_mood(membank_group)
register_rules(membank_group)
