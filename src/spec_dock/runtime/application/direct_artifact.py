"""Artifact identities and publications from worktree-local owner files."""

from __future__ import annotations

from datetime import datetime, timezone
import errno
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING

from spec_dock.runtime.application.artifact_query import list_artifacts, show_artifact
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.scope_expectations import check_scope_expectations
from spec_dock.runtime.application.scope_query import load_scope_views
from spec_dock.runtime.application.start_snapshot import capture_local_inputs, verify_local_inputs
from spec_dock.runtime.application.worktree_observation import read_selection, resolve_scope
from spec_dock.runtime.domain.artifacts import (
    allocate_artifact_filename_for_timestamp,
    allocate_generic_imported_artifact_filename_for_timestamp,
    is_ambiguous_blank_artifact_slug,
    scan_artifact_slot_ledger,
)
from spec_dock.runtime.domain.ids import slugify, validate_input_slug_kebab
from spec_dock.runtime.infra import clock
from spec_dock.runtime.infra.file_publication import FilePublicationIncomplete, publish_file, read_regular_file
from spec_dock.runtime.infra.git_process import GitProcessError
from spec_dock.runtime.infra.json_store import open_guarded_directory, read_guarded_json_bytes
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.artifact_query import ArtifactCatalogEntry
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.start_snapshot import LocalInput


def _view(entry: ArtifactCatalogEntry) -> dict[str, object]:
    return {
        "id": entry.artifact_id,
        "scope_id": entry.scope_id,
        "path": entry.relative_path,
        "type": entry.creation_type or entry.observed_type,
    }


def _verify_captured(context: ProjectContext, inputs: tuple[LocalInput, ...], *, root_owner: bool) -> None:
    if not root_owner:
        verify_local_inputs(context, inputs)
        return
    for expected in inputs:
        observed = read_guarded_json_bytes(context.root / expected.relative_path)
        if observed is None or observed[1:] != (expected.payload, expected.identity):
            raise ValueError("Artifact workspace input changed")


