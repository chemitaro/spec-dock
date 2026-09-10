"""Owner-bound private lifecycle state and stage stores."""

from __future__ import annotations

import base64
from collections.abc import Mapping
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
from typing import TYPE_CHECKING, Literal, NoReturn, cast

from spec_dock.provider_lifecycle.candidate import FIXED_DOMAINS
from spec_dock.provider_lifecycle.contracts import (
    SEED_PATHS,
    ActiveState,
    CompletionReceipt,
    InodeWitness,
    Operation,
    SeedAdmissionState,
    SeedPolicy,
    StageOwner,
)
from spec_dock.provider_lifecycle.filesystem import NativeAtomicFilesystem
from spec_dock.provider_lifecycle.wire import parse_installation_record, serialize_installation_record

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

PRIVATE_NAMESPACE_PREFIX = ".spec-dock-provider-lifecycle-v1-euid-"
PRIVATE_DIRECTORY_MODE = 0o700
PRIVATE_METADATA_MODE = 0o600
RECORD_TEMP_MODE = 0o644
ACTIVE_NAME = "ACTIVE.json"
ACTIVE_TEMP_NAME = "ACTIVE.json.tmp"
RECEIPT_NAME = "CLEANUP-COMPLETED.json"
RECEIPT_TEMP_NAME = "CLEANUP-COMPLETED.json.tmp"
RECORD_TEMP_NAME = "RECORD-TEMP"
STAGE_NAME = "STAGE"
STAGE_OWNER_NAME = "STAGE-OWNER.json"
PRIVATE_ENTRY_NAMES = (
    ACTIVE_NAME,
    ACTIVE_TEMP_NAME,
    RECEIPT_NAME,
    RECEIPT_TEMP_NAME,
    RECORD_TEMP_NAME,
    STAGE_NAME,
)
STAGE_ENTRY_NAMES = (
    "docs",
    "templates",
    "system",
    "scripts",
    "slot-spec-dock",
    "slot-spec-dock-grill-with-docs",
)
STAGE_TARGET_PATHS = tuple(domain[1] for domain in FIXED_DOMAINS)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_GENERATION = re.compile(r"^[0-9a-f]{32}$")
_INVOCATION_IDS = {
    "init",
    "init-force",
    "update",
    "uninstall-dry-run",
    "uninstall-dry-run-keep",
    "uninstall-apply",
    "uninstall-apply-keep",
}
_CLEANUP_IDS = {"init-force", "update", "uninstall-apply-keep"}

_DESIRED_INVOCATION_PREFIXES = {
    "init": ("spec-dock", "init"),
    "init-force": ("spec-dock", "init", "--force"),
    "update": ("spec-dock", "update"),
    "uninstall-dry-run": ("spec-dock", "uninstall"),
    "uninstall-dry-run-keep": ("spec-dock", "uninstall", "--keep-specs"),
    "uninstall-apply": ("spec-dock", "uninstall", "--apply"),
    "uninstall-apply-keep": ("spec-dock", "uninstall", "--apply", "--keep-specs"),
}
_CLEANUP_INVOCATION_PREFIXES = {
    "init-force": ("spec-dock", "init", "--force", "--provider-cleanup-token"),
    "update": ("spec-dock", "update", "--provider-cleanup-token"),
    "uninstall-apply-keep": (
        "spec-dock",
        "uninstall",
        "--apply",
        "--keep-specs",
        "--provider-cleanup-token",
    ),
}


class PrivateStateError(RuntimeError):
    """Private state is absent, invalid, foreign, or unsafe to mutate."""


class PrivateStateForeignError(PrivateStateError):
    """A fixed private object must be preserved and cannot be adopted."""


def _fail(message: str) -> NoReturn:
    raise PrivateStateError(message)


def _directory_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


