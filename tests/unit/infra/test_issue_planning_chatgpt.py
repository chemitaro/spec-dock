import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.issue_planning_prompt import (  # noqa: E402
    PlanningOutputExpectation,
    PlanningPromptAttachment,
    SynthesizedPlanningPrompt,
)
from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    OracleAuthoringZipSnapshot,
    PlanningInvocationResult,
    PlanningSourceEvidence,
)
from spec_dock_runtime.infra import issue_planning_chatgpt  # noqa: E402
from spec_dock_runtime.infra.contracts import StoredMetaRecord  # noqa: E402


def test_path_oracle_direct_argv_environment_and_planner_snapshot(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path, symlink=True)
    calls: list[tuple[list[str], dict[str, str], bool]] = []

    def fake_run(argv, **kwargs):
        calls.append((list(argv), dict(kwargs["env"]), kwargs["shell"]))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        assert argv.count("--prompt") == 1
        assert argv[argv.index("--prompt") + 1] == 'literal $(touch nope); "quoted"'
        assert "--write-output" not in argv
        _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    original_result_type = issue_planning_chatgpt.PlanningInvocationResult
    constructor_calls: list[dict[str, object]] = []

    def result_spy(**kwargs):
        constructor_calls.append(dict(kwargs))
        return original_result_type(**kwargs)

    monkeypatch.setattr(issue_planning_chatgpt, "PlanningInvocationResult", result_spy)
    result = _invoke(tmp_path, role="planner", prompt='literal $(touch nope); "quoted"')

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.authoring_zip is not None
    assert result.review_json is None
    submit_calls = [call for call in calls if "--prompt" in call[0]]
    assert len(submit_calls) == 1
    argv, child_env, shell = submit_calls[0]
    assert Path(argv[0]) == executable.resolve()
    assert shell is False
    assert child_env["PATH"] == os.environ["PATH"]
    assert child_env["LANG"] == "ja_JP.UTF-8"
    assert "OPENAI_API_KEY" not in child_env
    assert "AZURE_OPENAI_API_KEY" not in child_env
    assert "SPECDOCK_CHATGPT_COMMAND" not in child_env
    serialized = str(result.to_dict())
    assert "sessions" not in serialized
    assert "oracle-home" not in serialized
    assert result.authoring_zip.zip_bytes not in repr(result).encode()
    assert constructor_calls
    assert all("transient_payload" not in kwargs for kwargs in constructor_calls)


def test_reviewer_returns_typed_closed_json_without_private_transcript(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_reviewer_session(kwargs["env"], argv)
        return _completed(argv, stdout=b"private oracle diagnostic")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, role="reviewer")

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.review_json is not None
    assert result.review_json.json_bytes == b'{"verdict":"pass"}'
    assert result.authoring_zip is None
    assert "private prompt" not in repr(result)
    assert "private oracle diagnostic" not in str(result.to_dict())