def query_artifact(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    root_without_current = namespace.scope == "@root" and namespace.expect_current is None
    views = () if root_without_current else load_scope_views(context.root / "spec-dock")
    selection = None if root_without_current else read_selection(context, views)
    target = None if namespace.scope == "@root" else resolve_scope(context, views, namespace.scope, selection=selection)
    check_scope_expectations(
        context,
        views,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    inputs = capture_local_inputs(context, views)
    scope = target.id if target is not None else "@root"
    owner = target.path if target is not None else context.root / "spec-dock"
    descriptor = open_guarded_directory(owner)
    try:
        if namespace.command_path == "artifact list":
            catalog = list_artifacts(repo_root=context.root, scope=scope)
            data = FamilyData(
                "artifact-list", {"scope_id": catalog.scope_id, "items": tuple(map(_view, catalog.items))}
            )
        else:
            entry = show_artifact(repo_root=context.root, scope=scope, artifact_id=namespace.artifact_id)
            data = FamilyData("artifact", {"artifact": _view(entry), "changed": False})
        fresh = open_guarded_directory(owner)
        try:
            before, after = os.fstat(descriptor), os.fstat(fresh)
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                raise ValueError("Artifact owner identity changed")
        finally:
            os.close(fresh)
    finally:
        os.close(descriptor)
    _verify_captured(context, inputs, root_owner=scope == "@root")
    return OperationResult(namespace.command_path, "succeeded", data, 0)


def mutate_artifact(
    namespace: argparse.Namespace, context: ProjectContext, invocation_cwd: Path
) -> OperationResult[object]:
    context.require_writer()
    imported = namespace.command_path == "artifact import file"
    views = (
        ()
        if namespace.scope == "@root" and namespace.expect_current is None
        else load_scope_views(context.root / "spec-dock")
    )
    selection = (
        None if namespace.scope == "@root" and namespace.expect_current is None else read_selection(context, views)
    )
    target = None if namespace.scope == "@root" else resolve_scope(context, views, namespace.scope, selection=selection)
    owner = target.path if target is not None else context.root / "spec-dock"
    scope_id = target.id if target is not None else "root"
    if namespace.expect_backend is not None and (target is None or namespace.expect_backend != target.backend.kind):
        raise ValueError("owner backend does not match --expect-backend")
    if namespace.expect_current is not None:
        expected = resolve_scope(context, views, namespace.expect_current, selection=selection).id
        if (
            selection is None
            or selection.status != "selected"
            or selection.record is None
            or selection.record.scope_id != expected
        ):
            raise ValueError("direct target does not match --expect-current")
    artifacts = owner / "artifacts"
    date = datetime.fromisoformat(clock.now_iso().replace("Z", "+00:00"))
    date = date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc)
    timestamp = date.strftime("%Y%m%dt%H%M%Sz")
    if imported:
        source_path = Path(namespace.path).expanduser()
        source_path = Path(os.path.normpath(source_path if source_path.is_absolute() else invocation_cwd / source_path))

        def source_snapshot():
            try:
                return read_regular_file(source_path)
            except FileNotFoundError as error:
                raise FileNotFoundError("Artifact source was not found") from error
            except ValueError as error:
                raise ValueError("Artifact source is unavailable or is not a single-link regular file") from error
            except OSError as error:
                if error.errno in (errno.ELOOP, errno.ENOTDIR):
                    raise ValueError("Artifact source is unavailable or is not a single-link regular file") from error
                raise OSError(error.errno, "Artifact source is unavailable due to an I/O failure") from error

        source = source_snapshot()
        name_max = (
            os.pathconf(artifacts if artifacts.exists() else owner, "PC_NAME_MAX") if hasattr(os, "pathconf") else 255
        )
        path, artifact_id = allocate_generic_imported_artifact_filename_for_timestamp(
            artifacts, timestamp=timestamp, original_basename=source_path.name, name_max_bytes=name_max
        )
        payload, mode, artifact_type = source.payload, source.mode, "generic-file"
    else:
        title = namespace.title.strip()
        if not title:
            raise ValueError("Artifact title must not be empty")
        slug = validate_input_slug_kebab(
            namespace.slug.strip() if namespace.slug is not None else slugify(title), field="--slug"
        )
        artifact_type = namespace.type
        if artifact_type == "blank" and is_ambiguous_blank_artifact_slug(slug):
            raise ValueError("blank Artifact slug must not start with a supported type prefix")
        template_path = context.root / "spec-dock/templates/artifacts" / f"{artifact_type}.md"
        template = read_regular_file(template_path)
        text = template.payload.decode("utf-8")
        if not text.strip():
            raise ValueError("Artifact template must not be empty")
        path, artifact_id = allocate_artifact_filename_for_timestamp(
            artifacts, timestamp=timestamp, artifact_type=artifact_type, slug=slug
        )
        replacements = {
            "<SCOPE_ID>": scope_id,
            "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
            "YYYY-MM-DD": date.date().isoformat(),
        }
        issue_ref = (
            "#" + target.github_ref.rsplit("#", 1)[1] if target is not None and target.github_ref is not None else ""
        )
        replacements["<GITHUB_ISSUE_NUMBER_OR_URL>"] = issue_ref
        if target is not None:
            prefix = {"initiative": "INIT", "epic": "EPIC", "issue": "ISS"}[target.kind]
            replacements[f"<{prefix}_ID>"] = target.id
            replacements[f"<{prefix}_TITLE>"] = target.title
            if target.kind == "epic":
                assert target.parent_id is not None
                replacements["<INIT_ID>"] = target.parent_id
            elif target.kind == "issue":
                parent_scope = next(view for view in views if view.id == target.parent_id)
                assert parent_scope.parent_id is not None
                replacements.update({
                    "<EPIC_ID>": parent_scope.id,
                    "<INIT_ID>": parent_scope.parent_id,
                    "<FEATURE_ID>": target.id,
                    "<FEATURE_NAME>": target.title,
                    "<ISSUE_NUMBER_OR_URL>": issue_ref,
                })
        else:
            for field in (
                "INIT_ID",
                "INIT_TITLE",
                "EPIC_ID",
                "EPIC_TITLE",
                "ISS_ID",
                "ISS_TITLE",
                "FEATURE_ID",
                "FEATURE_NAME",
                "ISSUE_NUMBER_OR_URL",
            ):
                replacements[f"<{field}>"] = ""
        for prefix in ("ARTIFACT", "ADR", "DISC", "RESEARCH", "INTERVIEW", "DECISION_CANDIDATE", "PR_REPAIR_BATCH"):
            replacements[f"<{prefix}_ID>"] = artifact_id
            replacements[f"<{prefix}_TITLE>"] = title
        for key, value in replacements.items():
            text = text.replace(key, value)
        payload, mode = text.encode("utf-8"), 0o666
    inputs = capture_local_inputs(context, views)
    initial_problem, initial_ledger = scan_artifact_slot_ledger(artifacts)
    if initial_problem is not None:
        raise ValueError(initial_problem)
    relative_path = path.relative_to(context.root).as_posix()
    artifact: dict[str, object] = {
        "id": artifact_id,
        "scope_id": scope_id,
        "path": relative_path,
        "type": artifact_type if artifact_type != "blank" else "untyped-markdown",
    }

    def verify_inputs() -> None:
        fresh = resolve_context(str(context.root), context.root, timeout=namespace.timeout)
        if fresh.clone_identity != context.clone_identity or fresh.worktree_identity != context.worktree_identity:
            raise ValueError("Git project physical identity changed")
        fresh.require_writer()
        _verify_captured(fresh, inputs, root_owner=target is None)
        if imported and source_snapshot() != source:
            raise ValueError("Artifact source changed")
        if not imported and read_regular_file(template_path) != template:
            raise ValueError("Artifact template changed")

    def verify() -> None:
        verify_inputs()
        problem, ledger = scan_artifact_slot_ledger(artifacts)
        if problem is not None or ledger != initial_ledger:
            raise ValueError("Artifact catalog changed before publication")

    verify()
    effect = Effect("artifact", "planned", relative_path)
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("artifact", {"artifact": artifact, "changed": False, "can_apply": True, "blockers": ()}),
            0,
            effects=(effect,),
        )
    directory_attempted = created_directory = published = False
    try:
        parent = open_guarded_directory(owner)
        try:
            try:
                directory_attempted = True
                os.mkdir("artifacts", dir_fd=parent)
                created_directory = True
                os.fsync(parent)
            except FileExistsError:
                directory_attempted = False
        finally:
            os.close(parent)
        slot = re.match(r"[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?", path.name)
        assert slot is not None
        publish_file(path, payload, stage_name=f".publish-{slot[0]}.tmp", verify=verify, mode=mode)
        published = True
        verify_inputs()
        entry = show_artifact(
            repo_root=context.root, scope="@root" if target is None else scope_id, artifact_id=artifact_id
        )
        return OperationResult(
            namespace.command_path,
            "succeeded",
            FamilyData("artifact", {"artifact": _view(entry), "changed": True}),
            0,
            effects=(Effect("artifact", "succeeded", relative_path),),
        )
    except (ValueError, OSError, RuntimeError, LookupError) as error:
        if isinstance(error, FilePublicationIncomplete):
            published = error.confirmed
        uncertain = isinstance(error, FilePublicationIncomplete) and not published
        partial = published or uncertain or directory_attempted
        effects = (
            (
                Effect(
                    "artifact", "succeeded" if published else "unknown" if uncertain else "not_attempted", relative_path
                ),
            )
            if partial
            else ()
        )
        if directory_attempted and not published and not uncertain:
            effects = (
                Effect(
                    "artifact.directory",
                    "succeeded" if created_directory else "unknown",
                    artifacts.relative_to(context.root).as_posix(),
                ),
                *effects,
            )
        code = (
            "GIT_FAILED"
            if isinstance(error, GitProcessError)
            else "ARTIFACT_PUBLICATION_INCOMPLETE"
            if partial
            else "PRECONDITION_FAILED"
            if isinstance(error, ValueError)
            else "LOCAL_IO_FAILED"
        )
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData("artifact", {"artifact": artifact if published else None, "changed": published}),
            6 if partial else 3 if isinstance(error, ValueError) else 5,
            effects=effects,
            error=Diagnostic(code, str(error), error.details() if isinstance(error, GitProcessError) else {}),
            recovery=RecoveryInstructions(("Inspect the candidate and owner files before a new explicit operation.",))
            if partial
            else None,
        )
