"""Universal JSON read/write utilities."""

import json
from pathlib import Path
from typing import Any


def read_json(path: Path, default: Any) -> Any:
    """Read JSON from path, returning default if file doesn't exist."""
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    """Write data as indented JSON to path."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
