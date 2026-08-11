import os
from pathlib import Path
import re
import shutil
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliRulesContract(CliRuntimeHarness):
    def test_scaffolded_pr_merge_preparer_uses_evidence_gated_repair_continuation_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            skill = (target / ".agents" / "skills" / "github-pr-merge-preparer" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            skill_template = (
                target / ".agents" / "skills" / "github-pr-merge-preparer" / "templates" / "pr-repair-batch.md"
            ).read_text(encoding="utf-8")
            artifact_template = (target / "spec-dock" / "templates" / "artifacts" / "pr-repair-batch.md").read_text(
                encoding="utf-8"
            )
            discussion_template = (target / "spec-dock" / "templates" / "discussions" / "pr-repair-batch.md").read_text(
                encoding="utf-8"
            )

            installed_surfaces = (skill, skill_template, artifact_template, discussion_template)
            template_surfaces = (skill_template, artifact_template, discussion_template)
            normalized_surfaces = tuple(" ".join(text.split()) for text in installed_surfaces)
            normalized_template_surfaces = tuple(" ".join(text.split()) for text in template_surfaces)
            required_markers = (
                "ChatGPT Consultation Gate",
                "Integrated Repair Strategy",
                "Iteration Ledger",
                "strategy_delta",
                "orchestrator_disposition",
                "telemetry only",
            )
            missing_by_surface = {
                index: [marker for marker in required_markers if marker not in normalized]
                for index, normalized in enumerate(normalized_surfaces)
                if any(marker not in normalized for marker in required_markers)
            }
            forbidden_markers = (
                "Default autonomous repair limit is one repair attempt",
                "Default autonomous repair limit is two repair attempts",
                "Default total autonomous repair limit is four repair attempts",
                "Loop limits for the same failure class or total repair attempts are reached.",
                "Loop limits for the same root-cause family or total repair attempts are reached.",
                "same `root_cause_family` appears after a repair commit",
                "same `root_cause_family` reappears after a repair commit",
            )
            forbidden_by_surface = {
                index: [marker for marker in forbidden_markers if marker in normalized]
                for index, normalized in enumerate(normalized_surfaces)
                if any(marker in normalized for marker in forbidden_markers)
            }
            assert not missing_by_surface and not forbidden_by_surface, (
                f"missing evidence-gated markers by installed surface: {missing_by_surface}; "
                f"legacy stop-authority markers by installed surface: {forbidden_by_surface}"
            )

            fallback_binding_markers = (
                "bound_strategy_context",
                "fallback_invocation_id",
                "fallback_approved_by",
                "fallback_approved_at",
                "fallback_manual_analysis_ref",
                "fallback_consumed_at",
            )
            missing_fallback_bindings = {
                index: [marker for marker in fallback_binding_markers if marker not in normalized]
                for index, normalized in enumerate(normalized_template_surfaces)
                if any(marker not in normalized for marker in fallback_binding_markers)
            }
            assert not missing_fallback_bindings, (
                f"missing one-invocation fallback bindings by installed template surface: {missing_fallback_bindings}"
            )

            for index, normalized in enumerate(normalized_template_surfaces):
                for state in ("fresh", "stale", "failed", "unavailable", "consultation_denied", "unsafe"):
                    assert state in normalized, f"missing consultation state {state!r} in template surface {index}"
                assert "refresh" in normalized and "hard-unrecoverable" in normalized, (
                    f"template surface {index} must require stale refresh-first and permit fallback only after "
                    "hard-unrecoverable consultation/recovery"
                )
                for marker in (
                    "`fallback_approval_denied` is an unconditional stop.",
                    "An expired or consumed fallback approval is an unconditional stop.",
                    "A fallback approval is bound to exactly one `fallback_invocation_id` and must not be reused.",
                    "advisory evidence",
                    "orchestrator",
                    "material `strategy_delta`",
                ):
                    assert marker in normalized, (
                        f"missing semantic fallback/authority marker {marker!r} in surface {index}"
                    )
                assert "repair unit is incomplete or repeatedly fails" not in normalized, (
                    f"template surface {index} retains an unconditional failure-count stop"
                )

            # Existing hard human gates and non-blocking / forbidden-write boundaries remain intact.
            for marker in (
                "permission_or_auth",
                "external_or_flaky",
                "base_branch_conflict",
                "requirement expansion",
                "breaking change",
                "migration",
                "secret/deployment setting change",
                "ambiguous review intent",
                "Do not mutate the PR branch solely to record those findings.",
                "PR merge.",
                "Auto-merge enablement.",
                "Branch deletion.",
                "Review thread resolve.",
            ):
                assert marker in skill

            assert artifact_template == discussion_template
            artifact_help = self._run_runtime_capture(target, ["new", "artifact", "--help"]).stdout
            assert "--consultation" not in artifact_help
            assert "--strategy" not in artifact_help

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
                init_dir / "artifacts" / "rules.md": (
                    target / "spec-dock" / "docs" / "rules" / "initiative" / "artifacts.md"
                ),
                epic_dir / "issues" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md",
                epic_dir / "artifacts" / "rules.md": target / "spec-dock" / "docs" / "rules" / "epic" / "artifacts.md",
                issue_dir / "artifacts" / "rules.md": target
                / "spec-dock"
                / "docs"
                / "rules"
                / "issue"
                / "artifacts.md",
            }
            for link_path, target_path in expected_rules_links.items():
                assert link_path.is_symlink(), f"missing rules symlink: {link_path}"
                assert link_path.resolve() == target_path.resolve()
                assert str(link_path.readlink()) == os.path.relpath(target_path, start=link_path.parent)

            assert not (init_dir / "epics" / "new-epic").exists()
            assert not (epic_dir / "issues" / "new-issue").exists()
            assert list((init_dir / "epics").glob("new-*")) == []
            assert list((epic_dir / "issues").glob("new-*")) == []
            assert not (init_dir / "discussions").exists()
            assert not (epic_dir / "discussions").exists()
            assert not (issue_dir / "discussions").exists()

    def test_scaffold_docs_point_to_runtime_commands_and_rules_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            templates_readme = (target / "spec-dock" / "templates" / "README.md").read_text(encoding="utf-8")
            workflow_initiative = (target / "spec-dock" / "docs" / "workflow_initiative.md").read_text(encoding="utf-8")
            workflow_epic = (target / "spec-dock" / "docs" / "workflow_epic.md").read_text(encoding="utf-8")
            workflow_issue = (target / "spec-dock" / "docs" / "workflow_issue.md").read_text(encoding="utf-8")
            docs_readme = (target / "spec-dock" / "docs" / "README.md").read_text(encoding="utf-8")
            reference_github = (target / "spec-dock" / "docs" / "reference_github.md").read_text(encoding="utf-8")
            initiative_epics_rules = (target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md").read_text(
                encoding="utf-8"
            )
            initiative_discussions_rules = (
                target / "spec-dock" / "docs" / "rules" / "initiative" / "discussions.md"
            ).read_text(encoding="utf-8")
            initiative_artifacts_rules = (
                target / "spec-dock" / "docs" / "rules" / "initiative" / "artifacts.md"
            ).read_text(encoding="utf-8")
            epic_issues_rules = (target / "spec-dock" / "docs" / "rules" / "epic" / "issues.md").read_text(
                encoding="utf-8"
            )
            epic_discussions_rules = (target / "spec-dock" / "docs" / "rules" / "epic" / "discussions.md").read_text(
                encoding="utf-8"
            )
            epic_artifacts_rules = (target / "spec-dock" / "docs" / "rules" / "epic" / "artifacts.md").read_text(
                encoding="utf-8"
            )
            issue_discussions_rules = (target / "spec-dock" / "docs" / "rules" / "issue" / "discussions.md").read_text(
                encoding="utf-8"
            )
            issue_artifacts_rules = (target / "spec-dock" / "docs" / "rules" / "issue" / "artifacts.md").read_text(
                encoding="utf-8"
            )
            hub_skill = (target / ".agents" / "skills" / "spec-dock-hub" / "SKILL.md").read_text(encoding="utf-8")
            issue_skill = (target / ".agents" / "skills" / "spec-dock-issue-execution" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            issue_planning_skill = (target / ".agents" / "skills" / "spec-dock-issue-planning" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            initiative_planning_skill = (
                target / ".agents" / "skills" / "spec-dock-initiative-planning" / "SKILL.md"
            ).read_text(encoding="utf-8")
            epic_planning_skill = (target / ".agents" / "skills" / "spec-dock-epic-planning" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            chatgpt_authoring_skill = (
                target / ".agents" / "skills" / "spec-dock-chatgpt-authoring" / "SKILL.md"
            ).read_text(encoding="utf-8")
            codex_adapter_skill = (target / ".agents" / "skills" / "spec-dock-codex-adapter" / "SKILL.md").read_text(
                encoding="utf-8"
            )
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
            assert (
                '`./spec-dock/scripts/spec-dock new epic --initiative <initiative-id> --title "..."`'
                in workflow_initiative
            )
            assert "./spec-dock/scripts/spec-dock validate" in workflow_initiative
            assert "./spec-dock/scripts/spec-dock sync" in workflow_initiative
            assert "./spec " not in workflow_initiative
            assert "epics/new-epic" not in workflow_initiative

            assert "`spec-dock/docs/rules/epic/issues.md`" in workflow_epic
            assert '`./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title "..."`' in workflow_epic
            assert "./spec-dock/scripts/spec-dock validate" in workflow_epic
            assert "./spec-dock/scripts/spec-dock sync" in workflow_epic
            assert "./spec " not in workflow_epic
            assert "issues/new-issue" not in workflow_epic

            for command in (
                './spec-dock/scripts/spec-dock new issue --epic <epic-id> --title "..."',
                ('./spec-dock/scripts/spec-dock new issue --create-github-issue --epic <epic-id> --title "..."'),
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync",
            ):
                assert command in workflow_issue
            assert "spec-dock-issue-planning" in workflow_issue
            assert "spec-dock-issue-execution" in workflow_issue
            assert "spec-dock-chatgpt-authoring" in docs_readme
            assert "spec-dock-chatgpt-authoring" in hub_skill
            assert "workflow_spec_authoring.md" in issue_planning_skill
            assert "workflow_issue.md" in issue_planning_skill
            assert "name: spec-dock-chatgpt-authoring" in chatgpt_authoring_skill
            assert "evidence-only" in chatgpt_authoring_skill
            assert "github-synced" in chatgpt_authoring_skill
            assert "local-context" in chatgpt_authoring_skill
            assert "must not claim" in chatgpt_authoring_skill
            assert "reviewer pass" in chatgpt_authoring_skill
            assert "merge-ready" in chatgpt_authoring_skill
            branch_section = chatgpt_authoring_skill.split("Choose exactly one branch:", 1)[1].split(
                "Evaluate an import result", 1
            )[0]
            branch_bullets = [line for line in branch_section.splitlines() if line.startswith("- ")]
            assert len(branch_bullets) == 4
            preservation_bullets = {line.removeprefix("- ").split(":", 1)[0]: line for line in branch_bullets}
            expected_branch_headings = {
                "Complete standalone Markdown",
                "Complete received inline answer",
                "Genuinely incomplete or unavailable inline output",
                "ZIP/tree output",
            }
            assert set(preservation_bullets) == expected_branch_headings
            standalone = preservation_bullets["Complete standalone Markdown"]
            for token in (
                "Workbench",
                "explicitly runs `artifact import chatgpt-output`",
                "verifies the receipt",
                "`imported_byte_exact`",
                "only from the Workbench source to the imported Artifact",
            ):
                assert token in standalone
            inline = preservation_bullets["Complete received inline answer"]
            for token in (
                "captures only the complete answer text",
                "without adding, removing, reformatting, or normalizing content",
                "explicitly imports it",
                "`captured_received_text`",
                "never claim identity with provider-original bytes",
                "wrapper transcript containing prompts or metadata",
            ):
                assert token in inline
            unavailable = preservation_bullets["Genuinely incomplete or unavailable inline output"]
            for token in (
                "`skipped_inline_unavailable`",
                "reason, decision owner, nonblocking rationale, and next action or revisit condition",
                "Do not record source/destination paths, hashes, byte counts, or a byte-exact claim",
            ):
                assert token in unavailable
            zip_tree = preservation_bullets["ZIP/tree output"]
            for token in (
                "review, quarantine, stage, and validation lane",
                "Do not convert it to single-file import",
                "weaken existing ZIP safety checks",
            ):
                assert token in zip_tree

            import_result_bullets = [
                line for line in chatgpt_authoring_skill.splitlines() if line.startswith("- `committed=")
            ]
            assert len(import_result_bullets) == 2
            import_pass = next(line for line in import_result_bullets if "with no warning" in line)
            for token in (
                "`committed=true`",
                "final repo-relative path",
                "SHA-256",
                "byte count",
                "`import_kind=chatgpt-output`",
                "`storage_identity=blank`",
                "preservation result is `pass`",
            ):
                assert token in import_pass
            import_warning = next(
                line for line in chatgpt_authoring_skill.splitlines() if line.startswith("- The same complete receipt")
            )
            for token in (
                "complete receipt",
                "`committed=true`",
                "warning",
                "`pass-with-warning`",
                "retain the warning",
                "do not retry automatically",
                "duplicate import",
            ):
                assert token in import_warning
            import_block = next(line for line in import_result_bullets if "`committed=false`" in line)
            for token in (
                "missing receipt field",
                "eligibility failure",
                "unresolved semantic completeness",
                "block adoption and canonical rewrite",
            ):
                assert token in import_block
            failed_import = next(
                line
                for line in chatgpt_authoring_skill.splitlines()
                if line.startswith("- Never reclassify a complete source whose import failed")
            )
            assert "`skipped_inline_unavailable`" in failed_import
            for forbidden_claim in (
                "canonical adoption completed",
                "`.assurance.json` mutation",
                "reviewer pass, including fresh `spec-reviewer`, `code-reviewer`, or `qa-reviewer` pass",
                "execution-ready",
                "PR-ready",
                "merge-ready",
                "Issue finish",
                "Epic completion",
                "PR delivery",
            ):
                assert forbidden_claim in chatgpt_authoring_skill
            for planning_skill in (initiative_planning_skill, epic_planning_skill, issue_planning_skill):
                assert (
                    "Immediately after output is received, and before claim review, Evidence Adoption Ledger "
                    "disposition, or canonical rewrite, invoke the shared `spec-dock-chatgpt-authoring` "
                    "preservation checkpoint."
                ) in planning_skill
                assert (
                    "Refer to the shared skill for branch, status, and import-result rules; do not copy that "
                    "decision matrix here."
                ) in planning_skill
                for forbidden_matrix_token in (
                    *(f"- {heading}:" for heading in expected_branch_headings),
                    "establishes `imported_byte_exact`",
                    "Record `captured_received_text`",
                    "record `skipped_inline_unavailable`",
                    "`committed=true`",
                    "`committed=false`",
                    "`pass-with-warning`",
                    "`import_kind=chatgpt-output`",
                    "`storage_identity=blank`",
                    "missing receipt field",
                    "duplicate import",
                    "review, quarantine, stage, and validation lane",
                    "single-file import",
                    "weaken existing ZIP safety checks",
                ):
                    assert forbidden_matrix_token not in planning_skill
            assert "/Users/" not in chatgpt_authoring_skill
            assert "oracle-" + "chatgpt" not in chatgpt_authoring_skill
            assert "./spec " not in workflow_issue
            assert "issues/new-issue" not in workflow_issue
            assert (
                './spec-dock/scripts/spec-dock new issue --no-github --epic <epic-id> --title "..."'
                not in workflow_issue
            )

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
                    '`./spec-dock/scripts/spec-dock new epic --initiative <id> --title "<title>"`',
                ),
                (
                    epic_issues_rules,
                    '`./spec-dock/scripts/spec-dock new issue --epic <id> --title "<title>"`',
                ),
            ):
                assert "spec-dock/docs/" in text
                assert expected_command in text
                assert "./spec " not in text
            for text, expected_command in (
                (
                    initiative_artifacts_rules,
                    "future `new artifact` surface",
                ),
                (
                    epic_artifacts_rules,
                    "future `new artifact` surface",
                ),
                (
                    issue_artifacts_rules,
                    "future `new artifact` surface",
                ),
            ):
                assert "spec-dock/docs/" in text
                assert expected_command in text
                assert "new doc " not in text
                assert "./spec " not in text
            for text in (initiative_discussions_rules, epic_discussions_rules, issue_discussions_rules):
                assert "preservation surface" in text
                assert "Historical creation command examples are intentionally omitted" in text
                assert "new doc " not in text
                assert "./spec " not in text
            for skill_text in (
                hub_skill,
                issue_skill,
                chatgpt_authoring_skill,
                codex_adapter_skill,
                copilot_adapter_skill,
            ):
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

            for skill_text in (hub_skill, chatgpt_authoring_skill, codex_adapter_skill, copilot_adapter_skill):
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

    def test_new_artifact_numbering_and_validate_ignore_initiative_artifact_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])

            initiative_dir = target / "spec-dock" / "initiatives" / "init-00001-auth-platform"
            artifacts_dir = initiative_dir / "artifacts"
            rules_target = target / "spec-dock" / "docs" / "rules" / "initiative" / "artifacts.md"

            self._run_runtime(target, ["new", "artifact", "adr", "--initiative", "1", "--title", "Decision one"])
            self._run_runtime(target, ["new", "artifact", "disc", "--initiative", "1", "--title", "Why now"])

            rules_link = artifacts_dir / "rules.md"
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()
            adr_files = sorted(artifacts_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(artifacts_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in artifacts_dir.iterdir()) == sorted([
                adr_files[0].name,
                disc_files[0].name,
                "rules.md",
            ])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_new_artifact_numbering_and_validate_ignore_epic_artifact_rules_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._init_origin_repo(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )

            epic_dir = (
                target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / "epics" / "epic-00002-jwt-auth"
            )
            artifacts_dir = epic_dir / "artifacts"
            rules_target = target / "spec-dock" / "docs" / "rules" / "epic" / "artifacts.md"

            self._run_runtime(target, ["new", "artifact", "adr", "--epic", "2", "--title", "Decision one"])
            self._run_runtime(target, ["new", "artifact", "disc", "--epic", "2", "--title", "Why now"])

            rules_link = artifacts_dir / "rules.md"
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()
            adr_files = sorted(artifacts_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(artifacts_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in artifacts_dir.iterdir()) == sorted([
                adr_files[0].name,
                disc_files[0].name,
                "rules.md",
            ])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_new_artifact_numbering_and_validate_ignore_issue_artifact_rules_symlink(self) -> None:
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
            artifacts_dir = issue_dir / "artifacts"
            rules_target = target / "spec-dock" / "docs" / "rules" / "issue" / "artifacts.md"

            self._run_runtime(target, ["new", "artifact", "adr", "--issue", "3", "--title", "Decision one"])
            self._run_runtime(target, ["new", "artifact", "disc", "--issue", "3", "--title", "Why now"])

            rules_link = artifacts_dir / "rules.md"
            assert rules_link.is_symlink(), f"missing rules symlink: {rules_link}"
            assert rules_link.resolve() == rules_target.resolve()
            adr_files = sorted(artifacts_dir.glob("*-adr-decision-one.md"))
            disc_files = sorted(artifacts_dir.glob("*-disc-why-now.md"))
            assert len(adr_files) == 1
            assert len(disc_files) == 1
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-adr-decision-one\.md$", adr_files[0].name)
            assert re.search(r"^[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?-disc-why-now\.md$", disc_files[0].name)
            assert sorted(path.name for path in artifacts_dir.iterdir()) == sorted([
                adr_files[0].name,
                disc_files[0].name,
                "rules.md",
            ])

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, (
                f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}"
            )
            assert "spec-dock: ok (validate)" in validate_result.stdout

    def test_validate_rejects_symlinked_artifacts_dir(self) -> None:
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
            artifacts_dir = issue_dir / "artifacts"
            external_artifacts = target / "external-artifacts"
            external_artifacts.mkdir()
            shutil.rmtree(artifacts_dir)
            artifacts_dir.symlink_to(external_artifacts)

            validate_result = self._run_runtime_capture(target, ["validate"])

            assert validate_result.returncode != 0
            assert "Unsafe artifact directory" in validate_result.stderr
            assert "must not be a symlink" in validate_result.stderr

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

    def test_chatgpt_and_authoring_pack_handoff_wrappers_remain_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            chatgpt_wrapper = target / "spec-dock" / "scripts" / "spec-dock-chatgpt"
            top_help = self._run_wrapper_capture(chatgpt_wrapper, ["--help"], cwd=target)
            assert top_help.returncode == 0
            assert "{planning,review}" in top_help.stdout

            create_help = self._run_wrapper_capture(
                chatgpt_wrapper,
                ["planning", "create", "--help"],
                cwd=target,
            )
            assert create_help.returncode == 0
            assert "--issue" in create_help.stdout
            assert "--output" in create_help.stdout

            authoring_pack = target / "spec-dock" / "scripts" / "authoring-pack"
            for filename in (
                "prepare_chatgpt_authoring_pack.py",
                "review_chatgpt_authoring_pack.py",
                "stage_chatgpt_authoring_pack.py",
            ):
                assert (authoring_pack / filename).is_file()
