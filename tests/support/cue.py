"""Evaluate CUE spec documents with the real `cue` binary, the way contract K1 of epic-00425 lays them out.

Tests that need `cue` fail instead of skipping when it is missing, so CI proves the type with the real tool.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

PINNED_CUE_VERSION = "v0.17.1"
SCOPE_FILES = ("requirement.cue", "design.cue", "plan.cue")
V1 = Path(__file__).resolve().parents[2] / "src/spec_dock/cue/v1"
_INSTALL = (
    f"`cue` {PINNED_CUE_VERSION} is required on PATH for the CUE spec type tests. Install it inside this worktree, "
    f'for example: GOBIN="$PWD/.workbench/bin" go install cuelang.org/go/cmd/cue@{PINNED_CUE_VERSION} '
    '&& PATH="$PWD/.workbench/bin:$PATH" uv run pytest'
)


def cue_executable() -> str:
    """The `cue` found on PATH; a missing one fails the calling test instead of skipping it."""
    found = shutil.which("cue")
    if found is None:
        pytest.fail(_INSTALL, pytrace=False)
    return found


@dataclass(frozen=True)
class Evaluation:
    returncode: int
    data: dict[str, Any] | None
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and self.data is not None

    @property
    def findings(self) -> dict[str, list[dict[str, str]]]:
        assert self.data is not None, self.stderr
        return self.data["findings"]

    def reported_rules(self) -> set[str]:
        """Rules whose finding list is not empty."""
        return {rule for rule, items in self.findings.items() if items}


def document(**fields: object) -> str:
    """One `package spec` file whose top-level fields are written as JSON, which CUE reads as is."""
    lines = ["package spec", ""]
    lines += [f"{json.dumps(name)}: {json.dumps(value, ensure_ascii=False)}" for name, value in fields.items()]
    return "\n".join(lines) + "\n"


def write_scope(directory: Path, requirement: str, design: str = "", plan: str = "") -> Path:
    """Write the three Scope files; an empty text becomes a file with only the package clause."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in zip(SCOPE_FILES, (requirement, design, plan), strict=True):
        (directory / name).write_text(text or "package spec\n", encoding="utf-8")
    return directory


def evaluate(scope: Path, kind: str | None, *, overlay: Path | None = None, schema: Path = V1) -> Evaluation:
    """`cue export --out json -t kind=<kind>` over the type, the optional repository type, then the Scope files.

    `kind=None` leaves the tag out, which SpecDock never does; tests use it to see that error.
    """
    command = [cue_executable(), "export", "--out", "json"]
    if kind is not None:
        command += ["-t", f"kind={kind}"]
    command += [str(path) for path in sorted(schema.glob("*.cue"))]
    if overlay is not None:
        command += [str(path) for path in sorted(overlay.glob("*.cue"))]
    command += [str(scope / name) for name in SCOPE_FILES]
    completed = subprocess.run(command, cwd=scope, capture_output=True, text=True, check=False, timeout=60)
    data = json.loads(completed.stdout) if completed.returncode == 0 else None
    return Evaluation(completed.returncode, data, completed.stderr)


def cue_string_body(text: str) -> str:
    """The text as the inside of a CUE double-quoted string (what replaces a marker placed between quotes)."""
    out: list[str] = []
    for character in text:
        if character == "\\":
            out.append("\\\\")
        elif character == '"':
            out.append('\\"')
        elif character == "\n":
            out.append("\\n")
        elif character == "\t":
            out.append("\\t")
        elif ord(character) < 0x20 or ord(character) == 0x7F:
            out.append(f"\\u{ord(character):04x}")
        else:
            out.append(character)
    return "".join(out)
