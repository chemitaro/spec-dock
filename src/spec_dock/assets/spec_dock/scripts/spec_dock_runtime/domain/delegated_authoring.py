from __future__ import annotations

import hashlib
import json
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .authority import GRANT_DESIGN_BASELINE, GRANT_PLANNING_INPUT, GRANT_REVIEW_INPUT, VALID_GRANTS


VALID_ROLES: tuple[str, ...] = ("system-architect", "implementation-planner")
VALID_TARGETS: tuple[str, ...] = ("design", "plan")
VALID_HOST_SURFACES: tuple[str, ...] = ("cli", "desktop")

ROLE_TARGETS: dict[str, str] = {
    "system-architect": "design",
    "implementation-planner": "plan",
}

REQUIRED_SOURCE_GRANTS: dict[str, dict[str, tuple[str, ...]]] = {
    "system-architect": {
        "requirement": (GRANT_REVIEW_INPUT, GRANT_PLANNING_INPUT),
    },
    "implementation-planner": {
        "requirement": (GRANT_REVIEW_INPUT, GRANT_PLANNING_INPUT),
        "design": (GRANT_DESIGN_BASELINE,),
    },
}

OLD_SANDBOX_KEYS: tuple[str, ...] = ("sandbox_mode", "sandbox_workspace_write")
NEGATIVE_PROBE_BOUNDARY_CATEGORIES: tuple[str, ...] = (
    "requirement.md",
    "peer_artifact",
    "report.md",
    "src/",
    "tests/",
    ".codex/",
    ".agents/",
    ".env*",
)


@dataclass(frozen=True)
class DelegatedAuthoringPaths:
    task_dir: Path
    manifest_path: Path
    permission_profile_path: Path
    probe_plan_path: Path
    session_invocation_path: Path


@dataclass(frozen=True)
class DelegatedAuthoringResult:
    ok: bool
    status: str
    reason: str
    role: str
    scope_id: str
    target: str
    host_surface: str
    target_artifact_path: Path | None = None
    paths: DelegatedAuthoringPaths | None = None
    manifest_hash: str | None = None
    permission_profile_name: str | None = None
    permission_profile_hash: str | None = None
    session_invocation_hash: str | None = None
    host_surface_acceptance_eligible: bool = False
    acceptance_counted: bool = False
    details: tuple[str, ...] = ()


def validate_manifest_request(*, role: str, scope_id: str, target: str, host_surface: str) -> tuple[str, ...]:
    errors: list[str] = []
    if role not in VALID_ROLES:
        errors.append(f"invalid_role={role}")
    if target not in VALID_TARGETS:
        errors.append(f"invalid_target={target}")
    if role in ROLE_TARGETS and target != ROLE_TARGETS[role]:
        errors.append(f"role_target_mismatch={role}:{target}")
    if host_surface not in VALID_HOST_SURFACES:
        errors.append(f"invalid_host_surface={host_surface}")
    if not scope_id.strip():
        errors.append("missing_scope")
    return tuple(errors)


def load_authority_file(path: Path) -> Mapping[str, object]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
    elif suffix == ".toml":
        data = _loads_toml(text)
    else:
        raise RuntimeError("input_authority_file must be .json or .toml")
    if not isinstance(data, Mapping):
        raise RuntimeError("input_authority_file must contain a table/object")
    return data


def validate_input_authority(
    data: Mapping[str, object],
    *,
    role: str,
    authority_base_dir: Path | None = None,
) -> tuple[str, ...]:
    errors: list[str] = []
    source_revisions = _mapping(data.get("source_revisions"))
    input_authority = _mapping(data.get("input_authority"))
    if source_revisions is None:
        errors.append("missing_source_revisions")
    if input_authority is None:
        errors.append("missing_input_authority")
    if source_revisions is None or input_authority is None:
        return tuple(errors)

    required_sources = ["requirement"]
    if role == "implementation-planner":
        required_sources.append("design")
    for source in required_sources:
        revision = _text(source_revisions.get(source))
        if revision is None:
            errors.append(f"missing_source_revision={source}")
        source_auth = _mapping(input_authority.get(source))
        if source_auth is None:
            errors.append(f"missing_input_authority_entry={source}")
            continue
        errors.extend(
            _validate_authority_entry(
                source,
                source_auth,
                expected_revision=revision,
                required_grants=REQUIRED_SOURCE_GRANTS.get(role, {}).get(source, ()),
                authority_base_dir=authority_base_dir,
            )
        )
    return tuple(errors)


