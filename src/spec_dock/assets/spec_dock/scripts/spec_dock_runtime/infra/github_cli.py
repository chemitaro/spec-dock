from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..domain.models import IssueSnapshot

_GH_ISSUE_URL_RE = re.compile(r"/issues/(?P<num>[0-9]+)\b")


def ensure_gh_available() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError(
            "'gh' CLI not found. Install GitHub CLI (gh), or use '--no-github' for 'new', or omit '--github' for 'sync'."
        )


def issue_index_raw(repo_root: Path, *, limit: int) -> dict[int, dict[str, Any]]:
    ensure_gh_available()
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        "all",
        "--limit",
        str(limit),
        "--json",
        "number,state,title,labels,updatedAt,url",
    ]
    try:
        p = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e

    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"gh returned invalid JSON: {' '.join(cmd)}") from e
    if not isinstance(data, list):
        raise RuntimeError(f"gh returned invalid JSON payload (expected a list): {' '.join(cmd)}")

    index: dict[int, dict[str, Any]] = {}
    for item in data:
        try:
            number = int(item.get("number"))
        except (TypeError, ValueError):
            continue
        index[number] = item
    return index


def issue_create_raw(repo_root: Path, *, title: str, body: str) -> int:
    ensure_gh_available()
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    try:
        p = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e

    out = f"{(p.stdout or '').strip()}\n{(p.stderr or '').strip()}".strip()
    m = _GH_ISSUE_URL_RE.search(out)
    if not m:
        raise RuntimeError(f"Failed to parse issue number from gh output:\n{out}")
    return int(m.group("num"))


def issue_view_minimal_raw(repo_root: Path, *, issue_number: int) -> dict[str, Any]:
    ensure_gh_available()
    cmd = ["gh", "issue", "view", str(issue_number), "--json", "number,url"]
    try:
        p = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e

    try:
        data = json.loads((p.stdout or "").strip())
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from gh issue view for issue #{issue_number}") from e
    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid gh issue view payload for issue #{issue_number}")

    try:
        number = int(data.get("number"))
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Invalid gh issue view payload: number={data.get('number')}") from e
    if number != issue_number:
        raise RuntimeError(f"gh issue view returned mismatched number: expected {issue_number}, got {number}")
    return data


def issue_index(repo_root: Path, *, limit: int) -> list[IssueSnapshot]:
    index = issue_index_raw(repo_root, limit=limit)
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
    return issue_create_raw(repo_root, title=title, body=body)


def issue_view_minimal(repo_root: Path, issue_number: int) -> IssueSnapshot:
    raw = issue_view_minimal_raw(repo_root, issue_number=issue_number)
    return IssueSnapshot(
        issue_number=int(raw.get("number")),
        state=str(raw.get("state", "")),
        title=str(raw.get("title", "")),
        labels=[],
        updated_at=str(raw.get("updatedAt", "")),
        url=str(raw.get("url", "")),
    )
