"""Temporary clones of a bare `origin` for canonical-mode tests; no network and no user state.

remote = bare_remote(tmp_path / "remote.git")      # main holds a schema-4 declaration (and the shipped ignore rules)
main = clone(remote, tmp_path / "main")              # local identity, no auto maintenance
linked = add_worktree(main, tmp_path / "linked", "feature")
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.runtime_environment import GitInstallation, RuntimeEnvironment

if TYPE_CHECKING:
    from collections.abc import Mapping

    import pytest

SHIPPED_GITIGNORE = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/.gitignore"
CANONICAL_DECLARATION = {"schema_version": 4, "writer_protocol": "specdock.worktree-writer/v1"}


def git(root: Path, *args: str, check: bool = True, input: bytes | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], check=False, capture_output=True, input=input, env=_clean_environment()
    )
    if check and completed.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.decode(errors='replace')}")
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _clean_environment() -> dict[str, str]:
    import os

    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def configure(root: Path) -> None:
    git(root, "config", "user.name", "Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "maintenance.auto", "false")


def bare_remote(
    path: Path,
    *,
    files: Mapping[str, bytes] | None = None,
    gitignore: bool = True,
    declaration: object = CANONICAL_DECLARATION,
) -> Path:
    """A bare repository whose main branch holds one commit of the given checkout files."""
    path = path.parent.resolve() / path.name
    subprocess.run(
        ["git", "init", "-q", "--bare", "--initial-branch=main", str(path)], check=True, env=_clean_environment()
    )
    seed = path.parent / f".{path.name}.seed"
    subprocess.run(["git", "init", "-q", "--initial-branch=main", str(seed)], check=True, env=_clean_environment())
    configure(seed)
    content: dict[str, bytes] = {"spec-dock/workspace.json": (json.dumps(declaration) + "\n").encode()}
    if gitignore:
        content["spec-dock/.gitignore"] = SHIPPED_GITIGNORE.read_bytes()
    content.update(files or {})
    for relative, payload in content.items():
        target = seed / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    git(seed, "add", "-A")
    git(seed, "commit", "-qm", "seed")
    git(seed, "push", "-q", str(path), "HEAD:refs/heads/main")
    return path


def clone(remote: Path, path: Path, *options: str) -> Path:
    subprocess.run(["git", "clone", "-q", *options, str(remote), str(path)], check=True, env=_clean_environment())
    configure(path)
    return path.resolve()


def add_worktree(main: Path, path: Path, branch: str) -> Path:
    git(main, "worktree", "add", "-q", "-b", branch, str(path))
    return path.resolve()


def environment(
    *,
    git_version: tuple[int, int, int] = (2, 54, 0),
    container: bool = False,
    environ: Mapping[str, str] | None = None,
) -> RuntimeEnvironment:
    import os
    import shutil

    values = dict(os.environ if environ is None else environ)
    reported = "git version " + ".".join(str(part) for part in git_version)
    return RuntimeEnvironment(
        "darwin",
        ("/.dockerenv",) if container else (),
        GitInstallation(shutil.which("git"), git_version, reported),
        values,
    )


def isolate_user_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Point HOME and XDG_STATE_HOME at a temporary directory and drop tool-session markers."""
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    for key in ("CODEX_SANDBOX", "CLAUDECODE", "container", "REMOTE_CONTAINERS", "CODESPACES"):
        monkeypatch.delenv(key, raising=False)
    return home
