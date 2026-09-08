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
    ".github/workflows/ci.yml",
})
CURRENT_SLOT_MARKERS = frozenset({
    ".agents/skills/spec-dock/.spec-dock-provider-slot.json",
    ".agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json",
})
CURRENT_RETAINED_SKILL_FILES = (
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
)
REMOVED_INSTALL_ROOT_PREFIXES = (
    ".agents/host-adapters/",
    ".codex/",
    ".github/agents/",
)
REMOVED_SKILL_NAMES = frozenset({
    "spec-dock-hub",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-epic-execution",
    "spec-dock-issue-planning",
    "spec-dock-issue-execution",
    "spec-dock-chatgpt-authoring",
    "spec-dock-initiative-planning-manual",
    "spec-dock-epic-planning-manual",
    "spec-dock-issue-planning-manual",
    "spec-dock-clarification",
    "spec-dock-adr-facilitation",
    "spec-dock-codex-adapter",
    "spec-dock-copilot-adapter",
    "git-commit-conventional-ja",
    "github-pr-observation",
    "github-pr-creator",
    "github-pr-merge-preparer",
    "spec-driven-tdd-workflow",
    "spec-dock-system-architect",
    "spec-dock-implementation-planner",
})
REMOVED_DOC_PATHS = frozenset({
    "docs/authoring/chatgpt-pack.md",
    "docs/authoring/decision-routing.md",
    "docs/reference_authoring_pack_backend.md",
    "docs/reference_hard_cutover.md",
    "docs/github.md",
    "docs/phase_design.md",
    "docs/phase_plan.md",
    "docs/phase_plan_epic.md",
    "docs/phase_plan_initiative.md",
    "docs/phase_plan_issue.md",
    "docs/phase_requirement.md",
    "docs/workflow-tree.md",
    "docs/workflow_adr.md",
    "docs/workflow_chatgpt_authoring_pack.md",
    "docs/workflow_clarification.md",
    "docs/workflow_epic.md",
    "docs/workflow_initiative.md",
    "docs/workflow_issue.md",
    "docs/workflow_spec_authoring.md",
})
REMOVED_TEMPLATE_PREFIXES = (
    "templates/discussions/",
    "templates/assurance/",
    "templates/issue-profiles/",
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


def test_s40b_provider_install_root_is_current_catalog_only() -> None:
    actual = _relative_files(INSTALL_ROOT)

    assert actual == CURRENT_INSTALL_ROOT_FILES
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_INSTALL_ROOT_PREFIXES)
    assert all(
        not (path.startswith(".agents/skills/") and Path(path).parts[2] in REMOVED_SKILL_NAMES) for path in actual
    )


def test_s40b_retained_skill_identity_matches_current_provider_and_dogfood() -> None:
    for relative_path in CURRENT_RETAINED_SKILL_FILES:
        provider = INSTALL_ROOT / relative_path
        dogfood = REPO_ROOT / relative_path
        assert provider.is_file() and not provider.is_symlink()
        assert dogfood.is_file() and not dogfood.is_symlink()
        assert provider.read_bytes() == dogfood.read_bytes()
        assert provider.stat().st_mode & 0o777 == dogfood.stat().st_mode & 0o777


def test_s40b_retained_ci_and_gitignore_are_deterministic_assets() -> None:
    ci = (INSTALL_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python3 ./spec-dock/scripts/spec-dock sync" in ci
    assert "python3 ./spec-dock/scripts/spec-dock validate" in ci
    assert "spec-dock-chatgpt" not in ci
    assert (SCAFFOLD_ROOT / ".gitignore").is_file()


def test_s40b_only_runtime_wrapper_is_executable_across_current_surfaces(tmp_path: Path) -> None:
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


def test_s40b_provider_scaffold_excludes_removed_docs_and_templates() -> None:
    actual = _relative_files(SCAFFOLD_ROOT)
    assert REMOVED_DOC_PATHS.isdisjoint(actual)
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_TEMPLATE_PREFIXES)
    assert "templates/artifacts/pr-repair-batch.md" not in actual
    current_docs = tuple((SCAFFOLD_ROOT / "docs").rglob("*.md"))
    for removed_path in REMOVED_DOC_PATHS:
        removed_name = Path(removed_path).name
        retired_routes = (f"`{removed_name}`", f"]({removed_name})", f"spec-dock/{removed_path}")
        assert all(
            all(route not in path.read_text(encoding="utf-8") for route in retired_routes) for path in current_docs
        ), f"Current documentation still routes to retired path: {removed_path}"


def test_s40b_fresh_init_materializes_current_external_catalog_and_slot_markers(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    installed_external = frozenset(
        path for path in _relative_files(tmp_path) if path.startswith(".agents/") or path.startswith(".github/")
    )
    assert installed_external == CURRENT_INSTALL_ROOT_FILES | CURRENT_SLOT_MARKERS
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == (SCAFFOLD_ROOT / ".gitignore").read_bytes()


def test_s45_fresh_preserves_unrelated_and_obsolete_looking_external_paths(tmp_path: Path) -> None:
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


def test_s45_existing_consumer_seed_is_preserved(tmp_path: Path) -> None:
    seed = tmp_path / ".github/workflows/ci.yml"
    seed.parent.mkdir(parents=True)
    seed.write_bytes(b"consumer workflow\n")
    before = (seed.read_bytes(), os.lstat(seed).st_ino)

    assert main(["init", str(tmp_path)]) == 0

    assert (seed.read_bytes(), os.lstat(seed).st_ino) == before


def test_s45_foreign_fixed_root_is_preserved_and_blocks_fresh_install(tmp_path: Path) -> None:
    root = tmp_path / "spec-dock/docs"
    root.mkdir(parents=True)
    sentinel = root / "consumer.md"
    sentinel.write_bytes(b"consumer-owned\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    assert _filesystem_snapshot(tmp_path) == before


def test_s45_foreign_skill_slot_is_preserved_and_blocks_fresh_install(tmp_path: Path) -> None:
    slot = tmp_path / ".agents/skills/spec-dock"
    slot.mkdir(parents=True)
    sentinel = slot / "consumer.md"
    sentinel.write_bytes(b"consumer-owned\n")
    before = _filesystem_snapshot(tmp_path)

    assert main(["init", str(tmp_path)]) == 1

    assert _filesystem_snapshot(tmp_path) == before
