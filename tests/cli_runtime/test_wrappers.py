import os
from pathlib import Path
import re
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliRulesContract(CliRuntimeHarness):
    def test_new_nodes_create_rules_symlinks_and_no_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
                assert link_path.is_symlink(), f"missing rules symlink: {link_path}"
                assert link_path.resolve() == target_path.resolve()
                assert str(link_path.readlink()) == os.path.relpath(target_path, start=link_path.parent)

            assert not (init_dir / "epics" / "new-epic").exists()
            assert not (epic_dir / "issues" / "new-issue").exists()
            assert list((init_dir / "epics").glob("new-*")) == []
            assert list((epic_dir / "issues").glob("new-*")) == []

    def test_scaffold_docs_point_to_runtime_commands_and_rules_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            hub_skill = (
                target / ".agents" / "skills" / "spec-dock-hub" / "SKILL.md"
            ).read_text(encoding="utf-8")
            issue_skill = (
                target / ".agents" / "skills" / "spec-dock-issue-execution" / "SKILL.md"
            ).read_text(encoding="utf-8")
            issue_planning_skill = (
                target / ".agents" / "skills" / "spec-dock-issue-planning" / "SKILL.md"
            ).read_text(encoding="utf-8")
            codex_adapter_skill = (
                target / ".agents" / "skills" / "spec-dock-codex-adapter" / "SKILL.md"
            ).read_text(encoding="utf-8")
            copilot_adapter_skill = (
                target / ".agents" / "skills" / "spec-dock-copilot-adapter" / "SKILL.md"
            ).read_text(encoding="utf-8")

            assert "`spec-dock/docs/rules/**`" in templates_readme
            assert "`rules.md` symlink" in templates_readme
            assert "./spec-dock/scripts/spec-dock" in templates_readme
            assert "./spec " not in templates_readme
            assert "epics/new-epic" not in templates_readme
            assert "issues/new-issue" not in templates_readme

            assert "`spec-dock/docs/rules/initiative/epics.md`" in workflow_initiative
            assert "`./spec-dock/scripts/spec-dock new epic --initiative <initiative-id> --title \"...\"`" in workflow_initiative
            assert "./spec-dock/scripts/spec-dock validate" in workflow_initiative
            assert "./spec-dock/scripts/spec-dock sync" in workflow_initiative
            assert "./spec " not in workflow_initiative
            assert "epics/new-epic" not in workflow_initiative

            assert "`spec-dock/docs/rules/epic/issues.md`" in workflow_epic
            assert "`./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"`" in workflow_epic
            assert "./spec-dock/scripts/spec-dock validate" in workflow_epic
            assert "./spec-dock/scripts/spec-dock sync" in workflow_epic
            assert "./spec " not in workflow_epic
            assert "issues/new-issue" not in workflow_epic

            for command in (
                "./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title \"...\"",
                (
                    "./spec-dock/scripts/spec-dock new issue --create-github-issue --epic "
                    "<epic-id> --title \"...\""
                ),
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync",
            ):
                assert command in workflow_issue
            assert "spec-dock-issue-planning" in workflow_issue
            assert "spec-dock-issue-execution" in workflow_issue
            assert "workflow_spec_authoring.md" in issue_planning_skill
            assert "workflow_clarification.md" in issue_planning_skill
            assert "workflow_issue.md" in issue_planning_skill
            assert "./spec " not in workflow_issue
            assert "issues/new-issue" not in workflow_issue
            assert "./spec-dock/scripts/spec-dock new issue --no-github --epic <epic-id> --title \"...\"" not in workflow_issue

            assert "`spec-dock/docs/rules/**`" in reference_github
            assert "`--no-github` は node creation option ではありません" in reference_github
            assert "`--create-github-issue`" in reference_github
            assert "`--github-issue <n>`" in reference_github
            assert "./spec-dock/scripts/spec-dock" in reference_github
            assert "./spec " not in reference_github
            assert "issues/new-issue" not in reference_github

            for text, expected_command in (
                (
                    initiative_epics_rules,
                    "`./spec-dock/scripts/spec-dock new epic --initiative <id> --title \"<title>\"`",
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
                assert "spec-dock/docs/" in text
                assert expected_command in text
                assert "./spec " not in text
            for skill_text in (hub_skill, issue_skill, codex_adapter_skill, copilot_adapter_skill):
                assert "./spec-dock/scripts/spec-dock" in skill_text
                assert "./spec " not in skill_text
            assert "name: spec-dock-hub" in hub_skill
            assert "SpecDock Hub" in hub_skill
            assert "route selector" in hub_skill
            assert "global invariant" in hub_skill

            assert "./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>" in issue_skill
            assert "./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>" in issue_skill
            assert "./spec-dock/scripts/spec-dock deps check <target>" in issue_skill
            assert "./spec-dock/scripts/spec-dock validate" in issue_skill
            assert "./spec-dock/scripts/spec-dock sync" in issue_skill
            assert "--no-github" in issue_skill

            for skill_text in (hub_skill, codex_adapter_skill, copilot_adapter_skill):
                assert "./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>" not in skill_text
                assert "./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>" not in skill_text
                assert "./spec-dock/scripts/spec-dock deps check <target>" not in skill_text
                assert "./spec-dock/scripts/spec-dock validate" not in skill_text
                assert "./spec-dock/scripts/spec-dock sync" not in skill_text

            assert "`spec-dock/docs/reference_deps.md`" in hub_skill
            assert "`spec-dock/docs/reference_sync.md`" in hub_skill
            assert "`spec-dock/docs/reference_deps.md`" in codex_adapter_skill
            assert "`spec-dock/docs/reference_sync.md`" in codex_adapter_skill
            assert "`spec-dock/docs/reference_deps.md`" in copilot_adapter_skill
            assert "`spec-dock/docs/reference_sync.md`" in copilot_adapter_skill

            assert "--no-github" not in initiative_epics_rules

    def test_new_doc_numbering_and_validate_ignore_initiative_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])

            initiative_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            discussions_dir = initiative_dir / "discussions"
            rules_target = target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"

            rules_link = discussions_dir / "rules.md"
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()

            self._run_runtime(target, ["new", "doc", "adr", "--initiative", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--initiative", "1", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in discussions_dir.iterdir()) == sorted([adr_files[0].name, disc_files[0].name, "rules.md"])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_new_doc_numbering_and_validate_ignore_epic_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()

            self._run_runtime(target, ["new", "doc", "adr", "--epic", "2", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--epic", "2", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in discussions_dir.iterdir()) == sorted([adr_files[0].name, disc_files[0].name, "rules.md"])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_new_doc_numbering_and_validate_ignore_issue_discussion_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

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
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()

            self._run_runtime(target, ["new", "doc", "adr", "--issue", "3", "--title", "Decision one"])
            self._run_runtime(target, ["new", "doc", "disc", "--issue", "3", "--title", "Why now"])

            adr_files = sorted(discussions_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(discussions_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in discussions_dir.iterdir()) == sorted([adr_files[0].name, disc_files[0].name, "rules.md"])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_runtime_entrypoint_fails_fast_when_runtime_module_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            runtime_app = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py"
            runtime_backup = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "app.py.bak"
            runtime_app.rename(runtime_backup)

            p = self._run_runtime_capture(target, ["sync"])
            assert p.returncode != 0
            assert "runtime module missing" in p.stderr
            assert "spec-dock update" in p.stderr
