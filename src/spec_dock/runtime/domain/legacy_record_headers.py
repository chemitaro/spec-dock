"""Validate historical header shapes without adopting their identities or effects."""

from __future__ import annotations

import re

_TRANSITION_PHASES = {
    "migration": ("prepared", "applying", "recovery-required", "committed", "rollback-required", "rolled-back"),
    "installation": ("preparing", "staged", "applying", "recovery-required", "committed", "rolled-back"),
    "finalization": ("prepared", "committed"),
    "handover": ("prepared", "committed", "rolling-back", "rolled-back"),
}


def readable_legacy_header(payload: dict[str, object], kind: str) -> bool:
    if kind in _TRANSITION_PHASES:
        return _transition_header(payload, kind)
    if kind == "engine":
        return all(_text(payload.get(key)) for key in ("executable", "distribution_root", "distribution_digest"))
    if kind == "control":
        worktrees = payload.get("worktrees")
        return (
            _nonnegative(payload.get("epoch"))
            and _text(payload.get("writer_protocol"))
            and _text(payload.get("engine_digest"))
            and payload.get("mode") in ("uninitialized", "maintenance", "ready", "recovery-required")
            and isinstance(worktrees, list)
            and all(_worktree(item) for item in worktrees)
        )
    if kind == "registry":
        high_water = payload.get("high_water")
        branches = payload.get("branch_bindings", [])
        return (
            _nonnegative(payload.get("revision"))
            and isinstance(high_water, dict)
            and set(high_water) == {"initiative", "epic", "issue"}
            and all(_nonnegative(value) for value in high_water.values())
            and _strings(payload.get("reserved_ids"))
            and _strings(payload.get("deleted_ids", []))
            and isinstance(branches, list)
            and all(
                isinstance(item, dict) and all(_text(item.get(key)) for key in ("scope_id", "name", "initial_sha"))
                for item in branches
            )
        )
    if kind == "active":
        return (
            _text(payload.get("worktree_id"))
            and _nonnegative(payload.get("revision"))
            and (payload.get("focus_id") is None or _text(payload.get("focus_id")))
            and all(_active_entry(payload.get(role)) for role in ("initiative", "epic", "issue"))
        )
    if kind == "journal":
        effects = payload.get("effects")
        operation_id = payload.get("operation_id")
        return (
            isinstance(operation_id, str)
            and re.fullmatch(r"[0-9a-f]{32}", operation_id) is not None
            and all(_text(payload.get(key)) for key in ("command", "request_fingerprint", "phase", "engine_digest"))
            and all(_nonnegative(payload.get(key)) for key in ("writer_epoch", "sequence"))
            and all(_strings(payload.get(key)) for key in ("effect_plan", "backup_refs"))
            and _pairs(payload.get("fixed_targets"), str)
            and _pairs(payload.get("before_revisions"), int)
            and payload.get("terminal_status") in ("pending", "succeeded", "failed", "unknown", "rolled-back")
            and isinstance(effects, list)
            and all(_effect(item) for item in effects)
        )
    return False


def _transition_header(payload: dict[str, object], kind: str) -> bool:
    operation_id = payload.get("operation_id")
    if not (
        isinstance(operation_id, str)
        and re.fullmatch(r"[0-9a-f]{32}", operation_id) is not None
        and _text(payload.get("common_dir"))
        and _nonnegative(payload.get("control_epoch"))
        and payload.get("phase") in _TRANSITION_PHASES[kind]
    ):
        return False
    if kind == "migration":
        return all(
            _text(payload.get(key)) for key in ("repository_uid", "source_inventory_digest", "engine_digest")
        ) and all(isinstance(payload.get(key), list) for key in ("worktrees", "files", "completed_paths"))
    if not isinstance(payload.get("targets"), list):
        return False
    if kind == "installation":
        return payload.get("action") in ("init", "update", "uninstall")
    if kind == "finalization":
        return _text(payload.get("engine_digest")) and _strings(payload.get("targets"))
    return all(
        _text(payload.get(key))
        for key in (
            "source_update_id",
            "prior_executable",
            "prior_distribution_root",
            "prior_digest",
            "next_executable",
            "next_distribution_root",
            "next_digest",
        )
    ) and _strings(payload.get("targets"))


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _nonnegative(value: object) -> bool:
    return type(value) is int and value >= 0


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _pairs(value: object, expected: type[str] | type[int]) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, list) and len(item) == 2 and isinstance(item[0], str) and type(item[1]) is expected
        for item in value
    )


def _worktree(value: object) -> bool:
    return (
        isinstance(value, dict)
        and all(_text(value.get(key)) for key in ("id", "root", "writer_protocol", "engine_digest"))
        and type(value.get("schema_version")) is int
        and type(value.get("active")) is bool
        and (value.get("alias") is None or _text(value.get("alias")))
    )


def _active_entry(value: object) -> bool:
    return value is None or (isinstance(value, dict) and _text(value.get("id")) and _text(value.get("path")))


def _effect(value: object) -> bool:
    return (
        isinstance(value, dict)
        and _text(value.get("id"))
        and _text(value.get("target"))
        and value.get("kind") in ("local", "git", "remote")
        and value.get("status") in ("intent", "succeeded", "failed", "unknown", "not-applied")
        and (value.get("retry_of") is None or _text(value.get("retry_of")))
        and (value.get("remote_ref") is None or _text(value.get("remote_ref")))
        and _pairs(value.get("after_revisions", []), int)
    )
