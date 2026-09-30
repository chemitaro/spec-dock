"""Public Start keeps Git checkout and publishes only a local direct target."""

from __future__ import annotations

from dataclasses import replace
import json
import os
import shlex
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.contracts import GithubIssueRecord
from tests.cli_runtime.test_issue413_contract import make_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "retired",
    [["--source", "cache"], ["--source=cache"], ["--allow-stale"], ["--resume", "0" * 32], ["--rollback", "0" * 32]],
)
def test_start_rejects_retired_inputs_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], retired: list[str]
) -> None:
    assert main(["--project", str(tmp_path / "missing"), "work", "start", "iss-00413", *retired, "--json"]) == 2
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert output.err == ""
    assert list(tmp_path.iterdir()) == []


def committed_workspace(root: Path) -> Path:
    make_workspace(root)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    return root


def open_issue(root: Path, repository: str, number: int) -> GithubIssueRecord:
    return GithubIssueRecord(
        number,
        repository,
        "Fixture",
        "open",
        "open",
        None,
        "2026-09-30T00:00:00Z",
        f"https://github.com/{repository}/issues/{number}",
    )


@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "init-00001"]])
def test_start_expectation_mismatch_stops_before_git_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    branch_before = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True
    ).stdout
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", *guard, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "EXPECTATION_FAILED"
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent/work-target").exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True
        ).stdout
        == branch_before
    )


def test_start_requires_ascii_branch_name_before_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--base",
            "HEAD",
            "--branch",
            "feature/日本語",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent/work-target").exists()


def test_start_rejects_candidate_without_scope_before_creating_or_checking_out_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    original = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.rstrip("\n")
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "bad-base"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(root), "rm", "spec-dock/initiatives/init-00001-fixture/.meta.json"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "no scope",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "checkout", "-q", original], check=True, capture_output=True)

    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "bad-base", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent/work-target").exists()
    assert (
        subprocess.run(
            ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True, text=True
        ).stdout
        == original + "\n"
    )
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "refs/heads/init-00001-fixture"], capture_output=True
        ).returncode
        != 0
    )


@pytest.mark.parametrize("ancestor_changed", [False, True])
def test_start_reads_three_level_candidate_metadata_before_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], ancestor_changed: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    base = json.loads((initiative / ".meta.json").read_bytes())
    epic = initiative / "epics/epic-00002-fixture"
    issue = epic / "issues/iss-00003-fixture"
    for path, scope_id, kind, parent, number, epic_id in (
        (epic, "epic-00002", "epic", "init-00001", 2, None),
        (issue, "iss-00003", "issue", "epic-00002", 3, "epic-00002"),
    ):
        path.mkdir(parents=True)
        metadata = dict(base, id=scope_id, type=kind, parent_id=parent, initiative_id="init-00001", epic_id=epic_id)
        metadata["github"] = dict(base["github"], issue_number=number)
        (path / ".meta.json").write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "hierarchy",
        ],
        check=True,
        capture_output=True,
    )
    if ancestor_changed:
        subprocess.run(
            ["git", "-C", str(root), "update-index", "--assume-unchanged", str(epic.relative_to(root) / ".meta.json")],
            check=True,
            capture_output=True,
        )

    def get_live(_, repo_root, repository, number):
        if ancestor_changed and number == 3:
            metadata_path = epic / ".meta.json"
            metadata_path.write_bytes(metadata_path.read_bytes() + b"\n")
        return open_issue(repo_root, repository, number)

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", get_live)
    assert main(["--project", str(root), "work", "start", "iss-00003", "--base", "HEAD", "--json"]) == (
        3 if ancestor_changed else 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["scope_id"] == "iss-00003"
    assert result["data"]["started"] is not ancestor_changed
    if ancestor_changed:
        assert result["effects"] == []


@pytest.mark.parametrize("completed", [False, True])
@pytest.mark.parametrize("duplicate", [False, True])
def test_start_requires_candidate_dependency_itself_to_be_completed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    completed: bool,
    duplicate: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    first = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata = json.loads(first.read_bytes())
    second = first.parent.parent / "init-00002-fixture"
    second.mkdir()
    dependency = dict(metadata, id="init-00002", github=dict(metadata["github"], issue_number=2))
    (second / ".meta.json").write_text(json.dumps(dependency))
    metadata["depends_on"] = ["init-00002"] * (2 if duplicate else 1)
    first.write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "dependency",
        ],
        check=True,
        capture_output=True,
    )
    calls: list[int] = []

    def get_live(_, repo_root, repository, number):
        calls.append(number)
        record = open_issue(repo_root, repository, number)
        return (
            replace(record, state="completed", raw_state="closed", state_reason="completed")
            if number == 2 and completed
            else record
        )

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", get_live)
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == (
        0 if completed and not duplicate else 3
    )
    result = json.loads(capsys.readouterr().out)
    assert sorted(calls) == ([] if duplicate else [1, 2])
    if duplicate:
        assert result["error"]["code"] == "PRECONDITION_FAILED"
        assert result["effects"] == []
    elif not completed:
        assert result["error"]["code"] == "READINESS_NOT_SATISFIED"
        assert result["effects"] == []
        assert not (root / "spec-dock/.agent/work-target").exists()
    else:
        assert result["data"]["started"] is True


