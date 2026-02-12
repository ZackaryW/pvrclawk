import subprocess
from pathlib import Path

from pvrclawk.skills.core.updater import update_skill_repos


def test_update_skill_repos_skips_non_git_repo(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo-no-git"
    (repo / "skills").mkdir(parents=True)

    def _fail_run(*args, **kwargs):
        raise AssertionError("git pull should not be called for non-git repo")

    monkeypatch.setattr("pvrclawk.skills.core.updater.subprocess.run", _fail_run)
    results = update_skill_repos([repo])

    assert len(results) == 1
    assert results[0].status == "skipped"
    assert "no .git" in results[0].message.lower()


def test_update_skill_repos_runs_git_pull_for_git_repo(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo-git"
    (repo / "skills").mkdir(parents=True)
    (repo / ".git").mkdir()
    calls: list[tuple[list[str], Path]] = []

    def _mock_run(cmd, cwd, check, capture_output, text):
        calls.append((cmd, Path(cwd)))
        return subprocess.CompletedProcess(cmd, 0, stdout="Already up to date.\n", stderr="")

    monkeypatch.setattr("pvrclawk.skills.core.updater.subprocess.run", _mock_run)
    results = update_skill_repos([repo])

    assert len(results) == 1
    assert results[0].status == "updated"
    assert calls == [(["git", "pull"], repo)]

