"""The dashboard model (epic-00427 D-04): one pure view of a structure snapshot for the screens and the summary.

States copy `evaluate_all` (the readiness that `dependency check` and `work start` use); this module only adds
what the dashboard needs on top: an Epic or Initiative with in-progress descendants is in progress, the board
lane with awaiting merge, the recommended order (R-31), cleanup candidates, child stages, dependency paths,
the comparison with a "seen" record and the time axis. Nothing here reads files or the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_readiness import evaluate_all
from spec_dock.runtime.domain.canonical_structure import branch_names_scope, parse_timestamp
from spec_dock.runtime.domain.dashboard_snapshot import PullRequestInfo

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from spec_dock.runtime.domain.canonical_readiness import ScopeReadiness
    from spec_dock.runtime.domain.canonical_structure import (
        PullRequest,
        ScopeNode,
        StructureAnomaly,
        StructureSnapshot,
    )
    from spec_dock.runtime.domain.dashboard_snapshot import PullRequestStatus
    from spec_dock.runtime.domain.selectors import ScopeKind

DashboardState = Literal["done", "doing", "blocked", "ready", "unknown"]
Lane = Literal["blocked", "ready", "doing", "awaiting_merge", "done", "unknown"]
MergeGroup = Literal["mergeable", "needs_fix"]
PullRequestPhase = Literal["none", "draft", "open", "needs_fix", "merged", "closed"]
ChangeKind = Literal["new", "state", "pr"]
EventKind = Literal["created", "closed", "pr_opened", "pr_merged"]

STATES: Final[tuple[DashboardState, ...]] = ("done", "doing", "blocked", "ready", "unknown")
KINDS: Final[tuple[ScopeKind, ...]] = ("initiative", "epic", "issue")
STALE_AFTER: Final = timedelta(minutes=30)
_FROM_READINESS: Final[Mapping[str, DashboardState]] = {
    "DONE": "done",
    "UNKNOWN": "unknown",
    "DOING": "doing",
    "BLOCKED": "blocked",
    "READY": "ready",
}


@dataclass(frozen=True)
class ScopeReason:
    """Why a Scope is in its state; `numbers` are the Issues it names (waits, the closed parent, the PR)."""

    code: str
    text: str
    numbers: tuple[int, ...] = ()


@dataclass(frozen=True)
class ScopeModel:
    id: str
    number: int
    kind: ScopeKind
    title: str
    parent_id: str | None
    children: tuple[str, ...]
    state: DashboardState
    reason: ScopeReason
    readiness: ScopeReadiness
    pr: PullRequest | None
    lane: Lane
    merge: MergeGroup | None
    downstream: int
    waits: int
    keep_visible: bool
    created_at: str
    closed_at: str | None
    url: str

    @property
    def open(self) -> bool:
        return self.state != "done"


@dataclass(frozen=True)
class CleanupCandidate:
    scope_id: str
    code: Literal["all_descendants_closed", "closed_with_open_descendants", "open_under_closed_parent"]
    text: str


@dataclass(frozen=True)
class ChildStages:
    stages: tuple[tuple[str, ...], ...]
    external: tuple[tuple[str, int], ...]
    cyclic: tuple[str, ...]


@dataclass(frozen=True)
class DependencyPath:
    direct: tuple[str, ...]
    indirect: tuple[str, ...]


@dataclass(frozen=True)
class RootWaits:
    scope_ids: tuple[str, ...]
    external: tuple[int, ...]


@dataclass(frozen=True)
class SeenScope:
    state: DashboardState
    pr: PullRequestPhase | None


@dataclass(frozen=True)
class ScopeChange:
    kinds: frozenset[ChangeKind]
    state_before: DashboardState | None
    pr_before: PullRequestPhase | None


@dataclass(frozen=True)
class WeekTotal:
    week_start: str
    created: int
    closed: int


@dataclass(frozen=True)
class TimelineEvent:
    at: str
    kind: EventKind
    scope_id: str
    number: int


@dataclass(frozen=True)
class DashboardModel:
    snapshot: StructureSnapshot
    repository: str
    fetched_at: str
    stale: bool
    anomalies: tuple[StructureAnomaly, ...]
    pull_requests: PullRequestInfo
    pull_request_status: PullRequestStatus
    scopes: Mapping[str, ScopeModel]
    cleanup: tuple[CleanupCandidate, ...]

    def scope(self, scope_id: str) -> ScopeModel:
        return self.scopes[scope_id]

    def ordered(self, scope_ids: Iterable[str]) -> tuple[str, ...]:
        return tuple(sorted(scope_ids, key=lambda item: recommended_key(self.scopes[item])))

    def lane(self, lane: Lane) -> tuple[str, ...]:
        return self.ordered(item.id for item in self.scopes.values() if item.lane == lane)


def recommended_key(scope: ScopeModel) -> tuple[object, ...]:
    """R-31: mergeable, needs fix, doing, ready (most waiting first), blocked (fewest waits), unknown, done."""
    if scope.merge == "mergeable":
        group = 0
    elif scope.merge == "needs_fix":
        group = 1
    else:
        group = {"doing": 2, "ready": 3, "blocked": 4, "unknown": 5, "done": 6}[scope.state]
    if group == 4:
        return (group, scope.waits, -scope.downstream, scope.number)
    if group == 5:
        return (group, scope.number)
    if group == 6:
        closed = -parse_timestamp(scope.closed_at).timestamp() if scope.closed_at else 0.0
        return (group, closed, scope.number)
    return (group, -scope.downstream, scope.number)


class _Graph:
    """Scope-only parent/child and blocked-by relations of a snapshot, safe against broken parent links."""

    def __init__(self, snapshot: StructureSnapshot) -> None:
        self.snapshot = snapshot
        self.nodes: dict[str, ScopeNode] = {node.id: node for node in snapshot.scopes if node.id is not None}
        self.by_number: dict[int, str] = {node.number: scope for scope, node in self.nodes.items()}
        self.parent: dict[str, str | None] = {
            scope: self.by_number.get(node.parent) if node.parent is not None else None
            for scope, node in self.nodes.items()
        }
        children: dict[str, list[str]] = {scope: [] for scope in self.nodes}
        for scope, parent in self.parent.items():
            if parent is not None and parent != scope:
                children[parent].append(scope)
        self.children = {scope: tuple(sorted(items, key=self.number)) for scope, items in children.items()}
        self.prerequisites: dict[str, tuple[str, ...]] = {
            scope: tuple(self.by_number[n] for n in node.blocked_by if n in self.by_number)
            for scope, node in self.nodes.items()
        }
        waiters: dict[str, list[str]] = {scope: [] for scope in self.nodes}
        for scope, items in self.prerequisites.items():
            for item in items:
                waiters[item].append(scope)
        self.waiters = {scope: tuple(items) for scope, items in waiters.items()}
        self._ancestors: dict[str, tuple[str, ...]] = {}
        self._descendants: dict[str, tuple[str, ...]] = {}

    def number(self, scope: str) -> int:
        return self.nodes[scope].number

    def is_open(self, scope: str) -> bool:
        return self.nodes[scope].state == "open"

    def ancestors(self, scope: str) -> tuple[str, ...]:
        found = self._ancestors.get(scope)
        if found is None:
            chain: list[str] = []
            current = self.parent[scope]
            while current is not None and current != scope and current not in chain:
                chain.append(current)
                current = self.parent[current]
            found = self._ancestors[scope] = tuple(chain)
        return found

    def descendants(self, scope: str) -> tuple[str, ...]:
        found = self._descendants.get(scope)
        if found is None:
            seen: list[str] = []
            stack = list(self.children[scope])
            while stack:
                item = stack.pop()
                if item == scope or item in seen:
                    continue
                seen.append(item)
                stack.extend(self.children[item])
            found = self._descendants[scope] = tuple(sorted(seen, key=self.number))
        return found

    def chain_prerequisites(self, scope: str) -> tuple[str, ...]:
        """Scope prerequisites declared by the Scope or inherited from its ancestors."""
        found: list[str] = []
        for member in (scope, *self.ancestors(scope)):
            found.extend(item for item in self.prerequisites[member] if item not in found)
        return tuple(found)

    def downstream(self, scope: str, *, open_only: bool) -> tuple[set[str], set[str]]:
        """(all, direct) Scopes that wait for the Scope directly or indirectly.

        A Scope waits with its descendants; anything that waits for an ancestor also waits for the Scope.
        """
        seen: set[str] = set()
        queue: list[str] = []
        out: set[str] = set()
        direct: set[str] = set()

        def visit(item: str) -> None:
            if (open_only and not self.is_open(item)) or item in seen:
                return
            seen.add(item)
            queue.append(item)

        origin = (scope, *self.ancestors(scope))
        for item in origin:
            visit(item)
        while queue:
            current = queue.pop()
            for waiter in self.waiters[current]:
                for member in (waiter, *self.descendants(waiter)):
                    if open_only and not self.is_open(member):
                        continue
                    if current == scope and member == waiter:
                        direct.add(member)
                    out.add(member)
                    visit(member)
                    for ancestor in self.ancestors(member):
                        visit(ancestor)
        out.difference_update(origin)
        direct.difference_update(origin)
        return out, direct


def build_model(snapshot: StructureSnapshot, *, now: datetime) -> DashboardModel:
    graph = _Graph(snapshot)
    readiness = evaluate_all(snapshot)
    pull_requests = PullRequestInfo.of(snapshot)
    pr_status = pull_requests.status(now)
    states: dict[str, DashboardState] = {}
    for scope, node in graph.nodes.items():
        state = _FROM_READINESS[readiness[scope].state]
        if node.kind != "issue" and state in ("blocked", "ready") and _doing_descendants(graph, scope):
            state = "doing"
        states[scope] = state
    scopes: dict[str, ScopeModel] = {}
    for scope, node in graph.nodes.items():
        state = states[scope]
        pr = pull_requests.by_scope.get(scope) if pr_status != "unknown" else None
        merge = _merge_group(pr) if state == "doing" and node.kind == "issue" else None
        lane: Lane = "awaiting_merge" if merge is not None else state
        result = readiness[scope]
        waits = {item.number for item in result.blockers if item.role in ("prerequisite", "external")}
        scopes[scope] = ScopeModel(
            id=scope,
            number=node.number,
            kind=node.kind,  # type: ignore[arg-type]
            title=node.title,
            parent_id=graph.parent[scope],
            children=graph.children[scope],
            state=state,
            reason=_reason(graph, result, state, merge, pr),
            readiness=result,
            pr=pr,
            lane=lane,
            merge=merge,
            downstream=len(graph.downstream(scope, open_only=True)[0]) if graph.is_open(scope) else 0,
            waits=len(waits),
            keep_visible=not graph.is_open(scope) and any(graph.is_open(d) for d in graph.descendants(scope)),
            created_at=node.created_at,
            closed_at=node.closed_at,
            url=node.url,
        )
    cleanup = _cleanup(graph, scopes)
    return DashboardModel(
        snapshot=snapshot,
        repository=snapshot.repository,
        fetched_at=snapshot.fetched_at,
        stale=now - parse_timestamp(snapshot.fetched_at) > STALE_AFTER,
        anomalies=snapshot.anomalies,
        pull_requests=pull_requests,
        pull_request_status=pr_status,
        scopes=scopes,
        cleanup=tuple(sorted(cleanup, key=lambda item: (recommended_key(scopes[item.scope_id]), item.code))),
    )


def _doing_descendants(graph: _Graph, scope: str) -> tuple[str, ...]:
    return tuple(item for item in graph.descendants(scope) if graph.is_open(item) and graph.nodes[item].in_progress)


def _merge_group(pr: PullRequest | None) -> MergeGroup | None:
    if pr is None or pr.state != "open" or pr.is_draft:
        return None
    return "needs_fix" if pr.checks == "failure" or pr.mergeable == "conflicting" else "mergeable"


def _numbers(items: Iterable[int]) -> str:
    return "・".join(f"#{item}" for item in items)


def _reason(
    graph: _Graph, result: ScopeReadiness, state: DashboardState, merge: MergeGroup | None, pr: PullRequest | None
) -> ScopeReason:
    scope = result.scope_id
    if state == "done":
        return ScopeReason("closed", "終わった")
    if state == "unknown":
        first = result.unknown[0]
        return ScopeReason(first.code, f"構造が分からない（{first.code}）", (first.number,))
    if state == "doing":
        if merge is not None and pr is not None:
            if merge == "needs_fix":
                causes = [
                    text
                    for flag, text in ((pr.checks == "failure", "CI が失敗"), (pr.mergeable == "conflicting", "衝突"))
                    if flag
                ]
                return ScopeReason(
                    "pr_needs_fix", f"PR #{pr.number} を直す必要がある（{'・'.join(causes)}）", (pr.number,)
                )
            suffix = "（CI は実行中）" if pr.checks == "pending" else ""
            return ScopeReason("pr_mergeable", f"PR #{pr.number} をマージできる{suffix}", (pr.number,))
        if result.in_progress:
            return ScopeReason("in_progress", "作業中")
        doing = _doing_descendants(graph, scope)
        return ScopeReason(
            "descendant_in_progress", f"配下の {len(doing)}件が作業中", tuple(graph.number(item) for item in doing)
        )
    if state == "blocked":
        closed = [item for item in result.blockers if item.role == "ancestor"]
        if closed:
            return ScopeReason("parent_closed", f"親 {closed[0].scope_id} が閉じている", (closed[0].number,))
        own = [item for item in result.blockers if item.declared_by == scope]
        if own:
            numbers = tuple(dict.fromkeys(item.number for item in own))
            code = "waiting" if any(item.role == "prerequisite" for item in own) else "waiting_external"
            return ScopeReason(code, f"{_numbers(numbers)} を待つ", numbers)
        inherited = [item for item in result.blockers if item.role in ("prerequisite", "external")]
        numbers = tuple(dict.fromkeys(item.number for item in inherited))
        declared = inherited[0].declared_by if inherited else None
        return ScopeReason("inherited_waiting", f"上位の {declared} が {_numbers(numbers)} を待つ", numbers)
    return ScopeReason("no_waits", "待っているものはない")


def _cleanup(graph: _Graph, scopes: Mapping[str, ScopeModel]) -> list[CleanupCandidate]:
    """Epic R-20's two kinds (finished open parents, closed parents with open descendants) and, per Epic R-10,
    the open Scopes blocked because an ancestor is closed."""
    found: list[CleanupCandidate] = []
    for scope, item in scopes.items():
        descendants = graph.descendants(scope)
        if item.open and item.kind != "issue" and descendants and not any(graph.is_open(d) for d in descendants):
            found.append(
                CleanupCandidate(
                    scope, "all_descendants_closed", f"配下の {len(descendants)}件がすべて終わったのに、開いたまま"
                )
            )
        if item.keep_visible:
            count = sum(1 for d in descendants if graph.is_open(d))
            found.append(
                CleanupCandidate(scope, "closed_with_open_descendants", f"閉じたのに、配下の {count}件が開いている")
            )
        if item.state == "blocked" and item.reason.code == "parent_closed":
            parent = graph.by_number[item.reason.numbers[0]]
            found.append(CleanupCandidate(scope, "open_under_closed_parent", f"閉じた親 {parent} の下で開いている"))
    return found


# --- Child stages and dependency paths (R-15, R-18) -------------------------------------------------------


def child_stages(model: DashboardModel, parent_id: str | None, *, open_only: bool = False) -> ChildStages:
    """Split the direct children (top-level Scopes when parent_id is None) into dependency stages.

    A child waits for a sibling when anything in its subtree is blocked by something in the sibling's subtree;
    targets outside every sibling subtree are external. Children on a cycle are left out of the stages.
    """
    graph = _Graph(model.snapshot)
    if parent_id is None:
        children = tuple(sorted((s for s, p in graph.parent.items() if p is None), key=graph.number))
    else:
        children = graph.children[parent_id]
    if open_only:
        children = tuple(item for item in children if graph.is_open(item))
    owner: dict[int, str] = {}
    for child in children:
        for member in (child, *graph.descendants(child)):
            owner[graph.number(member)] = child
    edges: dict[str, set[str]] = {child: set() for child in children}
    external: list[tuple[str, int]] = []
    for child in children:
        for member in (child, *graph.descendants(child)):
            node = graph.nodes[member]
            if open_only and node.state != "open":
                continue
            for target in node.blocked_by:
                if open_only and not _issue_open(model.snapshot, target):
                    continue
                holder = owner.get(target)
                if holder is None:
                    if (child, target) not in external:
                        external.append((child, target))
                elif holder != child:
                    edges[child].add(holder)
    cyclic = _cyclic(children, edges)
    stage: dict[str, int] = {}

    def depth(item: str, path: tuple[str, ...] = ()) -> int:
        if item in stage:
            return stage[item]
        before = [depth(dep, (*path, item)) for dep in edges[item] if dep not in cyclic and dep not in path]
        stage[item] = 1 + max(before, default=0)
        return stage[item]

    for child in children:
        if child not in cyclic:
            depth(child)
    count = max(stage.values(), default=0)
    stages = tuple(
        model.ordered(item for item in children if stage.get(item) == level) for level in range(1, count + 1)
    )
    return ChildStages(stages, tuple(external), tuple(item for item in children if item in cyclic))


def _issue_open(snapshot: StructureSnapshot, number: int) -> bool:
    node = snapshot.issues.get(number)
    if node is not None:
        return node.state == "open"
    external = snapshot.external.get(number)
    return external is None or external.state == "open"


def _cyclic(items: tuple[str, ...], edges: Mapping[str, set[str]]) -> set[str]:
    """Members of strongly connected components larger than one (Tarjan, iterative enough for sibling sets)."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    found: set[str] = set()
    counter = [0]

    def connect(item: str) -> None:
        index[item] = low[item] = counter[0]
        counter[0] += 1
        stack.append(item)
        on_stack.add(item)
        for target in edges[item]:
            if target not in index:
                connect(target)
                low[item] = min(low[item], low[target])
            elif target in on_stack:
                low[item] = min(low[item], index[target])
        if low[item] == index[item]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == item:
                    break
            if len(component) > 1:
                found.update(component)

    for item in items:
        if item not in index:
            connect(item)
    return found


