import os
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliRulesContract(CliRuntimeHarness):
    def test_new_nodes_create_rules_symlinks_and_no_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
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
            self.assertIn("入口/ナビゲーション用", templates_readme)
            self.assertIn("サポートされた実行経路", templates_readme)
            self.assertNotIn("正本は runtime command と", templates_readme)
            self.assertNotIn("wrapper", templates_readme)
            self.assertNotIn("new-epic", templates_readme)
            self.assertNotIn("new-issue", templates_readme)

            self.assertIn("`epics/rules.md`", workflow_initiative)
            self.assertIn("`spec-dock/docs/rules/initiative/epics.md`", workflow_initiative)
            self.assertIn(
                "`./spec-dock/scripts/spec-dock new epic --initiative <initiative-id> --title \"...\"`",
                workflow_initiative,
            )
            self.assertIn("への入口", workflow_initiative)
            self.assertIn("正本は後者", workflow_initiative)
            self.assertIn("./spec-dock/scripts/spec-dock validate", workflow_initiative)
            self.assertIn("./spec-dock/scripts/spec-dock sync", workflow_initiative)
            self.assertNotIn("この組み合わせを正本とする", workflow_initiative)
            self.assertNotIn("./spec ", workflow_initiative)
            self.assertNotIn("wrapper", workflow_initiative)
            self.assertNotIn("new-epic", workflow_initiative)

            self.assertIn("`issues/rules.md`", workflow_epic)
            self.assertIn("`spec-dock/docs/rules/epic/issues.md`", workflow_epic)
            self.assertIn(
                "`./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"`",
                workflow_epic,
            )
            self.assertIn("への入口", workflow_epic)
            self.assertIn("正本は後者", workflow_epic)
            self.assertIn("./spec-dock/scripts/spec-dock validate", workflow_epic)
            self.assertIn("./spec-dock/scripts/spec-dock sync", workflow_epic)
            self.assertNotIn("この組み合わせを正本とする", workflow_epic)
            self.assertNotIn("./spec ", workflow_epic)
            self.assertNotIn("wrapper", workflow_epic)
            self.assertNotIn("new-issue", workflow_epic)

            for command in (
                "./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"",
                (
                    "./spec-dock/scripts/spec-dock new issue --create-github-issue --epic "
                    "<epic-id> --title \"...\""
                ),
                "./spec-dock/scripts/spec-dock new issue --no-github --epic <epic-id> --title \"...\"",
                (
                    "./spec-dock/scripts/spec-dock import issue <num|#num|canonical-url> "
                    "--title \"...\" [--epic <epic-id>] [--allow-foreign-url]"
                ),
                "./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url>",
                "./spec-dock/scripts/spec-dock active set --id <issue-id>",
                "./spec-dock/scripts/spec-dock active set --github-issue <n>",
                (
                    "./spec-dock/scripts/spec-dock active set "
                    "<issue-id|github-issue-number|url> --checkout"
                ),
                "./spec-dock/scripts/spec-dock active show",
                "`./spec-dock/scripts/spec-dock deps check <target> --github`",
                "`./spec-dock/scripts/spec-dock active set <target> --github --force`",
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync --github",
            ):
                self.assertIn(command, workflow_issue)
            self.assertIn("plan upfront approval", workflow_issue)
            self.assertIn("step result approval", workflow_issue)
            self.assertIn("docs impact", workflow_issue)
            self.assertIn("final diff review quality gate", workflow_issue)
            self.assertNotIn("./spec ", workflow_issue)

            self.assertIn("`spec-dock/docs/rules/**`", reference_github)
            self.assertIn(
                "`./spec-dock/scripts/spec-dock new issue --no-github --epic <id> --title \"...\"`",
                reference_github,
            )
            self.assertIn("`--create-github-issue`", reference_github)
            self.assertIn("`--github-issue <n>`", reference_github)
            self.assertIn("入口/ナビゲーション用", reference_github)
            self.assertIn("サポートされた実行経路", reference_github)
            self.assertIn("`./spec-dock/scripts/spec-dock validate` / `./spec-dock/scripts/spec-dock sync`", reference_github)
            self.assertNotIn("正本は runtime command と", reference_github)
            self.assertNotIn("./spec ", reference_github)
            self.assertNotIn("wrapper", reference_github)
            self.assertNotIn("new-issue", reference_github)

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
                self.assertIn("リポジトリ root から実行してください", text)
                self.assertIn("nested directory では相対 path が変わります", text)
                self.assertIn(expected_command, text)
                self.assertNotIn("./spec ", text)

    def test_new_doc_numbering_and_validate_ignore_initiative_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])

            initiative_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            discussions_dir = initiative_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"

            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--initiative", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--initiative", "1", "--title", "Why now"])

            self.assertTrue((discussions_dir / "001-adr-decision-one.md").is_file())
            self.assertTrue((discussions_dir / "002-disc-why-now.md").is_file())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                ["001-adr-decision-one.md", "002-disc-why-now.md", "rules.md"],
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])

            epic_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
            )
            discussions_dir = epic_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md"
            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--epic", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--epic", "1", "--title", "Why now"])

            self.assertTrue((discussions_dir / "001-adr-decision-one.md").is_file())
            self.assertTrue((discussions_dir / "002-disc-why-now.md").is_file())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                ["001-adr-decision-one.md", "002-disc-why-now.md", "rules.md"],
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
            )
            discussions_dir = issue_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md"
            rules_link = discussions_dir / "rules.md"
            self.assertTrue(rules_link.is_symlink(), f"missing rules symlink: {rules_link}")
            self.assertEqual(rules_link.resolve(), rules_target.resolve())

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "1", "--title", "Why now"])

            self.assertTrue((discussions_dir / "001-adr-decision-one.md").is_file())
            self.assertTrue((discussions_dir / "002-disc-why-now.md").is_file())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.iterdir()),
                ["001-adr-decision-one.md", "002-disc-why-now.md", "rules.md"],
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
