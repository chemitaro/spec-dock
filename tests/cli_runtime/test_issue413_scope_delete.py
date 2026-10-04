"""Explicit local subtree deletion retains verified backups and honest effects."""

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


@pytest.mark.parametrize("container_kind", ["initiative", "epic", "issue"])
@pytest.mark.parametrize("private_name", [".workbench", ".workbench-copy"])
@pytest.mark.parametrize("target", ["iss-00003", "iss-00099"])
def test_scope_delete_ignores_private_and_noncanonical_containers_without_reading_them(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    container_kind: str,
    private_name: str,
    target: str,
) -> None:
    from pathlib import Path

    root, parent, metadata = dependency_workspace(tmp_path)
    containers = {
        "initiative": root / "spec-dock/initiatives",
        "epic": parent.parent.parent,
        "issue": metadata.parent.parent,
    }
    private = containers[container_kind] / private_name
    ghost = private / "iss-00099-private"
    ghost.mkdir(parents=True)
    (ghost / ".meta.json").write_bytes(b"{private malformed metadata")
    duplicate = private / metadata.parent.name
    duplicate.mkdir()
    (duplicate / ".meta.json").write_bytes(metadata.read_bytes())
    (private / "evidence.bin").write_bytes(b"\x00\xffprivate evidence")
    private_before = {path.relative_to(private): path.read_bytes() for path in private.rglob("*") if path.is_file()}
    target_before = {
        path.relative_to(metadata.parent): path.read_bytes() for path in metadata.parent.rglob("*") if path.is_file()
    }
    parent_before = parent.read_bytes()
    metadata_inodes = {(path.stat().st_dev, path.stat().st_ino) for path in private.rglob(".meta.json")}
    backup = tmp_path / "delete-backup"
    log = github_fixture(tmp_path, monkeypatch, {})
    original_open, original_iterdir = os.open, Path.iterdir

    def guarded_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        try:
            observed = os.stat(path, dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if (observed.st_dev, observed.st_ino) in metadata_inodes:
                raise AssertionError("Scope delete attempted to read private metadata")
        return original_open(path, flags, mode, dir_fd=dir_fd)

    def guarded_iterdir(path: Path):
        if path == private or path.is_relative_to(private):
            raise AssertionError("Scope delete attempted to enumerate a noncanonical container")
        return original_iterdir(path)

    with monkeypatch.context() as guard:
        guard.setattr(os, "open", guarded_open)
        guard.setattr(Path, "iterdir", guarded_iterdir)
        code = main(["--project", str(root), "scope", "delete", target, "--backup-dir", str(backup), "--yes", "--json"])
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert {
        path.relative_to(private): path.read_bytes() for path in private.rglob("*") if path.is_file()
    } == private_before
    assert parent.read_bytes() == parent_before and not log.exists()
    assert not (root / ".git/spec-dock").exists()
    if target == "iss-00003":
        assert code == 0 and result["status"] == "succeeded"
        assert result["data"]["result"]["removed_ids"] == [target]
        assert not metadata.parent.exists()
        restored = backup / metadata.parent.relative_to(root)
        assert {
            path.relative_to(restored): path.read_bytes() for path in restored.rglob("*") if path.is_file()
        } == target_before
    else:
        assert code == 4 and result["error"]["code"] == "SCOPE_NOT_FOUND" and result["effects"] == []
        assert not backup.exists()
        assert {
            path.relative_to(metadata.parent): path.read_bytes()
            for path in metadata.parent.rglob("*")
            if path.is_file()
        } == target_before


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


@pytest.mark.skipif(os.name != "posix", reason="native POSIX FIFO boundary")
def test_scope_delete_refuses_a_fifo_before_creating_backup_without_blocking(tmp_path: Path) -> None:
    root, _parent, metadata = dependency_workspace(tmp_path)
    fifo = metadata.parent / "unsupported-fifo"
    os.mkfifo(fifo)
    before = metadata.read_bytes()
    backup = tmp_path / "delete-backup"
    process = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()
    assert process.returncode == 3, stdout + stderr
    assert stderr == "" and json.loads(stdout)["effects"] == []
    assert fifo.exists() and metadata.read_bytes() == before and not backup.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX terminal fixture")
@pytest.mark.parametrize("answer", [b"yes\n", b"no\n"])
def test_scope_delete_accepts_or_declines_terminal_confirmation_after_showing_its_plan(
    tmp_path: Path, answer: bytes
) -> None:
    from pathlib import Path
    import pty

    root, _parent, metadata = dependency_workspace(tmp_path)
    before = metadata.read_bytes()
    backup = tmp_path / "delete-backup"
    master, slave = pty.openpty()
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "spec_dock.cli",
                "--project",
                str(root),
                "scope",
                "delete",
                "iss-00003",
                "--backup-dir",
                str(backup),
            ],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        )
        os.write(master, answer)
        stdout, stderr = process.communicate(timeout=8)
    finally:
        os.close(master)
        os.close(slave)
    assert b"Confirm" in stderr
    assert b"iss-00003" in stderr and str(backup).encode() in stderr
    if answer == b"yes\n":
        assert process.returncode == 0, stdout + stderr
        assert not metadata.parent.exists()
        assert (backup / metadata.relative_to(root)).read_bytes() == before
    else:
        assert process.returncode == 3, stdout + stderr
        assert b"CONFIRMATION_DECLINED" in stderr
        assert metadata.read_bytes() == before and not backup.exists()
        assert not (root / "spec-dock/.agent").exists()


