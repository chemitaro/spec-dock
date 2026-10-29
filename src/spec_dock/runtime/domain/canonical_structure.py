"""GitHub structure representation for canonical mode: labels, IDs, kind changes and the structure snapshot."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.dependency_vnext import dependency_listing, validate_dependency_graph
from spec_dock.runtime.domain.ids import CANONICAL_ID_RE, format_id

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.domain.selectors import ScopeKind

KIND_LABELS: Final[Mapping[ScopeKind, str]] = {
    "initiative": "spec-dock:initiative",
    "epic": "spec-dock:epic",
    "issue": "spec-dock:issue",
}
IN_PROGRESS_LABEL: Final = "spec-dock:in-progress"
ID_PREFIXES: Final[Mapping[ScopeKind, str]] = {"initiative": "init", "epic": "epic", "issue": "iss"}
PARENT_KINDS: Final[Mapping[ScopeKind, ScopeKind | None]] = {"initiative": None, "epic": "initiative", "issue": "epic"}

SNAPSHOT_VERSION: Final = 1
GITHUB_HOST: Final = "github.com"

KIND_LABEL_MULTIPLE = "KIND_LABEL_MULTIPLE"
SCOPE_KIND_CHANGED: Final = "SCOPE_KIND_CHANGED"
PARENT_FOREIGN_REPOSITORY = "PARENT_FOREIGN_REPOSITORY"
SUB_ISSUE_FOREIGN_REPOSITORY = "SUB_ISSUE_FOREIGN_REPOSITORY"
DEPENDENCY_FOREIGN_REPOSITORY = "DEPENDENCY_FOREIGN_REPOSITORY"
PARENT_MISSING = "PARENT_MISSING"
PARENT_INVALID = "PARENT_INVALID"
DEPENDENCY_INVALID = "DEPENDENCY_INVALID"
DEPENDENCY_CYCLE = "DEPENDENCY_CYCLE"
# Element anomalies travel with one Issue's facts; structure anomalies are recomputed from the whole snapshot.
FACT_ANOMALY_CODES: Final = frozenset({KIND_LABEL_MULTIPLE})
RELATION_ANOMALY_CODES: Final = frozenset({
    PARENT_FOREIGN_REPOSITORY,
    SUB_ISSUE_FOREIGN_REPOSITORY,
    DEPENDENCY_FOREIGN_REPOSITORY,
})
ELEMENT_ANOMALY_CODES: Final = FACT_ANOMALY_CODES | RELATION_ANOMALY_CODES
_DEPENDENCY_CODES: Final = frozenset({DEPENDENCY_INVALID, DEPENDENCY_CYCLE})


@dataclass(frozen=True)
class LabelDefinition:
    name: str
    color: str
    description: str


LABEL_DEFINITIONS: Final = (
    LabelDefinition("spec-dock:initiative", "5319e7", "SpecDock Initiative scope"),
    LabelDefinition("spec-dock:epic", "1d76db", "SpecDock Epic scope"),
    LabelDefinition("spec-dock:issue", "0e8a16", "SpecDock Issue scope"),
    LabelDefinition("spec-dock:in-progress", "fbca04", "SpecDock work in progress"),
)
_KINDS_BY_LABEL: Final[Mapping[str, ScopeKind]] = {label: kind for kind, label in KIND_LABELS.items()}
_KINDS_BY_PREFIX: Final[Mapping[str, ScopeKind]] = {prefix: kind for kind, prefix in ID_PREFIXES.items()}


def kind_from_labels(labels: Iterable[str]) -> tuple[ScopeKind | None, str | None]:
    """Return the Scope kind, or no kind and an anomaly when several kind labels are present."""
    kinds = {_KINDS_BY_LABEL[label] for label in labels if label in _KINDS_BY_LABEL}
    if len(kinds) > 1:
        return None, KIND_LABEL_MULTIPLE
    return (kinds.pop(), None) if kinds else (None, None)


def scope_id(kind: ScopeKind, number: int) -> str:
    if number <= 0:
        raise ValueError("GitHub Issue number must be positive")
    return format_id(ID_PREFIXES[kind], number)


def parse_scope_id(value: str) -> tuple[ScopeKind, int]:
    """Parse a GitHub-numbered Scope ID; local IDs do not exist in canonical mode."""
    text = value.strip().lower()
    matched = CANONICAL_ID_RE.fullmatch(text)
    number = int(text.partition("-")[2]) if matched is not None else 0
    if matched is None or number <= 0:
        raise ValueError(f"not a canonical Scope ID: {value!r}")
    return _KINDS_BY_PREFIX[matched.group(1)], number


def branch_names_scope(branch: str, scope_id: str) -> bool:
    """A branch belongs to a Scope when its last segment is the ID or starts with `<ID>-` (Epic design ch. 7)."""
    if CANONICAL_ID_RE.fullmatch(scope_id) is None:
        raise ValueError(f"not a canonical Scope ID: {scope_id!r}")
    name = branch.rpartition("/")[2]
    return name == scope_id or name.startswith(f"{scope_id}-")


def format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp has no timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


IssueState = Literal["open", "closed"]


@dataclass(frozen=True)
class IssueFacts:
    """One Issue as GitHub reports it; SpecDock keeps nothing in the body, so it is never read."""

    number: int
    database_id: int
    title: str
    state: str
    state_reason: str | None
    labels: tuple[str, ...]
    assignees: tuple[str, ...]
    updated_at: str
    url: str
    created_at: str
    closed_at: str | None


@dataclass(frozen=True)
class RelatedIssue:
    """A parent, child or blocker; repository is the lowercase owner/name."""

    number: int
    repository: str
    title: str | None = None
    state: str | None = None


@dataclass(frozen=True)
class FetchedIssue:
    facts: IssueFacts
    parent: RelatedIssue | None
    sub_issues: tuple[RelatedIssue, ...]
    blocked_by: tuple[RelatedIssue, ...]


@dataclass(frozen=True)
class ScopeNode:
    number: int
    database_id: int
    id: str | None
    kind: ScopeKind | None
    title: str
    state: IssueState
    state_reason: str | None
    labels: tuple[str, ...]
    assignees: tuple[str, ...]
    in_progress: bool
    parent: int | None
    sub_issues: tuple[int, ...]
    blocked_by: tuple[int, ...]
    blocking: tuple[int, ...]
    updated_at: str
    url: str
    created_at: str  # iss-00438: GitHub createdAt and closedAt, for epic-00427's time axis
    closed_at: str | None


@dataclass(frozen=True)
class ExternalIssue:
    number: int
    title: str
    state: IssueState


@dataclass(frozen=True)
class StructureAnomaly:
    number: int
    code: str
    message: str


@dataclass(frozen=True)
class LocalWrite:
    at: str
    command: str
    numbers: tuple[int, ...]


@dataclass(frozen=True)
class KindChange:
    """GitHub moved this number to another kind; `directories` are its catalog names of the old kinds."""

    number: int
    current_id: str
    directories: tuple[str, ...]


class SnapshotFormatError(ValueError):
    """The stored snapshot is not a known version-1 document; callers refetch."""


@dataclass(frozen=True)
class StructureSnapshot:
    repository: str
    fetched_at: str
    fetch_started_at: str
    issues: Mapping[int, ScopeNode]
    external: Mapping[int, ExternalIssue]
    anomalies: tuple[StructureAnomaly, ...]
    local_writes: tuple[LocalWrite, ...]

    @property
    def scopes(self) -> tuple[ScopeNode, ...]:
        return tuple(self.issues[number] for number in sorted(self.issues) if self.issues[number].id is not None)

    def find(self, scope_id: str) -> ScopeNode | None:
        try:
            _, number = parse_scope_id(scope_id)
        except ValueError:
            return None
        node = self.issues.get(number)
        return node if node is not None and node.id == scope_id.strip().lower() else None

    def anomalies_for(self, number: int) -> tuple[StructureAnomaly, ...]:
        return tuple(anomaly for anomaly in self.anomalies if anomaly.number == number)

    def to_json(self) -> dict[str, object]:
        return {
            "version": SNAPSHOT_VERSION,
            "repository": self.repository,
            "fetched_at": self.fetched_at,
            "fetch_started_at": self.fetch_started_at,
            "issues": {str(number): _node_json(self.issues[number]) for number in sorted(self.issues)},
            "external": {
                str(number): {"number": item.number, "title": item.title, "state": item.state}
                for number, item in sorted(self.external.items())
            },
            "anomalies": [
                {"number": item.number, "code": item.code, "message": item.message} for item in self.anomalies
            ],
            "local_writes": [
                {"at": item.at, "command": item.command, "numbers": list(item.numbers)} for item in self.local_writes
            ],
        }

    @classmethod
    def from_json(cls, payload: object) -> StructureSnapshot:
        """Load only a well-formed version-1 document; anything else means refetch."""
        try:
            return _snapshot_from_json(payload)
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, SnapshotFormatError):
                raise
            raise SnapshotFormatError(f"structure snapshot is malformed: {error}") from error


_SNAPSHOT_KEYS: Final = frozenset({
    "version",
    "repository",
    "fetched_at",
    "fetch_started_at",
    "issues",
    "external",
    "anomalies",
    "local_writes",
})
_NODE_KEYS: Final = frozenset({
    "number",
    "database_id",
    "id",
    "kind",
    "title",
    "state",
    "state_reason",
    "labels",
    "assignees",
    "in_progress",
    "parent",
    "sub_issues",
    "blocked_by",
    "blocking",
    "updated_at",
    "url",
    "created_at",
    "closed_at",
})


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SnapshotFormatError(message)


def _object(value: object, keys: frozenset[str], what: str) -> dict[str, object]:
    _require(isinstance(value, dict) and set(value) == keys, f"{what} has unexpected keys")
    return cast("dict[str, object]", value)


def _integer(value: object, what: str, *, optional: bool = False) -> int | None:
    if optional and value is None:
        return None
    _require(type(value) is int and cast("int", value) > 0, f"{what} must be a positive integer")
    return cast("int", value)


def _text(value: object, what: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    _require(isinstance(value, str), f"{what} must be a string")
    return cast("str", value)


def _numbers(value: object, what: str) -> tuple[int, ...]:
    _require(isinstance(value, list), f"{what} must be a list")
    return tuple(cast("int", _integer(item, what)) for item in cast("list[object]", value))


def _texts(value: object, what: str) -> tuple[str, ...]:
    _require(isinstance(value, list), f"{what} must be a list")
    return tuple(cast("str", _text(item, what)) for item in cast("list[object]", value))


def _time(value: object, what: str) -> str:
    text = cast("str", _text(value, what))
    parse_timestamp(text)
    return text


def _optional_time(value: object, what: str) -> str | None:
    return None if value is None else _time(value, what)


def _snapshot_from_json(payload: object) -> StructureSnapshot:
    document = _object(payload, _SNAPSHOT_KEYS, "snapshot")
    _require(type(document["version"]) is int and document["version"] == SNAPSHOT_VERSION, "unknown snapshot version")
    repository = cast("str", _text(document["repository"], "repository"))
    _own_slug(repository)
    issues: dict[int, ScopeNode] = {}
    raw_issues = document["issues"]
    _require(isinstance(raw_issues, dict), "issues must be an object")
    for key, raw in cast("dict[str, object]", raw_issues).items():
        node = _node_from_json(raw)
        _require(key == str(node.number), "Issue key does not match its number")
        issues[node.number] = node
    external: dict[int, ExternalIssue] = {}
    raw_external = document["external"]
    _require(isinstance(raw_external, dict), "external must be an object")
    for key, raw in cast("dict[str, object]", raw_external).items():
        item = _object(raw, frozenset({"number", "title", "state"}), "external Issue")
        number = cast("int", _integer(item["number"], "external number"))
        _require(key == str(number), "external key does not match its number")
        external[number] = ExternalIssue(
            number, cast("str", _text(item["title"], "title")), _state_value(item["state"])
        )
    anomalies: list[StructureAnomaly] = []
    _require(isinstance(document["anomalies"], list), "anomalies must be a list")
    for raw in cast("list[object]", document["anomalies"]):
        item = _object(raw, frozenset({"number", "code", "message"}), "anomaly")
        anomalies.append(
            StructureAnomaly(
                cast("int", _integer(item["number"], "anomaly number")),
                cast("str", _text(item["code"], "anomaly code")),
                cast("str", _text(item["message"], "anomaly message")),
            )
        )
    writes: list[LocalWrite] = []
    _require(isinstance(document["local_writes"], list), "local_writes must be a list")
    for raw in cast("list[object]", document["local_writes"]):
        item = _object(raw, frozenset({"at", "command", "numbers"}), "local write")
        at = cast("str", _text(item["at"], "local write time"))
        parse_timestamp(at)
        writes.append(
            LocalWrite(at, cast("str", _text(item["command"], "command")), _numbers(item["numbers"], "numbers"))
        )
    for name in ("fetched_at", "fetch_started_at"):
        parse_timestamp(cast("str", _text(document[name], name)))
    return StructureSnapshot(
        repository=repository,
        fetched_at=cast("str", document["fetched_at"]),
        fetch_started_at=cast("str", document["fetch_started_at"]),
        issues=issues,
        external=external,
        anomalies=tuple(anomalies),
        local_writes=tuple(writes),
    )


def _state_value(value: object) -> IssueState:
    _require(value in ("open", "closed"), "state must be open or closed")
    return cast("IssueState", value)


def _node_from_json(raw: object) -> ScopeNode:
    item = _object(raw, _NODE_KEYS, "Issue")
    number = cast("int", _integer(item["number"], "number"))
    kind = item["kind"]
    _require(kind is None or kind in KIND_LABELS, "kind is unknown")
    scope = _text(item["id"], "id", optional=True)
    expected = None if kind is None else scope_id(cast("ScopeKind", kind), number)
    _require(scope == expected, "id does not match the kind and number")
    _require(isinstance(item["in_progress"], bool), "in_progress must be a boolean")
    return ScopeNode(
        number=number,
        database_id=cast("int", _integer(item["database_id"], "database_id")),
        id=scope,
        kind=cast("ScopeKind | None", kind),
        title=cast("str", _text(item["title"], "title")),
        state=_state_value(item["state"]),
        state_reason=_text(item["state_reason"], "state_reason", optional=True),
        labels=_texts(item["labels"], "labels"),
        assignees=_texts(item["assignees"], "assignees"),
        in_progress=cast("bool", item["in_progress"]),
        parent=_integer(item["parent"], "parent", optional=True),
        sub_issues=_numbers(item["sub_issues"], "sub_issues"),
        blocked_by=_numbers(item["blocked_by"], "blocked_by"),
        blocking=_numbers(item["blocking"], "blocking"),
        updated_at=cast("str", _text(item["updated_at"], "updated_at")),
        url=cast("str", _text(item["url"], "url")),
        created_at=_time(item["created_at"], "created_at"),
        closed_at=_optional_time(item["closed_at"], "closed_at"),
    )


def _node_json(node: ScopeNode) -> dict[str, object]:
    return {
        "number": node.number,
        "database_id": node.database_id,
        "id": node.id,
        "kind": node.kind,
        "title": node.title,
        "state": node.state,
        "state_reason": node.state_reason,
        "labels": list(node.labels),
        "assignees": list(node.assignees),
        "in_progress": node.in_progress,
        "parent": node.parent,
        "sub_issues": list(node.sub_issues),
        "blocked_by": list(node.blocked_by),
        "blocking": list(node.blocking),
        "updated_at": node.updated_at,
        "url": node.url,
        "created_at": node.created_at,
        "closed_at": node.closed_at,
    }


def _anomaly(number: int, code: str, message: str) -> StructureAnomaly:
    return StructureAnomaly(number, code, message)


def _state(value: str | None) -> IssueState:
    lowered = (value or "").lower()
    if lowered not in ("open", "closed"):
        raise ValueError(f"unknown GitHub Issue state: {value!r}")
    return cast("IssueState", lowered)


def _node_from_facts(
    facts: IssueFacts, *, parent: int | None, sub_issues: tuple[int, ...], blocked_by: tuple[int, ...]
) -> tuple[ScopeNode, tuple[StructureAnomaly, ...]] | None:
    kind, kind_anomaly = kind_from_labels(facts.labels)
    if kind is None and kind_anomaly is None:
        return None
    number = facts.number
    if number <= 0 or facts.database_id <= 0:
        raise ValueError("GitHub Issue number and id must be positive")
    anomalies: list[StructureAnomaly] = []
    if kind_anomaly is not None:
        anomalies.append(_anomaly(number, kind_anomaly, f"#{number} has more than one spec-dock kind label; keep one"))
    labels = tuple(sorted(set(facts.labels)))
    node = ScopeNode(
        number=number,
        database_id=facts.database_id,
        id=None if kind is None else scope_id(kind, number),
        kind=kind,
        title=facts.title,
        state=_state(facts.state),
        state_reason=facts.state_reason.lower() if facts.state_reason else None,
        labels=labels,
        assignees=tuple(sorted(set(facts.assignees))),
        in_progress=IN_PROGRESS_LABEL in labels,
        parent=parent,
        sub_issues=sub_issues,
        blocked_by=blocked_by,
        blocking=(),
        updated_at=facts.updated_at,
        url=facts.url,
        created_at=facts.created_at,
        closed_at=facts.closed_at,
    )
    return node, tuple(anomalies)


def build_snapshot(
    repository: str, issues: Iterable[FetchedIssue], *, fetched_at: str, fetch_started_at: str
) -> StructureSnapshot:
    """Build a snapshot from one full read of the kind-labelled Issues of one repository."""
    repository = repository.lower()
    own = _own_slug(repository)
    nodes: dict[int, ScopeNode] = {}
    element: dict[int, tuple[StructureAnomaly, ...]] = {}
    fetched = tuple(issues)
    for issue in fetched:
        number = issue.facts.number
        relation: list[StructureAnomaly] = []
        parent: int | None = None
        if issue.parent is not None:
            if issue.parent.repository.lower() == own:
                parent = issue.parent.number
            else:
                relation.append(_foreign(number, PARENT_FOREIGN_REPOSITORY, "parent", issue.parent))
        children: list[int] = []
        for child in issue.sub_issues:
            if child.repository.lower() == own:
                children.append(child.number)
            else:
                relation.append(_foreign(number, SUB_ISSUE_FOREIGN_REPOSITORY, "sub-issue", child))
        blockers: set[int] = set()
        for blocker in issue.blocked_by:
            if blocker.repository.lower() == own:
                blockers.add(blocker.number)
            else:
                relation.append(_foreign(number, DEPENDENCY_FOREIGN_REPOSITORY, "blocker", blocker))
        built = _node_from_facts(
            issue.facts, parent=parent, sub_issues=tuple(dict.fromkeys(children)), blocked_by=tuple(sorted(blockers))
        )
        if built is None:
            continue
        if number in nodes:
            raise ValueError(f"GitHub returned Issue #{number} twice")
        nodes[number], facts_anomalies = built
        element[number] = facts_anomalies + tuple(relation)
    external: dict[int, ExternalIssue] = {}
    for issue in fetched:
        for blocker in issue.blocked_by:
            if blocker.repository.lower() == own and blocker.number not in nodes:
                external[blocker.number] = ExternalIssue(blocker.number, blocker.title or "", _state(blocker.state))
    return _finish(repository, fetched_at, fetch_started_at, nodes, external, element, ())


def _own_slug(repository: str) -> str:
    host, _, slug = repository.partition("/")
    if host != GITHUB_HOST or slug.count("/") != 1:
        raise ValueError("repository must be github.com/<owner>/<repo>")
    return slug


def _foreign(number: int, code: str, role: str, related: RelatedIssue) -> StructureAnomaly:
    return _anomaly(
        number,
        code,
        f"#{number} has a {role} in another repository ({related.repository.lower()}#{related.number}); "
        "SpecDock keeps it out of this structure",
    )


def _finish(
    repository: str,
    fetched_at: str,
    fetch_started_at: str,
    issues: dict[int, ScopeNode],
    external: dict[int, ExternalIssue],
    element: Mapping[int, tuple[StructureAnomaly, ...]],
    local_writes: tuple[LocalWrite, ...],
) -> StructureSnapshot:
    reverse: dict[int, list[int]] = {number: [] for number in issues}
    for number, node in issues.items():
        for blocker in node.blocked_by:
            if blocker in reverse:
                reverse[blocker].append(number)
    finished = {
        number: replace(node, blocking=tuple(sorted(reverse[number]))) for number, node in sorted(issues.items())
    }
    referenced = {blocker for node in finished.values() for blocker in node.blocked_by if blocker not in finished}
    anomalies = [item for number in finished for item in element.get(number, ())]
    anomalies.extend(_structure_anomalies(finished, element))
    return StructureSnapshot(
        repository=repository,
        fetched_at=fetched_at,
        fetch_started_at=fetch_started_at,
        issues=finished,
        external={number: item for number, item in sorted(external.items()) if number in referenced},
        anomalies=tuple(sorted(anomalies, key=lambda item: (item.number, item.code, item.message))),
        local_writes=local_writes,
    )


@dataclass(frozen=True)
class _GraphNode:
    id: str
    parent_id: str | None


def _structure_anomalies(
    issues: Mapping[int, ScopeNode], element: Mapping[int, tuple[StructureAnomaly, ...]]
) -> list[StructureAnomaly]:
    found: list[StructureAnomaly] = []
    foreign_parent = {
        number for number, items in element.items() if any(item.code == PARENT_FOREIGN_REPOSITORY for item in items)
    }
    broken = set(foreign_parent)
    for number, node in issues.items():
        if node.kind is None:
            continue
        expected = PARENT_KINDS[node.kind]
        if expected is None:
            if node.parent is not None:
                broken.add(number)
                found.append(_anomaly(number, PARENT_INVALID, f"Initiative #{number} must not have a parent"))
            continue
        if node.parent is None:
            broken.add(number)
            if number not in foreign_parent:
                found.append(_anomaly(number, PARENT_MISSING, f"{node.kind} #{number} needs a {expected} parent"))
            continue
        parent = issues.get(node.parent)
        if parent is None or parent.id is None or parent.kind != expected:
            broken.add(number)
            found.append(
                _anomaly(
                    number,
                    PARENT_INVALID,
                    f"{node.kind} #{number} has parent #{node.parent}, which is not a valid {expected} Scope",
                )
            )
    valid: dict[int, bool] = {}

    def is_valid(number: int) -> bool:
        if number not in valid:
            node = issues[number]
            valid[number] = (
                node.id is not None
                and number not in broken
                and (node.parent is None or (node.parent in issues and is_valid(node.parent)))
            )
        return valid[number]

    graph = [number for number in issues if is_valid(number)]
    ids = {number: cast("str", issues[number].id) for number in graph}
    numbers = {scope: number for number, scope in ids.items()}

    def ancestors(number: int) -> set[int]:
        chain: set[int] = set()
        parent = issues[number].parent
        while parent is not None:
            chain.add(parent)
            parent = issues[parent].parent
        return chain

    raw: dict[str, list[str]] = {scope: [] for scope in numbers}
    for number in graph:
        for target in issues[number].blocked_by:
            if target not in ids:
                continue
            if target == number or target in ancestors(number) or number in ancestors(target):
                found.append(
                    _anomaly(
                        number,
                        DEPENDENCY_INVALID,
                        f"#{number} is blocked by #{target}, which is itself, an ancestor or a descendant",
                    )
                )
                continue
            raw[ids[number]].append(ids[target])
    nodes = tuple(_GraphNode(ids[number], ids.get(cast("int", issues[number].parent))) for number in graph)
    edges = {scope: tuple(targets) for scope, targets in raw.items()}
    try:
        validate_dependency_graph(cast("tuple[ScopeView, ...]", nodes), edges)
    except ValueError as error:
        members = _cycle_members(nodes, edges)
        for scope in sorted(members, key=numbers.__getitem__):
            others = ", ".join(f"#{numbers[item]}" for item in sorted(members[scope], key=numbers.__getitem__))
            found.append(
                _anomaly(numbers[scope], DEPENDENCY_CYCLE, f"#{numbers[scope]} is in a dependency cycle with {others}")
            )
        if not members:
            found.append(_anomaly(min(graph), DEPENDENCY_CYCLE, str(error)))
    return found


def _cycle_members(nodes: tuple[_GraphNode, ...], edges: dict[str, tuple[str, ...]]) -> dict[str, set[str]]:
    """Strongly connected components over the same effective-dependency and child edges the rule visits."""
    views = cast("tuple[ScopeView, ...]", nodes)
    children: dict[str, list[str]] = {node.id: [] for node in nodes}
    for node in nodes:
        if node.parent_id is not None:
            children[node.parent_id].append(node.id)
    successors = {
        node.id: [edge.target_id for edge in dependency_listing(views, edges, node.id).effective] + children[node.id]
        for node in nodes
    }
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    members: dict[str, set[str]] = {}

    def connect(scope: str) -> None:
        index[scope] = low[scope] = len(index)
        stack.append(scope)
        on_stack.add(scope)
        for target in successors[scope]:
            if target not in index:
                connect(target)
                low[scope] = min(low[scope], low[target])
            elif target in on_stack:
                low[scope] = min(low[scope], index[target])
        if low[scope] == index[scope]:
            component: set[str] = set()
            while True:
                item = stack.pop()
                on_stack.discard(item)
                component.add(item)
                if item == scope:
                    break
            if len(component) > 1:
                for item in component:
                    members[item] = component - {item}

    for node in nodes:
        if node.id not in index:
            connect(node.id)
    return members


@dataclass(frozen=True)
class UpsertIssue:
    """Reflect an Issue's own fields after a create, edit, label, assignee or reread result."""

    facts: IssueFacts


