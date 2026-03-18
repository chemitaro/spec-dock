from __future__ import annotations

from pathlib import Path
from typing import cast

from ..domain.models import SpecGraph, SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import ActiveManifestEntry, StoredMetaRecord
from .contracts import DoctorFinding, DoctorRequest, DoctorResult
from .ports import Ports


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


def _resolve_specdock_dir(ports: Ports) -> Path:
    if ports.specdock_dir is not None:
        return ports.specdock_dir
    if ports.repo_root is not None:
        return ports.repo_root / "spec-dock"
    raise RuntimeError("specdock_dir is required")


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _finding_from_error(error_message: str) -> DoctorFinding:
    if "Duplicate id detected" in error_message or "Duplicate numeric id detected" in error_message:
        return DoctorFinding(
            code="duplicate_id",
            message=error_message,
            guidance=[
                "重複している .meta.json の id を一意に修正してください。",
                "修正後に `spec-dock/scripts/spec-dock validate` を再実行してください。",
            ],
        )
    if "Duplicate discussion sequence detected" in error_message:
        return DoctorFinding(
            code="duplicate_seq",
            message=error_message,
            guidance=[
                "対象 scope の discussions 配下で重複 sequence の markdown を整理してください。",
                "修正後に `spec-dock/scripts/spec-dock validate` を再実行してください。",
            ],
        )
    if "Missing required artifact" in error_message:
        return DoctorFinding(
            code="missing_artifact",
            message=error_message,
            guidance=[
                "欠損 artifact をテンプレートまたは履歴から復元してください。",
                "復元後に `spec-dock/scripts/spec-dock validate` を再実行してください。",
            ],
        )
    if (
        "Unsupported legacy meta.json detected" in error_message
        or ".meta.json" in error_message
    ):
        return DoctorFinding(
            code="broken_meta",
            message=error_message,
            guidance=[
                "壊れた .meta.json を JSON object と required fields が揃う状態に修復してください。",
                "修復後に `spec-dock/scripts/spec-dock validate` を再実行してください。",
            ],
        )
    return DoctorFinding(
        code="validation_error",
        message=error_message,
        guidance=[
            "validate エラーの原因を解消してください。",
            "解消後に `spec-dock/scripts/spec-dock validate` を再実行してください。",
        ],
    )


def _resolve_active_entry_path(
    entry: ActiveManifestEntry,
    *,
    specdock_dir: Path,
    repo_root: Path | None,
) -> Path | None:
    if entry.path is None or not entry.path.strip():
        return None
    raw = Path(entry.path.strip())
    current_repo_root = repo_root if repo_root is not None else specdock_dir.parent
    candidates: list[Path] = []

    if raw.is_absolute():
        try:
            rel_from_repo_root = raw.relative_to(current_repo_root)
            candidates.append(current_repo_root / rel_from_repo_root)
        except ValueError:
            pass
        parts = raw.parts
        for specdock_index in range(len(parts) - 1, -1, -1):
            if parts[specdock_index] != specdock_dir.name:
                continue
            candidates.append(current_repo_root / Path(*parts[specdock_index:]))
    else:
        candidates.append(current_repo_root / raw)

    resolved_specdock_dir = specdock_dir.resolve(strict=False)
    for candidate in candidates:
        try:
            candidate.resolve(strict=False).relative_to(resolved_specdock_dir)
        except ValueError:
            continue
        return candidate
    return None


def _stale_active_pointer_finding(
    ports: Ports,
    *,
    specdock_dir: Path,
    graph: SpecGraph | None,
    warnings: list[str],
) -> DoctorFinding | None:
    if ports.active_state_store is None:
        return None

    try:
        load_result = ports.active_state_store.load_active_manifest(specdock_dir)
    except RuntimeError as error:
        return DoctorFinding(
            code="stale_active_pointer",
            message=f"failed to load active manifest: {error}",
            guidance=[
                "`spec-dock/scripts/spec-dock active clear` で active pointer をクリアしてください。",
                "`spec-dock/scripts/spec-dock active set <target>` で active pointer を再設定してください。",
            ],
        )
    for warning in load_result.warnings:
        _append_unique(warnings, warning)

    manifest = load_result.manifest
    invalid_manifest_warnings = [
        warning
        for warning in load_result.warnings
        if warning.startswith("active_manifest_invalid_json:")
        or warning.startswith("active_manifest_invalid_shape:")
    ]
    if manifest is None:
        if invalid_manifest_warnings:
            return DoctorFinding(
                code="stale_active_pointer",
                message="; ".join(invalid_manifest_warnings),
                guidance=[
                    "`spec-dock/scripts/spec-dock active clear` で active pointer をクリアしてください。",
                    "`spec-dock/scripts/spec-dock active set <target>` で active pointer を再設定してください。",
                ],
            )
        return None

    stale_reasons: list[str] = []
    graph_ids = set(graph.nodes_by_id.keys()) if graph is not None else None
    for layer in ("initiative", "epic", "issue"):
        entry = getattr(manifest, layer)
        if entry is None:
            continue
        if graph_ids is not None and entry.id not in graph_ids:
            stale_reasons.append(f"{layer}.id={entry.id} is not found in current graph")
        resolved_path = _resolve_active_entry_path(entry, specdock_dir=specdock_dir, repo_root=ports.repo_root)
        if resolved_path is None:
            stale_reasons.append(f"{layer}.path is missing")
            continue
        if not resolved_path.exists():
            stale_reasons.append(f"{layer}.path not found: {entry.path}")
            continue
        if not resolved_path.is_dir():
            stale_reasons.append(f"{layer}.path is not a directory: {entry.path}")

    if not stale_reasons:
        return None

    return DoctorFinding(
        code="stale_active_pointer",
        message="; ".join(stale_reasons),
        guidance=[
            "`spec-dock/scripts/spec-dock active clear` で active pointer をクリアしてください。",
            "`spec-dock/scripts/spec-dock active set <target>` で active pointer を再設定してください。",
        ],
    )


def doctor(req: DoctorRequest, ports: Ports) -> DoctorResult:
    del req
    warnings: list[str] = []
    findings: list[DoctorFinding] = []
    graph: SpecGraph | None = None
    specdock_dir = _resolve_specdock_dir(ports)

    try:
        records = ports.node_reader.load_node_records()
    except RuntimeError as error:
        findings.append(_finding_from_error(str(error)))
    else:
        try:
            graph = build_graph([_to_spec_node_seed(record) for record in records])
            report = validate_graph_and_deps(graph, issue_depends_on_map=None, repo_root=ports.repo_root)
        except RuntimeError as error:
            findings.append(_finding_from_error(str(error)))
        else:
            if report.errors:
                findings.append(_finding_from_error(str(report.errors[0])))
            for warning in report.warnings:
                _append_unique(warnings, warning)

    stale_pointer = _stale_active_pointer_finding(
        ports,
        specdock_dir=specdock_dir,
        graph=graph,
        warnings=warnings,
    )
    if stale_pointer is not None:
        findings.append(stale_pointer)

    return DoctorResult(ok=(len(findings) == 0), findings=findings, warnings=warnings)
