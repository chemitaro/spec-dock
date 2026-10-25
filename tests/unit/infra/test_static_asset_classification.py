"""installation show and canonical check classify static asset bytes with one rule."""

from __future__ import annotations

from spec_dock.runtime.infra.static_assets import StaticAsset, classify_static_digest

CURRENT = "a" * 64
OLD = "b" * 64
ASSET = StaticAsset("spec-dock/docs/README.md", b"", CURRENT, 0o644, False, (OLD,))


def test_digest_classification_matches_the_installation_show_vocabulary() -> None:
    assert classify_static_digest(ASSET, None) == "missing"
    assert classify_static_digest(ASSET, CURRENT) == "current"
    assert classify_static_digest(ASSET, OLD) == "known-old"
    assert classify_static_digest(ASSET, "c" * 64) == "unknown"
