import builtins
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.issue_planning_prompt import (  # noqa: E402
    PlanningOutputExpectation,
    SynthesizedPlanningPrompt,
)
from spec_dock_runtime.application.ports import IssuePlanningDependencies  # noqa: E402
from spec_dock_runtime.cli.bootstrap import _Clock, _IssuePlanningGateway  # noqa: E402
from spec_dock_runtime.domain import issue_planning_contracts  # noqa: E402
from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    OracleAuthoringZipSnapshot,
    PlanningInvocationResult,
    PlanningSourceEvidence,
)
from spec_dock_runtime.infra import (  # noqa: E402
    issue_planning_chatgpt,
    issue_planning_oracle_artifact,
)
from spec_dock_runtime.infra.contracts import StoredMetaRecord  # noqa: E402

PLANNING_DEPENDENCIES = IssuePlanningDependencies(clock=_Clock(), gateway=_IssuePlanningGateway())


def test_session_ids_are_oracle_0161_normalizer_fixed_points(
    monkeypatch,
) -> None:
    monkeypatch.setattr(issue_planning_chatgpt.secrets, "token_hex", lambda _size: "0123abcd")

    for role in ("planner", "semantic_revision", "reviewer"):
        session_id = issue_planning_chatgpt._new_session_id(role, _source_evidence())
        words = session_id.split("-")

        assert _oracle_0161_normalize_slug(session_id) == session_id
        assert "_" not in session_id
        assert 3 <= len(words) <= 5
        assert all(re.fullmatch(r"[a-z0-9]{1,10}", word) for word in words)


@pytest.mark.parametrize("role", ["planner", "semantic_revision"])
def test_path_oracle_direct_argv_environment_and_planner_snapshot(
    monkeypatch,
    tmp_path: Path,
    role: str,
) -> None:
    executable = _fake_executable(tmp_path, symlink=True)
    calls: list[tuple[list[str], dict[str, str], bool, object, bool, bool]] = []

    def fake_run(argv, **kwargs):
        calls.append(
            (
                list(argv),
                dict(kwargs["env"]),
                kwargs["shell"],
                kwargs["stdin"],
                kwargs["capture_output"],
                kwargs["check"],
            )
        )
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
    result = _invoke(tmp_path, role=role, prompt='literal $(touch nope); "quoted"')

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.authoring_zip is not None
    assert result.review_json is None
    submit_calls = [call for call in calls if "--prompt" in call[0]]
    assert len(submit_calls) == 1
    argv, child_env, shell, stdin, capture_output, check = submit_calls[0]
    assert Path(argv[0]) == executable.resolve()
    assert shell is False
    assert stdin is subprocess.DEVNULL
    assert capture_output is True
    assert check is False
    assert [call[0][1:] for call in calls[:3]] == [
        ["--version"],
        ["--help"],
        ["session", "--help"],
    ]
    assert all(
        shell is False
        and stdin is subprocess.DEVNULL
        and capture_output is True
        and check is False
        for _, _, shell, stdin, capture_output, check in calls
    )
    assert child_env["PATH"] == os.environ["PATH"]
    assert child_env["LANG"] == "ja_JP.UTF-8"
    assert "SPECDOCK_ORACLE_REMOTE_CHROME" not in child_env
    assert "OPENAI_API_KEY" not in child_env
    assert "AZURE_OPENAI_API_KEY" not in child_env
    assert "SPECDOCK_CHATGPT_COMMAND" not in child_env
    serialized = str(result.to_dict())
    assert "sessions" not in serialized
    assert "oracle-home" not in serialized
    assert result.authoring_zip.zip_bytes not in repr(result).encode()
    assert constructor_calls
    assert all("transient_payload" not in kwargs for kwargs in constructor_calls)
    _assert_managed_chrome_argv(argv)


