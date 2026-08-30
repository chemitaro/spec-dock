from collections.abc import Mapping
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace
from typing import cast

import pytest
from scripts.quality.full_regression_baseline import (
    CandidateObservation,
    evaluate_baseline,
    failure_signature,
    normalize_failure_message,
    parse_baseline,
)

from tests.conftest import build_candidate_observation

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

POLICY_SKIP_HINT = "--run-full-regression"
FULL_REGRESSION_VERIFIER = (
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/"
    "epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/"
    "iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py"
)
FULL_REGRESSION_HISTORICAL_LEDGER = (
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/"
    "epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/"
    "iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-ledger.json"
)
FULL_REGRESSION_HISTORICAL_TIMING_WEIGHTS = (
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/"
    "epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/"
    "iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-timing-weights.json"
)
FULL_REGRESSION_ROOT_LEDGER = "full-regression-ledger.json"
FULL_REGRESSION_ROOT_TIMING_WEIGHTS = "full-regression-timing-weights.json"
FULL_REGRESSION_LEDGER = FULL_REGRESSION_ROOT_LEDGER
ISSUE368_HISTORICAL_LEDGER_SHA256 = "3fb3192110ad9981a6826dae8a5eea30f12bc9f5b65106173dc5777749a8ea3b"
ISSUE368_HISTORICAL_TIMING_WEIGHTS_SHA256 = "b647b3a0ee3f24202c954e0dd367809dc8981ba686bf6a67f349868ab01da5fc"
PRE_MIGRATION_LEDGER_CURRENT_HEAD = "fc02e1215d2b9e056a2c18bd1411fe489efdf2f2"
PRE_MIGRATION_SCHEMA1_PROJECTION_SHA256 = "f997de22e6507e6a27ce76284df079c9dd1e65bb015e309801b4aa041ea3dfcf"
RETAINED_SKILL_HISTORICAL_NODE = (
    "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source"
)
RETAINED_SKILL_SUCCESSOR_NODE = "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood"


def test_full_regression_authority_is_root_and_issue368_history_is_frozen() -> None:
    repository = _repo_root()

    root_ledger = repository / FULL_REGRESSION_ROOT_LEDGER
    root_timing_weights = repository / FULL_REGRESSION_ROOT_TIMING_WEIGHTS
    assert root_ledger.is_file()
    assert root_timing_weights.is_file()

    canonical_sources = (
        repository / "tests/conftest.py",
        repository / "scripts/quality/verify_full_regression.py",
        repository / ".github/workflows/provider-full-regression.yml",
    )
    for source_path in canonical_sources:
        source = source_path.read_text(encoding="utf-8")
        assert "iss-00368-recognized-workspace-reconciliation" not in source

    historical_artifacts = (
        (
            repository / FULL_REGRESSION_HISTORICAL_LEDGER,
            ISSUE368_HISTORICAL_LEDGER_SHA256,
        ),
        (
            repository / FULL_REGRESSION_HISTORICAL_TIMING_WEIGHTS,
            ISSUE368_HISTORICAL_TIMING_WEIGHTS_SHA256,
        ),
    )
    for artifact_path, expected_sha256 in historical_artifacts:
        assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == expected_sha256


def test_full_regression_signature_normalization_is_platform_independent() -> None:
    repository = Path("/repo")
    macos_runtime_error = (
        "RuntimeError: retry `/private/var/folders/aa/bb/T/tmpabc/spec-dock/scripts/spec-dock update`."
    )
    linux_runtime_error = "RuntimeError: retry `/tmp/tmpxyz/spec-dock/scripts/spec-dock update`."
    compact_assertion = (
        "AssertionError: assert [] == [('/repo', 10000)]\n"
        "  \n"
        "  Right contains one more item: ('/repo', 10000)\n"
        "  Use -v to get more diff"
    )
    expanded_assertion = (
        "AssertionError: assert [] == [('/repo', 10000)]\n"
        "  \n"
        "  Right contains one more item: ('/repo', 10000)\n"
        "  \n"
        "  Full diff:\n"
        "  + []\n"
        "  - [('/repo', 10000)]"
    )

    assert normalize_failure_message(macos_runtime_error, repository) == normalize_failure_message(
        linux_runtime_error,
        repository,
    )
    assert normalize_failure_message(compact_assertion, repository) == normalize_failure_message(
        expanded_assertion,
        repository,
    )


