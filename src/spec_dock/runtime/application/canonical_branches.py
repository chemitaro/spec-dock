"""Canonical-mode `branch show/create/switch` (iss-00431).

The default name is the Scope ID itself (`iss-00454`; Epic design ch. 7). Create and switch stop with
SCOPE_KIND_CHANGED when GitHub moved the target to another kind; show only warns. Create and switch keep today's
Git steps (existing refs are never reset; switching needs a clean worktree, holds the clone Start lock and keeps
the selection record). Instead of today's `.meta.json` check of the commit, a commit whose tree still tracks
`spec-dock/initiatives` is refused: checking it out would replace this checkout's catalog link.
"""

from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

from spec_dock.runtime.application.branch_operations import (
    BranchData,
    _capture_selection,
    _check_switch_target,
    _data,
    _fresh_context,
    _verify_selection,
)
from spec_dock.runtime.application.canonical_errors import (
    BASE_HAS_SPECS_RECOVERY,
    CANONICAL_BASE_HAS_SPECS,
    CanonicalCommandError,
)
from spec_dock.runtime.application.canonical_scopes import (
    check_canonical_scope_expectations,
    load_canonical_scopes,
    resolve_canonical_scope,
)
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, EffectStatus, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.work_target_store import StoredSelection


def branch_operation(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, offline=namespace.offline)
    source_selection = _capture_selection(context) if namespace.command_path != "branch show" else None
    selection = read_selection(context, scopes.views, stored=source_selection)
    target = resolve_canonical_scope(context, scopes, namespace.target, selection=selection)
    check_canonical_scope_expectations(
        context,
        scopes,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    if namespace.command_path != "branch show":
        scopes.require_kind_unchanged(target.id)
    name = getattr(namespace, "name", None) or target.id
    if not name.isascii():
        raise ValueError("branch name must be ASCII")
    checked = run_git(context.root, "check-ref-format", "--branch", name, timeout=namespace.timeout)
    if checked != (name + "\n").encode("ascii"):
        raise ValueError("branch must name a literal ref, not checkout shorthand")
    tip = _branch_tip(context, name, namespace.timeout)
    warnings = scopes.warnings()
    if namespace.command_path == "branch create":
        context.require_writer()
        if tip is not None:
            raise ValueError("branch already exists; existing refs are never reset")
        base = parse_commit_oid(
            run_git(
                context.root,
                "rev-parse",
                "--verify",
                "--end-of-options",
                f"{namespace.base}^{{commit}}",
                timeout=namespace.timeout,
            )
        )
        refuse_specs_at(context, base, timeout=namespace.timeout)
        if namespace.dry_run:
            return _planned(namespace, target.id, name, base, "git.branch.create", warnings)
        captured = _require_captured(source_selection)
        _fresh_context(context, namespace.timeout)
        _verify_selection(context, captured)
        try:
            run_git(context.root, "branch", name, base, timeout=namespace.timeout, mutation=True)
        except GitProcessError as error:
            status, created = _observe_create_failure(context, name, base, error, captured, namespace.timeout)
            return _incomplete(
                namespace,
                target.id,
                name,
                created,
                "git.branch.create",
                status,
                error,
                switched=False,
                warnings=warnings,
            )
        try:
            _fresh_context(context, namespace.timeout)
            if _branch_tip(context, name, namespace.timeout) != base:
                raise ValueError("created branch differs from the fixed base commit")
            _verify_selection(context, captured)
        except (OSError, ValueError, RuntimeError) as error:
            return _incomplete(
                namespace,
                target.id,
                name,
                base,
                "git.branch.create",
                "succeeded",
                error,
                switched=False,
                warnings=warnings,
            )
        return OperationResult(
            namespace.command_path,
            "succeeded",
            _data(target.id, name, base, created=True, switched=False),
            0,
            effects=(Effect("git.branch.create", "succeeded", name),),
            warnings=warnings,
        )
    if namespace.command_path == "branch switch":
        context.require_writer()
        if tip is None:
            raise LookupError("requested branch ref is missing")
        refuse_specs_at(context, tip, timeout=namespace.timeout)
        _check_switch_target(context, name, timeout=namespace.timeout)
        if namespace.dry_run:
            return _planned(namespace, target.id, name, tip, "git.checkout", warnings)
        return _switch(namespace, context, target.id, name, tip, _require_captured(source_selection), warnings)
    return OperationResult(
        namespace.command_path,
        "succeeded",
        _data(target.id, name, tip, created=False, switched=False),
        0,
        warnings=warnings,
    )


def refuse_specs_at(context: ProjectContext, commit: str, *, timeout: float) -> None:
    """Stop before writing when the commit's tree tracks spec-dock/initiatives (a pre-migration commit)."""
    listed = run_git(context.root, "ls-tree", "--name-only", commit, "--", LINK_RELATIVE.as_posix(), timeout=timeout)
    if listed.strip():
        raise CanonicalCommandError(
            CANONICAL_BASE_HAS_SPECS,
            f"commit {commit} still tracks {LINK_RELATIVE}; checking it out would replace the catalog link",
            recovery=(BASE_HAS_SPECS_RECOVERY,),
            details={"commit": commit, "path": LINK_RELATIVE.as_posix(), "next_step": BASE_HAS_SPECS_RECOVERY},
        )


def _switch(
    namespace: argparse.Namespace,
    context: ProjectContext,
    scope_id: str,
    name: str,
    tip: str,
    source_selection: StoredSelection,
    warnings: tuple[Diagnostic, ...],
) -> OperationResult[object]:
    with ExitStack() as held:
        try:
            lock = held.enter_context(StartLock(context.common_dir, timeout=namespace.lock_timeout))
        except StartLockBusy as error:
            return OperationResult(
                namespace.command_path,
                "failed",
                _data(scope_id, name, tip, created=False, switched=False),
                3,
                error=Diagnostic("START_LOCK_BUSY", str(error), {}),
            )
        lock.verify()
        if lock.identity != context.clone_identity:
            raise ValueError("Git project physical identity changed")
        _check_switch_target(context, name, timeout=namespace.timeout)
        current = _fresh_context(context, namespace.timeout)
        _verify_selection(context, source_selection)
        if current.branch == name and current.head == tip:
            if run_git(current.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                raise ValueError("branch switch requires a clean worktree")
            return OperationResult(
                namespace.command_path,
                "unchanged",
                _data(scope_id, name, tip, created=False, switched=False),
                0,
                effects=(Effect("git.checkout", "unchanged", name),),
                warnings=warnings,
            )
        try:
            run_git(context.root, "checkout", name, timeout=namespace.timeout, mutation=True)
        except GitProcessError as error:
            status, moved, verification_error = _observe_switch_failure(
                context, name, tip, error, source_selection, namespace.timeout
            )
            return _incomplete(
                namespace,
                scope_id,
                name,
                tip,
                "git.checkout",
                status,
                error,
                switched=moved,
                warnings=warnings,
                verification_error=verification_error,
            )
        try:
            after = _fresh_context(context, namespace.timeout)
            if after.branch != name or after.head != tip:
                raise ValueError("checkout differs from the fixed branch snapshot")
            if run_git(after.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                raise ValueError("checkout left a dirty worktree")
            _verify_selection(after, source_selection)
        except (OSError, ValueError, RuntimeError) as error:
            return _incomplete(
                namespace, scope_id, name, tip, "git.checkout", "succeeded", error, switched=True, warnings=warnings
            )
    return OperationResult(
        namespace.command_path,
        "succeeded",
        _data(scope_id, name, tip, created=False, switched=True),
        0,
        effects=(Effect("git.checkout", "succeeded", name),),
        warnings=warnings,
    )


def _observe_create_failure(
    context: ProjectContext,
    name: str,
    base: str,
    error: GitProcessError,
    captured: StoredSelection,
    timeout: float,
) -> tuple[EffectStatus, str | None]:
    """The legacy `branch_operations` reading after a failed `git branch`; a failed reread leaves it unknown."""
    status: EffectStatus = "unknown"
    created: str | None = None
    try:
        after = _fresh_context(context, timeout)
        created = _branch_tip(after, name, timeout)
        if created is not None:
            if created == base:
                status = "succeeded"
        elif not error.uncertain:
            status = "failed"
        _verify_selection(after, captured)
    except (OSError, ValueError, RuntimeError):
        pass
    return status, created


def _observe_switch_failure(
    context: ProjectContext,
    name: str,
    tip: str,
    error: GitProcessError,
    captured: StoredSelection,
    timeout: float,
) -> tuple[EffectStatus, bool, str | None]:
    """The legacy reading after a failed `git checkout`: on the target, or certainly back where it was."""
    status: EffectStatus = "unknown"
    switched = False
    try:
        after = _fresh_context(context, timeout)
        if after.branch == name and after.head == tip:
            status, switched = "succeeded", True
            if run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                raise ValueError("checkout left a dirty worktree")
            _verify_selection(after, captured)
        elif after.branch == context.branch and after.head == context.head and not error.uncertain:
            _verify_selection(after, captured)
            if not run_git(after.root, "status", "--porcelain", "-z", timeout=timeout):
                status = "failed"
    except (OSError, ValueError, RuntimeError) as verification:
        return status, switched, str(verification)
    return status, switched, None


def _branch_tip(context: ProjectContext, name: str, timeout: float) -> str | None:
    observed = run_git(
        context.root, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}", timeout=timeout, missing_ok=True
    )
    return parse_commit_oid(observed) if observed else None


def _planned(
    namespace: argparse.Namespace,
    scope_id: str,
    name: str,
    tip: str,
    effect: str,
    warnings: tuple[Diagnostic, ...],
) -> OperationResult[object]:
    data = _data(scope_id, name, tip, created=False, switched=False)
    return OperationResult(
        namespace.command_path,
        "planned",
        BranchData({**data.result, "can_apply": True, "blockers": ()}),
        0,
        effects=(Effect(effect, "planned", name),),
        warnings=warnings,
    )


def _incomplete(
    namespace: argparse.Namespace,
    scope_id: str,
    name: str,
    tip: str | None,
    effect: str,
    status: EffectStatus,
    error: Exception,
    *,
    switched: bool,
    warnings: tuple[Diagnostic, ...],
    verification_error: str | None = None,
) -> OperationResult[object]:
    """A Git failure or a failed check after the write; an applied or uncertain effect makes it partial (exit 6)."""
    partial = status != "failed"
    if isinstance(error, GitProcessError):
        details = error.details()
        if verification_error is not None:
            details = {**details, "verification_error": verification_error}
        diagnostic = Diagnostic("GIT_FAILED", str(error), details)
    else:
        code = "BRANCH_VERIFICATION_FAILED" if effect == "git.branch.create" else "CHECKOUT_VERIFICATION_FAILED"
        diagnostic = Diagnostic(code, str(error), {})
    return OperationResult(
        namespace.command_path,
        "partial" if partial else "failed",
        _data(scope_id, name, tip, created=effect == "git.branch.create" and tip is not None, switched=switched),
        6 if partial else 5,
        effects=(Effect(effect, status, name),),
        error=diagnostic,
        warnings=warnings,
    )


def _require_captured(selection: StoredSelection | None) -> StoredSelection:
    if selection is None:
        raise RuntimeError("the direct selection was not captured before a Git branch mutation")
    return selection