def test_missing_or_invalid_oracle_starts_no_process(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(issue_planning_chatgpt.shutil, "which", lambda _name: None)
    monkeypatch.setattr(
        issue_planning_chatgpt.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Oracle process must not start"),
    )
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")


def test_role_expectation_mismatch_starts_no_process(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        issue_planning_chatgpt.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("invalid contract must not start Oracle"),
    )
    result = issue_planning_chatgpt.invoke_issue_planning_chatgpt(
        repo_root=tmp_path,
        role="reviewer",
        source_evidence=_source_evidence(),
        synthesized=SynthesizedPlanningPrompt(
            role="reviewer",
            prompt="fixed",
            attachments=(),
            output_expectation=_authoring_expectation(),
        ),
    )
    assert (result.status, result.reason) == (
        "rejected",
        "planning_context_rejected",
    )


@pytest.mark.parametrize("kind", ["directory", "fifo", "broken-link", "loop", "non-executable"])
def test_invalid_path_entries_are_unavailable(
    monkeypatch,
    tmp_path: Path,
    kind: str,
) -> None:
    candidate = tmp_path / "oracle"
    if kind == "directory":
        candidate.mkdir()
    elif kind == "fifo":
        os.mkfifo(candidate)
    elif kind == "broken-link":
        candidate.symlink_to(tmp_path / "missing")
    elif kind == "loop":
        candidate.symlink_to(candidate)
    else:
        candidate.write_text("#!/bin/sh\n", encoding="utf-8")
        candidate.chmod(0o600)
    monkeypatch.setattr(issue_planning_chatgpt.shutil, "which", lambda _name: str(candidate))
    monkeypatch.setattr(
        issue_planning_chatgpt.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("invalid Oracle must not start"),
    )
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")


@pytest.mark.parametrize("preflight_failure", ["version", "root-help", "session-help"])
def test_unsupported_version_or_capability_submits_no_prompt(
    monkeypatch,
    tmp_path: Path,
    preflight_failure: str,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            version = b"0.16.2\n" if preflight_failure == "version" else b"0.16.1\n"
            return _completed(argv, stdout=version)
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=b"missing flags" if preflight_failure == "root-help" else _root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(
                argv,
                stdout=b"missing flags" if preflight_failure == "session-help" else _session_help(),
            )
        pytest.fail("prompt must not be submitted")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("blocked", "oracle_capability_unsupported")
    assert not any("--prompt" in argv for argv in calls)


def test_executable_identity_change_before_submit_starts_no_prompt(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    identities = iter([(1, 2, 3, 4), (1, 2, 3, 5)])

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        pytest.fail("changed executable must not receive a prompt")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt, "_executable_identity", lambda _path: next(identities))
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")
    assert not any("--prompt" in argv for argv in calls)


def test_timeout_recovers_same_session_without_duplicate_submit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            _write_metadata_only(kwargs["env"], argv, status="running")
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        assert argv[1] == "session"
        assert "--harvest" in argv and "--no-recover" in argv
        _write_planner_session(kwargs["env"], argv, session_id=argv[2])
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, timeout_seconds=0.1)
    assert result.status == "pass"
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1


def test_timeout_with_unknown_terminal_state_requires_human_recovery(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            _write_metadata_only(kwargs["env"], argv, status="running")
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        return _completed(argv, returncode=1, stderr=b"token=private")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, timeout_seconds=0.1)
    assert (result.status, result.reason) == (
        "blocked",
        "oracle_session_recovery_required",
    )
    assert sum("--prompt" in argv for argv in calls) == 1
    assert "private" not in repr(result)


def test_recovery_revalidates_path_identity_before_harvest(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    identities = iter([(1, 2, 3, 4), (1, 2, 3, 4), (1, 2, 3, 5)])

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            _write_metadata_only(kwargs["env"], argv, status="running")
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        pytest.fail("changed Oracle identity must prevent harvest")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt, "_executable_identity", lambda _path: next(identities))
    result = _invoke(tmp_path, timeout_seconds=0.1)

    assert (result.status, result.reason) == (
        "blocked",
        "oracle_session_recovery_required",
    )
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 0
    assert result.authoring_zip is None
    assert result.review_json is None


@pytest.mark.parametrize(
    "invalid_metadata",
    ["wrong-session", "wrong-mode", "malformed", "deep-nesting"],
)
def test_invalid_session_metadata_is_rejected_without_harvest(
    monkeypatch,
    tmp_path: Path,
    invalid_metadata: str,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            session_id = _session_id(argv)
            session = _session_dir(kwargs["env"], session_id)
            session.mkdir(parents=True, exist_ok=True)
            if invalid_metadata == "malformed":
                (session / "meta.json").write_bytes(b'{"id":')
            elif invalid_metadata == "deep-nesting":
                depth = 20_000
                (session / "meta.json").write_bytes(b'{"x":' * depth + b"0" + b"}" * depth)
            else:
                _write_metadata(
                    session,
                    "wrong-session" if invalid_metadata == "wrong-session" else session_id,
                    "completed",
                    [],
                    mode="api" if invalid_metadata == "wrong-mode" else "browser",
                )
            return _completed(argv)
        pytest.fail("invalid metadata must prevent harvest")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 0
    assert "oracle-home" not in repr(result)


def test_public_adapter_normalizes_unsafe_planner_root_constructor_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("candidate\t/requirement.md", "body\n")

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(kwargs["env"], argv, zip_bytes=buffer.getvalue())
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")
    assert result.authoring_zip is None
    assert result.review_json is None
    assert "candidate" not in repr(result)


@pytest.mark.parametrize("invalid_json", [b'{"verdict":"pass","verdict":"fail"}', b'{"score":NaN}'])
def test_public_adapter_normalizes_strict_reviewer_json_failures(
    monkeypatch,
    tmp_path: Path,
    invalid_json: bytes,
) -> None:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_reviewer_session(kwargs["env"], argv, answer=invalid_json)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, role="reviewer")

    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")
    assert result.authoring_zip is None
    assert result.review_json is None
    assert invalid_json.decode() not in repr(result)


@pytest.mark.parametrize("zip_failure", ["encrypted", "unsupported-compression"])
def test_public_adapter_normalizes_unsupported_zip_features(
    monkeypatch,
    tmp_path: Path,
    zip_failure: str,
) -> None:
    executable = _fake_executable(tmp_path)
    zip_bytes = _zip_with_unsupported_feature(zip_failure)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(kwargs["env"], argv, zip_bytes=zip_bytes)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")
    assert result.authoring_zip is None
    assert result.review_json is None
    assert "requirement.md" not in repr(result)


def test_public_adapter_rejects_zip_entry_count_overflow(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for index in range(2049):
            archive.writestr(f"candidate/{index}.md", "")

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(kwargs["env"], argv, zip_bytes=buffer.getvalue())
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")
    assert result.authoring_zip is None
    assert result.review_json is None


@pytest.mark.parametrize("role", ["planner", "semantic_revision", "reviewer"])
def test_cross_kind_output_is_rejected(monkeypatch, tmp_path: Path, role: str) -> None:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if role in {"planner", "semantic_revision"}:
            _write_reviewer_session(kwargs["env"], argv)
        else:
            _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, role=role)
    assert (result.status, result.reason) == ("rejected", "oracle_artifact_missing")
    assert result.authoring_zip is None
    assert result.review_json is None


def test_prompt_pack_preserves_exact_binary_attachment_bytes(tmp_path: Path) -> None:
    candidate = b"PK\x03\x04\x00\xffexact"
    synthesized = SynthesizedPlanningPrompt(
        role="reviewer",
        prompt="fixed prompt",
        attachments=(),
        exact_attachments=(
            PlanningPromptAttachment(
                name="target-candidate.zip",
                classification="review-target",
                source_label="candidate.zip",
                content=candidate,
            ),
        ),
        output_expectation=_review_expectation(),
    )
    pack = tmp_path / "pack"
    issue_planning_chatgpt._write_transport_pack(pack, synthesized, _source_evidence())
    assert (pack / "target-candidate.zip").read_bytes() == candidate
    assert not (pack / "prompt.md").exists()
    assert not (pack / "expected-output-contract.md").exists()
    assert not (pack / "safe-output-constraints.md").exists()


@pytest.mark.parametrize("mismatch", ["logical-filename", "internal-root"])
def test_planner_rejects_wrong_expected_zip_identity(
    monkeypatch,
    tmp_path: Path,
    mismatch: str,
) -> None:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        filename = "other.zip" if mismatch == "logical-filename" else None
        root = "other-root" if mismatch == "internal-root" else None
        _write_planner_session(kwargs["env"], argv, filename=filename, internal_root=root)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("rejected", "oracle_artifact_rejected")


@pytest.mark.parametrize("role", ["planner", "reviewer"])
def test_exact_repository_access_failure_is_blocked(
    monkeypatch,
    tmp_path: Path,
    role: str,
) -> None:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_reviewer_session(kwargs["env"], argv, answer=b"repository access failed")
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path, role=role)
    assert (result.status, result.reason) == (
        "blocked",
        "github_exact_branch_unavailable",
    )
    assert result.authoring_zip is None
    assert result.review_json is None


