import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.delegated_authoring import (
            DelegatedAuthoringManifestRequest,
            generate_delegated_authoring_manifest,
        )
        from spec_dock_runtime.domain import delegated_authoring
    finally:
        sys.path.pop(0)
    return DelegatedAuthoringManifestRequest, generate_delegated_authoring_manifest, delegated_authoring


class TestDelegatedAuthoringManifest(unittest.TestCase):
    def test_valid_authority_generates_manifest_profile_probe_and_session_invocation(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root)

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertTrue(result.ok, result.details)
            self.assertEqual(result.status, "generated")
            self.assertTrue(result.host_surface_acceptance_eligible)
            self.assertFalse(result.acceptance_counted)
            self.assertEqual(result.target_artifact_path, issue_dir / "design.md")
            self.assertIsNotNone(result.paths)
            paths = result.paths
            assert paths is not None
            self.assertTrue(paths.manifest_path.is_file())
            self.assertTrue(paths.permission_profile_path.is_file())
            self.assertTrue(paths.probe_plan_path.is_file())
            self.assertTrue(paths.session_invocation_path.is_file())
            manifest = paths.manifest_path.read_text(encoding="utf-8")
            self.assertIn('role = "system-architect"', manifest)
            self.assertIn('target = "design"', manifest)
            self.assertIn("[diff_gate]", manifest)
            manifest_data = tomllib.loads(manifest)
            profile = paths.permission_profile_path.read_text(encoding="utf-8")
            profile_data = tomllib.loads(profile)
            profile_name = result.permission_profile_name
            self.assertIsNotNone(profile_name)
            assert profile_name is not None
            target_rel = (issue_dir / "design.md").relative_to(repo_root).as_posix()
            task_rel = paths.task_dir.relative_to(repo_root).as_posix()
            sentinel_path = Path(manifest_data["negative_probe_sentinel"])
            sentinel_rel = sentinel_path.relative_to(repo_root).as_posix()
            sentinel_map = manifest_data["negative_probe_sentinels"]
            expected_categories = {
                "requirement.md",
                "peer_artifact",
                "report.md",
                "src/",
                "tests/",
                ".codex/",
                ".agents/",
                ".env*",
            }
            self.assertEqual(set(sentinel_map), expected_categories)
            self.assertFalse(
                sentinel_path.is_relative_to(paths.task_dir),
                "negative sentinel must be outside the allowed task_dir",
            )
            self.assertTrue(sentinel_rel.startswith("spec-dock/"))
            self.assertEqual(Path(sentinel_map["requirement.md"]).parent, issue_dir / "discussions")
            self.assertEqual(Path(sentinel_map["peer_artifact"]).parent, issue_dir / "discussions")
            self.assertIn(".plan.md.", Path(sentinel_map["peer_artifact"]).name)
            self.assertEqual(Path(sentinel_map["report.md"]).parent, issue_dir / "discussions")
            self.assertEqual(Path(sentinel_map["src/"]).parent, repo_root / "src")
            self.assertEqual(Path(sentinel_map["tests/"]).parent, repo_root / "tests")
            self.assertEqual(Path(sentinel_map[".codex/"]).parent, repo_root / ".codex")
            self.assertEqual(Path(sentinel_map[".agents/"]).parent, repo_root / ".agents")
            self.assertEqual(Path(sentinel_map[".env*"]).parent, repo_root)
            self.assertTrue(Path(sentinel_map[".env*"]).name.startswith(".env."))
            self.assertEqual(profile_data["default_permissions"], profile_name)
            profile_config = profile_data["permissions"][profile_name]
            self.assertEqual(profile_config["filesystem"][":minimal"], "read")
            workspace_rules = profile_config["filesystem"][":workspace_roots"]
            self.assertEqual(workspace_rules["."], "read")
            self.assertEqual(workspace_rules[target_rel], "write")
            self.assertEqual(workspace_rules[task_rel], "write")
            self.assertNotIn(sentinel_rel, workspace_rules)
            for sentinel in sentinel_map.values():
                self.assertNotIn(Path(sentinel).relative_to(repo_root).as_posix(), workspace_rules)
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
            probe = paths.probe_plan_path.read_text(encoding="utf-8")
            for category, sentinel in sentinel_map.items():
                self.assertIn(f"category: `{category}`", probe)
                self.assertIn(Path(sentinel).as_posix(), probe)
                self.assertTrue(Path(sentinel).name.endswith(".spec-dock-permission-probe-denied"))
            self.assertIn("real artifact/source/test/config/secret files must not be touched", probe)
            real_protected_paths = {
                issue_dir / "requirement.md",
                issue_dir / "design.md",
                issue_dir / "plan.md",
                issue_dir / "report.md",
                repo_root / ".env",
            }
            self.assertTrue(real_protected_paths.isdisjoint({Path(path) for path in sentinel_map.values()}))
            session = paths.session_invocation_path.read_text(encoding="utf-8")
            self.assertIn('executor = "codex-cli"', session)
            self.assertIn(f'manifest_hash = "{result.manifest_hash}"', session)
            self.assertIn(f'permission_profile_name = "{result.permission_profile_name}"', session)
            self.assertIn(f'permission_profile_hash = "{result.permission_profile_hash}"', session)
            self.assertIn(f'default_permissions = "{result.permission_profile_name}"', session)
            self.assertIn("old_sandbox_settings_absent = true", session)
            self.assertIn("host_surface_acceptance_eligible = true", session)
            self.assertIn("acceptance_counted = false", session)

    def test_minimal_promotion_json_blocks_without_artifacts(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, minimal_promotion=True)

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("promotion_status_not_approved=requirement", result.details)
            self.assertIn("promotion_missing_artifact_path=requirement", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_unstructured_markdown_evidence_blocks_without_artifacts(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, evidence_suffix=".md")

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("unstructured_promotion_record_evidence=requirement", result.details)
            self.assertIn("unstructured_reviewer_evidence_evidence=requirement", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_missing_reviewer_evidence_path_blocks_without_artifacts(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, remove_key="reviewer_evidence_path")

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.status, "blocked")
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("missing_requirement_reviewer_evidence_path", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_stale_or_mismatched_authority_blocks_without_profile(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, reviewer_target_hash="stale-hash")

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertIn("reviewer_hash_mismatch=requirement", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_promotion_reviewer_evidence_path_mismatch_blocks_without_artifacts(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, mismatched_promotion_reviewer_path=True)

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("promotion_reviewer_evidence_path_mismatch=requirement", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_missing_required_grant_blocks_without_profile(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root, required_grants=["review_input"])

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("missing_required_grant=requirement:planning_input", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_invalid_required_grant_blocks_without_profile(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(
                repo_root,
                required_grants=["review_input", "planning_input", "admin"],
            )

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("invalid_required_grant=requirement:admin", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_implementation_planner_requires_design_baseline_input(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(
                repo_root,
                include_design=True,
                design_required_grants=["review_input"],
            )

            result = generate(
                request_cls(
                    role="implementation-planner",
                    scope_id="iss-00126",
                    target="plan",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertFalse(result.ok)
            self.assertEqual(result.reason, "input_authority_not_verified")
            self.assertIn("missing_required_grant=design:design_baseline", result.details)
            self.assertFalse((issue_dir / "discussions" / "delegated-authoring").exists())

    def test_implementation_planner_accepts_requirement_and_design_authority(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            issue_dir = _make_issue_scope(repo_root)
            authority_file = _write_authority_file(
                repo_root,
                include_design=True,
                design_required_grants=["design_baseline"],
            )

            result = generate(
                request_cls(
                    role="implementation-planner",
                    scope_id="iss-00126",
                    target="plan",
                    host_surface="cli",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertTrue(result.ok, result.details)
            self.assertEqual(result.target_artifact_path, issue_dir / "plan.md")
            assert result.paths is not None
            self.assertTrue(result.paths.manifest_path.is_file())

    def test_desktop_host_surface_generates_fallback_not_acceptance_counted(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root)

            result = generate(
                request_cls(
                    role="system-architect",
                    scope_id="iss-00126",
                    target="design",
                    host_surface="desktop",
                    input_authority_file=authority_file,
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                )
            )

            self.assertTrue(result.ok, result.details)
            self.assertFalse(result.host_surface_acceptance_eligible)
            self.assertFalse(result.acceptance_counted)
            assert result.paths is not None
            session = result.paths.session_invocation_path.read_text(encoding="utf-8")
            self.assertIn('executor = "desktop-fallback"', session)
            self.assertIn("host_surface_acceptance_eligible = false", session)
            self.assertIn("acceptance_counted = false", session)

    def test_cli_and_desktop_same_authority_use_distinct_task_dirs_without_overwrite(self) -> None:
        request_cls, generate, _domain = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _make_issue_scope(repo_root)
            authority_file = _write_authority_file(repo_root)
            base_kwargs = {
                "role": "system-architect",
                "scope_id": "iss-00126",
                "target": "design",
                "input_authority_file": authority_file,
                "repo_root": repo_root,
                "specdock_dir": repo_root / "spec-dock",
            }

            cli_result = generate(request_cls(host_surface="cli", **base_kwargs))
            desktop_result = generate(request_cls(host_surface="desktop", **base_kwargs))

            self.assertTrue(cli_result.ok, cli_result.details)
            self.assertTrue(desktop_result.ok, desktop_result.details)
            assert cli_result.paths is not None
            assert desktop_result.paths is not None
            self.assertNotEqual(cli_result.paths.task_dir, desktop_result.paths.task_dir)
            self.assertIn("-cli-", cli_result.paths.task_dir.name)
            self.assertIn("-desktop-", desktop_result.paths.task_dir.name)
            self.assertNotEqual(cli_result.manifest_hash, desktop_result.manifest_hash)
            self.assertNotEqual(cli_result.session_invocation_hash, desktop_result.session_invocation_hash)

            cli_session = cli_result.paths.session_invocation_path.read_text(encoding="utf-8")
            desktop_session = desktop_result.paths.session_invocation_path.read_text(encoding="utf-8")
            self.assertIn('host_surface = "cli"', cli_session)
            self.assertIn("host_surface_acceptance_eligible = true", cli_session)
            self.assertIn("acceptance_counted = false", cli_session)
            self.assertNotIn('host_surface = "desktop"', cli_session)
            self.assertIn('host_surface = "desktop"', desktop_session)
            self.assertIn("host_surface_acceptance_eligible = false", desktop_session)
            self.assertIn("acceptance_counted = false", desktop_session)

            cli_manifest = cli_result.paths.manifest_path.read_text(encoding="utf-8")
            desktop_manifest = desktop_result.paths.manifest_path.read_text(encoding="utf-8")
            self.assertIn('host_surface = "cli"', cli_manifest)
            self.assertIn("host_surface_acceptance_eligible = true", cli_manifest)
            self.assertIn("acceptance_counted = false", cli_manifest)
            self.assertIn('host_surface = "desktop"', desktop_manifest)
            self.assertIn("host_surface_acceptance_eligible = false", desktop_manifest)
            self.assertIn("acceptance_counted = false", desktop_manifest)


def _make_issue_scope(repo_root: Path) -> Path:
    issue_dir = (
        repo_root
        / "spec-dock"
        / "initiatives"
        / "init-00001-architecture"
        / "epics"
        / "epic-00112-delegated-authoring"
        / "issues"
        / "iss-00126-write-capable"
    )
    issue_dir.mkdir(parents=True)
    (issue_dir / ".meta.json").write_text(json.dumps({"id": "iss-00126"}) + "\n", encoding="utf-8")
    (issue_dir / "design.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    (issue_dir / "plan.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    return issue_dir


def _write_authority_file(
    repo_root: Path,
    *,
    remove_key: str | None = None,
    reviewer_target_hash: str = "hash-1",
    required_grants: list[str] | None = None,
    include_design: bool = False,
    design_required_grants: list[str] | None = None,
    minimal_promotion: bool = False,
    evidence_suffix: str = ".json",
    mismatched_promotion_reviewer_path: bool = False,
) -> Path:
    evidence_dir = repo_root / "evidence"
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
                    reviewer_evidence_path=(
                        evidence_dir / "requirement-reviewer-other.json"
                        if mismatched_promotion_reviewer_path
                        else reviewer_path
                    ),
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
        "reviewer_target_hash": reviewer_target_hash,
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
    authority_path = evidence_dir / "authority.json"
    authority_path.write_text(
        json.dumps(
            {
                "source_revisions": source_revisions,
                "input_authority": input_authority,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return authority_path


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
