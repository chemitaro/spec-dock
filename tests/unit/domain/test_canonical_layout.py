"""Catalog and link locations, the correct-link rule, ignore lines and the Git version floor (contract C3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_dock.runtime.domain.canonical_layout import (
    EXCLUDE_LINES,
    GITIGNORE_LINES,
    CatalogLayout,
    LinkObservation,
    append_lines,
    git_supported,
    link_state,
    missing_lines,
    parse_git_version,
)

MAIN = Path("/work/repo")
LINKED = Path("/work/trees/feature")


def test_the_main_checkout_links_relatively_and_a_linked_worktree_absolutely() -> None:
    layout = CatalogLayout(MAIN, MAIN / ".git", LINKED)
    assert layout.catalog == MAIN / "spec-dock/.canonical"
    assert layout.link_text(MAIN) == ".canonical"
    assert layout.link_text(LINKED) == "/work/repo/spec-dock/.canonical"
    assert layout.link_path(LINKED) == LINKED / "spec-dock/initiatives"
    assert layout.checkouts == (MAIN, LINKED) and not layout.is_main


def test_running_in_the_main_checkout_links_only_the_main_checkout() -> None:
    layout = CatalogLayout(MAIN, MAIN / ".git", MAIN)
    assert layout.checkouts == (MAIN,) and layout.is_main


CATALOG = MAIN / "spec-dock/.canonical"


@pytest.mark.parametrize(
    ("observed", "state"),
    [
        (LinkObservation(MAIN / "spec-dock/initiatives", "absent"), "absent"),
        (LinkObservation(MAIN / "spec-dock/initiatives", "symlink", ".canonical", CATALOG), "correct"),
        (
            LinkObservation(MAIN / "spec-dock/initiatives", "symlink", "/work/repo/spec-dock/.canonical", CATALOG),
            "wrong_link",
        ),
        (LinkObservation(MAIN / "spec-dock/initiatives", "symlink", ".canonical", None), "wrong_link"),
        (LinkObservation(MAIN / "spec-dock/initiatives", "symlink", ".canonical", Path("/elsewhere")), "wrong_link"),
        (LinkObservation(MAIN / "spec-dock/initiatives", "directory", entries=3), "occupied"),
        (LinkObservation(MAIN / "spec-dock/initiatives", "file"), "occupied"),
        (LinkObservation(MAIN / "spec-dock/initiatives", "other"), "occupied"),
    ],
)
def test_only_the_expected_symlink_resolving_to_the_catalog_is_correct(observed: LinkObservation, state: str) -> None:
    assert link_state(observed, expected_text=".canonical", catalog=CATALOG) == state


def test_a_link_is_never_correct_while_the_catalog_is_missing() -> None:
    observed = LinkObservation(MAIN / "spec-dock/initiatives", "symlink", ".canonical", CATALOG)
    assert link_state(observed, expected_text=".canonical", catalog=None) == "wrong_link"


def test_the_ignore_lines_have_a_repository_root_and_a_spec_dock_form() -> None:
    assert EXCLUDE_LINES == ("/spec-dock/.canonical/", "/spec-dock/initiatives", "!/spec-dock/initiatives/")
    assert GITIGNORE_LINES == ("/.canonical/", "/initiatives", "!/initiatives/")


def test_missing_lines_ignore_trailing_whitespace_and_carriage_returns() -> None:
    text = "# local\r\n/spec-dock/.canonical/  \r\n/spec-dock/initiatives\r\n!/spec-dock/initiatives/\n"
    assert missing_lines(text, EXCLUDE_LINES) == ()
    assert missing_lines(None, EXCLUDE_LINES) == EXCLUDE_LINES


def test_appending_all_three_lines_adds_a_note_and_keeps_existing_content() -> None:
    appended = append_lines("*.log", EXCLUDE_LINES)
    assert appended == (
        "*.log\n# spec-dock canonical catalog and link (added by spec-dock canonical link)\n"
        "/spec-dock/.canonical/\n/spec-dock/initiatives\n!/spec-dock/initiatives/\n"
    )
    assert append_lines(None, EXCLUDE_LINES).startswith("# spec-dock canonical")


def test_a_partial_block_is_completed_with_the_whole_block_in_order() -> None:
    partial = "/spec-dock/.canonical/\n!/spec-dock/initiatives/\n"
    assert missing_lines(partial, EXCLUDE_LINES) == EXCLUDE_LINES
    appended = append_lines(partial, EXCLUDE_LINES)
    assert appended.startswith(partial) and appended.endswith(
        "/spec-dock/.canonical/\n/spec-dock/initiatives\n!/spec-dock/initiatives/\n"
    )
    assert missing_lines(appended, EXCLUDE_LINES) == ()
    assert append_lines(appended, EXCLUDE_LINES) == appended


def test_lines_present_in_the_wrong_order_count_as_missing() -> None:
    reversed_order = "!/spec-dock/initiatives/\n/spec-dock/initiatives\n/spec-dock/.canonical/\n"
    assert missing_lines(reversed_order, EXCLUDE_LINES) == EXCLUDE_LINES
    later_user_line = "/spec-dock/.canonical/\n/spec-dock/initiatives\n!/spec-dock/initiatives/\n*.log\n"
    assert missing_lines(later_user_line, EXCLUDE_LINES) == ()


@pytest.mark.parametrize(
    ("reported", "version", "supported"),
    [
        ("git version 2.54.0", (2, 54, 0), True),
        ("git version 2.39.5 (Apple Git-154)\n", (2, 39, 5), True),
        ("git version 2.38", (2, 38, 0), True),
        ("git version 2.37.9", (2, 37, 9), False),
        ("git version 2.34.1", (2, 34, 1), False),
        ("git version 3.0.0.windows.1", (3, 0, 0), True),
        ("not git", None, False),
        ("", None, False),
    ],
)
def test_git_version_floor_is_two_thirty_eight(
    reported: str, version: tuple[int, int, int] | None, supported: bool
) -> None:
    assert parse_git_version(reported) == version
    assert git_supported(version) is supported
