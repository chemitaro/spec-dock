"""Canonical `dependency` command contracts kept from the legacy-mode tests (iss-00440).

Replaces the common-contract tests of tests/cli_runtime/test_issue413_dependency.py, which stored `depends_on`
in schema-3 `.meta.json` files. Canonical edges are GitHub blocked-by relations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.scope("epic", 4, "spare", parent=1)
    return world


def _catalog(world: WriteWorld) -> str:
    return tree_digest(world.catalog)


def test_dependency_add_dry_run_plans_edges_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog(world)
    code, payload = world.run("dependency", "add", "--from", "epic-00002", "--to", "epic-00004", "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    data = payload["data"]["result"]
    assert data["can_apply"] is True and data["blockers"] == [] and data["changed"] is False
    assert payload["effects"] == [{"kind": "dependency-edge", "status": "planned", "target": "epic-00002->epic-00004"}]
    assert world.writes() == [] and world.changesets() == [] and _catalog(world) == before
    assert world.fake().issue(2).blocked_by == []


def test_dependency_duplicate_add_is_unchanged_with_an_unchanged_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(2, by=4))
    record_before = _catalog(world)
    code, payload = world.run("dependency", "add", "--from", "epic-00002", "--to", "epic-00004")
    assert (code, payload["status"]) == (0, "unchanged"), payload
    assert payload["data"]["result"]["changed"] is False
    assert payload["effects"] == [
        {"kind": "dependency-edge", "status": "unchanged", "target": "epic-00002->epic-00004"}
    ]
    assert world.writes() == [] and _catalog(world) == record_before


@pytest.mark.parametrize("guard", [("--expect-backend", "local"), ("--expect-current", "init-00001")])
def test_dependency_mutation_target_guards_refuse_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], guard: tuple[str, str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.select("iss-00003", 3)
    record = next((world.main / "spec-dock/.agent/work-target").iterdir())
    selected, before = record.read_bytes(), _catalog(world)
    code, payload = world.run("dependency", "add", "--from", "@epic", "--to", "epic-00004", *guard)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert world.writes() == [] and record.read_bytes() == selected and _catalog(world) == before
    code, payload = world.run("dependency", "add", "--from", "@epic", "--to", "epic-00004", "--expect-current", "@epic")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED"), payload
    code, payload = world.run(
        "dependency", "add", "--from", "@epic", "--to", "epic-00004", "--expect-current", "iss-00003"
    )
    assert code == 0, payload
    assert payload["effects"] == [
        {"kind": "dependency-edge", "status": "succeeded", "target": "epic-00002->epic-00004"}
    ]
    assert record.read_bytes() == selected


@pytest.mark.parametrize(
    "edge",
    [("epic-00002", "epic-00002"), ("iss-00003", "epic-00002"), ("epic-00002", "iss-00003")],
)
def test_dependency_add_rejects_self_and_ancestry_edges_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], edge: tuple[str, str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog(world)
    code, payload = world.run("dependency", "add", "--from", edge[0], "--to", edge[1])
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert world.writes() == [] and _catalog(world) == before


def test_dependency_add_rejects_an_inherited_wait_cycle_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.scope("issue", 5, "other leaf", parent=4)
    world.edit(lambda fake: fake.block(4, by=2))  # epic-00004 (and so iss-00005) waits for epic-00002
    code, payload = world.run("dependency", "add", "--from", "iss-00003", "--to", "iss-00005")
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    assert "CYCLE" in payload["error"]["message"].upper()
    assert world.writes() == []


def test_dependency_mutation_proceeds_while_start_exclusion_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    world = _world(tmp_path, monkeypatch, capsys)
    with StartLock(world.main / ".git", timeout=0):
        code, payload = world.run("dependency", "add", "--from", "epic-00002", "--to", "epic-00004")
    assert code == 0, payload
    assert payload["data"]["result"]["changed"] is True
    assert [item[1] for item in world.writes()] == ["repos/example/repo/issues/2/dependencies/blocked_by"]


@pytest.mark.parametrize("view", ["declared", "effective", None])
def test_dependency_text_view_distinguishes_declared_from_inherited_edges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], view: str | None
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(2, by=4))
    options = ["--view", view] if view else []
    assert main(["--project", str(world.main), "dependency", "list", "iss-00003", *options]) == 0
    output = capsys.readouterr()
    assert output.err == "" and "scope_id=iss-00003" in output.out
    if view == "declared":
        assert "declared=[]" in output.out and "effective=" not in output.out and "epic-00004" not in output.out
    elif view == "effective":
        assert 'effective=["epic-00004"]' in output.out and "declared=" not in output.out
    else:
        assert "declared=[]" in output.out and 'effective=["epic-00004"]' in output.out


@pytest.mark.parametrize(
    "command", [("scope", "list"), ("dependency", "list", "iss-00003"), ("dependency", "check", "iss-00003")]
)
def test_readonly_previews_preserve_readiness_and_leave_all_inputs_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], command: tuple[str, ...]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.edit(lambda fake: fake.block(2, by=4))
    before = tree_digest(world.main)
    code, payload = world.run(*command, "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    assert payload["data"]["result"]["can_apply"] is True and payload["effects"] == []
    if command[1] == "check":
        assert payload["data"]["result"]["ready"] is False
    assert tree_digest(world.main) == before and world.writes() == [] and world.changesets() == []