@pytest.mark.parametrize("role", ["planner", "semantic_revision"])
@pytest.mark.parametrize(
    "answer",
    [
        b"repository access failed: using main instead",
        b"additional prose before repository access failed",
    ],
)
def test_authoring_zip_with_repository_access_failure_near_match_is_rejected(
    monkeypatch,
    tmp_path: Path,
    role: str,
    answer: bytes,
) -> None:
    result = _invoke_with_authoring_transcripts(
        monkeypatch,
        tmp_path,
        role=role,
        transcript_payloads=(
            b"# Oracle Browser Transcript\n"
            b"## Prompt\nprivate prompt\n"
            b"## Answer\n"
            + answer
            + b"\n",
        ),
    )
    assert (result.status, result.reason) == (
        "rejected",
        "oracle_artifact_rejected",
    )
    assert result.authoring_zip is None
    assert result.review_json is None


@pytest.mark.parametrize(
    "transcript_payloads",
    [
        (b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\nmalformed answer\n",),
        (
            b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n"
            b"## Answer\ncandidate ready\n## Answer\ncandidate ready\n",
        ),
        (
            b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n"
            b"## Answer\ncandidate ready\n",
            b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n"
            b"## Answer\ncandidate ready\n",
        ),
    ],
)
def test_authoring_zip_rejects_malformed_or_multiple_transcript_state(
    monkeypatch,
    tmp_path: Path,
    transcript_payloads: tuple[bytes, ...],
) -> None:
    result = _invoke_with_authoring_transcripts(
        monkeypatch,
        tmp_path,
        transcript_payloads=transcript_payloads,
    )
    assert (result.status, result.reason) == (
        "rejected",
        "oracle_artifact_rejected",
    )
    assert result.authoring_zip is None
    assert result.review_json is None


def test_authoring_zip_with_normal_success_transcript_is_accepted(
    monkeypatch,
    tmp_path: Path,
) -> None:
    result = _invoke_with_authoring_transcripts(
        monkeypatch,
        tmp_path,
        transcript_payloads=(
            b"# Oracle Browser Transcript\n"
            b"## Prompt\nprivate prompt\n"
            b"## Answer\ncandidate ready\n",
        ),
    )
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.authoring_zip is not None


def test_typed_planner_zip_fails_closed_in_legacy_application_before_publication(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("candidate/requirement.md", "not a legacy marker frame")
    zip_bytes = zip_buffer.getvalue()
    snapshot = OracleAuthoringZipSnapshot(
        expected_logical_filename="candidate.zip",
        observed_transport_filename="candidate.zip",
        internal_root="candidate",
        size_bytes=len(zip_bytes),
        sha256=hashlib.sha256(zip_bytes).hexdigest(),
        zip_bytes=zip_bytes,
    )
    transport = PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=_source_evidence(),
        response_bytes=snapshot.size_bytes,
        response_sha256=snapshot.sha256,
        authoring_zip=snapshot,
    )
    publisher_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["PlanningCreateRequest", "run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=lambda **_kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **_kwargs: transport,
        publisher=lambda **kwargs: publisher_calls.append(kwargs),
    )

    assert (result.status, result.reason) == ("stale", "planning_source_stale")
    assert publisher_calls == []
    assert list(output.iterdir()) == []


def _patch_runtime(monkeypatch, tmp_path: Path, executable: Path, fake_run) -> None:
    monkeypatch.setattr(issue_planning_chatgpt.shutil, "which", lambda _name: str(executable))
    monkeypatch.setattr(issue_planning_chatgpt.subprocess, "run", fake_run)
    monkeypatch.setenv("ORACLE_HOME_DIR", str(tmp_path / "oracle-home"))
    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    monkeypatch.setenv("OPENAI_API_KEY", "private")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "private")
    monkeypatch.setenv("SPECDOCK_CHATGPT_COMMAND", "private-wrapper")


