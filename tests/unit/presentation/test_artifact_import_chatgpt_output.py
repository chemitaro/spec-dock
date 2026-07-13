import json
from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.contracts import ArtifactImportError, ArtifactImportResult
        from spec_dock_runtime.presentation.cli_text import (
            render_artifact_import_error_json,
            render_artifact_import_error_text,
            render_artifact_import_json,
            render_artifact_import_text,
        )
    finally:
        sys.path.pop(0)
    return (
        ArtifactImportError,
        ArtifactImportResult,
        render_artifact_import_error_json,
        render_artifact_import_error_text,
        render_artifact_import_json,
        render_artifact_import_text,
    )


def test_artifact_import_success_renderers_expose_only_content_free_relative_fields() -> None:
    (
        _ArtifactImportError,
        ArtifactImportResult,
        _render_error_json,
        _render_error_text,
        render_json,
        render_text,
    ) = _runtime_modules()
    secret = "sk-secret-body-value"
    absolute = "/private/tmp/private-repo"
    result = ArtifactImportResult(
        import_kind="chatgpt-output",
        storage_identity="blank",
        artifact_id="20260714t010203z",
        scope_id="iss-00317",
        source_path=Path("spec-dock/.workbench/raw.md"),
        destination_path=Path(
            "spec-dock/initiatives/init-local-00003/epics/epic-00312/issues/iss-00317/artifacts/"
            "20260714t010203z-blank-chatgpt-output-raw-report.md"
        ),
        sha256="a" * 64,
        byte_count=27,
        committed=True,
        cleanup_state="removed",
        warning_codes=(),
    )

    text = render_text(result)
    json_text = render_json(result)
    combined = "\n".join([*text.stdout_lines, *text.stderr_lines, *text.warnings, *json_text.stdout_lines])
    assert "import_kind=chatgpt-output" in combined
    assert "storage_identity=blank" in combined
    assert "committed=true" in combined
    assert secret not in combined
    assert absolute not in combined
    for claim in ("canonical", "adopted", "reviewed"):
        assert claim not in combined.lower()

    payload = json.loads(json_text.stdout_lines[0])
    assert set(payload) == {
        "status",
        "import_kind",
        "storage_identity",
        "artifact_id",
        "scope_id",
        "source",
        "destination",
        "sha256",
        "byte_count",
        "committed",
        "cleanup_state",
        "warning_codes",
    }


def test_artifact_import_failure_renderers_hide_raw_exception_and_paths() -> None:
    (
        ArtifactImportError,
        _ArtifactImportResult,
        render_error_json,
        render_error_text,
        _render_json,
        _render_text,
    ) = _runtime_modules()
    error = ArtifactImportError(code="source_ineligible", cleanup_state="not_created")

    text = render_error_text(error)
    json_text = render_error_json(error)
    combined = "\n".join([*text.stdout_lines, *text.stderr_lines, *json_text.stdout_lines])
    assert "code=source_ineligible" in combined
    assert "committed=false" in combined
    assert "/private/" not in combined
    assert "OSError" not in combined
    assert "Traceback" not in combined
    payload = json.loads(json_text.stdout_lines[0])
    assert payload == {
        "status": "error",
        "import_kind": "chatgpt-output",
        "storage_identity": "blank",
        "code": "source_ineligible",
        "committed": False,
        "cleanup_state": "not_created",
    }
