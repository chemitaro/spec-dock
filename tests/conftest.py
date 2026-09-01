from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Literal, cast

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from scripts.quality.full_regression_baseline import CandidateObservation, FullRegressionBaseline

HEAVY_NODE_PREFIXES = (
    "tests/cli_runtime/",
    "tests/integration/",
    "tests/manual_tests/",
    "tests/unit/infra/test_init_update.py::",
)

REQUIRED_FAST_NODE_IDS = frozenset({
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
FULL_REGRESSION_LEDGER = Path(__file__).parents[1] / "full-regression-ledger.json"

_full_regression_guard_active = False
_full_regression_ledger_errors: list[str] = []
_full_regression_shard_mode = False
_full_regression_collected: tuple[str, ...] = ()
_full_regression_reports: list[pytest.TestReport] = []
_full_regression_baseline: FullRegressionBaseline | None = None
_full_regression_observation_path: Path | None = None


def _report_outcome(report: pytest.TestReport) -> str | None:
    was_xfail = getattr(report, "wasxfail", None)
    if report.when != "call":
        if report.failed:
            return "error"
        if report.skipped:
            return "skipped"
        return None
    if was_xfail:
        return "xfailed" if report.skipped else "xpassed"
    if report.failed:
        return "failed"
    if report.skipped:
        return "skipped"
    if report.passed:
        return "passed"
    return "error"


def _report_failure_message(report: pytest.TestReport) -> str:
    reprcrash = getattr(report.longrepr, "reprcrash", None)
    return reprcrash.message if reprcrash is not None else str(report.longrepr)


def build_candidate_observation(
    collected: Iterable[str],
    reports: Iterable[pytest.TestReport],
    *,
    repository: Path,
) -> CandidateObservation:
    """Adapt pytest collection/reports to the shared pure evaluator input."""

    from scripts.quality.full_regression_baseline import CandidateObservation, failure_signature

    collected_nodes = tuple(collected)
    executed_nodes: list[str] = []
    outcomes: dict[str, str] = {}
    signatures: dict[str, str] = {}
    for report in reports:
        outcome = _report_outcome(report)
        if outcome is None:
            continue
        executed_nodes.append(report.nodeid)
        outcomes[report.nodeid] = outcome
        if outcome == "failed" and report.when == "call":
            signatures[report.nodeid] = failure_signature(_report_failure_message(report), repository)
    return CandidateObservation(
        collected=collected_nodes,
        executed=tuple(executed_nodes),
        outcomes=cast("Mapping[str, Literal['passed', 'failed', 'skipped', 'xfailed', 'xpassed', 'error']]", outcomes),
        failure_signatures=signatures,
        retirement_evidence={},
    )


def _observation_payload(observation: CandidateObservation) -> dict[str, object]:
    return {
        "schema_version": 1,
        "collected": list(observation.collected),
        "executed": list(observation.executed),
        "outcomes": dict(observation.outcomes),
        "failure_signatures": dict(observation.failure_signatures),
        "retirement_evidence": {
            evidence_id: {"checked": evidence.checked, "outcome": evidence.outcome}
            for evidence_id, evidence in observation.retirement_evidence.items()
        },
    }


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
    parser.addoption(
        "--full-regression-observation",
        action="store",
        type=Path,
        default=None,
        help="Write the machine-readable observation for a full-regression shard.",
    )


def _classification_error(item: pytest.Item, reason: str) -> pytest.UsageError:
    return pytest.UsageError(f"test lane classification conflict for {item.nodeid}: {reason}")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    global _full_regression_baseline, _full_regression_collected, _full_regression_guard_active
    global _full_regression_ledger_errors, _full_regression_observation_path
    global _full_regression_reports, _full_regression_shard_mode

    run_full_regression = config.getoption("--run-full-regression")
    _full_regression_shard_mode = config.getoption("--full-regression-shard")
    _full_regression_observation_path = config.getoption("--full-regression-observation")
    _full_regression_baseline = None
    _full_regression_ledger_errors = []
    _full_regression_reports = []
    _full_regression_guard_active = False
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
        _full_regression_collected = tuple(item.nodeid for item in items)
        if _full_regression_shard_mode:
            return
        _full_regression_guard_active = True
        try:
            from scripts.quality.full_regression_baseline import parse_baseline

            _full_regression_baseline = parse_baseline(json.loads(FULL_REGRESSION_LEDGER.read_text(encoding="utf-8")))
        except (ImportError, OSError, ValueError, KeyError, TypeError, pytest.UsageError) as exc:
            _full_regression_ledger_errors.append(f"{type(exc).__name__}: {exc}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if not (_full_regression_guard_active or _full_regression_shard_mode):
        return
    _full_regression_reports.append(report)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if _full_regression_shard_mode:
        if _full_regression_observation_path is None:
            return
        try:
            observation = build_candidate_observation(
                _full_regression_collected,
                _full_regression_reports,
                repository=Path.cwd().resolve(),
            )
            _full_regression_observation_path.parent.mkdir(parents=True, exist_ok=True)
            _full_regression_observation_path.write_text(
                json.dumps(_observation_payload(observation), sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError, TypeError) as exc:
            print(f"full-regression observation write failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
        return
    if not _full_regression_guard_active:
        return
    if _full_regression_baseline is None or _full_regression_ledger_errors:
        details = {"ledger_errors": sorted(_full_regression_ledger_errors)}
        print(f"full-regression ledger mismatch: {json.dumps(details, sort_keys=True)}", file=sys.stderr)
        session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
        return
    try:
        from scripts.quality.full_regression_baseline import evaluate_baseline

        observation = build_candidate_observation(
            _full_regression_collected,
            _full_regression_reports,
            repository=Path.cwd().resolve(),
        )
        result = evaluate_baseline(_full_regression_baseline, observation)
    except (ImportError, OSError, ValueError, TypeError) as exc:
        details = {"ledger_errors": [f"{type(exc).__name__}: {exc}"]}
        print(f"full-regression ledger mismatch: {json.dumps(details, sort_keys=True)}", file=sys.stderr)
        session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
        return
    if result.verified:
        print(f"verified {len(result.active_verified)} approved failure signatures against the full-regression ledger")
        return
    print(f"full-regression ledger mismatch: {json.dumps(result.to_dict(), sort_keys=True)}", file=sys.stderr)
    session.exitstatus = pytest.ExitCode.INTERNAL_ERROR
