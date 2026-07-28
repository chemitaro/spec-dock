"""Fixed direct-argv ChatGPT transport for Issue Planning."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
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
        _write_transport_pack(pack, synthesized, source_evidence)
        result, streams = invoke_backend_with_capture(
            BackendInvokeRequest(
                prompt_pack=pack,
                output_dir=output,
                backend_command=_FIXED_CHATGPT_USE,
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
            return _result("blocked", "backend_nonzero", source_evidence, result.exit_code, len(streams.stdout))
        if result.status != "pass":
            return _result("rejected", "planning_context_rejected", source_evidence, result.exit_code, 0)
        return classify_transport_frame(
            streams.stdout,
            role=role,
            source_head=source_evidence.local_head,
            source_evidence=source_evidence,
            backend_exit_code=result.exit_code,
        )


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
    source_manifest = {
        "source_paths": [path for path, _ in synthesized.attachments],
        "source_hashes": {
            path: hashlib.sha256(body.encode("utf-8")).hexdigest()
            for path, body in synthesized.attachments
        },
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
