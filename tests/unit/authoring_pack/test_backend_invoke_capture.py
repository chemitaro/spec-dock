from pathlib import Path
import subprocess
import sys

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
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
    assert captured["argv"][0] == "/fixed/wrapper"
    assert captured["kwargs"]["cwd"] == str(tmp_path.resolve())
    assert "shell" not in captured["kwargs"]
    assert "payload" not in str(result.to_dict())


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
