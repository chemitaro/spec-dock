import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)

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


class TestInitUpdate(CliRuntimeHarness):
    _CANONICAL_RULES_PROVIDER_ASSET_MAP = {
        "spec-dock/docs/rules/initiative/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md"
        ),
        "spec-dock/docs/rules/initiative/epics.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md"
        ),
        "spec-dock/docs/rules/epic/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md"
        ),
        "spec-dock/docs/rules/epic/issues.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md"
        ),
        "spec-dock/docs/rules/issue/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"
        ),
    }
    _DOGFOODING_MIRROR_PROVIDER_ASSET_MAP = {
        "spec-dock/templates/README.md": "src/spec_dock/assets/spec_dock/templates/README.md",
        "spec-dock/scripts/README.md": "src/spec_dock/assets/spec_dock/scripts/README.md",
        "spec-dock/docs/workflow_initiative.md": (
            "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md"
        ),
        "spec-dock/docs/workflow_epic.md": "src/spec_dock/assets/spec_dock/docs/workflow_epic.md",
        "spec-dock/docs/workflow_issue.md": "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
        "spec-dock/docs/reference_github.md": (
            "src/spec_dock/assets/spec_dock/docs/reference_github.md"
        ),
        "spec-dock/docs/rules/initiative/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md"
        ),
        "spec-dock/docs/rules/initiative/epics.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md"
        ),
        "spec-dock/docs/rules/epic/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md"
        ),
        "spec-dock/docs/rules/epic/issues.md": "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md",
        "spec-dock/docs/rules/issue/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"
        ),
    }
    _DOGFOODING_RUNTIME_MIRROR_PROVIDER_ASSET_MAP = {
        "spec-dock/scripts/spec_dock_runtime/application/create_node.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/doctor.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/repo_context.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/sync_state.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/import_node.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/commands/new.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/commands/import_cmd.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/domain/validation.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/infra/git_cli.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py"
        ),
    }

    _CANONICAL_RULES_EXPECTATIONS = {
        "docs/rules/initiative/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには initiative に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --initiative <id> --title",
            ),
            "absent": (
                "--epic <id>",
                "--issue <id>",
            ),
        },
        "docs/rules/initiative/epics.md": {
            "contains": (
                "# epics/rules.md",
                "このディレクトリには initiative 配下の epic を作成します。",
                "Epic workflow: `spec-dock/docs/workflow_epic.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new epic --initiative <id> --title",
            ),
            "absent": (
                "--no-github",
                "new issue --epic",
                "new doc adr",
            ),
        },
        "docs/rules/epic/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには epic に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --epic <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "--issue <id>",
            ),
        },
        "docs/rules/epic/issues.md": {
            "contains": (
                "# issues/rules.md",
                "このディレクトリには epic 配下の issue を作成します。",
                "Issue workflow: `spec-dock/docs/workflow_issue.md`",
                "GitHub linkage: `spec-dock/docs/reference_github.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new issue --epic <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "new doc adr",
            ),
        },
        "docs/rules/issue/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには issue に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --issue <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "--epic <id>",
            ),
        },
    }

    def _assert_canonical_rules_files_contract(self, text_map: dict[str, str]) -> None:
        for rel_suffix, expected in self._CANONICAL_RULES_EXPECTATIONS.items():
            matching_paths = [path for path in text_map if path.endswith(rel_suffix)]
            self.assertEqual(
                len(matching_paths),
                1,
                f"expected exactly one canonical rules document for {rel_suffix}: {matching_paths}",
            )
            rel_path = matching_paths[0]
            text = text_map[rel_path]
            for fragment in expected["contains"]:
                self.assertIn(
                    fragment,
                    text,
                    f"expected canonical rules fragment missing from {rel_path}: {fragment}",
                )
            for fragment in expected["absent"]:
                self.assertNotIn(
                    fragment,
                    text,
                    f"unexpected canonical rules fragment present in {rel_path}: {fragment}",
                )

    def _assert_canonical_rules_files_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[1]
        for installed_rel_path, asset_rel_path in self._CANONICAL_RULES_PROVIDER_ASSET_MAP.items():
            installed_path = installed_base / installed_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(installed_path.is_file(), f"missing canonical rules file: {installed_path}")
            self.assertTrue(asset_path.is_file(), f"missing canonical rules asset: {asset_path}")
            self.assertEqual(
                installed_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"canonical rules file diverged from provider asset: {installed_rel_path}",
            )

    def _assert_checked_in_dogfooding_mirror_docs_match_provider_assets(self, repo_root: Path) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_MIRROR_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(mirror_path.is_file(), f"missing checked-in dogfooding mirror file: {mirror_path}")
            self.assertTrue(asset_path.is_file(), f"missing provider asset file: {asset_path}")
            self.assertEqual(
                mirror_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"checked-in dogfooding mirror file diverged from provider asset: {mirror_rel_path}",
            )

    def _assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(self, repo_root: Path) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_RUNTIME_MIRROR_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(mirror_path.is_file(), f"missing checked-in dogfooding runtime mirror file: {mirror_path}")
            self.assertTrue(asset_path.is_file(), f"missing provider runtime asset file: {asset_path}")
            self.assertEqual(
                mirror_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"checked-in dogfooding runtime mirror file diverged from provider asset: {mirror_rel_path}",
            )

    def _assert_installed_templates_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[1]
        mirror_root = installed_base / "spec-dock" / "templates"
        asset_root = repo_root / "src/spec_dock/assets/spec_dock/templates"

        mirror_entries = sorted(path.relative_to(mirror_root).as_posix() for path in mirror_root.rglob("*"))
        asset_entries = sorted(path.relative_to(asset_root).as_posix() for path in asset_root.rglob("*"))
        self.assertEqual(
            mirror_entries,
            asset_entries,
            "installed templates tree diverged from provider assets",
        )

        for rel_path in asset_entries:
            mirror_path = mirror_root / rel_path
            asset_path = asset_root / rel_path
            self.assertEqual(
                mirror_path.is_dir(),
                asset_path.is_dir(),
                f"installed templates entry kind diverged from provider asset: {rel_path}",
            )
            self.assertEqual(
                mirror_path.is_file(),
                asset_path.is_file(),
                f"installed templates entry kind diverged from provider asset: {rel_path}",
            )
            if asset_path.is_file():
                self.assertEqual(
                    mirror_path.read_text(encoding="utf-8"),
                    asset_path.read_text(encoding="utf-8"),
                    f"installed template diverged from provider asset: {rel_path}",
                )

    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            # Repo-root shortcut (best-effort; only assert when symlinks are supported).
            if self._can_create_symlink(target):
                self.assertTrue((target / "spec").is_symlink(), "repo-root shortcut missing: spec")

            self.assertTrue((target / "spec-dock" / "docs").is_dir())
            self.assertTrue((target / "spec-dock" / "templates").is_dir())
            self.assertTrue((target / "spec-dock" / "scripts").is_dir())
            self.assertTrue((target / "spec-dock" / "system").is_dir())
            self.assertTrue((target / "spec-dock" / "initiatives").is_dir())
            self.assertTrue((target / "spec-dock" / "active").is_dir())
            self.assertTrue((target / "spec-dock" / ".agent").is_dir())
            self.assertTrue((target / "spec-dock" / ".gitignore").is_file())
            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".agent/", gitignore)
            self.assertIn("active/", gitignore)

            docs_dir = target / "spec-dock" / "docs"
            self.assertTrue((docs_dir / "README.md").is_file())
            self.assertTrue((docs_dir / "guide.md").is_file())
            self.assertTrue((docs_dir / "workflow_initiative.md").is_file())
            self.assertTrue((docs_dir / "workflow_epic.md").is_file())
            self.assertTrue((docs_dir / "workflow_issue.md").is_file())
            self.assertTrue((docs_dir / "workflow_adr.md").is_file())
            self.assertTrue((docs_dir / "phase_requirement.md").is_file())
            self.assertTrue((docs_dir / "phase_design.md").is_file())
            self.assertTrue((docs_dir / "phase_plan.md").is_file())
            self.assertTrue((docs_dir / "reference_github.md").is_file())
            self.assertTrue((docs_dir / "reference_naming.md").is_file())
            self.assertTrue((docs_dir / "reference_sync.md").is_file())

            docs_readme = (docs_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("spec-driven-tdd-workflow", docs_readme)
            self.assertIn("spec-dock-initiative-planning", docs_readme)
            self.assertIn("spec-dock-epic-planning", docs_readme)
            self.assertIn("spec-dock-issue-execution", docs_readme)
            self.assertIn("spec-dock-adr-facilitation", docs_readme)
            self.assertIn("reference レイヤ", docs_readme)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", docs_readme)
            self.assertIn("[phase_design.md](phase_design.md)", docs_readme)
            self.assertIn("[phase_plan.md](phase_plan.md)", docs_readme)

            guide_text = (docs_dir / "guide.md").read_text(encoding="utf-8")
            self.assertIn("phase playbook（共通の作り方）", guide_text)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", guide_text)
            self.assertIn("[phase_design.md](phase_design.md)", guide_text)
            self.assertIn("[phase_plan.md](phase_plan.md)", guide_text)

            workflow_initiative = (docs_dir / "workflow_initiative.md").read_text(encoding="utf-8")
            workflow_epic = (docs_dir / "workflow_epic.md").read_text(encoding="utf-8")
            workflow_issue = (docs_dir / "workflow_issue.md").read_text(encoding="utf-8")
            workflow_adr = (docs_dir / "workflow_adr.md").read_text(encoding="utf-8")
            self.assertIn("spec-dock-initiative-planning", workflow_initiative)
            self.assertIn("spec-dock-epic-planning", workflow_epic)
            self.assertIn("spec-dock-issue-execution", workflow_issue)
            self.assertIn("spec-dock-adr-facilitation", workflow_adr)
            self.assertIn("plan upfront approval", workflow_issue)
            self.assertIn("step result approval", workflow_issue)
            self.assertIn("docs impact", workflow_issue)
            self.assertIn("final diff review quality gate", workflow_issue)
            self.assertIn("reviewer approval", workflow_issue)
            for command in (
                "./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title",
                "./spec-dock/scripts/spec-dock import issue <num|#num|canonical-url> --title",
                "./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url>",
                "./spec-dock/scripts/spec-dock active set --id <issue-id>",
                "./spec-dock/scripts/spec-dock active set --github-issue <n>",
                "./spec-dock/scripts/spec-dock active show",
                "./spec-dock/scripts/spec-dock deps check <target> --github",
                "./spec-dock/scripts/spec-dock active set <target> --github --force",
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync --github",
            ):
                self.assertIn(command, workflow_issue)
            self.assertNotIn("./spec ", workflow_issue)

            # v2 does not ship legacy docs/old/ (keep the published docs minimal).
            self.assertFalse((docs_dir / "old").exists())

            # Runtime script exists; legacy close scripts must not be present.
            scripts_dir = target / "spec-dock" / "scripts"
            self.assertTrue((scripts_dir / "spec-dock").is_file())
            self.assertEqual(list(scripts_dir.glob("spec-dock-close*.sh")), [])

            # Placeholders exist (active pointers must never be broken).
            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertTrue((placeholder_root / "initiative" / "README.md").is_file())
            self.assertTrue((placeholder_root / "epic" / "README.md").is_file())
            self.assertTrue((placeholder_root / "issue" / "README.md").is_file())
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)

            # Legacy (v1) templates should not be installed.
            templates_dir = target / "spec-dock" / "templates"
            self._assert_installed_templates_match_provider_assets(target)
            for legacy in ("requirement.md", "design.md", "plan.md", "report.md"):
                self.assertFalse((templates_dir / legacy).exists(), f"legacy template leaked: {legacy}")
            self.assertEqual(list(templates_dir.rglob("current")), [])
            self.assertEqual(list(templates_dir.rglob("completed")), [])

            # Issue templates should be sufficiently detailed (regression guard).
            initiative_templates_dir = templates_dir / "initiative"
            epic_templates_dir = templates_dir / "epic"
            issue_templates_dir = templates_dir / "issue"

            req_text = (issue_templates_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertIn("## 対象ユーザー / 利用シナリオ", req_text)
            self.assertIn("## 用語（ドメイン語彙）", req_text)
            for scope_templates in (
                initiative_templates_dir,
                epic_templates_dir,
                issue_templates_dir,
            ):
                self.assertFalse((scope_templates / "discussions" / "rules.md").exists())
                self.assertFalse((scope_templates / "adrs").exists())
                self.assertFalse((scope_templates / "artifacts").exists())
                self.assertEqual(list((scope_templates / "discussions").glob("new-*")), [])
            self.assertFalse((initiative_templates_dir / "epics" / "new-epic").exists())
            self.assertFalse((epic_templates_dir / "issues" / "new-issue").exists())
            self.assertFalse((initiative_templates_dir / "discussions" / "rules.md").exists())
            self.assertFalse((epic_templates_dir / "discussions" / "rules.md").exists())
            self.assertFalse((issue_templates_dir / "discussions" / "rules.md").exists())

            rules_dir = target / "spec-dock" / "docs" / "rules"
            self.assertTrue((rules_dir / "initiative" / "discussions.md").is_file())
            self.assertTrue((rules_dir / "initiative" / "epics.md").is_file())
            self.assertTrue((rules_dir / "epic" / "discussions.md").is_file())
            self.assertTrue((rules_dir / "epic" / "issues.md").is_file())
            self.assertTrue((rules_dir / "issue" / "discussions.md").is_file())

            discussions_templates_dir = templates_dir / "discussions"
            self.assertTrue((discussions_templates_dir / "adr.md").is_file())
            self.assertTrue((discussions_templates_dir / "note.md").is_file())
            self.assertTrue((discussions_templates_dir / "disc.md").is_file())
            self.assertTrue((discussions_templates_dir / "research.md").is_file())
            self.assertEqual(list(initiative_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(epic_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(issue_templates_dir.rglob("README.md")), [])

            design_text = (issue_templates_dir / "design.md").read_text(encoding="utf-8")
            # UML is embedded as small subsections (not a single block at the end).
            self.assertIn("```plantuml", design_text)
            self.assertIn("### UML（", design_text)

            plan_text = (issue_templates_dir / "plan.md").read_text(encoding="utf-8")
            self.assertIn("#### update_plan（着手時に登録）", plan_text)
            self.assertIn("./spec-dock/active/issue/report.md", plan_text)
            self.assertIn("## 実行ルール（全ステップ共通）", plan_text)
            self.assertIn("Red → Green → Refactor → review → fix → re-review → report → commit/no-op", plan_text)
            self.assertIn("S90 — docs impact resolution / docs refresh", plan_text)
            self.assertIn("S99 — final diff review quality gate", plan_text)
            self.assertIn("`git diff <base>...HEAD`", plan_text)
            self.assertIn("reviewer verdict", plan_text)

            report_text = (issue_templates_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## 遭遇した問題と解決", report_text)

            skills_root = target / ".agents" / "skills"
            self._assert_managed_skills_installed(target)

            skill_text = (skills_root / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`discussions/`", skill_text)
            self.assertIn("./spec-dock/scripts/spec-dock new doc adr --issue", skill_text)
            self.assertNotIn("adrs/new-adr", skill_text)
            self.assertFalse(
                (target / ".github" / "workflows" / "spec-dock-close.yml").exists()
            )

    def test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._assert_canonical_rules_files_match_provider_assets(target)

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/docs/rules/initiative/discussions.md",
                "spec-dock/docs/rules/initiative/epics.md",
                "spec-dock/docs/rules/epic/discussions.md",
                "spec-dock/docs/rules/epic/issues.md",
                "spec-dock/docs/rules/issue/discussions.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_canonical_rules_files_contract(text_map)
            self._assert_discussion_guidance_contract(text_map)

    def test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            corrupted_rules_text_map = {
                installed_rel_path: f"corrupted canonical rules guidance for {installed_rel_path}\n"
                for installed_rel_path in self._CANONICAL_RULES_PROVIDER_ASSET_MAP
            }
            for installed_rel_path, corrupted_rules_text in corrupted_rules_text_map.items():
                canonical_rules_path = target / installed_rel_path
                self._write_text_force(canonical_rules_path, corrupted_rules_text)
                self.assertEqual(
                    canonical_rules_path.read_text(encoding="utf-8"),
                    corrupted_rules_text,
                )

            self._write_text_force(
                target / "spec-dock" / "docs" / "workflow_adr.md",
                "./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title \"...\"\n",
            )
            legacy_template_text_map = {
                "spec-dock/templates/adr.md": "# legacy adr template\n",
                "spec-dock/templates/initiative/discussions/rules.md": (
                    "legacy naming: <type>-00001-<slug>.md\n"
                ),
                "spec-dock/templates/epic/discussions/rules.md": (
                    "legacy epic discussion rules\n"
                ),
                "spec-dock/templates/issue/discussions/rules.md": (
                    "legacy issue discussion rules\n"
                ),
                "spec-dock/templates/issue/discussions/_template.md": (
                    "# legacy discussion scaffold\n"
                ),
                "spec-dock/templates/initiative/epics/new-epic": "#!/bin/sh\n",
                "spec-dock/templates/epic/issues/new-issue": "#!/bin/sh\n",
            }
            for legacy_rel_path, legacy_text in legacy_template_text_map.items():
                legacy_path = target / legacy_rel_path
                legacy_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(legacy_path, legacy_text)
                self.assertTrue(legacy_path.is_file(), f"expected legacy template fixture: {legacy_rel_path}")
            self._write_text_force(
                target / "spec-dock" / "scripts" / "README.md",
                "legacy example: new adr --issue ...\n",
            )
            self._write_text_force(
                target / ".agents" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md",
                "legacy skill example: new adr --issue ...\n",
            )

            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_canonical_rules_files_match_provider_assets(target)
            self._assert_installed_templates_match_provider_assets(target)
            for installed_rel_path, corrupted_rules_text in corrupted_rules_text_map.items():
                self.assertNotEqual(
                    (target / installed_rel_path).read_text(encoding="utf-8"),
                    corrupted_rules_text,
                    f"canonical rules file was not refreshed: {installed_rel_path}",
                )
            for legacy_rel_path in legacy_template_text_map:
                self.assertFalse((target / legacy_rel_path).exists(), f"legacy template survived update: {legacy_rel_path}")

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/docs/rules/initiative/discussions.md",
                "spec-dock/docs/rules/initiative/epics.md",
                "spec-dock/docs/rules/epic/discussions.md",
                "spec-dock/docs/rules/epic/issues.md",
                "spec-dock/docs/rules/issue/discussions.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_canonical_rules_files_contract(text_map)
            self._assert_discussion_guidance_contract(text_map)

    def test_update_preserves_legacy_artifacts_inside_existing_node_trees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._write_text_force(
                target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                "corrupted managed rules\n",
            )
            managed_legacy_artifacts = {
                target / "spec-dock" / "templates" / "initiative" / "epics" / "new-epic": "#!/bin/sh\n",
                target / "spec-dock" / "templates" / "epic" / "issues" / "new-issue": "#!/bin/sh\n",
                target / "spec-dock" / "templates" / "issue" / "discussions" / "rules.md": (
                    "managed legacy rules\n"
                ),
            }
            for artifact_path, artifact_text in managed_legacy_artifacts.items():
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(artifact_path, artifact_text)

            node_root = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            node_legacy_artifacts = {
                node_root / "epics" / "new-epic": "node legacy wrapper\n",
                node_root / "epics" / "rules.md": "node legacy rules copy\n",
                node_root / "epics" / "epic-local-00001-jwt-auth" / "issues" / "new-issue": (
                    "node issue wrapper\n"
                ),
                node_root
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-refresh-token"
                / "discussions"
                / "rules.md": "node issue discussion rules copy\n",
            }
            for artifact_path, artifact_text in node_legacy_artifacts.items():
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(artifact_path, artifact_text)
                self.assertEqual(artifact_path.read_text(encoding="utf-8"), artifact_text)

            self.assertEqual(main(["update", str(target)]), 0)

            self._assert_canonical_rules_files_match_provider_assets(target)
            self._assert_installed_templates_match_provider_assets(target)
            for artifact_path in managed_legacy_artifacts:
                self.assertFalse(artifact_path.exists(), f"managed legacy artifact survived update: {artifact_path}")
            for artifact_path, artifact_text in node_legacy_artifacts.items():
                self.assertTrue(artifact_path.is_file(), f"node-tree artifact should be preserved: {artifact_path}")
                self.assertEqual(artifact_path.read_text(encoding="utf-8"), artifact_text)

    def test_current_guidance_documents_match_discussion_numbering_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        guidance_paths = [
            "src/spec_dock/assets/spec_dock/templates/README.md",
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md",
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md",
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/reference_naming.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_adr.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_epic.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md",
            "src/spec_dock/assets/spec_dock/docs/phase_requirement.md",
            "src/spec_dock/assets/spec_dock/docs/phase_design.md",
            "src/spec_dock/assets/spec_dock/docs/phase_plan.md",
            "src/spec_dock/assets/spec_dock/docs/README.md",
            "src/spec_dock/assets/spec_dock/docs/guide.md",
            "src/spec_dock/assets/spec_dock/scripts/README.md",
            "src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md",
        ]
        text_map = self._read_text_map(repo_root, guidance_paths)
        self._assert_canonical_rules_files_contract(text_map)
        self._assert_discussion_guidance_contract(text_map)

    def test_pyproject_excludes_deleted_wrapper_era_assets_from_package_data(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

        for package_data_pattern in _ISS_00031_EXCLUDE_PATTERNS:
            self.assertIn(
                f'"{package_data_pattern}"',
                pyproject_text,
                f"missing exclude-package-data guard for stale build artifact: {package_data_pattern}",
            )

    def test_built_wheel_excludes_deleted_wrapper_era_assets_from_stale_build_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"

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

            build_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    "--no-deps",
                    "--wheel-dir",
                    str(wheel_dir),
                    str(build_context),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                build_result.returncode,
                0,
                "expected local wheel build to succeed:\n"
                f"STDOUT:\n{build_result.stdout}\nSTDERR:\n{build_result.stderr}",
            )

            wheel_paths = list(wheel_dir.glob("*.whl"))
            self.assertEqual(len(wheel_paths), 1, f"expected one wheel, got: {wheel_paths}")

            with zipfile.ZipFile(wheel_paths[0]) as wheel_zip:
                wheel_entries = set(wheel_zip.namelist())

            self.assertIn(
                "spec_dock/assets/spec_dock/templates/README.md",
                wheel_entries,
                "sanity check failed: built wheel did not include expected live template asset",
            )
            for stale_rel_path in _ISS_00031_STALE_WHEEL_PATHS:
                self.assertNotIn(
                    stale_rel_path,
                    wheel_entries,
                    f"built wheel unexpectedly shipped stale build artifact: {stale_rel_path}",
                )

    def test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(runtime_script.is_file(), f"dogfooding runtime script missing: {runtime_script}")

        doctor_help = subprocess.run(
            [sys.executable, str(runtime_script), "doctor", "--help"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            doctor_help.returncode,
            0,
            msg=(
                "checked-in dogfooding runtime must expose 'doctor'\n"
                f"stdout:\n{doctor_help.stdout}\n"
                f"stderr:\n{doctor_help.stderr}\n"
            ),
        )
        self.assertIn("usage: spec-dock/scripts/spec-dock doctor", doctor_help.stdout)

        legacy_active = subprocess.run(
            [sys.executable, str(runtime_script), "active", "set", "--initiative", "1"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(legacy_active.returncode, 2)
        self.assertIn("'active set' supports explicit targets:", legacy_active.stderr)
        self.assertIn("active set --id <node-id>", legacy_active.stderr)

    def test_checked_in_dogfooding_mirror_docs_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_checked_in_dogfooding_mirror_docs_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_mirror_templates_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_installed_templates_match_provider_assets(repo_root, repo_root=repo_root)

    def test_checked_in_dogfooding_runtime_mirror_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_release_lock_backward_compat_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
    assert issue_gateway.calls == [(str(repo_root), 555, None)], issue_gateway.calls
    assert sum(1 for record in node_repo.records if record.id == "iss-00555") == 1, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_parent_fallback_reresolve_inside_lock_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
    def __init__(self, records):
        self.records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
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
        _record(
            kind="epic",
            node_id="epic-local-00002",
            title="Session rotation",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00002-session-rotation",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

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
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        active_state_store=active_state_store,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    captured = {{"resolve_calls": 0}}
    original_resolve_parent_from_active = app_import_node.resolve_parent_from_active
    original_sync_after_import = app_import_node.sync_after_import
    def _drifting_resolve_parent_from_active(graph, child_kind, active):
        del graph, active
        assert child_kind == "issue", child_kind
        captured["resolve_calls"] += 1
        if captured["resolve_calls"] == 1:
            return "epic-local-00001"
        return "epic-local-00002"
    app_import_node.resolve_parent_from_active = _drifting_resolve_parent_from_active
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        result = app_import_node.import_issue(
            app_contracts.ImportNodeRequest(
                issue_number=777,
                title="Parent drift import",
                slug=None,
                parent_id=None,
            ),
            ports,
        )
    finally:
        app_import_node.resolve_parent_from_active = original_resolve_parent_from_active
        app_import_node.sync_after_import = original_sync_after_import

    assert captured["resolve_calls"] == 2, captured
    assert result.node.parent_id == "epic-local-00002", result.node.parent_id
    assert "/epic-local-00002-session-rotation/" in result.node.path.as_posix(), result.node.path
    assert issue_gateway.calls == [(str(repo_root), 777, None)], issue_gateway.calls
    assert [name for name, _path in active_state_store.calls] == [
        "load_active_manifest_no_migrate",
        "load_active_manifest_no_migrate",
    ], active_state_store.calls
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_active_deps_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
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
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

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

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    current_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert current_status.effective_status == "open"
    assert deps_result.inspection.evaluation.ready is True
    assert deps_result.inspection.evaluation.guard_reason == "ready"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "other/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_non_issue_deps_target_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_issue_create_lock_scope_narrowing_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, %r)
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
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
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

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _FailingTemplateScaffolder(_StubTemplateScaffolder):
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
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
                    requested_node_id=None,
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
                requested_node_id=None,
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
                    requested_node_id=None,
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
                requested_node_id=None,
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
                    requested_node_id=None,
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
                requested_node_id=None,
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
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00815`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
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

    with patch.object(
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
                    requested_node_id=None,
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

    with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
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

    with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
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
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00817`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
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

    with patch.object(
        app_create_node,
        "_post_write_duplicate_guard",
        side_effect=RuntimeError("simulated post-write duplicate guard failure"),
    ):
        with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
            try:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        requested_node_id=None,
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
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_issue_create_pre_github_validation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, %r)
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
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
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
            "requested-id-with-github-mode",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-00001",
                "requested_node_id": "iss-local-00100",
            },
            "Cannot combine '--id' with GitHub-backed node creation",
        ),
        (
            "missing-epic",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": None,
                "requested_node_id": None,
            },
            "--epic is required",
        ),
        (
            "partial-repo-identity",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-00001",
                "requested_node_id": None,
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
                "requested_node_id": None,
            },
            "Initiative not found: init-local-99999",
        ),
        (
            "missing-epic-node",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-99999",
                "requested_node_id": None,
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
            "requested_node_id": None,
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
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_non_issue_create_guidance_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, %r)
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
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
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
                requested_node_id=None,
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
    with patch.object(app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated epic write failure")):
        try:
            app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="JWT auth",
                    slug=None,
                    parent_id="init-local-00001",
                    requested_node_id=None,
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
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_create_mode_graph_preflight_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, %r)
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
                requested_node_id=None,
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
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_same_repo_index_missing_view_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
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
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": ["iss-local-00001"]}},
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
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

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
            title="Current Repo Scoped",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo-scoped",
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
            title="Target",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-target",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Current repo #301",
                labels=["done"],
                updated_at="2026-03-19T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
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

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert deps_result.inspection.evaluation.ready is True
    dep_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert dep_status.source == "github"
    assert dep_status.effective_status == "done"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "current/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_sync_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_active_deps_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
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
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

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

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"
    assert issue_gateway.view_calls == [
        (str(repo_root), 101, "current/repo"),
        (str(repo_root), 201, "current/repo"),
    ]

    for target_id, expected_status in (
        ("init-local-00001", "open"),
        ("epic-local-00001", "done"),
    ):
        issue_gateway.view_calls.clear()
        deps_result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id=target_id, github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )
        target_status = deps_result.inspection.issue_statuses[target_id]
        assert target_status.source == "github"
        assert target_status.effective_status == expected_status
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_numeric_branch_current_repo_overlap_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
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
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_tool_version_fallback_reads_pyproject(self) -> None:
        import spec_dock.cli as cli

        expected = _expected_spec_dock_version()
        old_version = getattr(cli, "__version__", None)
        old_file = getattr(cli, "__file__", None)
        try:
            cli.__version__ = "0.0.0+unknown"
            repo_root = Path(__file__).resolve().parents[1]
            cli.__file__ = str(repo_root / "src" / "spec_dock" / "cli.py")
            self.assertEqual(cli._tool_version(), expected)
        finally:
            if old_version is not None:
                cli.__version__ = old_version
            if old_file is not None:
                cli.__file__ = old_file

    def test_no_skill_option_is_rejected(self) -> None:
        import spec_dock.cli as cli

        with self.assertRaises(SystemExit) as cm:
            cli._parse_args(["init", "--no-skill", "."])
        self.assertEqual(cm.exception.code, 2)

    def test_update_migrates_legacy_single_skill_and_preserves_custom_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            skills_root = target / ".agents" / "skills"
            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                if skill_name == "spec-driven-tdd-workflow":
                    continue
                shutil.rmtree(skills_root / skill_name)

            custom_dir = skills_root / "my-custom-skill"
            custom_dir.mkdir(parents=True, exist_ok=True)
            (custom_dir / "SKILL.md").write_text("# custom\n", encoding="utf-8")
            (custom_dir / "notes.txt").write_text("keep\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)
            self.assertTrue((custom_dir / "SKILL.md").is_file())
            self.assertTrue((custom_dir / "notes.txt").is_file())

    def test_update_installs_full_skill_set_for_legacy_no_skill_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            skills_root = target / ".agents" / "skills"

            self.assertEqual(main(["init", str(target)]), 0)
            shutil.rmtree(skills_root)
            self.assertFalse(skills_root.exists())
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                shutil.rmtree(skills_root / skill_name)
            self.assertEqual(list(skills_root.glob("*")), [])
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_update_skill_sync_converges_after_interrupted_run(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            original_copy_file = cli._copy_file
            failed_once = False

            def interrupted_copy(src: Path, dest: Path) -> None:
                nonlocal failed_once
                if (
                    not failed_once
                    and dest.as_posix().endswith("/.agents/skills/spec-dock-epic-planning/SKILL.md")
                ):
                    failed_once = True
                    raise RuntimeError("simulated skill sync interruption")
                original_copy_file(src, dest)

            cli._copy_file = interrupted_copy
            try:
                self.assertEqual(main(["update", str(target)]), 1)
            finally:
                cli._copy_file = original_copy_file

            self.assertTrue(failed_once)
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_bundled_skill_assets_cover_managed_manifest(self) -> None:
        import spec_dock.cli as cli

        self.assertEqual(cli._managed_skill_names(), _EXPECTED_MANAGED_SKILL_NAMES)
        with cli._assets_dir() as assets_dir:
            for skill_name in cli._managed_skill_names():
                skill_path = assets_dir / "codex_skills" / skill_name / "SKILL.md"
                self.assertTrue(skill_path.is_file(), f"missing bundled skill asset: {skill_path}")

    def test_bundled_skill_routing_contract(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            skills_dir = assets_dir / "codex_skills"
            hub_text = (skills_dir / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            initiative_text = (skills_dir / "spec-dock-initiative-planning" / "SKILL.md").read_text(encoding="utf-8")
            epic_text = (skills_dir / "spec-dock-epic-planning" / "SKILL.md").read_text(encoding="utf-8")
            issue_text = (skills_dir / "spec-dock-issue-execution" / "SKILL.md").read_text(encoding="utf-8")
            adr_text = (skills_dir / "spec-dock-adr-facilitation" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(
            "`spec-dock-initiative-planning`: initiative-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-epic-planning`: epic-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-issue-execution`: issue-level TDD execution and report updates.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-adr-facilitation`: ADR drafting/decision facilitation linked to the current workflow.",
            hub_text,
        )
        self.assertIn("`spec-dock/docs/reference_github.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", hub_text)
        self.assertIn("`spec-dock/active/context-pack.md`", hub_text)

        self.assertIn("`spec-dock/docs/workflow_initiative.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", initiative_text)
        self.assertIn("create/import an initiative", initiative_text)
        self.assertIn("scope-specific constraints and decisions", initiative_text)

        self.assertIn("`spec-dock/docs/workflow_epic.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", epic_text)
        self.assertIn("create/import an epic", epic_text)
        self.assertIn("scope-specific constraints and decisions", epic_text)

        self.assertIn("`spec-dock/docs/workflow_issue.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", issue_text)
        self.assertIn("`spec-dock/active/context-pack.md`", issue_text)
        self.assertIn("implement the active issue via TDD", issue_text)
        self.assertIn("source of truth", issue_text)
        self.assertIn("docs impact resolution step", issue_text)
        self.assertIn("final diff review quality gate", issue_text)

        self.assertIn("`spec-dock/docs/workflow_adr.md`", adr_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", adr_text)
        self.assertIn("Return to the current parent workflow", adr_text)
        self.assertIn("create/update an ADR", adr_text)

        for skill_text in (hub_text, initiative_text, epic_text, issue_text, adr_text):
            self.assertNotIn("runtime-operations", skill_text)

    def test_init_fails_without_force_when_spec_dock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Second init without --force should fail.
            self.assertNotEqual(main(["init", str(target)]), 0)

    def test_update_keeps_initiatives_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            marker = target / "spec-dock" / "initiatives" / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")

            # Simulate legacy (v1) leftovers that v2 should prune on update.
            legacy_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            legacy_workflow.parent.mkdir(parents=True, exist_ok=True)
            legacy_workflow.write_text("legacy\n", encoding="utf-8")

            legacy_symlink = target / "spec-dock" / "current-initiative"
            created_symlink = False
            try:
                # v1 style link target (so v2 can safely prune without deleting v2-generated shortcuts).
                os.symlink("initiative/current", legacy_symlink)
                created_symlink = True
            except OSError:
                # Some environments may restrict symlinks; workflow pruning is still validated.
                created_symlink = False

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(marker.is_file())
            self._assert_version_file(target)
            self.assertFalse(legacy_workflow.exists())
            if created_symlink:
                self.assertFalse(legacy_symlink.is_symlink())

    def _clear_active_entrypoints(self, target: Path) -> Path:
        active_dir = target / "spec-dock" / "active"
        for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
            p = active_dir / name
            if p.is_symlink() or p.is_file():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                shutil.rmtree(p)
        self.assertEqual(list(active_dir.iterdir()), [])
        return active_dir

    def _overlay_checked_in_dogfooding_runtime(self, target: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        checked_in_scripts_dir = repo_root / "spec-dock" / "scripts"
        target_scripts_dir = target / "spec-dock" / "scripts"
        self.assertTrue(checked_in_scripts_dir.is_dir(), f"checked-in scripts dir missing: {checked_in_scripts_dir}")
        self.assertTrue(target_scripts_dir.is_dir(), f"target scripts dir missing: {target_scripts_dir}")

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
        self.assertTrue((initiative_dir / ".meta.json").is_file())
        self.assertTrue((epic_dir / ".meta.json").is_file())
        self.assertTrue((issue_dir / ".meta.json").is_file())
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
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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
            self.assertEqual(
                import_result.returncode,
                0,
                msg=f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}",
            )
            self.assertIn("spec-dock: ok (import issue)", import_result.stdout)
            self.assertNotIn("import_post_sync_failed", import_result.stderr)
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())

    def test_checked_in_dogfooding_runtime_subprocess_issue_create_gateway_failure_pre_github_parity(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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
            self.assertEqual(
                create_result.returncode,
                1,
                msg=f"new issue stdout:\n{create_result.stdout}\nnew issue stderr:\n{create_result.stderr}",
            )
            self.assertIn("Outcome: pre_github_fail", create_result.stderr)
            self.assertNotIn("GitHub issue was created:", create_result.stderr)

            after_issue_dirs = sorted(p.name for p in issues_dir.iterdir() if p.is_dir())
            self.assertEqual(after_issue_dirs, before_issue_dirs)
            self.assertFalse(any(name.endswith("-gateway-failure-issue") for name in after_issue_dirs))

            gh_calls = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(gh_calls), 1, msg=f"unexpected gh calls: {gh_calls}")
            self.assertEqual(gh_calls[0], "issue create", msg=f"unexpected gh calls: {gh_calls}")

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

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
            self._write_json_force(
                depends_issue_dir / "deps.json",
                {"schema_version": 1, "depends_on": [123]},
            )

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003", "--json"],
            )
            self.assertEqual(
                deps_result.returncode,
                3,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            payload = json.loads(deps_result.stdout)
            self.assertEqual(payload.get("effective_depends_on"), ["iss-local-00001"])
            self.assertEqual(payload.get("blockers"), ["iss-local-00001"])
            self.assertNotIn("Ambiguous github.issue_number=123", deps_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_repo_scoped_url_target_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123, "repo_owner": "current", "repo_name": "repo"}
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

            ambiguous_active = self._run_runtime_capture(target, ["active", "set", "123", "--force"])
            self.assertEqual(
                ambiguous_active.returncode,
                1,
                msg=f"active(ambiguous) stdout:\n{ambiguous_active.stdout}\nactive(ambiguous) stderr:\n{ambiguous_active.stderr}",
            )
            self.assertIn("Ambiguous github.issue_number=123", ambiguous_active.stderr)

            scoped_active = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/other/repo/issues/123", "--force"],
            )
            self.assertEqual(
                scoped_active.returncode,
                0,
                msg=f"active(scoped) stdout:\n{scoped_active.stdout}\nactive(scoped) stderr:\n{scoped_active.stderr}",
            )
            self.assertIn("spec-dock: ok (active set)", scoped_active.stdout)

            active_manifest = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_manifest["issue"]["id"], "iss-local-00002")

            scoped_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/other/repo/issues/123", "--json"],
            )
            self.assertIn(
                scoped_deps.returncode,
                (0, 3),
                msg=f"deps(scoped) stdout:\n{scoped_deps.stdout}\ndeps(scoped) stderr:\n{scoped_deps.stderr}",
            )
            self.assertIn('"target": "iss-local-00002"', scoped_deps.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_current_repo_url_target_resolves_unscoped_current_parity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

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

            active_current = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/current/repo/issues/123", "--force"],
            )
            self.assertEqual(
                active_current.returncode,
                0,
                msg=f"active(current) stdout:\n{active_current.stdout}\nactive(current) stderr:\n{active_current.stderr}",
            )
            active_manifest = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_manifest["issue"]["id"], "iss-local-00001")

            deps_current = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/current/repo/issues/123", "--json"],
            )
            self.assertIn(
                deps_current.returncode,
                (0, 3),
                msg=f"deps(current) stdout:\n{deps_current.stdout}\ndeps(current) stderr:\n{deps_current.stderr}",
            )
            self.assertIn('"target": "iss-local-00001"', deps_current.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

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
                with self.subTest(dep_ref=dep_ref):
                    self._write_json_force(
                        depends_issue_dir / "deps.json",
                        {"schema_version": 1, "depends_on": [dep_ref]},
                    )
                    deps_result = self._run_runtime_capture(
                        target,
                        ["deps", "check", "--id", "iss-local-00003", "--json"],
                    )
                    self.assertEqual(
                        deps_result.returncode,
                        3,
                        msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
                    )
                    payload = json.loads(deps_result.stdout)
                    self.assertEqual(payload.get("effective_depends_on"), [expected_dep])
                    self.assertEqual(payload.get("blockers"), [expected_dep])

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, _current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

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
            self._write_json_force(
                depends_issue_dir / "deps.json",
                {"schema_version": 1, "depends_on": [123]},
            )

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003"],
            )
            self.assertEqual(
                deps_result.returncode,
                1,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            self.assertIn(
                "No node found for github.issue_number=123 in current repo scope (current/repo)",
                deps_result.stderr,
            )
            self.assertIn("Create/link the node first.", deps_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_keeps_sync_deps_active_validate_doctor_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            deps_result = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-local-00001"])
            self.assertIn(
                deps_result.returncode,
                (0, 3),
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            self.assertTrue(
                "spec-dock: ok (deps check)" in deps_result.stdout
                or "spec-dock: blocked (deps check)" in deps_result.stderr,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )

            active_result = self._run_runtime_capture(target, ["active", "set", "--id", "iss-local-00001", "--force"])
            self.assertEqual(
                active_result.returncode,
                0,
                msg=f"active stdout:\n{active_result.stdout}\nactive stderr:\n{active_result.stderr}",
            )
            self.assertIn("spec-dock: ok (active set)", active_result.stdout)

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                0,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("spec-dock: ok (doctor) findings=0", doctor_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_keeps_lone_unscoped_legacy_without_backfill_parity(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

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
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])

    def test_checked_in_dogfooding_runtime_subprocess_keeps_readonly_lone_unscoped_without_backfill_parity(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

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
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])
            self.assertEqual(current_meta_path.stat().st_mode & 0o222, 0)

    def test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("epic missing parent_id", validate_result.stderr)
            self.assertNotIn("Missing required artifact", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("epic missing parent_id", doctor_result.stderr)
            self.assertNotIn("Missing required artifact", doctor_result.stderr)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed: Missing required artifact", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertNotIn("spec-dock: ok (sync)", sync_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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
            self.assertEqual(
                import_result.returncode,
                1,
                msg=f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}",
            )
            self.assertIn("preflight validate failed", import_result.stderr)
            self.assertIn("Missing required artifact", import_result.stderr)
            self.assertIn("report.md", import_result.stderr)
            self.assertFalse(
                (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-local-00001-auth-platform"
                    / "epics"
                    / "epic-local-00001-jwt-auth"
                    / "issues"
                    / "iss-00123-imported-issue"
                ).exists()
            )
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

    def test_checked_in_dogfooding_runtime_subprocess_import_partial_write_doctor_first_parity(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime import app as runtime_app
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import import_node as app_import_node
finally:
    sys.path.pop(0)

os.chdir({str(target)!r})
stderr_buffer = io.StringIO()
with patch.object(
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
            self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)
            agent_dir = target / "spec-dock" / ".agent"

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertTrue(
                "deps_preflight_failed" in sync_result.stderr or "DEPS_DISABLED" in sync_result.stderr,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

    def test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
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

            sync_result = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("Missing required artifact", validate_result.stderr)
            self.assertIn("design.md", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("[missing_artifact] Missing required artifact", doctor_result.stderr)
            self.assertIn("design.md", doctor_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)

            meta_path = issue_dir / ".meta.json"
            meta_path.chmod(meta_path.stat().st_mode | 0o200)
            meta_path.unlink()

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=active",
                        "pid=1234",
                        "user=tester",
                        "created_unix=9999999999",
                        "created_iso=2286-11-20T17:46:39Z",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            validate_in_progress = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_in_progress.returncode,
                1,
                msg=f"validate(in_progress) stdout:\n{validate_in_progress.stdout}\nvalidate(in_progress) stderr:\n{validate_in_progress.stderr}",
            )
            self.assertIn("Create in-progress state detected", validate_in_progress.stderr)
            self.assertNotIn("Missing required artifact", validate_in_progress.stderr)

            sync_in_progress = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_in_progress.returncode,
                1,
                msg=f"sync(in_progress) stdout:\n{sync_in_progress.stdout}\nsync(in_progress) stderr:\n{sync_in_progress.stderr}",
            )
            self.assertIn("Create in-progress state detected", sync_in_progress.stderr)

            doctor_in_progress = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_in_progress.returncode,
                1,
                msg=f"doctor(in_progress) stdout:\n{doctor_in_progress.stdout}\ndoctor(in_progress) stderr:\n{doctor_in_progress.stderr}",
            )
            self.assertIn("[stale_create_lock]", doctor_in_progress.stderr)
            self.assertIn("Create in-progress state detected", doctor_in_progress.stderr)
            self.assertNotIn("[missing_artifact]", doctor_in_progress.stderr)

            lock_path.write_text(
                "\n".join(
                    [
                        "token=stale",
                        "pid=4321",
                        "user=tester",
                        "created_unix=0",
                        "created_iso=1970-01-01T00:00:00Z",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            validate_stale = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_stale.returncode,
                1,
                msg=f"validate(stale) stdout:\n{validate_stale.stdout}\nvalidate(stale) stderr:\n{validate_stale.stderr}",
            )
            self.assertIn("Stale create-lock state detected", validate_stale.stderr)
            self.assertNotIn("Missing required artifact", validate_stale.stderr)

            sync_stale = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertEqual(
                sync_stale.returncode,
                1,
                msg=f"sync(stale) stdout:\n{sync_stale.stdout}\nsync(stale) stderr:\n{sync_stale.stderr}",
            )
            self.assertIn("Stale create-lock state detected", sync_stale.stderr)

            doctor_stale = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_stale.returncode,
                1,
                msg=f"doctor(stale) stdout:\n{doctor_stale.stdout}\ndoctor(stale) stderr:\n{doctor_stale.stderr}",
            )
            self.assertIn("[stale_create_lock]", doctor_stale.stderr)
            self.assertIn("Stale create-lock state detected", doctor_stale.stderr)
            self.assertNotIn("[missing_artifact]", doctor_stale.stderr)

    def test_update_rebuilds_active_entrypoints_from_persisted_manifest_when_valid_and_active_dir_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_rebuilds_placeholder_symlink_entrypoints_from_persisted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                pathfile = active_dir / f"{layer}.path"
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                pathfile.unlink(missing_ok=True)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                os.symlink(rel_placeholder, link)
                self.assertTrue(link.is_symlink())

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    self.assertTrue(link.exists())
                    self.assertEqual(link.resolve(), expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_rebuilds_placeholder_pathfile_entrypoints_from_persisted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_placeholder + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    if link.exists():
                        self.assertEqual(link.resolve(), expected.resolve())
                    else:
                        self.assertTrue(pathfile.is_file())
                        resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                        self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_mixed_entrypoints_keep_healthy_real_and_rebuild_placeholder_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)

            (active_dir / "initiative.path").write_text(
                os.path.relpath(initiative_dir, start=active_dir) + "\n",
                encoding="utf-8",
            )
            (active_dir / "epic.path").write_text(
                os.path.relpath(placeholder_root / "epic", start=active_dir) + "\n",
                encoding="utf-8",
            )
            (active_dir / "issue.path").write_text(
                os.path.relpath(placeholder_root / "issue", start=active_dir) + "\n",
                encoding="utf-8",
            )

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)

    def test_update_keeps_placeholder_and_none_context_pack_when_persisted_manifest_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_placeholder + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/README.md`", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_rewrites_stale_context_pack_when_rebuilding_active_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            # Simulate partial deletion: entrypoints disappeared but stale context-pack remains.
            for name in ("initiative", "epic", "issue", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.write_text(
                "# Context Pack (stale)\n\n## Active\n- initiative: (none)\n- epic: (none)\n- issue: (none)\n",
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_entrypoints_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            active_dir = target / "spec-dock" / "active"
            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_skips_persisted_target_resolution_when_active_entrypoints_are_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            with patch(
                "spec_dock.cli._resolve_manifest_target_dir",
                side_effect=AssertionError("healthy active entrypoint should skip persisted target resolution"),
            ):
                self.assertEqual(main(["update", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)

    def test_update_regenerates_context_pack_from_existing_active_entrypoints_when_manifest_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            active_dir = target / "spec-dock" / "active"
            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_pathfiles_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            for layer, node_dir in (
                ("initiative", initiative_dir),
                ("epic", epic_dir),
                ("issue", issue_dir),
            ):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_target = os.path.relpath(node_dir, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_recovers_active_entrypoints_from_id_when_persisted_paths_are_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, _issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-00001", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-00001",
                        "path": "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": (
                            "spec-dock/initiatives/init-local-00001-auth-platform/epics/"
                            "epic-local-00001-jwt-auth/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "requirement.md"))

    def test_update_falls_back_to_placeholder_when_persisted_active_manifest_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_falls_back_to_placeholder_when_persisted_path_points_to_same_layer_wrong_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            wrong_issue_dir = issue_dir.parent / "iss-local-00002-other-issue"
            wrong_issue_dir.mkdir(parents=True, exist_ok=True)
            self._write_json_force(
                wrong_issue_dir / ".meta.json",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00002",
                    "title": "Other issue",
                    "slug": "other-issue",
                    "parent_id": "epic-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": "epic-local-00001",
                },
            )
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                (wrong_issue_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": wrong_issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertNotIn("iss-local-00002", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_prefers_id_based_recovery_when_same_layer_wrong_id_path_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            wrong_issue_dir = issue_dir.parent / "iss-local-00002-other-issue"
            wrong_issue_dir.mkdir(parents=True, exist_ok=True)
            self._write_json_force(
                wrong_issue_dir / ".meta.json",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00002",
                    "title": "Other issue",
                    "slug": "other-issue",
                    "parent_id": "epic-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": "epic-local-00001",
                },
            )
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                (wrong_issue_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": wrong_issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "requirement.md"))
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-00002", context_pack_text)

    def test_update_bootstraps_active_fallback_entrypoints_when_active_dir_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])
            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)

    def test_update_regenerates_context_pack_from_persisted_active_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_bootstraps_active_path_files_when_active_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_rebuilds_active_path_files_from_persisted_manifest_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_repairs_stale_active_path_files_to_persisted_targets_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

    def test_update_repairs_stale_active_path_files_to_placeholder_when_persisted_manifest_broken_and_symlink_creation_fails(
        self,
    ) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent == active_dir and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_prefers_existing_active_entrypoints_over_stale_persisted_manifest_for_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            # Keep healthy entrypoints via pathfiles, then inject stale persisted ids.
            entry_targets = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, target_dir in entry_targets.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    if link.is_symlink() or link.is_file():
                        link.unlink(missing_ok=True)
                    elif link.is_dir():
                        shutil.rmtree(link)
                    rel_target = os.path.relpath(target_dir, start=active_dir)
                    (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_prefers_real_pathfile_entrypoint_over_placeholder_symlink_when_manifest_is_stale(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            placeholder_root = specdock_dir / "system" / "active-none"

            entry_targets = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, target_dir in entry_targets.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    if link.is_symlink() or link.is_file():
                        link.unlink(missing_ok=True)
                    elif link.is_dir():
                        shutil.rmtree(link)
                    rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                    os.symlink(rel_placeholder, link)
                    rel_real = os.path.relpath(target_dir, start=active_dir)
                    (active_dir / f"{layer}.path").write_text(rel_real + "\n", encoding="utf-8")

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_ids = {
                "initiative": "init-local-00001",
                "epic": "epic-local-00001",
                "issue": "iss-local-00001",
            }
            for layer, expected_id in expected_ids.items():
                with self.subTest(layer=layer):
                    pointer = active_dir / layer
                    self.assertTrue(pointer.is_symlink())
                    self.assertEqual(pointer.resolve(), entry_targets[layer].resolve())

                    resolved = cli._resolve_existing_active_entrypoint(
                        specdock_dir,
                        active_dir=active_dir,
                        layer=layer,
                    )
                    self.assertIsNotNone(resolved)
                    if resolved is None:
                        continue
                    self.assertEqual(resolved[1], expected_id)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- epic: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_same_layer_non_symlink_file_conflict_using_real_pathfile_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            issue_link = active_dir / "issue"
            issue_pathfile = active_dir / "issue.path"

            if issue_link.is_symlink() or issue_link.is_file():
                issue_link.unlink(missing_ok=True)
            elif issue_link.is_dir():
                shutil.rmtree(issue_link)
            issue_pathfile.unlink(missing_ok=True)

            issue_pathfile.write_text(os.path.relpath(issue_dir, start=active_dir) + "\n", encoding="utf-8")
            issue_link.write_text("stale non-symlink conflict\n", encoding="utf-8")
            self.assertTrue(issue_link.exists())
            self.assertFalse(issue_link.is_symlink())

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            if issue_link.exists():
                self.assertTrue(issue_link.is_symlink())
                self.assertEqual(issue_link.resolve(), issue_dir.resolve())
            else:
                self.assertTrue(issue_pathfile.is_file())
                rel_target = issue_pathfile.read_text(encoding="utf-8").strip()
                self.assertEqual((active_dir / rel_target).resolve(), issue_dir.resolve())
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_same_layer_invalid_directory_conflict_using_real_pathfile_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            placeholder_root = specdock_dir / "system" / "active-none"
            issue_link = active_dir / "issue"
            issue_pathfile = active_dir / "issue.path"

            if issue_link.is_symlink() or issue_link.is_file():
                issue_link.unlink(missing_ok=True)
            elif issue_link.is_dir():
                shutil.rmtree(issue_link)
            issue_pathfile.unlink(missing_ok=True)

            issue_link.mkdir(parents=True, exist_ok=True)
            (issue_link / "report.md").write_text("stale invalid directory conflict\n", encoding="utf-8")
            self.assertFalse((issue_link / ".meta.json").exists())
            issue_pathfile.write_text(
                os.path.relpath(placeholder_root / "issue", start=active_dir) + "\n",
                encoding="utf-8",
            )
            self.assertTrue(issue_link.exists())
            self.assertFalse(issue_link.is_symlink())

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            if issue_link.exists():
                self.assertTrue(issue_link.is_symlink())
                self.assertEqual(issue_link.resolve(), issue_dir.resolve())
            else:
                self.assertTrue(issue_pathfile.is_file())
                rel_target = issue_pathfile.read_text(encoding="utf-8").strip()
                self.assertEqual((active_dir / rel_target).resolve(), issue_dir.resolve())
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_dangling_active_symlink_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            pointer = active_dir / "initiative"
            pointer.unlink(missing_ok=True)
            os.symlink("../system/active-none/missing-initiative", pointer)
            self.assertTrue(pointer.is_symlink())
            self.assertFalse(pointer.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder = target / "spec-dock" / "system" / "active-none" / "initiative" / "README.md"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                placeholder.read_text(encoding="utf-8"),
            )
