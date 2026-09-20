from __future__ import annotations

import os
from pathlib import Path

from tests.cli_runtime.harness import main

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets"
INSTALL_ROOT = PROVIDER_ROOT / "install_root"
SCAFFOLD_ROOT = PROVIDER_ROOT / "spec_dock"

CURRENT_INSTALL_ROOT_FILES = frozenset({
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
    ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
})
CURRENT_RETAINED_SKILL_FILES = (
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
)


def _relative_files(root: Path) -> frozenset[str]:
    return frozenset(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    )


def _executable_relative_files(root: Path) -> frozenset[str]:
    return frozenset(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and path.stat().st_mode & 0o111
    )


def _filesystem_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    snapshot: dict[str, tuple[object, ...]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        info = path.lstat()
        if path.is_symlink():
            snapshot[relative] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            snapshot[relative] = ("file", info.st_mode & 0o777, path.read_bytes())
        elif path.is_dir():
            snapshot[relative] = ("directory", info.st_mode & 0o777)
    return snapshot


def test_provider_install_root_is_current_catalog_only() -> None:
    actual = _relative_files(INSTALL_ROOT)

    assert actual == CURRENT_INSTALL_ROOT_FILES


def test_retained_skill_identity_matches_current_provider_and_dogfood() -> None:
    for relative_path in CURRENT_RETAINED_SKILL_FILES:
        provider = INSTALL_ROOT / relative_path
        dogfood = REPO_ROOT / relative_path
        assert provider.is_file() and not provider.is_symlink()
        assert dogfood.is_file() and not dogfood.is_symlink()
        assert provider.read_bytes() == dogfood.read_bytes()
        assert provider.stat().st_mode & 0o777 == dogfood.stat().st_mode & 0o777


def test_only_runtime_wrapper_is_executable_across_current_surfaces(tmp_path: Path) -> None:
    assert _executable_relative_files(PROVIDER_ROOT) == frozenset({"spec_dock/scripts/spec-dock"})
    dogfood_paths = {
        *(REPO_ROOT / path for path in CURRENT_INSTALL_ROOT_FILES),
        *(
            path
            for root in ("docs", "templates", "scripts", "system")
            for path in (REPO_ROOT / "spec-dock" / root).rglob("*")
            if path.is_file()
        ),
    }
    dogfood_executables = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in dogfood_paths
        if not path.is_symlink() and path.stat().st_mode & 0o111
    }
    assert dogfood_executables == {"spec-dock/scripts/spec-dock"}

    assert main(["init", str(tmp_path)]) == 0
    assert _executable_relative_files(tmp_path) == frozenset({"spec-dock/scripts/spec-dock"})


def test_fresh_init_copies_exact_current_external_catalog(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    installed_external = frozenset(
        path for path in _relative_files(tmp_path) if path.startswith(".agents/") or path.startswith(".github/")
    )
    assert installed_external == CURRENT_INSTALL_ROOT_FILES
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == (SCAFFOLD_ROOT / ".gitignore").read_bytes()


def test_fresh_init_preserves_unrelated_and_obsolete_looking_external_paths(tmp_path: Path) -> None:
    unrelated = tmp_path / "README.user.md"
    unrelated.write_bytes(b"user content\n")
    obsolete_skill = tmp_path / ".agents/skills/spec-dock-issue-planning/SKILL.md"
    obsolete_skill.parent.mkdir(parents=True)
    obsolete_skill.write_bytes(b"user-owned obsolete-looking skill\n")
    native_shim = tmp_path / ".codex/agents/legacy.md"
    native_shim.parent.mkdir(parents=True)
    native_shim.write_bytes(b"user-owned native shim\n")
    unknown_workflow = tmp_path / ".github/workflows/user.yml"
    unknown_workflow.parent.mkdir(parents=True)
    unknown_workflow.write_bytes(b"user-owned workflow\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 0

    after = _filesystem_snapshot(tmp_path)
    for path in (unrelated, obsolete_skill, native_shim, unknown_workflow):
        relative = path.relative_to(tmp_path).as_posix()
        assert after[relative] == before[relative]
    assert (tmp_path / "spec-dock/docs/README.md").is_file()
    assert (tmp_path / "spec-dock/.gitignore").is_file()


def test_existing_consumer_workflow_is_preserved(tmp_path: Path) -> None:
    seed = tmp_path / ".github/workflows/ci.yml"
    seed.parent.mkdir(parents=True)
    seed.write_bytes(b"consumer workflow\n")
    before = (seed.read_bytes(), os.lstat(seed).st_ino)

    assert main(["init", str(tmp_path)]) == 0

    assert (seed.read_bytes(), os.lstat(seed).st_ino) == before


def test_foreign_fixed_root_is_preserved_and_blocks_fresh_install(tmp_path: Path) -> None:
    root = tmp_path / "spec-dock/docs"
    root.mkdir(parents=True)
    sentinel = root / "consumer.md"
    sentinel.write_bytes(b"consumer-owned\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    assert _filesystem_snapshot(tmp_path) == before


def test_init_replaces_the_fixed_skill_directory(tmp_path: Path) -> None:
    slot = tmp_path / ".agents/skills/spec-dock"
    slot.mkdir(parents=True)
    sentinel = slot / "local.md"
    sentinel.write_text("discard")
    assert main(["init", str(tmp_path)]) == 0
    assert not sentinel.exists()
    assert (slot / "SKILL.md").is_file()