def test_reviewer_returns_typed_closed_json_without_private_transcript(
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
    _assert_managed_chrome_argv(next(argv for argv in calls if "--prompt" in argv))


def test_missing_managed_chrome_contract_starts_no_oracle(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[object] = []
    monkeypatch.delenv("SPECDOCK_ORACLE_REMOTE_CHROME", raising=False)
    monkeypatch.setenv("ORACLE_HOME_DIR", str(tmp_path / "oracle-home"))
    monkeypatch.setattr(
        issue_planning_chatgpt.subprocess,
        "run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")
    assert calls == []
    assert not (tmp_path / "oracle-home" / "sessions").exists()


@pytest.mark.parametrize(
    "value",
    [
        "",
        "http://127.0.0.1:9223",
        "127.0.0.1",
        "127.0.0.1:0",
        "127.0.0.1:65536",
        "127.0.0.1:not-a-port",
        "0.0.0.0:9223",
        "user@127.0.0.1:9223",
        "127.0.0.1:9223/path",
        "127.0.0.1:9223 ",
        "127.0.0.1:9223#fragment",
    ],
)
def test_invalid_managed_chrome_contract_starts_no_oracle(
    monkeypatch,
    tmp_path: Path,
    value: str,
) -> None:
    calls: list[object] = []
    monkeypatch.setenv("SPECDOCK_ORACLE_REMOTE_CHROME", value)
    monkeypatch.setenv("ORACLE_HOME_DIR", str(tmp_path / "oracle-home"))
    monkeypatch.setattr(
        issue_planning_chatgpt.subprocess,
        "run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")
    assert calls == []
    assert not (tmp_path / "oracle-home" / "sessions").exists()


@pytest.mark.parametrize(
    ("failure", "status", "payload"),
    [
        ("connection-refused", 200, b"{}"),
        ("non-200", 503, b"{}"),
        ("malformed-json", 200, b"{"),
        ("non-object-json", 200, b"[]"),
        ("missing-websocket-url", 200, b"{}"),
        (
            "wrong-host",
            200,
            b'{"webSocketDebuggerUrl":"ws://192.0.2.1:9223/devtools/browser/fake"}',
        ),
        (
            "wrong-port",
            200,
            b'{"webSocketDebuggerUrl":"ws://127.0.0.1:9224/devtools/browser/fake"}',
        ),
    ],
)
def test_unreachable_or_non_cdp_managed_chrome_submits_no_prompt(
    monkeypatch,
    tmp_path: Path,
    failure: str,
    status: int,
    payload: bytes,
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
        pytest.fail("prompt must not be submitted")

    _patch_runtime(
        monkeypatch,
        tmp_path,
        executable,
        fake_run,
        patch_managed_chrome=False,
    )
    monkeypatch.setattr(
        issue_planning_chatgpt.http.client,
        "HTTPConnection",
        lambda *_args, **_kwargs: _FakeHttpConnection(
            status=status,
            payload=payload,
            fail_request=failure == "connection-refused",
        ),
    )

    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_unavailable")
    assert not any("--prompt" in argv for argv in calls)
    assert not (tmp_path / "oracle-home" / "sessions").exists()


@pytest.mark.parametrize(
    ("endpoint", "debugger_url"),
    [
        (
            ("localhost", 9223),
            b'{"webSocketDebuggerUrl":"ws://127.0.0.1:9223/devtools/browser/fake"}',
        ),
        (
            ("127.0.0.1", 9223),
            b'{"webSocketDebuggerUrl":"ws://localhost:9223/devtools/browser/fake"}',
        ),
    ],
)
def test_managed_chrome_preflight_accepts_loopback_host_alias(
    monkeypatch,
    endpoint: tuple[str, int],
    debugger_url: bytes,
) -> None:
    monkeypatch.setattr(
        issue_planning_chatgpt.http.client,
        "HTTPConnection",
        lambda *_args, **_kwargs: _FakeHttpConnection(
            status=200,
            payload=debugger_url,
            fail_request=False,
        ),
    )

    assert issue_planning_chatgpt._preflight_managed_chrome(endpoint) is True


def test_localhost_managed_chrome_contract_normalizes_to_numeric_loopback(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    preflight_endpoints: list[tuple[str, int]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setenv("SPECDOCK_ORACLE_REMOTE_CHROME", "localhost:9223")

    def preflight(endpoint: tuple[str, int]) -> bool:
        preflight_endpoints.append(endpoint)
        return True

    monkeypatch.setattr(issue_planning_chatgpt, "_preflight_managed_chrome", preflight)
    result = _invoke(tmp_path)

    assert result.status == "pass"
    assert preflight_endpoints == [("127.0.0.1", 9223)]
    _assert_managed_chrome_argv(next(argv for argv in calls if "--prompt" in argv))


@pytest.mark.parametrize(
    "missing_flag",
    [
        b"--model",
        b"--browser-model-strategy",
        b"--remote-chrome",
    ],
)
def test_required_model_and_remote_chrome_capabilities_are_preflighted(
    monkeypatch,
    tmp_path: Path,
    missing_flag: bytes,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help().replace(missing_flag, b""))
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        pytest.fail("prompt must not be submitted")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_capability_unsupported")
    assert not any("--prompt" in argv for argv in calls)


def test_user_model_config_cannot_override_product_selector(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    oracle_home = tmp_path / "oracle-home"
    oracle_home.mkdir()
    (oracle_home / "config.json").write_text(
        '{"model":"gpt-5.6-pro"}',
        encoding="utf-8",
    )

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert result.status == "pass"
    argv = next(argv for argv in calls if "--prompt" in argv)
    _assert_managed_chrome_argv(argv)
    assert "gpt-5.6-pro" not in argv
    assert "gpt-5.5-pro" not in argv


def test_no_personal_profile_or_wrapper_argument_is_emitted(
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
        _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    result = _invoke(tmp_path)

    assert result.status == "pass"
    argv = next(argv for argv in calls if "--prompt" in argv)
    forbidden = {
        "--browser-attach-running",
        "--browser-manual-login",
        "--browser-manual-login-profile-dir",
        "--browser-chrome-profile",
        "--browser-cookie-path",
        "--copy-profile",
        "--browser-port",
        "--browser-debug-port",
        "--browser-inline-cookies",
        "--browser-inline-cookies-file",
        "--write-output",
        "oracle-chatgpt",
        "chatgpt-use",
    }
    assert not forbidden.intersection(argv)


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
            attachment_paths=(),
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


@pytest.mark.parametrize(
    "preflight_failure",
    ["version", "unsupported-version", "root-help", "session-help"],
)
def test_unsupported_version_or_capability_submits_no_prompt(
    monkeypatch,
    tmp_path: Path,
    preflight_failure: str,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    recovery_calls: list[object] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            version = (
                b"0.16.2\n"
                if preflight_failure == "version"
                else b"0.17.0\n"
                if preflight_failure == "unsupported-version"
                else b"0.16.1\n"
            )
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
    monkeypatch.setattr(
        issue_planning_chatgpt,
        "_recover_same_session",
        lambda **kwargs: recovery_calls.append(kwargs),
    )
    result = _invoke(tmp_path)
    assert (result.status, result.reason) == ("blocked", "oracle_capability_unsupported")
    assert not any("--prompt" in argv for argv in calls)
    assert not any("--harvest" in argv for argv in calls)
    assert recovery_calls == []
    assert not (tmp_path / "oracle-home" / "sessions").exists()


@pytest.mark.parametrize(
    "preflight_failure",
    [
        "version-timeout",
        "version-nonzero",
        "root-help-timeout",
        "root-help-nonzero",
        "session-help-timeout",
        "session-help-nonzero",
    ],
)
def test_preflight_timeout_or_nonzero_submits_no_prompt_or_recovery(
    monkeypatch,
    tmp_path: Path,
    preflight_failure: str,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    recovery_calls: list[object] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        command = argv[1:]
        if command == ["--version"]:
            if preflight_failure == "version-timeout":
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
            return _completed(
                argv,
                stdout=b"0.16.1\n",
                returncode=1 if preflight_failure == "version-nonzero" else 0,
            )
        if command == ["--help"]:
            if preflight_failure == "root-help-timeout":
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
            return _completed(
                argv,
                stdout=_root_help(),
                returncode=1 if preflight_failure == "root-help-nonzero" else 0,
            )
        if command == ["session", "--help"]:
            if preflight_failure == "session-help-timeout":
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
            return _completed(
                argv,
                stdout=_session_help(),
                returncode=1 if preflight_failure == "session-help-nonzero" else 0,
            )
        pytest.fail("preflight failure must prevent prompt submission")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(
        issue_planning_chatgpt,
        "_recover_same_session",
        lambda **kwargs: recovery_calls.append(kwargs),
    )
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_capability_unsupported")
    assert not any("--prompt" in argv for argv in calls)
    assert not any("--harvest" in argv for argv in calls)
    assert recovery_calls == []
    assert not (tmp_path / "oracle-home" / "sessions").exists()


def test_preflight_receipt_records_content_free_capability_surface(
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
            return _completed(argv, stdout=_root_help() + b" private-help-output")
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help() + b" private-session-help-output")
        pytest.fail("preflight receipt must not submit a prompt")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    receipt = issue_planning_chatgpt._read_oracle_preflight_receipt(
        executable,
        child_env=issue_planning_chatgpt._sanitized_child_environment(),
        cwd=tmp_path,
    )

    assert receipt.version == "0.16.1"
    assert receipt.version_exit_code == 0
    assert receipt.root_help_exit_code == 0
    assert receipt.session_help_exit_code == 0
    assert receipt.missing_root_capabilities == ()
    assert receipt.missing_session_capabilities == ()
    assert receipt.supported_by_current_runtime is True
    assert "private-help-output" not in repr(receipt)
    assert "private-session-help-output" not in repr(receipt)
    assert calls == [
        [str(executable.resolve()), "--version"],
        [str(executable.resolve()), "--help"],
        [str(executable.resolve()), "session", "--help"],
    ]


def test_preflight_receipt_fail_closes_before_help_for_unsupported_version(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.17.0\n")
        pytest.fail("unsupported version must not probe help")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    receipt = issue_planning_chatgpt._read_oracle_preflight_receipt(
        executable,
        child_env=issue_planning_chatgpt._sanitized_child_environment(),
        cwd=tmp_path,
    )

    assert receipt.version == "0.17.0"
    assert receipt.version_exit_code == 0
    assert receipt.root_help_exit_code is None
    assert receipt.session_help_exit_code is None
    assert receipt.missing_root_capabilities == tuple(
        flag.decode("ascii") for flag in issue_planning_chatgpt._ROOT_CAPABILITIES
    )
    assert receipt.missing_session_capabilities == tuple(
        flag.decode("ascii") for flag in issue_planning_chatgpt._SESSION_CAPABILITIES
    )
    assert receipt.supported_by_current_runtime is False
    assert calls == [[str(executable.resolve()), "--version"]]


@pytest.mark.parametrize(
    "version_output",
    [
        b"0.16.1\nextra\n",
        b"/private/home/user/oracle\n",
        b"https://private.example/session/opaque\n",
        b"malformed version\n",
    ],
)
def test_preflight_receipt_rejects_non_token_version_output(
    monkeypatch,
    tmp_path: Path,
    version_output: bytes,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=version_output)
        pytest.fail("malformed version output must not probe help")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    receipt = issue_planning_chatgpt._read_oracle_preflight_receipt(
        executable,
        child_env=issue_planning_chatgpt._sanitized_child_environment(),
        cwd=tmp_path,
    )

    assert receipt.version is None
    assert receipt.supported_by_current_runtime is False
    assert version_output.decode().strip() not in repr(receipt)
    assert calls == [[str(executable.resolve()), "--version"]]


def test_malformed_version_output_submits_no_prompt_or_recovery(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    recovery_calls: list[object] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\nextra\n")
        pytest.fail("malformed version output must not probe help or submit")

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(
        issue_planning_chatgpt,
        "_recover_same_session",
        lambda **kwargs: recovery_calls.append(kwargs),
    )
    result = _invoke(tmp_path)

    assert (result.status, result.reason) == ("blocked", "oracle_capability_unsupported")
    assert calls == [[str(executable.resolve()), "--version"]]
    assert recovery_calls == []
    assert not (tmp_path / "oracle-home" / "sessions").exists()


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
    managed_chrome_preflights = 0

    def preflight_managed_chrome(_endpoint) -> bool:
        nonlocal managed_chrome_preflights
        managed_chrome_preflights += 1
        return True

    monkeypatch.setattr(
        issue_planning_chatgpt,
        "_preflight_managed_chrome",
        preflight_managed_chrome,
    )
    result = _invoke(tmp_path, timeout_seconds=0.1)
    assert result.status == "pass"
    assert managed_chrome_preflights == 1
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1
    prompt_argv = next(argv for argv in calls if "--prompt" in argv)
    harvest_argv = next(argv for argv in calls if "--harvest" in argv)
    _assert_exact_harvest_argv(
        harvest_argv,
        executable=executable,
        session_id=_session_id(prompt_argv),
    )


def test_recovery_polls_same_session_after_harvest_until_completed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    submitted: tuple[dict[str, str], list[str]] | None = None

    def fake_run(argv, **kwargs):
        nonlocal submitted
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            submitted = (kwargs["env"], list(argv))
            _write_metadata_only(kwargs["env"], argv, status="running")
            return _completed(argv, returncode=1)
        return _completed(argv, returncode=1)

    def complete_same_session(_seconds: float) -> None:
        assert submitted is not None
        _write_planner_session(
            *submitted,
            transcript_payloads=(
                b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\ncandidate ready\n",
            ),
        )

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt.time, "sleep", complete_same_session)
    result = _invoke(tmp_path, timeout_seconds=1.0)

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1
    prompt_argv = next(argv for argv in calls if "--prompt" in argv)
    harvest_argv = next(argv for argv in calls if "--harvest" in argv)
    _assert_exact_harvest_argv(
        harvest_argv,
        executable=executable,
        session_id=_session_id(prompt_argv),
    )


def test_recovery_polls_after_harvest_timeout_until_completed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    submitted: tuple[dict[str, str], list[str]] | None = None

    def fake_run(argv, **kwargs):
        nonlocal submitted
        calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return _completed(argv, stdout=b"0.16.1\n")
        if argv[1:] == ["--help"]:
            return _completed(argv, stdout=_root_help())
        if argv[1:] == ["session", "--help"]:
            return _completed(argv, stdout=_session_help())
        if "--prompt" in argv:
            submitted = (kwargs["env"], list(argv))
            _write_metadata_only(kwargs["env"], argv, status="running")
            return _completed(argv, returncode=1)
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    def complete_same_session(_seconds: float) -> None:
        assert submitted is not None
        _write_planner_session(
            *submitted,
            transcript_payloads=(
                b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\ncandidate ready\n",
            ),
        )

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt.time, "sleep", complete_same_session)
    result = _invoke(tmp_path, timeout_seconds=1.0)

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1
    prompt_argv = next(argv for argv in calls if "--prompt" in argv)
    harvest_argv = next(argv for argv in calls if "--harvest" in argv)
    _assert_exact_harvest_argv(
        harvest_argv,
        executable=executable,
        session_id=_session_id(prompt_argv),
    )


def test_recovery_poll_uses_one_monotonic_deadline(
    monkeypatch,
    tmp_path: Path,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    harvest_timeouts: list[float] = []
    clock = _FakeMonotonicClock()

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
        harvest_timeouts.append(kwargs["timeout"])
        clock.now += 0.6
        return _completed(argv, returncode=1)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(issue_planning_chatgpt.time, "sleep", clock.sleep)
    result = _invoke(tmp_path, timeout_seconds=1.0)

    assert (result.status, result.reason) == (
        "blocked",
        "oracle_session_recovery_required",
    )
    assert harvest_timeouts and 0 < harvest_timeouts[0] <= 1.0
    assert sum(clock.sleeps) <= 0.4
    assert clock.now <= 1.0
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1


@pytest.mark.parametrize("invalid_metadata", ["malformed", "wrong-session", "wrong-mode"])
def test_recovery_poll_rejects_invalid_metadata_without_further_wait(
    monkeypatch,
    tmp_path: Path,
    invalid_metadata: str,
) -> None:
    executable = _fake_executable(tmp_path)
    calls: list[list[str]] = []
    sleeps: list[float] = []

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
            return _completed(argv, returncode=1)
        session = _session_dir(kwargs["env"], argv[2])
        if invalid_metadata == "malformed":
            (session / "meta.json").write_bytes(b'{"id":')
        else:
            _write_metadata(
                session,
                "wrong-session" if invalid_metadata == "wrong-session" else argv[2],
                "running",
                [],
                mode="api" if invalid_metadata == "wrong-mode" else "browser",
            )
        return _completed(argv, returncode=1)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt.time, "sleep", sleeps.append)
    result = _invoke(tmp_path, timeout_seconds=1.0)

    assert (result.status, result.reason) == (
        "rejected",
        "oracle_artifact_rejected",
    )
    assert sleeps == []
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1
    assert result.authoring_zip is None
    assert result.review_json is None


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

    clock = _FakeMonotonicClock()
    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    monkeypatch.setattr(issue_planning_chatgpt.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(issue_planning_chatgpt.time, "sleep", clock.sleep)
    result = _invoke(tmp_path, timeout_seconds=0.1)
    assert (result.status, result.reason) == (
        "blocked",
        "oracle_session_recovery_required",
    )
    assert sum("--prompt" in argv for argv in calls) == 1
    assert sum("--harvest" in argv for argv in calls) == 1
    assert sum(clock.sleeps) <= 0.1
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


def test_direct_file_operands_preserve_order_and_do_not_materialize_pack(
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
        _write_planner_session(kwargs["env"], argv)
        return _completed(argv)

    _patch_runtime(monkeypatch, tmp_path, executable, fake_run)
    paths = (tmp_path / "attachments", tmp_path / "candidate.zip", tmp_path / "source.md")
    input_root = paths[0]

    def rejects_input_mutation(path: Path) -> bool:
        return path in paths or path.is_relative_to(input_root)

    original_mkdir = Path.mkdir
    original_write_bytes = Path.write_bytes
    original_write_text = Path.write_text
    original_unlink = Path.unlink
    original_rename = Path.rename
    original_replace = Path.replace
    original_iterdir = Path.iterdir
    original_glob = Path.glob
    original_rglob = Path.rglob
    original_resolve = Path.resolve
    original_stat = Path.stat
    original_read_bytes = Path.read_bytes
    original_open = Path.open
    original_builtin_open = builtins.open
    original_scandir = os.scandir
    original_listdir = os.listdir
    original_zip_file = zipfile.ZipFile
    original_sha256 = hashlib.sha256
    input_archive_calls = 0
    input_copy_calls = 0
    input_hash_calls = 0

    def guard(path: Path) -> None:
        if rejects_input_mutation(path):
            raise AssertionError("direct transport mutated or inspected an input path")

    def path_like(value: object) -> Path | None:
        if isinstance(value, (str, os.PathLike)):
            return Path(value)
        return None

    def guard_value(value: object) -> None:
        candidate = path_like(value)
        if candidate is not None:
            guard(candidate)

    def guarded_mkdir(path: Path, *args: object, **kwargs: object) -> None:
        guard(path)
        original_mkdir(path, *args, **kwargs)

    def guarded_write_bytes(path: Path, *args: object, **kwargs: object) -> int:
        guard(path)
        return original_write_bytes(path, *args, **kwargs)

    def guarded_write_text(path: Path, *args: object, **kwargs: object) -> int:
        guard(path)
        return original_write_text(path, *args, **kwargs)

    def guarded_unlink(path: Path, *args: object, **kwargs: object) -> None:
        guard(path)
        original_unlink(path, *args, **kwargs)

    def guarded_rename(path: Path, *args: object, **kwargs: object) -> Path:
        guard(path)
        return original_rename(path, *args, **kwargs)

    def guarded_replace(path: Path, *args: object, **kwargs: object) -> Path:
        guard(path)
        return original_replace(path, *args, **kwargs)

    def guarded_iterdir(path: Path, *args: object, **kwargs: object):
        guard(path)
        return original_iterdir(path, *args, **kwargs)

    def guarded_glob(path: Path, *args: object, **kwargs: object):
        guard(path)
        return original_glob(path, *args, **kwargs)

    def guarded_rglob(path: Path, *args: object, **kwargs: object):
        guard(path)
        return original_rglob(path, *args, **kwargs)

    def guarded_resolve(path: Path, *args: object, **kwargs: object) -> Path:
        guard(path)
        return original_resolve(path, *args, **kwargs)

    def guarded_stat(path: Path, *args: object, **kwargs: object):
        guard(path)
        return original_stat(path, *args, **kwargs)

    def guarded_read_bytes(path: Path, *args: object, **kwargs: object) -> bytes:
        guard(path)
        return original_read_bytes(path, *args, **kwargs)

    def guarded_open(path: Path, *args: object, **kwargs: object):
        guard(path)
        return original_open(path, *args, **kwargs)

    def guarded_builtin_open(file: object, *args: object, **kwargs: object):
        guard_value(file)
        return original_builtin_open(file, *args, **kwargs)

    def guarded_scandir(path: object = "."):
        guard_value(path)
        return original_scandir(path)

    def guarded_listdir(path: object = ".") -> list[str]:
        guard_value(path)
        return original_listdir(path)

    def guarded_copy_operation(*args: object, **kwargs: object):
        nonlocal input_copy_calls
        if any(
            (candidate := path_like(value)) is not None
            and rejects_input_mutation(candidate)
            for value in args[:2]
        ):
            input_copy_calls += 1
            raise AssertionError("direct transport copied an input path")
        return kwargs.pop("_original")(  # type: ignore[no-any-return]
            *args,
            **kwargs,
        )

    def guarded_copyfileobj(*args: object, **kwargs: object):
        return original_copyfileobj(*args, **kwargs)

    def guarded_zip_file(file: object, *args: object, **kwargs: object):
        nonlocal input_archive_calls
        candidate = path_like(file)
        if candidate is not None and rejects_input_mutation(candidate):
            input_archive_calls += 1
            raise AssertionError("direct transport archived an input path")
        return original_zip_file(file, *args, **kwargs)

    def guarded_sha256(*args: object, **kwargs: object):
        nonlocal input_hash_calls
        input_hash_calls += 1
        raise AssertionError("direct transport hashed an input path")

    def artifact_without_hash(kind: str, path: Path) -> dict[str, object]:
        contents = original_read_bytes(path)
        return {
            "kind": kind,
            "path": str(path),
            "sizeBytes": len(contents),
            "sha256": original_sha256(contents).hexdigest(),
            "validation": {"type": "zip" if kind == "file" else "generic", "ok": True},
        }

    monkeypatch.setattr(Path, "mkdir", guarded_mkdir)
    monkeypatch.setattr(Path, "write_bytes", guarded_write_bytes)
    monkeypatch.setattr(Path, "write_text", guarded_write_text)
    monkeypatch.setattr(Path, "unlink", guarded_unlink)
    monkeypatch.setattr(Path, "rename", guarded_rename)
    monkeypatch.setattr(Path, "replace", guarded_replace)
    monkeypatch.setattr(Path, "iterdir", guarded_iterdir)
    monkeypatch.setattr(Path, "glob", guarded_glob)
    monkeypatch.setattr(Path, "rglob", guarded_rglob)
    monkeypatch.setattr(Path, "resolve", guarded_resolve)
    monkeypatch.setattr(Path, "stat", guarded_stat)
    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    monkeypatch.setattr(Path, "open", guarded_open)
    monkeypatch.setattr(builtins, "open", guarded_builtin_open)
    monkeypatch.setattr(os, "scandir", guarded_scandir)
    monkeypatch.setattr(os, "listdir", guarded_listdir)
    original_copy = shutil.copy
    original_copy2 = shutil.copy2
    original_copyfile = shutil.copyfile
    original_move = shutil.move
    original_copyfileobj = shutil.copyfileobj
    monkeypatch.setattr(
        shutil,
        "copy",
        lambda *args, **kwargs: guarded_copy_operation(
            *args, _original=original_copy, **kwargs
        ),
    )
    monkeypatch.setattr(
        shutil,
        "copy2",
        lambda *args, **kwargs: guarded_copy_operation(
            *args, _original=original_copy2, **kwargs
        ),
    )
    monkeypatch.setattr(
        shutil,
        "copyfile",
        lambda *args, **kwargs: guarded_copy_operation(
            *args, _original=original_copyfile, **kwargs
        ),
    )
    monkeypatch.setattr(
        shutil,
        "move",
        lambda *args, **kwargs: guarded_copy_operation(
            *args, _original=original_move, **kwargs
        ),
    )
    monkeypatch.setattr(shutil, "copyfileobj", guarded_copyfileobj)
    monkeypatch.setattr(zipfile, "ZipFile", guarded_zip_file)
    monkeypatch.setattr(hashlib, "sha256", guarded_sha256)
    monkeypatch.setattr(
        issue_planning_oracle_artifact,
        "hashlib",
        SimpleNamespace(sha256=original_sha256),
    )
    monkeypatch.setattr(
        issue_planning_contracts,
        "hashlib",
        SimpleNamespace(sha256=original_sha256),
    )
    monkeypatch.setattr(sys.modules[__name__], "_artifact", artifact_without_hash)

    synthesized = SynthesizedPlanningPrompt(
        role="planner",
        prompt="fixed prompt",
        attachment_paths=paths,
        output_expectation=_authoring_expectation(),
    )
    result = issue_planning_chatgpt.invoke_issue_planning_chatgpt(
        repo_root=tmp_path,
        role="planner",
        source_evidence=_source_evidence(),
        synthesized=synthesized,
    )

    assert result.status == "pass"
    submit = next(argv for argv in calls if "--prompt" in argv)
    assert [Path(submit[index + 1]) for index, value in enumerate(submit) if value == "--file"] == list(paths)
    assert len([value for value in submit if value == "--file"]) == len(paths)
    assert not any("prompt-pack" in str(path) for path in tmp_path.iterdir())
    assert input_archive_calls == 0
    assert input_copy_calls == 0
    assert input_hash_calls == 0


def test_s04_direct_transport_accepts_path_only_synthesized_input() -> None:
    synthesized = SynthesizedPlanningPrompt(
        role="planner",
        prompt="fixed prompt",
        attachment_paths=(Path("attachments"), Path("spec-dock/requirement.md")),
        output_expectation=_authoring_expectation(),
    )

    assert synthesized.attachment_paths == (
        Path("attachments"),
        Path("spec-dock/requirement.md"),
    )


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
        transcript_payloads=(b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\n" + answer + b"\n",),
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
            b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\ncandidate ready\n",
            b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\ncandidate ready\n",
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
        transcript_payloads=(b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\ncandidate ready\n",),
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
        dependencies=PLANNING_DEPENDENCIES,
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


def _patch_runtime(
    monkeypatch,
    tmp_path: Path,
    executable: Path,
    fake_run,
    *,
    patch_managed_chrome: bool = True,
) -> None:
    monkeypatch.setattr(issue_planning_chatgpt.shutil, "which", lambda _name: str(executable))
    monkeypatch.setattr(issue_planning_chatgpt.subprocess, "run", fake_run)
    monkeypatch.setenv("ORACLE_HOME_DIR", str(tmp_path / "oracle-home"))
    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    monkeypatch.setenv("OPENAI_API_KEY", "private")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "private")
    monkeypatch.setenv("SPECDOCK_CHATGPT_COMMAND", "private-wrapper")
    monkeypatch.setenv("SPECDOCK_ORACLE_REMOTE_CHROME", "127.0.0.1:9223")
    if patch_managed_chrome:
        monkeypatch.setattr(
            issue_planning_chatgpt,
            "_preflight_managed_chrome",
            lambda _endpoint: True,
        )


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
            attachment_paths=(tmp_path / "attachments", tmp_path / "source.md"),
            output_expectation=(_review_expectation() if role == "reviewer" else _authoring_expectation()),
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
    return (
        b"--engine --file --slug --wait --prompt --browser-attachments "
        b"--model --browser-model-strategy --remote-chrome --browser-no-cookie-sync"
    )


def _assert_managed_chrome_argv(argv: list[str]) -> None:
    assert argv.count("--engine") == 1
    assert argv[argv.index("--engine") + 1] == "browser"
    assert argv.count("--model") == 1
    assert argv[argv.index("--model") + 1] == "Pro"
    assert argv.count("--browser-model-strategy") == 1
    assert argv[argv.index("--browser-model-strategy") + 1] == "select"
    assert argv.count("--remote-chrome") == 1
    assert argv[argv.index("--remote-chrome") + 1] == "127.0.0.1:9223"
    assert argv.count("--browser-no-cookie-sync") == 1
    assert argv.count("--wait") == 1
    assert argv.count("--browser-attachments") == 1
    assert argv[argv.index("--browser-attachments") + 1] == "always"
    for singleton in ("--prompt", "--slug"):
        assert argv.count(singleton) == 1
    assert argv.count("--file") == 2
    assert [Path(argv[index + 1]).name for index, value in enumerate(argv) if value == "--file"] == [
        "attachments",
        "source.md",
    ]


def _assert_exact_harvest_argv(
    argv: list[str],
    *,
    executable: Path,
    session_id: str,
) -> None:
    assert argv == [
        str(executable.resolve()),
        "session",
        session_id,
        "--harvest",
        "--no-recover",
    ]


class _FakeHttpResponse:
    def __init__(self, *, status: int, payload: bytes) -> None:
        self.status = status
        self._payload = payload

    def read(self, _limit: int) -> bytes:
        return self._payload


class _FakeHttpConnection:
    def __init__(
        self,
        *,
        status: int,
        payload: bytes,
        fail_request: bool,
    ) -> None:
        self._response = _FakeHttpResponse(status=status, payload=payload)
        self._fail_request = fail_request

    def request(self, *_args, **_kwargs) -> None:
        if self._fail_request:
            raise ConnectionRefusedError

    def getresponse(self) -> _FakeHttpResponse:
        return self._response

    def close(self) -> None:
        return


class _FakeMonotonicClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def _session_help() -> bytes:
    return b"--harvest --no-recover"


def _session_dir(env: dict[str, str], session_id: str) -> Path:
    return Path(env["ORACLE_HOME_DIR"]) / "sessions" / session_id


def _session_id(argv: list[str]) -> str:
    return argv[argv.index("--slug") + 1]


def _oracle_0161_normalize_slug(value: str) -> str:
    words = [word[:10] for word in re.findall(r"[a-z0-9]+", value.lower())[:5]]
    if not 3 <= len(words) <= 5:
        raise ValueError("Oracle custom slug must contain 3 to 5 words")
    return "-".join(words)


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
    resolved_id = session_id or _oracle_0161_normalize_slug(_session_id(argv))
    session = _session_dir(env, resolved_id)
    artifact = session / "artifacts" / (filename or "iss-00003-issue-planning-documents.zip")
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
        onboarding_companion_path=("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"),
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
    session_id = _oracle_0161_normalize_slug(_session_id(argv))
    session = _session_dir(env, session_id)
    transcript = session / "artifacts" / "transcript.md"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_bytes(b"# Oracle Browser Transcript\n## Prompt\nprivate prompt\n## Answer\n" + answer + b"\n")
    _write_metadata(session, session_id, "completed", [_artifact("transcript", transcript)])


def _write_metadata_only(env: dict[str, str], argv: list[str], *, status: str) -> None:
    session_id = _oracle_0161_normalize_slug(_session_id(argv))
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
