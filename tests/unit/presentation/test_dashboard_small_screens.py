"""Small screen fixes of the dashboard assets (iss-00572): the empty repository card and the narrow graph band."""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard"


def test_a_repository_without_scopes_says_so_on_its_card() -> None:
    script = (ASSETS / "views" / "overview.js").read_text(encoding="utf-8")
    assert "if (structure && !scopes.length) body =" in script and "Scope はまだありません" in script
    assert ".sd-ov__none" in (ASSETS / "views" / "overview.css").read_text(encoding="utf-8")


def test_the_narrow_graph_starts_under_the_band_of_marks() -> None:
    css = (ASSETS / "views" / "graph.css").read_text(encoding="utf-8")
    narrow = css[css.index("@container app (max-width: 640px)") :]
    assert ".gx { background: var(--ds-bg-2); }" in narrow
    assert ".gx .gx-view { top: 46px;" in narrow
