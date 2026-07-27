import contextlib
import io
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.contracts import UseCases  # noqa: E402
from spec_dock_runtime.application.issue_planning import (  # noqa: E402
    PlanningApplyRequest,
    PlanningCreateRequest,
    PlanningReviewRequest,
    PlanningReviseRequest,
)
from spec_dock_runtime.cli.chatgpt_parser import build_parser  # noqa: E402
from spec_dock_runtime.cli.chatgpt_registry import build_registry  # noqa: E402
from spec_dock_runtime.cli.dispatch import dispatch  # noqa: E402
from spec_dock_runtime.domain.issue_planning_contracts import PlanningCommandResult  # noqa: E402


def _unexpected(_request):
    raise AssertionError("unexpected use case call")


def _use_cases(**planning):
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
        planning_create=planning.get("planning_create", _unexpected),
        planning_revise=planning.get("planning_revise", _unexpected),
        planning_review=planning.get("planning_review", _unexpected),
        planning_apply=planning.get("planning_apply", _unexpected),
    )


@pytest.mark.parametrize(
    ("argv", "use_case_name", "request_type", "reason"),
    [
        (
            ["planning", "create", "--issue", "iss-00003", "--output", "/tmp/out"],
            "planning_create",
            PlanningCreateRequest,
            "candidate_created",
        ),
        (
            [
                "planning",
                "revise",
                "--candidate",
                "/tmp/candidate.zip",
                "--request",
                "/tmp/request.json",
                "--output",
                "/tmp/out",
            ],
            "planning_revise",
            PlanningReviseRequest,
            "candidate_revised",
        ),
        (
            [
                "review",
                "planning",
                "--issue",
                "iss-00003",
                "--mode",
                "archive-candidate",
                "--candidate",
                "/tmp/candidate.zip",
                "--output",
                "/tmp/out",
            ],
            "planning_review",
            PlanningReviewRequest,
            "review_completed",
        ),
        (
            [
                "planning",
                "apply",
                "--issue",
                "iss-00003",
                "--mode",
                "archive-candidate",
                "--review-result",
                "/tmp/review.json",
                "--human-decision",
                "/tmp/decision.json",
                "--expected-head",
                "a" * 40,
                "--output",
                "/tmp/out",
                "--candidate",
                "/tmp/candidate.zip",
                "--logical-filename",
                "candidate.zip",
                "--zip-sha256",
                "b" * 64,
            ],
            "planning_apply",
            PlanningApplyRequest,
            "adoption_published",
        ),
    ],
)
def test_each_leaf_dispatches_exactly_one_typed_request(argv, use_case_name, request_type, reason) -> None:
    calls = []

    def fake(request):
        calls.append(request)
        return PlanningCommandResult(
            status="ready" if reason == "adoption_published" else "ok",
            reason=reason,
            issue_id="iss-00003",
        )

    registry = build_registry()
    namespace = build_parser(registry).parse_args(argv)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = dispatch(namespace, registry, _use_cases(**{use_case_name: fake}))
    assert exit_code == 0
    assert len(calls) == 1
    assert isinstance(calls[0], request_type)


@pytest.mark.parametrize(
    "argv",
    [
        [
            "review",
            "planning",
            "--issue",
            "iss-00003",
            "--mode",
            "archive-candidate",
            "--candidate",
            "/tmp/candidate.zip",
            "--reviewed-head",
            "a" * 40,
            "--output",
            "/tmp/out",
        ],
        [
            "review",
            "planning",
            "--issue",
            "iss-00003",
            "--mode",
            "git-bound",
            "--candidate",
            "/tmp/candidate.zip",
            "--reviewed-head",
            "a" * 40,
            "--output",
            "/tmp/out",
        ],
        [
            "planning",
            "apply",
            "--issue",
            "iss-00003",
            "--mode",
            "archive-candidate",
            "--review-result",
            "/tmp/review.json",
            "--human-decision",
            "/tmp/decision.json",
            "--expected-head",
            "a" * 40,
            "--output",
            "/tmp/out",
            "--candidate",
            "/tmp/candidate.zip",
            "--logical-filename",
            "candidate.zip",
        ],
        [
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
            "--output",
            "/tmp/out",
            "--reviewed-head",
            "a" * 40,
            "--candidate",
            "/tmp/candidate.zip",
        ],
    ],
)
def test_cross_mode_or_partial_identity_options_fail_before_use_case(argv) -> None:
    calls = []

    def spy(request):
        calls.append(request)
        raise AssertionError("must not be called")

    registry = build_registry()
    namespace = build_parser(registry).parse_args(argv)
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        exit_code = dispatch(
            namespace,
            registry,
            _use_cases(planning_review=spy, planning_apply=spy),
        )
    assert exit_code == 1
    assert calls == []
    assert "error:" in stderr.getvalue()


def test_text_and_json_dispatch_share_result_semantics() -> None:
    result = PlanningCommandResult(
        status="blocked",
        reason="missing_evidence",
        issue_id="iss-00003",
    )
    registry = build_registry()
    outputs = []
    for output_format in ("text", "json"):
        namespace = build_parser(registry).parse_args(
            [
                "planning",
                "create",
                "--issue",
                "iss-00003",
                "--output",
                "/tmp/out",
                "--format",
                output_format,
            ]
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            assert dispatch(
                namespace,
                registry,
                _use_cases(planning_create=lambda _request: result),
            ) == 1
        outputs.append(stdout.getvalue())
    assert "status: blocked" in outputs[0]
    assert '"status":"blocked"' in outputs[1]
    assert "missing_evidence" in outputs[0] and "missing_evidence" in outputs[1]
