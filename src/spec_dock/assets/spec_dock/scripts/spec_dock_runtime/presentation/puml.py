from __future__ import annotations

from typing import Any

from ..render_puml import _render_deps_disabled_deps_issues_puml
from ..render_puml import _render_deps_disabled_tree_puml
from ..render_puml import _render_deps_issues_puml
from ..render_puml import _render_tree_ready_board_puml


def render_tree_ready_board_puml(
    tree_state: dict[str, Any],
    *,
    active: dict[str, Any] | None,
    todo_only: bool,
) -> str:
    return _render_tree_ready_board_puml(tree_state, active=active, todo_only=todo_only)


def render_deps_disabled_tree_puml(*, todo_only: bool, error: str | None) -> str:
    return _render_deps_disabled_tree_puml(todo_only=todo_only, error=error)


def render_deps_issues_puml(deps_issues_state: dict[str, Any]) -> str:
    return _render_deps_issues_puml(deps_issues_state)


def render_deps_disabled_deps_issues_puml(*, error: str | None) -> str:
    return _render_deps_disabled_deps_issues_puml(error=error)
