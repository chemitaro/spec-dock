from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
from typing import Literal
import zipfile

from spec_dock_runtime.domain.authoring_pack.authority_boundary import (
    scan_authoring_payload,
    scan_constraint_sensitive_payload,
)
from spec_dock_runtime.domain.authoring_pack.prompt_pack_contract import (
    ADOPTION_STATUS,
    AUTHORITY,
    BUNDLE_GENERATION_NOT_PROMOTION,
    EXPECTED_OUTPUT_ROOT,
    REQUIRED_METADATA,
)

PackReviewStatus = Literal["pass", "fail", "blocked", "stale", "rejected"]
PackInputKind = Literal["zip", "tree"]

SUPPORTED_TEXT_SUFFIXES = {".json", ".md", ".txt", ".yml", ".yaml"}
NESTED_ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z"}
MAX_ENTRY_BYTES = 2_000_000
MAX_TOTAL_BYTES = 10_000_000
JSON_METADATA = tuple(path for path in REQUIRED_METADATA if path.endswith(".json"))
SECRET_PATH_PARTS = {"secret", "secrets", "token", "tokens", "credential", "credentials", "password", "passwords"}
CLAIM_SCAN_EXCLUDED_PATHS = {
    "safe-output-constraints.md",
    "chatgpt-use-prompt.md",
    "expected-output-contract.md",
}


@dataclass(frozen=True)
class PackReviewResult:
    status: PackReviewStatus
    input_path: str
    input_kind: PackInputKind
    authority: str = AUTHORITY
    adoption_status: str = ADOPTION_STATUS
    bundle_generation_not_promotion: bool = BUNDLE_GENERATION_NOT_PROMOTION
    evidence_mode: str | None = None
    fallback: bool = False
    authority_level: str = "zip_review"
    missing_evidence: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    reviewed_files: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "input_path": self.input_path,
            "input_kind": self.input_kind,
            "authority": self.authority,
            "adoption_status": self.adoption_status,
            "bundle_generation_not_promotion": self.bundle_generation_not_promotion,
            "evidence_mode": self.evidence_mode,
            "fallback": self.fallback,
            "authority_level": self.authority_level,
            "missing_evidence": list(self.missing_evidence),
            "findings": list(self.findings),
            "reviewed_files": list(self.reviewed_files),
        }


def review_pack_input(input_path: Path) -> PackReviewResult:
    if not input_path.exists():
        return PackReviewResult(
            status="blocked",
            input_path=str(input_path),
            input_kind="tree",
            findings=("input_missing",),
        )
    if input_path.is_symlink():
        return PackReviewResult(
            status="rejected",
            input_path=str(input_path),
            input_kind="tree",
            findings=("symlink_input_root",),
        )
    if input_path.is_dir():
        return _review_tree(input_path)
    if zipfile.is_zipfile(input_path):
        return _review_zip(input_path)
    return PackReviewResult(
        status="fail",
        input_path=str(input_path),
        input_kind="tree",
        findings=("unsupported_input_kind",),
    )


def _review_zip(input_path: Path) -> PackReviewResult:
    findings: list[str] = []
    payloads: dict[str, str] = {}
    reviewed_files: list[str] = []
    total_size = 0
    root = EXPECTED_OUTPUT_ROOT.rstrip("/")
    with zipfile.ZipFile(input_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos if not info.is_dir()]
        if not names:
            findings.append("empty_zip")
        for info in infos:
            if info.is_dir():
                continue
            total_size += info.file_size
            rel_name = _relative_name(info.filename, root, findings)
            if rel_name is None:
                continue
            _validate_entry(info, rel_name, findings)
            reviewed_files.append(rel_name)
            if _can_read_text_payload(info, rel_name):
                try:
                    payloads[rel_name] = archive.read(info).decode("utf-8")
                except (RuntimeError, zipfile.BadZipFile):
                    findings.append(f"unreadable_payload:{rel_name}")
                except UnicodeDecodeError:
                    findings.append(f"binary_payload:{rel_name}")
        if total_size > MAX_TOTAL_BYTES:
            findings.append("oversized_total")
    metadata_status = _validate_metadata(payloads, findings)
    findings.extend(_scan_payloads(payloads))
    return PackReviewResult(
        status=_status_from_findings(tuple(findings), metadata_status),
        input_path=str(input_path),
        input_kind="zip",
        findings=tuple(dict.fromkeys(findings)),
        reviewed_files=tuple(sorted(reviewed_files)),
    )


