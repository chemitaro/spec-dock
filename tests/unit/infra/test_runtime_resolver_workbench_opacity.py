from __future__ import annotations

from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import delete_node
    finally:
        sys.path.pop(0)
    return delete_node


def test_delete_fallback_scan_prunes_workbench_and_preserves_near_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    delete_node = _runtime_modules()
    specdock_dir = tmp_path / "spec-dock"
    initiatives_root = specdock_dir / "initiatives"
    valid_dir = initiatives_root / ".workbench-copy" / "iss-00001-valid"

    def guarded_walk(root: Path, *, topdown: bool):
        assert Path(root) == initiatives_root
        assert topdown is True
        child_dirs = [".workbench", ".workbench-copy"]
        yield initiatives_root, child_dirs, []
        if ".workbench" in child_dirs:
            raise AssertionError("walk attempted to enter .workbench")
        yield initiatives_root / ".workbench-copy", ["iss-00001-valid"], []
        yield valid_dir, [], []

    monkeypatch.setattr(delete_node.os, "walk", guarded_walk)

    matches = delete_node._matching_target_directories(
        specdock_dir,
        canonical_id="iss-00001",
        kind="issue",
    )

    # The near-name branch remains traversable, but it is not a canonical managed-node location.
    assert matches == []
