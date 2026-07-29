"""Fixed direct-argv ChatGPT transport for Issue Planning."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.authoring_pack.backend_invoke import invoke_backend_with_capture
from spec_dock_runtime.domain.authoring_pack.authority_boundary import (
    private_absolute_path_finding,
    scan_constraint_sensitive_payload,
)
from spec_dock_runtime.domain.authoring_pack.backend_invoke_contract import BackendInvokeRequest
from spec_dock_runtime.domain.issue_planning_contracts import (
    PlanningInvocationResult,
    PlanningSourceEvidence,
)
from spec_dock_runtime.infra.git_cli import origin_github_repo_slug

if TYPE_CHECKING:
    from spec_dock_runtime.application.issue_planning_prompt import SynthesizedPlanningPrompt

_FIXED_CHATGPT_USE = "/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt"
_END_MARKER = "<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>"


def resolve_issue_planning_github_repository(repo_root: Path) -> str | None:
    return origin_github_repo_slug(repo_root)


def classify_transport_frame(
    stdout: bytes,
    *,
    role: Literal["planner", "reviewer"],
    source_head: str,
    source_evidence: PlanningSourceEvidence | None = None,
    backend_exit_code: int | None = 0,
) -> PlanningInvocationResult:
    response_bytes = len(stdout)
    if not stdout.strip():
        return _result(
            "blocked",
            "backend_output_missing",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return _result(
            "rejected",
            "backend_response_malformed",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )

    start_marker = (
        f"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role={role} source_head={source_head}>>>"
    )
    if text.count(start_marker) == 1 and _END_MARKER not in text:
        return _result(
            "blocked",
            "backend_response_partial",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    if text.count(start_marker) != 1 or text.count(_END_MARKER) != 1:
        return _result(
            "rejected",
            "backend_response_malformed",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    start_index = text.index(start_marker)
    end_index = text.index(_END_MARKER)
    if end_index < start_index:
        return _result(
            "rejected",
            "backend_response_malformed",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    before = text[:start_index]
    payload = text[start_index + len(start_marker) : end_index].strip()
    after = text[end_index + len(_END_MARKER) :]
    if before.strip() or after.strip():
        return _result(
            "rejected",
            "backend_response_malformed",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    if not payload:
        return _result(
            "blocked",
            "backend_response_partial",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    if scan_constraint_sensitive_payload(payload) or private_absolute_path_finding(payload):
        return _result(
            "rejected",
            "sensitive_input_rejected",
            source_evidence,
            backend_exit_code,
            response_bytes,
        )
    payload_bytes = payload.encode("utf-8")
    return PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=source_evidence,
        backend_exit_code=backend_exit_code,
        response_bytes=response_bytes,
        response_sha256=hashlib.sha256(payload_bytes).hexdigest(),
        transient_payload=payload_bytes,
    )


def invoke_issue_planning_chatgpt(
    *,
    repo_root: Path,
    role: Literal["planner", "reviewer"],
    source_evidence: PlanningSourceEvidence,
    synthesized: SynthesizedPlanningPrompt,
    timeout_seconds: float | None = None,
) -> PlanningInvocationResult:
    with TemporaryDirectory(prefix="specdock-issue-planning-") as raw_temp:
        temp_root = Path(raw_temp)
        pack = temp_root / "prompt-pack"
        output = temp_root / "output"
        final_output = temp_root / "final-assistant-message.txt"
        _write_transport_pack(pack, synthesized, source_evidence)
        if final_output.exists() or final_output.is_symlink():
            return _result("rejected", "planning_context_rejected", source_evidence, None, 0)
        backend_command = shlex.join(
            (
                _FIXED_CHATGPT_USE,
                "--write-output",
                str(final_output),
            )
        )
        result, _streams = invoke_backend_with_capture(
            BackendInvokeRequest(
                prompt_pack=pack,
                output_dir=output,
                backend_command=backend_command,
                prompt="Use only the attached Issue Planning transport pack.",
                slug=(
                    f"specdock-{role}-{source_evidence.snapshot_id[:12]}-"
                    f"{temp_root.name[-8:]}"
                ),
                timeout_seconds=timeout_seconds,
                working_dir=repo_root,
            ),
            env={},
        )
        if "backend_command_not_found" in result.blockers or "backend_os_error" in result.blockers:
            return _result("blocked", "backend_unavailable", source_evidence, None, 0)
        if "backend_timeout" in result.blockers:
            return _result("blocked", "backend_timeout", source_evidence, None, 0)
        if result.exit_code not in (None, 0):
            return _result("blocked", "backend_nonzero", source_evidence, result.exit_code, 0)
        if result.status != "pass":
            return _result("rejected", "planning_context_rejected", source_evidence, result.exit_code, 0)
        final_output_bytes = _read_regular_file_bytes(final_output)
        if not final_output_bytes:
            return _result(
                "blocked",
                "backend_output_missing",
                source_evidence,
                result.exit_code,
                0,
            )
        return classify_transport_frame(
            final_output_bytes,
            role=role,
            source_head=source_evidence.local_head,
            source_evidence=source_evidence,
            backend_exit_code=result.exit_code,
        )


def _read_regular_file_bytes(path: Path) -> bytes | None:
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            return None
        flags = os.O_RDONLY
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            return handle.read()
    except OSError:
        return None
    finally:
        os.close(descriptor)


def _result(
    status: Literal["blocked", "rejected"],
    reason: str,
    source_evidence: PlanningSourceEvidence | None,
    exit_code: int | None,
    response_bytes: int,
) -> PlanningInvocationResult:
    return PlanningInvocationResult(
        status=status,
        reason=reason,
        source_evidence=source_evidence,
        backend_exit_code=exit_code,
        response_bytes=response_bytes,
    )


def _write_transport_pack(
    pack: Path,
    synthesized: SynthesizedPlanningPrompt,
    source: PlanningSourceEvidence,
) -> None:
    pack.mkdir()
    (pack / ".specdock-authoring-pack").write_text("issue-planning-transport-v1\n", encoding="utf-8")
    attachment_names: list[str] = []
    for index, (relative, body) in enumerate(synthesized.attachments):
        name = f"context-{index:03d}.md"
        attachment_names.append(name)
        (pack / name).write_text(f"source_path: {relative}\n\n{body}", encoding="utf-8")
    exact_source_hashes: dict[str, str] = {}
    for attachment in synthesized.exact_attachments:
        if attachment.name in attachment_names:
            raise ValueError("exact planning attachment name collides with prompt pack")
        target = pack / attachment.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(attachment.content)
        if hashlib.sha256(target.read_bytes()).hexdigest() != attachment.sha256:
            raise OSError("exact planning attachment changed while writing prompt pack")
        attachment_names.append(attachment.name)
        exact_source_hashes[attachment.source_label] = attachment.sha256
    (pack / "chatgpt-use-prompt.md").write_text(synthesized.prompt, encoding="utf-8")
    (pack / "expected-output-contract.md").write_text(
        "The exact response frame in chatgpt-use-prompt.md is required.\n",
        encoding="utf-8",
    )
    (pack / "safe-output-constraints.md").write_text(
        "Evidence only. No repository mutation, transcript, credential, or private host path.\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 1,
        "generated_by": "spec-dock-issue-planning",
        "expected_output_root": "transport-only",
        "required_metadata": [],
        "files": attachment_names,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }
    provenance = {
        "evidence_mode": "github-synced",
        "sync_state": "synced",
        "github_sync": "verified",
        "source_manifest_hash": source.source_manifest_hash,
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }
    source_hashes = {
        path: hashlib.sha256(body.encode("utf-8")).hexdigest()
        for path, body in synthesized.attachments
    }
    for label, digest in exact_source_hashes.items():
        existing = source_hashes.get(label)
        if existing is not None and existing != digest:
            raise ValueError("planning attachment source label has conflicting bytes")
        source_hashes[label] = digest
    source_manifest = {
        "source_paths": list(source_hashes),
        "source_hashes": source_hashes,
        "source_manifest_hash": source.source_manifest_hash,
    }
    _write_json(pack / "manifest.json", manifest)
    _write_json(pack / "provenance.json", provenance)
    _write_json(pack / "source-manifest.json", source_manifest)
    _write_json(pack / "stale-if.json", {"source_head_changes": source.local_head})


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
