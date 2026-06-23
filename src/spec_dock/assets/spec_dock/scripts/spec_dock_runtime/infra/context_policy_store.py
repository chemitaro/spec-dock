from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from spec_dock_runtime.domain.context_routing import ContextRoutingPolicy, context_routing_policy_from_dict

CONTEXT_POLICY_PATH = "spec-dock/system/assurance/context-routing-policy.json"


@dataclass(frozen=True)
class ContextPolicyLoadResult:
    status: str
    policy: ContextRoutingPolicy | None
    reason: str
    details: tuple[str, ...] = ()


class ContextPolicyStore:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = Path(repo_root)

    def load(self) -> ContextPolicyLoadResult:
        path = self._repo_root / CONTEXT_POLICY_PATH
        if not path.exists() or not path.is_file():
            return ContextPolicyLoadResult(
                status="missing",
                policy=None,
                reason="context_policy_missing",
                details=(CONTEXT_POLICY_PATH,),
            )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return ContextPolicyLoadResult(
                status="invalid",
                policy=None,
                reason="context_policy_invalid",
                details=(exc.__class__.__name__,),
            )
        if not isinstance(payload, dict):
            return ContextPolicyLoadResult(
                status="invalid",
                policy=None,
                reason="context_policy_invalid",
                details=("policy root must be an object",),
            )
        try:
            policy = context_routing_policy_from_dict(payload)
        except ValueError as exc:
            return ContextPolicyLoadResult(
                status="invalid",
                policy=None,
                reason="context_policy_invalid",
                details=(str(exc),),
            )
        return ContextPolicyLoadResult(status="valid", policy=policy, reason="ok")
