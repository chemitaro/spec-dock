from __future__ import annotations

import os
import re
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Literal
from typing import cast

from ..domain.ids import (
    find_existing_id_by_num,
    format_id,
    normalize_local_id_input,
    parse_id,
    resolve_id_input,
    resolve_input_title_and_slug,
    slugify,
    validate_input_slug_kebab,
)
from ..domain.models import SpecGraph, SpecNode, SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import StoredMetaRecord
from .contracts import (
    CreateDiscussionDocRequest,
    CreateDiscussionDocResult,
    CreateNodeRequest,
    CreateNodeResult,
    CreatePlan,
)
from .ports import Ports

_META_FILENAME = ".meta.json"
_DISCUSSION_DOC_TYPES = ("adr", "disc", "research", "note")
_DISCUSSION_DOC_FILENAME_RE = re.compile(
    r"^(?P<seq>[0-9]{3})-(?P<doc_type>adr|disc|research|note)-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)


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


def _resolve_node_repo(ports: Ports):
    if ports.node_repo is not None:
        return ports.node_repo

    if ports.node_reader is None:
        raise RuntimeError("node_repo is required")

    class _NodeRepoAdapter:
        def __init__(self, reader):
            self._reader = reader

        def load_node_records(self, specdock_dir: Path):
            try:
                return self._reader.load_node_records(specdock_dir)
            except TypeError:
                return self._reader.load_node_records()

        def write_meta(self, dest_dir: Path, record: StoredMetaRecord) -> None:
            writer = getattr(self._reader, "write_meta", None)
            if writer is None:
                raise RuntimeError("node_repo.write_meta is required")
            writer(dest_dir, record)

    return _NodeRepoAdapter(ports.node_reader)


def _resolve_template_scaffolder(ports: Ports):
    if ports.template_scaffolder is None:
        raise RuntimeError("template_scaffolder is required")
    return ports.template_scaffolder


def _to_spec_node_seed(record: StoredMetaRecord) -> SpecNodeSeed:
    return SpecNodeSeed(
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
    )


def load_graph(ports: Ports, *, validate: bool) -> SpecGraph:
    specdock_dir = _resolve_specdock_dir(ports)
    node_repo = _resolve_node_repo(ports)
    records = node_repo.load_node_records(specdock_dir)
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    if validate:
        repo_root = _resolve_repo_root(ports)
        report = validate_graph_and_deps(graph, repo_root=repo_root)
        if report.errors:
            raise RuntimeError(report.errors[0])
    return graph


def _prefix_for_kind(kind: Literal["initiative", "epic", "issue"]) -> str:
    if kind == "initiative":
        return "init"
    if kind == "epic":
        return "epic"
    return "iss"


def _resolve_github_mode(
    req: CreateNodeRequest, kind: Literal["initiative", "epic", "issue"]
) -> Literal["create", "link_existing", "local_only"]:
    if req.github_mode is None:
        return "create" if kind == "issue" else "local_only"
    if req.github_mode not in ("create", "link_existing", "local_only"):
        raise RuntimeError(f"Unsupported github mode: {req.github_mode}")
    return req.github_mode


def _next_id(graph: SpecGraph, prefix: str, *, local: bool) -> str:
    max_num = 0
    for node_id in graph.nodes_by_id:
        try:
            parsed_prefix, is_local, num = parse_id(str(node_id))
        except RuntimeError:
            continue
        if parsed_prefix != prefix:
            continue
        if is_local != local:
            continue
        max_num = max(max_num, num)
    return format_id(prefix, max_num + 1, local=local)


def resolve_parent_for_create(
    req: CreateNodeRequest,
    graph: SpecGraph,
    *,
    kind: Literal["initiative", "epic", "issue"],
) -> str | None:
    if kind == "initiative":
        return None

    if kind == "epic":
        if req.parent_id is None:
            raise RuntimeError("--initiative is required")
        parent_id = resolve_id_input(req.parent_id, prefix="init", field="initiative", nodes=graph.nodes_by_id)
        parent = graph.nodes_by_id.get(parent_id)
        if parent is None or parent.kind != "initiative":
            raise RuntimeError(f"Initiative not found: {parent_id}")
        return parent.id

    if req.parent_id is None:
        raise RuntimeError("--epic is required")
    parent_id = resolve_id_input(req.parent_id, prefix="epic", field="epic", nodes=graph.nodes_by_id)
    parent = graph.nodes_by_id.get(parent_id)
    if parent is None or parent.kind != "epic":
        raise RuntimeError(f"Epic not found: {parent_id}")
    if not parent.initiative_id:
        raise RuntimeError(f"Epic meta missing initiative_id: {parent.id}")
    return parent.id


def guard_github_issue_uniqueness(graph: SpecGraph, github_issue_number: int | None) -> None:
    if github_issue_number is None:
        return
    linked = [
        node
        for node in graph.nodes_by_id.values()
        if node.kind in ("initiative", "epic", "issue")
        and node.github_issue_number == int(github_issue_number)
    ]
    if not linked:
        return
    linked = sorted(linked, key=lambda node: (node.kind, node.id, node.meta_path.as_posix()))
    found = ", ".join(f"{node.kind}:{node.id} ({node.meta_path.as_posix()})" for node in linked)
    raise RuntimeError(
        f"github.issue_number={int(github_issue_number)} is already linked: {found}. "
        "Fix github.issue_number in one of the listed .meta.json files, "
        "or choose a different GitHub issue number (target)."
    )


def _scaffold_file_paths(template_dir: Path, dest_dir: Path) -> list[Path]:
    if not template_dir.exists() or not template_dir.is_dir():
        raise RuntimeError(f"Missing template directory: {template_dir}")
    files: list[Path] = []
    for src_path in sorted(template_dir.rglob("*"), key=lambda p: p.as_posix()):
        if src_path.is_file():
            files.append(dest_dir / src_path.relative_to(template_dir))
    return files


def _replacements(
    *,
    kind: Literal["initiative", "epic", "issue"],
    node_id: str,
    title: str,
    parent_id: str | None,
    initiative_id: str | None,
    github_issue_number: int | None,
    today: str,
) -> dict[str, str]:
    issue_ref = f"#{github_issue_number}" if github_issue_number is not None else ""
    common = {
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": today,
    }
    if kind == "initiative":
        return {
            "<INIT_ID>": node_id,
            "<INIT_TITLE>": title,
            "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
            **common,
        }
    if kind == "epic":
        assert parent_id is not None
        return {
            "<EPIC_ID>": node_id,
            "<EPIC_TITLE>": title,
            "<INIT_ID>": parent_id,
            "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
            **common,
        }
    assert parent_id is not None and initiative_id is not None
    return {
        "<ISS_ID>": node_id,
        "<ISS_TITLE>": title,
        "<FEATURE_ID>": node_id,
        "<FEATURE_NAME>": title,
        "<EPIC_ID>": parent_id,
        "<INIT_ID>": initiative_id,
        "<ISSUE_NUMBER_OR_URL>": issue_ref,
        "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
        **common,
    }


def _resolve_dest_dir(
    *,
    kind: Literal["initiative", "epic", "issue"],
    node_id: str,
    slug: str,
    graph: SpecGraph,
    specdock_dir: Path,
    parent_id: str | None,
) -> tuple[Path, str | None, str | None]:
    if kind == "initiative":
        return specdock_dir / "initiatives" / f"{node_id}-{slug}", None, None

    assert parent_id is not None
    parent = graph.nodes_by_id.get(parent_id)
    if parent is None:
        raise RuntimeError(f"Parent not found: {parent_id}")

    if kind == "epic":
        return parent.path / "epics" / f"{node_id}-{slug}", parent.id, None

    if not parent.initiative_id:
        raise RuntimeError(f"Epic meta missing initiative_id: {parent.id}")
    return parent.path / "issues" / f"{node_id}-{slug}", parent.initiative_id, parent.id


def plan_node_creation(
    req: CreateNodeRequest,
    graph: SpecGraph,
    *,
    kind: Literal["initiative", "epic", "issue"],
    specdock_dir: Path,
    today: str,
) -> CreatePlan:
    title, slug = resolve_input_title_and_slug(req.title, req.slug)
    mode = _resolve_github_mode(req, kind)
    prefix = _prefix_for_kind(kind)

    if mode in ("create", "link_existing"):
        if req.requested_node_id is not None:
            raise RuntimeError(
                "Cannot combine '--id' with GitHub mode. Omit GitHub flags (or use '--no-github') to create local ids."
            )
        if req.github_issue_number is None:
            raise RuntimeError("github_issue_number is required for github mode")
        node_id = format_id(prefix, int(req.github_issue_number), local=False)
        guard_github_issue_uniqueness(graph, int(req.github_issue_number))
    else:
        if req.github_issue_number is not None:
            raise RuntimeError("Cannot combine '--no-github' with '--github-issue'.")
        if req.requested_node_id is None:
            node_id = _next_id(graph, prefix, local=True)
        else:
            node_id = normalize_local_id_input(str(req.requested_node_id), prefix=prefix, field="id")

    parsed_prefix, is_local, num = parse_id(node_id)
    existing_id = find_existing_id_by_num(graph.nodes_by_id, prefix=parsed_prefix, num=num, local=is_local)
    if existing_id:
        existing = graph.nodes_by_id[existing_id]
        raise RuntimeError(f"id already exists: {existing_id} ({existing.meta_path})")

    parent_id = resolve_parent_for_create(req, graph, kind=kind)
    dest_dir, initiative_id, epic_id = _resolve_dest_dir(
        kind=kind,
        node_id=node_id,
        slug=slug,
        graph=graph,
        specdock_dir=specdock_dir,
        parent_id=parent_id,
    )
    replacements = _replacements(
        kind=kind,
        node_id=node_id,
        title=title,
        parent_id=parent_id,
        initiative_id=initiative_id,
        github_issue_number=req.github_issue_number,
        today=today,
    )
    template_dir = specdock_dir / "templates" / kind
    planned_paths = _scaffold_file_paths(template_dir, dest_dir)
    planned_paths.append(dest_dir / _META_FILENAME)
    meta_path = dest_dir / _META_FILENAME
    return CreatePlan(
        meta=StoredMetaRecord(
            kind=kind,
            id=node_id,
            title=title,
            slug=slug,
            path=dest_dir.as_posix(),
            parent_id=parent_id,
            initiative_id=initiative_id,
            epic_id=epic_id,
            github_issue_number=req.github_issue_number,
            meta_path=meta_path.as_posix(),
        ),
        dest_dir=dest_dir,
        replacements=replacements,
        planned_paths=planned_paths,
    )


def _resolve_template_dir(plan: CreatePlan) -> Path:
    for parent in [plan.dest_dir, *plan.dest_dir.parents]:
        if parent.name == "spec-dock":
            return parent / "templates" / plan.meta.kind
    raise RuntimeError(f"spec-dock root not found from destination: {plan.dest_dir}")


def execute_create_plan(plan: CreatePlan, ports: Ports) -> list[Path]:
    node_repo = _resolve_node_repo(ports)
    template_scaffolder = _resolve_template_scaffolder(ports)

    collisions = [path for path in plan.planned_paths if path.exists()]
    if collisions:
        raise RuntimeError(f"Destination already exists: {collisions[0]}")

    template_dir = _resolve_template_dir(plan)
    created_paths = template_scaffolder.copy_scaffolded_tree(
        src_dir=template_dir,
        dest_dir=plan.dest_dir,
        replacements=plan.replacements,
    )
    node_repo.write_meta(plan.dest_dir, plan.meta)
    return [*created_paths, Path(plan.meta.meta_path)]


def _resolve_scope_node(req: CreateDiscussionDocRequest, graph: SpecGraph) -> SpecNode:
    scope_node_id = req.scope_node_id
    if req.scope_kind is not None:
        scope_prefix = _prefix_for_kind(req.scope_kind)
        scope_node_id = resolve_id_input(
            req.scope_node_id,
            prefix=scope_prefix,
            field=f"--{req.scope_kind}",
            nodes=graph.nodes_by_id,
        )

    scope = graph.nodes_by_id.get(scope_node_id)
    if scope is None:
        raise RuntimeError(f"Scope node not found: {scope_node_id}")
    if req.scope_kind is not None and scope.kind != req.scope_kind:
        raise RuntimeError(f"Scope kind mismatch: expected {req.scope_kind}, got {scope.kind}")
    if scope.kind not in ("initiative", "epic", "issue"):
        raise RuntimeError(f"Unsupported scope kind for discussion docs: {scope.kind}")
    return scope


def _normalize_discussion_doc_inputs(req: CreateDiscussionDocRequest) -> tuple[str, str, str]:
    doc_type = str(req.doc_type).strip().lower()
    if doc_type not in _DISCUSSION_DOC_TYPES:
        allowed = ", ".join(_DISCUSSION_DOC_TYPES)
        raise RuntimeError(f"Unknown discussion doc type: {doc_type} (allowed: {allowed})")

    title = str(req.title).strip()
    if not title:
        raise RuntimeError("--title is required")

    slug = str(req.slug).strip() if req.slug is not None else slugify(title)
    if not slug:
        raise RuntimeError("Failed to derive slug from title. Pass --slug explicitly.")
    slug = validate_input_slug_kebab(slug, field="--slug")
    return doc_type, title, slug


def _scan_discussion_sequence_sources(discussions_dir: Path) -> list[tuple[int, str, Path]]:
    refs: list[tuple[int, str, Path]] = []
    if not discussions_dir.exists():
        return refs
    for path in sorted(discussions_dir.glob("*.md"), key=lambda p: p.as_posix()):
        matched = _DISCUSSION_DOC_FILENAME_RE.fullmatch(path.name)
        if not matched:
            continue
        refs.append((int(matched.group("seq")), str(matched.group("doc_type")), path))
    return refs


def _next_discussion_doc_seq(discussions_dir: Path) -> int:
    refs = _scan_discussion_sequence_sources(discussions_dir)
    if not refs:
        return 1

    max_seq = 0
    by_seq: dict[int, list[Path]] = {}
    for seq, _doc_type, path in refs:
        max_seq = max(max_seq, seq)
        by_seq.setdefault(seq, []).append(path)

    duplicate_seqs = sorted(seq for seq, paths in by_seq.items() if len(paths) > 1)
    if duplicate_seqs:
        dup_seq = duplicate_seqs[0]
        files = ", ".join(path.name for path in sorted(by_seq[dup_seq], key=lambda p: p.as_posix()))
        raise RuntimeError(
            f"Duplicate discussion sequence detected under {discussions_dir}: seq={dup_seq:03d} files=[{files}]"
        )

    next_seq = max_seq + 1
    if next_seq > 999:
        raise RuntimeError(
            "Discussion sequence overflow: next sequence would exceed 999. "
            "Create a follow-up issue to decide whether to archive old discussion docs or extend sequence width."
        )
    return next_seq


def _resolve_specdock_root(path: Path) -> Path:
    for current in [path, *path.parents]:
        if current.name == "spec-dock":
            return current
    raise RuntimeError(f"spec-dock root not found from scope path: {path}")


def _doc_id_from_path(path: Path) -> str:
    matched = _DISCUSSION_DOC_FILENAME_RE.fullmatch(path.name)
    if matched is None:
        raise RuntimeError(f"Invalid discussion document filename: {path.name}")
    return f"{matched.group('seq')}-{matched.group('doc_type')}"


def plan_discussion_doc(
    req: CreateDiscussionDocRequest,
    graph: SpecGraph,
    *,
    today: str | None = None,
) -> tuple[Path, Path, dict[str, str]]:
    scope = _resolve_scope_node(req, graph)
    doc_type, title, slug = _normalize_discussion_doc_inputs(req)

    specdock_dir = _resolve_specdock_root(scope.path)
    template_path = specdock_dir / "templates" / "discussions" / f"{doc_type}.md"
    discussions_dir = scope.path / "discussions"
    seq = _next_discussion_doc_seq(discussions_dir)
    seq_text = f"{seq:03d}"
    doc_id = f"{seq_text}-{doc_type}"
    dest_path = discussions_dir / f"{seq_text}-{doc_type}-{slug}.md"
    if dest_path.exists():
        raise RuntimeError(f"Discussion doc already exists: {dest_path}")

    replacements = {
        "<ADR_ID>": doc_id,
        "<ADR_TITLE>": title,
        "<DISC_ID>": doc_id,
        "<DISC_TITLE>": title,
        "<RESEARCH_ID>": doc_id,
        "<RESEARCH_TITLE>": title,
        "<NOTE_ID>": doc_id,
        "<NOTE_TITLE>": title,
        "<SCOPE_ID>": scope.id,
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": today if today is not None else date.today().isoformat(),
    }
    return template_path, dest_path, replacements


def create_discussion_doc(req: CreateDiscussionDocRequest, ports: Ports) -> CreateDiscussionDocResult:
    template_scaffolder = _resolve_template_scaffolder(ports)
    graph = load_graph(ports, validate=False)
    today = ports.clock.today() if ports.clock is not None else date.today().isoformat()
    template_path, dest_path, replacements = plan_discussion_doc(req, graph, today=today)

    template_text = template_scaffolder.load_template_text(template_path)
    rendered_text = template_scaffolder.render_text(template_text, replacements)
    template_scaffolder.write_text(dest_path, rendered_text)
    doc_id = _doc_id_from_path(dest_path)

    return CreateDiscussionDocResult(
        doc_id=doc_id,
        doc_type=doc_id.split("-", 1)[1],
        scope_node_id=replacements["<SCOPE_ID>"],
        path=dest_path,
        warnings=[],
    )


def _github_issue_body(
    *,
    kind: Literal["initiative", "epic", "issue"],
    graph: SpecGraph,
    req: CreateNodeRequest,
) -> str:
    if kind == "initiative":
        return (
            "Created by spec-dock.\n\n"
            "Type: initiative\n"
            "Local specs are stored under `spec-dock/initiatives/`.\n"
        )

    parent_id = resolve_parent_for_create(req, graph, kind=kind)
    if parent_id is None:
        raise RuntimeError("parent is required")
    if kind == "epic":
        return (
            "Created by spec-dock.\n\n"
            "Type: epic\n"
            f"Initiative: {parent_id}\n\n"
            "Local specs are stored under `spec-dock/initiatives/`.\n"
        )

    epic = graph.nodes_by_id.get(parent_id)
    if epic is None or not epic.initiative_id:
        raise RuntimeError(f"Epic not found: {parent_id}")
    return (
        "Created by spec-dock.\n\n"
        "Type: issue\n"
        f"Epic: {epic.id}\n"
        f"Initiative: {epic.initiative_id}\n\n"
        "Local specs are stored under `spec-dock/initiatives/`.\n"
    )


def create_node_core(
    req: CreateNodeRequest,
    ports: Ports,
    *,
    kind: Literal["initiative", "epic", "issue"],
) -> CreateNodeResult:
    graph = load_graph(ports, validate=False)
    mode = _resolve_github_mode(req, kind)
    title, _slug = resolve_input_title_and_slug(req.title, req.slug)
    github_issue_number = req.github_issue_number

    if mode == "create" and github_issue_number is None:
        if ports.issue_gateway is None:
            raise RuntimeError("issue_gateway is required for github issue creation")
        repo_root = _resolve_repo_root(ports)
        github_issue_number = ports.issue_gateway.issue_create(
            repo_root,
            title=title,
            body=_github_issue_body(kind=kind, graph=graph, req=req),
        )

    if mode == "link_existing" and github_issue_number is None:
        raise RuntimeError("github_issue_number is required for link_existing mode")

    specdock_dir = _resolve_specdock_dir(ports)
    today = ports.clock.today() if ports.clock is not None else date.today().isoformat()
    plan = plan_node_creation(
        replace(
            req,
            github_mode=mode,
            github_issue_number=github_issue_number,
        ),
        graph,
        kind=kind,
        specdock_dir=specdock_dir,
        today=today,
    )
    created_paths = execute_create_plan(plan, ports)
    return CreateNodeResult(
        node=_to_spec_node(plan.meta),
        created_paths=created_paths,
        warnings=[],
    )


def create_initiative(req: CreateNodeRequest, ports: Ports) -> CreateNodeResult:
    return create_node_core(req, ports, kind="initiative")


def create_epic(req: CreateNodeRequest, ports: Ports) -> CreateNodeResult:
    return create_node_core(req, ports, kind="epic")


def create_issue(req: CreateNodeRequest, ports: Ports) -> CreateNodeResult:
    return create_node_core(req, ports, kind="issue")
