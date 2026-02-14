from pathlib import Path

from pvrclawk.utils.config import (
    AppConfig,
    load_config,
    set_config_value,
    write_config,
)


def test_app_config_defaults():
    cfg = AppConfig()
    assert cfg.prune.auto_threshold == 20
    assert cfg.decay.half_life_days == 7
    assert cfg.mood.default == 0.5
    assert cfg.mood.smoothing == 0.1
    assert cfg.auto_archive_active is True
    assert cfg.federation.discovery.only_dot_pvrclawk is True
    assert cfg.federation.discovery.max_git_lookup_levels == 10
    assert cfg.federation.scoring.root_importance_base == 1.0
    assert cfg.federation.scoring.host_relevance_base == 1.0


def test_auto_archive_active_configurable():
    cfg = AppConfig(auto_archive_active=False)
    assert cfg.auto_archive_active is False


def test_write_and_load_config_roundtrip(tmp_path: Path):
    path = tmp_path / "config.toml"
    cfg = AppConfig(auto_archive_active=False)
    cfg.federation.discovery.external_roots = ["/tmp/remote-a"]
    cfg.federation.discovery.candidate_paths = ["custom-bank"]
    cfg.federation.scoring.host_distance_decay = 0.8
    write_config(path, cfg)
    loaded = load_config(path)
    assert loaded.auto_archive_active is False
    assert loaded.prune.auto_threshold == 20
    assert loaded.federation.discovery.external_roots == ["/tmp/remote-a"]
    assert loaded.federation.discovery.candidate_paths == ["custom-bank"]
    assert loaded.federation.scoring.host_distance_decay == 0.8


def test_set_config_value(tmp_path: Path):
    path = tmp_path / "config.toml"
    write_config(path, AppConfig())
    updated = set_config_value(path, "mood.smoothing", "0.3")
    assert updated.mood.smoothing == 0.3


def test_set_auto_archive_active(tmp_path: Path):
    path = tmp_path / "config.toml"
    write_config(path, AppConfig())
    updated = set_config_value(path, "auto_archive_active", "false")
    assert updated.auto_archive_active is False


def test_set_config_nested_federation_value(tmp_path: Path):
    path = tmp_path / "config.toml"
    write_config(path, AppConfig())
    updated = set_config_value(path, "federation.discovery.max_git_lookup_levels", "12")
    assert updated.federation.discovery.max_git_lookup_levels == 12
