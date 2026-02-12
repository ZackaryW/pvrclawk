import click
import os
from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.session import Session


EXPECTED_ROOT_ENTRIES = {
    "nodes",
    "additional_memory",
    "index.json",
    "links.json",
    "rules.json",
    "mood.json",
    "session.json",
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


def _resolve_session(storage: StorageEngine, explicit_session_id: str | None) -> Session | None:
    if explicit_session_id:
        storage.init_db()
        return storage.activate_session(session_id=explicit_session_id)
    env_session_id = os.getenv("PVRCLAWK_SESSION", "").strip()
    if env_session_id:
        storage.init_db()
        return storage.activate_session(session_id=env_session_id)
    return storage.load_active_session()


@click.group(help="Manage the graph-based membank.")
@click.option("--path", "root_path", default=".pvrclawk", help="Path to membank storage (or project root that contains .pvrclawk).")
@click.option("--session", "session_id", default=None, help="Session UUID override.")
@click.pass_context
def membank_group(ctx: click.Context, root_path: str, session_id: str | None) -> None:
    """Manage the graph-based membank."""
    ctx.ensure_object(dict)
    resolved_root = _resolve_storage_root(root_path)
    storage = StorageEngine(Path(resolved_root))
    ctx.obj["root_path"] = str(resolved_root)
    ctx.obj["session"] = _resolve_session(storage, session_id)


from pvrclawk.membank.commands.config import register_config  # noqa: E402
from pvrclawk.membank.commands.focus import register_focus  # noqa: E402
from pvrclawk.membank.commands.init import register_init  # noqa: E402
from pvrclawk.membank.commands.link import register_link  # noqa: E402
from pvrclawk.membank.commands.mood import register_mood  # noqa: E402
from pvrclawk.membank.commands.node import register_node  # noqa: E402
from pvrclawk.membank.commands.prune import register_prune  # noqa: E402
from pvrclawk.membank.commands.rules import register_rules  # noqa: E402
from pvrclawk.membank.commands.session import register_session  # noqa: E402

register_init(membank_group)
register_config(membank_group)
register_node(membank_group)
register_link(membank_group)
register_focus(membank_group)
register_prune(membank_group)
register_mood(membank_group)
register_rules(membank_group)
register_session(membank_group)
