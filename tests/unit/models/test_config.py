from pvrclawk.membank.models.config import AppConfig


def test_config_defaults():
    cfg = AppConfig()
    assert cfg.prune.auto_threshold == 20
    assert cfg.decay.half_life_days == 7
    assert cfg.mood.default == 0.5
