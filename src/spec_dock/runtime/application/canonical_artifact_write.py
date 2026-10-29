"""Canonical-mode `artifact create` and `artifact import file` (iss-00432; Epic design ch. 4 and 6).

A Scope Artifact is published once into `<catalog>/<bucket>/<ID>/artifacts/` under the catalog lock and recorded
in one changeset; the naming, template and source rules are the legacy ones (`direct_artifact.mutate_artifact`,
copied here so the legacy module stays unchanged). The structure is read at display freshness: nothing is
written to GitHub. `@root` Artifacts stay in this checkout's `spec-dock/artifacts/`, as in legacy mode.
"""

from __future__ import annotations

from datetime import datetime, timezone
import errno
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_catalog import catalog_changes, require_writable_format
from spec_dock.runtime.application.canonical_scope_read import catalog_artifacts, replace_namespace
from spec_dock.runtime.application.canonical_scopes import (
    check_canonical_scope_expectations,
    load_canonical_scopes,
    resolve_canonical_scope,
)
from spec_dock.runtime.application.canonical_writes import CATALOG_LOCK_TIMEOUT, LOCAL_FAILURES
from spec_dock.runtime.application.direct_artifact import _view, mutate_artifact
from spec_dock.runtime.application.worktree_observation import read_selection
from spec_dock.runtime.domain.artifacts import (
    allocate_artifact_filename_for_timestamp,
    allocate_generic_imported_artifact_filename_for_timestamp,
    is_ambiguous_blank_artifact_slug,
    scan_artifact_slot_ledger,
)
from spec_dock.runtime.domain.canonical_layout import LINK_RELATIVE
from spec_dock.runtime.domain.ids import slugify, validate_input_slug_kebab
from spec_dock.runtime.infra import clock
from spec_dock.runtime.infra.file_publication import FilePublicationIncomplete, publish_file, read_regular_file
from spec_dock.runtime.infra.json_store import open_guarded_directory
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, Effect, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.application.canonical_scopes import CanonicalScopes
    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.scope_query import ScopeView
    from spec_dock.runtime.infra.file_publication import FileSnapshot


def create_artifact(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    context.require_writer()
    if namespace.scope == "@root" and namespace.expect_current is None:
        return mutate_artifact(namespace, context, Path.cwd())
    scopes = load_canonical_scopes(
        context, timeout=namespace.timeout, link=namespace.scope != "@root", offline=namespace.offline
    )
    selection = read_selection(context, scopes.views)
    target = (
        None
        if namespace.scope == "@root"
        else resolve_canonical_scope(context, scopes, namespace.scope, selection=selection)
    )
    check_canonical_scope_expectations(
        context,
        scopes,
        selection,
        target=target,
        expected_current=namespace.expect_current,
        expected_backend=namespace.expect_backend,
    )
    if target is None:  # checked here; the legacy @root publication cannot read canonical Scopes
        return mutate_artifact(replace_namespace(namespace, expect_current=None), context, Path.cwd())
    scopes.require_kind_unchanged(target.id)
    return _publish_scope_artifact(namespace, context, scopes, target)


def _publish_scope_artifact(
    namespace: argparse.Namespace, context: ProjectContext, scopes: CanonicalScopes, target: ScopeView
) -> OperationResult[object]:
    assert scopes.catalog is not None
    catalog = scopes.catalog.catalog
    require_writable_format(catalog)
    scopes.require_directory(target.id)
    directory = scopes.directories[target.id]
    owner = directory.path  # the real catalog path, never through the spec-dock/initiatives link
    shown = (LINK_RELATIVE / directory.relative).as_posix()
    artifacts = owner / "artifacts"
    imported = namespace.command_path == "artifact import file"
    date = datetime.fromisoformat(clock.now_iso().replace("Z", "+00:00"))
    date = date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc)
    timestamp = date.strftime("%Y%m%dt%H%M%Sz")
    source_path: Path | None = None
    source: FileSnapshot | None = None
    template_path: Path | None = None
    template: FileSnapshot | None = None
    if imported:
        source_path = _source_path(namespace.path)
        source = _source_snapshot(source_path)
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
        for key, value in _replacements(scopes, target, artifact_id, title, date).items():
            text = text.replace(key, value)
        payload, mode = text.encode("utf-8"), 0o666
    initial_problem, initial_ledger = scan_artifact_slot_ledger(artifacts)
    if initial_problem is not None:
        raise ValueError(initial_problem)
    relative = path.relative_to(catalog)
    shown_path = f"{shown}/artifacts/{path.name}"
    artifact: dict[str, object] = {
        "id": artifact_id,
        "scope_id": target.id,
        "path": shown_path,
        "type": artifact_type if artifact_type != "blank" else "untyped-markdown",
    }

    def verify() -> None:
        if source_path is not None and _source_snapshot(source_path) != source:
            raise ValueError("Artifact source changed")
        if template_path is not None and read_regular_file(template_path) != template:
            raise ValueError("Artifact template changed")
        problem, ledger = scan_artifact_slot_ledger(artifacts)
        if problem is not None or ledger != initial_ledger:
            raise ValueError("Artifact catalog changed before publication")

    verify()
    if namespace.dry_run:
        return OperationResult(
            namespace.command_path,
            "planned",
            FamilyData("artifact", {"artifact": artifact, "changed": False, "can_apply": True, "blockers": ()}),
            0,
            effects=(Effect("artifact", "planned", shown_path),),
            warnings=scopes.warnings(),
        )
    published = attempted = False
    try:
        with catalog_changes(
            catalog, command=namespace.command_path, origin="command", timeout=CATALOG_LOCK_TIMEOUT
        ) as changes:
            parent = open_guarded_directory(owner)
            try:
                os.mkdir("artifacts", dir_fd=parent)
                os.fsync(parent)
            except FileExistsError:
                pass
            finally:
                os.close(parent)
            slot = re.match(r"[0-9]{8}t[0-9]{6}z(?:-[0-9]{2})?", path.name)
            assert slot is not None
            attempted = True
            try:
                publish_file(path, payload, stage_name=f".publish-{slot[0]}.tmp", verify=verify, mode=mode)
            except FilePublicationIncomplete as error:
                if error.confirmed:
                    changes.add(relative)
                raise
            published = True
            changes.add(relative)
    except LOCAL_FAILURES as error:
        if isinstance(error, FilePublicationIncomplete):
            published = error.confirmed
        uncertain = isinstance(error, FilePublicationIncomplete) and not published
        partial = published or uncertain
        status = "succeeded" if published else "unknown" if uncertain else "failed" if attempted else "not_attempted"
        return OperationResult(
            namespace.command_path,
            "partial" if partial else "failed",
            FamilyData("artifact", {"artifact": artifact if published else None, "changed": published}),
            6 if partial else getattr(error, "exit_code", 3 if isinstance(error, ValueError) else 5),
            effects=(Effect("artifact", status, shown_path),) if attempted else (),
            warnings=scopes.warnings(),
            error=Diagnostic(
                "ARTIFACT_PUBLICATION_INCOMPLETE" if partial else getattr(error, "code", "LOCAL_IO_FAILED"),
                str(error),
                dict(getattr(error, "details", {}) or {}),
            ),
            recovery=RecoveryInstructions(("Inspect the candidate and owner files before a new explicit operation.",))
            if partial
            else None,
        )
    entries = [item for item in catalog_artifacts(owner, shown, target.id) if item.artifact_id == artifact_id]
    view = _view(entries[0]) if len(entries) == 1 else artifact
    return OperationResult(
        namespace.command_path,
        "succeeded",
        FamilyData("artifact", {"artifact": view, "changed": True, "snapshot": scopes.snapshot_payload()}),
        0,
        effects=(Effect("artifact", "succeeded", shown_path),),
        warnings=scopes.warnings(),
    )