def _open_absolute_directory_no_follow(path: str | os.PathLike[str]) -> int:
    """Open every component of an absolute directory path without following links."""

    raw_path = os.fspath(path)
    if not Path(raw_path).is_absolute() or "\x00" in raw_path:
        raise PrivateStateError("directory path must be absolute and NUL-free")
    components = Path(raw_path).parts[1:]
    current_fd = os.open(os.sep, _directory_open_flags())
    try:
        for component in components:
            if component in {"", ".", ".."}:
                raise PrivateStateError("directory path contains an unsafe component")
            next_fd = os.open(component, _directory_open_flags(), dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _exact(value: Mapping[str, object], keys: Sequence[str], label: str) -> None:
    if tuple(value.keys()) != tuple(keys):
        _fail(f"{label} keys are not exact")


def _string(value: object, label: str, *, allow_null: bool = False) -> str | None:
    if value is None and allow_null:
        return None
    if not isinstance(value, str) or "\x00" in value:
        _fail(f"{label} must be a NUL-free string")
    return cast("str", value)


def _integer(value: object, label: str, *, nonnegative: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(f"{label} must be an integer")
    if nonnegative and value < 0:
        _fail(f"{label} must be non-negative")
    return cast("int", value)


def _digest(value: object, label: str, *, allow_null: bool = False) -> str | None:
    value = _string(value, label, allow_null=allow_null)
    if value is None:
        return None
    if _DIGEST.fullmatch(value) is None:
        _fail(f"{label} must be a lowercase SHA-256 digest")
    return value


def _generation(value: object, label: str) -> str:
    value = _string(value, label)
    assert value is not None
    if _GENERATION.fullmatch(value) is None:
        _fail(f"{label} must be 32 lowercase hexadecimal characters")
    return value


def _json_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


def _read_json_bytes(raw: bytes, maximum: int, label: str) -> Mapping[str, object]:
    if len(raw) > maximum or not raw.endswith(b"\n") or raw[:-1].find(b"\n") >= 0:
        _fail(f"{label} has invalid size or line ending")
    try:
        text = raw[:-1].decode("utf-8")
    except UnicodeDecodeError as exc:
        _fail(f"{label} is not UTF-8: {exc}")

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in items:
            if key in result:
                _fail(f"{label} has duplicate key {key!r}")
            result[key] = item
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=lambda constant: _fail(constant))
    except PrivateStateError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not JSON: {exc}")
    if not isinstance(value, Mapping):
        _fail(f"{label} must be an object")
    if _json_bytes(value) != raw:
        _fail(f"{label} must be compact canonical JSON")
    return value


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail(f"{label} must be an object")
    return cast("Mapping[str, object]", value)


def _base64(value: object, label: str) -> bytes:
    value = _string(value, label)
    assert value is not None
    try:
        return base64.b64decode(value, validate=True)
    except (TypeError, ValueError) as exc:
        _fail(f"{label} is not valid base64: {exc}")


def repository_key_for(device: int, inode: int, euid: int) -> str:
    """Compute the exact repository identity key without a terminal LF."""

    payload = json.dumps(
        ["spec-dock-repository-key-v1", device, inode, euid],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def tuple_key_for(operation: str, candidate_digest: str, seed_policy: str) -> str:
    """Compute the exact operation tuple key without a terminal LF."""

    _digest(candidate_digest, "candidate_digest")
    payload = json.dumps(
        ["spec-dock-lifecycle-tuple-v1", operation, candidate_digest, seed_policy],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def cleanup_token_for(repository_key: str, tuple_key: str, result_family: str, operation_generation: str) -> str:
    """Compute the generation-bound WIR-INV-001 cleanup token."""

    for value, label in ((repository_key, "repository_key"), (tuple_key, "tuple_key")):
        _digest(value, label)
    _generation(operation_generation, "operation_generation")
    payload = json.dumps(
        ["spec-dock-terminal-cleanup-v2", repository_key, tuple_key, result_family, operation_generation],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _inode_mapping(witness: InodeWitness) -> dict[str, object]:
    if not isinstance(witness, InodeWitness):
        _fail("inode witness must be InodeWitness")
    return {
        "kind": witness.kind,
        "device": witness.device,
        "inode": witness.inode,
        "ctime_ns": witness.ctime_ns,
        "mode": witness.mode,
        "link_count": witness.link_count,
        "size": witness.size,
        "sha256": witness.sha256,
    }


def _parse_inode(value: object, label: str, *, allow_null: bool = False) -> InodeWitness | None:
    if value is None and allow_null:
        return None
    mapping = _mapping(value, label)
    _exact(mapping, ("kind", "device", "inode", "ctime_ns", "mode", "link_count", "size", "sha256"), label)
    kind = _string(mapping["kind"], f"{label}.kind")
    if kind not in {"regular", "directory"}:
        _fail(f"{label}.kind is invalid")
    device = _integer(mapping["device"], f"{label}.device", nonnegative=True)
    inode = _integer(mapping["inode"], f"{label}.inode", nonnegative=True)
    ctime_ns = _integer(mapping["ctime_ns"], f"{label}.ctime_ns", nonnegative=True)
    mode = _integer(mapping["mode"], f"{label}.mode", nonnegative=True)
    link_count = _integer(mapping["link_count"], f"{label}.link_count", nonnegative=True)
    size = mapping["size"]
    digest = mapping["sha256"]
    if kind == "directory":
        if size is not None or digest is not None:
            _fail(f"{label} directory witness must have null size/sha256")
        parsed_size = None
        parsed_digest = None
    else:
        parsed_size = _integer(size, f"{label}.size", nonnegative=True)
        parsed_digest = _digest(digest, f"{label}.sha256")
    return InodeWitness(kind, device, inode, ctime_ns, mode, link_count, parsed_size, parsed_digest)  # type: ignore[arg-type]


def _record_ref(value: object, label: str) -> dict[str, object]:
    mapping = _mapping(value, label)
    _exact(mapping, ("kind", "bytes_base64", "sha256", "witness"), label)
    kind = _string(mapping["kind"], f"{label}.kind")
    if kind not in {"absent", "legacy-0.2.3", "final"}:
        _fail(f"{label}.kind is invalid")
    raw = mapping["bytes_base64"]
    digest = mapping["sha256"]
    witness = mapping["witness"]
    if kind == "absent":
        if raw is not None or digest is not None or witness is not None:
            _fail(f"{label} absent record must contain null fields")
    else:
        data = _base64(raw, f"{label}.bytes_base64")
        parsed_digest = _digest(digest, f"{label}.sha256")
        parsed_witness = _parse_inode(witness, f"{label}.witness")
        if (
            parsed_witness is None
            or parsed_witness.kind != "regular"
            or parsed_witness.mode != RECORD_TEMP_MODE
            or parsed_witness.link_count != 1
        ):
            _fail(f"{label}.witness must be a mode0644 regular file")
        assert parsed_digest is not None
        if hashlib.sha256(data).hexdigest() != parsed_digest:
            _fail(f"{label}.sha256 does not match bytes")
    return dict(mapping)


def _expected_record(value: object) -> dict[str, str]:
    mapping = _mapping(value, "expected_incomplete_record")
    _exact(mapping, ("bytes_base64", "sha256"), "expected_incomplete_record")
    data = _base64(mapping["bytes_base64"], "expected_incomplete_record.bytes_base64")
    if len(data) > 4096:
        _fail("expected incomplete record is oversized")
    digest = _digest(mapping["sha256"], "expected_incomplete_record.sha256")
    assert digest is not None
    try:
        parse_installation_record(data)
    except ValueError as exc:
        _fail(f"expected incomplete record is invalid: {exc}")
    if hashlib.sha256(data).hexdigest() != digest:
        _fail("expected incomplete record digest does not match bytes")
    encoded = _string(mapping["bytes_base64"], "expected_incomplete_record.bytes_base64")
    assert encoded is not None
    return {"bytes_base64": encoded, "sha256": digest}


def _bootstrap(value: object) -> dict[str, object]:
    mapping = _mapping(value, "bootstrap_container")
    _exact(mapping, ("disposition", "witness"), "bootstrap_container")
    disposition = _string(mapping["disposition"], "bootstrap_container.disposition")
    if disposition not in {"existing", "planned-create", "created"}:
        _fail("bootstrap_container disposition is invalid")
    witness = _parse_inode(mapping["witness"], "bootstrap_container.witness", allow_null=True)
    if disposition == "planned-create" and witness is not None:
        _fail("planned-create bootstrap must have null witness")
    if disposition != "planned-create" and (witness is None or witness.kind != "directory"):
        _fail("bound bootstrap must have a directory witness")
    return dict(mapping)


def _seed_admission(value: object) -> dict[str, SeedAdmissionState]:
    mapping = _mapping(value, "ACTIVE.seed_admission")
    _exact(mapping, SEED_PATHS, "ACTIVE.seed_admission")
    result: dict[str, SeedAdmissionState] = {}
    for path in SEED_PATHS:
        state = _string(mapping[path], f"ACTIVE.seed_admission.{path}")
        if state not in {"absent", "present"}:
            _fail(f"ACTIVE.seed_admission.{path} is invalid")
        result[path] = cast("SeedAdmissionState", state)
    return result


def _owned_targets(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) != 6:
        _fail("owned_target_witnesses must contain six entries")
    raw: list[object] = value
    result: list[dict[str, object]] = []
    for index, item in enumerate(raw):
        mapping = _mapping(item, "owned_target_witness")
        _exact(
            mapping,
            (
                "path",
                "original_kind",
                "original_tree_digest",
                "original_inode",
                "terminal_kind",
                "terminal_tree_digest",
            ),
            "owned_target_witness",
        )
        path = _string(mapping["path"], "owned_target_witness.path")
        if path != STAGE_TARGET_PATHS[index]:
            _fail("owned target witness path order is not fixed")
        for key in ("original_kind", "terminal_kind"):
            kind = _string(mapping[key], f"owned_target_witness.{key}")
            if kind not in {None, "absent", "directory"}:
                _fail(f"owned_target_witness.{key} is invalid")
        for key in ("original_tree_digest", "terminal_tree_digest"):
            _digest(mapping[key], f"owned_target_witness.{key}", allow_null=True)
        original_kind = mapping["original_kind"]
        terminal_kind = mapping["terminal_kind"]
        original_inode = _parse_inode(mapping["original_inode"], "owned_target_witness.original_inode", allow_null=True)
        if original_kind == "directory" and original_inode is None:
            _fail("directory original target needs an inode witness")
        if original_kind == "directory" and mapping["original_tree_digest"] is None:
            _fail("directory original target needs a tree digest")
        if original_kind == "absent" and mapping["original_tree_digest"] is not None:
            _fail("absent original target cannot have a tree digest")
        if original_kind == "absent" and original_inode is not None:
            _fail("absent original target cannot have an inode witness")
        if terminal_kind == "directory" and mapping["terminal_tree_digest"] is None:
            _fail("directory terminal target needs a tree digest")
        if terminal_kind == "absent" and mapping["terminal_tree_digest"] is not None:
            _fail("absent terminal target cannot have a tree digest")
        result.append(dict(mapping))
    return result


def _registered_entries(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) != 6:
        _fail("registered_stage_entries must contain six entries")
    raw: list[object] = value
    result: list[dict[str, object]] = []
    for index, item in enumerate(raw):
        mapping = _mapping(item, "registered_stage_entry")
        _exact(
            mapping, ("name", "target_path", "candidate_tree_digest", "original_tree_digest"), "registered_stage_entry"
        )
        if mapping["name"] != STAGE_ENTRY_NAMES[index] or mapping["target_path"] != STAGE_TARGET_PATHS[index]:
            _fail("registered stage entry order is not fixed")
        _digest(mapping["candidate_tree_digest"], "candidate_tree_digest", allow_null=True)
        _digest(mapping["original_tree_digest"], "original_tree_digest", allow_null=True)
        result.append(dict(mapping))
    return result


def _validate_rendered_invocation(
    invocation_id: str,
    rendered: str,
    *,
    cleanup_token: str | None = None,
) -> None:
    prefixes = _CLEANUP_INVOCATION_PREFIXES if cleanup_token is not None else _DESIRED_INVOCATION_PREFIXES
    prefix = prefixes.get(invocation_id)
    if prefix is None:
        _fail("invocation_id is not supported")
    try:
        tokens = shlex.split(rendered, posix=True)
    except ValueError as exc:
        _fail(f"rendered invocation is not canonical: {exc}")
    expected_length = len(prefix) + (3 if cleanup_token is not None else 2)
    if "\x00" in rendered or len(tokens) != expected_length:
        _fail("rendered invocation is not canonical")
    if tuple(tokens[: len(prefix)]) != prefix:
        _fail("rendered invocation does not match invocation_id")
    if cleanup_token is not None and tokens[len(prefix)] != cleanup_token:
        _fail("rendered cleanup invocation token does not match")
    separator_index = len(prefix) + (1 if cleanup_token is not None else 0)
    if tokens[separator_index] != "--":
        _fail("rendered invocation must use the fixed target separator")
    target = tokens[separator_index + 1]
    if not target.startswith("/") or target in {"", "/"}:
        _fail("rendered invocation target must be normalized absolute path")
    if shlex.join(tokens) != rendered:
        _fail("rendered invocation is not canonical")


def _invocation(value: object, label: str, *, cleanup: bool = False) -> dict[str, str]:
    mapping = _mapping(value, label)
    expected = (
        ("role", "invocation_id", "cleanup_token", "rendered_command")
        if cleanup
        else ("invocation_id", "rendered_command")
    )
    _exact(mapping, expected, label)
    if cleanup:
        if mapping["role"] != "cleanup-retry":
            _fail(f"{label}.role is invalid")
        _digest(mapping["cleanup_token"], f"{label}.cleanup_token")
        invocation_id = _string(mapping["invocation_id"], f"{label}.invocation_id")
        if invocation_id not in _CLEANUP_IDS:
            _fail(f"{label}.invocation_id is invalid")
    else:
        invocation_id = _string(mapping["invocation_id"], f"{label}.invocation_id")
        if invocation_id not in _INVOCATION_IDS:
            _fail(f"{label}.invocation_id is invalid")
    rendered = _string(mapping["rendered_command"], f"{label}.rendered_command")
    assert invocation_id is not None and rendered is not None
    _validate_rendered_invocation(
        invocation_id,
        rendered,
        cleanup_token=cast("str", mapping["cleanup_token"]) if cleanup else None,
    )
    return {key: value for key, value in mapping.items() if isinstance(value, str)}


def _active_mapping(state: ActiveState) -> dict[str, object]:
    return {
        "schema_version": state.schema_version,
        "state": state.state,
        "repository_key": state.repository_key,
        "repository_identity": dict(state.repository_identity),
        "tuple_key": state.tuple_key,
        "operation_generation": state.operation_generation,
        "operation": state.operation,
        "candidate_digest": state.candidate_digest,
        "seed_policy": state.seed_policy,
        "seed_admission": dict(state.seed_admission),
        "result_family": state.result_family,
        "original_record": dict(state.original_record),
        "expected_incomplete_record": dict(state.expected_incomplete_record),
        "bootstrap_container": dict(state.bootstrap_container),
        "owned_target_witnesses": [dict(item) for item in state.owned_target_witnesses],
        "registered_stage_entries": [dict(item) for item in state.registered_stage_entries],
        "record_temp_witness": None if state.record_temp_witness is None else _inode_mapping(state.record_temp_witness),
        "terminal_record_digest": state.terminal_record_digest,
        "cleanup_token": state.cleanup_token,
        "cleanup_retry_invocation": dict(state.cleanup_retry_invocation),
        "deferred_invocation": None if state.deferred_invocation is None else dict(state.deferred_invocation),
    }


def _parse_active(value: Mapping[str, object]) -> ActiveState:
    keys = (
        "schema_version",
        "state",
        "repository_key",
        "repository_identity",
        "tuple_key",
        "operation_generation",
        "operation",
        "candidate_digest",
        "seed_policy",
        "seed_admission",
        "result_family",
        "original_record",
        "expected_incomplete_record",
        "bootstrap_container",
        "owned_target_witnesses",
        "registered_stage_entries",
        "record_temp_witness",
        "terminal_record_digest",
        "cleanup_token",
        "cleanup_retry_invocation",
        "deferred_invocation",
    )
    _exact(value, keys, "ACTIVE")
    if value["schema_version"] != 2:
        _fail("ACTIVE schema_version must be 2")
    state = _string(value["state"], "ACTIVE.state")
    if state not in {"prepared", "running", "ready", "terminal-cleanup"}:
        _fail("ACTIVE.state is invalid")
    repository_key = _digest(value["repository_key"], "ACTIVE.repository_key")
    tuple_key = _digest(value["tuple_key"], "ACTIVE.tuple_key")
    operation_generation = _generation(value["operation_generation"], "ACTIVE.operation_generation")
    raw_operation = _string(value["operation"], "ACTIVE.operation")
    if raw_operation not in {"install", "update", "uninstall"}:
        _fail("ACTIVE.operation is invalid")
    operation = cast("str", raw_operation)
    candidate_digest = _digest(value["candidate_digest"], "ACTIVE.candidate_digest")
    seed_policy = _string(value["seed_policy"], "ACTIVE.seed_policy")
    if seed_policy not in {"create-if-absent", "preserve-only"}:
        _fail("ACTIVE.seed_policy is invalid")
    seed_admission = _seed_admission(value["seed_admission"])
    result_family = _string(value["result_family"], "ACTIVE.result_family")
    if result_family not in {"install", "legacy-migration", "update", "uninstall"}:
        _fail("ACTIVE.result_family is invalid")
    identity = _mapping(value["repository_identity"], "ACTIVE.repository_identity")
    _exact(identity, ("device", "inode", "euid"), "ACTIVE.repository_identity")
    identity_value = {
        key: _integer(identity[key], f"ACTIVE.repository_identity.{key}", nonnegative=True) for key in identity
    }
    original_record = _record_ref(value["original_record"], "ACTIVE.original_record")
    expected_record = _expected_record(value["expected_incomplete_record"])
    expected_record_model = parse_installation_record(base64.b64decode(expected_record["bytes_base64"]))
    bootstrap = _bootstrap(value["bootstrap_container"])
    owned = _owned_targets(value["owned_target_witnesses"])
    registered = _registered_entries(value["registered_stage_entries"])
    record_temp = _parse_inode(value["record_temp_witness"], "ACTIVE.record_temp_witness", allow_null=True)
    if record_temp is not None and (
        record_temp.kind != "regular" or record_temp.mode != RECORD_TEMP_MODE or record_temp.link_count != 1
    ):
        _fail("ACTIVE.record_temp_witness must be mode0644 regular")
    terminal_digest = _digest(value["terminal_record_digest"], "ACTIVE.terminal_record_digest")
    cleanup_token = _digest(value["cleanup_token"], "ACTIVE.cleanup_token")
    cleanup_invocation = _invocation(value["cleanup_retry_invocation"], "ACTIVE.cleanup_retry_invocation", cleanup=True)
    deferred = (
        None
        if value["deferred_invocation"] is None
        else _invocation(value["deferred_invocation"], "ACTIVE.deferred_invocation")
    )
    assert (
        repository_key is not None
        and tuple_key is not None
        and candidate_digest is not None
        and terminal_digest is not None
        and cleanup_token is not None
    )
    if (
        expected_record_model.state != "incomplete"
        or expected_record_model.operation != operation
        or expected_record_model.candidate_digest != candidate_digest
        or expected_record_model.seed_policy != seed_policy
    ):
        _fail("ACTIVE expected incomplete record does not match operation identity")
    if tuple_key_for(operation, candidate_digest, seed_policy) != tuple_key:
        _fail("ACTIVE tuple_key does not match operation identity")
    if result_family == "legacy-migration" and (operation != "install" or seed_policy != "preserve-only"):
        _fail("ACTIVE legacy-migration relation is invalid")
    if result_family == "update" and (operation != "update" or seed_policy != "preserve-only"):
        _fail("ACTIVE update relation is invalid")
    if result_family == "uninstall" and (operation != "uninstall" or seed_policy != "preserve-only"):
        _fail("ACTIVE uninstall relation is invalid")
    if result_family == "install" and operation != "install":
        _fail("ACTIVE install relation is invalid")
    if cleanup_token_for(repository_key, tuple_key, result_family, operation_generation) != cleanup_token:
        _fail("ACTIVE.cleanup_token does not match identity")
    return ActiveState(
        2,
        state,  # type: ignore[arg-type]
        repository_key,
        identity_value,
        tuple_key,
        operation_generation,
        operation,  # type: ignore[arg-type]
        candidate_digest,
        seed_policy,  # type: ignore[arg-type]
        seed_admission,  # type: ignore[arg-type]
        result_family,  # type: ignore[arg-type]
        original_record,
        expected_record,
        bootstrap,
        owned,
        registered,
        record_temp,
        terminal_digest,
        cleanup_token,
        cleanup_invocation,
        deferred,
    )


def _receipt_mapping(receipt: CompletionReceipt) -> dict[str, object]:
    return {
        "schema_version": receipt.schema_version,
        "repository_key": receipt.repository_key,
        "tuple_key": receipt.tuple_key,
        "operation_generation": receipt.operation_generation,
        "operation": receipt.operation,
        "candidate_digest": receipt.candidate_digest,
        "seed_policy": receipt.seed_policy,
        "result_family": receipt.result_family,
        "terminal_record_digest": receipt.terminal_record_digest,
        "cleanup_token": receipt.cleanup_token,
        "cleanup_retry_invocation": dict(receipt.cleanup_retry_invocation),
        "deferred_invocation": None if receipt.deferred_invocation is None else dict(receipt.deferred_invocation),
    }


def _parse_receipt(value: Mapping[str, object]) -> CompletionReceipt:
    keys = (
        "schema_version",
        "repository_key",
        "tuple_key",
        "operation_generation",
        "operation",
        "candidate_digest",
        "seed_policy",
        "result_family",
        "terminal_record_digest",
        "cleanup_token",
        "cleanup_retry_invocation",
        "deferred_invocation",
    )
    _exact(value, keys, "CLEANUP-COMPLETED")
    if value["schema_version"] != 1:
        _fail("receipt schema_version must be 1")
    repository_key = _digest(value["repository_key"], "receipt.repository_key")
    tuple_key = _digest(value["tuple_key"], "receipt.tuple_key")
    generation = _generation(value["operation_generation"], "receipt.operation_generation")
    operation = _string(value["operation"], "receipt.operation")
    if operation not in {"install", "update", "uninstall"}:
        _fail("receipt operation is invalid")
    digest = _digest(value["candidate_digest"], "receipt.candidate_digest")
    seed = _string(value["seed_policy"], "receipt.seed_policy")
    if seed not in {"create-if-absent", "preserve-only"}:
        _fail("receipt seed_policy is invalid")
    family = _string(value["result_family"], "receipt.result_family")
    if family not in {"install", "legacy-migration", "update", "uninstall"}:
        _fail("receipt result_family is invalid")
    terminal = _digest(value["terminal_record_digest"], "receipt.terminal_record_digest")
    token = _digest(value["cleanup_token"], "receipt.cleanup_token")
    cleanup = _invocation(value["cleanup_retry_invocation"], "receipt.cleanup_retry_invocation", cleanup=True)
    deferred = (
        None
        if value["deferred_invocation"] is None
        else _invocation(value["deferred_invocation"], "receipt.deferred_invocation")
    )
    assert (
        repository_key is not None
        and tuple_key is not None
        and digest is not None
        and terminal is not None
        and token is not None
    )
    assert family is not None
    if tuple_key_for(cast("str", operation), cast("str", digest), cast("str", seed)) != tuple_key:
        _fail("receipt tuple_key does not match operation identity")
    if cleanup_token_for(repository_key, tuple_key, cast("str", family), generation) != token:
        _fail("receipt cleanup token does not match identity")
    return CompletionReceipt(
        1,
        repository_key,
        tuple_key,
        generation,
        cast("Operation", operation),
        digest,
        cast("SeedPolicy", seed),
        cast("Literal['install', 'legacy-migration', 'update', 'uninstall']", family),
        terminal,
        token,
        cleanup,
        deferred,
    )


def _owner_mapping(owner: StageOwner) -> dict[str, object]:
    return {
        "schema_version": owner.schema_version,
        "repository_key": owner.repository_key,
        "tuple_key": owner.tuple_key,
        "operation_generation": owner.operation_generation,
        "operation": owner.operation,
        "candidate_digest": owner.candidate_digest,
        "seed_policy": owner.seed_policy,
        "result_family": owner.result_family,
        "entry_names": list(owner.entry_names),
        "candidate_domain_digests": list(owner.candidate_domain_digests),
        "original_domain_digests": list(owner.original_domain_digests),
    }


def _parse_owner(value: Mapping[str, object]) -> StageOwner:
    keys = (
        "schema_version",
        "repository_key",
        "tuple_key",
        "operation_generation",
        "operation",
        "candidate_digest",
        "seed_policy",
        "result_family",
        "entry_names",
        "candidate_domain_digests",
        "original_domain_digests",
    )
    _exact(value, keys, "STAGE-OWNER")
    if value["schema_version"] != 1:
        _fail("STAGE-OWNER schema_version must be 1")
    repository_key = _digest(value["repository_key"], "STAGE-OWNER.repository_key")
    tuple_key = _digest(value["tuple_key"], "STAGE-OWNER.tuple_key")
    generation = _generation(value["operation_generation"], "STAGE-OWNER.operation_generation")
    operation = _string(value["operation"], "STAGE-OWNER.operation")
    if operation not in {"install", "update", "uninstall"}:
        _fail("STAGE-OWNER operation is invalid")
    candidate_digest = _digest(value["candidate_digest"], "STAGE-OWNER.candidate_digest")
    seed = _string(value["seed_policy"], "STAGE-OWNER.seed_policy")
    if seed not in {"create-if-absent", "preserve-only"}:
        _fail("STAGE-OWNER seed_policy is invalid")
    family = _string(value["result_family"], "STAGE-OWNER.result_family")
    if family not in {"install", "legacy-migration", "update", "uninstall"}:
        _fail("STAGE-OWNER result_family is invalid")
    names = value["entry_names"]
    if not isinstance(names, list) or tuple(names) != STAGE_ENTRY_NAMES:
        _fail("STAGE-OWNER entry_names are not fixed")
    candidate_digests = value["candidate_domain_digests"]
    original_digests = value["original_domain_digests"]
    if (
        not isinstance(candidate_digests, list)
        or len(candidate_digests) != 6
        or not isinstance(original_digests, list)
        or len(original_digests) != 6
    ):
        _fail("STAGE-OWNER domain digest arrays must contain six entries")
    for item in [*candidate_digests, *original_digests]:
        _digest(item, "STAGE-OWNER domain digest", allow_null=True)
    assert repository_key is not None and tuple_key is not None and candidate_digest is not None
    return StageOwner(
        1,
        repository_key,
        tuple_key,
        generation,
        cast("Operation", operation),
        candidate_digest,
        cast("SeedPolicy", seed),
        cast("Literal['install', 'legacy-migration', 'update', 'uninstall']", family),
        tuple(names),
        tuple(candidate_digests),
        tuple(original_digests),
    )  # type: ignore[arg-type]


class _PrivateStore:
    filename: str
    maximum: int
    mode: int

    def __init__(
        self,
        namespace: str | os.PathLike[str],
        filename: str,
        maximum: int,
        mode: int,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        repository_root_fd: int | None = None,
        repository_root_binding: tuple[int, int] | None = None,
    ) -> None:
        if repository_root is not None and repository_root_fd is not None:
            raise ValueError("repository_root and repository_root_fd are mutually exclusive")
        if repository_root_fd is None and repository_root_binding is not None:
            raise ValueError("repository_root_binding requires repository_root_fd")
        self.namespace = Path(namespace)
        self.filename = filename
        self.maximum = maximum
        self.mode = mode
        self.repository_root = None if repository_root is None else Path(repository_root)
        self.repository_root_fd = repository_root_fd
        self.repository_root_binding = repository_root_binding

    def _open_namespace(self) -> int:
        if not self.namespace.is_absolute():
            raise PrivateStateError("private namespace must be absolute")
        try:
            if self.repository_root is None:
                if self.repository_root_fd is None:
                    fd = _open_absolute_directory_no_follow(self.namespace)
                else:
                    opened_namespace = _open_private_namespace_at(
                        self.repository_root_fd,
                        self.namespace,
                        expected_binding=self.repository_root_binding,
                    )
                    assert opened_namespace is not None
                    fd = opened_namespace
            else:
                opened_namespace = _open_private_namespace(self.repository_root, self.namespace)
                assert opened_namespace is not None
                fd = opened_namespace
        except OSError as exc:
            raise PrivateStateError("private namespace cannot be opened") from exc
        try:
            opened = os.fstat(fd)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or opened.st_nlink < 2
                or opened.st_uid != _effective_euid()
                or stat.S_IMODE(opened.st_mode) != PRIVATE_DIRECTORY_MODE
            ):
                raise PrivateStateForeignError("private namespace directory is unsafe")
            names = os.listdir(fd)  # noqa: PTH208
            if any(name not in PRIVATE_ENTRY_NAMES for name in names):
                raise PrivateStateForeignError("private namespace contains an unknown entry")
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _read_bytes(
        self, filename: str | None = None, maximum: int | None = None, mode: int | None = None
    ) -> bytes | None:
        name = self.filename if filename is None else filename
        maximum = self.maximum if maximum is None else maximum
        mode = self.mode if mode is None else mode
        fd = self._open_namespace()
        try:
            try:
                value = os.stat(name, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                return None
            if (
                not stat.S_ISREG(value.st_mode)
                or value.st_nlink != 1
                or value.st_uid != _effective_euid()
                or stat.S_IMODE(value.st_mode) != mode
            ):
                raise PrivateStateForeignError(f"private object {name} is unsafe")
            if value.st_size > maximum:
                raise PrivateStateForeignError(f"private object {name} is oversized")
            object_fd = os.open(
                name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), dir_fd=fd
            )
            try:
                opened = os.fstat(object_fd)
                if (
                    opened.st_dev != value.st_dev
                    or opened.st_ino != value.st_ino
                    or opened.st_ctime_ns != value.st_ctime_ns
                ):
                    raise PrivateStateForeignError(f"private object {name} changed while opening")
                data = os.read(object_fd, maximum + 1)
                after = os.fstat(object_fd)
                if (
                    after.st_dev != opened.st_dev
                    or after.st_ino != opened.st_ino
                    or after.st_ctime_ns != opened.st_ctime_ns
                    or len(data) > maximum
                ):
                    raise PrivateStateForeignError(f"private object {name} changed while reading")
                return data
            finally:
                os.close(object_fd)
        finally:
            os.close(fd)

    def _publish_bytes(
        self,
        payload: bytes,
        *,
        filename: str | None = None,
        temporary: str | None = None,
        mode: int | None = None,
        maximum: int | None = None,
        expected_existing: InodeWitness | None = None,
        fault: Callable[[str], None] | None = None,
        fault_prefix: str | None = None,
    ) -> None:
        name = self.filename if filename is None else filename
        temporary = f"{name}.tmp" if temporary is None else temporary
        mode = self.mode if mode is None else mode
        maximum = self.maximum if maximum is None else maximum
        if len(payload) > maximum:
            raise PrivateStateError(f"{name} payload is oversized")
        namespace_fd = self._open_namespace()
        filesystem = NativeAtomicFilesystem()
        temporary_fd = -1
        try:
            if fault is not None and fault_prefix is not None:
                fault(f"{fault_prefix}-temp-open")
            existing_temporary = self._read_bound_witness(namespace_fd, temporary, mode, maximum=maximum)
            if (
                existing_temporary is not None
                and self._read_bound_bytes(
                    namespace_fd,
                    temporary,
                    mode,
                    maximum=maximum,
                    expected=existing_temporary,
                )
                != payload
            ):
                filesystem.unlink_bound(namespace_fd, temporary, existing_temporary)
                filesystem.fsync_directory(namespace_fd)
                existing_temporary = None
            if existing_temporary is None:
                try:
                    temporary_fd = os.open(
                        temporary,
                        os.O_WRONLY
                        | os.O_CREAT
                        | os.O_EXCL
                        | getattr(os, "O_NOFOLLOW", 0)
                        | getattr(os, "O_CLOEXEC", 0),
                        mode,
                        dir_fd=namespace_fd,
                    )
                except FileExistsError as exc:
                    raise PrivateStateForeignError(f"private temporary object {temporary} changed during open") from exc
                os.fchmod(temporary_fd, mode)
                if fault is not None and fault_prefix is not None:
                    fault(f"{fault_prefix}-temp-write")
                cursor = 0
                while cursor < len(payload):
                    cursor += os.write(temporary_fd, payload[cursor:])
            if fault is not None and fault_prefix is not None:
                fault(f"{fault_prefix}-temp-fsync")
            if temporary_fd < 0:
                temporary_fd = os.open(
                    temporary,
                    os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=namespace_fd,
                )
            os.fsync(temporary_fd)
            os.close(temporary_fd)
            temporary_fd = -1
            temporary_witness = self._read_bound_witness(namespace_fd, temporary, mode, maximum=maximum)
            if temporary_witness is None:
                raise PrivateStateError(f"private temporary object {temporary} disappeared before publication")
            existing = self._read_bound_witness(namespace_fd, name, mode, maximum=maximum)
            if expected_existing is not None and existing is None:
                raise PrivateStateForeignError(f"private object {name} disappeared during update")
            if fault is not None and fault_prefix is not None:
                fault(f"{fault_prefix}-temp-rename")
            if existing is None:
                filesystem.rename_no_replace(
                    namespace_fd,
                    temporary,
                    namespace_fd,
                    name,
                    expected_source=temporary_witness,
                )
            else:
                if expected_existing is None or existing != expected_existing:
                    raise PrivateStateForeignError(f"private object {name} belongs to another operation")
                filesystem.exchange(
                    namespace_fd,
                    temporary,
                    namespace_fd,
                    name,
                    expected_source=temporary_witness,
                    expected_destination=expected_existing,
                )
                old = filesystem.capture_inode(namespace_fd, temporary, "regular")
                if old is None or not NativeAtomicFilesystem._same_content_identity(old, expected_existing):
                    raise PrivateStateForeignError(f"old private object {name} changed during exchange")
                filesystem.unlink_bound(namespace_fd, temporary, old)
            if fault is not None and fault_prefix is not None:
                fault(f"{fault_prefix}-parent-fsync")
            filesystem.fsync_directory(namespace_fd)
            durable = self._read_bound_witness(namespace_fd, name, mode, maximum=maximum)
            if durable is None or not NativeAtomicFilesystem._same_content_identity(durable, temporary_witness):
                raise PrivateStateForeignError(f"private object {name} changed after publication")
        finally:
            if temporary_fd >= 0:
                os.close(temporary_fd)
            os.close(namespace_fd)

    @staticmethod
    def _read_bound_witness(
        parent_fd: int,
        name: str,
        mode: int,
        *,
        maximum: int | None = None,
    ) -> InodeWitness | None:
        try:
            value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        if (
            not stat.S_ISREG(value.st_mode)
            or value.st_nlink != 1
            or value.st_uid != _effective_euid()
            or stat.S_IMODE(value.st_mode) != mode
        ):
            raise PrivateStateForeignError(f"private object {name} is unsafe")
        if maximum is not None and value.st_size > maximum:
            raise PrivateStateForeignError(f"private object {name} is oversized")
        object_fd = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        try:
            opened = os.fstat(object_fd)
            if not NativeAtomicFilesystem._same_inode(value, opened):
                raise PrivateStateForeignError(f"private object {name} changed while opening")
            digest = hashlib.sha256()
            while True:
                chunk = os.read(object_fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            after = os.fstat(object_fd)
            if not NativeAtomicFilesystem._same_inode(opened, after):
                raise PrivateStateForeignError(f"private object {name} changed while reading")
            return NativeAtomicFilesystem._witness(after, "regular", digest.hexdigest())
        finally:
            os.close(object_fd)

    def _current_witness(self) -> InodeWitness | None:
        namespace_fd = self._open_namespace()
        try:
            return self._read_bound_witness(namespace_fd, self.filename, self.mode, maximum=self.maximum)
        finally:
            os.close(namespace_fd)

    def ensure_durable(self, expected: InodeWitness | None = None) -> InodeWitness | None:
        """Re-establish namespace-entry durability before trusting visible state."""

        namespace_fd = self._open_namespace()
        try:
            current = self._read_bound_witness(namespace_fd, self.filename, self.mode, maximum=self.maximum)
            if expected is not None and current != expected:
                raise PrivateStateForeignError(f"private object {self.filename} changed before durability repair")
            os.fsync(namespace_fd)
            durable = self._read_bound_witness(namespace_fd, self.filename, self.mode, maximum=self.maximum)
            if expected is not None and durable != expected:
                raise PrivateStateForeignError(f"private object {self.filename} changed during durability repair")
            if current != durable:
                raise PrivateStateForeignError(f"private object {self.filename} changed during durability repair")
            return durable
        finally:
            os.close(namespace_fd)

    @staticmethod
    def _read_bound_bytes(
        parent_fd: int,
        name: str,
        mode: int,
        *,
        maximum: int | None = None,
        expected: InodeWitness | None = None,
    ) -> bytes:
        fd = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), dir_fd=parent_fd)
        try:
            opened = os.fstat(fd)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1
                or opened.st_uid != _effective_euid()
                or stat.S_IMODE(opened.st_mode) != mode
            ):
                raise PrivateStateForeignError(f"private object {name} is unsafe")
            if maximum is not None and opened.st_size > maximum:
                raise PrivateStateForeignError(f"private object {name} is oversized")
            if expected is not None and (
                opened.st_dev != expected.device
                or opened.st_ino != expected.inode
                or opened.st_ctime_ns != expected.ctime_ns
                or stat.S_IMODE(opened.st_mode) != expected.mode
                or opened.st_nlink != expected.link_count
                or opened.st_size != expected.size
            ):
                raise PrivateStateForeignError(f"private object {name} changed while opening")
            digest = hashlib.sha256()
            chunks: list[bytes] = []
            total = 0
            while True:
                limit = min(1024 * 1024, maximum + 1 - total) if maximum is not None else 1024 * 1024
                chunk = os.read(fd, limit)
                if not chunk:
                    break
                chunks.append(chunk)
                digest.update(chunk)
                total += len(chunk)
                if maximum is not None and total > maximum:
                    raise PrivateStateForeignError(f"private object {name} is oversized")
            after = os.fstat(fd)
            if not NativeAtomicFilesystem._same_inode(opened, after):
                raise PrivateStateForeignError(f"private object {name} changed while reading")
            data = b"".join(chunks)
            if expected is not None:
                current = NativeAtomicFilesystem._witness(after, "regular", digest.hexdigest())
                if not NativeAtomicFilesystem._same_content_identity(current, expected):
                    raise PrivateStateForeignError(f"private object {name} changed while reading")
            return data
        finally:
            os.close(fd)


def _effective_euid() -> int:
    return os.geteuid() if hasattr(os, "geteuid") else os.getuid()


def _open_private_namespace(
    repository_root: str | os.PathLike[str],
    namespace: str | os.PathLike[str],
    *,
    effective_euid: int | None = None,
    allow_missing: bool = False,
) -> int | None:
    """Open a namespace only after binding the complete private directory chain."""

    root = Path(repository_root)
    namespace_path = Path(namespace)
    if (
        not root.is_absolute()
        or not root.name
        or "\x00" in os.fspath(root)
        or not namespace_path.is_absolute()
        or "\x00" in os.fspath(namespace_path)
    ):
        raise PrivateStateError("repository/private namespace paths must be absolute and NUL-free")
    euid = _effective_euid() if effective_euid is None else effective_euid
    try:
        parent_fd = _open_absolute_directory_no_follow(root.parent)
    except OSError as exc:
        raise PrivateStateError("repository parent cannot be opened without following links") from exc
    top_fd: int | None = None
    namespace_fd: int | None = None
    try:
        parent_stat = os.fstat(parent_fd)
        try:
            root_stat = os.stat(root.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as exc:
            raise PrivateStateError("repository root cannot be opened without following links") from exc
        if (
            not stat.S_ISDIR(root_stat.st_mode)
            or not stat.S_ISDIR(parent_stat.st_mode)
            or parent_stat.st_dev != root_stat.st_dev
        ):
            raise PrivateStateError("repository root/parent binding is unsafe")
        if root_stat.st_uid != euid:
            raise PrivateStateError("repository root owner is not the effective user")

        repository_key = repository_key_for(root_stat.st_dev, root_stat.st_ino, euid)
        top_name = f"{PRIVATE_NAMESPACE_PREFIX}{euid}"
        expected_namespace = root.parent / top_name / repository_key
        if namespace_path != expected_namespace:
            raise PrivateStateForeignError("private namespace binding is unsafe")

        try:
            top_value = os.stat(top_name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as exc:
            if allow_missing:
                return None
            raise PrivateStateError("private namespace cannot be opened") from exc
        _check_private_directory(top_value, parent_stat.st_dev, euid)
        top_fd = os.open(top_name, _directory_open_flags(), dir_fd=parent_fd)
        opened_top = os.fstat(top_fd)
        if (opened_top.st_dev, opened_top.st_ino) != (top_value.st_dev, top_value.st_ino):
            raise PrivateStateForeignError("private top directory changed while opening")
        _check_private_directory(opened_top, parent_stat.st_dev, euid)

        try:
            namespace_value = os.stat(repository_key, dir_fd=top_fd, follow_symlinks=False)
        except FileNotFoundError as exc:
            if allow_missing:
                return None
            raise PrivateStateError("private namespace cannot be opened") from exc
        _check_private_directory(namespace_value, parent_stat.st_dev, euid)
        namespace_fd = os.open(repository_key, _directory_open_flags(), dir_fd=top_fd)
        opened_namespace = os.fstat(namespace_fd)
        if (opened_namespace.st_dev, opened_namespace.st_ino) != (
            namespace_value.st_dev,
            namespace_value.st_ino,
        ):
            raise PrivateStateForeignError("private namespace changed while opening")
        _check_private_directory(opened_namespace, parent_stat.st_dev, euid)
        result = namespace_fd
        namespace_fd = None
        return result
    finally:
        if namespace_fd is not None:
            os.close(namespace_fd)
        if top_fd is not None:
            os.close(top_fd)
        os.close(parent_fd)


def validate_private_namespace(
    repository_root: str | os.PathLike[str],
    namespace: str | os.PathLike[str],
    *,
    effective_euid: int | None = None,
) -> bool:
    """Validate the complete private namespace chain without creating or changing it."""

    fd = _open_private_namespace(
        repository_root,
        namespace,
        effective_euid=effective_euid,
        allow_missing=True,
    )
    if fd is None:
        return False
    os.close(fd)
    return True


def _open_private_namespace_at(
    repository_root_fd: int,
    namespace: str | os.PathLike[str],
    *,
    effective_euid: int | None = None,
    allow_missing: bool = False,
    create: bool = False,
    expected_binding: tuple[int, int] | None = None,
) -> int | None:
    """Open or create a private namespace from an already-bound root descriptor."""

    namespace_path = Path(namespace)
    if not namespace_path.is_absolute() or "\x00" in os.fspath(namespace_path):
        raise PrivateStateError("private namespace path must be absolute and NUL-free")
    euid = _effective_euid() if effective_euid is None else effective_euid
    try:
        root_stat = os.fstat(repository_root_fd)
        parent_fd = os.open("..", _directory_open_flags(), dir_fd=repository_root_fd)
    except OSError as exc:
        raise PrivateStateError("repository root/parent cannot be opened from the bound descriptor") from exc
    top_fd: int | None = None
    namespace_fd: int | None = None
    try:
        parent_stat = os.fstat(parent_fd)
        if (
            not stat.S_ISDIR(root_stat.st_mode)
            or not stat.S_ISDIR(parent_stat.st_mode)
            or parent_stat.st_dev != root_stat.st_dev
        ):
            raise PrivateStateError("repository root/parent binding is unsafe")
        if expected_binding is not None and (root_stat.st_dev, root_stat.st_ino) != expected_binding:
            raise PrivateStateError("repository root binding changed")
        if root_stat.st_uid != euid:
            raise PrivateStateError("repository root owner is not the effective user")

        repository_key = repository_key_for(root_stat.st_dev, root_stat.st_ino, euid)
        top_name = f"{PRIVATE_NAMESPACE_PREFIX}{euid}"
        if namespace_path.name != repository_key or namespace_path.parent.name != top_name:
            raise PrivateStateForeignError("private namespace binding is unsafe")

        if create:
            _mkdir_private(parent_fd, top_name, parent_stat.st_dev, euid)
        else:
            try:
                top_value = os.stat(top_name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                if allow_missing:
                    return None
                raise PrivateStateError("private namespace cannot be opened") from None
            _check_private_directory(top_value, parent_stat.st_dev, euid)
        top_fd = os.open(top_name, _directory_open_flags(), dir_fd=parent_fd)
        opened_top = os.fstat(top_fd)
        if not create and (opened_top.st_dev != top_value.st_dev or opened_top.st_ino != top_value.st_ino):
            raise PrivateStateForeignError("private top directory changed while opening")
        _check_private_directory(opened_top, parent_stat.st_dev, euid)

        if create:
            _mkdir_private(top_fd, repository_key, parent_stat.st_dev, euid)
        else:
            try:
                namespace_value = os.stat(repository_key, dir_fd=top_fd, follow_symlinks=False)
            except FileNotFoundError:
                if allow_missing:
                    return None
                raise PrivateStateError("private namespace cannot be opened") from None
            _check_private_directory(namespace_value, parent_stat.st_dev, euid)
        namespace_fd = os.open(repository_key, _directory_open_flags(), dir_fd=top_fd)
        opened_namespace = os.fstat(namespace_fd)
        if not create and (
            opened_namespace.st_dev != namespace_value.st_dev or opened_namespace.st_ino != namespace_value.st_ino
        ):
            raise PrivateStateForeignError("private namespace changed while opening")
        _check_private_directory(opened_namespace, parent_stat.st_dev, euid)
        result = namespace_fd
        namespace_fd = None
        return result
    finally:
        if namespace_fd is not None:
            os.close(namespace_fd)
        if top_fd is not None:
            os.close(top_fd)
        os.close(parent_fd)


def validate_private_namespace_at(
    repository_root_fd: int,
    namespace: str | os.PathLike[str],
    *,
    effective_euid: int | None = None,
    expected_binding: tuple[int, int] | None = None,
) -> bool:
    """Validate a private namespace without resolving the visible repository path."""

    fd = _open_private_namespace_at(
        repository_root_fd,
        namespace,
        effective_euid=effective_euid,
        allow_missing=True,
        expected_binding=expected_binding,
    )
    if fd is None:
        return False
    os.close(fd)
    return True


def resolve_private_namespace_at(
    repository_root_fd: int,
    namespace: str | os.PathLike[str],
    *,
    effective_euid: int | None = None,
    expected_binding: tuple[int, int] | None = None,
) -> Path:
    """Create a deterministic private namespace from an already-bound root descriptor."""

    fd = _open_private_namespace_at(
        repository_root_fd,
        namespace,
        effective_euid=effective_euid,
        create=True,
        expected_binding=expected_binding,
    )
    assert fd is not None
    os.close(fd)
    return Path(namespace)


def resolve_private_namespace(repository_root: str | os.PathLike[str], *, effective_euid: int | None = None) -> Path:
    """Create and return the deterministic same-filesystem private namespace."""

    root = Path(repository_root)
    if not root.is_absolute() or "\x00" in os.fspath(root):
        raise PrivateStateError("repository root must be absolute")
    if not root.name:
        raise PrivateStateError("repository root must have a final directory component")
    euid = _effective_euid() if effective_euid is None else effective_euid
    try:
        parent_fd = _open_absolute_directory_no_follow(root.parent)
    except OSError as exc:
        raise PrivateStateError("repository parent cannot be opened without following links") from exc
    try:
        parent_stat = os.fstat(parent_fd)
        root_stat = os.stat(root.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISDIR(root_stat.st_mode)
            or not stat.S_ISDIR(parent_stat.st_mode)
            or parent_stat.st_dev != root_stat.st_dev
        ):
            raise PrivateStateError("repository root/parent binding is unsafe")
        if root_stat.st_uid != euid:
            raise PrivateStateError("repository root owner is not the effective user")
        repository_key = repository_key_for(root_stat.st_dev, root_stat.st_ino, euid)
        top_name = f"{PRIVATE_NAMESPACE_PREFIX}{euid}"
        _mkdir_private(parent_fd, top_name, parent_stat.st_dev, euid)
        top_fd = os.open(
            top_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        try:
            top_stat = os.fstat(top_fd)
            _check_private_directory(top_stat, parent_stat.st_dev, euid)
            _mkdir_private(top_fd, repository_key, parent_stat.st_dev, euid)
            namespace_fd = os.open(
                repository_key,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=top_fd,
            )
            try:
                namespace_stat = os.fstat(namespace_fd)
                _check_private_directory(namespace_stat, parent_stat.st_dev, euid)
            finally:
                os.close(namespace_fd)
        finally:
            os.close(top_fd)
        return root.parent / top_name / repository_key
    finally:
        os.close(parent_fd)


def _check_private_directory(value: os.stat_result, device: int, euid: int) -> None:
    if (
        not stat.S_ISDIR(value.st_mode)
        or value.st_dev != device
        or value.st_uid != euid
        or stat.S_IMODE(value.st_mode) != PRIVATE_DIRECTORY_MODE
    ):
        raise PrivateStateForeignError("private directory binding is unsafe")


def _mkdir_private(parent_fd: int, name: str, device: int, euid: int) -> None:
    try:
        os.mkdir(name, PRIVATE_DIRECTORY_MODE, dir_fd=parent_fd)
    except FileExistsError:
        pass
    except OSError as exc:
        raise PrivateStateError(f"cannot create private directory {name}") from exc
    try:
        os.fsync(parent_fd)
    except OSError as exc:
        raise PrivateStateError(f"cannot persist private directory {name}") from exc
    fd = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    try:
        _check_private_directory(os.fstat(fd), device, euid)
    finally:
        os.close(fd)


class ActiveStateStore(_PrivateStore):
    """Strict ACTIVE.json store and public RECORD-TEMP staging seam."""

    def __init__(
        self,
        namespace: str | os.PathLike[str],
        *,
        repository_root: str | os.PathLike[str] | None = None,
        repository_root_fd: int | None = None,
        repository_root_binding: tuple[int, int] | None = None,
    ) -> None:
        namespace_path = _coerce_namespace(namespace)
        super().__init__(
            namespace_path,
            ACTIVE_NAME,
            32768,
            PRIVATE_METADATA_MODE,
            repository_root=repository_root,
            repository_root_fd=repository_root_fd,
            repository_root_binding=repository_root_binding,
        )

    def load(self) -> ActiveState | None:
        raw = self._read_bytes()
        return None if raw is None else _parse_active(_read_json_bytes(raw, self.maximum, "ACTIVE"))

    read = load

    def save(self, state: ActiveState, *, fault: Callable[[str], None] | None = None) -> None:
        value = _active_mapping(state)
        parsed = _parse_active(value)
        existing = self.load()
        expected_existing = None
        if existing is not None:
            if (
                existing.repository_key,
                existing.tuple_key,
                existing.operation_generation,
                existing.operation,
                existing.candidate_digest,
                existing.seed_policy,
                existing.result_family,
            ) != (
                parsed.repository_key,
                parsed.tuple_key,
                parsed.operation_generation,
                parsed.operation,
                parsed.candidate_digest,
                parsed.seed_policy,
                parsed.result_family,
            ):
                raise PrivateStateForeignError("ACTIVE belongs to another operation")
            expected_existing = self._current_witness()
            if expected_existing is None:
                raise PrivateStateForeignError("ACTIVE disappeared before update")
        self._publish_bytes(
            _json_bytes(_active_mapping(parsed)),
            expected_existing=expected_existing,
            fault=fault,
            fault_prefix="active",
        )

    write = save

    def write_record_temp(
        self,
        payload: bytes,
        *,
        fault: Callable[[str], None] | None = None,
    ) -> InodeWitness:
        record = parse_installation_record(payload)
        canonical = serialize_installation_record(record)
        if payload != canonical:
            raise PrivateStateError("RECORD-TEMP must contain canonical public record bytes")
        namespace_fd = self._open_namespace()
        created_temp = False
        try:
            try:
                if fault is not None:
                    fault("record-temp-open")
                fd = os.open(
                    RECORD_TEMP_NAME,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    RECORD_TEMP_MODE,
                    dir_fd=namespace_fd,
                )
                created_temp = True
            except FileExistsError:
                existing = self._read_bound_witness(
                    namespace_fd,
                    RECORD_TEMP_NAME,
                    RECORD_TEMP_MODE,
                    maximum=4096,
                )
                active = self.load()
                existing_payload = (
                    None
                    if existing is None
                    else self._read_bound_bytes(
                        namespace_fd,
                        RECORD_TEMP_NAME,
                        RECORD_TEMP_MODE,
                        maximum=4096,
                        expected=existing,
                    )
                )
                if existing is None or active is None:
                    raise PrivateStateForeignError("existing RECORD-TEMP is not the expected public record") from None
                if existing_payload == payload and active.record_temp_witness == existing:
                    if fault is not None:
                        fault("record-temp-parent-fsync")
                    os.fsync(namespace_fd)
                    return existing
                original = active.original_record
                original_payload = original.get("bytes_base64")
                original_witness = original.get("witness")
                if not (
                    isinstance(original_payload, str)
                    and original_witness == _inode_mapping(existing)
                    and existing_payload == base64.b64decode(original_payload)
                ):
                    raise PrivateStateForeignError("existing RECORD-TEMP is not the expected public record") from None
                NativeAtomicFilesystem().unlink_bound(namespace_fd, RECORD_TEMP_NAME, existing)
                os.fsync(namespace_fd)
                fd = os.open(
                    RECORD_TEMP_NAME,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    RECORD_TEMP_MODE,
                    dir_fd=namespace_fd,
                )
                created_temp = True
            try:
                if fault is not None:
                    fault("record-temp-write")
                cursor = 0
                while cursor < len(payload):
                    cursor += os.write(fd, payload[cursor:])
                os.fchmod(fd, RECORD_TEMP_MODE)
                if fault is not None:
                    fault("record-temp-fsync")
                os.fsync(fd)
            finally:
                os.close(fd)
            if fault is not None:
                fault("record-temp-parent-fsync")
            os.fsync(namespace_fd)
            witness = self._read_bound_witness(
                namespace_fd,
                RECORD_TEMP_NAME,
                RECORD_TEMP_MODE,
                maximum=4096,
            )
            if witness is None:
                raise PrivateStateError("RECORD-TEMP disappeared after publication")
            return witness
        except BaseException as failure:
            if created_temp:
                try:
                    residue = self._read_bound_witness(
                        namespace_fd,
                        RECORD_TEMP_NAME,
                        RECORD_TEMP_MODE,
                        maximum=4096,
                    )
                    if residue is not None:
                        NativeAtomicFilesystem().unlink_bound(namespace_fd, RECORD_TEMP_NAME, residue)
                        os.fsync(namespace_fd)
                except BaseException as cleanup_failure:
                    raise PrivateStateError("RECORD-TEMP cleanup failed after publication error") from cleanup_failure
            raise failure
        finally:
            os.close(namespace_fd)

    def load_record_temp(self) -> bytes | None:
        return self._read_bytes(RECORD_TEMP_NAME, 4096, RECORD_TEMP_MODE)


class CompletionReceiptStore(_PrivateStore):
    """Strict completion receipt store."""

    def __init__(
        self,
        namespace: str | os.PathLike[str],
        *,
        repository_root: str | os.PathLike[str] | None = None,
        repository_root_fd: int | None = None,
        repository_root_binding: tuple[int, int] | None = None,
    ) -> None:
        namespace_path = _coerce_namespace(namespace)
        super().__init__(
            namespace_path,
            RECEIPT_NAME,
            16384,
            PRIVATE_METADATA_MODE,
            repository_root=repository_root,
            repository_root_fd=repository_root_fd,
            repository_root_binding=repository_root_binding,
        )

    def load(self) -> CompletionReceipt | None:
        raw = self._read_bytes()
        return None if raw is None else _parse_receipt(_read_json_bytes(raw, self.maximum, "CLEANUP-COMPLETED"))

    read = load

    def save(self, receipt: CompletionReceipt, *, fault: Callable[[str], None] | None = None) -> None:
        value = _receipt_mapping(receipt)
        parsed = _parse_receipt(value)
        existing = self.load()
        expected_existing = None
        if existing is not None:
            if (
                existing.repository_key,
                existing.tuple_key,
                existing.operation_generation,
                existing.operation,
                existing.candidate_digest,
                existing.seed_policy,
                existing.result_family,
            ) != (
                parsed.repository_key,
                parsed.tuple_key,
                parsed.operation_generation,
                parsed.operation,
                parsed.candidate_digest,
                parsed.seed_policy,
                parsed.result_family,
            ):
                raise PrivateStateForeignError("completion receipt belongs to another operation")
            expected_existing = self._current_witness()
            if expected_existing is None:
                raise PrivateStateForeignError("completion receipt disappeared before update")
        self._publish_bytes(
            _json_bytes(_receipt_mapping(parsed)),
            expected_existing=expected_existing,
            fault=fault,
            fault_prefix="receipt",
        )

    write = save


class StageStore:
    """Fixed six-entry stage ownership with P1 rebuild/P2 reuse semantics."""

    def __init__(
        self,
        namespace: str | os.PathLike[str],
        active_store: ActiveStateStore | None = None,
        *,
        repository_root: str | os.PathLike[str] | None = None,
        repository_root_fd: int | None = None,
        repository_root_binding: tuple[int, int] | None = None,
    ) -> None:
        self.namespace = _coerce_namespace(namespace)
        self.active_store = active_store
        self.repository_root = None if repository_root is None else Path(repository_root)
        self.repository_root_fd = repository_root_fd
        self.repository_root_binding = repository_root_binding
        if self.repository_root is not None and self.repository_root_fd is not None:
            raise ValueError("repository_root and repository_root_fd are mutually exclusive")
        if self.repository_root_fd is None and self.repository_root_binding is not None:
            raise ValueError("repository_root_binding requires repository_root_fd")
        self.write_count = 0

    def _namespace_fd(self) -> int:
        return _PrivateStore(
            self.namespace,
            "",
            1,
            PRIVATE_METADATA_MODE,
            repository_root=self.repository_root,
            repository_root_fd=self.repository_root_fd,
            repository_root_binding=self.repository_root_binding,
        )._open_namespace()

    def _ensure_stage(self, fault: Callable[[str], None] | None = None) -> None:
        namespace_fd = self._namespace_fd()
        try:
            try:
                os.stat(STAGE_NAME, dir_fd=namespace_fd, follow_symlinks=False)
            except FileNotFoundError:
                if fault is not None:
                    fault("stage-mkdir")
                with contextlib.suppress(FileExistsError):
                    os.mkdir(STAGE_NAME, PRIVATE_DIRECTORY_MODE, dir_fd=namespace_fd)
            os.fsync(namespace_fd)
            stage_fd = os.open(
                STAGE_NAME,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=namespace_fd,
            )
            try:
                value = os.fstat(stage_fd)
                _check_private_directory(value, os.fstat(namespace_fd).st_dev, _effective_euid())
            finally:
                os.close(stage_fd)
        finally:
            os.close(namespace_fd)

    def _stage_fd(self) -> int:
        namespace_fd = self._namespace_fd()
        stage_fd: int | None = None
        try:
            stage_fd = os.open(
                STAGE_NAME,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=namespace_fd,
            )
            try:
                _check_private_directory(os.fstat(stage_fd), os.fstat(namespace_fd).st_dev, _effective_euid())
            except BaseException:
                os.close(stage_fd)
                stage_fd = None
                raise
            return stage_fd
        except FileNotFoundError as exc:
            raise PrivateStateError("STAGE is not durable") from exc
        finally:
            os.close(namespace_fd)

    def _read_owner_bytes(self) -> bytes | None:
        try:
            stage_fd = self._stage_fd()
        except PrivateStateForeignError:
            raise
        except PrivateStateError:
            return None
        try:
            try:
                value = os.stat(STAGE_OWNER_NAME, dir_fd=stage_fd, follow_symlinks=False)
            except FileNotFoundError:
                return None
            if (
                not stat.S_ISREG(value.st_mode)
                or value.st_uid != _effective_euid()
                or value.st_nlink != 1
                or stat.S_IMODE(value.st_mode) != PRIVATE_METADATA_MODE
            ):
                raise PrivateStateForeignError("STAGE-OWNER.json is unsafe")
            fd = os.open(
                STAGE_OWNER_NAME,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                dir_fd=stage_fd,
            )
            try:
                raw = os.read(fd, 8193)
            finally:
                os.close(fd)
            if len(raw) > 8192:
                raise PrivateStateForeignError("STAGE-OWNER.json is oversized")
            return raw
        finally:
            os.close(stage_fd)

    def load_owner(self) -> StageOwner | None:
        raw = self._read_owner_bytes()
        return None if raw is None else _parse_owner(_read_json_bytes(raw, 8192, "STAGE-OWNER"))

    read_owner = load_owner

    def _validate_stage_entries(self) -> tuple[str, ...]:
        stage_fd = self._stage_fd()
        try:
            names = tuple(sorted(os.listdir(stage_fd), key=lambda name: os.fsencode(name)))  # noqa: PTH208
            allowed = {STAGE_OWNER_NAME, *STAGE_ENTRY_NAMES}
            if any(name not in allowed for name in names):
                raise PrivateStateForeignError("STAGE contains an unknown entry")
            for name in names:
                if name == STAGE_OWNER_NAME:
                    continue
                value = os.stat(name, dir_fd=stage_fd, follow_symlinks=False)
                if (
                    not stat.S_ISDIR(value.st_mode)
                    or value.st_uid != _effective_euid()
                    or stat.S_IMODE(value.st_mode) != PRIVATE_DIRECTORY_MODE
                ):
                    raise PrivateStateForeignError(f"stage entry {name} is unsafe")
            return tuple(name for name in STAGE_ENTRY_NAMES if name in names)
        finally:
            os.close(stage_fd)

    def _require_prepared_active(self) -> ActiveState:
        if self.active_store is None:
            raise PrivateStateError("stage writes require an ActiveStateStore binding")
        active = self.active_store.load()
        if active is None or active.state not in {"prepared", "running", "ready", "terminal-cleanup"}:
            raise PrivateStateError("durable ACTIVE must precede stage writes")
        return active

    def save_owner(self, owner: StageOwner, *, fault: Callable[[str], None] | None = None) -> None:
        self._require_prepared_active()
        self._ensure_stage(fault)
        value = _owner_mapping(owner)
        parsed = _parse_owner(value)
        existing_owner = self.load_owner()
        if existing_owner is not None:
            if existing_owner != parsed:
                raise PrivateStateForeignError("STAGE-OWNER.json belongs to another operation")
            stage_fd = self._stage_fd()
            try:
                os.fsync(stage_fd)
            finally:
                os.close(stage_fd)
            return
        payload = _json_bytes(_owner_mapping(parsed))
        if len(payload) > 8192:
            raise PrivateStateError("STAGE-OWNER is oversized")
        stage_fd = self._stage_fd()
        try:
            if fault is not None:
                fault("stage-owner-write")
            fd = os.open(
                STAGE_OWNER_NAME,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                PRIVATE_METADATA_MODE,
                dir_fd=stage_fd,
            )
            try:
                cursor = 0
                while cursor < len(payload):
                    cursor += os.write(fd, payload[cursor:])
                if fault is not None:
                    fault("stage-owner-fsync")
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(stage_fd)
            self.write_count += 1
        except FileExistsError as exc:
            raise PrivateStateForeignError("STAGE-OWNER.json already exists") from exc
        finally:
            os.close(stage_fd)

    @staticmethod
    def _owner_exists(stage_fd: int) -> bool:
        try:
            os.stat(STAGE_OWNER_NAME, dir_fd=stage_fd, follow_symlinks=False)
            return True
        except FileNotFoundError:
            return False

    def ensure_registered_entries(
        self,
        names: Sequence[str] = STAGE_ENTRY_NAMES,
        *,
        fault: Callable[[str], None] | None = None,
    ) -> None:
        self._require_prepared_active()
        self._ensure_stage(fault)
        if any(name not in STAGE_ENTRY_NAMES for name in names):
            raise PrivateStateError("stage rebuild attempted an unregistered entry")
        stage_fd = self._stage_fd()
        try:
            for name in names:
                try:
                    os.mkdir(name, PRIVATE_DIRECTORY_MODE, dir_fd=stage_fd)
                except FileExistsError:
                    value = os.stat(name, dir_fd=stage_fd, follow_symlinks=False)
                    if (
                        not stat.S_ISDIR(value.st_mode)
                        or value.st_uid != _effective_euid()
                        or stat.S_IMODE(value.st_mode) != PRIVATE_DIRECTORY_MODE
                    ):
                        raise PrivateStateForeignError(f"stage entry {name} is unsafe") from None
                else:
                    self.write_count += 1
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)

    def ensure_durable(self, owner: StageOwner) -> None:
        """Re-fsync a complete stage before reusing it after an interrupted I/O."""

        self.require_valid(owner)
        stage_fd = self._stage_fd()
        try:
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)
        self.require_valid(owner)

    def reuse_if_valid(self, owner: StageOwner) -> bool:
        current = self.load_owner()
        if current is None or current != owner:
            return False
        entries = self._validate_stage_entries()
        return entries == STAGE_ENTRY_NAMES

    def inspect(self, owner: StageOwner) -> tuple[Literal["absent", "incomplete", "complete"], tuple[str, ...]]:
        """Classify the fixed stage without creating or changing any entry."""

        namespace_fd = self._namespace_fd()
        try:
            try:
                value = os.stat(STAGE_NAME, dir_fd=namespace_fd, follow_symlinks=False)
            except FileNotFoundError:
                return "absent", ()
            _check_private_directory(value, os.fstat(namespace_fd).st_dev, _effective_euid())
        finally:
            os.close(namespace_fd)

        current = self.load_owner()
        entries = self._validate_stage_entries()
        if current is not None and current != owner:
            raise PrivateStateForeignError("STAGE-OWNER.json belongs to another operation")
        return ("complete" if current == owner and entries == STAGE_ENTRY_NAMES else "incomplete"), entries

    def require_valid(self, owner: StageOwner) -> None:
        """Validate prepared-stage authority without changing private state."""

        current = self.load_owner()
        if current is None:
            raise PrivateStateForeignError("STAGE-OWNER.json is missing")
        if current != owner:
            raise PrivateStateForeignError("STAGE-OWNER.json belongs to another operation")
        if self._validate_stage_entries() != STAGE_ENTRY_NAMES:
            raise PrivateStateForeignError("STAGE entries are incomplete")

    def rebuild_registered_entries(
        self,
        owner: StageOwner,
        registered_names: Sequence[str] = STAGE_ENTRY_NAMES,
        builder: Callable[[str, int], None] | None = None,
    ) -> None:
        """Rebuild only already-registered names; P2 reuse never reaches this method."""

        self._require_prepared_active()
        if tuple(registered_names) != STAGE_ENTRY_NAMES or any(
            name not in STAGE_ENTRY_NAMES for name in registered_names
        ):
            raise PrivateStateError("stage rebuild names are not the fixed registered set")
        self.ensure_registered_entries(registered_names)
        self.save_owner(owner)
        stage_fd = self._stage_fd()
        try:
            for name in registered_names:
                if builder is not None:
                    builder(name, stage_fd)
            os.fsync(stage_fd)
        finally:
            os.close(stage_fd)


def _coerce_namespace(value: str | os.PathLike[str]) -> Path:
    path = Path(value)
    if not path.is_absolute():
        return resolve_private_namespace(path)
    if path.name == "STAGE":
        path = path.parent
    if re.fullmatch(r"[0-9a-f]{64}", path.name) and path.parent.name.startswith(PRIVATE_NAMESPACE_PREFIX):
        return path
    return resolve_private_namespace(path)


__all__ = [
    "ACTIVE_NAME",
    "PRIVATE_ENTRY_NAMES",
    "RECEIPT_NAME",
    "RECORD_TEMP_NAME",
    "STAGE_ENTRY_NAMES",
    "ActiveStateStore",
    "CompletionReceiptStore",
    "PrivateStateError",
    "PrivateStateForeignError",
    "StageStore",
    "cleanup_token_for",
    "repository_key_for",
    "resolve_private_namespace",
    "resolve_private_namespace_at",
    "tuple_key_for",
    "validate_private_namespace",
    "validate_private_namespace_at",
]
