import contextlib
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
CHATGPT_EXECUTABLE = RUNTIME_SCRIPTS_DIR / "spec-dock-chatgpt"
CORE_EXECUTABLE = RUNTIME_SCRIPTS_DIR / "spec-dock"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime import chatgpt_app  # noqa: E402
from spec_dock_runtime.application.contracts import UseCases  # noqa: E402
from spec_dock_runtime.application.issue_planning import (  # noqa: E402
    PlanningApplyRequest,
    PlanningCreateRequest,
    PlanningReviewRequest,
    PlanningReviseRequest,
)
from spec_dock_runtime.cli import bootstrap  # noqa: E402
from spec_dock_runtime.domain.issue_planning_contracts import PlanningCommandResult  # noqa: E402


def _run_help(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHATGPT_EXECUTABLE), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _unexpected(_request):
    raise AssertionError("unexpected use case call")


def _use_cases(planning_create):
    return UseCases(
        create_initiative=_unexpected,
        create_epic=_unexpected,
        create_issue=_unexpected,
        create_artifact_doc=_unexpected,
        import_initiative=_unexpected,
        import_epic=_unexpected,
        import_issue=_unexpected,
        set_active=_unexpected,
        show_active=_unexpected,
        clear_active=_unexpected,
        sync=_unexpected,
        check_deps=_unexpected,
        validate_tree=_unexpected,
        planning_create=planning_create,
    )


def test_top_level_and_group_help_expose_only_closed_command_family() -> None:
    top = _run_help("--help")
    assert top.returncode == 0
    assert "{planning,review}" in top.stdout
    assert "authoring" not in top.stdout

    planning = _run_help("planning", "--help")
    assert planning.returncode == 0
    assert "{create,revise,apply}" in planning.stdout
    assert "review planning" not in planning.stdout

    review = _run_help("review", "--help")
    assert review.returncode == 0
    assert "planning" in review.stdout
    assert "create" not in review.stdout


@pytest.mark.parametrize(
    ("args", "required_options"),
    [
        (("planning", "create", "--help"), ("--issue", "--output", "--context-manifest", "--format")),
        (("planning", "revise", "--help"), ("--candidate", "--request", "--output", "--format")),
        (
            ("review", "planning", "--help"),
            ("--issue", "--mode", "--candidate", "--reviewed-head", "--output", "--format"),
        ),
        (
            ("planning", "apply", "--help"),
            (
                "--issue",
                "--mode",
                "--review-result",
                "--human-decision",
                "--expected-head",
                "--output",
                "--candidate",
                "--logical-filename",
                "--zip-sha256",
                "--reviewed-head",
                "--format",
            ),
        ),
    ],
)
def test_leaf_help_freezes_required_and_conditional_options(args, required_options) -> None:
    result = _run_help(*args)
    assert result.returncode == 0
    for option in required_options:
        assert option in result.stdout
    for forbidden in ("--repo", "--repository", "--branch", "--target", "--prompt", "--backend"):
        assert forbidden not in result.stdout


