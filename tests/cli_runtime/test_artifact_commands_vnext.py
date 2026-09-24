"""Artifact inventory leaves return identifiers without reading stored content."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def test_artifact_list_show_cli_return_only_catalog_metadata(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    catalog = repo / "spec-dock" / "artifacts"
    catalog.mkdir(exist_ok=True)
    (catalog / "20260925t000000z--source.bin").write_bytes(b"secret payload")
    listed = run_vnext(
        ["artifact", "list", "--scope", "@root", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert listed.exit_code == 0
    payload = json.loads(listed.stdout)
    assert payload["data"]["scope_id"] == "root"
    artifact_id = payload["data"]["items"][0]["artifact_id"]
    assert "secret payload" not in listed.stdout
    shown = run_vnext(
        ["artifact", "show", artifact_id, "--scope", "@root", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert shown.exit_code == 0
    assert json.loads(shown.stdout)["data"]["artifact_id"] == artifact_id
    assert "secret payload" not in shown.stdout
