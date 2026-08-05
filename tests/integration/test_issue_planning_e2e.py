from __future__ import annotations

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Any, cast
import zipfile

import pytest

from spec_dock.cli import main as installer_main

REPO_ROOT = Path(__file__).resolve().parents[2]
BRANCH = "feature/issue-planning"
ISSUE_ID = "iss-00334"
CURRENT_ROADMAP = b"S01 through S10 are closed, including S07 and S08. S11 review is pending. S12 through S14 remain."


def _run_git(repo: Path, *args: str, env: dict[str, str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _prepare_target(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, str]]:
    target = tmp_path / "target"
    target.mkdir()
    assert installer_main(["init", str(target)]) == 0
    installed_skill = (target / ".agents/skills/spec-dock-issue-planning/SKILL.md").read_text(encoding="utf-8")
    assert "./spec-dock/scripts/spec-dock-chatgpt" in installed_skill
    assert "oracle" in installed_skill
    assert "PATH" in installed_skill
    assert "do not use a personal wrapper" in installed_skill.lower()
    assert "SPECDOCK_ORACLE_REMOTE_CHROME" in installed_skill
    assert "loopback" in installed_skill.lower()
    assert "already-running authenticated" in installed_skill.lower()
    assert "profile" in installed_skill.lower()
    assert "cookie" in installed_skill.lower()
    shutil.rmtree(target / "spec-dock/initiatives")
    shutil.copytree(REPO_ROOT / "spec-dock/initiatives", target / "spec-dock/initiatives")
    issue_meta = next(
        path
        for path in (target / "spec-dock/initiatives").rglob(".meta.json")
        if json.loads(path.read_text(encoding="utf-8")).get("id") == ISSUE_ID
    )
    issue_dir = issue_meta.parent
    meta = json.loads(issue_meta.read_text(encoding="utf-8"))
    kinds = {
        "requirement.md": "要件定義書（Issue）",
        "design.md": "設計書（Issue）",
        "plan.md": "実装計画書（Issue）",
    }
    dependencies = {
        "requirement.md": "",
        "design.md": '依存: ["requirement.md"]\n',
        "plan.md": '依存: ["requirement.md", "design.md"]\n',
    }
    for name, kind in kinds.items():
        (issue_dir / name).write_text(
            "---\n"
            f"種別: {kind}\n"
            f'ID: "{ISSUE_ID}"\n'
            'タイトル: "Integration fixture"\n'
            '状態: "approved"\n'
            '作成者: "Test"\n'
            '最終更新: "2026-07-28"\n'
            f"{dependencies[name]}"
            f'親: ["{meta["epic_id"]}", "{meta["initiative_id"]}"]\n'
            "---\n\n"
            f"# {ISSUE_ID} Integration fixture\n\n"
            "## Contract\n\n"
            "Hermetic planning chain fixture.\n",
            encoding="utf-8",
        )

    bare = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)
    ssh = tmp_path / "git-ssh"
    ssh.write_text(
        "#!/bin/sh\n"
        f'case "$2" in\n'
        f"  \"git-upload-pack 'chemitaro/spec-dock.git'\") exec git-upload-pack {bare!s} ;;\n"
        f"  \"git-receive-pack 'chemitaro/spec-dock.git'\") exec git-receive-pack {bare!s} ;;\n"
        "  *) exit 97 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    ssh.chmod(0o755)
    env = {**os.environ, "GIT_SSH_COMMAND": str(ssh)}
    _run_git(target, "init", "-b", BRANCH, env=env)
    _run_git(target, "config", "user.name", "SpecDock Test", env=env)
    _run_git(target, "config", "user.email", "specdock@example.invalid", env=env)
    _run_git(
        target,
        "remote",
        "add",
        "origin",
        "git@github.com:chemitaro/spec-dock.git",
        env=env,
    )
    _run_git(target, "add", ".", env=env)
    _run_git(target, "commit", "-m", "fixture", env=env)
    _run_git(target, "push", "-u", "origin", BRANCH, env=env)

    sync = subprocess.run(
        [
            str(target / "spec-dock/scripts/spec-dock"),
            "sync",
            "--no-github",
            "--no-update-active",
        ],
        cwd=target,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert sync.returncode == 0, sync.stderr
    if _run_git(target, "status", "--porcelain", env=env):
        _run_git(target, "add", ".", env=env)
        _run_git(target, "commit", "-m", "fixture sync", env=env)
        _run_git(target, "push", env=env)

    return target, bare, issue_dir, env


_FAKE_ORACLE = r"""#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import zipfile


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def append_record(home: Path, value: object) -> None:
    with (home / "fake-oracle-invocations.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def guide(issue_id: str, epic_id: str, initiative_id: str) -> bytes:
    blocks = "\n\n".join(
        "```plantuml\n@startuml\n"
        f"title {title}\nactor Human\ncomponent SpecDock\nHuman --> SpecDock\n"
        "@enduml\n```"
        for title in (
            "System Context",
            "Responsibility Boundary",
            "Planning Sequence",
            "Implementation Roadmap",
        )
    )
    return (
        "# New-member guide\n\n"
        "This guide is subordinate to requirement.md, design.md, and plan.md. "
        "Those canonical documents have precedence.\n\n"
        "## Initiative, Epic, and Issue lineage\n\n"
        f"The exact planning lineage is {initiative_id}, {epic_id}, and {issue_id}.\n\n"
        "## Purpose and scope\n\nPurpose and scope are bounded to onboarding.\n\n"
        "## System context\n\nThe system context identifies actors and boundaries.\n\n"
        "## Authority and responsibility boundary\n\n"
        "Authority and responsibility remain with the Human and deterministic Runtime.\n\n"
        "## Current architecture and target architecture\n\n"
        "Current architecture and target architecture describe the bounded transition.\n\n"
        "## ChatGPT First planning lifecycle\n\n"
        "ChatGPT First governs the planning lifecycle.\n\n"
        "## Direct Oracle and reference-only chatgpt-use\n\n"
        "The Runtime uses Oracle directly; chatgpt-use is reference-only.\n\n"
        "## Candidate, Review, Human, and apply lifecycle\n\n"
        "Candidate, Review, exact Human approval, and apply form the controlled lifecycle.\n\n"
        "## Exact current branch gate\n\n"
        "The exact current branch is mandatory; no default branch fallback is permitted.\n\n"
        "## Roadmap and operations\n\n"
        "S01 through S10 are closed, including S07 and S08. S11 review is pending. "
        "S12 through S14 remain.\n\n"
        "## Provider authority and projection\n\nProvider authority precedes projection.\n\n"
        "## Failure modes\n\nFailure modes stop closed.\n\n"
        "## First-day checklist\n\nThe first-day checklist directs the new member.\n\n"
        f"{blocks}\n"
    ).encode()


home = Path(os.environ["ORACLE_HOME_DIR"])
repository_root = Path.cwd()
if not (repository_root / "spec-dock/initiatives").is_dir():
    candidate_root = home.parent / "target"
    if (candidate_root / "spec-dock/initiatives").is_dir():
        repository_root = candidate_root
home.mkdir(parents=True, exist_ok=True)
argv = sys.argv[1:]
record = {
    "argv": [sys.argv[0], *argv],
    "cwd": str(Path.cwd()),
    "environment": {key: os.environ[key] for key in sorted(os.environ)},
}

if argv == ["--version"]:
    append_record(home, record)
    print("0.16.1")
    raise SystemExit(0)
if argv == ["--help"]:
    append_record(home, record)
    print("--engine --file --slug --wait --prompt --browser-attachments --model --browser-model-strategy --remote-chrome")
    raise SystemExit(0)
if argv == ["session", "--help"]:
    append_record(home, record)
    print("--harvest --no-recover")
    raise SystemExit(0)
if argv[:1] == ["session"]:
    append_record(home, record)
    raise SystemExit(0)

required_prefix = [
    "--engine", "browser",
    "--model", "Pro",
    "--browser-model-strategy", "select",
    "--remote-chrome",
]
if argv[:7] != required_prefix:
    raise SystemExit(92)
if re.fullmatch(r"127\.0\.0\.1:[1-9][0-9]{0,4}", argv[7]) is None:
    raise SystemExit(92)
if argv[8] != "--browser-no-cookie-sync":
    raise SystemExit(92)
if "SPECDOCK_ORACLE_REMOTE_CHROME" in os.environ:
    raise SystemExit(93)

prompt = argv[argv.index("--prompt") + 1]
file_paths = [
    Path(argv[index + 1])
    for index, value in enumerate(argv)
    if value == "--file"
]
slug = argv[argv.index("--slug") + 1]
record["prompt"] = prompt
record["attachment_paths"] = [str(path) for path in file_paths]
append_record(home, record)

match = re.search(
    r"## Expected output\n\n(\{[^\n]+\})\n\n",
    prompt,
)
if match is None:
    raise SystemExit(91)
expectation = json.loads(match.group(1))
session = home / "sessions" / slug
artifacts = session / "artifacts"
artifacts.mkdir(parents=True)

if (home / "fake-repository-access-failure").exists():
    artifact = artifacts / "transcript.md"
    artifact.write_bytes(
        b"# Fake Oracle transcript\n\n## Answer\nrepository access failed\n"
    )
    payload = artifact.read_bytes()
    write_json(
        session / "meta.json",
        {
            "id": slug,
            "mode": "browser",
            "status": "completed",
            "artifacts": [{
                "kind": "transcript",
                "path": artifact.relative_to(session).as_posix(),
                "sizeBytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "validation": {"ok": True},
            }],
        },
    )
    raise SystemExit(0)

if expectation["kind"] == "authoring_zip":
    logical = expectation["logical_filename"]
    root = expectation["internal_root"]
    issue_id = logical.removesuffix("-issue-planning-documents.zip")
    issue_meta_path = next(
        path
        for path in (repository_root / "spec-dock/initiatives").rglob(".meta.json")
        if json.loads(path.read_text(encoding="utf-8")).get("id") == issue_id
    )
    issue_meta = json.loads(issue_meta_path.read_text(encoding="utf-8"))
    issue_dir = issue_meta_path.parent
    payloads = {
        name: (issue_dir / name).read_bytes().rstrip()
        + f"\n\nOracle session {slug}\n".encode()
        for name in ("requirement.md", "design.md", "plan.md")
    }
    companion = expectation["onboarding_companion_path"]
    payloads[companion] = guide(
        issue_id,
        issue_meta["epic_id"],
        issue_meta["initiative_id"],
    )
    artifact = artifacts / logical
    with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_STORED) as archive:
        for relative in sorted(payloads, key=lambda value: value.encode()):
            info = zipfile.ZipInfo(
                f"{root}/{relative}",
                date_time=(2026, 7, 29, 12, 0, 0),
            )
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, payloads[relative])
    kind = "file"
else:
    identity_match = re.search(
        r"## Reviewed identity\n\n(\{[^\n]+\})\n\n"
        r"## Reviewed identity SHA-256\n\n([0-9a-f]{64})\n",
        prompt,
    )
    if identity_match is None:
        raise SystemExit(94)
    identity = json.loads(identity_match.group(1))
    identity_sha = identity_match.group(2)
    verdicts_path = home / "fake-review-verdicts.json"
    verdicts = json.loads(verdicts_path.read_text(encoding="utf-8"))
    verdict = verdicts.pop(0) if verdicts else "pass"
    write_json(verdicts_path, verdicts)
    findings = (
        [{
            "id": "F-1",
            "severity": "p1",
            "exact_location": "design.md",
            "violated_requirement_or_contradiction": "missing test fixture",
            "concrete_impact": "the fake integration chain is incomplete",
        }]
        if verdict == "fail"
        else []
    )
    answer = json.dumps(
        {
            "reviewed_identity": identity,
            "reviewed_identity_sha256": identity_sha,
            "verdict": verdict,
            "findings": findings,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    artifact = artifacts / "transcript.md"
    artifact.write_bytes(b"# Fake Oracle transcript\n\n## Answer\n" + answer + b"\n")
    kind = "transcript"

payload = artifact.read_bytes()
write_json(
    session / "meta.json",
    {
        "id": slug,
        "mode": "browser",
        "status": "completed",
        "artifacts": [{
            "kind": kind,
            "path": artifact.relative_to(session).as_posix(),
            "sizeBytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "validation": {"ok": True},
        }],
    },
)
"""

_API_SENTINELS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "ORACLE_API_KEY",
)


def _fake_runtime(
    tmp_path: Path,
    git_env: dict[str, str],
    verdicts: list[str],
    remote_chrome: str,
    *,
    repository_access_failure: bool = False,
) -> tuple[dict[str, str], Path, Path]:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    executable = fake_bin / "oracle"
    executable.write_text(_FAKE_ORACLE, encoding="utf-8")
    executable.chmod(0o755)
    oracle_home = tmp_path / "oracle-home-v0.16.1"
    oracle_home.mkdir()
    (oracle_home / "fake-review-verdicts.json").write_text(
        json.dumps(verdicts),
        encoding="utf-8",
    )
    if repository_access_failure:
        (oracle_home / "fake-repository-access-failure").touch()
    env = {
        **os.environ,
        "GIT_SSH_COMMAND": git_env["GIT_SSH_COMMAND"],
        "ORACLE_HOME_DIR": str(oracle_home),
        "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', os.defpath)}",
        "SPECDOCK_ORACLE_REMOTE_CHROME": remote_chrome,
    }
    env.update({key: f"sentinel-{key.lower()}" for key in _API_SENTINELS})
    return env, oracle_home, executable


def _invocation_records(oracle_home: Path) -> list[dict[str, Any]]:
    path = oracle_home / "fake-oracle-invocations.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _assert_oracle_submission(
    records: list[dict[str, Any]],
    *,
    target: Path,
    oracle_home: Path,
    executable: Path,
    env: dict[str, str],
    expected_attachment_paths: tuple[Path, ...] = (),
) -> None:
    prompt_records = [record for record in records if "--prompt" in record["argv"]]
    assert len(prompt_records) == 1
    assert prompt_records[0]["cwd"] == str(target)
    assert executable.is_file() and os.access(executable, os.X_OK)
    assert all(record["argv"][0] == str(executable) for record in records)
    assert all("--write-output" not in record["argv"] for record in records)
    forbidden = {
        "--project",
        "--profile",
        "--host",
        "--config",
        "--backend",
        "oracle-chatgpt",
        "chatgpt-use",
        "--browser-attach-running",
        "--browser-manual-login",
        "--browser-manual-login-profile-dir",
        "--browser-chrome-profile",
        "--browser-cookie-path",
        "--copy-profile",
        "--browser-port",
        "--browser-debug-port",
        "--browser-inline-cookies",
        "--browser-inline-cookies-file",
    }
    assert all(not forbidden.intersection(record["argv"]) for record in records)
    child_environment = prompt_records[0]["environment"]
    assert all(key not in child_environment for key in _API_SENTINELS)
    assert "SPECDOCK_ORACLE_REMOTE_CHROME" not in child_environment
    argv = prompt_records[0]["argv"]
    assert argv[1:10] == [
        "--engine",
        "browser",
        "--model",
        "Pro",
        "--browser-model-strategy",
        "select",
        "--remote-chrome",
        env["SPECDOCK_ORACLE_REMOTE_CHROME"],
        "--browser-no-cookie-sync",
    ]
    prompt = prompt_records[0]["prompt"]
    head = _run_git(target, "rev-parse", "HEAD", env=env)
    assert '"repository":"chemitaro/spec-dock"' in prompt
    assert f'"branch":"{BRANCH}"' in prompt
    assert f'"source_head":"{head}"' in prompt
    assert "Never substitute the default branch" in prompt
    assert '"kind":"authoring_zip"' in prompt or '"kind":"review_json"' in prompt
    onboarding_headings = (
        "init-/epic-/iss- lineage",
        "Purpose/scope",
        "System context",
        "Authority/responsibility",
        "Current architecture/target architecture",
        "ChatGPT First planning workflow",
        "Provider-owned direct Oracle/reference-only chatgpt-use",
        "Candidate/Review/Human/apply lifecycle",
        "Exact branch failure",
        "S01/S07/S08/S14 status/roadmap",
        "Provider/projection",
        "Failure modes",
        "First-day checklist",
    )
    if '"kind":"authoring_zip"' in prompt:
        assert "13 nonempty distinct H2s, exact labels, no split/merge" not in prompt
        assert all(heading not in prompt for heading in onboarding_headings)
        assert "4+ valid `plantuml` fences" not in prompt
    else:
        assert "13 nonempty distinct H2s, exact labels, no split/merge" not in prompt
        assert all(heading not in prompt for heading in onboarding_headings)
        assert (
            "4+ valid `plantuml` fences: system context/responsibility boundary/"
            "planning sequence/implementation roadmap."
        ) not in prompt
    assert len(prompt_records[0]["attachment_paths"]) >= 1
    assert all("prompt-pack" not in path for path in prompt_records[0]["attachment_paths"])
    assert str(oracle_home) not in prompt
    if expected_attachment_paths:
        assert prompt_records[0]["attachment_paths"][-len(expected_attachment_paths) :] == [
            str(path) for path in expected_attachment_paths
        ]