def test_core_cli_help_does_not_include_chatgpt_leaf_commands() -> None:
    result = subprocess.run(
        [sys.executable, str(CORE_EXECUTABLE), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "planning create" not in result.stdout
    assert "review planning" not in result.stdout
    assert "spec-dock-chatgpt" not in result.stdout


def test_provider_executable_has_shebang_and_user_executable_bit() -> None:
    assert CHATGPT_EXECUTABLE.read_bytes().startswith(b"#!/usr/bin/env python3\n")
    assert CHATGPT_EXECUTABLE.stat().st_mode & 0o100


def test_chatgpt_app_full_tracer_uses_existing_dispatch_and_injected_use_case(monkeypatch) -> None:
    calls = []

    def planning_create(request):
        calls.append(request)
        return PlanningCommandResult(
            status="ok",
            reason="candidate_created",
            issue_id=request.issue_id,
        )

    monkeypatch.setattr(chatgpt_app, "_find_specdock_dir", lambda: Path("/repo/spec-dock"))
    monkeypatch.setattr(
        chatgpt_app,
        "build_runtime",
        lambda _specdock_dir, repo_root: SimpleNamespace(use_cases=_use_cases(planning_create)),
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = chatgpt_app.main([
            "planning",
            "create",
            "--issue",
            "iss-00003",
            "--output",
            "/tmp/out",
            "--format",
            "json",
        ])
    assert exit_code == 0
    assert len(calls) == 1
    assert '"status":"ok"' in stdout.getvalue()


def test_help_returns_before_repository_resolution(monkeypatch) -> None:
    monkeypatch.setattr(
        chatgpt_app,
        "_find_specdock_dir",
        lambda: (_ for _ in ()).throw(AssertionError("repo resolution must not run")),
    )
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        assert chatgpt_app.main(["--help"]) == 0


def test_issue_planning_revise_help_states_review_sibling_contract() -> None:
    result = _run_help("planning", "revise", "--help")
    assert result.returncode == 0
    assert "planning-review-result.json" in result.stdout
    assert "same directory" in result.stdout.lower()


@pytest.mark.parametrize(
    "args",
    [
        (
            "review",
            "planning",
            "--issue",
            "iss-00003",
            "--mode",
            "git-bound",
            "--reviewed-head",
            "a" * 40,
            "--output",
            "/tmp/out",
        ),
        (
            "planning",
            "apply",
            "--issue",
            "iss-00003",
            "--mode",
            "git-bound",
            "--review-result",
            "/tmp/review.json",
            "--human-decision",
            "/tmp/decision.json",
            "--expected-head",
            "a" * 40,
            "--reviewed-head",
            "a" * 40,
            "--output",
            "/tmp/out",
        ),
    ],
)
def test_git_bound_review_and_apply_require_candidate_argument(
    args: tuple[str, ...],
) -> None:
    result = _run_help(*args)

    assert result.returncode == 1
    assert "reason: operation_candidate_required" in result.stdout


def test_build_runtime_configures_all_issue_planning_use_cases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    specdock_dir = tmp_path / "spec-dock"
    specdock_dir.mkdir()
    calls: list[str] = []
    planning_dependencies: list[object] = []

    def configured(name: str):
        def operation(**kwargs):
            calls.append(name)
            planning_dependencies.append(kwargs["dependencies"])
            request = kwargs["request"]
            issue_id = getattr(request, "issue_id", "iss-00003")
            return PlanningCommandResult(
                status="blocked",
                reason=f"{name}_reached",
                issue_id=issue_id,
            )

        return operation

    monkeypatch.setattr(bootstrap._NodeReader, "load_node_records", lambda self: ())
    monkeypatch.setattr(bootstrap, "application_run_issue_planning_create", configured("create"), raising=False)
    monkeypatch.setattr(bootstrap, "application_run_issue_planning_review", configured("review"), raising=False)
    monkeypatch.setattr(bootstrap, "application_run_issue_planning_revise", configured("revise"), raising=False)
    monkeypatch.setattr(bootstrap, "application_run_issue_planning_apply", configured("apply"), raising=False)

    use_cases = bootstrap.build_runtime(specdock_dir, repo_root=tmp_path).use_cases
    use_cases.planning_create(PlanningCreateRequest("iss-00003", tmp_path))
    use_cases.planning_review(
        PlanningReviewRequest(
            "iss-00003",
            "git-bound",
            tmp_path,
            candidate_path=tmp_path / "candidate.zip",
            reviewed_head="a" * 40,
        )
    )
    use_cases.planning_revise(PlanningReviseRequest(tmp_path / "candidate.zip", tmp_path / "request.json", tmp_path))
    use_cases.planning_apply(
        PlanningApplyRequest(
            issue_id="iss-00003",
            mode="git-bound",
            review_result_path=tmp_path / "review.json",
            human_decision_path=tmp_path / "decision.json",
            expected_head="a" * 40,
            output_dir=tmp_path,
            candidate_path=tmp_path / "candidate.zip",
            reviewed_head="a" * 40,
        )
    )

    assert calls == ["create", "review", "revise", "apply"]
    assert planning_dependencies[0] is not None
    assert all(dependencies is planning_dependencies[0] for dependencies in planning_dependencies)
