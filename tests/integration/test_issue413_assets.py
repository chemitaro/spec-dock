"""Installation manages only one explicit worktree's static package resources."""

from __future__ import annotations

import json
import os
from pathlib import Path
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

    def unexpected(*_args: object, **_kwargs: object) -> object:
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


@pytest.mark.parametrize("leaf", ["show", "init"])
def test_installation_read_and_initialization_help_describes_only_one_worktree(
    capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    assert main(["--project", "/missing", "installation", leaf, "--help"]) == 0
    output = capsys.readouterr().out
    assert "static" in output and "one" in output and "package" in output
    assert "registered worktrees" not in output and "readable installation control" not in output
    assert "journal IDs" not in output and "engine digest" not in output


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
