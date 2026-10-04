"""Edit one local Scope title without GitHub state, control or shared exclusion."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import replace
import json
import secrets
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.commands.runtime_dispatch import scope_payload
from spec_dock.runtime.infra.direct_json import MetadataPublicationIncomplete, replace_existing_json
from spec_dock.runtime.infra.git_process import GitProcessError, run_git
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.direct_json import PublishedJson


def edit_scope(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    title = namespace.title.strip()
    if not title:
        raise ValueError("Scope title must not be empty")
    views = load_scope_views(context.root / "spec-dock")
    selection = read_selection(context, views)
    target = resolve_scope(context, views, namespace.target, selection=selection)
    if namespace.expect_backend is not None and target.backend.kind != namespace.expect_backend:
        raise ValueError("target backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if selection.status != "selected" or selection.record is None or selection.record.scope_id != expected:
            raise ValueError("direct target does not match --expect-current")
    inputs = capture_local_inputs(context, views)
    captured = next(
        item
        for item in inputs
        if item.relative_path == (target.path / ".meta.json").relative_to(context.root).as_posix()
    )
    payload = {**json.loads(captured.payload), "title": title, "revision": target.revision + 1}

    def verify_source() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        verify_local_inputs(fresh, inputs)

    def verify_stage(path: Path) -> None:
        verify_source()
        if not run_git(
            context.root,
            "check-ignore",
            "--no-index",
            "--",
            path.relative_to(context.root).as_posix(),
            missing_ok=True,
            timeout=namespace.timeout,
        ):
            raise ValueError("metadata staging path must be ignored by Git")

    if title == target.title:
        verify_source()
        data: dict[str, object] = {
            "scope": scope_payload(target, context),
            "github_ref": target.github_ref,
            "changed": False,
        }
        if namespace.dry_run:
            data.update(can_apply=True, blockers=())
        return OperationResult(
            namespace.command_path, "planned" if namespace.dry_run else "unchanged", FamilyData("scope", data), 0
        )
    updated = replace(target, title=title, revision=target.revision + 1)
    if namespace.dry_run:
        verify_stage(context.root / "spec-dock/.agent/staging" / f".stage-{secrets.token_hex(16)}")
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData(
                "scope",
                {
                    "scope": scope_payload(updated, context),
                    "github_ref": updated.github_ref,
                    "changed": False,
                    "can_apply": True,
                    "blockers": (),
                },
            ),
            0,
            effects=(Effect("metadata", "planned", target.id),),
        )
    published: PublishedJson | None = None
    try:
        published = replace_existing_json(
            target.path / ".meta.json",
            payload,
            expected_bytes=captured.payload,
            expected_identity=captured.identity,
            staging_dir=context.root / "spec-dock/.agent/staging",
            before_replace=verify_source,
            before_stage=verify_stage,
        )
        inputs = tuple(
            replace(item, payload=published.payload, identity=published.identity) if item == captured else item
            for item in inputs
        )
        verify_source()
    except (ValueError, OSError, RuntimeError) as error:
        if isinstance(error, MetadataPublicationIncomplete):
            published = error.published
        confirmed = published is not None
        uncertain = isinstance(error, MetadataPublicationIncomplete) and not confirmed
        observed_scope: dict[str, object] | None = None
        if published is not None:
            inputs = tuple(
                replace(item, payload=published.payload, identity=published.identity) if item == captured else item
                for item in inputs
            )
            with suppress(ValueError, OSError, RuntimeError):
                verify_source()
                observed_scope = scope_payload(updated, context)
        return OperationResult(
            namespace.command_path,
            "partial" if confirmed or uncertain else "failed",
            FamilyData(
                "scope",
                {
                    "scope": observed_scope,
                    "github_ref": target.github_ref,
                    "changed": confirmed,
                    "metadata_observation": "confirmed-publication" if confirmed else "before-operation",
                },
            ),
            6 if confirmed or uncertain else 5 if isinstance(error, (OSError, RuntimeError)) else 3,
            effects=(
                Effect(
                    "metadata",
                    "succeeded"
                    if confirmed
                    else "unknown"
                    if uncertain
                    else "not_attempted"
                    if isinstance(error, ValueError)
                    else "failed",
                    target.id,
                ),
            ),
            error=Diagnostic(
                "GIT_FAILED" if isinstance(error, GitProcessError) else "SCOPE_EDIT_INCOMPLETE",
                str(error),
                error.details() if isinstance(error, GitProcessError) else {},
            ),
            recovery=RecoveryInstructions((
                f"Inspect current metadata for {target.id} before a new explicit edit; no automatic rollback or resume.",
            )),
        )
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData(
            "scope", {"scope": scope_payload(updated, context), "github_ref": updated.github_ref, "changed": True}
        ),
        0,
        effects=(Effect("metadata", "succeeded", target.id),),
    )