def generated_profile_has_old_sandbox_settings(text: str) -> bool:
    return "sandbox_mode" in text or "[sandbox_workspace_write]" in text


def render_manifest_toml(
    *,
    role: str,
    scope_id: str,
    target: str,
    host_surface: str,
    target_artifact_path: Path,
    input_authority_file: Path,
    input_authority_hash: str,
    permission_profile_name: str,
    positive_probe_id: str,
    negative_sentinel_paths: Mapping[str, Path],
    output_paths: DelegatedAuthoringPaths,
    host_surface_acceptance_eligible: bool,
    acceptance_counted: bool,
    source_revisions: Mapping[str, object],
) -> str:
    lines = [
        'schema = "spec-dock.delegated-authoring.manifest.v1"',
        f'role = "{_toml_escape(role)}"',
        f'scope_id = "{_toml_escape(scope_id)}"',
        f'target = "{_toml_escape(target)}"',
        f'host_surface = "{_toml_escape(host_surface)}"',
        f'target_artifact_path = "{_toml_escape(target_artifact_path.as_posix())}"',
        f'input_authority_file = "{_toml_escape(input_authority_file.as_posix())}"',
        f'input_authority_hash = "{input_authority_hash}"',
        f'permission_profile_name = "{_toml_escape(permission_profile_name)}"',
        f'positive_probe_id = "{_toml_escape(positive_probe_id)}"',
        f'positive_probe_target = "{_toml_escape(target_artifact_path.as_posix())}"',
        f'negative_probe_sentinel = "{_toml_escape(_first_sentinel(negative_sentinel_paths).as_posix())}"',
        f'host_surface_acceptance_eligible = {_toml_bool(host_surface_acceptance_eligible)}',
        f'acceptance_counted = {_toml_bool(acceptance_counted)}',
        "",
        "[generated_artifacts]",
        f'manifest = "{_toml_escape(output_paths.manifest_path.as_posix())}"',
        f'permission_profile = "{_toml_escape(output_paths.permission_profile_path.as_posix())}"',
        f'probe_plan = "{_toml_escape(output_paths.probe_plan_path.as_posix())}"',
        f'session_invocation = "{_toml_escape(output_paths.session_invocation_path.as_posix())}"',
        "",
        "[source_revisions]",
    ]
    for key, value in sorted(source_revisions.items()):
        if isinstance(value, str):
            lines.append(f'{key} = "{_toml_escape(value)}"')
    lines.append("")
    lines.append("[diff_gate]")
    lines.append('required = true')
    lines.append('forbidden_diff = "none"')
    lines.append('dirty_diff_abort = true')
    lines.append("")
    lines.append("[negative_probe_sentinels]")
    for category in NEGATIVE_PROBE_BOUNDARY_CATEGORIES:
        sentinel = negative_sentinel_paths[category]
        lines.append(f'"{_toml_escape(category)}" = "{_toml_escape(sentinel.as_posix())}"')
    return "\n".join(lines) + "\n"