def test_scope_delete_backs_up_the_exact_subtree_and_preserves_other_scopes_and_github(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, metadata = dependency_workspace(tmp_path)
    document = metadata.parent / "requirement.md"
    document.write_bytes("# 削除前の仕様\n保持する本文。\n".encode())
    scratch = metadata.parent / ".workbench/evidence.bin"
    scratch.parent.mkdir()
    scratch.write_bytes(b"\x00\xffignored evidence")
    before = {path.relative_to(root): path.read_bytes() for path in (metadata, document, scratch)}
    parent_before = parent.read_bytes()
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
            "scope delete fixture",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "branch", "iss-00003-retained", "HEAD"], check=True, capture_output=True)
    exact_branch = subprocess.check_output(["git", "-C", str(root), "rev-parse", "refs/heads/iss-00003-retained"])
    backup = tmp_path / "delete-backup"
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["data"]["kind"] == "deletion" and result["status"] == "succeeded"
    data = result["data"]["result"]
    assert data["removed_ids"] == ["iss-00003"] and data["remaining_paths"] == []
    assert data["backup_path"] == str(backup) and data["changed_paths"] == [
        metadata.parent.relative_to(root).as_posix()
    ]
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "scope.delete", "status": "succeeded", "target": metadata.parent.relative_to(root).as_posix()},
    ]
    assert not metadata.parent.exists() and parent.read_bytes() == parent_before
    assert all((backup / relative).read_bytes() == exact for relative, exact in before.items())
    assert (
        subprocess.check_output(["git", "-C", str(root), "rev-parse", "refs/heads/iss-00003-retained"]) == exact_branch
    )
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert not log.exists() and not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX mode and symlink boundary")
def test_scope_delete_backup_preserves_modes_and_link_bytes_without_following_the_link(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, metadata = dependency_workspace(tmp_path)
    external = tmp_path / "external.txt"
    external.write_bytes(b"external bytes stay unchanged")
    document = metadata.parent / "design.md"
    document.write_bytes(b"scope-owned document")
    document.chmod(0o640)
    link = metadata.parent / "external-link"
    link.symlink_to(external)
    metadata.parent.chmod(0o750)
    backup = tmp_path / "delete-backup"
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 0
    )
    capsys.readouterr()
    copied = backup / metadata.parent.relative_to(root)
    assert stat.S_IMODE(copied.stat().st_mode) == 0o750
    assert stat.S_IMODE((copied / "design.md").stat().st_mode) == 0o640
    assert (copied / "design.md").read_bytes() == b"scope-owned document"
    assert (copied / link.name).is_symlink() and (copied / link.name).readlink() == external
    assert external.read_bytes() == b"external bytes stay unchanged" and not metadata.parent.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory flock boundary")
