"""Structure documents for the structure graph's node check (iss-00532): a real snapshot and a generated one."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import random
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.application.dashboard_site import RepositoryView, SiteRepository
from spec_dock.runtime.domain.dashboard_model import build_model
from spec_dock.runtime.domain.dashboard_snapshot import parse_snapshot_document
from spec_dock.runtime.infra.github_structure import GithubRepository
from spec_dock.runtime.presentation.dashboard_api import scope_document, structure_document
from tests.support.dashboard import closed, node, snapshot

if TYPE_CHECKING:
    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot

NOW = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)


def document(structure: StructureSnapshot, *, now: datetime = NOW) -> dict[str, Any]:
    """The structure API document of a snapshot, as the server returns it (no "seen" baseline)."""
    payload = structure.to_json()
    return document_of(payload, now=now)


def _view(payload: dict[str, Any], now: datetime) -> RepositoryView:
    repository = GithubRepository.parse(str(payload["repository"]))
    parsed = parse_snapshot_document(payload, repository=repository.key)
    model = build_model(parsed.snapshot, now=now)
    return RepositoryView(SiteRepository(repository, None, ()), "ok", parsed, None, model, "r1")


def document_of(payload: dict[str, Any], *, now: datetime = NOW) -> dict[str, Any]:
    return structure_document(_view(payload, now), now=now, baseline=None, latest=None)


def scope_of(structure: StructureSnapshot, scope_id: str, *, now: datetime = NOW) -> dict[str, Any] | None:
    """The `scopes/<ID>` API document of a snapshot's Scope."""
    return scope_document(_view(structure.to_json(), now), scope_id, baseline=None)


def generated(count: int = 250, *, seed: int = 532) -> StructureSnapshot:
    """About `count` Scopes: 2 Initiatives, Epics of 8–16 Issues with dependency chains, a few dependencies across
    Epics (in the real structures almost every dependency stays in one parent), a third of the Issues closed."""
    rng = random.Random(seed)
    start = datetime(2026, 5, 4, tzinfo=timezone.utc)
    nodes = []
    number = 1
    initiatives = []
    for _ in range(2):
        initiatives.append(number)
        nodes.append(node(number, "initiative", title=f"Initiative {number}", created_at=_at(start, number)))
        number += 1
    issues: list[int] = []
    while number <= count:
        epic = number
        parent = initiatives[rng.randrange(2)] if rng.random() < 0.8 else None
        nodes.append(node(epic, "epic", parent=parent, title=f"Epic {epic} の題名", created_at=_at(start, epic)))
        number += 1
        members: list[int] = []
        for _ in range(rng.randint(8, 16)):
            if number > count:
                break
            blocked = []
            if members and rng.random() < 0.55:
                blocked.append(members[rng.randrange(max(0, len(members) - 3), len(members))])
            if issues and rng.random() < 0.02:  # the real structures: almost every dependency stays in one parent
                blocked.append(issues[rng.randrange(max(0, len(issues) - 40), len(issues))])
            title = f"Issue {number} の少し長い題名で、2行に折り返して切れるかを見る"
            created = _at(start, number)
            if rng.random() < 0.33:
                item = closed(
                    number,
                    "issue",
                    parent=epic,
                    title=title,
                    blocked_by=tuple(blocked),
                    created_at=created,
                    closed_at=_at(start, number + 20),
                )
            else:
                item = node(
                    number,
                    "issue",
                    parent=epic,
                    title=title,
                    blocked_by=tuple(blocked),
                    created_at=created,
                    in_progress=rng.random() < 0.1,
                )
            nodes.append(item)
            members.append(number)
            number += 1
        issues.extend(members)
    structure = snapshot(*nodes)
    return replace(structure, repository="github.com/o/generated")


def _at(start: datetime, number: int) -> str:
    return (start + timedelta(hours=number * 14)).strftime("%Y-%m-%dT%H:%M:%SZ")


# iss-00578: the shape of a real Epic with many lines (taikyohiyou_project epic-02233, 22 Issues): one Issue that many
# wait for (54), one that waits for almost every other (53), and lines that pass several stage columns.
_MANY_LINES = {
    35: (),
    36: (54,),
    37: (36,),
    38: (36, 41, 43, 44, 46, 51, 52, 54),
    39: (41, 52),
    40: (39, 41),
    41: (49, 52, 54),
    42: (40, 41),
    43: (44, 52),
    44: (51, 52, 54),
    45: (37, 38, 43, 44),
    46: (54,),
    47: (46,),
    48: (37, 43),
    49: (54,),
    50: (42,),
    51: (54,),
    52: (54,),
    53: (*range(36, 53), 71, 83),
    54: (),
    71: (44, 46),
    83: (),
}
_MANY_LINES_DONE = {35, 36, 37, 41, 43, 44, 46, 47, 49, 51, 52, 54, 71}
_MANY_LINES_DOING = {38, 39, 48, 83}


def many_lines(base: int = 600) -> StructureSnapshot:
    """An Initiative with one Epic of 22 Issues whose dependencies fan out from one and into one (iss-00578)."""
    items = [node(base, "initiative", in_progress=True), node(base + 1, "epic", parent=base, in_progress=True)]
    for n, deps in _MANY_LINES.items():
        number = base + 100 + n
        blocked = tuple(base + 100 + d for d in deps)
        if n in _MANY_LINES_DONE:
            items.append(closed(number, "issue", parent=base + 1, blocked_by=blocked))
        else:
            items.append(node(number, "issue", parent=base + 1, blocked_by=blocked, in_progress=n in _MANY_LINES_DOING))
    return replace(snapshot(*items), repository="github.com/o/many-lines")
