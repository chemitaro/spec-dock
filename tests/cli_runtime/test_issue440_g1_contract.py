"""Public read contracts of the external CLI in canonical mode: read-only leaves, text rendering, help.

Replaces the schema-3 tests of tests/cli_runtime/test_issue413_contract.py (iss-00440).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.legacy_contracts_g1 import chain_world, raw, select_record

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    return chain_world(tmp_path, monkeypatch, capsys)


def test_scope_read_help_explains_current_metadata_and_unobserved_github_state(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for leaf in ("list", "show"):
        assert main(["scope", leaf, "--help"]) == 0
        help_text = capsys.readouterr().out
        # 0.5.0: the reads describe the GitHub structure snapshot instead of current .meta.json metadata.
        assert "GitHub structure snapshot" in help_text and "Current metadata" not in help_text
        assert "cached state" not in help_text and "specdock.cli/v2" in help_text


def test_unconnected_directory_platform_returns_a_public_failure_before_writes(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    before = tree_digest(world.main)
    # A missing POSIX adapter still fails closed on an otherwise supported OS.
    monkeypatch.setattr("spec_dock.runtime.infra.json_store.os", SimpleNamespace(name="unavailable"))
    code, out, err = raw(world, "scope", "show", "init-00001", "--json")
    assert code == 5
    result = json.loads(out)
    assert result["status"] == "failed" and result["error"]["code"] == "LOCAL_IO_FAILED"
    assert result["effects"] == []
    assert "directory adapter" in result["error"]["message"]
    assert "not connected" in result["error"]["message"]
    assert err == "" and tree_digest(world.main) == before
    assert not (world.main / "spec-dock/.agent").exists() and not (world.main / ".git/spec-dock").exists()


def test_scope_read_dry_run_exposes_a_valid_preview_without_writes(world: CanonicalWorld) -> None:
    before = tree_digest(world.main)
    code, result = world.run("scope", "show", "init-00001", "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned"
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert result["effects"] == [] and tree_digest(world.main) == before
    assert not (world.main / "spec-dock/.agent").exists() and not (world.main / ".git/spec-dock").exists()
    assert world.fake().writes() == []


def test_scope_text_read_displays_the_target_authority_and_path_without_changing_files(
    world: CanonicalWorld,
) -> None:
    assert world.run("scope", "show", "init-00001")[0] == 0  # the first read saves the structure snapshot
    before = tree_digest(world.main)
    code, out, err = raw(world, "scope", "show", "init-00001")
    assert code == 0, out + err
    for value in ("init-00001", "plan", "github", "spec-dock/initiatives/00000-00999/init-00001"):
        assert value in out, out
    assert err == "" and tree_digest(world.main) == before
    assert not (world.main / ".git/spec-dock").exists() and not (world.main / "spec-dock/.agent").exists()


def test_active_text_read_displays_empty_or_selected_direct_and_current_branch(world: CanonicalWorld) -> None:
    for selected in (False, True):
        if selected:
            select_record(world, "init-00001", 1)
        assert world.run("active", "show")[0] == 0
        before = tree_digest(world.main)
        code, out, err = raw(world, "active", "show")
        assert code == 0, out + err
        assert ("selected" if selected else "empty") in out
        if selected:
            assert "init-00001" in out and "gh:example/repo#1" in out
        assert "main" in out and err == ""
        assert tree_digest(world.main) == before and not (world.main / ".git/spec-dock").exists()


def test_every_public_leaf_help_describes_the_v2_envelope_without_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.cli.catalog import LEAF_PATHS

    assert len(LEAF_PATHS) == 53  # 0.5.0 removed `workspace migrate` and `workbench copy`
    for leaf in LEAF_PATHS:
        assert main(["--project", str(tmp_path / "missing"), "help", *leaf.split(), "--json"]) == 0
        output = capsys.readouterr()
        result = json.loads(output.out)
        assert result["schema_version"] == "specdock.cli/v2" and result["effects"] == [] and output.err == ""
        help_text = result["data"]["text"]
        assert "specdock.cli/v2" in help_text and "specdock.cli/v1" not in help_text, leaf
    assert list(tmp_path.iterdir()) == []


def test_project_root_with_crlf_is_not_normalized(world: CanonicalWorld, tmp_path: Path) -> None:
    from tests.support.canonical_repo import add_worktree

    # `canonical link` stops (CANONICAL_NOT_LINKED) at a path with CR/LF, so the odd root is a linked worktree
    # read by a leaf that needs no link; the root must still be used exactly as given.
    odd = add_worktree(world.main, tmp_path / "consumer\r\nname", "odd")
    assert "\r\n" in str(odd)
    code, result = world.run("dependency", "list", "init-00001", checkout=odd)
    assert code == 0, result
    assert result["data"]["result"]["scope_id"] == "init-00001"


def test_active_show_empty_is_read_only_and_does_not_create_state(world: CanonicalWorld) -> None:
    code, result = world.run("active", "show")
    assert code == 0, result
    data = result["data"]
    assert data["kind"] == "active"
    assert data["selection"]["status"] == "empty"
    assert data["selection"]["scope_id"] is None
    assert data["ancestors"] == []
    assert not (world.main / "spec-dock/.agent").exists()
    assert not (world.main / ".git/spec-dock").exists()


def test_dynamic_scope_uses_direct_record_and_keeps_it_stale_when_scope_disappears(world: CanonicalWorld) -> None:
    path = select_record(world, "iss-00003", 3, branch="selected-branch")
    before = path.read_bytes()
    code, result = world.run("scope", "show", "@current")
    assert code == 0, result
    assert result["data"]["result"]["scope"]["id"] == "iss-00003"

    # The record now names a Scope that is not in the GitHub structure: an incomplete tree, never an empty selection.
    payload = json.loads(before)
    path.write_text(json.dumps(dict(payload, scope_id="iss-00009", github_ref="gh:example/repo#9")))
    vanished = path.read_bytes()
    code, result = world.run("scope", "show", "@current")
    assert code != 0, result
    assert result["effects"] == []
    assert path.read_bytes() == vanished
