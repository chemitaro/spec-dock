"""Observable contracts for directory replacement, independent of the old wire."""

from pathlib import Path

from spec_dock.cli import main


def test_update_replaces_whole_directories_and_preserves_data(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    stale = tmp_path / "spec-dock/templates/local-only.txt"
    stale.write_text("discard this customization")
    data = tmp_path / "spec-dock/initiatives/example/requirement.md"
    data.parent.mkdir(parents=True)
    data.write_bytes(b"user data\n")
    assert main(["update", str(tmp_path)]) == 0
    assert not stale.exists()
    assert data.read_bytes() == b"user data\n"
    assert (tmp_path / "spec-dock/spec-dock.version").read_text().strip() == "0.2.4"


def test_installed_runtime_starts_from_current_catalog(tmp_path: Path) -> None:
    import subprocess
    import sys

    assert main(["init", str(tmp_path)]) == 0
    result = subprocess.run(
        [sys.executable, str(tmp_path / "spec-dock/scripts/spec-dock"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "validate" in result.stdout


def test_update_mid_copy_failure_is_nontransactional_and_rerunnable_without_touching_data(
    tmp_path: Path, monkeypatch
) -> None:
    import stat

    from spec_dock import __version__, installer

    assert main(["init", str(tmp_path)]) == 0
    data = tmp_path / "spec-dock/initiatives/preservation/sentinel.txt"
    data.parent.mkdir(parents=True)
    data.write_bytes(b"user data\n")
    version = tmp_path / installer.VERSION_FILE
    version.write_bytes(b"old-version\n")
    sources = installer._sources(installer.ASSETS)
    stale_paths: list[Path] = []
    for relative in installer.TOOL_DIRECTORIES:
        stale = tmp_path / relative / "pre-update-stale.txt"
        stale.write_text("remove on retry", encoding="utf-8")
        stale_paths.append(stale)

    def snapshot(root: Path) -> dict[str, tuple[object, ...]]:
        entries: dict[str, tuple[object, ...]] = {}
        for path in sorted((root, *root.rglob("*"))):
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            relative = "." if path == root else path.relative_to(root).as_posix()
            mode = stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)
            if path.is_symlink():
                entries[relative] = ("symlink", path.readlink().as_posix(), mode)
            elif path.is_dir():
                entries[relative] = ("directory", mode)
            elif path.is_file():
                entries[relative] = ("file", path.read_bytes(), mode)
            else:
                entries[relative] = ("other", mode)
        return entries

    original_copy = installer._copy
    copy_count = 0

    def fail_during_fourth_copy(source: Path, destination: Path) -> None:
        nonlocal copy_count
        copy_count += 1
        if copy_count < 4:
            original_copy(source, destination)
            return
        if copy_count == 4:
            destination.mkdir()
            (destination / "partial.txt").write_bytes(b"partial copy\n")
            raise OSError("injected fourth-copy failure")
        raise AssertionError("installer continued copying after the injected fourth-copy failure")

    with monkeypatch.context() as patch:
        patch.setattr(installer, "_copy", fail_during_fourth_copy)
        assert main(["update", str(tmp_path)]) != 0

    assert copy_count == 4
    for index, (relative, source) in enumerate(zip(installer.TOOL_DIRECTORIES, sources, strict=True)):
        destination = tmp_path / relative
        if index < 3:
            assert snapshot(destination) == snapshot(source)
            assert not stale_paths[index].exists()
        elif index == 3:
            assert (destination / "partial.txt").read_bytes() == b"partial copy\n"
            assert snapshot(destination) != snapshot(source)
            assert not stale_paths[index].exists()
        else:
            assert stale_paths[index].read_text(encoding="utf-8") == "remove on retry"

    assert version.read_bytes() == b"old-version\n"
    assert data.read_bytes() == b"user data\n"

    assert main(["update", str(tmp_path)]) == 0
    for relative, source, stale in zip(installer.TOOL_DIRECTORIES, sources, stale_paths, strict=True):
        destination = tmp_path / relative
        assert snapshot(destination) == snapshot(source)
        assert not stale.exists()
    assert not any((tmp_path / relative / "partial.txt").exists() for relative in installer.TOOL_DIRECTORIES)
    assert version.read_text(encoding="utf-8") == f"{__version__}\n"
    assert data.read_bytes() == b"user data\n"


def test_uninstall_dry_run_then_removes_only_tool_directories(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    data = tmp_path / "spec-dock/local.md"
    data.write_text("keep")
    assert main(["uninstall", str(tmp_path)]) == 0
    assert (tmp_path / "spec-dock/scripts").is_dir()
    assert main(["uninstall", str(tmp_path), "--apply"]) == 0
    assert not (tmp_path / "spec-dock/scripts").exists()
    assert not (tmp_path / ".agents/skills/spec-dock").exists()
    assert data.read_text() == "keep"
    assert main(["uninstall", str(tmp_path), "--apply"]) == 0


def test_symlink_parent_is_rejected_before_any_replacement(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    import shutil

    shutil.rmtree(tmp_path / ".agents/skills")
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "sentinel"
    sentinel.write_text("keep")
    (tmp_path / ".agents/skills").symlink_to(outside, target_is_directory=True)
    old = tmp_path / "spec-dock/docs/old.txt"
    old.write_text("unchanged")
    assert main(["update", str(tmp_path)]) != 0
    assert old.read_text() == "unchanged"
    assert sentinel.read_text() == "keep"


def test_force_init_replaces_tools_without_reseeding_settings(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    ignore = tmp_path / "spec-dock/.gitignore"
    ignore.write_text("local setting\n")
    assert main(["init", str(tmp_path)]) != 0
    assert main(["init", str(tmp_path), "--force"]) == 0
    assert ignore.read_text() == "local setting\n"
    assert not (tmp_path / ".github").exists()


def test_all_six_directories_match_package_and_discard_old_files(tmp_path: Path) -> None:
    from spec_dock.installer import ASSETS

    pairs = [
        (ASSETS / "spec_dock" / name, tmp_path / "spec-dock" / name)
        for name in ("docs", "templates", "system", "scripts")
    ]
    pairs += [
        (ASSETS / "install_root/.agents/skills" / name, tmp_path / ".agents/skills" / name)
        for name in ("spec-dock", "spec-dock-grill-with-docs")
    ]

    def contents(root: Path) -> dict[str, bytes]:
        return {
            str(p.relative_to(root)): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}
        }

    assert main(["init", str(tmp_path)]) == 0
    for source, target in pairs:
        assert contents(target) == contents(source)
        (target / "obsolete.txt").write_text("discard")
    assert main(["update", str(tmp_path)]) == 0
    for source, target in pairs:
        assert contents(target) == contents(source)


def test_missing_source_is_rejected_before_deleting_anything(tmp_path: Path) -> None:
    import pytest

    from spec_dock.installer import install

    assert main(["init", str(tmp_path)]) == 0
    sentinel = tmp_path / "spec-dock/docs/local.md"
    sentinel.write_text("unchanged")
    with pytest.raises(ValueError, match="Missing packaged directory"):
        install(tmp_path, version="new", fresh=False, assets=tmp_path / "missing-package")
    assert sentinel.read_text() == "unchanged"


def test_version_hard_link_does_not_modify_external_data(tmp_path: Path) -> None:
    import os

    assert main(["init", str(tmp_path)]) == 0
    external = tmp_path / "data.txt"
    external.write_text("user data")
    version = tmp_path / "spec-dock/spec-dock.version"
    version.unlink()
    os.link(external, version)
    assert main(["update", str(tmp_path)]) == 0
    assert external.read_text() == "user data"
    assert version.read_text() == "0.2.4\n"


def test_fresh_install_rejects_copy_into_its_scaffold_source(tmp_path: Path, monkeypatch) -> None:
    import pytest

    from spec_dock import installer

    assets = tmp_path / "assets"
    for name in installer.ROOTS:
        (assets / "spec_dock" / name).mkdir(parents=True)
    for name in installer.SKILLS:
        (assets / "install_root/.agents/skills" / name).mkdir(parents=True)
    target = assets / "spec_dock"
    sentinel = target / "source.txt"
    sentinel.write_bytes(b"original distribution")

    def unexpected_copy(*args, **kwargs):
        pytest.fail("overlapping source reached copy")

    monkeypatch.setattr(installer, "_copy", unexpected_copy)
    with pytest.raises(ValueError, match="overlaps the distribution source"):
        installer.install(target, version="new", fresh=True, assets=assets)
    assert sentinel.read_bytes() == b"original distribution"
    assert not (target / "spec-dock").exists()
    assert not (target / ".agents").exists()


def test_failed_fresh_init_is_retried_after_preserving_partial_scaffold(tmp_path: Path, monkeypatch) -> None:
    from spec_dock import installer

    def partial_copy(source, destination):
        destination.mkdir()
        (destination / "local.txt").write_bytes(b"preserve me")
        raise OSError("injected initial copy failure")

    with monkeypatch.context() as patch:
        patch.setattr(installer, "_copy", partial_copy)
        assert main(["init", str(tmp_path)]) != 0
    scaffold = tmp_path / "spec-dock"
    assert not (scaffold / ".gitignore").exists()
    assert main(["update", str(tmp_path)]) == 0
    assert not (scaffold / ".gitignore").exists()
    assert (scaffold / "local.txt").read_bytes() == b"preserve me"
    preserved = tmp_path / "preserved-scaffold"
    scaffold.rename(preserved)
    assert main(["init", str(tmp_path)]) == 0
    assert (scaffold / ".gitignore").is_file()
    assert (preserved / "local.txt").read_bytes() == b"preserve me"
