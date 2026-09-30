"""Import exact GitHub Issues through the normal, control-free public CLI."""

from __future__ import annotations

import json
import os
import shutil
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_scope_publish import publication_fixture

if TYPE_CHECKING:
    from pathlib import Path


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


def test_import_publishes_the_confirmed_issue_number_with_get_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    existing = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = existing.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    scope = root / "spec-dock/initiatives/init-00413-imported-scope"
    metadata = json.loads((scope / ".meta.json").read_bytes())
    assert metadata["id"] == "init-00413" and metadata["schema_version"] == 3
    assert metadata["github"] == {"issue_number": 413, "repo_owner": "example", "repo_name": "repo"}
    assert result["data"]["result"]["scope"]["id"] == "init-00413"
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#413"
    assert result["effects"] == [{"kind": "scaffold", "status": "succeeded", "target": "init-00413"}]
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(call["method"], call["endpoint"]) for call in calls] == [("GET", "repos/example/repo/issues/413")]
    assert existing.read_bytes() == before and not (root / ".git/spec-dock").exists()
    assert "operation_id" not in result


def test_import_returns_the_live_closed_reason_without_persisting_a_lifecycle_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace("state='open',state_reason=None", "state='closed',state_reason='completed'")
    )
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    status = result["data"]["result"]["scope"]["status"]
    assert status["state"] == "completed" and status["source"] == "github" and status["authority"] == "github"
    assert status["observed_at"] is not None
    metadata = json.loads((root / "spec-dock/initiatives/init-00413-imported-scope/.meta.json").read_bytes())
    assert metadata["lifecycle"] is None
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


@pytest.mark.parametrize(
    "reference,hint",
    [
        ("https://github.com/example/repo/issues/413", []),
        ("413", ["--github-repo", "EXAMPLE/REPO"]),
    ],
)
def test_import_accepts_existing_exact_reference_forms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], reference: str, hint: list[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            reference,
            "--title",
            "Imported Scope",
            *hint,
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#413"
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


@pytest.mark.parametrize(
    "reference,options",
    [
        ("413", []),
        ("gh:foreign/repo#413", []),
        ("gh:example/repo#413", ["--github-repo", "different/repo"]),
        ("gh:example/repo#413", ["--offline"]),
    ],
)
def test_import_rejects_unbound_or_offline_refs_before_github(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    reference: str,
    options: list[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            reference,
            "--title",
            "Imported Scope",
            *options,
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert not log.exists() and not (root / "spec-dock/.agent").exists()


@pytest.mark.parametrize(
    "replacement",
    [
        ("title='Existing Scope'", "pull_request={},title='Existing Scope'"),
        ("api.github.com/repos/example/repo", "api.github.com/repos/foreign/repo"),
        ("HTTP/2.0 200 OK", "HTTP/2.0 503 Unavailable"),
    ],
)
def test_import_stops_on_a_rejected_or_unverified_get_without_publishing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], replacement: tuple[str, str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(executable.read_text().replace(*replacement))
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert not (root / "spec-dock/initiatives/init-00413-imported-scope").exists()
    assert not (root / "spec-dock/.agent").exists()
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


def test_import_dry_run_reads_the_issue_without_creating_local_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned" and result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "scaffold", "status": "planned", "target": None}]
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (root / "spec-dock/.agent").exists()
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


def test_import_reports_both_paths_when_a_competing_publication_links_the_same_issue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    published = root / "spec-dock/initiatives/init-00413-imported-scope"
    competing = root / "spec-dock/initiatives/init-local-00413-competing-scope"
    original_fsync = os.fsync
    injected = False

    def fsync(descriptor: int) -> None:
        nonlocal injected
        if published.exists() and not injected:
            injected = True
            shutil.copytree(published, competing, symlinks=True)
            metadata = json.loads((competing / ".meta.json").read_bytes())
            metadata.update(id="init-local-00413", slug="competing-scope")
            (competing / ".meta.json").unlink()
            (competing / ".meta.json").write_text(json.dumps(metadata))
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["data"]["result"]["changed"] is True, result
    assert result["effects"] == [{"kind": "scaffold", "status": "succeeded", "target": "init-00413"}]
    assert set(result["error"]["details"]["paths"]) == {str(published), str(competing)}
    assert (published / ".meta.json").exists() and (competing / ".meta.json").exists()
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]


def test_import_of_an_already_linked_ref_fails_without_a_mutation_or_partial_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    existing = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = existing.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#1",
            "--title",
            "Duplicate Scope",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert existing.read_bytes() == before
    assert not (root / "spec-dock/initiatives/init-00001-duplicate-scope").exists()
    assert not log.exists()


def test_import_retains_the_exact_ref_after_input_changes_during_get_without_claiming_a_remote_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    executable = tmp_path / "gh-bin/gh"
    change = (
        f" with open({str(metadata)!r}) as stream: metadata=json.load(stream)\n"
        " metadata['title']='Concurrent Edit'; metadata['revision']+=1\n"
        f" with open({str(metadata)!r},'w') as stream: json.dump(metadata,stream)\n"
    )
    executable.write_text(executable.read_text().replace("if method=='GET':\n", "if method=='GET':\n" + change))
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "import",
            "github",
            "initiative",
            "gh:example/repo#413",
            "--title",
            "Imported Scope",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["error"]["code"] == "SCOPE_PUBLICATION_INCOMPLETE"
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#413"
    assert result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "scaffold", "status": "not_attempted", "target": "init-00413"}]
    assert json.loads(metadata.read_bytes())["title"] == "Concurrent Edit"
    assert not (root / "spec-dock/initiatives/init-00413-imported-scope").exists()
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]
