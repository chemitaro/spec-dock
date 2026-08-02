from pathlib import Path
import shlex
import subprocess
import sys

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.authoring_pack import backend_invoke  # noqa: E402
from spec_dock_runtime.domain.authoring_pack.backend_invoke_contract import BackendInvokeRequest  # noqa: E402


def test_capture_entrypoint_uses_direct_argv_verified_cwd_and_keeps_streams_transient(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout=b"payload", stderr=b"diagnostic")

    monkeypatch.setattr(backend_invoke, "validate_prompt_pack", lambda path: _valid_pack(path))
    monkeypatch.setattr(backend_invoke, "_unsafe_output_blockers", lambda path: ())
    monkeypatch.setattr(backend_invoke, "_write_summary", lambda *args: None)
    monkeypatch.setattr(backend_invoke.subprocess, "run", fake_run)
    invoke = backend_invoke.invoke_backend_with_capture
    result, streams = invoke(
        BackendInvokeRequest(
            prompt_pack=tmp_path / "pack",
            output_dir=tmp_path / "output",
            backend_command="/fixed/wrapper",
            working_dir=tmp_path,
        ),
        env={},
    )
    assert result.status == "pass"
    assert streams.stdout == b"payload"
    assert streams.stderr == b"diagnostic"
    captured_argv = captured["argv"]
    captured_kwargs = captured["kwargs"]
    assert isinstance(captured_argv, list)
    assert isinstance(captured_kwargs, dict)
    assert captured_argv[0] == "/fixed/wrapper"
    assert captured_kwargs["cwd"] == str(tmp_path.resolve())
    assert "shell" not in captured_kwargs
    assert "payload" not in str(result.to_dict())


def test_capture_entrypoint_preserves_write_output_as_direct_redacted_argv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured_argv: list[str] | None = None
    captured_kwargs: dict[str, object] | None = None
    final_output = tmp_path / "private output" / "final-assistant-message.txt"

    def fake_run(argv, **kwargs):
        nonlocal captured_argv, captured_kwargs
        captured_argv = argv
        captured_kwargs = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout=b"diagnostic", stderr=b"sentinel")

    monkeypatch.setattr(backend_invoke, "validate_prompt_pack", lambda path: _valid_pack(path))
    monkeypatch.setattr(backend_invoke, "_unsafe_output_blockers", lambda path: ())
    monkeypatch.setattr(backend_invoke, "_write_summary", lambda *args: None)
    monkeypatch.setattr(backend_invoke.subprocess, "run", fake_run)
    result, streams = backend_invoke.invoke_backend_with_capture(
        BackendInvokeRequest(
            prompt_pack=tmp_path / "pack",
            output_dir=tmp_path / "output",
            backend_command=shlex.join(("/fixed/wrapper", "--write-output", str(final_output))),
            working_dir=tmp_path,
        ),
        env={},
    )

    assert captured_argv is not None
    assert captured_argv[:3] == ["/fixed/wrapper", "--write-output", str(final_output)]
    assert captured_kwargs is not None
    assert "shell" not in captured_kwargs
    assert streams.stdout == b"diagnostic"
    assert streams.stderr == b"sentinel"
    assert str(final_output) not in str(result.to_dict())


def _valid_pack(path: Path):
    from spec_dock_runtime.domain.authoring_pack.backend_invoke_contract import PromptPackValidation

    return PromptPackValidation(
        status="pass",
        prompt_pack=path,
        blockers=(),
        evidence_mode="github-synced",
        source_manifest_hash="a" * 64,
        github_sync="verified",
        sync_state="synced",
    )