def test_full_regression_ledger_migration_preserves_schema1_history() -> None:
    payload = json.loads((_repo_root() / FULL_REGRESSION_LEDGER).read_text(encoding="utf-8"))
    rows = payload["failure_paths"]
    assert isinstance(rows, list)

    schema1_projection = [
        {
            "nodeid": row["nodeid"],
            "fixed_point_signature_sha256": row["fixed_point_signature_sha256"],
            "rationale": row.get("rationale", ""),
        }
        for row in rows
    ]
    projection_bytes = json.dumps(
        schema1_projection,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    assert payload["schema_version"] == 2
    assert payload["current_head_sha"] == PRE_MIGRATION_LEDGER_CURRENT_HEAD
    assert hashlib.sha256(projection_bytes).hexdigest() == PRE_MIGRATION_SCHEMA1_PROJECTION_SHA256

    resolved_rows = [row for row in rows if row.get("lifecycle") == "resolved"]
    assert [row["nodeid"] for row in resolved_rows] == [RETAINED_SKILL_HISTORICAL_NODE]
    assert resolved_rows[0]["resolution_mode"] == "superseded"
    assert resolved_rows[0]["successor_nodeid"] == RETAINED_SKILL_SUCCESSOR_NODE
    assert all(row.get("lifecycle") == "active" for row in rows if row["nodeid"] != RETAINED_SKILL_HISTORICAL_NODE)
    assert not any(row.get("lifecycle") == "retired" for row in rows)


def _fake_report(
    nodeid: str,
    *,
    when: str = "call",
    outcome: str,
    wasxfail: str | None = None,
    message: str = "",
) -> pytest.TestReport:
    return cast(
        "pytest.TestReport",
        SimpleNamespace(
            nodeid=nodeid,
            when=when,
            outcome=outcome,
            passed=outcome == "passed",
            failed=outcome == "failed",
            skipped=outcome == "skipped",
            wasxfail=wasxfail,
            longrepr=SimpleNamespace(reprcrash=SimpleNamespace(message=message)) if message else "",
        ),
    )


def test_pytest_adapter_builds_typed_observation_for_xfail_and_phase_errors() -> None:
    repository = Path("/repo")
    passed = "tests/sample.py::test_passed"
    failed = "tests/sample.py::test_failed"
    skipped = "tests/sample.py::test_skipped"
    xfailed = "tests/sample.py::test_xfailed"
    xpassed = "tests/sample.py::test_xpassed"
    setup_error = "tests/sample.py::test_setup_error"
    teardown_error = "tests/sample.py::test_teardown_error"
    reports = (
        _fake_report(passed, outcome="passed"),
        _fake_report(failed, outcome="failed", message="AssertionError: fixed failure"),
        _fake_report(skipped, outcome="skipped"),
        _fake_report(xfailed, outcome="skipped", wasxfail="expected failure"),
        _fake_report(xpassed, outcome="passed", wasxfail="unexpected pass"),
        _fake_report(setup_error, when="setup", outcome="failed", message="fixture setup failed"),
        _fake_report(teardown_error, when="teardown", outcome="failed", message="teardown failed"),
    )

    observation = build_candidate_observation(
        (passed, failed, skipped, xfailed, xpassed, setup_error, teardown_error),
        reports,
        repository=repository,
    )

    assert isinstance(observation, CandidateObservation)
    assert observation.executed == (passed, failed, skipped, xfailed, xpassed, setup_error, teardown_error)
    assert observation.outcomes == {
        passed: "passed",
        failed: "failed",
        skipped: "skipped",
        xfailed: "xfailed",
        xpassed: "xpassed",
        setup_error: "error",
        teardown_error: "error",
    }
    assert observation.failure_signatures == {
        failed: failure_signature("AssertionError: fixed failure", repository),
    }


def test_pytest_adapter_preserves_duplicate_and_missing_coverage_for_shared_evaluator() -> None:
    duplicate = "tests/sample.py::test_duplicate"
    missing = "tests/sample.py::test_missing"
    observation = build_candidate_observation(
        (duplicate, duplicate, missing),
        (_fake_report(duplicate, outcome="passed"),),
        repository=Path("/repo"),
    )
    baseline = parse_baseline({
        "schema_version": 2,
        "failure_paths": [
            {
                "nodeid": duplicate,
                "fixed_point_signature_sha256": "a" * 64,
                "rationale": "historical",
                "lifecycle": "resolved",
                "resolution_mode": "fixed-in-place",
            },
            {
                "nodeid": missing,
                "fixed_point_signature_sha256": "b" * 64,
                "rationale": "historical",
                "lifecycle": "resolved",
                "resolution_mode": "fixed-in-place",
            },
        ],
    })

    result = evaluate_baseline(baseline, observation)

    assert not result.verified
    assert any(item.code == "coverage_mismatch" for item in result.violations)


def test_standalone_observation_round_trip_and_merge_use_typed_shared_result() -> None:
    from scripts.quality.verify_full_regression import (
        merge_observations,
        observation_from_json,
        observation_to_json,
    )

    first = CandidateObservation(
        collected=("tests/sample.py::test_first",),
        executed=("tests/sample.py::test_first",),
        outcomes={"tests/sample.py::test_first": "xpassed"},
        failure_signatures={},
        retirement_evidence={},
    )
    second = CandidateObservation(
        collected=("tests/sample.py::test_second",),
        executed=("tests/sample.py::test_second",),
        outcomes={"tests/sample.py::test_second": "passed"},
        failure_signatures={},
        retirement_evidence={},
    )

    round_tripped = observation_from_json(observation_to_json(first))
    merged = merge_observations((round_tripped, second))

    assert round_tripped == first
    assert merged.collected == ("tests/sample.py::test_first", "tests/sample.py::test_second")
    assert merged.outcomes["tests/sample.py::test_first"] == "xpassed"
    assert merged.outcomes["tests/sample.py::test_second"] == "passed"
    baseline = parse_baseline({
        "schema_version": 2,
        "failure_paths": [
            {
                "nodeid": "tests/sample.py::test_first",
                "fixed_point_signature_sha256": "a" * 64,
                "rationale": "historical",
                "lifecycle": "resolved",
                "resolution_mode": "fixed-in-place",
            }
        ],
    })
    assert not evaluate_baseline(baseline, round_tripped).verified


def test_standalone_runner_uses_hook_observation_without_junit_inference(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from scripts.quality import verify_full_regression as verifier

    candidate_sha = "a" * 40
    nodeid = "tests/sample.py::test_failure"
    artifact_root = tmp_path / "artifacts"
    verifier.LEDGER = tmp_path / "ledger.json"
    verifier.LEDGER.write_text(
        json.dumps({
            "schema_version": 1,
            "current_head_sha": candidate_sha,
            "failure_paths": [
                {
                    "nodeid": nodeid,
                    "fixed_point_signature_sha256": "0" * 64,
                    "rationale": "historical",
                }
            ],
        }),
        encoding="utf-8",
    )
    verifier.TIMING_WEIGHTS = tmp_path / "timing-weights.json"
    verifier.TIMING_WEIGHTS.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        verifier.sys,
        "argv",
        ["verify_full_regression.py", "--artifact-dir", str(artifact_root), "--shards", "1"],
    )
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 0.0)

    commands: list[list[str]] = []

    def fake_run_streamed(
        argv: list[str],
        *,
        cwd: Path,
        output_path: Path,
        stream: bool = True,
    ) -> int:
        del cwd, stream
        commands.append(argv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if "--collect-only" in argv:
            output_path.write_text(f"[   0.0s] {nodeid}\n", encoding="utf-8")
            return 0
        observation_path = Path(
            next(arg.split("=", 1)[1] for arg in argv if arg.startswith("--full-regression-observation="))
        )
        observation_path.write_text(
            json.dumps({
                "schema_version": 1,
                "collected": [nodeid],
                "executed": [nodeid],
                "outcomes": {nodeid: "failed"},
                "failure_signatures": {nodeid: "0" * 64},
                "retirement_evidence": {},
            }),
            encoding="utf-8",
        )
        output_path.write_text("", encoding="utf-8")
        return 0

    monkeypatch.setattr(verifier, "_run_streamed", fake_run_streamed)
    monkeypatch.setattr(verifier, "_load_timing_weights", lambda repository, head: ({}, 1.0))

    def fake_subprocess_run(argv, **kwargs):
        if argv[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(argv, 0, stdout=f"{candidate_sha}\n")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(verifier.subprocess, "run", fake_subprocess_run)

    assert verifier.main() == 0
    result_paths = list(artifact_root.glob("*/result.json"))
    assert len(result_paths) == 1
    result = json.loads(result_paths[0].read_text(encoding="utf-8"))
    assert result["status"] == "verified"
    assert any("--full-regression-observation=" in arg for command in commands for arg in command)
    assert not any("--junitxml=" in arg for command in commands for arg in command)


def test_manual_full_regression_shard_without_observation_keeps_pytest_exit_status(
    tmp_path: Path,
) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/unit/test_manual_shard.py": (
                "import pytest\n\n"
                "@pytest.mark.full_regression\n"
                "def test_passes():\n"
                "    pass\n\n"
                "@pytest.mark.full_regression\n"
                "def test_fails():\n"
                "    assert False\n"
            )
        },
    )
    result = _run_pytest(
        project,
        "--run-full-regression",
        "--full-regression-shard",
        "-p",
        "no:cacheprovider",
        "tests/unit/test_manual_shard.py::test_passes",
        "tests/unit/test_manual_shard.py::test_fails",
    )

    assert result.returncode == 1, _result_output(result)
    assert "full-regression shard observation path is missing" not in _result_output(result)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_full_regression_verifier():
    path = _repo_root() / FULL_REGRESSION_VERIFIER
    spec = importlib.util.spec_from_file_location("issue_368_full_regression_verifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_regression_timing_evidence_is_observation_only(monkeypatch) -> None:
    verifier = _load_full_regression_verifier()
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 610.0)

    evidence = verifier._timing_evidence(
        overall_started=0.0,
        collection_seconds=110.0,
        shard_elapsed_seconds=500.0,
    )

    assert evidence == {
        "collection_seconds": 110.0,
        "shard_elapsed_seconds": 500.0,
        "total_elapsed_seconds": 610.0,
    }


