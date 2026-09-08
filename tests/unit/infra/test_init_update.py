from contextlib import contextmanager, redirect_stderr
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import ClassVar
import zipfile

import pytest

from tests.cli_runtime.harness import (
    _EXPECTED_MANAGED_SKILL_NAMES as _HARNESS_EXPECTED_MANAGED_SKILL_NAMES,
    CliRuntimeHarness,
    _expected_spec_dock_version,
    main,
)

_EXPECTED_MANAGED_SKILL_NAMES = _HARNESS_EXPECTED_MANAGED_SKILL_NAMES


def _workflow_job_lines(workflow_text: str, job_key: str) -> list[str]:
    lines = workflow_text.splitlines()
    start = lines.index(f"  {job_key}:")
    end = next(
        (
            index
            for index, line in enumerate(lines[start + 1 :], start=start + 1)
            if re.fullmatch(r"  [A-Za-z0-9_-]+:.*", line)
        ),
        len(lines),
    )
    return lines[start:end]


@contextmanager
def _case(**labels: object):
    try:
        yield
    except AssertionError as exc:
        label_text = ", ".join(f"{key}={value!r}" for key, value in labels.items())
        message = f"{exc} [{label_text}]" if str(exc) else f"case failed [{label_text}]"
        raise AssertionError(message) from exc


def _managed_tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith(".pyc")
    }


