import hashlib
import json
from pathlib import Path
import re
import sys

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
    ("tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow"),
    (
        "tests/unit/infra/test_init_update.py::TestInitUpdate::"
        "test_issue_68_provider_only_workflow_is_not_shipped_via_install_root"
    ),
})


POLICY_SKIP_REASON = "full_regression test is disabled by default; use --run-full-regression to run it"
FULL_REGRESSION_LEDGER = (
    Path(__file__).parents[1] / "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/"
    "epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/"
    "iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-ledger.json"
)

_full_regression_guard_active = False
_full_regression_expected: dict[str, str] = {}
_full_regression_failures: dict[str, str] = {}
_full_regression_errors: list[str] = []
_full_regression_missing_nodes: set[str] = set()
_full_regression_ledger_errors: list[str] = []
_full_regression_shard_mode = False


def _normalize_failure_message(message: str, repository: Path) -> str:
    message = message.split(" +  where ", 1)[0]
    message = message.replace(str(repository), "<repo>")
    message = re.sub(r"/tmp/tmp[^/`'\"\\ ]*", "<tmp>", message)
    message = re.sub(
        r"/(?:private/)?var/folders/[^/]+/[^/]+/T/tmp[^/`'\"\\ ]*",
        "<tmp>",
        message,
    )
    message = re.sub(r"/(?:private/)?var/folders/[^'\" ,]+", "<tmp-runtime-path>", message)
    message = re.sub(
        r"(\n\s*Right contains one more item:[^\n]*)\n(?:\s*\n)?\s*Full diff:.*\Z",
        r"\1\n  Use -v to get more diff",
        message,
        flags=re.DOTALL,
    )
    message = message.replace("<repo>/.venv/bin/python3", "<python>")
    message = message.replace("<repo>/.venv/bin/python", "<python>")
    return " ".join(message.split())


def _approved_full_regression_signatures() -> dict[str, str]:
    ledger = json.loads(FULL_REGRESSION_LEDGER.read_text(encoding="utf-8"))
    failure_paths = ledger.get("failure_paths", [])
    expected = {
        entry["nodeid"]: entry["fixed_point_signature_sha256"]
        for entry in failure_paths
        if entry.get("current_status") == "failed"
        and entry.get("fixed_point_status") == "failed"
        and entry.get("disposition") == "approved-no-op"
        and entry.get("failure_signature_match") is True
        and entry.get("current_signature_sha256") == entry.get("fixed_point_signature_sha256")
    }
    if len(expected) != len(failure_paths) or not expected:
        raise pytest.UsageError("full-regression ledger contains incomplete failure signatures")
    return expected


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-full-regression",
        action="store_true",
        default=False,
        help="Run full_regression tests instead of applying the default policy skip.",
    )
    parser.addoption(
        "--full-regression-shard",
        action="store_true",
        default=False,
        help="Run an explicitly selected full-regression shard without global ledger completeness checks.",
    )


def _classification_error(item: pytest.Item, reason: str) -> pytest.UsageError:
    return pytest.UsageError(f"test lane classification conflict for {item.nodeid}: {reason}")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    global _full_regression_guard_active, _full_regression_expected, _full_regression_missing_nodes
    global _full_regression_shard_mode

    run_full_regression = config.getoption("--run-full-regression")
    _full_regression_shard_mode = config.getoption("--full-regression-shard")
    if _full_regression_shard_mode and not run_full_regression:
        raise pytest.UsageError("--full-regression-shard requires --run-full-regression")

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

    if run_full_regression and not config.option.collectonly:
        if _full_regression_shard_mode:
            return
        _full_regression_guard_active = True
        try:
            expected = _approved_full_regression_signatures()
        except (OSError, ValueError, KeyError, TypeError, pytest.UsageError) as exc:
            _full_regression_ledger_errors.append(f"{type(exc).__name__}: {exc}")
            expected = {}
        _full_regression_expected = expected
        collected_nodeids = {item.nodeid for item in items}
        _full_regression_missing_nodes = set(expected) - collected_nodeids


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if not _full_regression_guard_active or not report.failed:
        return
    if report.when != "call":
        _full_regression_errors.append(report.nodeid)
        return
    reprcrash = getattr(report.longrepr, "reprcrash", None)
    message = reprcrash.message if reprcrash is not None else str(report.longrepr)
    normalized = _normalize_failure_message(message, Path.cwd().resolve())
    _full_regression_failures[report.nodeid] = hashlib.sha256(normalized.encode()).hexdigest()


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _full_regression_guard_active:
        return
    expected = _full_regression_expected
    actual = _full_regression_failures
    if (
        not _full_regression_errors
        and not _full_regression_ledger_errors
        and not _full_regression_missing_nodes
        and actual == expected
    ):
        print(f"verified {len(actual)} approved failure signatures against the full-regression ledger")
        return
    details = {
        "unexpected_errors": sorted(_full_regression_errors),
        "ledger_errors": sorted(_full_regression_ledger_errors),
        "missing_expected_nodes": sorted(_full_regression_missing_nodes),
        "missing_failures": sorted(set(expected) - set(actual)),
        "unexpected_failures": sorted(set(actual) - set(expected)),
        "signature_mismatches": sorted(
            nodeid for nodeid in set(actual) & set(expected) if actual[nodeid] != expected[nodeid]
        ),
    }
    print(f"full-regression ledger mismatch: {json.dumps(details, sort_keys=True)}", file=sys.stderr)
    session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
