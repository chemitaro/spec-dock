"""Read-only Scope projections and a title-only edit through the new CLI."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

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
    preview = run_vnext(
        ["scope", "edit", "@current", "--title", "Renamed", "--expect-current", issue.id, "--dry-run", "--json"],
        **arguments,
    )
    assert json.loads(preview.stdout)["status"] == "planned"
    assert (
        json.loads(run_vnext(["scope", "show", issue.id, "--json"], **arguments).stdout)["data"]["item"]["title"]
        == "Issue"
    )
    edited = run_vnext(
        ["scope", "edit", "@current", "--title", "Renamed", "--expect-current", issue.id, "--json"],
        **arguments,
    )
    assert edited.exit_code == 0 and json.loads(edited.stdout)["data"]["changed"]
    assert document.read_bytes() == before_document
    shown_after = run_vnext(["scope", "show", issue.id, "--json"], **arguments)
    assert json.loads(shown_after.stdout)["data"]["item"]["title"] == "Renamed"


def test_unexpected_failures_report_effect_uncertainty_by_command_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, _views, initiative, _epic, _issue = _three_scopes(tmp_path)
    arguments = {"invocation_cwd": specdock_dir.parent, "engine_digest": "engine-a", "engine_version": "test"}

    def fail_read(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("injected read failure")

    monkeypatch.setattr("spec_dock_runtime.cli.vnext_runtime.run_scope_query", fail_read)
    read = run_vnext(["scope", "list", "--json"], **arguments)
    assert read.exit_code == 1
    read_payload = json.loads(read.stdout)
    assert read_payload["status"] == "failed" and read_payload["effects"] == []

    def fail_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("injected write failure")

    monkeypatch.setattr("spec_dock_runtime.cli.vnext_runtime.run_scope_edit", fail_write)
    write = run_vnext(["scope", "edit", initiative.id, "--title", "New", "--json"], **arguments)
    assert write.exit_code == 6
    write_payload = json.loads(write.stdout)
    assert write_payload["status"] == "partial"
    assert write_payload["effects"][0]["status"] == "unknown"

    def fail_context(*_args: object, **_kwargs: object) -> None:
        raise OSError("injected context failure")

    with monkeypatch.context() as context_patch:
        context_patch.setattr("spec_dock_runtime.cli.vnext_runtime._context", fail_context)
        preflight = run_vnext(["scope", "edit", initiative.id, "--title", "New", "--json"], **arguments)
    assert preflight.exit_code == 5
    assert json.loads(preflight.stdout)["effects"] == []