@dataclass(frozen=True)
class SetParent:
    child: int
    parent: int | None


@dataclass(frozen=True)
class AddBlockedBy:
    number: int
    blocker: int
    external: ExternalIssue | None = None


@dataclass(frozen=True)
class RemoveBlockedBy:
    number: int
    blocker: int


StructureChange = UpsertIssue | SetParent | AddBlockedBy | RemoveBlockedBy


def element_anomalies(snapshot: StructureSnapshot, number: int) -> tuple[StructureAnomaly, ...]:
    return tuple(item for item in snapshot.anomalies_for(number) if item.code in ELEMENT_ANOMALY_CODES)


def apply_changes(
    snapshot: StructureSnapshot, changes: Sequence[StructureChange], *, at: str, command: str
) -> StructureSnapshot:
    """Reflect confirmed GitHub writes immediately and record them as local writes."""
    return _apply(snapshot, changes, at=at, command=command, lenient=False)[0]


def apply_changes_lenient(
    snapshot: StructureSnapshot, changes: Sequence[StructureChange], *, at: str, command: str
) -> tuple[StructureSnapshot, tuple[StructureChange, ...]]:
    """Reflect what fits; a change naming a number this snapshot lacks is skipped and returned (Epic ch. 2)."""
    return _apply(snapshot, changes, at=at, command=command, lenient=True)


