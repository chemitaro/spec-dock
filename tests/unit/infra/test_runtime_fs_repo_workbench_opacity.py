import json
from pathlib import Path
import sys

import pytest


def _runtime_fs_repo():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import fs_repo
    finally:
        sys.path.pop(0)
    return fs_repo


def _write_meta(path: Path, *, node_id: str = "init-00001") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "type": "initiative",
            "id": node_id,
            "title": "Platform",
            "slug": "platform",
        })
        + "\n",
        encoding="utf-8",
    )


def test_workbench_readme_and_payloads_remain_semantically_opaque(tmp_path: Path) -> None:
    fs_repo = _runtime_fs_repo()
    specdock_dir = tmp_path / "spec-dock"
    initiative_dir = specdock_dir / "initiatives" / "init-00001-platform"
    _write_meta(initiative_dir / ".meta.json")
    baseline = fs_repo.load_node_records(specdock_dir)

    workbench = initiative_dir / ".workbench"
    workbench.mkdir()
    (workbench / "README.md").write_text("# Workbench\n", encoding="utf-8")
    _write_meta(workbench / "fake-node" / ".meta.json")
    (workbench / "legacy" / "meta.json").parent.mkdir(parents=True, exist_ok=True)
    (workbench / "legacy" / "meta.json").write_text("not json\n", encoding="utf-8")
    (workbench / "decisions").mkdir()
    (workbench / "decisions" / "adr-999.md").write_text("# Fake ADR\n", encoding="utf-8")
    (workbench / "binary.bin").write_bytes(b"\x00\x01\x02\xff")
    (workbench / "invalid-utf8.bin").write_bytes(b"\xff\xfe\x80")

    assert fs_repo.load_node_records(specdock_dir) == baseline


@pytest.mark.parametrize("metadata_name", [".meta.json", "meta.json"])
def test_node_metadata_discovery_preserves_near_name_behavior(tmp_path: Path, metadata_name: str) -> None:
    fs_repo = _runtime_fs_repo()
    specdock_dir = tmp_path / "spec-dock"
    initiative_dir = specdock_dir / "initiatives" / "init-00001-platform"
    _write_meta(initiative_dir / ".meta.json")
    metadata_path = initiative_dir / ".workbench-copy" / metadata_name
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text("not json\n", encoding="utf-8")

    with pytest.raises((RuntimeError, json.JSONDecodeError)):
        fs_repo.load_node_records(specdock_dir)


def test_current_metadata_outside_workbench_remains_strict(tmp_path: Path) -> None:
    fs_repo = _runtime_fs_repo()
    specdock_dir = tmp_path / "spec-dock"
    initiative_dir = specdock_dir / "initiatives" / "init-00001-platform"
    _write_meta(initiative_dir / ".meta.json")
    malformed_path = initiative_dir / "notes" / ".meta.json"
    malformed_path.parent.mkdir(parents=True, exist_ok=True)
    malformed_path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match=r"Invalid \.meta\.json \(expected object\)"):
        fs_repo.load_node_records(specdock_dir)


@pytest.mark.parametrize(
    ("function_name", "metadata_name"),
    [("_iter_node_meta_paths", ".meta.json"), ("_find_legacy_meta_paths", "meta.json")],
)
def test_metadata_walk_prunes_workbench_before_descendant_access(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    function_name: str,
    metadata_name: str,
) -> None:
    fs_repo = _runtime_fs_repo()
    initiatives_root = tmp_path / "initiatives"

    def guarded_walk(root: Path, *, topdown: bool):
        assert Path(root) == initiatives_root
        assert topdown is True
        child_dirs = [".workbench", "regular"]
        yield initiatives_root, child_dirs, []
        if ".workbench" in child_dirs:
            raise AssertionError("walk attempted to enter .workbench")
        yield initiatives_root / "regular", [], [metadata_name]

    monkeypatch.setattr(fs_repo.os, "walk", guarded_walk)

    result = getattr(fs_repo, function_name)(initiatives_root)

    assert result == [initiatives_root / "regular" / metadata_name]
