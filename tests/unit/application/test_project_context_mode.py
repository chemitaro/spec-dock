"""Workspace declaration versions 3 and 4 select the legacy or the canonical mode."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.project_context import (
    probe_workspace_mode,
    read_workspace_declaration,
    workspace_mode,
)

if TYPE_CHECKING:
    from pathlib import Path

NEW = "specdock.worktree-writer/v1"
OLD = "specdock.writer/v1"


def _declare(root: Path, payload: object) -> Path:
    path = root / "spec-dock/workspace.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.mark.parametrize(("version", "mode"), [(3, "legacy"), (4, "canonical")])
@pytest.mark.parametrize("protocol", [NEW, OLD])
def test_versions_three_and_four_select_a_mode(tmp_path: Path, version: int, mode: str, protocol: str) -> None:
    declaration = read_workspace_declaration(
        _declare(tmp_path, {"schema_version": version, "writer_protocol": protocol})
    )
    assert workspace_mode(declaration) == mode
    assert probe_workspace_mode(tmp_path) == mode


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 5, "writer_protocol": NEW},
        {"schema_version": 2, "writer_protocol": NEW},
        {"schema_version": True, "writer_protocol": NEW},
        {"schema_version": "4", "writer_protocol": NEW},
        {"schema_version": 4, "writer_protocol": "specdock.unknown/v9"},
        {"writer_protocol": NEW},
        ["not", "an", "object"],
    ],
)
def test_other_declarations_are_refused_and_never_probe_as_a_mode(tmp_path: Path, payload: object) -> None:
    with pytest.raises(ValueError):
        read_workspace_declaration(_declare(tmp_path, payload))
    assert probe_workspace_mode(tmp_path) is None


def test_probe_never_raises_for_missing_or_broken_files(tmp_path: Path) -> None:
    assert probe_workspace_mode(tmp_path) is None
    path = tmp_path / "spec-dock/workspace.json"
    path.parent.mkdir()
    path.write_bytes(b"{broken")
    assert probe_workspace_mode(tmp_path) is None
    path.unlink()
    path.mkdir()
    assert probe_workspace_mode(tmp_path) is None


def test_mode_of_a_mapping_requires_a_known_version() -> None:
    with pytest.raises(ValueError):
        workspace_mode({"schema_version": 5})
