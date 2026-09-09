from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

from spec_dock import cli
from tests.conftest import REQUIRED_FAST_NODE_IDS

_EXPECTED_REQUIRED_FAST_NODE_IDS = frozenset({
    "tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess",
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_checked_in_dogfooding_mirror_docs_match_provider_assets"
    ),
    ("tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow"),
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_issue_68_provider_only_workflow_is_not_shipped_via_install_root"
    ),
})

_EXPECTED_BASELINE_ROWS = (
    (
        "active",
        "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
        "0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f",
        None,
    ),
    (
        "resolved",
        "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source",
        "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
        "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood",
    ),
    (
        "active",
        "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
        "f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
        "3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
        "55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
        "ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
        "ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
        "22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
        "0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
        "541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
        "44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
        "0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
        "f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
        "3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619",
        None,
    ),
    (
        "active",
        "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
        "20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9",
        None,
    ),
)

_ISSUE_BOUNDARY_SHA256 = {
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/requirement.md": "091de3fe6e7b11b5ab6a269f07a3c4597068c8224bc91b7d8b6f3ddc25e140b1",
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/design.md": "d021cae493648a65e45485e253cd8944a698c55bfc18203d21ae1f3e2d8a29d9",
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/plan.md": "cd2726b90a4bdf068906ab940f47bdd0c999e1a943f50e646d4937cf136971c8",
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/requirement.md": "f240f9e8a87828b13bc5061b5dc59d870c25081eaf7671ff7d7a381d7c7331b7",
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/design.md": "9521b4b102c3cf57b042c288f700ef53c54fd4cb0105b792551bd18d502c5576",
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/plan.md": "45eacc30d921563ad627adac584ea64f835afd1dcdc3902f78c396d11ac6a095",
}

_RETIREMENT_SUCCESSOR_SUFFIXES = frozenset({
    "::test_t01_wire_v12_inventory_and_generated_projection_are_exact",
    "::test_t02_candidate_record_marker_and_legacy_fixture_are_closed_and_deterministic",
    "::test_t03_fixed_roots_slots_seeds_and_protected_sentinels_are_exact",
    "::test_t04_prepared_active_precedes_stage_and_p1_only_rebuilds_registered_entries",
    "::test_t05_linux_and_macos_native_atomic_adapters_have_no_unsafe_fallback",
    "::test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations",
    "::test_t07_legacy_migration_uninstall_and_old_package_mutation_zero",
    "::test_t08_pre_import_shared_lease_and_ready_admission_are_enforced",
    "::test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal",
    "::test_t10_existing_and_new_checkout_are_pinned_and_generation_safe",
    "::test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound",
    "::test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent",
    "::test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical",
    "::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged",
})

_BASELINE_NODE_IDS = frozenset(row[1] for row in _EXPECTED_BASELINE_ROWS)


def _explicit_classification_matches(nodeid: str) -> tuple[str, ...]:
    matches: list[str] = []
    if nodeid in _BASELINE_NODE_IDS:
        matches.append("KEEP-baseline")
    if nodeid in _EXPECTED_REQUIRED_FAST_NODE_IDS:
        matches.append("KEEP-required-fast")
    if nodeid.startswith("tests/unit/provider_lifecycle/"):
        matches.append("KEEP-provider-lifecycle-successors")
    if nodeid.startswith((
        "tests/cli_runtime/test_provider_lifecycle_bootstrap.py::",
        "tests/cli_runtime/test_provider_lifecycle_handoff.py::",
        "tests/cli_runtime/test_generation_checkout.py::",
        "tests/cli_runtime/test_worktree_lifecycle_coordination.py::",
    )):
        matches.append("KEEP-runtime-lifecycle-successors")
    if nodeid.startswith((
        "tests/integration/test_provider_lifecycle_dogfood.py::",
        "tests/integration/test_issue_392_acceptance.py::",
    )):
        matches.append("KEEP-integration-successors")
    if nodeid.startswith("tests/cli_runtime/test_distribution_cutover.py::") and nodeid not in _BASELINE_NODE_IDS:
        matches.append("KEEP-distribution-cutover")
    if nodeid.startswith("tests/unit/infra/test_init_update.py::") and nodeid not in _EXPECTED_REQUIRED_FAST_NODE_IDS:
        matches.append("KEEP-init-update")
    if not matches:
        matches.append("KEEP-default")
    return tuple(matches)


