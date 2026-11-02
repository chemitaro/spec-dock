"""`workspace validate` (and doctor on an empty catalog) on a canonical schema-4 checkout (iss-00440, G4).

Replaces the mode-independent tests of tests/cli_runtime/test_issue413_workspace_validate.py and
tests/cli_runtime/test_workspace_diagnostics_commands_vnext.py, which ran on a schema-3 workspace. The `--ci`
variants were removed with `workspace validate --ci` in 0.5.0.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.scope("epic", 2, "Core", parent=1)
    world.scope("issue", 3, "Leaf", parent=2)
    return world


def untouched(root: Path) -> tuple[str, str]:
    return tree_digest(root), git(root, "status", "--porcelain", "--ignored")


def test_empty_workspace_is_valid_unless_nodes_are_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    before = untouched(world.main)
    code, valid = world.run("workspace", "validate")
    assert code == 0, valid
    assert valid["data"]["result"]["valid"] is True
    assert valid["data"]["result"]["node_count"] == 0 and valid["data"]["result"]["findings"] == []
    assert valid["effects"] == []
    code, required = world.run("workspace", "validate", "--require-nodes")
    assert code == 7
    assert required["data"]["result"]["valid"] is False and required["data"]["result"]["node_count"] == 0
    assert [item["code"] for item in required["data"]["result"]["findings"]] == ["NODES_REQUIRED"]
    assert required["effects"] == []
    code, doctor = world.run("workspace", "doctor")
    assert code == 0, doctor
    assert doctor["data"]["kind"] == "diagnostic" and doctor["effects"] == []
    assert untouched(world.main) == before
    assert not (world.main / ".git/spec-dock").exists() and not (world.main / "spec-dock/.agent").exists()
    assert world.fake().writes() == []


def test_structural_validation_ignores_corrupt_execution_and_legacy_state(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = world.main / "spec-dock/.agent/work-target"
    state.mkdir(parents=True)
    (state / ("target-" + "a" * 32 + ".json")).write_bytes(b"private runtime body")
    legacy = world.main / ".git/spec-dock/control"
    legacy.mkdir(parents=True)
    (legacy / "control.json").write_bytes(b"private legacy body")

    def unexpected(*_args: object, **_kwargs: object) -> object:
        pytest.fail("structure validation must not inspect direct execution or legacy state, or take a Start lock")

    monkeypatch.setattr("spec_dock.runtime.infra.work_target_store.WorkTargetStore.read", unexpected)
    monkeypatch.setattr("spec_dock.runtime.infra.legacy_reader.inspect_legacy_files", unexpected)
    monkeypatch.setattr("spec_dock.runtime.infra.start_lock.StartLock.__enter__", unexpected)
    before = untouched(world.main)
    code, payload = world.run("workspace", "validate")
    assert code == 0, payload
    assert payload["data"]["result"]["valid"] is True and payload["effects"] == []
    assert "private" not in str(payload)
    assert untouched(world.main) == before


def test_validation_preview_is_read_only_and_does_not_reserve_any_work(world: CanonicalWorld) -> None:
    before = untouched(world.main)
    code, payload = world.run("workspace", "validate", "--dry-run")
    assert code == 0, payload
    assert payload["status"] == "planned" and payload["data"]["result"]["can_apply"] is True
    assert payload["data"]["result"]["blockers"] == [] and payload["effects"] == []
    assert untouched(world.main) == before
    assert world.fake().writes() == []


@pytest.mark.parametrize("selected", [False, True])
def test_working_validation_checks_an_explicit_current_scope_expectation(world: CanonicalWorld, selected: bool) -> None:
    if selected:
        world.select("iss-00003", 3)
    before = untouched(world.main)
    code, payload = world.run("workspace", "validate", "--expect-current", "iss-00003")
    assert code == (0 if selected else 3), payload
    assert payload["effects"] == []
    assert untouched(world.main) == before
