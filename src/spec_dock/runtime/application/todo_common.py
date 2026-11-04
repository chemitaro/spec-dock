"""What every `todo` command in a checkout opens first: the linked catalog, its repository, settings and snapshot.

Nothing here contacts GitHub: the repository comes from the origin remote (a local Git read) and the structure
snapshot is the saved one (epic-00547 D-11, D-12).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import functools
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import require_linked
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.domain.todo_record import TodoError
from spec_dock.runtime.domain.todo_settings import Effective, Layer, resolve
from spec_dock.runtime.infra.github_snapshot import SnapshotStore
from spec_dock.runtime.infra.github_structure import GithubRepository, repository_for_checkout
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.infra.todo_store import TodoStore
from spec_dock.runtime.infra.user_config import read_user_todo_settings
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable
    from pathlib import Path

    from spec_dock.runtime.application.canonical_catalog import LinkedCatalog
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.domain.canonical_structure import StructureSnapshot
    from spec_dock.runtime.presentation.envelope import OperationResult


def utc_now() -> datetime:
    """The current time; tests replace it."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def settings_warnings(layers: tuple[Layer, ...]) -> tuple[Diagnostic, ...]:
    return tuple(
        Diagnostic(
            "TODO_SETTINGS_INVALID",
            f"the {layer.layer} settings {layer.path} are skipped: {layer.reason}",
            {"path": layer.path, "layer": layer.layer, "reason": layer.reason},
        )
        for layer in layers
        if layer.state == "invalid"
    )


@dataclass(frozen=True)
class TodoRepository:
    context: ProjectContext
    linked: LinkedCatalog
    store: TodoStore
    repository: GithubRepository | None
    state_root: Path
    settings: Effective

    @property
    def catalog(self) -> Path:
        return self.linked.catalog

    def snapshot(self) -> StructureSnapshot | None:
        if self.repository is None:
            return None
        snapshot, _probe = SnapshotStore(self.state_root, self.repository).load()
        return snapshot

    def warnings(self) -> tuple[Diagnostic, ...]:
        return settings_warnings(self.settings.layers)


def open_repository(context: ProjectContext, namespace: argparse.Namespace) -> TodoRepository:
    """Stop with CANONICAL_NOT_LINKED unless the link is correct (F-03), then read the settings layers."""
    linked = require_linked(context, timeout=namespace.timeout)
    store = TodoStore(linked.catalog)
    try:
        repository: GithubRepository | None = repository_for_checkout(context.root, timeout=namespace.timeout)
    except (ValueError, OSError, RuntimeError):  # no usable origin (GitProcessError is a RuntimeError)
        repository = None
    settings = resolve((read_user_todo_settings(), store.read_settings()))
    return TodoRepository(context, linked, store, repository, resolve_state_root(), settings)


def command_error(error: TodoError) -> CanonicalCommandError:
    details = dict(error.details)
    if error.next_step is not None:
        details.setdefault("next_step", error.next_step)
    return CanonicalCommandError(
        error.code,
        error.message,
        exit_code=error.exit_code,
        recovery=(error.next_step,) if error.next_step else (),
        details=details,
    )


def todo_handler(
    handler: Callable[[argparse.Namespace, ProjectContext], OperationResult[object]],
) -> Callable[[argparse.Namespace, ProjectContext], OperationResult[object]]:
    """Render a domain TodoError the way dispatch renders every canonical failure."""

    @functools.wraps(handler)
    def wrapped(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
        try:
            return handler(namespace, context)
        except TodoError as error:
            raise command_error(error) from error

    return wrapped
