"""The Python check and the CUE type `#Todo` agree on the same fixtures, file by file (iss-00549 D-08, R-02).

`cue` is required: like the Scope type tests, this fails instead of skipping without it.
"""

from __future__ import annotations

import json
from pathlib import Path

from spec_dock.runtime.application.todo_check import cue_failures
from spec_dock.runtime.domain.todo_record import validate
from spec_dock.runtime.infra.cue_schemas import shipped_schemas, todo_schema_path
from spec_dock.runtime.infra.cue_tool import locate_cue
from tests.support.cue import cue_executable

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures/todo"


def _fixtures() -> dict[str, dict[str, object]]:
    found = {
        f"{group}/{path.name}": json.loads(path.read_text(encoding="utf-8"))
        for group in ("valid", "invalid")
        for path in sorted((FIXTURES / group).glob("*.json"))
    }
    assert len(found) >= 30
    return found


def test_python_and_cue_reject_exactly_the_invalid_fixtures(tmp_path: Path) -> None:
    cue_executable()
    documents = _fixtures()
    python_failures = {name for name, record in documents.items() if validate(record)}
    failures, unmatched = cue_failures(locate_cue(timeout=30), documents, cwd=tmp_path, timeout=60)
    assert unmatched == ()
    assert set(failures) == python_failures
    assert python_failures == {name for name in documents if name.startswith("invalid/")}
    for name in failures:
        assert failures[name], name  # each failure carries at least one message


def test_the_todo_type_is_not_a_scope_schema() -> None:
    assert todo_schema_path().is_file()
    assert shipped_schemas() == ("specdock/v1",)
