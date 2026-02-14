"""Universal config model and TOML I/O."""

from pathlib import Path
import tomllib

from pydantic import BaseModel, Field


class PruneConfig(BaseModel):
    auto_threshold: int = 20
    max_cluster_size: int = 100


class DecayConfig(BaseModel):
    half_life_days: int = 7


class MoodConfig(BaseModel):
    default: float = 0.5
    smoothing: float = 0.1


class FederationDiscoveryConfig(BaseModel):
    only_dot_pvrclawk: bool = True
    allow_no_git_boundary: bool = False
    max_git_lookup_levels: int = 10
    candidate_paths: list[str] = Field(default_factory=list)
    external_roots: list[str] = Field(default_factory=list)


class FederationScoringConfig(BaseModel):
    class BankPathPenaltyRule(BaseModel):
        pattern: str
        multiplier: float = 1.0

    root_importance_base: float = 1.0
    host_relevance_base: float = 1.0
    root_distance_decay: float = 0.35
    host_distance_decay: float = 0.45
    cross_bank_link_weight: float = 0.3
    bank_path_penalties: list[BankPathPenaltyRule] = Field(default_factory=list)


class FederationConfig(BaseModel):
    enabled_default: bool = False
    discovery: FederationDiscoveryConfig = FederationDiscoveryConfig()
    scoring: FederationScoringConfig = FederationScoringConfig()
    dsl_rules: list[str] = Field(default_factory=list)


class RetrievalConfig(BaseModel):
    """Resistance factor: nodes with score below this threshold are excluded from focus results."""

    resistance_threshold: float = 0.37


class AppConfig(BaseModel):
    prune: PruneConfig = PruneConfig()
    decay: DecayConfig = DecayConfig()
    mood: MoodConfig = MoodConfig()
    federation: FederationConfig = FederationConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    auto_archive_active: bool = True


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        return AppConfig()
    raw = path.read_text(encoding="utf-8")
    data = tomllib.loads(raw)
    return AppConfig.model_validate(data)


def write_config(path: Path, config: AppConfig) -> None:
    dumped = config.model_dump()
    discovery = dumped["federation"]["discovery"]
    scoring = dumped["federation"]["scoring"]
    candidate_paths = ", ".join(f'"{item}"' for item in discovery["candidate_paths"])
    external_roots = ", ".join(f'"{item}"' for item in discovery["external_roots"])
    dsl_rules = ", ".join(f'"{item}"' for item in dumped["federation"]["dsl_rules"])
    content = (
        f"auto_archive_active = {str(dumped['auto_archive_active']).lower()}\n\n"
        "[prune]\n"
        f"auto_threshold = {dumped['prune']['auto_threshold']}\n"
        f"max_cluster_size = {dumped['prune']['max_cluster_size']}\n\n"
        "[decay]\n"
        f"half_life_days = {dumped['decay']['half_life_days']}\n\n"
        "[mood]\n"
        f"default = {dumped['mood']['default']}\n"
        f"smoothing = {dumped['mood']['smoothing']}\n\n"
        "[retrieval]\n"
        f"resistance_threshold = {dumped['retrieval']['resistance_threshold']}\n\n"
        "[federation]\n"
        f"enabled_default = {str(dumped['federation']['enabled_default']).lower()}\n"
        f"dsl_rules = [{dsl_rules}]\n\n"
        "[federation.discovery]\n"
        f"only_dot_pvrclawk = {str(discovery['only_dot_pvrclawk']).lower()}\n"
        f"allow_no_git_boundary = {str(discovery['allow_no_git_boundary']).lower()}\n"
        f"max_git_lookup_levels = {discovery['max_git_lookup_levels']}\n"
        f"candidate_paths = [{candidate_paths}]\n"
        f"external_roots = [{external_roots}]\n\n"
        "[federation.scoring]\n"
        f"root_importance_base = {scoring['root_importance_base']}\n"
        f"host_relevance_base = {scoring['host_relevance_base']}\n"
        f"root_distance_decay = {scoring['root_distance_decay']}\n"
        f"host_distance_decay = {scoring['host_distance_decay']}\n"
        f"cross_bank_link_weight = {scoring['cross_bank_link_weight']}\n"
    )
    for rule in scoring["bank_path_penalties"]:
        content += (
            "\n[[federation.scoring.bank_path_penalties]]\n"
            f'pattern = "{rule["pattern"]}"\n'
            f"multiplier = {rule['multiplier']}\n"
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
    parsed = _parse_value(value)
    if "." not in key:
        setattr(config, key, parsed)
        write_config(path, config)
        return config

    parts = key.split(".")
    target = config
    for part in parts[:-1]:
        target = getattr(target, part)
    setattr(target, parts[-1], parsed)
    write_config(path, config)
    return config
