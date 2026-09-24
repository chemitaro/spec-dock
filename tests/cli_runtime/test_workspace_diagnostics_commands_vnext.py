"""Workspace validation and doctor leaves preserve read-only diagnostic outcomes."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_workspace_diagnostics_cli_reports_valid_and_required_nodes(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    control = cast("Path", common["common_dir"]) / "spec-dock" / "control" / "control.json"
    before = control.read_bytes()
    valid = run_vnext(
        ["workspace", "validate", "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4"
    )
    assert valid.exit_code == 0
    assert json.loads(valid.stdout)["data"]["valid"] is True
    required = run_vnext(
        ["workspace", "validate", "--require-nodes", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert required.exit_code == 7
    assert "nodes_required" in {item["code"] for item in json.loads(required.stdout)["data"]["findings"]}
    doctor = run_vnext(
        ["workspace", "doctor", "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4"
    )
    assert doctor.exit_code == 0
    assert control.read_bytes() == before
