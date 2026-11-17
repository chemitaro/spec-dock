"""The runtime gives no directory or repository name a meaning of its own (iss-00635 T-05)."""

from __future__ import annotations

from pathlib import Path

import pytest

RUNTIME = Path(__file__).resolve().parents[3] / "src/spec_dock/runtime"


@pytest.mark.parametrize("word", ["TIER_LABELS", "事業", "プロダクト", "サービス", "businesses", "products"])
def test_the_runtime_has_no_name_mapping(word: str) -> None:
    hits = [str(path.relative_to(RUNTIME)) for path in sorted(RUNTIME.rglob("*.py")) if word in path.read_text("utf-8")]
    assert hits == [], hits
