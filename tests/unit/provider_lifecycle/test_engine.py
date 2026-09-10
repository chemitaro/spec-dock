from __future__ import annotations

from dataclasses import replace
from io import BytesIO
import os
from pathlib import Path
import subprocess
import tarfile
from types import SimpleNamespace
from typing import cast

import pytest

from spec_dock.provider_lifecycle.candidate import FIXED_DOMAINS
from spec_dock.provider_lifecycle.contracts import ActiveState, LifecycleMode, LifecycleRequest, Operation
from spec_dock.provider_lifecycle.engine import FAULT_POINTS, ProviderLifecycleEngine
from spec_dock.provider_lifecycle.legacy_fixture import LEGACY_SOURCE_COMMIT
from spec_dock.provider_lifecycle.private_state import (
    ActiveStateStore,
    PrivateStateError,
    PrivateStateForeignError,
    StageStore,
    resolve_private_namespace,
)
from spec_dock.provider_lifecycle.wire import parse_installation_record, serialize_public_result


def _materialize_legacy_workspace(root: Path) -> None:
    repository = Path(__file__).parents[3]
    sources = [f"src/spec_dock/assets/{suffix}" for _kind, _public, suffix in FIXED_DOMAINS]
    archive = subprocess.run(
        ["git", "archive", "--format=tar", LEGACY_SOURCE_COMMIT, "--", *sources, "spec-dock/spec-dock.version"],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as stream:
        for member in stream:
            if member.name == "spec-dock/spec-dock.version":
                destination = root / member.name
            else:
                domain = next(
                    (
                        item
                        for item in FIXED_DOMAINS
                        if member.name == f"src/spec_dock/assets/{item[2]}"
                        or member.name.startswith(f"src/spec_dock/assets/{item[2]}/")
                    ),
                    None,
                )
                if domain is None:
                    continue
                destination = root / domain[1] / member.name[len(f"src/spec_dock/assets/{domain[2]}") :].lstrip("/")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(member.linkname)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = stream.extractfile(member)
                assert source is not None
                destination.write_bytes(source.read())
                destination.chmod(0o755 if member.mode & 0o111 else 0o644)


def _request(
    root: Path,
    operation: Operation,
    *,
    mode: LifecycleMode = "apply",
    specs_mode: str | None = None,
) -> LifecycleRequest:
    return LifecycleRequest(
        str(root.resolve()),
        mode,
        mode == "apply",
        specs_mode=specs_mode,
        operation=operation,
        seed_policy="create-if-absent" if operation == "install" else "preserve-only",
    )


def _workspace_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    snapshot: dict[str, tuple[object, ...]] = {}
    for path in (root, *root.rglob("*")):
        relative = "." if path == root else path.relative_to(root).as_posix()
        value = path.lstat()
        if path.is_symlink():
            snapshot[relative] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            snapshot[relative] = ("file", value.st_mode & 0o777, path.read_bytes())
        else:
            snapshot[relative] = ("directory", value.st_mode & 0o777)
    return snapshot


def test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations(tmp_path: Path) -> None:
    for index, point in enumerate(sorted(FAULT_POINTS)):
        workspace = (tmp_path / f"fault-{index}-{point}").resolve()
        workspace.mkdir()
        request = _request(workspace, "install")

        first = ProviderLifecycleEngine(fault_injector=point).execute(request, force=True)
        serialize_public_result(first)
        assert first.status in {"blocked", "partial_failure", "completed", "completed_with_warnings"}

        retry = first
        for _attempt in range(4):
            if retry.status == "completed":
                break
            if retry.continuation["next_action"] == "retry-cleanup":
                command = retry.continuation["next_command"]
                assert isinstance(command, str)
                token = command.split("--provider-cleanup-token ", 1)[1].split(" -- ", 1)[0]
                retry = ProviderLifecycleEngine().execute(request, force=True, cleanup_token=token)
            else:
                if retry.continuation["next_action"] != "none":
                    assert retry.continuation["next_action"] == "run-request"
                retry = ProviderLifecycleEngine().execute(request, force=True)
            serialize_public_result(retry)
        assert retry.status == "completed"
        assert retry.code in {"install-completed", "update-completed", "terminal-cleanup-completed"}


def test_t06_exchange_keeps_the_old_root_in_stage_until_cleanup(tmp_path: Path) -> None:
    workspace = (tmp_path / "exchange-recovery").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    consumer_file = workspace / "spec-dock" / "docs" / "consumer-owned.txt"
    consumer_file.write_text("consumer-owned\n", encoding="utf-8")

    request = _request(workspace, "update")
    interrupted = ProviderLifecycleEngine(fault_injector="source-parent-fsync").execute(request)
    assert interrupted.status == "partial_failure"
    assert interrupted.mutation_started is True

    namespace = resolve_private_namespace(workspace)
    staged_old_root = namespace / "STAGE" / "docs"
    assert staged_old_root.is_dir()
    assert (staged_old_root / "consumer-owned.txt").read_text(encoding="utf-8") == "consumer-owned\n"
    assert not consumer_file.exists()

    resumed = ProviderLifecycleEngine().execute(request)
    serialize_public_result(resumed)
    assert resumed.status == "completed"


def test_t06_bootstrap_active_publication_failure_restores_absent_pre_state(tmp_path: Path) -> None:
    workspace = (tmp_path / "bootstrap-active-recovery").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")
    occurrences = 0

    def fail_bootstrap_active_publication(point: str) -> None:
        nonlocal occurrences
        if point == "active-parent-fsync":
            occurrences += 1
            if occurrences == 2:
                raise OSError("bootstrap ACTIVE publication failed")

    first = ProviderLifecycleEngine(fault_injector=fail_bootstrap_active_publication).execute(request, force=True)
    assert first.status == "blocked"
    assert first.code == "bootstrap-container-conflict"
    assert first.bootstrap_rolled_back is True
    assert first.mutation_started is False
    assert not (workspace / "spec-dock").exists()

    namespace = resolve_private_namespace(workspace)
    active = ActiveStateStore(namespace, repository_root=workspace).load()
    assert active is not None
    assert active.state == "prepared"
    assert active.bootstrap_container == {"disposition": "planned-create", "witness": None}
    resumed = ProviderLifecycleEngine().execute(request, force=True)
    assert resumed.status == "completed"


def test_t06_record_temp_witness_failure_cleans_unbound_temp_before_retry(tmp_path: Path) -> None:
    workspace = (tmp_path / "record-temp-witness-recovery").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")
    occurrences = 0

    def fail_record_temp_witness(point: str) -> None:
        nonlocal occurrences
        if point == "active-temp-open":
            occurrences += 1
            if occurrences == 3:
                raise OSError("RECORD-TEMP witness publication failed")

    first = ProviderLifecycleEngine(fault_injector=fail_record_temp_witness).execute(request, force=True)
    assert first.status == "partial_failure"
    assert first.code == "lifecycle-preparation-failed"
    assert first.phase == "publish-incomplete-record"
    assert first.mutation_started is True

    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    active = active_store.load()
    assert active is not None
    assert active.record_temp_witness is None
    assert not (namespace / "RECORD-TEMP").exists()
    resumed = ProviderLifecycleEngine().execute(request, force=True)
    assert resumed.status == "completed"


def test_t07_legacy_migration_uninstall_and_old_package_mutation_zero(tmp_path: Path) -> None:
    workspace = (tmp_path / "legacy").resolve()
    workspace.mkdir()
    _materialize_legacy_workspace(workspace)
    protected = workspace / "spec-dock" / "initiatives" / "protected.txt"
    protected.parent.mkdir(parents=True)
    protected.write_bytes(b"consumer-owned\n")
    before_protected = (protected.read_bytes(), protected.lstat().st_ino)

    migrated = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert migrated.status == "completed"
    assert migrated.code == "legacy-migration-completed"
    assert (protected.read_bytes(), protected.lstat().st_ino) == before_protected
    record = parse_installation_record((workspace / "spec-dock/spec-dock.version").read_bytes())
    assert record.state == "ready"
    assert record.version == "0.2.4"

    uninstalled = ProviderLifecycleEngine().execute(
        _request(workspace, "uninstall", specs_mode="keep"),
    )
    assert uninstalled.status == "completed"
    assert uninstalled.code == "uninstall-completed"
    assert parse_installation_record((workspace / "spec-dock/spec-dock.version").read_bytes()).state == (
        "tooling-absent-preserved-data"
    )
    assert not (workspace / "spec-dock/docs").exists()
    assert not (workspace / ".agents/skills/spec-dock").exists()
    assert (protected.read_bytes(), protected.lstat().st_ino) == before_protected

    before_rejected_purge = _workspace_snapshot(workspace)
    rejected = ProviderLifecycleEngine().execute(
        _request(workspace, "uninstall", specs_mode="remove"),
    )
    assert rejected.status == "error"
    assert rejected.code == "spec-history-purge-removed"
    assert _workspace_snapshot(workspace) == before_rejected_purge


@pytest.mark.parametrize(
    ("failure", "expected_code"),
    [
        (PrivateStateForeignError("foreign private authority"), "stage-owner-mismatch"),
        (PrivateStateError("private authority I/O"), "lifecycle-preparation-failed"),
    ],
)
def test_t04_initial_private_authority_preserves_foreign_vs_io_wire_codes(
    monkeypatch, tmp_path: Path, failure: PrivateStateError, expected_code: str
) -> None:
    modes: tuple[LifecycleMode, ...] = ("apply", "dry-run")
    for index, mode in enumerate(modes):
        workspace = (tmp_path / f"authority-{expected_code}-{index}").resolve()
        workspace.mkdir()
        engine = ProviderLifecycleEngine()

        def fail_stores(*_args, **_kwargs):
            raise failure

        monkeypatch.setattr(engine, "_stores", fail_stores)
        before = _workspace_snapshot(workspace)
        result = engine.execute(_request(workspace, "install", mode=mode), force=True)

        serialize_public_result(result)
        assert result.status == "blocked"
        assert result.code == expected_code
        assert result.operation is None
        assert result.candidate_digest is None
        assert result.seed_policy is None
        assert result.mutation_started is False
        assert result.continuation["next_action"] == "none"
        assert _workspace_snapshot(workspace) == before


def test_t04_foreign_stage_owner_is_stage_owner_mismatch_in_candidate_staging(monkeypatch, tmp_path: Path) -> None:
    workspace = (tmp_path / "stage-owner").resolve()
    workspace.mkdir()
    engine = ProviderLifecycleEngine()

    def fail_prepare_stage(*_args, **_kwargs):
        raise PrivateStateForeignError("foreign stage owner")

    monkeypatch.setattr(engine, "_prepare_stage", fail_prepare_stage)
    result = engine.execute(_request(workspace, "install"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "stage-owner-mismatch"
    assert result.operation == "install"
    assert result.candidate_digest is not None
    assert result.seed_policy == "create-if-absent"
    assert result.phase == "candidate-staging"
    assert result.last_completed_phase == "preflight"
    assert result.mutation_started is False
    assert result.actions == ()


def test_t04_prepared_uninstall_dry_run_preserves_foreign_stage_before_plan(monkeypatch, tmp_path: Path) -> None:
    workspace = (tmp_path / "prepared-uninstall").resolve()
    workspace.mkdir()
    request = _request(workspace, "uninstall", mode="dry-run")
    active = cast(
        "ActiveState",
        SimpleNamespace(
            operation="uninstall",
            seed_policy="preserve-only",
            result_family="uninstall",
            repository_key="a" * 64,
            tuple_key="b" * 64,
            operation_generation="0" * 32,
            candidate_digest="c" * 64,
            registered_stage_entries=({"candidate_tree_digest": None, "original_tree_digest": None},) * 6,
        ),
    )

    class ForeignStage:
        def __init__(self) -> None:
            self.calls = 0

        def inspect(self, owner):
            self.calls += 1
            raise PrivateStateForeignError("foreign prepared stage")

    foreign_stage = ForeignStage()
    stage = cast("StageStore", foreign_stage)
    engine = ProviderLifecycleEngine()
    monkeypatch.setattr(engine, "_observe_domains", lambda _root_fd: pytest.fail("target was observed"))
    root_fd = os.open(workspace, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        result = engine._resume_or_block(
            request,
            "uninstall",
            "preserve-only",
            None,
            active,
            None,
            None,
            stage,
            root_fd,
            force=None,
        )
    finally:
        os.close(root_fd)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "stage-owner-mismatch"
    assert result.operation == "uninstall"
    assert result.candidate_digest == "c" * 64
    assert result.seed_policy == "preserve-only"
    assert result.mutation_started is False
    assert foreign_stage.calls == 1


@pytest.mark.parametrize("fault_point", ["stage-mkdir", "stage-owner-write"])
def test_t04_prepared_uninstall_dry_run_plans_without_repairing_incomplete_stage(
    tmp_path: Path, fault_point: str
) -> None:
    workspace = (tmp_path / fault_point).resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    request = _request(workspace, "uninstall")
    first = ProviderLifecycleEngine(fault_injector=fault_point).execute(request, force=True)
    assert first.status == "blocked"
    assert first.code == "lifecycle-preparation-failed"

    before = _workspace_snapshot(workspace)
    dry_run = ProviderLifecycleEngine().execute(_request(workspace, "uninstall", mode="dry-run"))

    serialize_public_result(dry_run)
    assert dry_run.status == "planned"
    assert dry_run.code == "uninstall-planned"
    assert _workspace_snapshot(workspace) == before


def test_t04_active_reentry_rejects_repository_identity_mismatch(tmp_path: Path) -> None:
    workspace = (tmp_path / "active-binding").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")
    first = ProviderLifecycleEngine(fault_injector="stage-mkdir").execute(request, force=True)
    assert first.status == "blocked"

    namespace = resolve_private_namespace(workspace)
    store = ActiveStateStore(namespace, repository_root=workspace)
    active = store.load()
    assert active is not None
    store.save(
        replace(
            active,
            repository_identity={
                "device": active.repository_identity["device"],
                "inode": active.repository_identity["inode"] + 1,
                "euid": active.repository_identity["euid"],
            },
        )
    )
    before = _workspace_snapshot(workspace)

    result = ProviderLifecycleEngine().execute(request, force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "stage-owner-mismatch"
    assert result.mutation_started is False
    assert _workspace_snapshot(workspace) == before


@pytest.mark.parametrize("operation", ["install", "uninstall"])
def test_t04_active_records_explicit_original_and_terminal_kinds(tmp_path: Path, operation: Operation) -> None:
    workspace = (tmp_path / operation).resolve()
    workspace.mkdir()
    if operation == "uninstall":
        installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
        assert installed.status == "completed"

    result = ProviderLifecycleEngine(fault_injector="stage-mkdir").execute(_request(workspace, operation), force=True)
    assert result.status == "blocked"

    namespace = resolve_private_namespace(workspace)
    store = ActiveStateStore(namespace, repository_root=workspace)
    active = store.load()
    assert active is not None
    expected_original = "directory" if operation == "uninstall" else "absent"
    expected_terminal = "absent" if operation == "uninstall" else "directory"
    assert {item["original_kind"] for item in active.owned_target_witnesses} == {expected_original}
    assert {item["terminal_kind"] for item in active.owned_target_witnesses} == {expected_terminal}
    if operation == "uninstall":
        assert all(item["terminal_tree_digest"] is None for item in active.owned_target_witnesses)
    else:
        assert all(isinstance(item["terminal_tree_digest"], str) for item in active.owned_target_witnesses)

    invalid = replace(
        active,
        owned_target_witnesses=tuple(
            {**item, "terminal_kind": None, "terminal_tree_digest": None} for item in active.owned_target_witnesses
        ),
    )
    with pytest.raises(PrivateStateError):
        store.save(invalid)
