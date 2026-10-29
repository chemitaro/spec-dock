"""Shared writing side of canonical-mode commands (iss-00432; Epic design ch. 2, 4 and 6).

A command opens one session: the link and catalog format are checked locally first, then the structure
snapshot at `decision` freshness (a change check every time, a refetch after a change or five minutes). The
command rereads the Issues its decision depends on, checks every stop condition, and only then writes. Each
GitHub write goes through `write`, which records the effect and reflects the result into the snapshot at once;
an uncertain write is never repeated. Catalog writes happen under the catalog lock with one changeset.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import sys
from typing import TYPE_CHECKING, TypeVar

from spec_dock.runtime.application.canonical_catalog import (
    LinkedCatalog,
    catalog_changes,
    require_linked,
    require_writable_format,
)
from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.canonical_scopes import OFFLINE_MESSAGE, build_canonical_scopes
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.canonical_structure import (
    LABEL_DEFINITIONS,
    AddBlockedBy,
    ExternalIssue,
    RemoveBlockedBy,
    SetParent,
    UpsertIssue,
)
from spec_dock.runtime.infra.catalog_tree import CatalogTree
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.github_snapshot import GITHUB_SNAPSHOT_STALE, SnapshotStore, StructureSnapshotService
from spec_dock.runtime.infra.github_structure import (
    SYSTEM_CLOCK,
    GithubApi,
    GithubStructureClient,
    GithubStructureError,
    repository_for_checkout,
)
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable, Iterable, Sequence
    from pathlib import Path

    from contextlib import AbstractContextManager

    from spec_dock.runtime.application.canonical_catalog import CatalogChanges
    from spec_dock.runtime.application.canonical_scopes import CanonicalScopes
    from spec_dock.runtime.domain.canonical_changeset import ChangesetOrigin
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.application.worktree_observation import SelectionObservation
    from spec_dock.runtime.domain.canonical_structure import IssueFacts, ScopeNode, StructureChange
    from spec_dock.runtime.infra.github_snapshot import FreshnessLevel
    from spec_dock.runtime.infra.github_structure import GithubClock, GithubRepository
    from spec_dock.runtime.presentation.envelope import EffectStatus, ResultStatus

    ServiceFactory = Callable[[GithubRepository, Path, float], StructureSnapshotService]

_T = TypeVar("_T")

# Tests replace it to check the one-second spacing between writes without waiting.
WRITE_CLOCK: GithubClock = SYSTEM_CLOCK
# The catalog lock wait (Epic ch. 4: up to 10 seconds, then CANONICAL_LOCK_BUSY).
CATALOG_LOCK_TIMEOUT = 10.0

# What a command catches after its first write, to report partial instead of a plain failure.
LOCAL_FAILURES: tuple[type[Exception], ...] = (CanonicalCommandError, ValueError, OSError, RuntimeError, LookupError)

SNAPSHOT_STALE_MESSAGE = (
    "a write was confirmed on GitHub but the structure snapshot could not show it; the next read refetches it"
)


def writing_service(repository: GithubRepository, root: Path, timeout: float) -> StructureSnapshotService:
    api = GithubApi(timeout=timeout, cwd=root, clock=WRITE_CLOCK)
    return StructureSnapshotService(
        repository,
        store=SnapshotStore(resolve_state_root(), repository),
        client=GithubStructureClient(repository, api),
        clock=api.clock,
    )


class WriteFailed(Exception):
    """A GitHub write failed or its result is unknown; the session already recorded the effect."""

    def __init__(self, cause: GithubStructureError) -> None:
        super().__init__(str(cause))
        self.cause = cause


@dataclass
class WriteSession:
    context: ProjectContext
    command: str
    repository: GithubRepository
    service: StructureSnapshotService
    catalog: LinkedCatalog | None
    scopes: CanonicalScopes
    effects: list[Effect] = field(default_factory=list)
    warnings: list[Diagnostic] = field(default_factory=list)
    facts: dict[int, IssueFacts] = field(default_factory=dict)

    @property
    def client(self) -> GithubStructureClient:
        return self.service.client

    def selection(self) -> SelectionObservation:
        return read_selection(self.context, self.scopes.views)

    def resolve(self, selector: str, selection: SelectionObservation) -> ScopeView:
        return resolve_scope(self.context, self.scopes.views, selector, selection=selection)

    def node(self, scope_id: str) -> ScopeNode:
        return self.scopes.node(scope_id)

    def reread(self, numbers: Iterable[int]) -> None:
        """Read the Issues a decision depends on and decide on what GitHub reports now (R-I4)."""
        changes: list[StructureChange] = []
        for number in dict.fromkeys(numbers):
            facts = self.client.get_issue(number)
            self.facts[number] = facts
            changes.append(UpsertIssue(facts))
        if changes:
            self.reflect(changes, command=f"{self.command} (reread)")

    def reread_parent(self, number: int) -> None:
        """Decide on the parent GitHub reports now; a non-Scope or foreign parent is left as the snapshot has it."""
        parent = self.client.get_parent(number)
        if parent is None:
            self.reflect([SetParent(number, None)], command=f"{self.command} (reread)")
        elif parent.repository == self.repository.slug and parent.number in self.scopes.snapshot.issues:
            self.reflect([SetParent(number, parent.number)], command=f"{self.command} (reread)")

    def reread_blockers(self, number: int) -> None:
        """Replace the snapshot's blocked-by edges of `number` with GitHub's current same-repository ones."""
        current = {
            item.number: item
            for item in self.client.list_blocked_by(number)
            if item.repository == self.repository.slug
        }
        known = set(self.scopes.snapshot.issues[number].blocked_by) if number in self.scopes.snapshot.issues else set()
        changes: list[StructureChange] = [RemoveBlockedBy(number, blocker) for blocker in sorted(known - set(current))]
        for blocker in sorted(set(current) - known):
            item = current[blocker]
            state = "closed" if item.state == "closed" else "open"
            changes.append(AddBlockedBy(number, blocker, ExternalIssue(blocker, item.title or "", state)))
        if changes:
            self.reflect(changes, command=f"{self.command} (reread)")

    def reflect(self, changes: Sequence[StructureChange], *, command: str | None = None) -> None:
        reflection = self.service.reflect_writes(changes, command=command or self.command)
        if reflection.skipped and not any(item.code == GITHUB_SNAPSHOT_STALE for item in self.warnings):
            self.warnings.append(Diagnostic(GITHUB_SNAPSHOT_STALE, SNAPSHOT_STALE_MESSAGE, {}))
        if reflection.snapshot is not None:
            self.scopes = build_canonical_scopes(
                self.context,
                self.repository,
                replace(self.scopes.fresh, snapshot=reflection.snapshot),
                self.catalog,
            )

    def catalog_changes(self, *, origin: ChangesetOrigin = "command") -> AbstractContextManager[CatalogChanges]:
        """The catalog lock and one changeset for this command's catalog writes."""
        assert self.catalog is not None
        return catalog_changes(self.catalog.catalog, command=self.command, origin=origin, timeout=CATALOG_LOCK_TIMEOUT)

    def reload_catalog(self) -> None:
        """See directories created or moved by this command."""
        if self.catalog is not None:
            self.catalog = LinkedCatalog(self.catalog.layout, self.catalog.catalog, CatalogTree(self.catalog.catalog))
            self.scopes = build_canonical_scopes(self.context, self.repository, self.scopes.fresh, self.catalog)

    def write(
        self,
        kind: str,
        target: str | None,
        call: Callable[[], _T],
        changes: Callable[[_T], Sequence[StructureChange]] | None = None,
    ) -> _T:
        try:
            value = call()
        except GithubStructureError as error:
            self.effects.append(Effect(kind, "unknown" if error.uncertain else "failed", target))
            raise WriteFailed(error) from error
        self.effects.append(Effect(kind, "succeeded", target))
        if changes is not None:
            self.reflect(changes(value))
        return value

    def known_facts(self, number: int) -> IssueFacts:
        known = self.facts.get(number)
        if known is None:
            known = self.client.get_issue(number)
            self.facts[number] = known
        return known

    def ensure_labels(self, names: Sequence[str]) -> None:
        """Create missing label definitions; a label any snapshot Issue carries already exists."""
        carried = {label for node in self.scopes.snapshot.issues.values() for label in node.labels}
        definitions = {definition.name: definition for definition in LABEL_DEFINITIONS}
        for name in names:
            if name in carried or self.client.label_exists(name):
                continue
            definition = definitions[name]
            self.write("github.label.create", name, lambda definition=definition: self.client.create_label(definition))

    def result(
        self, status: ResultStatus, data: object, *, effects: Sequence[Effect] | None = None
    ) -> OperationResult[object]:
        return OperationResult(
            self.command,
            status,
            data,
            0,
            effects=tuple(self.effects if effects is None else effects),
            warnings=tuple(self.warnings),
        )

    def incomplete(
        self,
        data: object,
        error: Exception,
        *,
        pending: Sequence[tuple[str, str | None]] = (),
        recovery: Sequence[str] = (),
        code: str = "CANONICAL_WRITE_INCOMPLETE",
    ) -> OperationResult[object]:
        """Report what was applied, what is unknown and what was not attempted; never roll back."""
        effects = [*self.effects, *(Effect(kind, "not_attempted", target) for kind, target in pending)]
        applied = any(effect.status in ("succeeded", "unknown") for effect in effects)
        diagnostic = diagnostic_for(error, code)
        if not applied:
            effects = [effect for effect in effects if effect.status != "not_attempted"]
        return OperationResult(
            self.command,
            "partial" if applied else "failed",
            data,
            6 if applied else _failure_exit(error),
            effects=tuple(effects),
            warnings=tuple(self.warnings),
            error=diagnostic,
            recovery=RecoveryInstructions(tuple(recovery)) if recovery else None,
        )


