"""Read-only Scope projections and a title-only edit through the new CLI."""

from __future__ import annotations

import json
from pathlib import Path
import sys

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


def test_scope_list_show_and_edit_target_the_same_scope(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, epic, issue = _three_scopes(tmp_path)
    arguments = {"invocation_cwd": specdock_dir.parent, "engine_digest": "engine-a", "engine_version": "test"}
    listed = run_vnext(["scope", "list", "--kind", "issue", "--parent", epic.id, "--json"], **arguments)
    assert listed.exit_code == 0
    items = json.loads(listed.stdout)["data"]["items"]
    assert len(items) == 1 and items[0]["id"] == issue.id and items[0]["backend"] == "local"
    assert items[0]["path"].startswith("spec-dock/initiatives/")
    run_vnext(["active", "set", issue.id], **arguments)
    shown = run_vnext(["scope", "show", "@current", "--json"], **arguments)
    assert json.loads(shown.stdout)["data"]["item"]["id"] == issue.id
    document = issue.path / "requirement.md"
    before_document = document.read_bytes()
    preview = run_vnext(["scope", "edit", "@current", "--title", "Renamed", "--dry-run", "--json"], **arguments)
    assert json.loads(preview.stdout)["status"] == "planned"
    assert (
        json.loads(run_vnext(["scope", "show", issue.id, "--json"], **arguments).stdout)["data"]["item"]["title"]
        == "Issue"
    )
    edited = run_vnext(["scope", "edit", "@current", "--title", "Renamed", "--json"], **arguments)
    assert edited.exit_code == 0 and json.loads(edited.stdout)["data"]["changed"]
    assert document.read_bytes() == before_document
    shown_after = run_vnext(["scope", "show", issue.id, "--json"], **arguments)
    assert json.loads(shown_after.stdout)["data"]["item"]["title"] == "Renamed"
