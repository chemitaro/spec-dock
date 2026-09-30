import json


def _runtime_modules():

    from spec_dock.runtime.application.contracts import WorkbenchCopyError
    from spec_dock.runtime.presentation.cli_text import (
        render_workbench_copy_error_json,
        render_workbench_copy_error_text,
    )

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
    assert "experimental=true" in combined_text
    assert "canonical=false" in combined_text
    assert "disposable=true" in combined_text
    assert "one_shot=true" in combined_text
    assert "sync=false" in combined_text
    assert "rollback" not in combined_text
    assert payload == {
        "status": "error",
        "command": "copy",
        "code": "copy_failed",
        "side": None,
        "mutation_started": True,
        "experimental": True,
        "canonical": False,
        "disposable": True,
        "one_shot": True,
        "sync": False,
    }
