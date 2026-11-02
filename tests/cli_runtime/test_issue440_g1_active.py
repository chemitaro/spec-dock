"""Direct selection through `active set/clear/show` and dynamic roles in canonical mode.

Replaces the schema-3 tests of tests/cli_runtime/test_issue413_active.py (iss-00440). The record store and its
fail-closed removal are shared by both modes; only the fixture moved to a CanonicalWorld.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.legacy_contracts_g1 import chain_world, clears, run_process, select_record, token

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    return chain_world(tmp_path, monkeypatch, capsys, sibling=True)


def test_active_set_empty_requires_start_without_acquiring_selection(world: CanonicalWorld) -> None:
    code, result = world.run("active", "set", "init-00001")
    assert (code, result["error"]["code"]) == (3, "WORK_START_REQUIRED")
    assert result["effects"] == []
    assert not (world.main / "spec-dock/.agent").exists()
    assert not (world.main / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX flock boundary")
def test_clear_in_another_process_does_not_wait_for_start_lock(world: CanonicalWorld) -> None:
    from spec_dock.runtime.infra.start_lock import StartLock

    record = select_record(world, "init-00001", 1)
    with StartLock(world.main / ".git", timeout=0):
        completed = run_process(world, "active", "clear", "--all", timeout=15)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert json.loads(completed.stdout)["data"]["selection"]["status"] == "empty"
    assert not record.exists()


@pytest.mark.parametrize("operation", [["set", "init-00001"], ["clear", "--all"]])
@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "epic-00002"]])
def test_active_expectation_mismatch_preserves_observed_record(
    world: CanonicalWorld, operation: list[str], guard: list[str]
) -> None:
    record = select_record(world, "init-00001", 1)
    before = record.read_bytes()
    code, result = world.run("active", *operation, *guard)
    assert code == 3, result
    assert result["effects"] == []
    assert record.read_bytes() == before


@pytest.mark.parametrize("entry", ["unknown", "symlink", "stage"])
def test_clear_all_never_purges_unrecognized_or_redirected_entries(
    world: CanonicalWorld, tmp_path: Path, entry: str
) -> None:
    directory = world.main / "spec-dock/.agent/work-target"
    directory.mkdir(parents=True)
    outside = tmp_path / "preserve.json"
    outside.write_bytes(b"preserve")
    path = directory / (
        "target-" + "b" * 32 + ".json" if entry == "symlink" else ".stage-pending" if entry == "stage" else "unexpected"
    )
    if entry == "symlink":
        path.symlink_to(outside)
    else:
        path.write_bytes(b"preserve")
    code, result = world.run("active", "clear", "--all", "--yes")
    assert code == 3, result
    assert result["effects"] == []
    assert path.read_bytes() == b"preserve"
    assert outside.read_bytes() == b"preserve"


def test_active_set_same_direct_is_unchanged_and_preserves_exact_record(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 1)
    before = record.read_bytes()
    assert world.run("active", "set", "@current")[0] == 0  # the first set aligns spec-dock/active
    code, result = world.run("active", "set", "@current")
    assert (code, result["status"]) == (0, "unchanged"), result
    assert result["data"]["selection"]["scope_id"] == "init-00001"
    # Canonical set reports each aligned navigation link as an unchanged active.link effect; nothing else.
    assert {(effect["kind"], effect["status"]) for effect in result["effects"]} <= {("active.link", "unchanged")}
    assert record.read_bytes() == before


@pytest.mark.parametrize("target", ["init-00001", "init-1", "gh:example/repo#1", "@current"])
def test_active_set_existing_direct_resolves_exact_selectors_without_acquisition_or_remote_calls(
    world: CanonicalWorld, target: str
) -> None:
    record = select_record(world, "init-00001", 1)
    before = record.read_bytes()
    assert world.run("active", "set", "@current")[0] == 0
    digest = tree_digest(world.main)
    code, result = world.run("active", "set", target)
    # Canonical set reads the GitHub structure snapshot and its link sync tries the Start lock without waiting,
    # so only the selector resolution, the unchanged record and the absence of GitHub writes carry over.
    assert (code, result["status"]) == (0, "unchanged"), result
    assert [effect for effect in result["effects"] if effect["kind"] != "active.link"] == []
    assert result["data"]["selection"]["scope_id"] == "init-00001"
    assert record.read_bytes() == before and tree_digest(world.main) == digest
    assert world.fake().writes() == []


@pytest.mark.parametrize("legacy_kind", ["files", "directories-and-hardlink"])
def test_active_clear_preserves_legacy_manifests_projections_and_cache_bytes(
    world: CanonicalWorld, tmp_path: Path, legacy_kind: str
) -> None:
    record = select_record(world, "init-00001", 1)
    agent = record.parent.parent
    work = world.main / "spec-dock/.work"
    work.mkdir()
    old_bytes = b'{"schema_version":2,"issue":{"id":"iss-00099","future_field":"keep"}}\r\n'
    for path in (work / "active.json", work / "current.json", agent / "active.json"):
        path.write_bytes(old_bytes)
    cached = agent / "index.json"
    cached.write_bytes(b'{"active":{"issue":{"id":"iss-00099"}},"nodes":{}}\r\n')
    generated = world.main / "spec-dock/old-projection/current-runbook.json"
    generated.parent.mkdir()
    if legacy_kind == "files":
        generated.write_bytes(b"private old runbook\r\n")
    else:
        generated.mkdir()
        (generated / "preserve.bin").write_bytes(b"\x00private\xff")
        (tmp_path / "outside-alias.json").hardlink_to(cached)
    trees = {path: tree_digest(path) for path in (work, generated.parent)}
    preserved = {path: path.read_bytes() for path in (agent / "active.json", cached)}
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty" and not record.exists()
    assert result["status"] == "succeeded"
    assert all(tree_digest(path) == digest for path, digest in trees.items())
    assert all(path.read_bytes() == content for path, content in preserved.items())
    assert cached.stat().st_nlink == (2 if legacy_kind == "directories-and-hardlink" else 1)
    assert "private" not in json.dumps(result) and "iss-00099" not in json.dumps(result)
    assert not (world.main / ".git/spec-dock").exists()


@pytest.mark.parametrize("arguments", [["set", "@current"], ["clear", "--all"]])
def test_active_refuses_a_hardlinked_current_record_without_changing_the_record_or_external_alias(
    world: CanonicalWorld, tmp_path: Path, arguments: list[str]
) -> None:
    record = select_record(world, "init-00001", 1)
    alias = tmp_path / "external-selection-alias.json"
    alias.hardlink_to(record)
    before = tree_digest(world.main)
    old_alias = alias.read_bytes()
    code, result = world.run("active", *arguments)
    assert (code, result["status"]) == (3, "failed"), result
    assert result["effects"] == []
    assert record.exists() and record.stat().st_nlink == 2
    assert tree_digest(world.main) == before and alias.read_bytes() == old_alias
    assert str(alias) not in json.dumps(result)


def test_clear_all_preserves_stale_selection_until_it_is_explicitly_removed(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 99)  # its GitHub reference no longer matches the Scope: stale
    code, result = world.run("active", "clear", "--from", "init-00001")
    assert code == 3, result
    assert result["effects"] == []
    assert record.exists()
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_clear_all_can_remove_stale_record_with_missing_scope_metadata(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00005", 5)  # no such Scope on GitHub
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_clear_unlink_sync_failure_reports_unknown_removal_instead_of_no_effect(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = select_record(world, "init-00001", 1)
    real_unlink = os.unlink
    real_fsync = os.fsync
    unlinked = False

    def unlink(path, *args, **kwargs):
        nonlocal unlinked
        real_unlink(path, *args, **kwargs)
        if path == record.name:
            unlinked = True

    def fsync(fd):
        if unlinked:
            raise OSError("fixture sync failure after unlink")
        real_fsync(fd)

    monkeypatch.setattr(os, "unlink", unlink)
    monkeypatch.setattr(os, "fsync", fsync)
    code, result = world.run("active", "clear", "--all")
    assert (code, result["status"]) == (6, "partial"), result
    assert result["effects"] == [{"kind": "selection.clear", "status": "unknown", "target": token(record)}]
    assert "fixture sync failure after unlink" in result["error"]["message"]
    assert not record.exists()


def test_clear_from_preserves_replacement_after_target_resolution(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = select_record(world, "init-00001", 1)
    replacement = record.with_name("target-" + "b" * 32 + ".json")
    payload = record.read_bytes()
    real_listdir = os.listdir
    real_close = os.close
    directory_id = record.parent.stat().st_ino
    captured = False
    replaced = False

    def listed(path):
        nonlocal captured
        entries = real_listdir(path)
        if isinstance(path, int) and os.fstat(path).st_ino == directory_id:
            captured = True
        return entries

    def closed(fd):
        nonlocal replaced
        selected_directory = captured and not replaced and os.fstat(fd).st_ino == directory_id
        real_close(fd)
        if selected_directory:
            replaced = True
            record.unlink()
            replacement.write_bytes(payload)

    monkeypatch.setattr(os, "listdir", listed)
    monkeypatch.setattr(os, "close", closed)
    code, result = world.run("active", "clear", "--from", "init-00001")
    assert code == 0, result
    assert replaced
    assert replacement.read_bytes() == payload
    assert result["data"]["selection"]["selection_token"] == "b" * 32
    assert all(effect["target"] != "b" * 32 for effect in result["effects"])
    assert result["status"] == "unchanged"


def test_clear_concurrent_old_name_removal_is_unchanged_and_keeps_new_record(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = select_record(world, "init-00001", 1)
    payload = record.read_bytes()
    replacement = record.with_name("target-" + "b" * 32 + ".json")
    real_unlink = os.unlink
    raced = False

    def unlink(path, *args, **kwargs):
        nonlocal raced
        if path == record.name and not raced:
            raced = True
            real_unlink(path, *args, **kwargs)
            replacement.write_bytes(payload)
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert raced
    assert result["status"] == "unchanged"
    assert replacement.read_bytes() == payload
    assert result["data"]["selection"]["selection_token"] == "b" * 32
    assert result["effects"] == [{"kind": "selection.clear", "status": "unchanged", "target": token(record)}]


def test_clear_corrupt_record_requires_yes_then_removes_only_regular_observed_name(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 1)
    record.write_bytes(b"broken json")
    code, result = world.run("active", "clear", "--all")
    assert code == 3, result
    assert result["effects"] == []
    assert record.read_bytes() == b"broken json"
    code, result = world.run("active", "clear", "--all", "--yes")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


@pytest.mark.parametrize("identity", ["clone_identity", "worktree_identity"])
def test_clear_physical_identity_mismatch_requires_explicit_yes(world: CanonicalWorld, identity: str) -> None:
    record = select_record(world, "init-00001", 1)
    payload = json.loads(record.read_bytes())
    payload[identity]["device"] = str(int(payload[identity]["device"]) + 1)
    record.write_text(json.dumps(payload))
    before = record.read_bytes()
    code, result = world.run("active", "clear", "--all")
    assert code == 3, result
    assert result["effects"] == []
    assert record.read_bytes() == before
    code, result = world.run("active", "clear", "--all", "--dry-run")
    assert code == 0, result
    assert clears(result["effects"]) == [{"kind": "selection.clear", "status": "planned", "target": token(record)}]
    assert record.read_bytes() == before
    code, result = world.run("active", "clear", "--all", "--yes")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_corrupt_clear_dry_run_requires_no_approval_and_preserves_record(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 1)
    record.write_bytes(b"broken json")
    code, result = world.run("active", "clear", "--all", "--dry-run")
    assert (code, result["status"]) == (0, "planned"), result
    assert clears(result["effects"]) == [{"kind": "selection.clear", "status": "planned", "target": token(record)}]
    assert record.read_bytes() == b"broken json"


def test_active_clear_all_removes_observed_record_without_git_or_remote_effects(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 1)
    head = (world.main / ".git/HEAD").read_bytes()
    code, result = world.run("active", "clear", "--all")
    assert code == 0, result
    assert result["data"]["selection"]["status"] == "empty"
    # Without spec-dock/system/active-none the fallback links are only warnings, so the clear is the one effect.
    assert result["effects"] == [{"kind": "selection.clear", "status": "succeeded", "target": token(record)}]
    assert not record.exists()
    assert (world.main / ".git/HEAD").read_bytes() == head
    assert not (world.main / ".git/spec-dock").exists()
    assert world.fake().writes() == []


def test_clear_multiple_records_reports_failed_and_unattempted_handles_after_unlink_failure(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = select_record(world, "init-00001", 1)
    payload = original.read_bytes()
    records = [original.with_name(f"target-{letter * 32}.json") for letter in ("a", "b", "c")]
    original.unlink()
    for record in records:
        record.write_bytes(payload)
    real_unlink = os.unlink
    attempted: list[str] = []

    def unlink(path, *args, **kwargs):
        if path in {record.name for record in records}:
            attempted.append(path)
            if len(attempted) == 2:
                raise PermissionError("fixture second record refused")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    code, result = world.run("active", "clear", "--all", "--yes")
    assert (code, result["status"]) == (6, "partial"), result
    assert len(attempted) == 2
    unattempted = next(record for record in records if record.name not in attempted)
    assert result["effects"] == [
        {"kind": "selection.clear", "status": "succeeded", "target": attempted[0][7:-5]},
        {"kind": "selection.clear", "status": "failed", "target": attempted[1][7:-5]},
        {"kind": "selection.clear", "status": "not_attempted", "target": token(unattempted)},
    ]
    assert not (original.parent / attempted[0]).exists()
    assert (original.parent / attempted[1]).read_bytes() == payload and unattempted.read_bytes() == payload


def test_clear_first_failure_returns_effects_without_claiming_a_partial_mutation(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = select_record(world, "init-00001", 1)
    payload = original.read_bytes()
    second = original.with_name("target-" + "b" * 32 + ".json")
    second.write_bytes(payload)
    attempted = []

    def unlink(path, *args, **kwargs):
        attempted.append(path)
        raise PermissionError("fixture first unlink refused")

    monkeypatch.setattr(os, "unlink", unlink)
    code, result = world.run("active", "clear", "--all", "--yes")
    assert (code, result["status"]) == (5, "failed"), result
    assert len(attempted) == 1
    assert [effect["status"] for effect in result["effects"]] == ["failed", "not_attempted"]
    assert result["effects"][0]["target"] == attempted[0][7:-5]
    assert {effect["target"] for effect in result["effects"]} == {token(original), "b" * 32}
    assert original.read_bytes() == payload and second.read_bytes() == payload


def test_clear_unknown_directory_sync_reports_all_later_handles_as_unattempted(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = select_record(world, "init-00001", 1)
    payload = original.read_bytes()
    records = [original, *(original.with_name(f"target-{letter * 32}.json") for letter in ("b", "c"))]
    for record in records[1:]:
        record.write_bytes(payload)
    real_fsync = os.fsync

    def syncing(descriptor):
        if os.fstat(descriptor).st_ino == original.parent.stat().st_ino and not all(
            record.exists() for record in records
        ):
            raise OSError("fixture directory sync refused")
        return real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", syncing)
    code, result = world.run("active", "clear", "--all", "--yes")
    assert code == 6, result
    assert [effect["status"] for effect in result["effects"]] == ["unknown", "not_attempted", "not_attempted"]
    assert {effect["target"] for effect in result["effects"]} == {token(record) for record in records}
    assert sum(record.exists() for record in records) == 2
    assert all(record.read_bytes() == payload for record in records if record.exists())


def test_clear_conflicting_record_retains_changed_bytes_and_unattempted_handles(
    world: CanonicalWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = select_record(world, "init-00001", 1)
    payload = original.read_bytes()
    records = [original, *(original.with_name(f"target-{letter * 32}.json") for letter in ("b", "c"))]
    for record in records[1:]:
        record.write_bytes(payload)
    changed = payload + b" "
    real_unlink = os.unlink
    unlinked = []

    def unlink(path, *args, **kwargs):
        real_unlink(path, *args, **kwargs)
        unlinked.append(path)
        for record in records:
            if record.exists():
                record.write_bytes(changed)

    monkeypatch.setattr(os, "unlink", unlink)
    code, result = world.run("active", "clear", "--all", "--yes")
    assert code == 6, result
    assert len(unlinked) == 1
    assert [effect["status"] for effect in result["effects"]] == ["succeeded", "failed", "not_attempted"]
    assert {effect["target"] for effect in result["effects"]} == {token(record) for record in records}
    assert sum(record.exists() for record in records) == 2
    assert all(record.read_bytes() == changed for record in records if record.exists())


@pytest.mark.parametrize("from_target", ["init-00001", "epic-00002", "iss-00003", "iss-00004", "iss-00099"])
def test_active_clear_from_removes_whole_direct_only_for_its_current_chain(
    world: CanonicalWorld, from_target: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    expected = 4 if from_target == "iss-00099" else 0
    code, result = world.run("active", "clear", "--from", from_target)
    assert code == expected, result
    if from_target in ("iss-00004", "iss-00099"):
        assert record.read_bytes() == before
        assert result["effects"] == []
        if expected == 0:
            assert result["status"] == "unchanged"
    else:
        assert not record.exists()
        assert result["data"]["selection"]["status"] == "empty"
        assert result["data"]["ancestors"] == []
        code, shown = world.run("scope", "show", "@current")
        assert code == 4, shown
        assert shown["effects"] == []


@pytest.mark.parametrize(
    "role,scope_id",
    [("@current", "iss-00003"), ("@issue", "iss-00003"), ("@epic", "epic-00002"), ("@initiative", "init-00001")],
)
def test_dynamic_roles_derive_current_ancestors_from_direct_scope(
    world: CanonicalWorld, role: str, scope_id: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("scope", "show", role)
    assert code == 0, result
    assert result["data"]["result"]["scope"]["id"] == scope_id
    assert result["effects"] == []
    assert record.read_bytes() == before


def test_clear_dry_run_preserves_selection_and_only_reports_planned_removal(world: CanonicalWorld) -> None:
    record = select_record(world, "init-00001", 1)
    before = record.read_bytes()
    code, result = world.run("active", "clear", "--all", "--dry-run")
    assert (code, result["status"]) == (0, "planned"), result
    # Canonical dry-run may also plan the fallback active.link effects; the selection part is the same.
    assert clears(result["effects"]) == [{"kind": "selection.clear", "status": "planned", "target": token(record)}]
    assert record.read_bytes() == before
