"""The repositories' nesting from the registered main checkouts (iss-00613 T-01〜T-05, iss-00635 T-01).

Only the parent remains: the directory names between a parent and a child mean nothing (iss-00635 R-01).
"""

from __future__ import annotations

import importlib

from spec_dock.runtime.application.dashboard_nesting import repository_nesting

CO = "github.com/o/company-os"
HL = "github.com/o/housing-lifecycle"
TK = "github.com/o/taikyohiyou_project"
ID = "github.com/o/input-devices"
GM = "github.com/o/generic-mona"
TC = "github.com/o/tenting-cradle"
YB = "github.com/o/yubisaki"
SD = "github.com/o/spec-dock"
OW = "github.com/o/orca-web"

MACHINE: list[tuple[str, str | None]] = [
    (CO, "/ws/company-os"),
    (GM, "/ws/company-os/businesses/input-devices/products/generic-mona"),
    (HL, "/ws/company-os/businesses/housing-lifecycle"),
    (ID, "/ws/company-os/businesses/input-devices"),
    (OW, "/ws/tools/orca-web"),
    (SD, "/ws/tools/spec-dock"),
    (TK, "/ws/company-os/businesses/housing-lifecycle/products/taikyohiyou_project"),
    (TC, "/ws/company-os/businesses/input-devices/products/tenting-cradle"),
    (YB, "/ws/company-os/businesses/input-devices/products/yubisaki"),
]


# --- T-01: the machine's registry shape ----------------------------------------------------------------------


def test_the_machine_shape_nests_the_company_and_leaves_the_tools_at_the_top() -> None:
    assert repository_nesting(MACHINE) == {
        CO: None,
        GM: ID,
        HL: CO,
        ID: CO,
        OW: None,
        SD: None,
        TK: HL,
        TC: ID,
        YB: ID,
    }


def test_the_result_keeps_the_shown_order() -> None:
    assert list(repository_nesting(MACHINE)) == [key for key, _path in MACHINE]


def test_the_directory_names_between_do_not_matter() -> None:
    """The same shape under other names nests the same way (iss-00635 R-01)."""
    named: list[tuple[str, str | None]] = [
        ("a", "/ws/a"),
        ("b", "/ws/a/businesses/b"),
        ("c", "/ws/a/businesses/b/products/c"),
        ("d", "/ws/a/businesses/b/services/d"),
    ]
    other: list[tuple[str, str | None]] = [
        ("a", "/ws/a"),
        ("b", "/ws/a/groups/b"),
        ("c", "/ws/a/groups/b/team/c"),
        ("d", "/ws/a/groups/b/x/y/d"),
    ]
    expected = {"a": None, "b": "a", "c": "b", "d": "b"}
    assert repository_nesting(named) == expected
    assert repository_nesting(other) == expected


def test_the_tier_labels_are_gone() -> None:
    module = importlib.import_module("spec_dock.runtime.application.dashboard_nesting")
    assert not hasattr(module, "TIER_LABELS")
    assert not hasattr(module, "Nesting")


# --- T-02: the boundary shapes -------------------------------------------------------------------------------


def test_a_shared_name_prefix_is_not_nesting() -> None:
    shown: list[tuple[str, str | None]] = [("a", "/ws/a"), ("a-b", "/ws/a-b"), ("a/x", "/ws/a/x")]
    assert repository_nesting(shown) == {"a": None, "a-b": None, "a/x": "a"}


def test_the_same_path_is_not_nesting() -> None:
    shown: list[tuple[str, str | None]] = [("a", "/ws/a"), ("b", "/ws/a")]
    assert repository_nesting(shown) == {"a": None, "b": None}


def test_a_child_of_two_repositories_at_the_same_path_takes_the_first_shown() -> None:
    shown: list[tuple[str, str | None]] = [("b", "/ws/a"), ("a", "/ws/a"), ("c", "/ws/a/products/c")]
    assert repository_nesting(shown)["c"] == "b"


def test_three_levels_take_the_nearest_ancestor() -> None:
    shown: list[tuple[str, str | None]] = [
        ("c", "/ws/a/groups/team/b/services/c"),
        ("a", "/ws/a"),
        ("b", "/ws/a/groups/team/b"),
    ]
    assert repository_nesting(shown) == {"c": "b", "a": None, "b": "a"}


# --- T-03: a repository without one checkout (two clones) ----------------------------------------------------


def test_an_ambiguous_repository_is_at_the_top_and_parents_nothing() -> None:
    shown: list[tuple[str, str | None]] = [("top", "/ws/top"), ("amb", None), ("inner", "/ws/top/x/clone/products/in")]
    assert repository_nesting(shown) == {"top": None, "amb": None, "inner": "top"}


def test_inside_an_ambiguous_clone_without_a_shown_ancestor_is_at_the_top() -> None:
    shown: list[tuple[str, str | None]] = [("amb", None), ("inner", "/ws/clone/products/in")]
    assert repository_nesting(shown) == {"amb": None, "inner": None}


# --- T-04: hidden repositories (never in `shown`) ------------------------------------------------------------


def test_inside_a_hidden_repository_is_the_child_of_the_outer_shown_ancestor() -> None:
    shown: list[tuple[str, str | None]] = [
        (CO, "/ws/company-os"),
        (TK, "/ws/company-os/businesses/housing-lifecycle/products/taikyohiyou_project"),
    ]
    assert repository_nesting(shown) == {CO: None, TK: CO}


def test_inside_a_hidden_repository_without_a_shown_ancestor_is_at_the_top() -> None:
    shown: list[tuple[str, str | None]] = [(TK, "/ws/company-os/businesses/housing-lifecycle/products/tk")]
    assert repository_nesting(shown) == {TK: None}


# --- T-05: paths that are not absolute -----------------------------------------------------------------------


def test_paths_that_are_not_absolute_are_not_used() -> None:
    shown: list[tuple[str, str | None]] = [
        ("top", "/ws/top"),
        ("empty", ""),
        ("relative", "ws/top/products/rel"),
        ("inner", "/ws/top/businesses/b/products/in"),
    ]
    assert repository_nesting(shown) == {"top": None, "empty": None, "relative": None, "inner": "top"}


def test_a_relative_repository_never_parents() -> None:
    shown: list[tuple[str, str | None]] = [("relative", "ws"), ("inner", "/ws/products/in")]
    assert repository_nesting(shown) == {"relative": None, "inner": None}