def _collect_all_node_ids(repository: Path) -> set[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return {line for line in result.stdout.splitlines() if line.startswith("tests/") and "::" in line}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent(tmp_path: Path, capsys) -> None:
    repository = Path(__file__).parents[2]
    production = repository / "src" / "spec_dock"
    source = inspect.getsource(cli)
    assert "managed_distribution" not in source
    assert not (production / "managed_distribution.py").exists()
    assert not (production / "assets" / "managed_distribution.json").exists()
    assert all("managed_distribution" not in path.read_text(encoding="utf-8") for path in production.rglob("*.py"))

    target = (tmp_path / "consumer").resolve()
    target.mkdir()
    assert cli.main(["init", str(target), "--json"]) == 0
    install_output = capsys.readouterr().out
    install = json.loads(install_output)
    assert install["code"] == "install-completed"
    assert install["candidate_digest"]

    before_rejected_purge = {
        path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
    }
    assert cli.main(["uninstall", str(target), "--apply", "--remove-specs", "--json"]) == 2
    rejected_output = capsys.readouterr().out
    rejected = json.loads(rejected_output)
    assert rejected["code"] == "spec-history-purge-removed"
    assert {
        path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
    } == before_rejected_purge

    assert cli.main(["uninstall", str(target), "--apply", "--keep-specs", "--json"]) == 0
    uninstall = json.loads(capsys.readouterr().out)
    assert uninstall["code"] == "uninstall-completed"
    assert (target / "spec-dock/spec-dock.version").is_file()


def test_t14_classification_registry_has_no_unclassified_overlap_or_premature_retirement() -> None:
    repository = Path(__file__).parents[2]
    collected = _collect_all_node_ids(repository)
    classifications = {nodeid: _explicit_classification_matches(nodeid) for nodeid in collected}
    unclassified = sorted(nodeid for nodeid, matches in classifications.items() if not matches)
    overlap = sorted(f"{nodeid}: {matches}" for nodeid, matches in classifications.items() if len(matches) != 1)

    retired_file = repository / "tests/unit/infra/test_managed_distribution.py"
    retired_nodes = [
        nodeid for nodeid in collected if nodeid.startswith("tests/unit/infra/test_managed_distribution.py::")
    ]
    missing_successors = sorted(
        suffix for suffix in _RETIREMENT_SUCCESSOR_SUFFIXES if not any(nodeid.endswith(suffix) for nodeid in collected)
    )
    prematurely_retired = []
    if retired_file.exists() or retired_nodes:
        prematurely_retired.append("tests/unit/infra/test_managed_distribution.py is still collected")
    prematurely_retired.extend(f"missing successor: {suffix}" for suffix in missing_successors)

    assert not unclassified
    assert not overlap
    assert not prematurely_retired


def test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged() -> None:
    repository = Path(__file__).parents[2]

    ledger_path = repository / "full-regression-ledger.json"
    assert _sha256(ledger_path) == "838f1415f2a4399a3f18cf7914dc0b2f3648cb06a5d623de4ca7a22648a87a0d"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = ledger["failure_paths"]
    observed_rows = tuple(
        (
            row["lifecycle"],
            row["nodeid"],
            row["fixed_point_signature_sha256"],
            row.get("successor_nodeid"),
        )
        for row in rows
    )
    assert observed_rows == _EXPECTED_BASELINE_ROWS
    assert len(rows) == 15
    assert sum(row["lifecycle"] == "active" for row in rows) == 14
    assert sum(row["lifecycle"] == "resolved" for row in rows) == 1
    assert all(row["current_signature_sha256"] == row["fixed_point_signature_sha256"] for row in rows)
    assert all(row["failure_signature_match"] is True for row in rows)
    assert all(row["current_status"] == row["fixed_point_status"] == "failed" for row in rows)
    assert all(row["disposition"] == "approved-no-op" for row in rows)

    timing_path = repository / "full-regression-timing-weights.json"
    assert _sha256(timing_path) == "820a2b4cf5c11bfb811361468822c98525140a250c99dcf23eba4c63dd4ab297"
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    assert timing["schema_version"] == 1
    assert len(timing["node_seconds"]) == 243

    assert REQUIRED_FAST_NODE_IDS == _EXPECTED_REQUIRED_FAST_NODE_IDS
    for nodeid in _EXPECTED_REQUIRED_FAST_NODE_IDS:
        relative_file, *symbols = nodeid.split("::")
        source = (repository / relative_file).read_text(encoding="utf-8")
        assert all(symbol in source for symbol in symbols)

    tests_root = repository / "tests"
    assert not (tests_root / "unit/infra/test_managed_distribution.py").exists()
    obsolete_remove_flag_test = "test_uninstall_forwards_" + "remove_specs_flag"
    assert not any(obsolete_remove_flag_test in path.read_text(encoding="utf-8") for path in tests_root.rglob("*.py"))

    workflow = (repository / ".github/workflows/provider-ci.yml").read_text(encoding="utf-8")
    assert "on:\n  pull_request:" in workflow
    assert "provider-tests:" in workflow
    assert "provider-distribution-parity:" in workflow
    assert "runs-on: ${{ matrix.os }}" in workflow
    assert "os: [ubuntu-latest, macos-latest]" in workflow
    assert "ref: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "CANDIDATE_SHA: ${{ github.event.pull_request.head.sha }}" in workflow
    for command in (
        "uv run pytest tests/unit/provider_lifecycle",
        "uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py",
        (
            "uv run pytest --run-full-regression --full-regression-shard "
            "tests/cli_runtime/test_provider_lifecycle_bootstrap.py "
            "tests/cli_runtime/test_provider_lifecycle_handoff.py "
            "tests/cli_runtime/test_generation_checkout.py "
            "tests/cli_runtime/test_worktree_lifecycle_coordination.py"
        ),
        "uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py",
    ):
        assert f"run: {command}" in workflow
    assert "make lint" in workflow
    assert "run: uv run pytest\n" in workflow
    assert "test_managed_distribution" not in workflow
    assert "continue-on-error" not in workflow
    assert "verify_full_regression" not in workflow

    for relative_path, expected_sha256 in _ISSUE_BOUNDARY_SHA256.items():
        path = repository / relative_path
        assert path.is_file()
        assert _sha256(path) == expected_sha256
