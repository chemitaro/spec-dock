"""Scope title editing preserves documents and needs no shared engine control."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_dependency import dependency_workspace
from tests.cli_runtime.test_issue413_finish import github_fixture

if TYPE_CHECKING:
    from pathlib import Path


def test_scope_edit_updates_only_the_selected_metadata_title_without_github_or_control(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    payload = json.loads(metadata.read_bytes())
    payload["unknown"] = {"nested": ["保全", {"value": True}]}
    metadata.write_text(json.dumps(payload))
    metadata.chmod(0o640)
    document = metadata.parent / "requirement.md"
    document.write_text("# 人間が編集した仕様\n保持する本文。\n")
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (*root.glob("spec-dock/**/.meta.json"), record, document)}
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "edit",
            "@epic",
            "--title",
            "  更新したタイトル  ",
            "--offline",
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    scope = result["data"]["result"]["scope"]
    assert result["data"]["kind"] == "scope" and result["data"]["result"]["changed"] is True
    assert scope["id"] == "epic-00002" and scope["title"] == "更新したタイトル" and scope["revision"] == 1
    assert result["effects"] == [{"kind": "metadata", "status": "succeeded", "target": "epic-00002"}]
    assert json.loads(metadata.read_bytes()) == {**payload, "title": "更新したタイトル", "revision": 1}
    assert stat.S_IMODE(metadata.stat().st_mode) == 0o640
    assert all(path.read_bytes() == exact for path, exact in before.items() if path != metadata)
    assert output.err == "" and not log.exists() and not (root / ".git/spec-dock").exists()


def test_scope_edit_dry_run_returns_a_valid_title_plan_without_staging_or_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in (metadata, child)}
    assert (
        main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "変更予定", "--dry-run", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert result["status"] == "planned" and data["can_apply"] is True and data["blockers"] == []
    assert data["changed"] is False and data["scope"]["title"] == "変更予定"
    assert result["effects"] == [{"kind": "metadata", "status": "planned", "target": "epic-00002"}]
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()


def test_scope_edit_preserves_genuine_existing_local_lifecycle_without_remote_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    payload = json.loads(metadata.read_bytes())
    payload.update(
        backend="local",
        github=None,
        lifecycle={"state": "open", "revision": 6, "updated_at": "2026-09-29T00:00:00Z", "extra": ["保全"]},
    )
    metadata.write_text(json.dumps(payload))
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "edit",
            "epic-00002",
            "--title",
            "既存資料の編集",
            "--offline",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["github_ref"] is None and data["scope"]["backend"] == "local"
    assert data["scope"]["status"]["state"] == "open" and data["changed"] is True
    assert json.loads(metadata.read_bytes()) == {**payload, "title": "既存資料の編集", "revision": 1}
    assert not log.exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("dry_run", [False, True])
def test_scope_edit_same_title_preserves_bytes_revision_and_identity_without_staging(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    before = metadata.read_bytes()
    payload = json.loads(before)
    identity = metadata.stat().st_dev, metadata.stat().st_ino
    options = ["--dry-run"] if dry_run else []
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "edit",
            "epic-00002",
            "--title",
            f"  {payload['title']}  ",
            *options,
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == ("planned" if dry_run else "unchanged") and result["effects"] == []
    assert result["data"]["result"]["changed"] is False
    assert result["data"]["result"]["scope"]["revision"] == payload["revision"]
    if dry_run:
        assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert metadata.read_bytes() == before and (metadata.stat().st_dev, metadata.stat().st_ino) == identity
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "epic-00002"]])
def test_scope_edit_guard_mismatch_preserves_title_documents_and_direct_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root, metadata, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (metadata, child, record)}
    assert main(["--project", str(root), "scope", "edit", "@epic", "--title", "拒否する変更", *guard, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and result["error"]["code"] == "PRECONDITION_FAILED"
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not (root / "spec-dock/.agent/staging").exists()


def test_scope_edit_confirmed_publication_cleanup_failure_keeps_the_updated_scope_and_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    previous = metadata.stat().st_dev, metadata.stat().st_ino
    real_close = os.close
    failed = False

    def close(descriptor: int) -> None:
        nonlocal failed
        observed = os.fstat(descriptor)
        current = metadata.stat()
        identity = observed.st_dev, observed.st_ino
        should_fail = not failed and identity == (current.st_dev, current.st_ino) and identity != previous
        real_close(descriptor)
        if should_fail:
            failed = True
            raise OSError("fixture: confirmed title publication cleanup failed")

    monkeypatch.setattr(os, "close", close)
    assert main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "確認済みタイトル", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert failed and result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["scope"]["title"] == "確認済みタイトル"
    assert result["effects"] == [{"kind": "metadata", "status": "succeeded", "target": "epic-00002"}]
    assert json.loads(metadata.read_bytes())["title"] == "確認済みタイトル"
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_scope_edit_uncertain_replacement_does_not_claim_an_observed_scope_or_repeat_the_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    real_replace = os.replace
    attempts: list[str] = []

    def replace(source_path: str, destination_path: str, **kwargs: int) -> None:
        attempts.append(destination_path)
        real_replace(source_path, destination_path, **kwargs)
        raise OSError("fixture: replacement result unavailable")

    monkeypatch.setattr(os, "replace", replace)
    assert main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "不明な置換", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert attempts == [".meta.json"] and result["status"] == "partial"
    assert result["data"]["result"]["scope"] is None and result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "metadata", "status": "unknown", "target": "epic-00002"}]
    assert json.loads(metadata.read_bytes())["title"] == "不明な置換"
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_scope_edit_preserves_an_actor_change_detected_before_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    payload = json.loads(metadata.read_bytes())
    actor = {**payload, "revision": payload["revision"] + 1, "actor": {"preserve": True}}
    real_fsync = os.fsync
    edited = False

    def fsync(descriptor: int) -> None:
        nonlocal edited
        if not edited and stat.S_ISREG(os.fstat(descriptor).st_mode):
            edited = True
            metadata.write_text(json.dumps(actor))
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "拒否する変更", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert edited and result["data"]["result"]["changed"] is False
    assert result["effects"] == [{"kind": "metadata", "status": "not_attempted", "target": "epic-00002"}]
    assert json.loads(metadata.read_bytes()) == actor
    assert not list((root / "spec-dock/.agent/staging").iterdir())


@pytest.mark.skipif(os.name != "posix", reason="native POSIX executable Git boundary")
def test_scope_edit_native_git_failure_after_confirmed_publication_keeps_original_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    native_git = shutil.which("git")
    assert native_git is not None
    bin_dir = tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    diagnostic = "fixture: original Git failure\nsecond diagnostic line\n"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        f"if sys.argv[-2:] == ['rev-parse', '--show-toplevel'] and json.load(open({str(metadata)!r}))['title'] == '公開後の確認':\n"
        f" sys.stderr.write({diagnostic!r}); sys.exit(73)\n"
        f"os.execv({native_git!r}, [{native_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "公開後の確認", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["status"] == "partial" and result["data"]["result"]["changed"] is True
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == diagnostic
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["effects"] == [{"kind": "metadata", "status": "succeeded", "target": "epic-00002"}]
    assert result["data"]["result"]["scope"] is None and json.loads(metadata.read_bytes())["title"] == "公開後の確認"


def test_scope_edit_help_describes_local_metadata_without_cached_state_or_journal_recovery(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "scope", "edit"]) == 0
    output = capsys.readouterr().out
    assert "specdock.cli/v2" in output and "scope, github_ref, changed" in output
    assert "cached" not in output and "--resume" not in output and "journal" not in output


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory flock boundary")
def test_scope_edit_proceeds_while_start_exclusion_is_held(tmp_path: Path) -> None:
    import fcntl

    root, metadata, _child = dependency_workspace(tmp_path)
    descriptor = os.open(root / ".git", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "scope",
                "edit",
                "epic-00002",
                "--title",
                "ロック外の編集",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == "" and json.loads(result.stdout)["data"]["result"]["changed"] is True
        assert json.loads(metadata.read_bytes())["title"] == "ロック外の編集" and not (root / ".git/spec-dock").exists()
    finally:
        os.close(descriptor)


def test_scope_edit_dry_run_refuses_redirected_staging_and_preserves_the_external_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, metadata, _child = dependency_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "preserve.txt"
    marker.write_bytes(b"preserve external content")
    agent = root / "spec-dock/.agent"
    agent.mkdir()
    (agent / "staging").symlink_to(outside, target_is_directory=True)
    before = metadata.read_bytes()
    assert (
        main(["--project", str(root), "scope", "edit", "epic-00002", "--title", "拒否する変更", "--dry-run", "--json"])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 128
    assert "is beyond a symbolic link\n" in result["error"]["details"]["git"]["stderr"]
    assert result["effects"] == [] and metadata.read_bytes() == before
    assert marker.read_bytes() == b"preserve external content" and sorted(path.name for path in outside.iterdir()) == [
        "preserve.txt"
    ]
    assert (agent / "staging").is_symlink()
