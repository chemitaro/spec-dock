"""CUE Scopes in a test catalog and stand-ins for the `cue` binary (iss-00473 tests).

    fake = install_fake_cue(tmp_path, monkeypatch, version="cue version v0.17.1")   # a recording stand-in
    hide_cue(monkeypatch)                                                             # no `cue` on PATH at all

The stand-in records each argv as one JSON line; the real `cue` stays available unless a test hides it.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


@dataclass(frozen=True)
class FakeCue:
    directory: Path
    log: Path

    def calls(self) -> list[list[str]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]


def install_fake_cue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    version: str = "cue version v0.17.1",
    export_stdout: str = "{}",
    export_stderr: str = "",
    export_code: int = 0,
    sleep: float = 0.0,
    version_code: int = 0,
) -> FakeCue:
    """Put a `cue` stand-in first on PATH: `cue version` prints `version`; `cue export` prints the given output."""
    directory = tmp_path / "fake-cue-bin"
    directory.mkdir(exist_ok=True)
    log = directory / "calls.jsonl"
    script = directory / "cue"
    script.write_text(
        f"#!{sys.executable}\n"
        "import json, sys, time\n"
        f"open({str(log)!r}, 'a', encoding='utf-8').write(json.dumps(sys.argv[1:]) + '\\n')\n"
        f"time.sleep({sleep!r})\n"
        "if sys.argv[1:2] == ['version']:\n"
        f"    print({version!r}); sys.exit({version_code!r})\n"
        f"sys.stdout.write({export_stdout!r}); sys.stderr.write({export_stderr!r}); sys.exit({export_code!r})\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{directory}{os.pathsep}{os.environ.get('PATH', '')}")
    return FakeCue(directory, log)


def hide_cue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop every PATH entry that holds a `cue`, keeping the rest (git, the fake gh, the guards)."""
    entries = os.environ.get("PATH", "").split(os.pathsep)
    kept = [entry for entry in entries if not (entry and (Path(entry) / "cue").exists())]
    monkeypatch.setenv("PATH", os.pathsep.join(kept))
    assert shutil.which("cue") is None


ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "tests/fixtures/cue/v1/samples"
SKELETON = ROOT / "src/spec_dock/assets/spec_dock/design-system/explanation-skeleton.html"
SKELETON_MARKER = "<!-- spec-dock:explanation-skeleton -->"


def skeleton_explanation() -> str:
    return SKELETON.read_text(encoding="utf-8")


def written_explanation() -> str:
    """The shipped skeleton after its author removed the marker line."""
    return skeleton_explanation().replace(SKELETON_MARKER + "\n", "")


def place_sample(directory: Path, sample: str, *, explanation: str | None = None, report: bool = True) -> Path:
    """Make `directory` a CUE Scope holding one I-1 sample's three files, a written explanation and report.md."""
    directory.mkdir(parents=True, exist_ok=True)
    for name in ("requirement.cue", "design.cue", "plan.cue"):
        shutil.copyfile(SAMPLES / sample / name, directory / name)
    (directory / "explanation.html").write_text(
        written_explanation() if explanation is None else explanation, encoding="utf-8"
    )
    if report:
        (directory / "report.md").write_text("# report\n", encoding="utf-8")
    return directory


def sample_expectation(sample: str) -> dict[str, object]:
    return json.loads((SAMPLES / sample / "expected.json").read_text(encoding="utf-8"))


def sample_names() -> list[str]:
    return sorted(path.name for path in SAMPLES.iterdir() if path.is_dir())
