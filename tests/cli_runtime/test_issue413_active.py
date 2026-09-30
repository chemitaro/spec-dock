"""Direct selection changes through the control-free public CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from tests.cli_runtime.test_issue413_contract import add_scope, make_workspace


def test_active_set_empty_requires_start_without_acquiring_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    assert main(["--project", str(root), "active", "set", "init-00001", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "WORK_START_REQUIRED"
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent").exists()
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX flock boundary")
def test_clear_in_another_process_does_not_wait_for_start_lock(tmp_path: Path) -> None:
    import fcntl

    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    descriptor = os.open(root / ".git", os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "from spec_dock.cli import main; import sys; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "active",
                "clear",
                "--all",
                "--json",
            ],
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
            capture_output=True,
            timeout=5,
        )
    finally:
        os.close(descriptor)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert json.loads(completed.stdout)["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_active_help_describes_start_only_acquisition_and_direct_clear(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "active", "set"]) == 0
    help_text = capsys.readouterr().out
    assert "work start" in help_text
    assert "unchanged" in help_text
    assert "--from-branch" not in help_text
    assert main(["help", "active", "clear"]) == 0
    help_text = capsys.readouterr().out
    assert "observed" in help_text
    assert "--all --yes" in help_text
    assert "promot" in help_text


@pytest.mark.parametrize("operation", [["set", "init-00001"], ["clear", "--all"]])
@pytest.mark.parametrize("guard", [["--expect-backend", "local"], ["--expect-current", "epic-00002"]])
def test_active_expectation_mismatch_preserves_observed_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], operation: list[str], guard: list[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    record = select_fixture(root)
    before = record.read_bytes()
    assert main(["--project", str(root), "active", *operation, *guard, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert record.read_bytes() == before


@pytest.mark.parametrize("entry", ["unknown", "symlink", "stage"])
def test_clear_all_never_purges_unrecognized_or_redirected_entries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], entry: str
) -> None:
    root = make_workspace(tmp_path / "consumer")
    directory = root / "spec-dock/.agent/work-target"
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
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert path.read_bytes() == b"preserve"
    assert outside.read_bytes() == b"preserve"


def select_fixture(root: Path, *, scope_id: str = "init-00001", number: int = 1) -> Path:
    context = resolve_context(str(root), root)
    with WorkTargetStore(root) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                scope_id,
                f"gh:example/repo#{number}",
                "main",
                "2026-09-30T00:00:00Z",
                context.clone_identity,
                context.worktree_identity,
            )
        )
        return store.path / handle.basename


def test_active_set_same_direct_is_unchanged_and_preserves_exact_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    assert main(["--project", str(root), "active", "set", "@current", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "unchanged"
    assert result["data"]["selection"]["scope_id"] == "init-00001"
    assert result["effects"] == []
    assert record.read_bytes() == before


def test_clear_all_preserves_stale_selection_until_it_is_explicitly_removed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    metadata.write_text(json.dumps(dict(payload, github=dict(payload["github"], repo_name="other"))))
    assert main(["--project", str(root), "active", "clear", "--from", "init-00001", "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert record.exists()
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_clear_all_can_remove_stale_record_with_missing_scope_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    (root / "spec-dock/initiatives/init-00001-fixture/.meta.json").unlink()
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_clear_unlink_sync_failure_reports_unknown_removal_instead_of_no_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["effects"] == [{"kind": "selection.clear", "status": "unknown", "target": record.name[7:-5]}]
    assert "fixture sync failure after unlink" in result["error"]["message"]
    assert not record.exists()


def test_clear_from_preserves_replacement_after_target_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--from", "init-00001", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert replaced
    assert replacement.read_bytes() == payload
    assert result["data"]["selection"]["selection_token"] == "b" * 32
    assert all(effect["target"] != "b" * 32 for effect in result["effects"])
    assert result["status"] == "unchanged"


def test_clear_concurrent_old_name_removal_is_unchanged_and_keeps_new_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert raced
    assert result["status"] == "unchanged"
    assert replacement.read_bytes() == payload
    assert result["data"]["selection"]["selection_token"] == "b" * 32
    assert result["effects"] == [{"kind": "selection.clear", "status": "unchanged", "target": record.name[7:-5]}]


@pytest.mark.parametrize("flag", ["--from-branch", "--resume", "--rollback"])
def test_active_retired_acquisition_inputs_fail_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    args = (
        ["active", "set", "--from-branch"] if flag == "--from-branch" else ["active", "clear", "--all", flag, "0" * 32]
    )
    assert main(["--project", str(tmp_path / "absent"), *args, "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []


def test_clear_corrupt_record_requires_yes_then_removes_only_regular_observed_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    record.write_bytes(b"broken json")
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert record.read_bytes() == b"broken json"
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


@pytest.mark.parametrize("identity", ["clone_identity", "worktree_identity"])
def test_clear_physical_identity_mismatch_requires_explicit_yes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], identity: str
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    payload = json.loads(record.read_bytes())
    payload[identity]["device"] = str(int(payload[identity]["device"]) + 1)
    record.write_text(json.dumps(payload))
    before = record.read_bytes()
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert record.read_bytes() == before
    assert main(["--project", str(root), "active", "clear", "--all", "--dry-run", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["effects"] == [
        {"kind": "selection.clear", "status": "planned", "target": record.name[7:-5]}
    ]
    assert record.read_bytes() == before
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["selection"]["status"] == "empty"
    assert not record.exists()


def test_corrupt_clear_dry_run_requires_no_approval_and_preserves_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    record.write_bytes(b"broken json")
    assert main(["--project", str(root), "active", "clear", "--all", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["effects"] == [{"kind": "selection.clear", "status": "planned", "target": record.name[7:-5]}]
    assert record.read_bytes() == b"broken json"


def test_active_clear_all_removes_observed_record_without_git_or_remote_effects(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    assert main(["--project", str(root), "active", "clear", "--all", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["selection"]["status"] == "empty"
    assert result["effects"] == [{"kind": "selection.clear", "status": "succeeded", "target": record.name[7:-5]}]
    assert not record.exists()
    assert metadata.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()


def test_clear_multiple_records_reports_failed_and_unattempted_handles_after_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    original = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert len(attempted) == 2
    unattempted = next(record for record in records if record.name not in attempted)
    assert result["effects"] == [
        {"kind": "selection.clear", "status": "succeeded", "target": attempted[0][7:-5]},
        {"kind": "selection.clear", "status": "failed", "target": attempted[1][7:-5]},
        {"kind": "selection.clear", "status": "not_attempted", "target": unattempted.name[7:-5]},
    ]
    assert not (original.parent / attempted[0]).exists()
    assert (original.parent / attempted[1]).read_bytes() == payload and unattempted.read_bytes() == payload


def test_clear_first_failure_returns_effects_without_claiming_a_partial_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    original = select_fixture(root)
    payload = original.read_bytes()
    second = original.with_name("target-" + "b" * 32 + ".json")
    second.write_bytes(payload)
    attempted = []

    def unlink(path, *args, **kwargs):
        attempted.append(path)
        raise PermissionError("fixture first unlink refused")

    monkeypatch.setattr(os, "unlink", unlink)
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert len(attempted) == 1
    assert [effect["status"] for effect in result["effects"]] == ["failed", "not_attempted"]
    assert result["effects"][0]["target"] == attempted[0][7:-5]
    assert {effect["target"] for effect in result["effects"]} == {original.name[7:-5], "b" * 32}
    assert original.read_bytes() == payload and second.read_bytes() == payload


def test_clear_unknown_directory_sync_reports_all_later_handles_as_unattempted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    original = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert [effect["status"] for effect in result["effects"]] == ["unknown", "not_attempted", "not_attempted"]
    assert {effect["target"] for effect in result["effects"]} == {record.name[7:-5] for record in records}
    assert sum(record.exists() for record in records) == 2
    assert all(record.read_bytes() == payload for record in records if record.exists())


def test_clear_conflicting_record_retains_changed_bytes_and_unattempted_handles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    original = select_fixture(root)
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
    assert main(["--project", str(root), "active", "clear", "--all", "--yes", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert len(unlinked) == 1
    assert [effect["status"] for effect in result["effects"]] == ["succeeded", "failed", "not_attempted"]
    assert {effect["target"] for effect in result["effects"]} == {record.name[7:-5] for record in records}
    assert sum(record.exists() for record in records) == 2
    assert all(record.read_bytes() == changed for record in records if record.exists())


@pytest.mark.parametrize("from_target", ["init-00001", "epic-00002", "iss-00003", "iss-00004", "iss-00099"])
def test_active_clear_from_removes_whole_direct_only_for_its_current_chain(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], from_target: str
) -> None:
    root = make_workspace(tmp_path / "consumer")
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    add_scope(root, "iss-00004", "issue", "epic-00002", epic)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    expected = 4 if from_target == "iss-00099" else 0
    assert main(["--project", str(root), "active", "clear", "--from", from_target, "--json"]) == expected
    result = json.loads(capsys.readouterr().out)
    if from_target in ("iss-00004", "iss-00099"):
        assert record.read_bytes() == before
        assert result["effects"] == []
        if expected == 0:
            assert result["status"] == "unchanged"
    else:
        assert not record.exists()
        assert result["data"]["selection"]["status"] == "empty"
        assert result["data"]["ancestors"] == []
        assert main(["--project", str(root), "scope", "show", "@current", "--json"]) == 4
        assert json.loads(capsys.readouterr().out)["effects"] == []


@pytest.mark.parametrize(
    "role,scope_id",
    [("@current", "iss-00003"), ("@issue", "iss-00003"), ("@epic", "epic-00002"), ("@initiative", "init-00001")],
)
def test_dynamic_roles_derive_current_ancestors_from_direct_scope(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], role: str, scope_id: str
) -> None:
    root = make_workspace(tmp_path / "consumer")
    epic = add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
    record = select_fixture(root, scope_id="iss-00003", number=3)
    before = record.read_bytes()
    assert main(["--project", str(root), "scope", "show", role, "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["id"] == scope_id
    assert result["effects"] == []
    assert record.read_bytes() == before


def test_clear_dry_run_preserves_selection_and_only_reports_planned_removal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = record.read_bytes()
    assert main(["--project", str(root), "active", "clear", "--all", "--dry-run", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["effects"] == [{"kind": "selection.clear", "status": "planned", "target": record.name[7:-5]}]
    assert record.read_bytes() == before
