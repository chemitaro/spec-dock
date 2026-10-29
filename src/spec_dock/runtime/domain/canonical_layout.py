"""Where a clone's catalog and links live, what a correct link is, and the ignore lines (contract C3)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.canonical_structure import parse_scope_id, scope_id as canonical_scope_id

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
GITIGNORE_PATH: Final = "spec-dock/.gitignore"  # where GITIGNORE_LINES apply, from the checkout root
EXCLUDE_NOTE: Final = "# spec-dock canonical catalog and link (added by spec-dock canonical link)"
MINIMUM_GIT_VERSION: Final = (2, 38, 0)
# A Scope directory is <catalog>/<bucket>/<ID>/: the bucket is its number's thousand range, never its kind
# (Epic design ch. 2, iss-00460).
BUCKET_SIZE: Final = 1000
BUCKET_NAME_SHAPE: Final = re.compile(r"^[0-9]+-[0-9]+$")  # shaped like a bucket; is_bucket_name decides
# From a Scope directory back to spec-dock/ through the spec-dock/initiatives link (bucket, ID, initiatives).
SCOPE_TO_SPEC_DOCK: Final = PurePosixPath("../../..")

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


def ignore_rules_state(text: str | None, lines: Sequence[str]) -> tuple[tuple[str, ...], bool]:
    """(lines absent from the text, whether the negation fails to follow the rule it re-includes).

    Git applies the last matching pattern, so the last line (`!/…/initiatives/`) must come after the line before it
    (`/…/initiatives`); otherwise a real initiatives directory is ignored too. The other line's place does not matter.
    """
    stripped = [line.rstrip() for line in (text or "").splitlines()]
    absent = tuple(rule for rule in lines if rule not in stripped)
    if absent:
        return absent, False
    rule, negation = lines[-2], lines[-1]
    last = {value: max(index for index, line in enumerate(stripped) if line == value) for value in (rule, negation)}
    return (), last[negation] < last[rule]


def missing_lines(text: str | None, lines: Sequence[str]) -> tuple[str, ...]:
    """The rule lines not in effect: none when all are present in an effective order, else all of them."""
    absent, misordered = ignore_rules_state(text, lines)
    return tuple(lines) if absent or misordered else ()


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


def scope_bucket(number: int) -> str:
    """The bucket of a Scope number: its thousand range, both ends as wide as the ID number (`00000-00999`)."""
    if number < 1:
        raise ValueError("GitHub Issue number must be positive")
    width = max(5, len(str(number)))
    lower = number - number % BUCKET_SIZE
    return f"{lower:0{width}d}-{lower + BUCKET_SIZE - 1:0{width}d}"


def scope_relative(scope_id: str) -> PurePosixPath:
    """A Scope directory relative to the catalog, `<bucket>/<ID>`; only an exact canonical ID has one."""
    kind, number = parse_scope_id(scope_id)
    if canonical_scope_id(kind, number) != scope_id:
        raise ValueError(f"not an exact canonical Scope ID: {scope_id!r}")
    return PurePosixPath(scope_bucket(number), scope_id)


def is_bucket_name(name: str) -> bool:
    """Exactly the name some number's bucket has (`0-999` and `00000-00998` are not)."""
    if BUCKET_NAME_SHAPE.fullmatch(name) is None:
        return False
    lower = int(name.partition("-")[0])
    return lower % BUCKET_SIZE == 0 and name == scope_bucket(max(lower, 1))
