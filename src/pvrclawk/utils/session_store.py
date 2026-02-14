import hashlib
import os
from pathlib import Path


def normalize_target_path(path: Path) -> str:
    return str(path.resolve())


def target_hash(path: Path) -> str:
    normalized = normalize_target_path(path)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def resolve_session_store_root() -> Path:
    override = os.getenv("PVRCLAWK_SESSION_STORE_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / ".config" / "pvrclawk").resolve()


def resolve_session_bucket(path: Path) -> Path:
    root = resolve_session_store_root()
    return root / "sessions" / target_hash(path)