@pytest.mark.parametrize("removed_flag", ["--timeout-seconds", "--max-total-seconds"])
def test_full_regression_removed_budget_flags_are_rejected(monkeypatch, removed_flag: str) -> None:
    verifier = _load_full_regression_verifier()
    monkeypatch.setattr(verifier.sys, "argv", ["verify-full-regression.py", removed_flag, "1"])

    with pytest.raises(SystemExit) as exc_info:
        verifier._parse_args()

    assert exc_info.value.code == 2


def test_full_regression_stream_waits_for_natural_completion_and_saves_unterminated_output(
    tmp_path: Path,
) -> None:
    verifier = _load_full_regression_verifier()
    output_path = tmp_path / "unterminated.log"

    code = verifier._run_streamed(
        [
            sys.executable,
            "-c",
            (
                "import sys, time; sys.stdout.write('unterminated'); sys.stdout.flush(); "
                "time.sleep(0.1); raise SystemExit(7)"
            ),
        ],
        cwd=tmp_path,
        output_path=output_path,
        stream=False,
    )

    assert code == 7
    assert "unterminated" in output_path.read_text(encoding="utf-8")


def test_full_regression_workflow_has_no_execution_time_caps() -> None:
    workflow = (_repo_root() / ".github/workflows/provider-full-regression.yml").read_text(encoding="utf-8")

    assert "timeout-minutes" not in workflow
    assert "--timeout-seconds" not in workflow
    assert "--max-total-seconds" not in workflow
    assert "--shards 4" in workflow