def upstream(model: DashboardModel, scope_id: str, *, open_only: bool = False) -> DependencyPath:
    """What must finish before the Scope: its own prerequisites (direct), then those inherited from its ancestors
    and, recursively, the descendants and prerequisites of everything reached (indirect)."""
    graph = _Graph(model.snapshot)

    def wanted(item: str) -> bool:
        return not open_only or graph.is_open(item)

    direct = [item for item in graph.prerequisites[scope_id] if wanted(item)]
    inherited = [item for item in graph.chain_prerequisites(scope_id) if wanted(item) and item not in direct]
    seen = {scope_id, *direct, *inherited}
    indirect: list[str] = list(inherited)
    queue = [*direct, *inherited]
    while queue:
        current = queue.pop()
        candidates = (*graph.descendants(current), *graph.chain_prerequisites(current))
        for item in candidates:
            if item in seen or not wanted(item):
                continue
            seen.add(item)
            indirect.append(item)
            queue.append(item)
    return DependencyPath(tuple(sorted(direct, key=graph.number)), tuple(sorted(indirect, key=graph.number)))


def downstream_ids(model: DashboardModel, scope_id: str, *, open_only: bool = True) -> DependencyPath:
    """What waits for the Scope; with open_only its size is the Scope's `downstream` count."""
    graph = _Graph(model.snapshot)
    out, direct = graph.downstream(scope_id, open_only=open_only)
    return DependencyPath(tuple(sorted(direct, key=graph.number)), tuple(sorted(out - direct, key=graph.number)))


