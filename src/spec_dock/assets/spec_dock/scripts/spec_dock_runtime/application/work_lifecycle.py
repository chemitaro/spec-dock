"""Compose work transitions from fixed Scope and selection snapshots."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import TYPE_CHECKING

from spec_dock_runtime.application.active_selection import clear_selection, select_scope
from spec_dock_runtime.application.branch_vnext import (
    _git,
    _resolve_commit,
    _verify_scope_at_commit,
    create_scope_branch,
    show_scope_branch,
)
from spec_dock_runtime.application.dependency_vnext import check_scope_readiness
from spec_dock_runtime.application.operation_executor import (
    prepare_operation,
    record_effect_intent,
    record_effect_observation,
    record_effect_result,
)
from spec_dock_runtime.application.scope_completion import _descendants, plan_close
from spec_dock_runtime.application.scope_query import load_scope_views, show_scope
from spec_dock_runtime.cli.admission import admit_writer
from spec_dock_runtime.domain.lifecycle import (
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    SelectionState,
    decode_scope_metadata,
    encode_scope_metadata,
)
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3
from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.git_cli import worktree_list
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json
from spec_dock_runtime.infra.operation_journal import JournalStore
from spec_dock_runtime.infra.writer_lock import WriterLock

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from spec_dock_runtime.application.scope_completion import CompletionDecision
    from spec_dock_runtime.application.scope_query import ScopeView
    from spec_dock_runtime.domain.dependency_vnext import ReadinessResult
    from spec_dock_runtime.domain.lifecycle import ObservedState


@dataclass(frozen=True)
class WorkFinishPlan:
    target_id: str
    completion: CompletionDecision
    selection_after: SelectionState


@dataclass(frozen=True)
class WorkFinishResult:
    target_id: str
    completion_changed: bool
    selection_changed: bool
    operation_id: str | None


@dataclass(frozen=True)
class WorkStartPlan:
    target_id: str
    selection_after: SelectionState
    stale: bool


@dataclass(frozen=True)
class WorkStartResult:
    target_id: str
    branch: str
    selection_changed: bool
    operation_id: str


def _ancestry(views: tuple[ScopeView, ...], scope_id: str) -> tuple[str, ...]:
    by_id = {view.id: view for view in views}
    result: list[str] = []
    current = by_id[scope_id]
    while current.parent_id is not None:
        if current.parent_id not in by_id or current.parent_id in result:
            raise ValueError("Scope ancestry is missing or cyclic")
        result.append(current.parent_id)
        current = by_id[current.parent_id]
    return tuple(result)


def plan_start_work(
    views: tuple[ScopeView, ...],
    *,
    target: str,
    selection: SelectionState,
    current_state: ObservedState | None,
    readiness: ReadinessResult,
    switch_active: bool,
) -> WorkStartPlan:
    """Fix a ready Scope and guard cross-branch selection changes."""
    scope = show_scope(views, target, selection=selection)
    if readiness.target_id != scope.id or not readiness.ready:
        raise ValueError("START_NOT_READY")
    focus_id = selection.focus_id
    if focus_id is not None:
        if current_state not in ("open", "completed", "not-planned", "unknown"):
            raise ValueError("CURRENT_STATUS_UNOBSERVED")
        related = (
            focus_id == scope.id or focus_id in _ancestry(views, scope.id) or scope.id in _ancestry(views, focus_id)
        )
        if not related and current_state in ("open", "unknown") and not switch_active:
            raise ValueError("SWITCH_ACTIVE_REQUIRED")
    return WorkStartPlan(scope.id, select_scope(views, scope.id, current=selection), readiness.stale)


def _head_state(repo_root: Path) -> tuple[str, str]:
    branch = _git(repo_root, "branch", "--show-current")
    if branch.returncode != 0:
        raise RuntimeError("current Git branch could not be read")
    return branch.stdout.strip(), _resolve_commit(repo_root, "HEAD")


def _require_clean_start(repo_root: Path) -> None:
    status = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise ValueError("work start requires a clean working tree")


def _current_start_state(
    repo_root: Path, views: tuple[ScopeView, ...], selection: SelectionState, gateway: GithubIssueGateway | None
) -> ObservedState | None:
    if selection.focus_id is None:
        return None
    current = show_scope(views, selection.focus_id)
    if isinstance(current.backend, LocalBackend):
        return current.status.state
    if gateway is None:
        raise ValueError("live GitHub state is required for the current active Scope")
    remote = gateway.get(
        repo_root,
        f"{current.backend.repo_owner}/{current.backend.repo_name}",
        current.backend.issue_number,
    )
    return remote.state


def _start_plan(
    *,
    repo_root: Path,
    worktree_id: str,
    target: str,
    source: str,
    allow_stale: bool,
    offline: bool,
    gateway: GithubIssueGateway | None,
    switch_active: bool,
) -> tuple[tuple[ScopeView, ...], SelectionState, WorkStartPlan]:
    specdock_dir = repo_root / "spec-dock"
    views = load_scope_views(specdock_dir)
    selection, _ = load_selection_v3(specdock_dir, worktree_id=worktree_id)
    readiness = check_scope_readiness(
        specdock_dir,
        target,
        source=source,
        for_start=True,
        allow_stale=allow_stale,
        offline=offline,
        gateway=gateway,
        worktree_id=worktree_id,
    )
    plan = plan_start_work(
        views,
        target=target,
        selection=selection,
        current_state=_current_start_state(repo_root, views, selection, gateway),
        readiness=readiness,
        switch_active=switch_active,
    )
    return views, selection, plan


def start_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target: str,
    base: str | None = None,
    branch_name: str | None = None,
    switch_active: bool = False,
    source: str = "github",
    allow_stale: bool = False,
    offline: bool = False,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> WorkStartResult:
    """Start one ready Scope with fixed checkout and selection effects."""
    _require_clean_start(repo_root)
    _views, selection, plan = _start_plan(
        repo_root=repo_root,
        worktree_id=worktree_id,
        target=target,
        source=source,
        allow_stale=allow_stale,
        offline=offline,
        gateway=gateway,
        switch_active=switch_active,
    )
    try:
        binding = show_scope_branch(repo_root, common_dir, plan.target_id)
        if base is not None:
            raise ValueError("--base is valid only when creating a new canonical branch")
        if branch_name is not None and branch_name != binding.name:
            raise ValueError("requested branch differs from the canonical binding")
    except LookupError:
        if base is None and not _head_state(repo_root)[0]:
            raise ValueError("new work start from detached HEAD requires --base") from None
        binding = create_scope_branch(
            repo_root=repo_root,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            scope_id=plan.target_id,
            base=base or "HEAD",
            name=branch_name,
            lock_timeout=lock_timeout,
        )
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        _require_clean_start(repo_root)
        current_views, current_selection, current_plan = _start_plan(
            repo_root=repo_root,
            worktree_id=worktree_id,
            target=plan.target_id,
            source=source,
            allow_stale=allow_stale,
            offline=offline,
            gateway=gateway,
            switch_active=switch_active,
        )
        if current_selection != selection or current_plan.target_id != plan.target_id:
            raise ValueError("work start inputs changed before checkout")
        if show_scope_branch(repo_root, common_dir, plan.target_id) != binding:
            raise ValueError("canonical branch binding changed before work start")
        for worktree in worktree_list(repo_root):
            if worktree.branch == binding.name and worktree.path.resolve(strict=True) != repo_root.resolve(strict=True):
                raise ValueError("canonical branch is checked out in another worktree")
        branch_tip = _resolve_commit(repo_root, f"refs/heads/{binding.name}")
        _verify_scope_at_commit(repo_root, current_views, plan.target_id, branch_tip)
        source_branch, source_sha = _head_state(repo_root)
        fixed = {
            "scope": plan.target_id,
            "worktree": worktree_id,
            "branch": binding.name,
            "branch_sha": branch_tip,
            "source_branch": source_branch,
            "source_sha": source_sha,
            "selection_before": _selection_chain(selection),
            "selection_after": _selection_chain(current_plan.selection_after),
            "readiness_source": source,
            "allow_stale": str(allow_stale).lower(),
            "offline": str(offline).lower(),
            "switch_active": str(switch_active).lower(),
        }
        assert control is not None
        journal = JournalStore(common_dir)
        operation = prepare_operation(
            command="work.start",
            fixed_targets=fixed,
            effect_plan=("checkout", "selection-set"),
            request_fingerprint=_fingerprint(fixed),
            before_revisions={"selection": selection.revision},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        journal.create(operation)
        checkout_intent = record_effect_intent(operation, effect_id="checkout", kind="git", target=binding.name)
        journal.update(checkout_intent, expected_sequence=operation.sequence)
        if (source_branch, source_sha) != (binding.name, branch_tip):
            switched = _git(repo_root, "switch", "--no-guess", binding.name, timeout=60.0)
            if switched.returncode != 0:
                raise RuntimeError("work start checkout failed; inspect the pending operation")
        _verify_start_checkout(repo_root, fixed)
        checkout_done = record_effect_result(checkout_intent, effect_id="checkout", status="succeeded")
        journal.update(checkout_done, expected_sequence=checkout_intent.sequence)
        _require_start_readiness(
            repo_root,
            plan.target_id,
            source=source,
            allow_stale=allow_stale,
            offline=offline,
            gateway=gateway,
            worktree_id=worktree_id,
        )
        selection_intent = record_effect_intent(
            checkout_done, effect_id="selection-set", kind="local", target=worktree_id
        )
        journal.update(selection_intent, expected_sequence=checkout_done.sequence)
        after_views = load_scope_views(repo_root / "spec-dock")
        after_selection = select_scope(after_views, plan.target_id, current=selection)
        if _selection_chain(after_selection) != fixed["selection_after"]:
            raise ValueError("work start selection changed after checkout")
        _, selection_identity = load_selection_v3(repo_root / "spec-dock", worktree_id=worktree_id)
        if after_selection != selection:
            save_selection_v3(
                repo_root / "spec-dock", after_selection, views=after_views, expected_identity=selection_identity
            )
        selection_done = record_effect_result(
            selection_intent,
            effect_id="selection-set",
            status="succeeded",
            after_revisions={"selection": after_selection.revision},
        )
        journal.update(selection_done, expected_sequence=selection_intent.sequence)
        terminal = replace(
            selection_done, phase="complete", terminal_status="succeeded", sequence=selection_done.sequence + 1
        )
        journal.update(terminal, expected_sequence=selection_done.sequence)
        return WorkStartResult(plan.target_id, binding.name, after_selection != selection, operation.operation_id)


def _verify_start_checkout(repo_root: Path, fixed: Mapping[str, str]) -> None:
    if _head_state(repo_root) != (fixed["branch"], fixed["branch_sha"]):
        raise RuntimeError("work start checkout differs from the recorded branch and SHA")
    _require_clean_start(repo_root)
    views = load_scope_views(repo_root / "spec-dock")
    show_scope(views, fixed["scope"])
    _verify_scope_at_commit(repo_root, views, fixed["scope"], fixed["branch_sha"])


def _require_start_readiness(
    repo_root: Path,
    target: str,
    *,
    source: str,
    allow_stale: bool,
    offline: bool,
    gateway: GithubIssueGateway | None,
    worktree_id: str,
) -> None:
    result = check_scope_readiness(
        repo_root / "spec-dock",
        target,
        source=source,
        for_start=True,
        allow_stale=allow_stale,
        offline=offline,
        gateway=gateway,
        worktree_id=worktree_id,
    )
    if not result.ready:
        raise ValueError("START_NOT_READY after checkout")


def resume_start_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operation_id: str,
    expected_scope_id: str | None = None,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> WorkStartResult:
    """Reconcile an exact pending checkout and selection without a blind branch reset."""
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        if expected_scope_id is not None and fixed.get("scope") != expected_scope_id:
            raise ValueError("work start recovery target differs from the recorded Scope ID")
        revisions = dict(operation.before_revisions)
        if (
            operation.command != "work.start"
            or operation.effect_plan != ("checkout", "selection-set")
            or set(fixed)
            != {
                "scope",
                "worktree",
                "branch",
                "branch_sha",
                "source_branch",
                "source_sha",
                "selection_before",
                "selection_after",
                "readiness_source",
                "allow_stale",
                "offline",
                "switch_active",
            }
            or fixed["worktree"] != worktree_id
            or fixed["readiness_source"] not in ("github", "cache")
            or any(fixed[item] not in ("true", "false") for item in ("allow_stale", "offline", "switch_active"))
            or set(revisions) != {"selection"}
            or operation.request_fingerprint != _fingerprint(fixed)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
        ):
            raise ValueError("work start recovery differs from the recorded request")
        before = _decode_selection_chain(
            fixed["selection_before"], worktree_id=worktree_id, revision=revisions["selection"]
        )
        after = _decode_selection_chain(
            fixed["selection_after"],
            worktree_id=worktree_id,
            revision=before.revision + (fixed["selection_before"] != fixed["selection_after"]),
        )
        if operation.terminal_status == "succeeded":
            return WorkStartResult(fixed["scope"], fixed["branch"], before != after, operation_id)
        if operation.terminal_status != "pending":
            raise ValueError("work start recovery requires a pending operation")
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        binding = show_scope_branch(repo_root, common_dir, fixed["scope"])
        if (
            binding.name != fixed["branch"]
            or _resolve_commit(repo_root, f"refs/heads/{binding.name}") != fixed["branch_sha"]
        ):
            raise ValueError("work start canonical branch changed")
        selection, selection_identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        if selection not in (before, after):
            raise ValueError("work start selection differs from the recorded state")
        current = _head_state(repo_root)
        old = (fixed["source_branch"], fixed["source_sha"])
        desired = (fixed["branch"], fixed["branch_sha"])
        if current not in (old, desired):
            raise ValueError("work start HEAD differs from recorded before/after state")
        _require_clean_start(repo_root)
        if not operation.effects:
            if current != old or selection != before:
                raise ValueError("work start changed before checkout intent")
            advanced = record_effect_intent(operation, effect_id="checkout", kind="git", target=binding.name)
            journal.update(advanced, expected_sequence=operation.sequence)
            operation = advanced
        if operation.effects[0].id != "checkout" or operation.effects[0].target != binding.name:
            raise ValueError("work start checkout effect differs")
        if operation.effects[0].status == "intent":
            if current == old and current != desired:
                for worktree in worktree_list(repo_root):
                    if worktree.branch == binding.name and worktree.path.resolve(strict=True) != repo_root.resolve(
                        strict=True
                    ):
                        raise ValueError("canonical branch is checked out in another worktree")
                switched = _git(repo_root, "switch", "--no-guess", binding.name, timeout=60.0)
                if switched.returncode != 0:
                    raise RuntimeError("work start checkout failed during recovery")
            _verify_start_checkout(repo_root, fixed)
            advanced = record_effect_result(operation, effect_id="checkout", status="succeeded")
            journal.update(advanced, expected_sequence=operation.sequence)
            operation = advanced
        elif operation.effects[0].status != "succeeded":
            raise ValueError("work start checkout effect cannot be reconciled")
        _verify_start_checkout(repo_root, fixed)
        if selection == before:
            _require_start_readiness(
                repo_root,
                fixed["scope"],
                source=fixed["readiness_source"],
                allow_stale=fixed["allow_stale"] == "true",
                offline=fixed["offline"] == "true",
                gateway=gateway,
                worktree_id=worktree_id,
            )
        views = load_scope_views(specdock_dir)
        if select_scope(views, fixed["scope"], current=before) != after:
            raise ValueError("work start selection does not match the fixed Scope")
        if len(operation.effects) == 1:
            if selection != before:
                raise ValueError("work start selection changed before effect intent")
            advanced = record_effect_intent(operation, effect_id="selection-set", kind="local", target=worktree_id)
            journal.update(advanced, expected_sequence=operation.sequence)
            operation = advanced
        if len(operation.effects) != 2 or operation.effects[1].id != "selection-set":
            raise ValueError("work start selection effect differs")
        if operation.effects[1].status == "intent":
            if selection == before and after != before:
                save_selection_v3(specdock_dir, after, views=views, expected_identity=selection_identity)
            advanced = record_effect_result(
                operation,
                effect_id="selection-set",
                status="succeeded",
                after_revisions={"selection": after.revision},
            )
            journal.update(advanced, expected_sequence=operation.sequence)
            operation = advanced
        elif operation.effects[1].status != "succeeded" or selection != after:
            raise ValueError("work start selection effect cannot be reconciled")
        terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
        journal.update(terminal, expected_sequence=operation.sequence)
        return WorkStartResult(fixed["scope"], binding.name, before != after, operation_id)


def plan_finish_work(
    views: tuple[ScopeView, ...],
    *,
    target: str,
    statuses: Mapping[str, ObservedState],
    selection: SelectionState,
) -> WorkFinishPlan:
    """Fix the requested Scope before any lifecycle or active mutation occurs."""
    scope = show_scope(views, target, selection=selection)
    completion = plan_close(views, scope.id, statuses)
    selection_after = clear_selection(views, current=selection, from_target=scope.id)
    return WorkFinishPlan(scope.id, completion, selection_after)


def _fingerprint(fixed: dict[str, str]) -> str:
    encoded = json.dumps(fixed, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _metadata_digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _selection_chain(selection: SelectionState) -> str:
    return json.dumps(
        [selection.initiative_id, selection.epic_id, selection.issue_id, selection.focus_id], separators=(",", ":")
    )


def _live_statuses(
    *, repo_root: Path, views: tuple[ScopeView, ...], scope: ScopeView, gateway: GithubIssueGateway | None
) -> dict[str, ObservedState]:
    statuses: dict[str, ObservedState] = {}
    for view in (scope, *_descendants(views, scope)):
        if isinstance(view.backend, LocalBackend):
            statuses[view.id] = view.status.state
        else:
            if gateway is None:
                raise ValueError("GitHub Scope requires a live gateway for work finish")
            remote = gateway.get(
                repo_root,
                f"{view.backend.repo_owner}/{view.backend.repo_name}",
                view.backend.issue_number,
            )
            statuses[view.id] = remote.state
    return statuses


def finish_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    target: str,
    updated_at: str,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> WorkFinishResult:
    """Record completion and selection clearing as separate resumable effects."""
    if not updated_at:
        raise ValueError("work finish timestamp is required")
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        control = load_control(common_dir)
        admit_writer(
            control,
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
        )
        views = load_scope_views(specdock_dir)
        selection, selection_identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        scope = show_scope(views, target, selection=selection)
        statuses = _live_statuses(repo_root=repo_root, views=views, scope=scope, gateway=gateway)
        plan = plan_finish_work(views, target=scope.id, statuses=statuses, selection=selection)
        selection_changed = plan.selection_after != selection
        if not plan.completion.changed and not selection_changed:
            return WorkFinishResult(scope.id, False, False, None)
        loaded = read_guarded_json(scope.path / ".meta.json")
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing")
        metadata = decode_scope_metadata(loaded[0])
        if type(metadata.backend) is not type(scope.backend) or metadata.revision != scope.revision:
            raise ValueError("Scope metadata changed before work finish")
        next_metadata_payload = loaded[0]
        after_revision = metadata.revision
        if plan.completion.changed and isinstance(metadata.backend, LocalBackend):
            lifecycle = metadata.backend.lifecycle
            next_metadata = replace(
                metadata,
                backend=LocalBackend(LocalLifecycle("completed", lifecycle.revision + 1, updated_at)),
                revision=metadata.revision + 1,
            )
            next_metadata_payload = encode_scope_metadata(next_metadata)
            after_revision = next_metadata.revision
        assert control is not None
        fixed = {
            "scope": scope.id,
            "worktree": worktree_id,
            "backend": "local" if isinstance(metadata.backend, LocalBackend) else "github",
            "github_ref": scope.github_ref or "",
            "updated_at": updated_at,
            "before_state": plan.completion.before,
            "metadata_before_digest": _metadata_digest(loaded[0]),
            "metadata_after_digest": _metadata_digest(next_metadata_payload),
            "selection_before": _selection_chain(selection),
            "selection_after": _selection_chain(plan.selection_after),
            "lifecycle_changed": str(plan.completion.changed).lower(),
        }
        journal = JournalStore(common_dir)
        operation = prepare_operation(
            command="work.finish",
            fixed_targets=fixed,
            effect_plan=("lifecycle-update", "selection-clear"),
            request_fingerprint=_fingerprint(fixed),
            before_revisions={"metadata": metadata.revision, "selection": selection.revision},
            engine_digest=engine_digest,
            writer_epoch=control.epoch,
        )
        journal.create(operation)
        lifecycle_intent = record_effect_intent(
            operation,
            effect_id="lifecycle-update",
            kind="local" if isinstance(metadata.backend, LocalBackend) else "remote",
            target=scope.id,
        )
        journal.update(lifecycle_intent, expected_sequence=operation.sequence)
        if plan.completion.changed and isinstance(metadata.backend, LocalBackend):
            atomic_write_json(scope.path / ".meta.json", next_metadata_payload, expected_identity=loaded[1])
        if plan.completion.changed and isinstance(metadata.backend, GithubBackend):
            if gateway is None:
                raise AssertionError("GitHub gateway was checked before the journal")
            backend = metadata.backend
            try:
                remote = gateway.set_state(
                    repo_root,
                    f"{backend.repo_owner}/{backend.repo_name}",
                    backend.issue_number,
                    state="closed",
                    reason="completed",
                )
                if remote.state != "completed":
                    raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True)
            except RemoteIssueError as error:
                observed = record_effect_result(
                    lifecycle_intent,
                    effect_id="lifecycle-update",
                    status="unknown" if error.uncertain else "failed",
                )
                journal.update(observed, expected_sequence=lifecycle_intent.sequence)
                if not error.uncertain:
                    terminal_failure = replace(
                        observed, phase="complete", terminal_status="failed", sequence=observed.sequence + 1
                    )
                    journal.update(terminal_failure, expected_sequence=observed.sequence)
                raise
        lifecycle_done = record_effect_result(
            lifecycle_intent,
            effect_id="lifecycle-update",
            status="succeeded",
            after_revisions={"metadata": after_revision},
            remote_ref=scope.github_ref if isinstance(metadata.backend, GithubBackend) else None,
        )
        journal.update(lifecycle_done, expected_sequence=lifecycle_intent.sequence)
        selection_intent = record_effect_intent(
            lifecycle_done, effect_id="selection-clear", kind="local", target=worktree_id
        )
        journal.update(selection_intent, expected_sequence=lifecycle_done.sequence)
        if selection_changed:
            save_selection_v3(specdock_dir, plan.selection_after, views=views, expected_identity=selection_identity)
        selection_done = record_effect_result(
            selection_intent,
            effect_id="selection-clear",
            status="succeeded",
            after_revisions={"selection": plan.selection_after.revision},
        )
        journal.update(selection_done, expected_sequence=selection_intent.sequence)
        terminal = replace(
            selection_done, phase="complete", terminal_status="succeeded", sequence=selection_done.sequence + 1
        )
        journal.update(terminal, expected_sequence=selection_done.sequence)
        return WorkFinishResult(scope.id, plan.completion.changed, selection_changed, operation.operation_id)


def _decode_selection_chain(raw: str, *, worktree_id: str, revision: int) -> SelectionState:
    try:
        fields = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("recorded work finish selection is invalid") from error
    if (
        not isinstance(fields, list)
        or len(fields) != 4
        or any(item is not None and not isinstance(item, str) for item in fields)
    ):
        raise ValueError("recorded work finish selection is invalid")
    return SelectionState(worktree_id, revision, *fields)


def resume_finish_work(
    *,
    repo_root: Path,
    common_dir: Path,
    worktree_id: str,
    engine_digest: str,
    expected_epoch: int,
    operation_id: str,
    expected_scope_id: str | None = None,
    gateway: GithubIssueGateway | None = None,
    lock_timeout: float = 0.0,
) -> WorkFinishResult:
    """Reconcile a fixed finish; never blindly resend an uncertain remote effect."""
    specdock_dir = repo_root / "spec-dock"
    with WriterLock(common_dir, timeout=lock_timeout):
        journal = JournalStore(common_dir)
        operation = journal.load(operation_id)
        fixed = dict(operation.fixed_targets)
        if expected_scope_id is not None and fixed.get("scope") != expected_scope_id:
            raise ValueError("work finish recovery target differs from the recorded Scope ID")
        revisions = dict(operation.before_revisions)
        if (
            operation.command != "work.finish"
            or operation.effect_plan != ("lifecycle-update", "selection-clear")
            or set(fixed)
            != {
                "scope",
                "worktree",
                "backend",
                "github_ref",
                "updated_at",
                "before_state",
                "metadata_before_digest",
                "metadata_after_digest",
                "selection_before",
                "selection_after",
                "lifecycle_changed",
            }
            or fixed["worktree"] != worktree_id
            or fixed["backend"] not in ("local", "github")
            or (fixed["backend"] == "local" and fixed["github_ref"] != "")
            or fixed["before_state"] not in ("open", "completed")
            or fixed["lifecycle_changed"] not in ("true", "false")
            or set(revisions) != {"metadata", "selection"}
            or operation.request_fingerprint != _fingerprint(fixed)
            or operation.engine_digest != engine_digest
            or operation.writer_epoch != expected_epoch
        ):
            raise ValueError("work finish recovery differs from the recorded request")
        before_selection = _decode_selection_chain(
            fixed["selection_before"], worktree_id=worktree_id, revision=revisions["selection"]
        )
        after_selection = _decode_selection_chain(
            fixed["selection_after"],
            worktree_id=worktree_id,
            revision=revisions["selection"] + (fixed["selection_before"] != fixed["selection_after"]),
        )
        lifecycle_changed = fixed["lifecycle_changed"] == "true"
        selection_changed = after_selection != before_selection
        if lifecycle_changed != (fixed["before_state"] == "open"):
            raise ValueError("recorded work finish lifecycle transition is invalid")
        if operation.terminal_status == "succeeded":
            return WorkFinishResult(fixed["scope"], lifecycle_changed, selection_changed, operation_id)
        if operation.terminal_status != "pending":
            raise ValueError("work finish recovery requires a pending operation")
        admit_writer(
            load_control(common_dir),
            common_dir=common_dir,
            worktree_id=worktree_id,
            engine_digest=engine_digest,
            expected_epoch=expected_epoch,
            recovery_operation_id=operation_id,
        )
        views = load_scope_views(specdock_dir)
        scope = show_scope(views, fixed["scope"])
        backend_name = "local" if isinstance(scope.backend, LocalBackend) else "github"
        if backend_name != fixed["backend"] or (scope.github_ref or "") != fixed["github_ref"]:
            raise ValueError("recorded work finish backend changed")
        statuses = _live_statuses(repo_root=repo_root, views=views, scope=scope, gateway=gateway)
        plan_close(views, scope.id, statuses)
        if clear_selection(views, current=before_selection, from_target=scope.id) != after_selection:
            raise ValueError("recorded work finish selection does not match the fixed Scope")
        metadata_path = scope.path / ".meta.json"
        loaded = read_guarded_json(metadata_path)
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing during work finish recovery")
        metadata = decode_scope_metadata(loaded[0])
        if type(metadata.backend) is not type(scope.backend) or metadata.raw.get("id") != scope.id:
            raise ValueError("recorded work finish Scope identity changed")
        local = isinstance(metadata.backend, LocalBackend)
        expected_metadata_revision = revisions["metadata"] + (lifecycle_changed and local)
        if local:
            lifecycle = metadata.backend.lifecycle
            applied = (
                lifecycle_changed
                and metadata.revision == expected_metadata_revision
                and lifecycle.state == "completed"
                and lifecycle.updated_at == fixed["updated_at"]
            )
            unapplied = metadata.revision == revisions["metadata"] and lifecycle.state == fixed["before_state"]
        else:
            applied = (
                lifecycle_changed
                and metadata.revision == expected_metadata_revision
                and statuses[scope.id] == "completed"
            )
            unapplied = metadata.revision == revisions["metadata"] and statuses[scope.id] == fixed["before_state"]
        if not applied and not unapplied:
            raise ValueError("work finish metadata differs from recorded before/after state")
        expected_digest = fixed["metadata_after_digest"] if applied else fixed["metadata_before_digest"]
        if _metadata_digest(loaded[0]) != expected_digest:
            raise ValueError("work finish metadata differs from recorded before/after content")
        if operation.effects:
            effect = operation.effects[0]
            if (
                effect.id != "lifecycle-update"
                or effect.target != scope.id
                or effect.kind != ("local" if local else "remote")
            ):
                raise ValueError("recorded work finish lifecycle effect is invalid")
        else:
            if applied:
                raise ValueError("work finish lifecycle changed before effect intent")
            next_record = record_effect_intent(
                operation, effect_id="lifecycle-update", kind="local" if local else "remote", target=scope.id
            )
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if operation.effects[0].status == "intent":
            if local and unapplied and lifecycle_changed:
                if statuses[scope.id] != "open":
                    raise ValueError("work finish lifecycle precondition changed during recovery")
                lifecycle = metadata.backend.lifecycle
                next_metadata = replace(
                    metadata,
                    backend=LocalBackend(LocalLifecycle("completed", lifecycle.revision + 1, fixed["updated_at"])),
                    revision=metadata.revision + 1,
                )
                atomic_write_json(metadata_path, encode_scope_metadata(next_metadata), expected_identity=loaded[1])
            if not local and lifecycle_changed and not applied:
                raise ValueError("remote work finish is not confirmed; refusing a blind retry")
            succeeded = record_effect_result(
                operation,
                effect_id="lifecycle-update",
                status="succeeded",
                after_revisions={"metadata": expected_metadata_revision},
                remote_ref=scope.github_ref if not local else None,
            )
            journal.update(succeeded, expected_sequence=operation.sequence)
            operation = succeeded
        elif operation.effects[0].status == "unknown" and not local:
            if not applied:
                raise ValueError("remote work finish remains uncertain; refusing a blind retry")
            succeeded = record_effect_observation(
                operation,
                effect_id="lifecycle-update",
                outcome="observed_applied",
                after_revisions={"metadata": expected_metadata_revision},
                remote_ref=scope.github_ref,
            )
            journal.update(succeeded, expected_sequence=operation.sequence)
            operation = succeeded
        elif operation.effects[0].status != "succeeded" or (lifecycle_changed and not applied):
            raise ValueError("recorded work finish lifecycle effect cannot be reconciled")
        selection, selection_identity = load_selection_v3(specdock_dir, worktree_id=worktree_id)
        if selection not in (before_selection, after_selection):
            raise ValueError("active selection differs from recorded work finish before/after state")
        if len(operation.effects) == 1:
            if selection_changed and selection == after_selection:
                raise ValueError("work finish selection changed before effect intent")
            next_record = record_effect_intent(operation, effect_id="selection-clear", kind="local", target=worktree_id)
            journal.update(next_record, expected_sequence=operation.sequence)
            operation = next_record
        if len(operation.effects) != 2 or operation.effects[1].id != "selection-clear":
            raise ValueError("recorded work finish selection effect is invalid")
        if operation.effects[1].status == "intent":
            if selection_changed and selection == before_selection:
                save_selection_v3(specdock_dir, after_selection, views=views, expected_identity=selection_identity)
            succeeded = record_effect_result(
                operation,
                effect_id="selection-clear",
                status="succeeded",
                after_revisions={"selection": after_selection.revision},
            )
            journal.update(succeeded, expected_sequence=operation.sequence)
            operation = succeeded
        elif operation.effects[1].status != "succeeded" or selection != after_selection:
            raise ValueError("recorded work finish selection effect cannot be reconciled")
        terminal = replace(operation, phase="complete", terminal_status="succeeded", sequence=operation.sequence + 1)
        journal.update(terminal, expected_sequence=operation.sequence)
        return WorkFinishResult(scope.id, lifecycle_changed, selection_changed, operation_id)