def test_full_regression_workflow_uses_canonical_runner_without_issue368_fallback() -> None:
    workflow = (_repo_root() / ".github/workflows/provider-full-regression.yml").read_text(encoding="utf-8")
    flattened = " ".join(workflow.split())

    assert "uv run python -m scripts.quality.verify_full_regression --shards 4" in flattened
    assert "verify-full-regression.py" not in workflow


def test_full_regression_main_keeps_verified_status_after_long_observation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    verifier = _load_full_regression_verifier()
    candidate_sha = "a" * 40
    nodeid = "tests/sample.py::test_one"
    artifact_root = tmp_path / "artifacts"
    verifier.LEDGER = tmp_path / "ledger.json"
    verifier.LEDGER.write_text(
        json.dumps({
            "current_head_sha": candidate_sha,
            "failure_paths": [
                {
                    "nodeid": nodeid,
                    "current_status": "failed",
                    "fixed_point_status": "failed",
                    "disposition": "approved-no-op",
                    "failure_signature_match": True,
                    "current_signature_sha256": "0" * 64,
                    "fixed_point_signature_sha256": "0" * 64,
                }
            ],
        }),
        encoding="utf-8",
    )
    verifier.TIMING_WEIGHTS = tmp_path / "timing-weights.json"
    verifier.TIMING_WEIGHTS.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        verifier.sys,
        "argv",
        [
            "verify-full-regression.py",
            "--artifact-dir",
            str(artifact_root),
            "--shards",
            "1",
        ],
    )

    monotonic_calls = 0

    def long_observation() -> float:
        nonlocal monotonic_calls
        monotonic_calls += 1
        return 0.0 if monotonic_calls <= 2 else 601.0

    monkeypatch.setattr(verifier.time, "monotonic", long_observation)

    def fake_run(
        argv: list[str],
        *,
        cwd: Path,
        output_path: Path,
        stream: bool = True,
    ) -> int:
        del cwd, stream
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if "--collect-only" in argv:
            output_path.write_text(f"[   0.0s] {nodeid}\n", encoding="utf-8")
        else:
            junit_path = Path(next(arg.split("=", 1)[1] for arg in argv if arg.startswith("--junitxml=")))
            junit_path.write_text("<testsuite />", encoding="utf-8")
            output_path.write_text("", encoding="utf-8")
        return 0

    monkeypatch.setattr(verifier, "_run_streamed", fake_run)
    monkeypatch.setattr(verifier, "_load_timing_weights", lambda repository, head: ({}, 1.0))
    monkeypatch.setattr(verifier, "_junit_nodeids", lambda junit_path: {nodeid})
    monkeypatch.setattr(verifier, "_failure_signatures", lambda junit_path, repository: ({nodeid: "0" * 64}, []))

    def fake_subprocess_run(argv, **kwargs):
        if argv[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(argv, 0, stdout=f"{candidate_sha}\n")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(verifier.subprocess, "run", fake_subprocess_run)

    assert verifier.main() == 0
    result_paths = list(artifact_root.glob("*/result.json"))
    assert len(result_paths) == 1
    result = json.loads(result_paths[0].read_text(encoding="utf-8"))
    assert result["status"] == "verified"
    assert abs(result["total_elapsed_seconds"] - 601.0) < 1e-9


def test_full_regression_main_collects_all_shards_before_invalid_execution_result(
    monkeypatch,
    tmp_path: Path,
) -> None:
    verifier = _load_full_regression_verifier()
    candidate_sha = "b" * 40
    nodeids = ("tests/sample.py::test_one", "tests/sample.py::test_two")
    artifact_root = tmp_path / "artifacts"
    verifier.LEDGER = tmp_path / "ledger.json"
    verifier.LEDGER.write_text(
        json.dumps({
            "current_head_sha": candidate_sha,
            "failure_paths": [
                {
                    "nodeid": nodeids[0],
                    "current_status": "failed",
                    "fixed_point_status": "failed",
                    "disposition": "approved-no-op",
                    "failure_signature_match": True,
                    "current_signature_sha256": "0" * 64,
                    "fixed_point_signature_sha256": "0" * 64,
                }
            ],
        }),
        encoding="utf-8",
    )
    verifier.TIMING_WEIGHTS = tmp_path / "timing-weights.json"
    verifier.TIMING_WEIGHTS.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        verifier.sys,
        "argv",
        [
            "verify-full-regression.py",
            "--artifact-dir",
            str(artifact_root),
            "--shards",
            "2",
        ],
    )
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 0.0)

    invocations: list[tuple[str, ...]] = []

    def fake_run(
        argv: list[str],
        *,
        cwd: Path,
        output_path: Path,
        stream: bool = True,
    ) -> int:
        del cwd, stream
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if "--collect-only" in argv:
            output_path.write_text("".join(f"[   0.0s] {nodeid}\n" for nodeid in nodeids), encoding="utf-8")
            return 0
        selected = tuple(arg for arg in argv if arg.startswith("tests/"))
        invocations.append(selected)
        junit_path = Path(next(arg.split("=", 1)[1] for arg in argv if arg.startswith("--junitxml=")))
        junit_path.write_text("<testsuite />", encoding="utf-8")
        output_path.write_text("", encoding="utf-8")
        return 2 if selected == (nodeids[0],) else 0

    monkeypatch.setattr(verifier, "_run_streamed", fake_run)
    monkeypatch.setattr(verifier, "_load_timing_weights", lambda repository, head: ({}, 1.0))

    def fake_subprocess_run(argv, **kwargs):
        if argv[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(argv, 0, stdout=f"{candidate_sha}\n")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(verifier.subprocess, "run", fake_subprocess_run)

    assert verifier.main() == 1
    assert set(invocations) == {(nodeids[0],), (nodeids[1],)}
    result_paths = list(artifact_root.glob("*/result.json"))
    assert len(result_paths) == 1
    result = json.loads(result_paths[0].read_text(encoding="utf-8"))
    assert result["status"] == "shard-execution-invalid"
    assert {shard["exit_code"] for shard in result["shards"]} == {2}


def test_full_regression_weighted_shards_are_deterministic_and_preserve_collection_order() -> None:
    verifier = _load_full_regression_verifier()
    nodeids = [
        "tests/sample.py::test_d",
        "tests/sample.py::test_c",
        "tests/sample.py::test_b",
        "tests/sample.py::test_a",
    ]

    shards = verifier._partition_nodeids(
        nodeids,
        2,
        timing_weights={
            "tests/sample.py::test_a": 8.0,
            "tests/sample.py::test_b": 7.0,
        },
        default_weight=1.0,
    )

    assert shards == [
        ["tests/sample.py::test_c", "tests/sample.py::test_a"],
        ["tests/sample.py::test_d", "tests/sample.py::test_b"],
    ]
    assert sorted(nodeid for shard in shards for nodeid in shard) == sorted(nodeids)


def test_full_regression_weighted_shards_spread_known_slow_nodes() -> None:
    verifier = _load_full_regression_verifier()
    slow = [f"tests/sample.py::test_slow_{index}" for index in range(4)]
    fast = [f"tests/sample.py::test_fast_{index}" for index in range(8)]

    shards = verifier._partition_nodeids(
        [*slow, *fast],
        4,
        timing_weights=dict.fromkeys(slow, 10.0),
        default_weight=1.0,
    )

    assert all(len(set(shard) & set(slow)) == 1 for shard in shards)
    assert {nodeid for shard in shards for nodeid in shard} == {*slow, *fast}


def test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup() -> None:
    from tests.cli_runtime.conftest import _can_reuse_fresh_init_result

    module = "tests.cli_runtime.test_distribution_cutover"

    assert _can_reuse_fresh_init_result(module, "test_s50_update_restores_missing_asset")
    assert _can_reuse_fresh_init_result(module, "test_s70_uninstall_removes_managed_asset")
    assert _can_reuse_fresh_init_result(module, "test_i368_recognized_update_stays_on_held_root")
    assert not _can_reuse_fresh_init_result(module, "test_i369_fresh_entrypoint_matrix")
    assert not _can_reuse_fresh_init_result(module, "test_s70_uninstall_allows_fresh_reinit")
    assert not _can_reuse_fresh_init_result(module, "test_s45_init_materializes_current_catalog")


def test_full_regression_shards_preserve_ledger_assertion_verbosity() -> None:
    verifier = (_repo_root() / FULL_REGRESSION_VERIFIER).read_text(encoding="utf-8")

    assert '"-q",' in verifier
    assert '"-vv",' not in verifier


def _run_pytest(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def _result_output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def _collected_node_ids(result: subprocess.CompletedProcess[str]) -> set[str]:
    return {line for line in result.stdout.splitlines() if line.startswith("tests/") and "::" in line}


def _prepare_mini_project(
    tmp_path: Path,
    test_files: Mapping[str, str],
    *,
    ledger_guard: bool = False,
) -> Path:
    shared_quality_root = _repo_root() / "scripts"
    mini_quality_root = tmp_path / "scripts"
    (mini_quality_root / "quality").mkdir(parents=True)
    shutil.copy2(shared_quality_root / "__init__.py", mini_quality_root / "__init__.py")
    shutil.copy2(
        shared_quality_root / "quality" / "__init__.py",
        mini_quality_root / "quality" / "__init__.py",
    )
    shutil.copy2(
        shared_quality_root / "quality" / "full_regression_baseline.py",
        mini_quality_root / "quality" / "full_regression_baseline.py",
    )
    classifier_path = _repo_root() / "tests" / "conftest.py"
    assert classifier_path.is_file(), f"S01 classifier is missing: {classifier_path}"

    tests_root = tmp_path / "tests"
    tests_root.mkdir(parents=True)
    classifier = classifier_path.read_text(encoding="utf-8")
    if not ledger_guard:
        classifier = classifier.replace(
            "if run_full_regression and not config.option.collectonly:\n",
            "if False and run_full_regression and not config.option.collectonly:\n",
        )
    (tests_root / "conftest.py").write_text(classifier, encoding="utf-8")
    (tmp_path / "pytest.ini").write_text(
        "[pytest]\n"
        "addopts = --strict-markers\n"
        "markers =\n"
        "    fast: default provider test lane\n"
        "    full_regression: long-running provider regression lane\n",
        encoding="utf-8",
    )

    for relative_path, source in test_files.items():
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")

    return tmp_path


def _write_full_regression_ledger(project: Path, nodeids: tuple[str, ...]) -> None:
    ledger = project / "full-regression-ledger.json"
    ledger.write_text(
        json.dumps({
            "schema_version": 1,
            "failure_paths": [
                {
                    "nodeid": nodeid,
                    "current_status": "failed",
                    "fixed_point_status": "failed",
                    "disposition": "approved-no-op",
                    "failure_signature_match": True,
                    "current_signature_sha256": "0" * 64,
                    "fixed_point_signature_sha256": "0" * 64,
                }
                for nodeid in nodeids
            ],
        }),
        encoding="utf-8",
    )


def test_focused_collection_does_not_require_global_inventory(tmp_path: Path) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {"tests/unit/test_fast_sample.py": "def test_fast_sample():\n    pass\n"},
    )

    result = _run_pytest(
        project,
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        "tests/unit/test_fast_sample.py::test_fast_sample",
    )

    assert result.returncode == 0, _result_output(result)
    assert _collected_node_ids(result) == {"tests/unit/test_fast_sample.py::test_fast_sample"}


def test_repo_root_lane_partition_is_complete_and_keeps_required_fast_nodes() -> None:
    repo_root = _repo_root()
    common_args = ("--collect-only", "-q", "-p", "no:cacheprovider")

    all_result = _run_pytest(repo_root, *common_args)
    fast_result = _run_pytest(repo_root, *common_args, "-m", "fast")
    full_result = _run_pytest(repo_root, *common_args, "-m", "full_regression")

    assert all_result.returncode == 0, _result_output(all_result)
    assert fast_result.returncode == 0, _result_output(fast_result)
    assert full_result.returncode == 0, _result_output(full_result)

    collected = _collected_node_ids(all_result)
    fast = _collected_node_ids(fast_result)
    full_regression = _collected_node_ids(full_result)
    unclassified = collected - (fast | full_regression)

    assert not fast & full_regression
    assert fast | full_regression == collected
    assert not unclassified
    assert full_regression
    assert fast >= REQUIRED_FAST_NODE_IDS


def test_explicit_fast_and_full_regression_markers_are_rejected(
    tmp_path: Path,
) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/unit/test_conflict.py": (
                "import pytest\n\n"
                "@pytest.mark.fast\n"
                "@pytest.mark.full_regression\n"
                "def test_conflicting_lanes():\n"
                "    pass\n"
            )
        },
    )

    result = _run_pytest(
        project,
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
    )
    output = _result_output(result)

    assert result.returncode != 0, output
    assert "fast" in output
    assert "full_regression" in output


