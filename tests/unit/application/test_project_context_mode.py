"""Only a schema-4 workspace declaration is admitted; schema 3 is reported as not migrated."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.project_context import (
    WorkspaceNotMigrated,
    declares_schema_4,
    read_workspace_declaration,
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


@pytest.mark.parametrize("protocol", [NEW, OLD])
def test_schema_four_is_admitted_and_schema_three_is_not_migrated(tmp_path: Path, protocol: str) -> None:
    declaration = read_workspace_declaration(_declare(tmp_path, {"schema_version": 4, "writer_protocol": protocol}))
    assert declaration["schema_version"] == 4
    assert declares_schema_4(tmp_path) is True
    with pytest.raises(WorkspaceNotMigrated):
        read_workspace_declaration(_declare(tmp_path, {"schema_version": 3, "writer_protocol": protocol}))
    assert declares_schema_4(tmp_path) is False


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
    assert declares_schema_4(tmp_path) is False


def test_probe_never_raises_for_missing_or_broken_files(tmp_path: Path) -> None:
    assert declares_schema_4(tmp_path) is False
    path = tmp_path / "spec-dock/workspace.json"
    path.parent.mkdir()
    path.write_bytes(b"{broken")
    assert declares_schema_4(tmp_path) is False
    path.unlink()
    path.mkdir()
    assert declares_schema_4(tmp_path) is False


@pytest.mark.parametrize(
    "text",
    [
        '{"schema_version":99,"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}',
        '{"schema_version":4,"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}',
        '{"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1","writer_protocol":"specdock.writer/v1"}',
    ],
)
def test_duplicate_member_declaration_is_ambiguous_and_not_schema_four(tmp_path: Path, text: str) -> None:
    path = tmp_path / "spec-dock/workspace.json"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        read_workspace_declaration(path)
    assert declares_schema_4(tmp_path) is False


def test_observed_context_reports_a_schema_three_declaration_that_vanished_as_a_value_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    from spec_dock.runtime.application import project_context

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    path = _declare(tmp_path, {"schema_version": 3, "writer_protocol": NEW})
    real = project_context.read_guarded_json_bytes

    reads: list[Path] = []

    def vanish(target: Path) -> object:
        if target == path:
            reads.append(target)
            if len(reads) > 1:
                path.unlink()
                return None
        return real(target)

    monkeypatch.setattr(project_context, "read_guarded_json_bytes", vanish)
    with pytest.raises(ValueError, match="missing or invalid"):
        project_context.resolve_observed_context(str(tmp_path), tmp_path)
    assert len(reads) == 2
