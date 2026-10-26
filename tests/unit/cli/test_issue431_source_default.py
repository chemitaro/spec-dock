"""`--source` of dependency check and workspace sync: legacy values stay `local`; explicitness is recorded (iss-00431)."""

from __future__ import annotations

import pytest

from spec_dock.runtime.cli.options import parse_vnext, parse_vnext_output


@pytest.mark.parametrize("leaf", [["dependency", "check", "iss-00001"], ["workspace", "sync"]])
def test_without_source_the_value_is_local_and_not_explicit(leaf: list[str]) -> None:
    parsed = parse_vnext(leaf)
    assert (parsed.source, parsed.source_explicit) == ("local", False)


@pytest.mark.parametrize("leaf", [["dependency", "check", "iss-00001"], ["workspace", "sync"]])
@pytest.mark.parametrize("value", ["local", "github"])
def test_an_explicit_source_is_kept_and_marked(leaf: list[str], value: str) -> None:
    parsed = parse_vnext([*leaf, "--source", value])
    assert (parsed.source, parsed.source_explicit) == (value, True)
    parsed = parse_vnext([*leaf, f"--source={value}"])
    assert (parsed.source, parsed.source_explicit) == (value, True)


@pytest.mark.parametrize("leaf", [["dependency", "check"], ["workspace", "sync"]])
def test_help_shows_the_same_source_choices_without_a_default(leaf: list[str]) -> None:
    outcome = parse_vnext_output([*leaf, "--help"])
    assert "[--source {local,github}]" in outcome.stdout
    assert "default" not in outcome.stdout.lower().split("options:")[1].split("target:")[0]


def test_other_leaves_have_no_source_marker() -> None:
    assert not hasattr(parse_vnext(["scope", "list"]), "source_explicit")