def _failure_exit(error: Exception) -> int:
    if isinstance(error, CanonicalCommandError):
        return error.exit_code
    return 3 if isinstance(error, ValueError) else 4 if isinstance(error, LookupError) else 5


def diagnostic_for(error: Exception, code: str) -> Diagnostic:
    cause = error.cause if isinstance(error, WriteFailed) else error
    if isinstance(cause, GithubStructureError):
        details: dict[str, object] = {"status": cause.status, "endpoint": cause.endpoint}
        if cause.retry_at is not None:
            details["retry_at"] = cause.retry_at
        return Diagnostic(cause.code, cause.message, details)
    if isinstance(cause, GitProcessError):
        return Diagnostic("GIT_FAILED", str(cause), cause.details())
    code_of = getattr(cause, "code", None)
    return Diagnostic(code_of if isinstance(code_of, str) else code, str(cause), dict(getattr(cause, "details", {})))


def open_write_session(
    context: ProjectContext,
    namespace: argparse.Namespace,
    *,
    link: bool,
    level: FreshnessLevel = "decision",
    refresh: bool = False,
    service_factory: ServiceFactory | None = None,
) -> WriteSession:
    """Local checks first (link, catalog format), then the snapshot; any failure here precedes every write.

    With `link`, the command writes catalog files and needs a correct link and a writable format. `refresh`
    refetches the whole structure instead of a change check (for decisions over every relation).
    """
    if namespace.offline:
        raise ValueError(OFFLINE_MESSAGE)
    catalog: LinkedCatalog | None
    if link:
        catalog = require_linked(context, timeout=namespace.timeout)
        require_writable_format(catalog.catalog)
    else:
        try:  # a command that writes no file still shows directories through a correct link
            catalog = require_linked(context, timeout=namespace.timeout)
        except (CanonicalCommandError, GitProcessError, OSError):
            catalog = None
    repository = repository_for_checkout(context.root, timeout=namespace.timeout)
    service = (service_factory or writing_service)(repository, context.root, namespace.timeout)
    fresh = service.refresh() if refresh else service.ensure_fresh(level)
    scopes = build_canonical_scopes(context, repository, fresh, catalog)
    return WriteSession(context, namespace.command_path, repository, service, catalog, scopes)


