"""dispatch() routes by workspace mode at one place, with an entry before resolve_context."""

from __future__ import annotations

import argparse
import json
import subprocess
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.commands.runtime_dispatch import dispatch
from spec_dock.runtime.presentation.command_data import DiagnosticData
from spec_dock.runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

    from spec_dock.runtime.application.project_context import ProjectContext


def _repository(root: Path, version: int) -> Path:
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    (root / "spec-dock").mkdir()
    (root / "spec-dock/workspace.json").write_text(
        json.dumps({"schema_version": version, "writer_protocol": "specdock.worktree-writer/v1"}), encoding="utf-8"
    )
    return root


def _namespace(command: str, root: Path, **extra: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "command_path": command,
        "project": str(root),
        "timeout": 30.0,
        "json": True,
        "dry_run": False,
        "expect_current": None,
        "expect_backend": None,
    }
    values.update(extra)
    return argparse.Namespace(**values)


def _result(output: tuple[int, str, str]) -> tuple[int, Any]:
    return output[0], json.loads(output[1])


def test_canonical_group_commands_stop_in_a_schema_three_repository(tmp_path: Path) -> None:
    root = _repository(tmp_path / "legacy", 3)
    code, result = _result(dispatch(_namespace("canonical status", root), root))
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_MIGRATED"
    assert "migrate-to-canonical" in " ".join(result["recovery"]["instructions"])


def test_entries_before_resolve_context_run_first_and_may_decline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.commands import canonical_dispatch

    root = _repository(tmp_path / "legacy", 3)
    calls: list[str] = []

    def registered(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object] | None:
        calls.append(namespace.command_path)
        if getattr(namespace, "registered", False):
            return OperationResult(namespace.command_path, "succeeded", DiagnosticData(), 0)
        return None

    def no_context(*args: object, **kwargs: object) -> object:
        raise AssertionError("resolve_context must not run before the independent entry")

    monkeypatch.setitem(canonical_dispatch.REPOSITORY_INDEPENDENT_HANDLERS, "canonical sync", registered)
    monkeypatch.setattr("spec_dock.runtime.application.project_context.resolve_context", no_context)
    code, result = _result(dispatch(_namespace("canonical sync", tmp_path, registered=True), tmp_path))
    assert (code, result["status"], calls) == (0, "succeeded", ["canonical sync"])
    monkeypatch.undo()
    monkeypatch.setitem(canonical_dispatch.REPOSITORY_INDEPENDENT_HANDLERS, "canonical sync", registered)
    code, result = _result(dispatch(_namespace("canonical sync", root, registered=False), root))
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_MIGRATED"


def test_schema_four_runs_registered_canonical_handlers_with_the_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.commands import canonical_dispatch

    root = _repository(tmp_path / "canonical", 4)
    seen: list[str] = []

    def handler(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
        seen.append(context.mode)
        return OperationResult(namespace.command_path, "succeeded", DiagnosticData(), 0)

    monkeypatch.setitem(canonical_dispatch.CANONICAL_HANDLERS, "scope list", handler)
    assert _result(dispatch(_namespace("scope list", root), root))[0] == 0 and seen == ["canonical"]
    code, result = _result(dispatch(_namespace("scope show", root, target="init-00001"), root))
    assert code == 3 and result["error"]["code"] == "CANONICAL_NOT_IMPLEMENTED"


def test_schema_three_reaches_the_legacy_handler_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repository(tmp_path / "legacy", 3)
    reached: list[str] = []

    def legacy(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
        reached.append(context.mode)
        return OperationResult(namespace.command_path, "succeeded", DiagnosticData(), 0)

    monkeypatch.setattr("spec_dock.runtime.application.direct_sync.sync_workspace", legacy)
    assert _result(dispatch(_namespace("workspace sync", root, source="local", allow_invalid=False), root))[0] == 0
    assert reached == ["legacy"]


def test_canonical_errors_accept_only_failure_exit_codes() -> None:
    import pytest

    from spec_dock.runtime.application.canonical_errors import CanonicalCommandError

    for code in (0, 6, 8):
        with pytest.raises(ValueError):
            CanonicalCommandError("X", "y", exit_code=code)
    assert CanonicalCommandError("X", "y", exit_code=7, recovery=("next",)).result("scope list").exit_code == 7


def test_handler_types_and_recovery_texts_are_importable_at_runtime() -> None:
    from spec_dock.runtime.application import canonical_errors
    from spec_dock.runtime.commands import canonical_dispatch

    assert canonical_dispatch.CanonicalHandler is not None
    assert canonical_dispatch.RepositoryIndependentHandler is not None
    assert canonical_errors.MIGRATE_NOT_APPLICABLE_RECOVERY.startswith("No writer-protocol migration")
    assert canonical_errors.CANONICAL_NOT_LINKED_RECOVERY == "spec-dock canonical link"


def test_canonical_check_is_answered_before_resolve_context_even_in_a_schema_three_repository(
    tmp_path: Path,
) -> None:
    from spec_dock.runtime.application.canonical_check import check_canonical_commit
    from spec_dock.runtime.commands.canonical_dispatch import REPOSITORY_INDEPENDENT_HANDLERS

    assert REPOSITORY_INDEPENDENT_HANDLERS["canonical check"] is check_canonical_commit
    root = _repository(tmp_path / "legacy", 3)
    subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=F", "-c", "user.email=f@example.invalid", "commit", "-qm", "f"],
        check=True,
    )
    code, result = _result(dispatch(_namespace("canonical check", root, commit="HEAD"), root))
    assert code == 7 and result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    assert "WORKSPACE_NOT_MIGRATED" in [item["code"] for item in result["data"]["result"]["failures"]]
