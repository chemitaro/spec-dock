"""Import an existing GitHub Issue as a local v3 Scope without remote mutation."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path

from spec_dock_runtime.application.create_github_scope import (
    GithubScopeGateway,
    _parent_records,
    _require_open_ancestors,
)
from spec_dock_runtime.application.create_node import (
    CreatePlanExecutionError,
    _precheck_pre_github_create_rules_sources,
    _precheck_pre_github_create_symlink_capability,
    _to_spec_node,
    execute_create_plan,
)
from spec_dock_runtime.application.github_scope_scaffold import build_github_scope_scaffold
from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.application.ports import Ports
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.ids import resolve_input_title_and_slug
from spec_dock_runtime.domain.selectors import ScopeKind, parse_github_ref
from spec_dock_runtime.infra import fs_repo, git_cli, template_scaffolder
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.json_store import open_guarded_directory, read_guarded_json_at
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.registry_store import RegistryStore
from spec_dock_runtime.infra.writer_lock import WriterLock


@dataclass(frozen=True)
class GithubScopeImported:
    id: str
    path: Path
    github_ref: str
    operation_id: str


def import_github_scope(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    kind: ScopeKind,
    github_ref: str,
    repo_hint: str | None,
    title: str,
    parent_id: str | None,
    slug: str | None,
    gateway: GithubScopeGateway,
    updated_at: str,
    lock_timeout: float = 0.0,
) -> GithubScopeImported:
    """Read one exact Issue, bind its repository and publish only local files."""
    normalized_title, normalized_slug = resolve_input_title_and_slug(title, slug)
    target = parse_github_ref(github_ref, repo_hint=repo_hint)
    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    if not updated_at:
        raise ValueError("GitHub Scope import requires an update timestamp")
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
        if f"{target.owner}/{target.repo}" != repository:
            raise ValueError("foreign GitHub Issue import is rejected")
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
        if any(
            record.github_issue_number == target.issue_number
            and (
                record.github_repo_owner is None
                or record.github_repo_name is None
                or f"{record.github_repo_owner}/{record.github_repo_name}".lower() == repository
            )
            for record in records.values()
        ):
            raise ValueError("GitHub Issue is already linked to a local Scope")
        remote = gateway.get(repo_root, repository, target.issue_number)
        if remote.repository.lower() != repository or remote.number != target.issue_number:
            raise ValueError("GitHub Issue identity changed during import")
        create_plan, metadata_payload = build_github_scope_scaffold(
            specdock_dir=specdock_dir,
            kind=kind,
            title=normalized_title,
            slug=normalized_slug,
            parent_id=parent_id,
            parent_record=parent_record,
            repository=repository,
            issue_number=target.issue_number,
            today=updated_at[:10],
        )
        if create_plan.meta.id in RegistryStore(common_dir).load()[0].deleted_ids:
            raise ValueError("deleted Scope ID cannot be imported again")
        fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "kind": kind,
                    "github_ref": f"gh:{repository}#{target.issue_number}",
                    "title": normalized_title,
                    "slug": normalized_slug,
                    "parent": parent_id,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        assert control is not None
        operation = prepare_operation(
            command="scope.import",
            effect_plan=("scaffold",),
            fixed_targets={
                "target": create_plan.meta.id,
                "github_ref": f"gh:{repository}#{target.issue_number}",
                "parent": parent_id or "",
                "slug": normalized_slug,
            },
            request_fingerprint=f"sha256:{fingerprint}",
            before_revisions={},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        ports = Ports(
            node_reader=fs_repo,
            repo_root=repo_root,
            specdock_dir=specdock_dir,
            node_repo=fs_repo,
            template_scaffolder=template_scaffolder,
        )
        with ExitStack() as anchors:
            parent_anchor_fd: int | None = None
            if parent_record is not None:
                parent_anchor_fd = open_guarded_directory(parent_path)
                anchors.callback(os.close, parent_anchor_fd)
                bound = read_guarded_json_at(parent_anchor_fd, ".meta.json")
                if bound is None or bound[1] != parent_meta_identity:
                    raise ValueError("Scope parent identity changed before import")
            journal = JournalStore(common_dir)
            journal.create(operation)
            intent = record_effect_intent(operation, effect_id="scaffold", kind="local", target=create_plan.meta.id)
            journal.update(intent, expected_sequence=operation.sequence)
            try:
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
                if error.phase == "none":
                    terminal = replace(failed, phase="complete", terminal_status="failed", sequence=failed.sequence + 1)
                    journal.update(terminal, expected_sequence=failed.sequence)
                raise
            succeeded = record_effect_result(intent, effect_id="scaffold", status="succeeded")
            journal.update(succeeded, expected_sequence=intent.sequence)
            terminal = replace(
                succeeded, phase="complete", terminal_status="succeeded", sequence=succeeded.sequence + 1
            )
            journal.update(terminal, expected_sequence=succeeded.sequence)
            return GithubScopeImported(
                create_plan.meta.id,
                create_plan.dest_dir,
                f"gh:{repository}#{target.issue_number}",
                operation.operation_id,
            )
