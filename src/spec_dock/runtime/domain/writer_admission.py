"""Writer-only schema/feature admission, leaving unknown optional data intact."""

from __future__ import annotations


def require_supported_features(payload: dict[str, object]) -> None:
    if "required_features" not in payload:
        return
    features = payload["required_features"]
    if not isinstance(features, list) or any(not isinstance(feature, str) for feature in features):
        raise ValueError("required_features must be a string array")
    if features:
        raise ValueError("unsupported required_features")


def require_workspace_write(payload: dict[str, object]) -> None:
    require_supported_features(payload)
    if "type" in payload or "control_epoch" in payload:
        raise ValueError("workspace contains a forbidden schema field")


def require_scope_structure(payload: dict[str, object]) -> None:
    required = {
        "schema_version",
        "type",
        "id",
        "title",
        "slug",
        "parent_id",
        "initiative_id",
        "epic_id",
        "depends_on",
        "backend",
        "github",
        "lifecycle",
        "revision",
    }
    if not required <= payload.keys():
        raise ValueError("Scope metadata is missing required schema fields")


def require_scope_write(payload: dict[str, object]) -> None:
    require_scope_structure(payload)
    require_supported_features(payload)
