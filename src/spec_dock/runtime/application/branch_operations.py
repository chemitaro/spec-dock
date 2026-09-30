"""Observe and change Git branches without persistent Scope bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import physical_identity, resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import (
    capture_local_inputs,
    read_candidate,
    verify_candidate,
    verify_local_inputs,
)
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.git_ref import parse_commit_oid
from spec_dock.runtime.infra.git_cli import worktree_list
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.infra.json_store import read_guarded_json
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, EffectStatus, OperationResult, ResultStatus

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.project_context import ProjectContext


@dataclass(frozen=True)
class BranchData:
    result: dict[str, object]
    kind: str = "branch"


def branch_operation(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[BranchData]:
    views = load_scope_views(context.root / "spec-dock")
    target = resolve_scope(context, views, namespace.target)
    if namespace.command_path != "branch show":
        if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
            raise ValueError("target backend does not match --expect-backend")
        if namespace.expect_current is not None:
            expected = resolve_scope(context, views, namespace.expect_current).id
            current = read_selection(context, views)
            if current.record is None or current.record.scope_id != expected:
                raise ValueError("direct target does not match --expect-current")
    loaded = read_guarded_json(target.path / ".meta.json")
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("Scope metadata disappeared")
    slug = loaded[0].get("slug")
    if not isinstance(slug, str) or not slug:
        raise ValueError("Scope slug is missing")
    name = getattr(namespace, "name", None) or f"{target.id}-{slug}"
    if not name.isascii():
        raise ValueError("branch name must be ASCII")
    checked = run_git(context.root, "check-ref-format", "--branch", name, timeout=namespace.timeout)
    if checked != (name + "\n").encode("ascii"):
        raise ValueError("branch must name a literal ref, not checkout shorthand")
    observed = run_git(
        context.root,
        "rev-parse",
        "--verify",
        "--quiet",
        f"refs/heads/{name}",
        timeout=namespace.timeout,
        missing_ok=True,
    )
    tip = parse_commit_oid(observed) if observed else None
    created = False
    switched = False
    status: ResultStatus = "succeeded"
    effects: tuple[Effect, ...] = ()
    if namespace.command_path == "branch create":
        context.require_writer()
        if tip is not None:
            raise ValueError("branch already exists; existing refs are never reset")
        tip = parse_commit_oid(
            run_git(
                context.root,
                "rev-parse",
                "--verify",
                "--end-of-options",
                f"{namespace.base}^{{commit}}",
                timeout=namespace.timeout,
            )
        )
        read_candidate(context, tip, target, views, timeout=namespace.timeout, proposed_token=None)
        if namespace.dry_run:
            status = "planned"
            effects = (Effect("git.branch.create", "planned", name),)
        else:
            _fresh_context(context, namespace.timeout)
            try:
                run_git(context.root, "branch", name, tip, timeout=namespace.timeout, mutation=True)
                created = True
                effects = (Effect("git.branch.create", "succeeded", name),)
                _fresh_context(context, namespace.timeout)
                expected_tip = tip
                tip = parse_commit_oid(
                    run_git(
                        context.root,
                        "rev-parse",
                        "--verify",
                        "--quiet",
                        f"refs/heads/{name}",
                        timeout=namespace.timeout,
                    )
                )
                if tip != expected_tip:
                    raise ValueError("created branch differs from the fixed base commit")
            except (OSError, ValueError, RuntimeError) as error:
                if effects:
                    return OperationResult(
                        namespace.command_path,
                        "partial",
                        _data(target.id, name, tip, created=created, switched=False),
                        6,
                        effects=effects,
                        error=Diagnostic(
                            "GIT_FAILED" if isinstance(error, GitProcessError) else "BRANCH_VERIFICATION_FAILED",
                            str(error),
                            error.details() if isinstance(error, GitProcessError) else {},
                        ),
                    )
                assert isinstance(error, GitProcessError)
                create_effect: EffectStatus = "unknown"
                try:
                    after = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
                    if (
                        after.clone_identity != context.clone_identity
                        or after.worktree_identity != context.worktree_identity
                    ):
                        raise ValueError("Git project identity changed")
                    ref = run_git(
                        context.root,
                        "rev-parse",
                        "--verify",
                        "--quiet",
                        f"refs/heads/{name}",
                        timeout=namespace.timeout,
                        missing_ok=True,
                    )
                    if ref:
                        actual_tip = parse_commit_oid(ref)
                        created = True
                        if actual_tip == tip:
                            create_effect = "succeeded"
                        tip = actual_tip
                    elif not error.uncertain:
                        create_effect = "failed"
                except (OSError, ValueError, RuntimeError):
                    pass
                partial = create_effect != "failed"
                return OperationResult(
                    namespace.command_path,
                    "partial" if partial else "failed",
                    _data(target.id, name, tip, created=created, switched=False),
                    6 if partial else 5,
                    effects=(Effect("git.branch.create", create_effect, name),),
                    error=Diagnostic("GIT_FAILED", str(error), error.details()),
                )
    elif namespace.command_path == "branch switch":
        context.require_writer()
        if tip is None:
            raise LookupError("requested branch ref is missing")
        candidate = read_candidate(context, tip, target, views, timeout=namespace.timeout, proposed_token=None)
        for entry in worktree_list(context.root, timeout=namespace.timeout):
            if entry.branch == name and physical_identity(entry.path) != context.worktree_identity:
                raise ValueError("requested branch is checked out in another worktree")
        if run_git(context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
            raise ValueError("branch switch requires a clean worktree")
        source_inputs = capture_local_inputs(context, views)
        if namespace.dry_run:
            status = "planned"
            effects = (Effect("git.checkout", "planned", name),)
        else:
            current_context = _fresh_context(context, namespace.timeout)
            verify_local_inputs(context, source_inputs)
            if current_context.branch == name and current_context.head == tip:
                verify_candidate(current_context, candidate)
                if run_git(current_context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                    raise ValueError("branch switch requires a clean worktree")
                return OperationResult(
                    namespace.command_path,
                    "unchanged",
                    _data(target.id, name, tip, created=False, switched=False),
                    0,
                    effects=(Effect("git.checkout", "unchanged", name),),
                )
            try:
                run_git(context.root, "checkout", name, timeout=namespace.timeout, mutation=True)
                effects = (Effect("git.checkout", "succeeded", name),)
                after = _fresh_context(context, namespace.timeout)
                if after.branch != name or after.head != tip:
                    raise ValueError("checkout differs from the fixed branch snapshot")
                verify_candidate(after, candidate)
                if run_git(after.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                    raise ValueError("checkout left a dirty worktree")
                switched = True
            except (OSError, ValueError, RuntimeError) as error:
                if isinstance(error, GitProcessError) and not effects:
                    effect_status: EffectStatus = "unknown"
                    try:
                        after = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
                        if (
                            after.clone_identity != context.clone_identity
                            or after.worktree_identity != context.worktree_identity
                        ):
                            raise ValueError("Git project identity changed")
                        if after.branch == name and after.head == tip:
                            verify_candidate(after, candidate)
                            if not run_git(context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                                switched = True
                                effect_status = "succeeded"
                        elif after.branch == context.branch and after.head == context.head and not error.uncertain:
                            verify_local_inputs(after, source_inputs)
                            if not run_git(context.root, "status", "--porcelain", "-z", timeout=namespace.timeout):
                                effect_status = "failed"
                    except (OSError, ValueError, RuntimeError):
                        pass
                    effects = (Effect("git.checkout", effect_status, name),)
                partial = any(effect.status in ("succeeded", "unknown") for effect in effects)
                return OperationResult(
                    namespace.command_path,
                    "partial" if partial else "failed",
                    _data(target.id, name, tip, created=False, switched=switched),
                    6 if partial else 5,
                    effects=effects,
                    error=Diagnostic(
                        "GIT_FAILED" if isinstance(error, GitProcessError) else "CHECKOUT_VERIFICATION_FAILED",
                        str(error),
                        error.details() if isinstance(error, GitProcessError) else {},
                    ),
                )
    data = _data(target.id, name, tip, created=created, switched=switched)
    if namespace.dry_run:
        data = BranchData({**data.result, "can_apply": True, "blockers": ()})
    return OperationResult(
        namespace.command_path,
        status,
        data,
        0,
        effects=effects,
    )


def _data(scope_id: str, name: str, tip: str | None, *, created: bool, switched: bool) -> BranchData:
    return BranchData({
        "scope_id": scope_id,
        "name": name,
        "tip": tip,
        "created": created,
        "switched": switched,
        "binding_persisted": False,
    })


def _fresh_context(context: ProjectContext, timeout: float) -> ProjectContext:
    fresh = resolve_context(str(context.root), context.root, timeout=timeout)
    if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
        raise ValueError("Git project physical identity changed")
    return fresh