def check_expectations(
    session: WriteSession, namespace: argparse.Namespace, selection: SelectionObservation, target: ScopeView | None
) -> None:
    check_scope_expectations(
        session.context,
        session.scopes.views,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )


def needs_confirmation(namespace: argparse.Namespace) -> bool:
    """True when the command would have to prompt but cannot: no --yes, not a dry run, and no TTY or JSON mode."""
    return (
        not namespace.yes
        and not namespace.dry_run
        and (namespace.json or namespace.non_interactive or not sys.stdin.isatty())
    )


def confirmed_interactively(namespace: argparse.Namespace, lines: Sequence[str]) -> bool:
    """Prompt on the terminal unless --yes or a dry run; the legacy prompt shape."""
    if namespace.yes or namespace.dry_run:
        return True
    for line in lines:
        print(line, file=sys.stderr)
    print("Confirm [yes/no]: ", end="", file=sys.stderr, flush=True)
    return sys.stdin.readline().strip().lower() in {"yes", "y"}


def declined(command: str, data: object) -> OperationResult[object]:
    return OperationResult(
        command, "failed", data, 3, error=Diagnostic("CONFIRMATION_DECLINED", "operation was not confirmed", {})
    )


def planned(command: str, data: object, effects: Sequence[tuple[str, str | None]], warnings=()) -> OperationResult[object]:
    status: EffectStatus = "planned"
    return OperationResult(
        command,
        "planned",
        data,
        0,
        effects=tuple(Effect(kind, status, target) for kind, target in effects),
        warnings=tuple(warnings),
    )
