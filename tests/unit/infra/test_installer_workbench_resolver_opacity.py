from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock import cli

if TYPE_CHECKING:
    import pytest


def _write_meta(path: Path, *, node_id: str, node_type: str = "issue") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"id": node_id, "type": node_type}) + "\n",
        encoding="utf-8",
    )


def test_manifest_target_fallback_prunes_workbench_before_descendant_access(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
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

    monkeypatch.setattr(cli.os, "walk", guarded_walk)
    _write_meta(valid_dir / ".meta.json", node_id="iss-00001")

    resolved = cli._resolve_manifest_target_dir(
        specdock_dir,
        "issue",
        expected_id="iss-00001",
        persisted_path=None,
    )

    assert resolved == valid_dir.resolve()


def test_manifest_target_rejects_direct_persisted_workbench_candidate(tmp_path: Path) -> None:
    specdock_dir = tmp_path / "spec-dock"
    hidden_dir = specdock_dir / "initiatives" / "init-00001-parent" / ".workbench" / "iss-00001-hidden"
    _write_meta(hidden_dir / ".meta.json", node_id="iss-00001")

    resolved = cli._resolve_manifest_target_dir(
        specdock_dir,
        "issue",
        expected_id="iss-00001",
        persisted_path=hidden_dir.relative_to(tmp_path).as_posix(),
    )

    assert resolved is None


def test_manifest_target_accepts_direct_persisted_near_name_candidate(tmp_path: Path) -> None:
    specdock_dir = tmp_path / "spec-dock"
    candidate = specdock_dir / "initiatives" / ".workbench-copy" / "iss-00001-valid"
    _write_meta(candidate / ".meta.json", node_id="iss-00001")

    resolved = cli._resolve_manifest_target_dir(
        specdock_dir,
        "issue",
        expected_id="iss-00001",
        persisted_path=candidate.relative_to(tmp_path).as_posix(),
    )

    assert resolved == candidate.resolve()
