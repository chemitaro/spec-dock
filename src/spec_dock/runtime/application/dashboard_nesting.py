"""The repositories' nesting and tier labels, from their registered main checkouts (iss-00613 D-01).

A pure function: it compares the given paths by their parts and touches no file, network, clock or path
resolution. The caller resolves the paths once when it reads the listing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

TIER_LABELS: Mapping[str, str] = {"businesses": "事業", "products": "プロダクト", "services": "サービス"}

_Parts = tuple[str, ...]


@dataclass(frozen=True)
class Nesting:
    parent: str | None
    tier: tuple[str, ...]


def _parts(path: str | None) -> _Parts | None:
    """The path's parts, or None for a path that is not absolute (empty included, F-05)."""
    if not path:
        return None
    pure = PurePosixPath(path)
    return pure.parts if pure.is_absolute() else None


def _contains(outer: _Parts, inner: _Parts) -> bool:
    """Whether `outer` is a proper head of `inner` by parts (not by characters; the same path does not count)."""
    return len(outer) < len(inner) and inner[: len(outer)] == outer


def repository_nesting(shown: Sequence[tuple[str, str | None]], boundaries: Sequence[str]) -> dict[str, Nesting]:
    """Each shown repository's nearest shown ancestor and the tier labels between them.

    `shown` holds the listed repositories as (key, resolved main checkout or None) in the listing's order;
    `boundaries` holds every registry row's resolved main checkout (hidden, unknown and ambiguous rows too).
    A repository without one checkout is at the top and parents nothing (F-02). The labels count from the
    nearest registered checkout, so the names of a hidden repository and above it never show (F-03).
    """
    checkouts = [(key, _parts(path)) for key, path in shown]
    walls = [parts for parts in (_parts(path) for path in boundaries) if parts is not None]
    walls.extend(parts for _key, parts in checkouts if parts is not None)
    result: dict[str, Nesting] = {}
    for key, child in checkouts:
        parent: tuple[str, _Parts] | None = None
        if child is not None:
            for other, outer in checkouts:
                # Strictly longer only: of two at the same path, the first shown wins (a fixed result).
                if outer is not None and _contains(outer, child) and (parent is None or len(outer) > len(parent[1])):
                    parent = (other, outer)
        if parent is None or child is None:
            result[key] = Nesting(None, ())
            continue
        nearest = max((wall for wall in walls if _contains(wall, child)), key=len)
        between = child[len(nearest) : -1]
        result[key] = Nesting(parent[0], tuple(TIER_LABELS.get(name, name) for name in between))
    return result