def _fake_executable(tmp_path: Path, *, symlink: bool = False) -> Path:
    target = tmp_path / "oracle-real"
    target.write_text("#!/bin/sh\n", encoding="utf-8")
    target.chmod(0o700)
    if not symlink:
        return target
    alias = tmp_path / "oracle"
    alias.symlink_to(target)
    return alias


def _invoke(
    tmp_path: Path,
    *,
    role: str = "planner",
    prompt: str = "fixed prompt",
    timeout_seconds: float | None = None,
):
    return issue_planning_chatgpt.invoke_issue_planning_chatgpt(
        repo_root=tmp_path,
        role=role,
        source_evidence=_source_evidence(),
        synthesized=SynthesizedPlanningPrompt(
            role=role,
            prompt=prompt,
            attachments=(("source.md", "safe context"),),
            output_expectation=(
                _review_expectation()
                if role == "reviewer"
                else _authoring_expectation()
            ),
        ),
        timeout_seconds=timeout_seconds,
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


def _completed(argv, *, stdout: bytes = b"", stderr: bytes = b"", returncode: int = 0):
    return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr=stderr)


def _root_help() -> bytes:
    return b"--engine --file --slug --wait --prompt --browser-attachments"


def _session_help() -> bytes:
    return b"--harvest --no-recover"


