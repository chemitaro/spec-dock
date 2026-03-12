from __future__ import annotations

from pathlib import Path

from ..domain.models import IssueSnapshot
from ..github import _gh_issue_index


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
