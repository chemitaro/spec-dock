from collections.abc import Mapping
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

from tests.conftest import _normalize_failure_message

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

    assert _normalize_failure_message(macos_runtime_error, repository) == _normalize_failure_message(
        linux_runtime_error,
        repository,
    )
    assert _normalize_failure_message(compact_assertion, repository) == _normalize_failure_message(
        expanded_assertion,
        repository,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_full_regression_verifier():
    path = _repo_root() / FULL_REGRESSION_VERIFIER
    spec = importlib.util.spec_from_file_location("issue_368_full_regression_verifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_regression_total_slo_evidence_includes_collection_and_shards(monkeypatch) -> None:
    verifier = _load_full_regression_verifier()
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 610.0)

    evidence = verifier._timing_evidence(
        overall_started=0.0,
        collection_seconds=110.0,
        shard_elapsed_seconds=500.0,
        slo_seconds=600.0,
    )

    assert evidence == {
        "collection_seconds": 110.0,
        "shard_elapsed_seconds": 500.0,
        "total_elapsed_seconds": 610.0,
        "slo_seconds": 600.0,
        "slo_status": "fail",
    }


def test_full_regression_phase_budget_cannot_extend_the_total_deadline(monkeypatch) -> None:
    verifier = _load_full_regression_verifier()
    now = 110.0
    monkeypatch.setattr(verifier.time, "monotonic", lambda: now)

    assert (
        abs(
            verifier._remaining_phase_budget(
                overall_started=0.0,
                max_total_seconds=600.0,
                phase_timeout_seconds=600.0,
            )
            - 490.0
        )
        < 1e-9
    )

    now = 610.0
    assert (
        abs(
            verifier._remaining_phase_budget(
                overall_started=0.0,
                max_total_seconds=600.0,
                phase_timeout_seconds=600.0,
            )
        )
        < 1e-9
    )


def test_full_regression_stream_timeout_survives_unterminated_output(tmp_path: Path) -> None:
    verifier = _load_full_regression_verifier()
    output_path = tmp_path / "unterminated.log"
    started = time.monotonic()

    code, timed_out = verifier._run_streamed(
        [
            sys.executable,
            "-c",
            "import sys, time; sys.stdout.write('unterminated'); sys.stdout.flush(); time.sleep(2)",
        ],
        cwd=tmp_path,
        output_path=output_path,
        timeout_seconds=0.1,
        stream=False,
    )

    assert timed_out is True
    assert code != 0
    assert time.monotonic() - started < 1.5
    assert "unterminated" in output_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("child_body", "expected_output"),
    [
        (
            "import sys, time\n"
            "while True:\n"
            "    sys.stdout.write('continuous\\n')\n"
            "    sys.stdout.flush()\n"
            "    time.sleep(0.001)\n",
            "continuous",
        ),
        (
            "import sys, time\nsys.stdout.write('intermittent\\n')\nsys.stdout.flush()\ntime.sleep(5)\n",
            "intermittent",
        ),
        ("import time\ntime.sleep(5)\n", None),
    ],
    ids=("continuous-write", "intermittent-write", "silent"),
)
def test_full_regression_leader_exit_cannot_leave_stdout_descendant(
    tmp_path: Path,
    child_body: str,
    expected_output: str | None,
) -> None:
    verifier = _load_full_regression_verifier()
    child = tmp_path / "child.py"
    parent = tmp_path / "parent.py"
    output_path = tmp_path / "descendant.log"
    child.write_text(child_body, encoding="utf-8")
    parent.write_text(
        "import subprocess, sys, time\nsubprocess.Popen([sys.executable, 'child.py'])\ntime.sleep(0.1)\n",
        encoding="utf-8",
    )
    started = time.monotonic()

    code, timed_out = verifier._run_streamed(
        [sys.executable, str(parent)],
        cwd=tmp_path,
        output_path=output_path,
        timeout_seconds=0.5,
        stream=False,
    )

    assert timed_out is True
    assert code == 124
    assert time.monotonic() - started < 1.5
    if expected_output is not None:
        assert expected_output in output_path.read_text(encoding="utf-8")


def test_full_regression_final_result_rechecks_deadline_after_postprocessing(monkeypatch) -> None:
    verifier = _load_full_regression_verifier()
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 600.001)

    result = verifier._finalize_result(
        {"status": "verified", "candidate_sha": "a" * 40},
        overall_started=0.0,
        collection_seconds=0.25,
        shard_elapsed_seconds=599.0,
        slo_seconds=600.0,
    )

    assert result["status"] == "total-timeout"
    assert result["underlying_status"] == "verified"
    assert result["slo_status"] == "fail"
    assert abs(result["total_elapsed_seconds"] - 600.001) < 1e-9


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


def test_full_regression_workflow_enforces_the_total_slo() -> None:
    workflow = (_repo_root() / ".github/workflows/provider-full-regression.yml").read_text(encoding="utf-8")

    assert "--timeout-seconds 600 --max-total-seconds 600 --shards 4" in workflow
    assert "timeout-minutes: 12" in workflow


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
    ledger = (
        project
        / "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics"
        / "epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues"
        / "iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-ledger.json"
    )
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        json.dumps({
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
            ]
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