def _session_dir(env: dict[str, str], session_id: str) -> Path:
    return Path(env["ORACLE_HOME_DIR"]) / "sessions" / session_id


def _session_id(argv: list[str]) -> str:
    return argv[argv.index("--slug") + 1]


def _write_planner_session(
    env: dict[str, str],
    argv: list[str],
    *,
    session_id: str | None = None,
    zip_bytes: bytes | None = None,
    filename: str | None = None,
    internal_root: str | None = None,
    transcript_payloads: tuple[bytes, ...] = (),
) -> None:
    resolved_id = session_id or _session_id(argv)
    session = _session_dir(env, resolved_id)
    artifact = session / "artifacts" / (
        filename or "iss-00003-issue-planning-documents.zip"
    )
    artifact.parent.mkdir(parents=True, exist_ok=True)
    if zip_bytes is None:
        with zipfile.ZipFile(artifact, "w") as archive:
            archive.writestr(
                f"{internal_root or 'iss-00003-issue-planning-documents'}/requirement.md",
                "body\n",
            )
    else:
        artifact.write_bytes(zip_bytes)
    artifacts = [_artifact("file", artifact)]
    for index, payload in enumerate(transcript_payloads):
        transcript = session / "artifacts" / f"transcript-{index}.md"
        transcript.write_bytes(payload)
        artifacts.append(_artifact("transcript", transcript))
    _write_metadata(session, resolved_id, "completed", artifacts)


def _invoke_with_authoring_transcripts(
    monkeypatch,
    tmp_path: Path,
    *,
    transcript_payloads: tuple[bytes, ...],
    role: str = "planner",
) -> PlanningInvocationResult:
    executable = _fake_executable(tmp_path)

    def fake_run(argv, **kwargs):
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(
            kwargs["env"],
            argv,
            transcript_payloads=transcript_payloads,
        )
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    return _invoke(tmp_path, role=role)


def _authoring_expectation() -> PlanningOutputExpectation:
    return PlanningOutputExpectation(
        kind="authoring_zip",
        logical_filename="iss-00003-issue-planning-documents.zip",
        internal_root="iss-00003-issue-planning-documents",
        exact_inventory=(
            "requirement.md",
            "design.md",
            "plan.md",
            "artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md",
        ),
        onboarding_companion_path=(
            "artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"
        ),
    )


