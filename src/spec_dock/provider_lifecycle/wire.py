"""Strict serializers and validators for the closed Wire v12 surface."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import re
import shlex
from typing import NoReturn, cast

from spec_dock.provider_lifecycle import _wire_generated as wire
from spec_dock.provider_lifecycle.contracts import (
    InstallationRecord,
    LifecycleAction,
    LifecycleRequest,
    LifecycleResult,
    Operation,
    RecordState,
    SeedPolicy,
    SkillSlotMarker,
)


class WireValidationError(ValueError):
    """The supplied value is outside the finite lifecycle wire contract."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SLOT_NAMES = ("spec-dock", "spec-dock-grill-with-docs")
_SLOT_PATHS = (
    ".agents/skills/spec-dock",
    ".agents/skills/spec-dock-grill-with-docs",
)
_RESULT_KEYS = (
    "schema_version",
    "target",
    "mode",
    "apply",
    "specs_mode",
    "status",
    "code",
    "operation",
    "candidate_digest",
    "seed_policy",
    "mutation_started",
    "bootstrap_rolled_back",
    "phase",
    "last_completed_phase",
    "retry_command",
    "continuation",
    "failed_paths",
    "pending_paths",
    "summary",
    "actions",
    "guidance",
    "warnings",
    "errors",
)
_CONTINUATION_KEYS = (
    "next_action",
    "next_command",
    "after_cleanup_action",
    "after_cleanup_command",
)
_SUMMARY_KEYS = ("planned", "completed", "preserved", "pending", "failed", "warnings")
_ACTION_KEYS = ("path", "category", "status", "reason")
_PUBLIC_PATH_RANK = {path: index for index, path in enumerate(wire.TARGET_PATH_ORDER)}
_ACTION_STATUS_VALUES = ("planned", "completed", "preserved", "pending", "failed", "warning")
_CONTINUATION_NEXT_VALUES = ("none", "retry-cleanup", "run-request")
_CONTINUATION_AFTER_VALUES = ("none", "run-request")
_ACTION_RULES = {
    ("container", "fresh-container-create"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", "create-if-absent"), ("install", "preserve-only")}),
    ),
    ("container", "shared-container-preserve"): (
        frozenset({"preserved"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("record", "incomplete-record-publish"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("record", "terminal-record-publish"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("record", "terminal-record-current"): (
        frozenset({"preserved"}),
        frozenset({("uninstall", None)}),
    ),
    ("root", "candidate-root-create"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("root", "candidate-root-replace"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("root", "candidate-root-current"): (
        frozenset({"preserved"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("root", "owned-root-remove"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("uninstall", None)}),
    ),
    ("root", "owned-root-absent"): (
        frozenset({"preserved"}),
        frozenset({("uninstall", None)}),
    ),
    ("slot", "candidate-slot-create"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("slot", "candidate-slot-replace"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("slot", "candidate-slot-current"): (
        frozenset({"preserved"}),
        frozenset({("install", None), ("update", None)}),
    ),
    ("slot", "owned-slot-remove"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("uninstall", None)}),
    ),
    ("slot", "owned-slot-absent"): (
        frozenset({"preserved"}),
        frozenset({("uninstall", None)}),
    ),
    ("seed", "fresh-seed-create"): (
        frozenset({"planned", "completed", "pending", "failed"}),
        frozenset({("install", "create-if-absent")}),
    ),
    ("seed", "consumer-seed-present"): (
        frozenset({"preserved"}),
        frozenset({("install", "create-if-absent")}),
    ),
    ("seed", "preserve-only-seed"): (
        frozenset({"preserved"}),
        frozenset({("install", "preserve-only"), ("update", "preserve-only"), ("uninstall", "preserve-only")}),
    ),
    ("stage", "candidate-stage-create"): (
        frozenset({"completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("stage", "candidate-stage-reuse"): (
        frozenset({"preserved"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("stage", "candidate-stage-cleanup"): (
        frozenset({"completed", "pending", "failed"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("stage", "candidate-stage-cleanup-warning"): (
        frozenset({"warning"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
    ("preservation", "consumer-data-preserve"): (
        frozenset({"preserved"}),
        frozenset({("install", None), ("update", None), ("uninstall", None)}),
    ),
}
_ERRORS = {
    "lifecycle-preparation-failed": "Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly.",
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
}
_CLEANUP_WARNING = (
    "Provider tooling reached the requested terminal state, but the owned external stage could not be removed."
)
_LIFECYCLE_GUIDANCE = (
    "Run continuation.next_command to resume the exact lifecycle operation.",
    "Do not switch operation, candidate package, or seed policy.",
)
_PREPARATION_GUIDANCE: tuple[str, ...] = ()
_ACTIVE_LEGACY_GUIDANCE = (
    "Run the last compatible SpecDock package with the same legacy operation until its recovery markers are cleared.",
    "Do not delete, rename, or convert legacy recovery files manually.",
)
_LIFECYCLE_PARTIAL_GUIDANCE = _LIFECYCLE_GUIDANCE
_CLEANUP_WARNING_GUIDANCE = (
    "Run continuation.next_command to finish owned stage cleanup.",
    "The requested terminal tooling state is already durable.",
)
_CLEANUP_FAILED_DEFERRED_GUIDANCE = (
    "Run continuation.next_command to retry owned stage cleanup.",
    "After cleanup succeeds, run continuation.after_cleanup_command.",
    "The requested terminal tooling state is already durable.",
)
_CLEANUP_FAILED_NONE_GUIDANCE = (
    "Run continuation.next_command to retry owned stage cleanup.",
    "No lifecycle request is pending after cleanup.",
    "The requested terminal tooling state is already durable.",
)
_CLEANUP_COMPLETED_DEFERRED_GUIDANCE = (
    "Owned provider stage cleanup completed; no lifecycle operation was executed.",
    "Run continuation.next_command to execute the preserved requested operation.",
)
_CLEANUP_COMPLETED_NONE_GUIDANCE = (
    "Owned provider stage cleanup completed; no lifecycle operation was executed.",
    "No lifecycle operation is pending.",
)
_PURGE_GUIDANCE = (
    "Use tooling-only uninstall without --remove-specs.",
    "Spec history and Workbench data remain consumer-owned.",
)


def _fail(message: str) -> NoReturn:
    raise WireValidationError(message)


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail(f"{label} must be an object")
    return cast("Mapping[str, object]", value)


def _exact_keys(value: Mapping[str, object], expected: Sequence[str], label: str) -> None:
    if tuple(value.keys()) != tuple(expected):
        _fail(f"{label} keys must be exactly {tuple(expected)!r}")


def _text(value: object, label: str, *, allow_null: bool = False) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or "\x00" in value:
        _fail(f"{label} must be a NUL-free string")
    return cast("str", value)


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        _fail(f"{label} must be a boolean")
    return cast("bool", value)


def _integer(value: object, label: str, *, nonnegative: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(f"{label} must be an integer")
    if nonnegative and value < 0:
        _fail(f"{label} must be non-negative")
    return cast("int", value)


def _digest(value: object, label: str, *, allow_null: bool = False) -> str | None:
    value = _text(value, label, allow_null=allow_null)
    if value is None:
        return None
    if _DIGEST.fullmatch(value) is None:
        _fail(f"{label} must be a lowercase SHA-256 digest")
    return value


def _decode_json(payload: bytes | bytearray | memoryview | str, maximum: int, label: str) -> Mapping[str, object]:
    if isinstance(payload, str):
        raw = payload.encode("utf-8")
    elif isinstance(payload, (bytes, bytearray, memoryview)):
        raw = bytes(payload)
    else:
        _fail(f"{label} payload must be bytes or string")
    if len(raw) > maximum:
        _fail(f"{label} exceeds {maximum} bytes")
    if not raw.endswith(b"\n") or raw[:-1].find(b"\n") >= 0:
        _fail(f"{label} must have exactly one terminal LF")
    try:
        decoded = raw[:-1].decode("utf-8")
    except UnicodeDecodeError as exc:
        _fail(f"{label} is not UTF-8: {exc}")

    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                _fail(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            decoded,
            object_pairs_hook=reject_duplicate,
            parse_constant=lambda constant: _fail(f"{label} contains {constant}"),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        if isinstance(exc, WireValidationError):
            raise
        _fail(f"{label} is not valid JSON: {exc}")
    obj = _mapping(value, label)
    canonical = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
    if canonical != raw:
        _fail(f"{label} must use canonical compact JSON")
    return obj


def _canonical(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


def _record_mapping(record: InstallationRecord) -> dict[str, object]:
    if not isinstance(record, InstallationRecord):
        _fail("installation record must be InstallationRecord")
    slots = _mapping(record.skill_slots, "skill_slots")
    _exact_keys(slots, _SLOT_NAMES, "skill_slots")
    return {
        "schema_version": record.schema_version,
        "state": record.state,
        "operation": record.operation,
        "version": record.version,
        "candidate_digest": record.candidate_digest,
        "seed_policy": record.seed_policy,
        "skill_slots": dict(slots),
    }


def _validate_record_mapping(value: Mapping[str, object]) -> InstallationRecord:
    _exact_keys(
        value,
        ("schema_version", "state", "operation", "version", "candidate_digest", "seed_policy", "skill_slots"),
        "installation record",
    )
    if _integer(value["schema_version"], "schema_version") != 1:
        _fail("installation record schema_version must be 1")
    state = _text(value["state"], "state")
    if state not in ("incomplete", "ready", "tooling-absent-preserved-data"):
        _fail("invalid installation record state")
    assert state is not None
    operation = _text(value["operation"], "operation", allow_null=True)
    if operation is not None and operation not in ("install", "update", "uninstall"):
        _fail("invalid installation record operation")
    version = _text(value["version"], "version")
    if version != "0.2.4":
        _fail("installation record version must be 0.2.4")
    assert version is not None
    digest = _digest(value["candidate_digest"], "candidate_digest")
    assert digest is not None
    seed_policy = _text(value["seed_policy"], "seed_policy")
    if seed_policy not in ("create-if-absent", "preserve-only"):
        _fail("invalid installation record seed_policy")
    assert seed_policy is not None
    slots = _mapping(value["skill_slots"], "skill_slots")
    _exact_keys(slots, _SLOT_NAMES, "skill_slots")
    normalized_slots: dict[str, str] = {}
    for slot in _SLOT_NAMES:
        slot_version = _text(slots[slot], f"skill_slots.{slot}")
        if slot_version != "0.2.4":
            _fail("skill slot version must be 0.2.4")
        assert slot_version is not None
        normalized_slots[slot] = slot_version
    if state == "incomplete":
        if operation is None:
            _fail("incomplete installation record requires operation")
        if operation in ("update", "uninstall") and seed_policy != "preserve-only":
            _fail("incomplete update or uninstall record requires preserve-only seed_policy")
    elif state == "tooling-absent-preserved-data":
        if operation is not None or seed_policy != "preserve-only":
            _fail("tooling-absent-preserved-data record requires null operation and preserve-only seed_policy")
    elif operation is not None:
        _fail("terminal installation record requires null operation")
    return InstallationRecord(
        1,
        cast("RecordState", state),
        cast("Operation | None", operation),
        version,
        digest,
        cast("SeedPolicy", seed_policy),
        normalized_slots,
    )


def parse_installation_record(payload: bytes | bytearray | memoryview | str) -> InstallationRecord:
    """Parse one exact public installation record."""

    return _validate_record_mapping(_decode_json(payload, 4096, "installation record"))


def serialize_installation_record(record: InstallationRecord) -> bytes:
    """Serialize an installation record with the normative key order."""

    value = _record_mapping(record)
    _validate_record_mapping(value)
    return _canonical(value)


def _marker_mapping(marker: SkillSlotMarker) -> dict[str, object]:
    if not isinstance(marker, SkillSlotMarker):
        _fail("slot marker must be SkillSlotMarker")
    return {
        "schema_version": marker.schema_version,
        "slot": marker.slot,
        "version": marker.version,
        "candidate_digest": marker.candidate_digest,
    }


def _validate_marker_mapping(value: Mapping[str, object]) -> SkillSlotMarker:
    _exact_keys(value, ("schema_version", "slot", "version", "candidate_digest"), "slot marker")
    if _integer(value["schema_version"], "schema_version") != 1:
        _fail("slot marker schema_version must be 1")
    slot = _text(value["slot"], "slot")
    if slot not in _SLOT_PATHS:
        _fail("slot marker slot is not a fixed public slot")
    assert slot is not None
    version = _text(value["version"], "version")
    if version != "0.2.4":
        _fail("slot marker version must be 0.2.4")
    assert version is not None
    digest = _digest(value["candidate_digest"], "candidate_digest")
    assert digest is not None
    return SkillSlotMarker(1, slot, version, digest)


def parse_slot_marker(payload: bytes | bytearray | memoryview | str) -> SkillSlotMarker:
    """Parse one exact provider slot marker."""

    return _validate_marker_mapping(_decode_json(payload, 2048, "slot marker"))


def serialize_slot_marker(marker: SkillSlotMarker) -> bytes:
    """Serialize one exact provider slot marker."""

    value = _marker_mapping(marker)
    _validate_marker_mapping(value)
    return _canonical(value)


def _action_mapping(action: LifecycleAction | Mapping[str, object]) -> dict[str, str]:
    if isinstance(action, LifecycleAction):
        value: Mapping[str, object] = {
            "path": action.path,
            "category": action.category,
            "status": action.status,
            "reason": action.reason,
        }
    else:
        value = _mapping(action, "action")
    _exact_keys(value, _ACTION_KEYS, "action")
    normalized = {key: _text(value[key], f"action.{key}") for key in _ACTION_KEYS}
    if any(item is None for item in normalized.values()):
        _fail("action fields cannot be null")
    path = normalized["path"]
    category = normalized["category"]
    status = normalized["status"]
    reason = normalized["reason"]
    assert path is not None and category is not None and status is not None and reason is not None
    if path not in _PUBLIC_PATH_RANK:
        _fail(f"action path is not in TARGET_PATH_ORDER: {path}")
    if status not in _ACTION_STATUS_VALUES:
        _fail("invalid action status")
    rule = _ACTION_RULES.get((category, reason))
    if rule is None:
        _fail("action category/reason is outside the finite action wire")
    if status not in rule[0]:
        _fail("action status is not allowed for this category/reason")
    return {key: value for key, value in normalized.items() if value is not None}


def _continuation(value: Mapping[str, object]) -> dict[str, str | None]:
    _exact_keys(value, _CONTINUATION_KEYS, "continuation")
    next_action = _text(value["next_action"], "continuation.next_action")
    after_action = _text(value["after_cleanup_action"], "continuation.after_cleanup_action")
    next_command = _text(value["next_command"], "continuation.next_command", allow_null=True)
    after_command = _text(value["after_cleanup_command"], "continuation.after_cleanup_command", allow_null=True)
    if next_action not in _CONTINUATION_NEXT_VALUES or after_action not in _CONTINUATION_AFTER_VALUES:
        _fail("invalid continuation action")
    if (next_action == "none") != (next_command is None):
        _fail("continuation next action/command mismatch")
    if (after_action == "none") != (after_command is None):
        _fail("continuation after-cleanup action/command mismatch")
    return {
        "next_action": next_action,
        "next_command": next_command,
        "after_cleanup_action": after_action,
        "after_cleanup_command": after_command,
    }


def _string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or "\x00" in item for item in value):
        _fail(f"{label} must be an array of strings")
    return cast("list[str]", value)


def _validate_action_context(
    actions: Sequence[Mapping[str, str]], operation: str | None, seed_policy: str | None
) -> None:
    if not actions:
        return
    if operation is None:
        _fail("actions require a concrete operation")
    for action in actions:
        rule = _ACTION_RULES[action["category"], action["reason"]]
        contexts = rule[1]
        if not any(
            allowed_operation == operation and (allowed_policy is None or allowed_policy == seed_policy)
            for allowed_operation, allowed_policy in contexts
        ):
            _fail("action operation or seed policy is outside the finite action wire")


def _summary(value: Mapping[str, object], actions: Sequence[Mapping[str, str]]) -> dict[str, int]:
    _exact_keys(value, _SUMMARY_KEYS, "summary")
    expected = dict.fromkeys(_SUMMARY_KEYS, 0)
    for action in actions:
        status = action["status"]
        if status in expected:
            expected[status] += 1
    result: dict[str, int] = {}
    for key in _SUMMARY_KEYS:
        result[key] = _integer(value[key], f"summary.{key}", nonnegative=True)
        if result[key] != expected[key]:
            _fail(f"summary.{key} does not match action statuses")
    return result


def _relation_accepts(value: object, token: str | None) -> bool:
    if token is None:
        return value is None
    if token in {"null", "None"}:
        return value is None
    if "=" in token:
        expression, expected = token.split("=", 1)
        if expression not in {
            "record.seed_policy",
            "record.operation",
        }:
            return False
        return value == expected
    if token in {
        "request.candidate_digest",
        "record.candidate_digest",
        "record.seed_policy",
        "record.operation",
        "legacy_fixture.aggregate_digest",
        "owned_target_digest",
        "active.operation",
        "active.candidate_digest",
        "active.seed_policy",
        "receipt.operation",
        "receipt.candidate_digest",
        "receipt.seed_policy",
    }:
        return value is not None
    return value == token


def _render_retry(target: str, token: str) -> str | None:
    quoted_target = shlex.join([target])
    if token == "install/create-if-absent retry":
        return f"spec-dock init --force -- {quoted_target}"
    if token == "install/preserve-only retry":
        return f"spec-dock update -- {quoted_target}"
    if token == "update retry":
        return f"spec-dock update -- {quoted_target}"
    if token == "uninstall retry":
        return f"spec-dock uninstall --apply --keep-specs -- {quoted_target}"
    return None


def _active_retry_matches(value: str | None, target: str, operation: str | None, seed_policy: str | None) -> bool:
    if operation == "install":
        if seed_policy == "create-if-absent":
            prefix = "spec-dock init --force"
        elif seed_policy == "preserve-only":
            prefix = "spec-dock update"
        else:
            return False
    elif operation == "update":
        prefix = "spec-dock update"
    elif operation == "uninstall":
        prefix = "spec-dock uninstall --apply --keep-specs"
    else:
        return False
    expected_target = shlex.join([target])
    if value is None:
        return False
    pattern = rf"{re.escape(prefix)} --provider-cleanup-token [0-9a-f]{{64}} -- {re.escape(expected_target)}"
    return re.fullmatch(pattern, value) is not None


def _retry_matches(
    value: str | None, token: str | None, target: str, operation: str | None, seed_policy: str | None
) -> bool:
    if token is None:
        return value is None
    if token == "active.cleanup_retry_command":
        return _active_retry_matches(value, target, operation, seed_policy)
    expected = _render_retry(target, token)
    return expected is not None and value == expected


def _continuation_matches(value: Mapping[str, str | None], profile: str, retry_command: str | None) -> bool:
    next_action = value["next_action"]
    next_command = value["next_command"]
    after_action = value["after_cleanup_action"]
    after_command = value["after_cleanup_command"]
    if profile in {"NONE", "CLEANUP-COMPLETED-NONE", "CLEANUP-REPLAY-NONE"}:
        return (next_action, next_command, after_action, after_command) == ("none", None, "none", None)
    if profile in {"LIFECYCLE-RETRY", "CLEANUP-FAILED-NONE"}:
        return (next_action, next_command, after_action, after_command) == (
            "run-request" if profile == "LIFECYCLE-RETRY" else "retry-cleanup",
            retry_command,
            "none",
            None,
        )
    if profile == "CLEANUP-WARNING":
        return (next_action, next_command, after_action, after_command) == (
            "retry-cleanup",
            retry_command,
            "none",
            None,
        )
    if profile == "CLEANUP-FAILED-DEFERRED":
        return (
            next_action == "retry-cleanup"
            and next_command == retry_command
            and after_action == "run-request"
            and after_command is not None
        )
    if profile in {"CLEANUP-COMPLETED-DEFERRED", "CLEANUP-REPLAY-DEFERRED"}:
        return (
            next_action == "run-request"
            and next_command is not None
            and after_action == "none"
            and after_command is None
        )
    if profile in {"CLEANUP-FAILED-BY-ROLE-AND-DEFERRED", "CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED"}:
        if after_action == "run-request":
            return (
                after_command is not None
                and next_action == ("retry-cleanup" if profile.startswith("CLEANUP-FAILED") else "run-request")
                and next_command == retry_command
            )
        return (next_action, next_command, after_action, after_command) == (
            "retry-cleanup" if profile.startswith("CLEANUP-FAILED") else "none",
            retry_command if profile.startswith("CLEANUP-FAILED") else None,
            "none",
            None,
        )
    return False


_LIFECYCLE_ACTION_PATHS = (
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
_UNINSTALL_TARGET_PATHS = _LIFECYCLE_ACTION_PATHS[2:8]
_UNINSTALL_SEED_PATHS = _LIFECYCLE_ACTION_PATHS[8:10]
_INSTALL_TARGET_CATEGORIES = ("root", "root", "root", "root", "slot", "slot")


def _action(
    path: str,
    category: str,
    status: str,
    reason: str,
) -> dict[str, str]:
    return {"path": path, "category": category, "status": status, "reason": reason}


_PARTIAL_TARGET_PHASE_INDEX = {
    "install": {
        "publish-docs": 0,
        "publish-templates": 1,
        "publish-system": 2,
        "publish-scripts": 3,
        "publish-slot-spec-dock": 4,
        "publish-slot-spec-dock-grill-with-docs": 5,
    },
    "update": {
        "publish-docs": 0,
        "publish-templates": 1,
        "publish-system": 2,
        "publish-scripts": 3,
        "publish-slot-spec-dock": 4,
        "publish-slot-spec-dock-grill-with-docs": 5,
    },
    "uninstall": {
        "detach-docs": 0,
        "detach-templates": 1,
        "detach-system": 2,
        "detach-scripts": 3,
        "detach-slot-spec-dock": 4,
        "detach-slot-spec-dock-grill-with-docs": 5,
    },
}
_PARTIAL_SEED_PHASE_INDEX = {
    "create-seed-spec-dock-gitignore": 0,
    "create-seed-consumer-ci": 1,
}


def _partial_action_profile_matches(
    actions: Sequence[Mapping[str, str]],
    *,
    operation: str,
    seed_policy: str,
    phase: str,
) -> bool:
    """Validate one exact partial lifecycle action vector."""

    if operation not in _PARTIAL_TARGET_PHASE_INDEX:
        return False
    if operation == "uninstall" and seed_policy != "preserve-only":
        return False
    if operation == "update" and seed_policy != "preserve-only":
        return False
    if operation == "install" and seed_policy not in {"create-if-absent", "preserve-only"}:
        return False
    if len(actions) != len(_LIFECYCLE_ACTION_PATHS) or [item["path"] for item in actions] != list(
        _LIFECYCLE_ACTION_PATHS
    ):
        return False
    if actions[0] != _action("spec-dock", "container", "preserved", "shared-container-preserve"):
        return False
    if actions[-1] != _action("@provider-stage", "stage", "pending", "candidate-stage-cleanup"):
        return False

    terminal_record_failure = phase == "publish-terminal-record"
    expected_record = _action(
        "spec-dock/spec-dock.version",
        "record",
        "failed" if terminal_record_failure else "completed",
        "terminal-record-publish" if terminal_record_failure else "incomplete-record-publish",
    )
    if actions[1] != expected_record:
        return False

    target_phase_index = _PARTIAL_TARGET_PHASE_INDEX[operation].get(phase)
    if operation == "uninstall":
        for index, (action, path, category) in enumerate(
            zip(actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True)
        ):
            if action["path"] != path or action["category"] != category:
                return False
            absent = action["reason"] == f"owned-{category}-absent"
            present = action["reason"] == f"owned-{category}-remove"
            if not absent and not present:
                return False
            if absent:
                if action["status"] != "preserved":
                    return False
                continue
            if phase == "verify-target":
                if action["status"] not in {"completed", "failed"}:
                    return False
                continue
            if target_phase_index is not None and index == target_phase_index:
                expected_status = "failed"
            elif target_phase_index is not None and index > target_phase_index:
                expected_status = "pending"
            else:
                expected_status = "completed"
            if action["status"] != expected_status:
                return False
        return all(
            action == _action(path, "seed", "preserved", "preserve-only-seed")
            for action, path in zip(actions[8:10], _UNINSTALL_SEED_PATHS, strict=True)
        )

    for index, (action, path, category) in enumerate(
        zip(actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True)
    ):
        if action["path"] != path or action["category"] != category:
            return False
        current = action["reason"] == f"candidate-{category}-current"
        if current:
            if action["status"] != "preserved" or index == target_phase_index:
                return False
            continue
        if action["reason"] not in {f"candidate-{category}-create", f"candidate-{category}-replace"}:
            return False
        if phase == "verify-target":
            if action["status"] not in {"completed", "failed"}:
                return False
            continue
        if target_phase_index is not None and index == target_phase_index:
            expected_status = "failed"
        elif target_phase_index is not None and index > target_phase_index:
            expected_status = "pending"
        else:
            expected_status = "completed"
        if action["status"] != expected_status:
            return False

    if operation == "update" or seed_policy == "preserve-only":
        return all(
            action == _action(path, "seed", "preserved", "preserve-only-seed")
            for action, path in zip(actions[8:10], _UNINSTALL_SEED_PATHS, strict=True)
        )

    seed_phase_index = _PARTIAL_SEED_PHASE_INDEX.get(phase)
    for index, (action, path) in enumerate(zip(actions[8:10], _UNINSTALL_SEED_PATHS, strict=True)):
        if action["path"] != path or action["category"] != "seed":
            return False
        if action["reason"] == "consumer-seed-present":
            if action["status"] != "preserved" or index == seed_phase_index:
                return False
            continue
        if action["reason"] != "fresh-seed-create":
            return False
        if seed_phase_index is None or index < seed_phase_index:
            expected_status = "completed"
        elif index == seed_phase_index:
            expected_status = "failed"
        else:
            expected_status = "pending"
        if action["status"] != expected_status:
            return False
    return True


def _action_profile_matches(
    actions: Sequence[Mapping[str, str]],
    profile: str,
    *,
    operation: str | None,
    seed_policy: str | None,
    phase: str,
) -> bool:
    """Validate the finite action profile named by a generated Wire row."""

    if profile == "empty":
        return not actions
    if profile == "terminal cleanup completed action set":
        return list(actions) == [_action("@provider-stage", "stage", "completed", "candidate-stage-cleanup")]
    if profile == "terminal cleanup retry-failed action set":
        return list(actions) == [_action("@provider-stage", "stage", "failed", "candidate-stage-cleanup")]
    if profile == "bootstrap cleanup-failed action set":
        if operation != "install" or seed_policy not in {"create-if-absent", "preserve-only"}:
            return False
        if not 11 <= len(actions) <= 13:
            return False
        if actions[:2] != [
            _action("spec-dock", "container", "failed", "fresh-container-create"),
            _action("spec-dock/spec-dock.version", "record", "pending", "incomplete-record-publish"),
        ]:
            return False
        for action, path, category in zip(
            actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
        ):
            if action not in (
                _action(path, category, "pending", f"candidate-{category}-create"),
                _action(path, category, "pending", f"candidate-{category}-replace"),
            ):
                return False
        position = 8
        if seed_policy == "preserve-only":
            for path in _UNINSTALL_SEED_PATHS:
                if actions[position] != _action(path, "seed", "preserved", "preserve-only-seed"):
                    return False
                position += 1
        else:
            if actions[position] not in (
                _action("spec-dock/.gitignore", "seed", "pending", "fresh-seed-create"),
                _action("spec-dock/.gitignore", "seed", "preserved", "consumer-seed-present"),
            ):
                return False
            position += 1
            parent_paths = []
            while position < len(actions) and actions[position]["path"] in {".github", ".github/workflows"}:
                parent_paths.append(actions[position]["path"])
                if actions[position] != _action(
                    actions[position]["path"], "container", "pending", "fresh-container-create"
                ):
                    return False
                position += 1
            if parent_paths == [".github"]:
                return False
            if position >= len(actions) or actions[position] not in (
                _action(".github/workflows/ci.yml", "seed", "pending", "fresh-seed-create"),
                _action(".github/workflows/ci.yml", "seed", "preserved", "consumer-seed-present"),
            ):
                return False
            position += 1
        return position + 1 == len(actions) and actions[position] == _action(
            "@provider-stage", "stage", "pending", "candidate-stage-cleanup"
        )
    if profile == "AP-PREP-PARTIAL":
        if operation not in {"install", "update", "uninstall"} or not 11 <= len(actions) <= 13:
            return False
        if [item["path"] for item in actions[:2]] != list(_LIFECYCLE_ACTION_PATHS[:2]):
            return False
        if operation == "uninstall":
            if actions[0] != _action("spec-dock", "container", "preserved", "shared-container-preserve"):
                return False
        elif actions[0] not in (
            _action("spec-dock", "container", "preserved", "shared-container-preserve"),
            _action("spec-dock", "container", "completed", "fresh-container-create"),
        ):
            return False
        if actions[1] != _action("spec-dock/spec-dock.version", "record", "failed", "incomplete-record-publish"):
            return False
        if operation == "uninstall":
            for action, path, category in zip(
                actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
            ):
                if action not in (
                    _action(path, category, "pending", f"owned-{category}-remove"),
                    _action(path, category, "preserved", f"owned-{category}-absent"),
                ):
                    return False
        else:
            for action, path, category in zip(
                actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
            ):
                if action not in (
                    _action(path, category, "pending", f"candidate-{category}-create"),
                    _action(path, category, "pending", f"candidate-{category}-replace"),
                ):
                    return False
        position = 8
        if seed_policy == "preserve-only":
            for path in _UNINSTALL_SEED_PATHS:
                if actions[position] != _action(path, "seed", "preserved", "preserve-only-seed"):
                    return False
                position += 1
        elif operation == "install" and seed_policy == "create-if-absent":
            if actions[position]["path"] != "spec-dock/.gitignore":
                return False
            if actions[position] not in (
                _action("spec-dock/.gitignore", "seed", "pending", "fresh-seed-create"),
                _action("spec-dock/.gitignore", "seed", "preserved", "consumer-seed-present"),
            ):
                return False
            position += 1
            parent_paths = []
            while position < len(actions) and actions[position]["path"] in {".github", ".github/workflows"}:
                parent_paths.append(actions[position]["path"])
                if actions[position] != _action(
                    actions[position]["path"], "container", "pending", "fresh-container-create"
                ):
                    return False
                position += 1
            if parent_paths == [".github"]:
                return False
            if position >= len(actions) or actions[position]["path"] != ".github/workflows/ci.yml":
                return False
            if actions[position] not in (
                _action(".github/workflows/ci.yml", "seed", "pending", "fresh-seed-create"),
                _action(".github/workflows/ci.yml", "seed", "preserved", "consumer-seed-present"),
            ):
                return False
            position += 1
        else:
            return False
        return position + 1 == len(actions) and actions[position] == _action(
            "@provider-stage", "stage", "pending", "candidate-stage-cleanup"
        )
    if profile == "AP-U-ABSENT":
        return list(actions) == [
            _action("spec-dock", "container", "preserved", "shared-container-preserve"),
            _action("spec-dock/spec-dock.version", "record", "preserved", "terminal-record-current"),
            _action("spec-dock/.gitignore", "seed", "preserved", "preserve-only-seed"),
            _action(".github/workflows/ci.yml", "seed", "preserved", "preserve-only-seed"),
        ]
    if profile.startswith("AP-U-"):
        if operation != "uninstall" or seed_policy != "preserve-only":
            return False
        if profile.endswith("-PLAN"):
            expected = [_action("spec-dock", "container", "preserved", "shared-container-preserve")]
            expected.append(_action("spec-dock/spec-dock.version", "record", "planned", "terminal-record-publish"))
            expected.extend(
                _action(path, category, "planned", f"owned-{category}-remove")
                for path, category in zip(_UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True)
            )
            expected.extend(_action(path, "seed", "preserved", "preserve-only-seed") for path in _UNINSTALL_SEED_PATHS)
            if len(actions) != len(expected):
                return False
            if actions[:2] != expected[:2] or actions[8:] != expected[8:]:
                return False
            return all(
                action
                in (
                    _action(path, category, "planned", f"owned-{category}-remove"),
                    _action(path, category, "preserved", f"owned-{category}-absent"),
                )
                for action, path, category in zip(
                    actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
                )
            )
        if profile.endswith("-TERM") or profile.endswith("-WARN"):
            stage_status = "warning" if profile.endswith("-WARN") else "completed"
            expected = [_action("spec-dock", "container", "preserved", "shared-container-preserve")]
            expected.append(_action("spec-dock/spec-dock.version", "record", "completed", "terminal-record-publish"))
            expected_targets = tuple(zip(_UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True))
            expected.extend(
                _action(path, category, "completed", f"owned-{category}-remove") for path, category in expected_targets
            )
            expected.extend(_action(path, "seed", "preserved", "preserve-only-seed") for path in _UNINSTALL_SEED_PATHS)
            expected.append(
                _action(
                    "@provider-stage",
                    "stage",
                    stage_status,
                    "candidate-stage-cleanup" if stage_status == "completed" else "candidate-stage-cleanup-warning",
                )
            )
            if (
                len(actions) != len(expected)
                or actions[:2] != expected[:2]
                or actions[8:10] != expected[8:10]
                or actions[10] != expected[10]
            ):
                return False
            return all(
                action
                in (
                    _action(path, category, "completed", f"owned-{category}-remove"),
                    _action(path, category, "preserved", f"owned-{category}-absent"),
                )
                for action, path, category in zip(
                    actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
                )
            )
        return False
    if profile.startswith("exact ") and " partial action set at " in profile:
        prefix, expected_phase = profile.split(" at ", 1)
        if phase != expected_phase or operation not in {"install", "update", "uninstall"}:
            return False
        if prefix != f"exact {operation} partial action set":
            return False
        return _partial_action_profile_matches(
            actions,
            operation=operation,
            seed_policy=seed_policy or "",
            phase=phase,
        )
    if profile in {
        "install-create terminal action set",
        "install-preserve terminal action set",
        "update terminal action set",
    }:
        if operation not in {"install", "update"} or seed_policy not in {"create-if-absent", "preserve-only"}:
            return False
        if len(actions) != len(_LIFECYCLE_ACTION_PATHS) or [item["path"] for item in actions] != list(
            _LIFECYCLE_ACTION_PATHS
        ):
            return False
        if (
            actions[0]["category"] != "container"
            or actions[0]["reason"]
            not in {
                "shared-container-preserve",
                "fresh-container-create",
            }
            or actions[0]["status"] not in {"preserved", "completed"}
        ):
            return False
        if actions[1] != _action("spec-dock/spec-dock.version", "record", "completed", "terminal-record-publish"):
            return False
        for action, path, category in zip(
            actions[2:8], _UNINSTALL_TARGET_PATHS, _INSTALL_TARGET_CATEGORIES, strict=True
        ):
            if action["path"] != path or action["category"] != category:
                return False
            if action["reason"] == f"candidate-{category}-current":
                if action["status"] != "preserved":
                    return False
            elif action["reason"] in {f"candidate-{category}-create", f"candidate-{category}-replace"}:
                if action["status"] != "completed":
                    return False
            else:
                return False
        for action, path in zip(actions[8:10], _UNINSTALL_SEED_PATHS, strict=True):
            if action["path"] != path or action["category"] != "seed":
                return False
            if seed_policy == "preserve-only":
                if action != _action(path, "seed", "preserved", "preserve-only-seed"):
                    return False
            elif action["reason"] == "fresh-seed-create":
                if action["status"] != "completed":
                    return False
            elif action != _action(path, "seed", "preserved", "consumer-seed-present"):
                return False
        return actions[-1] == _action("@provider-stage", "stage", "completed", "candidate-stage-cleanup")
    if profile in {
        "install-create terminal + one stage warning",
        "install-preserve terminal + one stage warning",
        "update terminal + one stage warning",
    }:
        if not actions or actions[-1] != _action(
            "@provider-stage", "stage", "warning", "candidate-stage-cleanup-warning"
        ):
            return False
        completed_actions = list(actions)
        completed_actions[-1] = _action("@provider-stage", "stage", "completed", "candidate-stage-cleanup")
        return _action_profile_matches(
            completed_actions,
            profile.removesuffix(" + one stage warning") + " action set",
            operation=operation,
            seed_policy=seed_policy,
            phase=phase,
        )
    return False


def _variant_matches(
    variant: str,
    *,
    operation: str | None,
    specs_mode: str | None,
    retry_command: str | None,
    continuation: Mapping[str, str | None],
) -> bool:
    """Use public command echoes to narrow rows where the closed result permits it."""

    if not variant.startswith("desired "):
        if "specs_mode=keep" in variant and specs_mode != "keep":
            return False
        if "specs_mode=null" in variant and specs_mode is not None:
            return False
    if variant.startswith("cleanup-retry "):
        base = variant.removeprefix("cleanup-retry ").split(" token", 1)[0]
        expected_operation = {"init-force": "install", "update": "update", "uninstall-apply-keep": "uninstall"}.get(
            base
        )
        if expected_operation != operation:
            return False
        if retry_command is None:
            return continuation["next_action"] == "none"
        if base == "init-force" and not retry_command.startswith("spec-dock init --force --provider-cleanup-token "):
            return False
        if base == "update" and not retry_command.startswith("spec-dock update --provider-cleanup-token "):
            return False
        if base == "uninstall-apply-keep" and not retry_command.startswith(
            "spec-dock uninstall --apply --keep-specs --provider-cleanup-token "
        ):
            return False
    if variant.startswith("receipt-only token replay "):
        base = variant.removeprefix("receipt-only token replay ").split(";", 1)[0].strip("`")
        if base == "uninstall-apply-keep" and specs_mode != "keep":
            return False
        if base in {"init-force", "update"} and specs_mode is not None:
            return False
    if variant.startswith("desired `"):
        command_label = variant.removeprefix("desired `").split(";", 1)[0]
        command_prefix = {
            "init": "spec-dock init -- ",
            "init --force": "spec-dock init --force -- ",
            "update": "spec-dock update -- ",
            "uninstall dry-run default": "spec-dock uninstall -- ",
            "uninstall dry-run keep": "spec-dock uninstall --keep-specs -- ",
            "uninstall apply default": "spec-dock uninstall --apply -- ",
            "uninstall apply keep": "spec-dock uninstall --apply --keep-specs -- ",
        }.get(command_label)
        if command_prefix is None:
            return False
        command_echo = (
            continuation["after_cleanup_command"]
            if continuation["next_action"] == "retry-cleanup"
            else continuation["next_command"]
        )
        if command_echo is not None and not command_echo.startswith(command_prefix):
            return False
    return True


def _expected_guidance(code: str, continuation: Mapping[str, str | None]) -> tuple[str, ...]:
    if code == "active-legacy-recovery":
        return _ACTIVE_LEGACY_GUIDANCE
    if code in {"install-partial-failure", "update-partial-failure", "uninstall-partial-failure"}:
        return _LIFECYCLE_PARTIAL_GUIDANCE
    if code == "lifecycle-preparation-failed":
        return _PREPARATION_GUIDANCE
    if code.endswith("-completed-with-cleanup-warning"):
        return _CLEANUP_WARNING_GUIDANCE
    if code == "terminal-cleanup-failed":
        return (
            _CLEANUP_FAILED_DEFERRED_GUIDANCE
            if continuation["after_cleanup_action"] == "run-request"
            else _CLEANUP_FAILED_NONE_GUIDANCE
        )
    if code == "terminal-cleanup-completed":
        return (
            _CLEANUP_COMPLETED_DEFERRED_GUIDANCE
            if continuation["next_action"] == "run-request"
            else _CLEANUP_COMPLETED_NONE_GUIDANCE
        )
    if code == "spec-history-purge-removed":
        return _PURGE_GUIDANCE
    return ()


def _validate_relation(
    *,
    mode: str,
    apply: bool,
    status: str,
    code: str,
    operation: str | None,
    candidate_digest: str | None,
    seed_policy: str | None,
    mutation_started: bool,
    bootstrap_rolled_back: bool,
    phase: str,
    last_completed_phase: str,
    retry_command: str | None,
    continuation: Mapping[str, str | None],
    target: str,
    specs_mode: str | None,
    actions: Sequence[Mapping[str, str]],
) -> None:
    matches = []
    for row in wire.RELATION_ROWS:
        if row["code"] != code:
            continue
        if row["mode"] != mode or row["apply"] != apply or row["status"] != status:
            continue
        row_operation = cast("str | None", row["operation"])
        row_candidate = cast("str", row["candidate_digest"])
        row_seed = cast("str", row["seed_policy"])
        row_retry = cast("str | None", row["retry"])
        row_continuation = cast("str", row["continuation"])
        row_actions = cast("str", row["actions"])
        if not _relation_accepts(operation, row_operation):
            continue
        if not _relation_accepts(candidate_digest, row_candidate):
            continue
        if not _relation_accepts(seed_policy, row_seed):
            continue
        if row["mutation_started"] != mutation_started or row["bootstrap_rolled_back"] != bootstrap_rolled_back:
            continue
        if row["phase"] != phase or row["last_completed_phase"] != last_completed_phase:
            continue
        if not _retry_matches(retry_command, row_retry, target, operation, seed_policy):
            continue
        if not _continuation_matches(continuation, row_continuation, retry_command):
            continue
        if not _action_profile_matches(
            actions,
            row_actions,
            operation=operation,
            seed_policy=seed_policy,
            phase=phase,
        ):
            continue
        if not _variant_matches(
            cast("str", row["variant"]),
            operation=operation,
            specs_mode=specs_mode,
            retry_command=retry_command,
            continuation=continuation,
        ):
            continue
        matches.append(row)
    if not matches:
        _fail("public result does not match a Wire v12 relation row")


def _validate_result_mapping(value: Mapping[str, object]) -> dict[str, object]:
    _exact_keys(value, _RESULT_KEYS, "public result")
    if _integer(value["schema_version"], "schema_version") != 1:
        _fail("public result schema_version must be 1")
    target = _text(value["target"], "target")
    assert target is not None
    mode = _text(value["mode"], "mode")
    apply = _bool(value["apply"], "apply")
    if mode not in ("dry-run", "apply") or apply != (mode == "apply"):
        _fail("mode/apply mismatch")
    assert mode is not None
    specs_mode = _text(value["specs_mode"], "specs_mode", allow_null=True)
    if specs_mode not in (None, "keep", "remove"):
        _fail("invalid specs_mode")
    status = _text(value["status"], "status")
    code = _text(value["code"], "code")
    assert status is not None and code is not None
    if status not in wire.PUBLIC_STATUS_VALUES or code not in wire.PUBLIC_CODE_VALUES:
        _fail("unknown public status or code")
    operation = _text(value["operation"], "operation", allow_null=True)
    if operation not in (None, "install", "update", "uninstall"):
        _fail("invalid public operation")
    candidate_digest = _digest(value["candidate_digest"], "candidate_digest", allow_null=True)
    seed_policy = _text(value["seed_policy"], "seed_policy", allow_null=True)
    if seed_policy not in (None, "create-if-absent", "preserve-only"):
        _fail("invalid public seed_policy")
    mutation_started = _bool(value["mutation_started"], "mutation_started")
    bootstrap_rolled_back = _bool(value["bootstrap_rolled_back"], "bootstrap_rolled_back")
    phase = _text(value["phase"], "phase")
    last_completed_phase = _text(value["last_completed_phase"], "last_completed_phase")
    assert phase is not None and last_completed_phase is not None
    if phase not in wire.PHASE_VALUES or last_completed_phase not in wire.LAST_COMPLETED_PHASE_VALUES:
        _fail("unknown public phase")
    retry_command = _text(value["retry_command"], "retry_command", allow_null=True)
    continuation = _continuation(_mapping(value["continuation"], "continuation"))
    failed_paths = _string_list(value["failed_paths"], "failed_paths")
    pending_paths = _string_list(value["pending_paths"], "pending_paths")
    for paths, label in ((failed_paths, "failed_paths"), (pending_paths, "pending_paths")):
        if any(path not in _PUBLIC_PATH_RANK for path in paths):
            _fail(f"{label} contains an unknown path")
        if len(paths) != len(set(paths)):
            _fail(f"{label} contains duplicate paths")
        if list(paths) != sorted(paths, key=_PUBLIC_PATH_RANK.__getitem__):
            _fail(f"{label} is not in TARGET_PATH_ORDER")
    raw_actions_value = value["actions"]
    if not isinstance(raw_actions_value, list):
        _fail("actions must be an array")
    raw_actions: list[object] = raw_actions_value
    actions = []
    for action in raw_actions:
        actions.append(_action_mapping(_mapping(action, "action")))
    _validate_action_context(actions, operation, seed_policy)
    action_paths = [action["path"] for action in actions]
    if len(action_paths) != len(set(action_paths)):
        _fail("actions contains duplicate paths")
    if action_paths != sorted(action_paths, key=_PUBLIC_PATH_RANK.__getitem__):
        _fail("actions is not in TARGET_PATH_ORDER")
    derived_failed = [action["path"] for action in actions if action["status"] == "failed"]
    derived_pending = [action["path"] for action in actions if action["status"] == "pending"]
    if failed_paths != derived_failed or pending_paths != derived_pending:
        _fail("public path arrays do not match actions")
    if status in ("blocked", "error") and (actions or failed_paths or pending_paths):
        _fail("blocked/error result must expose empty action details")
    guidance = _string_list(value["guidance"], "guidance")
    warnings = _string_list(value["warnings"], "warnings")
    errors = _string_list(value["errors"], "errors")
    if (
        status == "completed_with_warnings"
        and not any(action["status"] == "warning" for action in actions)
        and not warnings
    ):
        _fail("warning result must expose warning evidence")
    summary = _summary(_mapping(value["summary"], "summary"), actions)
    if len(warnings) > 1 or len(errors) > 1:
        _fail("warnings and errors are single-item arrays")
    expected_errors = [_ERRORS[code]] if code in _ERRORS and status in ("blocked", "partial_failure", "error") else []
    if errors != expected_errors:
        _fail("error text does not match the closed diagnostic profile")
    expected_warnings = [_CLEANUP_WARNING] if code.endswith("-completed-with-cleanup-warning") else []
    if warnings != expected_warnings:
        _fail("warning text does not match the closed diagnostic profile")
    if tuple(guidance) != _expected_guidance(code, continuation):
        _fail("guidance does not match the closed diagnostic profile")
    _validate_relation(
        mode=mode,
        apply=apply,
        status=status,
        code=code,
        operation=operation,
        candidate_digest=candidate_digest,
        seed_policy=seed_policy,
        mutation_started=mutation_started,
        bootstrap_rolled_back=bootstrap_rolled_back,
        phase=phase,
        last_completed_phase=last_completed_phase,
        retry_command=retry_command,
        continuation=continuation,
        target=target,
        specs_mode=specs_mode,
        actions=actions,
    )
    return {
        "schema_version": 1,
        "target": target,
        "mode": mode,
        "apply": apply,
        "specs_mode": specs_mode,
        "status": status,
        "code": code,
        "operation": operation,
        "candidate_digest": candidate_digest,
        "seed_policy": seed_policy,
        "mutation_started": mutation_started,
        "bootstrap_rolled_back": bootstrap_rolled_back,
        "phase": phase,
        "last_completed_phase": last_completed_phase,
        "retry_command": retry_command,
        "continuation": continuation,
        "failed_paths": list(failed_paths),
        "pending_paths": list(pending_paths),
        "summary": summary,
        "actions": actions,
        "guidance": list(guidance),
        "warnings": list(warnings),
        "errors": list(errors),
    }


def _result_mapping(result: LifecycleResult) -> dict[str, object]:
    if not isinstance(result, LifecycleResult):
        _fail("public result must be LifecycleResult")
    return {
        "schema_version": result.schema_version,
        "target": result.target,
        "mode": result.mode,
        "apply": result.apply,
        "specs_mode": result.specs_mode,
        "status": result.status,
        "code": result.code,
        "operation": result.operation,
        "candidate_digest": result.candidate_digest,
        "seed_policy": result.seed_policy,
        "mutation_started": result.mutation_started,
        "bootstrap_rolled_back": result.bootstrap_rolled_back,
        "phase": result.phase,
        "last_completed_phase": result.last_completed_phase,
        "retry_command": result.retry_command,
        "continuation": dict(result.continuation),
        "failed_paths": list(result.failed_paths),
        "pending_paths": list(result.pending_paths),
        "summary": dict(result.summary),
        "actions": [
            {
                "path": action.path,
                "category": action.category,
                "status": action.status,
                "reason": action.reason,
            }
            if isinstance(action, LifecycleAction)
            else dict(action)
            for action in result.actions
        ],
        "guidance": list(result.guidance),
        "warnings": list(result.warnings),
        "errors": list(result.errors),
    }


def build_public_result(
    request: LifecycleRequest,
    *,
    status: str,
    code: str,
    operation: str | object | None = ...,
    candidate_digest: str | object | None = ...,
    seed_policy: str | object | None = ...,
    mutation_started: bool = False,
    bootstrap_rolled_back: bool = False,
    phase: str = "request-validation",
    last_completed_phase: str = "not-started",
    retry_command: str | None = None,
    continuation: Mapping[str, object] | None = None,
    failed_paths: Sequence[str] = (),
    pending_paths: Sequence[str] = (),
    summary: Mapping[str, int] | None = None,
    actions: Sequence[LifecycleAction | Mapping[str, object]] = (),
    guidance: Sequence[str] = (),
    warnings: Sequence[str] = (),
    errors: Sequence[str] | None = None,
) -> LifecycleResult:
    """Build and validate a result; all output values remain wire-closed."""

    if not isinstance(request, LifecycleRequest):
        _fail("request must be LifecycleRequest")
    actual_operation = request.operation if operation is ... else operation
    actual_digest = request.candidate_digest if candidate_digest is ... else candidate_digest
    actual_seed = request.seed_policy if seed_policy is ... else seed_policy
    normalized_actions = tuple(LifecycleAction(**_action_mapping(action)) for action in actions)
    normalized_continuation = (
        {
            "next_action": "none",
            "next_command": None,
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        }
        if continuation is None
        else _continuation(_mapping(continuation, "continuation"))
    )
    if summary is None:
        counts = dict.fromkeys(_SUMMARY_KEYS, 0)
        for action in normalized_actions:
            if action.status in counts:
                counts[action.status] += 1
        actual_summary = counts
    else:
        actual_summary = dict(summary)
    actual_errors = (
        tuple(errors)
        if errors is not None
        else tuple([_ERRORS[code]] if code in _ERRORS and status in ("blocked", "partial_failure", "error") else [])
    )
    result = LifecycleResult(
        schema_version=1,
        target=request.target,
        mode=request.mode,
        apply=request.apply,
        specs_mode=request.specs_mode,
        status=status,
        code=code,
        operation=actual_operation,  # type: ignore[arg-type]
        candidate_digest=actual_digest,  # type: ignore[arg-type]
        seed_policy=actual_seed,  # type: ignore[arg-type]
        mutation_started=mutation_started,
        bootstrap_rolled_back=bootstrap_rolled_back,
        phase=phase,
        last_completed_phase=last_completed_phase,
        retry_command=retry_command,
        continuation=normalized_continuation,
        failed_paths=tuple(failed_paths),
        pending_paths=tuple(pending_paths),
        summary=actual_summary,
        actions=normalized_actions,
        guidance=tuple(guidance),
        warnings=tuple(warnings),
        errors=actual_errors,
    )
    validate_public_result(result)
    return result


def validate_public_result(result: LifecycleResult | Mapping[str, object] | bytes | str) -> None:
    """Validate a result object or its decoded/encoded public representation."""

    value: Mapping[str, object]
    if isinstance(result, LifecycleResult):
        value = _result_mapping(result)
    elif isinstance(result, Mapping):
        value = result
    else:
        value = _decode_json(result, 65536, "public result")
    _validate_result_mapping(value)


def serialize_public_result(result: LifecycleResult) -> bytes:
    """Serialize a validated public result (useful for focused tests)."""

    value = _validate_result_mapping(_result_mapping(result))
    return _canonical(value)


__all__ = [
    "WireValidationError",
    "build_public_result",
    "parse_installation_record",
    "parse_slot_marker",
    "serialize_installation_record",
    "serialize_public_result",
    "serialize_slot_marker",
    "validate_public_result",
]
