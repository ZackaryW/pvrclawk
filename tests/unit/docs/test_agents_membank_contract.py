from pathlib import Path


def _read_membank_doc() -> str:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "AGENTS" / "membank.md").read_text(encoding="utf-8")


def test_membank_doc_keeps_mandatory_order_for_agents():
    content = _read_membank_doc()
    assert "## Mandatory Order (Do This First)" in content


def test_membank_doc_keeps_session_precedence_without_repo_env_overrides():
    content = _read_membank_doc()
    assert "1. `--session <uuid>` override on `membank` group" in content
    assert "2. `PVRCLAWK_SESSION` environment variable" in content
    assert "3. Active session from session index" in content
    assert "PVRCLAWK_SESSION_STORE_ROOT" not in content


def test_membank_doc_avoids_legacy_local_session_runtime_path():
    content = _read_membank_doc()
    assert "Active `.pvrclawk/session.json`" not in content