def test_forbidden_explicit_lane_overrides_are_rejected(tmp_path: Path) -> None:
    cases = (
        (
            "required-fast-full",
            "tests/unit/infra/test_init_update.py",
            (
                "import pytest\n\n"
                "class TestInitUpdate:\n"
                "    @pytest.mark.full_regression\n"
                "    def test_checked_in_dogfooding_mirror_docs_match_provider_assets(self):\n"
                "        pass\n"
            ),
            "required-fast",
        ),
        (
            "heavy-fast",
            "tests/cli_runtime/test_override.py",
            ("import pytest\n\n@pytest.mark.fast\ndef test_heavy_override():\n    pass\n"),
            "heavy-prefix",
        ),
    )

    for case_name, relative_path, source, expected_reason in cases:
        project = _prepare_mini_project(
            tmp_path / case_name,
            {relative_path: source},
        )
        result = _run_pytest(
            project,
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
        )
        output = _result_output(result)

        assert result.returncode != 0, (case_name, output)
        assert expected_reason in output, (case_name, output)


def test_dynamic_lane_markers_are_visible_to_marker_selection(
    tmp_path: Path,
) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/unit/test_fast_sample.py": "def test_fast_sample():\n    pass\n",
            "tests/unit/test_explicit_full_sample.py": (
                "import pytest\n\n@pytest.mark.full_regression\ndef test_explicit_full_sample():\n    pass\n"
            ),
            "tests/cli_runtime/test_heavy_sample.py": ("def test_heavy_sample():\n    pass\n"),
        },
    )

    fast_result = _run_pytest(
        project,
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        "-m",
        "fast",
    )
    full_result = _run_pytest(
        project,
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        "-m",
        "full_regression",
    )

    assert fast_result.returncode == 0, _result_output(fast_result)
    assert full_result.returncode == 0, _result_output(full_result)
    assert _collected_node_ids(fast_result) == {"tests/unit/test_fast_sample.py::test_fast_sample"}
    assert _collected_node_ids(full_result) == {
        "tests/cli_runtime/test_heavy_sample.py::test_heavy_sample",
        "tests/unit/test_explicit_full_sample.py::test_explicit_full_sample",
    }


