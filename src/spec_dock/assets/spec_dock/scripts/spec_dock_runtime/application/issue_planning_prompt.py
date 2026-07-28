"""Pure, bounded synthesis for provider-owned Issue Planning prompts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.domain.authoring_pack.authority_boundary import (
    is_credential_like_path,
    private_absolute_path_finding,
    scan_constraint_sensitive_payload,
)

if TYPE_CHECKING:
    from spec_dock_runtime.domain.issue_planning_contracts import PlanningContext

MAX_DEPENDENCIES = 32
MAX_RELEVANT_FILES = 16
MAX_RELEVANT_FILE_BYTES = 256 * 1024
MAX_RELEVANT_TOTAL_BYTES = 2 * 1024 * 1024
MAX_OPERATOR_ENTRIES = 16
MAX_OPERATOR_ENTRY_BYTES = 4 * 1024
MAX_OPERATOR_TOTAL_BYTES = 32 * 1024


@dataclass(frozen=True)
class SynthesizedPlanningPrompt:
    role: Literal["planner", "reviewer"]
    prompt: str
    attachments: tuple[tuple[str, str], ...]


def synthesize_issue_planning_prompt(
    *,
    role: Literal["planner", "reviewer"],
    context: PlanningContext,
    repo_root: Path,
    upstream: str,
    remote_head: str,
    resource_root: Path | None = None,
) -> SynthesizedPlanningPrompt:
    if len(context.dependency_summary) > MAX_DEPENDENCIES:
        raise ValueError("dependencies exceed bounded limit")
    if len(context.relevant_source_paths) > MAX_RELEVANT_FILES:
        raise ValueError("relevant source paths exceed bounded limit")
    if len(context.operator_context) > MAX_OPERATOR_ENTRIES:
        raise ValueError("operator context exceeds bounded limit")

    operator_bytes = 0
    for entry in context.operator_context:
        encoded = entry.encode("utf-8")
        operator_bytes += len(encoded)
        if len(encoded) > MAX_OPERATOR_ENTRY_BYTES or operator_bytes > MAX_OPERATOR_TOTAL_BYTES:
            raise ValueError("operator context exceeds bounded byte limit")
        _reject_sensitive(entry)

    root = repo_root.resolve(strict=True)
    paths = (*context.canonical_issue_paths, *context.relevant_source_paths)
    attachments: list[tuple[str, str]] = []
    relevant_bytes = 0
    for relative in sorted(set(paths), key=lambda item: item.encode("utf-8")):
        is_relevant = relative in context.relevant_source_paths
        target = _safe_source_file(root, relative)
        raw = target.read_bytes()
        if is_relevant:
            relevant_bytes += len(raw)
            if len(raw) > MAX_RELEVANT_FILE_BYTES or relevant_bytes > MAX_RELEVANT_TOTAL_BYTES:
                raise ValueError("relevant source bytes exceed bounded limit")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("relevant source must be UTF-8") from error
        _reject_sensitive(text)
        attachments.append((relative, text))

    resources = resource_root or _provider_resource_root()
    role_prompt = (resources / f"{role}-prompt.md").read_text(encoding="utf-8")
    transport = (resources / "transport-output-contract.md").read_text(encoding="utf-8")
    identity = {
        **context.to_dict(),
        "upstream": upstream,
        "remote_head": remote_head,
    }
    dynamic = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    _reject_sensitive(dynamic)
    exact_frame = (
        f"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role={role} "
        f"source_head={context.source_head}>>>"
    )
    prompt = (
        f"{role_prompt.rstrip()}\n\n## Source identity and bounded context\n\n{dynamic}\n\n"
        f"## Exact frame for this invocation\n\n{exact_frame}\n\n{transport.rstrip()}\n"
    )
    return SynthesizedPlanningPrompt(role=role, prompt=prompt, attachments=tuple(attachments))


def _safe_source_file(root: Path, relative: str) -> Path:
    if "\\" in relative or is_credential_like_path(relative):
        raise ValueError("relevant source path is unsafe")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in ("", ".", "..", ".workbench") for part in path.parts):
        raise ValueError("relevant source path is unsafe")
    target = root / Path(*path.parts)
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("relevant source path is symlinked")
    try:
        resolved = target.resolve(strict=True)
    except OSError as error:
        raise ValueError("relevant source path is missing") from error
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("relevant source path is outside repository or not a file")
    return resolved


def _reject_sensitive(text: str) -> None:
    if scan_constraint_sensitive_payload(text):
        raise ValueError("sensitive dynamic context rejected")
    if private_absolute_path_finding(text):
        raise ValueError("private absolute path rejected")


def _provider_resource_root() -> Path:
    return (
        Path(__file__).resolve().parents[4]
        / "install_root"
        / ".agents"
        / "skills"
        / "spec-dock-issue-planning"
        / "resources"
    )
