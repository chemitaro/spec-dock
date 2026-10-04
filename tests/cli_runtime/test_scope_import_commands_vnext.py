"""Exact GitHub imports through the normal public CLI, without POST or replay."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_scope_publish import publication_fixture

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_scope_import_previews_and_publishes_the_linked_number_without_post(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = tree_digest(root)
    command = [
        "--project",
        str(root),
        "scope",
        "import",
        "github",
        "initiative",
        "gh:example/repo#47",
        "--title",
        "Local plan",
        "--json",
    ]
    assert main([*command, "--dry-run"]) == 0
    planned = json.loads(capsys.readouterr().out)
    assert planned["status"] == "planned"
    assert planned["data"]["result"]["scope"] is None
    assert planned["data"]["result"]["github_ref"] == "gh:example/repo#47"
    assert planned["data"]["result"]["can_apply"] is True
    assert planned["effects"] == [{"kind": "scaffold", "status": "planned", "target": None}]
    assert tree_digest(root) == before
    assert main(command) == 0
    result = json.loads(capsys.readouterr().out)
    scope = result["data"]["result"]["scope"]
    assert scope["id"] == "init-00047" and scope["backend"] == "github"
    assert scope["github_ref"] == result["data"]["result"]["github_ref"] == "gh:example/repo#47"
    assert scope["status"]["state"] == "open" and scope["status"]["source"] == "github"
    assert scope["status"]["authority"] == "github" and scope["status"]["observed_at"] is not None
    metadata = json.loads((root / scope["path"] / ".meta.json").read_bytes())
    assert metadata["id"] == "init-00047" and metadata["github"]["issue_number"] == 47
    assert metadata["lifecycle"] is None and "operation_id" not in result
    assert [(json.loads(line)["method"], json.loads(line)["endpoint"]) for line in log.read_text().splitlines()] == [
        ("GET", "repos/example/repo/issues/47"),
        ("GET", "repos/example/repo/issues/47"),
    ]
    assert not (root / ".git/spec-dock").exists()


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
