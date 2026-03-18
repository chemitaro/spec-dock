import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)


class TestInitUpdate(CliRuntimeHarness):
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
                self.assertTrue((scope_templates / "discussions" / "rules.md").is_file())
                self.assertFalse((scope_templates / "adrs").exists())
                self.assertFalse((scope_templates / "artifacts").exists())
                self.assertEqual(list((scope_templates / "discussions").glob("new-*")), [])

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

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/templates/initiative/discussions/rules.md",
                "spec-dock/templates/epic/discussions/rules.md",
                "spec-dock/templates/issue/discussions/rules.md",
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
            self._assert_discussion_guidance_contract(text_map)

    def test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._write_text_force(
                target / "spec-dock" / "docs" / "workflow_adr.md",
                "./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title \"...\"\n",
            )
            self._write_text_force(
                target / "spec-dock" / "templates" / "initiative" / "discussions" / "rules.md",
                "legacy naming: <type>-00001-<slug>.md\n",
            )
            self._write_text_force(
                target / "spec-dock" / "scripts" / "README.md",
                "legacy example: new adr --issue ...\n",
            )
            self._write_text_force(
                target / ".agents" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md",
                "legacy skill example: new adr --issue ...\n",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/templates/initiative/discussions/rules.md",
                "spec-dock/templates/epic/discussions/rules.md",
                "spec-dock/templates/issue/discussions/rules.md",
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
            self._assert_discussion_guidance_contract(text_map)

    def test_current_guidance_documents_match_discussion_numbering_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        guidance_paths = [
            "src/spec_dock/assets/spec_dock/templates/README.md",
            "src/spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md",
            "src/spec_dock/assets/spec_dock/templates/epic/discussions/rules.md",
            "src/spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
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
            "spec-deps/current/discussions/rules.md",
            "spec-deps/README.md",
        ]
        text_map = self._read_text_map(repo_root, guidance_paths)
        self._assert_discussion_guidance_contract(text_map)

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

            initiative_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = initiative_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
            issue_dir.mkdir(parents=True, exist_ok=True)

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

            context_pack_path = target / "spec-dock" / "active" / "context-pack.md"
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