def test_start_allows_candidate_title_change_with_same_scope_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata_path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    original = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.rstrip("\n")
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "revised-base"], check=True, capture_output=True)
    metadata = json.loads(metadata_path.read_bytes())
    metadata["title"] = "Revised title"
    metadata_path.write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "title",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "checkout", "-q", original], check=True, capture_output=True)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "revised-base", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is True
    assert json.loads(metadata_path.read_bytes())["title"] == "Revised title"


def test_same_scope_on_different_branch_replaces_only_captured_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    old_token = first["data"]["selection_token"]
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "alternate",
            "--base",
            "HEAD",
            "--json",
        ])
        == 0
    )
    second = json.loads(capsys.readouterr().out)
    new_token = second["data"]["selection_token"]
    assert old_token != new_token
    assert second["data"]["branch_after"] == "alternate"
    assert second["effects"][-2:] == [
        {"kind": "selection.clear", "status": "succeeded", "target": "init-00001"},
        {"kind": "selection.publish", "status": "succeeded", "target": "init-00001"},
    ]
    assert [path.name for path in (root / "spec-dock/.agent/work-target").iterdir()] == [f"target-{new_token}.json"]


@pytest.mark.parametrize("switch", [False, True])
def test_different_scope_requires_explicit_switch_and_replaces_only_old_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], switch: bool
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    first_path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata = json.loads(first_path.read_bytes())
    second = first_path.parent.parent / "init-00002-fixture"
    second.mkdir()
    (second / ".meta.json").write_text(
        json.dumps(dict(metadata, id="init-00002", github=dict(metadata["github"], issue_number=2)))
    )
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "second scope",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    old_token = json.loads(capsys.readouterr().out)["data"]["selection_token"]
    flags = ["--switch-active"] if switch else []
    assert main(["--project", str(root), "work", "start", "init-00002", "--base", "HEAD", *flags, "--json"]) == (
        0 if switch else 3
    )
    result = json.loads(capsys.readouterr().out)
    directory = root / "spec-dock/.agent/work-target"
    if switch:
        assert result["effects"][-2] == {"kind": "selection.clear", "status": "succeeded", "target": "init-00001"}
        assert [path.name for path in directory.iterdir()] == [f"target-{result['data']['selection_token']}.json"]
        assert not (directory / f"target-{old_token}.json").exists()
    else:
        assert result["error"]["code"] == "SWITCH_ACTIVE_REQUIRED"
        assert result["effects"] == []
        assert [path.name for path in directory.iterdir()] == [f"target-{old_token}.json"]


