from __future__ import annotations

import json
from typing import Any, cast

import pytest

from spec_dock.provider_lifecycle import _wire_generated
from spec_dock.provider_lifecycle.contracts import LifecycleRequest
from spec_dock.provider_lifecycle.wire import (
    WireValidationError,
    build_public_result,
    parse_installation_record,
    parse_slot_marker,
    serialize_installation_record,
    serialize_slot_marker,
    validate_public_result,
)

_RELATION_TARGET = "/tmp/wire-relation-consumer"
_RELATION_DIGEST = "d" * 64
_RELATION_CLEANUP_TOKEN = "e" * 64
_RELATION_PATHS = (
    "spec-dock",
    "spec-dock/spec-dock.version",
    "spec-dock/docs",
    "spec-dock/templates",
    "spec-dock/system",
    "spec-dock/scripts",
    ".agents/skills/spec-dock",
    ".agents/skills/spec-dock-grill-with-docs",
    "spec-dock/.gitignore",
    ".github/workflows/ci.yml",
    "@provider-stage",
)
_RELATION_CATEGORIES = ("container", "record", "root", "root", "root", "root", "slot", "slot", "seed", "seed", "stage")
_RELATION_ERROR_TEXT = {
    "already-initialized": "SpecDock tooling is already installed; use init --force or update.",
    "tooling-not-installed": "SpecDock tooling is not installed for this target.",
    "installation-record-invalid": "The SpecDock installation record is invalid.",
    "installation-record-state-inconsistent": "The SpecDock installation record does not match the observed tooling state.",
    "resume-operation-mismatch": "The incomplete operation can be resumed only with the same operation.",
    "resume-candidate-mismatch": "The incomplete operation can be resumed only with the same candidate digest.",
    "resume-seed-policy-mismatch": "The incomplete operation can be resumed only with the same seed policy.",
    "candidate-invalid": "The packaged provider candidate is invalid.",
    "candidate-digest-mismatch": "The staged provider candidate digest does not match the packaged candidate.",
    "repository-operation-busy": "Another SpecDock command holds repository coordination; retry after it exits.",
    "repository-coordination-unavailable": "Required repository coordination is unavailable; no operation was executed.",
    "unsafe-repository-binding": "The repository root binding is unsafe or changed during the operation.",
    "unsafe-parent-binding": "A required parent directory binding is unsafe or changed during the operation.",
    "unsafe-target-type": "A fixed provider target has an unsupported filesystem type.",
    "foreign-tooling-root": "A fixed tooling root exists without provider ownership evidence.",
    "foreign-skill-slot": "A fixed skill slot exists without matching provider ownership evidence.",
    "unsupported-legacy-version": "This legacy SpecDock version is not eligible for automatic migration.",
    "active-legacy-recovery": "Legacy recovery evidence is active; complete recovery with the last compatible package before migration.",
    "modified-legacy-workspace": "The legacy 0.2.3 tooling payload is not an exact clean migration source.",
    "atomic-rename-unavailable": "The required native atomic rename primitive is unavailable.",
    "stage-owner-mismatch": "The existing provider stage does not match this repository, operation, candidate, and seed policy.",
    "bootstrap-container-conflict": "The shared spec-dock container cannot be safely created or bound.",
    "bootstrap-cleanup-failed": "The fresh container bootstrap failed and could not be restored to the exact absent pre-state.",
    "terminal-cleanup-failed": "The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly.",
    "install-partial-failure": "SpecDock install stopped after durable mutation; rerun the exact retry command.",
    "update-partial-failure": "SpecDock update stopped after durable mutation; rerun the exact retry command.",
    "uninstall-partial-failure": "SpecDock uninstall stopped after durable mutation; rerun the exact retry command.",
    "invalid-request": "The SpecDock lifecycle request is invalid.",
    "spec-history-purge-removed": "Spec history purge has been removed; uninstall is tooling-only.",
    "lifecycle-preparation-failed": "Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly.",
}
_RELATION_WARNING = (
    "Provider tooling reached the requested terminal state, but the owned external stage could not be removed."
)


