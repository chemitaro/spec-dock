import os
from pathlib import Path
import shlex
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


def test_complete_frame_with_transcript_marker_mentions_is_accepted() -> None:
    classify = issue_planning_chatgpt.classify_transport_frame
    payload = (
        "# Raw transcript vocabulary\n\n"
        "The term raw transcript names an evidence class.\n"
        "- ChatGPT transcript、credential、private absolute pathを保存しない。\n"
        "The runtime must not persist a browser transcript."
    ).encode()
    result = classify(
        b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
        + b"a" * 40
        + b">>>\n"
        + payload
        + b"\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n",
        role="planner",
        source_head="a" * 40,
    )

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.transient_payload == payload
    assert payload not in repr(result).encode()
    assert payload.decode() not in str(result.to_dict())


def test_complete_frame_with_structured_transcript_is_rejected_without_leakage() -> None:
    classify = issue_planning_chatgpt.classify_transport_frame
    payload = "# Oracle Browser Transcript\n## Prompt\nprivate requirement body\n## Answer\nprivate response body"
    result = classify(
        (
            "<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + "a" * 40
            + f">>>\n{payload}\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
        ).encode(),
        role="planner",
        source_head="a" * 40,
    )

    assert (result.status, result.reason) == ("rejected", "sensitive_input_rejected")
    assert result.transient_payload is None
    assert "private requirement body" not in repr(result)
    assert "private response body" not in str(result.to_dict())


def test_fixed_adapter_classifies_only_ephemeral_final_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    final_frame = (
        b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
        + b"a" * 40
        + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
    )
    diagnostic_prefix = b"d" * 3_737
    diagnostic_suffix = b"f" * 78
    stderr_sentinel = b"private diagnostic sentinel"
    captured_output_path: list[Path] = []

    def fake_invoke(request, *, env):
        output_path = _output_path_from_request(request)
        captured_output_path.append(output_path)
        assert not output_path.exists()
        output_path.write_bytes(final_frame)
        return (
            type(
                "Result",
                (),
                {"blockers": (), "exit_code": 0, "status": "pass"},
            )(),
            BackendStreamCapture(
                stdout=diagnostic_prefix + final_frame + diagnostic_suffix,
                stderr=stderr_sentinel,
            ),
        )

    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", fake_invoke)
    result = _invoke_fixed_adapter(tmp_path)

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.transient_payload == b"body"
    assert result.response_bytes == len(final_frame)
    assert captured_output_path
    assert not captured_output_path[0].exists()
    serialized = str(result.to_dict())
    assert diagnostic_prefix.decode() not in repr(result)
    assert diagnostic_suffix.decode() not in serialized
    assert stderr_sentinel.decode() not in serialized
    assert str(captured_output_path[0]) not in serialized


def test_fixed_adapter_does_not_fall_back_to_valid_stdout(
    monkeypatch,
    tmp_path: Path,
) -> None:
    valid_frame = (
        b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
        + b"a" * 40
        + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
    )

    def fake_invoke(request, *, env):
        _output_path_from_request(request)
        return (
            type(
                "Result",
                (),
                {"blockers": (), "exit_code": 0, "status": "pass"},
            )(),
            BackendStreamCapture(stdout=valid_frame),
        )

    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", fake_invoke)
    result = _invoke_fixed_adapter(tmp_path)

    assert (result.status, result.reason) == ("blocked", "backend_output_missing")
    assert result.transient_payload is None


@pytest.mark.parametrize(
    ("final_output", "expected"),
    [
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
            b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\nbody\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\noutside",
            ("rejected", "backend_response_malformed"),
        ),
        (
            b"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\nbody\n<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=planner source_head="
            + b"a" * 40
            + b">>>\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>",
            ("rejected", "backend_response_malformed"),
        ),
        (b"\xff", ("rejected", "backend_response_malformed")),
    ],
)
def test_fixed_adapter_retains_strict_frame_validation_for_final_output(
    monkeypatch,
    tmp_path: Path,
    final_output: bytes,
    expected: tuple[str, str],
) -> None:
    def fake_invoke(request, *, env):
        _output_path_from_request(request).write_bytes(final_output)
        return (
            type(
                "Result",
                (),
                {"blockers": (), "exit_code": 0, "status": "pass"},
            )(),
            BackendStreamCapture(stdout=b"arbitrary diagnostic output"),
        )

    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", fake_invoke)
    result = _invoke_fixed_adapter(tmp_path)

    assert (result.status, result.reason) == expected
    assert result.transient_payload is None


