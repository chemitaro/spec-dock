from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..domain import delegated_authoring as domain


@dataclass(frozen=True)
class DelegatedAuthoringManifestRequest:
    role: str
    scope_id: str
    target: str
    host_surface: str
    input_authority_file: Path
    repo_root: Path
    specdock_dir: Path


def generate_delegated_authoring_manifest(
    req: DelegatedAuthoringManifestRequest,
) -> domain.DelegatedAuthoringResult:
    request_errors = domain.validate_manifest_request(
        role=req.role,
        scope_id=req.scope_id,
        target=req.target,
        host_surface=req.host_surface,
    )
    if request_errors:
        return _blocked(req, "invalid_request", request_errors)
    if not req.input_authority_file.is_file():
        return _blocked(req, "missing_input_authority_file", (str(req.input_authority_file),))

    try:
        authority_data = domain.load_authority_file(req.input_authority_file)
    except Exception as error:
        return _blocked(req, "invalid_input_authority_file", (str(error),))

    authority_errors = domain.validate_input_authority(
        authority_data,
        role=req.role,
        authority_base_dir=req.input_authority_file.parent,
    )
    if authority_errors:
        return _blocked(req, "input_authority_not_verified", authority_errors)

    scope_dir = _resolve_scope_dir(req.specdock_dir, req.scope_id)
    if scope_dir is None:
        return _blocked(req, "scope_not_found", (req.scope_id,))
    target_artifact_path = scope_dir / f"{req.target}.md"
    task_id = _task_id(
        req.role,
        req.scope_id,
        req.target,
        req.host_surface,
        domain.sha256_file(req.input_authority_file),
    )
    task_dir = scope_dir / "discussions" / "delegated-authoring" / task_id
    output_paths = domain.DelegatedAuthoringPaths(
        task_dir=task_dir,
        manifest_path=task_dir / "manifest.toml",
        permission_profile_path=task_dir / "permission-profile.toml",
        probe_plan_path=task_dir / "probe-plan.md",
        session_invocation_path=task_dir / "session-invocation.toml",
    )
    permission_profile_name = f"spec-dock-{task_id}"
    positive_probe_id = f"{task_id}-positive"
    negative_sentinel_paths = _negative_sentinel_paths(
        repo_root=req.repo_root,
        scope_dir=scope_dir,
        task_id=task_id,
        target=req.target,
    )
    host_surface_acceptance_eligible = req.host_surface == "cli"
    acceptance_counted = False

    source_revisions = authority_data.get("source_revisions")
    if not isinstance(source_revisions, dict):
        return _blocked(req, "missing_source_revisions", ())
    input_authority_hash = domain.sha256_file(req.input_authority_file)
    manifest_text = domain.render_manifest_toml(
        role=req.role,
        scope_id=req.scope_id,
        target=req.target,
        host_surface=req.host_surface,
        target_artifact_path=target_artifact_path,
        input_authority_file=req.input_authority_file,
        input_authority_hash=input_authority_hash,
        permission_profile_name=permission_profile_name,
        positive_probe_id=positive_probe_id,
        negative_sentinel_paths=negative_sentinel_paths,
        output_paths=output_paths,
        host_surface_acceptance_eligible=host_surface_acceptance_eligible,
        acceptance_counted=acceptance_counted,
        source_revisions=source_revisions,
    )
    profile_text = domain.render_permission_profile_toml(
        profile_name=permission_profile_name,
        target_artifact_path=_relative_to_repo(target_artifact_path, req.repo_root),
        task_dir=_relative_to_repo(task_dir, req.repo_root),
    )
    if domain.generated_profile_has_old_sandbox_settings(profile_text):
        return _blocked(req, "generated_profile_contains_old_sandbox_settings", ())
    probe_text = domain.render_probe_plan_markdown(
        positive_probe_id=positive_probe_id,
        target_artifact_path=target_artifact_path,
        negative_sentinel_paths=negative_sentinel_paths,
    )
    manifest_hash = domain.sha256_text(manifest_text)
    profile_hash = domain.sha256_text(profile_text)
    session_text = domain.render_session_invocation_toml(
        executor="codex-cli" if req.host_surface == "cli" else "desktop-fallback",
        host_surface=req.host_surface,
        role=req.role,
        scope_id=req.scope_id,
        target_artifact_path=target_artifact_path,
        manifest_path=output_paths.manifest_path,
        manifest_hash=manifest_hash,
        permission_profile_name=permission_profile_name,
        permission_profile_hash=profile_hash,
        positive_probe_id=positive_probe_id,
        positive_probe_target=target_artifact_path,
        negative_probe_plan_path=output_paths.probe_plan_path,
        diff_gate_plan_path=output_paths.probe_plan_path,
        host_surface_acceptance_eligible=host_surface_acceptance_eligible,
        acceptance_counted=acceptance_counted,
    )
    session_hash = domain.sha256_text(session_text)

    task_dir.mkdir(parents=True, exist_ok=True)
    output_paths.manifest_path.write_text(manifest_text, encoding="utf-8")
    output_paths.permission_profile_path.write_text(profile_text, encoding="utf-8")
    output_paths.probe_plan_path.write_text(probe_text, encoding="utf-8")
    output_paths.session_invocation_path.write_text(session_text, encoding="utf-8")

    return domain.DelegatedAuthoringResult(
        ok=True,
        status="generated",
        reason="ok",
        role=req.role,
        scope_id=req.scope_id,
        target=req.target,
        host_surface=req.host_surface,
        target_artifact_path=target_artifact_path,
        paths=output_paths,
        manifest_hash=manifest_hash,
        permission_profile_name=permission_profile_name,
        permission_profile_hash=profile_hash,
        session_invocation_hash=session_hash,
        host_surface_acceptance_eligible=host_surface_acceptance_eligible,
        acceptance_counted=acceptance_counted,
    )


