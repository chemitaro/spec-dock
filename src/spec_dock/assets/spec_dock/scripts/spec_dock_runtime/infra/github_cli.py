from __future__ import annotations

from pathlib import Path

from ..domain.models import IssueSnapshot
from ..github import _gh_issue_create
from ..github import _gh_issue_index
from ..github import _gh_issue_view_minimal


def issue_index(repo_root: Path, *, limit: int) -> list[IssueSnapshot]:
    index = _gh_issue_index(repo_root, limit=limit)
    snapshots: list[IssueSnapshot] = []
    for item in index.values():
        snapshots.append(
            IssueSnapshot(
                issue_number=int(item.get("number")),
                state=str(item.get("state", "")),
                title=str(item.get("title", "")),
                labels=[
                    str(label.get("name", ""))
                    for label in (item.get("labels") or [])
                    if isinstance(label, dict)
                ],
                updated_at=str(item.get("updatedAt", "")),
                url=str(item.get("url", "")),
            )
        )
    return snapshots


def issue_create(repo_root: Path, title: str, body: str) -> int:
    return _gh_issue_create(repo_root, title=title, body=body)


def issue_view_minimal(repo_root: Path, issue_number: int) -> IssueSnapshot:
    raw = _gh_issue_view_minimal(repo_root, issue_number=issue_number)
    return IssueSnapshot(
        issue_number=int(raw.get("number")),
        state=str(raw.get("state", "")),
        title=str(raw.get("title", "")),
        labels=[],
        updated_at=str(raw.get("updatedAt", "")),
        url=str(raw.get("url", "")),
    )