def test_existing_branch_tip_changed_during_live_get_stops_before_git_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "requested", "HEAD"], check=True, capture_output=True)
    (root / "note.txt").write_text("new tip")
    subprocess.run(["git", "-C", str(root), "add", "note.txt"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "next",
        ],
        check=True,
        capture_output=True,
    )
    original = subprocess.run(
        ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True
    ).stdout

    def get_live(_, repo_root, repository, number):
        subprocess.run(
            ["git", "-C", str(root), "update-ref", "refs/heads/requested", "HEAD"], check=True, capture_output=True
        )
        return open_issue(repo_root, repository, number)

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", get_live)
    assert main(["--project", str(root), "work", "start", "init-00001", "--branch", "requested", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert (
        subprocess.run(
            ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"], check=True, capture_output=True
        ).stdout
        == original
    )


def test_start_creates_checks_out_and_selects_without_git_control(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["kind"] == "work-start"
    assert result["data"]["started"] is True
    assert result["data"]["branch_after"] == "init-00001-fixture"
    assert result["data"]["selection_token"]
    assert [item["kind"] for item in result["effects"]] == ["git.branch.create", "git.checkout", "selection.publish"]
    assert (
        subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
        == "init-00001-fixture"
    )
    records = list((root / "spec-dock/.agent/work-target").glob("target-*.json"))
    assert len(records) == 1
    assert json.loads(records[0].read_bytes())["scope_id"] == "init-00001"
    assert metadata.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == b""


def test_start_does_not_publish_after_checkout_changes_worktree_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    linked = tmp_path / "created-during-checkout"
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(
        "#!/bin/sh\nunset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE\n"
        f"if [ ! -d {shlex.quote(str(linked))} ]; then\n"
        f"  git -C {shlex.quote(str(root))} worktree add --detach {shlex.quote(str(linked))} HEAD >&2\n"
        "fi\n"
    )
    hook.chmod(0o700)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is False
    assert result["error"]["code"] == "WORKTREE_INVENTORY_CHANGED"
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "not_attempted", "target": "init-00001"}
    assert linked.is_dir()
    assert not (root / "spec-dock/.agent/work-target").exists()
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"init-00001-fixture\n"


def test_start_rejects_branch_checked_out_by_another_worktree_before_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "occupied", str(linked), "HEAD"],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    before = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--branch", "occupied", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "BRANCH_IN_USE"
    assert result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == before
    assert not (root / "spec-dock/.agent/work-target").exists()


def test_start_reports_publication_unknown_when_sync_fails_after_record_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    original_fsync = os.fsync
    directory = root / "spec-dock/.agent/work-target"

    def fail_after_publication(descriptor: int) -> None:
        if list(directory.glob("target-*.json")):
            raise OSError("fixture: directory synchronization failed after rename")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_after_publication)
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is False
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "unknown", "target": "init-00001"}
    assert len(list(directory.glob("target-*.json"))) == 1
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"init-00001-fixture\n"


def test_start_reports_failed_publication_when_stage_sync_fails_before_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    original_fsync = os.fsync
    directory = root / "spec-dock/.agent/work-target"

    def fail_stage_sync(descriptor: int) -> None:
        if list(directory.glob(".stage-*")):
            raise OSError("fixture: stage synchronization failed")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_stage_sync)
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["effects"][-1] == {"kind": "selection.publish", "status": "failed", "target": "init-00001"}
    assert not list(directory.glob("target-*.json"))
    assert len(list(directory.glob(".stage-*"))) == 1


def test_switch_reports_clear_unknown_when_sync_fails_after_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    old_token = json.loads(capsys.readouterr().out)["data"]["selection_token"]
    directory = root / "spec-dock/.agent/work-target"

    def failed_clear_sync(descriptor: int) -> None:
        raise OSError("fixture: synchronization failed after unlink")

    monkeypatch.setattr(os, "fsync", failed_clear_sync)
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "alternate",
            "--base",
            "HEAD",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"][-2:] == [
        {"kind": "selection.clear", "status": "unknown", "target": "init-00001"},
        {"kind": "selection.publish", "status": "not_attempted", "target": "init-00001"},
    ]
    assert not (directory / f"target-{old_token}.json").exists()
    assert not list(directory.iterdir())


def test_switch_rechecks_inventory_after_old_target_removal_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    capsys.readouterr()
    original_unlink = os.unlink
    linked = tmp_path / "created-after-clear"

    def unlink_and_add_worktree(path, *, dir_fd=None):
        original_unlink(path, dir_fd=dir_fd)
        if isinstance(path, str) and path.startswith("target-"):
            subprocess.run(
                ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"],
                check=True,
                capture_output=True,
            )

    monkeypatch.setattr(os, "unlink", unlink_and_add_worktree)
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "alternate",
            "--base",
            "HEAD",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "WORKTREE_INVENTORY_CHANGED"
    assert result["effects"][-2:] == [
        {"kind": "selection.clear", "status": "succeeded", "target": "init-00001"},
        {"kind": "selection.publish", "status": "not_attempted", "target": "init-00001"},
    ]
    assert not list((root / "spec-dock/.agent/work-target").iterdir())


def test_start_dry_run_does_not_take_lock_or_create_branch_or_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )

    def forbidden_lock(self: object) -> None:
        raise AssertionError("dry-run must not acquire Start lock")

    monkeypatch.setattr("spec_dock.runtime.application.work_start.StartLock.__enter__", forbidden_lock)
    before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["started"] is False
    assert {item["status"] for item in result["effects"]} == {"planned"}
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before
    assert not (root / "spec-dock/.agent").exists()


