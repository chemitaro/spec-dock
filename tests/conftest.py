import pytest

HEAVY_NODE_PREFIXES = (
    "tests/cli_runtime/",
    "tests/integration/",
    "tests/manual_tests/",
    "tests/unit/infra/test_init_update.py::",
)

REQUIRED_FAST_NODE_IDS = frozenset({
    "tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_legacy_flag_reports_parser_error",
    "tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess",
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_checked_in_dogfooding_mirror_docs_match_provider_assets"
    ),
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_checked_in_dogfooding_mirror_templates_match_provider_assets"
    ),
    ("tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow"),
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_issue_68_provider_only_workflow_is_not_shipped_via_install_root"
    ),
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets"
    ),
})

# Issue 360 removes the pre-S40B distribution surfaces. These historical
# characterization tests assert files that are intentionally no longer
# shipped; the replacement catalog contract is exercised by
# ``tests/cli_runtime/test_distribution_cutover.py``. Retained runtime,
# preservation, uninstall, and Issue 359 safety tests remain in the suite.
RETIRED_ISSUE360_INIT_UPDATE_PREFIXES = (
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_provider_discussion_interview_template_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_skills_provider_assets_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_creates_expected_structure",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_shipped_docs_describe_workbench_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_gitignore_fallback_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_scaffolds_discussion_guidance_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_discussion_guidance_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_current_guidance_documents_",
    # Existing dogfood parity is intentionally deferred to S80 after the
    # S25/S55 ownership classifier has refreshed the consumer projection.
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_profile_templates_are_provider_and_installed_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_spec_document_templates_keep_policy_out_of_scaffold",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_69_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_install_root_tree_exists",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_authoritative_inventory_paths_are_classified_under_install_root",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_legacy_codex_skills_tree_is_retired",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_70_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_102_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_103_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_105_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_116_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_117_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_127_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_134_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_142_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_176_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_180_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_182_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_188_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_197_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_211_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_218_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_219_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_222_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_232_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_233_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_246_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_247_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_314_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_s04_codex_agent_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_93_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_174_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_chatgpt_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_deleted_role_skill_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_prunes_deleted_role_skill_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_host_adapter_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_generated_native_shims_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_copies_legacy_codex_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_copies_codex_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_manages_native_shims_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_non_boolean_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_manifest_missing_required_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_missing_or_null_required_host_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_required_host_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_duplicate_required_host_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_preflight_rejects_invalid_host_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_missing_or_malformed_required_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_parent_traversal_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_windows_drive_relative_native_shim_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_native_shim_target_file_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_obsolete_exact_file_paths_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_current_dir_obsolete_exact_file_paths_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_rejects_directory_like_obsolete_exact_file_paths_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_partial_unlink_failure_reports_failed_separately",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_json_covers_success_rerun_and_partial_failure_statuses",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_dry_run_removes_known_agent_skill_mismatch",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_dry_run_removes_exact_match_bootstrap_and_product_reusable_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_dry_run_preserves_mismatch_bootstrap_and_product_reusable_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_dry_run_preserves_non_core_comparison_errors_for_manual_review",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_migrates_legacy_single_skill_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_installs_full_skill_set_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_skill_sync_converges_",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_parent_fallback_reresolve_inside_lock_parity",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_active_deps_status_parity",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_same_repo_index_missing_view_fallback_parity",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_active_deps_parity",
)

POLICY_SKIP_REASON = "full_regression test is disabled by default; use --run-full-regression to run it"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-full-regression",
        action="store_true",
        default=False,
        help="Run full_regression tests instead of applying the default policy skip.",
    )


def _classification_error(item: pytest.Item, reason: str) -> pytest.UsageError:
    return pytest.UsageError(f"test lane classification conflict for {item.nodeid}: {reason}")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    run_full_regression = config.getoption("--run-full-regression")

    for item in items:
        if item.nodeid.startswith(RETIRED_ISSUE360_INIT_UPDATE_PREFIXES):
            item.add_marker(
                pytest.mark.skip(reason="retired legacy distribution surface; covered by Issue 360 cutover tests")
            )

        has_fast = item.get_closest_marker("fast") is not None
        has_full_regression = item.get_closest_marker("full_regression") is not None

        if has_fast and has_full_regression:
            raise _classification_error(
                item,
                "item cannot have both fast and full_regression markers",
            )

        if item.nodeid in REQUIRED_FAST_NODE_IDS:
            if has_full_regression:
                raise _classification_error(
                    item,
                    "required-fast item cannot have a full_regression marker",
                )
            if not has_fast:
                item.add_marker("fast")
        elif item.nodeid.startswith(HEAVY_NODE_PREFIXES):
            if has_fast:
                raise _classification_error(
                    item,
                    "heavy-prefix item cannot have a fast marker",
                )
            if not has_full_regression:
                item.add_marker("full_regression")
        elif not has_fast and not has_full_regression:
            item.add_marker("fast")

        is_fast = item.get_closest_marker("fast") is not None
        is_full_regression = item.get_closest_marker("full_regression") is not None
        if is_fast == is_full_regression:
            raise _classification_error(
                item,
                "item must have exactly one of fast or full_regression",
            )
        if is_full_regression and not run_full_regression:
            item.add_marker(pytest.mark.skip(reason=POLICY_SKIP_REASON))
