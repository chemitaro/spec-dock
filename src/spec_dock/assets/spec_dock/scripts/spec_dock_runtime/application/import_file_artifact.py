from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import (
    BinaryArtifactPublishError,
    ExplicitFileArtifactPublishRequest,
    ExplicitFileSourcePreflightRequest,
    FileArtifactImportError,
    FileArtifactImportRequest,
    FileArtifactImportResult,
)
from spec_dock_runtime.application.create_artifact_doc import (
    ArtifactSetupTarget,
    _ensure_artifacts_setup_for_target,
    _format_artifact_timestamp,
)
from spec_dock_runtime.application.create_node import (
    _acquire_create_lock,
    _prefix_for_kind,
    _release_create_lock,
    _resolve_specdock_dir,
    load_graph,
)
from spec_dock_runtime.domain.artifacts import format_generic_imported_artifact_filename
from spec_dock_runtime.domain.ids import resolve_id_input

if TYPE_CHECKING:
    from spec_dock_runtime.application.ports import Ports


@dataclass(frozen=True)
class _FileArtifactTarget:
    kind: str
    id: str
    path: Path
    artifacts_dir: Path
    rules_kind: str


def import_file_artifact(req: FileArtifactImportRequest, ports: Ports) -> FileArtifactImportResult:
    repo_root = _absolute_path(ports.repo_root)
    source_guard = ports.explicit_file_source_guard
    publisher = ports.explicit_file_artifact_publisher
    if repo_root is None or source_guard is None or publisher is None:
        raise FileArtifactImportError(code="runtime_not_configured", cleanup_state="not_created")
    specdock_dir = _resolve_specdock_dir(ports)
    target = _resolve_target(req, ports, specdock_dir)
    original_basename = req.source_path.name
    try:
        filename = format_generic_imported_artifact_filename(
            timestamp=_format_artifact_timestamp(ports.clock.now_iso() if ports.clock is not None else None),
            original_basename=original_basename,
        )
    except RuntimeError:
        raise FileArtifactImportError(code="source_ineligible", cleanup_state="not_created") from None

    try:
        guarded_source = source_guard.guard_explicit_file_source(
            ExplicitFileSourcePreflightRequest(
                repo_root=repo_root,
                source_path=req.source_path,
            )
        )
    except BinaryArtifactPublishError as error:
        raise FileArtifactImportError(code=error.code, cleanup_state=error.cleanup_state) from None
    except Exception:
        raise FileArtifactImportError(code="runtime_failed", cleanup_state="not_created") from None

    destination_path = target.artifacts_dir / filename
    try:
        destination = destination_path.relative_to(repo_root)
    except ValueError:
        guarded_source.close()
        raise FileArtifactImportError(code="result_path_invalid", cleanup_state="not_created") from None
    source_visibility = guarded_source.source_visibility
    source_display = guarded_source.source_display

    lock_path: Path | None = None
    lock_token: str | None = None
    result: FileArtifactImportResult | None = None
    body_error: FileArtifactImportError | None = None
    try:
        try:
            lock_path, lock_token = _acquire_create_lock(specdock_dir)
        except RuntimeError:
            raise FileArtifactImportError(code="create_lock_failed", cleanup_state="not_created") from None
        except OSError:
            raise FileArtifactImportError(code="runtime_failed", cleanup_state="not_created") from None
        try:
            _ensure_artifacts_setup_for_target(
                target=ArtifactSetupTarget(
                    path=target.path,
                    artifacts_dir=target.artifacts_dir,
                    rules_kind=target.rules_kind,
                ),
                specdock_dir=specdock_dir,
            )
        except RuntimeError:
            raise FileArtifactImportError(code="artifact_setup_failed", cleanup_state="not_created") from None
        except OSError:
            raise FileArtifactImportError(code="runtime_failed", cleanup_state="not_created") from None
        try:
            published = publisher.publish_explicit_file(
                ExplicitFileArtifactPublishRequest(
                    repo_root=repo_root,
                    guarded_source=guarded_source,
                    destination_path=destination_path,
                )
            )
        except BinaryArtifactPublishError as error:
            raise FileArtifactImportError(code=error.code, cleanup_state=error.cleanup_state) from None

        if published.destination_path != destination_path or not published.committed:
            raise RuntimeError("explicit publisher returned an invalid committed identity")
        publication_state = "committed_with_warning" if published.warning_codes else "committed"
        result = FileArtifactImportResult(
            import_kind="file",
            storage_identity="generic",
            target_kind=req.target_kind,
            target_id=target.id,
            artifact_id=filename,
            source_visibility=source_visibility,
            source=source_display,
            destination=destination,
            committed=True,
            publication_state=publication_state,
            cleanup_state=published.cleanup_state,
            warning_codes=published.warning_codes,
            retry_disposition="not_needed",
            canonical=False,
        )
    except FileArtifactImportError as error:
        body_error = error
    finally:
        guarded_source.close()
        if lock_path is not None and lock_token is not None:
            try:
                _release_create_lock(lock_path, lock_token, specdock_dir=specdock_dir)
            except Exception as release_error:
                if body_error is None and result is not None:
                    result = replace(
                        result,
                        publication_state="committed_with_warning",
                        warning_codes=(*result.warning_codes, "create_lock_release_failed"),
                    )
                elif body_error is None:
                    body_error = FileArtifactImportError(
                        code="create_lock_release_failed",
                        cleanup_state="not_created",
                    )
                else:
                    raise body_error from release_error
    if body_error is not None:
        raise body_error
    assert result is not None
    return result


def _resolve_target(
    req: FileArtifactImportRequest,
    ports: Ports,
    specdock_dir: Path,
) -> _FileArtifactTarget:
    if req.target_kind == "root":
        if req.target_value is not None:
            raise FileArtifactImportError(code="target_invalid", cleanup_state="not_created")
        if specdock_dir.is_symlink() or not specdock_dir.is_dir():
            raise FileArtifactImportError(code="target_invalid", cleanup_state="not_created")
        return _FileArtifactTarget(
            kind="root",
            id="root",
            path=specdock_dir,
            artifacts_dir=specdock_dir / "artifacts",
            rules_kind="root",
        )
    if req.target_kind not in ("initiative", "epic", "issue") or req.target_value is None:
        raise FileArtifactImportError(code="target_invalid", cleanup_state="not_created")
    graph = load_graph(ports, validate=False)
    try:
        target_id = resolve_id_input(
            req.target_value,
            prefix=_prefix_for_kind(req.target_kind),
            field=f"--{req.target_kind}",
            nodes=graph.nodes_by_id,
        )
    except RuntimeError:
        raise FileArtifactImportError(code="target_invalid", cleanup_state="not_created") from None
    node = graph.nodes_by_id.get(target_id)
    if node is None or node.kind != req.target_kind:
        raise FileArtifactImportError(code="target_invalid", cleanup_state="not_created")
    return _FileArtifactTarget(
        kind=node.kind,
        id=node.id,
        path=node.path,
        artifacts_dir=node.path / "artifacts",
        rules_kind=node.kind,
    )


def _absolute_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else Path.cwd() / path
