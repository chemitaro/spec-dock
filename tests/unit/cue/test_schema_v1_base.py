"""The common fields of the specdock/v1 type: schema, kind, assurance (iss-00472 RQ-03, RQ-04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import document, evaluate, write_scope

if TYPE_CHECKING:
    from pathlib import Path

ASSURANCE = {"level": "standard", "reason": "通常の変更"}


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_a_scope_with_only_the_required_fields_evaluates_with_the_kind_from_the_tag(tmp_path: Path, kind: str) -> None:
    scope = write_scope(tmp_path, document(schema="specdock/v1", assurance=ASSURANCE))
    result = evaluate(scope, kind)
    assert result.ok, result.stderr
    assert result.data is not None
    assert result.data["schema"] == "specdock/v1"
    assert result.data["kind"] == kind
    assert result.data["assurance"] == ASSURANCE
