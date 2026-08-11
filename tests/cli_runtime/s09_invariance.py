from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    import subprocess


S09_LEGACY_EVIDENCE_MUTATIONS = (
    "thin_report",
    "heavy_report",
    "evidence_adoption_ledger",
    "delegated_authority",
    "assurance",
    "planning_level",
    "legacy_active_extra_fields",
    "draft_artifact",
    "repair_artifact",
)


def normalize_s09_process_result(
    result: subprocess.CompletedProcess[str],
    *,
    repo_root: Path,
    bin_root: Path | None = None,
) -> tuple[int, str, str]:
    """Return the complete CLI observation with only test-root paths normalized."""

    replacements = [(str(repo_root), "<repo>")]
    if bin_root is not None:
        replacements.append((str(bin_root), "<bin>"))

    def normalize(text: str) -> str:
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    return result.returncode, normalize(result.stdout), normalize(result.stderr)


def _find_issue_dir(target: Path, issue_id: str) -> Path:
    matches = sorted((target / "spec-dock" / "initiatives").glob(f"**/{issue_id}-*"))
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one {issue_id} directory, found {matches}")
    return matches[0]


def apply_s09_legacy_evidence_mutation(target: Path, mutation: str, *, issue_id: str) -> tuple[Path, ...]:
    issue_dir = _find_issue_dir(target, issue_id)
    if mutation == "thin_report":
        path = issue_dir / "report.md"
        path.write_bytes(b"")
        return (path,)
    if mutation == "heavy_report":
        path = issue_dir / "report.md"
        path.write_text("# Report\n\n" + ("historical detail\n" * 128), encoding="utf-8")
        return (path,)
    if mutation == "evidence_adoption_ledger":
        path = issue_dir / "report.md"
        path.write_text(
            "# Report\n\n## Evidence Adoption Ledger\n\n"
            "| ID | adoption_status | target_artifact | next_action |\n"
            "|---|---|---|---|\n"
            "| EAL-S09 | blocked | design.md | historical only |\n",
            encoding="utf-8",
        )
        return (path,)
    if mutation == "delegated_authority":
        path = issue_dir / "design.md"
        path.write_text(
            "---\nstatus: draft\nauthority: proposed\ngrants: [implementation_start]\n"
            "approval: pending-main-promotion\n---\n# Design\n",
            encoding="utf-8",
        )
        return (path,)
    if mutation == "assurance":
        path = issue_dir / ".assurance.json"
        path.write_text('{"authorized_profile":"critical","grade":"blocked"}\n', encoding="utf-8")
        return (path,)
    if mutation == "planning_level":
        path = issue_dir / "plan.md"
        path.write_text("# Plan\n\nPlanning Level: critical\nReviewer gate: blocked\n", encoding="utf-8")
        return (path,)
    if mutation == "legacy_active_extra_fields":
        path = target / "spec-dock" / ".agent" / "active.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["authority"] = "approved"
        payload["grants"] = ["implementation_start"]
        issue = payload.get("issue")
        if isinstance(issue, dict):
            issue["promotion_record"] = {"status": "pending"}
            issue["planning_level"] = "critical"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return (path,)
    if mutation == "draft_artifact":
        path = issue_dir / "artifacts" / "20260810t010101z-draft-plan-historical.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\nauthority: proposed\n---\n# Historical draft\n", encoding="utf-8")
        return (path,)
    if mutation == "repair_artifact":
        path = issue_dir / "artifacts" / "20260810t010102z-pr-repair-batch-historical.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Historical repair batch\n\nreviewer: blocked\n", encoding="utf-8")
        return (path,)
    raise AssertionError(f"unknown S09 mutation: {mutation}")
