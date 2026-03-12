from __future__ import annotations

import json

from ..application.contracts import SyncStateResult
from ..render_md import _render_dashboard_md
from ..render_md import _render_deps_disabled_dashboard_md
from .contracts import DashboardArtifact
from .json_state import render_index_artifact


def render_dashboard(result: SyncStateResult, *, top_limit: int = 10) -> DashboardArtifact:
    if result.deps_preflight_error is not None:
        text = _render_deps_disabled_dashboard_md(error=result.deps_preflight_error)
        return DashboardArtifact(markdown_text=text if text.endswith("\n") else text + "\n")

    index_artifact = render_index_artifact(result)
    index_payload = json.loads(index_artifact.all_json_text)
    nodes = index_payload.get("nodes") if isinstance(index_payload, dict) else {}
    active = index_payload.get("active") if isinstance(index_payload, dict) else None
    if not isinstance(nodes, dict):
        nodes = {}
    text = _render_dashboard_md(nodes, active=active if isinstance(active, dict) else None, top_limit=top_limit)
    return DashboardArtifact(markdown_text=text if text.endswith("\n") else text + "\n")
