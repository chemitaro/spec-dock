"""Artifact list/show distinguish creation types from stored evidence observations."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.artifact_query import list_artifacts, show_artifact  # noqa: E402
from spec_dock_runtime.application.artifact_vnext import create_scope_artifact, import_scope_file  # noqa: E402
from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_artifact_catalog_accepts_current_historical_unknown_and_generic_without_reading_body(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    artifacts = initiative.path / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "20260925t000000z-research-study.md").write_text("secret body", encoding="utf-8")
    (artifacts / "20260925t000001z-newtype-study.md").write_text("other secret", encoding="utf-8")
    (artifacts / "20260925t000002z--source.bin").write_bytes(b"\x00\x01")
    (artifacts / "001-note-old.md").write_text("old secret", encoding="utf-8")
    result = list_artifacts(repo_root=common["repo_root"], scope=initiative.id)
    assert len(result.items) == 4
    assert [item.artifact_id for item in result.items] == [
        "001-note",
        "20260925t000000z-research",
        "20260925t000001z",
        "20260925t000002z--source.bin",
    ]
    assert result.items[1].creation_type == "research"
    assert result.items[2].creation_type is None
    assert all(item.observed_authority == "unverified" for item in result.items)
    assert "secret" not in str(result)
    assert show_artifact(repo_root=common["repo_root"], scope=initiative.id, artifact_id="001-note") == result.items[0]


def test_root_scope_can_list_generic_but_rejects_duplicate_slots(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    root = cast("Path", common["repo_root"]) / "spec-dock" / "artifacts"
    root.mkdir(exist_ok=True)
    (root / "20260925t000000z--first.bin").write_bytes(b"x")
    result = list_artifacts(repo_root=common["repo_root"], scope="@root")
    assert len(result.items) == 1 and result.items[0].scope_id == "root"
    (root / "20260925t000000z--second.bin").write_bytes(b"y")
    with pytest.raises(ValueError, match="ARTIFACT_CATALOG_INVALID"):
        list_artifacts(repo_root=common["repo_root"], scope="@root")


def test_scope_artifact_creation_accepts_local_initiative_and_rejects_root(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    entry = create_scope_artifact(
        scope=initiative.id,
        artifact_type="research",
        title="Evidence",
        slug="evidence",
        **{key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")},
    )
    assert entry.scope_id == initiative.id
    assert entry.creation_type == "research"
    assert entry.observed_authority == "unverified"
    assert show_artifact(repo_root=common["repo_root"], scope=initiative.id, artifact_id=entry.artifact_id) == entry
    with pytest.raises(ValueError, match="Scope"):
        create_scope_artifact(
            scope="@root",
            artifact_type="research",
            title="Wrong",
            slug=None,
            **{
                key: common[key]
                for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")
            },
        )


@pytest.mark.parametrize("artifact_type", ("blank", "research", "interview", "disc", "decision-candidate", "adr"))
def test_six_creation_types_remain_distinct_from_observed_authority(tmp_path: Path, artifact_type: str) -> None:
    common = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    entry = create_scope_artifact(
        scope=initiative.id,
        artifact_type=artifact_type,
        title="Evidence",
        slug="evidence",
        **{key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")},
    )
    assert entry.artifact_id
    assert entry.observed_authority == "unverified"
    assert entry.creation_type == (None if artifact_type == "blank" else artifact_type)


def test_root_file_import_keeps_source_and_returns_private_catalog_entry(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    source = tmp_path / "external-secret.bin"
    source.write_bytes(b"private contents")
    entry = import_scope_file(
        scope="@root",
        source_path=source,
        **{key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")},
    )
    assert entry.scope_id == "root"
    assert entry.creation_type is None
    assert entry.observed_authority == "unverified"
    assert source.read_bytes() == b"private contents"
    assert str(source) not in str(entry)
    assert "private contents" not in str(entry)