def _relation_operation(row: dict[str, object]) -> str | None:
    token = row["operation"]
    if token in {"install", "update", "uninstall"}:
        return cast("str", token)
    if token is None or token == "null":
        return None
    variant = str(row["variant"])
    if token in {"active.operation", "receipt.operation"}:
        if "uninstall" in variant:
            return "uninstall"
        if "update" in variant:
            return "update"
        return "install"
    if token == "record.operation":
        return "install"
    raise AssertionError(f"unhandled operation token: {token}")


def _relation_seed_policy(row: dict[str, object], operation: str | None) -> str | None:
    token = row["seed_policy"]
    if token in {"create-if-absent", "preserve-only"}:
        return cast("str", token)
    if token is None or token == "null":
        return None
    if token == "record.seed_policy=preserve-only":
        return "preserve-only"
    if token in {"record.seed_policy", "active.seed_policy", "receipt.seed_policy"}:
        variant = str(row["variant"])
        if operation == "install" and ("init" in variant or "create-if-absent" in variant):
            return "create-if-absent"
        return "preserve-only"
    raise AssertionError(f"unhandled seed policy token: {token}")


def _relation_digest(token: object) -> str | None:
    if token is None or token == "null":
        return None
    return _RELATION_DIGEST


def _relation_specs_mode(row: dict[str, object]) -> str | None:
    variant = str(row["variant"])
    if "specs_mode=keep" in variant:
        return "keep"
    if "uninstall remove" in variant:
        return "remove"
    return None


def _relation_desired_command(row: dict[str, object], operation: str | None, seed_policy: str | None) -> str:
    variant = str(row["variant"])
    command = variant.removeprefix("desired `").split(";", 1)[0].strip("`")
    command_prefix = {
        "init": "spec-dock init -- ",
        "init --force": "spec-dock init --force -- ",
        "update": "spec-dock update -- ",
        "uninstall dry-run default": "spec-dock uninstall -- ",
        "uninstall dry-run keep": "spec-dock uninstall --keep-specs -- ",
        "uninstall apply default": "spec-dock uninstall --apply -- ",
        "uninstall apply keep": "spec-dock uninstall --apply --keep-specs -- ",
    }.get(command)
    if command_prefix is not None:
        return command_prefix + _RELATION_TARGET
    if operation == "uninstall":
        return f"spec-dock uninstall --apply --keep-specs -- {_RELATION_TARGET}"
    if operation == "update" or seed_policy == "preserve-only":
        return f"spec-dock update -- {_RELATION_TARGET}"
    return f"spec-dock init --force -- {_RELATION_TARGET}"


def _relation_retry(row: dict[str, object], operation: str | None, seed_policy: str | None) -> str | None:
    token = row["retry"]
    if token is None:
        return None
    if token == "active.cleanup_retry_command":
        if operation == "uninstall":
            prefix = "spec-dock uninstall --apply --keep-specs"
        elif operation == "update" or seed_policy == "preserve-only":
            prefix = "spec-dock update"
        else:
            prefix = "spec-dock init --force"
        return f"{prefix} --provider-cleanup-token {_RELATION_CLEANUP_TOKEN} -- {_RELATION_TARGET}"
    prefixes = {
        "install/create-if-absent retry": "spec-dock init --force -- ",
        "install/preserve-only retry": "spec-dock update -- ",
        "update retry": "spec-dock update -- ",
        "uninstall retry": "spec-dock uninstall --apply --keep-specs -- ",
    }
    try:
        return prefixes[cast("str", token)] + _RELATION_TARGET
    except KeyError as error:
        raise AssertionError(f"unhandled retry token: {token}") from error


