from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = (
    Path(__file__).parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.authoring_pack.github_fetch_policy import (  # noqa: E402
    BACKOFF_SECONDS,
    DIAGNOSTIC_EXCERPT_MAX_BYTES,
    MAX_ATTEMPTS,
    classify_fetch_outcome,
    run_origin_fetch_policy,
    safe_diagnostic,
)
from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (  # noqa: E402
    _fetch_summary,
)
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    GitProcessOutcome,
)
from spec_dock_runtime.infra.authoring_pack.git_fetch import (  # noqa: E402
    GitFetchExecutionRequest,
    execute_git_fetch,
)


class _CompletedProcess:
    returncode = 0
    stdout = b""
    stderr = b""


def test_git_fetch_execution_request_has_fixed_policy() -> None:
    request = GitFetchExecutionRequest.for_repo(Path("/tmp/repo"))

    assert request.executable == "git"
    assert request.argv == ("fetch", "--prune", "origin")
    assert request.timeout_seconds == pytest.approx(60.0)
    assert request.environment_policy_id == "git-fetch-noninteractive-v1"


def test_execute_git_fetch_reports_spawn_failure(monkeypatch) -> None:
    request = GitFetchExecutionRequest.for_repo(Path("/tmp/repo"))

    def fail_to_spawn(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr("subprocess.run", fail_to_spawn)

    outcome = execute_git_fetch(request)

    assert outcome.return_code is None
    assert outcome.termination == "spawn_error"
    assert outcome.os_error_kind == "FileNotFoundError"
    assert outcome.stdout == b""
    assert outcome.stderr == b""


def test_execute_git_fetch_uses_fixed_argv_cwd_and_noninteractive_environment(monkeypatch) -> None:
    captured = {}

    def capture_run(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return _CompletedProcess()

    monkeypatch.setattr("subprocess.run", capture_run)
    monkeypatch.setenv("GIT_TRACE", "1")

    outcome = execute_git_fetch(GitFetchExecutionRequest.for_repo(Path("/tmp/repo")))

    assert outcome.return_code == 0
    assert captured["argv"] == ["git", "fetch", "--prune", "origin"]
    assert captured["cwd"] == "/tmp/repo"
    assert captured["shell"] is False
    assert captured["timeout"] == pytest.approx(60.0)
    assert captured["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert captured["env"]["LC_ALL"] == "C"
    assert captured["env"]["LANG"] == "C"
    assert "GIT_TRACE" not in captured["env"]


def test_spawn_failure_becomes_typed_bounded_fetch_evidence() -> None:
    summary = _fetch_summary(
        GitProcessOutcome(
            return_code=None,
            termination="spawn_error",
            stdout=b"",
            stderr=b"raw exception details must not escape",
            duration_ms=4,
            os_error_kind="FileNotFoundError",
        )
    )

    payload = summary.to_dict()

    assert payload["status"] == "failed"
    assert payload["attempts"][0]["failure_class"] == "spawn_failure"
    assert payload["attempts"][0]["return_code"] is None
    assert "raw exception" not in str(payload)


def test_timeout_capture_becomes_typed_bounded_fetch_evidence(monkeypatch) -> None:
    def time_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=["git", "fetch", "--prune", "origin"],
            timeout=60.0,
            output="partial stdout",
            stderr=b"raw timeout details",
        )

    monkeypatch.setattr("subprocess.run", time_out)

    outcome = execute_git_fetch(GitFetchExecutionRequest.for_repo(Path("/tmp/repo")))
    payload = _fetch_summary(outcome).to_dict()

    assert outcome.termination == "timeout"
    assert outcome.return_code is None
    assert outcome.stdout == b"partial stdout"
    assert outcome.stderr == b"raw timeout details"
    assert payload["policy_id"] == "origin-fetch-v1"
    assert payload["status"] == "failed"
    assert payload["attempts"][0]["termination"] == "timeout"
    assert payload["attempts"][0]["return_code"] is None
    assert "partial stdout" not in str(payload)
    assert "raw timeout details" not in str(payload)


@pytest.mark.parametrize(
    ("termination", "stderr", "expected_class", "confidence", "retryable"),
    [
        ("timeout", b"", "timeout", "certain", True),
        ("exited", b"fatal: unable to access: Connection reset by peer", "transient_transport", "probable", True),
        ("exited", b"HTTP 503 Service Unavailable", "transient_transport", "probable", True),
        ("exited", b"HTTP 429: too many requests", "remote_throttled", "probable", True),
        ("exited", b"cannot lock ref 'refs/remotes/origin/main': .lock exists", "local_ref_lock_contention", "probable", True),
        ("exited", b"ERROR: Repository not found.", "remote_access_denied_or_not_found", "probable", False),
        ("exited", b"fatal: Authentication failed", "remote_access_denied_or_not_found", "probable", False),
        ("exited", b"git@example.com: Permission denied (publickey).", "remote_access_denied_or_not_found", "probable", False),
        ("exited", b"Host key verification failed.", "host_identity_failure", "probable", False),
        ("exited", b"SSL certificate problem: unable to get local issuer certificate", "host_identity_failure", "probable", False),
        ("exited", b"fatal: 'origin' does not appear to be a git repository", "repository_configuration", "probable", False),
        ("exited", b"fatal: could not write file: Operation not permitted", "execution_or_filesystem_denied", "probable", False),
        ("spawn_error", b"", "spawn_failure", "certain", False),
        ("cancelled", b"", "cancelled", "certain", False),
        ("exited", b"unmatched provider error", "unknown", "unknown", False),
    ],
)
def test_classifier_table(termination, stderr, expected_class, confidence, retryable) -> None:
    outcome = GitProcessOutcome(
        return_code=None if termination != "exited" else 1,
        termination=termination,
        stdout=b"",
        stderr=stderr,
        duration_ms=1,
    )

    classification = classify_fetch_outcome(outcome)

    assert classification.failure_class == expected_class
    assert classification.confidence == confidence
    assert classification.retryable is retryable


def test_conflicting_signals_fail_closed_as_unknown() -> None:
    outcome = GitProcessOutcome(
        return_code=1,
        termination="exited",
        stdout=b"",
        stderr=b"Repository not found; connection reset by peer",
        duration_ms=1,
    )

    classification = classify_fetch_outcome(outcome)

    assert classification.failure_class == "unknown"
    assert classification.confidence == "unknown"
    assert classification.retryable is False


def test_retry_uses_same_request_shape_and_bounded_fake_sleep() -> None:
    request = GitFetchExecutionRequest.for_repo(Path("/tmp/repo"))
    observed_requests = []
    outcomes = iter(
        [
            GitProcessOutcome(1, "exited", b"", b"Connection reset by peer", 2),
            GitProcessOutcome(0, "exited", b"", b"", 3),
        ]
    )
    sleeps: list[float] = []

    def executor(actual_request):
        observed_requests.append(actual_request)
        return next(outcomes)

    summary = run_origin_fetch_policy(request, executor=executor, sleeper=sleeps.append)

    assert summary.status == "success"
    assert len(summary.attempts) == 2 == MAX_ATTEMPTS
    assert observed_requests == [request, request]
    assert observed_requests[0] is observed_requests[1]
    assert sleeps == [BACKOFF_SECONDS] == [0.25]


def test_http_5xx_retries_once_then_succeeds() -> None:
    outcomes = iter(
        [
            GitProcessOutcome(1, "exited", b"", b"HTTP 503 Service Unavailable", 2),
            GitProcessOutcome(0, "exited", b"", b"", 3),
        ]
    )
    calls = []
    sleeps: list[float] = []

    def executor(request):
        calls.append(request)
        return next(outcomes)

    summary = run_origin_fetch_policy(
        GitFetchExecutionRequest.for_repo(Path("/tmp/repo")),
        executor=executor,
        sleeper=sleeps.append,
    )

    assert summary.status == "success"
    assert len(calls) == len(summary.attempts) == 2
    assert summary.attempts[0].failure_class == "transient_transport"
    assert summary.attempts[0].confidence == "probable"
    assert summary.attempts[0].retryable is True
    assert sleeps == [0.25]


def test_timeout_retries_only_to_total_attempt_budget_without_real_sleep() -> None:
    request = GitFetchExecutionRequest.for_repo(Path("/tmp/repo"))
    calls = []
    sleeps: list[float] = []

    def executor(actual_request):
        calls.append(actual_request)
        return GitProcessOutcome(None, "timeout", b"", b"timeout raw", 60_000)

    summary = run_origin_fetch_policy(request, executor=executor, sleeper=sleeps.append)

    assert summary.status == "failed"
    assert len(calls) == len(summary.attempts) == 2
    assert sleeps == [0.25]
    assert all(attempt.failure_class == "timeout" for attempt in summary.attempts)


@pytest.mark.parametrize("termination", ["spawn_error", "cancelled"])
def test_spawn_and_cancel_never_retry(termination) -> None:
    calls = []

    def executor(request):
        calls.append(request)
        return GitProcessOutcome(None, termination, b"", b"private", 1)

    summary = run_origin_fetch_policy(
        GitFetchExecutionRequest.for_repo(Path("/tmp/repo")), executor=executor, sleeper=lambda _: None
    )

    assert len(calls) == 1
    assert summary.status == ("cancelled" if termination == "cancelled" else "failed")


@pytest.mark.parametrize(
    "stderr",
    [b"ERROR: Repository not found.", b"unmatched provider error"],
)
def test_permanent_and_unknown_failures_never_retry(stderr) -> None:
    calls = []

    def executor(request):
        calls.append(request)
        return GitProcessOutcome(1, "exited", b"", stderr, 1)

    summary = run_origin_fetch_policy(
        GitFetchExecutionRequest.for_repo(Path("/tmp/repo")), executor=executor, sleeper=lambda _: None
    )

    assert summary.status == "failed"
    assert len(calls) == len(summary.attempts) == 1
    assert summary.attempts[0].retryable is False


def test_ref_lock_retry_never_removes_lock_file(tmp_path) -> None:
    lock_file = tmp_path / "sentinel.lock"
    lock_file.write_text("owned elsewhere", encoding="utf-8")

    summary = run_origin_fetch_policy(
        GitFetchExecutionRequest.for_repo(tmp_path),
        executor=lambda _request: GitProcessOutcome(
            1,
            "exited",
            b"",
            b"cannot lock ref 'refs/remotes/origin/main': .lock exists",
            1,
        ),
        sleeper=lambda _: None,
    )

    assert len(summary.attempts) == 2
    assert all(attempt.failure_class == "local_ref_lock_contention" for attempt in summary.attempts)
    assert lock_file.read_text(encoding="utf-8") == "owned elsewhere"


def test_safe_diagnostic_redacts_secrets_paths_non_utf8_and_truncates() -> None:
    raw = (
        b"https://alice:secret@example.com/repo token=ghp_abcdefghijklmnopqrstuvwxyz123456 "
        b"Authorization: Bearer super-secret /Users/alice/private/repo \xff "
        + b"x" * 2000
    )

    diagnostic = safe_diagnostic(raw, code="transient_transport")
    payload = diagnostic.to_dict()

    assert diagnostic.source_byte_count == len(raw)
    assert diagnostic.excerpt_byte_count <= DIAGNOSTIC_EXCERPT_MAX_BYTES == 1024
    assert diagnostic.truncated is True
    assert diagnostic.redaction_applied is True
    assert diagnostic.redacted_sha256
    serialized = str(payload)
    for unsafe in ("alice:secret", "ghp_", "super-secret", "/Users/alice"):
        assert unsafe not in serialized