def root_waits(model: DashboardModel, scope_id: str) -> RootWaits:
    """For a blocked Scope: the ends of its open upstream (no open prerequisite on their chain, no open
    descendant) that are not blocked themselves, and the open non-Scope Issues upstream waits for."""
    if model.scopes[scope_id].state != "blocked":
        return RootWaits((), ())
    path = upstream(model, scope_id, open_only=True)
    members = (*path.direct, *path.indirect)
    graph = _Graph(model.snapshot)
    roots = [
        item
        for item in members
        if model.scopes[item].state != "blocked"
        and not any(graph.is_open(other) for other in graph.chain_prerequisites(item))
        and not any(graph.is_open(other) for other in graph.descendants(item))
    ]
    external: list[int] = []
    for member in (scope_id, *members):
        for blocker in model.scopes[member].readiness.blockers:
            if blocker.role == "external" and blocker.number not in external:
                external.append(blocker.number)
    return RootWaits(model.ordered(roots), tuple(sorted(external)))


# --- Seen records (R-29, D-18) ------------------------------------------------------------------------------


def pull_request_phase(model: DashboardModel, scope: ScopeModel) -> PullRequestPhase | None:
    if model.pull_request_status == "unknown":
        return None
    pr = scope.pr
    if pr is None:
        return "none"
    if pr.state != "open":
        return pr.state
    if pr.is_draft:
        return "draft"
    return "needs_fix" if _merge_group(pr) == "needs_fix" else "open"


