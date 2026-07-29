from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from types import SimpleNamespace

from spec_dock.cli import main as installer_main

REPO_ROOT = Path(__file__).resolve().parents[2]
BRANCH = "feature/issue-planning"
ISSUE_ID = "iss-00334"


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


def _planner_payload(issue_dir: Path, marker: str) -> bytes:
    parts: list[bytes] = []
    names = ("requirement.md", "design.md", "plan.md")
    for index, name in enumerate(names):
        body = (issue_dir / name).read_bytes().rstrip() + f"\n\n{marker}\n".encode()
        parts.append(f"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>\n".encode())
        parts.append(body)
        parts.append(f"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>".encode())
        if index != len(names) - 1:
            parts.append(b"\n")
    return b"".join(parts)


def _backend_fake(issue_dir: Path, review_verdicts: list[str]):
    planner_calls = 0

    def invoke(request, *, env):
        nonlocal planner_calls
        prompt = (request.prompt_pack / "chatgpt-use-prompt.md").read_text(encoding="utf-8")
        match = re.search(
            r"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=(planner|reviewer) "
            r"source_head=([0-9a-f]{40})>>>",
            prompt,
        )
        assert match is not None
        role, source_head = match.groups()
        if role == "planner":
            planner_calls += 1
            payload = _planner_payload(issue_dir, f"S06 fake planner version {planner_calls}")
        else:
            identity = json.loads((request.prompt_pack / "reviewed-identity.json").read_text(encoding="utf-8"))
            identity_sha = (request.prompt_pack / "reviewed-identity-sha256.txt").read_text(encoding="ascii").strip()
            verdict = review_verdicts.pop(0) if review_verdicts else "pass"
            findings = (
                [
                    {
                        "id": "F-1",
                        "severity": "p1",
                        "exact_location": "design.md",
                        "violated_requirement_or_contradiction": "missing test fixture",
                        "concrete_impact": "the fake integration chain is incomplete",
                    }
                ]
                if verdict == "fail"
                else []
            )
            payload = json.dumps(
                {
                    "reviewed_identity": identity,
                    "reviewed_identity_sha256": identity_sha,
                    "verdict": verdict,
                    "findings": findings,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        framed = (
            (f"<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role={role} source_head={source_head}>>>\n").encode()
            + payload
            + b"\n<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>\n"
        )
        argv = shlex.split(request.backend_command)
        assert argv.count("--write-output") == 1
        output_index = argv.index("--write-output")
        assert output_index + 1 < len(argv)
        final_output = Path(argv[output_index + 1])
        assert final_output.is_absolute()
        final_output.write_bytes(framed)
        return (
            SimpleNamespace(status="pass", blockers=(), exit_code=0),
            SimpleNamespace(stdout=b"fake backend diagnostic", stderr=b""),
        )

    return invoke


@contextmanager
def _installed_runtime(target: Path, issue_dir: Path, verdicts: list[str]):
    previous = {
        name: module
        for name, module in tuple(sys.modules.items())
        if name == "spec_dock_runtime" or name.startswith("spec_dock_runtime.")
    }
    for name in previous:
        sys.modules.pop(name, None)
    scripts = target / "spec-dock/scripts"
    sys.path.insert(0, str(scripts))
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        from spec_dock_runtime import chatgpt_app
        from spec_dock_runtime.infra import issue_planning_chatgpt

        issue_planning_chatgpt.invoke_backend_with_capture = _backend_fake(
            issue_dir,
            verdicts,
        )
        yield chatgpt_app
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
        sys.path.remove(str(scripts))
        for name in tuple(sys.modules):
            if name == "spec_dock_runtime" or name.startswith("spec_dock_runtime."):
                sys.modules.pop(name, None)
        sys.modules.update(previous)


def _invoke(app, target: Path, args: list[str]) -> dict[str, object]:
    stdout = io.StringIO()
    previous = Path.cwd()
    os.chdir(target)
    try:
        with redirect_stdout(stdout):
            code = app.main([*args, "--format", "json"])
    finally:
        os.chdir(previous)
    assert code == 0, stdout.getvalue()
    return json.loads(stdout.getvalue())


def _create(app, target: Path, output: Path) -> tuple[Path, dict[str, object]]:
    result = _invoke(
        app,
        target,
        ["planning", "create", "--issue", ISSUE_ID, "--output", str(output)],
    )
    assert (result["status"], result["reason"]) == ("ok", "candidate_created")
    identity = result["output"]["candidate_identity"]
    candidate = output / identity["logical_filename"]
    return candidate, identity


def _review(
    app,
    target: Path,
    output: Path,
    *,
    mode: str,
    candidate: Path | None = None,
) -> tuple[Path, dict[str, object]]:
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
    if candidate is not None:
        args.extend(["--candidate", str(candidate)])
    else:
        args.extend(["--reviewed-head", _run_git(target, "rev-parse", "HEAD", env=os.environ)])
    result = _invoke(app, target, args)
    assert (result["status"], result["reason"]) == ("ok", "review_completed")
    return output / result["output"]["review_result_file"], result


def _write_approval(review_path: Path, destination: Path) -> dict[str, object]:
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


def test_archive_full_fake_chain_reaches_ready(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target, bare, issue_dir, env = _prepare_target(tmp_path)
    monkeypatch.setenv("GIT_SSH_COMMAND", env["GIT_SSH_COMMAND"])
    output = tmp_path / "candidate"
    reviews = tmp_path / "reviews"
    operation = tmp_path / "operation"
    for path in (output, reviews, operation):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    with _installed_runtime(target, issue_dir, ["pass"]) as app:
        candidate, identity = _create(app, target, output)
        review_path, _ = _review(
            app,
            target,
            reviews,
            mode="archive-candidate",
            candidate=candidate,
        )
        decision_path = tmp_path / "decision.json"
        _write_approval(review_path, decision_path)
        result = _invoke(
            app,
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
        )
    assert result["status"] == "ready"
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
    monkeypatch,
) -> None:
    target, bare, issue_dir, env = _prepare_target(tmp_path)
    monkeypatch.setenv("GIT_SSH_COMMAND", env["GIT_SSH_COMMAND"])
    output = tmp_path / "candidate"
    reviews = tmp_path / "reviews"
    operation = tmp_path / "operation"
    for path in (output, reviews, operation):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    before = {name: (issue_dir / name).read_bytes() for name in ("requirement.md", "design.md", "plan.md")}
    with _installed_runtime(target, issue_dir, ["pass"]) as app:
        _create(app, target, output)
        review_path, _ = _review(app, target, reviews, mode="git-bound")
        decision_path = tmp_path / "decision.json"
        _write_approval(review_path, decision_path)
        head = _run_git(target, "rev-parse", "HEAD", env=env)
        result = _invoke(
            app,
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
                "--reviewed-head",
                head,
            ],
        )
    assert result["status"] == "ready"
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
    monkeypatch,
) -> None:
    target, _bare, issue_dir, env = _prepare_target(tmp_path)
    monkeypatch.setenv("GIT_SSH_COMMAND", env["GIT_SSH_COMMAND"])
    candidates = tmp_path / "candidates"
    first_reviews = tmp_path / "first-reviews"
    revised = tmp_path / "revised"
    fresh_reviews = tmp_path / "fresh-reviews"
    for path in (candidates, first_reviews, revised, fresh_reviews):
        path.mkdir()
    forbidden_before = _forbidden_snapshot(target, issue_dir)
    with _installed_runtime(target, issue_dir, ["fail", "pass"]) as app:
        candidate, identity = _create(app, target, candidates)
        old_bytes = candidate.read_bytes()
        review_path, first_review = _review(
            app,
            target,
            first_reviews,
            mode="archive-candidate",
            candidate=candidate,
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
            app,
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
            ],
        )
        assert (revision["status"], revision["reason"]) == ("ok", "candidate_revised")
        new_identity = revision["output"]["candidate_identity"]
        new_candidate = revised / new_identity["logical_filename"]
        fresh_review_path, fresh = _review(
            app,
            target,
            fresh_reviews,
            mode="archive-candidate",
            candidate=new_candidate,
        )
    assert fresh["output"]["verdict"] == "pass"
    assert new_identity["version"] == identity["version"] + 1
    assert new_identity["candidate_id"] != identity["candidate_id"]
    assert new_identity["zip_sha256"] != identity["zip_sha256"]
    assert candidate.read_bytes() == old_bytes
    assert fresh_review_path.is_file()
    assert _forbidden_snapshot(target, issue_dir) == forbidden_before
    assert _run_git(target, "status", "--porcelain", env=env) == ""