def test_full_regression_option_and_permission_contract(tmp_path: Path) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/unit/test_fast_behavior.py": (
                "from pathlib import Path\n\n"
                "def test_fast_behavior():\n"
                '    Path("fast-ran").write_text("yes", encoding="utf-8")\n'
            ),
            "tests/cli_runtime/test_heavy_behavior.py": (
                "from pathlib import Path\n\n"
                "def test_heavy_behavior():\n"
                '    Path("heavy-ran").write_text("yes", encoding="utf-8")\n'
            ),
        },
    )
    fast_sentinel = project / "fast-ran"
    heavy_sentinel = project / "heavy-ran"

    help_result = _run_pytest(project, "--help")
    assert help_result.returncode == 0, _result_output(help_result)
    assert POLICY_SKIP_HINT in help_result.stdout

    ordinary_result = _run_pytest(project, "-q", "-rs", "-p", "no:cacheprovider")
    ordinary_output = _result_output(ordinary_result)
    assert ordinary_result.returncode == 0, ordinary_output
    assert "1 passed" in ordinary_output
    assert "1 skipped" in ordinary_output
    assert POLICY_SKIP_HINT in ordinary_output
    assert fast_sentinel.is_file()
    assert not heavy_sentinel.exists()

    marker_only_result = _run_pytest(
        project,
        "-q",
        "-rs",
        "-p",
        "no:cacheprovider",
        "-m",
        "full_regression",
    )
    marker_only_output = _result_output(marker_only_result)
    assert marker_only_result.returncode == 0, marker_only_output
    assert "1 skipped" in marker_only_output
    assert POLICY_SKIP_HINT in marker_only_output
    assert not heavy_sentinel.exists()

    fast_sentinel.unlink()
    full_result = _run_pytest(
        project,
        "-q",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
    )
    full_output = _result_output(full_result)
    assert full_result.returncode == 0, full_output
    assert "2 passed" in full_output
    assert POLICY_SKIP_HINT not in full_output
    assert fast_sentinel.is_file()
    assert heavy_sentinel.is_file()

    fast_sentinel.unlink()
    heavy_sentinel.unlink()
    heavy_only_result = _run_pytest(
        project,
        "-q",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
        "-m",
        "full_regression",
    )
    heavy_only_output = _result_output(heavy_only_result)
    assert heavy_only_result.returncode == 0, heavy_only_output
    assert "1 passed" in heavy_only_output
    assert POLICY_SKIP_HINT not in heavy_only_output
    assert not fast_sentinel.exists()
    assert heavy_sentinel.is_file()


