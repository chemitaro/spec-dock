from __future__ import annotations

import re
from pathlib import Path

from .deps import validate_deps_cycles
from .ids import parse_id, validate_lowercase, validate_slug
from .models import SpecGraph, SpecNode, ValidationReport

_DISCUSSION_DOC_FILENAME_RE = re.compile(
    r"^(?P<seq>[0-9]{3})-(?P<doc_type>adr|disc|research|note)-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)


def _meta_json_path_for_output(node: SpecNode, *, repo_root: Path | None = None) -> str:
    """Return a stable meta path for diagnostics (repo-relative when possible)."""
    meta_path = node.meta_path
    if repo_root is not None:
        try:
            return meta_path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return meta_path.as_posix()


def _normalize_repo_slug(owner: str | None, repo: str | None) -> str | None:
    normalized_owner = str(owner or "").strip().lower()
    normalized_repo = str(repo or "").strip().lower()
    if not normalized_owner or not normalized_repo:
        return None
    return f"{normalized_owner}/{normalized_repo}"


def _format_linked_github_nodes(linked: list[SpecNode], *, repo_root: Path | None = None) -> str:
    return ", ".join(
        f"{n.kind}:{n.id} ({_meta_json_path_for_output(n, repo_root=repo_root)})"
        for n in linked
    )


def _path_for_output(path: Path, *, repo_root: Path | None = None) -> str:
    if repo_root is not None:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def _normalize_repo_slug_value(slug: str | None) -> str | None:
    text = str(slug or "").strip().lower()
    if not text:
        return None
    owner, sep, repo = text.partition("/")
    if not sep or not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _github_linkage_key(
    node: SpecNode,
    *,
    current_repo_slug: str | None,
) -> tuple[str | None, int] | None:
    if node.kind not in ("initiative", "epic", "issue"):
        return None
    if node.github_issue_number is None:
        return None
    repo_slug = _normalize_repo_slug(node.github_repo_owner, node.github_repo_name) or current_repo_slug
    return (repo_slug, int(node.github_issue_number))


def _validate_discussion_sequences(graph: SpecGraph, *, repo_root: Path | None = None) -> None:
    scopes = sorted(
        (node for node in graph.nodes_by_id.values() if node.kind in ("initiative", "epic", "issue")),
        key=lambda node: (node.kind, node.id, node.path.as_posix()),
    )
    for scope in scopes:
        discussions_dir = scope.path / "discussions"
        if not discussions_dir.exists():
            continue
        by_seq: dict[int, list[Path]] = {}
        for path in sorted(discussions_dir.glob("*.md"), key=lambda p: p.as_posix()):
            matched = _DISCUSSION_DOC_FILENAME_RE.fullmatch(path.name)
            if matched is None:
                continue
            seq = int(matched.group("seq"))
            by_seq.setdefault(seq, []).append(path)
        duplicate_seqs = sorted(seq for seq, paths in by_seq.items() if len(paths) > 1)
        if not duplicate_seqs:
            continue
        dup_seq = duplicate_seqs[0]
        files = ", ".join(path.name for path in sorted(by_seq[dup_seq], key=lambda p: p.as_posix()))
        raise RuntimeError(
            "Duplicate discussion sequence detected under "
            f"{_path_for_output(discussions_dir, repo_root=repo_root)}: "
            f"seq={dup_seq:03d} files=[{files}]"
        )


def validate_github_issue_numbers_unique(
    graph: SpecGraph,
    repo_root: Path | None = None,
    *,
    current_repo_slug: str | None = None,
) -> None:
    """Ensure github linkage (`repo + issue_number`) is unique across initiative/epic/issue nodes."""
    normalized_current_repo_slug = _normalize_repo_slug_value(current_repo_slug)
    by_linkage: dict[tuple[str | None, int], list[SpecNode]] = {}
    by_issue_number: dict[int, list[tuple[SpecNode, str | None, str | None]]] = {}
    for node in graph.nodes_by_id.values():
        explicit_repo_slug = _normalize_repo_slug(node.github_repo_owner, node.github_repo_name)
        key = _github_linkage_key(node, current_repo_slug=normalized_current_repo_slug)
        if key is None:
            continue
        by_linkage.setdefault(key, []).append(node)
        _repo_slug, issue_number = key
        by_issue_number.setdefault(issue_number, []).append((node, explicit_repo_slug, _repo_slug))

    # Fail closed: when current repo is unknown, mixing scoped and unscoped linkage for
    # the same issue number can represent duplicate logical linkage.
    if normalized_current_repo_slug is None:
        for issue_number in sorted(by_issue_number.keys()):
            linked_rows = by_issue_number[issue_number]
            has_explicit = any(explicit_repo_slug is not None for _, explicit_repo_slug, _ in linked_rows)
            has_unscoped = any(effective_repo_slug is None for _, _, effective_repo_slug in linked_rows)
            if not (has_explicit and has_unscoped):
                continue
            linked = sorted(
                [node for node, _explicit_repo_slug, _effective_repo_slug in linked_rows],
                key=lambda n: (n.kind, n.id, _meta_json_path_for_output(n, repo_root=repo_root)),
            )
            found = _format_linked_github_nodes(linked, repo_root=repo_root)
            raise RuntimeError(
                "Ambiguous github.linkage scope detected (fail-closed): "
                f"repo=(current-or-unknown) github.issue_number={issue_number} has both "
                f"scoped and unscoped linkage: {found}. "
                "Configure current repo remote (origin) or normalize linkage scope to restore uniqueness."
            )

    for repo_slug, issue_number in sorted(by_linkage.keys(), key=lambda item: (item[0] or "", item[1])):
        linked = sorted(
            by_linkage[(repo_slug, issue_number)],
            key=lambda n: (n.kind, n.id, _meta_json_path_for_output(n, repo_root=repo_root)),
        )
        if len(linked) <= 1:
            continue
        found = _format_linked_github_nodes(linked, repo_root=repo_root)
        repo_label = repo_slug if repo_slug is not None else "(current-or-unknown)"
        raise RuntimeError(
            f"Duplicate github.linkage detected: repo={repo_label} github.issue_number={issue_number} "
            f"is linked by multiple nodes: {found}. "
            "Fix github linkage in one of the listed .meta.json files to restore uniqueness."
        )


def validate_graph(
    graph: SpecGraph,
    repo_root: Path | None = None,
    *,
    current_repo_slug: str | None = None,
) -> ValidationReport:
    """Validate structural integrity and return accumulated errors/warnings."""
    try:
        _validate_graph_or_raise(
            graph,
            repo_root=repo_root,
            current_repo_slug=current_repo_slug,
        )
    except RuntimeError as e:
        return ValidationReport(errors=[str(e)], warnings=[])
    return ValidationReport(errors=[], warnings=[])


def validate_graph_and_deps(
    graph: SpecGraph,
    issue_depends_on_map: dict[str, list[str]] | None = None,
    repo_root: Path | None = None,
    *,
    current_repo_slug: str | None = None,
) -> ValidationReport:
    """Validate the graph and dependency-related preconditions."""
    report = validate_graph(
        graph,
        repo_root=repo_root,
        current_repo_slug=current_repo_slug,
    )
    if report.errors:
        return report
    if issue_depends_on_map is None:
        return report
    try:
        validate_deps_cycles(issue_depends_on_map)
    except RuntimeError as e:
        return ValidationReport(errors=[str(e)], warnings=[])
    return report


def _validate_graph_or_raise(
    graph: SpecGraph,
    *,
    repo_root: Path | None = None,
    current_repo_slug: str | None = None,
) -> None:
    numeric_ids: dict[tuple[str, bool, int], list[str]] = {}
    for node_id in graph.nodes_by_id.keys():
        prefix, is_local, num = parse_id(str(node_id))
        numeric_ids.setdefault((prefix, is_local, num), []).append(str(node_id))

    for (prefix, is_local, num), ids in sorted(numeric_ids.items()):
        uniq = sorted(set(ids))
        if len(uniq) > 1:
            marker = "-local" if is_local else ""
            raise RuntimeError(
                f"Duplicate numeric id detected: {prefix}{marker}-{num} matches multiple ids: {', '.join(uniq)}"
            )

    validate_github_issue_numbers_unique(
        graph,
        repo_root=repo_root,
        current_repo_slug=current_repo_slug,
    )
    _validate_discussion_sequences(graph, repo_root=repo_root)

    for node_id, node in graph.nodes_by_id.items():
        validate_lowercase(node_id, field="id")
        parse_id(node_id)
        if not node.title:
            raise RuntimeError(f"Missing title in .meta.json: {node.meta_path}")
        if not node.slug:
            raise RuntimeError(f"Missing slug in .meta.json: {node.meta_path}")
        validate_slug(node.slug, field="slug")

        if node.kind == "initiative":
            if node.parent_id is not None:
                raise RuntimeError(f"initiative parent_id must be null: {node.id}")
            if node.initiative_id is not None or node.epic_id is not None:
                raise RuntimeError(f"initiative must not have initiative_id/epic_id: {node.id}")
            continue

        if node.kind == "epic":
            if not node.parent_id:
                raise RuntimeError(f"epic missing parent_id: {node.meta_path}")
            if not node.initiative_id:
                raise RuntimeError(f"epic missing initiative_id: {node.meta_path}")
            if node.parent_id != node.initiative_id:
                raise RuntimeError(
                    f"epic parent_id mismatch: {node.id} parent_id={node.parent_id} initiative_id={node.initiative_id}"
                )
            parent = graph.nodes_by_id.get(node.parent_id)
            if not parent or parent.kind != "initiative":
                raise RuntimeError(f"epic points to invalid parent initiative: {node.parent_id}")
            continue

        if node.kind == "issue":
            if not node.parent_id:
                raise RuntimeError(f"issue missing parent_id: {node.meta_path}")
            if not node.initiative_id or not node.epic_id:
                raise RuntimeError(f"issue missing initiative_id/epic_id: {node.meta_path}")
            if node.parent_id != node.epic_id:
                raise RuntimeError(
                    f"issue parent_id mismatch: {node.id} parent_id={node.parent_id} epic_id={node.epic_id}"
                )
            epic = graph.nodes_by_id.get(node.epic_id)
            if not epic or epic.kind != "epic":
                raise RuntimeError(f"issue points to invalid epic_id: {node.epic_id}")
            initiative = graph.nodes_by_id.get(node.initiative_id)
            if not initiative or initiative.kind != "initiative":
                raise RuntimeError(f"issue points to invalid initiative_id: {node.initiative_id}")
            if epic.initiative_id and epic.initiative_id != node.initiative_id:
                raise RuntimeError(
                    f"issue initiative_id mismatch: {node.id} initiative_id={node.initiative_id} but epic {epic.id} initiative_id={epic.initiative_id}"
                )
            continue

        raise RuntimeError(f"Unknown node type: {node.kind} ({node.meta_path})")
