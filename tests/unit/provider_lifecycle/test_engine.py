from __future__ import annotations

from dataclasses import replace
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from types import SimpleNamespace
from typing import cast

import pytest

from spec_dock.provider_lifecycle.candidate import FIXED_DOMAINS
from spec_dock.provider_lifecycle.contracts import (
    SEED_PATHS,
    ActiveState,
    CompletionReceipt,
    LifecycleAction,
    LifecycleMode,
    LifecycleRequest,
    Operation,
)
from spec_dock.provider_lifecycle.engine import FAULT_POINTS, ProviderLifecycleEngine
from spec_dock.provider_lifecycle.filesystem import DomainTreeIdentity, NativeAtomicFilesystem
from spec_dock.provider_lifecycle.legacy_fixture import LEGACY_SOURCE_COMMIT
from spec_dock.provider_lifecycle.private_state import (
    ActiveStateStore,
    CompletionReceiptStore,
    PrivateStateError,
    PrivateStateForeignError,
    StageStore,
    cleanup_token_for,
    repository_key_for,
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


def _assert_first_red_partial_shape(
    result,
    *,
    expected_phase: str,
    expected_last_completed_phase: str,
    expected_actions: list[LifecycleAction],
) -> None:
    assert result.status == "partial_failure"
    assert result.phase == expected_phase
    assert result.last_completed_phase == expected_last_completed_phase
    assert result.actions == tuple(expected_actions)
    assert result.failed_paths == tuple(item.path for item in expected_actions if item.status == "failed")
    assert result.pending_paths == tuple(item.path for item in expected_actions if item.status == "pending")
    assert dict(result.summary) == {
        status: sum(item.status == status for item in expected_actions)
        for status in ("planned", "completed", "preserved", "pending", "failed", "warnings")
    }
    serialize_public_result(result)


def test_t01_partial_action_vectors_are_operation_and_seed_specific(tmp_path: Path) -> None:
    cases: tuple[tuple[Operation, Operation, str, str], ...] = (
        ("install", "install", "create-if-absent", "pending"),
        ("update", "install", "preserve-only", "preserved"),
    )
    for index, (request_operation, expected_operation, seed_policy, seed_status) in enumerate(cases):
        workspace = (tmp_path / f"partial-{index}").resolve()
        workspace.mkdir()
        result = ProviderLifecycleEngine(fault_injector="root-system-publish-or-detach").execute(
            _request(workspace, request_operation), force=True
        )
        expected_actions = [
            LifecycleAction("spec-dock", "container", "preserved", "shared-container-preserve"),
            LifecycleAction("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
            LifecycleAction("spec-dock/docs", "root", "completed", "candidate-root-create"),
            LifecycleAction("spec-dock/templates", "root", "completed", "candidate-root-create"),
            LifecycleAction("spec-dock/system", "root", "failed", "candidate-root-create"),
            LifecycleAction("spec-dock/scripts", "root", "pending", "candidate-root-create"),
            LifecycleAction(".agents/skills/spec-dock", "slot", "pending", "candidate-slot-create"),
            LifecycleAction(".agents/skills/spec-dock-grill-with-docs", "slot", "pending", "candidate-slot-create"),
            LifecycleAction(
                "spec-dock/.gitignore",
                "seed",
                seed_status,
                "fresh-seed-create" if seed_policy == "create-if-absent" else "preserve-only-seed",
            ),
            LifecycleAction(
                ".github/workflows/ci.yml",
                "seed",
                seed_status,
                "fresh-seed-create" if seed_policy == "create-if-absent" else "preserve-only-seed",
            ),
            LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
        ]
        _assert_first_red_partial_shape(
            result,
            expected_phase="publish-system",
            expected_last_completed_phase="publish-templates",
            expected_actions=expected_actions,
        )
        assert result.operation == expected_operation
        assert result.seed_policy == seed_policy


def test_t01_update_partial_action_vector_preserves_current_domains(tmp_path: Path) -> None:
    workspace = (tmp_path / "update-partial").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    (workspace / "spec-dock/system/consumer-owned.txt").write_text("consumer-owned\n", encoding="utf-8")

    result = ProviderLifecycleEngine(fault_injector="root-system-publish-or-detach").execute(
        _request(workspace, "update"), force=True
    )
    expected_actions = [
        LifecycleAction("spec-dock", "container", "preserved", "shared-container-preserve"),
        LifecycleAction("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
        LifecycleAction("spec-dock/docs", "root", "preserved", "candidate-root-current"),
        LifecycleAction("spec-dock/templates", "root", "preserved", "candidate-root-current"),
        LifecycleAction("spec-dock/system", "root", "failed", "candidate-root-replace"),
        LifecycleAction("spec-dock/scripts", "root", "preserved", "candidate-root-current"),
        LifecycleAction(".agents/skills/spec-dock", "slot", "preserved", "candidate-slot-current"),
        LifecycleAction(".agents/skills/spec-dock-grill-with-docs", "slot", "preserved", "candidate-slot-current"),
        LifecycleAction("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    ]
    _assert_first_red_partial_shape(
        result,
        expected_phase="publish-system",
        expected_last_completed_phase="publish-templates",
        expected_actions=expected_actions,
    )
    assert result.operation == "update"
    assert result.seed_policy == "preserve-only"


def test_t01_preserve_only_verify_failure_excludes_seed_phases(tmp_path: Path) -> None:
    workspace = (tmp_path / "preserve-only-verify-failure").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"

    result = ProviderLifecycleEngine(fault_injector="target-verify").execute(_request(workspace, "update"), force=True)

    serialize_public_result(result)
    assert result.status == "partial_failure"
    assert result.phase == "verify-target"
    assert result.last_completed_phase == "publish-slot-spec-dock-grill-with-docs"
    assert result.actions[-3:] == (
        LifecycleAction("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    )


@pytest.mark.parametrize(
    ("fault_point", "expected_last_completed_phase", "failed_index"),
    [
        ("root-docs-publish-or-detach", "publish-incomplete-record", 0),
        ("root-system-publish-or-detach", "detach-templates", 2),
    ],
)
def test_t01_uninstall_partial_action_vectors_follow_uninstall_sequence(
    tmp_path: Path, fault_point: str, expected_last_completed_phase: str, failed_index: int
) -> None:
    workspace = (tmp_path / fault_point).resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"

    result = ProviderLifecycleEngine(fault_injector=fault_point).execute(_request(workspace, "uninstall"), force=True)
    expected_actions = [
        LifecycleAction("spec-dock", "container", "preserved", "shared-container-preserve"),
        LifecycleAction("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
    ]
    for index, (category, path, _source) in enumerate(FIXED_DOMAINS):
        status = "failed" if index == failed_index else "completed" if index < failed_index else "pending"
        expected_actions.append(LifecycleAction(path, category, status, f"owned-{category}-remove"))
    expected_actions.extend([
        LifecycleAction("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        LifecycleAction("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    ])
    expected_phase = "detach-docs" if failed_index == 0 else "detach-system"
    _assert_first_red_partial_shape(
        result,
        expected_phase=expected_phase,
        expected_last_completed_phase=expected_last_completed_phase,
        expected_actions=expected_actions,
    )
    assert result.operation == "uninstall"
    assert result.seed_policy == "preserve-only"


def test_t01_uninstall_resume_actions_use_invocation_initial_absence(tmp_path: Path) -> None:
    workspace = (tmp_path / "uninstall-resume-absence").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    request = _request(workspace, "uninstall")

    first = ProviderLifecycleEngine(fault_injector="root-system-publish-or-detach").execute(request, force=True)
    assert first.status == "partial_failure"

    resumed = ProviderLifecycleEngine(fault_injector="root-scripts-publish-or-detach").execute(request)

    serialize_public_result(resumed)
    assert resumed.status == "partial_failure"
    assert resumed.phase == "detach-scripts"
    assert resumed.actions[2:8] == (
        LifecycleAction("spec-dock/docs", "root", "preserved", "owned-root-absent"),
        LifecycleAction("spec-dock/templates", "root", "preserved", "owned-root-absent"),
        LifecycleAction("spec-dock/system", "root", "completed", "owned-root-remove"),
        LifecycleAction("spec-dock/scripts", "root", "failed", "owned-root-remove"),
        LifecycleAction(".agents/skills/spec-dock", "slot", "pending", "owned-slot-remove"),
        LifecycleAction(".agents/skills/spec-dock-grill-with-docs", "slot", "pending", "owned-slot-remove"),
    )


@pytest.mark.parametrize("missing_count", range(7))
def test_t01_incomplete_uninstall_plan_precedes_already_absent_code(tmp_path: Path, missing_count: int) -> None:
    workspace = (tmp_path / f"incomplete-uninstall-{missing_count}").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    interrupted = ProviderLifecycleEngine(fault_injector="root-docs-publish-or-detach").execute(
        _request(workspace, "uninstall"), force=True
    )
    assert interrupted.status == "partial_failure"

    for _category, path, _source in FIXED_DOMAINS[:missing_count]:
        shutil.rmtree(workspace / path)

    dry_run = ProviderLifecycleEngine().execute(_request(workspace, "uninstall", mode="dry-run"))
    assert dry_run.status == "planned"
    assert dry_run.code == "uninstall-planned"
    serialize_public_result(dry_run)


def test_t01_orphan_incomplete_uninstall_record_is_closed_without_new_active(tmp_path: Path) -> None:
    workspace = (tmp_path / "orphan-incomplete-uninstall").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    request = _request(workspace, "uninstall")
    interrupted = ProviderLifecycleEngine(fault_injector="root-docs-publish-or-detach").execute(request, force=True)
    assert interrupted.status == "partial_failure"

    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    assert active_store.load() is not None
    record_path = workspace / "spec-dock/spec-dock.version"
    record_before = record_path.read_bytes()
    (namespace / "ACTIVE.json").unlink()
    assert active_store.load() is None

    result = ProviderLifecycleEngine().execute(request, force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "installation-record-state-inconsistent"
    assert result.operation is None
    assert result.candidate_digest == interrupted.candidate_digest
    assert result.seed_policy == interrupted.seed_policy
    assert result.mutation_started is False
    assert record_path.read_bytes() == record_before
    assert active_store.load() is None


def test_t01_active_resume_rejects_mismatched_receipt_before_mutation(tmp_path: Path) -> None:
    workspace = (tmp_path / "active-receipt-mismatch").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")
    interrupted = ProviderLifecycleEngine(fault_injector="root-system-publish-or-detach").execute(request, force=True)
    assert interrupted.status == "partial_failure"

    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    receipt_store = CompletionReceiptStore(namespace, repository_root=workspace)
    active = active_store.load()
    assert active is not None
    receipt_store.save(
        CompletionReceipt(
            1,
            active.repository_key,
            active.tuple_key,
            "0" * 32,
            active.operation,
            active.candidate_digest,
            active.seed_policy,
            active.result_family,
            active.terminal_record_digest,
            cleanup_token_for(active.repository_key, active.tuple_key, active.result_family, "0" * 32),
            active.cleanup_retry_invocation,
            active.deferred_invocation,
        )
    )
    before = _workspace_snapshot(workspace)
    active_before = active_store.load()
    receipt_before = receipt_store.load()

    result = ProviderLifecycleEngine().execute(request, force=True)

    serialize_public_result(result)
    assert result.status == "error"
    assert result.code == "invalid-request"
    assert result.mutation_started is False
    assert _workspace_snapshot(workspace) == before
    assert active_store.load() == active_before
    assert receipt_store.load() == receipt_before


def test_t01_uninstall_verify_rejects_non_directory_target(tmp_path: Path) -> None:
    workspace = (tmp_path / "uninstall-unsupported-target").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    outside = (tmp_path / "outside").resolve()
    outside.write_text("consumer-owned\n", encoding="utf-8")

    def introduce_unsupported_target(point: str) -> None:
        if point == "target-verify":
            (workspace / "spec-dock/docs").symlink_to(outside)

    result = ProviderLifecycleEngine(fault_injector=introduce_unsupported_target).execute(
        _request(workspace, "uninstall"), force=True
    )

    serialize_public_result(result)
    assert result.status == "partial_failure"
    assert result.code == "uninstall-partial-failure"
    assert result.phase == "verify-target"
    assert result.failed_paths == ("spec-dock/docs",)
    assert result.actions[2] == LifecycleAction("spec-dock/docs", "root", "failed", "owned-root-remove")
    assert (workspace / "spec-dock/docs").is_symlink()


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


@pytest.mark.parametrize("seed_policy", ["create-if-absent", "preserve-only"])
def test_t06_bootstrap_cleanup_failure_publishes_closed_install_actions(
    monkeypatch, tmp_path: Path, seed_policy: str
) -> None:
    workspace = (tmp_path / f"bootstrap-cleanup-failure-{seed_policy}").resolve()
    workspace.mkdir()
    request = _request(workspace, "install" if seed_policy == "create-if-absent" else "update")
    root_stat = workspace.stat()
    original_remove_tree_bound = NativeAtomicFilesystem.remove_tree_bound

    def fail_bootstrap_cleanup(
        filesystem: NativeAtomicFilesystem, parent_fd: int, name: str, tree: DomainTreeIdentity
    ) -> None:
        current = os.fstat(parent_fd)
        if name == "spec-dock" and (current.st_dev, current.st_ino) == (root_stat.st_dev, root_stat.st_ino):
            raise OSError("bootstrap cleanup blocked")
        original_remove_tree_bound(filesystem, parent_fd, name, tree)

    monkeypatch.setattr(NativeAtomicFilesystem, "remove_tree_bound", fail_bootstrap_cleanup)
    result = ProviderLifecycleEngine(fault_injector="bootstrap-container-fsync").execute(request, force=True)

    expected = [
        {
            "path": "spec-dock",
            "category": "container",
            "status": "failed",
            "reason": "fresh-container-create",
        },
        {
            "path": "spec-dock/spec-dock.version",
            "category": "record",
            "status": "pending",
            "reason": "incomplete-record-publish",
        },
        *[
            {
                "path": path,
                "category": category,
                "status": "pending",
                "reason": f"candidate-{category}-create",
            }
            for category, path, _source in FIXED_DOMAINS
        ],
    ]
    if seed_policy == "preserve-only":
        expected.extend([
            {
                "path": "spec-dock/.gitignore",
                "category": "seed",
                "status": "preserved",
                "reason": "preserve-only-seed",
            },
            {
                "path": ".github/workflows/ci.yml",
                "category": "seed",
                "status": "preserved",
                "reason": "preserve-only-seed",
            },
        ])
    else:
        expected.extend([
            {
                "path": "spec-dock/.gitignore",
                "category": "seed",
                "status": "pending",
                "reason": "fresh-seed-create",
            },
            {
                "path": ".github",
                "category": "container",
                "status": "pending",
                "reason": "fresh-container-create",
            },
            {
                "path": ".github/workflows",
                "category": "container",
                "status": "pending",
                "reason": "fresh-container-create",
            },
            {
                "path": ".github/workflows/ci.yml",
                "category": "seed",
                "status": "pending",
                "reason": "fresh-seed-create",
            },
        ])
    expected.append({
        "path": "@provider-stage",
        "category": "stage",
        "status": "pending",
        "reason": "candidate-stage-cleanup",
    })

    assert result.status == "partial_failure"
    assert result.code == "bootstrap-cleanup-failed"
    assert result.actions == tuple(LifecycleAction(**item) for item in expected)
    assert result.failed_paths == ("spec-dock",)
    assert result.pending_paths == tuple(item["path"] for item in expected if item["status"] == "pending")


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
    before_cleanup_attempt = _workspace_snapshot(workspace)
    rejected_cleanup = ProviderLifecycleEngine().execute(request, force=True, cleanup_token=active.cleanup_token)
    serialize_public_result(rejected_cleanup)
    assert rejected_cleanup.status == "error"
    assert rejected_cleanup.code == "invalid-request"
    assert rejected_cleanup.mutation_started is False
    assert _workspace_snapshot(workspace) == before_cleanup_attempt
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


def test_t04_stage_rebuild_revalidates_frozen_candidate_before_consumer_mutation(monkeypatch, tmp_path: Path) -> None:
    repository = Path(__file__).parents[3]
    assets_root = tmp_path / "assets"
    shutil.copytree(repository / "src/spec_dock/assets", assets_root)
    drifted_file = assets_root / "spec_dock/docs/reference_naming.md"
    engine = ProviderLifecycleEngine(assets_root=assets_root)
    original_candidate = engine._candidate
    mutated = False

    def capture_then_drift():
        nonlocal mutated
        candidate = original_candidate()
        if not mutated:
            drifted_file.write_bytes(drifted_file.read_bytes() + b"\nsource drift\n")
            mutated = True
        return candidate

    monkeypatch.setattr(engine, "_candidate", capture_then_drift)
    workspace = (tmp_path / "stage-rebuild-drift").resolve()
    workspace.mkdir()

    result = engine.execute(_request(workspace, "install"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "lifecycle-preparation-failed"
    assert result.phase == "candidate-staging"
    assert result.mutation_started is False
    assert not (workspace / "spec-dock").exists()
    active = ActiveStateStore(resolve_private_namespace(workspace), repository_root=workspace).load()
    assert active is not None
    assert active.state == "prepared"
    assert active.candidate_digest != engine._candidate().aggregate_digest


def test_t04_seed_admission_freezes_provider_created_action_provenance(tmp_path: Path) -> None:
    workspace = (tmp_path / "seed-provenance").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")

    first = ProviderLifecycleEngine(fault_injector="target-verify").execute(request, force=True)

    assert first.status == "partial_failure"
    active = ActiveStateStore(resolve_private_namespace(workspace), repository_root=workspace).load()
    assert active is not None
    assert active.seed_admission == dict.fromkeys(SEED_PATHS, "absent")
    first_seed_actions = {action.path: action for action in first.actions if action.category == "seed"}
    assert first_seed_actions == {
        path: LifecycleAction(path, "seed", "completed", "fresh-seed-create") for path in SEED_PATHS
    }

    resumed = ProviderLifecycleEngine().execute(request, force=True)

    assert resumed.status == "completed"
    resumed_seed_actions = {action.path: action for action in resumed.actions if action.category == "seed"}
    assert resumed_seed_actions == {
        path: LifecycleAction(path, "seed", "completed", "fresh-seed-create") for path in SEED_PATHS
    }


def test_t04_seed_admission_preserves_present_seed_through_reentry(tmp_path: Path) -> None:
    workspace = (tmp_path / "present-seed-provenance").resolve()
    workspace.mkdir()
    existing_gitignore = workspace / "spec-dock/.gitignore"
    existing_ci = workspace / ".github/workflows/ci.yml"
    existing_gitignore.parent.mkdir(parents=True)
    existing_ci.parent.mkdir(parents=True)
    existing_gitignore.write_bytes(b"consumer gitignore\n")
    existing_ci.write_bytes(b"consumer ci\n")
    request = _request(workspace, "install")

    first = ProviderLifecycleEngine(fault_injector="stage-mkdir").execute(request, force=True)

    assert first.status == "blocked"
    active = ActiveStateStore(resolve_private_namespace(workspace), repository_root=workspace).load()
    assert active is not None
    assert active.seed_admission == dict.fromkeys(SEED_PATHS, "present")
    existing_gitignore.unlink()
    existing_ci.unlink()

    resumed = ProviderLifecycleEngine().execute(request, force=True)

    assert resumed.status == "completed"
    assert not existing_gitignore.exists()
    assert not existing_ci.exists()
    resumed_seed_actions = {action.path: action for action in resumed.actions if action.category == "seed"}
    assert resumed_seed_actions == {
        path: LifecycleAction(path, "seed", "preserved", "consumer-seed-present") for path in SEED_PATHS
    }


@pytest.mark.parametrize("seed_path", SEED_PATHS)
@pytest.mark.parametrize("unsafe_kind", ["symlink", "directory", "fifo"])
def test_t04_update_unsafe_seed_type_blocks_before_admission_mutation(
    tmp_path: Path,
    seed_path: str,
    unsafe_kind: str,
) -> None:
    workspace = (tmp_path / f"unsafe-seed-{unsafe_kind}-{seed_path.replace('/', '-')}").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"

    seed = workspace / seed_path
    seed.unlink()
    if unsafe_kind == "symlink":
        target = tmp_path / f"{seed_path.replace('/', '-')}-target"
        target.write_text("consumer target\n", encoding="utf-8")
        seed.symlink_to(target)
    elif unsafe_kind == "directory":
        seed.mkdir()
    else:
        os.mkfifo(seed)

    before = _workspace_snapshot(workspace)
    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    receipt_store = CompletionReceiptStore(namespace, repository_root=workspace)
    active_before = active_store.load()
    receipt_before = receipt_store.load()

    result = ProviderLifecycleEngine().execute(_request(workspace, "update"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "unsafe-target-type"
    assert result.operation == "update"
    assert result.seed_policy == "preserve-only"
    assert result.phase == "preflight"
    assert result.last_completed_phase == "request-validation"
    assert result.mutation_started is False
    assert result.actions == ()
    assert _workspace_snapshot(workspace) == before
    assert active_store.load() == active_before
    assert receipt_store.load() == receipt_before


@pytest.mark.parametrize("seed_path", SEED_PATHS)
def test_t04_legacy_unsafe_seed_type_blocks_before_admission_mutation(tmp_path: Path, seed_path: str) -> None:
    workspace = (tmp_path / f"legacy-unsafe-seed-{seed_path.replace('/', '-')}").resolve()
    workspace.mkdir()
    _materialize_legacy_workspace(workspace)

    seed = workspace / seed_path
    seed.parent.mkdir(parents=True, exist_ok=True)
    seed.unlink(missing_ok=True)
    os.mkfifo(seed)
    before = _workspace_snapshot(workspace)

    result = ProviderLifecycleEngine().execute(_request(workspace, "update"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "unsafe-target-type"
    assert result.operation == "install"
    assert result.seed_policy == "preserve-only"
    assert result.mutation_started is False
    assert _workspace_snapshot(workspace) == before


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


def test_t04_private_authority_stays_bound_to_leased_root_after_visible_path_swap(tmp_path: Path) -> None:
    requested = (tmp_path / "repository").resolve()
    replacement = (tmp_path / "replacement").resolve()
    original_location = (tmp_path / "original-location").resolve()
    requested.mkdir()
    replacement.mkdir()
    original_binding = os.lstat(requested)
    replacement_binding = os.lstat(replacement)

    class SwapVisibleRootFilesystem(NativeAtomicFilesystem):
        swapped = False

        def probe_native_capability(self, parent_fd: int) -> None:
            if not self.swapped:
                requested.rename(original_location)
                replacement.rename(requested)
                self.swapped = True
            super().probe_native_capability(parent_fd)

    result = ProviderLifecycleEngine(filesystem=SwapVisibleRootFilesystem()).execute(
        _request(requested, "install"), force=True
    )

    serialize_public_result(result)
    assert result.status == "completed"
    private_root = requested.parent / f".spec-dock-provider-lifecycle-v1-euid-{os.geteuid()}"
    original_namespace = private_root / repository_key_for(
        original_binding.st_dev, original_binding.st_ino, os.geteuid()
    )
    replacement_namespace = private_root / repository_key_for(
        replacement_binding.st_dev, replacement_binding.st_ino, os.geteuid()
    )
    assert original_namespace.is_dir()
    assert not replacement_namespace.exists()


def test_t04_indeterminate_preparation_observation_is_not_classified_as_p2a(monkeypatch, tmp_path: Path) -> None:
    workspace = (tmp_path / "indeterminate-preparation").resolve()
    workspace.mkdir()
    request = _request(workspace, "install")
    engine = ProviderLifecycleEngine(fault_injector="stage-mkdir")
    first = engine.execute(request, force=True)
    assert first.status == "blocked"

    namespace = resolve_private_namespace(workspace)
    active = ActiveStateStore(namespace, repository_root=workspace).load()
    assert active is not None
    monkeypatch.setattr(engine, "_observe_record", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("unknown")))
    root_fd = os.open(workspace, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        result = engine._partial_failure_result(request, active, OSError("record publication failed"), root_fd)
    finally:
        os.close(root_fd)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "stage-owner-mismatch"
    assert result.operation == "install"
    assert result.candidate_digest == active.candidate_digest
    assert result.seed_policy == active.seed_policy
    assert result.phase == "candidate-staging"
    assert result.last_completed_phase == "preflight"
    assert result.mutation_started is False
    assert result.actions == ()


def test_t04_cleanup_token_mismatch_is_the_closed_request_error(tmp_path: Path) -> None:
    workspace = (tmp_path / "invalid-cleanup-token").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    request = _request(workspace, "update")
    occurrences = 0

    def fail_cleanup(point: str) -> None:
        nonlocal occurrences
        if point == "stage-entry-docs-remove":
            occurrences += 1
            if occurrences == 2:
                raise OSError("stage cleanup failed")

    first = ProviderLifecycleEngine(fault_injector=fail_cleanup).execute(request, force=True)
    assert first.status == "partial_failure"
    assert first.code == "terminal-cleanup-failed"

    result = ProviderLifecycleEngine().execute(request, force=True, cleanup_token="0" * 64)

    serialize_public_result(result)
    assert result.status == "error"
    assert result.code == "invalid-request"
    assert result.operation is None
    assert result.candidate_digest is None
    assert result.seed_policy is None
    assert result.phase == "request-validation"
    assert result.last_completed_phase == "not-started"
    assert result.mutation_started is False


def test_t04_first_desired_request_is_saved_by_receipt_before_active_reconciliation(tmp_path: Path) -> None:
    workspace = (tmp_path / "receipt-first-request").resolve()
    workspace.mkdir()
    base_request = _request(workspace, "install")
    first = ProviderLifecycleEngine(fault_injector="active-expected-unlink").execute(base_request, force=True)
    assert first.status == "partial_failure"
    assert first.code == "terminal-cleanup-failed"

    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    receipt_store = CompletionReceiptStore(namespace, repository_root=workspace)
    active = active_store.load()
    receipt = receipt_store.load()
    assert active is not None and receipt is not None
    assert active.deferred_invocation is None
    assert receipt.deferred_invocation is None

    desired = _request(workspace, "uninstall", specs_mode="keep")
    result = ProviderLifecycleEngine().execute(desired)

    serialize_public_result(result)
    assert result.status == "completed"
    assert result.code == "terminal-cleanup-completed"
    assert result.continuation["next_action"] == "run-request"
    assert result.continuation["next_command"] == "spec-dock uninstall --apply --keep-specs -- " + str(workspace)
    stored_receipt = receipt_store.load()
    assert stored_receipt is not None
    assert stored_receipt.deferred_invocation == {
        "invocation_id": "uninstall-apply-keep",
        "rendered_command": "spec-dock uninstall --apply --keep-specs -- " + str(workspace),
    }


def test_t04_receipt_owned_deferred_request_survives_active_reconciliation_failure(tmp_path: Path) -> None:
    workspace = (tmp_path / "receipt-active-reconciliation-failure").resolve()
    workspace.mkdir()
    base_request = _request(workspace, "install")
    first = ProviderLifecycleEngine(fault_injector="active-expected-unlink").execute(base_request, force=True)
    assert first.status == "partial_failure"
    assert first.code == "terminal-cleanup-failed"

    desired = _request(workspace, "uninstall", specs_mode="keep")
    failed = ProviderLifecycleEngine(fault_injector="active-temp-open").execute(desired)

    serialize_public_result(failed)
    assert failed.status == "partial_failure"
    assert failed.code == "terminal-cleanup-failed"
    assert failed.continuation["next_action"] == "retry-cleanup"
    assert failed.continuation["after_cleanup_action"] == "run-request"
    assert failed.continuation["after_cleanup_command"] == "spec-dock uninstall --apply --keep-specs -- " + str(
        workspace
    )
    namespace = resolve_private_namespace(workspace)
    receipt = CompletionReceiptStore(namespace, repository_root=workspace).load()
    active = ActiveStateStore(namespace, repository_root=workspace).load()
    assert receipt is not None and active is not None
    assert receipt.deferred_invocation is not None
    assert active.deferred_invocation is None


def test_t04_absent_update_preserve_only_rejects_init_force_seed_mismatch(tmp_path: Path) -> None:
    workspace = (tmp_path / "absent-update-seed").resolve()
    workspace.mkdir()
    update_request = _request(workspace, "update")
    first = ProviderLifecycleEngine(fault_injector="stage-mkdir").execute(update_request, force=True)
    assert first.status == "blocked"
    assert first.operation == "install"
    assert first.seed_policy == "preserve-only"

    namespace = resolve_private_namespace(workspace)
    active_store = ActiveStateStore(namespace, repository_root=workspace)
    active = active_store.load()
    assert active is not None
    before = _workspace_snapshot(workspace)

    result = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "resume-seed-policy-mismatch"
    assert result.operation == active.operation
    assert result.candidate_digest == active.candidate_digest
    assert result.seed_policy == active.seed_policy
    assert result.phase == "preflight"
    assert result.last_completed_phase == "request-validation"
    assert result.mutation_started is False
    assert _workspace_snapshot(workspace) == before
    assert active_store.load() == active


@pytest.mark.parametrize("foreign_part", ["owner", "entry"])
def test_t04_cleanup_preserves_foreign_stage_authority_and_payload(tmp_path: Path, foreign_part: str) -> None:
    workspace = (tmp_path / f"foreign-stage-{foreign_part}").resolve()
    workspace.mkdir()
    installed = ProviderLifecycleEngine().execute(_request(workspace, "install"), force=True)
    assert installed.status == "completed"
    request = _request(workspace, "update")
    occurrences = 0

    def fail_cleanup(point: str) -> None:
        nonlocal occurrences
        if point == "stage-entry-docs-remove":
            occurrences += 1
            if occurrences == 2:
                raise OSError("stage cleanup failed")

    first = ProviderLifecycleEngine(fault_injector=fail_cleanup).execute(request, force=True)
    assert first.status == "partial_failure"
    assert first.code == "terminal-cleanup-failed"

    namespace = resolve_private_namespace(workspace)
    stage = namespace / "STAGE"
    owner_path = stage / "STAGE-OWNER.json"
    docs_path = stage / "docs"
    if foreign_part == "owner":
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        owner["operation_generation"] = "1" * 32
        owner_path.write_text(json.dumps(owner, separators=(",", ":")) + "\n", encoding="utf-8")
        owner_path.chmod(0o600)
        expected_owner = owner_path.read_bytes()
        expected_entry = docs_path
    else:
        foreign_file = docs_path / "foreign.txt"
        foreign_file.write_text("foreign\n", encoding="utf-8")
        expected_owner = owner_path.read_bytes()
        expected_entry = foreign_file

    result = ProviderLifecycleEngine().execute(request, force=True)

    serialize_public_result(result)
    assert result.status == "partial_failure"
    assert result.code == "terminal-cleanup-failed"
    assert owner_path.read_bytes() == expected_owner
    assert expected_entry.exists()
