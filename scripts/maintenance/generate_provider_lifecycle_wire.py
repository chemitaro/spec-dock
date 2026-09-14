#!/usr/bin/env python3
"""Project the normative provider lifecycle wire artifact into Python.

This is a development-time generator.  Runtime code imports only the
generated module and never reads the parent artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DEFAULT = REPOSITORY_ROOT / "spec-dock" / "active" / "epic" / "artifacts" / "provider-lifecycle-wire-contract.md"
OUTPUT_DEFAULT = REPOSITORY_ROOT / "src" / "spec_dock" / "provider_lifecycle" / "_wire_generated.py"
EXPECTED_COUNTS = {
    "status": 6,
    "code": 41,
    "phase": 23,
    "last_completed_phase": 24,
    "relation": 168,
    "public_golden": 40,
    "record_golden": 4,
}


class GeneratorError(ValueError):
    """Raised when the normative artifact is not the expected closed shape."""


def _section(text: str, start: str, end: str) -> str:
    try:
        start_at = text.index(start)
        end_at = text.index(end, start_at + len(start))
    except ValueError as exc:
        raise GeneratorError(f"missing artifact section: {start!r} -> {end!r}") from exc
    return text[start_at:end_at]


def _cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value


def _table_rows(section: str, expected_columns: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| ---"):
            continue
        cells = [_cell(part) for part in line.strip().strip("|").split("|")]
        if len(cells) == expected_columns and cells[0] not in {
            "Code",
            "Item",
            "Rank",
            "Order",
            "Status",
        }:
            rows.append(cells)
    return rows


def _json_fences(section: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for match in re.finditer(r"```json\n([^\n]+)\n```", section):
        raw = match.group(1)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GeneratorError(f"invalid JSON golden: {exc}") from exc
        if not isinstance(value, dict):
            raise GeneratorError("JSON golden is not an object")
        canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if canonical != raw:
            raise GeneratorError("JSON golden is not canonical compact JSON")
        result.append(value)
    return result


def _parse_phases(section: str) -> list[str]:
    match = re.search(r"```text\n(.*?)\n```", section, flags=re.DOTALL)
    if match is None:
        raise GeneratorError("missing exact phase enum fence")
    values = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if values != [
        "request-validation",
        "preflight",
        "candidate-staging",
        "bootstrap-container",
        "publish-incomplete-record",
        "publish-docs",
        "publish-templates",
        "publish-system",
        "publish-scripts",
        "publish-slot-spec-dock",
        "publish-slot-spec-dock-grill-with-docs",
        "create-seed-spec-dock-gitignore",
        "create-seed-consumer-ci",
        "detach-docs",
        "detach-templates",
        "detach-system",
        "detach-scripts",
        "detach-slot-spec-dock",
        "detach-slot-spec-dock-grill-with-docs",
        "verify-target",
        "publish-terminal-record",
        "cleanup-stage",
        "complete",
    ]:
        raise GeneratorError("phase enum drifted from the approved Wire v12 list")
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def _parse_source(source: Path) -> dict[str, Any]:
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    source_id_match = re.search(r'^ID:\s*"([^"]+)"$', text, flags=re.MULTILINE)
    if source_id_match is None:
        raise GeneratorError("source artifact ID is missing")

    status_section = _section(text, "## 9. Status enum", "## 10. Complete")
    status_rows = _table_rows(status_section, 3)
    statuses = [row[0] for row in status_rows]
    status_exits = {row[0]: int(row[1]) for row in status_rows}
    if statuses != [
        "planned",
        "completed",
        "completed_with_warnings",
        "blocked",
        "partial_failure",
        "error",
    ]:
        raise GeneratorError("status enum drifted from Wire v12")

    relation_section = _section(
        text,
        "## 10. Complete code/value/phase relation matrix",
        "## 11. Retry, continuation, messages and guidance",
    )
    relation_rows_raw = _table_rows(relation_section, 16)
    if not relation_rows_raw:
        raise GeneratorError("relation matrix is empty")
    relation_rows: list[dict[str, Any]] = []
    for row in relation_rows_raw:
        relation_rows.append({
            "code": row[0],
            "variant": row[1],
            "status": row[2],
            "mode": row[3],
            "apply": row[4].lower() == "true",
            "operation": None if row[5] == "null" else row[5],
            "candidate_digest": row[6],
            "seed_policy": row[7],
            "mutation_started": row[8].lower() == "true",
            "bootstrap_rolled_back": row[9].lower() == "true",
            "phase": row[10],
            "last_completed_phase": row[11],
            "retry": None if row[12] == "null" else row[12],
            "actions": row[13],
            "exit_code": int(row[14]),
            "continuation": row[15],
        })
    codes: list[str] = []
    for relation_row in relation_rows:
        if relation_row["code"] not in codes:
            codes.append(relation_row["code"])

    target_section = _section(text, "### WIR-ORD-001", "## 4. Durable")
    target_rows = _table_rows(target_section, 2)
    target_paths = [row[1] for row in target_rows]

    phase_section = _section(text, "### WIR-PHASE-001", "### WIR-PHASE-002")
    phases = _parse_phases(phase_section)
    last_completed = [*phases, "not-started"]

    record_section = _section(text, "### WIR-REC-003", "## 5. Observed")
    records = _json_fences(record_section)
    public_section = _section(text, "## 13. JSON goldens", "## 14. Public text")
    public = _json_fences(public_section)

    counts = {
        "status": len(statuses),
        "code": len(codes),
        "phase": len(phases),
        "last_completed_phase": len(last_completed),
        "relation": len(relation_rows),
        "public_golden": len(public),
        "record_golden": len(records),
    }
    if counts != EXPECTED_COUNTS:
        raise GeneratorError(f"Wire inventory mismatch: expected {EXPECTED_COUNTS}, got {counts}")

    for relation_row in relation_rows:
        if relation_row["status"] not in statuses:
            raise GeneratorError(f"relation has unknown status: {relation_row['status']}")
        if relation_row["phase"] not in phases or relation_row["last_completed_phase"] not in last_completed:
            raise GeneratorError("relation has unknown phase")
        if relation_row["exit_code"] != status_exits[relation_row["status"]]:
            raise GeneratorError("relation exit code disagrees with status enum")

    return {
        "source_id": source_id_match.group(1),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "statuses": statuses,
        "status_exits": status_exits,
        "codes": codes,
        "phases": phases,
        "last_completed": last_completed,
        "target_paths": target_paths,
        "relations": relation_rows,
        "public": public,
        "records": records,
    }


def _python_literal(value: object) -> str:
    return repr(value)


def _render(data: dict[str, Any]) -> bytes:
    lines = [
        '"""Generated from the normative provider lifecycle Wire v12 artifact."""',
        "",
        "from __future__ import annotations",
        "",
        f"SOURCE_ID = {_python_literal(data['source_id'])}",
        f"SOURCE_SHA256 = {_python_literal(data['source_sha256'])}",
        "",
        f"PUBLIC_STATUS_VALUES = {_python_literal(tuple(data['statuses']))}",
        f"PUBLIC_STATUS_EXIT_CODES = {_python_literal(data['status_exits'])}",
        f"PUBLIC_CODE_VALUES = {_python_literal(tuple(data['codes']))}",
        f"PHASE_VALUES = {_python_literal(tuple(data['phases']))}",
        f"LAST_COMPLETED_PHASE_VALUES = {_python_literal(tuple(data['last_completed']))}",
        f"TARGET_PATH_ORDER = {_python_literal(tuple(data['target_paths']))}",
        "",
        f"RELATION_ROWS = {_python_literal(tuple(data['relations']))}",
        "",
        f"PUBLIC_JSON_GOLDENS = {_python_literal(tuple(data['public']))}",
        f"RECORD_GOLDENS = {_python_literal(tuple(data['records']))}",
        "",
    ]
    raw = ("\n".join(lines)).encode("utf-8")
    try:
        formatted = subprocess.run(
            ["ruff", "format", "--stdin-filename", "_wire_generated.py", "-"],
            input=raw,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GeneratorError("ruff is required to render deterministic generated output") from exc
    if not formatted.endswith(b"\n"):
        raise GeneratorError("formatted generated output has no terminal LF")
    return formatted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = _render(_parse_source(args.source))
    except (OSError, UnicodeError, GeneratorError) as exc:
        print(f"generate_provider_lifecycle_wire.py: {exc}", file=sys.stderr)
        return 1
    if args.check:
        try:
            actual = args.output.read_bytes()
        except OSError as exc:
            print(f"generate_provider_lifecycle_wire.py: {exc}", file=sys.stderr)
            return 1
        if actual != expected:
            print(f"generated output differs: {args.output}", file=sys.stderr)
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
