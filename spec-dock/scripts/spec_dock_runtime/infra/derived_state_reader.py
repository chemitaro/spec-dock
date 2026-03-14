from __future__ import annotations

from pathlib import Path

from .json_store import load_json


def load_cached_issue_status_by_id(specdock_dir: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    agent_dir = specdock_dir / ".agent"
    state_index: dict[str, object] | None = None

    for state_index_path in (agent_dir / "index-all.json", agent_dir / "index.json"):
        if not state_index_path.is_file():
            continue
        try:
            loaded = load_json(state_index_path)
        except RuntimeError:
            continue
        if isinstance(loaded, dict):
            state_index = loaded
            break

    if not isinstance(state_index, dict):
        return out

    raw_nodes = state_index.get("nodes")
    if not isinstance(raw_nodes, dict):
        return out

    for issue_id, item in raw_nodes.items():
        if not isinstance(issue_id, str) or not isinstance(item, dict):
            continue
        raw_status = item.get("status")
        if not isinstance(raw_status, str):
            continue
        status = raw_status.strip().lower()
        if status in ("done", "open", "unknown"):
            out[issue_id] = status
    return out
