"""Public Start keeps Git checkout and publishes only a local direct target."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.contracts import GithubIssueRecord
from tests.cli_runtime.test_issue413_contract import make_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


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
