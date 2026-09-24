"""Resume a fixed GitHub Scope create without repeating its remote POST."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.create_github_scope import (
    GithubScopeCreated,
    GithubScopeGateway,
    _parent_records,
    _require_open_ancestors,
)
from spec_dock_runtime.application.create_node import CreatePlanExecutionError, execute_create_plan
from spec_dock_runtime.application.github_create_effect import operation_marker
from spec_dock_runtime.application.github_scope_scaffold import build_github_scope_scaffold
from spec_dock_runtime.application.operation_executor import (
    assert_resume_request,
    record_effect_intent,
    record_effect_observation,
    record_effect_result,
)
from spec_dock_runtime.application.ports import Ports
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.ids import resolve_input_title_and_slug
from spec_dock_runtime.domain.selectors import ScopeKind, parse_github_ref
from spec_dock_runtime.infra import fs_repo, git_cli, template_scaffolder
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.github_lifecycle import RemoteIssueError
from spec_dock_runtime.infra.json_store import open_guarded_directory, read_guarded_json, read_guarded_json_at
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from spec_dock_runtime.application.contracts import CreatePlan
    from spec_dock_runtime.domain.operation import OperationRecord
    from spec_dock_runtime.infra.contracts import GithubIssueRecord


def _fingerprint(kind: ScopeKind, title: str, slug: str, parent_id: str | None, repository: str) -> str:
    payload = {"kind": kind, "title": title, "slug": slug, "parent": parent_id, "repo": repository}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"sha256:{digest}"


def _remote_issue(
    operation: OperationRecord,
    *,
    journal: JournalStore,
    gateway: GithubScopeGateway,
    repo_root: Path,
    repository: str,
    title: str,
) -> tuple[OperationRecord, GithubIssueRecord]:
    if not operation.effects or operation.effects[0].id != "github-create":
        raise ValueError("GitHub create journal has no remote intent")
    effect = operation.effects[0]
    if effect.status == "intent":
        unknown = record_effect_result(operation, effect_id="github-create", status="unknown")
        journal.update(unknown, expected_sequence=operation.sequence)
        operation, effect = unknown, unknown.effects[0]
    if effect.status == "unknown":
        matches = gateway.find_by_marker(repo_root, repository, operation_marker(operation.operation_id))
        if len(matches) != 1:
            raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True)
        remote = matches[0]
        if (
            remote.repository.lower() != repository.lower()
            or remote.number <= 0
            or remote.state != "open"
            or remote.title != title
        ):
            raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True)
        operation_after = record_effect_observation(
            operation,
            effect_id="github-create",
            outcome="observed_applied",
            remote_ref=f"gh:{repository}#{remote.number}",
        )
        journal.update(operation_after, expected_sequence=operation.sequence)
        return operation_after, remote
    if effect.status != "succeeded" or effect.remote_ref is None:
        raise ValueError("GitHub create effect cannot be resumed")
    parsed = parse_github_ref(effect.remote_ref)
    if f"{parsed.owner}/{parsed.repo}" != repository.lower():
        raise ValueError("GitHub receipt repository differs from fixed target")
    remote = gateway.get(repo_root, repository, parsed.issue_number)
    if (
        remote.repository.lower() != repository.lower()
        or remote.number != parsed.issue_number
        or remote.state != "open"
        or remote.title != title
    ):
        raise RemoteIssueError("GITHUB_CREATE_IDENTITY_UNKNOWN", uncertain=True)
    return operation, remote


def _published_scope_matches(destination: Path, payload: dict[str, object], planned_paths: list[Path]) -> bool:
    if destination.is_symlink() or not destination.is_dir():
        return False
    loaded = read_guarded_json(destination / ".meta.json")
    return loaded is not None and loaded[0] == payload and all(os.path.lexists(path) for path in planned_paths)


def _assert_no_unfinished_transaction(destination: Path) -> None:
    parent = destination.parent
    if not parent.exists():
        return
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("Scope destination parent is redirected")
    prefix = f".{destination.name}.transaction-"
    if any(entry.name.startswith(prefix) for entry in parent.iterdir()):
        raise RuntimeError("unfinished Scope scaffold transaction requires inspection")


def resume_local_scaffold(
    operation: OperationRecord,
    *,
    journal: JournalStore,
    plan: CreatePlan,
    metadata: dict[str, object],
    repo_root: Path,
    specdock_dir: Path,
    parent_fd: int | None,
) -> OperationRecord:
    """Reconcile one scaffold effect and retry only verified absent publication."""
    local = (
        operation.effects[-1]
        if operation.effects and (operation.effects[-1].retry_of or operation.effects[-1].id) == "scaffold"
        else None
    )
    if local is not None and local.status == "intent":
        unknown = record_effect_result(operation, effect_id="scaffold", status="unknown")
        journal.update(unknown, expected_sequence=operation.sequence)
        operation, local = unknown, unknown.effects[-1]
    if local is not None and local.status == "succeeded":
        if not _published_scope_matches(plan.dest_dir, metadata, plan.planned_paths):
            raise RuntimeError("recorded Scope scaffold no longer matches its fixed operation")
    elif local is not None and local.status in ("failed", "unknown"):
        if local.status == "unknown" and _published_scope_matches(plan.dest_dir, metadata, plan.planned_paths):
            observed = record_effect_observation(operation, effect_id="scaffold", outcome="observed_applied")
        else:
            if os.path.lexists(plan.dest_dir):
                raise RuntimeError("Scope destination is occupied by unverified content")
            _assert_no_unfinished_transaction(plan.dest_dir)
            observed = record_effect_observation(operation, effect_id="scaffold", outcome="observed_not_applied")
        journal.update(observed, expected_sequence=operation.sequence)
        operation, local = observed, observed.effects[-1]
    if local is None or local.status == "not-applied":
        if os.path.lexists(plan.dest_dir):
            raise RuntimeError("Scope destination appeared before retry")
        _assert_no_unfinished_transaction(plan.dest_dir)
        intent = record_effect_intent(operation, effect_id="scaffold", kind="local", target=plan.meta.id)
        journal.update(intent, expected_sequence=operation.sequence)
        ports = Ports(
            node_reader=fs_repo,
            repo_root=repo_root,
            specdock_dir=specdock_dir,
            node_repo=fs_repo,
            template_scaffolder=template_scaffolder,
        )
        try:
            execute_create_plan(
                plan,
                ports,
                metadata_writer=lambda directory_fd: fs_repo.write_meta_payload_at(directory_fd, metadata),
                parent_anchor_fd=parent_fd,
            )
        except CreatePlanExecutionError as error:
            failed = record_effect_result(
                intent, effect_id="scaffold", status="failed" if error.phase == "none" else "unknown"
            )
            journal.update(failed, expected_sequence=intent.sequence)
            raise
        succeeded = record_effect_result(intent, effect_id="scaffold", status="succeeded")
        journal.update(succeeded, expected_sequence=intent.sequence)
        operation = succeeded
    if operation.effects[-1].status != "succeeded":
        raise RuntimeError("Scope scaffold recovery remains incomplete")
    return operation


def resume_github_scope_create(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    kind: ScopeKind,
    title: str,
    parent_id: str | None,
    slug: str | None,
    operation_id: str,
    gateway: GithubScopeGateway,
    lock_timeout: float = 0.0,
) -> GithubScopeCreated:
    """Reconcile recorded effects, then publish only an absent local scaffold."""
    normalized_title, normalized_slug = resolve_input_title_and_slug(title, slug)
    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        repository = git_cli.origin_github_publication_repo_slug(repo_root)
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        if operation.effect_plan != ("github-create", "scaffold") or not fixed.get("updated_at"):
            raise ValueError("journal is not a recoverable GitHub Scope create")
        if operation.effects and (
            operation.effects[0].id != "github-create"
            or any((effect.retry_of or effect.id) != "scaffold" for effect in operation.effects[1:])
        ):
            raise ValueError("GitHub Scope create journal has unexpected effects")
        assert_resume_request(
            operation,
            command="scope.create",
            fixed_targets={
                "kind": kind,
                "repository": repository,
                "title": normalized_title,
                "parent": parent_id or "",
                "slug": normalized_slug,
                "updated_at": fixed["updated_at"],
            },
            request_fingerprint=_fingerprint(kind, normalized_title, normalized_slug, parent_id, repository),
            current_revisions={},
            engine_digest=engine_digest,
            writer_epoch=expected_epoch,
        )
        records = {record.id: record for record in fs_repo.load_node_records(specdock_dir)}
        ancestors = _parent_records(kind=kind, parent_id=parent_id, records=records)
        parent_identity = _require_open_ancestors(
            ancestors=ancestors, repo_root=repo_root, repository=repository, gateway=gateway
        )
        parent_record = ancestors[0] if ancestors else None
        with ExitStack() as anchors:
            parent_fd: int | None = None
            if parent_record is not None:
                parent_path = Path(parent_record.path).resolve(strict=True)
                if not parent_path.is_relative_to(specdock_dir.resolve(strict=True)):
                    raise ValueError("Scope parent is outside this workspace")
                parent_fd = open_guarded_directory(parent_path)
                anchors.callback(os.close, parent_fd)
                bound = read_guarded_json_at(parent_fd, ".meta.json")
                if bound is None or bound[1] != parent_identity:
                    raise ValueError("Scope parent identity changed during recovery")
            operation, remote = _remote_issue(
                operation,
                journal=journal,
                gateway=gateway,
                repo_root=repo_root,
                repository=repository,
                title=normalized_title,
            )
            plan, metadata = build_github_scope_scaffold(
                specdock_dir=specdock_dir,
                kind=kind,
                title=normalized_title,
                slug=normalized_slug,
                parent_id=parent_id,
                parent_record=parent_record,
                repository=repository,
                issue_number=remote.number,
                today=fixed["updated_at"][:10],
            )
            if any(
                record.github_issue_number == remote.number
                and f"{record.github_repo_owner}/{record.github_repo_name}".lower() == repository.lower()
                and record.id != plan.meta.id
                for record in records.values()
            ):
                raise ValueError("GitHub Issue is linked to another local Scope")
            operation = resume_local_scaffold(
                operation,
                journal=journal,
                plan=plan,
                metadata=metadata,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                parent_fd=parent_fd,
            )
            complete = replace(
                operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1
            )
            journal.update(complete, expected_sequence=operation.sequence)
            return GithubScopeCreated(plan.meta.id, plan.dest_dir, f"gh:{repository}#{remote.number}", operation_id)
