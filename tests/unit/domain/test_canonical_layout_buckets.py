"""Scope directories live under their number's thousand bucket (contract C3, iss-00460)."""

from __future__ import annotations

import os
from pathlib import PurePosixPath

import pytest

from spec_dock.runtime.domain.canonical_layout import (
    BUCKET_SIZE,
    LINK_RELATIVE,
    SCOPE_TO_SPEC_DOCK,
    is_bucket_name,
    scope_bucket,
    scope_relative,
)


@pytest.mark.parametrize(
    ("number", "bucket"),
    [
        (1, "00000-00999"),
        (454, "00000-00999"),
        (999, "00000-00999"),
        (1000, "01000-01999"),
        (2114, "02000-02999"),
        (99999, "99000-99999"),
        (100000, "100000-100999"),
        (100454, "100000-100999"),
        (1000000, "1000000-1000999"),
    ],
)
def test_a_bucket_is_the_numbers_thousand_range_as_wide_as_the_id_number(number: int, bucket: str) -> None:
    assert scope_bucket(number) == bucket


@pytest.mark.parametrize("number", [0, -1, -1000])
def test_numbers_below_one_have_no_bucket(number: int) -> None:
    with pytest.raises(ValueError):
        scope_bucket(number)


def test_the_kind_never_changes_the_bucket() -> None:
    assert BUCKET_SIZE == 1000
    assert {scope_relative(name).parent for name in ("init-00454", "epic-00454", "iss-00454")} == {
        PurePosixPath("00000-00999")
    }


@pytest.mark.parametrize(
    ("scope_id", "relative"),
    [
        ("iss-00454", "00000-00999/iss-00454"),
        ("epic-02114", "02000-02999/epic-02114"),
        ("iss-100454", "100000-100999/iss-100454"),
    ],
)
def test_a_scope_directory_is_its_bucket_then_its_id(scope_id: str, relative: str) -> None:
    assert scope_relative(scope_id) == PurePosixPath(relative)


@pytest.mark.parametrize("invalid", ["iss-454", "iss-000454", "ISS-00454", " iss-00454", "iss-00000", "iss-00454-foo"])
def test_only_an_exact_id_has_a_scope_place(invalid: str) -> None:
    with pytest.raises(ValueError):
        scope_relative(invalid)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("00000-00999", True),
        ("01000-01999", True),
        ("99000-99999", True),
        ("100000-100999", True),
        ("1000000-1000999", True),
        ("0-999", False),
        ("00000-00998", False),
        ("00001-01000", False),
        ("000000-000999", False),
        ("1000-1999", False),
        ("01000-01999x", False),
        ("iss-00454", False),
    ],
)
def test_only_exact_bucket_names_are_buckets(name: str, expected: bool) -> None:
    assert is_bucket_name(name) is expected


def test_three_levels_lead_from_a_scope_directory_back_to_spec_dock() -> None:
    assert PurePosixPath("../../..") == SCOPE_TO_SPEC_DOCK
    joined = LINK_RELATIVE / scope_relative("iss-00454") / SCOPE_TO_SPEC_DOCK
    assert os.path.normpath(joined) == "spec-dock"
