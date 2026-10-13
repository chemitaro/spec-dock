"""Human navigation links derived from the direct selection; never a selection authority."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["initiative", "epic", "issue"]
ROLES: tuple[Role, ...] = ("initiative", "epic", "issue")


@dataclass(frozen=True)
class LinkPlan:
    role: Role
    target: str


def plan_links(chain: tuple[tuple[str, str], ...]) -> tuple[LinkPlan, ...]:
    """Map (kind, spec-dock relative path) entries to the three role links; absent roles use the fallback."""
    paths = dict(chain)
    return tuple(LinkPlan(role, paths.get(role, f"system/active-none/{role}")) for role in ROLES)
