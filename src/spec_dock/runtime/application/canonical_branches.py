"""Canonical-mode `branch show/create/switch` (iss-00431).

The default name is `<ID>-<slug>` with the slug from the GitHub body marker. Create and switch keep today's
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
from spec_dock.runtime.application.canonical_scopes import load_canonical_scopes
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.start_lock import StartLock, StartLockBusy
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, EffectStatus, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


def branch_operation(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    scopes = load_canonical_scopes(context, timeout=namespace.timeout, link=False, offline=namespace.offline)
    source_selection = _capture_selection(context) if namespace.command_path != "branch show" else None
    selection = read_selection(context, scopes.views, stored=source_selection)
    target = resolve_scope(context, scopes.views, namespace.target, selection=selection)
    check_scope_expectations(
        context,
        scopes.views,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    name = getattr(namespace, "name", None) or f"{target.id}-{scopes.node(target.id).slug}"
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
        assert source_selection is not None
        _fresh_context(context, namespace.timeout)
        _verify_selection(context, source_selection)
        try:
            run_git(context.root, "branch", name, base, timeout=namespace.timeout, mutation=True)
        except GitProcessError as error:
            created = _branch_tip(context, name, namespace.timeout)
            status: EffectStatus = "succeeded" if created == base else "unknown" if error.uncertain else "failed"
            return _incomplete(namespace, target.id, name, created, "git.branch.create", status, error, switched=False)
        created_tip = _branch_tip(context, name, namespace.timeout)
        if created_tip != base:
            raise ValueError("created branch differs from the fixed base commit")
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
        assert source_selection is not None
        return _switch(namespace, context, target.id, name, tip, source_selection, warnings)
    return OperationResult(
        namespace.command_path,
        "succeeded",
        _data(target.id, name, tip, created=False, switched=False),
        0,
        warnings=warnings,
    )


def refuse_specs_at(context: ProjectContext, commit: str, *, timeout: float) -> None:
    """Stop before writing when the commit's tree tracks spec-dock/initiatives (a pre-migration commit)."""
    listed = run_git(
        context.root, "ls-tree", "--name-only", commit, "--", LINK_RELATIVE.as_posix(), timeout=timeout
    )
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
    source_selection: object,
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
        _verify_selection(context, source_selection)  # type: ignore[arg-type]
        if current.branch == name and current.head == tip:
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
            after = _fresh_context(context, namespace.timeout)
            moved = after.branch == name and after.head == tip
            status: EffectStatus = "succeeded" if moved else "unknown" if error.uncertain else "failed"
            return _incomplete(namespace, scope_id, name, tip, "git.checkout", status, error, switched=moved)
        after = _fresh_context(context, namespace.timeout)
        if after.branch != name or after.head != tip:
            raise ValueError("checkout differs from the fixed branch snapshot")
        _verify_selection(after, source_selection)  # type: ignore[arg-type]
    return OperationResult(
        namespace.command_path,
        "succeeded",
        _data(scope_id, name, tip, created=False, switched=True),
        0,
        effects=(Effect("git.checkout", "succeeded", name),),
        warnings=warnings,
    )


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
    error: GitProcessError,
    *,
    switched: bool,
) -> OperationResult[object]:
    partial = status != "failed"
    return OperationResult(
        namespace.command_path,
        "partial" if partial else "failed",
        _data(scope_id, name, tip, created=effect == "git.branch.create" and tip is not None, switched=switched),
        6 if partial else 5,
        effects=(Effect(effect, status, name),),
        error=Diagnostic("GIT_FAILED", str(error), error.details()),
    )