def seen_scopes(model: DashboardModel) -> dict[str, SeenScope]:
    """The per-Scope part of a "seen" record; the server stores it as {ID: {state, pr}}."""
    return {scope.id: SeenScope(scope.state, pull_request_phase(model, scope)) for scope in model.scopes.values()}


def compare_seen(model: DashboardModel, baseline: Mapping[str, SeenScope] | None) -> dict[str, ScopeChange]:
    """Scopes whose state or pull request phase changed since the baseline, and new Scopes; titles,
    parents and dependencies alone do not count. A PR change needs a known phase on both sides."""
    if baseline is None:
        return {}
    changes: dict[str, ScopeChange] = {}
    for scope_id, now in seen_scopes(model).items():
        before = baseline.get(scope_id)
        if before is None:
            changes[scope_id] = ScopeChange(frozenset({"new"}), None, None)
            continue
        kinds: set[ChangeKind] = set()
        if before.state != now.state:
            kinds.add("state")
        if before.pr is not None and now.pr is not None and before.pr != now.pr:
            kinds.add("pr")
        if kinds:
            changes[scope_id] = ScopeChange(frozenset(kinds), before.state, before.pr)
    return changes


# --- Time axis (R-16) --------------------------------------------------------------------------------------


def _week_start(value: datetime) -> datetime:
    day = value.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return day - timedelta(days=day.weekday())