def _review_expectation() -> PlanningOutputExpectation:
    return PlanningOutputExpectation(
        kind="review_json",
        closed_json_top_level_keys=(
            "reviewed_identity",
            "reviewed_identity_sha256",
            "verdict",
            "findings",
        ),
        closed_json_finding_keys=(
            "id",
            "severity",
            "exact_location",
            "violated_requirement_or_contradiction",
            "concrete_impact",
        ),
    )


def _write_reviewer_session(
    env: dict[str, str],
    argv: list[str],
    *,
    answer: bytes = b'{"verdict":"pass"}',
) -> None:
    session_id = _session_id(argv)
    session = _session_dir(env, session_id)
    transcript = session / "artifacts" / "transcript.md"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_bytes(b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\n" + answer + b"\n")
    _write_metadata(session, session_id, "completed", [_artifact("transcript", transcript)])


def _write_metadata_only(env: dict[str, str], argv: list[str], *, status: str) -> None:
    session_id = _session_id(argv)
    session = _session_dir(env, session_id)
    session.mkdir(parents=True, exist_ok=True)
    _write_metadata(session, session_id, status, [])


def _artifact(kind: str, path: Path) -> dict[str, object]:
    contents = path.read_bytes()
    return {
        "kind": kind,
        "path": str(path),
        "sizeBytes": len(contents),
        "sha256": hashlib.sha256(contents).hexdigest(),
        "validation": {"type": "zip" if kind == "file" else "generic", "ok": True},
    }


def _write_metadata(
    session: Path,
    session_id: str,
    status: str,
    artifacts: list[dict[str, object]],
    *,
    mode: str = "browser",
) -> None:
    session.mkdir(parents=True, exist_ok=True)
    (session / "meta.json").write_text(
        json.dumps({
            "id": session_id,
            "status": status,
            "mode": mode,
            "artifacts": artifacts,
        }),
        encoding="utf-8",
    )


def _zip_with_unsupported_feature(failure: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("candidate/requirement.md", "body\n")
    payload = bytearray(buffer.getvalue())
    local = payload.index(b"PK\x03\x04")
    central = payload.index(b"PK\x01\x02")
    if failure == "encrypted":
        payload[local + 6 : local + 8] = (1).to_bytes(2, "little")
        payload[central + 8 : central + 10] = (1).to_bytes(2, "little")
    else:
        payload[local + 8 : local + 10] = (99).to_bytes(2, "little")
        payload[central + 10 : central + 12] = (99).to_bytes(2, "little")
    return bytes(payload)


def _planning_tree(repo_root: Path) -> Path:
    issue_dir = repo_root / "spec-dock" / "initiatives" / "init-one" / "epics" / "epic-one" / "issues" / "iss-one"
    issue_dir.mkdir(parents=True)
    dependencies = {
        "requirement.md": "",
        "design.md": '依存: ["requirement.md"]\n',
        "plan.md": '依存: ["requirement.md", "design.md"]\n',
    }
    kinds = {
        "requirement.md": "要件定義書（Issue）",
        "design.md": "設計書（Issue）",
        "plan.md": "実装計画書（Issue）",
    }
    for filename in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / filename).write_text(
            "---\n"
            f"種別: {kinds[filename]}\n"
            'ID: "iss-00003"\n'
            'タイトル: "Issue"\n'
            '状態: "approved"\n'
            '作成者: "Author"\n'
            '最終更新: "2026-07-27"\n'
            f"{dependencies[filename]}"
            '親: ["epic-00002", "init-00001"]\n'
            "---\n\n"
            "# iss-00003 Issue\n\n"
            "Substantive content.\n",
            encoding="utf-8",
        )
    return issue_dir


def _record(path: Path) -> StoredMetaRecord:
    return StoredMetaRecord(
        kind="issue",
        id="iss-00003",
        title="Issue",
        slug="issue",
        path=path.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(path / ".meta.json").as_posix(),
    )
