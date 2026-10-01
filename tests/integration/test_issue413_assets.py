"""Installation manages only one explicit worktree's static package resources."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

import pytest

from spec_dock import __version__
from spec_dock.cli import main
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.tree_backup import tree_digest


def uninitialized_worktree(root: Path) -> Path:
    root.mkdir()
    run_git(root, "init", "-q", "--initial-branch=main", mutation=True)
    (root / "readme.md").write_text("existing project work\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("dry_run", [False, True])
def test_init_places_only_static_assets_and_a_new_declaration_in_the_explicit_worktree(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, dry_run: bool
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    before = tree_digest(target)
    git_before = tree_digest(target / ".git")

    def unexpected(*_args: object, **_kwargs: object) -> None:
        pytest.fail("static init must not contact GitHub or acquire a Start lock")

    monkeypatch.setattr("spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", unexpected)
    monkeypatch.setattr("spec_dock.runtime.infra.start_lock.StartLock.__enter__", unexpected)
    flags = ["--dry-run"] if dry_run else ["--yes"]
    assert main(["installation", "init", str(target), *flags, "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert result["data"]["kind"] == "installation" and data["target"] == str(target)
    assert data["package_version"] == __version__ and data["backup_path"] is None
    assert data["changed_paths"] == [] and data["retired_paths"] == []
    assert not (target / ".git/spec-dock").exists() and tree_digest(target / ".git") == git_before
    assert not (target / "spec-dock/scripts/spec_dock_runtime").exists()

    assert not (target / "spec-dock/.agent").exists()
    assert (target / "readme.md").read_text() == "existing project work\n" and not tuple(outside.iterdir())
    if dry_run:
        assert result["status"] == "planned" and data["can_apply"] is True
        assert data["created_paths"] == [] and tree_digest(target) == before
        assert all(effect["status"] == "planned" for effect in result["effects"])
    else:
        declaration = json.loads((target / "spec-dock/workspace.json").read_bytes())
        assert declaration == {"schema_version": 3, "writer_protocol": "specdock.worktree-writer/v1"}
        assert (target / "spec-dock/templates/issue/requirement.md").is_file()
        assert (target / "spec-dock/scripts/spec-dock").is_file()
        assert (target / ".agents/skills/spec-dock/SKILL.md").is_file()
        assert (target / ".agents/skills/spec-dock-grill-with-docs/SKILL.md").is_file()
        assert "spec-dock/workspace.json" in data["created_paths"]
        assert main(["--project", str(target), "workspace", "validate", "--json"]) == 0
        capsys.readouterr()


@pytest.mark.parametrize(
    "conflict", ["spec-dock/workspace.json", "spec-dock/docs/README.md", ".agents/skills/spec-dock/SKILL.md"]
)
def test_init_refuses_any_existing_destination_without_publishing_other_assets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], conflict: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    existing = target / conflict
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"private user-owned contents")
    before = tree_digest(target)
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "PRECONDITION_FAILED"
    assert "exists" in result["error"]["message"] and conflict in result["error"]["message"]
    assert result["effects"] == [] and tree_digest(target) == before
    assert "private user-owned contents" not in output.out + output.err


def test_installation_show_does_not_require_a_workspace_or_control_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    before = tree_digest(target)
    assert main(["installation", "show", "--target", str(target), "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert result["data"]["kind"] == "installation" and data["target"] == str(target)
    assert data["package_version"] == __version__ and data["backup_path"] is None
    assert data["created_paths"] == [] and data["changed_paths"] == [] and data["retired_paths"] == []
    assert result["effects"] == [] and tree_digest(target) == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory-descriptor publication fixtures")
@pytest.mark.parametrize("after_publication", [False, True])
def test_init_reports_partial_publication_and_each_unattempted_asset_without_rollback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, after_publication: bool
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    git_before = tree_digest(target / ".git")
    original = os.link
    attempted: list[str] = []

    def fail_link(
        source: str,
        destination: str,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
        follow_symlinks: bool = True,
    ) -> None:
        attempted.append(destination)
        if after_publication:
            original(source, destination, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd, follow_symlinks=follow_symlinks)
        raise OSError("native injected publication failure")

    monkeypatch.setattr(os, "link", fail_link)
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 6
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "partial" and not output.err
    assert any(
        effect["status"] == "succeeded" and effect["kind"] == "installation.directory" for effect in result["effects"]
    )
    assert any(
        effect["target"] == "spec-dock/workspace.json" and effect["status"] == "not_attempted"
        for effect in result["effects"]
    )
    assert any(
        effect["target"] == "spec-dock/scripts/spec-dock" and effect["status"] == "not_attempted"
        for effect in result["effects"]
    )
    assert len(attempted) == 1 and tree_digest(target / ".git") == git_before
    assert not (target / "spec-dock/workspace.json").exists()
    if after_publication:
        retained = tuple(target.rglob(".install-*.tmp"))
        assert len(retained) == 1
        assert any(
            effect["target"] == retained[0].relative_to(target).as_posix() and effect["status"] == "unknown"
            for effect in result["effects"]
        )


@pytest.mark.parametrize("leaf", ["show", "init", "update", "uninstall"])
def test_installation_read_and_initialization_help_describes_only_one_worktree(
    capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    assert main(["--project", "/missing", "installation", leaf, "--help"]) == 0
    output = capsys.readouterr().out
    assert "static" in output and "one" in output and "package" in output
    assert "registered worktrees" not in output and "readable installation control" not in output
    assert "journal IDs" not in output and "engine digest" not in output
    assert "--commit" not in output and "--resume" not in output and "--finalize" not in output


@pytest.mark.parametrize("flag", ["--resume", "--rollback"])
def test_init_rejects_retired_recovery_before_git_admission_or_asset_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, flag: str
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    assert main(["installation", "init", "/missing", flag, "a" * 32, "--yes", "--json"]) == 2
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert not output.err and not tuple(outside.iterdir())


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symlink, hardlink and FIFO fixtures")
@pytest.mark.parametrize("shape", ["parent-symlink", "dangling", "file-symlink", "hardlink", "fifo"])
def test_init_refuses_unsafe_or_existing_entries_without_following_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    outside = tmp_path / "private"
    outside.mkdir()
    private = outside / "private.md"
    private.write_text("private canary body\n", encoding="utf-8")
    if shape == "parent-symlink":
        (target / ".agents").symlink_to(outside, target_is_directory=True)
    else:
        destination = target / "spec-dock/docs/README.md"
        destination.parent.mkdir(parents=True)
        if shape == "file-symlink":
            destination.symlink_to(private)
        elif shape == "dangling":
            destination.symlink_to(outside / "absent")
        elif shape == "hardlink":
            os.link(private, destination)
        else:
            os.mkfifo(destination)
    excluded = frozenset({"spec-dock/docs/README.md"}) if shape == "fifo" else frozenset()
    before, outside_before = tree_digest(target, excluded_entries=excluded), tree_digest(outside)
    fifo_identity = destination.lstat().st_ino if shape == "fifo" else None
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and "private canary body" not in output.out + output.err
    assert tree_digest(target, excluded_entries=excluded) == before and tree_digest(outside) == outside_before
    if shape == "fifo":
        assert destination.is_fifo() and destination.lstat().st_ino == fifo_identity


@pytest.mark.parametrize(
    "guard", ["project-conflict", "subdirectory", "relative", "backend", "current", "confirmation"]
)
def test_init_applies_exact_target_and_expectation_guards_before_publication(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, guard: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    subdirectory = target / "nested"
    subdirectory.mkdir()
    other = uninitialized_worktree(tmp_path / "other")
    monkeypatch.chdir(target)
    arguments = ["installation", "init", str(target), "--json", "--yes"]
    if guard == "project-conflict":
        arguments += ["--project", str(other)]
    elif guard == "subdirectory":
        arguments[2] = str(subdirectory)
    elif guard == "relative":
        arguments[2] = "."
    elif guard == "backend":
        arguments += ["--expect-backend", "github"]
    elif guard == "current":
        arguments += ["--expect-current", "iss-00001"]
    else:
        arguments.remove("--yes")
    before, other_before = tree_digest(target), tree_digest(other)
    assert main(arguments) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and tree_digest(target) == before and tree_digest(other) == other_before


def test_init_in_a_linked_worktree_does_not_install_into_main_or_shared_git(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = uninitialized_worktree(tmp_path / "main")
    run_git(root, "add", "--", "readme.md", mutation=True)
    run_git(
        root,
        "-c",
        "user.name=fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-qm",
        "fixture",
        mutation=True,
    )
    linked = tmp_path / "linked"
    run_git(root, "worktree", "add", "-b", "linked", str(linked), mutation=True)
    main_before, git_before = tree_digest(root), tree_digest(root / ".git")
    assert main(["installation", "init", str(linked), "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["target"] == str(linked)
    assert (linked / "spec-dock/workspace.json").is_file() and not (root / "spec-dock").exists()
    assert tree_digest(root) == main_before and tree_digest(root / ".git") == git_before
    assert main(["installation", "show", "--target", str(linked), "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)["data"]["result"]
    assert (
        shown["workspace"]["schema_version"] == 3
        and shown["workspace"]["writer_protocol"] == "specdock.worktree-writer/v1"
    )
    assert all(asset["classification"] == "current" for asset in shown["assets"])
    missing = linked / "spec-dock/docs/README.md"
    missing.unlink()
    linked_before = tree_digest(linked)
    assert (
        main([
            "installation",
            "update",
            "--target",
            str(linked),
            "--backup-dir",
            str(root / "backup"),
            "--yes",
            "--json",
        ])
        == 3
    )
    refused = json.loads(capsys.readouterr().out)
    assert refused["effects"] == [] and tree_digest(linked) == linked_before and not (root / "backup").exists()
    assert (
        main([
            "installation",
            "update",
            "--target",
            str(linked),
            "--backup-dir",
            str(tmp_path / "update-backup"),
            "--yes",
            "--json",
        ])
        == 0
    )
    updated = json.loads(capsys.readouterr().out)
    assert updated["data"]["result"]["created_paths"] == ["spec-dock/docs/README.md"]
    assert missing.is_file() and tree_digest(root) == main_before and tree_digest(root / ".git") == git_before
    assert (
        main([
            "installation",
            "uninstall",
            "--target",
            str(linked),
            "--backup-dir",
            str(tmp_path / "uninstall-backup"),
            "--yes",
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    assert not missing.exists() and tree_digest(root) == main_before and tree_digest(root / ".git") == git_before


def test_init_reads_package_resources_from_a_traversable_archive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    package = Path(__file__).resolve().parents[2] / "src/spec_dock"
    archive_path = tmp_path / "resources.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in (package / "assets").rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, "spec_dock/" + path.relative_to(package).as_posix())
    target = uninitialized_worktree(tmp_path / "consumer")
    with zipfile.ZipFile(archive_path) as archive:
        monkeypatch.setattr(
            "spec_dock.runtime.infra.static_assets.files", lambda _package: zipfile.Path(archive, "spec_dock/")
        )
        assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    assert (target / "spec-dock/scripts/spec-dock").read_bytes() == (package / "shim_vnext.py").read_bytes()


@pytest.mark.parametrize("dry_run", [False, True])
def test_update_replaces_only_verified_old_static_bytes_after_an_external_backup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, dry_run: bool
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt").read_bytes()
    installed = target / "spec-dock/scripts/spec-dock"
    installed.write_bytes(old_bytes)
    protected = (
        "spec-dock/workspace.json",
        "spec-dock/initiatives/user-scope/.meta.json",
        "spec-dock/initiatives/user-scope/requirement.md",
        "spec-dock/artifacts/user-evidence.bin",
        "spec-dock/.workbench/notes.md",
        "spec-dock/.agent/work-target/user-selected.json",
        ".git/spec-dock/control/engine.json",
    )
    for relative in protected[1:]:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"private protected body\n")
    preserved = {relative: (target / relative).read_bytes() for relative in protected}
    before, git_before = tree_digest(target), tree_digest(target / ".git")
    backup = tmp_path / "backup"
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    flags = ["--dry-run"] if dry_run else ["--yes"]
    assert main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), *flags, "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert result["data"]["kind"] == "installation" and data["target"] == str(target)
    assert data["created_paths"] == [] and data["retired_paths"] == []
    assert "private protected body" not in output.out + output.err and not output.err
    assert all((target / relative).read_bytes() == payload for relative, payload in preserved.items())
    assert tree_digest(target / ".git") == git_before and not tuple(outside.iterdir())
    if dry_run:
        assert result["status"] == "planned" and data["can_apply"] is True
        assert data["changed_paths"] == [] and not backup.exists() and tree_digest(target) == before
        assert all(effect["status"] == "planned" for effect in result["effects"])
    else:
        assert result["status"] == "succeeded" and data["changed_paths"] == ["spec-dock/scripts/spec-dock"]
        assert data["backup_path"] == str(backup)
        assert (backup / "static/spec-dock/scripts/spec-dock").read_bytes() == old_bytes
        assert (backup / "static/spec-dock/scripts/spec-dock").stat().st_mode & 0o777 == 0o755
        assert {path.relative_to(backup).as_posix() for path in backup.rglob("*") if path.is_file()} == {
            "static/spec-dock/scripts/spec-dock"
        }
        assert (
            installed.read_bytes() == (Path(__file__).resolve().parents[2] / "src/spec_dock/shim_vnext.py").read_bytes()
        )
        assert installed.stat().st_mode & 0o777 == 0o755


def test_update_adds_a_missing_static_file_without_rewriting_the_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    declaration = target / "spec-dock/workspace.json"
    declaration.write_text(
        json.dumps({**json.loads(declaration.read_bytes()), "user_setting": "preserve"}), encoding="utf-8"
    )
    declaration_before = declaration.read_bytes()
    destination = target / "spec-dock/docs/README.md"
    destination.unlink()
    backup = tmp_path / "backup"
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert (
        data["created_paths"] == ["spec-dock/docs/README.md"]
        and data["changed_paths"] == []
        and data["retired_paths"] == []
    )
    assert declaration.read_bytes() == declaration_before
    assert (
        destination.read_bytes()
        == (Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/docs/README.md").read_bytes()
    )
    assert backup.is_dir() and not tuple(path for path in backup.rglob("*") if path.is_file())


def test_update_adds_a_missing_static_directory_without_a_runtime_or_state_store(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    directory = target / "spec-dock/templates/artifacts"
    for file in directory.iterdir():
        file.unlink()
    directory.rmdir()
    backup = tmp_path / "backup"
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 0
    )
    data = json.loads(capsys.readouterr().out)["data"]["result"]
    expected = {
        f"spec-dock/templates/artifacts/{name}.md"
        for name in ("adr", "blank", "decision-candidate", "disc", "interview", "research")
    }
    assert set(data["created_paths"]) == expected | {"spec-dock/templates/artifacts"}
    assert data["changed_paths"] == [] and not (target / "spec-dock/.agent").exists()
    assert not (target / "spec-dock/scripts/spec_dock_runtime").exists()


def test_update_retires_only_known_legacy_runtime_files_after_preservation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-control-store.txt").read_bytes()
    relative = "spec-dock/scripts/spec_dock_runtime/infra/control_store.py"
    retired = target / relative
    retired.parent.mkdir(parents=True)
    retired.write_bytes(old_bytes)
    unknown = retired.parent / "user-extension.py"
    unknown.write_bytes(b"private user extension\n")
    backup = tmp_path / "backup"
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["retired_paths"] == [relative] and data["changed_paths"] == [] and data["created_paths"] == []
    assert not retired.exists() and unknown.read_bytes() == b"private user extension\n"
    assert (backup / "static" / relative).read_bytes() == old_bytes
    assert retired.parent.is_dir() and not (target / ".git/spec-dock").exists()


@pytest.mark.parametrize("dry_run", [False, True])
def test_uninstall_preserves_workspace_specs_ignored_state_and_unknown_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    owned = target / "spec-dock/docs/README.md"
    old_bytes = owned.read_bytes()
    protected = (
        "spec-dock/workspace.json",
        "spec-dock/.gitignore",
        "spec-dock/initiatives/user-scope/.meta.json",
        "spec-dock/artifacts/user-evidence.bin",
        "spec-dock/.workbench/notes.md",
        "spec-dock/.agent/work-target/user-selected.json",
        "spec-dock/docs/user-notes.md",
        ".agents/skills/spec-dock/user-notes.md",
    )
    for relative in protected[2:]:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"private protected body\n")
    before, git_before = tree_digest(target), tree_digest(target / ".git")
    preserved = {relative: (target / relative).read_bytes() for relative in protected}
    backup = tmp_path / "backup"
    flags = ["--dry-run"] if dry_run else ["--yes"]
    assert (
        main(["installation", "uninstall", "--target", str(target), "--backup-dir", str(backup), *flags, "--json"]) == 0
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert data["created_paths"] == [] and data["changed_paths"] == []
    assert "private protected body" not in output.out + output.err and not output.err
    assert all((target / relative).read_bytes() == payload for relative, payload in preserved.items())
    assert tree_digest(target / ".git") == git_before
    if dry_run:
        assert result["status"] == "planned" and data["retired_paths"] == []
        assert data["can_apply"] is True and tree_digest(target) == before and not backup.exists()
    else:
        assert result["status"] == "succeeded" and len(data["retired_paths"]) == 84
        assert "spec-dock/docs/README.md" in data["retired_paths"] and not owned.exists()
        assert (backup / "static/spec-dock/docs/README.md").read_bytes() == old_bytes
        assert not any((backup / "static" / relative).exists() for relative in protected)
        assert run_git(target, "check-ignore", "--no-index", "--", "spec-dock/.agent/work-target/user-selected.json")
        assert main(["installation", "uninstall", "--target", str(target), "--json"]) == 0
        again = json.loads(capsys.readouterr().out)
        assert again["status"] == "unchanged" and again["effects"] == []


def test_update_reports_a_created_backup_when_capture_cleanup_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt").read_bytes()
    installed = target / "spec-dock/scripts/spec-dock"
    installed.write_bytes(old_bytes)
    before = tree_digest(target)
    backup = tmp_path / "backup"
    original_cleanup = tempfile.TemporaryDirectory.cleanup

    def fail_after_cleanup(directory: tempfile.TemporaryDirectory[str]) -> None:
        original_cleanup(directory)
        if Path(directory.name).name.startswith(".specdock-static-backup-"):
            raise OSError("injected capture cleanup failure")

    monkeypatch.setattr(tempfile.TemporaryDirectory, "cleanup", fail_after_cleanup)
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert result["status"] == "partial" and result["error"]["code"] == "INSTALLATION_INCOMPLETE"
    assert data["backup_verified"] is True and data["restore_verified"] is True
    assert data["changed_paths"] == [] and data["retired_paths"] == []
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "installation.change", "status": "not_attempted", "target": "spec-dock/scripts/spec-dock"},
    ]
    assert (backup / "static/spec-dock/scripts/spec-dock").read_bytes() == old_bytes
    assert tree_digest(target) == before and not output.err


@pytest.mark.skipif(os.name != "posix", reason="native POSIX directory-descriptor retirement fixture")
@pytest.mark.parametrize("after_removal", [False, True])
def test_update_retains_the_backup_and_reports_uncertain_retirement_without_rollback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, after_removal: bool
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-control-store.txt").read_bytes()
    relative = "spec-dock/scripts/spec_dock_runtime/infra/control_store.py"
    retired = target / relative
    retired.parent.mkdir(parents=True)
    retired.write_bytes(old_bytes)
    remaining = target / "spec-dock/spec-dock.version"
    remaining.write_bytes(b"81eb44adba68d374959a8d20f74157ed94d15dd2\n")
    parent = retired.parent.stat()
    original_unlink = os.unlink
    attempts: list[str] = []

    def fail_unlink(path: str | Path, *, dir_fd: int | None = None) -> None:
        if str(path) == retired.name and dir_fd is not None:
            held = os.fstat(dir_fd)
            if (held.st_dev, held.st_ino) == (parent.st_dev, parent.st_ino):
                attempts.append(str(path))
                if after_removal:
                    original_unlink(path, dir_fd=dir_fd)
                raise OSError("injected static retirement failure")
        original_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr(os, "unlink", fail_unlink)
    backup = tmp_path / "backup"
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert result["status"] == "partial" and data["retired_paths"] == [] and not output.err
    assert attempts == [retired.name]
    assert result["effects"] == [
        {"kind": "backup", "status": "succeeded", "target": str(backup)},
        {"kind": "installation.retire", "status": "unknown", "target": relative},
        {"kind": "installation.retire", "status": "not_attempted", "target": "spec-dock/spec-dock.version"},
    ]
    assert (backup / "static" / relative).read_bytes() == old_bytes
    assert (backup / "static/spec-dock/spec-dock.version").read_bytes() == remaining.read_bytes()
    assert retired.exists() is not after_removal
    assert remaining.is_file() and (target / "spec-dock/docs/README.md").is_file()


@pytest.mark.parametrize("leaf", ["update", "uninstall"])
@pytest.mark.parametrize(
    "relative", ["spec-dock/docs/README.md", "spec-dock/scripts/spec_dock_runtime/infra/control_store.py"]
)
def test_static_changes_refuse_unknown_current_or_retired_files_before_preservation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str, relative: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    modified = target / relative
    modified.parent.mkdir(parents=True, exist_ok=True)
    modified.write_bytes(b"private modified user contents\n")
    before = tree_digest(target)
    backup = tmp_path / "backup"
    assert main(["installation", leaf, "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "failed" and result["error"]["code"] == "PRECONDITION_FAILED"
    assert "modified or unknown" in result["error"]["message"] and relative in result["error"]["message"]
    assert result["effects"] == [] and tree_digest(target) == before and not backup.exists()
    assert "private modified user contents" not in output.out + output.err


@pytest.mark.skipif(os.name != "posix", reason="native POSIX symbolic-link fixture")
@pytest.mark.parametrize(
    "relative", ["spec-dock/docs/README.md", "spec-dock/scripts/spec_dock_runtime/infra/control_store.py"]
)
def test_update_refuses_redirected_current_or_retired_files_as_a_precondition(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], relative: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    redirected = target / relative
    redirected.parent.mkdir(parents=True, exist_ok=True)
    redirected.unlink(missing_ok=True)
    outside = tmp_path / "private-file"
    outside.write_bytes(b"private redirected body\n")
    redirected.symlink_to(outside)
    before = tree_digest(target)
    backup = tmp_path / "backup"
    assert (
        main(["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 3
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert tree_digest(target) == before and not backup.exists() and redirected.is_symlink()
    assert outside.read_bytes() == b"private redirected body\n"
    assert "private redirected body" not in output.out + output.err


def test_init_rejects_a_package_inventory_that_would_embed_a_runtime(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    package = tmp_path / "package"
    resources = package / "assets"
    resources.mkdir(parents=True)
    payload = b"inert fixture, never executable\n"
    (resources / "injected.py").write_bytes(payload)
    (resources / "static-inventory.json").write_text(
        json.dumps({
            "schema_version": "specdock.static-inventory/v1",
            "files": [
                {
                    "path": "spec-dock/scripts/spec_dock_runtime/injected.py",
                    "source": "injected.py",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "mode": 0o644,
                    "init_only": False,
                    "known_old_sha256": [],
                }
            ],
            "retired": [],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr("spec_dock.runtime.infra.static_assets.files", lambda _package: package)
    before = tree_digest(target)
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert tree_digest(target) == before and not (target / "spec-dock/scripts/spec_dock_runtime").exists()


@pytest.mark.parametrize(
    "arguments",
    [
        ["--version", "0.1.0"],
        ["--commit", "a" * 40],
        ["--maintenance"],
        ["--finalize"],
        ["--activate-engine"],
        ["--from-update", "a" * 32],
        ["--resume", "a" * 32],
        ["--rollback", "a" * 32],
    ],
)
def test_update_rejects_retired_engine_and_recovery_options_before_git_admission(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, arguments: list[str]
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    assert main(["installation", "update", "--target", "/missing", *arguments, "--yes", "--json"]) == 2
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert not output.err and not tuple(outside.iterdir())


@pytest.mark.parametrize("guard", ["internal", "existing", "symlink-parent", "confirmation"])
def test_update_checks_backup_location_and_confirmation_before_any_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt").read_bytes()
    (target / "spec-dock/scripts/spec-dock").write_bytes(old_bytes)
    backup = tmp_path / "backup"
    if guard == "internal":
        backup = target / "backup"
    elif guard == "existing":
        backup.write_bytes(b"private existing backup\n")
    elif guard == "symlink-parent":
        outside = tmp_path / "outside"
        outside.mkdir()
        redirected = tmp_path / "redirected"
        redirected.symlink_to(outside, target_is_directory=True)
        backup = redirected / "backup"
    arguments = ["installation", "update", "--target", str(target), "--backup-dir", str(backup), "--json"]
    if guard != "confirmation":
        arguments.append("--yes")
    before, surrounding = tree_digest(target), tree_digest(tmp_path)
    assert main(arguments) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and tree_digest(target) == before and tree_digest(tmp_path) == surrounding
    assert "private existing backup" not in output.out + output.err


@pytest.mark.parametrize("leaf", ["update", "uninstall"])
def test_static_changes_stop_if_the_observed_asset_is_replaced_with_same_bytes_during_backup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, leaf: str
) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert main(["installation", "init", str(target), "--yes", "--json"]) == 0
    capsys.readouterr()
    relative = "spec-dock/scripts/spec-dock"
    installed = target / relative
    old_bytes = (Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt").read_bytes()
    installed.write_bytes(old_bytes)
    original = installed.stat()
    before, git_before = tree_digest(target), tree_digest(target / ".git")
    backup = tmp_path / "backup"
    native_sync = os.fsync
    replaced: list[int] = []

    def replace_after_backup_sync(descriptor: int) -> None:
        native_sync(descriptor)
        if replaced or not backup.is_dir():
            return
        observed, expected = os.fstat(descriptor), backup.stat()
        if (observed.st_dev, observed.st_ino) != (expected.st_dev, expected.st_ino):
            return
        replacement = installed.with_name("same-content-actor")
        replacement.write_bytes(old_bytes)
        replacement.chmod(original.st_mode & 0o777)
        replacement.replace(installed)
        replaced.append(installed.stat().st_ino)

    monkeypatch.setattr(os, "fsync", replace_after_backup_sync)
    assert main(["installation", leaf, "--target", str(target), "--backup-dir", str(backup), "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert len(replaced) == 1 and replaced[0] != original.st_ino
    assert result["status"] == "partial" and result["error"]["code"] == "INSTALLATION_INCOMPLETE"
    assert data["changed_paths"] == data["created_paths"] == data["retired_paths"] == []
    assert data["backup_verified"] is True and data["restore_verified"] is True
    assert result["effects"][0] == {"kind": "backup", "status": "succeeded", "target": str(backup)}
    if leaf == "update":
        assert result["effects"][1:] == [
            {"kind": "installation.change", "status": "not_attempted", "target": relative},
        ]
    else:
        assert len(result["effects"]) == 85
        assert all(
            effect["kind"] == "installation.retire" and effect["status"] == "not_attempted"
            for effect in result["effects"][1:]
        )
        assert {"kind": "installation.retire", "status": "not_attempted", "target": relative} in result["effects"]
    assert installed.stat().st_ino == replaced[0] and installed.read_bytes() == old_bytes
    assert (backup / "static" / relative).read_bytes() == old_bytes
    assert tree_digest(target) == before and tree_digest(target / ".git") == git_before