def _applicable(issues: Mapping[int, ScopeNode], change: StructureChange) -> bool:
    if isinstance(change, UpsertIssue):
        return True
    if isinstance(change, SetParent):
        return change.child in issues and (change.parent is None or change.parent in issues)
    if isinstance(change, AddBlockedBy):
        return change.number in issues and (change.blocker in issues or change.external is not None)
    return change.number in issues


def _apply(
    snapshot: StructureSnapshot, changes: Sequence[StructureChange], *, at: str, command: str, lenient: bool
) -> tuple[StructureSnapshot, tuple[StructureChange, ...]]:
    parse_timestamp(at)
    issues = dict(snapshot.issues)
    external = dict(snapshot.external)
    element = {number: element_anomalies(snapshot, number) for number in issues}
    touched: set[int] = set()
    skipped: list[StructureChange] = []
    for change in changes:
        if lenient and not _applicable(issues, change):
            skipped.append(change)
            continue
        if isinstance(change, UpsertIssue):
            _upsert(issues, external, element, change.facts)
            touched.add(change.facts.number)
        elif isinstance(change, SetParent):
            touched.update(_set_parent(issues, element, change))
        elif isinstance(change, AddBlockedBy):
            node = _node_for_change(issues, change.number)
            issues[change.number] = replace(node, blocked_by=tuple(sorted({*node.blocked_by, change.blocker})))
            if change.external is not None and change.blocker not in issues:
                external[change.blocker] = change.external
            touched.update((change.number, change.blocker))
        else:
            node = _node_for_change(issues, change.number)
            issues[change.number] = replace(
                node, blocked_by=tuple(item for item in node.blocked_by if item != change.blocker)
            )
            touched.update((change.number, change.blocker))
    writes = (*snapshot.local_writes, LocalWrite(at, command, tuple(sorted(touched))))
    finished = _finish(
        snapshot.repository, snapshot.fetched_at, snapshot.fetch_started_at, issues, external, element, writes
    )
    return finished, tuple(skipped)