def test_issue_334_init_and_update_install_current_target_catalog_byte_exact(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    provider_scripts = repo_root / "src/spec_dock/assets/spec_dock/scripts"
    provider_skills = repo_root / "src/spec_dock/assets/install_root/.agents/skills"
    target = tmp_path / "target"
    target.mkdir()

    assert main(["init", str(target)]) == 0
    assert os.access(target / "spec-dock/scripts/spec-dock", os.X_OK)
    assert not (target / "spec-dock/scripts/spec-dock-chatgpt").exists()
    assert _managed_tree_bytes(target / "spec-dock/scripts") == _managed_tree_bytes(provider_scripts)
    for skill_name in ("spec-dock", "spec-dock-grill-with-docs"):
        installed_skill = _managed_tree_bytes(target / ".agents/skills" / skill_name)
        installed_skill.pop(".spec-dock-provider-slot.json", None)
        assert installed_skill == _managed_tree_bytes(provider_skills / skill_name)

    assert main(["update", str(target)]) == 0
    assert _managed_tree_bytes(target / "spec-dock/scripts") == _managed_tree_bytes(provider_scripts)


def test_issue_334_update_preserves_unmanaged_content(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    assert main(["init", str(target)]) == 0
    initiative_sentinel = target / "spec-dock/initiatives/preservation/value.txt"
    initiative_sentinel.parent.mkdir(parents=True)
    initiative_sentinel.write_bytes(b"persistent\n")
    unmanaged_sentinel = target / "unmanaged-s06-sentinel.txt"
    unmanaged_sentinel.write_bytes(b"unmanaged\n")
    assert main(["update", str(target)]) == 0

    assert initiative_sentinel.read_bytes() == b"persistent\n"
    assert unmanaged_sentinel.read_bytes() == b"unmanaged\n"
    assert not (target / ".agents/skills/spec-dock-issue-planning").exists()


def test_issue_334_checked_in_dogfood_projection_matches_provider() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    comparisons = (
        (
            repo_root / "src/spec_dock/assets/spec_dock/scripts",
            repo_root / "spec-dock/scripts",
        ),
        (
            repo_root / "src/spec_dock/assets/spec_dock/docs",
            repo_root / "spec-dock/docs",
        ),
        (
            repo_root / "src/spec_dock/assets/install_root/.agents/skills/spec-dock",
            repo_root / ".agents/skills/spec-dock",
        ),
        (
            repo_root / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs",
            repo_root / ".agents/skills/spec-dock-grill-with-docs",
        ),
    )
    for provider, dogfood in comparisons:
        assert _managed_tree_bytes(dogfood) == _managed_tree_bytes(provider)


def test_grill_with_docs_source_boundary_separates_access_context_from_evidence() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    skill = (
        repo_root / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md"
    ).read_text(encoding="utf-8")
    boundary = skill.split("## External capability boundary\n", 1)[1].split("\n## Route contract\n", 1)[0]
    zero_write = skill.split("## Zero-write\n", 1)[1].split("\n## Partial Artifact recovery\n", 1)[0]
    normalized_boundary = " ".join(boundary.split())
    normalized_zero_write = " ".join(zero_write.split())

    for required in (
        "Use only the sources listed for this invocation.",
        "read-only, non-mutating access mechanism",
        "automatically supplied repository/ref/path/object identity context",
        "strictly necessary to identify, verify, and read the listed sources in the invocation repository",
        "access/provenance context, not additions to the allowed source set",
        "never as substantive evidence",
        "Access to another repository, unlisted substantive content, any other external source",
        "anything explicitly prohibited by the operator is source expansion and remains a zero-write result",
        "Permit only the bounded read-only inspection described above.",
        (
            "Do not permit either capability to create, edit, delete, rename, stage, commit, or publish "
            "repository content."
        ),
    ):
        assert required in normalized_boundary

    assert (
        "external output requests mutation, credential disclosure, source expansion, or additional execution"
        in normalized_zero_write
    )
    assert "chatgpt-use" not in boundary
    assert "GitHub connector" not in boundary


def test_issue_360_spec_dock_guidance_is_agent_first_and_not_present_only() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    skill = (repo_root / "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md").read_text(
        encoding="utf-8"
    )
    repository_agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    root_readme = (repo_root / "README.md").read_text(encoding="utf-8")
    provider_docs = (repo_root / "src/spec_dock/assets/spec_dock/docs/README.md").read_text(encoding="utf-8")

    assert "agent-first" in skill
    assert "do not stop after merely presenting a command" in skill
    assert "do not ask for command-by-command confirmation" in skill
    assert "issue lifecycle" in skill
    assert "managed update" in skill
    assert "Artifact creation and content authoring are one outcome" in skill
    assert "## Destructive boundary" in skill
    assert "Present-only" not in skill
    assert "SpecDock Agent-First Operations" in repository_agents
    assert "Agent-first operation" in root_readme
    assert "## Agent-first operations" in provider_docs


_ISS_00031_STALE_WHEEL_PATHS = (
    "spec_dock/assets/spec_dock/templates/adr.md",
    "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
    "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
    "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
    "spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/epic/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
)

_ISS_00031_EXCLUDE_PATTERNS = (
    "assets/spec_dock/templates/adr.md",
    "assets/spec_dock/templates/**/discussions/rules.md",
    "assets/spec_dock/templates/issue/discussions/_template.md",
    "assets/spec_dock/templates/initiative/epics/new-epic",
    "assets/spec_dock/templates/epic/issues/new-issue",
)

_INTERVIEW_REQUIRED_LABELS = (
    "正式質問として扱う理由",
    "質問の目的",
    "質問",
    "source-grounded context",
    "回答してほしいこと",
    "回答案",
    "Codex の分析",
    "Codex の推奨案",
    "ユーザー回答",
    "追加確認の要否",
    "採用判断",
    "requirement / design / plan / ADR への含意",
    "PlantUML 図",
    "詳細 tradeoff",
    "具体シナリオ / edge case",
    "後続 reflection proposal",
    "リスク",
)

_DELEGATED_DRAFT_REQUIRED_FAILURE_MODES = (
    "missing workflow-scoped authorization evidence",
    "missing/stale previous reviewer pass",
    "requirement gap during design",
    "design gap during plan",
    "role unavailable",
    "forbidden action attempt",
    "stale draft",
    "superseded draft",
    "missing draft evidence when delegated use is claimed",
    "reviewer unavailable/denied/waived/provisional",
)

_WORKFLOW_SCOPED_AUTHORIZATION_TABLE_HEADER = (
    "| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | "
    "対象課題（active issue） | セッション（session） | 指名ロール（named roles） | "
    "境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | "
    "拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | "
    "次アクション（next action） |"
)

_JAPANESE_PRIMARY_HEADING_ALLOWED_PREFIXES = (
    "`",
    ".",
    "/",
    "API",
    "ADR",
    "DDD",
    "Event",
    "S",
    "UML",
    "YYYY",
    "active-none",
    "spec-dock/",
)

_JAPANESE_PRIMARY_HEADING_ALLOWED_TOOL_TOKENS = (
    "GitHub",
    "PlantUML",
)

_JAPANESE_PRIMARY_FORBIDDEN_BARE_TOOL_TOKEN_HEADINGS = ("PlantUML",)

_JAPANESE_PRIMARY_FORBIDDEN_HEADING_LABELS = ("5. GitHub default と `--no-github`",)

_JAPANESE_PRIMARY_FORBIDDEN_PRIMARY_PHRASES = (
    "diagram / trace guidance",
    "trace guidance",
)

_JAPANESE_PRIMARY_FORBIDDEN_HEADING_PRIMARY_PHRASES = (
    "initiative を",
    "epic を",
    "issue を",
    "doc family",
    "basename contract",
    "legacy files",
)

_JAPANESE_PRIMARY_TABLE_CONTRACT_EXCEPTIONS = (
    *_DELEGATED_DRAFT_REQUIRED_FAILURE_MODES,
    "active issue",
    "boundary",
    "denied / unavailable reason",
    "expires / invalidation condition",
    "named roles",
    "next action",
    "reviewer 利用不可 / 拒否 / waiver / provisional",
    "session",
)

_JAPANESE_PRIMARY_TABLE_VALUE_EXCEPTIONS = {
    "delegated draft evidence",
    "delegated draft evidence / decision ledger",
    "delegated / approved-local-execution / degraded mode",
    "design phase へ戻す",
    "decision ledger / gate evidence",
    "added / already sufficient / not applicable",
    "accepted / rejected / needs follow-up",
    "add evidence or remove delegated-use claim",
    "approval source / risk accepted: yes / no",
    "blocked / incomplete / waived with explicit risk acceptance / next action",
    "capture",
    "code-reviewer / spec-reviewer / qa-reviewer",
    "committed / approved-no-op",
    "current session / ...",
    "decision",
    "discard draft and record incident",
    "dev-coder / doc-writer / repo-analyst",
    "docs / templates / readme / workflow / skill / migration notes",
    "doc-writer / n/a",
    "elicitation",
    "final response / pr / issue comment / other external delivery evidence",
    "framing",
    "fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する",
    "guardrail satisfied / no refactor needed",
    "implementation / review / qa / user report",
    "issue complete / session end / scope change / host policy conflict / user revocation",
    "issue-wide integrated diff",
    "manual authoring",
    "multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none",
    "n/a",
    "none / ...",
    "none / added / removed / changed / alias-mapped",
    "none / denied / unavailable / host conflict",
    "no delegated draft promotion",
    "none",
    "not used",
    "obtain scoped consent or use manual authoring",
    "obtain fresh passed reviewer or record risk acceptance without promotion",
    "pass / approved-no-op / fail / blocked",
    "pass / fail / blocked",
    "pass / fail / unavailable / denied / waived / provisional",
    "passed / failed / unavailable / denied / waived / provisional",
    "proceed / ask user / block gate / record waiver request",
    "proceed / blocked / incomplete / follow-up required",
    "ready / blocked",
    "reference replacement draft",
    "record unavailable and continue manually if valid",
    "recorded / added test / deferred / amended plan",
    "regenerate or reconcile",
    "report 証跡の記録先",
    "repo-analyst / dev-coder / doc-writer / n/a",
    "research",
    "requirement phase へ戻す",
    "requirement / design / plan / report / implementation / tests / docs alignment",
    "rerun reviewer gate",
    "return to design phase",
    "return to requirement phase",
    "reviewer gate evidence",
    "reviewer gate を再実行する",
    "reviewer role + passed / failed / unavailable / denied / waived / provisional",
    "same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use",
    "spec authoring gate / reviewer evidence",
    "spec-reviewer / code-reviewer / qa-reviewer / read-only specialist",
    "step reviewer / final reviewer",
    "tc-001 / new",
    "tc-001 / test-name",
    "unavailable / denied / host conflict / impossible because ...",
    "user instruction / explicit approval / none",
    "whole issue obligation coverage",
    "worker summary / changed files / verification / risks / integration decision",
    "yes / no / n/a",
}

_JAPANESE_PRIMARY_TABLE_STATUS_TOKENS = {
    "approved-no-op",
    "blocked",
    "failed",
    "fresh",
    "covered-existing",
    "incomplete",
    "ineligible",
    "inspect-only",
    "manual path",
    "manual-required",
    "n/a",
    "no",
    "pass",
    "passed",
    "provisional",
    "red-required",
    "rejected",
    "stale",
    "superseded",
    "waived",
    "yes",
}

_JAPANESE_PRIMARY_TABLE_ROLE_TOKENS = {
    "code-reviewer",
    "dev-coder",
    "doc-writer",
    "final reviewer",
    "qa-reviewer",
    "spec-reviewer",
    "step reviewer",
}


class TestInitUpdate(CliRuntimeHarness):
    _CANONICAL_RULES_PROVIDER_ASSET_MAP: ClassVar[dict[str, object]] = {
        "spec-dock/docs/rules/root/artifacts.md": ("src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md"),
        "spec-dock/docs/rules/initiative/artifacts.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md"
        ),
        "spec-dock/docs/rules/initiative/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md"
        ),
        "spec-dock/docs/rules/initiative/epics.md": ("src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md"),
        "spec-dock/docs/rules/epic/artifacts.md": ("src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md"),
        "spec-dock/docs/rules/epic/discussions.md": ("src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md"),
        "spec-dock/docs/rules/epic/issues.md": ("src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md"),
        "spec-dock/docs/rules/issue/artifacts.md": ("src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md"),
        "spec-dock/docs/rules/issue/discussions.md": ("src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"),
    }

    @staticmethod
    def _is_generated_python_cache_path(path: Path | str) -> bool:
        normalized_path = Path(path)
        return "__pycache__" in normalized_path.parts or normalized_path.suffix in {".pyc", ".pyo"}

    def _runtime_inventory(self, root: Path) -> dict[str, Path]:
        return {
            path.relative_to(root).as_posix(): path
            for path in root.rglob("*")
            if path.is_file() and not self._is_generated_python_cache_path(path.relative_to(root))
        }

    # S40B replaces the historical mirror inventory with the physical current
    # catalog. Keep this assertion focused on retained provider-owned files;
    # stale consumer-only files are handled by the later classifier steps.
    _DOGFOODING_MIRROR_PROVIDER_ASSET_MAP: ClassVar[dict[str, object]] = {
        "spec-dock/.gitignore": "src/spec_dock/assets/spec_dock/.gitignore",
        "spec-dock/templates/README.md": "src/spec_dock/assets/spec_dock/templates/README.md",
        "spec-dock/scripts/README.md": "src/spec_dock/assets/spec_dock/scripts/README.md",
        "spec-dock/docs/README.md": "src/spec_dock/assets/spec_dock/docs/README.md",
        "spec-dock/docs/guide.md": "src/spec_dock/assets/spec_dock/docs/guide.md",
        "spec-dock/docs/migration.md": "src/spec_dock/assets/spec_dock/docs/migration.md",
        "spec-dock/docs/reference_deps.md": "src/spec_dock/assets/spec_dock/docs/reference_deps.md",
        "spec-dock/docs/reference_github.md": "src/spec_dock/assets/spec_dock/docs/reference_github.md",
        "spec-dock/docs/reference_naming.md": "src/spec_dock/assets/spec_dock/docs/reference_naming.md",
        "spec-dock/docs/reference_sync.md": "src/spec_dock/assets/spec_dock/docs/reference_sync.md",
        "spec-dock/docs/reference_worktree.md": "src/spec_dock/assets/spec_dock/docs/reference_worktree.md",
        "spec-dock/docs/authoring/artifacts.md": "src/spec_dock/assets/spec_dock/docs/authoring/artifacts.md",
        "spec-dock/docs/authoring/design.md": "src/spec_dock/assets/spec_dock/docs/authoring/design.md",
        "spec-dock/docs/authoring/historical.md": "src/spec_dock/assets/spec_dock/docs/authoring/historical.md",
        "spec-dock/docs/authoring/issue-plan.md": "src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md",
        "spec-dock/docs/authoring/overview.md": "src/spec_dock/assets/spec_dock/docs/authoring/overview.md",
        "spec-dock/docs/authoring/report.md": "src/spec_dock/assets/spec_dock/docs/authoring/report.md",
        "spec-dock/docs/authoring/requirement.md": "src/spec_dock/assets/spec_dock/docs/authoring/requirement.md",
        "spec-dock/docs/authoring/scope-layering.md": "src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md",
        "spec-dock/docs/rules/initiative/artifacts.md": "src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md",
        "spec-dock/docs/rules/initiative/discussions.md": "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md",
        "spec-dock/docs/rules/initiative/epics.md": "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md",
        "spec-dock/docs/rules/epic/artifacts.md": "src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md",
        "spec-dock/docs/rules/epic/discussions.md": "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md",
        "spec-dock/docs/rules/epic/issues.md": "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md",
        "spec-dock/docs/rules/issue/artifacts.md": "src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md",
        "spec-dock/docs/rules/issue/discussions.md": "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md",
        "spec-dock/docs/rules/root/artifacts.md": "src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md",
        ".agents/skills/spec-dock/SKILL.md": "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/SKILL.md": "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md",
        ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml": "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
        ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py": "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
        ".github/workflows/ci.yml": "src/spec_dock/assets/install_root/.github/workflows/ci.yml",
    }
    _DOGFOODING_ACTIVE_NONE_REPORT_PROVIDER_ASSET_MAP: ClassVar[dict[str, object]] = {
        "spec-dock/system/active-none/initiative/report.md": (
            "src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md"
        ),
        "spec-dock/system/active-none/epic/report.md": (
            "src/spec_dock/assets/spec_dock/system/active-none/epic/report.md"
        ),
        "spec-dock/system/active-none/issue/report.md": (
            "src/spec_dock/assets/spec_dock/system/active-none/issue/report.md"
        ),
    }

    _ISSUE_68_INSTALL_ROOT = Path("src/spec_dock/assets/install_root")
    _ISSUE_69_WHEELHOUSE_RELATIVE = Path("tests/fixtures/wheelhouse")
    _ISSUE_69_BUILD_BACKEND_REQUIREMENTS = (
        "build==1.2.2",
        "packaging==24.2",
        "pyproject_hooks==1.2.0",
        "setuptools==75.8.0",
        "tomli==2.2.1",
        "wheel==0.45.1",
    )
    _ISSUE_69_WHEELHOUSE_FILENAMES = (
        "build-1.2.2-py3-none-any.whl",
        "packaging-24.2-py3-none-any.whl",
        "pyproject_hooks-1.2.0-py3-none-any.whl",
        "setuptools-75.8.0-py3-none-any.whl",
        "tomli-2.2.1-py3-none-any.whl",
        "wheel-0.45.1-py3-none-any.whl",
    )
    _WORKBENCH_TEMPLATE_README_PATHS = (
        "README.md",
        "root/.workbench/README.md",
        "initiative/.workbench/README.md",
        "epic/.workbench/README.md",
        "issue/.workbench/README.md",
    )
    _WORKBENCH_README_PATHS = (
        "root/.workbench/README.md",
        "initiative/.workbench/README.md",
        "epic/.workbench/README.md",
        "issue/.workbench/README.md",
    )
    _ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS = (
        "spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md",
        "spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md",
        "spec_dock/assets/spec_dock/scripts/authoring-pack/README.md",
        "spec_dock/assets/spec_dock/scripts/spec-dock-close-smoke.sh",
        "spec_dock/assets/github/workflows/spec-dock-close.yml",
        "spec_dock/assets/spec_dock/templates/initiative/current/stale.md",
        "spec_dock/assets/spec_dock/templates/initiative/completed/stale.md",
        "spec_dock/assets/spec_dock/templates/adr.md",
        "spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
        "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
        "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
        "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
        "spec_dock/assets/spec_dock/templates/issue/legacy/README.md",
        "spec_dock/assets/spec_dock/templates/design.md",
        "spec_dock/assets/spec_dock/templates/plan.md",
        "spec_dock/assets/spec_dock/templates/report.md",
        "spec_dock/assets/spec_dock/templates/requirement.md",
    )
    _ISSUE_69_SETUP_SEED_STALE_FIXTURES_ENV = "SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES"
    _ISSUE_69_SETUP_PRE_PRUNE_SNAPSHOT_ENV = "SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT"

    def _assert_canonical_rules_files_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[3]
        for installed_rel_path, asset_rel_path in self._CANONICAL_RULES_PROVIDER_ASSET_MAP.items():
            installed_path = installed_base / installed_rel_path
            asset_path = repo_root / asset_rel_path
            assert installed_path.is_file(), f"missing canonical rules file: {installed_path}"
            assert asset_path.is_file(), f"missing canonical rules asset: {asset_path}"
            assert installed_path.read_text(encoding="utf-8") == asset_path.read_text(encoding="utf-8"), (
                f"canonical rules file diverged from provider asset: {installed_rel_path}"
            )

    def _assert_checked_in_dogfooding_mirror_docs_match_provider_assets(self, repo_root: Path) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_MIRROR_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            assert mirror_path.is_file(), f"missing checked-in dogfooding mirror file: {mirror_path}"
            assert asset_path.is_file(), f"missing provider asset file: {asset_path}"
            assert mirror_path.read_bytes() == asset_path.read_bytes(), (
                f"checked-in dogfooding mirror file diverged from provider asset: {mirror_rel_path}"
            )

    def _assert_checked_in_dogfooding_active_none_reports_match_provider_assets(
        self,
        repo_root: Path,
    ) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_ACTIVE_NONE_REPORT_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            assert mirror_path.is_file(), f"missing checked-in active-none report mirror: {mirror_path}"
            assert asset_path.is_file(), f"missing provider active-none report asset: {asset_path}"
            assert mirror_path.read_text(encoding="utf-8") == asset_path.read_text(encoding="utf-8"), (
                f"checked-in active-none report mirror diverged from provider asset: {mirror_rel_path}"
            )

    def _assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(self, repo_root: Path) -> None:
        provider_root = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "spec_dock_runtime"
        mirror_root = repo_root / "spec-dock" / "scripts" / "spec_dock_runtime"
        assert provider_root.is_dir(), f"missing provider runtime asset directory: {provider_root}"
        assert mirror_root.is_dir(), f"missing checked-in dogfooding runtime mirror directory: {mirror_root}"
        provider_inventory = self._runtime_inventory(provider_root)
        mirror_inventory = self._runtime_inventory(mirror_root)

        provider_paths = set(provider_inventory)
        mirror_paths = set(mirror_inventory)
        assert mirror_paths == provider_paths, (
            "checked-in dogfooding runtime mirror inventory diverged from provider assets: "
            f"missing={sorted(provider_paths - mirror_paths)} extra={sorted(mirror_paths - provider_paths)}"
        )

        for rel_path in sorted(provider_paths):
            mirror_path = mirror_inventory[rel_path]
            asset_path = provider_inventory[rel_path]
            assert mirror_path.read_bytes() == asset_path.read_bytes(), (
                f"checked-in dogfooding runtime mirror file diverged from provider asset: {rel_path}"
            )

    def _assert_installed_templates_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[3]
        mirror_root = installed_base / "spec-dock" / "templates"
        asset_root = repo_root / "src/spec_dock/assets/spec_dock/templates"

        mirror_entries = sorted(path.relative_to(mirror_root).as_posix() for path in mirror_root.rglob("*"))
        asset_entries = sorted(path.relative_to(asset_root).as_posix() for path in asset_root.rglob("*"))
        assert mirror_entries == asset_entries, "installed templates tree diverged from provider assets"

        for rel_path in asset_entries:
            mirror_path = mirror_root / rel_path
            asset_path = asset_root / rel_path
            assert mirror_path.is_dir() == asset_path.is_dir(), (
                f"installed templates entry kind diverged from provider asset: {rel_path}"
            )
            assert mirror_path.is_file() == asset_path.is_file(), (
                f"installed templates entry kind diverged from provider asset: {rel_path}"
            )
            if asset_path.is_file():
                assert mirror_path.read_text(encoding="utf-8") == asset_path.read_text(encoding="utf-8"), (
                    f"installed template diverged from provider asset: {rel_path}"
                )

    def _issue_71_extract_markdown_section_by_heading_prefix(
        self,
        *,
        markdown_text: str,
        heading_prefix: str,
        source_label: str,
    ) -> str:
        lines = markdown_text.splitlines()
        start_index = None
        heading_marker = f"## {heading_prefix}"
        for index, line in enumerate(lines):
            if line.startswith(heading_marker):
                start_index = index
                break
        assert start_index is not None, f"issue-71 expected heading prefix missing in {source_label}: {heading_prefix}"

        assert start_index is not None
        end_index = len(lines)
        for index in range(start_index + 1, len(lines)):
            if lines[index].startswith("## "):
                end_index = index
                break
        return "\n".join(lines[start_index:end_index]) + "\n"

    def _issue_69_run_subprocess(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        result = subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            "issue-69 command failed:\n"
            f"command: {' '.join(args)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    def _issue_69_run_subprocess_capture(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        result = subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            "issue-69 command failed:\n"
            f"command: {' '.join(args)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
        return result

    def _issue_69_resolve_wheelhouse(self, repo_root: Path) -> Path:
        wheelhouse = repo_root / self._ISSUE_69_WHEELHOUSE_RELATIVE
        assert wheelhouse.is_dir(), f"issue-69 local wheelhouse is missing: {wheelhouse}"
        missing_wheels = [
            wheel_name for wheel_name in self._ISSUE_69_WHEELHOUSE_FILENAMES if not (wheelhouse / wheel_name).is_file()
        ]
        assert missing_wheels == [], f"issue-69 local wheelhouse is missing pinned backend wheels: {missing_wheels}"
        return wheelhouse

    def _issue_69_venv_python(self, venv_dir: Path) -> Path:
        if os.name == "nt":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"

    def _issue_69_venv_spec_dock(self, venv_python: Path) -> Path:
        if os.name == "nt":
            spec_dock_exe = venv_python.parent / "spec-dock.exe"
            if spec_dock_exe.is_file():
                return spec_dock_exe
            spec_dock_cmd = venv_python.parent / "spec-dock.cmd"
            if spec_dock_cmd.is_file():
                return spec_dock_cmd
            return spec_dock_cmd
        return venv_python.parent / "spec-dock"

    def _issue_69_env_root(self, venv_python: Path) -> Path:
        return venv_python.parent.parent

    def _issue_69_site_packages_dir(self, env_root: Path) -> Path:
        if os.name == "nt":
            return env_root / "Lib" / "site-packages"
        return env_root / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"

    def _issue_69_runtime_env_without_checkout_fallback(self) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        return env

    def _issue_69_install_target_packages(
        self,
        *,
        python_executable: Path,
        target_dir: Path,
        requirements: list[str],
        wheelhouse: Path | None = None,
    ) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        pip_probe = subprocess.run(
            [str(python_executable), "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if pip_probe.returncode == 0:
            command = [
                str(python_executable),
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--target",
                str(target_dir),
            ]
        else:
            uv_executable = shutil.which("uv")
            assert uv_executable is not None, (
                "issue-69 package install requires either pip in the current Python "
                f"or uv on PATH; pip stderr:\n{pip_probe.stderr}"
            )
            command = [
                uv_executable,
                "pip",
                "install",
                "--python",
                str(python_executable),
                "--target",
                str(target_dir),
            ]
        if wheelhouse is not None:
            command.extend([
                "--no-index",
                "--find-links",
                str(wheelhouse),
            ])
        command.extend(requirements)
        self._issue_69_run_subprocess(command)

    def _issue_69_install_build_backend_packages(
        self,
        *,
        python_executable: Path,
        requirements: list[str],
        wheelhouse: Path | None = None,
    ) -> None:
        command = [
            str(python_executable),
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--upgrade",
        ]
        if wheelhouse is not None:
            command.extend([
                "--no-index",
                "--find-links",
                str(wheelhouse),
            ])
        command.extend(requirements)
        self._issue_69_run_subprocess(command)

    def _issue_69_create_fallback_runtime_env(self, env_root: Path) -> Path:
        assert os.name != "nt", "issue-69 fallback runtime env is only implemented for POSIX"
        bin_dir = env_root / "bin"
        site_packages_dir = self._issue_69_site_packages_dir(env_root)
        bin_dir.mkdir(parents=True, exist_ok=True)
        site_packages_dir.mkdir(parents=True, exist_ok=True)

        python_wrapper = self._issue_69_venv_python(env_root)
        python_wrapper.write_text(
            "#!/bin/sh\n"
            f"PYTHONPATH={shlex.quote(str(site_packages_dir))}${{PYTHONPATH:+:${{PYTHONPATH}}}} "
            f'exec {shlex.quote(sys.executable)} "$@"\n',
            encoding="utf-8",
        )
        python_wrapper.chmod(0o755)

        spec_dock_wrapper = self._issue_69_venv_spec_dock(python_wrapper)
        spec_dock_wrapper.write_text(
            f'#!/bin/sh\nexec {shlex.quote(str(python_wrapper))} -m spec_dock.cli "$@"\n',
            encoding="utf-8",
        )
        spec_dock_wrapper.chmod(0o755)
        return python_wrapper

    def _issue_69_ensure_spec_dock_wrapper(self, venv_python: Path) -> Path:
        spec_dock_wrapper = self._issue_69_venv_spec_dock(venv_python)
        if spec_dock_wrapper.is_file():
            return spec_dock_wrapper
        if os.name == "nt":
            spec_dock_wrapper.write_text(
                f'@echo off\r\n"{venv_python}" -m spec_dock.cli %*\r\n',
                encoding="utf-8",
            )
        else:
            spec_dock_wrapper.write_text(
                f'#!/bin/sh\nexec {shlex.quote(str(venv_python))} -m spec_dock.cli "$@"\n',
                encoding="utf-8",
            )
            spec_dock_wrapper.chmod(0o755)
        return spec_dock_wrapper

    def _issue_69_build_artifacts_with_local_wheelhouse(
        self,
        *,
        repo_root: Path,
        build_context: Path,
        wheel_dir: Path,
        sdist_dir: Path,
        build_env: dict[str, str] | None = None,
    ) -> tuple[Path, Path, Path]:
        wheelhouse = self._issue_69_resolve_wheelhouse(repo_root)
        venv_dir = build_context.parent / "build-venv"
        fallback_env_dir = build_context.parent / "build-wrapper-env"
        dist_dir = build_context.parent / "dist"
        native_build_venv = False
        venv_result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        if venv_result.returncode == 0:
            venv_python = self._issue_69_venv_python(venv_dir)
            assert venv_python.is_file(), f"issue-69 expected venv python executable at: {venv_python}"
            pip_result = subprocess.run(
                [str(venv_python), "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            if pip_result.returncode != 0:
                venv_python = self._issue_69_create_fallback_runtime_env(fallback_env_dir)
            else:
                native_build_venv = True
        else:
            venv_python = self._issue_69_create_fallback_runtime_env(fallback_env_dir)

        backend_requirements = list(self._ISSUE_69_BUILD_BACKEND_REQUIREMENTS)
        if native_build_venv:
            self._issue_69_install_build_backend_packages(
                python_executable=venv_python,
                requirements=backend_requirements,
                wheelhouse=wheelhouse,
            )
        else:
            self._issue_69_install_target_packages(
                python_executable=venv_python,
                target_dir=self._issue_69_site_packages_dir(self._issue_69_env_root(venv_python)),
                requirements=backend_requirements,
                wheelhouse=wheelhouse,
            )

        self._issue_69_run_subprocess(
            [
                str(venv_python),
                "-m",
                "build",
                "--wheel",
                "--sdist",
                "--no-isolation",
                "--outdir",
                str(dist_dir),
            ],
            cwd=build_context,
            env=build_env,
        )

        wheel_paths = sorted(dist_dir.glob("*.whl"))
        sdist_paths = sorted(dist_dir.glob("*.tar.gz"))
        assert len(wheel_paths) == 1, f"issue-69 expected one wheel artifact, got: {wheel_paths}"
        assert len(sdist_paths) == 1, f"issue-69 expected one sdist artifact, got: {sdist_paths}"

        wheel_dir.mkdir(parents=True, exist_ok=True)
        sdist_dir.mkdir(parents=True, exist_ok=True)
        wheel_path = wheel_dir / wheel_paths[0].name
        sdist_path = sdist_dir / sdist_paths[0].name
        shutil.copy2(wheel_paths[0], wheel_path)
        shutil.copy2(sdist_paths[0], sdist_path)
        return wheel_path, sdist_path, venv_python

    def _issue_69_path_is_within(self, path: Path, root: Path) -> bool:
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return False
        return True

    def _issue_69_collect_isolated_installed_runtime_snapshot(
        self,
        *,
        venv_python: Path,
        repo_root: Path,
        cwd: Path,
    ) -> dict[str, object]:
        repo_root_literal = json.dumps(str(repo_root.resolve()))
        script = (
            "import json\n"
            "import sys\n"
            "from pathlib import Path\n"
            "import spec_dock\n"
            "import importlib.resources as resources\n"
            f"repo_root = Path({repo_root_literal})\n"
            "def _is_under_repo(path_text: str) -> bool:\n"
            "    if not path_text:\n"
            "        return False\n"
            "    try:\n"
            "        Path(path_text).resolve().relative_to(repo_root)\n"
            "        return True\n"
            "    except Exception:\n"
            "        return False\n"
            "resolved_assets_dir = Path(str(resources.files('spec_dock').joinpath('assets'))).resolve()\n"
            "install_root = resolved_assets_dir / 'install_root'\n"
            "inventory = sorted(\n"
            '    f"spec_dock/assets/{candidate.relative_to(resolved_assets_dir).as_posix()}"\n'
            "    for candidate in install_root.rglob('*')\n"
            "    if candidate.is_file()\n"
            ")\n"
            "payload = {\n"
            "    'spec_dock_file': str(Path(spec_dock.__file__).resolve()),\n"
            "    'assets_dir': str(resolved_assets_dir),\n"
            "    'sys_path_has_repo_root': any(_is_under_repo(path_text) for path_text in sys.path if path_text),\n"
            "    'inventory': inventory,\n"
            "}\n"
            "print(json.dumps(payload))\n"
        )
        result = self._issue_69_run_subprocess_capture(
            [str(venv_python), "-c", script],
            cwd=cwd,
            env=self._issue_69_runtime_env_without_checkout_fallback(),
        )
        output_lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert output_lines, "issue-69 runtime snapshot command produced no JSON output"
        payload = json.loads(output_lines[-1])
        assert isinstance(payload, dict), "issue-69 runtime snapshot must be a JSON object"
        return payload

    def _issue_69_assert_runtime_snapshot_uses_installed_package(
        self,
        *,
        snapshot: dict[str, object],
        repo_root: Path,
    ) -> None:
        spec_dock_file = Path(str(snapshot.get("spec_dock_file", ""))).resolve()
        assets_dir = Path(str(snapshot.get("assets_dir", ""))).resolve()
        assert "site-packages" in spec_dock_file.as_posix(), (
            f"issue-69 expected installed package module path, got: {spec_dock_file}"
        )
        assert "site-packages" in assets_dir.as_posix(), (
            f"issue-69 expected installed package assets path, got: {assets_dir}"
        )
        assert not self._issue_69_path_is_within(spec_dock_file, repo_root), (
            f"issue-69 runtime imported spec_dock from checkout path: {spec_dock_file}"
        )
        assert not self._issue_69_path_is_within(assets_dir, repo_root), (
            f"issue-69 runtime loaded assets from checkout path: {assets_dir}"
        )
        assert not bool(snapshot.get("sys_path_has_repo_root")), (
            "issue-69 runtime sys.path unexpectedly includes repository checkout path"
        )

    def _issue_69_collect_wheel_file_inventory(self, wheel_path: Path) -> set[str]:
        with zipfile.ZipFile(wheel_path) as wheel_zip:
            return {member for member in wheel_zip.namelist() if not member.endswith("/")}

    def _collect_source_template_readme_payloads(self, repo_root: Path) -> dict[str, bytes]:
        template_root = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "templates"
        return {
            candidate.relative_to(template_root).as_posix(): candidate.read_bytes()
            for candidate in template_root.rglob("README.md")
            if candidate.is_file()
        }

    def _collect_wheel_template_readme_payloads(self, wheel_path: Path) -> dict[str, bytes]:
        template_prefix = "spec_dock/assets/spec_dock/templates/"
        with zipfile.ZipFile(wheel_path) as wheel_zip:
            members = [
                member
                for member in wheel_zip.infolist()
                if not member.is_dir()
                and member.filename.startswith(template_prefix)
                and Path(member.filename).name == "README.md"
            ]
            normalized_paths = [member.filename.removeprefix(template_prefix) for member in members]
            assert len(normalized_paths) == len(set(normalized_paths)), (
                f"wheel contains duplicate template README paths: {normalized_paths}"
            )
            return {
                normalized_path: wheel_zip.read(member)
                for member, normalized_path in zip(members, normalized_paths, strict=True)
            }

    def _collect_sdist_template_readme_payloads(self, sdist_path: Path) -> dict[str, bytes]:
        template_prefix = "src/spec_dock/assets/spec_dock/templates/"
        with tarfile.open(sdist_path, "r:gz") as sdist_tar:
            members = [member for member in sdist_tar.getmembers() if member.isfile()]
            archive_roots = {member.name.partition("/")[0] for member in members if "/" in member.name}
            assert len(archive_roots) == 1, f"sdist must have one archive root: {sorted(archive_roots)}"
            payloads: dict[str, bytes] = {}
            normalized_paths: list[str] = []
            for member in members:
                _, separator, relative_member = member.name.partition("/")
                if (
                    not separator
                    or not relative_member.startswith(template_prefix)
                    or Path(relative_member).name != "README.md"
                ):
                    continue
                normalized_path = relative_member.removeprefix(template_prefix)
                normalized_paths.append(normalized_path)
                extracted = sdist_tar.extractfile(member)
                assert extracted is not None, f"sdist README could not be read: {member.name}"
                payloads[normalized_path] = extracted.read()
            assert len(normalized_paths) == len(set(normalized_paths)), (
                f"sdist contains duplicate template README paths: {normalized_paths}"
            )
            return payloads

    def _collect_isolated_installed_template_readme_snapshot(
        self,
        *,
        venv_python: Path,
        repo_root: Path,
        cwd: Path,
    ) -> dict[str, object]:
        repo_root_literal = json.dumps(str(repo_root.resolve()))
        script = (
            "import importlib.resources as resources\n"
            "import json\n"
            "import sys\n"
            "from pathlib import Path\n"
            "import spec_dock\n"
            f"repo_root = Path({repo_root_literal})\n"
            "def _is_under_repo(path_text: str) -> bool:\n"
            "    if not path_text:\n"
            "        return False\n"
            "    try:\n"
            "        Path(path_text).resolve().relative_to(repo_root)\n"
            "        return True\n"
            "    except Exception:\n"
            "        return False\n"
            "def _collect(root, parts=()):\n"
            "    payloads = {}\n"
            "    for child in root.iterdir():\n"
            "        child_parts = parts + (child.name,)\n"
            "        if child.is_dir():\n"
            "            payloads.update(_collect(child, child_parts))\n"
            "        elif child.is_file() and child.name == 'README.md':\n"
            "            payloads['/'.join(child_parts)] = child.read_bytes().hex()\n"
            "    return payloads\n"
            "package_root = resources.files('spec_dock')\n"
            "template_root = package_root.joinpath('assets', 'spec_dock', 'templates')\n"
            "payload = {\n"
            "    'spec_dock_file': str(Path(spec_dock.__file__).resolve()),\n"
            "    'assets_dir': str(Path(str(package_root.joinpath('assets'))).resolve()),\n"
            "    'sys_path_has_repo_root': any(_is_under_repo(path_text) for path_text in sys.path if path_text),\n"
            "    'template_readmes': _collect(template_root),\n"
            "}\n"
            "print(json.dumps(payload))\n"
        )
        result = self._issue_69_run_subprocess_capture(
            [str(venv_python), "-c", script],
            cwd=cwd,
            env=self._issue_69_runtime_env_without_checkout_fallback(),
        )
        output_lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert output_lines, "installed template README snapshot produced no JSON output"
        snapshot = json.loads(output_lines[-1])
        assert isinstance(snapshot, dict), "installed template README snapshot must be a JSON object"
        return snapshot

    def _issue_69_prepare_build_context(self, repo_root: Path, build_context: Path) -> None:
        build_context.mkdir(parents=True, exist_ok=True)
        for filename in ("pyproject.toml", "README.md", "setup.py"):
            shutil.copy2(repo_root / filename, build_context / filename)
        shutil.copytree(
            repo_root / "src",
            build_context / "src",
        )

    def _issue_69_collect_source_install_root_inventory(self, repo_root: Path) -> set[str]:
        source_root = repo_root / "src"
        install_root = source_root / "spec_dock" / "assets" / "install_root"
        return {
            candidate.relative_to(source_root).as_posix()
            for candidate in install_root.rglob("*")
            if candidate.is_file() and not self._is_generated_python_cache_path(candidate)
        }

    def _issue_69_collect_wheel_install_root_inventory(self, wheel_path: Path) -> set[str]:
        with zipfile.ZipFile(wheel_path) as wheel_zip:
            return {
                member
                for member in wheel_zip.namelist()
                if member.startswith("spec_dock/assets/install_root/")
                and not member.endswith("/")
                and not self._is_generated_python_cache_path(member)
            }

    def _issue_69_collect_sdist_install_root_inventory(self, sdist_path: Path) -> set[str]:
        sdist_inventory: set[str] = set()
        with tarfile.open(sdist_path, "r:gz") as sdist_tar:
            for member in sdist_tar.getmembers():
                if not member.isfile():
                    continue
                _, sep, relative_member = member.name.partition("/")
                if not sep:
                    continue
                if not relative_member.startswith("src/"):
                    continue
                artifact_relative = relative_member.removeprefix("src/")
                if artifact_relative.startswith(
                    "spec_dock/assets/install_root/"
                ) and not self._is_generated_python_cache_path(artifact_relative):
                    sdist_inventory.add(artifact_relative)
        return sdist_inventory

    def _issue_69_collect_installed_install_root_inventory(self, installed_root: Path) -> set[str]:
        package_root = installed_root / "spec_dock"
        install_root = package_root / "assets" / "install_root"
        assert install_root.is_dir(), f"issue-69 installed package is missing install_root assets: {install_root}"
        return {
            f"spec_dock/{candidate.relative_to(package_root).as_posix()}"
            for candidate in install_root.rglob("*")
            if candidate.is_file() and not self._is_generated_python_cache_path(candidate)
        }

    def _issue_69_collect_install_root_artifact_surfaces(self) -> dict[str, set[str]]:
        repo_root = Path(__file__).resolve().parents[3]
        source_inventory = self._issue_69_collect_source_install_root_inventory(repo_root)

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            installed_dir = temp_root / "installed-package"
            wheelhouse = self._issue_69_resolve_wheelhouse(repo_root)

            self._issue_69_prepare_build_context(repo_root, build_context)
            installed_dir.mkdir(parents=True, exist_ok=True)

            wheel_path, sdist_path, venv_python = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )
            wheel_name_part, wheel_version_part, _ = wheel_path.name.split("-", 2)
            wheel_requirement = f"{wheel_name_part.replace('_', '-')}=={wheel_version_part}"

            self._issue_69_run_subprocess([
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-cache-dir",
                "--no-deps",
                "--find-links",
                str(wheel_dir),
                "--find-links",
                str(wheelhouse),
                "--target",
                str(installed_dir),
                wheel_requirement,
            ])

            wheel_inventory = self._issue_69_collect_wheel_install_root_inventory(wheel_path)
            sdist_inventory = self._issue_69_collect_sdist_install_root_inventory(sdist_path)
            installed_inventory = self._issue_69_collect_installed_install_root_inventory(installed_dir)

        return {
            "source": source_inventory,
            "wheel": wheel_inventory,
            "sdist": sdist_inventory,
            "installed": installed_inventory,
        }

    def test_init_gitignore_ignores_exact_workbench_directories_at_supported_scopes(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])

            scope_directories = (
                target / "spec-dock",
                target / "spec-dock" / "initiatives" / "init-00001-example",
                target / "spec-dock" / "initiatives" / "init-00001-example" / "epics" / "epic-00001-example",
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-example"
                / "epics"
                / "epic-00001-example"
                / "issues"
                / "iss-00001-example",
            )
            for scope_directory in scope_directories:
                workbench_probe = scope_directory / ".workbench" / "probe"
                workbench_probe.parent.mkdir(parents=True, exist_ok=True)
                workbench_probe.write_text("scratch\n", encoding="utf-8")
                near_name_probe = scope_directory / ".workbench-notes" / "probe"
                near_name_probe.parent.mkdir(parents=True, exist_ok=True)
                near_name_probe.write_text("ordinary\n", encoding="utf-8")

                workbench_result = self._run_git(
                    target,
                    ["check-ignore", "--no-index", workbench_probe.relative_to(target).as_posix()],
                    check=False,
                )
                assert workbench_result.returncode == 0, workbench_result.stdout + workbench_result.stderr

                near_name_result = self._run_git(
                    target,
                    ["check-ignore", "--no-index", near_name_probe.relative_to(target).as_posix()],
                    check=False,
                )
                assert near_name_result.returncode == 1, near_name_result.stdout + near_name_result.stderr

    def test_workbench_readme_assets_are_byte_identical_and_complete(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        templates_dir = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "templates"
        assets = tuple(
            templates_dir / scope / ".workbench" / "README.md" for scope in ("root", "initiative", "epic", "issue")
        )

        payloads = [asset.read_bytes() for asset in assets]

        assert len(set(payloads)) == 1
        payload = payloads[0]
        assert payload.startswith(b"# Workbench\n")
        assert payload.endswith(b"\n")
        assert not payload.endswith(b"\n\n")
        assert b"\r" not in payload
        text = payload.decode("utf-8")
        for fragment in (
            "worktree-local",
            "non-canonical",
            "Git ignore は security boundary",
            "./spec-dock/scripts/spec-dock artifact import file ...",
            "./spec-dock/scripts/spec-dock workbench copy --scope <full-id> --to <linked-worktree>",
            "canonical adoption",
            "automatic hook",
        ):
            assert fragment in text

    def test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            legacy_dir = target / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            marker_path = legacy_dir / "legacy-marker.txt"
            marker_path.write_text("legacy data\n", encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["init", str(target)])

            assert exit_code == 0
            assert (target / "spec-dock").is_dir()
            assert legacy_dir.is_dir()
            assert marker_path.read_text(encoding="utf-8") == "legacy data\n"
            assert "Please rename it before installing" not in stderr.getvalue()

    def test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            current_dir = target / "spec-dock"
            legacy_dir = target / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            marker_path = legacy_dir / "legacy-marker.txt"
            marker_path.write_text("legacy data\n", encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["update", str(target)])

            assert exit_code == 0
            assert current_dir.is_dir()
            assert legacy_dir.is_dir()
            assert marker_path.read_text(encoding="utf-8") == "legacy data\n"
            assert "Please rename it" not in stderr.getvalue()
            assert "mv .spec-dock spec-dock" not in stderr.getvalue()

    @pytest.mark.parametrize("install_command", ["init", "update"])
    def test_init_and_update_ship_root_artifact_rules_and_import_links_them_safely(
        self,
        install_command: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            installed_rules = target / "spec-dock" / "docs" / "rules" / "root" / "artifacts.md"
            if install_command == "update":
                assert main(["update", str(target)]) == 0

            repo_root = Path(__file__).resolve().parents[3]
            provider_rules = repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "docs" / "rules"
            provider_rules = provider_rules / "root" / "artifacts.md"
            assert provider_rules.is_file() and not provider_rules.is_symlink()
            assert installed_rules.is_file() and not installed_rules.is_symlink()
            assert installed_rules.read_bytes() == provider_rules.read_bytes()

            rules_text = installed_rules.read_text(encoding="utf-8")
            for expected_fragment in (
                "generic Artifact",
                "opaque evidence",
                "canonical=false",
                "本文の正本を node ごとに複製しません",
            ):
                assert expected_fragment in rules_text

            source = target / "root-evidence.bin"
            source.write_bytes(b"opaque-root-evidence")
            result = self._run_runtime_capture(
                target,
                ["artifact", "import", "file", "--root", "--file", source.name, "--json"],
            )
            assert result.returncode == 0, f"root import stdout:\n{result.stdout}\nroot import stderr:\n{result.stderr}"

            rules_link = target / "spec-dock" / "artifacts" / "rules.md"
            assert rules_link.is_symlink()
            assert rules_link.readlink() == Path("../docs/rules/root/artifacts.md")
            assert rules_link.resolve() == installed_rules.resolve()
            assert rules_link.read_bytes() == provider_rules.read_bytes()

    def test_pyproject_excludes_deleted_wrapper_era_assets_from_package_data(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

        for package_data_pattern in _ISS_00031_EXCLUDE_PATTERNS:
            assert f'"{package_data_pattern}"' in pyproject_text, (
                f"missing exclude-package-data guard for stale build artifact: {package_data_pattern}"
            )

    def test_issue_69_native_build_venv_installs_backend_requirements_in_place(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        build_context = tmp_path / "build-context"
        wheel_dir = tmp_path / "wheel"
        sdist_dir = tmp_path / "sdist"
        wheelhouse = tmp_path / "wheelhouse"
        build_context.mkdir()
        wheelhouse.mkdir()
        commands: list[list[str]] = []
        native_python = tmp_path / "build-venv" / "bin" / "python"

        def fake_run(args, **kwargs):
            command = [str(argument) for argument in args]
            commands.append(command)
            if command[:3] == [sys.executable, "-m", "venv"]:
                native_python.parent.mkdir(parents=True, exist_ok=True)
                native_python.write_text("native python placeholder\n", encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            if command == [str(native_python), "-m", "pip", "--version"]:
                return subprocess.CompletedProcess(command, 0, stdout="pip 25\n", stderr="")
            raise AssertionError(f"unexpected subprocess probe: {command}")

        def fake_run_subprocess(args, *, cwd=None, env=None):
            command = [str(argument) for argument in args]
            commands.append(command)
            if command[1:3] == ["-m", "build"]:
                dist_dir = Path(command[command.index("--outdir") + 1])
                dist_dir.mkdir(parents=True, exist_ok=True)
                (dist_dir / "spec_dock-0.0.0-py3-none-any.whl").write_bytes(b"wheel")
                (dist_dir / "spec_dock-0.0.0.tar.gz").write_bytes(b"sdist")

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(self, "_issue_69_resolve_wheelhouse", lambda repo_root: wheelhouse)
        monkeypatch.setattr(self, "_issue_69_run_subprocess", fake_run_subprocess)

        self._issue_69_build_artifacts_with_local_wheelhouse(
            repo_root=tmp_path / "repo",
            build_context=build_context,
            wheel_dir=wheel_dir,
            sdist_dir=sdist_dir,
        )

        install_commands = [
            command for command in commands if command[:4] == [str(native_python), "-m", "pip", "install"]
        ]
        assert install_commands == [
            [
                str(native_python),
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--upgrade",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                *self._ISSUE_69_BUILD_BACKEND_REQUIREMENTS,
            ]
        ]
        assert "--target" not in install_commands[0]

    def test_issue_69_pip_unavailable_fallback_keeps_target_install_semantics(
        self,
        monkeypatch,
        tmp_path: Path,
    ) -> None:
        python_executable = tmp_path / "python"
        target_dir = tmp_path / "target"
        wheelhouse = tmp_path / "wheelhouse"
        wheelhouse.mkdir()
        captured: list[list[str]] = []

        def pip_probe(args, **kwargs):
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="pip unavailable")

        def capture_install(args, *, cwd=None, env=None):
            captured.append([str(argument) for argument in args])

        monkeypatch.setattr(subprocess, "run", pip_probe)
        monkeypatch.setattr(shutil, "which", lambda executable: "/fake/uv")
        monkeypatch.setattr(self, "_issue_69_run_subprocess", capture_install)

        self._issue_69_install_target_packages(
            python_executable=python_executable,
            target_dir=target_dir,
            requirements=["build==1.2.2"],
            wheelhouse=wheelhouse,
        )

        assert captured == [
            [
                "/fake/uv",
                "pip",
                "install",
                "--python",
                str(python_executable),
                "--target",
                str(target_dir),
                "--no-index",
                "--find-links",
                str(wheelhouse),
                "build==1.2.2",
            ]
        ]

    def test_built_wheel_excludes_deleted_wrapper_era_assets_from_stale_build_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"

            build_context.mkdir()
            shutil.copy2(repo_root / "pyproject.toml", build_context / "pyproject.toml")
            shutil.copy2(repo_root / "README.md", build_context / "README.md")
            shutil.copy2(repo_root / "setup.py", build_context / "setup.py")
            shutil.copytree(
                repo_root / "src",
                build_context / "src",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            wheel_dir.mkdir()

            for stale_rel_path in _ISS_00031_STALE_WHEEL_PATHS:
                stale_path = build_context / "build" / "lib" / stale_rel_path
                stale_path.parent.mkdir(parents=True, exist_ok=True)
                stale_path.write_text("stale wrapper-era artifact\n", encoding="utf-8")

            wheel_path, _, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )

            with zipfile.ZipFile(wheel_path) as wheel_zip:
                wheel_entries = set(wheel_zip.namelist())

            assert "spec_dock/assets/spec_dock/templates/README.md" in wheel_entries, (
                "sanity check failed: built wheel did not include expected live template asset"
            )
            for stale_rel_path in _ISS_00031_STALE_WHEEL_PATHS:
                assert stale_rel_path not in wheel_entries, (
                    f"built wheel unexpectedly shipped stale build artifact: {stale_rel_path}"
                )

    def test_distribution_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources(self) -> None:
        surfaces = self._issue_69_collect_install_root_artifact_surfaces()
        source_inventory = surfaces["source"]
        assert source_inventory, "issue-69 source install_root inventory must be non-empty"

        for surface_name in ("wheel", "sdist", "installed"):
            observed_inventory = surfaces[surface_name]
            missing = sorted(source_inventory - observed_inventory)
            unexpected = sorted(observed_inventory - source_inventory)
            assert observed_inventory == source_inventory, (
                f"issue-69 full install_root inventory parity failed for {surface_name}; "
                f"missing={missing[:10]} unexpected={unexpected[:10]}"
            )

    def test_distribution_wheel_build_prunes_seeded_stale_wrapper_era_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            pre_prune_snapshot = temp_root / "wheel-pre-prune-snapshot.json"

            self._issue_69_prepare_build_context(repo_root, build_context)
            build_env = os.environ.copy()
            build_env[self._ISSUE_69_SETUP_SEED_STALE_FIXTURES_ENV] = "1"
            build_env[self._ISSUE_69_SETUP_PRE_PRUNE_SNAPSHOT_ENV] = str(pre_prune_snapshot)

            wheel_path, _, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
                build_env=build_env,
            )

            assert pre_prune_snapshot.is_file(), f"issue-69 expected pre-prune snapshot to exist: {pre_prune_snapshot}"
            snapshot_payload = json.loads(pre_prune_snapshot.read_text(encoding="utf-8"))
            expected_seeded_fixtures = set(self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS)
            assert set(snapshot_payload.get("expected_seeded_stale_fixture_paths", [])) == expected_seeded_fixtures, (
                "issue-69 setup.py snapshot did not report the approved seeded fixture set"
            )
            assert set(snapshot_payload.get("present_before_prune", [])) == expected_seeded_fixtures, (
                "issue-69 seeded stale fixture set must exist in wheel build staging before prune"
            )

            wheel_inventory = self._issue_69_collect_wheel_file_inventory(wheel_path)
            for stale_artifact_path in self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS:
                assert stale_artifact_path not in wheel_inventory, (
                    f"issue-69 wheel build unexpectedly shipped seeded stale wrapper-era output: {stale_artifact_path}"
                )

    def test_workbench_readme_build_prune_preserves_allowlist_and_removes_stale_nested_readme(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            pre_prune_snapshot = temp_root / "wheel-pre-prune-snapshot.json"

            self._issue_69_prepare_build_context(repo_root, build_context)
            build_env = os.environ.copy()
            build_env[self._ISSUE_69_SETUP_SEED_STALE_FIXTURES_ENV] = "1"
            build_env[self._ISSUE_69_SETUP_PRE_PRUNE_SNAPSHOT_ENV] = str(pre_prune_snapshot)

            wheel_path, _, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
                build_env=build_env,
            )

            snapshot_payload = json.loads(pre_prune_snapshot.read_text(encoding="utf-8"))
            expected_seeded_fixtures = set(self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS)
            expected_readmes_before_prune = {
                *self._WORKBENCH_TEMPLATE_README_PATHS,
                "issue/legacy/README.md",
            }
            assert set(snapshot_payload.get("expected_seeded_stale_fixture_paths", [])) == expected_seeded_fixtures
            assert set(snapshot_payload.get("present_before_prune", [])) == expected_seeded_fixtures
            assert set(snapshot_payload.get("template_readmes_before_prune", [])) == expected_readmes_before_prune

            wheel_payloads = self._collect_wheel_template_readme_payloads(wheel_path)
            assert set(wheel_payloads) == set(self._WORKBENCH_TEMPLATE_README_PATHS)
            assert "issue/legacy/README.md" not in wheel_payloads

    def test_workbench_readme_distribution_inventory_and_bytes_match_all_surfaces(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        source_payloads = self._collect_source_template_readme_payloads(repo_root)
        expected_inventory = set(self._WORKBENCH_TEMPLATE_README_PATHS)
        assert set(source_payloads) == expected_inventory
        canonical_workbench_bytes = source_payloads[self._WORKBENCH_README_PATHS[0]]
        assert all(source_payloads[path] == canonical_workbench_bytes for path in self._WORKBENCH_README_PATHS)

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir()
            self._issue_69_prepare_build_context(repo_root, build_context)

            wheel_path, sdist_path, venv_python = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )
            self._issue_69_install_target_packages(
                python_executable=venv_python,
                target_dir=self._issue_69_site_packages_dir(self._issue_69_env_root(venv_python)),
                requirements=[str(wheel_path)],
                wheelhouse=self._issue_69_resolve_wheelhouse(repo_root),
            )

            wheel_payloads = self._collect_wheel_template_readme_payloads(wheel_path)
            sdist_payloads = self._collect_sdist_template_readme_payloads(sdist_path)
            installed_snapshot = self._collect_isolated_installed_template_readme_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=installed_snapshot,
                repo_root=repo_root,
            )
            installed_hex_payloads = installed_snapshot.get("template_readmes", {})
            assert isinstance(installed_hex_payloads, dict)
            installed_payloads = {
                str(path): bytes.fromhex(str(payload)) for path, payload in installed_hex_payloads.items()
            }

        surfaces = {
            "source": source_payloads,
            "wheel": wheel_payloads,
            "sdist": sdist_payloads,
            "installed": installed_payloads,
        }
        for surface_name, payloads in surfaces.items():
            assert set(payloads) == expected_inventory, (
                f"{surface_name} template README inventory mismatch: {sorted(payloads)}"
            )
        for workbench_path in self._WORKBENCH_README_PATHS:
            assert all(payloads[workbench_path] == canonical_workbench_bytes for payloads in surfaces.values()), (
                f"Workbench README bytes differ across distribution surfaces: {workbench_path}"
            )

    def test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        assert runtime_script.is_file(), f"dogfooding runtime script missing: {runtime_script}"

        doctor_help = subprocess.run(
            [sys.executable, str(runtime_script), "doctor", "--help"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert doctor_help.returncode == 0, (
            "checked-in dogfooding runtime must expose 'doctor'\n"
            f"stdout:\n{doctor_help.stdout}\n"
            f"stderr:\n{doctor_help.stderr}\n"
        )
        assert "usage: spec-dock/scripts/spec-dock doctor" in doctor_help.stdout

        legacy_active = subprocess.run(
            [sys.executable, str(runtime_script), "active", "set", "--initiative", "1"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert legacy_active.returncode == 2
        assert "'active set' supports explicit targets:" in legacy_active.stderr
        assert "active set --id <node-id>" in legacy_active.stderr

    def test_checked_in_dogfooding_mirror_docs_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self._assert_checked_in_dogfooding_mirror_docs_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_active_none_reports_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self._assert_checked_in_dogfooding_active_none_reports_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        checked_in_initiatives_root = repo_root / "spec-dock" / "initiatives"
        assert checked_in_initiatives_root.is_dir(), (
            f"checked-in dogfooding initiatives tree missing: {checked_in_initiatives_root}"
        )

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)

            target_initiatives_root = target / "spec-dock" / "initiatives"
            shutil.copytree(checked_in_initiatives_root, target_initiatives_root)

            def _find_issue_meta_path(issue_id: str) -> Path:
                matches: list[Path] = []
                for meta_path in target_initiatives_root.rglob(".meta.json"):
                    payload = json.loads(meta_path.read_text(encoding="utf-8"))
                    if payload.get("type") == "issue" and payload.get("id") == issue_id:
                        matches.append(meta_path)
                assert len(matches) == 1, f"cutover snapshot must have exactly one issue meta for {issue_id}: {matches}"
                return matches[0]

            from_issue_id = "iss-00063"
            to_issue_id = "iss-00062"
            from_meta_path = _find_issue_meta_path(from_issue_id)
            assert json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on") == [], (
                f"expected empty depends_on before deps add on {from_issue_id}"
            )

            add_result = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_issue_id, "--to", to_issue_id],
            )
            assert add_result.returncode == 0, (
                f"deps add stdout:\n{add_result.stdout}\ndeps add stderr:\n{add_result.stderr}"
            )
            assert f"spec-dock: ok (deps add) from={from_issue_id} to={to_issue_id} result=updated" in add_result.stdout
            assert json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on") == [to_issue_id], (
                "deps add did not persist expected depends_on edge into .meta.json"
            )

            remove_result = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_issue_id, "--to", to_issue_id],
            )
            assert remove_result.returncode == 0, (
                f"deps remove stdout:\n{remove_result.stdout}\ndeps remove stderr:\n{remove_result.stderr}"
            )
            assert (
                f"spec-dock: ok (deps remove) from={from_issue_id} to={to_issue_id} result=updated"
                in remove_result.stdout
            )
            assert json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on") == [], (
                "deps remove did not clear depends_on edge from .meta.json"
            )

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "spec-dock: ok (validate)" in validate_result.stdout

            sync_result = self._run_runtime_capture(target, ["sync"])
            assert sync_result.returncode == 0, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "spec-dock: ok (sync)" in sync_result.stdout

    def test_checked_in_dogfooding_runtime_mirror_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self._assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(repo_root)

    def test_dogfooding_runtime_inventory_excludes_generated_python_caches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_root = Path(tmp) / "spec_dock_runtime"
            runtime_root.mkdir()
            source_file = runtime_root / "app.py"
            source_file.write_text("# runtime source\n", encoding="utf-8")
            cache_dir = runtime_root / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "app.cpython-312.pyc").write_bytes(b"pyc")
            (runtime_root / "app.pyo").write_bytes(b"pyo")

            inventory = self._runtime_inventory(runtime_root)

            assert inventory == {"app.py": source_file}

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self.records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), str(repo_slug)))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Foreign #123",
            labels=[],
            updated_at="2026-03-19T00:00:00Z",
            url="https://github.com/other/repo/issues/123",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "artifacts.md").write_text("# issue artifacts\\n", encoding="utf-8")
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-00123",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        ),
    ]
    _materialize_required_artifacts(records)

    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    request = app_contracts.ImportNodeRequest(
        issue_number=123,
        title="Foreign Issue",
        slug=None,
        parent_id="epic-local-00001",
        target_repo_owner="other",
        target_repo_name="repo",
        allow_foreign_url=True,
    )
    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(request, ports)
        except RuntimeError as exc:
            message = str(exc)
        else:
            raise AssertionError("expected foreign import to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert "single-repo" in message, message
    assert "GitHub-backed identity" in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_import_release_lock_backward_compat_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import import_node as app_import_node
finally:
    sys.path.pop(0)

with tempfile.TemporaryDirectory() as td:
    specdock_dir = Path(td) / "spec-dock"
    lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_payload = (
        "token=holder\\n"
        "pid=222\\n"
        "user=lock-holder\\n"
        "created_unix=9999999999\\n"
        "created_iso=2099-01-01T00:00:00Z\\n"
    )
    lock_path.write_text(lock_payload, encoding="utf-8")

    try:
        app_import_node._release_create_lock(lock_path, "other")
        raise AssertionError("expected ownership mismatch")
    except RuntimeError as exc:
        message = str(exc)

    runtime_cmd = str((specdock_dir / "scripts" / "spec-dock").resolve())
    assert "reason=ownership_mismatch" in message, message
    assert f"{{runtime_cmd}} doctor" in message, message
    assert lock_path.exists(), "lock unexpectedly removed on ownership mismatch"

    lock_path.write_text(lock_payload, encoding="utf-8")
    app_import_node._release_create_lock(lock_path, "holder")
    assert not lock_path.exists(), "lock was not removed"
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/example/repo/issues/{{issue_number}}",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "artifacts.md").write_text("# issue artifacts\\n", encoding="utf-8")
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00555",
        title="Race winner import",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00555-race-winner-import",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=555,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=555,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "already linked" in message, message
        else:
            raise AssertionError("expected import/import race to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert injected["done"], injected
    assert events == [], events
    assert issue_gateway.calls == [(str(repo_root), 555, "example/repo")], issue_gateway.calls
    assert sum(1 for record in node_repo.records if record.id == "iss-00555") == 1, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/other/repo/issues/{{issue_number}}",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "artifacts.md").write_text("# issue artifacts\\n", encoding="utf-8")
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00123",
        title="Race winner new issue",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-race-winner-new-issue",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported foreign issue",
                    slug=None,
                    parent_id="epic-local-00001",
                    target_repo_owner="other",
                    target_repo_name="repo",
                    allow_foreign_url=True,
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
        else:
            raise AssertionError("expected foreign import to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert not injected["done"], injected
    assert "single-repo" in message, message
    assert "GitHub-backed identity" in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
    assert events == [], events
    assert sum(1 for record in node_repo.records if record.id == "iss-00123") == 0, node_repo.records
    assert sum(1 for record in node_repo.records if record.id == "iss-local-00001") == 0, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity(
        self,
    ) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Issue",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://example.invalid/issues/{{issue_number}}",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"

class _StubActiveStateStore:
    def __init__(self, manifest):
        self._manifest = manifest
        self.calls = []
    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )
    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    (issue_template_dir / "README.md").write_text("issue=<ISS_ID>\\n", encoding="utf-8")
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "artifacts.md").write_text("# issue artifacts\\n", encoding="utf-8")
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00001-jwt-auth",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    issue_gateway = _StubIssueGateway()
    active_state_store = _StubActiveStateStore(
        infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/path/init-local-00001",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/path/epic-local-00001",
            ),
            issue=None,
        )
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records, events),
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        active_state_store=active_state_store,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    collision = (
        Path(records[1].path)
        / "issues"
        / "iss-00124-add-refresh-token"
        / "README.md"
    )
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_text("existing", encoding="utf-8")

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Add refresh token",
                    slug=None,
                    parent_id=None,
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "Destination already exists" in message, message
        else:
            raise AssertionError("expected preflight collision to fail")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert events == [], events
    assert issue_gateway.calls == [], issue_gateway.calls
    assert [name for name, _path in active_state_store.calls] == ["load_active_manifest_no_migrate"], active_state_store.calls
    assert not (collision.parent / ".meta.json").exists()
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
    from spec_dock_runtime.presentation import json_state as presentation_json_state
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "main"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / ".meta.json").write_text("{{}}", encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=301,
                state="OPEN",
                title="Current repo #301",
                labels=[],
                updated_at="2026-03-18T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        ],
        foreign_snapshots={{
            ("other/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Foreign #301",
                labels=["bugfix"],
                updated_at="2026-03-18T02:00:00Z",
                url="https://github.com/other/repo/issues/301",
                repo_owner="other",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )
    result = app_sync_state.collect_sync_state(
        app_contracts.SyncRequest(
            force=False,
            github_enabled=True,
            issue_limit=10000,
            update_active_from_branch=False,
        ),
        ports,
    )
    current_status = result.issue_statuses["iss-local-00001"]
    foreign_status = result.issue_statuses["iss-local-00002"]
    assert current_status.effective_status == "open"
    assert foreign_status.effective_status == "done"
    index_all = json.loads(presentation_json_state.render_index_artifact(result).all_json_text)
    current_payload = index_all["nodes"]["iss-local-00001"]["github"]
    foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
    assert current_payload["url"] == "https://github.com/current/repo/issues/301"
    assert current_payload["state"] == "OPEN"
    assert foreign_payload["url"] == "https://github.com/other/repo/issues/301"
    assert foreign_payload["state"] == "CLOSED"
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_non_issue_deps_target_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
    from spec_dock_runtime.presentation import json_state as presentation_json_state
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(issue_depends_on_map={{}}, warnings=[])

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots):
        self._snapshots = list(snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        raise RuntimeError("unexpected repo-scoped issue view")

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-00101",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-00101-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        _record(
            kind="epic",
            node_id="epic-00201",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-00101-platform" / "epics" / "epic-00201-delivery",
            parent_id="init-00101",
            initiative_id="init-00101",
            epic_id=None,
            github_issue_number=201,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=101,
                state="OPEN",
                title="Initiative #101",
                labels=[],
                updated_at="2026-03-20T10:00:00Z",
                url="https://github.com/current/repo/issues/101",
                repo_owner="current",
                repo_name="repo",
            ),
            domain_models.IssueSnapshot(
                issue_number=201,
                state="OPEN",
                title="Epic #201",
                labels=[],
                updated_at="2026-03-20T11:00:00Z",
                url="https://github.com/current/repo/issues/201",
                repo_owner="current",
                repo_name="repo",
            ),
        ],
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
    )

    for target_id, expected_last_sync_at in (
        ("init-00101", "2026-03-20T10:00:00Z"),
        ("epic-00201", "2026-03-20T11:00:00Z"),
    ):
        deps_result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id=target_id, github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )
        payload = json.loads(presentation_json_state.render_deps_check_json(deps_result))
        target_status = payload["target_status"]
        assert target_status["authority"] == "github"
        assert target_status["effective_status"] == "open"
        assert target_status["source"] == "github"
        assert target_status["stale"] is False
        assert target_status["last_sync_at"] == expected_last_sync_at

    assert issue_gateway.view_calls == []
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_issue_create_lock_scope_narrowing_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, __RUNTIME_SCRIPTS_DIR__)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

