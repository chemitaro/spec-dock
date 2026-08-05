"""Provider-owned direct Oracle transport for Issue Planning."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
import http.client
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
from tempfile import TemporaryDirectory
import time
from typing import TYPE_CHECKING, Literal
from urllib.parse import urlsplit

from spec_dock_runtime.domain.issue_planning_contracts import (
    OracleAuthoringZipSnapshot,
    OracleReviewJsonPayload,
    PlanningInvocationResult,
    PlanningSourceEvidence,
)
from spec_dock_runtime.infra.git_cli import origin_github_repo_slug
from spec_dock_runtime.infra.issue_planning_oracle_artifact import (
    OracleArtifactError,
    OracleArtifactReader,
    artifact_reader_for_version,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from spec_dock_runtime.application.issue_planning_prompt import (
        PlanningOutputExpectation,
        SynthesizedPlanningPrompt,
    )

_PREFLIGHT_TIMEOUT_SECONDS = 10.0
_MAX_CDP_VERSION_BYTES = 64 * 1024
_DEFAULT_RUN_TIMEOUT_SECONDS = 2 * 60 * 60
_DEFAULT_RECOVERY_TIMEOUT_SECONDS = 2 * 60
_RECOVERY_POLL_INTERVAL_SECONDS = 0.25
_SessionState = Literal["terminal", "nonterminal", "missing", "invalid"]
_ORACLE_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_SAFE_ENVIRONMENT_KEYS = frozenset({
    "HOME",
    "LANG",
    "ORACLE_HOME_DIR",
    "PATH",
    "TMPDIR",
    "TZ",
})
_SESSION_ROLE_SLUGS = {
    "planner": "planner",
    "semantic_revision": "semantic-revision",
    "reviewer": "reviewer",
}


@dataclass(frozen=True)
class _OracleCompatibilityProfile:
    """Private exact-version Oracle contract selected during preflight."""

    profile_id: str
    version: str
    required_root_capabilities: tuple[str, ...]
    required_session_capabilities: tuple[str, ...]
    browser_argv_builder: Callable[..., list[str]]
    inline_mode_characterized: bool
    stage_evidence_decoder: Callable[[str], _SessionState]
    artifact_reader: OracleArtifactReader
    harvest_argv_builder: Callable[[Path, str], tuple[str, ...]]
    capture_argv_builder: Callable[[Path, str], tuple[str, ...]]

    @property
    def browser_argv_policy(self) -> Callable[..., list[str]]:
        """Expose the profile-owned browser policy without a generic fallback."""

        return self.browser_argv_builder


def _build_oracle_0161_browser_argv(
    executable: Path,
    managed_chrome: tuple[str, int],
    session_id: str,
    prompt: str,
    attachment_paths: tuple[Path, ...],
) -> list[str]:
    """Build the characterized 0.16.1 browser invocation without normalization."""

    argv = [
        str(executable),
        "--engine",
        "browser",
        "--model",
        "Pro",
        "--browser-model-strategy",
        "select",
        "--remote-chrome",
        f"{managed_chrome[0]}:{managed_chrome[1]}",
        "--browser-no-cookie-sync",
        "--wait",
        "--browser-attachments",
        "always",
        "--slug",
        session_id,
        "--prompt",
        prompt,
    ]
    for attachment_path in attachment_paths:
        argv.extend(("--file", str(attachment_path)))
    return argv


def _build_oracle_0170_browser_argv(
    executable: Path,
    managed_chrome: tuple[str, int],
    session_id: str,
    prompt: str,
    attachment_paths: tuple[Path, ...],
) -> list[str]:
    """Build the characterized 0.17.0 browser invocation."""

    argv = [
        str(executable),
        "--engine",
        "browser",
        "--model",
        "gpt-5.6",
        "--browser-model-strategy",
        "select",
        "--remote-chrome",
        f"{managed_chrome[0]}:{managed_chrome[1]}",
        "--browser-no-cookie-sync",
        "--wait",
        "--browser-attachments",
        "always",
        "--slug",
        session_id,
        "--prompt",
        prompt,
    ]
    for attachment_path in attachment_paths:
        argv.extend(("--file", str(attachment_path)))
    return argv


def _build_oracle_0161_session_argv(
    executable: Path,
    session_id: str,
) -> tuple[str, ...]:
    """Return the characterized 0.16.1 same-session command unchanged."""

    return (
        str(executable),
        "session",
        session_id,
        "--harvest",
        "--no-recover",
    )


def _build_oracle_0170_session_argv(
    executable: Path,
    session_id: str,
) -> tuple[str, ...]:
    """Return the characterized 0.17.0 same-session command unchanged."""

    return (
        str(executable),
        "session",
        session_id,
        "--harvest",
        "--no-recover",
    )


def _decode_oracle_0161_stage(status_value: str) -> _SessionState:
    return "terminal" if status_value == "completed" else "nonterminal"


def _decode_oracle_0170_stage(status_value: object) -> _SessionState:
    return "terminal" if status_value == "completed" else "invalid"


_ORACLE_PROFILE_REGISTRY: dict[str, _OracleCompatibilityProfile] = {
    "0.16.1": _OracleCompatibilityProfile(
        profile_id="oracle-0.16.1",
        version="0.16.1",
        required_root_capabilities=(
            "--engine",
            "--file",
            "--slug",
            "--wait",
            "--prompt",
            "--browser-attachments",
            "--model",
            "--browser-model-strategy",
            "--remote-chrome",
            "--browser-no-cookie-sync",
        ),
        required_session_capabilities=("--harvest", "--no-recover"),
        browser_argv_builder=_build_oracle_0161_browser_argv,
        inline_mode_characterized=False,
        stage_evidence_decoder=_decode_oracle_0161_stage,
        artifact_reader=artifact_reader_for_version("0.16.1"),
        harvest_argv_builder=_build_oracle_0161_session_argv,
        capture_argv_builder=_build_oracle_0161_session_argv,
    ),
    "0.17.0": _OracleCompatibilityProfile(
        profile_id="oracle-0.17.0",
        version="0.17.0",
        required_root_capabilities=(
            "--engine",
            "--file",
            "--slug",
            "--wait",
            "--prompt",
            "--browser-attachments",
            "--model",
            "--browser-model-strategy",
            "--remote-chrome",
            "--browser-no-cookie-sync",
        ),
        required_session_capabilities=("--harvest", "--no-recover"),
        browser_argv_builder=_build_oracle_0170_browser_argv,
        inline_mode_characterized=True,
        stage_evidence_decoder=_decode_oracle_0170_stage,
        artifact_reader=artifact_reader_for_version("0.17.0"),
        harvest_argv_builder=_build_oracle_0170_session_argv,
        capture_argv_builder=_build_oracle_0170_session_argv,
    ),
}

# Retain the existing private test seams while making the profile the owner.
_ROOT_CAPABILITIES = tuple(
    capability.encode("ascii")
    for capability in _ORACLE_PROFILE_REGISTRY["0.16.1"].required_root_capabilities
)
_SESSION_CAPABILITIES = tuple(
    capability.encode("ascii")
    for capability in _ORACLE_PROFILE_REGISTRY["0.16.1"].required_session_capabilities
)


@dataclass(frozen=True)
class _OraclePreflightReceipt:
    """Content-free result of the current Oracle preflight checks."""

    version: str | None
    version_exit_code: int | None
    root_help_exit_code: int | None
    session_help_exit_code: int | None
    missing_root_capabilities: tuple[str, ...]
    missing_session_capabilities: tuple[str, ...]
    supported_by_current_runtime: bool
    profile_id: str | None = None


def _profile_for_version(version: str | None) -> _OracleCompatibilityProfile | None:
    if version is None:
        return None
    return _ORACLE_PROFILE_REGISTRY.get(version)


def _profile_is_complete(profile: _OracleCompatibilityProfile | None) -> bool:
    reader = profile.artifact_reader if profile is not None else None
    review_output_characterized = getattr(reader, "review_output_characterized", None)
    return bool(
        profile is not None
        and profile.required_root_capabilities
        and profile.required_session_capabilities
        and isinstance(profile.inline_mode_characterized, bool)
        and callable(profile.browser_argv_builder)
        and callable(profile.stage_evidence_decoder)
        and callable(profile.harvest_argv_builder)
        and callable(profile.capture_argv_builder)
        and reader is not None
        and reader.version == profile.version
        and isinstance(review_output_characterized, bool)
        and callable(reader.read_session_status)
        and callable(reader.snapshot_authoring_zip)
        and callable(reader.snapshot_review_json)
        and callable(reader.has_exact_repository_access_failure)
    )


def resolve_issue_planning_github_repository(repo_root: Path) -> str | None:
    return origin_github_repo_slug(repo_root)


def invoke_issue_planning_chatgpt(
    *,
    repo_root: Path,
    role: Literal["planner", "semantic_revision", "reviewer"],
    source_evidence: PlanningSourceEvidence,
    synthesized: SynthesizedPlanningPrompt,
    timeout_seconds: float | None = None,
) -> PlanningInvocationResult:
    expectation = synthesized.output_expectation
    if not _invocation_contract_is_valid(role, synthesized, expectation):
        return _result("rejected", "planning_context_rejected", source_evidence, None)
    managed_chrome = _parse_managed_chrome_endpoint(os.environ.get("SPECDOCK_ORACLE_REMOTE_CHROME"))
    if managed_chrome is None:
        return _result("blocked", "oracle_unavailable", source_evidence, None)
    executable = _resolve_oracle_executable()
    if executable is None:
        return _result("blocked", "oracle_unavailable", source_evidence, None)
    executable_identity = _executable_identity(executable)
    if executable_identity is None:
        return _result("blocked", "oracle_unavailable", source_evidence, None)
    child_env = _sanitized_child_environment()
    preflight = _read_oracle_preflight_receipt(
        executable,
        child_env=child_env,
        cwd=repo_root,
    )
    profile = _profile_for_version(preflight.version)
    if not preflight.supported_by_current_runtime or profile is None:
        return _result(
            "blocked",
            "oracle_capability_unsupported",
            source_evidence,
            None,
        )
    if role == "reviewer" and not profile.artifact_reader.review_output_characterized:
        return _result(
            "blocked",
            "oracle_capability_unsupported",
            source_evidence,
            None,
        )
    if not _preflight_managed_chrome(managed_chrome):
        return _result("blocked", "oracle_unavailable", source_evidence, None)

    with TemporaryDirectory(prefix="specdock-issue-planning-") as raw_temp:
        temp_root = Path(raw_temp)
        staging = temp_root / "staging"
        session_id = _new_session_id(role, source_evidence)
        session_root = _oracle_home(child_env) / "sessions" / session_id
        if session_root.exists() or session_root.is_symlink():
            return _result(
                "blocked",
                "oracle_session_recovery_required",
                source_evidence,
                None,
            )
        final_executable = _resolve_oracle_executable()
        if (
            final_executable is None
            or final_executable != executable
            or _executable_identity(final_executable) != executable_identity
        ):
            return _result("blocked", "oracle_unavailable", source_evidence, None)
        argv = profile.browser_argv_policy(
            final_executable,
            managed_chrome,
            session_id,
            synthesized.prompt,
            tuple(synthesized.attachment_paths),
        )
        run_timeout = (
            timeout_seconds if timeout_seconds is not None and timeout_seconds > 0 else _DEFAULT_RUN_TIMEOUT_SECONDS
        )
        exit_code: int | None = None
        needs_recovery = False
        try:
            completed = _run_oracle(
                argv,
                child_env=child_env,
                cwd=repo_root,
                timeout=run_timeout,
            )
            exit_code = completed.returncode
            needs_recovery = completed.returncode != 0
        except (subprocess.TimeoutExpired, OSError):
            needs_recovery = True

        session_state = _session_state(
            session_root,
            profile=profile,
            session_id=session_id,
        )
        if session_state == "invalid":
            return _result(
                "rejected",
                "oracle_artifact_rejected",
                source_evidence,
                exit_code,
            )
        if needs_recovery or session_state != "terminal":
            recovered_state = _recover_same_session(
                executable=final_executable,
                executable_identity=executable_identity,
                profile=profile,
                session_id=session_id,
                session_root=session_root,
                child_env=child_env,
                cwd=repo_root,
                timeout=min(run_timeout, _DEFAULT_RECOVERY_TIMEOUT_SECONDS),
            )
            if recovered_state == "invalid":
                return _result(
                    "rejected",
                    "oracle_artifact_rejected",
                    source_evidence,
                    exit_code,
                )
            if recovered_state != "terminal":
                return _result(
                    "blocked",
                    "oracle_session_recovery_required",
                    source_evidence,
                    exit_code,
                )
        return _collect_typed_result(
            role=role,
            expectation=expectation,
            profile=profile,
            session_root=session_root,
            session_id=session_id,
            staging=staging,
            source_evidence=source_evidence,
            exit_code=exit_code,
        )


def _parse_managed_chrome_endpoint(value: str | None) -> tuple[str, int] | None:
    if value is None:
        return None
    match = re.fullmatch(r"(127\.0\.0\.1|localhost):([0-9]{1,5})", value)
    if match is None:
        return None
    port = int(match.group(2))
    if not 1 <= port <= 65535:
        return None
    return "127.0.0.1", port


def _preflight_managed_chrome(endpoint: tuple[str, int]) -> bool:
    host, port = endpoint
    connection = http.client.HTTPConnection(
        host,
        port,
        timeout=_PREFLIGHT_TIMEOUT_SECONDS,
    )
    try:
        connection.request(
            "GET",
            "/json/version",
            headers={"Connection": "close"},
        )
        response = connection.getresponse()
        if response.status != 200:
            return False
        payload = response.read(_MAX_CDP_VERSION_BYTES + 1)
        if len(payload) > _MAX_CDP_VERSION_BYTES:
            return False
        parsed_payload = json.loads(payload)
        if not isinstance(parsed_payload, dict):
            return False
        debugger_url = parsed_payload.get("webSocketDebuggerUrl")
        if not isinstance(debugger_url, str) or not debugger_url:
            return False
        parsed_url = urlsplit(debugger_url)
        if (
            parsed_url.scheme not in {"ws", "wss"}
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.hostname not in {"127.0.0.1", "localhost"}
            or parsed_url.port != port
        ):
            return False
    except (OSError, ValueError, json.JSONDecodeError, http.client.HTTPException):
        return False
    finally:
        connection.close()
    return True


def _resolve_oracle_executable() -> Path | None:
    candidate_text = shutil.which("oracle")
    if not candidate_text:
        return None
    candidate = Path(candidate_text)
    try:
        resolved = candidate.resolve(strict=True)
        mode = resolved.stat().st_mode
    except (OSError, RuntimeError):
        return None
    if not stat.S_ISREG(mode) or not os.access(resolved, os.X_OK):
        return None
    return resolved


def _executable_identity(path: Path) -> tuple[int, int, int, int] | None:
    try:
        metadata = path.stat()
    except OSError:
        return None
    if not stat.S_ISREG(metadata.st_mode) or not os.access(path, os.X_OK):
        return None
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
    )


def _preflight_supported_oracle(
    executable: Path,
    *,
    child_env: dict[str, str],
    cwd: Path,
) -> bool:
    return _read_oracle_preflight_receipt(
        executable,
        child_env=child_env,
        cwd=cwd,
    ).supported_by_current_runtime


def _read_oracle_preflight_receipt(
    executable: Path,
    *,
    child_env: dict[str, str],
    cwd: Path,
) -> _OraclePreflightReceipt:
    legacy_profile = _ORACLE_PROFILE_REGISTRY["0.16.1"]
    missing_root_capabilities = legacy_profile.required_root_capabilities
    missing_session_capabilities = legacy_profile.required_session_capabilities
    try:
        version_result = _run_oracle(
            [str(executable), "--version"],
            child_env=child_env,
            cwd=cwd,
            timeout=_PREFLIGHT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _OraclePreflightReceipt(
            version=None,
            profile_id=None,
            version_exit_code=None,
            root_help_exit_code=None,
            session_help_exit_code=None,
            missing_root_capabilities=missing_root_capabilities,
            missing_session_capabilities=missing_session_capabilities,
            supported_by_current_runtime=False,
        )

    version = _preflight_version(version_result.stdout)
    profile = _profile_for_version(version)
    if version_result.returncode != 0 or profile is None or not _profile_is_complete(profile):
        return _OraclePreflightReceipt(
            version=version,
            profile_id=profile.profile_id if profile is not None else None,
            version_exit_code=version_result.returncode,
            root_help_exit_code=None,
            session_help_exit_code=None,
            missing_root_capabilities=missing_root_capabilities,
            missing_session_capabilities=missing_session_capabilities,
            supported_by_current_runtime=False,
        )

    try:
        root_help = _run_oracle(
            [str(executable), "--help"],
            child_env=child_env,
            cwd=cwd,
            timeout=_PREFLIGHT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _OraclePreflightReceipt(
            version=version,
            profile_id=profile.profile_id,
            version_exit_code=version_result.returncode,
            root_help_exit_code=None,
            session_help_exit_code=None,
            missing_root_capabilities=missing_root_capabilities,
            missing_session_capabilities=missing_session_capabilities,
            supported_by_current_runtime=False,
        )

    root_tokens = _help_option_tokens(root_help.stdout)
    missing_root_capabilities = tuple(
        capability
        for capability in profile.required_root_capabilities
        if capability not in root_tokens
    )
    if root_help.returncode != 0 or missing_root_capabilities:
        return _OraclePreflightReceipt(
            version=version,
            profile_id=profile.profile_id,
            version_exit_code=version_result.returncode,
            root_help_exit_code=root_help.returncode,
            session_help_exit_code=None,
            missing_root_capabilities=missing_root_capabilities,
            missing_session_capabilities=missing_session_capabilities,
            supported_by_current_runtime=False,
        )
    try:
        session_help = _run_oracle(
            [str(executable), "session", "--help"],
            child_env=child_env,
            cwd=cwd,
            timeout=_PREFLIGHT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _OraclePreflightReceipt(
            version=version,
            profile_id=profile.profile_id,
            version_exit_code=version_result.returncode,
            root_help_exit_code=root_help.returncode,
            session_help_exit_code=None,
            missing_root_capabilities=missing_root_capabilities,
            missing_session_capabilities=missing_session_capabilities,
            supported_by_current_runtime=False,
        )

    session_tokens = _help_option_tokens(session_help.stdout)
    missing_session_capabilities = tuple(
        capability
        for capability in profile.required_session_capabilities
        if capability not in session_tokens
    )
    return _OraclePreflightReceipt(
        version=version,
        profile_id=profile.profile_id,
        version_exit_code=version_result.returncode,
        root_help_exit_code=root_help.returncode,
        session_help_exit_code=session_help.returncode,
        missing_root_capabilities=missing_root_capabilities,
        missing_session_capabilities=missing_session_capabilities,
        supported_by_current_runtime=(
            root_help.returncode == 0
            and session_help.returncode == 0
            and not missing_root_capabilities
            and not missing_session_capabilities
            and _profile_is_complete(profile)
        ),
    )


_HELP_OPTION_RE = re.compile(rb"(?<![A-Za-z0-9_])--[A-Za-z0-9][A-Za-z0-9-]*")


def _help_option_tokens(output: bytes) -> frozenset[str]:
    return frozenset(
        match.group(0).decode("ascii")
        for match in _HELP_OPTION_RE.finditer(output)
    )


def _preflight_version(stdout: bytes) -> str | None:
    value = stdout.decode("utf-8", errors="replace").strip()
    return value if _ORACLE_VERSION_RE.fullmatch(value) else None


def _run_oracle(
    argv: Sequence[str],
    *,
    child_env: dict[str, str],
    cwd: Path,
    timeout: float,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=child_env,
        shell=False,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _recover_same_session(
    *,
    executable: Path,
    executable_identity: tuple[int, int, int, int],
    profile: _OracleCompatibilityProfile,
    session_id: str,
    session_root: Path,
    child_env: dict[str, str],
    cwd: Path,
    timeout: float,
) -> _SessionState:
    deadline = time.monotonic() + timeout
    initial_state = _session_state(session_root, profile=profile, session_id=session_id)
    if initial_state in {"terminal", "invalid"}:
        return initial_state
    recovery_executable = _resolve_oracle_executable()
    if (
        recovery_executable is None
        or recovery_executable != executable
        or _executable_identity(recovery_executable) != executable_identity
    ):
        return "nonterminal"
    pre_harvest_state = _session_state(session_root, profile=profile, session_id=session_id)
    if pre_harvest_state in {"terminal", "invalid"}:
        return pre_harvest_state
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return pre_harvest_state
    with suppress(OSError, subprocess.TimeoutExpired):
        _run_oracle(
            profile.harvest_argv_builder(recovery_executable, session_id),
            child_env=child_env,
            cwd=cwd,
            timeout=remaining,
        )
    return _poll_same_session_state(
        session_root,
        profile=profile,
        session_id=session_id,
        deadline=deadline,
    )


def _poll_same_session_state(
    session_root: Path,
    *,
    profile: _OracleCompatibilityProfile,
    session_id: str,
    deadline: float,
) -> _SessionState:
    while True:
        state = _session_state(session_root, profile=profile, session_id=session_id)
        if state in {"terminal", "invalid"}:
            return state
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return state
        time.sleep(min(_RECOVERY_POLL_INTERVAL_SECONDS, remaining))


def _session_state(
    session_root: Path,
    *,
    profile: _OracleCompatibilityProfile,
    session_id: str,
) -> _SessionState:
    try:
        status_value = profile.artifact_reader.read_session_status(
            session_root,
            session_id=session_id,
            oracle_version=profile.version,
        )
    except OracleArtifactError as error:
        return "missing" if error.code == "oracle_session_missing" else "invalid"
    return profile.stage_evidence_decoder(status_value)


def _collect_typed_result(
    *,
    role: Literal["planner", "semantic_revision", "reviewer"],
    expectation: PlanningOutputExpectation,
    profile: _OracleCompatibilityProfile,
    session_root: Path,
    session_id: str,
    staging: Path,
    source_evidence: PlanningSourceEvidence,
    exit_code: int | None,
) -> PlanningInvocationResult:
    try:
        reader = profile.artifact_reader
        if reader.has_exact_repository_access_failure(
            session_root,
            session_id=session_id,
            oracle_version=profile.version,
            staging_dir=staging / "branch-gate",
        ):
            return _result(
                "blocked",
                "github_exact_branch_unavailable",
                source_evidence,
                exit_code,
            )
        if role in {"planner", "semantic_revision"}:
            authoring_zip = reader.snapshot_authoring_zip(
                session_root,
                session_id=session_id,
                oracle_version=profile.version,
                staging_dir=staging,
            )
            if (
                authoring_zip.expected_logical_filename != expectation.logical_filename
                or authoring_zip.internal_root != expectation.internal_root
            ):
                raise OracleArtifactError("oracle_artifact_rejected")
            return _pass_result(
                source_evidence=source_evidence,
                exit_code=exit_code,
                authoring_zip=authoring_zip,
            )
        review_json = reader.snapshot_review_json(
            session_root,
            session_id=session_id,
            oracle_version=profile.version,
            staging_dir=staging,
        )
        return _pass_result(
            source_evidence=source_evidence,
            exit_code=exit_code,
            review_json=review_json,
        )
    except OracleArtifactError as error:
        status: Literal["blocked", "rejected"] = (
            "blocked" if error.code == "oracle_session_recovery_required" else "rejected"
        )
        reason = (
            error.code
            if error.code
            in {
                "oracle_artifact_missing",
                "oracle_artifact_ambiguous",
                "oracle_artifact_rejected",
            }
            else "oracle_artifact_rejected"
        )
        return _result(status, reason, source_evidence, exit_code)


def _pass_result(
    *,
    source_evidence: PlanningSourceEvidence,
    exit_code: int | None,
    authoring_zip: OracleAuthoringZipSnapshot | None = None,
    review_json: OracleReviewJsonPayload | None = None,
) -> PlanningInvocationResult:
    typed = authoring_zip if authoring_zip is not None else review_json
    if typed is None:
        raise ValueError("typed Oracle output is required")
    return PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=source_evidence,
        backend_exit_code=exit_code,
        response_bytes=typed.size_bytes,
        response_sha256=typed.sha256,
        authoring_zip=authoring_zip,
        review_json=review_json,
    )


def _result(
    status: Literal["blocked", "rejected"],
    reason: str,
    source_evidence: PlanningSourceEvidence | None,
    exit_code: int | None,
) -> PlanningInvocationResult:
    return PlanningInvocationResult(
        status=status,
        reason=reason,
        source_evidence=source_evidence,
        backend_exit_code=exit_code,
    )


def _sanitized_child_environment() -> dict[str, str]:
    result = {key: value for key, value in os.environ.items() if key in _SAFE_ENVIRONMENT_KEYS or key.startswith("LC_")}
    result.setdefault("PATH", os.defpath)
    return result


def _oracle_home(child_env: dict[str, str]) -> Path:
    configured = child_env.get("ORACLE_HOME_DIR")
    if configured:
        return Path(configured)
    home = child_env.get("HOME")
    return Path(home) / ".oracle" if home else Path.home() / ".oracle"


def _new_session_id(
    role: Literal["planner", "semantic_revision", "reviewer"],
    source_evidence: PlanningSourceEvidence,
) -> str:
    return f"specdock-{_SESSION_ROLE_SLUGS[role]}-{source_evidence.snapshot_id[:6]}-{secrets.token_hex(4)}"


def _invocation_contract_is_valid(
    role: str,
    synthesized: SynthesizedPlanningPrompt,
    expectation: PlanningOutputExpectation | None,
) -> bool:
    if synthesized.role != role or expectation is None:
        return False
    expected_kind = "review_json" if role == "reviewer" else "authoring_zip"
    return role in {"planner", "semantic_revision", "reviewer"} and expectation.kind == expected_kind
