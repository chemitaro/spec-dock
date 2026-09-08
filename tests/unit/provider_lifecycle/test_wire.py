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