def test_scope_delete_proceeds_in_another_process_while_start_exclusion_is_held(tmp_path: Path) -> None:
    import fcntl

    root, _parent, metadata = dependency_workspace(tmp_path)
    before = metadata.read_bytes()
    backup = tmp_path / "delete-backup"
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
                "delete",
                "iss-00003",
                "--backup-dir",
                str(backup),
                "--yes",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == "" and json.loads(result.stdout)["data"]["result"]["removed_ids"] == ["iss-00003"]
        assert not metadata.parent.exists() and (backup / metadata.relative_to(root)).read_bytes() == before
        assert not (root / ".git/spec-dock").exists()
    finally:
        os.close(descriptor)


def test_delete_preserves_another_worktree_record_then_sync_observes_it_as_stale_after_checkout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    subprocess.run(["git", "-C", str(root), "add", "--", "spec-dock/initiatives"], check=True, capture_output=True)
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
            "fixture scopes",
        ],
        check=True,
        capture_output=True,
    )
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    own = select_fixture(root, scope_id="iss-00003", number=3)
    other = select_fixture(linked, scope_id="iss-00003", number=3)
    before = other.read_bytes()
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--clear-active",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    assert not own.exists() and not child.parent.exists() and other.read_bytes() == before
    assert (linked / child.relative_to(root)).exists()
    subprocess.run(
        ["git", "-C", str(root), "add", "-u", "--", "spec-dock/initiatives"], check=True, capture_output=True
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
            "fixture deletion",
        ],
        check=True,
        capture_output=True,
    )
    tip = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()
    subprocess.run(["git", "-C", str(linked), "checkout", "--detach", tip], check=True, capture_output=True)
    assert main(["--project", str(root), "workspace", "sync", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    row = next(item for item in result["data"]["worktrees"] if item["path"] == str(linked))
    assert row["selection"]["status"] == "stale" and row["selection"]["scope_id"] == "iss-00003"
    assert result["effects"] == [] and other.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()


def test_delete_does_not_clear_a_new_token_after_the_captured_token_was_removed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    original = record.read_bytes()
    replacement = record.with_name("target-" + "b" * 32 + ".json")
    payload = json.loads(original)
    payload.update(scope_id="epic-00002", github_ref="gh:example/repo#2")
    new_bytes = json.dumps(payload).encode()
    backup = tmp_path / "delete-backup"
    real_unlink = os.unlink
    raced = False

    def unlink(path: str, **kwargs: int) -> None:
        nonlocal raced
        if path == record.name and not raced:
            raced = True
            real_unlink(path, **kwargs)
            replacement.write_bytes(new_bytes)
        real_unlink(path, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--clear-active",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert raced and replacement.read_bytes() == new_bytes and not child.parent.exists()
    assert result["effects"][1] == {"kind": "selection.clear", "status": "unchanged", "target": record.name[7:-5]}
    assert result["data"]["result"]["changed_paths"] == [child.parent.relative_to(root).as_posix()]
    assert (backup / record.relative_to(root)).read_bytes() == original


def test_scope_delete_refuses_a_non_recursive_parent_without_creating_a_backup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in (parent, child)}
    backup = tmp_path / "delete-backup"
    assert (
        main(["--project", str(root), "scope", "delete", "epic-00002", "--backup-dir", str(backup), "--yes", "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and "RECURSIVE_REQUIRED" in result["error"]["message"]
    assert all(path.read_bytes() == exact for path, exact in before.items()) and not backup.exists()


def test_recursive_delete_dry_run_lists_the_plan_without_backup_or_workspace_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    before = {path: path.read_bytes() for path in (parent, child)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "epic-00002",
            "--recursive",
            "--backup-dir",
            str(backup),
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    relative = parent.parent.relative_to(root).as_posix()
    assert result["status"] == "planned" and data["can_apply"] is True and data["blockers"] == []
    assert data["removed_ids"] == [] and data["changed_paths"] == [] and data["remaining_paths"] == [relative]
    assert data["backup_path"] == str(backup)
    assert result["effects"] == [
        {"kind": "backup", "status": "planned", "target": str(backup)},
        {"kind": "scope.delete", "status": "planned", "target": relative},
    ]
    assert all(path.read_bytes() == exact for path, exact in before.items()) and not backup.exists()
    assert not (root / "spec-dock/.agent").exists()


def test_delete_dry_run_lists_dependency_edit_and_captured_clear_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (parent, child, source, record)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "@epic",
            "--recursive",
            "--clear-active",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    relative = parent.parent.relative_to(root).as_posix()
    assert result["effects"] == [
        {"kind": "backup", "status": "planned", "target": str(backup)},
        {"kind": "metadata", "status": "planned", "target": "epic-00004"},
        {"kind": "selection.clear", "status": "planned", "target": record.name[7:-5]},
        {"kind": "scope.delete", "status": "planned", "target": relative},
    ]
    data = result["data"]["result"]
    assert data["can_apply"] is True and data["blockers"] == []
    assert data["removed_ids"] == [] and data["changed_paths"] == []
    assert data["remaining_paths"] == [
        source.relative_to(root).as_posix(),
        record.relative_to(root).as_posix(),
        relative,
    ]
    assert all(path.read_bytes() == exact for path, exact in before.items())
    assert not backup.exists() and not (root / "spec-dock/.agent/staging").exists()


@pytest.mark.parametrize("mode", [["--yes"], ["--dry-run"]])
def test_delete_refuses_a_backup_path_that_traverses_into_git_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], mode: list[str]
) -> None:
    root, _parent, metadata = dependency_workspace(tmp_path)
    before = metadata.read_bytes()
    (root / "scratch").mkdir()
    backup = root / "scratch/../.git/new-backup"
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), *mode, "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert metadata.read_bytes() == before and not (root / ".git/new-backup").exists()


def test_delete_dry_run_refuses_a_redirected_backup_parent_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, metadata = dependency_workspace(tmp_path)
    before = metadata.read_bytes()
    external = tmp_path / "external"
    external.mkdir()
    alias = tmp_path / "backup-alias"
    alias.symlink_to(external, target_is_directory=True)
    backup = alias / "new-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--backup-dir",
            str(backup),
            "--dry-run",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and metadata.read_bytes() == before
    assert list(external.iterdir()) == [] and alias.is_symlink()


def test_delete_dry_run_refuses_redirected_metadata_staging_with_original_git_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    external = tmp_path / "external"
    external.mkdir()
    staging = root / "spec-dock/.agent/staging"
    staging.parent.mkdir()
    staging.symlink_to(external, target_is_directory=True)
    before = {path: path.read_bytes() for path in (source, child)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--dry-run",
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 128
    assert "is beyond a symbolic link\n" in result["error"]["details"]["git"]["stderr"]
    assert result["effects"] == [] and not backup.exists()
    assert all(path.read_bytes() == exact for path, exact in before.items()) and list(external.iterdir()) == []


def test_recursive_delete_requires_clear_active_for_the_captured_direct_descendant(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (parent, child, record)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "@epic",
            "--recursive",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and "CLEAR_ACTIVE_REQUIRED" in result["error"]["message"]
    assert all(path.read_bytes() == exact for path, exact in before.items()) and not backup.exists()


def test_delete_refuses_an_unreadable_direct_selection_without_assuming_it_is_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    record.write_bytes(b"broken direct selection")
    before = {child: child.read_bytes(), record: record.read_bytes()}
    backup = tmp_path / "delete-backup"
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert all(path.read_bytes() == exact for path, exact in before.items()) and not backup.exists()


def test_delete_refuses_incoming_dependencies_without_explicit_detachment(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    before = {path: path.read_bytes() for path in (parent, child, source)}
    backup = tmp_path / "delete-backup"
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and "DETACH_DEPENDENCIES_REQUIRED" in result["error"]["message"]
    assert all(path.read_bytes() == exact for path, exact in before.items()) and not backup.exists()


def test_delete_backs_up_survivor_metadata_and_clears_only_the_captured_direct_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload.update(depends_on=["iss-00003"], unknown={"nested": ["保全"]})
    source.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    token = record.name[7:-5]
    before = {path.relative_to(root): path.read_bytes() for path in (child, source, record)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "@epic",
            "--recursive",
            "--clear-active",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["removed_ids"] == ["epic-00002", "iss-00003"] and data["remaining_paths"] == []
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "metadata", "status": "succeeded", "target": "epic-00004"},
        {"kind": "selection.clear", "status": "succeeded", "target": token},
        {"kind": "scope.delete", "status": "succeeded", "target": parent.parent.relative_to(root).as_posix()},
    ]
    assert json.loads(source.read_bytes()) == {**payload, "depends_on": [], "revision": 1}
    assert all((backup / relative).read_bytes() == exact for relative, exact in before.items())
    assert not record.exists() and not parent.parent.exists()
    assert data["changed_paths"] == [
        source.relative_to(root).as_posix(),
        record.relative_to(root).as_posix(),
        parent.parent.relative_to(root).as_posix(),
    ]
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "@epic"]])
def test_delete_guard_mismatch_stops_before_backup_or_clear(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = {path: path.read_bytes() for path in (parent, child, record)}
    backup = tmp_path / "delete-backup"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "@epic",
            "--recursive",
            "--clear-active",
            "--backup-dir",
            str(backup),
            *guard,
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and all(path.read_bytes() == exact for path, exact in before.items())
    assert not backup.exists()


def test_delete_unknown_detachment_preserves_backup_and_subtree_without_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    original = source.read_bytes()
    backup = tmp_path / "delete-backup"
    real_replace = os.replace
    attempts: list[str] = []

    def replace(source_name: str, destination_name: str, **kwargs: int) -> None:
        attempts.append(destination_name)
        real_replace(source_name, destination_name, **kwargs)
        raise OSError("fixture: detachment outcome unavailable")

    monkeypatch.setattr(os, "replace", replace)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert attempts == [".meta.json"] and child.exists() and parent.exists()
    assert result["status"] == "partial" and result["data"]["result"]["removed_ids"] == []
    assert result["data"]["result"]["changed_paths"] == []
    assert result["data"]["result"]["remaining_paths"] == [
        source.relative_to(root).as_posix(),
        child.parent.relative_to(root).as_posix(),
    ]
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "metadata", "status": "unknown", "target": "epic-00004"},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert (backup / source.relative_to(root)).read_bytes() == original
    assert json.loads(source.read_bytes())["depends_on"] == []
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_delete_preserves_a_changed_direct_record_and_the_subtree_after_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    token = record.name[7:-5]
    before = record.read_bytes()
    actor = {**json.loads(before), "selected_branch": "actor-branch"}
    backup = tmp_path / "delete-backup"
    real_mkdir = os.mkdir
    changed = False

    def mkdir(path: str, mode: int = 0o777, **kwargs: int) -> None:
        nonlocal changed
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not changed:
            changed = True
            record.write_text(json.dumps(actor))

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--clear-active",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and result["status"] == "partial" and child.exists()
    assert json.loads(record.read_bytes()) == actor and (backup / record.relative_to(root)).read_bytes() == before
    assert result["data"]["result"]["removed_ids"] == [] and result["data"]["result"]["changed_paths"] == []
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "selection.clear", "status": "failed", "target": token},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_incomplete_backup_is_retained_and_never_allows_subtree_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    destination_parent = backup / child.parent.relative_to(root)
    real_open = os.open
    failed = False

    def open_file(path: str, flags: int, mode: int = 0o777, **kwargs: int) -> int:
        nonlocal failed
        parent = kwargs.get("dir_fd")
        if path == ".meta.json" and flags & os.O_CREAT and parent is not None and destination_parent.exists():
            opened, saved_parent = os.fstat(parent), destination_parent.stat()
            if (opened.st_dev, opened.st_ino) == (saved_parent.st_dev, saved_parent.st_ino):
                failed = True
                raise OSError("fixture: backup destination write failed")
        return real_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", open_file)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert failed and backup.is_dir() and child.read_bytes() == before
    assert result["status"] == "partial" and result["data"]["result"]["removed_ids"] == []
    assert result["effects"] == [
        {"kind": "backup", "status": "unknown", "target": str(backup)},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_delete_preserves_actor_metadata_changed_before_detachment_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    actor = {**payload, "actor": {"preserve": True}, "revision": 1}
    backup = tmp_path / "delete-backup"
    real_fsync = os.fsync
    changed = False

    def fsync(descriptor: int) -> None:
        nonlocal changed
        if not changed and stat.S_ISREG(os.fstat(descriptor).st_mode):
            try:
                candidate = json.loads(os.pread(descriptor, 65536, 0))
            except (OSError, ValueError):
                candidate = None
            if isinstance(candidate, dict) and candidate.get("depends_on") == [] and candidate.get("revision") == 1:
                changed = True
                source.write_text(json.dumps(actor))
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and json.loads(source.read_bytes()) == actor and child.exists()
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "metadata", "status": "not_attempted", "target": "epic-00004"},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert json.loads((backup / source.relative_to(root)).read_bytes()) == payload
    assert not list((root / "spec-dock/.agent/staging").iterdir())


@pytest.mark.skipif(os.name != "posix", reason="native POSIX executable Git boundary")
def test_delete_post_removal_git_failure_keeps_confirmed_deletion_and_original_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    native_git = shutil.which("git")
    assert native_git is not None
    bin_dir = tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    diagnostic = "fixture: post-removal Git failure\nsecond diagnostic line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        f"if sys.argv[-2:] == ['rev-parse', '--show-toplevel'] and not os.path.exists({str(child.parent)!r}):\n"
        f" sys.stderr.write({diagnostic!r}); sys.exit(73)\n"
        f"os.execv({native_git!r}, [{native_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["stderr"] == diagnostic
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert result["data"]["result"]["removed_ids"] == ["iss-00003"]
    assert result["data"]["result"]["remaining_paths"] == []
    assert result["data"]["result"]["changed_paths"] == [child.parent.relative_to(root).as_posix()]
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "scope.delete", "status": "succeeded", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert not child.parent.exists() and (backup / child.relative_to(root)).read_bytes() == before


def test_confirmed_direct_clear_survives_a_later_descriptor_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    held = record.parent.stat()
    backup = tmp_path / "delete-backup"
    real_close = os.close
    injected = False

    def close(descriptor: int) -> None:
        nonlocal injected
        opened = os.fstat(descriptor)
        confirmed = not record.exists() and (opened.st_dev, opened.st_ino) == (held.st_dev, held.st_ino)
        real_close(descriptor)
        if confirmed and not injected:
            injected = True
            raise OSError("fixture: confirmed clear cleanup failed")

    monkeypatch.setattr(os, "close", close)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--clear-active",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert injected and not record.exists() and child.exists()
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "selection.clear", "status": "succeeded", "target": record.name[7:-5]},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert result["data"]["result"]["changed_paths"] == [record.relative_to(root).as_posix()]
    assert result["data"]["result"]["remaining_paths"] == [child.parent.relative_to(root).as_posix()]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX executable Git boundary")
