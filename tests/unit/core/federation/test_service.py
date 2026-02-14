from pathlib import Path

import pytest

from pvrclawk.membank.core.federation.service import FederatedMembankService
from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.nodes import Memory
from pvrclawk.utils.config import FederationScoringConfig


def _init_bank(path: Path, content: str, tag: str) -> None:
    storage = StorageEngine(path)
    storage.init_db()
    node = Memory(content=content)
    node.add_tag(tag, 1.0)
    storage.save_node(node, "memory")


def test_discover_banks_requires_git_boundary_by_default(tmp_path: Path):
    host = tmp_path / "project" / ".pvrclawk"
    _init_bank(host, "host note", "federation")
    cfg = AppConfig()
    service = FederatedMembankService(host, cfg)
    with pytest.raises(ValueError, match="Could not locate .git"):
        service.discover_banks()


def test_discover_banks_includes_dot_and_configured_candidates(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host = repo / "apps" / "host" / ".pvrclawk"
    sibling = repo / "libs" / "shared" / ".pvrclawk"
    custom = repo / "custombank"
    _init_bank(host, "host note", "federation")
    _init_bank(sibling, "sibling note", "federation")
    _init_bank(custom, "custom note", "federation")

    cfg = AppConfig()
    cfg.federation.discovery.candidate_paths = ["custombank"]
    service = FederatedMembankService(host, cfg)
    contexts = service.discover_banks()
    roots = {ctx.root for ctx in contexts}
    assert host in roots
    assert sibling in roots
    assert custom in roots


def test_root_proximity_increases_importance(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host = repo / "apps" / "host" / ".pvrclawk"
    near_root = repo / ".pvrclawk"
    far_from_root = repo / "apps" / "host" / "nested" / ".pvrclawk"
    _init_bank(host, "host", "federation")
    _init_bank(near_root, "near root", "federation")
    _init_bank(far_from_root, "far root", "federation")

    cfg = AppConfig()
    cfg.federation.scoring.host_relevance_base = 1.0
    cfg.federation.scoring.host_distance_decay = 0.0
    cfg.federation.scoring.root_distance_decay = 0.8
    service = FederatedMembankService(host, cfg)
    contexts = {ctx.root: ctx for ctx in service.discover_banks()}
    assert service._bank_multiplier(contexts[near_root]) > service._bank_multiplier(contexts[far_from_root])


def test_host_proximity_increases_relevance(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host = repo / "apps" / "host" / ".pvrclawk"
    close_to_host = repo / "apps" / "host" / "nested" / ".pvrclawk"
    far_from_host = repo / ".pvrclawk"
    _init_bank(host, "host", "federation")
    _init_bank(close_to_host, "close host", "federation")
    _init_bank(far_from_host, "far host", "federation")

    cfg = AppConfig()
    cfg.federation.scoring.root_importance_base = 1.0
    cfg.federation.scoring.root_distance_decay = 0.0
    cfg.federation.scoring.host_distance_decay = 0.8
    service = FederatedMembankService(host, cfg)
    contexts = {ctx.root: ctx for ctx in service.discover_banks()}
    assert service._bank_multiplier(contexts[close_to_host]) > service._bank_multiplier(contexts[far_from_host])


def test_regex_path_penalty_can_downrank_single_bank(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    host = repo / "apps" / "host" / ".pvrclawk"
    penalized = repo / "libs" / "legacy" / ".pvrclawk"
    neutral = repo / "libs" / "modern" / ".pvrclawk"
    _init_bank(host, "host", "federation")
    _init_bank(penalized, "legacy", "federation")
    _init_bank(neutral, "modern", "federation")

    cfg = AppConfig()
    cfg.federation.scoring.root_distance_decay = 0.0
    cfg.federation.scoring.host_distance_decay = 0.0
    cfg.federation.scoring.bank_path_penalties = [
        FederationScoringConfig.BankPathPenaltyRule(pattern=r"/legacy$", multiplier=0.25)
    ]
    service = FederatedMembankService(host, cfg)
    contexts = {ctx.root: ctx for ctx in service.discover_banks()}
    assert service._bank_multiplier(contexts[penalized]) < service._bank_multiplier(contexts[neutral])
