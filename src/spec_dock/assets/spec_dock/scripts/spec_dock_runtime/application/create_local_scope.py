"""Plan offline local Scope creation before reserving an ID or writing files."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.domain.ids import resolve_input_title_and_slug
from spec_dock_runtime.domain.lifecycle import GithubBackend, LocalBackend, decode_scope_metadata
from spec_dock_runtime.domain.selectors import ScopeIdSelector, ScopeKind, parse_scope_selector
from spec_dock_runtime.infra.json_store import open_guarded_directory, read_guarded_json, read_guarded_json_at

if TYPE_CHECKING:
    from spec_dock_runtime.application.contracts import CreatePlan
    from spec_dock_runtime.infra.contracts import StoredMetaRecord


@dataclass(frozen=True)
class AncestorState:
    id: str
    kind: ScopeKind
    backend: Literal["local", "github"]
    state: Literal["open", "completed", "not-planned", "unknown"]
    stale: bool
    parent_id: str | None = None

    def __post_init__(self) -> None:
        selector = parse_scope_selector(self.id)
        if not isinstance(selector, ScopeIdSelector) or selector.id != self.id or selector.kind != self.kind:
            raise ValueError("ancestor ID and kind must be canonical")
        if (self.backend == "local") != ("-local-" in self.id):
            raise ValueError("ancestor backend does not match Scope ID")


@dataclass(frozen=True)
class LocalScopePlan:
    kind: ScopeKind
    title: str
    slug: str
    parent_id: str | None
    warnings: tuple[str, ...]
    needs_network: bool = False


@dataclass(frozen=True)
class LocalScopeCreated:
    id: str
    path: Path
    operation_id: str
    warnings: tuple[str, ...]


def plan_local_scope_create(
    *,
    kind: ScopeKind,
    title: str,
    parent: AncestorState | None,
    ancestors: tuple[AncestorState, ...],
    slug: str | None = None,
) -> LocalScopePlan:
    """Require an explicit open parent and known-open ancestry without network fallback."""
    expected_parent = {"initiative": None, "epic": "initiative", "issue": "epic"}[kind]
    if expected_parent is None:
        if parent is not None or ancestors:
            raise ValueError("initiative cannot have a parent or ancestors")
    elif parent is None:
        raise ValueError(f"{kind} requires an explicit parent")
    elif parent.kind != expected_parent:
        raise ValueError(f"{kind} parent kind must be {expected_parent}")
    if kind == "issue":
        initiative_ancestors = [item for item in ancestors if item.kind == "initiative"]
        if len(initiative_ancestors) != 1 or parent is None or parent.parent_id != initiative_ancestors[0].id:
            raise ValueError("issue requires its matching initiative ancestor")
    warnings: list[str] = []
    all_ancestors = (parent, *ancestors) if parent is not None else ancestors
    seen: set[str] = set()
    for ancestor in all_ancestors:
        if ancestor.id in seen:
            continue
        seen.add(ancestor.id)
        if ancestor.state != "open":
            if ancestor.backend == "local":
                raise ValueError("local ancestor is terminal")
            raise ValueError("GitHub ancestor must have a saved open status")
        if ancestor.backend == "github" and not ancestor.stale:
            raise ValueError("GitHub ancestor requires a saved stale status observation")
        if ancestor.backend == "github" and ancestor.stale:
            warning = "ancestor status is from a stale GitHub cache"
            if warning not in warnings:
                warnings.append(warning)
    normalized_title, normalized_slug = resolve_input_title_and_slug(title, slug)
    return LocalScopePlan(kind, normalized_title, normalized_slug, parent.id if parent else None, tuple(warnings))


def _build_local_scaffold(
    *,
    specdock_dir: Path,
    scope_id: str,
    plan: LocalScopePlan,
    parent_record: StoredMetaRecord | None,
    updated_at: str,
) -> tuple[CreatePlan, dict[str, object]]:
    from spec_dock_runtime.application.contracts import CreatePlan
    from spec_dock_runtime.application.create_node import _replacements, _rules_scaffold_specs, _scaffold_file_paths
    from spec_dock_runtime.infra.contracts import StoredMetaRecord

    kind = plan.kind
    if parent_record is None:
        dest_parent = specdock_dir / "initiatives"
        initiative_id = None
        epic_id = None
    else:
        dest_parent = Path(parent_record.path) / ("epics" if kind == "epic" else "issues")
        initiative_id = parent_record.id if kind == "epic" else parent_record.initiative_id
        epic_id = parent_record.id if kind == "issue" else None
    destination = dest_parent / f"{scope_id}-{plan.slug}"
    metadata_payload: dict[str, object] = {
        "schema_version": 3,
        "type": kind,
        "id": scope_id,
        "title": plan.title,
        "slug": plan.slug,
        "parent_id": plan.parent_id,
        "initiative_id": initiative_id,
        "epic_id": epic_id,
        "depends_on": [],
        "backend": "local",
        "github": None,
        "lifecycle": {"state": "open", "revision": 0, "updated_at": updated_at},
        "revision": 0,
    }
    template_dir = specdock_dir / "templates" / kind
    paths = _scaffold_file_paths(template_dir, destination)
    paths.extend(
        link for link, _target in _rules_scaffold_specs(kind=kind, dest_dir=destination, specdock_dir=specdock_dir)
    )
    paths.append(destination / ".meta.json")
    node_record = StoredMetaRecord(
        kind=kind,
        id=scope_id,
        title=plan.title,
        slug=plan.slug,
        path=str(destination),
        parent_id=plan.parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=None,
        meta_path=str(destination / ".meta.json"),
    )
    return (
        CreatePlan(
            meta=node_record,
            dest_dir=destination,
            replacements=_replacements(
                kind=kind,
                node_id=scope_id,
                title=plan.title,
                parent_id=plan.parent_id,
                initiative_id=initiative_id,
                github_issue_number=None,
                today=updated_at[:10],
            ),
            planned_paths=paths,
        ),
        metadata_payload,
    )


def create_local_scope(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    kind: ScopeKind,
    title: str,
    parent: AncestorState | None,
    ancestors: tuple[AncestorState, ...],
    updated_at: str,
    slug: str | None = None,
    lock_timeout: float = 0.0,
) -> LocalScopeCreated:
    """Create one local Scope with a burned ID and a durable scaffold journal."""
    from spec_dock_runtime.application.create_node import CreatePlanExecutionError, execute_create_plan
    from spec_dock_runtime.application.operation_executor import (
        prepare_operation,
        record_effect_intent,
        record_effect_result,
    )
    from spec_dock_runtime.application.ports import Ports
    from spec_dock_runtime.cli.admission import admit_writer
    from spec_dock_runtime.infra import fs_repo, template_scaffolder
    from spec_dock_runtime.infra.control_store import load_control
    from spec_dock_runtime.infra.github_status_cache import cached_github_ancestor_open
    from spec_dock_runtime.infra.operation_journal import JournalStore
    from spec_dock_runtime.infra.registry_store import RegistryStore
    from spec_dock_runtime.infra.writer_lock import WriterLock

    if not updated_at:
        raise ValueError("local Scope requires an update timestamp")
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
        )
        plan = plan_local_scope_create(kind=kind, title=title, parent=parent, ancestors=ancestors, slug=slug)
        records = {record.id: record for record in fs_repo.load_node_records(specdock_dir)}
        parent_meta_identity: tuple[int, int] | None = None
        for ancestor in (parent, *ancestors):
            if ancestor is None:
                continue
            record = records.get(ancestor.id)
            if record is None or record.kind != ancestor.kind or record.parent_id != ancestor.parent_id:
                raise ValueError("parent or ancestor graph changed")
            loaded = read_guarded_json(Path(record.meta_path))
            if loaded is None or not isinstance(loaded[0], dict):
                raise ValueError("parent or ancestor metadata is missing")
            if parent is not None and ancestor.id == parent.id:
                parent_meta_identity = loaded[1]
            metadata = decode_scope_metadata(loaded[0])
            if metadata.backend.kind != ancestor.backend:
                raise ValueError("parent or ancestor backend changed")
            if isinstance(metadata.backend, LocalBackend) and metadata.backend.lifecycle.state != ancestor.state:
                raise ValueError("local parent or ancestor lifecycle changed")
            if isinstance(metadata.backend, GithubBackend):
                if ancestor.state != "open" or not ancestor.stale:
                    raise ValueError("GitHub ancestor must use a stale cached open observation")
                cached_github_ancestor_open(specdock_dir, ancestor.id, metadata.backend)
        parent_record = None
        if kind != "initiative":
            assert parent is not None
            parent_record = records[parent.id]
            parent_path = Path(parent_record.path).resolve(strict=True)
            if not parent_path.is_relative_to(specdock_dir.resolve(strict=True)):
                raise ValueError("parent Scope path is outside this workspace")
        scope_id = RegistryStore(common_dir).reserve_locked(kind=kind, repo_root=repo_root)
        create_plan, metadata_payload = _build_local_scaffold(
            specdock_dir=specdock_dir,
            scope_id=scope_id,
            plan=plan,
            parent_record=parent_record,
            updated_at=updated_at,
        )
        fingerprint = hashlib.sha256(
            json.dumps(metadata_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        ports = Ports(
            node_reader=fs_repo,
            repo_root=repo_root,
            specdock_dir=specdock_dir,
            node_repo=fs_repo,
            template_scaffolder=template_scaffolder,
        )
        with ExitStack() as anchors:
            parent_anchor_fd: int | None = None
            if parent is not None:
                parent_anchor_fd = open_guarded_directory(parent_path)
                anchors.callback(os.close, parent_anchor_fd)
                bound = read_guarded_json_at(parent_anchor_fd, ".meta.json")
                if bound is None or bound[1] != parent_meta_identity:
                    raise ValueError("Scope parent identity changed before publication")
            assert control is not None
            journal = JournalStore(common_dir)
            operation = prepare_operation(
                command="scope.create",
                effect_plan=("scaffold",),
                fixed_targets={
                    "target": scope_id,
                    "parent": plan.parent_id or "",
                    "kind": kind,
                    "title": plan.title,
                    "slug": plan.slug,
                    "updated_at": updated_at,
                },
                request_fingerprint=f"sha256:{fingerprint}",
                before_revisions={},
                engine_digest=engine_digest,
                writer_epoch=control.epoch,
            )
            journal.create(operation)
            intent = record_effect_intent(operation, effect_id="scaffold", kind="local", target=scope_id)
            journal.update(intent, expected_sequence=operation.sequence)
            try:
                execute_create_plan(
                    create_plan,
                    ports,
                    metadata_writer=lambda directory_fd: fs_repo.write_meta_payload_at(directory_fd, metadata_payload),
                    parent_anchor_fd=parent_anchor_fd,
                )
            except CreatePlanExecutionError as exc:
                failure_status = "failed" if exc.phase == "none" else "unknown"
                failed = record_effect_result(intent, effect_id="scaffold", status=failure_status)
                journal.update(failed, expected_sequence=intent.sequence)
                if failure_status == "failed":
                    terminal = replace(failed, phase="complete", terminal_status="failed", sequence=failed.sequence + 1)
                    journal.update(terminal, expected_sequence=failed.sequence)
                raise
            succeeded = record_effect_result(intent, effect_id="scaffold", status="succeeded")
            journal.update(succeeded, expected_sequence=intent.sequence)
            completed = replace(
                succeeded, phase="complete", terminal_status="succeeded", sequence=succeeded.sequence + 1
            )
            journal.update(completed, expected_sequence=succeeded.sequence)
            return LocalScopeCreated(scope_id, create_plan.dest_dir, operation.operation_id, plan.warnings)


def resume_local_scope(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    kind: ScopeKind,
    title: str,
    parent: AncestorState | None,
    ancestors: tuple[AncestorState, ...],
    slug: str | None,
    operation_id: str,
    lock_timeout: float = 0.0,
) -> LocalScopeCreated:
    """Resume the original reserved ID after reconciling its scaffold effect."""
    from spec_dock_runtime.application.operation_executor import assert_resume_request
    from spec_dock_runtime.application.resume_github_scope import resume_local_scaffold
    from spec_dock_runtime.cli.admission import admit_writer
    from spec_dock_runtime.infra import fs_repo
    from spec_dock_runtime.infra.control_store import load_control
    from spec_dock_runtime.infra.github_status_cache import cached_github_ancestor_open
    from spec_dock_runtime.infra.operation_journal import JournalStore
    from spec_dock_runtime.infra.registry_store import RegistryStore
    from spec_dock_runtime.infra.writer_lock import WriterLock

    specdock_dir = repo_root / "spec-dock"
    if specdock_dir.is_symlink() or not specdock_dir.is_dir():
        raise ValueError("SpecDock workspace root is missing or redirected")
    plan = plan_local_scope_create(kind=kind, title=title, parent=parent, ancestors=ancestors, slug=slug)
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        try:
            operation = journal.load(operation_id)
        except FileNotFoundError as error:
            raise LookupError("Scope create recovery operation does not exist") from error
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        fixed = dict(operation.fixed_targets)
        if operation.effect_plan != ("scaffold",) or not fixed.get("updated_at"):
            raise ValueError("journal is not a recoverable local Scope create")
        if any((effect.retry_of or effect.id) != "scaffold" for effect in operation.effects):
            raise ValueError("local Scope create journal has unexpected effects")
        scope_id = fixed.get("target", "")
        registry = RegistryStore(common_dir).load()[0]
        if scope_id not in registry.reserved or scope_id in registry.deleted_ids:
            raise ValueError("local Scope create reservation is missing or deleted")
        records = {record.id: record for record in fs_repo.load_node_records(specdock_dir)}
        parent_meta_identity: tuple[int, int] | None = None
        for ancestor in (parent, *ancestors):
            if ancestor is None:
                continue
            record = records.get(ancestor.id)
            if record is None or record.kind != ancestor.kind or record.parent_id != ancestor.parent_id:
                raise ValueError("parent or ancestor graph changed")
            loaded = read_guarded_json(Path(record.meta_path))
            if loaded is None or not isinstance(loaded[0], dict):
                raise ValueError("parent or ancestor metadata is missing")
            if parent is not None and ancestor.id == parent.id:
                parent_meta_identity = loaded[1]
            metadata = decode_scope_metadata(loaded[0])
            if metadata.backend.kind != ancestor.backend:
                raise ValueError("parent or ancestor backend changed")
            if isinstance(metadata.backend, LocalBackend) and metadata.backend.lifecycle.state != ancestor.state:
                raise ValueError("local parent or ancestor lifecycle changed")
            if isinstance(metadata.backend, GithubBackend):
                if ancestor.state != "open" or not ancestor.stale:
                    raise ValueError("GitHub ancestor must use a stale cached open observation")
                cached_github_ancestor_open(specdock_dir, ancestor.id, metadata.backend)
        parent_record = records[parent.id] if parent is not None else None
        if parent_record is not None and not Path(parent_record.path).resolve(strict=True).is_relative_to(
            specdock_dir.resolve(strict=True)
        ):
            raise ValueError("parent Scope path is outside this workspace")
        create_plan, metadata_payload = _build_local_scaffold(
            specdock_dir=specdock_dir,
            scope_id=scope_id,
            plan=plan,
            parent_record=parent_record,
            updated_at=fixed["updated_at"],
        )
        fingerprint = hashlib.sha256(
            json.dumps(metadata_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        assert_resume_request(
            operation,
            command="scope.create",
            fixed_targets={
                "target": scope_id,
                "parent": plan.parent_id or "",
                "kind": kind,
                "title": plan.title,
                "slug": plan.slug,
                "updated_at": fixed["updated_at"],
            },
            request_fingerprint=f"sha256:{fingerprint}",
            current_revisions={},
            engine_digest=engine_digest,
            writer_epoch=expected_epoch,
        )
        with ExitStack() as anchors:
            parent_fd: int | None = None
            if parent_record is not None:
                parent_path = Path(parent_record.path).resolve(strict=True)
                parent_fd = open_guarded_directory(parent_path)
                anchors.callback(os.close, parent_fd)
                bound = read_guarded_json_at(parent_fd, ".meta.json")
                if bound is None or bound[1] != parent_meta_identity:
                    raise ValueError("Scope parent identity changed during create recovery")
            operation = resume_local_scaffold(
                operation,
                journal=journal,
                plan=create_plan,
                metadata=metadata_payload,
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                parent_fd=parent_fd,
            )
            completed = replace(
                operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1
            )
            journal.update(completed, expected_sequence=operation.sequence)
            return LocalScopeCreated(scope_id, create_plan.dest_dir, operation_id, plan.warnings)
