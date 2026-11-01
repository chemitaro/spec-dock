"""The Issue plan template shows one step per line with status right after title and realizes (iss-00489 R-03)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree
from tests.support.cue import cue_executable

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets"
TEMPLATE = "spec-dock/templates/cue/issue/plan.cue"
PROVIDER = ASSETS / "spec_dock/templates/cue/issue/plan.cue"
# The bytes 0.4.0 shipped (c43aadd5b); a consumer holding them must be able to `installation update`.
PREVIOUS = ROOT / "tests/fixtures/issue489/issue-plan-cue-0.4.0.txt"
PREVIOUS_SHA256 = "08b4c2fd41459117329ac84713218c6bb0b22521ff6252388e3b4fe34d89d034"
STEP_EXAMPLE = re.compile(r'^\s*//\s*("S-01": \{.*\})\s*$', re.MULTILINE)


def _step_example() -> str:
    [line] = STEP_EXAMPLE.findall(PROVIDER.read_text(encoding="utf-8"))
    return line


def test_the_step_example_is_one_line_with_status_after_title_and_realizes() -> None:
    line = _step_example()
    keys = re.findall(r"\b([a-z]+):", line)
    assert keys[:3] == ["title", "realizes", "status"], keys
    assert "status は title と realizes のすぐ後" in PROVIDER.read_text(encoding="utf-8")


def test_the_step_example_meets_the_step_type(tmp_path: Path) -> None:
    probe = tmp_path / "probe.cue"
    probe.write_text(f"package spec\n\nexample: #Step & {{{_step_example().split(': ', 1)[1][1:-1]}}}\n", "utf-8")
    types = sorted(str(path) for path in (ROOT / "src/spec_dock/cue/v1").glob("*_type.cue"))
    types += [str(ROOT / "src/spec_dock/cue/v1/base.cue")]
    done = subprocess.run(
        [cue_executable(), "export", *types, str(probe), "-e", "example", "-t", "kind=issue"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["status"] == "todo"


def test_the_inventory_and_the_dogfood_copy_follow_and_accept_the_previous_bytes() -> None:
    entries = {
        item["path"]: item for item in json.loads((ASSETS / "static-inventory.json").read_text("utf-8"))["files"]
    }
    entry = entries[TEMPLATE]
    assert entry["sha256"] == hashlib.sha256(PROVIDER.read_bytes()).hexdigest()
    assert entry["known_old_sha256"] == [PREVIOUS_SHA256]
    assert hashlib.sha256(PREVIOUS.read_bytes()).hexdigest() == PREVIOUS_SHA256
    assert (ROOT / TEMPLATE).read_bytes() == PROVIDER.read_bytes()


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    output = capsys.readouterr()
    return code, json.loads(output.out)


def test_installation_update_replaces_the_previous_template(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    (target / TEMPLATE).write_bytes(PREVIOUS.read_bytes())
    backup = tmp_path / "backup"
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes"
    )
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    assert applied["data"]["result"]["changed_paths"] == [TEMPLATE]
    assert (target / TEMPLATE).read_bytes() == PROVIDER.read_bytes()
    assert (backup / "static" / TEMPLATE).read_bytes() == PREVIOUS.read_bytes()
