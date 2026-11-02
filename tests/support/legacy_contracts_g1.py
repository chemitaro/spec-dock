"""Canonical fixtures for the common contracts that iss-00440 moved off the schema-3 fixtures (group G1).

    world = chain_world(tmp_path, monkeypatch, capsys)            # init-1 / epic-2 / iss-3 on the fake GitHub
    record = select_record(world, "iss-00003", 3)                 # the direct selection record's path
    code, out, err = raw(world, "active", "show")                 # text output (world.run always adds --json)

Every helper works on a CanonicalWorld/WriteWorld; nothing here reads `.meta.json` or a schema-3 workspace.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import spec_dock
from spec_dock.cli import main
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import REPOSITORY, CanonicalWorld
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    import pytest

RECORD_TIME = "2026-10-26T00:00:00Z"
# The package this test imported (the candidate, or the pre-removal code under PYTHONPATH); child processes use it.
SOURCE = Path(spec_dock.__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
# A child process gets the same scheduler stand-ins as tests/conftest.py's session guard: it never reaches a
# real service manager. Run it as `python -c CHILD_ENTRY ...argv` (or prepend CHILD_SETUP to a driver).
CHILD_SETUP = (
    "import sys\n"
    f"sys.path.insert(0, {str(ROOT)!r})\n"
    "from pathlib import Path\n"
    "from spec_dock.runtime.application import canonical_schedule\n"
    "from spec_dock.runtime.infra import canonical_scheduling, runtime_environment\n"
    "from tests.support.canonical_sync import FakeScheduler\n"
    "canonical_scheduling.scheduler_for = lambda kind, **_k: FakeScheduler(kind, simulate_run=True)\n"
    "canonical_scheduling.spec_dock_executable = lambda: Path('/opt/spec-dock/bin/spec-dock')\n"
    "runtime_environment.detect_service_manager = lambda environment, **_k: environment\n"
    "canonical_schedule.FIRST_RUN_WAIT = 0.0\n"
)
CHILD_ENTRY = CHILD_SETUP + "from spec_dock.cli import main\nsys.exit(main(sys.argv[1:]))\n"


def chain_world(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    write: bool = False,
    sibling: bool = False,
) -> CanonicalWorld:
    """init-00001 / epic-00002 / iss-00003 (and iss-00004 when `sibling`) with their catalog directories."""
    world = (WriteWorld if write else CanonicalWorld).create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    if sibling:
        world.scope("issue", 4, "other", parent=2)
    return world


def select_record(
    world: CanonicalWorld,
    scope_id: str,
    number: int,
    *,
    checkout: Path | None = None,
    branch: str | None = None,
) -> Path:
    """Publish a direct selection record as `work start` does and return its path."""
    from spec_dock.runtime.application.project_context import resolve_context
    from spec_dock.runtime.domain.work_target import WorkTarget
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    root = checkout or world.main
    context = resolve_context(str(root), root)
    with WorkTargetStore(root) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                scope_id,
                f"gh:{REPOSITORY}#{number}",
                branch or context.branch or "main",
                RECORD_TIME,
                context.clone_identity,
                context.worktree_identity,
            )
        )
        return store.path / handle.basename


def records(root: Path) -> list[Path]:
    return sorted((root / "spec-dock/.agent/work-target").glob("target-*.json"))


def token(record: Path) -> str:
    return record.name[len("target-") : -len(".json")]


def clears(effects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Only the selection effects; canonical clear and start add active.link effects after them."""
    return [effect for effect in effects if effect["kind"].startswith("selection.")]


def without_links(effects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [effect for effect in effects if effect["kind"] != "active.link"]


def raw(world: CanonicalWorld, *argv: str, checkout: Path | None = None) -> tuple[int, str, str]:
    """Run the CLI in process without --json."""
    code = main(["--project", str(checkout or world.main), *argv])
    captured = world.capsys.readouterr()
    return code, captured.out, captured.err


def run_process(world: CanonicalWorld, *argv: str, checkout: Path | None = None, timeout: float = 30) -> Any:
    """Run the CLI in a child process with the world's environment (fake gh on PATH, temporary state)."""
    return subprocess.run(
        [
            sys.executable,
            "-c",
            CHILD_ENTRY,
            "--project",
            str(checkout or world.main),
            *argv,
            "--json",
        ],
        env=child_environment(),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def child_environment() -> dict[str, str]:
    return dict(os.environ, PYTHONPATH=str(SOURCE))


def head_state(root: Path) -> tuple[str, str]:
    return git(root, "rev-parse", "HEAD"), git(root, "branch", "--show-current")


def payload_of(completed: Any) -> dict[str, Any]:
    return json.loads(completed.stdout)


def run_err(world: CanonicalWorld, *argv: str, checkout: Path | None = None) -> tuple[int, dict[str, Any], str]:
    """Like world.run, but also return stderr (world.run discards it)."""
    code, out, err = raw(world, *argv, "--json", checkout=checkout)
    return code, json.loads(out), err


def start_effects(effects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The Git and selection effects of work start; canonical start adds link and in-progress follow-ups after them."""
    core = ("git.branch.create", "git.checkout", "selection.clear", "selection.publish")
    return [effect for effect in effects if effect["kind"] in core]


def commit(root: Path, message: str, *paths: str) -> None:
    git(root, "add", "-f", "--", *(paths or (".",)))
    git(root, "commit", "-qm", message)
