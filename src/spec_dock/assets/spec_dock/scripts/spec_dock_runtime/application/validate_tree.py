from __future__ import annotations

from pathlib import Path
from typing import cast

from ..domain.models import SpecNodeKind, SpecNodeSeed
from ..domain.tree import build_graph
from ..domain.validation import validate_graph_and_deps
from ..infra.contracts import StoredMetaRecord
from .contracts import ValidateTreeRequest, ValidationResult
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


def validate_tree(req: ValidateTreeRequest, ports: Ports) -> ValidationResult:
    del req
    records = ports.node_reader.load_node_records()
    graph = build_graph([_to_spec_node_seed(record) for record in records])
    report = validate_graph_and_deps(graph, repo_root=ports.repo_root)
    return ValidationResult(report=report, checked_node_count=len(records))
