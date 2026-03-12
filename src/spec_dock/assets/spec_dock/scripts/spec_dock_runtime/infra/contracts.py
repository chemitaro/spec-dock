from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredMetaRecord:
    kind: str
    id: str
    title: str
    slug: str
    path: str
    parent_id: str | None
    initiative_id: str | None
    epic_id: str | None
    github_issue_number: int | None
    meta_path: str