def _relation_continuation(
    row: dict[str, object], retry_command: str | None, operation: str | None, seed_policy: str | None
) -> dict[str, str | None]:
    profile = str(row["continuation"])
    none = {
        "next_action": "none",
        "next_command": None,
        "after_cleanup_action": "none",
        "after_cleanup_command": None,
    }
    if profile in {"NONE", "CLEANUP-REPLAY-NONE"}:
        return none
    if profile == "LIFECYCLE-RETRY":
        return {
            "next_action": "run-request",
            "next_command": retry_command,
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        }
    if profile == "CLEANUP-WARNING":
        return {
            "next_action": "retry-cleanup",
            "next_command": retry_command,
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        }
    if profile == "CLEANUP-FAILED-DEFERRED":
        return {
            "next_action": "retry-cleanup",
            "next_command": retry_command,
            "after_cleanup_action": "run-request",
            "after_cleanup_command": _relation_desired_command(row, operation, seed_policy),
        }
    if profile == "CLEANUP-COMPLETED-DEFERRED":
        return {
            "next_action": "run-request",
            "next_command": _relation_desired_command(row, operation, seed_policy),
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        }
    if profile in {"CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED", "CLEANUP-FAILED-BY-ROLE-AND-DEFERRED"}:
        if retry_command is None:
            return none
        failed = profile.startswith("CLEANUP-FAILED")
        return {
            "next_action": "retry-cleanup" if failed else "run-request",
            "next_command": retry_command,
            "after_cleanup_action": "run-request",
            "after_cleanup_command": _relation_desired_command(row, operation, seed_policy),
        }
    if profile == "CLEANUP-REPLAY-DEFERRED":
        return {
            "next_action": "run-request",
            "next_command": _relation_desired_command(row, operation, seed_policy),
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        }
    raise AssertionError(f"unhandled continuation profile: {profile}")


def _relation_action(path: str, category: str, status: str, reason: str) -> dict[str, str]:
    return {"path": path, "category": category, "status": status, "reason": reason}


def _relation_install_terminal(seed_policy: str, *, warning: bool = False) -> list[dict[str, str]]:
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action("spec-dock/spec-dock.version", "record", "completed", "terminal-record-publish"),
    ]
    for path, category in zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True):
        actions.append(_relation_action(path, category, "completed", f"candidate-{category}-create"))
    seed_reason = "preserve-only-seed" if seed_policy == "preserve-only" else "fresh-seed-create"
    seed_status = "preserved" if seed_policy == "preserve-only" else "completed"
    actions.extend(_relation_action(path, "seed", seed_status, seed_reason) for path in _RELATION_PATHS[8:10])
    actions.append(
        _relation_action(
            "@provider-stage",
            "stage",
            "warning" if warning else "completed",
            "candidate-stage-cleanup-warning" if warning else "candidate-stage-cleanup",
        )
    )
    return actions


def _relation_uninstall(profile: str) -> list[dict[str, str]]:
    if profile == "AP-U-ABSENT":
        return [
            _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
            _relation_action("spec-dock/spec-dock.version", "record", "preserved", "terminal-record-current"),
            _relation_action("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
            _relation_action(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        ]
    planned = profile.endswith("-PLAN")
    warning = profile.endswith("-WARN")
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action(
            "spec-dock/spec-dock.version",
            "record",
            "planned" if planned else "completed",
            "terminal-record-publish",
        ),
    ]
    target_status = "planned" if planned else "completed"
    actions.extend(
        _relation_action(path, category, target_status, f"owned-{category}-remove")
        for path, category in zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True)
    )
    actions.extend(_relation_action(path, "seed", "preserved", "preserve-only-seed") for path in _RELATION_PATHS[8:10])
    if not planned:
        actions.append(
            _relation_action(
                "@provider-stage",
                "stage",
                "warning" if warning else "completed",
                "candidate-stage-cleanup-warning" if warning else "candidate-stage-cleanup",
            )
        )
    return actions


