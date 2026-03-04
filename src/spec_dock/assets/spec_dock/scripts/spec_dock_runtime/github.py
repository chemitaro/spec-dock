from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

_GH_ISSUE_URL_RE = re.compile(r"/issues/(?P<num>[0-9]+)\b")


def _ensure_gh_available() -> None:
    """Raise if GitHub CLI (`gh`) is not available in PATH."""
    if shutil.which("gh") is None:
        raise RuntimeError(
            "'gh' CLI not found. Install GitHub CLI (gh), or use '--no-github' for 'new', or omit '--github' for 'sync'."
        )


def _gh_issue_index(repo_root: Path, *, limit: int) -> dict[int, dict[str, Any]]:
    """Fetch GitHub issues via `gh` and index them by issue number."""
    _ensure_gh_available()
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
        raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{e.stderr.strip()}") from e

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


def _gh_issue_create(repo_root: Path, *, title: str, body: str) -> int:
    """Create a GitHub issue via `gh` and return its issue number."""
    _ensure_gh_available()
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


def _gh_issue_view_minimal(repo_root: Path, *, issue_number: int) -> dict[str, Any]:
    """Validate issue visibility via `gh issue view` and return minimal payload."""
    _ensure_gh_available()
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