def test_checkout_failure_preserves_created_branch_and_native_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    # Git's own index lock rejects checkout, while branch creation remains possible.
    (root / ".git/index.lock").write_bytes(b"")
    before = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "partial"
    assert result["data"]["started"] is False
    assert [(item["kind"], item["status"]) for item in result["effects"]] == [
        ("git.branch.create", "succeeded"),
        ("git.checkout", "failed"),
        ("selection.publish", "not_attempted"),
    ]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip() == before
    native = subprocess.run(
        ["git", "-C", str(root), "checkout", "init-00001-fixture"], capture_output=True, check=False
    )
    assert result["error"]["details"]["git"]["stderr"] == native.stderr.decode()
    assert result["error"]["details"]["git"]["returncode"] == native.returncode
    assert not output.err
    assert not (root / "spec-dock/.agent").exists()


def test_failed_post_checkout_hook_reports_observed_head_without_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nprintf 'fixture: post-checkout failed\\n' >&2\nexit 1\n")
    hook.chmod(0o700)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is False
    assert result["data"]["branch_after"] == "init-00001-fixture"
    assert result["effects"][1] == {"kind": "git.checkout", "status": "succeeded", "target": "init-00001-fixture"}
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert "fixture: post-checkout failed\n" in result["error"]["details"]["git"]["stderr"]
    assert not (root / "spec-dock/.agent/work-target").exists()


def test_readonly_git_probe_failure_after_checkout_does_not_relabel_checkout_as_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    real_run = subprocess.run

    def fail_post_checkout_probe(argv, **kwargs):
        if "check-ignore" in argv and (root / ".git/HEAD").read_text() == "ref: refs/heads/init-00001-fixture\n":
            return subprocess.CompletedProcess(argv, 19, stdout=b"", stderr=b"fixture: readonly ignore probe failed\n")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", fail_post_checkout_probe)
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("git.branch.create", "succeeded"),
        ("git.checkout", "succeeded"),
        ("selection.publish", "not_attempted"),
    ]
    assert result["error"]["details"]["git"]["returncode"] == 19


def test_existing_branch_requires_explicit_reuse_and_no_base(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    subprocess.run(["git", "-C", str(root), "branch", "init-00001-fixture"], check=True, capture_output=True)
    assert main(["--project", str(root), "work", "start", "init-00001", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "init-00001-fixture",
            "--base",
            "HEAD",
            "--json",
        ])
        == 3
    )
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert (
        main(["--project", str(root), "work", "start", "init-00001", "--branch", "init-00001-fixture", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is True
    assert result["effects"][0] == {"kind": "git.branch.create", "status": "unchanged", "target": "init-00001-fixture"}


def test_text_checkout_failure_preserves_native_stderr_newlines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    (root / ".git/index.lock").write_bytes(b"")
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD"]) == 6
    output = capsys.readouterr()
    native = subprocess.run(
        ["git", "-C", str(root), "checkout", "init-00001-fixture"], capture_output=True, check=False
    )
    assert output.err.endswith(native.stderr.decode())
    assert "spec-dock: partial" in output.out


def test_start_refuses_unignored_state_before_creating_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    (root / "spec-dock/.gitignore").write_bytes(b"")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "unignored",
        ],
        check=True,
        capture_output=True,
    )
    before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert "ignored" in result["error"]["message"]
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before
    assert not (root / "spec-dock/.agent").exists()


def test_start_rechecks_clean_state_after_acquiring_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    original_enter = StartLock.__enter__

    def enter_and_edit(lock: StartLock) -> StartLock:
        result = original_enter(lock)
        (root / "untracked.txt").write_text("changed after preflight")
        return result

    monkeypatch.setattr(StartLock, "__enter__", enter_and_edit)
    before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before
    assert (root / "untracked.txt").read_text() == "changed after preflight"


def test_other_worktree_stale_selection_reserves_scope_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.application.project_context import resolve_context
    from spec_dock.runtime.domain.work_target import WorkTarget
    from spec_dock.runtime.infra.work_target_store import WorkTargetStore

    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    other = resolve_context(str(linked), linked)
    with WorkTargetStore(linked) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                "init-00001",
                "gh:example/repo#1",
                "old",
                "2026-09-30T00:00:00Z",
                other.clone_identity,
                other.worktree_identity,
            )
        )
        before_record = (store.path / handle.basename).read_bytes()
    (linked / "spec-dock/initiatives/init-00001-fixture/.meta.json").unlink()
    before_refs = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "SCOPE_ALREADY_SELECTED"
    assert result["effects"] == []
    assert (linked / "spec-dock/.agent/work-target" / handle.basename).read_bytes() == before_record
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == before_refs


