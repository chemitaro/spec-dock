from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SpecNodeKind = Literal["initiative", "epic", "issue"]


@dataclass(frozen=True)
class SpecNodeSeed:
    kind: SpecNodeKind
    id: str
    title: str
    slug: str
    path: Path
    meta_path: Path
    parent_id: str | None
    initiative_id: str | None
    epic_id: str | None
    github_issue_number: int | None


@dataclass(frozen=True)
class SpecNode:
    kind: SpecNodeKind
    id: str
    title: str
    slug: str
    path: Path
    meta_path: Path
    parent_id: str | None
    initiative_id: str | None
    epic_id: str | None
    github_issue_number: int | None


@dataclass(frozen=True)
class SpecGraph:
    nodes_by_id: dict[str, SpecNode]


@dataclass(frozen=True)
class ValidationReport:
    errors: list[str]
    warnings: list[str]

