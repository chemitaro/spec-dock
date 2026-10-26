"""The catalog lock: a flock on the catalog directory, separate from the clone Start lock (contract C4)."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.catalog_lock import CatalogLock, CatalogLockBusy
from spec_dock.runtime.infra.start_lock import StartLock

if TYPE_CHECKING:
    from pathlib import Path

_TRY = (
    "from pathlib import Path; import sys; "
    "from spec_dock.runtime.infra.catalog_lock import CatalogLock; "
    "lock=CatalogLock(Path(sys.argv[1]), timeout=0); lock.__enter__(); lock.__exit__(None,None,None)"
)


def test_another_process_cannot_take_the_catalog_lock_while_it_is_held(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    with CatalogLock(catalog, timeout=0):
        blocked = subprocess.run(
            [sys.executable, "-c", _TRY, str(catalog)], capture_output=True, text=True, check=False
        )
        assert blocked.returncode != 0 and "CatalogLockBusy" in blocked.stderr
    available = subprocess.run([sys.executable, "-c", _TRY, str(catalog)], capture_output=True, text=True, check=False)
    assert available.returncode == 0, available.stderr
    assert list(catalog.iterdir()) == []


def test_a_busy_lock_gives_up_after_the_timeout(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    source = (
        "from pathlib import Path; import sys,time; "
        "from spec_dock.runtime.infra.catalog_lock import CatalogLock; "
        "lock=CatalogLock(Path(sys.argv[1]), timeout=0); lock.__enter__(); print('held',flush=True); time.sleep(30)"
    )
    owner = subprocess.Popen([sys.executable, "-c", source, str(catalog)], stdout=subprocess.PIPE, text=True)
    try:
        assert owner.stdout is not None and owner.stdout.readline() == "held\n"
        with pytest.raises(CatalogLockBusy):
            CatalogLock(catalog, timeout=0.2).__enter__()
    finally:
        owner.kill()
        owner.wait(timeout=5)
        if owner.stdout is not None:
            owner.stdout.close()


def test_the_catalog_lock_and_the_start_lock_do_not_wait_for_each_other(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    common = tmp_path / "common"
    common.mkdir()
    with CatalogLock(catalog, timeout=0), StartLock(common, timeout=0):
        pass


@pytest.mark.parametrize("timeout", [-1.0, 301.0, float("nan"), float("inf")])
def test_the_timeout_must_be_finite_and_within_five_minutes(tmp_path: Path, timeout: float) -> None:
    with pytest.raises(ValueError):
        CatalogLock(tmp_path, timeout=timeout).__enter__()