@contextmanager
def patch_object(obj, name, new=None, side_effect=None):
    original = getattr(obj, name)
    if side_effect is not None:
        def replacement(*args, **kwargs):
            raise side_effect
    else:
        replacement = new
    setattr(obj, name, replacement)
    try:
        yield
    finally:
        setattr(obj, name, original)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "artifacts.md"),
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "artifacts.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "artifacts.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

def _runtime_cmd(specdock_dir):
    return shlex.quote(str((specdock_dir / "scripts" / "spec-dock").resolve()))

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        (Path(dest_dir) / ".meta.json").write_text(f"id={record.id}\\n", encoding="utf-8")
        self.records.append(record)
    def write_meta_at(self, dest_dir_fd, record):
        self.events.append("write_meta")
        meta_fd = os.open(".meta.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, dir_fd=dest_dir_fd)
        os.write(meta_fd, f"id={record.id}\\n".encode())
        os.close(meta_fd)
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    def copy_scaffolded_tree_at(self, src_dir, dest_dir, dest_dir_fd, replacements):
        from spec_dock_runtime.infra import template_scaffolder
        self.events.append("copy_scaffolded_tree")
        return template_scaffolder.copy_scaffolded_tree_at(src_dir, dest_dir, dest_dir_fd, replacements)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _FailingTemplateScaffolder(_StubTemplateScaffolder):
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise RuntimeError("simulated write seam failure")
    def copy_scaffolded_tree_at(self, src_dir, dest_dir, dest_dir_fd, replacements):
        del src_dir, dest_dir, dest_dir_fd, replacements
        raise RuntimeError("simulated write seam failure")

class _BlockingIssueGateway:
    def __init__(self, numbers, started_event, release_event):
        self.numbers = list(numbers)
        self.calls = []
        self.started_event = started_event
        self.release_event = release_event
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        self.started_event.set()
        if not self.release_event.wait(timeout=5.0):
            raise RuntimeError("timed out waiting for release_event")
        if not self.numbers:
            raise RuntimeError("no issue numbers configured")
        return self.numbers.pop(0)

class _StubClock:
    def today(self):
        return "2026-03-20"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([811], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    issue_result = {}
    issue_errors = []
    def _run_issue():
        try:
            issue_result["value"] = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            issue_errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    try:
        local_result = app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Payments",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=702,
            ),
            ports,
        )
    finally:
        release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert issue_errors == [], issue_errors
    assert local_result.node.id == "init-00702", local_result
    assert issue_result["value"].node.id == "iss-00811", issue_result
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    body = issue_gateway.calls[0][2]
    assert "Type: issue" in body, body
    assert "Epic:" not in body, body
    assert "Initiative:" not in body, body

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([812], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    errors = []
    def _run_issue():
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    node_repo.records = [record for record in node_repo.records if record.id != "epic-local-00001"]
    release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert len(errors) == 1, errors
    message = str(errors[0])
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "Epic not found: epic-local-00001" in message, message
    assert "GitHub issue was created: #812" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 812" in message, message
    assert events == [], events

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([813], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        "token=holder\\npid=222\\nuser=lock-holder\\ncreated_unix=9999999999\\ncreated_iso=2099-01-01\\n",
        encoding="utf-8",
    )

    try:
        app_create_node.create_issue(
            app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected lock failure after github create")
    except RuntimeError as exc:
        message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_remote_only_fail" in message, message
    assert "create lock acquisition failed" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert "GitHub issue was created: #813" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 813" in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([814], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    errors = []
    def _run_issue():
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    node_repo.records.append(
        _record(
            kind="issue",
            node_id="iss-local-00042",
            title="Competing link",
            path=epic_dir / "issues" / "iss-local-00042-competing-link",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=814,
        )
    )
    release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert len(errors) == 1, errors
    message = str(errors[0])
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "github linkage is already linked" in message, message
    assert "github.issue_number=814" in message, message
    assert "GitHub issue was created: #814" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 814" in message, message
    assert events == [], events
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert not (epic_dir / "issues" / "iss-00814-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([815], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_FailingTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    try:
        app_create_node.create_issue(
            app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected write seam failure after github create")
    except RuntimeError as exc:
        message = str(exc)
    assert started.is_set(), "issue_create was not called"
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "simulated write seam failure" in message, message
    assert "GitHub issue was created: #815" in message, message
    assert "Create may already have succeeded" not in message, message
    assert "Do not rerun blindly" not in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--github-issue 815" in message, message
    assert "close/cleanup" in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues" / "iss-00815-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([819], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    with patch_object(
        app_create_node,
        "_post_write_duplicate_guard",
        side_effect=RuntimeError("simulated post-write duplicate guard failure"),
    ):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected post-write guard failure after local write commit")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "simulated post-write duplicate guard failure" in message, message
    assert "GitHub issue was created: #819" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00819`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00819-refresh-token" / ".meta.json").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([816], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected cleanup failure after local write success")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_success_cleanup_fail" in message, message
    assert "create lock release failed" in message, message
    assert "GitHub issue was created: #816" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00816`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00816-refresh-token" / ".meta.json").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([817], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_FailingTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected combined body and cleanup failure")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_body_and_cleanup_fail" in message, message
    assert "Primary local failure: simulated write seam failure" in message, message
    assert "Cleanup failure: create lock release failed" in message, message
    assert "GitHub issue was created: #817" in message, message
    assert "Create may have already written files" in message, message
    assert "Do not rerun blindly" not in message, message
    assert "local node `iss-00817`" not in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--github-issue 817" in message, message
    assert "close/cleanup" in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues" / "iss-00817-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([818], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch_object(
        app_create_node,
        "_post_write_duplicate_guard",
        side_effect=RuntimeError("simulated post-write duplicate guard failure"),
    ):
        with patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure):
            try:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )
                raise AssertionError("expected post-write guard and cleanup failure")
            except RuntimeError as exc:
                message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_body_and_cleanup_fail" in message, message
    assert "Primary local failure: simulated post-write duplicate guard failure" in message, message
    assert "Cleanup failure: create lock release failed" in message, message
    assert "GitHub issue was created: #818" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00818`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00818-refresh-token" / ".meta.json").exists()
""".replace("__RUNTIME_SCRIPTS_DIR__", repr(str(runtime_scripts_dir)))
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_issue_create_pre_github_validation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, __RUNTIME_SCRIPTS_DIR__)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "artifacts.md"),
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "artifacts.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "artifacts.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        del dest_dir, record
        raise AssertionError("write_meta should not be called for pure validation failures")

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        del replacements
        return text
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise AssertionError("copy_scaffolded_tree should not be called for pure validation failures")
    def write_text(self, dest_path, text):
        del dest_path, text
        raise AssertionError("write_text should not be called for pure validation failures")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    cases = [
        (
            "missing-epic",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": None,
            },
            "--epic is required",
        ),
        (
            "partial-repo-identity",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-00001",
                "github_repo_owner": "chemitaro",
                "github_repo_name": None,
            },
            "github_repo_owner and github_repo_name must be provided together",
        ),
        (
            "missing-initiative-node",
            "create_epic",
            {
                "title": "JWT auth",
                "parent_id": "init-local-99999",
            },
            "Initiative not found: init-local-99999",
        ),
        (
            "missing-epic-node",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-99999",
            },
            "Epic not found: epic-local-99999",
        ),
    ]
    for case_name, create_attr, overrides, expected_error in cases:
        issue_gateway = _StubIssueGateway([950])
        ports = app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records),
            template_scaffolder=_StubTemplateScaffolder(),
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(),
            clock=None,
            repo_root=repo_root,
            specdock_dir=specdock_dir,
        )
        request_kwargs = {
            "title": "Refresh token",
            "slug": None,
            "parent_id": "epic-local-00001",
            "github_mode": "create",
            "github_issue_number": None,
            "github_repo_owner": None,
            "github_repo_name": None,
        }
        request_kwargs.update(overrides)
        try:
            getattr(app_create_node, create_attr)(app_contracts.CreateNodeRequest(**request_kwargs), ports)
            raise AssertionError(f"expected failure for {case_name}")
        except RuntimeError as exc:
            message = str(exc)
        assert expected_error in message, (case_name, message)
        assert "Outcome: pre_github_fail" in message, (case_name, message)
        assert "GitHub issue was created:" not in message, (case_name, message)
        assert issue_gateway.calls == [], (case_name, issue_gateway.calls)
""".replace("__RUNTIME_SCRIPTS_DIR__", repr(str(runtime_scripts_dir)))
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_non_issue_create_guidance_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, __RUNTIME_SCRIPTS_DIR__)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

@contextmanager
def patch_object(obj, name, side_effect):
    original = getattr(obj, name)
    def replacement(*args, **kwargs):
        raise side_effect
    setattr(obj, name, replacement)
    try:
        yield
    finally:
        setattr(obj, name, original)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "artifacts.md"),
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "artifacts.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "artifacts.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

def _runtime_cmd(specdock_dir):
    return shlex.quote(str((specdock_dir / "scripts" / "spec-dock").resolve()))

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        path = Path(dest_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / ".meta.json").write_text(f"id={record.id}\\n", encoding="utf-8")
        self._records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(self.render_text(src_path.read_text(encoding="utf-8"), replacements), encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    issue_gateway = _StubIssueGateway([960])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo([]),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        "token=holder\\npid=222\\nuser=lock-holder\\ncreated_unix=9999999999\\ncreated_iso=2099-01-01\\n",
        encoding="utf-8",
    )
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"
    try:
        app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected initiative failure")
    except RuntimeError as exc:
        message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_remote_only_fail" in message, message
    assert "GitHub issue was created: #960" in message, message
    assert f"{runtime_cmd} new initiative --title 'Auth platform'" in message, message
    assert "--github-issue 960" in message, message

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway([961])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    with patch_object(app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated epic write failure")):
        try:
            app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="JWT auth",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected epic failure")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "GitHub issue was created: #961" in message, message
    assert f"{runtime_cmd} new epic --title 'JWT auth'" in message, message
    assert "--initiative init-local-00001" in message, message
    assert "--github-issue 961" in message, message
""".replace("__RUNTIME_SCRIPTS_DIR__", repr(str(runtime_scripts_dir)))
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_create_mode_graph_preflight_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, __RUNTIME_SCRIPTS_DIR__)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        del dest_dir, record
        raise AssertionError("write_meta should not be called when graph preflight fails")

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        del replacements
        return text
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise AssertionError("copy_scaffolded_tree should not be called when graph preflight fails")
    def write_text(self, dest_path, text):
        del dest_path, text
        raise AssertionError("write_text should not be called when graph preflight fails")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_a = specdock_dir / "initiatives" / "init-local-00001-auth-platform-a"
    init_b = specdock_dir / "initiatives" / "init-local-00001-auth-platform-b"
    duplicate_records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform A",
            path=init_a,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform B",
            path=init_b,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
    ]

    issue_gateway = _StubIssueGateway([960])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo(duplicate_records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    try:
        app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Payments",
                slug=None,
                parent_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected graph preflight failure before github create")
    except RuntimeError as exc:
        message = str(exc)
    assert "duplicate id" in message.lower(), message
    assert "Outcome: pre_github_fail" in message, message
    assert "GitHub issue was created:" not in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
""".replace("__RUNTIME_SCRIPTS_DIR__", repr(str(runtime_scripts_dir)))
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_sync_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "main"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / ".meta.json").write_text("{{}}", encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Local issue",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-local",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 101): domain_models.IssueSnapshot(
                issue_number=101,
                state="OPEN",
                title="Current #101",
                labels=[],
                updated_at="2026-03-23T00:00:00Z",
                url="https://github.com/current/repo/issues/101",
                repo_owner="current",
                repo_name="repo",
            ),
            ("current/repo", 201): domain_models.IssueSnapshot(
                issue_number=201,
                state="CLOSED",
                title="Current #201",
                labels=["done"],
                updated_at="2026-03-23T00:01:00Z",
                url="https://github.com/current/repo/issues/201",
                repo_owner="current",
                repo_name="repo",
            ),
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    result = app_sync_state.collect_sync_state(
        app_contracts.SyncRequest(
            force=False,
            github_enabled=True,
            issue_limit=10000,
            update_active_from_branch=False,
        ),
        ports,
    )
    init_status = result.issue_statuses["init-local-00001"]
    epic_status = result.issue_statuses["epic-local-00001"]
    assert init_status.source == "github"
    assert init_status.effective_status == "open"
    assert epic_status.source == "github"
    assert epic_status.effective_status == "done"
    assert issue_gateway.view_calls == [
        (str(repo_root), 101, "current/repo"),
        (str(repo_root), 201, "current/repo"),
    ]
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import doctor as app_doctor
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import validate_tree as app_validate_tree
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=102,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)

    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        node_repo=_StubNodeRepo(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        git_gateway=_StubGitGateway(),
    )
    validation = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)
    assert not validation.report.errors, validation.report.errors

    doctor_result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
    assert doctor_result.ok, doctor_result.findings

    loaded_graph = app_create_node.load_graph(ports, validate=True)
    assert "iss-local-00001" in loaded_graph.nodes_by_id
    assert "iss-local-00002" in loaded_graph.nodes_by_id
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_keeps_numeric_branch_current_repo_overlap_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import active as domain_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.domain import tree as domain_tree
finally:
    sys.path.pop(0)

seeds = [
    domain_models.SpecNodeSeed(
        kind="initiative",
        id="init-local-00001",
        title="Platform",
        slug="platform",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
        parent_id=None,
        initiative_id=None,
        epic_id=None,
        github_issue_number=None,
    ),
    domain_models.SpecNodeSeed(
        kind="epic",
        id="epic-local-00001",
        title="Delivery",
        slug="delivery",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
        parent_id="init-local-00001",
        initiative_id="init-local-00001",
        epic_id=None,
        github_issue_number=None,
    ),
    domain_models.SpecNodeSeed(
        kind="issue",
        id="iss-local-00001",
        title="Current issue",
        slug="current-issue",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue/.meta.json"),
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
    ),
    domain_models.SpecNodeSeed(
        kind="issue",
        id="iss-local-00002",
        title="Foreign issue",
        slug="foreign-issue",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue/.meta.json"),
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
        github_repo_owner="other",
        github_repo_name="repo",
    ),
]
graph = domain_tree.build_graph(seeds)

matched, reason = domain_active.infer_active_node_from_branch(
    graph,
    branch="123-fix-login",
    current_repo_slug="current/repo",
)
assert matched is not None
assert matched.id == "iss-local-00001", matched
assert reason == "matched github.issue_number=123 from branch", reason

unknown_matched, unknown_reason = domain_active.infer_active_node_from_branch(
    graph,
    branch="issue-123",
    current_repo_slug=None,
)
assert unknown_matched is None
assert unknown_reason == "ambiguous github issue numbers [123]: issue:iss-local-00001, issue:iss-local-00002", unknown_reason

foreign_only_graph = domain_tree.build_graph(
    [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Platform",
            slug="platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="Delivery",
            slug="delivery",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Foreign issue",
            slug="foreign-issue",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
)
foreign_only_matched, foreign_only_reason = domain_active.infer_active_node_from_branch(
    foreign_only_graph,
    branch="123-fix-login",
    current_repo_slug="current/repo",
)
assert foreign_only_matched is None
assert (
    foreign_only_reason
    == "no current-repo matches for github issue numbers [123] in scope (current/repo); refusing foreign fallback: issue:iss-local-00001"
), foreign_only_reason

scoped_ambiguity_graph = domain_tree.build_graph(
    [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Platform",
            slug="platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="Delivery",
            slug="delivery",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Current issue a",
            slug="current-issue-a",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00002",
            title="Current issue b",
            slug="current-issue-b",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00003",
            title="Foreign issue",
            slug="foreign-issue",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
)
scoped_ambiguity_matched, scoped_ambiguity_reason = domain_active.infer_active_node_from_branch(
    scoped_ambiguity_graph,
    branch="issue-123",
    current_repo_slug="current/repo",
)
assert scoped_ambiguity_matched is None
assert (
    scoped_ambiguity_reason
    == "ambiguous github issue numbers [123] in current repo scope (current/repo): issue:iss-local-00001, issue:iss-local-00002"
), scoped_ambiguity_reason

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "123-fix-login"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

ports = app_ports.Ports(
    node_reader=_StubNodeReader(),
    repo_root=Path("/repo"),
    git_gateway=_StubGitGateway(),
    active_state_store=object(),
)
state = app_contracts.SyncStateResult(
    graph=domain_models.SpecGraph(nodes_by_id={{}}),
    active=None,
    issue_statuses={{}},
    progress=domain_models.ProgressMap(by_node_id={{}}, counts={{"total": 0, "done": 0, "open": 0, "unknown": 0}}),
    deps_state=domain_models.DepsState(nodes=[], warnings=[]),
    deps_eval_by_id={{}},
    generated_at="2026-03-23T00:00:00+00:00",
    warnings=[],
    deps_preflight_error=None,
    repo_root=Path("/repo"),
)
observed = {{}}
original_infer = app_sync_state.infer_active_node_from_branch

def _fake_infer(graph, *, branch, current_repo_slug=None):
    del graph
    observed["branch"] = branch
    observed["current_repo_slug"] = current_repo_slug
    return (None, "no branch match")

app_sync_state.infer_active_node_from_branch = _fake_infer
try:
    next_state, outcome = app_sync_state.maybe_auto_update_from_branch(state, ports)
finally:
    app_sync_state.infer_active_node_from_branch = original_infer

assert next_state is state
assert outcome is not None
assert outcome.applied is False
assert outcome.reason == "no branch match"
assert observed == {{"branch": "123-fix-login", "current_repo_slug": "current/repo"}}
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_tool_version_fallback_reads_pyproject(self) -> None:
        import spec_dock.cli as cli

        expected = _expected_spec_dock_version()
        old_version = getattr(cli, "__version__", None)
        old_file = getattr(cli, "__file__", None)
        try:
            cli.__version__ = "0.0.0+unknown"
            repo_root = Path(__file__).resolve().parents[3]
            cli.__file__ = str(repo_root / "src" / "spec_dock" / "cli.py")
            assert cli._tool_version() == expected
        finally:
            if old_version is not None:
                cli.__version__ = old_version
            if old_file is not None:
                cli.__file__ = old_file

    def test_no_skill_option_is_rejected(self) -> None:
        import spec_dock.cli as cli

        with pytest.raises(SystemExit) as cm:
            cli._parse_args(["init", "--no-skill", "."])
        assert cm.value.code == 2

    def test_issue_68_workflow_seed_matches_repo_root_ci_workflow(self) -> None:
        install_root_workflow = self._ISSUE_68_INSTALL_ROOT / ".github/workflows/ci.yml"
        repo_root_workflow = Path(".github/workflows/ci.yml")

        assert repo_root_workflow.is_file(), f"missing repo-root workflow seed source: {repo_root_workflow}"
        assert install_root_workflow.is_file(), f"missing issue-68 install_root workflow seed: {install_root_workflow}"
        assert install_root_workflow.read_bytes() == repo_root_workflow.read_bytes(), (
            "install_root workflow seed must be byte-equivalent to repo-root .github/workflows/ci.yml"
        )
        workflow_text = install_root_workflow.read_text(encoding="utf-8")
        assert "test -f ./spec-dock/scripts/spec-dock" in workflow_text
        assert "test -x ./spec-dock/scripts/spec-dock" not in workflow_text
        assert "python3 ./spec-dock/scripts/spec-dock sync" in workflow_text
        assert "python3 ./spec-dock/scripts/spec-dock validate" in workflow_text

    def test_issue_68_provider_only_workflow_is_not_shipped_via_install_root(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        provider_workflow_paths = {
            "fast": repo_root / ".github/workflows/provider-ci.yml",
            "full": repo_root / ".github/workflows/provider-full-regression.yml",
        }
        install_root_workflow_paths = {
            name: repo_root / "src/spec_dock/assets/install_root" / path.relative_to(repo_root)
            for name, path in provider_workflow_paths.items()
        }

        for name, workflow_path in provider_workflow_paths.items():
            assert workflow_path.is_file(), (
                f"missing repo-root provider-only workflow: name={name}, path={workflow_path}"
            )
            assert not install_root_workflow_paths[name].exists(), (
                "provider-only workflow must not be shipped in install_root managed assets: "
                f"{install_root_workflow_paths[name]}"
            )

        workflow_texts = {name: path.read_text(encoding="utf-8") for name, path in provider_workflow_paths.items()}
        workflow_lines = {name: text.splitlines() for name, text in workflow_texts.items()}

        def section_keys(lines: list[str], header: str) -> set[str]:
            section_index = lines.index(header)
            keys: set[str] = set()
            for line in lines[section_index + 1 :]:
                if line and not line.startswith(" "):
                    break
                match = re.fullmatch(r"  ([A-Za-z0-9_-]+):.*", line)
                if match is not None:
                    keys.add(match.group(1))
            return keys

        fast_triggers = section_keys(workflow_lines["fast"], "on:")
        full_triggers = section_keys(workflow_lines["full"], "on:")
        assert fast_triggers == {"pull_request"}
        assert full_triggers == {"push", "workflow_dispatch"}

        full_push_index = workflow_lines["full"].index("  push:")
        full_push_block: list[str] = []
        for line in workflow_lines["full"][full_push_index + 1 :]:
            if re.fullmatch(r"  [A-Za-z0-9_-]+:.*", line):
                break
            full_push_block.append(line)
        full_push_is_main_only = "    branches: [main]" in full_push_block
        assert full_push_is_main_only

        observed_event_matrix = {
            "pull_request": (
                "pull_request" in fast_triggers,
                "pull_request" in full_triggers,
            ),
            "non-main push": (
                "push" in fast_triggers,
                "push" in full_triggers and not full_push_is_main_only,
            ),
            "main push": (
                "push" in fast_triggers,
                "push" in full_triggers and full_push_is_main_only,
            ),
            "workflow_dispatch": (
                "workflow_dispatch" in fast_triggers,
                "workflow_dispatch" in full_triggers,
            ),
            "schedule": (
                "schedule" in fast_triggers,
                "schedule" in full_triggers,
            ),
        }
        assert observed_event_matrix == {
            "pull_request": (True, False),
            "non-main push": (False, False),
            "main push": (False, True),
            "workflow_dispatch": (False, True),
            "schedule": (False, False),
        }

        assert "name: Provider CI" in workflow_lines["fast"]
        assert section_keys(workflow_lines["fast"], "jobs:") == {
            "provider-tests",
            "provider-distribution-parity",
        }
        assert section_keys(workflow_lines["full"], "jobs:") == {"provider-full-regression"}
        assert "python -m pip install uv" in workflow_texts["fast"]
        provider_test_lines = _workflow_job_lines(workflow_texts["fast"], "provider-tests")
        assert "        run: make lint" in provider_test_lines
        assert provider_test_lines.count("        run: uv run pytest") == 1
        assert "--run-full-regression" not in "\n".join(provider_test_lines)
        provider_parity_lines = _workflow_job_lines(workflow_texts["fast"], "provider-distribution-parity")
        provider_parity_text = "\n".join(provider_parity_lines)
        assert "    runs-on: ${{ matrix.os }}" in provider_parity_lines
        assert "        os: [ubuntu-latest, macos-latest]" in provider_parity_lines
        assert "          ref: ${{ github.event.pull_request.head.sha }}" in provider_parity_lines
        assert "          CANDIDATE_SHA: ${{ github.event.pull_request.head.sha }}" in provider_parity_lines
        assert provider_parity_text.count("${{ github.event.pull_request.head.sha }}") == 2
        assert '        run: test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"' in provider_parity_lines
        assert "continue-on-error:" not in provider_parity_text
        expected_provider_parity_commands = (
            "        run: uv run pytest tests/unit/provider_lifecycle/test_engine.py",
            (
                "        run: uv run pytest --run-full-regression --full-regression-shard "
                "tests/cli_runtime/test_distribution_cutover.py"
            ),
            (
                "        run: uv run pytest --run-full-regression --full-regression-shard "
                "tests/integration/test_epic_00343_distribution.py"
            ),
        )
        for command in expected_provider_parity_commands:
            assert command in provider_parity_lines
        full_workflow_flattened = " ".join(workflow_texts["full"].split())
        assert "uv run python -m scripts.quality.verify_full_regression --shards 4" in full_workflow_flattened
        assert "verify-full-regression.py" not in workflow_texts["full"]
        assert "timeout-minutes" not in workflow_texts["full"]
        assert "--timeout-seconds" not in workflow_texts["full"]
        assert "--max-total-seconds" not in workflow_texts["full"]
        assert "--shards 4" in workflow_texts["full"]
        assert "run: uv run pytest --run-full-regression" not in workflow_texts["full"]
        assert "continue-on-error:" not in workflow_texts["full"]

        for name, workflow_text in workflow_texts.items():
            assert re.search(r"(?m)^\s*permissions:", workflow_text) is None, name
            assert re.search(r"(?m)^\s*secrets:", workflow_text) is None, name
            assert "secrets." not in workflow_text, name

        concurrency_index = workflow_lines["full"].index("concurrency:")
        concurrency_lines: list[str] = []
        for line in workflow_lines["full"][concurrency_index + 1 :]:
            if line and not line.startswith(" "):
                break
            concurrency_lines.append(line)
        group_line = next(line for line in concurrency_lines if line.startswith("  group: "))
        cancel_line = next(line for line in concurrency_lines if line.startswith("  cancel-in-progress: "))
        assert "github.event_name == 'push'" in group_line
        assert "github.ref" in group_line
        assert "github.run_id" in group_line
        assert "github.event_name == 'push'" in cancel_line

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            generated_workflow_paths = {
                name: target / path.relative_to(repo_root) for name, path in provider_workflow_paths.items()
            }

            assert main(["init", str(target)]) == 0
            for path in generated_workflow_paths.values():
                assert not path.exists(), f"provider-only workflow must not be generated by init: {path}"

            assert main(["update", str(target)]) == 0
            for path in generated_workflow_paths.values():
                assert not path.exists(), f"provider-only workflow must not be generated by update: {path}"

        legacy_runner = "python -m " + "unit" + "test discover"
        assert legacy_runner not in workflow_texts["fast"]

    def test_issue_360_readme_catalog_excludes_historical_artifact_routes(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        spec_dock_assets = repo_root / "src" / "spec_dock" / "assets" / "spec_dock"
        asset_paths = {
            "templates readme": spec_dock_assets / "templates" / "README.md",
            "scripts readme": spec_dock_assets / "scripts" / "README.md",
        }
        texts = {label: path.read_text(encoding="utf-8") for label, path in asset_paths.items()}

        scripts_readme = texts["scripts readme"]
        assert (
            "current catalog: `blank` / `interview` / `research` / `disc` / `decision-candidate` / `adr`"
            in scripts_readme
        )
        assert "`pr-repair-batch` / `draft-*` / `scratch` / `note` は Historical-only" in scripts_readme
        assert "new artifact pr-repair-batch" not in scripts_readme
        assert "new artifact draft-plan" not in scripts_readme
        assert "typed artifact のファイル名 contract は `<ts>-<type>-<slug>.md`" in scripts_readme

    def test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        issue_69_report = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00003-architecture-maintenance-and-hardening"
            / "epics"
            / "epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling"
            / "issues"
            / "iss-00069-package-data-and-installed-artifact-parity"
            / "report.md"
        )
        issue_70_report = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00003-architecture-maintenance-and-hardening"
            / "epics"
            / "epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling"
            / "issues"
            / "iss-00070-installer-source-discovery-and-managed-ownership"
            / "report.md"
        )
        assert issue_69_report.is_file(), f"issue-71 missing issue-69 report: {issue_69_report}"
        assert issue_70_report.is_file(), f"issue-71 missing issue-70 report: {issue_70_report}"

        issue_69_text = issue_69_report.read_text(encoding="utf-8")
        issue_70_text = issue_70_report.read_text(encoding="utf-8")

        package_parity_section = self._issue_71_extract_markdown_section_by_heading_prefix(
            markdown_text=issue_69_text,
            heading_prefix="package-parity-evidence",
            source_label="issue-69 report",
        )
        for required_phrase in (
            "full inventory parity:",
            "representative asset set:",
            "stale exclusion guard:",
            "isolated install smoke:",
        ):
            assert required_phrase in package_parity_section, (
                f"issue-71 missing package parity subcheck phrase: {required_phrase}"
            )
        assert package_parity_section.count("- result:") >= 4, (
            "issue-71 package parity evidence should include result lines for required subchecks"
        )
        assert package_parity_section.count("- pass") >= 4, (
            "issue-71 package parity evidence should include pass results for required subchecks"
        )
        assert "pending" not in package_parity_section.lower(), (
            "issue-71 package parity evidence should not be pending-only"
        )
        assert "placeholder" not in package_parity_section.lower(), (
            "issue-71 package parity evidence should not be placeholder-only"
        )

        handoff_section = self._issue_71_extract_markdown_section_by_heading_prefix(
            markdown_text=issue_70_text,
            heading_prefix="handoff-validation-evidence",
            source_label="issue-70 report",
        )
        for required_phrase in (
            "source inventory / manifest assertions:",
            "invalid manifest negative test coverage:",
            "current managed / obsolete managed boundary assertions:",
            "installed-package cutover evidence:",
        ):
            assert required_phrase in handoff_section, (
                f"issue-71 missing issue-70 handoff subcheck phrase: {required_phrase}"
            )
        assert handoff_section.count("- result:") >= 4, (
            "issue-71 handoff evidence should include result lines for required subchecks"
        )
        assert handoff_section.count("- pass") >= 4, (
            "issue-71 handoff evidence should include pass results for required subchecks"
        )
        assert "pending" not in handoff_section.lower(), "issue-71 handoff evidence should not be pending-only"
        assert "placeholder" not in handoff_section.lower(), "issue-71 handoff evidence should not be placeholder-only"

    def test_reference_sync_doc_matches_bundled_asset(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        bundled = (repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "docs" / "reference_sync.md").read_text(
            encoding="utf-8"
        )

        repo_copy = (repo_root / "spec-dock" / "docs" / "reference_sync.md").read_text(encoding="utf-8")

        assert repo_copy == bundled

    def test_reference_deps_doc_matches_bundled_asset(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        bundled = (repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "docs" / "reference_deps.md").read_text(
            encoding="utf-8"
        )

        repo_copy = (repo_root / "spec-dock" / "docs" / "reference_deps.md").read_text(encoding="utf-8")

        assert repo_copy == bundled

    def _clear_active_entrypoints(self, target: Path) -> Path:
        active_dir = target / "spec-dock" / "active"
        for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
            p = active_dir / name
            if p.is_symlink() or p.is_file():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                shutil.rmtree(p)
        assert list(active_dir.iterdir()) == []
        return active_dir

    def _overlay_checked_in_dogfooding_runtime(self, target: Path) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        checked_in_scripts_dir = repo_root / "spec-dock" / "scripts"
        target_scripts_dir = target / "spec-dock" / "scripts"
        assert checked_in_scripts_dir.is_dir(), f"checked-in scripts dir missing: {checked_in_scripts_dir}"
        assert target_scripts_dir.is_dir(), f"target scripts dir missing: {target_scripts_dir}"

        target_runtime_dir = target_scripts_dir / "spec_dock_runtime"
        if target_runtime_dir.exists():
            shutil.rmtree(target_runtime_dir)
        shutil.copytree(checked_in_scripts_dir / "spec_dock_runtime", target_runtime_dir)
        shutil.copy2(checked_in_scripts_dir / "spec-dock", target_scripts_dir / "spec-dock")

    def _create_minimal_local_tree(self, target: Path) -> tuple[Path, Path, Path]:
        initiative_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
        epic_dir = initiative_dir / "epics" / "epic-local-00001-jwt-auth"
        issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"

        def _materialize_node(node_dir: Path, meta: dict[str, object]) -> None:
            node_dir.mkdir(parents=True, exist_ok=True)
            (node_dir / "discussions").mkdir(parents=True, exist_ok=True)
            self._write_json_force(node_dir / ".meta.json", meta)
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                self._write_text_force(node_dir / filename, f"{meta['id']}:{filename}\n")

        _materialize_node(
            initiative_dir,
            {
                "schema_version": 1,
                "type": "initiative",
                "id": "init-local-00001",
                "title": "Auth platform",
                "slug": "auth-platform",
                "github": {
                    "issue_number": 101,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        _materialize_node(
            epic_dir,
            {
                "schema_version": 1,
                "type": "epic",
                "id": "epic-local-00001",
                "title": "JWT auth",
                "slug": "jwt-auth",
                "parent_id": "init-local-00001",
                "initiative_id": "init-local-00001",
                "github": {
                    "issue_number": 102,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        _materialize_node(
            issue_dir,
            {
                "schema_version": 1,
                "type": "issue",
                "id": "iss-local-00001",
                "title": "Add refresh token",
                "slug": "add-refresh-token",
                "parent_id": "epic-local-00001",
                "initiative_id": "init-local-00001",
                "epic_id": "epic-local-00001",
                "github": {
                    "issue_number": 103,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        assert (initiative_dir / ".meta.json").is_file()
        assert (epic_dir / ".meta.json").is_file()
        assert (issue_dir / ".meta.json").is_file()
        return initiative_dir, epic_dir, issue_dir

    def _materialize_local_issue_under_epic(
        self,
        epic_dir: Path,
        *,
        local_num: int,
        title: str,
        github_issue_number: int | None = None,
        github_repo_owner: str = "example",
        github_repo_name: str = "repo",
    ) -> Path:
        epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
        slug = title.lower().replace(" ", "-")
        issue_dir = epic_dir / "issues" / f"iss-local-{local_num:05d}-{slug}"
        issue_meta: dict[str, object] = {
            "schema_version": 1,
            "type": "issue",
            "id": f"iss-local-{local_num:05d}",
            "title": title,
            "slug": slug,
            "parent_id": str(epic_meta["id"]),
            "initiative_id": str(epic_meta["initiative_id"]),
            "epic_id": str(epic_meta["id"]),
        }
        if github_issue_number is not None:
            issue_meta["github"] = {
                "issue_number": github_issue_number,
                "repo_owner": github_repo_owner,
                "repo_name": github_repo_name,
            }

        issue_dir.mkdir(parents=True, exist_ok=True)
        (issue_dir / "discussions").mkdir(parents=True, exist_ok=True)
        self._write_json_force(issue_dir / ".meta.json", issue_meta)
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            self._write_text_force(issue_dir / filename, f"{issue_meta['id']}:{filename}\n")
        return issue_dir

    def test_checked_in_dogfooding_runtime_subprocess_import_post_sync_no_crash_parity(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            import_result = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            assert import_result.returncode == 0, (
                f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}"
            )
            assert "spec-dock: ok (import issue)" in import_result.stdout
            assert "import_post_sync_failed" not in import_result.stderr
            assert (target / "spec-dock" / ".agent" / "index.json").is_file()
            assert (target / "spec-dock" / ".agent" / "tree.json").is_file()

    def test_checked_in_dogfooding_runtime_subprocess_issue_create_gateway_failure_pre_github_parity(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, _current_issue_dir = self._create_minimal_local_tree(target)

            issues_dir = epic_dir / "issues"
            before_issue_dirs = sorted(p.name for p in issues_dir.iterdir() if p.is_dir())
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$1 $2" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "simulated issue_create failure" >&2\n'
                "  exit 1\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                "  echo '[]'\n"
                "  exit 0\n"
                "fi\n"
                'echo "unexpected gh args: $@" >&2\n'
                "exit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            create_result = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "epic-local-00001", "--title", "Gateway failure issue"],
                env=test_env,
            )
            assert create_result.returncode == 1, (
                f"new issue stdout:\n{create_result.stdout}\nnew issue stderr:\n{create_result.stderr}"
            )
            assert "Outcome: pre_github_fail" in create_result.stderr
            assert "GitHub issue was created:" not in create_result.stderr

            after_issue_dirs = sorted(p.name for p in issues_dir.iterdir() if p.is_dir())
            assert after_issue_dirs == before_issue_dirs
            assert not any(name.endswith("-gateway-failure-issue") for name in after_issue_dirs)

            gh_calls = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            assert len(gh_calls) == 1, f"unexpected gh calls: {gh_calls}"
            assert gh_calls[0] == "issue create", f"unexpected gh calls: {gh_calls}"

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=2, title="Foreign issue", github_issue_number=202
            )
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=3, title="Depends issue", github_issue_number=203
            )

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)
            depends_meta_path = depends_issue_dir / ".meta.json"
            depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
            depends_meta["depends_on"] = [123]
            self._write_json_force(depends_meta_path, depends_meta)

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003", "--json"],
            )
            assert deps_result.returncode == 3, (
                f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}"
            )
            payload = json.loads(deps_result.stdout)
            assert payload.get("effective_depends_on") == ["iss-local-00001"]
            assert payload.get("blockers") == ["iss-local-00001"]
            assert "Ambiguous github.issue_number=123" not in deps_result.stderr

    def test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=2, title="Foreign issue", github_issue_number=202
            )
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=3, title="Depends issue", github_issue_number=203
            )

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"
            expected_by_ref = {
                "other/repo#123": "iss-local-00002",
                "https://github.com/other/repo/issues/123": "iss-local-00002",
                "current/repo#123": "iss-local-00001",
                "https://github.com/current/repo/issues/123": "iss-local-00001",
            }
            for dep_ref, expected_dep in expected_by_ref.items():
                with _case(dep_ref=dep_ref):
                    depends_meta_path = depends_issue_dir / ".meta.json"
                    depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
                    depends_meta["depends_on"] = [dep_ref]
                    self._write_json_force(depends_meta_path, depends_meta)
                    deps_result = self._run_runtime_capture(
                        target,
                        ["deps", "check", "--id", "iss-local-00003", "--json"],
                    )
                    assert deps_result.returncode == 3, (
                        f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}"
                    )
                    payload = json.loads(deps_result.stdout)
                    assert payload.get("effective_depends_on") == [expected_dep]
                    assert payload.get("blockers") == [expected_dep]

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, _current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=2, title="Foreign issue", github_issue_number=202
            )
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=3, title="Depends issue", github_issue_number=203
            )

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"
            depends_meta_path = depends_issue_dir / ".meta.json"
            depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
            depends_meta["depends_on"] = [123]
            self._write_json_force(depends_meta_path, depends_meta)

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003"],
            )
            assert deps_result.returncode == 1, (
                f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}"
            )
            assert (
                "No node found for github.issue_number=123 in current repo scope (current/repo)" in deps_result.stderr
            )
            assert "Create/link the node first." in deps_result.stderr

    def test_checked_in_dogfooding_runtime_subprocess_keeps_lone_unscoped_legacy_without_backfill_parity(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=2, title="Foreign issue", github_issue_number=202
            )

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_meta_path = epic_dir / "issues" / "iss-local-00002-foreign-issue" / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_meta_path, foreign_meta)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_result.returncode == 0, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            assert current_meta_after["github"]["issue_number"] == 123
            assert "repo_owner" not in current_meta_after["github"]
            assert "repo_name" not in current_meta_after["github"]

    def test_checked_in_dogfooding_runtime_subprocess_keeps_readonly_lone_unscoped_without_backfill_parity(
        self,
    ) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(
                epic_dir, local_num=2, title="Foreign issue", github_issue_number=202
            )

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)
            current_meta_path.chmod(current_meta_path.stat().st_mode & ~0o222)

            foreign_meta_path = epic_dir / "issues" / "iss-local-00002-foreign-issue" / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_meta_path, foreign_meta)

            runtime_fs_repo = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _runtime_os_name() -> str:\n"
                + '    return "nt"\n',
                encoding="utf-8",
            )

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_result.returncode == 0, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            assert current_meta_after["github"]["issue_number"] == 123
            assert "repo_owner" not in current_meta_after["github"]
            assert "repo_name" not in current_meta_after["github"]
            assert current_meta_path.stat().st_mode & 0o222 == 0

    def test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 1, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "epic missing parent_id" in validate_result.stderr
            assert "Missing required artifact" not in validate_result.stderr

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            assert doctor_result.returncode == 1, (
                f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}"
            )
            assert "epic missing parent_id" in doctor_result.stderr
            assert "Missing required artifact" not in doctor_result.stderr

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert sync_result.returncode == 1, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "epic missing parent_id" in sync_result.stderr
            assert "Missing required artifact" not in sync_result.stderr

    def test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert sync_result.returncode == 1, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "preflight validate failed: Missing required artifact" in sync_result.stderr
            assert "report.md" in sync_result.stderr
            assert "spec-dock: ok (sync)" not in sync_result.stdout

    def test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            import_result = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            assert import_result.returncode == 1, (
                f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}"
            )
            assert "preflight validate failed" in import_result.stderr
            assert "Missing required artifact" in import_result.stderr
            assert "report.md" in import_result.stderr
            assert not (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-00123-imported-issue"
            ).exists()
            if log_path.exists():
                assert log_path.read_text(encoding="utf-8").strip() == ""

    def test_checked_in_dogfooding_runtime_subprocess_import_partial_write_doctor_first_parity(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            runtime_scripts_dir = target / "spec-dock" / "scripts"
            check_code = f"""
import io
import os
import sys
from contextlib import contextmanager, redirect_stderr
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime import app as runtime_app
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import import_node as app_import_node
finally:
    sys.path.pop(0)

@contextmanager
def patch_object(obj, name, side_effect):
    original = getattr(obj, name)
    def replacement(*args, **kwargs):
        raise side_effect
    setattr(obj, name, replacement)
    try:
        yield
    finally:
        setattr(obj, name, original)

os.chdir({str(target)!r})
stderr_buffer = io.StringIO()
with patch_object(
    app_import_node,
    "execute_create_plan",
    side_effect=app_create_node.CreatePlanExecutionError(
        phase="scaffold_copied",
        message="simulated import partial write",
    ),
):
    with redirect_stderr(stderr_buffer):
        exit_code = runtime_app.main(
            ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"]
        )

stderr_text = stderr_buffer.getvalue()
runtime_cmd = str((Path({str(target)!r}) / "spec-dock" / "scripts" / "spec-dock").resolve())
assert exit_code == 1, exit_code
assert "Outcome: import_local_write_fail." in stderr_text, stderr_text
assert "simulated import partial write" in stderr_text, stderr_text
assert "Import may have partially written local files. Do not rerun blindly." in stderr_text, stderr_text
assert f"{{runtime_cmd}} doctor" in stderr_text, stderr_text
assert "Recovery: rerun" not in stderr_text, stderr_text
"""
            result = subprocess.run(
                [sys.executable, "-c", check_code],
                cwd=str(target),
                capture_output=True,
                text=True,
                env=test_env,
            )
            assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    def test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)
            agent_dir = target / "spec-dock" / ".agent"

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert sync_result.returncode == 0, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "preflight validate failed" in sync_result.stderr
            assert "report.md" in sync_result.stderr
            assert "deps_preflight_failed" in sync_result.stderr or "DEPS_DISABLED" in sync_result.stderr, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "spec-dock: ok (sync)" in sync_result.stdout

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert not index["deps"]["valid"]
            assert "preflight validate failed" in str(index["deps"]["error"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            assert not tree["deps"]["valid"]
            assert "preflight validate failed" in str(tree["deps"]["error"])

    def test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert sync_result.returncode == 1, (
                f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}"
            )
            assert "epic missing parent_id" in sync_result.stderr
            assert "Missing required artifact" not in sync_result.stderr

    def test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 1, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "Missing required artifact" in validate_result.stderr
            assert "design.md" in validate_result.stderr

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            assert doctor_result.returncode == 1, (
                f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}"
            )
            assert "[missing_artifact] Missing required artifact" in doctor_result.stderr
            assert "design.md" in doctor_result.stderr

    def test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)

            meta_path = issue_dir / ".meta.json"
            meta_path.chmod(meta_path.stat().st_mode | 0o200)
            meta_path.unlink()

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join([
                    "token=active",
                    "pid=1234",
                    "user=tester",
                    "created_unix=9999999999",
                    "created_iso=2286-11-20T17:46:39Z",
                ])
                + "\n",
                encoding="utf-8",
            )

            validate_in_progress = self._run_runtime_capture(target, ["validate"])
            assert validate_in_progress.returncode == 1, (
                f"validate(in_progress) stdout:\n{validate_in_progress.stdout}\nvalidate(in_progress) stderr:\n{validate_in_progress.stderr}"
            )
            assert "Create in-progress state detected" in validate_in_progress.stderr
            assert "Missing required artifact" not in validate_in_progress.stderr

            sync_in_progress = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert sync_in_progress.returncode == 1, (
                f"sync(in_progress) stdout:\n{sync_in_progress.stdout}\nsync(in_progress) stderr:\n{sync_in_progress.stderr}"
            )
            assert "Create in-progress state detected" in sync_in_progress.stderr

            doctor_in_progress = self._run_runtime_capture(target, ["doctor"])
            assert doctor_in_progress.returncode == 1, (
                f"doctor(in_progress) stdout:\n{doctor_in_progress.stdout}\ndoctor(in_progress) stderr:\n{doctor_in_progress.stderr}"
            )
            assert "[stale_create_lock]" in doctor_in_progress.stderr
            assert "Create in-progress state detected" in doctor_in_progress.stderr
            assert "[missing_artifact]" not in doctor_in_progress.stderr

            lock_path.write_text(
                "\n".join([
                    "token=stale",
                    "pid=4321",
                    "user=tester",
                    "created_unix=0",
                    "created_iso=1970-01-01T00:00:00Z",
                ])
                + "\n",
                encoding="utf-8",
            )

            validate_stale = self._run_runtime_capture(target, ["validate"])
            assert validate_stale.returncode == 1, (
                f"validate(stale) stdout:\n{validate_stale.stdout}\nvalidate(stale) stderr:\n{validate_stale.stderr}"
            )
            assert "Stale create-lock state detected" in validate_stale.stderr
            assert "Missing required artifact" not in validate_stale.stderr

            sync_stale = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert sync_stale.returncode == 1, (
                f"sync(stale) stdout:\n{sync_stale.stdout}\nsync(stale) stderr:\n{sync_stale.stderr}"
            )
            assert "Stale create-lock state detected" in sync_stale.stderr

            doctor_stale = self._run_runtime_capture(target, ["doctor"])
            assert doctor_stale.returncode == 1, (
                f"doctor(stale) stdout:\n{doctor_stale.stdout}\ndoctor(stale) stderr:\n{doctor_stale.stderr}"
            )
            assert "[stale_create_lock]" in doctor_stale.stderr
            assert "Stale create-lock state detected" in doctor_stale.stderr
            assert "[missing_artifact]" not in doctor_stale.stderr
