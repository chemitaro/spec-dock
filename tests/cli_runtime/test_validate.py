import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)


class TestCliValidate(CliRuntimeHarness):
    def test_validate_detects_broken_parent_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_detects_issue_initiative_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Payments platform", "--github-issue", "4"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["initiative_id"] = "init-00004"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_rejects_local_only_initiative_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            init_meta = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            meta = json.loads(init_meta.read_text(encoding="utf-8"))
            meta.pop("github", None)
            self._write_json_force(init_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("initiative missing github.issue_number", p.stderr)

    def test_validate_rejects_legacy_unscoped_issue_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3}
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("legacy unscoped github linkage", p.stderr)

    def test_sync_fails_preflight_on_partially_scoped_issue_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3, "repo_owner": "example"}
            self._write_json_force(issue_meta, meta)

            for args in (
                ["sync", "--no-update-active"],
                ["sync", "--no-update-active", "--force"],
            ):
                with self.subTest(args=args):
                    p = self._run_runtime_capture(target, args)
                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn("Invalid github.repo_owner/repo_name", p.stderr)
                    self.assertIn("both fields are required", p.stderr)
                    self.assertNotIn("deps_preflight_failed", p.stderr)

    def test_validate_rejects_blank_string_repo_scope_in_meta_loader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3, "repo_owner": "   ", "repo_name": "repo"}
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Invalid github.repo_owner/repo_name", p.stderr)
            self.assertIn("empty value is not allowed", p.stderr)
            self.assertNotIn("legacy unscoped github linkage", p.stderr)

    def test_validate_reports_invalid_meta_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            self._write_text_force(issue_meta, "[]\n")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("Invalid .meta.json", p.stderr)
            self.assertIn(str(issue_meta), p.stderr)

    def test_validate_detects_duplicate_github_issue_numbers_with_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / ".meta.json"
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1}
            self._write_json_force(issue_meta, issue_data)
            shutil.rmtree(target / ".git", ignore_errors=True)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate github.linkage detected", p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)
            self.assertIn("repo=(current-or-unknown)", p.stderr)
            self.assertIn("initiative:init-00001", p.stderr)
            self.assertIn("issue:iss-00003", p.stderr)
            self.assertIn("spec-dock/initiatives/init-00001-auth-platform/.meta.json", p.stderr)
            self.assertIn(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json",
                p.stderr,
            )
            self.assertIn("Fix github linkage", p.stderr)

    def test_validate_rejects_same_issue_number_when_repo_linkage_is_mixed_and_current_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / ".meta.json"
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(issue_meta, issue_data)
            shutil.rmtree(target / ".git", ignore_errors=True)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Ambiguous github.linkage scope detected", p.stderr)
            self.assertIn("fail-closed", p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)

    def test_validate_allows_same_issue_number_when_current_repo_is_resolved(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_same_repo_linked_hierarchy(target)

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / ".meta.json"
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(issue_meta, issue_data)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok", p.stdout)

    def test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-note-current.md").write_text("current\n", encoding="utf-8")
            (discussions_dir / "20260329todo.md").write_text("ignore me\n", encoding="utf-8")
            (discussions_dir / "rules.md").write_text("notes\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok", p.stdout)

    def test_validate_rejects_malformed_discussion_doc_candidates(self) -> None:
        cases = (
            "20260329t123456z.md",
            "20260329t123456z--adr-kickoff.md",
            "20260329t123456z-1-adr-kickoff.md",
            "20260329t123456z-0a-adr-kickoff.md",
            "20260329t123456z-ADR-kickoff.md",
            "20260329t123456z-01-NOTE-memo.md",
            "20260329t123456z-bogus-kickoff.md",
            "20260329T123456z-adr-upper-t.md",
            "20260329t123456Z-adr-upper-z.md",
            "20260329t123456z-00-adr-bad-suffix.md",
            "20260329t123456z-100-adr-too-wide.md",
            "20260329t123456z-adr.md",
            "20260329t123456z_adr-kickoff.md",
            "20260329t123456z01-adr-kickoff.md",
            "20260329-adr-kickoff.md",
            "20260329-99-adr-kickoff.md",
            "20260329x123456z-adr-kickoff.md",
            "20260329t123456zz-adr-kickoff.md",
            "20260329t1234z-adr-kickoff.md",
            "20260329t12345z-adr-kickoff.md",
            "20260329123456z-adr-kickoff.md",
            "20260329123456z-99-adr-kickoff.md",
            "001-adr.md",
            "001_adr-kickoff.md",
            "001-bogus-kickoff.md",
            "adr-kickoff.md",
            "adr_kickoff.md",
        )
        for name in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)

                    self._create_same_repo_linked_hierarchy(target)

                    discussions_dir = (
                        target
                        / "spec-dock"
                        / "initiatives"
                        / "init-00001-auth-platform"
                        / "epics"
                        / "epic-00002-jwt-auth"
                        / "issues"
                        / "iss-00003-add-refresh-token"
                        / "discussions"
                    )
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    (discussions_dir / name).write_text("bad\n", encoding="utf-8")
                    (discussions_dir / "rules.md").write_text("allowed\n", encoding="utf-8")

                    p = self._run_runtime_capture(target, ["validate"])
                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn("Malformed discussion document filename", p.stderr)
                    self.assertIn(name, p.stderr)
                    self.assertNotIn("rules.md", p.stderr)

    def test_validate_accepts_mixed_same_timestamp_unsuffixed_and_suffixed_slots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-adr-kickoff.md").write_text("kickoff\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-01-disc-options.md").write_text("options\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-99-research-spike.md").write_text("spike\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok", p.stdout)

    def test_validate_accepts_high_end_discussion_timestamp_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-99-adr-tail.md").write_text("tail\n", encoding="utf-8")
            (discussions_dir / "20260329t123457z-note-next.md").write_text("next\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok", p.stdout)

    def test_validate_accepts_research_discussion_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-research-spike.md").write_text("spike\n", encoding="utf-8")
            (discussions_dir / "001-research-legacy-spike.md").write_text("legacy\n", encoding="utf-8")
            (discussions_dir / "rules.md").write_text("notes\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok", p.stdout)

    def test_validate_detects_duplicate_discussion_timestamp_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate discussion timestamp slot detected", p.stderr)
            self.assertIn("slot=20260329t123456z", p.stderr)
            self.assertIn("20260329t123456z-adr-first.md", p.stderr)
            self.assertIn("20260329t123456z-disc-second.md", p.stderr)

    def test_validate_detects_duplicate_discussion_timestamp_suffix_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-01-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-01-note-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate discussion timestamp suffix detected", p.stderr)
            self.assertIn("slot=20260329t123456z-01", p.stderr)
            self.assertIn("20260329t123456z-01-adr-first.md", p.stderr)
            self.assertIn("20260329t123456z-01-note-second.md", p.stderr)

    def test_validate_detects_missing_required_artifact_docs_for_each_node_kind(self) -> None:
        artifact_names = ("requirement.md", "design.md", "plan.md", "report.md")
        node_roots = {
            "initiative": (
                Path("spec-dock/initiatives/init-00001-auth-platform"),
                "kind=initiative id=init-00001",
            ),
            "epic": (
                Path("spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth"),
                "kind=epic id=epic-00002",
            ),
            "issue": (
                Path(
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token"
                ),
                "kind=issue id=iss-00003",
            ),
        }
        cases = [
            (kind, artifact_name, node_root / artifact_name, expected)
            for kind, (node_root, expected) in node_roots.items()
            for artifact_name in artifact_names
        ]
        for _name, artifact_name, artifact_rel_path, expected in cases:
            with self.subTest(kind=_name, artifact=artifact_name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)

                    self._create_same_repo_linked_hierarchy(target)

                    artifact_path = target / artifact_rel_path
                    artifact_path.unlink(missing_ok=False)

                    p = self._run_runtime_capture(target, ["validate"])
                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn("Missing required artifact", p.stderr)
                    self.assertIn(expected, p.stderr)
                    self.assertIn(artifact_rel_path.as_posix(), p.stderr)

    def test_validate_detects_missing_required_meta_for_each_node_kind(self) -> None:
        cases = [
            (
                "initiative",
                Path("spec-dock/initiatives/init-00001-auth-platform/.meta.json"),
                "kind=initiative id=init-00001",
            ),
            (
                "epic",
                Path(
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/.meta.json"
                ),
                "kind=epic id=epic-00002",
            ),
            (
                "issue",
                Path(
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json"
                ),
                "kind=issue id=iss-00003",
            ),
        ]
        for kind, meta_rel_path, expected in cases:
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)

                    self._create_same_repo_linked_hierarchy(target)

                    meta_path = target / meta_rel_path
                    meta_path.unlink(missing_ok=False)

                    p = self._run_runtime_capture(target, ["validate"])
                    self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
                    self.assertIn("Missing required artifact", p.stderr)
                    self.assertIn(expected, p.stderr)
                    self.assertIn(meta_rel_path.as_posix(), p.stderr)

    def test_doctor_detects_missing_required_meta_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            meta_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json"
            )
            (target / meta_rel_path).unlink(missing_ok=False)

            p = self._run_runtime_capture(target, ["doctor"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: doctor: findings=1", p.stderr)
            self.assertIn("[missing_artifact]", p.stderr)
            self.assertIn(meta_rel_path.as_posix(), p.stderr)

    def test_validate_sync_and_doctor_classify_missing_meta_with_create_lock_in_progress(self) -> None:
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
            (issue_dir / ".meta.json").unlink(missing_ok=False)

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=active",
                        "pid=1234",
                        "user=tester",
                        f"created_unix={time.time():.6f}",
                        "created_iso=2026-03-23",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)
            self.assertIn("Create in-progress state detected", p_validate.stderr)
            self.assertIn(".meta.json", p_validate.stderr)
            self.assertNotIn("Missing required artifact", p_validate.stderr)

            p_sync = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertNotEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertIn("Create in-progress state detected", p_sync.stderr)
            self.assertNotIn("Missing required artifact", p_sync.stderr)

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            self.assertNotEqual(p_doctor.returncode, 0, p_doctor.stdout + p_doctor.stderr)
            self.assertIn("[stale_create_lock]", p_doctor.stderr)
            self.assertIn("Create in-progress state detected", p_doctor.stderr)
            self.assertNotIn("[missing_artifact]", p_doctor.stderr)

    def test_validate_sync_and_doctor_classify_missing_meta_with_stale_create_lock(self) -> None:
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
            (issue_dir / ".meta.json").unlink(missing_ok=False)

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=stale",
                        "pid=4321",
                        "user=tester",
                        "created_unix=0",
                        "created_iso=1970-01-01",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)
            self.assertIn("Stale create-lock state detected", p_validate.stderr)
            self.assertIn(".meta.json", p_validate.stderr)
            self.assertNotIn("Missing required artifact", p_validate.stderr)

            p_sync = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertNotEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertIn("Stale create-lock state detected", p_sync.stderr)
            self.assertNotIn("Missing required artifact", p_sync.stderr)

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            self.assertNotEqual(p_doctor.returncode, 0, p_doctor.stdout + p_doctor.stderr)
            self.assertIn("[stale_create_lock]", p_doctor.stderr)
            self.assertIn("Stale create-lock state detected", p_doctor.stderr)
            self.assertNotIn("[missing_artifact]", p_doctor.stderr)

    def test_validate_sync_and_doctor_detect_missing_required_plan_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            missing_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/plan.md"
            )
            (target / missing_rel_path).unlink(missing_ok=False)

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)
            self.assertIn("Missing required artifact", p_validate.stderr)
            self.assertIn(missing_rel_path.as_posix(), p_validate.stderr)

            p_sync = self._run_runtime_capture(target, ["sync", "--no-update-active"])
            self.assertNotEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertIn("preflight validate failed", p_sync.stderr)
            self.assertIn("Missing required artifact", p_sync.stderr)
            self.assertIn(missing_rel_path.as_posix(), p_sync.stderr)

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            self.assertNotEqual(p_doctor.returncode, 0, p_doctor.stdout + p_doctor.stderr)
            self.assertIn("[missing_artifact]", p_doctor.stderr)
            self.assertIn(missing_rel_path.as_posix(), p_doctor.stderr)

    def test_sync_force_continues_when_required_plan_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["sync", "--no-update-active"])

            agent_dir = target / "spec-dock" / ".agent"
            missing_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/plan.md"
            )
            (target / missing_rel_path).unlink(missing_ok=False)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertIn(missing_rel_path.as_posix(), p.stderr)

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index["warnings"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

    def test_sync_fails_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["sync", "--no-update-active"])

    def test_sync_force_continues_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            self._run_runtime(target, ["sync", "--no-update-active"])
            agent_dir = target / "spec-dock" / ".agent"
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertTrue(baseline_index["deps"]["valid"])
            self.assertEqual(baseline_index["deps"]["issue_edges"], [])
            self.assertIsNone(baseline_index["deps"]["error"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertEqual(index["deps"]["issue_edges"], [])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertIsNone(index["nodes"]["iss-00003"]["deps"])

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            self.assertFalse(deps_issues["deps"]["valid"])
            self.assertIn("preflight validate failed", str(deps_issues["deps"]["error"]))
            self.assertEqual(deps_issues["nodes"], {})
            self.assertEqual(deps_issues["edges"], [])

            tree_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            self.assertIn("deps_preflight_failed", tree_puml)
            self.assertIn("deps.valid=false", tree_puml)
            self.assertIn("--force", tree_puml)
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            self.assertIn("DEPS_DISABLED", dashboard)
            self.assertIn("deps_preflight_failed", dashboard)
            self.assertIn("deps.valid=false", dashboard)

            # Legacy v1 deps artifacts must always be removed.
            self.assertFalse((agent_dir / "deps.json").exists())
            self.assertFalse((agent_dir / "deps.puml").exists())
            self.assertFalse((agent_dir / "deps.todo.puml").exists())

    def test_sync_force_continues_when_meta_id_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "broken-id"
            self._write_json_force(issue_meta, meta)

            agent_dir = target / "spec-dock" / ".agent"
            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)
            (agent_dir / "index-all.json").unlink(missing_ok=True)
            (agent_dir / "tree-all.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["sync", "--no-update-active", "--force"])
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("preflight validate failed", p.stderr)
            self.assertIn("deps_preflight_failed", p.stderr)
            self.assertTrue((agent_dir / "index.json").is_file())
            self.assertTrue((agent_dir / "tree.json").is_file())
            self.assertTrue((agent_dir / "index-all.json").is_file())
            self.assertTrue((agent_dir / "tree-all.json").is_file())

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("deps_preflight_failed", index["warnings"])
            self.assertEqual(index["deps"]["issue_edges"], [])

    def test_sync_and_validate_do_not_backfill_or_relock_existing_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._create_same_repo_linked_hierarchy(target)

            init_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / ".meta.json"
            )
            epic_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / ".meta.json"
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta_paths = [init_meta_path, epic_meta_path, issue_meta_path]

            before_texts: dict[Path, str] = {}
            before_modes: dict[Path, int] = {}

            for meta_path in meta_paths:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta.pop("_spec_dock", None)
                self._write_json_force(meta_path, meta)
                if os.name == "posix":
                    try:
                        meta_path.chmod(meta_path.stat().st_mode | 0o200)
                    except OSError:
                        pass

                before_text = meta_path.read_text(encoding="utf-8")
                before_texts[meta_path] = before_text
                self.assertNotIn("_spec_dock", json.loads(before_text))
                if os.name == "posix":
                    before_modes[meta_path] = meta_path.stat().st_mode

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync"])

            for meta_path in meta_paths:
                after_text = meta_path.read_text(encoding="utf-8")
                self.assertEqual(after_text, before_texts[meta_path])
                self.assertNotIn("_spec_dock", json.loads(after_text))
                if os.name == "posix":
                    after_mode = meta_path.stat().st_mode
                    self.assertEqual(after_mode, before_modes[meta_path])
                    self.assertEqual(after_mode & 0o222, before_modes[meta_path] & 0o222)

    def test_sync_github_keeps_already_normalized_current_repo_linkage_no_origin_continuity(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Foreign issue", "--github-issue", "124"])

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )
            foreign_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-foreign-issue"
                / ".meta.json"
            )

            # already-normalized current linkage + explicit foreign same-number overlap.
            current_meta_before = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_before["github"]["issue_number"], 123)
            self.assertEqual(current_meta_before["github"]["repo_owner"], "current")
            self.assertEqual(current_meta_before["github"]["repo_name"], "repo")
            foreign_meta = json.loads(foreign_issue_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta_path, foreign_meta)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(sync_result.returncode, 0, sync_result.stdout + sync_result.stderr)

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertEqual(current_meta_after["github"]["repo_owner"], "current")
            self.assertEqual(current_meta_after["github"]["repo_name"], "repo")

            # no-origin continuity for already-normalized metadata.
            shutil.rmtree(target / ".git", ignore_errors=True)

            sync_after_no_origin = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(sync_after_no_origin.returncode, 0, sync_after_no_origin.stdout + sync_after_no_origin.stderr)

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(validate_result.returncode, 0, validate_result.stdout + validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(doctor_result.returncode, 0, doctor_result.stdout + doctor_result.stderr)

            deps_by_url = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/current/repo/issues/123", "--json"],
            )
            self.assertIn(deps_by_url.returncode, (0, 3), deps_by_url.stdout + deps_by_url.stderr)
            self.assertIn('"target": "iss-00123"', deps_by_url.stdout)

            deps_by_id = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00123", "--json"])
            self.assertIn(deps_by_id.returncode, (0, 3), deps_by_id.stdout + deps_by_id.stderr)
            self.assertIn('"target": "iss-00123"', deps_by_id.stdout)

            active_by_url = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/current/repo/issues/123", "--force"],
            )
            self.assertEqual(active_by_url.returncode, 0, active_by_url.stdout + active_by_url.stderr)

            active_by_id = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00123", "--force"])
            self.assertEqual(active_by_id.returncode, 0, active_by_id.stdout + active_by_id.stderr)

            ambiguous_number = self._run_runtime_capture(target, ["deps", "check", "123"])
            self.assertNotEqual(ambiguous_number.returncode, 0, ambiguous_number.stdout + ambiguous_number.stderr)
            self.assertIn("Ambiguous github.issue_number=123", ambiguous_number.stderr)

            ambiguous_flag = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123"])
            self.assertNotEqual(ambiguous_flag.returncode, 0, ambiguous_flag.stdout + ambiguous_flag.stderr)
            self.assertIn("Ambiguous github.issue_number=123", ambiguous_flag.stderr)

    def test_sync_github_keeps_readonly_lone_unscoped_meta_without_backfill(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"])

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )

            current_meta = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_issue_meta_path, current_meta)
            current_issue_meta_path.chmod(current_issue_meta_path.stat().st_mode & ~0o222)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(sync_result.returncode, 0, sync_result.stdout + sync_result.stderr)

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])
            self.assertEqual(current_issue_meta_path.stat().st_mode & 0o222, 0)

    def test_sync_github_no_backfill_path_does_not_emit_readonly_lock_warning(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"])
            self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"])

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )

            current_meta = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_issue_meta_path, current_meta)
            current_issue_meta_path.chmod(current_issue_meta_path.stat().st_mode & ~0o222)

            runtime_fs_repo = (
                target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            )
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _try_make_readonly(path):\n"
                + '    return False, "simulated-relock-failure"\n',
                encoding="utf-8",
            )

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(sync_result.returncode, 0, sync_result.stdout + sync_result.stderr)
            self.assertNotIn("readonly_lock_failed", sync_result.stderr)
            self.assertNotIn("simulated-relock-failure", sync_result.stderr)

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])

    def test_validate_and_sync_fail_fast_on_legacy_meta_json(self) -> None:
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
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"
            self.assertTrue(dot_meta_path.is_file())

            meta = json.loads(dot_meta_path.read_text(encoding="utf-8"))
            meta.pop("_spec_dock", None)
            self._write_json_force(dot_meta_path, meta)
            if os.name == "posix":
                dot_meta_path.chmod(dot_meta_path.stat().st_mode | 0o200)

            before_text = dot_meta_path.read_text(encoding="utf-8")
            dot_meta_path.rename(legacy_meta_path)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0)
            self.assertIn("Unsupported legacy meta.json detected", p_validate.stderr)
            self.assertIn(str(legacy_meta_path), p_validate.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertEqual(legacy_meta_path.read_text(encoding="utf-8"), before_text)

            p_sync = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p_sync.returncode, 0)
            self.assertIn("Unsupported legacy meta.json detected", p_sync.stderr)
            self.assertIn(str(legacy_meta_path), p_sync.stderr)
            self.assertFalse(dot_meta_path.exists())
            self.assertTrue(legacy_meta_path.is_file())
            self.assertEqual(legacy_meta_path.read_text(encoding="utf-8"), before_text)

    def test_validate_and_sync_fail_fast_when_dot_meta_and_legacy_coexist(self) -> None:
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
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"

            before_text = dot_meta_path.read_text(encoding="utf-8")
            legacy_meta_path.write_text("{ invalid legacy json\n", encoding="utf-8")

            p_validate = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p_validate.returncode, 0, p_validate.stdout + p_validate.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_validate.stderr)
            self.assertIn(str(legacy_meta_path), p_validate.stderr)

            self.assertEqual(dot_meta_path.read_text(encoding="utf-8"), before_text)
            self.assertTrue(legacy_meta_path.is_file())

            p_sync = self._run_runtime_capture(target, ["sync"])
            self.assertNotEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertIn("Unsupported legacy meta.json detected", p_sync.stderr)
            self.assertIn(str(legacy_meta_path), p_sync.stderr)

            self.assertEqual(dot_meta_path.read_text(encoding="utf-8"), before_text)
            self.assertTrue(legacy_meta_path.is_file())
