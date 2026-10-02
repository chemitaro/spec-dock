"""Fresh wheel consoles perform a complete same-clone work lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class InstalledConsole:
    executable: Path
    outside: Path
    environment: dict[str, str]
    provenance: dict[str, str]

    def run(self, root: Path, *arguments: str, expected_exit: int = 0) -> dict[str, Any]:
        completed = subprocess.run(
            [str(self.executable), "--project", str(root), *arguments, "--json"],
            cwd=self.outside,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert completed.returncode == expected_exit, (arguments, completed.stdout, completed.stderr)
        assert completed.stderr == ""
        payload = json.loads(completed.stdout)
        assert payload["schema_version"] == "specdock.cli/v2"
        assert payload["exit_code"] == expected_exit
        return payload


def install_console(tmp_path: Path) -> InstalledConsole:
    """Copy the current provider, then make that owned source path unavailable."""
    source = tmp_path / "provider"
    source.mkdir()
    shutil.copytree(ROOT / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"))
    for name in ("README.md", "pyproject.toml"):
        shutil.copy2(ROOT / name, source / name)
    source_digest = hashlib.sha256()
    for path in sorted(source.rglob("*")):
        if path.is_file():
            source_digest.update(path.relative_to(source).as_posix().encode() + b"\0")
            source_digest.update(hashlib.sha256(path.read_bytes()).digest())
    outside = tmp_path / "outside"
    outside.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    environment = {
        key: value for key, value in os.environ.items() if key in {"PATH", "SYSTEMROOT", "TMP", "TEMP", "TMPDIR"}
    }
    cache = subprocess.check_output(["uv", "cache", "dir"], text=True).strip()
    environment.update(
        HOME=str(home),
        XDG_CONFIG_HOME=str(home / "config"),
        UV_CACHE_DIR=cache,
        UV_OFFLINE="1",
        PIP_NO_INDEX="1",
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=str(home / "gitconfig"),
    )
    wheels = tmp_path / "wheels"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(wheels)],
        cwd=source,
        env=environment,
        check=True,
        capture_output=True,
    )
    wheel = next(wheels.glob("*.whl"))
    venv = tmp_path / "installed"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], env=environment, check=True, capture_output=True)
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run(
        ["uv", "pip", "install", "--python", str(python), str(wheel)],
        env=environment,
        check=True,
        capture_output=True,
    )
    subprocess.run([str(python), "-m", "pip", "check"], env=environment, check=True, capture_output=True)
    source.rename(tmp_path / "provider-unavailable")
    imported = subprocess.check_output(
        [str(python), "-I", "-c", "import spec_dock; print(spec_dock.__file__)"],
        cwd=outside,
        env=environment,
        text=True,
    ).strip()
    assert Path(imported).is_relative_to(venv)
    assert not source.exists()
    assert "PYTHONPATH" not in environment and "PYTHONHOME" not in environment
    provenance = {
        "provider_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "provider_source_status": subprocess.check_output(
            ["git", "status", "--porcelain", "--", "src", "README.md", "pyproject.toml", "uv.lock"],
            cwd=ROOT,
            text=True,
        ),
        "provider_source_sha256": source_digest.hexdigest(),
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "imported_package": imported,
        "python": sys.version,
        "platform": sys.platform,
    }
    return InstalledConsole(
        venv / ("Scripts/spec-dock.exe" if os.name == "nt" else "bin/spec-dock"), outside, environment, provenance
    )


def git(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *arguments], stderr=subprocess.PIPE)


def committed_hierarchy(root: Path) -> None:
    root.mkdir()
    git(root, "init", "--initial-branch=main", "-q")
    workspace = root / "spec-dock"
    initiative = workspace / "initiatives/init-00001-fixture"
    epic = initiative / "epics/epic-00002-fixture"
    for path, scope_id, kind, number, parent, initiative_id, epic_id in (
        (initiative, "init-00001", "initiative", 1, None, None, None),
        (epic, "epic-00002", "epic", 2, "init-00001", "init-00001", None),
        (epic / "issues/iss-00003-fixture", "iss-00003", "issue", 3, "epic-00002", "init-00001", "epic-00002"),
        (epic / "issues/iss-00004-fixture", "iss-00004", "issue", 4, "epic-00002", "init-00001", "epic-00002"),
        (epic / "issues/iss-00005-fixture", "iss-00005", "issue", 5, "epic-00002", "init-00001", "epic-00002"),
    ):
        path.mkdir(parents=True)
        metadata = {
            "schema_version": 3,
            "id": scope_id,
            "type": kind,
            "title": "Fixture",
            "slug": "fixture",
            "parent_id": parent,
            "initiative_id": initiative_id,
            "epic_id": epic_id,
            "backend": "github",
            "github": {"repo_owner": "example", "repo_name": "repo", "issue_number": number},
            "lifecycle": None,
            "revision": 0,
            "depends_on": [],
            "created_at": "2026-09-30T00:00:00Z",
            "updated_at": "2026-09-30T00:00:00Z",
        }
        (path / ".meta.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
        for name in ("requirement.md", "design.md", "plan.md", "report.md"):
            (path / name).write_text("# Fixture\n", encoding="utf-8")
    (workspace / "workspace.json").write_text(
        '{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n', encoding="utf-8"
    )
    (workspace / ".gitignore").write_text(".agent/\n.workbench/\n", encoding="utf-8")
    git(root, "add", "--", "spec-dock")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")


def github_process(tmp_path: Path, console: InstalledConsole) -> tuple[Path, Path]:
    """Only the external gh process is substituted; Git and consoles stay native."""
    state = tmp_path / "github.json"
    state.write_text(json.dumps({str(number): "open" for number in range(1, 6)}), encoding="utf-8")
    log = tmp_path / "github-calls.jsonl"
    binary = tmp_path / "bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\nfrom pathlib import Path\n"
        "args=sys.argv[1:]\n"
        "assert args[:4] == ['api','--hostname','github.com','--include']\n"
        "assert args[4] == '--method'\n"
        "method, endpoint = args[5:7]\n"
        "assert method in ('GET','PATCH') and endpoint.startswith('repos/example/repo/issues/')\n"
        "number=endpoint.rsplit('/',1)[1]\n"
        "state=Path(os.environ['SPECDOCK_TEST_GITHUB_STATE'])\n"
        "states=json.loads(state.read_text())\nassert number in states\n"
        "request=json.loads(sys.stdin.read()) if method == 'PATCH' else None\n"
        "if method == 'PATCH':\n"
        " assert args[7:] == ['--input','-']\n"
        " assert request == {'state':'closed','state_reason':'completed'}\n"
        " states[number]='completed'\n state.write_text(json.dumps(states))\n"
        "with Path(os.environ['SPECDOCK_TEST_GITHUB_LOG']).open('a') as out:\n"
        " out.write(json.dumps({'method':method,'number':int(number),'request':request})+'\\n')\n"
        "completed=states[number]=='completed'\n"
        "print('HTTP/2 200 OK\\n\\n'+json.dumps({'number':int(number),"
        "'repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':'https://github.com/example/repo/issues/'+number,'title':'Fixture',"
        "'state':'closed' if completed else 'open','state_reason':'completed' if completed else None,"
        "'updated_at':'2026-09-30T00:00:00Z'}))\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    console.environment.update(
        PATH=str(binary) + os.pathsep + console.environment.get("PATH", ""),
        SPECDOCK_TEST_GITHUB_STATE=str(state),
        SPECDOCK_TEST_GITHUB_LOG=str(log),
    )
    return state, log


def snapshot(root: Path) -> dict[str, tuple[int, bytes]]:
    return {
        path.relative_to(root).as_posix(): (path.stat().st_mode, path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    }


def test_fresh_console_start_parallel_sync_finish_and_next_issue(tmp_path: Path) -> None:
    console = install_console(tmp_path)
    seed = tmp_path / "seed"
    committed_hierarchy(seed)
    root = tmp_path / "main"
    subprocess.run(["git", "clone", "--no-hardlinks", str(seed), str(root)], check=True, capture_output=True)
    linked = tmp_path / "linked"
    git(root, "worktree", "add", "--detach", str(linked), "HEAD")
    state, log = github_process(tmp_path, console)
    evidence: dict[str, Any] = {"provenance": console.provenance, "operations": []}
    inputs = {
        path: path.read_bytes()
        for worktree in (root, linked)
        for path in (worktree / "spec-dock").rglob("*")
        if path.is_file()
    }

    def start(worktree: Path, target: str, branch: str, *, expected_exit: int = 0) -> dict[str, Any]:
        result = console.run(
            worktree, "work", "start", target, "--branch", branch, "--base", "HEAD", expected_exit=expected_exit
        )
        evidence["operations"].append(result)
        return result

    before_preview = snapshot(root)
    preview = console.run(root, "work", "start", "iss-00003", "--branch", "issue-a", "--base", "HEAD", "--dry-run")
    assert preview["status"] == "planned" and snapshot(root) == before_preview
    assert not (root / "spec-dock/.agent").exists()
    first = start(root, "iss-00003", "issue-a")
    assert first["data"]["started"] is True and git(root, "branch", "--show-current") == b"issue-a\n"
    first_record = root / "spec-dock/.agent/work-target" / f"target-{first['data']['selection_token']}.json"
    first_bytes = first_record.read_bytes()
    assert json.loads(first_bytes)["scope_id"] == "iss-00003"
    assert git(root, "status", "--porcelain") == b""

    linked_before = snapshot(linked)
    refs_before = git(root, "show-ref")
    collision = start(linked, "iss-00003", "duplicate", expected_exit=3)
    assert collision["error"]["code"] == "SCOPE_ALREADY_SELECTED" and collision["effects"] == []
    assert snapshot(linked) == linked_before and git(root, "show-ref") == refs_before
    assert first_record.read_bytes() == first_bytes

    second = start(linked, "iss-00004", "issue-b")
    assert second["data"]["started"] is True and git(linked, "branch", "--show-current") == b"issue-b\n"
    linked_record = linked / "spec-dock/.agent/work-target" / f"target-{second['data']['selection_token']}.json"
    linked_bytes = linked_record.read_bytes()
    before_sync = {worktree: snapshot(worktree) for worktree in (root, linked)}
    sync = console.run(root, "workspace", "sync", "--source", "github")
    evidence["operations"].append(sync)
    assert sync["effects"] == [] and sync["data"]["complete"] is True
    assert {row["selection"]["scope_id"] for row in sync["data"]["worktrees"]} == {"iss-00003", "iss-00004"}
    counts = {row["scope_id"]: row for row in sync["data"]["counts"]}
    assert counts["init-00001"]["descendant_selected_count"] == 2
    assert counts["epic-00002"]["direct_selected_count"] == 0
    assert counts["epic-00002"]["descendant_selected_count"] == 2
    assert all(snapshot(worktree) == value for worktree, value in before_sync.items())

    finish_preview = console.run(root, "work", "finish", "@current", "--dry-run")
    assert finish_preview["status"] == "planned" and first_record.read_bytes() == first_bytes
    assert json.loads(state.read_bytes())["3"] == "open"
    finished = console.run(root, "work", "finish", "@current", "--yes")
    evidence["operations"].append(finished)
    assert finished["data"]["completed"] is True and not first_record.exists()
    assert json.loads(state.read_bytes())["3"] == "completed"
    assert git(root, "branch", "--show-current") == b"issue-a\n"
    assert linked_record.read_bytes() == linked_bytes
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert [call for call in calls if call["method"] == "PATCH"] == [
        {"method": "PATCH", "number": 3, "request": {"state": "closed", "state_reason": "completed"}}
    ]
    assert calls[-1] == {"method": "GET", "number": 3, "request": None}

    next_issue = start(root, "iss-00005", "issue-c")
    assert next_issue["data"]["started"] is True
    assert next_issue["data"]["selection_token"] != first["data"]["selection_token"]
    assert git(root, "branch", "--show-current") == b"issue-c\n"
    assert linked_record.read_bytes() == linked_bytes
    for worktree in (root, linked):
        assert git(worktree, "status", "--porcelain") == b""
        assert len(list((worktree / "spec-dock/.agent/work-target").iterdir())) == 1
        assert not (worktree / "spec-dock/.agent/github-status-cache.json").exists()
        assert not (worktree / "spec-dock/.agent/active.json").exists()
    assert all(path.read_bytes() == value for path, value in inputs.items())
    assert not (root / ".git/spec-dock").exists()
    assert not (root / ".git/spec-dock-control").exists()
    assert not (root / "spec-dock/scripts/spec_dock_runtime").exists()
    evidence["github_calls"] = [json.loads(line) for line in log.read_text().splitlines()]
    (tmp_path / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps({"console_provenance": console.provenance}, sort_keys=True))
