"""Inputs of the legacy dashboard renderers, built from the structure snapshot (iss-00438, Epic ch. 13).

The shapes follow presentation/json_state.py (_build_state_payloads, _build_deps_issues_v2_payload,
_build_deps_raw_payload) so the renderers draw the same files. States come from canonical_readiness: DOING is
the in-progress label on any PC, and titles are GitHub's. Aggregating states from descendants is epic-00427's.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_readiness import evaluate_all
from spec_dock.runtime.domain.canonical_structure import PARENT_KINDS
from spec_dock.runtime.domain.ids import deps_node_sort_key
from spec_dock.runtime.domain.lifecycle import observe_github_state

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from spec_dock.runtime.domain.canonical_readiness import ScopeReadiness
    from spec_dock.runtime.domain.canonical_structure import ScopeNode, StructureSnapshot

DASHBOARD_FILES: Final = ("dashboard.md", "tree.puml", "tree-all.puml", "deps-issues.puml", "deps-raw.puml")
# Raise when the drawn shape changes, so an updated SpecDock redraws files whose structure did not change.
DASHBOARD_FORMAT: Final = 1
BLOCKERS_TOP_LIMIT: Final = 5  # the legacy readiness payload kept the first five blockers


@dataclass(frozen=True)
class DashboardInputs:
    index_nodes: dict[str, object]  # _render_dashboard_md
    tree: dict[str, object]  # _render_tree_ready_board_puml, drawn with todo_only True and False
    deps_issues: dict[str, object]  # _render_deps_issues_puml
    deps_raw: dict[str, object]  # _render_deps_raw_puml


def input_hash(snapshot: StructureSnapshot, *, snapshot_path: str = "") -> str:
    """SHA-256 of what the files show: `issues`, `external` and the anomalies (a foreign relation changes a
    state without changing `issues`), plus the drawing format and the snapshot path of the Observability line.
    Fetch times and local writes do not count."""
    document = snapshot.to_json()
    text = json.dumps(
        {
            "format": DASHBOARD_FORMAT,
            "snapshot_path": snapshot_path,
            "issues": document["issues"],
            "external": document["external"],
            "anomalies": document["anomalies"],
        },
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def dashboard_inputs(snapshot: StructureSnapshot) -> DashboardInputs:
    view = _View(snapshot)
    return DashboardInputs(view.index_nodes(), view.tree(), view.deps_issues(), view.deps_raw())


def _sorted(ids: Iterable[str]) -> list[str]:
    return sorted(ids, key=deps_node_sort_key)


class _View:
    def __init__(self, snapshot: StructureSnapshot) -> None:
        self.snapshot = snapshot
        self.readiness: Mapping[str, ScopeReadiness] = evaluate_all(snapshot)
        self.nodes: dict[str, ScopeNode] = {node.id: node for node in snapshot.scopes if node.id is not None}
        self.children: dict[str, list[str]] = {scope: [] for scope in self.nodes}
        for scope, node in self.nodes.items():
            parent = self._parent(node)
            if parent is not None:
                self.children[parent].append(scope)

    def _parent(self, node: ScopeNode) -> str | None:
        """The parent Scope ID when it is the kind the hierarchy expects; otherwise the node is not nested."""
        if node.parent is None or node.kind is None:
            return None
        parent = self.snapshot.issues.get(node.parent)
        if parent is None or parent.id is None or parent.kind != PARENT_KINDS[node.kind]:
            return None
        return parent.id

    def _of_kind(self, kind: str, scopes: Iterable[str]) -> list[str]:
        return _sorted(scope for scope in scopes if self.nodes[scope].kind == kind)

    def _blockers_top(self, scope: str) -> list[str]:
        """Blocking Scopes in ID order, then non-Scope Issues as #N, cut like the legacy payload."""
        blockers = [blocker for blocker in self.readiness[scope].blockers if blocker.role != "self"]
        scopes = _sorted({blocker.scope_id for blocker in blockers if blocker.scope_id is not None})
        external = sorted({blocker.number for blocker in blockers if blocker.scope_id is None})
        return [*scopes, *(f"#{number}" for number in external)][:BLOCKERS_TOP_LIMIT]

    def _issue_item(self, scope: str) -> dict[str, object]:
        node = self.nodes[scope]
        readiness = self.readiness[scope]
        return {
            "type": "issue",
            "title": node.title,
            "status": "done" if node.state == "closed" else "open",
            "board_state": readiness.state,
            "deps": {"ready": readiness.ready, "blockers_top": self._blockers_top(scope)},
        }

    def index_nodes(self) -> dict[str, object]:
        return {scope: self._issue_item(scope) for scope in self._of_kind("issue", self.nodes)}

    def tree(self) -> dict[str, object]:
        initiatives: list[dict[str, object]] = []
        for initiative in self._of_kind("initiative", self.nodes):
            epics: list[dict[str, object]] = []
            for epic in self._of_kind("epic", self.children[initiative]):
                issues: list[dict[str, object]] = [
                    {"id": issue, **self._issue_item(issue)} for issue in self._of_kind("issue", self.children[epic])
                ]
                epics.append({"id": epic, "title": self.nodes[epic].title, "issues": issues})
            initiatives.append({"id": initiative, "title": self.nodes[initiative].title, "epics": epics})
        return {"tree": initiatives}

    def _done(self, scope: str) -> bool:
        return self.nodes[scope].state == "closed"

    def _deps_node(self, scope: str) -> dict[str, object]:
        node = self.nodes[scope]
        if node.kind == "issue":
            readiness = self.readiness[scope]
            return {"type": "issue", "state": readiness.state.lower(), "ready": readiness.ready}
        return {"type": node.kind, "state": node.state, "ready": node.state == "closed"}

    def deps_issues(self) -> dict[str, object]:
        include = {scope for scope in self._of_kind("issue", self.nodes) if not self._done(scope)}
        edges: list[dict[str, str]] = []
        for scope in _sorted(include):
            for blocker in self.readiness[scope].blockers:
                if blocker.role != "prerequisite" or blocker.scope_id not in self.nodes:
                    continue
                edge = {"from": scope, "to": blocker.scope_id, "state": "blocking"}
                if edge not in edges:
                    edges.append(edge)
        include.update(edge["to"] for edge in edges)
        edges.sort(key=lambda edge: (deps_node_sort_key(edge["from"]), deps_node_sort_key(edge["to"])))
        return {
            "nodes": {scope: self._deps_node(scope) for scope in _sorted(include)},
            "edges": edges,
        }

    def _descendant_issues(self, scope: str) -> list[str]:
        found: list[str] = []
        pending = [scope]
        while pending:
            current = pending.pop()
            for child in self.children[current]:
                if self.nodes[child].kind == "issue":
                    found.append(child)
                pending.append(child)
        return found

    def _in_progress_raw(self, scope: str) -> bool:
        """Legacy _node_is_active_raw_participant: open, and a high-level Scope still has an open Issue."""
        if self.nodes[scope].kind == "issue":
            return not self._done(scope)
        issues = self._descendant_issues(scope)
        if issues and all(self._done(issue) for issue in issues):
            return False
        return not self._done(scope)

    def deps_raw(self) -> dict[str, object]:
        participants: set[str] = set()
        edges: list[dict[str, str]] = []
        for dependent in _sorted(self.nodes):
            for number in sorted(self.nodes[dependent].blocked_by):
                prerequisite = self.snapshot.issues.get(number)
                if prerequisite is None or prerequisite.id not in self.nodes:
                    continue
                target = prerequisite.id
                if not (self._in_progress_raw(dependent) and self._in_progress_raw(target)):
                    continue
                if observe_github_state(prerequisite.state, prerequisite.state_reason) == "completed":
                    continue
                participants.update((dependent, target))
                edges.append({"from": dependent, "to": target})
        edges.sort(key=lambda edge: (deps_node_sort_key(edge["from"]), deps_node_sort_key(edge["to"])))
        include = set(participants)
        pending = list(participants)
        while pending:
            parent = self._parent(self.nodes[pending.pop()])
            if parent is not None and parent not in include:
                include.add(parent)
                pending.append(parent)

        def high_level(scope: str, children: list[dict[str, object]], key: str) -> dict[str, object]:
            return {
                "id": scope,
                "title": self.nodes[scope].title,
                "state": self.nodes[scope].state,
                "state_source": "github",
                key: children,
            }

        tree: list[dict[str, object]] = []
        for initiative in self._of_kind("initiative", include):
            epics: list[dict[str, object]] = []
            for epic in self._of_kind("epic", set(self.children[initiative]) & include):
                issues: list[dict[str, object]] = [
                    {"id": issue, "title": self.nodes[issue].title, "state": self.readiness[issue].state.lower()}
                    for issue in self._of_kind("issue", set(self.children[epic]) & include)
                ]
                epics.append(high_level(epic, issues, "issues"))
            tree.append(high_level(initiative, epics, "epics"))
        return {"tree": tree, "edges": edges}
