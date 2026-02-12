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
