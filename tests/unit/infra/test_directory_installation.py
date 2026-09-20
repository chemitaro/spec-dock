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


def test_installed_runtime_starts_without_provider_markers(tmp_path: Path) -> None:
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
    assert not (tmp_path / ".agents/skills/spec-dock/.spec-dock-provider-slot.json").exists()


def test_failed_copy_can_be_retried_without_touching_data(tmp_path: Path, monkeypatch) -> None:
    import shutil

    assert main(["init", str(tmp_path)]) == 0
    data = tmp_path / "spec-dock/user-data.txt"
    data.write_bytes(b"keep")
    original = shutil.copytree

    def broken_copy(*args, **kwargs):
        raise OSError("injected disk error")

    with monkeypatch.context() as patch:
        patch.setattr(shutil, "copytree", broken_copy)
        assert main(["update", str(tmp_path)]) != 0
    assert data.read_bytes() == b"keep"
    assert shutil.copytree is original
    assert main(["update", str(tmp_path)]) == 0
    assert (tmp_path / "spec-dock/docs/README.md").is_file()
    assert data.read_bytes() == b"keep"


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
