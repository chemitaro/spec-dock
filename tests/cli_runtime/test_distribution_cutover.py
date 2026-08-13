from __future__ import annotations

import hashlib
from pathlib import Path

from spec_dock import cli
from tests.cli_runtime.harness import main


REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets"
INSTALL_ROOT = PROVIDER_ROOT / "install_root"
SCAFFOLD_ROOT = PROVIDER_ROOT / "spec_dock"

CURRENT_INSTALL_ROOT_FILES = frozenset(
    {
        ".agents/skills/spec-dock/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
        ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
        ".github/workflows/ci.yml",
    }
)
CURRENT_SKILL_SHA256 = {
    ".agents/skills/spec-dock/SKILL.md": "7d722020bc4666dd523ddb48d454d5af40367b1d712299e3d5c7dbc88319ae71",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md": "7182c1156bcf3635ffd3113cdcfb1d507c819b6aba6982673c0b10166f5da40c",
}

REMOVED_INSTALL_ROOT_PREFIXES = (
    ".agents/host-adapters/",
    ".codex/",
    ".github/agents/",
)
REMOVED_SKILL_NAMES = frozenset(
    {
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
    }
)
REMOVED_DOC_PATHS = frozenset(
    {
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
    }
)
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


def test_s40b_provider_install_root_is_current_catalog_only() -> None:
    actual = _relative_files(INSTALL_ROOT)

    assert actual == CURRENT_INSTALL_ROOT_FILES
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_INSTALL_ROOT_PREFIXES)
    assert all(
        not (path.startswith(".agents/skills/") and Path(path).parts[2] in REMOVED_SKILL_NAMES)
        for path in actual
    )


def test_s40b_retained_skill_identity_matches_issue359_final_source() -> None:
    for relative_path, expected_sha256 in CURRENT_SKILL_SHA256.items():
        actual_sha256 = hashlib.sha256((INSTALL_ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_sha256 == expected_sha256


def test_s40b_retained_ci_and_gitignore_are_deterministic_assets() -> None:
    ci = (INSTALL_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python3 ./spec-dock/scripts/spec-dock sync" in ci
    assert "python3 ./spec-dock/scripts/spec-dock validate" in ci
    assert "spec-dock-chatgpt" not in ci
    assert (SCAFFOLD_ROOT / ".gitignore").is_file()
    assert "_DEFAULT_SPEC_DOCK_GITIGNORE" not in Path(cli.__file__).read_text(encoding="utf-8")


def test_s40b_provider_scaffold_excludes_removed_docs_and_templates() -> None:
    actual = _relative_files(SCAFFOLD_ROOT)
    assert REMOVED_DOC_PATHS.isdisjoint(actual)
    assert all(not path.startswith(prefix) for path in actual for prefix in REMOVED_TEMPLATE_PREFIXES)
    assert "templates/artifacts/pr-repair-batch.md" not in actual


def test_s40b_fresh_init_materializes_only_current_external_catalog(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0

    installed = _relative_files(tmp_path)
    installed_external = frozenset(
        path
        for path in installed
        if path.startswith(".agents/") or path.startswith(".github/")
    )
    assert installed_external == CURRENT_INSTALL_ROOT_FILES
    assert (tmp_path / "spec-dock/.gitignore").read_bytes() == (SCAFFOLD_ROOT / ".gitignore").read_bytes()
    assert not (tmp_path / "spec-dock/scripts/spec-dock-chatgpt").exists()
