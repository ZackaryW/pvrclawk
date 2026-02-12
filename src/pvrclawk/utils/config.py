"""Universal config model and TOML I/O."""

from pathlib import Path
import tomllib

from pydantic import BaseModel


class PruneConfig(BaseModel):
    auto_threshold: int = 20
    max_cluster_size: int = 100


class DecayConfig(BaseModel):
    half_life_days: int = 7


class MoodConfig(BaseModel):
    default: float = 0.5
    smoothing: float = 0.1


class AppConfig(BaseModel):
    prune: PruneConfig = PruneConfig()
    decay: DecayConfig = DecayConfig()
    mood: MoodConfig = MoodConfig()
    auto_archive_active: bool = True


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        return AppConfig()
    raw = path.read_text(encoding="utf-8")
    data = tomllib.loads(raw)
    return AppConfig.model_validate(data)


def write_config(path: Path, config: AppConfig) -> None:
    dumped = config.model_dump()
    content = (
        f"auto_archive_active = {str(dumped['auto_archive_active']).lower()}\n\n"
        "[prune]\n"
        f"auto_threshold = {dumped['prune']['auto_threshold']}\n"
        f"max_cluster_size = {dumped['prune']['max_cluster_size']}\n\n"
        "[decay]\n"
        f"half_life_days = {dumped['decay']['half_life_days']}\n\n"
        "[mood]\n"
        f"default = {dumped['mood']['default']}\n"
        f"smoothing = {dumped['mood']['smoothing']}\n"
    )
    path.write_text(content, encoding="utf-8")


def _parse_value(value: str):
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def set_config_value(path: Path, key: str, value: str) -> AppConfig:
    config = load_config(path)
    if "." in key:
        section, field = key.split(".", 1)
        section_obj = getattr(config, section)
        setattr(section_obj, field, _parse_value(value))
    else:
        setattr(config, key, _parse_value(value))
    write_config(path, config)
    return config