def _blocked(
    req: DelegatedAuthoringManifestRequest,
    reason: str,
    details: tuple[str, ...],
) -> domain.DelegatedAuthoringResult:
    return domain.DelegatedAuthoringResult(
        ok=False,
        status="blocked",
        reason=reason,
        role=req.role,
        scope_id=req.scope_id,
        target=req.target,
        host_surface=req.host_surface,
        details=details,
    )


def _resolve_scope_dir(specdock_dir: Path, scope_id: str) -> Path | None:
    meta_paths = sorted(specdock_dir.glob(f"initiatives/**/{scope_id}*/.meta.json"))
    for meta_path in meta_paths:
        if _scope_meta_matches(meta_path, scope_id):
            return meta_path.parent
    active_issue = specdock_dir / "active" / "issue"
    if active_issue.exists():
        try:
            resolved = active_issue.resolve()
        except OSError:
            resolved = active_issue
        if _scope_meta_matches(resolved / ".meta.json", scope_id):
            return resolved
    return None


def _scope_meta_matches(meta_path: Path, scope_id: str) -> bool:
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return data.get("id") == scope_id


def _task_id(role: str, scope_id: str, target: str, host_surface: str, input_hash: str) -> str:
    return f"{scope_id}-{role}-{target}-{host_surface}-{input_hash[:12]}".replace("_", "-")


def _relative_to_repo(path: Path, repo_root: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError:
        return path


def _negative_sentinel_paths(*, repo_root: Path, scope_dir: Path, task_id: str, target: str) -> dict[str, Path]:
    peer_artifact = "plan.md" if target == "design" else "design.md"
    return {
        "requirement.md": scope_dir / "discussions" / f".{task_id}.requirement-md.spec-dock-permission-probe-denied",
        "peer_artifact": scope_dir / "discussions" / f".{task_id}.{peer_artifact}.spec-dock-permission-probe-denied",
        "report.md": scope_dir / "discussions" / f".{task_id}.report-md.spec-dock-permission-probe-denied",
        "src/": repo_root / "src" / f".{task_id}.spec-dock-permission-probe-denied",
        "tests/": repo_root / "tests" / f".{task_id}.spec-dock-permission-probe-denied",
        ".codex/": repo_root / ".codex" / f".{task_id}.spec-dock-permission-probe-denied",
        ".agents/": repo_root / ".agents" / f".{task_id}.spec-dock-permission-probe-denied",
        ".env*": repo_root / f".env.{task_id}.spec-dock-permission-probe-denied",
    }
