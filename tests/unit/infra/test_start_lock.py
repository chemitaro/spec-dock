"""Real process exclusion without any Git metadata lock file (Issue #413 D-05)."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.start_lock import StartLock

if TYPE_CHECKING:
    from pathlib import Path


def test_windows_mutex_uses_only_canonical_physical_identity() -> None:
    from spec_dock.runtime.domain.work_target import PhysicalIdentity
    from spec_dock.runtime.infra import start_lock

    identity = PhysicalIdentity("windows", "123", "00112233445566778899aabbccddeeff")
    assert start_lock.windows_mutex_name(identity) == (
        "Global\\SpecDock.Start.v1.bd36d6268c667cb9379b596ae36f9ea3cdece8d75199671d26feb8891eebc882"
    )


def test_start_lock_excludes_another_process_without_creating_files(tmp_path: Path) -> None:
    common = tmp_path / "common"
    common.mkdir()
    source = (
        "from pathlib import Path; import sys; "
        "from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy; "
        "lock=StartLock(Path(sys.argv[1]), timeout=0); "
        "lock.__enter__(); lock.__exit__(None,None,None)"
    )
    with StartLock(common, timeout=0):
        blocked = subprocess.run(
            [sys.executable, "-c", source, str(common)], capture_output=True, text=True, check=False
        )
        assert blocked.returncode != 0
        assert "StartLockBusy" in blocked.stderr
        assert list(common.iterdir()) == []
    available = subprocess.run([sys.executable, "-c", source, str(common)], capture_output=True, text=True, check=False)
    assert available.returncode == 0, available.stderr
    assert list(common.iterdir()) == []


def test_terminated_owner_releases_lock_without_cleanup(tmp_path: Path) -> None:
    common = tmp_path / "common"
    common.mkdir()
    source = (
        "from pathlib import Path; import sys,time; "
        "from spec_dock.runtime.infra.start_lock import StartLock; "
        "lock=StartLock(Path(sys.argv[1]), timeout=0); "
        "lock.__enter__(); print('held',flush=True); time.sleep(30)"
    )
    owner = subprocess.Popen([sys.executable, "-c", source, str(common)], stdout=subprocess.PIPE, text=True)
    try:
        assert owner.stdout is not None
        assert owner.stdout.readline() == "held\n"
        owner.kill()
        owner.wait(timeout=5)
        with StartLock(common, timeout=0):
            assert list(common.iterdir()) == []
    finally:
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=5)
        if owner.stdout is not None:
            owner.stdout.close()


def test_lock_keeps_physical_common_directory_and_detects_replacement(tmp_path: Path) -> None:
    common = tmp_path / "common"
    common.mkdir()
    with StartLock(common, timeout=0) as lock:
        lock.verify()
        common.rename(tmp_path / "original")
        common.mkdir()
        with pytest.raises(ValueError, match="identity changed"):
            lock.verify()
        assert list(common.iterdir()) == []


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), -1, 301])
def test_invalid_timeout_is_rejected_before_any_path_access(tmp_path: Path, timeout: float) -> None:
    with pytest.raises(ValueError, match="finite"), StartLock(tmp_path / "missing", timeout=timeout):
        pytest.fail("invalid lock acquired")
    assert list(tmp_path.iterdir()) == []
