"""The package maps a `schema` value to the type directory it ships (iss-00472 RQ-02, AC-08)."""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_dock.runtime.infra.cue_schemas import schema_directory, shipped_schemas

PACKAGE = Path(__file__).resolve().parents[3] / "src/spec_dock"


def test_the_first_version_names_the_v1_directory_of_the_package() -> None:
    assert schema_directory("specdock/v1") == PACKAGE / "cue/v1"


@pytest.mark.parametrize(
    "schema",
    [
        "specdock/v2",
        "specdock/v0",
        "specdock/v01",
        "specdock/V1",
        "specdock/v1/",
        "specdock/v1/../v1",
        " specdock/v1",
        "specdock/v1\n",
        "v1",
        "other/v1",
        "",
        None,
        1,
        ["specdock/v1"],
    ],
)
def test_a_version_the_package_does_not_ship_or_a_malformed_value_names_no_directory(schema: object) -> None:
    assert schema_directory(schema) is None


def test_the_package_lists_the_versions_it_ships_in_version_order() -> None:
    assert shipped_schemas() == ("specdock/v1",)
    assert all(schema_directory(name) is not None for name in shipped_schemas())
