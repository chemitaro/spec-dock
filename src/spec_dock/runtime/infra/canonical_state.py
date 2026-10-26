"""Files of the state root that the periodic sync owns (contract C9): per-catalog state, locks, log, runner files.

Every file is written to a temporary name in its directory, fsynced and renamed, so readers never take a
lock. A state.json write re-reads and replaces under a short flock on its catalog directory; the cycle
lock (`cycle.lock`) is a different file so one process can hold it while it writes state.
"""

from __future__ import annotations

from contextlib import contextmanager, suppress
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import shutil
import time
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_content import RUNTIME_DIRECTORY
from spec_dock.runtime.domain.canonical_scheduler import LOG_FILE
from spec_dock.runtime.domain.canonical_sync_state import (
    AcceptedChanges,
    CatalogSyncState,
    StateFormatError,
    state_key,
)
from spec_dock.runtime.infra.catalog_runtime import runtime_directory

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from contextlib import AbstractContextManager

STATE_FILE: Final = "state.json"
CYCLE_LOCK_FILE: Final = "cycle.lock"
RUNNER_LOCK_FILE: Final = "runner.lock"
RUNNER_RECORD_FILE: Final = "runner.json"
KICK_FILE: Final = "kick"
LOG_LIMIT: Final = 1024 * 1024
_DIRECTORY_FLAGS: Final = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)


class StateUnreadable(Exception):
    """A state.json that is unreadable, malformed or of an unknown version; it is never overwritten."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


class CycleBusy(TimeoutError):
    """Another cycle (periodic or manual) is processing this catalog."""


def catalog_state_dir(root: Path, catalog: str) -> Path:
    return root / "catalogs" / state_key(catalog)


def runner_lock_path(root: Path) -> Path:
    return root / RUNNER_LOCK_FILE


def runner_record_path(root: Path) -> Path:
    return root / RUNNER_RECORD_FILE


def kick_path(root: Path) -> Path:
    return root / KICK_FILE


def write_json_atomic(directory: Path, name: str, payload: object) -> None:
    """Write `directory/name` through a temporary file, fsync and rename; the directory is created if needed."""
    directory.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    temporary = directory / f".{name}.{secrets.token_hex(8)}.tmp"
    try:
        with Path(temporary).open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).replace(directory / name)
    except BaseException:
        with suppress(OSError):
            temporary.unlink()
        raise
    descriptor = os.open(directory, _DIRECTORY_FLAGS)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read_json(path: Path) -> object | None:
    """The parsed file, None when it does not exist; malformed JSON raises ValueError."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None
    return json.loads(raw.decode("utf-8"))


def _flock(descriptor: int, *, timeout: float) -> bool:
    import fcntl

    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(0.05, remaining))


@contextmanager
def directory_lock(directory: Path, *, timeout: float = 10.0) -> Iterator[None]:
    """A flock on `directory` itself (created if needed); TimeoutError when it cannot be taken in time."""
    directory.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(directory, _DIRECTORY_FLAGS)
    try:
        if not _flock(descriptor, timeout=timeout):
            raise TimeoutError(f"{directory} is locked by another SpecDock process")
        yield
    finally:
        os.close(descriptor)  # closing the descriptor releases the flock


@contextmanager
def file_lock(path: Path, *, timeout: float = 0.0, error: type[TimeoutError] = TimeoutError) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0), 0o644)
    try:
        if not _flock(descriptor, timeout=timeout):
            raise error(f"{path} is held by another SpecDock process")
        yield
    finally:
        os.close(descriptor)


def cycle_lock(root: Path, catalog: str, *, timeout: float = 0.0) -> AbstractContextManager[None]:
    """Hold for one catalog's whole cycle; a second cycle of the same catalog raises CycleBusy (judgment Q4)."""
    return file_lock(catalog_state_dir(root, catalog) / CYCLE_LOCK_FILE, timeout=timeout, error=CycleBusy)


def _load_state(path: Path) -> CatalogSyncState | None:
    try:
        payload = read_json(path)
    except (OSError, ValueError) as error:
        raise StateUnreadable(path, str(error)) from error
    if payload is None:
        return None
    try:
        return CatalogSyncState.from_json(payload)
    except StateFormatError as error:
        raise StateUnreadable(path, str(error)) from error


def read_catalog_state(root: Path, catalog: str) -> CatalogSyncState | None:
    """Read one catalog's state.json without a lock (it is replaced by rename); None when absent."""
    return _load_state(catalog_state_dir(root, catalog) / STATE_FILE)


def update_catalog_state(
    root: Path,
    catalog: str,
    mutate: Callable[[CatalogSyncState | None], CatalogSyncState],
    *,
    timeout: float = 10.0,
) -> CatalogSyncState:
    """Re-read under the catalog directory's flock, apply `mutate` and replace the file."""
    directory = catalog_state_dir(root, catalog)
    with directory_lock(directory, timeout=timeout):
        current = _load_state(directory / STATE_FILE)
        updated = mutate(current)
        if updated != current:  # an unchanged record is not rewritten
            write_json_atomic(directory, STATE_FILE, updated.to_json())
        return updated


def move_catalog_state(root: Path, old: str, new: str) -> bool:
    """Carry a moved main checkout's state (and its baseline) to the new key unless the new key has one."""
    source, target = catalog_state_dir(root, old), catalog_state_dir(root, new)
    if source == target or not (source / STATE_FILE).is_file() or (target / STATE_FILE).exists():
        return False
    state = _load_state(source / STATE_FILE)
    assert state is not None
    update_catalog_state(root, new, lambda _current: state.evolve(catalog=new))
    shutil.rmtree(source)
    return True


def remove_catalog_state(root: Path, catalog: str) -> bool:
    directory = catalog_state_dir(root, catalog)
    if not directory.exists():
        return False
    shutil.rmtree(directory)
    return True


def append_log(root: Path, line: str, *, limit: int = LOG_LIMIT) -> None:
    """Append one line; above `limit` bytes the log keeps one older generation (`.1`). Never write file contents."""
    root.mkdir(parents=True, exist_ok=True)
    log = root / LOG_FILE
    with directory_lock(root, timeout=10.0):
        with suppress(FileNotFoundError):
            if log.stat().st_size >= limit:
                Path(log).replace(root / f"{LOG_FILE}.1")
        with Path(log).open("a", encoding="utf-8") as stream:
            stream.write(line.rstrip("\n") + "\n")


ACCEPTED_FILE: Final = "accepted.json"


def read_accepted(catalog: Path) -> AcceptedChanges:
    """`<catalog>/.runtime/accepted.json`; a missing file is empty, a malformed one raises StateUnreadable."""
    path = catalog / RUNTIME_DIRECTORY / ACCEPTED_FILE
    try:
        payload = read_json(path)
        return AcceptedChanges.empty() if payload is None else AcceptedChanges.from_json(payload)
    except (OSError, ValueError) as error:
        raise StateUnreadable(path, str(error)) from error


def write_accepted(catalog: Path, accepted: AcceptedChanges) -> None:
    """Write accepted.json under the catalog lock; the .runtime directory is opened without following links."""
    directory = runtime_directory(catalog, PurePosixPath(RUNTIME_DIRECTORY))
    write_json_atomic(directory, ACCEPTED_FILE, accepted.to_json())