def test_ordinary_fast_failure_remains_nonzero_and_heavy_body_stays_zero(
    tmp_path: Path,
) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/unit/test_fast_failure.py": (
                'def test_fast_failure():\n    raise AssertionError("controlled fast failure")\n'
            ),
            "tests/cli_runtime/test_heavy_behavior.py": (
                "from pathlib import Path\n\n"
                "def test_heavy_behavior():\n"
                '    Path("heavy-ran").write_text("yes", encoding="utf-8")\n'
            ),
        },
    )

    result = _run_pytest(project, "-q", "-rs", "-p", "no:cacheprovider")
    output = _result_output(result)

    assert result.returncode == 1, output
    assert "controlled fast failure" in output
    assert "1 failed" in output
    assert "1 skipped" in output
    assert POLICY_SKIP_HINT in output
    assert not (project / "heavy-ran").exists()


def test_focused_and_marker_only_heavy_are_policy_skipped(tmp_path: Path) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/cli_runtime/test_heavy_behavior.py": (
                "from pathlib import Path\n\n"
                "def test_heavy_behavior():\n"
                '    Path("heavy-ran").write_text("yes", encoding="utf-8")\n'
            )
        },
    )
    heavy_node = "tests/cli_runtime/test_heavy_behavior.py::test_heavy_behavior"

    focused_result = _run_pytest(
        project,
        "-q",
        "-rs",
        "-p",
        "no:cacheprovider",
        heavy_node,
    )
    focused_output = _result_output(focused_result)
    assert focused_result.returncode == 0, focused_output
    assert "1 skipped" in focused_output
    assert POLICY_SKIP_HINT in focused_output
    assert not (project / "heavy-ran").exists()

    marker_only_result = _run_pytest(
        project,
        "-q",
        "-rs",
        "-p",
        "no:cacheprovider",
        "-m",
        "full_regression",
    )
    marker_only_output = _result_output(marker_only_result)
    assert marker_only_result.returncode == 0, marker_only_output
    assert "1 skipped" in marker_only_output
    assert POLICY_SKIP_HINT in marker_only_output
    assert not (project / "heavy-ran").exists()


