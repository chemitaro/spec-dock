"""Mode-independent help and argument-admission tests moved from legacy-mode files (iss-00440).

Moved unchanged from tests/cli_runtime/test_issue413_scope_publish.py, test_issue413_scope_import.py,
test_issue413_scope_edit.py, test_issue413_scope_lifecycle.py, test_issue413_scope_delete.py,
test_issue413_dependency.py, test_scope_create_commands_vnext.py and test_scope_import_commands_vnext.py,
whose remaining tests used a schema-3 fixture. None of them reads a project.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main

if TYPE_CHECKING:
    from pathlib import Path


def test_new_local_scope_is_rejected_before_project_access(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "create",
            "initiative",
            "--backend",
            "local",
            "--title",
            "New Scope",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_create_help_describes_only_github_numbered_publication(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "scope", "create", "initiative"]) == 0
    output = capsys.readouterr().out
    assert "local creation" not in output
    assert "specdock.cli/v2" in output
    assert "GitHub" in output
    assert "--resume" not in output
    assert "--rollback" not in output
    assert "journal" not in output


def test_import_help_describes_a_get_only_v2_operation_without_resume(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "scope", "import", "github", "initiative"]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output
    assert "--resume" not in output and "journal" not in output and "--rollback" not in output


def test_import_resume_is_retired_before_project_access(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--resume",
            "old-operation",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_edit_help_describes_local_metadata_without_cached_state_or_journal_recovery(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "scope", "edit"]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output and "scope, github_ref, changed" in output
    assert "cached" not in output and "--resume" not in output and "journal" not in output


@pytest.mark.parametrize("action", ["close", "reopen"])
def test_lifecycle_help_has_v2_results_without_journal_recovery(
    capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert main(["help", "scope", action]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output
    assert "--resume" not in output and "--rollback" not in output and "journal" not in output


@pytest.mark.parametrize("action", ["close", "reopen"])
def test_lifecycle_resume_is_retired_before_context(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            action,
            "init-00001",
            "--resume",
            "old-operation",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_delete_help_explains_verified_backup_and_per_path_results(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["scope", "delete", "--help"]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output and "--backup-dir" in output
    assert "removed_ids" in output and "remaining_paths" in output
    assert "spec-dock scope delete <scope-id> --backup-dir /absolute/backup --yes" in output
    assert "--resume" not in output and "OPERATION_ID" not in output and "journal" not in output


@pytest.mark.parametrize("flag", ["--resume", "--rollback"])
def test_scope_delete_retired_recovery_flags_stop_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "scope", "delete", "iss-00003", flag, "0" * 32, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("options", [["--source", "cache"], ["--source=cache"], ["--allow-stale"]])
def test_retired_dependency_readiness_inputs_are_rejected_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], options: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "dependency", "check", "iss-00003", *options, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("action", ["list", "check", "add", "remove"])
def test_dependency_leaf_help_describes_control_free_v2_operations(
    capsys: pytest.CaptureFixture[str], action: str
) -> None:
    assert main(["help", "dependency", action]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output
    assert "--source cache" not in output and "--resume" not in output and "journal" not in output
    if action == "check":
        assert "local" in output and "github" in output


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_new_local_scope_is_retired_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "create",
            kind,
            "--backend",
            "local",
            "--title",
            "Program",
            "--dry-run",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_import_rejects_resume_before_project_access(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#47",
            "--title",
            "Plan",
            "--resume",
            "old-operation",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_import_requires_an_exact_source_reference_before_project_access(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "import",
            "github",
            "initiative",
            "--title",
            "Plan",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []
