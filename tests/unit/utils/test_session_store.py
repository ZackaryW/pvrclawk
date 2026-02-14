from pathlib import Path

from pvrclawk.utils.session_store import resolve_session_bucket, resolve_session_store_root, target_hash


def test_target_hash_is_stable_for_path(tmp_path: Path):
    root = tmp_path / ".pvrclawk"
    h1 = target_hash(root)
    h2 = target_hash(root)
    assert h1 == h2
    assert len(h1) == 64


def test_resolve_session_store_root_uses_env_override(monkeypatch, tmp_path: Path):
    override = tmp_path / "custom-store"
    monkeypatch.setenv("PVRCLAWK_SESSION_STORE_ROOT", str(override))
    assert resolve_session_store_root() == override.resolve()


def test_resolve_session_store_root_defaults_to_home_config(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("PVRCLAWK_SESSION_STORE_ROOT", raising=False)
    fake_home = tmp_path / "fake-home"
    fake_home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(fake_home))
    assert resolve_session_store_root() == (fake_home / ".config" / "pvrclawk").resolve()


def test_resolve_session_bucket_appends_sessions_and_hash(monkeypatch, tmp_path: Path):
    override = tmp_path / "store"
    monkeypatch.setenv("PVRCLAWK_SESSION_STORE_ROOT", str(override))
    bucket = resolve_session_bucket(tmp_path / "project" / ".pvrclawk")
    assert bucket.parent == (override / "sessions").resolve()
