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