def _review_tree(input_path: Path) -> PackReviewResult:
    findings: list[str] = []
    payloads: dict[str, str] = {}
    reviewed_files: list[str] = []
    root = input_path / EXPECTED_OUTPUT_ROOT.rstrip("/")
    if root.is_symlink():
        findings.append("symlink_entry:specdock-authoring-pack")
    elif not root.is_dir():
        findings.append("wrong_root")
    else:
        for path in sorted(root.rglob("*")):
            if path.is_dir() and not path.is_symlink():
                continue
            rel_name = path.relative_to(root).as_posix()
            _validate_relative_path(rel_name, findings)
            if path.is_symlink():
                findings.append(f"symlink_entry:{rel_name}")
                reviewed_files.append(rel_name)
                continue
            if not path.is_file():
                continue
            _validate_tree_entry(path, rel_name, findings)
            reviewed_files.append(rel_name)
            if _is_supported_text(rel_name):
                try:
                    payloads[rel_name] = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    findings.append(f"binary_payload:{rel_name}")
        _validate_metadata(payloads, findings)
        findings.extend(_scan_payloads(payloads))
    return PackReviewResult(
        status=_status_from_findings(tuple(findings), "pass"),
        input_path=str(input_path),
        input_kind="tree",
        fallback=True,
        authority_level="lower_than_zip_review",
        missing_evidence=("zip-central-directory",),
        findings=tuple(dict.fromkeys(findings)),
        reviewed_files=tuple(sorted(reviewed_files)),
    )


def _relative_name(name: str, root: str, findings: list[str]) -> str | None:
    if not name.startswith(f"{root}/"):
        findings.append("wrong_root")
        return None
    rel_name = name[len(root) + 1 :]
    _validate_relative_path(rel_name, findings)
    return rel_name


def _validate_relative_path(rel_name: str, findings: list[str]) -> None:
    path = PurePosixPath(rel_name)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        findings.append(f"path_traversal:{rel_name}")
    if any(part.startswith(".") for part in path.parts):
        findings.append(f"hidden_path:{rel_name}")
    parts = tuple(part.lower() for part in path.parts)
    if parts and parts[0] in {"users", "home", "volumes", "private"}:
        findings.append(f"host_local_path:{rel_name}")
    if any(part in {".oracle", ".ssh"} for part in parts):
        findings.append(f"host_local_path:{rel_name}")
    if any(part in SECRET_PATH_PARTS or "api-key" in part or "api_key" in part for part in parts):
        findings.append(f"secret_path:{rel_name}")


def _validate_entry(info: zipfile.ZipInfo, rel_name: str, findings: list[str]) -> None:
    if info.flag_bits & 0x1:
        findings.append(f"encrypted_entry:{rel_name}")
    mode = (info.external_attr >> 16) & 0o170000
    if mode == 0o120000:
        findings.append(f"symlink_entry:{rel_name}")
    permissions = (info.external_attr >> 16) & 0o777
    if permissions & 0o111:
        findings.append(f"executable_entry:{rel_name}")
    if info.file_size > MAX_ENTRY_BYTES:
        findings.append(f"oversized_entry:{rel_name}")
    suffix = PurePosixPath(rel_name).suffix.lower()
    if suffix in NESTED_ARCHIVE_SUFFIXES:
        findings.append(f"nested_archive:{rel_name}")
    if suffix not in SUPPORTED_TEXT_SUFFIXES:
        findings.append(f"unsupported_suffix:{rel_name}")


