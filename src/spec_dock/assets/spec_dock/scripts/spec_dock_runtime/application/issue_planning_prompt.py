"""Pure, bounded synthesis for provider-owned Issue Planning prompts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
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
class PlanningPromptAttachment:
    name: str
    classification: Literal["review-target", "supplemental-context", "formal-evidence"]
    source_label: str
    content: bytes

    def __post_init__(self) -> None:
        for value, field_name in ((self.name, "name"), (self.source_label, "source_label")):
            if (
                not isinstance(value, str)
                or not value
                or "\\" in value
                or is_credential_like_path(value)
            ):
                raise ValueError(f"planning attachment {field_name} is unsafe")
            path = PurePosixPath(value)
            if path.is_absolute() or any(part in ("", ".", "..") or part.startswith(".") for part in path.parts):
                raise ValueError(f"planning attachment {field_name} is unsafe")
        if self.classification not in {
            "review-target",
            "supplemental-context",
            "formal-evidence",
        }:
            raise ValueError("planning attachment classification is invalid")
        if not isinstance(self.content, bytes):
            raise ValueError("planning attachment content must be bytes")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


@dataclass(frozen=True)
class SynthesizedPlanningPrompt:
    role: Literal["planner", "reviewer"]
    prompt: str
    attachments: tuple[tuple[str, str], ...]
    exact_attachments: tuple[PlanningPromptAttachment, ...] = ()


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


def synthesize_planning_evidence_prompt(
    *,
    role: Literal["planner", "reviewer"],
    source_head: str,
    repository: str,
    branch: str,
    exact_attachments: tuple[PlanningPromptAttachment, ...],
    instructions: tuple[str, ...] = (),
    supplemental_attachments: tuple[tuple[str, str], ...] = (),
    resource_root: Path | None = None,
) -> SynthesizedPlanningPrompt:
    if re.fullmatch(r"[0-9a-f]{40}", source_head) is None:
        raise ValueError("source HEAD is invalid")
    if not exact_attachments:
        raise ValueError("exact planning attachments are required")
    names = [item.name for item in exact_attachments]
    labels = [item.source_label for item in exact_attachments]
    if len(names) != len(set(names)) or len(labels) != len(set(labels)):
        raise ValueError("planning attachment names and source labels must be unique")
    dynamic = json.dumps(
        {
            "branch": branch,
            "repository": repository,
            "source_head": source_head,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    _reject_sensitive(dynamic)
    for instruction in instructions:
        _reject_sensitive(instruction)
    resources = resource_root or _provider_resource_root()
    resource_name = "reviewer-prompt.md" if role == "reviewer" else "revision-prompt.md"
    role_prompt = (resources / resource_name).read_text(encoding="utf-8")
    transport = (resources / "transport-output-contract.md").read_text(encoding="utf-8")
    index = "\n".join(
        f"- {item.name}: classification={item.classification}; "
        f"source_label={item.source_label}; sha256={item.sha256}"
        for item in exact_attachments
    )
    instruction_block = "\n".join(f"- {item}" for item in instructions) or "- none"
    frame = (
        f"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role={role} "
        f"source_head={source_head}>>>"
    )
    prompt = (
        f"{role_prompt.rstrip()}\n\n## Source identity\n\n{dynamic}\n\n"
        f"## Exact attachment index\n\n{index}\n\n"
        f"## Operation instructions\n\n{instruction_block}\n\n"
        f"## Exact frame for this invocation\n\n{frame}\n\n{transport.rstrip()}\n"
    )
    return SynthesizedPlanningPrompt(
        role=role,
        prompt=prompt,
        attachments=supplemental_attachments,
        exact_attachments=exact_attachments,
    )


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
