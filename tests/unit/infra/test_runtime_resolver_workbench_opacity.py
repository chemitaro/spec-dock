from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import delegated_authoring, delete_node
        from spec_dock_runtime.infra import assurance_store
    finally:
        sys.path.pop(0)
    return assurance_store, delete_node, delegated_authoring


def _write_meta(path: Path, *, node_id: str, node_type: str = "issue") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"id": node_id, "type": node_type}) + "\n",
        encoding="utf-8",
    )


def test_assurance_issue_scan_prunes_workbench_and_preserves_near_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assurance_store, _, _ = _runtime_modules()
    initiatives_root = tmp_path / "spec-dock" / "initiatives"
    valid_dir = initiatives_root / ".workbench-copy" / "iss-00001-valid"

    def guarded_walk(root: Path, *, topdown: bool):
        assert Path(root) == initiatives_root
        assert topdown is True
        child_dirs = [".workbench", ".workbench-copy"]
        yield initiatives_root, child_dirs, []
        if ".workbench" in child_dirs:
            raise AssertionError("walk attempted to enter .workbench")
        yield initiatives_root / ".workbench-copy", ["iss-00001-valid"], []
        yield valid_dir, [], [".meta.json"]

    monkeypatch.setattr(assurance_store.os, "walk", guarded_walk)
    _write_meta(valid_dir / ".meta.json", node_id="iss-00001")

    records = assurance_store.AssuranceStore(tmp_path)._issue_records()

    assert [record.issue_id for record in records] == ["iss-00001"]
    assert records[0].issue_dir == valid_dir.resolve()


def test_delete_fallback_scan_prunes_workbench_and_preserves_near_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, delete_node, _ = _runtime_modules()
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


def test_delegated_scope_scan_prunes_workbench_and_preserves_near_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, delegated_authoring = _runtime_modules()
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
        yield valid_dir, [], [".meta.json"]

    monkeypatch.setattr(delegated_authoring.os, "walk", guarded_walk)
    _write_meta(valid_dir / ".meta.json", node_id="iss-00001")

    resolved = delegated_authoring._resolve_scope_dir(specdock_dir, "iss-00001")

    assert resolved == valid_dir


def test_delegated_scope_active_fallback_rejects_workbench_target(tmp_path: Path) -> None:
    _, _, delegated_authoring = _runtime_modules()
    specdock_dir = tmp_path / "spec-dock"
    hidden_dir = specdock_dir / "initiatives" / "init-00001-parent" / ".workbench" / "iss-00001-hidden"
    _write_meta(hidden_dir / ".meta.json", node_id="iss-00001")
    active_issue = specdock_dir / "active" / "issue"
    active_issue.parent.mkdir(parents=True)
    active_issue.symlink_to(hidden_dir, target_is_directory=True)

    resolved = delegated_authoring._resolve_scope_dir(specdock_dir, "iss-00001")

    assert resolved is None
