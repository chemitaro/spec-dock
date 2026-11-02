"""Pure rules for Scope titles written in canonical mode (the copy-time rewrites were removed in 0.5.0)."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("title", ["Leaf", "  日本語の題名  ", "x" * 256, "Emoji 🚀 ok"])
def test_a_canonical_title_is_any_language_up_to_256_characters(title: str) -> None:
    from spec_dock.runtime.domain.canonical_scaffold import validate_canonical_title

    assert validate_canonical_title(title, field="--title") == title.strip()


@pytest.mark.parametrize(
    ("title", "reason"),
    [("", "empty"), ("   ", "empty"), ("a\nb", "control"), ("a\tb", "control"), ("x" * 257, "256")],
)
def test_a_canonical_title_rejects_empty_control_and_long_values(title: str, reason: str) -> None:
    from spec_dock.runtime.domain.canonical_scaffold import validate_canonical_title

    with pytest.raises(ValueError, match=reason):
        validate_canonical_title(title, field="--title")
