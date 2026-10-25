"""Schema-3 workspaces answer exactly as before canonical mode existed (AC-15, AC-428-16).

The expected outputs were recorded by running `collect` against the package source at be4810244,
the commit before this Issue, with the same fixture builder.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
from typing import Any

EXPECTED = Path(__file__).resolve().parents[1] / "fixtures/issue428/legacy-outputs.json"
LEGACY_DECLARATION = b'{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n'
LEGACY_SHIM = Path(__file__).resolve().parents[1] / "fixtures/issue413/legacy-shim.txt"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _cli(*argv: str) -> dict[str, Any]:
    from spec_dock.cli import main

    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main([*argv, "--json"])
    return {"exit_code": code, "result": json.loads(stdout.getvalue())}


def _schema_three_consumer(root: Path) -> Path:
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "--local", "maintenance.auto", "false")
    _git(root, "remote", "add", "origin", "https://github.com/example/repo.git")
    assert _cli("installation", "init", str(root), "--yes")["exit_code"] == 0
    (root / "spec-dock/workspace.json").write_bytes(LEGACY_DECLARATION)
    scope = root / "spec-dock/initiatives/init-00001-fixture"
    scope.mkdir(parents=True)
    metadata = {
        "schema_version": 3,
        "id": "init-00001",
        "type": "initiative",
        "title": "Fixture",
        "slug": "fixture",
        "parent_id": None,
        "initiative_id": None,
        "epic_id": None,
        "backend": "github",
        "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
        "lifecycle": None,
        "revision": 0,
        "depends_on": [],
        "created_at": "2026-09-30T00:00:00Z",
        "updated_at": "2026-09-30T00:00:00Z",
    }
    (scope / ".meta.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (scope / name).write_text("# Fixture\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    return root


def collect(work: Path) -> dict[str, Any]:
    """Run the representative schema-3 commands and return path-normalized results."""
    root = _schema_three_consumer(work / "consumer")
    outputs: dict[str, Any] = {}
    outputs["workspace validate"] = _cli("--project", str(root), "workspace", "validate")
    outputs["workspace validate --ci"] = _cli("--project", str(root), "workspace", "validate", "--ci")
    outputs["workspace doctor"] = _cli("--project", str(root), "workspace", "doctor")
    outputs["installation update --dry-run"] = _cli("installation", "update", "--target", str(root), "--dry-run")
    (root / "spec-dock/scripts/spec-dock").write_bytes(LEGACY_SHIM.read_bytes())
    outputs["installation update"] = _cli(
        "installation", "update", "--target", str(root), "--backup-dir", str(work / "backup"), "--yes"
    )
    outputs["declaration after update"] = (root / "spec-dock/workspace.json").read_text(encoding="utf-8")
    replacements = {str(work): "<WORK>", _git(root, "rev-parse", "HEAD"): "<HEAD>"}
    from spec_dock import __version__

    replacements[__version__] = "<VERSION>"
    text = json.dumps(outputs, sort_keys=True)
    for value, placeholder in replacements.items():
        text = text.replace(value, placeholder)
    return json.loads(text)


def test_schema_three_representative_commands_answer_as_before(tmp_path: Path) -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    actual = collect(tmp_path.resolve())
    assert actual == expected
    assert actual["declaration after update"] == LEGACY_DECLARATION.decode()