def test_full_permission_preserves_legitimate_outcomes_and_heavy_failure(
    tmp_path: Path,
) -> None:
    project = _prepare_mini_project(
        tmp_path / "outcomes",
        {
            "tests/unit/test_fast_behavior.py": (
                "from pathlib import Path\n\n"
                "def test_fast_behavior():\n"
                '    Path("fast-ran").write_text("yes", encoding="utf-8")\n'
            ),
            "tests/cli_runtime/test_full_outcomes.py": (
                "from pathlib import Path\n"
                "import pytest\n\n"
                "def test_heavy_behavior():\n"
                '    Path("heavy-ran").write_text("yes", encoding="utf-8")\n\n'
                '@pytest.mark.skip(reason="legitimate skip sentinel")\n'
                "def test_legitimate_skip():\n"
                "    raise AssertionError\n\n"
                '@pytest.mark.skipif(True, reason="legitimate skipif sentinel")\n'
                "def test_legitimate_skipif():\n"
                "    raise AssertionError\n\n"
                '@pytest.mark.xfail(reason="legitimate xfail sentinel", strict=True)\n'
                "def test_legitimate_xfail():\n"
                "    raise AssertionError\n"
            ),
        },
    )
    fast_sentinel = project / "fast-ran"
    heavy_sentinel = project / "heavy-ran"

    root_full_result = _run_pytest(
        project,
        "-q",
        "-rsx",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
    )
    root_full_output = _result_output(root_full_result)
    assert root_full_result.returncode == 0, root_full_output
    assert "2 passed" in root_full_output
    assert "2 skipped" in root_full_output
    assert "1 xfailed" in root_full_output
    assert "legitimate skip sentinel" in root_full_output
    assert "legitimate skipif sentinel" in root_full_output
    assert "legitimate xfail sentinel" in root_full_output
    assert POLICY_SKIP_HINT not in root_full_output
    assert fast_sentinel.is_file()
    assert heavy_sentinel.is_file()

    fast_sentinel.unlink()
    heavy_sentinel.unlink()
    heavy_only_result = _run_pytest(
        project,
        "-q",
        "-rsx",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
        "-m",
        "full_regression",
    )
    heavy_only_output = _result_output(heavy_only_result)
    assert heavy_only_result.returncode == 0, heavy_only_output
    assert "1 passed" in heavy_only_output
    assert "2 skipped" in heavy_only_output
    assert "1 xfailed" in heavy_only_output
    assert POLICY_SKIP_HINT not in heavy_only_output
    assert not fast_sentinel.exists()
    assert heavy_sentinel.is_file()

    heavy_sentinel.unlink()
    focused_result = _run_pytest(
        project,
        "-q",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
        "tests/cli_runtime/test_full_outcomes.py::test_heavy_behavior",
    )
    focused_output = _result_output(focused_result)
    assert focused_result.returncode == 0, focused_output
    assert "1 passed" in focused_output
    assert POLICY_SKIP_HINT not in focused_output
    assert heavy_sentinel.is_file()

    failing_project = _prepare_mini_project(
        tmp_path / "failure",
        {
            "tests/cli_runtime/test_heavy_failure.py": (
                'def test_heavy_failure():\n    raise AssertionError("controlled heavy failure")\n'
            )
        },
    )
    failing_result = _run_pytest(
        failing_project,
        "-q",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
        "tests/cli_runtime/test_heavy_failure.py::test_heavy_failure",
    )
    failing_output = _result_output(failing_result)
    assert failing_result.returncode == 1, failing_output
    assert "controlled heavy failure" in failing_output
    assert "1 failed" in failing_output


def test_full_regression_guard_rejects_missing_ledger(tmp_path: Path) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {"tests/cli_runtime/test_sample.py": "def test_sample():\n    pass\n"},
        ledger_guard=True,
    )

    result = _run_pytest(project, "-q", "-p", "no:cacheprovider", "--run-full-regression")
    output = _result_output(result)

    assert result.returncode == 3, output
    assert "ledger_errors" in output
    assert "verified " not in output


def test_full_regression_guard_rejects_deleted_or_renamed_ledger_node(tmp_path: Path) -> None:
    project = _prepare_mini_project(
        tmp_path,
        {"tests/cli_runtime/test_renamed.py": "def test_renamed():\n    pass\n"},
        ledger_guard=True,
    )
    missing_node = "tests/cli_runtime/test_deleted.py::test_deleted"
    _write_full_regression_ledger(project, (missing_node,))

    result = _run_pytest(project, "-q", "-p", "no:cacheprovider", "--run-full-regression")
    output = _result_output(result)

    assert result.returncode == 3, output
    assert missing_node in output
    assert "verified " not in output


def test_full_regression_guard_rejects_incomplete_selected_suite(tmp_path: Path) -> None:
    selected = "tests/cli_runtime/test_selected.py::test_selected"
    omitted = "tests/cli_runtime/test_omitted.py::test_omitted"
    project = _prepare_mini_project(
        tmp_path,
        {
            "tests/cli_runtime/test_selected.py": "def test_selected():\n    pass\n",
            "tests/cli_runtime/test_omitted.py": "def test_omitted():\n    pass\n",
        },
        ledger_guard=True,
    )
    _write_full_regression_ledger(project, (selected, omitted))

    result = _run_pytest(
        project,
        "-q",
        "-p",
        "no:cacheprovider",
        "--run-full-regression",
        selected,
    )
    output = _result_output(result)

    assert result.returncode == 3, output
    assert omitted in output
    assert "verified " not in output
