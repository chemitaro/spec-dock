"""The repositories' nesting and tier labels from the registered main checkouts (iss-00613 T-01〜T-05)."""

from __future__ import annotations

from spec_dock.runtime.application.dashboard_nesting import TIER_LABELS, Nesting, repository_nesting

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


def _boundaries(shown: list[tuple[str, str | None]]) -> list[str]:
    return [path for _key, path in shown if path is not None]


# --- T-01: the machine's registry shape ----------------------------------------------------------------------


def test_the_machine_shape_nests_the_company_and_leaves_the_tools_at_the_top() -> None:
    nesting = repository_nesting(MACHINE, _boundaries(MACHINE))
    assert set(nesting) == {key for key, _path in MACHINE}
    assert {key: value.parent for key, value in nesting.items()} == {
        CO: None,
        SD: None,
        OW: None,
        HL: CO,
        ID: CO,
        TK: HL,
        GM: ID,
        TC: ID,
        YB: ID,
    }
    assert {key: value.tier for key, value in nesting.items()} == {
        CO: (),
        SD: (),
        OW: (),
        HL: ("事業",),
        ID: ("事業",),
        TK: ("プロダクト",),
        GM: ("プロダクト",),
        TC: ("プロダクト",),
        YB: ("プロダクト",),
    }


def test_the_tier_labels() -> None:
    assert dict(TIER_LABELS) == {"businesses": "事業", "products": "プロダクト", "services": "サービス"}


# --- T-02: the boundary shapes -------------------------------------------------------------------------------


def test_a_shared_name_prefix_is_not_nesting() -> None:
    shown: list[tuple[str, str | None]] = [("a", "/ws/a"), ("a-b", "/ws/a-b"), ("a/x", "/ws/a/x")]
    nesting = repository_nesting(shown, _boundaries(shown))
    assert nesting["a-b"] == Nesting(None, ())
    assert nesting["a/x"] == Nesting("a", ())  # directly under the parent: no label


def test_the_same_path_is_not_nesting() -> None:
    shown: list[tuple[str, str | None]] = [("a", "/ws/a"), ("b", "/ws/a")]
    nesting = repository_nesting(shown, _boundaries(shown))
    assert nesting == {"a": Nesting(None, ()), "b": Nesting(None, ())}


def test_a_child_of_two_repositories_at_the_same_path_takes_the_first_shown() -> None:
    shown: list[tuple[str, str | None]] = [("b", "/ws/a"), ("a", "/ws/a"), ("c", "/ws/a/products/c")]
    nesting = repository_nesting(shown, _boundaries(shown))
    assert nesting["c"] == Nesting("b", ("プロダクト",))


def test_three_levels_take_the_nearest_ancestor() -> None:
    shown: list[tuple[str, str | None]] = [
        ("c", "/ws/a/groups/team/b/services/c"),
        ("a", "/ws/a"),
        ("b", "/ws/a/groups/team/b"),
    ]
    nesting = repository_nesting(shown, _boundaries(shown))
    assert nesting["a"] == Nesting(None, ())
    assert nesting["b"] == Nesting("a", ("groups", "team"))  # unknown names stay as they are
    assert nesting["c"] == Nesting("b", ("サービス",))


# --- T-03: a repository without one checkout (two clones) ----------------------------------------------------


def test_an_ambiguous_repository_is_at_the_top_and_parents_nothing() -> None:
    shown: list[tuple[str, str | None]] = [("top", "/ws/top"), ("amb", None), ("inner", "/ws/top/x/clone/products/in")]
    clones = ["/ws/top/x/clone", "/ws/elsewhere/clone"]
    nesting = repository_nesting(shown, [*_boundaries(shown), *clones])
    assert nesting["amb"] == Nesting(None, ())
    assert nesting["top"] == Nesting(None, ())
    # The child of the outer shown ancestor, labelled from the clone's checkout (the nearest registered row).
    assert nesting["inner"] == Nesting("top", ("プロダクト",))


def test_inside_an_ambiguous_clone_without_a_shown_ancestor_is_at_the_top() -> None:
    shown: list[tuple[str, str | None]] = [("amb", None), ("inner", "/ws/clone/products/in")]
    nesting = repository_nesting(shown, ["/ws/clone", "/ws/other", "/ws/clone/products/in"])
    assert nesting["inner"] == Nesting(None, ())


# --- T-04: hidden repositories and rows without a repository -------------------------------------------------


def test_inside_a_hidden_repository_is_the_child_of_the_outer_shown_ancestor() -> None:
    shown: list[tuple[str, str | None]] = [
        (CO, "/ws/company-os"),
        (TK, "/ws/company-os/businesses/housing-lifecycle/products/taikyohiyou_project"),
    ]
    hidden = "/ws/company-os/businesses/housing-lifecycle"
    nesting = repository_nesting(shown, [*_boundaries(shown), hidden])
    assert nesting[TK] == Nesting(CO, ("プロダクト",))
    assert "housing-lifecycle" not in nesting[TK].tier and "事業" not in nesting[TK].tier


def test_inside_a_hidden_repository_without_a_shown_ancestor_is_at_the_top() -> None:
    child = "/ws/company-os/businesses/housing-lifecycle/products/tk"
    shown: list[tuple[str, str | None]] = [(TK, child)]
    nesting = repository_nesting(shown, ["/ws/company-os", "/ws/company-os/businesses/housing-lifecycle", child])
    assert nesting[TK] == Nesting(None, ())


def test_a_row_without_a_repository_counts_as_a_boundary() -> None:
    shown: list[tuple[str, str | None]] = [("top", "/ws/top"), ("inner", "/ws/top/businesses/unknown/products/in")]
    unknown = "/ws/top/businesses/unknown"
    nesting = repository_nesting(shown, [*_boundaries(shown), unknown])
    assert nesting["inner"] == Nesting("top", ("プロダクト",))


# --- T-05: paths that are not absolute -----------------------------------------------------------------------


def test_paths_that_are_not_absolute_are_not_used() -> None:
    shown: list[tuple[str, str | None]] = [
        ("top", "/ws/top"),
        ("empty", ""),
        ("relative", "ws/top/products/rel"),
        ("inner", "/ws/top/businesses/b/products/in"),
    ]
    boundaries = ["/ws/top", "", "ws/top/businesses/b", "relative/x", "/ws/top/businesses/b/products/in"]
    nesting = repository_nesting(shown, boundaries)
    assert nesting["empty"] == Nesting(None, ())
    assert nesting["relative"] == Nesting(None, ())
    assert nesting["inner"] == Nesting("top", ("事業", "b", "プロダクト"))


def test_a_relative_repository_never_parents() -> None:
    shown: list[tuple[str, str | None]] = [("relative", "ws"), ("inner", "/ws/products/in")]
    nesting = repository_nesting(shown, ["ws", "/ws/products/in"])
    assert nesting["inner"] == Nesting(None, ())
