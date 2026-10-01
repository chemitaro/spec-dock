"""Read and validate dependency edges without writer admission or retired state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.domain.dependency_vnext import validate_dependency_graph
from spec_dock.runtime.domain.lifecycle import decode_scope_metadata
from spec_dock.runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from spec_dock.runtime.application.scope_query import ScopeView


def read_raw_edges(
    views: tuple[ScopeView, ...],
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[dict[str, object], tuple[int, int]]]]:
    raw: dict[str, tuple[str, ...]] = {}
    loaded_by_id: dict[str, tuple[dict[str, object], tuple[int, int]]] = {}
    for view in views:
        loaded = read_guarded_json(view.path / ".meta.json")
        if loaded is None or not isinstance(loaded[0], dict):
            raise ValueError("Scope metadata is missing or invalid")
        metadata = decode_scope_metadata(loaded[0])
        if (
            metadata.raw.get("id") != view.id
            or metadata.raw.get("type") != view.kind
            or metadata.raw.get("title") != view.title
            or metadata.raw.get("parent_id") != view.parent_id
            or metadata.revision != view.revision
        ):
            raise ValueError("Scope metadata changed during dependency read")
        depends_on = metadata.raw.get("depends_on")
        if not isinstance(depends_on, list) or any(not isinstance(item, str) for item in depends_on):
            raise ValueError("Scope dependencies must be canonical ID strings")
        raw[view.id] = tuple(depends_on)
        loaded_by_id[view.id] = metadata.raw, loaded[1]
    validate_dependency_graph(views, raw)
    return raw, loaded_by_id
