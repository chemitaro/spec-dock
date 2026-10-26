"""Where a clone's catalog and links live, what a correct link is, and the ignore lines (contract C3)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path, PurePosixPath
import re
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from collections.abc import Sequence

CANONICAL_BRANCH: Final = "spec-dock/canonical"
CANONICAL_REF: Final = "refs/heads/spec-dock/canonical"
CANONICAL_REMOTE: Final = "origin"
CANONICAL_TRACKING_REF: Final = "refs/remotes/origin/spec-dock/canonical"
CATALOG_RELATIVE: Final = PurePosixPath("spec-dock/.canonical")
LINK_RELATIVE: Final = PurePosixPath("spec-dock/initiatives")
MAIN_LINK_TEXT: Final = ".canonical"
CATALOG_LOCK_REASON: Final = "spec-dock canonical catalog"
# Ignore only a symlinked spec-dock/initiatives; a real directory's new files stay visible (Epic design ch. 3).
EXCLUDE_LINES: Final = ("/spec-dock/.canonical/", "/spec-dock/initiatives", "!/spec-dock/initiatives/")
GITIGNORE_LINES: Final = ("/.canonical/", "/initiatives", "!/initiatives/")
EXCLUDE_NOTE: Final = "# spec-dock canonical catalog and link (added by spec-dock canonical link)"
MINIMUM_GIT_VERSION: Final = (2, 38, 0)

LinkKind = Literal["absent", "symlink", "directory", "file", "other"]
LinkState = Literal["absent", "correct", "wrong_link", "occupied"]

_GIT_VERSION = re.compile(r"^git version (\d+)\.(\d+)(?:\.(\d+))?(?:[.\s].*)?$")


@dataclass(frozen=True)
class CatalogLayout:
    """Real paths of one clone's main checkout and the checkout a command runs in."""

    main_checkout: Path
    common_dir: Path
    checkout: Path

    @property
    def catalog(self) -> Path:
        return self.main_checkout / CATALOG_RELATIVE

    @property
    def is_main(self) -> bool:
        return self.checkout == self.main_checkout

    @property
    def checkouts(self) -> tuple[Path, ...]:
        return (self.main_checkout,) if self.is_main else (self.main_checkout, self.checkout)

    def link_path(self, checkout: Path) -> Path:
        return checkout / LINK_RELATIVE

    def link_text(self, checkout: Path) -> str:
        """Relative in the main checkout; absolute elsewhere, never a link to another link."""
        return MAIN_LINK_TEXT if checkout == self.main_checkout else str(self.catalog)


@dataclass(frozen=True)
class LinkObservation:
    path: Path
    kind: LinkKind
    text: str | None = None
    resolved: Path | None = None
    entries: int | None = None


def link_state(observed: LinkObservation, *, expected_text: str, catalog: Path | None) -> LinkState:
    """A correct link is a symlink with the expected value that resolves to the catalog's real path."""
    if observed.kind == "absent":
        return "absent"
    if observed.kind != "symlink":
        return "occupied"
    if observed.text == expected_text and catalog is not None and observed.resolved == catalog:
        return "correct"
    return "wrong_link"


def missing_lines(text: str | None, lines: Sequence[str]) -> tuple[str, ...]:
    """The rule lines that are not in effect: all of them unless each is present and the last copies are in order.

    Git applies the last matching pattern, so `!/spec-dock/initiatives/` must come after `/spec-dock/initiatives`;
    a block with a line missing or out of order is reported (and repaired) as a whole.
    """
    stripped = [line.rstrip() for line in (text or "").splitlines()]
    last = [max((index for index, line in enumerate(stripped) if line == rule), default=-1) for rule in lines]
    if all(index >= 0 for index in last) and all(a < b for a, b in pairwise(last)):
        return ()
    return tuple(lines)


def append_lines(text: str | None, lines: Sequence[str]) -> str:
    """Append the whole block in order when it is not in effect; earlier partial copies stay untouched."""
    current = text or ""
    if not missing_lines(current, lines):
        return current
    if current and not current.endswith("\n"):
        current += "\n"
    return current + "".join(f"{line}\n" for line in (EXCLUDE_NOTE, *lines))


def parse_git_version(reported: str) -> tuple[int, int, int] | None:
    matched = _GIT_VERSION.match(reported.strip())
    if matched is None:
        return None
    major, minor, patch = matched.groups()
    return int(major), int(minor), int(patch or 0)


def git_supported(version: tuple[int, int, int] | None) -> bool:
    return version is not None and version >= MINIMUM_GIT_VERSION