def _relation_preparation(profile: str, operation: str, seed_policy: str) -> list[dict[str, str]]:
    container_status = "completed" if operation == "install" and seed_policy == "create-if-absent" else "preserved"
    container_reason = "fresh-container-create" if container_status == "completed" else "shared-container-preserve"
    actions = [
        _relation_action("spec-dock", "container", container_status, container_reason),
        _relation_action("spec-dock/spec-dock.version", "record", "failed", "incomplete-record-publish"),
    ]
    if operation == "uninstall":
        actions.extend(
            _relation_action(path, category, "preserved", f"owned-{category}-absent")
            for path, category in zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True)
        )
    else:
        actions.extend(
            _relation_action(path, category, "pending", f"candidate-{category}-create")
            for path, category in zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True)
        )
    if seed_policy == "preserve-only" or operation == "uninstall":
        actions.extend(
            _relation_action(path, "seed", "preserved", "preserve-only-seed") for path in _RELATION_PATHS[8:10]
        )
    else:
        actions.extend([
            _relation_action("spec-dock/.gitignore", "seed", "pending", "fresh-seed-create"),
            _relation_action(".github", "container", "pending", "fresh-container-create"),
            _relation_action(".github/workflows", "container", "pending", "fresh-container-create"),
            _relation_action(".github/workflows/ci.yml", "seed", "pending", "fresh-seed-create"),
        ])
    actions.append(_relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"))
    return actions


def _relation_partial(profile: str, operation: str, seed_policy: str) -> list[dict[str, str]]:
    _prefix, phase = profile.split(" at ", 1)
    terminal_record_failure = phase == "publish-terminal-record"
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action(
            "spec-dock/spec-dock.version",
            "record",
            "failed" if terminal_record_failure else "completed",
            "terminal-record-publish" if terminal_record_failure else "incomplete-record-publish",
        ),
    ]
    current_target = {
        "publish-docs": 0,
        "publish-templates": 1,
        "publish-system": 2,
        "publish-scripts": 3,
        "publish-slot-spec-dock": 4,
        "publish-slot-spec-dock-grill-with-docs": 5,
    }.get(phase)
    for index, (path, category) in enumerate(zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True)):
        status = (
            "failed"
            if current_target == index
            else "pending"
            if current_target is not None and index > current_target
            else "completed"
        )
        actions.append(_relation_action(path, category, status, f"candidate-{category}-create"))
    if seed_policy == "preserve-only" or operation == "update":
        actions.extend(
            _relation_action(path, "seed", "preserved", "preserve-only-seed") for path in _RELATION_PATHS[8:10]
        )
    elif phase == "create-seed-spec-dock-gitignore":
        actions.extend([
            _relation_action("spec-dock/.gitignore", "seed", "failed", "fresh-seed-create"),
            _relation_action(".github/workflows/ci.yml", "seed", "pending", "fresh-seed-create"),
        ])
    elif phase == "create-seed-consumer-ci":
        actions.extend([
            _relation_action("spec-dock/.gitignore", "seed", "completed", "fresh-seed-create"),
            _relation_action(".github/workflows/ci.yml", "seed", "failed", "fresh-seed-create"),
        ])
    else:
        actions.extend(
            _relation_action(path, "seed", "completed", "fresh-seed-create") for path in _RELATION_PATHS[8:10]
        )
    actions.append(_relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"))
    return actions


def _relation_exact_uninstall(profile: str, phase: str) -> list[dict[str, str]]:
    terminal_record_failure = phase == "publish-terminal-record"
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action(
            "spec-dock/spec-dock.version",
            "record",
            "failed" if terminal_record_failure else "completed",
            "terminal-record-publish" if terminal_record_failure else "incomplete-record-publish",
        ),
    ]
    current = {
        "detach-docs": 0,
        "detach-templates": 1,
        "detach-system": 2,
        "detach-scripts": 3,
        "detach-slot-spec-dock": 4,
        "detach-slot-spec-dock-grill-with-docs": 5,
    }.get(phase)
    for index, (path, category) in enumerate(zip(_RELATION_PATHS[2:8], _RELATION_CATEGORIES[2:8], strict=True)):
        status = "failed" if current == index else "pending" if current is not None and index > current else "completed"
        actions.append(_relation_action(path, category, status, f"owned-{category}-remove"))
    actions.extend(_relation_action(path, "seed", "preserved", "preserve-only-seed") for path in _RELATION_PATHS[8:10])
    actions.append(_relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"))
    return actions


def _relation_actions(row: dict[str, object], operation: str | None, seed_policy: str | None) -> list[dict[str, str]]:
    profile = str(row["actions"])
    if profile == "empty":
        return []
    if profile == "terminal cleanup completed action set":
        return [_relation_action("@provider-stage", "stage", "completed", "candidate-stage-cleanup")]
    if profile == "terminal cleanup retry-failed action set":
        return [_relation_action("@provider-stage", "stage", "failed", "candidate-stage-cleanup")]
    if profile == "bootstrap cleanup-failed action set":
        return [
            _relation_action("spec-dock", "container", "failed", "fresh-container-create"),
            _relation_action("spec-dock/spec-dock.version", "record", "pending", "incomplete-record-publish"),
            *_relation_preparation("AP-PREP-PARTIAL", "install", cast("str", seed_policy))[2:],
        ]
    if profile.startswith("install-create terminal"):
        return _relation_install_terminal("create-if-absent", warning="+ one stage warning" in profile)
    if profile.startswith("install-preserve terminal"):
        return _relation_install_terminal("preserve-only", warning="+ one stage warning" in profile)
    if profile.startswith("update terminal"):
        return _relation_install_terminal("preserve-only", warning="+ one stage warning" in profile)
    if profile.startswith("AP-U-"):
        return _relation_uninstall(profile)
    if profile == "AP-PREP-PARTIAL":
        assert operation is not None and seed_policy is not None
        return _relation_preparation(profile, operation, seed_policy)
    if profile.startswith("exact ") and "uninstall" in profile:
        assert operation == "uninstall"
        return _relation_exact_uninstall(profile, str(row["phase"]))
    if profile.startswith("exact "):
        assert operation in {"install", "update"} and seed_policy is not None
        return _relation_partial(profile, operation, seed_policy)
    raise AssertionError(f"unhandled action profile: {profile}")


def _relation_guidance(code: str, continuation: dict[str, str | None]) -> list[str]:
    if code == "active-legacy-recovery":
        return [
            "Run the last compatible SpecDock package with the same legacy operation until its recovery markers are cleared.",
            "Do not delete, rename, or convert legacy recovery files manually.",
        ]
    if code in {"install-partial-failure", "update-partial-failure", "uninstall-partial-failure"}:
        return [
            "Run continuation.next_command to resume the exact lifecycle operation.",
            "Do not switch operation, candidate package, or seed policy.",
        ]
    if code.endswith("-completed-with-cleanup-warning"):
        return [
            "Run continuation.next_command to finish owned stage cleanup.",
            "The requested terminal tooling state is already durable.",
        ]
    if code == "terminal-cleanup-failed":
        return (
            [
                "Run continuation.next_command to retry owned stage cleanup.",
                "After cleanup succeeds, run continuation.after_cleanup_command.",
                "The requested terminal tooling state is already durable.",
            ]
            if continuation["after_cleanup_action"] == "run-request"
            else [
                "Run continuation.next_command to retry owned stage cleanup.",
                "No lifecycle request is pending after cleanup.",
                "The requested terminal tooling state is already durable.",
            ]
        )
    if code == "terminal-cleanup-completed":
        return (
            [
                "Owned provider stage cleanup completed; no lifecycle operation was executed.",
                "Run continuation.next_command to execute the preserved requested operation.",
            ]
            if continuation["next_action"] == "run-request"
            else [
                "Owned provider stage cleanup completed; no lifecycle operation was executed.",
                "No lifecycle operation is pending.",
            ]
        )
    if code == "spec-history-purge-removed":
        return [
            "Use tooling-only uninstall without --remove-specs.",
            "Spec history and Workbench data remain consumer-owned.",
        ]
    return []


def _relation_witness(row: dict[str, object]) -> dict[str, object]:
    operation = _relation_operation(row)
    seed_policy = _relation_seed_policy(row, operation)
    retry_command = _relation_retry(row, operation, seed_policy)
    continuation = _relation_continuation(row, retry_command, operation, seed_policy)
    actions = _relation_actions(row, operation, seed_policy)
    summary = {
        key: sum(action["status"] == key for action in actions)
        for key in ("planned", "completed", "preserved", "pending", "failed", "warnings")
    }
    code = cast("str", row["code"])
    status = cast("str", row["status"])
    warning = [_RELATION_WARNING] if code.endswith("-completed-with-cleanup-warning") else []
    error = (
        [_RELATION_ERROR_TEXT[code]]
        if code in _RELATION_ERROR_TEXT and status in {"blocked", "partial_failure", "error"}
        else []
    )
    return {
        "schema_version": 1,
        "target": _RELATION_TARGET,
        "mode": row["mode"],
        "apply": row["apply"],
        "specs_mode": _relation_specs_mode(row),
        "status": status,
        "code": code,
        "operation": operation,
        "candidate_digest": _relation_digest(row["candidate_digest"]),
        "seed_policy": seed_policy,
        "mutation_started": row["mutation_started"],
        "bootstrap_rolled_back": row["bootstrap_rolled_back"],
        "phase": row["phase"],
        "last_completed_phase": row["last_completed_phase"],
        "retry_command": retry_command,
        "continuation": continuation,
        "failed_paths": [action["path"] for action in actions if action["status"] == "failed"],
        "pending_paths": [action["path"] for action in actions if action["status"] == "pending"],
        "summary": summary,
        "actions": actions,
        "guidance": _relation_guidance(code, continuation),
        "warnings": warning,
        "errors": error,
    }


def _first_red_install_preserve_partial_result() -> dict[str, object]:
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
        _relation_action("spec-dock/docs", "root", "completed", "candidate-root-create"),
        _relation_action("spec-dock/templates", "root", "completed", "candidate-root-create"),
        _relation_action("spec-dock/system", "root", "failed", "candidate-root-create"),
        _relation_action("spec-dock/scripts", "root", "pending", "candidate-root-create"),
        _relation_action(".agents/skills/spec-dock", "slot", "pending", "candidate-slot-create"),
        _relation_action(".agents/skills/spec-dock-grill-with-docs", "slot", "pending", "candidate-slot-create"),
        _relation_action("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
        _relation_action(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        _relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    ]
    return _first_red_partial_result(
        operation="install",
        seed_policy="preserve-only",
        phase="publish-system",
        last_completed_phase="publish-templates",
        retry_command="spec-dock update -- " + _RELATION_TARGET,
        actions=actions,
    )


def _first_red_uninstall_partial_result() -> dict[str, object]:
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
        _relation_action("spec-dock/docs", "root", "completed", "owned-root-remove"),
        _relation_action("spec-dock/templates", "root", "completed", "owned-root-remove"),
        _relation_action("spec-dock/system", "root", "failed", "owned-root-remove"),
        _relation_action("spec-dock/scripts", "root", "pending", "owned-root-remove"),
        _relation_action(".agents/skills/spec-dock", "slot", "pending", "owned-slot-remove"),
        _relation_action(".agents/skills/spec-dock-grill-with-docs", "slot", "pending", "owned-slot-remove"),
        _relation_action("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
        _relation_action(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        _relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    ]
    return _first_red_partial_result(
        operation="uninstall",
        seed_policy="preserve-only",
        phase="detach-system",
        last_completed_phase="detach-templates",
        retry_command="spec-dock uninstall --apply --keep-specs -- " + _RELATION_TARGET,
        actions=actions,
    )


def _first_red_install_create_seed_partial_result() -> dict[str, object]:
    actions = [
        _relation_action("spec-dock", "container", "preserved", "shared-container-preserve"),
        _relation_action("spec-dock/spec-dock.version", "record", "completed", "incomplete-record-publish"),
        _relation_action("spec-dock/docs", "root", "completed", "candidate-root-create"),
        _relation_action("spec-dock/templates", "root", "completed", "candidate-root-create"),
        _relation_action("spec-dock/system", "root", "completed", "candidate-root-create"),
        _relation_action("spec-dock/scripts", "root", "completed", "candidate-root-create"),
        _relation_action(".agents/skills/spec-dock", "slot", "completed", "candidate-slot-create"),
        _relation_action(".agents/skills/spec-dock-grill-with-docs", "slot", "completed", "candidate-slot-create"),
        _relation_action("spec-dock/.gitignore", "seed", "failed", "fresh-seed-create"),
        _relation_action(".github/workflows/ci.yml", "seed", "pending", "fresh-seed-create"),
        _relation_action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"),
    ]
    return _first_red_partial_result(
        operation="install",
        seed_policy="create-if-absent",
        phase="create-seed-spec-dock-gitignore",
        last_completed_phase="publish-slot-spec-dock-grill-with-docs",
        retry_command="spec-dock init --force -- " + _RELATION_TARGET,
        actions=actions,
    )


def _first_red_partial_result(
    *,
    operation: str,
    seed_policy: str,
    phase: str,
    last_completed_phase: str,
    retry_command: str,
    actions: list[dict[str, str]],
) -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": 1,
        "target": _RELATION_TARGET,
        "mode": "apply",
        "apply": True,
        "specs_mode": None,
        "status": "partial_failure",
        "code": f"{operation}-partial-failure",
        "operation": operation,
        "candidate_digest": _RELATION_DIGEST,
        "seed_policy": seed_policy,
        "mutation_started": True,
        "bootstrap_rolled_back": False,
        "phase": phase,
        "last_completed_phase": last_completed_phase,
        "retry_command": retry_command,
        "continuation": {
            "next_action": "run-request",
            "next_command": retry_command,
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        },
        "failed_paths": [],
        "pending_paths": [],
        "summary": {},
        "actions": actions,
        "guidance": [
            "Run continuation.next_command to resume the exact lifecycle operation.",
            "Do not switch operation, candidate package, or seed policy.",
        ],
        "warnings": [],
        "errors": [_RELATION_ERROR_TEXT[f"{operation}-partial-failure"]],
    }
    _refresh_first_red_derived_fields(result)
    return result


def _refresh_first_red_derived_fields(result: dict[str, object]) -> None:
    actions = cast("list[dict[str, str]]", result["actions"])
    result["failed_paths"] = [action["path"] for action in actions if action["status"] == "failed"]
    result["pending_paths"] = [action["path"] for action in actions if action["status"] == "pending"]
    result["summary"] = {
        status: sum(action["status"] == status for action in actions)
        for status in ("planned", "completed", "preserved", "pending", "failed", "warnings")
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "record-reason",
        "record-status",
        "prior-pending",
        "multiple-failed",
        "current-completed",
        "later-completed",
        "stage-completed",
        "seed-pending",
    ],
)
def test_t01_partial_action_profile_rejects_every_unlisted_vector(mutation: str) -> None:
    if mutation in {"record-status"}:
        result = _first_red_uninstall_partial_result()
    elif mutation == "seed-pending":
        result = _first_red_install_create_seed_partial_result()
    else:
        result = _first_red_install_preserve_partial_result()
    actions = cast("list[dict[str, str]]", result["actions"])

    if mutation == "record-reason":
        actions[1]["reason"] = "terminal-record-publish"
    elif mutation == "record-status":
        actions[1]["status"] = "pending"
    elif mutation == "prior-pending":
        actions[2]["status"] = "pending"
    elif mutation == "multiple-failed":
        actions[3]["status"] = "failed"
    elif mutation == "current-completed":
        actions[4]["status"] = "completed"
    elif mutation == "later-completed":
        actions[5]["status"] = "completed"
    elif mutation == "stage-completed":
        actions[-1]["status"] = "completed"
    elif mutation == "seed-pending":
        actions[8]["status"] = "pending"
    else:
        raise AssertionError(f"unhandled mutation: {mutation}")
    _refresh_first_red_derived_fields(result)

    with pytest.raises(WireValidationError):
        validate_public_result(result)


@pytest.mark.parametrize(
    "row",
    _wire_generated.RELATION_ROWS,
    ids=lambda row: f"{row['code']}::{row['variant']}",
)
def test_t01_every_wire_relation_has_an_accepted_and_rejected_table_driven_witness(
    row: dict[str, object],
) -> None:
    witness = _relation_witness(row)
    validate_public_result(witness)

    rejected = dict(witness)
    rejected["phase"] = "preflight" if witness["phase"] != "preflight" else "complete"
    with pytest.raises(WireValidationError):
        validate_public_result(rejected)


def test_t01_wire_v12_inventory_and_generated_projection_are_exact() -> None:
    assert len(_wire_generated.PUBLIC_STATUS_VALUES) == 6
    assert len(_wire_generated.PUBLIC_CODE_VALUES) == 41
    assert len(_wire_generated.PHASE_VALUES) == 23
    assert len(_wire_generated.LAST_COMPLETED_PHASE_VALUES) == 24
    assert len(_wire_generated.RELATION_ROWS) == 168
    assert len(_wire_generated.PUBLIC_JSON_GOLDENS) == 40
    assert len(_wire_generated.RECORD_GOLDENS) == 4

    for golden in _wire_generated.PUBLIC_JSON_GOLDENS:
        validate_public_result(golden)
    for golden in _wire_generated.RECORD_GOLDENS:
        record = parse_installation_record(json.dumps(golden, ensure_ascii=False, separators=(",", ":")) + "\n")
        assert (
            serialize_installation_record(record)
            == json.dumps(golden, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
        )


def test_t01_record_and_slot_marker_parsers_reject_noncanonical_or_unknown_bytes() -> None:
    record = _wire_generated.RECORD_GOLDENS[0]
    canonical = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    assert parse_installation_record(canonical).candidate_digest == "d" * 64
    with pytest.raises(WireValidationError):
        parse_installation_record(canonical + b"\n")
    with pytest.raises(WireValidationError):
        parse_installation_record(canonical.replace(b'"state":"ready"', b'"extra":0,"state":"ready"'))

    marker = {
        "schema_version": 1,
        "slot": ".agents/skills/spec-dock",
        "version": "0.2.4",
        "candidate_digest": "d" * 64,
    }
    marker_bytes = json.dumps(marker, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    assert parse_slot_marker(marker_bytes).slot == marker["slot"]
    assert serialize_slot_marker(parse_slot_marker(marker_bytes)) == marker_bytes


def test_t01_build_public_result_preserves_the_closed_golden_byte_shape() -> None:
    golden = cast("dict[str, Any]", _wire_generated.PUBLIC_JSON_GOLDENS[0])
    request = LifecycleRequest(
        target=golden["target"],
        mode=golden["mode"],
        apply=golden["apply"],
        specs_mode=golden["specs_mode"],
        operation=golden["operation"],
        candidate_digest=golden["candidate_digest"],
        seed_policy=golden["seed_policy"],
    )
    result = build_public_result(
        request,
        status=golden["status"],
        code=golden["code"],
        phase=golden["phase"],
        last_completed_phase=golden["last_completed_phase"],
        mutation_started=golden["mutation_started"],
        bootstrap_rolled_back=golden["bootstrap_rolled_back"],
        retry_command=golden["retry_command"],
        continuation=golden["continuation"],
        failed_paths=golden["failed_paths"],
        pending_paths=golden["pending_paths"],
        summary=golden["summary"],
        actions=golden["actions"],
        guidance=golden["guidance"],
        warnings=golden["warnings"],
        errors=golden["errors"],
    )
    validate_public_result(result)
