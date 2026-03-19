from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Literal
from typing import cast

from ..domain.ids import resolve_id_input, resolve_input_title_and_slug
from ..domain.models import ActiveSelection, SpecGraph, SpecNode, SpecNodeKind
from ..domain.tree import resolve_parent_from_active
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import ActiveManifest, StoredMetaRecord
from .artifact_preflight import validate_required_artifacts_for_graph
from .contracts import CreateNodeRequest, ImportNodeRequest, ImportNodeResult
from .create_node import (
    _acquire_create_lock,
    _post_write_duplicate_guard,
    _release_create_lock,
    execute_create_plan,
    guard_github_issue_uniqueness,
    load_graph,
    plan_node_creation,
)
from .ports import Ports
from .sync_state import sync_after_import


def _resolve_specdock_dir(ports: Ports) -> Path:
    if ports.specdock_dir is not None:
        return ports.specdock_dir
    if ports.repo_root is not None:
        return ports.repo_root / "spec-dock"
    raise RuntimeError("specdock_dir is required")


def _resolve_repo_root(ports: Ports) -> Path:
    if ports.repo_root is None:
        raise RuntimeError("repo_root is required")
    return ports.repo_root


def _resolve_issue_gateway(ports: Ports):
    if ports.issue_gateway is None:
        raise RuntimeError("issue_gateway is required")
    return ports.issue_gateway


def _normalize_repo_slug_value(slug: str | None) -> str | None:
    text = str(slug or "").strip().lower()
    if not text:
        return None
    owner, sep, repo = text.partition("/")
    if not sep or not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _resolve_current_repo_slug(ports: Ports) -> str | None:
    if ports.git_gateway is None or ports.repo_root is None:
        return None
    resolver = getattr(ports.git_gateway, "origin_github_repo_slug", None)
    if not callable(resolver):
        return None
    try:
        raw = resolver(_resolve_repo_root(ports))
    except RuntimeError:
        return None
    return _normalize_repo_slug_value(raw)


def _active_selection_from_manifest(manifest: ActiveManifest | None) -> ActiveSelection:
    if manifest is None:
        return ActiveSelection(initiative_id=None, epic_id=None, issue_id=None)
    return ActiveSelection(
        initiative_id=manifest.initiative.id if manifest.initiative is not None else None,
        epic_id=manifest.epic.id if manifest.epic is not None else None,
        issue_id=manifest.issue.id if manifest.issue is not None else None,
    )


def _to_spec_node(record: StoredMetaRecord) -> SpecNode:
    return SpecNode(
        kind=cast(SpecNodeKind, record.kind),
        id=record.id,
        title=record.title,
        slug=record.slug,
        path=Path(record.path),
        meta_path=Path(record.meta_path),
        parent_id=record.parent_id,
        initiative_id=record.initiative_id,
        epic_id=record.epic_id,
        github_issue_number=record.github_issue_number,
        github_repo_owner=record.github_repo_owner,
        github_repo_name=record.github_repo_name,
    )


def resolve_parent_for_import(
    req: ImportNodeRequest,
    graph: SpecGraph,
    ports: Ports,
    *,
    kind: Literal["initiative", "epic", "issue"],
) -> str | None:
    if kind == "initiative":
        return None

    if req.parent_id is not None:
        if kind == "epic":
            parent_id = resolve_id_input(req.parent_id, prefix="init", field="initiative", nodes=graph.nodes_by_id)
            parent = graph.nodes_by_id.get(parent_id)
            if parent is None or parent.kind != "initiative":
                raise RuntimeError(f"Initiative not found: {parent_id}")
            return parent.id

        parent_id = resolve_id_input(req.parent_id, prefix="epic", field="epic", nodes=graph.nodes_by_id)
        parent = graph.nodes_by_id.get(parent_id)
        if parent is None or parent.kind != "epic":
            raise RuntimeError(f"Epic not found: {parent_id}")
        if not parent.initiative_id:
            raise RuntimeError(f"Epic meta missing initiative_id: {parent.id}")
        return parent.id

    if ports.active_state_store is None:
        raise RuntimeError("active_state_store is required for active parent fallback")

    load_result = ports.active_state_store.load_active_manifest_no_migrate(_resolve_specdock_dir(ports))
    active = _active_selection_from_manifest(load_result.manifest)
    return resolve_parent_from_active(graph, kind, active)


def build_linked_create_request(req: ImportNodeRequest, parent_id: str | None) -> CreateNodeRequest:
    owner = (req.target_repo_owner or "").strip().lower()
    repo = (req.target_repo_name or "").strip().lower()
    github_repo_owner = owner if owner and repo else None
    github_repo_name = repo if owner and repo else None
    return CreateNodeRequest(
        title=req.title,
        slug=req.slug,
        parent_id=parent_id,
        requested_node_id=None,
        github_mode="link_existing",
        github_issue_number=int(req.issue_number),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )


