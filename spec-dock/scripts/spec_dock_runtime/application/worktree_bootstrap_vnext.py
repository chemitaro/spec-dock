"""Explicit bounded consumer bootstrap with a target-only diagnostic record."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import os
import signal
import subprocess
import threading
from typing import TYPE_CHECKING

from spec_dock_runtime.application.worktree import _close_fd, _open_directory_no_follow, _verify_worktree_path_binding
from spec_dock_runtime.application.worktree_vnext import show_worktree
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.infra.control_store import control_directory, load_control
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class BootstrapOutcome:
    id: str
    status: str
    started: bool
    exit_code: int | None
    timed_out: bool
    diagnostic: str


def _record_path(common_dir: Path, target_id: str) -> Path:
    return control_directory(common_dir) / "bootstrap" / f"{target_id}.json"


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _publish_record(path: Path, *, target_id: str, status: str, attempt: int, exit_code: int | None) -> None:
    directory = path.parent
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink():
        raise ValueError("bootstrap record directory is redirected")
    previous = read_guarded_json(path)
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "worktree_id": target_id,
            "status": status,
            "attempt": attempt,
            "exit_code": exit_code,
            "updated_at": _stamp(),
        },
        expected_identity=previous[1] if previous is not None else None,
    )


def _run_make(path: Path, *, timeout: float) -> tuple[bool, int | None, bool, str]:
    try:
        process = subprocess.Popen(
            ["make", "init"],
            cwd=path,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError:
        return False, None, False, "make init could not start"
    stream = process.stdout
    assert stream is not None

    def drain() -> None:
        with stream:
            while stream.read(4096):
                pass

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    timed_out = False
    try:
        exit_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        exit_code = process.wait(timeout=10)
    reader.join(timeout=1)
    if reader.is_alive():
        timed_out = True
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
        reader.join(timeout=10)
    return True, exit_code, timed_out, "make init finished; output omitted"


def bootstrap_worktree(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    reference: str,
    recover: bool = False,
    dry_run: bool = False,
    offline: bool = False,
    timeout: float = 300.0,
    lock_timeout: float = 0.0,
) -> BootstrapOutcome:
    """Run make init only after explicit selection; record partial effects for this target."""
    if offline:
        raise ValueError("worktree bootstrap is unavailable offline")
    if recover and dry_run:
        raise ValueError("worktree bootstrap recovery cannot be combined with dry-run")
    if timeout <= 0:
        raise ValueError("bootstrap timeout must be positive")
    target = show_worktree(repo_root=repo_root, common_dir=common_dir, reference=reference)
    if target.id is None or not target.registered or target.bare or target.head is None:
        raise ValueError("bootstrap target must be an active registered worktree")
    if dry_run:
        return BootstrapOutcome(target.id, "planned", False, None, False, "make init")
    path = target.path
    lease_fd = _open_directory_no_follow(path)
    try:
        fcntl.flock(lease_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _verify_worktree_path_binding(path, lease_fd)
        record_path = _record_path(common_dir, target.id)
        with WriterLock(common_dir, timeout=lock_timeout):
            admit_writer(
                load_control(common_dir),
                common_dir=common_dir,
                worktree_id=worktree_id,
                engine_digest=engine_digest,
                expected_epoch=expected_epoch,
            )
            previous = read_guarded_json(record_path)
            pending = previous is not None and previous[0].get("status") in {"running", "partial"}
            if recover:
                if not pending:
                    raise ValueError("bootstrap target has no unresolved attempt to recover")
                attempt = int(previous[0]["attempt"])
                prior_exit = previous[0].get("exit_code")
                _publish_record(
                    record_path, target_id=target.id, status="reconciled", attempt=attempt, exit_code=prior_exit
                )
                return BootstrapOutcome(target.id, "reconciled", False, prior_exit, False, "attempt acknowledged")
            if pending:
                raise ValueError("bootstrap target has an unresolved attempt; inspect effects before recovery")
            attempt = 1 if previous is None else int(previous[0]["attempt"]) + 1
            _publish_record(record_path, target_id=target.id, status="running", attempt=attempt, exit_code=None)
        started, exit_code, timed_out, diagnostic = _run_make(path, timeout=timeout)
        status = "succeeded" if started and exit_code == 0 and not timed_out else ("partial" if started else "failed")
        with WriterLock(common_dir, timeout=lock_timeout):
            _publish_record(record_path, target_id=target.id, status=status, attempt=attempt, exit_code=exit_code)
        return BootstrapOutcome(target.id, status, started, exit_code, timed_out, diagnostic)
    finally:
        _close_fd(lease_fd)
