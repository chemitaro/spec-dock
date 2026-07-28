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
