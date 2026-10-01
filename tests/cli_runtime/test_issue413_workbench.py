"""Workbench copy uses native same-clone inventory and per-file publication."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_dependency import dependency_workspace


def workbench_workspace(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    root, _parent, child = dependency_workspace(tmp_path)
    subprocess.run(["git", "-C", str(root), "add", "--", "spec-dock"], check=True, capture_output=True)
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
            "Scope fixture",
        ],
        check=True,
        capture_output=True,
    )
    other = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "parallel", str(other)], check=True, capture_output=True
    )
    source = child.parent / ".workbench"
    destination = other / child.parent.relative_to(root) / ".workbench"
    source.mkdir()
    return root, other, source, destination


@pytest.mark.skipif(os.name != "posix", reason="native POSIX file mode")
@pytest.mark.parametrize("policy", ["error", "overwrite"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_same_bytes_with_different_file_modes_follow_the_explicit_conflict_policy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], policy: str, dry_run: bool
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    destination.mkdir()
    source_file, target_file = source / "script.sh", destination / "script.sh"
    source_file.write_bytes(b"#!/bin/sh\nexit 0\n")
    target_file.write_bytes(b"#!/bin/sh\nexit 0\n")
    source_file.chmod(0o700)
    target_file.chmod(0o600)
    flags = ["--yes", "--dry-run"] if dry_run else ["--yes"]
    assert main([
        "--project",
        str(root),
        "workbench",
        "copy",
        "--scope",
        "iss-00003",
        "--to-worktree",
        str(other),
        "--on-conflict",
        policy,
        *flags,
        "--json",
    ]) == (3 if policy == "error" else 0)
    result = json.loads(capsys.readouterr().out)
    assert source_file.read_bytes() == target_file.read_bytes() == b"#!/bin/sh\nexit 0\n"
    assert stat.S_IMODE(source_file.stat().st_mode) == 0o700
    if policy == "error":
        assert result["effects"] == [] and stat.S_IMODE(target_file.stat().st_mode) == 0o600
    elif dry_run:
        assert result["status"] == "planned" and stat.S_IMODE(target_file.stat().st_mode) == 0o600
        assert result["data"]["result"]["remaining_paths"] == ["script.sh"]
    else:
        assert result["status"] == "succeeded" and stat.S_IMODE(target_file.stat().st_mode) == 0o700
        assert result["data"]["result"]["copied_paths"] == ["script.sh"]


def test_copy_publishes_scope_file_to_native_linked_worktree_without_control(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"opaque evidence\x00\xff")
    metadata = {path: path.read_bytes() for tree in (root, other) for path in tree.glob("spec-dock/**/.meta.json")}
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"] == {
        "kind": "workbench",
        "result": {
            "scope_id": "iss-00003",
            "source_path": str(source),
            "destination_path": str(destination),
            "copied_paths": ["note.txt"],
            "remaining_paths": [],
        },
    }
    assert (destination / "note.txt").read_bytes() == b"opaque evidence\x00\xff"
    assert (source / "note.txt").read_bytes() == b"opaque evidence\x00\xff"
    assert all(path.read_bytes() == exact for path, exact in metadata.items())
    assert not (root / ".git/spec-dock").exists()
    assert not (other / "spec-dock/.agent").exists()


def test_copy_matches_existing_scope_by_normalized_github_linkage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"existing evidence")
    target_metadata = destination.parent / ".meta.json"
    payload = json.loads(target_metadata.read_bytes())
    payload["github"]["repo_owner"] = payload["github"]["repo_owner"].upper()
    payload["github"]["repo_name"] = payload["github"]["repo_name"].upper()
    target_metadata.write_text(json.dumps(payload))
    exact = target_metadata.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["note.txt"]
    assert (destination / "note.txt").read_bytes() == b"existing evidence"
    assert target_metadata.read_bytes() == exact


def test_copy_dynamic_scope_and_guards_use_the_existing_direct_selection_without_changing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"existing evidence")
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    arguments = [
        "--project",
        str(root),
        "workbench",
        "copy",
        "--scope",
        "@issue",
        "--to-worktree",
        str(other),
        "--expect-current",
        "@current",
        "--json",
    ]
    assert main([*arguments, "--expect-backend", "local"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == [] and not destination.exists()
    assert main([*arguments, "--expect-backend", "github"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope_id"] == "iss-00003"
    assert (destination / "note.txt").read_bytes() == b"existing evidence"
    assert record.read_bytes() == before
    assert not (other / "spec-dock/.agent").exists()


def test_copy_does_not_require_an_unrelated_prunable_worktree_to_exist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"existing evidence")
    obsolete = tmp_path / "obsolete"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "obsolete", str(obsolete)], check=True, capture_output=True
    )
    shutil.rmtree(obsolete)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["note.txt"]
    assert (destination / "note.txt").read_bytes() == b"existing evidence"
    assert not obsolete.exists()


def test_copy_preserves_a_concurrently_replaced_stage_and_never_publishes_its_foreign_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"source evidence")
    destination.mkdir()
    (destination / "note.txt").write_bytes(b"old destination evidence")
    real_fsync = os.fsync
    changed = False
    stage = None

    def fsync(descriptor: int) -> None:
        nonlocal changed, stage
        candidates = list(destination.glob(".copy-*.tmp"))
        if candidates and not changed:
            changed = True
            stage = candidates[0]
            stage.rename(destination / "held-original.tmp")
            stage.write_bytes(b"actor evidence")
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and not any(effect["status"] in {"succeeded", "unknown"} for effect in result["effects"])
    assert result["data"]["result"]["copied_paths"] == []
    assert (destination / "note.txt").read_bytes() == b"old destination evidence"
    assert stage is not None and stage.read_bytes() == b"actor evidence"
    assert (destination / "held-original.tmp").read_bytes() == b"source evidence"


def test_overwrite_replaces_complete_file_and_preserves_destination_only_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"new complete bytes")
    (source / "new.txt").write_bytes(b"new evidence")
    destination.mkdir()
    (destination / "note.txt").write_bytes(b"old complete bytes")
    (destination / "destination-only.txt").write_bytes(b"must stay")
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["new.txt", "note.txt"]
    assert result["data"]["result"]["remaining_paths"] == []
    assert (destination / "note.txt").read_bytes() == b"new complete bytes"
    assert (destination / "new.txt").read_bytes() == b"new evidence"
    assert (destination / "destination-only.txt").read_bytes() == b"must stay"


def test_copy_merges_nested_and_empty_directories_without_removing_existing_children(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "nested").mkdir()
    (source / "nested/note.bin").write_bytes(b"nested evidence")
    (source / "empty").mkdir()
    (destination / "nested").mkdir(parents=True)
    (destination / "nested/keep.txt").write_bytes(b"destination only")
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["empty", "nested/note.bin"]
    assert (destination / "empty").is_dir()
    assert (destination / "nested/note.bin").read_bytes() == b"nested evidence"
    assert (destination / "nested/keep.txt").read_bytes() == b"destination only"


@pytest.mark.skipif(os.name != "posix", reason="native POSIX mode preservation")
def test_copy_preserves_source_file_mode_without_changing_source_or_existing_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "script.sh").write_bytes(b"#!/bin/sh\nexit 0\n")
    (source / "script.sh").chmod(0o764)
    destination.mkdir()
    (destination / "keep.txt").write_bytes(b"destination evidence")
    (destination / "keep.txt").chmod(0o640)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    assert stat.S_IMODE((destination / "script.sh").stat().st_mode) == 0o764
    assert stat.S_IMODE((source / "script.sh").stat().st_mode) == 0o764
    assert stat.S_IMODE((destination / "keep.txt").stat().st_mode) == 0o640


@pytest.mark.skipif(os.name != "posix", reason="native symbolic links")
def test_copy_preserves_relative_link_text_without_following_external_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"plain evidence")
    (source / "link").symlink_to("note.txt")
    (source / "outside").symlink_to("../../../../../../private.bin")
    private = tmp_path / "private.bin"
    private.write_bytes(b"outside evidence must remain private")
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr().out
    assert (destination / "link").readlink() == Path("note.txt")
    assert (destination / "outside").readlink() == Path("../../../../../../private.bin")
    assert private.read_bytes() == b"outside evidence must remain private"
    assert "outside evidence must remain private" not in output


@pytest.mark.skipif(os.name != "posix", reason="native symbolic links")
@pytest.mark.parametrize("source_link", [False, True])
def test_overwrite_can_replace_regular_file_and_link_without_following_either_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], source_link: bool
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    destination.mkdir()
    external = tmp_path / "external.bin"
    external.write_bytes(b"external bytes")
    if source_link:
        (source / "entry").symlink_to("missing-relative-target")
        (destination / "entry").write_bytes(b"old regular bytes")
    else:
        (source / "entry").write_bytes(b"new regular bytes")
        (destination / "entry").symlink_to(str(external))
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["entry"]
    assert external.read_bytes() == b"external bytes"
    if source_link:
        assert (destination / "entry").readlink() == Path("missing-relative-target")
    else:
        assert not (destination / "entry").is_symlink()
        assert (destination / "entry").read_bytes() == b"new regular bytes"


def test_unknown_nested_directory_creation_reports_partial_and_remaining_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    destination.mkdir()
    (source / "nested").mkdir()
    (source / "nested/note.txt").write_bytes(b"evidence")
    original_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        original_mkdir(path, mode, dir_fd=dir_fd)
        if path == "nested" and dir_fd is not None:
            raise OSError("directory reply was lost")

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["data"]["result"]["copied_paths"] == []
    assert result["data"]["result"]["remaining_paths"] == ["nested", "nested/note.txt"]
    assert result["effects"] == [
        {"kind": "workbench-directory", "status": "unknown", "target": str(destination / "nested")},
        {"kind": "workbench-file", "status": "not_attempted", "target": str(destination / "nested/note.txt")},
    ]
    assert (destination / "nested").is_dir() and not (destination / "nested/note.txt").exists()


def test_empty_source_workbench_creates_an_empty_destination_without_a_registry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, _source, destination = workbench_workspace(tmp_path)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert destination.is_dir() and list(destination.iterdir()) == []
    assert result["status"] == "succeeded"
    assert result["data"]["result"]["copied_paths"] == result["data"]["result"]["remaining_paths"] == []
    assert result["effects"] == [{"kind": "workbench-directory", "status": "succeeded", "target": str(destination)}]


@pytest.mark.parametrize("reference", ["linked", "wt:legacy-id", "../linked"])
def test_copy_rejects_non_absolute_worktree_references_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], reference: str
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            reference,
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and list(tmp_path.iterdir()) == []


@pytest.mark.skipif(os.name != "posix", reason="native POSIX file mode")
def test_overwrite_preserves_source_mode_even_when_existing_bytes_match(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "script").write_bytes(b"same bytes")
    (source / "script").chmod(0o755)
    destination.mkdir()
    (destination / "script").write_bytes(b"same bytes")
    (destination / "script").chmod(0o600)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["script"]
    assert stat.S_IMODE((destination / "script").stat().st_mode) == 0o755


@pytest.mark.skipif(os.name != "posix", reason="native symbolic link directory race")
@pytest.mark.parametrize("nested", [False, True])
def test_directory_creation_conflict_preserves_actor_path_and_reports_no_unknown_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], nested: bool
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    if nested:
        (source / "nested").mkdir()
        (source / "nested/note.txt").write_bytes(b"source")
        destination.mkdir()
    else:
        (source / "note.txt").write_bytes(b"source")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "note.txt").write_bytes(b"external bytes")
    name = "nested" if nested else ".workbench"
    original_mkdir = os.mkdir

    def mkdir(path, mode=0o777, *, dir_fd=None):
        if path == name and dir_fd is not None:
            os.symlink(str(outside), path, dir_fd=dir_fd)
            raise FileExistsError("actor already owns the directory name")
        original_mkdir(path, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["data"]["result"]["copied_paths"] == []
    assert not any(effect["status"] in {"unknown", "succeeded"} for effect in result["effects"])
    assert (outside / "note.txt").read_bytes() == b"external bytes"
    assert (destination / "nested" if nested else destination).is_symlink()


def test_default_conflict_preflights_every_file_before_creating_any_destination_entry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "a-new.txt").write_bytes(b"new")
    (source / "z-conflict.txt").write_bytes(b"source")
    destination.mkdir()
    (destination / "z-conflict.txt").write_bytes(b"destination")
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not (destination / "a-new.txt").exists()
    assert (destination / "z-conflict.txt").read_bytes() == b"destination"


def test_overwrite_requires_confirmation_and_dry_run_leaves_missing_destination_absent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"evidence")
    arguments = [
        "--project",
        str(root),
        "workbench",
        "copy",
        "--scope",
        "iss-00003",
        "--to-worktree",
        str(other),
        "--on-conflict",
        "overwrite",
        "--json",
    ]
    assert main(arguments) == 3
    denied = json.loads(capsys.readouterr().out)
    assert denied["error"]["code"] == "CONFIRMATION_REQUIRED" and denied["effects"] == []
    assert not destination.exists()
    assert main([*arguments, "--dry-run"]) == 0
    planned = json.loads(capsys.readouterr().out)
    assert planned["status"] == "planned" and planned["data"]["result"]["can_apply"] is True
    assert planned["data"]["result"]["copied_paths"] == []
    assert planned["data"]["result"]["remaining_paths"] == ["note.txt"]
    assert not destination.exists() and list(source.iterdir()) == [source / "note.txt"]


@pytest.mark.skipif(os.name != "posix", reason="native terminal confirmation")
@pytest.mark.parametrize("answer", [b"yes\n", b"no\n"])
def test_overwrite_terminal_confirmation_displays_changed_paths_and_respects_the_answer(
    tmp_path: Path, answer: bytes
) -> None:
    import pty

    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"source bytes")
    destination.mkdir()
    (destination / "note.txt").write_bytes(b"destination bytes")
    master, slave = pty.openpty()
    process = None
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "spec_dock.cli",
                "--project",
                str(root),
                "workbench",
                "copy",
                "--scope",
                "iss-00003",
                "--to-worktree",
                str(other),
                "--on-conflict",
                "overwrite",
            ],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        )
        os.write(master, answer)
        stdout, stderr = process.communicate(timeout=8)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate()
        os.close(master)
        os.close(slave)
    assert b"note.txt" in stderr and b"Continue? [y/N]" in stderr
    assert process.returncode == (0 if answer == b"yes\n" else 3), stdout + stderr
    assert (destination / "note.txt").read_bytes() == (b"source bytes" if answer == b"yes\n" else b"destination bytes")
    assert (source / "note.txt").read_bytes() == b"source bytes"


@pytest.mark.parametrize("target_kind", ["same", "clone", "wrong-scope"])
def test_copy_refuses_other_clone_self_or_scope_identity_mismatch_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], target_kind: str
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"evidence")
    target = other
    if target_kind == "same":
        target = root
    elif target_kind == "clone":
        target = tmp_path / "independent-clone"
        subprocess.run(["git", "clone", "-q", str(root), str(target)], check=True, capture_output=True)
    else:
        metadata = destination.parent / ".meta.json"
        payload = json.loads(metadata.read_bytes())
        payload["github"]["repo_name"] = "different-repository"
        metadata.write_text(json.dumps(payload))
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(target),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and not destination.exists()
    assert (source / "note.txt").read_bytes() == b"evidence"


@pytest.mark.skipif(os.name != "posix", reason="native symbolic links")
@pytest.mark.parametrize("unsafe", ["source-root", "destination-root", "absolute-link", "fifo"])
def test_copy_rejects_unsafe_source_or_destination_without_following_external_content(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], unsafe: str
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"evidence")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "note.txt").write_bytes(b"external private bytes")
    if unsafe == "source-root":
        source.rename(source.parent / "moved-source")
        source.symlink_to(outside, target_is_directory=True)
    elif unsafe == "destination-root":
        destination.symlink_to(outside, target_is_directory=True)
    elif unsafe == "absolute-link":
        (source / "link").symlink_to(outside / "note.txt")
    else:
        os.mkfifo(source / "pipe")
    expected_exit = 5 if unsafe in {"source-root", "destination-root"} else 3
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == expected_exit
    )
    output = capsys.readouterr().out
    assert json.loads(output)["effects"] == [] and "external private bytes" not in output
    assert (outside / "note.txt").read_bytes() == b"external private bytes"


def test_unknown_second_file_publication_keeps_applied_and_unattempted_files_separate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    destination.mkdir()
    for name in ("a.txt", "b.txt", "c.txt"):
        (source / name).write_bytes(name.encode())
    original_link = os.link

    def link(src, dst, **kwargs):
        original_link(src, dst, **kwargs)
        if dst == "b.txt":
            raise OSError("file publication reply was lost")

    monkeypatch.setattr(os, "link", link)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["copied_paths"] == ["a.txt"]
    assert result["data"]["result"]["remaining_paths"] == ["b.txt", "c.txt"]
    assert result["effects"] == [
        {"kind": "workbench-file", "status": "succeeded", "target": str(destination / "a.txt")},
        {"kind": "workbench-file", "status": "unknown", "target": str(destination / "b.txt")},
        {"kind": "workbench-file", "status": "not_attempted", "target": str(destination / "c.txt")},
    ]
    assert (destination / "a.txt").read_bytes() == b"a.txt"
    assert (destination / "b.txt").read_bytes() == b"b.txt" and not (destination / "c.txt").exists()
    assert len(list(destination.glob(".copy-*.tmp"))) == 1
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False


def test_source_change_during_staging_preserves_original_destination_and_actor_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"new source")
    destination.mkdir()
    (destination / "note.txt").write_bytes(b"old destination")
    original_fsync = os.fsync
    changed = False

    def fsync(descriptor):
        nonlocal changed
        if stat.S_ISREG(os.fstat(descriptor).st_mode) and not changed:
            changed = True
            (source / "note.txt").write_bytes(b"actor source change")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fsync)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert changed and result["data"]["result"]["copied_paths"] == []
    assert (source / "note.txt").read_bytes() == b"actor source change"
    assert (destination / "note.txt").read_bytes() == b"old destination"
    assert list(destination.iterdir()) == [destination / "note.txt"]


def test_unknown_atomic_overwrite_keeps_old_file_until_replacement_and_preserves_new_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"new complete bytes")
    destination.mkdir()
    (destination / "note.txt").write_bytes(b"old complete bytes")
    original_replace = os.replace
    observed: list[bytes] = []

    def replace(src, dst, **kwargs):
        if dst == "note.txt":
            observed.append((destination / "note.txt").read_bytes())
            original_replace(src, dst, **kwargs)
            raise OSError("replacement reply was lost")
        original_replace(src, dst, **kwargs)

    monkeypatch.setattr(os, "replace", replace)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--on-conflict",
            "overwrite",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert observed == [b"old complete bytes"] and (destination / "note.txt").read_bytes() == b"new complete bytes"
    assert result["data"]["result"]["copied_paths"] == []
    assert result["data"]["result"]["remaining_paths"] == ["note.txt"]
    assert result["effects"] == [
        {"kind": "workbench-file", "status": "unknown", "target": str(destination / "note.txt")}
    ]


@pytest.mark.skipif(os.name != "posix", reason="native POSIX flock in another process")
def test_workbench_copy_completes_while_another_process_holds_start_exclusion(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"parallel evidence")
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import fcntl,os,sys; fd=os.open(sys.argv[1],os.O_RDONLY); "
            "fcntl.flock(fd,fcntl.LOCK_EX); print('ready',flush=True); sys.stdin.readline(); os.close(fd)",
            str(root / ".git"),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None and holder.stdout.readline() == "ready\n"
        code = main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        result = json.loads(capsys.readouterr().out)
    finally:
        holder.communicate("\n", timeout=10)
    assert holder.returncode == 0 and code == 0 and result["status"] == "succeeded"
    assert (destination / "note.txt").read_bytes() == b"parallel evidence"


def test_git_failure_after_confirmed_copy_keeps_applied_file_and_original_native_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"evidence")
    destination.mkdir()
    binary = tmp_path / "broken-bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text("#!/bin/sh\nprintf 'native Git failed\\nsecond error line\\n' >&2\nexit 27\n")
    git.chmod(0o700)
    original_link = os.link

    def link(src, dst, **kwargs):
        original_link(src, dst, **kwargs)
        if dst == "note.txt":
            monkeypatch.setenv("PATH", str(binary))

    monkeypatch.setattr(os, "link", link)
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == "" and result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 27
    assert result["error"]["details"]["git"]["stderr"] == "native Git failed\nsecond error line\n"
    assert result["data"]["result"]["copied_paths"] == ["note.txt"]
    assert result["data"]["result"]["remaining_paths"] == []
    assert result["effects"] == [
        {"kind": "workbench-file", "status": "succeeded", "target": str(destination / "note.txt")}
    ]
    assert (destination / "note.txt").read_bytes() == b"evidence"


def test_dry_run_reports_root_and_nested_directory_creation_without_writing_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "nested").mkdir()
    (source / "nested/note.txt").write_bytes(b"evidence")
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [
        {"kind": "workbench-directory", "status": "planned", "target": str(destination)},
        {"kind": "workbench-directory", "status": "planned", "target": str(destination / "nested")},
        {"kind": "workbench-file", "status": "planned", "target": str(destination / "nested/note.txt")},
    ]
    assert not destination.exists() and list((source / "nested").iterdir()) == [source / "nested/note.txt"]


def test_workbench_help_describes_absolute_same_clone_paths_and_per_file_results(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["workbench", "copy", "--help"]) == 0
    help_text = capsys.readouterr().out
    assert "copied_paths" in help_text and "remaining_paths" in help_text
    assert "/absolute/worktree" in help_text and "same Git clone" in help_text
    assert "--resume" not in help_text and "--rollback" not in help_text


@pytest.mark.parametrize("option", ["--resume", "--rollback"])
def test_workbench_rejects_retired_operation_ids_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], option: str
) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(tmp_path / "linked"),
            option,
            "a" * 32,
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def _refuse_external_metadata_open(monkeypatch: pytest.MonkeyPatch, files: list[Path]) -> None:
    identities = {(path.stat().st_dev, path.stat().st_ino) for path in files}
    native_open = os.open

    def open_file(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        descriptor = native_open(path, flags, mode, dir_fd=dir_fd)
        observed = os.fstat(descriptor)
        if (observed.st_dev, observed.st_ino) in identities:
            os.close(descriptor)
            raise AssertionError("external metadata must not be opened")
        return descriptor

    monkeypatch.setattr(os, "open", open_file)


@pytest.mark.parametrize("backend", ["github", "local"])
def test_copy_resolves_existing_scope_ids_independently_of_each_worktrees_slug(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], backend: str
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    scope_id = "iss-00003"
    if backend == "local":
        scope_id = "iss-local-00003"
        remapped = []
        for owner in (source.parent, destination.parent):
            metadata = owner / ".meta.json"
            payload = json.loads(metadata.read_bytes())
            payload.update(
                id=scope_id,
                backend="local",
                github=None,
                lifecycle={"state": "open", "revision": 0, "updated_at": "2026-09-30T00:00:00Z"},
            )
            metadata.write_text(json.dumps(payload))
            moved = owner.with_name(scope_id + "-fixture")
            owner.rename(moved)
            remapped.append(moved / ".workbench")
        source, destination = remapped
    target_owner = destination.parent
    target_metadata = target_owner / ".meta.json"
    payload = json.loads(target_metadata.read_bytes())
    payload["slug"] = "different-slug"
    target_metadata.write_text(json.dumps(payload))
    moved = target_owner.with_name(scope_id + "-different-slug")
    target_owner.rename(moved)
    destination = moved / ".workbench"
    (source / "note.bin").write_bytes(b"opaque source evidence\x00\xff")
    metadata_bytes = {
        path: path.read_bytes() for tree in (root, other) for path in tree.glob("spec-dock/**/.meta.json")
    }
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "  " + scope_id.upper() + "  ",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["scope_id"] == scope_id
    assert result["data"]["result"]["source_path"] == str(source)
    assert result["data"]["result"]["destination_path"] == str(destination)
    assert result["data"]["result"]["copied_paths"] == ["note.bin"]
    assert (
        (destination / "note.bin").read_bytes()
        == (source / "note.bin").read_bytes()
        == b"opaque source evidence\x00\xff"
    )
    assert all(path.read_bytes() == exact for path, exact in metadata_bytes.items())
    assert output.err == "" and not (root / ".git/spec-dock").exists()
    assert not (root / "spec-dock/.agent").exists() and not (other / "spec-dock/.agent").exists()


@pytest.mark.parametrize("side", ["source", "destination"])
@pytest.mark.parametrize("defect", ["missing", "malformed", "duplicate"])
def test_copy_rejects_invalid_scope_inventory_before_copying_any_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], side: str, defect: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"source evidence")
    destination.mkdir()
    (destination / "keep.txt").write_bytes(b"destination evidence")
    owner = source.parent if side == "source" else destination.parent
    metadata = owner / ".meta.json"
    if defect == "missing":
        metadata.unlink()
    elif defect == "malformed":
        metadata.write_bytes(b"invalid metadata")
    else:
        duplicate = owner.with_name("iss-00003-another-copy")
        shutil.copytree(owner, duplicate)
        payload = json.loads((duplicate / ".meta.json").read_bytes())
        payload["slug"] = "another-copy"
        (duplicate / ".meta.json").write_text(json.dumps(payload))
    before = (tree_digest(root), tree_digest(other))
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 3
    )
    output = capsys.readouterr()
    assert json.loads(output.out)["effects"] == [] and output.err == ""
    assert before == (tree_digest(root), tree_digest(other))
    assert list(destination.iterdir()) == [destination / "keep.txt"]


@pytest.mark.parametrize("existing_destination", [False, True])
def test_copy_missing_source_workbench_preserves_the_entire_destination(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], existing_destination: bool
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, other, source, destination = workbench_workspace(tmp_path)
    source.rmdir()
    if existing_destination:
        destination.mkdir()
        (destination / "keep.txt").write_bytes(b"destination evidence")
    before = (tree_digest(root), tree_digest(other))
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 4
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "failed" and result["effects"] == [] and output.err == ""
    assert before == (tree_digest(root), tree_digest(other))


@pytest.mark.parametrize("side", ["source", "destination"])
@pytest.mark.parametrize("level", ["initiative", "epic", "issue"])
def test_copy_rejects_redirected_scope_ancestors_before_opening_external_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], side: str, level: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"opaque source evidence")
    owner = source.parent if side == "source" else destination.parent
    redirected = {"issue": owner, "epic": owner.parent.parent, "initiative": owner.parent.parent.parent.parent}[level]
    outside = tmp_path / "outside"
    redirected.rename(outside)
    redirected.symlink_to(outside, target_is_directory=True)
    external_metadata = list(outside.rglob(".meta.json"))
    assert external_metadata
    before = (tree_digest(root), tree_digest(other), tree_digest(outside))
    with monkeypatch.context() as observed:
        _refuse_external_metadata_open(observed, external_metadata)
        assert (
            main([
                "--project",
                str(root),
                "workbench",
                "copy",
                "--scope",
                "iss-00003",
                "--to-worktree",
                str(other),
                "--json",
            ])
            == 3
        )
    output = capsys.readouterr()
    assert json.loads(output.out)["effects"] == [] and output.err == ""
    assert before == (tree_digest(root), tree_digest(other), tree_digest(outside))


@pytest.mark.parametrize("placement", ["initiatives-root", "unexpected-directory"])
def test_copy_ignores_unrelated_metadata_links_without_opening_their_external_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], placement: str
) -> None:
    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"source evidence")
    outside = tmp_path / "outside-meta.json"
    private = b"external private metadata must remain unread"
    outside.write_bytes(private)
    container = root / "spec-dock/initiatives"
    if placement == "unexpected-directory":
        container = container / "unexpected-directory"
        container.mkdir()
    redirect = container / ".meta.json"
    redirect.symlink_to(outside)
    with monkeypatch.context() as observed:
        _refuse_external_metadata_open(observed, [outside])
        assert (
            main([
                "--project",
                str(root),
                "workbench",
                "copy",
                "--scope",
                "iss-00003",
                "--to-worktree",
                str(other),
                "--json",
            ])
            == 0
        )
    output = capsys.readouterr()
    assert (destination / "note.txt").read_bytes() == b"source evidence"
    assert outside.read_bytes() == private and redirect.readlink() == outside
    assert private.decode() not in output.out + output.err
    assert not (root / ".git/spec-dock").exists() and not (other / "spec-dock/.agent").exists()


@pytest.mark.parametrize("side", ["source", "destination"])
def test_copy_rejects_file_instead_of_a_workbench_directory_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], side: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, other, source, destination = workbench_workspace(tmp_path)
    (source / "note.txt").write_bytes(b"source evidence")
    if side == "source":
        (source / "note.txt").unlink()
        source.rmdir()
        source.write_bytes(b"invalid source root")
    else:
        destination.write_bytes(b"invalid destination root")
    before = (tree_digest(root), tree_digest(other))
    assert (
        main([
            "--project",
            str(root),
            "workbench",
            "copy",
            "--scope",
            "iss-00003",
            "--to-worktree",
            str(other),
            "--json",
        ])
        == 5
    )
    output = capsys.readouterr()
    assert json.loads(output.out)["effects"] == [] and output.err == ""
    assert before == (tree_digest(root), tree_digest(other))