def _validate_tree_entry(path: Path, rel_name: str, findings: list[str]) -> None:
    try:
        stat_result = path.stat()
        size = stat_result.st_size
    except OSError:
        findings.append(f"unreadable_payload:{rel_name}")
        return
    if stat_result.st_mode & 0o111:
        findings.append(f"executable_entry:{rel_name}")
    if size > MAX_ENTRY_BYTES:
        findings.append(f"oversized_entry:{rel_name}")
    suffix = PurePosixPath(rel_name).suffix.lower()
    if suffix in NESTED_ARCHIVE_SUFFIXES:
        findings.append(f"nested_archive:{rel_name}")
    if suffix not in SUPPORTED_TEXT_SUFFIXES:
        findings.append(f"unsupported_suffix:{rel_name}")


def _can_read_text_payload(info: zipfile.ZipInfo, rel_name: str) -> bool:
    if info.flag_bits & 0x1:
        return False
    mode = (info.external_attr >> 16) & 0o170000
    if mode == 0o120000:
        return False
    return _is_supported_text(rel_name) and info.file_size <= MAX_ENTRY_BYTES


def _validate_metadata(payloads: dict[str, str], findings: list[str]) -> str:
    status = "pass"
    for metadata in REQUIRED_METADATA:
        if metadata not in payloads:
            findings.append(f"missing_metadata:{metadata}")
            status = "fail"
    objects: dict[str, object] = {}
    for metadata in JSON_METADATA:
        if metadata not in payloads:
            continue
        try:
            objects[metadata] = json.loads(payloads[metadata])
        except json.JSONDecodeError:
            findings.append(f"invalid_json:{metadata}")
            status = "fail"
    manifest = objects.get("manifest.json")
    source_manifest = objects.get("source-manifest.json")
    stale_if = objects.get("stale-if.json")
    if isinstance(manifest, dict):
        if manifest.get("authority") != AUTHORITY:
            findings.append("invalid_authority")
        if manifest.get("adoption_status") != ADOPTION_STATUS:
            findings.append("invalid_adoption_status")
        if manifest.get("bundle_generation_not_promotion") is not BUNDLE_GENERATION_NOT_PROMOTION:
            findings.append("invalid_bundle_generation_not_promotion")
    if isinstance(source_manifest, dict) and isinstance(stale_if, dict):
        expected_hash = stale_if.get("source_manifest_hash_changes", stale_if.get("source_manifest_hash"))
        if expected_hash is not None and source_manifest.get("source_manifest_hash") != expected_hash:
            findings.append("source_hash_mismatch")
            status = "stale"
    return status


def _scan_payloads(payloads: dict[str, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for rel_name, text in payloads.items():
        if rel_name in CLAIM_SCAN_EXCLUDED_PATHS:
            findings.extend(scan_constraint_sensitive_payload(text))
            continue
        findings.extend(scan_authoring_payload(text))
    return tuple(findings)


def _status_from_findings(findings: tuple[str, ...], metadata_status: str) -> PackReviewStatus:
    if any(finding == "wrong_root" for finding in findings):
        return "rejected"
    if any(_is_rejected_finding(finding) for finding in findings):
        return "rejected"
    if any(finding.startswith("source_hash_mismatch") for finding in findings) or metadata_status == "stale":
        return "stale"
    if (
        any(finding.startswith(("missing_metadata:", "invalid_json:")) for finding in findings)
        or metadata_status == "fail"
    ):
        return "fail"
    if findings:
        return "rejected"
    return "pass"


def _is_rejected_finding(finding: str) -> bool:
    return not finding.startswith(("missing_metadata:", "invalid_json:", "source_hash_mismatch"))


def _is_supported_text(rel_name: str) -> bool:
    return PurePosixPath(rel_name).suffix.lower() in SUPPORTED_TEXT_SUFFIXES
