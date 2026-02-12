"""Update configured skill repositories via git pull."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class UpdateResult:
    repo: Path
    status: str
    message: str


def update_skill_repos(repos: list[Path]) -> list[UpdateResult]:
    results: list[UpdateResult] = []
    for repo in repos:
        if not (repo / ".git").exists():
            results.append(UpdateResult(repo=repo, status="skipped", message="No .git directory"))
            continue
        try:
            proc = subprocess.run(
                ["git", "pull"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            msg = proc.stdout.strip() or "git pull succeeded"
            results.append(UpdateResult(repo=repo, status="updated", message=msg))
        except subprocess.CalledProcessError as exc:
            err = (exc.stderr or exc.stdout or "git pull failed").strip()
            results.append(UpdateResult(repo=repo, status="failed", message=err))
    return results

