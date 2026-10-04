"""Real POSIX handles and separate processes without Git metadata writes."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy

if TYPE_CHECKING:
    from collections.abc import Iterator

ROOT = Path(__file__).resolve().parents[2]


def _environment(tmp_path: Path) -> dict[str, str]:
    environment = {key: os.environ[key] for key in ("PATH",) if key in os.environ}
    environment.update({
        "HOME": str(tmp_path),
        "PYTHONPATH": str(ROOT / "src"),
        "PYTHONNOUSERSITE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
    })
    return environment


def _git(root: Path, environment: dict[str, str], *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments], env=environment, capture_output=True, text=True, check=True, timeout=20
    )
    return result.stdout.rstrip("\n")


def _repository(tmp_path: Path, name: str, environment: dict[str, str]) -> Path:
    root = tmp_path / name
    root.mkdir()
    _git(root, environment, "init", "--initial-branch=main", "-q")
    _git(
        root,
        environment,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "--allow-empty",
        "-qm",
        "fixture",
    )
    return root


def _snapshot(common_dir: Path) -> list[tuple[str, int, str | None]]:
    entries = []
    for path in (common_dir, *sorted(common_dir.rglob("*"))):
        observed = path.lstat()
        assert stat.S_ISDIR(observed.st_mode) or stat.S_ISREG(observed.st_mode)
        entries.append((
            "." if path == common_dir else path.relative_to(common_dir).as_posix(),
            stat.S_IMODE(observed.st_mode),
            hashlib.sha256(path.read_bytes()).hexdigest() if stat.S_ISREG(observed.st_mode) else None,
        ))
    return entries


def _command(mode: str, common_dir: Path, *arguments: str) -> list[str]:
    return [sys.executable, "-B", str(Path(__file__).resolve()), mode, str(common_dir), *arguments]


@contextmanager
def _holder(
    tmp_path: Path, common_dir: Path, environment: dict[str, str]
) -> Iterator[tuple[subprocess.Popen[str], dict[str, Any]]]:
    ready = tmp_path / "ready.json"
    process = subprocess.Popen(
        _command("hold", common_dir, str(ready)),
        cwd=tmp_path,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 20
        while not ready.exists():
            assert process.poll() is None, process.communicate(timeout=5)
            assert time.monotonic() < deadline, "native holder did not become ready"
            time.sleep(0.01)
        payload = json.loads(ready.read_bytes())
        assert payload["provider"] == str((ROOT / "src/spec_dock/__init__.py").resolve())
        print(json.dumps({"native_holder": payload}, sort_keys=True))
        yield process, payload
    finally:
        if process.poll() is None:
            try:
                stdout, stderr = process.communicate(input="release\n", timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
                raise
            assert process.returncode == 0, (stdout, stderr)
        else:
            process.communicate(timeout=5)


def _probe(tmp_path: Path, common_dir: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _command("probe", common_dir),
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )


def test_main_and_linked_worktree_processes_share_one_physical_lock_without_git_writes(tmp_path: Path) -> None:
    environment = _environment(tmp_path)
    root = _repository(tmp_path, "clone", environment)
    linked = tmp_path / "linked"
    _git(root, environment, "worktree", "add", "--detach", str(linked), "HEAD")
    common = Path(_git(root, environment, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    linked_common = Path(_git(linked, environment, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    before = _snapshot(common)
    with _holder(tmp_path, common, environment) as (_, held):
        blocked = _probe(tmp_path, linked_common, environment)
        assert blocked.returncode == 3 and json.loads(blocked.stdout) == {"status": "busy"}, blocked.stderr
        assert _snapshot(common) == before
    acquired = _probe(tmp_path, linked_common, environment)
    assert acquired.returncode == 0 and acquired.stderr == "", acquired
    assert json.loads(acquired.stdout)["identity"] == held["identity"]
    assert _snapshot(common) == before


def test_independent_clone_has_its_own_physical_lock(tmp_path: Path) -> None:
    environment = _environment(tmp_path)
    first = _repository(tmp_path, "first", environment) / ".git"
    second_root = tmp_path / "second"
    _git(first.parent, environment, "clone", "--no-hardlinks", str(first.parent), str(second_root))
    second = second_root / ".git"
    before = (_snapshot(first), _snapshot(second))
    with _holder(tmp_path, first, environment) as (_, held):
        acquired = _probe(tmp_path, second, environment)
        assert acquired.returncode == 0 and acquired.stderr == "", acquired
        assert json.loads(acquired.stdout)["identity"] != held["identity"]
    assert (_snapshot(first), _snapshot(second)) == before


def test_terminated_owner_releases_native_start_lock_without_pid_recovery(tmp_path: Path) -> None:
    environment = _environment(tmp_path)
    common = _repository(tmp_path, "clone", environment) / ".git"
    before = _snapshot(common)
    with _holder(tmp_path, common, environment) as (process, held):
        process.kill()
        assert process.wait(timeout=5) != 0
        acquired = _probe(tmp_path, common, environment)
        assert acquired.returncode == 0 and acquired.stderr == "", acquired
        assert json.loads(acquired.stdout)["identity"] == held["identity"]
    assert _snapshot(common) == before


def _native_process() -> int:
    import spec_dock

    mode, common = sys.argv[1], Path(sys.argv[2])
    assert Path(spec_dock.__file__).resolve() == (ROOT / "src/spec_dock/__init__.py").resolve()
    try:
        with StartLock(common, timeout=0) as held:
            held.verify()
            payload = {
                "status": "acquired",
                "identity": asdict(held.identity),
                "platform": sys.platform,
                "python": sys.version,
                "provider": str(Path(spec_dock.__file__).resolve()),
            }
            if mode == "hold":
                ready = Path(sys.argv[3])
                stage = ready.with_suffix(".stage")
                stage.write_text(json.dumps(payload), encoding="utf-8")
                stage.replace(ready)
                assert sys.stdin.readline() == "release\n"
            else:
                assert mode == "probe"
                print(json.dumps(payload, sort_keys=True))
    except StartLockBusy:
        print(json.dumps({"status": "busy"}))
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(_native_process())
