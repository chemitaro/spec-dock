"""`--source` of dependency check and workspace sync: only `github` is accepted and no default is shown (iss-00431)."""

from __future__ import annotations

import pytest

from spec_dock.runtime.cli.options import parse_vnext_output


@pytest.mark.parametrize("leaf", [["dependency", "check"], ["workspace", "sync"]])
def test_help_shows_the_same_source_choices_without_a_default(leaf: list[str]) -> None:
    outcome = parse_vnext_output([*leaf, "--help"])
    assert "[--source {github}]" in outcome.stdout
    assert "default" not in outcome.stdout.lower().split("options:")[1].split("target:")[0]
