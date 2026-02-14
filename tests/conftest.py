from click.testing import CliRunner
import pytest


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated_session_store(monkeypatch, tmp_path):
    monkeypatch.setenv("PVRCLAWK_SESSION_STORE_ROOT", str(tmp_path / "session-store"))