def test_delete_native_git_failure_after_detachment_keeps_applied_effects_and_original_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, parent, child = dependency_workspace(tmp_path)
    source = parent.parent.parent / "epic-00004-fixture/.meta.json"
    payload = json.loads(source.read_bytes())
    payload["depends_on"] = ["iss-00003"]
    source.write_text(json.dumps(payload))
    record = select_fixture(root, scope_id="iss-00003", number=3)
    backup = tmp_path / "delete-backup"
    native_git = shutil.which("git")
    assert native_git is not None
    bin_dir = tmp_path / "git-bin"
    bin_dir.mkdir()
    executable = bin_dir / "git"
    diagnostic = "fixture: original Git failure\nsecond diagnostic line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport json, os, sys\n"
        f"if sys.argv[-2:] == ['rev-parse', '--show-toplevel'] and json.load(open({str(source)!r}))['depends_on'] == []:\n"
        f" sys.stderr.write({diagnostic!r}); sys.exit(73)\n"
        f"os.execv({native_git!r}, [{native_git!r}, *sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "delete",
            "iss-00003",
            "--clear-active",
            "--detach-dependencies",
            "--backup-dir",
            str(backup),
            "--yes",
            "--json",
        ])
        == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["error"]["code"] == "GIT_FAILED"
    assert (
        result["error"]["details"]["git"]["stderr"] == diagnostic
        and result["error"]["details"]["git"]["returncode"] == 73
    )
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "metadata", "status": "succeeded", "target": "epic-00004"},
        {"kind": "selection.clear", "status": "not_attempted", "target": record.name[7:-5]},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert result["data"]["result"]["changed_paths"] == [source.relative_to(root).as_posix()]
    assert record.exists() and child.exists() and json.loads(source.read_bytes())["depends_on"] == []


