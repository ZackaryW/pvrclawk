from pathlib import Path
import tomllib

from pvrclawk.membank.models.config import AppConfig


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        return AppConfig()
    raw = path.read_text(encoding="utf-8")
    data = tomllib.loads(raw)
    return AppConfig.model_validate(data)


def write_config(path: Path, config: AppConfig) -> None:
    dumped = config.model_dump()
    content = (
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
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def set_config_value(path: Path, key: str, value: str) -> AppConfig:
    config = load_config(path)
    section, field = key.split(".", 1)
    section_obj = getattr(config, section)
    setattr(section_obj, field, _parse_value(value))
    write_config(path, config)
    return config