def render_permission_profile_toml(
    *,
    profile_name: str,
    target_artifact_path: Path,
    task_dir: Path,
) -> str:
    target_path = target_artifact_path.as_posix()
    task_path = task_dir.as_posix()
    return "\n".join(
        [
            f'default_permissions = "{_toml_escape(profile_name)}"',
            "",
            f'[permissions."{_toml_escape(profile_name)}".filesystem]',
            '":minimal" = "read"',
            "",
            f'[permissions."{_toml_escape(profile_name)}".filesystem.":workspace_roots"]',
            '"." = "read"',
            f'"{_toml_escape(target_path)}" = "write"',
            f'"{_toml_escape(task_path)}" = "write"',
            '".env" = "deny"',
            '".env.*" = "deny"',
            "",
            f'[permissions."{_toml_escape(profile_name)}".network]',
            "enabled = false",
        ]
    ) + "\n"


def render_probe_plan_markdown(
    *,
    positive_probe_id: str,
    target_artifact_path: Path,
    negative_sentinel_paths: Mapping[str, Path],
) -> str:
    lines = [
        "# Delegated Authoring Probe Plan",
        "",
        "## Positive Probe",
        f"- id: `{positive_probe_id}`",
        f"- target: `{target_artifact_path.as_posix()}`",
        "- expectation: delegated author can update only the exact target draft artifact.",
        "",
        "## Negative Probe",
        "- expectation: disposable sentinel creation must be denied for every forbidden boundary category.",
        "- real artifact/source/test/config/secret files must not be touched.",
        "- if a sentinel is created, remove only that sentinel, record fail-open evidence, and abort on dirty diff.",
        "",
    ]
    for category in NEGATIVE_PROBE_BOUNDARY_CATEGORIES:
        lines.append(f"- category: `{category}` sentinel: `{negative_sentinel_paths[category].as_posix()}`")
    lines.extend(
        [
            "",
            "## Diff Gate",
            "- require target artifact diff only.",
            "- require no forbidden path diff.",
            "- abort if cleanup leaves dirty probe artifacts.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_session_invocation_toml(
    *,
    executor: str,
    host_surface: str,
    role: str,
    scope_id: str,
    target_artifact_path: Path,
    manifest_path: Path,
    manifest_hash: str,
    permission_profile_name: str,
    permission_profile_hash: str,
    positive_probe_id: str,
    positive_probe_target: Path,
    negative_probe_plan_path: Path,
    diff_gate_plan_path: Path,
    host_surface_acceptance_eligible: bool,
    acceptance_counted: bool,
) -> str:
    return "\n".join(
        [
            f'executor = "{_toml_escape(executor)}"',
            f'host_surface = "{_toml_escape(host_surface)}"',
            f'role = "{_toml_escape(role)}"',
            f'scope_id = "{_toml_escape(scope_id)}"',
            f'target_artifact_path = "{_toml_escape(target_artifact_path.as_posix())}"',
            f'manifest_path = "{_toml_escape(manifest_path.as_posix())}"',
            f'manifest_hash = "{manifest_hash}"',
            f'permission_profile_name = "{_toml_escape(permission_profile_name)}"',
            f'permission_profile_hash = "{permission_profile_hash}"',
            f'default_permissions = "{_toml_escape(permission_profile_name)}"',
            f'positive_probe_id = "{_toml_escape(positive_probe_id)}"',
            f'positive_probe_target = "{_toml_escape(positive_probe_target.as_posix())}"',
            f'negative_probe_plan_path = "{_toml_escape(negative_probe_plan_path.as_posix())}"',
            f'diff_gate_plan_path = "{_toml_escape(diff_gate_plan_path.as_posix())}"',
            f'host_surface_acceptance_eligible = {_toml_bool(host_surface_acceptance_eligible)}',
            f'acceptance_counted = {_toml_bool(acceptance_counted)}',
            "",
            "[config_overrides]",
            f'default_permissions = "{_toml_escape(permission_profile_name)}"',
            "old_sandbox_settings_absent = true",
        ]
    ) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_authority_entry(
    source: str,
    entry: Mapping[str, object],
    *,
    expected_revision: str | None,
    required_grants: tuple[str, ...],
    authority_base_dir: Path | None,
) -> list[str]:
    errors: list[str] = []
    required = (
        "promotion_record_path",
        "reviewer_evidence_path",
        "approved_revision",
        "approved_content_hash",
        "reviewer_verdict",
        "reviewer_target_hash",
        "required_grants",
        "stale_check",
    )
    for key in required:
        if entry.get(key) is None:
            errors.append(f"missing_{source}_{key}")
    if errors:
        return errors
    if _text(entry.get("reviewer_verdict")) != "pass":
        errors.append(f"reviewer_not_pass={source}")
    if _text(entry.get("stale_check")) != "fresh":
        errors.append(f"stale_authority={source}")
    if expected_revision is not None and _text(entry.get("approved_revision")) != expected_revision:
        errors.append(f"revision_mismatch={source}")
    if _text(entry.get("approved_content_hash")) != _text(entry.get("reviewer_target_hash")):
        errors.append(f"reviewer_hash_mismatch={source}")
    grants = entry.get("required_grants")
    if not isinstance(grants, list | tuple) or not all(isinstance(item, str) and item.strip() for item in grants):
        errors.append(f"invalid_required_grants={source}")
    else:
        normalized_grants = tuple(item.strip() for item in grants)
        invalid_grants = tuple(grant for grant in normalized_grants if grant not in VALID_GRANTS)
        for grant in invalid_grants:
            errors.append(f"invalid_required_grant={source}:{grant}")
        for grant in required_grants:
            if grant not in normalized_grants:
                errors.append(f"missing_required_grant={source}:{grant}")
    for key in ("promotion_record_path", "reviewer_evidence_path"):
        evidence_path = _resolve_authority_path(str(entry[key]), authority_base_dir)
        if not evidence_path.is_file():
            errors.append(f"missing_{source}_{key}_file")
            continue
        errors.extend(
            _verify_evidence_file(
                source,
                evidence_path,
                entry,
                kind=key.removesuffix("_path"),
                authority_base_dir=authority_base_dir,
            )
        )
    return errors


def _verify_evidence_file(
    source: str,
    path: Path,
    entry: Mapping[str, object],
    *,
    kind: str,
    authority_base_dir: Path | None,
) -> list[str]:
    text = path.read_text(encoding="utf-8")
    parsed = _try_parse_structured(path, text)
    expected_revision = _text(entry.get("approved_revision"))
    expected_hash = _text(entry.get("approved_content_hash"))
    expected_reviewer_hash = _text(entry.get("reviewer_target_hash"))
    required_grants = _grants(entry.get("required_grants"))
    if parsed is not None:
        if kind == "promotion_record":
            promotion = _mapping(parsed.get("promotion_record")) or parsed
            return _verify_structured_promotion(
                source,
                promotion,
                expected_revision,
                expected_hash,
                required_grants,
                expected_reviewer_evidence_path=_text(entry.get("reviewer_evidence_path")),
                authority_base_dir=authority_base_dir,
            )
        reviewer = _mapping(parsed.get("reviewer_evidence")) or parsed
        return _verify_structured_reviewer(source, reviewer, expected_reviewer_hash)
    return [f"unstructured_{kind}_evidence={source}"]


def _verify_structured_promotion(
    source: str,
    promotion: Mapping[str, object],
    expected_revision: str | None,
    expected_hash: str | None,
    required_grants: tuple[str, ...] | None,
    *,
    expected_reviewer_evidence_path: str | None = None,
    authority_base_dir: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    required_text_fields = (
        "artifact_path",
        "approved_revision",
        "approved_hash",
        "approver",
        "approved_at",
        "reviewer_evidence_path",
    )
    for key in required_text_fields:
        if _text(promotion.get(key)) is None:
            errors.append(f"promotion_missing_{key}={source}")
    if _text(promotion.get("final_reviewer")) is None and _text(promotion.get("reviewer")) is None:
        errors.append(f"promotion_missing_reviewer={source}")
    if _text(promotion.get("status")) != "approved":
        errors.append(f"promotion_status_not_approved={source}")
    if _text(promotion.get("authority")) != "approved":
        errors.append(f"promotion_not_approved={source}")
    if expected_revision is not None and _text(promotion.get("approved_revision")) != expected_revision:
        errors.append(f"promotion_revision_mismatch={source}")
    if expected_hash is not None and _text(promotion.get("approved_hash")) != expected_hash:
        errors.append(f"promotion_hash_mismatch={source}")
    promotion_reviewer_path = _text(promotion.get("reviewer_evidence_path"))
    if (
        expected_reviewer_evidence_path is not None
        and promotion_reviewer_path is not None
        and _normalized_path_for_compare(promotion_reviewer_path, authority_base_dir)
        != _normalized_path_for_compare(expected_reviewer_evidence_path, authority_base_dir)
    ):
        errors.append(f"promotion_reviewer_evidence_path_mismatch={source}")
    approved_grants = _grants(promotion.get("approved_grants"))
    if approved_grants is None:
        approved_grants = _grants(promotion.get("grants"))
    if approved_grants is None:
        errors.append(f"promotion_missing_approved_grants={source}")
    elif required_grants is not None:
        for grant in required_grants:
            if grant not in approved_grants:
                errors.append(f"promotion_missing_required_grant={source}:{grant}")
    if not _ledger_blockers_remaining_zero(promotion.get("ledger_blockers_remaining")):
        errors.append(f"promotion_ledger_blockers_remaining={source}")
    return errors


def _resolve_authority_path(raw_path: str, authority_base_dir: Path | None) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute() and authority_base_dir is not None:
        path = authority_base_dir / path
    return path


def _normalized_path_for_compare(raw_path: str, authority_base_dir: Path | None = None) -> str:
    return _resolve_authority_path(raw_path, authority_base_dir).resolve(strict=False).as_posix()


def _verify_structured_reviewer(
    source: str,
    reviewer: Mapping[str, object],
    expected_reviewer_hash: str | None,
) -> list[str]:
    errors: list[str] = []
    if _text(reviewer.get("review_status")) != "pass" and _text(reviewer.get("reviewer_verdict")) != "pass":
        errors.append(f"reviewer_evidence_not_pass={source}")
    if expected_reviewer_hash is not None and _text(reviewer.get("reviewer_target_hash")) != expected_reviewer_hash:
        errors.append(f"reviewer_evidence_hash_mismatch={source}")
    return errors


def _try_parse_structured(path: Path, text: str) -> Mapping[str, object] | None:
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        elif path.suffix.lower() == ".toml":
            data = _loads_toml(text)
        else:
            return None
    except Exception:
        return None
    return data if isinstance(data, Mapping) else None


def _loads_toml(text: str) -> Mapping[str, object]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _loads_minimal_toml(text)


def _loads_minimal_toml(text: str) -> Mapping[str, object]:
    root: dict[str, object] = {}
    current: dict[str, object] = root
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part, {})  # type: ignore[assignment]
            continue
        if "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        current[key] = _parse_minimal_toml_value(raw_value)
    return root


def _parse_minimal_toml_value(raw_value: str) -> object:
    if raw_value in ("true", "false"):
        return raw_value == "true"
    if raw_value.startswith("[") and raw_value.endswith("]"):
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [_parse_minimal_toml_value(part.strip()) for part in inner.split(",")]
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return raw_value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return raw_value


def _mapping(value: object) -> Mapping[str, object] | None:
    return value if isinstance(value, Mapping) else None


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _grants(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list | tuple):
        return None
    grants: list[str] = []
    for item in value:
        text = _text(item)
        if text is None:
            return None
        grants.append(text)
    return tuple(grants)


def _ledger_blockers_remaining_zero(value: object) -> bool:
    if isinstance(value, int):
        return value == 0
    if isinstance(value, str):
        return value.strip() == "0"
    return False


def _first_sentinel(paths: Mapping[str, Path]) -> Path:
    return paths[NEGATIVE_PROBE_BOUNDARY_CATEGORIES[0]]


def _toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _toml_bool(value: bool) -> str:
    return "true" if value else "false"
