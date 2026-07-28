from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.authoring_pack.backend_invoke import validate_prompt_pack  # noqa: E402
from spec_dock_runtime.application.issue_planning_prompt import SynthesizedPlanningPrompt  # noqa: E402
from spec_dock_runtime.domain.authoring_pack.backend_invoke_contract import (  # noqa: E402
    BackendStreamCapture,
)
from spec_dock_runtime.domain.issue_planning_contracts import PlanningSourceEvidence  # noqa: E402
from spec_dock_runtime.infra import issue_planning_chatgpt  # noqa: E402


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        (b"", ("blocked", "backend_output_missing")),
        (
            b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\nbody",
            ("blocked", "backend_response_partial"),
        ),
        (
            b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\n\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n",
            ("blocked", "backend_response_partial"),
        ),
        (
            b"outside\n<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n",
            ("rejected", "backend_response_malformed"),
        ),
        (
            b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=reviewer source_head="
            + b"a" * 40
            + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n",
            ("rejected", "backend_response_malformed"),
        ),
    ],
)
def test_classify_transport_frame_negative_cases(stdout: bytes, expected: tuple[str, str]) -> None:
    classify = issue_planning_chatgpt.classify_transport_frame
    result = classify(stdout, role="planner", source_head="a" * 40)
    assert (result.status, result.reason) == expected
    assert result.transient_payload is None


def test_classify_transport_frame_accepts_exact_frame_without_serializing_payload() -> None:
    classify = issue_planning_chatgpt.classify_transport_frame
    result = classify(
        b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
        + b"a" * 40
        + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n",
        role="planner",
        source_head="a" * 40,
    )
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.transient_payload == b"body"
    assert b"body" not in repr(result).encode()
    assert "body" not in str(result.to_dict())


def test_complete_frame_with_secret_is_rejected_without_leakage() -> None:
    classify = issue_planning_chatgpt.classify_transport_frame
    secret = "token=abc123secret"
    result = classify(
        (
            "<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + "a" * 40
            + f">>>\n{secret}\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
        ).encode(),
        role="planner",
        source_head="a" * 40,
    )
    assert (result.status, result.reason) == ("rejected", "sensitive_input_rejected")
    assert secret not in repr(result)
    assert secret not in str(result.to_dict())


@pytest.mark.parametrize(
    ("blockers", "exit_code", "stdout", "expected"),
    [
        (("backend_command_not_found",), None, b"", ("blocked", "backend_unavailable")),
        (("backend_timeout",), None, b"partial secret", ("blocked", "backend_timeout")),
        (("backend_exit_code:7",), 7, b"", ("blocked", "backend_nonzero")),
        ((), 0, b"", ("blocked", "backend_output_missing")),
    ],
)
def test_fixed_adapter_classifies_backend_failures_without_stream_leakage(
    monkeypatch,
    tmp_path: Path,
    blockers: tuple[str, ...],
    exit_code: int | None,
    stdout: bytes,
    expected: tuple[str, str],
) -> None:
    captured_request: list[object] = []

    def fake_invoke(request, *, env):
        captured_request.append(request)
        assert validate_prompt_pack(request.prompt_pack).status == "pass"
        status = "pass" if not blockers else "blocked"
        return (
            type(
                "Result",
                (),
                {"blockers": blockers, "exit_code": exit_code, "status": status},
            )(),
            BackendStreamCapture(stdout=stdout, stderr=b"private diagnostic"),
        )

    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", fake_invoke)
    result = issue_planning_chatgpt.invoke_issue_planning_chatgpt(
        repo_root=tmp_path,
        role="planner",
        source_evidence=_source_evidence(),
        synthesized=SynthesizedPlanningPrompt(
            role="planner",
            prompt="fixed prompt",
            attachments=(("source.md", "$(touch sentinel); token words are inert data"),),
        ),
    )
    assert (result.status, result.reason) == expected
    assert len(captured_request) == 1
    request = captured_request[0]
    assert request.backend_command == issue_planning_chatgpt._FIXED_CHATGPT_USE
    assert request.working_dir == tmp_path
    assert "private diagnostic" not in repr(result)
    assert "partial secret" not in repr(result)


def _source_evidence() -> PlanningSourceEvidence:
    return PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash="b" * 64,
        snapshot_id="c" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )


def test_prompt_pack_preserves_exact_binary_attachment_bytes(tmp_path: Path) -> None:
    prompt_module = __import__(
        "spec_dock_runtime.application.issue_planning_prompt",
        fromlist=["PlanningPromptAttachment"],
    )
    candidate = b"PK\x03\x04\x00\xffexact"
    synthesized = SynthesizedPlanningPrompt(
        role="reviewer",
        prompt="fixed prompt",
        attachments=(),
        exact_attachments=(
            prompt_module.PlanningPromptAttachment(
                name="target-candidate.zip",
                classification="review-target",
                source_label="candidate.zip",
                content=candidate,
            ),
        ),
    )
    pack = tmp_path / "pack"
    issue_planning_chatgpt._write_transport_pack(pack, synthesized, _source_evidence())
    assert (pack / "target-candidate.zip").read_bytes() == candidate
    assert validate_prompt_pack(pack).status == "pass"