def _node_for_change(issues: Mapping[int, ScopeNode], number: int) -> ScopeNode:
    node = issues.get(number)
    if node is None:
        raise ValueError(f"Issue #{number} is not a Scope in this snapshot")
    return node


def _upsert(
    issues: dict[int, ScopeNode],
    external: dict[int, ExternalIssue],
    element: dict[int, tuple[StructureAnomaly, ...]],
    facts: IssueFacts,
) -> None:
    number = facts.number
    previous = issues.get(number)
    built = _node_from_facts(
        facts,
        parent=previous.parent if previous else None,
        sub_issues=previous.sub_issues if previous else (),
        blocked_by=previous.blocked_by if previous else (),
    )
    if built is None:
        issues.pop(number, None)
        element.pop(number, None)
        external[number] = ExternalIssue(number, facts.title, _state(facts.state))
        return
    issues[number], facts_anomalies = built
    relation = tuple(item for item in element.get(number, ()) if item.code in RELATION_ANOMALY_CODES)
    element[number] = facts_anomalies + relation
    external.pop(number, None)


def _set_parent(
    issues: dict[int, ScopeNode], element: dict[int, tuple[StructureAnomaly, ...]], change: SetParent
) -> set[int]:
    child = _node_for_change(issues, change.child)
    touched = {change.child}
    if child.parent is not None and child.parent in issues:
        old = issues[child.parent]
        issues[old.number] = replace(old, sub_issues=tuple(item for item in old.sub_issues if item != change.child))
        touched.add(old.number)
    if change.parent is not None:
        if change.parent in issues:
            new = issues[change.parent]
            siblings = tuple(item for item in new.sub_issues if item != change.child)
            issues[new.number] = replace(new, sub_issues=(*siblings, change.child))
        touched.add(change.parent)
    issues[change.child] = replace(child, parent=change.parent)
    element[change.child] = tuple(
        item for item in element.get(change.child, ()) if item.code != PARENT_FOREIGN_REPOSITORY
    )
    return touched


