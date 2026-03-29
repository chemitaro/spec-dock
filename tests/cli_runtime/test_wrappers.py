import os
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliRulesContract(CliRuntimeHarness):
    def test_new_nodes_create_rules_symlinks_and_no_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            init_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-00002-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-00003-add-refresh-token"
            expected_rules_links = {
                init_dir / "epics" / "rules.md": target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                init_dir / "discussions" / "rules.md": (
                    target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
                ),
                epic_dir / "issues" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md",
                epic_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md",
                issue_dir / "discussions" / "rules.md": target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md",
            }
            for link_path, target_path in expected_rules_links.items():
                self.assertTrue(link_path.is_symlink(), f"missing rules symlink: {link_path}")
                self.assertEqual(link_path.resolve(), target_path.resolve())
                self.assertEqual(os.readlink(link_path), os.path.relpath(target_path, start=link_path.parent))

            self.assertFalse((init_dir / "epics" / "new-epic").exists())
            self.assertFalse((epic_dir / "issues" / "new-issue").exists())
            self.assertEqual(list((init_dir / "epics").glob("new-*")), [])
            self.assertEqual(list((epic_dir / "issues").glob("new-*")), [])

    def test_scaffold_docs_point_to_runtime_commands_and_rules_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            templates_readme = (target / "spec-dock" / "templates" / "README.md").read_text(encoding="utf-8")
            workflow_initiative = (
                target / "spec-dock" / "docs" / "workflow_initiative.md"
            ).read_text(encoding="utf-8")
            workflow_epic = (target / "spec-dock" / "docs" / "workflow_epic.md").read_text(
                encoding="utf-8"
            )
            workflow_issue = (target / "spec-dock" / "docs" / "workflow_issue.md").read_text(
                encoding="utf-8"
            )
            reference_github = (target / "spec-dock" / "docs" / "reference_github.md").read_text(
                encoding="utf-8"
            )
            initiative_epics_rules = (
                target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md"
            ).read_text(encoding="utf-8")
            initiative_discussions_rules = (
                target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
            ).read_text(encoding="utf-8")
            epic_issues_rules = (
                target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md"
            ).read_text(encoding="utf-8")
            epic_discussions_rules = (
                target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md"
            ).read_text(encoding="utf-8")
            issue_discussions_rules = (
                target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md"
            ).read_text(encoding="utf-8")

            self.assertIn("`spec-dock/docs/rules/**`", templates_readme)
            self.assertIn("`rules.md` symlink", templates_readme)
            self.assertIn("./spec-dock/scripts/spec-dock", templates_readme)
            self.assertNotIn("./spec ", templates_readme)
            self.assertNotIn("epics/new-epic", templates_readme)
            self.assertNotIn("issues/new-issue", templates_readme)

            self.assertIn("`spec-dock/docs/rules/initiative/epics.md`", workflow_initiative)
            self.assertIn(
                "`./spec-dock/scripts/spec-dock new epic --initiative <initiative-id> --title \"...\"`",
                workflow_initiative,
            )
            self.assertIn("./spec-dock/scripts/spec-dock validate", workflow_initiative)
            self.assertIn("./spec-dock/scripts/spec-dock sync", workflow_initiative)
            self.assertNotIn("./spec ", workflow_initiative)
            self.assertNotIn("epics/new-epic", workflow_initiative)

            self.assertIn("`spec-dock/docs/rules/epic/issues.md`", workflow_epic)
            self.assertIn(
                "`./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"`",
                workflow_epic,
            )
            self.assertIn("./spec-dock/scripts/spec-dock validate", workflow_epic)
            self.assertIn("./spec-dock/scripts/spec-dock sync", workflow_epic)
            self.assertNotIn("./spec ", workflow_epic)
            self.assertNotIn("issues/new-issue", workflow_epic)

            for command in (
                "./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"",
                (
                    "./spec-dock/scripts/spec-dock new issue --create-github-issue --epic "
                    "<epic-id> --title \"...\""
                ),
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync --github",
            ):
                self.assertIn(command, workflow_issue)
            self.assertNotIn("./spec ", workflow_issue)
            self.assertNotIn("issues/new-issue", workflow_issue)
            self.assertNotIn(
                "./spec-dock/scripts/spec-dock new issue --no-github --epic <epic-id> --title \"...\"",
                workflow_issue,
            )

            self.assertIn("`spec-dock/docs/rules/**`", reference_github)
            self.assertIn(
                "`--no-github` は compatibility option として残っていますが、contract error で reject されます",
                reference_github,
            )
            self.assertIn("`--create-github-issue`", reference_github)
            self.assertIn("`--github-issue <n>`", reference_github)
            self.assertIn("./spec-dock/scripts/spec-dock", reference_github)
            self.assertNotIn("./spec ", reference_github)
            self.assertNotIn("issues/new-issue", reference_github)

            for text, expected_command in (
                (
                    initiative_epics_rules,
                    "`./spec-dock/scripts/spec-dock new epic --initiative <id> --title \"<title>\" --no-github`",
                ),
                (
                    initiative_discussions_rules,
                    "`./spec-dock/scripts/spec-dock new doc adr --initiative <id> --title \"<title>\"`",
                ),
                (
                    epic_issues_rules,
                    "`./spec-dock/scripts/spec-dock new issue --epic <id> --title \"<title>\"`",
                ),
                (
                    epic_discussions_rules,
                    "`./spec-dock/scripts/spec-dock new doc adr --epic <id> --title \"<title>\"`",
                ),
                (
                    issue_discussions_rules,
                    "`./spec-dock/scripts/spec-dock new doc adr --issue <id> --title \"<title>\"`",
                ),
            ):
                self.assertIn("spec-dock/docs/", text)
                self.assertIn(expected_command, text)
                self.assertNotIn("./spec ", text)

    def test_new_doc_numbering_and_validate_ignore_initiative_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])

            initiative_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            discussions_dir = initiative_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"

            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--initiative", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--initiative", "1", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            self.assertEqual(len(adr_files), 1)
            self.assertEqual(len(disc_files), 1)
            self.assertRegex(adr_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$")
            self.assertRegex(disc_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$")
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                sorted([adr_files[0].name, disc_files[0].name, "rules.md"]),
            )

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

    def test_new_doc_numbering_and_validate_ignore_epic_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
            )
            discussions_dir = epic_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md"
            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--epic", "2", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--epic", "2", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            self.assertEqual(len(adr_files), 1)
            self.assertEqual(len(disc_files), 1)
            self.assertRegex(adr_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$")
            self.assertRegex(disc_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$")
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                sorted([adr_files[0].name, disc_files[0].name, "rules.md"]),
            )

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

    def test_new_doc_numbering_and_validate_ignore_issue_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md"
            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "3", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "3", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            self.assertEqual(len(adr_files), 1)
            self.assertEqual(len(disc_files), 1)
            self.assertRegex(adr_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$")
            self.assertRegex(disc_files[0].name, r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$")
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                sorted([adr_files[0].name, disc_files[0].name, "rules.md"]),
            )

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

    def test_runtime_entrypoint_fails_fast_when_runtime_module_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            runtime_app = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py"
            runtime_backup = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py.bak"
            runtime_app.rename(runtime_backup)

            p = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("runtime module missing", p.stderr)
            self.assertIn("spec-dock update", p.stderr)