def test_subtree_unlink_with_unknown_outcome_retains_backup_and_reports_each_unfinished_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    real_unlink = os.unlink
    attempted = False

    def unlink(path: str, **kwargs: int) -> None:
        nonlocal attempted
        real_unlink(path, **kwargs)
        if path == ".meta.json" and not attempted:
            attempted = True
            raise OSError("fixture: unlink outcome unavailable")

    monkeypatch.setattr(os, "unlink", unlink)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert attempted and not child.exists() and child.parent.is_dir()
    assert (backup / child.relative_to(root)).read_bytes() == before
    documents = [child.parent / filename for filename in ("design.md", "plan.md", "report.md", "requirement.md")]
    assert all(path.read_bytes() == (backup / path.relative_to(root)).read_bytes() for path in documents)
    assert result["data"]["result"]["removed_ids"] == [] and result["data"]["result"]["changed_paths"] == []
    assert result["data"]["result"]["remaining_paths"] == [
        child.relative_to(root).as_posix(),
        *(path.relative_to(root).as_posix() for path in documents),
        child.parent.relative_to(root).as_posix(),
    ]
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "scope.delete", "status": "unknown", "target": child.relative_to(root).as_posix()},
        *(
            {"kind": "scope.delete", "status": "not_attempted", "target": path.relative_to(root).as_posix()}
            for path in documents
        ),
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_subtree_removal_preserves_a_new_file_that_was_not_in_the_verified_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    held = child.parent.stat()
    backup = tmp_path / "delete-backup"
    late = child.parent / "late.txt"
    real_listdir = os.listdir
    injected = False

    def listdir(path):
        nonlocal injected
        if isinstance(path, int):
            opened = os.fstat(path)
            if (
                not injected
                and (opened.st_dev, opened.st_ino) == (held.st_dev, held.st_ino)
                and (backup / child.relative_to(root)).exists()
            ):
                injected = True
                late.write_bytes(b"actor content without a backup")
        return real_listdir(path)

    monkeypatch.setattr(os, "listdir", listdir)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert injected and late.read_bytes() == b"actor content without a backup"
    assert not (backup / late.relative_to(root)).exists()
    assert result["data"]["result"]["removed_ids"] == []
    assert result["data"]["result"]["changed_paths"] == [
        child.relative_to(root).as_posix(),
        (child.parent / "design.md").relative_to(root).as_posix(),
    ]
    documents = [child.parent / filename for filename in ("plan.md", "report.md", "requirement.md")]
    assert all(path.read_bytes() == (backup / path.relative_to(root)).read_bytes() for path in documents)
    assert result["data"]["result"]["remaining_paths"] == [
        late.relative_to(root).as_posix(),
        *(path.relative_to(root).as_posix() for path in documents),
        child.parent.relative_to(root).as_posix(),
    ]
    assert result["effects"][-5:] == [
        {"kind": "scope.delete", "status": "not_attempted", "target": late.relative_to(root).as_posix()},
        *(
            {"kind": "scope.delete", "status": "not_attempted", "target": path.relative_to(root).as_posix()}
            for path in documents
        ),
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_subtree_removal_preserves_a_file_changed_after_backup_and_before_its_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    document = child.parent / "later.txt"
    document.write_bytes(b"original document")
    backup = tmp_path / "delete-backup"
    real_unlink = os.unlink
    injected = False

    def unlink(path: str, **kwargs: int) -> None:
        nonlocal injected
        real_unlink(path, **kwargs)
        if path == ".meta.json" and not injected:
            injected = True
            document.write_bytes(b"actor replacement that must be preserved")

    monkeypatch.setattr(os, "unlink", unlink)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert injected and document.read_bytes() == b"actor replacement that must be preserved"
    assert (backup / document.relative_to(root)).read_bytes() == b"original document"
    assert result["data"]["result"]["removed_ids"] == []
    assert result["data"]["result"]["changed_paths"] == [
        child.relative_to(root).as_posix(),
        (child.parent / "design.md").relative_to(root).as_posix(),
    ]
    untouched = [child.parent / filename for filename in ("plan.md", "report.md", "requirement.md")]
    assert all(path.read_bytes() == (backup / path.relative_to(root)).read_bytes() for path in untouched)
    assert result["data"]["result"]["remaining_paths"] == [
        document.relative_to(root).as_posix(),
        *(path.relative_to(root).as_posix() for path in untouched),
        child.parent.relative_to(root).as_posix(),
    ]
    assert result["effects"][-5:] == [
        {"kind": "scope.delete", "status": "not_attempted", "target": document.relative_to(root).as_posix()},
        *(
            {"kind": "scope.delete", "status": "not_attempted", "target": path.relative_to(root).as_posix()}
            for path in untouched
        ),
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_redirected_backup_root_never_writes_through_the_external_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "preserve.bin"
    marker.write_bytes(b"external bytes")
    real_mkdir = os.mkdir
    redirected = False

    def mkdir(path: str, mode: int = 0o777, **kwargs: int) -> None:
        nonlocal redirected
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not redirected:
            redirected = True
            backup.rename(tmp_path / "moved-backup")
            backup.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert redirected and child.read_bytes() == before and backup.is_symlink()
    assert marker.read_bytes() == b"external bytes" and sorted(path.name for path in outside.iterdir()) == [
        "preserve.bin"
    ]
    assert result["effects"] == [
        {"kind": "backup", "status": "unknown", "target": str(backup)},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]


def test_uncertain_backup_directory_creation_keeps_the_directory_and_does_not_delete_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    real_mkdir = os.mkdir
    injected = False

    def mkdir(path: str, mode: int = 0o777, **kwargs: int) -> None:
        nonlocal injected
        real_mkdir(path, mode, **kwargs)
        if path == backup.name and not injected:
            injected = True
            raise OSError("fixture: mkdir outcome unavailable")

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert injected and backup.is_dir() and child.read_bytes() == before
    assert result["effects"] == [
        {"kind": "backup", "status": "unknown", "target": str(backup)},
        {"kind": "scope.delete", "status": "not_attempted", "target": child.parent.relative_to(root).as_posix()},
    ]
    assert result["data"]["result"]["changed_paths"] == [] and result["data"]["result"]["removed_ids"] == []


def test_backup_root_redirected_after_open_never_writes_to_the_external_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _parent, child = dependency_workspace(tmp_path)
    before = child.read_bytes()
    backup = tmp_path / "delete-backup"
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "preserve.bin"
    marker.write_bytes(b"external bytes")
    real_close = os.close
    redirected = False

    def close(descriptor: int) -> None:
        nonlocal redirected
        opened = os.fstat(descriptor)
        candidate = backup.lstat() if backup.exists() else None
        should_redirect = (
            not redirected
            and candidate is not None
            and (opened.st_dev, opened.st_ino) == (candidate.st_dev, candidate.st_ino)
        )
        real_close(descriptor)
        if should_redirect:
            redirected = True
            backup.rename(tmp_path / "moved-backup")
            backup.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(os, "close", close)
    assert (
        main(["--project", str(root), "scope", "delete", "iss-00003", "--backup-dir", str(backup), "--yes", "--json"])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert redirected and child.read_bytes() == before and backup.is_symlink()
    assert marker.read_bytes() == b"external bytes" and sorted(path.name for path in outside.iterdir()) == [
        "preserve.bin"
    ]
    assert result["effects"][0] == {"kind": "backup", "status": "unknown", "target": str(backup)}
