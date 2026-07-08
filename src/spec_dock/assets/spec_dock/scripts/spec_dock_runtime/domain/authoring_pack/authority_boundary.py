from __future__ import annotations

import re

from spec_dock_runtime.domain.authoring_pack.prompt_pack_contract import (
    FORBIDDEN_AUTHORITY_CLAIMS as PROMPT_PACK_FORBIDDEN_AUTHORITY_CLAIMS,
)

LOCAL_FORBIDDEN_AUTHORITY_CLAIMS: tuple[str, ...] = (
    "canonical adoption",
    ".assurance.json mutation",
    "authorized_profile",
    "reviewer pass",
    "spec-review pass",
    "qa-review pass",
    "code-review pass",
    "execution-ready",
    "pr-ready",
    "mergeable pr",
)

FORBIDDEN_AUTHORITY_CLAIMS: tuple[str, ...] = tuple(
    dict.fromkeys((
        *(claim.lower() for claim in PROMPT_PACK_FORBIDDEN_AUTHORITY_CLAIMS),
        *LOCAL_FORBIDDEN_AUTHORITY_CLAIMS,
    ))
)

SECRET_MARKERS: tuple[str, ...] = (
    "private key",
    "api_key",
    "api key",
    "password=",
    "token=",
    "secret=",
    "credential",
)

RAW_TRANSCRIPT_MARKERS: tuple[str, ...] = (
    "raw transcript",
    "chatgpt transcript",
    "browser transcript",
)


def scan_authoring_payload(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    findings: list[str] = []
    for marker in FORBIDDEN_AUTHORITY_CLAIMS:
        if marker in lowered:
            findings.append(f"forbidden_authority_claim:{marker}")
    findings.extend(scan_sensitive_payload(text))
    return tuple(dict.fromkeys(findings))


def scan_sensitive_payload(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    findings: list[str] = []
    for marker in SECRET_MARKERS:
        if marker in lowered:
            findings.append(f"secret_like_payload:{marker.strip('=')}")
    findings.extend(_scan_structured_secret_fields(lowered))
    for marker in RAW_TRANSCRIPT_MARKERS:
        if marker in lowered:
            findings.append(f"raw_transcript:{marker}")
    return tuple(dict.fromkeys(findings))


def scan_constraint_sensitive_payload(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    findings: list[str] = []
    if "private key" in lowered and ("-----begin" in lowered or "block" in lowered):
        findings.append("secret_like_payload:private key")
    findings.extend(_scan_structured_secret_fields(lowered, require_secret_like_value=True))
    for marker in RAW_TRANSCRIPT_MARKERS:
        if marker in lowered:
            findings.append(f"raw_transcript:{marker}")
    return tuple(dict.fromkeys(findings))


def _scan_structured_secret_fields(text: str, *, require_secret_like_value: bool = False) -> tuple[str, ...]:
    if not any(keyword in text for keyword in ("api", "password", "token", "secret", "credential", "private")):
        return ()
    findings: list[str] = []
    for match in re.finditer(
        r'["\']?([a-z0-9_-]*(?:api[\s_-]?key|private[\s_-]?key|password|token|secret|credential)[a-z0-9_-]*)["\']?\s*[:=]\s*["\']?([^\s"\'{},\]]+)',
        text,
    ):
        marker = match.group(1)
        value = match.group(2)
        if require_secret_like_value and not _looks_like_secret_value(value):
            continue
        if "private" in marker:
            findings.append("secret_like_payload:private key")
        elif "token" in marker:
            findings.append("secret_like_payload:token")
        elif "secret" in marker:
            findings.append("secret_like_payload:secret")
        elif "credential" in marker:
            findings.append("secret_like_payload:credential")
        elif "password" in marker:
            findings.append("secret_like_payload:password")
        else:
            findings.append("secret_like_payload:api_key")
    return tuple(findings)


def _looks_like_secret_value(value: str) -> bool:
    lowered = value.lower()
    if len(value) >= 8:
        return True
    if any(char.isdigit() for char in value) and len(value) >= 5:
        return True
    return lowered.startswith(("sk-", "ghp_", "xoxb-", "akia"))
