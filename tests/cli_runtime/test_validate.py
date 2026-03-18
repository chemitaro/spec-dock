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


class TestCliValidate(CliRuntimeHarness):
    def test_validate_detects_broken_parent_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_detects_issue_initiative_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Payments platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["initiative_id"] = "init-local-00002"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_reports_invalid_meta_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / ".meta.json"
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1}
            self._write_json_force(issue_meta, issue_data)

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate github.issue_number detected", p.stderr)
            self.assertIn("github.issue_number=1", p.stderr)
            self.assertIn("initiative:init-local-00001", p.stderr)
            self.assertIn("issue:iss-local-00001", p.stderr)
            self.assertIn("spec-dock/initiatives/init-local-00001-auth-platform/.meta.json", p.stderr)
            self.assertIn(
                "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json",
                p.stderr,
            )
            self.assertIn("Fix github.issue_number", p.stderr)

    def test_validate_detects_duplicate_discussion_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Duplicate discussion sequence detected", p.stderr)
            self.assertIn("seq=001", p.stderr)
            self.assertIn("001-adr-first.md", p.stderr)
            self.assertIn("001-disc-second.md", p.stderr)

    def test_validate_detects_missing_required_artifact_docs_for_each_node_kind(self) -> None:
        artifact_names = ("requirement.md", "design.md", "plan.md", "report.md")
        node_roots = {
            "initiative": (
                Path("spec-dock/initiatives/init-local-00001-auth-platform"),
                "kind=initiative id=init-local-00001",
            ),
            "epic": (
                Path("spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth"),
                "kind=epic id=epic-local-00001",
            ),
            "issue": (
                Path(
                    "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token"
                ),
                "kind=issue id=iss-local-00001",
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

                    self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
                    self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
                    self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

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
                Path("spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
                "kind=initiative id=init-local-00001",
            ),
            (
                "epic",
                Path(
                    "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/.meta.json"
                ),
                "kind=epic id=epic-local-00001",
            ),
            (
                "issue",
                Path(
                    "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json"
                ),
                "kind=issue id=iss-local-00001",
            ),
        ]
        for kind, meta_rel_path, expected in cases:
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)

                    self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
                    self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
                    self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            meta_rel_path = Path(
                "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-00001-add-refresh-token/.meta.json"
            )
            (target / meta_rel_path).unlink(missing_ok=False)

            p = self._run_runtime_capture(target, ["doctor"])
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: doctor: findings=1", p.stderr)
            self.assertIn("[missing_artifact]", p.stderr)
            self.assertIn(meta_rel_path.as_posix(), p.stderr)

    def test_sync_fails_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["sync", "--no-update-active"])

    def test_sync_force_continues_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

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
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-local-99999"
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
            self.assertIsNone(index["nodes"]["iss-local-00001"]["deps"])

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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
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

            self._run_runtime(target, ["new", "initiative", "--no-github", "--title", "Auth platform"])
            self._run_runtime(target, ["new", "epic", "--no-github", "--initiative", "1", "--title", "JWT auth"])
            self._run_runtime(target, ["new", "issue", "--no-github", "--epic", "1", "--title", "Add refresh token"])

            init_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / ".meta.json"
            )
            epic_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / ".meta.json"
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-local-00001-auth-platform"
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-add-refresh-token"
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

    def test_validate_and_sync_fail_fast_on_legacy_meta_json(self) -> None:
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
