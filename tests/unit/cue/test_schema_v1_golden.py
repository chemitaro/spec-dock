"""specdock/v1 keeps giving the same result for the Scopes written against it (iss-00472 AC-07, K6).

Each sample under tests/fixtures/cue/v1/samples/<name>/ holds the three Scope files and expected.json:
the kind, and either the complete exported JSON or the field paths a shape error must name. A change to
v1 that alters any of these breaks compatibility; after release such a change belongs in cue/v2/.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.cue import evaluate

SAMPLES = Path(__file__).resolve().parents[2] / "fixtures/cue/v1/samples"


def _samples() -> list[Path]:
    return sorted(path for path in SAMPLES.iterdir() if path.is_dir())


def test_the_samples_cover_every_kind_and_level() -> None:
    expected = [json.loads((path / "expected.json").read_text(encoding="utf-8")) for path in _samples()]
    assert {item["kind"] for item in expected} == {"initiative", "epic", "issue"}
    assert {item["level"] for item in expected} == {"light", "standard", "strict", "critical"}
    assert any("export" in item for item in expected) and any("error_paths" in item for item in expected)


@pytest.mark.parametrize("sample", _samples(), ids=lambda path: path.name)
def test_a_v1_sample_evaluates_exactly_as_recorded(sample: Path) -> None:
    expected = json.loads((sample / "expected.json").read_text(encoding="utf-8"))
    result = evaluate(sample, expected["kind"])
    if "export" in expected:
        assert result.ok, result.stderr
        assert result.data == expected["export"]
        assert expected["export"]["assurance"]["level"] == expected["level"]
    else:
        assert not result.ok
        for path in expected["error_paths"]:
            assert path in result.stderr, result.stderr
        assert "cycle" not in result.stderr