def merge_refresh(current: StructureSnapshot | None, fresh: StructureSnapshot) -> StructureSnapshot:
    """Overlay writes reflected at or after the refetch started, so a refresh never erases them."""
    if current is None or current.repository != fresh.repository:
        return fresh
    started = parse_timestamp(fresh.fetch_started_at)
    recent = tuple(item for item in current.local_writes if parse_timestamp(item.at) >= started)
    issues = dict(fresh.issues)
    external = dict(fresh.external)
    element = {number: element_anomalies(fresh, number) for number in issues}
    for number in {number for item in recent for number in item.numbers}:
        if number in current.issues:
            issues[number] = current.issues[number]
            element[number] = element_anomalies(current, number)
        else:
            issues.pop(number, None)
            element.pop(number, None)
        if number in current.external:
            external[number] = current.external[number]
    return _finish(fresh.repository, fresh.fetched_at, fresh.fetch_started_at, issues, external, element, recent)


def kind_changes(snapshot: StructureSnapshot, directory_ids: Iterable[str]) -> Mapping[int, KindChange]:
    """Compare catalog `<ID>` names with the kind GitHub now gives the same number (Epic design ch. 2).

    A number whose Issue is missing, or whose kind is undecided (KIND_LABEL_MULTIPLE), is not a kind change.
    """
    found: dict[int, list[str]] = {}
    for name in directory_ids:
        try:
            _, number = parse_scope_id(name)
        except ValueError:
            continue
        node = snapshot.issues.get(number)
        if node is not None and node.id is not None and node.id != name:
            found.setdefault(number, []).append(name)
    return {
        number: KindChange(number, cast("str", snapshot.issues[number].id), tuple(sorted(names)))
        for number, names in sorted(found.items())
    }


def renamed_scope(snapshot: StructureSnapshot, scope_id: str) -> ScopeNode | None:
    """The Scope now holding this ID's number under another kind; it decides an old ID from the snapshot alone."""
    try:
        _, number = parse_scope_id(scope_id)
    except ValueError:
        return None
    node = snapshot.issues.get(number)
    if node is None or node.id is None or node.id == scope_id.strip().lower():
        return None
    return node


def dependency_violations(snapshot: StructureSnapshot, number: int, blocker: int) -> tuple[StructureAnomaly, ...]:
    """Preview the dependency anomalies that adding `number` blocked by `blocker` would introduce."""
    before = {(item.number, item.code) for item in snapshot.anomalies if item.code in _DEPENDENCY_CODES}
    preview = apply_changes(
        snapshot, [AddBlockedBy(number, blocker)], at=snapshot.fetched_at, command="dependency preview"
    )
    return tuple(
        item for item in preview.anomalies if item.code in _DEPENDENCY_CODES and (item.number, item.code) not in before
    )