def _source_path(value: str) -> Path:
    path = Path(value).expanduser()
    return Path(os.path.normpath(path if path.is_absolute() else Path.cwd() / path))


def _source_snapshot(path: Path) -> FileSnapshot:
    try:
        return read_regular_file(path)
    except FileNotFoundError as error:
        raise FileNotFoundError("Artifact source was not found") from error
    except ValueError as error:
        raise ValueError("Artifact source is unavailable or is not a single-link regular file") from error
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError("Artifact source is unavailable or is not a single-link regular file") from error
        raise OSError(error.errno, "Artifact source is unavailable due to an I/O failure") from error


def _replacements(
    scopes: CanonicalScopes, target: ScopeView, artifact_id: str, title: str, date: datetime
) -> dict[str, str]:
    """The legacy template placeholders, filled from the GitHub structure instead of `.meta.json`."""
    issue_ref = "#" + target.github_ref.rsplit("#", 1)[1] if target.github_ref is not None else ""
    replacements = {
        "<SCOPE_ID>": target.id,
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": date.date().isoformat(),
        "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
    }
    prefix = {"initiative": "INIT", "epic": "EPIC", "issue": "ISS"}[target.kind]
    replacements[f"<{prefix}_ID>"] = target.id
    replacements[f"<{prefix}_TITLE>"] = target.title
    if target.kind == "epic":
        replacements["<INIT_ID>"] = target.parent_id or ""
    elif target.kind == "issue":
        parent = scopes.view(target.parent_id) if target.parent_id is not None else None
        replacements.update({
            "<EPIC_ID>": parent.id if parent is not None else "",
            "<INIT_ID>": (parent.parent_id or "") if parent is not None else "",
            "<FEATURE_ID>": target.id,
            "<FEATURE_NAME>": target.title,
            "<ISSUE_NUMBER_OR_URL>": issue_ref,
        })
    for kind in ("ARTIFACT", "ADR", "DISC", "RESEARCH", "INTERVIEW", "DECISION_CANDIDATE", "PR_REPAIR_BATCH"):
        replacements[f"<{kind}_ID>"] = artifact_id
        replacements[f"<{kind}_TITLE>"] = title
    return replacements