def _invoke(
    target: Path,
    args: list[str],
    *,
    env: dict[str, str],
    oracle_home: Path,
    executable: Path,
    expects_oracle: bool = False,
    expected_returncode: int = 0,
    expected_attachment_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    before = len(_invocation_records(oracle_home))
    completed = subprocess.run(
        [
            str(target / "spec-dock/scripts/spec-dock-chatgpt"),
            *args,
            "--format",
            "json",
        ],
        # Keep the caller outside the repository so the fake Oracle's recorded
        # cwd proves that the runtime passed the exact repository root explicitly.
        cwd=target.parent,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == expected_returncode, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    public = json.dumps(result, sort_keys=True)
    assert str(oracle_home) not in public
    assert "prompt-pack" not in public
    assert "/sessions/" not in public
    new_records = _invocation_records(oracle_home)[before:]
    if expects_oracle:
        _assert_oracle_submission(
            new_records,
            target=target,
            oracle_home=oracle_home,
            executable=executable,
            env=env,
            expected_attachment_paths=expected_attachment_paths,
        )
    else:
        assert new_records == []
    return result


def _create(
    target: Path,
    output: Path,
    *,
    env: dict[str, str],
    oracle_home: Path,
    executable: Path,
    provided_paths: tuple[Path, ...] = (),
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    args = ["planning", "create", "--issue", ISSUE_ID, "--output", str(output)]
    for path in provided_paths:
        args.extend(["--provided-context-path", str(path)])
    result = _invoke(
        target,
        args,
        env=env,
        oracle_home=oracle_home,
        executable=executable,
        expects_oracle=True,
        expected_attachment_paths=provided_paths,
    )
    assert (result["status"], result["reason"]) == ("ok", "candidate_created")
    identity = result["output"]["candidate_identity"]
    candidate = output / identity["logical_filename"]
    _assert_candidate_contract(candidate)
    return candidate, identity, result


def _review(
    target: Path,
    output: Path,
    *,
    mode: str,
    candidate: Path,
    env: dict[str, str],
    oracle_home: Path,
    executable: Path,
    provided_paths: tuple[Path, ...] = (),
) -> tuple[Path, dict[str, Any]]:
    args = [
        "review",
        "planning",
        "--issue",
        ISSUE_ID,
        "--mode",
        mode,
        "--output",
        str(output),
    ]
    args.extend(["--candidate", str(candidate)])
    if mode == "git-bound":
        args.extend(["--reviewed-head", _run_git(target, "rev-parse", "HEAD", env=env)])
    for path in provided_paths:
        args.extend(["--provided-context-path", str(path)])
    result = _invoke(
        target,
        args,
        env=env,
        oracle_home=oracle_home,
        executable=executable,
        expects_oracle=True,
        expected_attachment_paths=provided_paths,
    )
    assert (result["status"], result["reason"]) == ("ok", "review_completed")
    return output / result["output"]["review_result_file"], result


def _assert_candidate_contract(candidate: Path) -> None:
    with zipfile.ZipFile(candidate) as archive:
        root = candidate.name.removesuffix(".zip")
        manifest = json.loads(archive.read(f"{root}/MANIFEST.json"))
        entries = manifest["entries"]
        assert sum(entry["role"] == "onboarding-companion" for entry in entries) == 1
        assert sorted(
            entry["role"] for entry in entries if entry["path"] in {"requirement.md", "design.md", "plan.md"}
        ) == ["design", "plan", "requirement"]
        companion = next(entry for entry in entries if entry["role"] == "onboarding-companion")
        checksums = archive.read(f"{root}/CHECKSUMS.sha256").decode("ascii")
        assert f"  {companion['path']}" in checksums
        source = json.loads(archive.read(f"{root}/SOURCE-BASELINE.json"))
        assert len(source["canonical_issue_paths"]) == 3


def _candidate_companion(
    candidate: Path,
    candidate_identity: dict[str, Any],
) -> tuple[str, bytes]:
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == candidate_identity["zip_sha256"]
    with zipfile.ZipFile(candidate) as archive:
        root = candidate.name.removesuffix(".zip")
        manifest = json.loads(archive.read(f"{root}/MANIFEST.json"))
        companion = next(entry for entry in manifest["entries"] if entry["role"] == "onboarding-companion")
        payload = archive.read(f"{root}/{companion['path']}")
        checksums = archive.read(f"{root}/CHECKSUMS.sha256").decode("ascii")
    assert CURRENT_ROADMAP in payload
    assert f"{hashlib.sha256(payload).hexdigest()}  {companion['path']}" in checksums.splitlines()
    return companion["path"], payload


def _assert_pass_review_carries_companion(
    review_path: Path,
    *,
    mode: str,
    candidate_identity: dict[str, Any],
    companion_path: str,
    companion_bytes: bytes,
) -> None:
    review = json.loads(review_path.read_bytes())
    assert review["verdict"] == "pass"
    reviewed_identity = review["reviewed_identity"]
    if mode == "archive-candidate":
        assert reviewed_identity["candidate_identity"] == candidate_identity
        return
    binding = reviewed_identity["git_bound_operation_binding"]
    assert binding["candidate_identity"] == candidate_identity
    assert binding["onboarding_companion"] == {
        "path": companion_path,
        "sha256": hashlib.sha256(companion_bytes).hexdigest(),
    }


def _assert_ready_companion(
    target: Path,
    operation: Path,
    *,
    issue_dir: Path,
    companion_path: str,
    companion_bytes: bytes,
) -> None:
    operation_files = list(operation.glob("planning-apply-*/operation.json"))
    assert len(operation_files) == 1
    payload = json.loads(operation_files[0].read_text(encoding="utf-8"))
    expected_target = (issue_dir.relative_to(target) / companion_path).as_posix()
    assert payload["companion_target_path"] == expected_target
    assert payload["companion_sha256"] == hashlib.sha256(companion_bytes).hexdigest()
    assert (target / expected_target).read_bytes() == companion_bytes


def _write_approval(review_path: Path, destination: Path) -> dict[str, Any]:
    review_bytes = review_path.read_bytes()
    review = json.loads(review_bytes)
    decision = {
        "schema_version": 1,
        "issue_id": ISSUE_ID,
        "reviewed_identity": review["reviewed_identity"],
        "reviewed_identity_sha256": review["reviewed_identity_sha256"],
        "review_result_sha256": hashlib.sha256(review_bytes).hexdigest(),
        "decision": "approved",
        "plan_adoption": True,
        "implementation_start": True,
        "decided_at": "2026-07-28T09:00:00+00:00",
    }
    destination.write_text(
        json.dumps(decision, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    return decision


def _forbidden_snapshot(target: Path, issue_dir: Path) -> dict[str, bytes]:
    initiatives = target / "spec-dock/initiatives"
    snapshot: dict[str, bytes] = {}
    for path in initiatives.rglob("*"):
        if not path.is_file():
            continue
        if path.is_relative_to(issue_dir) and path.name != ".assurance.json":
            continue
        snapshot[path.relative_to(target).as_posix()] = path.read_bytes()
    return snapshot


@pytest.fixture
def fake_cdp_endpoint():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/json/version":
                self.send_error(404)
                return
            host, port = cast("tuple[str, int]", self.server.server_address)
            payload = json.dumps({
                "webSocketDebuggerUrl": f"ws://{host}:{port}/devtools/browser/fake",
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = cast("tuple[str, int]", server.server_address)
    try:
        yield f"{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_exact_repository_access_failure_creates_no_candidate_or_mutation(
    tmp_path: Path,
    fake_cdp_endpoint: str,
) -> None:
    target, _bare, issue_dir, env = _prepare_target(tmp_path)
    runtime_env, oracle_home, executable = _fake_runtime(
        tmp_path,
        env,
        [],
        fake_cdp_endpoint,
        repository_access_failure=True,
    )
    output = tmp_path / "candidate"
    output.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    canonical_before = {name: (issue_dir / name).read_bytes() for name in ("requirement.md", "design.md", "plan.md")}

    result = _invoke(
        target,
        ["planning", "create", "--issue", ISSUE_ID, "--output", str(output)],
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
        expects_oracle=True,
        expected_returncode=1,
    )

    assert (result["status"], result["reason"]) == (
        "blocked",
        "github_exact_branch_unavailable",
    )
    assert result["output"] == {}
    assert list(output.iterdir()) == []
    assert canonical_before == {name: (issue_dir / name).read_bytes() for name in canonical_before}
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert _run_git(target, "status", "--porcelain", env=env) == ""


def test_archive_full_fake_chain_reaches_ready(
    tmp_path: Path,
    fake_cdp_endpoint: str,
) -> None:
    target, bare, issue_dir, env = _prepare_target(tmp_path)
    runtime_env, oracle_home, executable = _fake_runtime(
        tmp_path,
        env,
        ["pass"],
        fake_cdp_endpoint,
    )
    output = tmp_path / "candidate"
    reviews = tmp_path / "reviews"
    operation = tmp_path / "operation"
    for path in (output, reviews, operation):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    canonical_before = {name: (issue_dir / name).read_bytes() for name in ("requirement.md", "design.md", "plan.md")}
    candidate, identity, _ = _create(
        target,
        output,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    companion_path, companion_bytes = _candidate_companion(candidate, identity)
    review_path, _ = _review(
        target,
        reviews,
        mode="archive-candidate",
        candidate=candidate,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    _assert_pass_review_carries_companion(
        review_path,
        mode="archive-candidate",
        candidate_identity=identity,
        companion_path=companion_path,
        companion_bytes=companion_bytes,
    )
    assert canonical_before == {name: (issue_dir / name).read_bytes() for name in canonical_before}
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert _run_git(target, "status", "--porcelain", env=env) == ""
    decision_path = tmp_path / "decision.json"
    _write_approval(review_path, decision_path)
    result = _invoke(
        target,
        [
            "planning",
            "apply",
            "--issue",
            ISSUE_ID,
            "--mode",
            "archive-candidate",
            "--review-result",
            str(review_path),
            "--human-decision",
            str(decision_path),
            "--expected-head",
            _run_git(target, "rev-parse", "HEAD", env=env),
            "--output",
            str(operation),
            "--candidate",
            str(candidate),
            "--logical-filename",
            identity["logical_filename"],
            "--zip-sha256",
            identity["zip_sha256"],
        ],
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    assert result["status"] == "ready"
    _assert_ready_companion(
        target,
        operation,
        issue_dir=issue_dir,
        companion_path=companion_path,
        companion_bytes=companion_bytes,
    )
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert (
        _run_git(target, "rev-parse", "HEAD", env=env)
        == subprocess.check_output(
            ["git", "--git-dir", str(bare), "rev-parse", f"refs/heads/{BRANCH}"],
            text=True,
        ).strip()
    )


def test_git_bound_full_fake_chain_reaches_ready(
    tmp_path: Path,
    fake_cdp_endpoint: str,
) -> None:
    target, bare, issue_dir, env = _prepare_target(tmp_path)
    runtime_env, oracle_home, executable = _fake_runtime(
        tmp_path,
        env,
        ["pass"],
        fake_cdp_endpoint,
    )
    output = tmp_path / "candidate"
    reviews = tmp_path / "reviews"
    operation = tmp_path / "operation"
    for path in (output, reviews, operation):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    before = {name: (issue_dir / name).read_bytes() for name in ("requirement.md", "design.md", "plan.md")}
    candidate, identity, create = _create(
        target,
        output,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    companion_path, companion_bytes = _candidate_companion(candidate, identity)
    review_path, review = _review(
        target,
        reviews,
        mode="git-bound",
        candidate=candidate,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    _assert_pass_review_carries_companion(
        review_path,
        mode="git-bound",
        candidate_identity=identity,
        companion_path=companion_path,
        companion_bytes=companion_bytes,
    )
    binding = create["output"]["git_bound_operation_binding_sha256"]
    assert review["output"]["git_bound_operation_binding_sha256"] == binding
    assert before == {name: (issue_dir / name).read_bytes() for name in before}
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert _run_git(target, "status", "--porcelain", env=env) == ""
    decision_path = tmp_path / "decision.json"
    decision = _write_approval(review_path, decision_path)
    assert decision["reviewed_identity"]["git_bound_operation_binding"]["binding_sha256"] == binding
    head = _run_git(target, "rev-parse", "HEAD", env=env)
    result = _invoke(
        target,
        [
            "planning",
            "apply",
            "--issue",
            ISSUE_ID,
            "--mode",
            "git-bound",
            "--review-result",
            str(review_path),
            "--human-decision",
            str(decision_path),
            "--expected-head",
            head,
            "--output",
            str(operation),
            "--candidate",
            str(candidate),
            "--reviewed-head",
            head,
        ],
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
    )
    assert result["status"] == "ready"
    operation_files = list(operation.glob("planning-apply-*/operation.json"))
    assert len(operation_files) == 1
    assert json.loads(operation_files[0].read_text(encoding="utf-8"))["git_bound_operation_binding_sha256"] == binding
    _assert_ready_companion(
        target,
        operation,
        issue_dir=issue_dir,
        companion_path=companion_path,
        companion_bytes=companion_bytes,
    )
    assert before == {name: (issue_dir / name).read_bytes() for name in before}
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert (
        _run_git(target, "rev-parse", "HEAD", env=env)
        == subprocess.check_output(
            ["git", "--git-dir", str(bare), "rev-parse", f"refs/heads/{BRANCH}"],
            text=True,
        ).strip()
    )


def test_failed_review_semantic_revision_reaches_fresh_pass(
    tmp_path: Path,
    fake_cdp_endpoint: str,
) -> None:
    target, _bare, issue_dir, env = _prepare_target(tmp_path)
    runtime_env, oracle_home, executable = _fake_runtime(
        tmp_path,
        env,
        ["fail", "pass"],
        fake_cdp_endpoint,
    )
    candidates = tmp_path / "candidates"
    first_reviews = tmp_path / "first-reviews"
    revised = tmp_path / "revised"
    fresh_reviews = tmp_path / "fresh-reviews"
    for path in (candidates, first_reviews, revised, fresh_reviews):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    create_context_paths = (Path("operator/create"), Path("operator/create"))
    review_context_paths = (Path("operator/review"), Path("/outside/review"))
    revision_context_paths = (Path("operator/revision"), Path("/outside/revision"))
    candidate, identity, _ = _create(
        target,
        candidates,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
        provided_paths=create_context_paths,
    )
    old_bytes = candidate.read_bytes()
    review_path, first_review = _review(
        target,
        first_reviews,
        mode="archive-candidate",
        candidate=candidate,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
        provided_paths=review_context_paths,
    )
    request_path = review_path.with_name("planning-revision-request.json")
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "lane": "semantic",
                "candidate_identity": identity,
                "preserve_assumptions": ["keep approved scope"],
                "finding_ids": ["F-1"],
                "review_result_sha256": first_review["output"]["review_result_sha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    revision = _invoke(
        target,
        [
            "planning",
            "revise",
            "--candidate",
            str(candidate),
            "--request",
            str(request_path),
            "--output",
            str(revised),
            "--provided-context-path",
            str(revision_context_paths[0]),
            "--provided-context-path",
            str(revision_context_paths[1]),
        ],
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
        expects_oracle=True,
        expected_attachment_paths=revision_context_paths,
    )
    assert (revision["status"], revision["reason"]) == ("ok", "candidate_revised")
    new_identity = revision["output"]["candidate_identity"]
    new_candidate = revised / new_identity["logical_filename"]
    _assert_candidate_contract(new_candidate)
    fresh_review_path, fresh = _review(
        target,
        fresh_reviews,
        mode="archive-candidate",
        candidate=new_candidate,
        env=runtime_env,
        oracle_home=oracle_home,
        executable=executable,
        provided_paths=review_context_paths,
    )
    assert fresh["output"]["verdict"] == "pass"
    assert new_identity["version"] == identity["version"] + 1
    assert new_identity["candidate_id"] != identity["candidate_id"]
    assert new_identity["zip_sha256"] != identity["zip_sha256"]
    assert candidate.read_bytes() == old_bytes
    assert fresh_review_path.is_file()
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert _run_git(target, "status", "--porcelain", env=env) == ""
