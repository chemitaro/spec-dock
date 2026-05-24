import json
import tomllib
import unittest
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestDelegatedAuthoringCli(CliRuntimeHarness):
    def tearDown(self) -> None:
        for tmp in getattr(self, "_tmpdir", []):
            tmp.cleanup()
        super().tearDown()

    def test_manifest_command_generates_issue_local_artifacts(self) -> None:
        with self.subTest("cli host acceptance counted"):
            target = self._make_target_repo_with_scope()
            authority_file = self._write_authority_file(target)

            p = self._run_runtime_capture(
                target,
                [
                    "delegated-authoring",
                    "manifest",
                    "--role",
                    "system-architect",
                    "--scope",
                    "iss-00003",
                    "--target",
                    "design",
                    "--host-surface",
                    "cli",
                    "--input-authority-file",
                    str(authority_file),
                ],
            )

            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("spec-dock: ok (delegated-authoring manifest)", p.stdout)
            self.assertIn("host_surface_acceptance_eligible=true", p.stdout)
            self.assertIn("acceptance_counted=false", p.stdout)
            self.assertIn("manifest_path=", p.stdout)
            manifest_path = _stdout_path(p.stdout, "manifest_path")
            profile_path = _stdout_path(p.stdout, "permission_profile_path")
            probe_path = _stdout_path(p.stdout, "probe_plan_path")
            session_path = _stdout_path(p.stdout, "session_invocation_path")
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(profile_path.is_file())
            self.assertTrue(probe_path.is_file())
            self.assertTrue(session_path.is_file())
            profile = profile_path.read_text(encoding="utf-8")
            profile_data = tomllib.loads(profile)
            manifest_data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
            profile_name = _stdout_value(p.stdout, "permission_profile_name")
            target_rel = (_issue_dir(target) / "design.md").relative_to(target).as_posix()
            task_rel = profile_path.parent.resolve().relative_to(target.resolve()).as_posix()
            sentinel_path = Path(manifest_data["negative_probe_sentinel"]).resolve()
            sentinel_rel = sentinel_path.relative_to(target.resolve()).as_posix()
            sentinel_map = {category: Path(path).resolve() for category, path in manifest_data["negative_probe_sentinels"].items()}
            self.assertEqual(
                set(sentinel_map),
                {"requirement.md", "peer_artifact", "report.md", "src/", "tests/", ".codex/", ".agents/", ".env*"},
            )
            issue_dir = _issue_dir(target).resolve()
            self.assertEqual(sentinel_map["requirement.md"].parent, issue_dir / "discussions")
            self.assertEqual(sentinel_map["peer_artifact"].parent, issue_dir / "discussions")
            self.assertIn(".plan.md.", sentinel_map["peer_artifact"].name)
            self.assertEqual(sentinel_map["report.md"].parent, issue_dir / "discussions")
            target_root = target.resolve()
            self.assertEqual(sentinel_map["src/"].parent, target_root / "src")
            self.assertEqual(sentinel_map["tests/"].parent, target_root / "tests")
            self.assertEqual(sentinel_map[".codex/"].parent, target_root / ".codex")
            self.assertEqual(sentinel_map[".agents/"].parent, target_root / ".agents")
            self.assertEqual(sentinel_map[".env*"].parent, target_root)
            self.assertTrue(sentinel_map[".env*"].name.startswith(".env."))
            self.assertFalse(sentinel_path.is_relative_to(profile_path.parent))
            self.assertEqual(profile_data["default_permissions"], profile_name)
            profile_config = profile_data["permissions"][profile_name]
            self.assertEqual(profile_config["filesystem"][":minimal"], "read")
            workspace_rules = profile_config["filesystem"][":workspace_roots"]
            self.assertEqual(workspace_rules["."], "read")
            self.assertEqual(workspace_rules[target_rel], "write")
            self.assertEqual(workspace_rules[task_rel], "write")
            self.assertNotIn(sentinel_rel, workspace_rules)
            for sentinel in sentinel_map.values():
                self.assertNotIn(sentinel.relative_to(target.resolve()).as_posix(), workspace_rules)
            self.assertEqual(workspace_rules[".env"], "deny")
            self.assertEqual(workspace_rules[".env.*"], "deny")
            self.assertFalse(profile_config["network"]["enabled"])
            self.assertIn(f'[permissions."{profile_name}".filesystem]', profile)
            self.assertIn(f'[permissions."{profile_name}".filesystem.":workspace_roots"]', profile)
            self.assertIn(f'[permissions."{profile_name}".network]', profile)
            self.assertNotIn("[permissions]\n", profile)
            self.assertNotIn('mode = "workspace-write"', profile)
            self.assertNotIn("read = true", profile)
            self.assertNotIn("write = [", profile)
            self.assertNotIn("sandbox_mode", profile)
            self.assertNotIn("[sandbox_workspace_write]", profile)
            probe = probe_path.read_text(encoding="utf-8")
            for category, sentinel in sentinel_map.items():
                self.assertIn(f"category: `{category}`", probe)
                self.assertIn(sentinel.as_posix(), probe)
            session = session_path.read_text(encoding="utf-8")
            self.assertIn(f'default_permissions = "{profile_name}"', session)
            self.assertIn("host_surface_acceptance_eligible = true", session)
            self.assertIn("acceptance_counted = false", session)

    def test_manifest_command_blocks_bad_authority_without_generating_profile(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(target, remove_key="reviewer_evidence_path")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("missing_requirement_reviewer_evidence_path", p.stdout)
        issue_dir = _issue_dir(target)
        self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_manifest_command_blocks_missing_required_grant(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(target, required_grants=["review_input"])

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("missing_required_grant=requirement:planning_input", p.stdout)
        self.assertFalse((_issue_dir(target) / "discussions" / "delegated-authoring").exists())

    def test_manifest_command_blocks_invalid_required_grant(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(
            target,
            required_grants=["review_input", "planning_input", "admin"],
        )

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("invalid_required_grant=requirement:admin", p.stdout)
        self.assertFalse((_issue_dir(target) / "discussions" / "delegated-authoring").exists())

    def test_manifest_command_generates_implementation_planner_plan_with_design_input(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(
            target,
            include_design=True,
            design_required_grants=["design_baseline"],
        )

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "implementation-planner",
                "--scope",
                "iss-00003",
                "--target",
                "plan",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: ok (delegated-authoring manifest)", p.stdout)
        manifest_path = _stdout_path(p.stdout, "manifest_path")
        manifest = manifest_path.read_text(encoding="utf-8")
        self.assertIn('role = "implementation-planner"', manifest)
        self.assertIn('target = "plan"', manifest)
        self.assertIn("design =", manifest)
        self.assertEqual(
            _stdout_path(p.stdout, "target_artifact_path").resolve(),
            (_issue_dir(target) / "plan.md").resolve(),
        )

    def test_desktop_manifest_is_fallback_not_acceptance_counted(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(target)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "desktop",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("host_surface_acceptance_eligible=false", p.stdout)
        self.assertIn("acceptance_counted=false", p.stdout)
        session_path = _stdout_path(p.stdout, "session_invocation_path")
        session = session_path.read_text(encoding="utf-8")
        self.assertIn('executor = "desktop-fallback"', session)
        self.assertIn("host_surface_acceptance_eligible = false", session)

    def test_manifest_command_blocks_minimal_promotion_json(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(target, minimal_promotion=True)

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("promotion_status_not_approved=requirement", p.stdout)
        self.assertIn("promotion_missing_artifact_path=requirement", p.stdout)
        self.assertFalse((_issue_dir(target) / "discussions" / "delegated-authoring").exists())

    def test_manifest_command_blocks_unstructured_markdown_evidence(self) -> None:
        target = self._make_target_repo_with_scope()
        authority_file = self._write_authority_file(target, evidence_suffix=".md")

        p = self._run_runtime_capture(
            target,
            [
                "delegated-authoring",
                "manifest",
                "--role",
                "system-architect",
                "--scope",
                "iss-00003",
                "--target",
                "design",
                "--host-surface",
                "cli",
                "--input-authority-file",
                str(authority_file),
            ],
        )

        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("spec-dock: blocked (delegated-authoring manifest)", p.stdout)
        self.assertIn("unstructured_promotion_record_evidence=requirement", p.stdout)
        self.assertIn("unstructured_reviewer_evidence_evidence=requirement", p.stdout)
        self.assertFalse((_issue_dir(target) / "discussions" / "delegated-authoring").exists())

    def _make_target_repo_with_scope(self) -> Path:
        self._tmpdir = getattr(self, "_tmpdir", [])
        import tempfile

        tmp = tempfile.TemporaryDirectory()
        self._tmpdir.append(tmp)
        target = Path(tmp.name)
        self.assertEqual(main(["init", str(target)]), 0)
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=3, issue_title="Delegated authoring")
        return target

    def _write_authority_file(
        self,
        target: Path,
        *,
        remove_key: str | None = None,
        required_grants: list[str] | None = None,
        include_design: bool = False,
        design_required_grants: list[str] | None = None,
        minimal_promotion: bool = False,
        evidence_suffix: str = ".json",
    ) -> Path:
        evidence_dir = target / "authority-evidence"
        evidence_dir.mkdir()
        promotion_path = evidence_dir / f"requirement-promotion{evidence_suffix}"
        reviewer_path = evidence_dir / f"requirement-reviewer{evidence_suffix}"
        requirement_grants = required_grants or ["review_input", "planning_input"]
        if evidence_suffix == ".md":
            promotion_path.write_text(
                "approved_revision rev-1 approved_hash hash-1 status approved authority approved grants review_input planning_input\n",
                encoding="utf-8",
            )
            reviewer_path.write_text("review_status pass reviewer_target_hash hash-1\n", encoding="utf-8")
        else:
            promotion_path.write_text(
                json.dumps(
                    _promotion_record(
                        artifact_path="requirement.md",
                        approved_revision="rev-1",
                        approved_hash="hash-1",
                        approved_grants=requirement_grants,
                        reviewer_evidence_path=reviewer_path,
                        minimal=minimal_promotion,
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            reviewer_path.write_text(
                json.dumps({"review_status": "pass", "reviewer_target_hash": "hash-1"}) + "\n",
                encoding="utf-8",
            )
        entry = {
            "promotion_record_path": str(promotion_path),
            "reviewer_evidence_path": str(reviewer_path),
            "approved_revision": "rev-1",
            "approved_content_hash": "hash-1",
            "reviewer_verdict": "pass",
            "reviewer_target_hash": "hash-1",
            "required_grants": requirement_grants,
            "stale_check": "fresh",
        }
        if remove_key is not None:
            entry.pop(remove_key)
        source_revisions = {"requirement": "rev-1"}
        input_authority = {"requirement": entry}
        if include_design:
            design_promotion_path = evidence_dir / "design-promotion.json"
            design_reviewer_path = evidence_dir / "design-reviewer.json"
            design_grants = design_required_grants or ["design_baseline"]
            design_promotion_path.write_text(
                json.dumps(
                    _promotion_record(
                        artifact_path="design.md",
                        approved_revision="design-rev-1",
                        approved_hash="design-hash-1",
                        approved_grants=design_grants,
                        reviewer_evidence_path=design_reviewer_path,
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            design_reviewer_path.write_text(
                json.dumps({"review_status": "pass", "reviewer_target_hash": "design-hash-1"}) + "\n",
                encoding="utf-8",
            )
            source_revisions["design"] = "design-rev-1"
            input_authority["design"] = {
                "promotion_record_path": str(design_promotion_path),
                "reviewer_evidence_path": str(design_reviewer_path),
                "approved_revision": "design-rev-1",
                "approved_content_hash": "design-hash-1",
                "reviewer_verdict": "pass",
                "reviewer_target_hash": "design-hash-1",
                "required_grants": design_grants,
                "stale_check": "fresh",
            }
        authority_file = evidence_dir / "input-authority.json"
        authority_file.write_text(
            json.dumps(
                {
                    "source_revisions": source_revisions,
                    "input_authority": input_authority,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return authority_file


def _issue_dir(target: Path) -> Path:
    return (
        target
        / "spec-dock"
        / "initiatives"
        / "init-00001-auth-platform"
        / "epics"
        / "epic-00002-jwt-auth"
        / "issues"
        / "iss-00003-delegated-authoring"
    )


def _stdout_path(stdout: str, key: str) -> Path:
    return Path(_stdout_value(stdout, key))


def _stdout_value(stdout: str, key: str) -> str:
    for line in stdout.splitlines():
        prefix = f"{key}="
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing stdout path: {key}\n{stdout}")


def _promotion_record(
    *,
    artifact_path: str,
    approved_revision: str,
    approved_hash: str,
    approved_grants: list[str],
    reviewer_evidence_path: Path,
    minimal: bool = False,
) -> dict[str, object]:
    if minimal:
        return {
            "promotion_record": {
                "authority": "approved",
                "approved_revision": approved_revision,
                "approved_hash": approved_hash,
            }
        }
    return {
        "promotion_record": {
            "status": "approved",
            "authority": "approved",
            "artifact_path": artifact_path,
            "approved_revision": approved_revision,
            "approved_hash": approved_hash,
            "approved_grants": approved_grants,
            "approver": "main-orchestrator",
            "approved_at": "2026-05-24T00:00:00Z",
            "reviewer_evidence_path": str(reviewer_evidence_path),
            "final_reviewer": "spec-reviewer",
            "ledger_blockers_remaining": 0,
        }
    }


if __name__ == "__main__":
    unittest.main()
