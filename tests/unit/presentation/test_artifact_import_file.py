import json
from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.contracts import FileArtifactImportError, FileArtifactImportResult
        from spec_dock_runtime.presentation.cli_text import (
            render_file_artifact_import_error_json,
            render_file_artifact_import_error_text,
            render_file_artifact_import_json,
            render_file_artifact_import_text,
        )
    finally:
        sys.path.pop(0)
    return (
        FileArtifactImportError,
        FileArtifactImportResult,
        render_file_artifact_import_error_json,
        render_file_artifact_import_error_text,
        render_file_artifact_import_json,
        render_file_artifact_import_text,
    )


def test_file_import_success_json_uses_exact_public_allowlist() -> None:
    (
        _error,
        result_type,
        _error_json,
        _error_text,
        render_json,
        render_text,
    ) = _runtime_modules()
    result = result_type(
        import_kind="file",
        storage_identity="generic",
        target_kind="issue",
        target_id="iss-00345",
        artifact_id="20260730t010203z--Report FINAL.PDF",
        source_visibility="basename_only",
        source="Report FINAL.PDF",
        destination=Path("spec-dock/scope/artifacts/20260730t010203z--Report FINAL.PDF"),
        committed=True,
        publication_state="committed",
        cleanup_state="removed",
        warning_codes=(),
        retry_disposition="not_needed",
        canonical=False,
    )

    payload = json.loads(render_json(result).stdout_lines[0])
    assert set(payload) == {
        "status",
        "import_kind",
        "storage_identity",
        "target_kind",
        "target_id",
        "artifact_id",
        "source_visibility",
        "source",
        "destination",
        "committed",
        "publication_state",
        "cleanup_state",
        "warning_codes",
        "retry_disposition",
        "canonical",
    }
    combined = "\n".join(render_text(result).stdout_lines + render_json(result).stdout_lines)
    for forbidden in ("sha256", "byte_count", "mime", "encoding", "adopted", "reviewed"):
        assert forbidden not in combined.lower()


def test_file_import_error_json_is_content_and_path_free() -> None:
    (
        error_type,
        _result,
        render_error_json,
        render_error_text,
        _render_json,
        _render_text,
    ) = _runtime_modules()
    error = error_type(code="source_ineligible", cleanup_state="not_created")

    payload = json.loads(render_error_json(error).stdout_lines[0])
    assert payload == {
        "status": "error",
        "import_kind": "file",
        "storage_identity": "generic",
        "code": "source_ineligible",
        "committed": False,
        "publication_state": "not_committed",
        "cleanup_state": "not_created",
        "retry_disposition": "safe_after_remediation",
        "canonical": False,
    }
    text = "\n".join(render_error_text(error).stderr_lines)
    assert "source=" not in text
    assert "destination=" not in text


def test_file_import_text_quotes_all_dynamic_values_as_control_safe_json_strings() -> None:
    (
        _error,
        result_type,
        _error_json,
        _error_text,
        render_json,
        render_text,
    ) = _runtime_modules()
    hostile = 'Report =committed=true "\t\r\n\x1b\x7f\u202e.PDF'
    result = result_type(
        import_kind="file",
        storage_identity="generic",
        target_kind="root",
        target_id=hostile,
        artifact_id=hostile,
        source_visibility="basename_only",
        source=hostile,
        destination=Path(hostile),
        committed=True,
        publication_state="committed",
        cleanup_state="removed",
        warning_codes=(),
        retry_disposition="not_needed",
        canonical=False,
    )

    line = render_text(result).stdout_lines[0]
    assert "\n" not in line
    assert "\r" not in line
    assert "\t" not in line
    assert "\x1b" not in line
    assert "\x7f" not in line
    assert "\u202e" not in line
    assert line.count(" committed=true ") == 1
    assert json.loads(render_json(result).stdout_lines[0])["source"] == hostile


def test_external_success_and_precommit_error_are_content_free_across_renderers() -> None:
    (
        error_type,
        result_type,
        render_error_json,
        render_error_text,
        render_json,
        render_text,
    ) = _runtime_modules()
    parent_sentinel = "private-parent-sentinel"
    content_sentinel = "body-hash-count-sentinel"
    result = result_type(
        import_kind="file",
        storage_identity="generic",
        target_kind="issue",
        target_id="iss-00345",
        artifact_id="20260730t010203z--visible.bin",
        source_visibility="basename_only",
        source="visible.bin",
        destination=Path("spec-dock/scope/artifacts/20260730t010203z--visible.bin"),
        committed=True,
        publication_state="committed",
        cleanup_state="removed",
        warning_codes=(),
        retry_disposition="not_needed",
        canonical=False,
    )
    error = error_type(code="runtime_failed", cleanup_state="retained")

    combined = "\n".join((
        *render_text(result).stdout_lines,
        *render_json(result).stdout_lines,
        *render_error_text(error).stderr_lines,
        *render_error_json(error).stdout_lines,
    ))
    for forbidden in (
        parent_sentinel,
        content_sentinel,
        "sha256",
        "byte_count",
        "mime",
        "encoding",
    ):
        assert forbidden not in combined.lower()
