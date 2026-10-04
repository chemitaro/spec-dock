"""Linux/macOS contracts after retiring the Windows adapters (Issue #413)."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from spec_dock.cli import main
from spec_dock.runtime.domain.work_target import PhysicalIdentity

ROOT = Path(__file__).resolve().parents[2]


def test_physical_identity_contract_is_posix_only() -> None:
    schema = json.loads(
        (ROOT / "docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json").read_bytes()
    )["$defs"]["identity"]
    assert schema["properties"]["platform"] == {"const": "posix"}
    assert PhysicalIdentity.from_payload({"platform": "posix", "device": "123", "file_id": "456"}) == (
        PhysicalIdentity("posix", "123", "456")
    )
    with pytest.raises(ValueError, match="physical identity"):
        PhysicalIdentity.from_payload({
            "platform": "windows",
            "device": "123",
            "file_id": "00112233445566778899aabbccddeeff",
        })


def test_unsupported_business_stops_before_project_and_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("PATH", str(tmp_path / "no-executables"))
    assert main(["--project", str(tmp_path / "missing"), "work", "start", "iss-00413", "--base", "HEAD", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "UNSUPPORTED_PLATFORM"
    assert result["status"] == "failed" and result["effects"] == []
    assert output.err == "" and not tuple(tmp_path.iterdir())


def _unsupported_process(
    tmp_path: Path, arguments: list[str], *, utility: bool = False
) -> subprocess.CompletedProcess[str]:
    source = """
import builtins, json, sys
sys.path.insert(0, sys.argv[1])
original_import = builtins.__import__
utility = sys.argv[3] == 'utility'
def guarded_import(name, *args, **kwargs):
    if name == 'fcntl' or (utility and name.startswith((
        'spec_dock.runtime.application', 'spec_dock.runtime.commands', 'spec_dock.runtime.infra'
    ))):
        raise AssertionError('unexpected business/native import: ' + name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
from spec_dock.cli import main
sys.platform = 'win32'
raise SystemExit(main(json.loads(sys.argv[2])))
"""
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            source,
            str(ROOT / "src"),
            json.dumps(arguments),
            "utility" if utility else "business",
        ],
        cwd=tmp_path,
        env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )


@pytest.mark.parametrize(
    "arguments",
    [
        ["work", "start", "iss-00413", "--base", "HEAD"],
        ["installation", "init", "unused-target", "--yes"],
        ["workspace", "validate", "--ci"],
        ["workspace", "doctor", "--raw"],
    ],
)
def test_unsupported_real_entrypoint_reaches_guard_without_native_imports(tmp_path: Path, arguments: list[str]) -> None:
    completed = _unsupported_process(tmp_path, [*arguments, "--json"])
    assert completed.returncode == 3, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["error"]["code"] == "UNSUPPORTED_PLATFORM" and result["effects"] == []
    assert completed.stderr == "" and not tuple(tmp_path.iterdir())


@pytest.mark.parametrize("arguments", [["--help"], ["work", "start", "--help"], ["--version"], ["completion", "bash"]])
def test_unsupported_platform_keeps_utilities_context_free(tmp_path: Path, arguments: list[str]) -> None:
    completed = _unsupported_process(tmp_path, [*arguments, "--json"], utility=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["data"]["kind"] == "utility" and result["effects"] == []
    assert completed.stderr == "" and not tuple(tmp_path.iterdir())


def test_unsupported_platform_has_a_text_diagnostic(tmp_path: Path) -> None:
    completed = _unsupported_process(tmp_path, ["work", "start", "iss-00413", "--base", "HEAD"])
    assert completed.returncode == 3
    assert "UNSUPPORTED_PLATFORM" in completed.stderr
    assert completed.stdout == "spec-dock: failed (work start)\n"
    assert not tuple(tmp_path.iterdir())
