import json
from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.contracts import WorkbenchCopyError
        from spec_dock_runtime.presentation.cli_text import (
            render_workbench_copy_error_json,
            render_workbench_copy_error_text,
        )
    finally:
        sys.path.pop(0)
    return WorkbenchCopyError, render_workbench_copy_error_json, render_workbench_copy_error_text


def test_workbench_copy_failure_output_is_content_free_and_noncanonical() -> None:
    error_type, render_json, render_text = _runtime_modules()
    secret = "raw OSError secret body"
    error = error_type(
        code="copy_failed",
        message=secret,
        mutation_started=True,
    )

    text_output = render_text(error)
    json_output = render_json(error)
    combined_text = "\n".join((*text_output.stdout_lines, *text_output.stderr_lines))
    raw_json = "\n".join(json_output.stdout_lines)
    payload = json.loads(raw_json)

    assert secret not in combined_text
    assert secret not in raw_json
    assert "copy_failed" in combined_text
    assert "mutation_started=true" in combined_text
    assert "canonical" not in combined_text
    assert "rollback" not in combined_text
    assert payload == {
        "status": "error",
        "command": "copy",
        "code": "copy_failed",
        "side": None,
        "mutation_started": True,
        "experimental": True,
        "canonical": False,
        "one_shot": True,
        "sync": False,
    }
