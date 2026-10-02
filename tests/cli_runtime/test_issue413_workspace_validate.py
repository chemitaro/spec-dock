"""Validation distinguishes the working tree from one fixed committed snapshot."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_contract import add_scope, make_workspace
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("ci", [False, True])
def test_validation_without_control_is_read_only_and_reports_its_snapshot_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    head = run_git(root, "rev-parse", "HEAD").decode().strip()

    def unexpected(*_args: object, **_kwargs: object) -> object:
        pytest.fail("structural validation must not probe GitHub or acquire a Start lock")

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", unexpected)
    monkeypatch.setattr("spec_dock.runtime.infra.start_lock.StartLock.__enter__", unexpected)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert result["data"]["kind"] == "validation" and result["effects"] == []
    assert data["valid"] is True and data["findings"] == []
    assert data["snapshot_source"] == ("HEAD" if ci else "working-tree")
    assert data["node_count"] == 1
    if ci:
        assert data["snapshot_oid"] == head
    assert tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_ci_uses_the_captured_oid_even_if_head_moves_during_the_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra import committed_validation as reader

    root = committed_workspace(tmp_path / "consumer")
    head = run_git(root, "rev-parse", "HEAD").decode().strip()
    original_run = reader.run_git
    observed: list[str] = []
    after_fixture_change: list[str] = []

    def observe(path: Path, *args: str, timeout: float = 30) -> bytes:
        if args[0] == "ls-tree":
            observed.append(args[4])
            metadata = next((root / "spec-dock/initiatives").rglob(".meta.json"))
            metadata.write_text("private broken metadata")
            assert commit_fixture(root) != head
            after_fixture_change.append(tree_digest(root))
        return original_run(path, *args, timeout=timeout)

    monkeypatch.setattr(reader, "run_git", observe)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert observed == [head] and result["data"]["result"]["snapshot_oid"] == head
    assert result["data"]["result"]["node_count"] == 1 and result["effects"] == []
    assert tree_digest(root) == after_fixture_change[0]


def test_ci_fetches_only_metadata_bodies_and_never_artifact_or_runtime_bodies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from spec_dock.runtime.infra import committed_validation as reader

    root = committed_workspace(tmp_path / "consumer")
    owner = root / "spec-dock/initiatives/init-00001-fixture"
    paths = [
        "spec-dock/artifacts/20261001t000000z-research-root.md",
        "spec-dock/initiatives/init-00001-fixture/artifacts/20261001t000000z-adr-scope.md",
        "spec-dock/initiatives/init-00001-fixture/requirement.md",
        "spec-dock/initiatives/init-00001-fixture/.workbench/notes.txt",
        "spec-dock/.agent/work-target/target-" + "a" * 32 + ".json",
        "spec-dock/scripts/private-engine.py",
    ]
    for relative in paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"private-body must never be fetched")
    run_git(root, "add", "-f", "--", *paths, mutation=True)
    head = commit_fixture(root)
    metadata_paths = ["spec-dock/workspace.json", (owner / ".meta.json").relative_to(root).as_posix()]
    allowed = {run_git(root, "rev-parse", f"{head}:{path}").decode().strip() for path in metadata_paths}
    fetched: list[str] = []
    original_run = reader.run_git

    def observe(path: Path, *args: str, timeout: float = 30) -> bytes:
        if args[0] == "cat-file":
            assert args[1] == "blob" and args[2] in allowed, "a non-metadata body was requested"
            fetched.append(args[2])
        return original_run(path, *args, timeout=timeout)

    monkeypatch.setattr(reader, "run_git", observe)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 0
    output = capsys.readouterr()
    assert set(fetched) == allowed and len(fetched) == len(allowed)
    assert "private-body" not in output.out + output.err and tree_digest(root) == before


@pytest.mark.skipif(os.name != "posix", reason="native symlink fixture")
@pytest.mark.parametrize("owner", ["spec-dock", "spec-dock/initiatives/init-00001-fixture"])
@pytest.mark.parametrize("fault", ["directory-link", "file-link"])
@pytest.mark.parametrize("ci", [False, True])
def test_validation_rejects_redirected_artifact_structure_without_reading_its_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], owner: str, fault: str, ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    outside = tmp_path / "outside"
    outside.mkdir()
    private = outside / "20261001t000000z-research-private.md"
    private.write_bytes(b"private artifact body")
    artifacts = root / owner / "artifacts"
    if fault == "directory-link":
        artifacts.symlink_to(outside, target_is_directory=True)
    else:
        artifacts.mkdir()
        (artifacts / private.name).symlink_to(private)
    commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["valid"] is False and result["effects"] == []
    assert "private artifact body" not in output.out + output.err
    assert private.read_bytes() == b"private artifact body" and tree_digest(root) == before


@pytest.mark.parametrize("ci", [False, True])
def test_unrecognized_scope_entries_do_not_become_required_structural_nodes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    container = root / "spec-dock/initiatives"
    (container / "readme.md").write_text("private incidental body")
    archived = container / "archive/init-00002-retired"
    archived.mkdir(parents=True)
    (archived / ".meta.json").write_text("invalid ignored metadata")
    commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["node_count"] == 1 and tree_digest(root) == before


@pytest.mark.parametrize("fault", ["dependency", "parent", "missing-meta"])
@pytest.mark.parametrize("ci", [False, True])
def test_validation_checks_committed_dependency_and_parent_structure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fault: str, ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = next((root / "spec-dock/initiatives").rglob(".meta.json"))
    payload = json.loads(metadata.read_bytes())
    if fault == "missing-meta":
        metadata.unlink()
        (metadata.parent / "requirement.md").write_text("private surviving Scope body")
    else:
        payload["depends_on" if fault == "dependency" else "parent_id"] = (
            ["init-00002"] if fault == "dependency" else "init-00002"
        )
        metadata.write_text(json.dumps(payload))
    commit_fixture(root)
    before = tree_digest(root)
    before_files = {
        path.relative_to(root).as_posix(): (path.stat().st_mode, path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    }
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["findings"] and result["effects"] == []
    assert {
        path.relative_to(root).as_posix(): (path.stat().st_mode, path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    } == before_files
    assert tree_digest(root) == before


def test_ci_preserves_native_git_failure_details_without_any_effects(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    error = GitProcessError(("git", "-C", str(root), "ls-tree"), b"native git failure\nsecond line\n", 128)

    def fail(*_args: object, **_kwargs: object) -> object:
        raise error

    monkeypatch.setattr("spec_dock.runtime.infra.committed_validation.run_git", fail)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 5
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["details"] == error.details() and result["effects"] == [] and not output.err
    assert tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def commit_fixture(root: Path) -> str:
    run_git(root, "add", "--", "spec-dock", mutation=True)
    run_git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-qm",
        "validation fixture",
        mutation=True,
    )
    return run_git(root, "rev-parse", "HEAD").decode().strip()


@pytest.mark.parametrize("ci", [False, True])
@pytest.mark.parametrize("required", [False, True])
def test_empty_workspace_is_valid_unless_nodes_are_required(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool, required: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = next((root / "spec-dock/initiatives").rglob(".meta.json"))
    metadata.unlink()
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (metadata.parent / filename).unlink()
    metadata.parent.rmdir()
    commit_fixture(root)
    before = tree_digest(root)
    flags = (["--ci"] if ci else []) + (["--require-nodes"] if required else [])
    assert main(["--project", str(root), "workspace", "validate", *flags, "--json"]) == (7 if required else 0)
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["valid"] is not required and data["node_count"] == 0
    assert [item["code"] for item in data["findings"]] == (["NODES_REQUIRED"] if required else [])
    assert result["effects"] == [] and tree_digest(root) == before


@pytest.mark.parametrize("fault", ["scope", "workspace-missing", "workspace-unknown"])
def test_ci_rejects_invalid_committed_data_even_when_the_working_copy_is_valid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fault: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    path = (
        next((root / "spec-dock/initiatives").rglob(".meta.json"))
        if fault == "scope"
        else root / "spec-dock/workspace.json"
    )
    original = path.read_bytes()
    if fault == "workspace-missing":
        path.unlink()
    else:
        path.write_bytes(b'{"schema_version":99,"private":"private-body"}')
    invalid_head = commit_fixture(root)
    path.write_bytes(original)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["valid"] is False
    assert result["data"]["result"]["snapshot_oid"] == invalid_head
    assert result["data"]["result"]["findings"] and result["effects"] == []
    assert "private-body" not in output.out + output.err and tree_digest(root) == before
    assert main(["--project", str(root), "workspace", "validate", "--json"]) == 0
    capsys.readouterr()


@pytest.mark.parametrize("ci", [False, True])
def test_structural_validation_ignores_corrupt_execution_and_legacy_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    state = root / "spec-dock/.agent/work-target"
    state.mkdir(parents=True)
    (state / ("target-" + "a" * 32 + ".json")).write_bytes(b"private runtime body")
    legacy = root / ".git/spec-dock/control"
    legacy.mkdir(parents=True)
    (legacy / "control.json").write_bytes(b"private legacy body")

    def unexpected(*_args: object, **_kwargs: object) -> object:
        pytest.fail("structure validation must not inspect direct execution or legacy state")

    monkeypatch.setattr("spec_dock.runtime.infra.work_target_store.WorkTargetStore.read", unexpected)
    monkeypatch.setattr("spec_dock.runtime.infra.legacy_reader.inspect_legacy_files", unexpected)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out)["data"]["result"]["valid"] is True
    assert "private" not in output.out + output.err and tree_digest(root) == before


@pytest.mark.parametrize("expectation", [["--expect-current", "init-00001"], ["--expect-backend", "github"]])
def test_ci_does_not_silently_ignore_expectations_for_live_scope_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], expectation: list[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", *expectation, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert expectation[0] in result["error"]["message"] and tree_digest(root) == before


@pytest.mark.parametrize("owner", ["spec-dock", "spec-dock/initiatives/init-00001-fixture"])
@pytest.mark.parametrize("ci", [False, True])
def test_validation_detects_root_and_scope_artifact_slot_conflicts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], owner: str, ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    artifacts = root / owner / "artifacts"
    artifacts.mkdir()
    (artifacts / "20261001t000000z-research-first.md").write_text("private artifact first")
    (artifacts / "20261001t000000z-adr-second.md").write_text("private artifact second")
    commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["valid"] is False and result["effects"] == []
    assert "ARTIFACT_INVALID" in {item["code"] for item in result["data"]["result"]["findings"]}
    assert "private artifact" not in output.out + output.err and tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("fault", ["scope", "workspace-missing", "workspace-unknown"])
def test_ci_validation_uses_fixed_head_instead_of_uncommitted_declarations_or_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fault: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    if fault == "scope":
        next((root / "spec-dock/initiatives").rglob(".meta.json")).write_bytes(b'{"private-body": broken}')
    elif fault == "workspace-missing":
        (root / "spec-dock/workspace.json").unlink()
    else:
        (root / "spec-dock/workspace.json").write_bytes(b'{"schema_version":99,"private":"private-body"}')
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 0
    output = capsys.readouterr()
    data = json.loads(output.out)["data"]["result"]
    assert data["valid"] is True and data["snapshot_source"] == "HEAD"
    assert "private-body" not in output.out + output.err
    assert tree_digest(root) == before


def test_validation_help_distinguishes_fixed_head_from_live_expectations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "workspace", "validate", "--help"]) == 0
    text = capsys.readouterr().out
    assert "fixed HEAD" in text and "--expect-current" in text and "--expect-backend" in text
    assert not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("ci", [False, True])
def test_validation_reads_known_old_protocol_without_migrating_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    declaration = root / "spec-dock/workspace.json"
    declaration.write_text('{"schema_version":3,"writer_protocol":"specdock.writer/v1","control_epoch":7}')
    commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["valid"] is True
    assert tree_digest(root) == before and b'"control_epoch":7' in declaration.read_bytes()


@pytest.mark.parametrize("ci", [False, True])
def test_validation_preview_is_read_only_and_does_not_reserve_any_work(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    assert (
        main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--dry-run", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned" and result["data"]["result"]["can_apply"] is True
    assert result["data"]["result"]["blockers"] == [] and result["effects"] == []
    assert tree_digest(root) == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX selection store; Windows adapter is tested separately")
@pytest.mark.parametrize("selected", [False, True])
def test_working_validation_checks_an_explicit_current_scope_expectation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], selected: bool
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    if selected:
        select_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--expect-current", "init-00001", "--json"]) == (
        0 if selected else 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and tree_digest(root) == before


def test_ci_requires_a_commit_even_if_the_unborn_working_workspace_is_valid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert "HEAD" in result["error"]["message"] and result["effects"] == []
    assert tree_digest(root) == before
    assert main(["--project", str(root), "workspace", "validate", "--json"]) == 0
    capsys.readouterr()


def test_ci_checks_the_linked_worktrees_own_head_and_three_level_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
    linked = tmp_path / "linked"
    run_git(root, "worktree", "add", "-b", "fixture-linked", str(linked), "HEAD", mutation=True)
    initiative = linked / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(linked, "epic-00002", "epic", "init-00001", initiative)
    add_scope(linked, "iss-00003", "issue", "epic-00002", epic)
    linked_head = commit_fixture(linked)
    main_head = run_git(root, "rev-parse", "HEAD").decode().strip()
    (linked / "spec-dock/workspace.json").write_text("private uncommitted declaration")
    before = tree_digest(root), tree_digest(linked)
    assert main(["--project", str(linked), "workspace", "validate", "--ci", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["node_count"] == 3 and result["data"]["result"]["snapshot_oid"] == linked_head
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["node_count"] == 1 and result["data"]["result"]["snapshot_oid"] == main_head
    assert (tree_digest(root), tree_digest(linked)) == before


@pytest.mark.parametrize("ci", [False, True])
def test_validation_detects_duplicate_scope_ids_on_different_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = next((root / "spec-dock/initiatives").rglob(".meta.json"))
    duplicate = metadata.parent.with_name("init-00001-second")
    duplicate.mkdir()
    (duplicate / ".meta.json").write_text(json.dumps(dict(json.loads(metadata.read_bytes()), slug="second")))
    commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["valid"] is False and result["effects"] == []
    assert tree_digest(root) == before


@pytest.mark.parametrize("ci", [False, True])
@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
@pytest.mark.parametrize("filename", ["requirement.md", "design.md", "plan.md", "report.md"])
def test_validation_rejects_missing_required_scope_documents_without_changing_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool, kind: str, filename: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    owners = _three_level_documents(root)
    target = owners[kind] / filename
    target.unlink()
    commit_fixture(root)
    if ci:
        # A valid working copy cannot repair a missing committed document.
        target.write_text("private uncommitted replacement")
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert data["valid"] is False and data["node_count"] == 3
    finding = next(item for item in data["findings"] if item["code"] == "REQUIRED_DOCUMENT_INVALID")
    assert finding["details"] == {
        "scope_id": {"initiative": "init-00001", "epic": "epic-00002", "issue": "iss-00003"}[kind],
        "relative_path": target.relative_to(root).as_posix(),
    }
    assert result["effects"] == [] and tree_digest(root) == before
    assert "private" not in output.out + output.err and not output.err
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native directory and symlink document fixture")
@pytest.mark.parametrize("ci", [False, True])
@pytest.mark.parametrize("fault", ["directory", "symlink"])
def test_validation_rejects_nonregular_required_documents_without_reading_redirected_bodies(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ci: bool, fault: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    owners = _three_level_documents(root)
    document = owners["issue"] / "report.md"
    document.unlink()
    outside = tmp_path / "private-outside.md"
    outside.write_bytes(b"private redirected body")
    if fault == "directory":
        document.mkdir()
        (document / "private.txt").write_bytes(b"private directory body")
    else:
        document.symlink_to(outside)
    commit_fixture(root)
    before = tree_digest(root), outside.read_bytes()
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert any(item["code"] == "REQUIRED_DOCUMENT_INVALID" for item in result["data"]["result"]["findings"])
    assert result["effects"] == [] and "private" not in output.out + output.err
    assert (tree_digest(root), outside.read_bytes()) == before


@pytest.mark.parametrize("ci", [False, True])
def test_validation_treats_required_document_contents_and_historical_authority_as_opaque(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, ci: bool
) -> None:
    from pathlib import Path as ConcretePath

    root = committed_workspace(tmp_path / "consumer")
    owners = _three_level_documents(root)
    names = {"requirement.md", "design.md", "plan.md", "report.md"}
    for owner in owners.values():
        (owner / "report.md").write_bytes(b"")
        (owner / "design.md").write_bytes(b"\xff\x00private draft approval: pending")
        (owner / "plan.md").write_text("private legacy reviewer: blocked")
        (owner / ".assurance.json").write_text('{"grade":"blocked","private":true}')
    commit_fixture(root)
    before = tree_digest(root)
    original_open = ConcretePath.open

    def refuse_body_read(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> object:
        assert path.name not in names | {".assurance.json"}, "required document body was opened"
        return original_open(path, mode, buffering, encoding, errors, newline)

    monkeypatch.setattr(ConcretePath, "open", refuse_body_read)
    assert main(["--project", str(root), "workspace", "validate", *(["--ci"] if ci else []), "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["valid"] is True and result["effects"] == []
    assert "private" not in output.out + output.err
    # Restore the instrumentation before the test-only tree digest reads document bodies.
    monkeypatch.undo()
    assert tree_digest(root) == before


def _three_level_documents(root: Path) -> dict[str, Path]:
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    issue = add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    owners = {"initiative": initiative, "epic": epic, "issue": issue}
    for owner in owners.values():
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (owner / filename).write_text("private planning body")
    return owners
