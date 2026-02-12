import click
from pathlib import Path


EXPECTED_ROOT_ENTRIES = {
    "nodes",
    "additional_memory",
    "index.json",
    "links.json",
    "rules.json",
    "mood.json",
    "config.toml",
    "recent_uid.json",
}


def _looks_like_membank_root(path: Path) -> bool:
    return any((path / entry).exists() for entry in EXPECTED_ROOT_ENTRIES)


def _resolve_storage_root(root_path: str) -> Path:
    """Resolve membank root path, defaulting to .pvrclawk subpath for source dirs."""
    path = Path(root_path)
    if path.name == ".pvrclawk":
        return path
    if _looks_like_membank_root(path):
        return path
    return path / ".pvrclawk"


@click.group(help="Manage the graph-based membank.")
@click.option("--path", "root_path", default=".pvrclawk", help="Path to membank storage (or project root that contains .pvrclawk).")
@click.pass_context
def membank_group(ctx: click.Context, root_path: str) -> None:
    """Manage the graph-based membank."""
    ctx.ensure_object(dict)
    ctx.obj["root_path"] = str(_resolve_storage_root(root_path))


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