def _validate_url_repo_identity(
    req: ImportNodeRequest,
    *,
    current_repo_slug: str | None,
) -> None:
    owner = (req.target_repo_owner or "").strip().lower()
    repo = (req.target_repo_name or "").strip().lower()
    if not owner or not repo:
        return
    if req.allow_foreign_url:
        return

    if current_repo_slug is None:
        raise RuntimeError(
            "Cannot verify GitHub URL repository against current repo. "
            "Configure git remote.origin.url or pass '--allow-foreign-url'."
        )
    expected = f"{owner}/{repo}"
    actual = current_repo_slug
    if actual != expected:
        raise RuntimeError(
            "GitHub URL repository mismatch for import target: "
            f"target={expected}, current={actual}. "
            "Use '--allow-foreign-url' only when cross-repo import is intentional."
        )


def _target_repo_slug(req: ImportNodeRequest) -> str | None:
    owner = (req.target_repo_owner or "").strip()
    repo = (req.target_repo_name or "").strip()
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def import_node_core(
    req: ImportNodeRequest,
    ports: Ports,
    *,
    kind: Literal["initiative", "epic", "issue"],
) -> ImportNodeResult:
    title, slug = resolve_input_title_and_slug(req.title, req.slug)
    req = replace(req, title=title, slug=slug)

    current_repo_slug = _resolve_current_repo_slug(ports)
    try:
        graph = load_graph(ports, validate=False)
        report = validate_graph_and_deps(
            graph,
            repo_root=_resolve_repo_root(ports),
            current_repo_slug=current_repo_slug,
        )
        if report.errors:
            raise RuntimeError(report.errors[0])
    except RuntimeError as error:
        raise RuntimeError(f"preflight validate failed: {error}") from error
    try:
        validate_required_artifacts_for_graph(graph, repo_root=ports.repo_root)
    except RuntimeError as error:
        raise RuntimeError(f"preflight validate failed: {error}") from error

    issue_number = int(req.issue_number)
    _validate_url_repo_identity(req, current_repo_slug=current_repo_slug)
    specdock_dir = _resolve_specdock_dir(ports)
    today = ports.clock.today() if ports.clock is not None else date.today().isoformat()
    guard_github_issue_uniqueness(
        graph,
        issue_number,
        github_repo_owner=req.target_repo_owner,
        github_repo_name=req.target_repo_name,
        current_repo_slug=current_repo_slug,
    )
    precheck_parent_id = resolve_parent_for_import(req, graph, ports, kind=kind)
    precheck_req = build_linked_create_request(req, precheck_parent_id)
    precheck_plan = plan_node_creation(
        precheck_req,
        graph,
        kind=kind,
        specdock_dir=specdock_dir,
        today=today,
        current_repo_slug=current_repo_slug,
    )
    precheck_collisions = [path for path in precheck_plan.planned_paths if path.exists()]
    if precheck_collisions:
        raise RuntimeError(f"Destination already exists: {precheck_collisions[0]}")

    issue_gateway = _resolve_issue_gateway(ports)
    imported_issue = issue_gateway.issue_view_minimal(
        _resolve_repo_root(ports),
        issue_number,
        repo_slug=_target_repo_slug(req),
    )
    lock_path, lock_token = _acquire_create_lock(specdock_dir)
    result_node: SpecNode | None = None
    body_error: Exception | None = None
    try:
        graph = load_graph(ports, validate=False)
        guard_github_issue_uniqueness(
            graph,
            issue_number,
            github_repo_owner=req.target_repo_owner,
            github_repo_name=req.target_repo_name,
            current_repo_slug=current_repo_slug,
        )
        locked_parent_id = resolve_parent_for_import(req, graph, ports, kind=kind)
        create_req = build_linked_create_request(req, locked_parent_id)
        plan = plan_node_creation(
            create_req,
            graph,
            kind=kind,
            specdock_dir=specdock_dir,
            today=today,
            current_repo_slug=current_repo_slug,
        )
        execute_create_plan(plan, ports)
        _post_write_duplicate_guard(ports, node_id=plan.meta.id)
        result_node = _to_spec_node(plan.meta)
    except Exception as exc:
        body_error = exc
    finally:
        release_error: Exception | None = None
        try:
            _release_create_lock(lock_path, lock_token)
        except Exception as exc:
            release_error = exc

        if body_error is not None:
            if release_error is not None:
                raise RuntimeError(f"{body_error}; additionally {release_error}") from body_error
            raise body_error
        if release_error is not None:
            raise release_error

    if result_node is None:
        raise RuntimeError("import failed without result")

    post_import_sync = sync_after_import(ports)
    return ImportNodeResult(
        node=result_node,
        imported_issue=imported_issue,
        post_import_sync=post_import_sync,
        warnings=[],
    )


def import_initiative(req: ImportNodeRequest, ports: Ports) -> ImportNodeResult:
    return import_node_core(req, ports, kind="initiative")


def import_epic(req: ImportNodeRequest, ports: Ports) -> ImportNodeResult:
    return import_node_core(req, ports, kind="epic")


def import_issue(req: ImportNodeRequest, ports: Ports) -> ImportNodeResult:
    return import_node_core(req, ports, kind="issue")
