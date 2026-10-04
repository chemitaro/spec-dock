"""GitHub-numbered publication through the normal public Scope CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_scope_publish import publication_fixture
from tests.cli_runtime.test_scope_lifecycle_commands_vnext import existing_local_workspace

if TYPE_CHECKING:
    from pathlib import Path


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


@pytest.mark.parametrize("options,slug", [([], "program-plan"), (["--slug", "custom"], "custom")])
def test_github_scope_preview_normalizes_slug_without_allocating_an_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    options: list[str],
    slug: str,
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "Program Plan",
            *options,
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["result"] == {
        "scope": None,
        "github_ref": None,
        "title": "Program Plan",
        "slug": slug,
        "changed": False,
        "can_apply": True,
        "blockers": [],
    }
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "planned"),
        ("scaffold", "planned"),
    ]
    assert not log.exists() and tree_digest(root) == before


def test_scope_show_and_edit_preserve_existing_local_backend_and_documents(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, metadata = existing_local_workspace(tmp_path / "consumer")
    document = metadata.parent / "requirement.md"
    document.write_text("# 既存の要件\n本文を保全します。\n", encoding="utf-8")
    before = document.read_bytes()
    prefix = ["--project", str(root), "scope"]
    assert main([*prefix, "show", "init-00001", "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)["data"]["result"]["scope"]
    assert shown["id"] == "init-00001" and shown["backend"] == "local" and shown["github_ref"] is None
    assert shown["status"]["state"] == "open" and shown["status"]["authority"] == "local"
    assert main([*prefix, "edit", "init-00001", "--title", "Updated", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)["data"]["result"]
    assert result["changed"] is True and result["scope"]["id"] == "init-00001"
    assert result["scope"]["title"] == "Updated" and result["scope"]["revision"] == 1
    assert result["scope"]["status"]["state"] == "open" and result["scope"]["status"]["source"] == "local"
    assert json.loads(metadata.read_bytes())["title"] == "Updated"
    assert document.read_bytes() == before and not (root / ".git/spec-dock").exists()


def test_github_scope_create_rejects_missing_parent_before_remote_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "epic",
            "--backend",
            "github",
            "--parent",
            "init-00999",
            "--title",
            "Plan",
            "--yes",
            "--json",
        ])
        == 4
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and tree_digest(root) == before and not log.exists()


def test_github_scope_create_requires_confirmation_and_reports_the_numbered_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    existing = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = tree_digest(root)
    existing_bytes = existing.read_bytes()
    command = [
        "--project",
        str(root),
        "scope",
        "create",
        "initiative",
        "--backend",
        "github",
        "--title",
        "Plan",
        "--json",
    ]
    assert main(command) == 3
    denied = json.loads(capsys.readouterr().out)
    assert denied["error"]["code"] == "CONFIRMATION_REQUIRED" and denied["effects"] == []
    assert tree_digest(root) == before and not log.exists()
    assert main([*command, "--yes"]) == 0
    result = json.loads(capsys.readouterr().out)
    scope = result["data"]["result"]["scope"]
    assert scope["id"] == "init-00057" and scope["backend"] == "github"
    assert scope["kind"] == "initiative" and scope["parent_id"] is None and scope["revision"] == 0
    assert scope["github_ref"] == "gh:example/repo#57"
    assert scope["status"]["state"] == "open" and scope["status"]["authority"] == "github"
    created = root / scope["path"]
    metadata = json.loads((created / ".meta.json").read_bytes())
    assert metadata["id"] == "init-00057" and metadata["github"]["issue_number"] == 57
    assert all((created / name).is_file() for name in ("requirement.md", "design.md", "plan.md"))
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["POST"]
    assert existing.read_bytes() == existing_bytes and "operation_id" not in result
    assert not (root / ".git/spec-dock").exists()


def test_github_create_confirmation_rejects_native_origin_change_before_post(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = {path: path.read_bytes() for path in (root / "spec-dock").rglob("*") if path.is_file()}

    class AnswerAfterOriginChange:
        def isatty(self) -> bool:
            return True

        def readline(self) -> str:
            subprocess.run(
                ["git", "-C", str(root), "remote", "set-url", "origin", "https://github.com/example/other.git"],
                check=True,
                capture_output=True,
            )
            return "yes\n"

    monkeypatch.setattr(sys, "stdin", AnswerAfterOriginChange())
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "Plan",
        ])
        == 3
    )
    output = capsys.readouterr()
    assert "Confirm [yes/no]" in output.err and "GitHub repository changed" in output.err
    assert not log.exists() and not (root / "spec-dock/initiatives/init-00057-plan").exists()
    assert all(path.read_bytes() == exact for path, exact in before.items())


def test_confirmed_remote_create_can_be_imported_explicitly_without_a_second_post(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    destination = root / "spec-dock/initiatives/init-00057-plan"
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            "assert method=='POST' and endpoint=='repos/example/repo/issues'\n",
            "assert method=='POST' and endpoint=='repos/example/repo/issues'\n"
            "from pathlib import Path\n"
            f"Path({str(destination)!r}).write_bytes(b'Existing unrelated path.\\n')\n",
        )
    )
    command = [
        "--project",
        str(root),
        "scope",
        "create",
        "initiative",
        "--backend",
        "github",
        "--title",
        "Plan",
        "--yes",
        "--json",
    ]
    assert main(command) == 6
    partial = json.loads(capsys.readouterr().out)
    assert partial["status"] == "partial" and partial["data"]["result"]["scope"] is None
    assert partial["data"]["result"]["github_ref"] == "gh:example/repo#57"
    assert [(effect["kind"], effect["status"]) for effect in partial["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "not_attempted"),
    ]
    assert destination.read_bytes() == b"Existing unrelated path.\n" and "operation_id" not in partial
    before = tree_digest(root)
    assert main([*command, "--resume", "old-operation"]) == 2
    rejected = json.loads(capsys.readouterr().out)
    assert rejected["error"]["code"] == "ARGUMENT_RETIRED" and rejected["effects"] == []
    assert tree_digest(root) == before
    destination.unlink()
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#57",
            "--title",
            "Plan",
            "--json",
        ])
        == 0
    )
    imported = json.loads(capsys.readouterr().out)
    assert imported["data"]["result"]["scope"]["id"] == "init-00057"
    assert json.loads((destination / ".meta.json").read_bytes())["github"]["issue_number"] == 57
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["POST", "GET"]
    assert not (root / ".git/spec-dock").exists()