@pytest.mark.parametrize("output_kind", ["absent", "empty", "directory", "symlink", "fifo", "unreadable"])
def test_fixed_adapter_rejects_missing_or_unsafe_final_output(
    monkeypatch,
    tmp_path: Path,
    output_kind: str,
) -> None:
    def fake_invoke(request, *, env):
        output_path = _output_path_from_request(request)
        if output_kind == "empty":
            output_path.write_bytes(b"")
        elif output_kind == "directory":
            output_path.mkdir()
        elif output_kind == "symlink":
            target = output_path.with_name("target.txt")
            target.write_text("private response", encoding="utf-8")
            output_path.symlink_to(target)
        elif output_kind == "fifo":
            os.mkfifo(output_path)
        elif output_kind == "unreadable":
            output_path.write_text("private response", encoding="utf-8")
            output_path.chmod(0)
        return (
            type(
                "Result",
                (),
                {"blockers": (), "exit_code": 0, "status": "pass"},
            )(),
            BackendStreamCapture(stdout=b"valid-looking diagnostic"),
        )

    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", fake_invoke)
    result = _invoke_fixed_adapter(tmp_path)

    assert (result.status, result.reason) == ("blocked", "backend_output_missing")
    assert result.transient_payload is None


def test_fixed_adapter_rejects_preexisting_final_output_before_backend(
    monkeypatch,
    tmp_path: Path,
) -> None:
    private_root = tmp_path / "private-root"
    private_root.mkdir()
    (private_root / "final-assistant-message.txt").write_text(
        "unexpected preexisting output",
        encoding="utf-8",
    )

    class FixedTemporaryDirectory:
        def __init__(self, *, prefix: str) -> None:
            assert prefix == "specdock-issue-planning-"

        def __enter__(self) -> str:
            return str(private_root)

        def __exit__(self, *args) -> None:
            return None

    def unexpected_invoke(request, *, env):
        pytest.fail("backend must not run when the private output path already exists")

    monkeypatch.setattr(issue_planning_chatgpt, "TemporaryDirectory", FixedTemporaryDirectory)
    monkeypatch.setattr(issue_planning_chatgpt, "invoke_backend_with_capture", unexpected_invoke)
    result = _invoke_fixed_adapter(tmp_path)

    assert (result.status, result.reason) == ("rejected", "planning_context_rejected")
    assert result.transient_payload is None


@pytest.mark.parametrize(
    ("blockers", "exit_code", "stdout", "write_output", "expected"),
    [
        (
            ("backend_command_not_found",),
            None,
            b"",
            True,
            ("blocked", "backend_unavailable"),
        ),
        (
            ("backend_timeout",),
            None,
            b"partial secret",
            True,
            ("blocked", "backend_timeout"),
        ),
        (("backend_exit_code:7",), 7, b"", True, ("blocked", "backend_nonzero")),
        ((), 0, b"", False, ("blocked", "backend_output_missing")),
    ],
)
def test_fixed_adapter_classifies_backend_failures_without_stream_leakage(
    monkeypatch,
    tmp_path: Path,
    blockers: tuple[str, ...],
    exit_code: int | None,
    stdout: bytes,
    write_output: bool,
    expected: tuple[str, str],
) -> None:
    captured_request: list[object] = []
    captured_output_path: list[Path] = []
    file_sentinel = "private final output sentinel"

    def fake_invoke(request, *, env):
        captured_request.append(request)
        output_path = _output_path_from_request(request)
        captured_output_path.append(output_path)
        if write_output:
            output_path.write_text(file_sentinel, encoding="utf-8")
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
    assert shlex.split(request.backend_command)[0] == issue_planning_chatgpt._FIXED_CHATGPT_USE
    assert request.working_dir == tmp_path
    assert captured_output_path
    assert not captured_output_path[0].exists()
    assert "private diagnostic" not in repr(result)
    assert "partial secret" not in repr(result)
    assert file_sentinel not in repr(result)
    assert str(captured_output_path[0]) not in str(result.to_dict())


def _output_path_from_request(request) -> Path:
    argv = shlex.split(request.backend_command)
    assert argv[0] == issue_planning_chatgpt._FIXED_CHATGPT_USE
    assert argv.count("--write-output") == 1
    option_index = argv.index("--write-output")
    assert option_index + 1 < len(argv)
    output_path = Path(argv[option_index + 1])
    assert output_path.is_absolute()
    assert output_path.parent == request.prompt_pack.parent
    return output_path


def _invoke_fixed_adapter(tmp_path: Path):
    return issue_planning_chatgpt.invoke_issue_planning_chatgpt(
        repo_root=tmp_path,
        role="planner",
        source_evidence=_source_evidence(),
        synthesized=SynthesizedPlanningPrompt(
            role="planner",
            prompt="fixed prompt",
            attachments=(("source.md", "safe context"),),
        ),
    )


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
