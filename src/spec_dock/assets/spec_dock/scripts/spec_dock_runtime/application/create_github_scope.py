"""Create GitHub-backed Scopes with a durable remote/local effect boundary."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from spec_dock_runtime.application.create_node import (
    CreatePlanExecutionError,
    _precheck_pre_github_create_rules_sources,
    _precheck_pre_github_create_symlink_capability,
    _to_spec_node,
    execute_create_plan,
)
from spec_dock_runtime.application.github_create_effect import GithubCreateGateway, create_github_issue_effect
from spec_dock_runtime.application.github_scope_scaffold import build_github_scope_scaffold
from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.application.ports import Ports
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.ids import resolve_input_title_and_slug
from spec_dock_runtime.domain.lifecycle import GithubBackend, LocalBackend, decode_scope_metadata
from spec_dock_runtime.domain.selectors import ScopeIdSelector, ScopeKind, parse_scope_selector
from spec_dock_runtime.infra import fs_repo, git_cli, template_scaffolder
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.json_store import open_guarded_directory, read_guarded_json, read_guarded_json_at
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from spec_dock_runtime.infra.contracts import GithubIssueRecord, StoredMetaRecord


class GithubScopeGateway(GithubCreateGateway, Protocol):
    def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord: ...


@dataclass(frozen=True)
class GithubScopeCreated:
    id: str
    path: Path
    github_ref: str
    operation_id: str


def _parent_records(
    *, kind: ScopeKind, parent_id: str | None, records: dict[str, StoredMetaRecord]
) -> tuple[StoredMetaRecord, ...]:
    required = {"initiative": None, "epic": "initiative", "issue": "epic"}[kind]
    if required is None:
        if parent_id is not None:
            raise ValueError("initiative cannot have a parent")
        return ()
    if parent_id is None:
        raise ValueError(f"{kind} requires an explicit parent")
    selector = parse_scope_selector(parent_id)
    if not isinstance(selector, ScopeIdSelector) or selector.id != parent_id or selector.kind != required:
        raise ValueError(f"{kind} parent must be a canonical {required} ID")
    parent = records.get(parent_id)
    if parent is None or parent.kind != required:
        raise ValueError(f"{required} parent is missing")
    if kind == "epic":
        return (parent,)
    initiative = records.get(parent.initiative_id or "")
    if initiative is None or initiative.kind != "initiative" or parent.parent_id != initiative.id:
        raise ValueError("issue requires its matching initiative ancestor")
    return parent, initiative


def _require_open_ancestors(
    *,
    ancestors: tuple[StoredMetaRecord, ...],
    repo_root: Path,
    repository: str,
    gateway: GithubScopeGateway,
) -> tuple[int, int] | None:
    parent_meta_identity: tuple[int, int] | None = None
    for index, ancestor in enumerate(ancestors):
        loaded = read_guarded_json(Path(ancestor.meta_path))
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope ancestor metadata is missing")
        if index == 0:
            parent_meta_identity = loaded[1]
        metadata = decode_scope_metadata(loaded[0])
        if metadata.raw.get("id") != ancestor.id:
            raise ValueError("Scope ancestor identity changed")
        if isinstance(metadata.backend, LocalBackend):
            if metadata.backend.lifecycle.state != "open":
                raise ValueError("Scope ancestor is terminal")
            continue
        assert isinstance(metadata.backend, GithubBackend)
        if f"{metadata.backend.repo_owner}/{metadata.backend.repo_name}".lower() != repository.lower():
            raise ValueError("GitHub Scope ancestor belongs to a different repository")
        observed = gateway.get(repo_root, repository, metadata.backend.issue_number)
        if observed.state != "open":
            raise ValueError("GitHub Scope ancestor is not open")
    return parent_meta_identity


def create_github_scope(
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
    gateway: GithubScopeGateway,
    updated_at: str,
    lock_timeout: float = 0.0,
) -> GithubScopeCreated:
    """Validate local inputs first; never re-POST after the remote receipt is recorded."""
    normalized_title, normalized_slug = resolve_input_title_and_slug(title, slug)
    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    if not updated_at:
        raise ValueError("GitHub Scope requires an update timestamp")
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        repository = git_cli.origin_github_publication_repo_slug(repo_root)
        records = {record.id: record for record in fs_repo.load_node_records(specdock_dir)}
        ancestors = _parent_records(kind=kind, parent_id=parent_id, records=records)
        parent_meta_identity = _require_open_ancestors(
            ancestors=ancestors, repo_root=repo_root, repository=repository, gateway=gateway
        )
        parent_record = ancestors[0] if ancestors else None
        if parent_record is not None:
            parent_path = Path(parent_record.path).resolve(strict=True)
            if not parent_path.is_relative_to(specdock_dir.resolve(strict=True)):
                raise ValueError("parent Scope path is outside this workspace")
        _precheck_pre_github_create_rules_sources(kind=kind, specdock_dir=specdock_dir)
        _precheck_pre_github_create_symlink_capability(
            kind=kind, specdock_dir=specdock_dir, parent=_to_spec_node(parent_record) if parent_record else None
        )
        fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "kind": kind,
                    "title": normalized_title,
                    "slug": normalized_slug,
                    "parent": parent_id,
                    "repo": repository,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        journal = JournalStore(common_dir)
        assert control is not None
        operation = prepare_operation(
            command="scope.create",
            effect_plan=("github-create", "scaffold"),
            fixed_targets={
                "kind": kind,
                "repository": repository,
                "title": normalized_title,
                "parent": parent_id or "",
                "slug": normalized_slug,
                "updated_at": updated_at,
            },
            request_fingerprint=f"sha256:{fingerprint}",
            before_revisions={},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        with ExitStack() as anchors:
            parent_anchor_fd: int | None = None
            if parent_record is not None:
                parent_anchor_fd = open_guarded_directory(parent_path)
                anchors.callback(os.close, parent_anchor_fd)
                bound = read_guarded_json_at(parent_anchor_fd, ".meta.json")
                if bound is None or bound[1] != parent_meta_identity:
                    raise ValueError("Scope parent identity changed before GitHub create")
            journal.create(operation)
            advanced, remote = create_github_issue_effect(
                operation=operation,
                journal=journal,
                gateway=gateway,
                repo_root=repo_root,
                repository=repository,
                title=normalized_title,
                body=f"Created by SpecDock.\n\nType: {kind}\n",
            )
            create_plan, metadata_payload = build_github_scope_scaffold(
                specdock_dir=specdock_dir,
                kind=kind,
                title=normalized_title,
                slug=normalized_slug,
                parent_id=parent_id,
                parent_record=parent_record,
                repository=repository,
                issue_number=remote.number,
                today=updated_at[:10],
            )
            scope_id = create_plan.meta.id
            ports = Ports(
                node_reader=fs_repo,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                node_repo=fs_repo,
                template_scaffolder=template_scaffolder,
            )
            intent = record_effect_intent(advanced, effect_id="scaffold", kind="local", target=scope_id)
            journal.update(intent, expected_sequence=advanced.sequence)
            try:
                if any(
                    record.github_issue_number == remote.number
                    and (
                        record.github_repo_owner is None
                        or record.github_repo_name is None
                        or f"{record.github_repo_owner}/{record.github_repo_name}".lower() == repository.lower()
                    )
                    for record in records.values()
                ):
                    raise CreatePlanExecutionError(
                        phase="none", message="GitHub Issue is already linked to a local Scope"
                    )
                execute_create_plan(
                    create_plan,
                    ports,
                    metadata_writer=lambda directory_fd: fs_repo.write_meta_payload_at(directory_fd, metadata_payload),
                    parent_anchor_fd=parent_anchor_fd,
                )
            except CreatePlanExecutionError as error:
                failed = record_effect_result(
                    intent, effect_id="scaffold", status="failed" if error.phase == "none" else "unknown"
                )
                journal.update(failed, expected_sequence=intent.sequence)
                raise
            succeeded = record_effect_result(intent, effect_id="scaffold", status="succeeded")
            journal.update(succeeded, expected_sequence=intent.sequence)
            complete = replace(
                succeeded, phase="complete", terminal_status="succeeded", sequence=succeeded.sequence + 1
            )
            journal.update(complete, expected_sequence=succeeded.sequence)
            return GithubScopeCreated(
                scope_id, create_plan.dest_dir, f"gh:{repository}#{remote.number}", operation.operation_id
            )
