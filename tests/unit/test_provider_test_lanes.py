from collections.abc import Mapping
from pathlib import Path
import subprocess
import sys

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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def _prepare_mini_project(tmp_path: Path, test_files: Mapping[str, str]) -> Path:
    classifier_path = _repo_root() / "tests" / "conftest.py"
    assert classifier_path.is_file(), f"S01 classifier is missing: {classifier_path}"

    tests_root = tmp_path / "tests"
    tests_root.mkdir(parents=True)
    (tests_root / "conftest.py").write_text(
        classifier_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
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