def weekly_totals(model: DashboardModel, *, now: datetime, kinds: Iterable[ScopeKind] = KINDS) -> tuple[WeekTotal, ...]:
    """Cumulative created and closed counts at the end of each UTC week (Monday start) up to `now`."""
    wanted = set(kinds)
    selected = [scope for scope in model.scopes.values() if scope.kind in wanted]
    if not selected:
        return ()
    created = sorted(_week_start(parse_timestamp(item.created_at)) for item in selected)
    closed = sorted(_week_start(parse_timestamp(item.closed_at)) for item in selected if item.closed_at)
    totals: list[WeekTotal] = []
    week = created[0]
    last = max(_week_start(now), created[-1], *(closed[-1:] or ()))
    while week <= last:
        totals.append(
            WeekTotal(
                week.strftime("%Y-%m-%d"),
                sum(1 for item in created if item <= week),
                sum(1 for item in closed if item <= week),
            )
        )
        week += timedelta(days=7)
    return tuple(totals)


def recent_events(model: DashboardModel, *, limit: int | None = None) -> tuple[TimelineEvent, ...]:
    """Scope creation and completion, and the opening and merging of every pull request whose branch names a
    Scope (not only the one chosen for the Scope), newest first. Pull requests are left out while unknown."""
    events: list[TimelineEvent] = []
    for scope in model.scopes.values():
        events.append(TimelineEvent(scope.created_at, "created", scope.id, scope.number))
        if scope.closed_at:
            events.append(TimelineEvent(scope.closed_at, "closed", scope.id, scope.number))
    if model.pull_request_status != "unknown":
        for pr in model.pull_requests.items.values():
            owner = next((item for item in model.scopes if branch_names_scope(pr.head_ref_name, item)), None)
            if owner is None:
                continue
            events.append(TimelineEvent(pr.created_at, "pr_opened", owner, pr.number))
            if pr.merged_at:
                events.append(TimelineEvent(pr.merged_at, "pr_merged", owner, pr.number))
    events.sort(key=lambda item: (-parse_timestamp(item.at).timestamp(), item.number, item.kind))
    return tuple(events if limit is None else events[:limit])
