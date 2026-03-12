from __future__ import annotations

import json

from ..application.contracts import DepsCheckResult


def render_deps_check_json(result: DepsCheckResult) -> str:
    inspection = result.inspection
    payload = {
        "schema_version": 1,
        "target": inspection.target_id.value,
        "ready": bool(inspection.evaluation.ready),
        "effective_depends_on": list(inspection.effective_depends_on),
        "blockers": list(inspection.evaluation.blockers),
        "nodes": {
            node_id: {
                "state": node_state.status,
                "ready": bool(node_state.ready),
            }
            for node_id, node_state in inspection.node_states.items()
        },
        "warnings": list(result.warnings),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
