"""The repositories' nesting, from their registered main checkouts (iss-00613 D-01, iss-00635 D-01).

A pure function: it compares the given paths by their parts and touches no file, network, clock or path
resolution. The caller resolves the paths once when it reads the listing. The directory names between a parent
and a child mean nothing: only path containment decides.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_Parts = tuple[str, ...]


def _parts(path: str | None) -> _Parts | None:
    """The path's parts, or None for a path that is not absolute (empty included, F-05)."""
    if not path:
        return None
    pure = PurePosixPath(path)
    return pure.parts if pure.is_absolute() else None


def _contains(outer: _Parts, inner: _Parts) -> bool:
    """Whether `outer` is a proper head of `inner` by parts (not by characters; the same path does not count)."""
    return len(outer) < len(inner) and inner[: len(outer)] == outer


def repository_nesting(shown: Sequence[tuple[str, str | None]]) -> dict[str, str | None]:
    """Each shown repository's nearest shown ancestor (its key), or None at the top.

    `shown` holds the listed repositories as (key, resolved main checkout or None) in the listing's order. A
    repository without one checkout is at the top and parents nothing (F-02); a hidden repository is not shown,
    so the ones inside it nest under the outer shown ancestor (F-03).
    """
    checkouts = [(key, _parts(path)) for key, path in shown]
    result: dict[str, str | None] = {}
    for key, child in checkouts:
        parent: tuple[str, _Parts] | None = None
        if child is not None:
            for other, outer in checkouts:
                # Strictly longer only: of two at the same path, the first shown wins (a fixed result).
                if outer is not None and _contains(outer, child) and (parent is None or len(outer) > len(parent[1])):
                    parent = (other, outer)
        result[key] = parent[0] if parent is not None else None
    return result