def test_same_valid_target_on_same_branch_is_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get",
        lambda self, root, repo, number: open_issue(root, repo, number),
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    records = {path.name: path.read_bytes() for path in (root / "spec-dock/.agent/work-target").iterdir()}
    assert (
        main(["--project", str(root), "work", "start", "init-00001", "--branch", "init-00001-fixture", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "unchanged"
    assert result["data"]["started"] is True
    assert result["data"]["selection_token"] == first["data"]["selection_token"]
    assert {path.name: path.read_bytes() for path in (root / "spec-dock/.agent/work-target").iterdir()} == records
    assert {item["status"] for item in result["effects"]} <= {"unchanged"}


def test_unchanged_start_rejects_metadata_different_from_candidate_even_when_git_is_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata_path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 0
    capsys.readouterr()
    record_directory = root / "spec-dock/.agent/work-target"
    records_before = {path.name: path.read_bytes() for path in record_directory.iterdir()}
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--assume-unchanged", str(metadata_path.relative_to(root))],
        check=True,
        capture_output=True,
    )
    metadata = json.loads(metadata_path.read_bytes())
    metadata["title"] = "Uncommitted metadata hidden from Git status"
    metadata_path.write_text(json.dumps(metadata))
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == b""
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "init-00001-fixture",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["started"] is False
    assert result["effects"] == []
    assert {path.name: path.read_bytes() for path in record_directory.iterdir()} == records_before


@pytest.mark.parametrize("where", ["current", "candidate"])
def test_start_rejects_scope_unknown_required_feature_before_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    where: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    original = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]).decode().rstrip("\n")
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-qb", "bad-base"], check=True, capture_output=True)
    metadata_path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata = json.loads(metadata_path.read_bytes())
    metadata["required_features"] = ["future.scope-feature"]
    metadata_path.write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "unsupported scope feature",
        ],
        check=True,
        capture_output=True,
    )
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-q", original], check=True, capture_output=True)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    base = "bad-base" if where == "candidate" else "HEAD"
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", base, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent/work-target").exists()


def test_start_writer_rejects_scope_missing_required_nullable_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata_path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata = json.loads(metadata_path.read_bytes())
    del metadata["parent_id"]
    metadata_path.write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "missing schema field",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", "HEAD", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"required_features": None},
        {"required_features": False},
        {"required_features": 0},
        {"required_features": ""},
        {"required_features": {}},
        {"required_features": [1]},
        {"type": "workspace"},
        {"control_epoch": 1},
    ],
)
@pytest.mark.parametrize("where", ["current", "candidate"])
def test_start_rejects_invalid_writer_workspace_before_git_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    bad_payload: dict[str, object],
    where: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    original = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]).decode().rstrip("\n")
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-qb", "bad-base"], check=True, capture_output=True)
    workspace = root / "spec-dock/workspace.json"
    payload = json.loads(workspace.read_bytes())
    workspace.write_text(json.dumps(dict(payload, **bad_payload)))
    subprocess.run(["git", "-C", str(root), "add", "spec-dock"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "invalid workspace",
        ],
        check=True,
        capture_output=True,
    )
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-q", original], check=True, capture_output=True)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    base = "bad-base" if where == "candidate" else "HEAD"
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", base, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent/work-target").exists()


@pytest.mark.parametrize("where", ["current", "candidate"])
def test_start_rejects_probe_only_ignore_rule_before_git_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    where: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    original = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]).decode().rstrip("\n")
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-qb", "bad-base"], check=True, capture_output=True)
    (root / "spec-dock/.gitignore").write_text(".agent/work-target/target-0*.json\n.agent/work-target/.stage-0*\n")
    subprocess.run(["git", "-C", str(root), "add", "spec-dock/.gitignore"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "probe only ignore",
        ],
        check=True,
        capture_output=True,
    )
    if where == "candidate":
        subprocess.run(["git", "-C", str(root), "checkout", "-q", original], check=True, capture_output=True)
    monkeypatch.setattr("secrets.token_hex", lambda size: "f" * 32)
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    refs_before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    base = "bad-base" if where == "candidate" else "HEAD"
    assert main(["--project", str(root), "work", "start", "init-00001", "--base", base, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "WORK_TARGET_PATH_NOT_IGNORED"
    assert result["effects"] == []
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == refs_before
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == b""
