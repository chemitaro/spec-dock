"""Publish GitHub-numbered Scopes through the control-free public CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from spec_dock.cli import main


@pytest.mark.parametrize("operation", ["create", "import"])
def test_scope_publication_preview_does_not_load_retired_writers_or_control(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, log = publication_fixture(tmp_path, monkeypatch)
    before = tree_digest(root)
    command = (
        ["scope", "create", "initiative", "--backend", "github"]
        if operation == "create"
        else ["scope", "import", "github", "initiative", "gh:example/repo#413"]
    )
    script = (
        "import sys\nfrom spec_dock.cli import main\n"
        "assert main(sys.argv[1:]) == 0\n"
        "retired = {'spec_dock.runtime.application.create_node', "
        "'spec_dock.runtime.application.create_github_scope', "
        "'spec_dock.runtime.application.operation_executor', "
        "'spec_dock.runtime.application.sync_state', "
        "'spec_dock.runtime.infra.writer_lock', "
        "'spec_dock.runtime.infra.operation_journal', "
        "'spec_dock.runtime.infra.control_store'}\n"
        "loaded = sorted(retired.intersection(sys.modules))\nassert loaded == [], loaded\n"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            "--project",
            str(root),
            *command,
            "--title",
            "Isolated publication",
            "--dry-run",
            "--json",
        ],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["schema_version"] == "specdock.cli/v2" and result["status"] == "planned"
    assert all(effect["status"] == "planned" for effect in result["effects"])
    assert not completed.stderr and tree_digest(root) == before
    if operation == "create":
        assert not log.exists()
    else:
        assert [(call["method"], call["endpoint"]) for call in map(json.loads, log.read_text().splitlines())] == [
            ("GET", "repos/example/repo/issues/413")
        ]


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
@pytest.mark.parametrize("operation", ["create", "import"])
@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("missing", ["platform", "native-symbol"])
def test_scope_publication_without_a_safe_primitive_stops_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    operation: str,
    dry_run: bool,
    missing: str,
    kind: str,
) -> None:
    from types import SimpleNamespace

    from spec_dock.runtime.infra import json_store
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, log = publication_fixture(tmp_path, monkeypatch)
    parent: list[str] = []
    if kind == "epic":
        parent = ["--parent", "init-00001"]
    elif kind == "issue":
        from tests.cli_runtime.test_issue413_contract import add_scope

        add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
        parent = ["--parent", "epic-00002"]
    before = tree_digest(root)
    if missing == "platform":
        monkeypatch.setattr(json_store, "sys", SimpleNamespace(platform="unavailable"))
    else:
        monkeypatch.setattr(json_store, "ctypes", SimpleNamespace(CDLL=lambda *args, **kwargs: SimpleNamespace()))
    command = (
        ["scope", "create", kind, "--backend", "github"]
        if operation == "create"
        else ["scope", "import", "github", kind, "gh:example/repo#413"]
    )
    assert (
        main([
            "--project",
            str(root),
            *command,
            *parent,
            "--title",
            "Unavailable publication",
            "--yes",
            *(["--dry-run"] if dry_run else []),
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "LOCAL_IO_FAILED" and result["effects"] == []
    assert not log.exists() and not (root / "spec-dock/.agent").exists()
    assert tree_digest(root) == before


def test_new_local_scope_is_rejected_before_project_access(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "scope",
            "create",
            "initiative",
            "--backend",
            "local",
            "--title",
            "New Scope",
            "--json",
        ])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


def test_scope_create_help_describes_only_github_numbered_publication(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["help", "scope", "create", "initiative"]) == 0
    output = capsys.readouterr().out
    assert "local creation" not in output
    assert "specdock.cli/v2" in output
    assert "GitHub" in output
    assert "--resume" not in output
    assert "--rollback" not in output
    assert "journal" not in output


@pytest.mark.parametrize("imported", [False, True])
@pytest.mark.parametrize("guard", [["--expect-current", "init-00001"], ["--expect-backend", "local"]])
def test_scope_publication_expectation_mismatch_stops_before_remote_observation_or_local_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    imported: bool,
    guard: list[str],
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()
    command = (
        ["scope", "import", "github", "initiative", "gh:example/repo#413"]
        if imported
        else ["scope", "create", "initiative", "--backend", "github"]
    )
    assert main(["--project", str(root), *command, "--title", "Guarded Scope", *guard, "--yes", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "PRECONDITION_FAILED" and result["effects"] == []
    assert metadata.read_bytes() == before and not log.exists() and not (root / "spec-dock/.agent").exists()
    assert sorted(path.name for path in (root / "spec-dock/initiatives").iterdir()) == ["init-00001-fixture"]


@pytest.mark.parametrize("kind,prefix", [("initiative", "init"), ("epic", "epic"), ("issue", "iss")])
@pytest.mark.parametrize("imported", [False, True])
def test_scope_publication_accepts_canonical_current_and_backend_guards_with_dynamic_parents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    prefix: str,
    imported: bool,
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture
    from tests.cli_runtime.test_issue413_contract import add_scope

    root, log = publication_fixture(tmp_path, monkeypatch)
    number = 1
    scope_id = "init-00001"
    parent: list[str] = []
    if kind == "epic":
        parent = ["--parent", "@initiative"]
    elif kind == "issue":
        epic = add_scope(root, "epic-00002", "epic", "init-00001", root / "spec-dock/initiatives/init-00001-fixture")
        add_scope(root, "iss-00003", "issue", "epic-00002", epic)
        scope_id, number, parent = "iss-00003", 3, ["--parent", "@epic"]
    record = select_fixture(root, scope_id=scope_id, number=number)
    before = record.read_bytes()
    command = (
        ["scope", "import", "github", kind, "gh:example/repo#413"]
        if imported
        else ["scope", "create", kind, "--backend", "github"]
    )
    assert (
        main([
            "--project",
            str(root),
            *command,
            *parent,
            "--title",
            "Guarded Scope",
            "--expect-current",
            f"gh:example/repo#{number}",
            "--expect-backend",
            "github",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["id"] == f"{prefix}-{413 if imported else 57:05d}"
    assert record.read_bytes() == before
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert sum(row["method"] == "POST" for row in calls) == (0 if imported else 1)
    assert not (root / ".git/spec-dock").exists()


def test_created_metadata_remains_editable_without_a_permission_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _ = publication_fixture(tmp_path, monkeypatch)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    path = root / "spec-dock/initiatives/init-00057-new-scope/.meta.json"
    metadata = json.loads(path.read_bytes())
    metadata["title"] = "Manual Edit"
    path.write_text(json.dumps(metadata))
    assert main(["--project", str(root), "scope", "show", "init-00057", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["title"] == "Manual Edit"


def test_create_dry_run_needs_no_confirmation_and_publishes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--dry-run",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["result"]["can_apply"] is True
    assert result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["changed"] is False
    assert [effect["status"] for effect in result["effects"]] == ["planned", "planned"]
    assert result["data"]["result"]["scope"] is None
    assert not log.exists()
    assert not (root / "spec-dock/.agent").exists()
    assert all(path.read_bytes() == payload for path, payload in before.items())


@pytest.mark.parametrize("mode", [[], ["--non-interactive"]])
def test_create_json_without_yes_stops_before_github_or_local_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: list[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            *mode,
            "--json",
        ])
        == 3
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["error"]["code"] == "CONFIRMATION_REQUIRED"
    assert result["effects"] == []
    assert not log.exists()
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX terminal fixture")
@pytest.mark.parametrize("answer", [b"yes\n", b"no\n"])
def test_scope_create_accepts_a_terminal_confirmation_after_planning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: bytes
) -> None:
    import pty

    root, log = publication_fixture(tmp_path, monkeypatch)
    master, slave = pty.openpty()
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "spec_dock.cli",
                "--project",
                str(root),
                "scope",
                "create",
                "initiative",
                "--backend",
                "github",
                "--title",
                "New Scope",
            ],
            stdin=slave,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        )
        os.write(master, answer)
        stdout, stderr = process.communicate(timeout=8)
    finally:
        os.close(master)
        os.close(slave)
    assert b"Confirm" in stderr
    assert b"example/repo" in stderr
    if answer == b"yes\n":
        assert process.returncode == 0, stdout + stderr
        assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["POST"]
        assert (root / "spec-dock/initiatives/init-00057-new-scope/.meta.json").exists()
    else:
        assert process.returncode == 3, stdout + stderr
        assert b"CONFIRMATION_DECLINED" in stderr
        assert not log.exists()
        assert not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native FIFO boundary")
def test_scope_create_rejects_an_injected_fifo_without_blocking_directory_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    script = (
        "import os, sys\nfrom pathlib import Path\nfrom spec_dock.cli import main\n"
        f"root=Path({str(root)!r})\noriginal=os.listdir\ninjected=False\n"
        "def listing(path):\n"
        " global injected\n"
        " if isinstance(path,int) and not injected:\n"
        "  for stage in root.glob('spec-dock/.agent/staging/.stage-*'):\n"
        "   if stage.stat().st_ino==os.fstat(path).st_ino:\n"
        "    os.mkfifo('fixture.pipe',dir_fd=path); injected=True; break\n"
        " return original(path)\n"
        "os.listdir=listing\n"
        "sys.exit(main(['--project',str(root),'scope','create','initiative','--backend','github',"
        "'--title','New Scope','--yes','--json']))\n"
    )
    try:
        process = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            timeout=5,
            env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src")),
        )
    except subprocess.TimeoutExpired:
        pytest.fail("Scope publication blocked while opening an unsupported FIFO")
    assert process.returncode == 6, process.stdout + process.stderr
    result = json.loads(process.stdout)
    assert result["effects"] == [
        {"kind": "github-create", "status": "succeeded", "target": "gh:example/repo#57"},
        {"kind": "scaffold", "status": "failed", "target": "init-00057"},
    ]
    assert "unsupported entry" in result["error"]["message"]
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["POST"]
    assert not (root / "spec-dock/initiatives/init-00057-new-scope").exists()


def publication_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    from tests.cli_runtime.test_issue413_work_start import committed_workspace

    root = committed_workspace(tmp_path / "consumer")
    assets = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock"
    for relative in ("templates", "docs/rules"):
        shutil.copytree(assets / relative, root / "spec-dock" / relative)
    subprocess.run(
        ["git", "-C", str(root), "remote", "add", "origin", "https://github.com/example/repo.git"],
        check=True,
        capture_output=True,
    )
    bin_dir = tmp_path / "gh-bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-requests.jsonl"
    executable = bin_dir / "gh"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\n"
        "argv=sys.argv[1:]; method=argv[argv.index('--method')+1]; endpoint=argv[argv.index('--method')+2]\n"
        "assert argv[:5]==['api','--hostname','github.com','--include','--method']\n"
        "payload=json.load(sys.stdin) if '--input' in argv else None\n"
        f"with open({str(log)!r},'a') as stream: stream.write(json.dumps(dict(method=method,endpoint=endpoint,payload=payload))+'\\n')\n"
        "if method=='GET':\n"
        " number=int(endpoint.rsplit('/',1)[-1]); assert endpoint==f'repos/example/repo/issues/{number}'\n"
        " response=dict(number=number,repository_url='https://api.github.com/repos/example/repo',"
        "html_url=f'https://github.com/example/repo/issues/{number}',title='Existing Scope',"
        "state='open',state_reason=None,updated_at='2026-10-01T00:00:00Z')\n"
        " print('HTTP/2.0 200 OK\\n\\n'+json.dumps(response)); sys.exit(0)\n"
        "assert method=='POST' and endpoint=='repos/example/repo/issues'\n"
        "response=dict(number=57,repository_url='https://api.github.com/repos/example/repo',"
        "html_url='https://github.com/example/repo/issues/57',title=payload['title'],"
        "state='open',state_reason=None,updated_at='2026-10-01T00:00:00Z')\n"
        "print('HTTP/2.0 201 Created\\n\\n'+json.dumps(response))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    return root, log


@pytest.mark.parametrize("phase,scaffold_status", [("before-publish", "failed"), ("after-publish", "unknown")])
def test_parent_directory_swap_during_scaffold_sync_never_writes_the_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    phase: str,
    scaffold_status: str,
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, log = publication_fixture(tmp_path, monkeypatch)
    parent = root / "spec-dock/initiatives/init-00001-fixture"
    (parent / "epics").mkdir(exist_ok=True)
    metadata = (parent / ".meta.json").read_bytes()
    detached = tmp_path / "detached-parent"
    original_fsync = os.fsync
    swapped = False
    replacement_digest = None

    def sync(descriptor: int) -> None:
        nonlocal swapped, replacement_digest
        original_fsync(descriptor)
        if swapped:
            return
        opened = os.fstat(descriptor)
        if phase == "before-publish":
            directories = tuple((root / "spec-dock/.agent/staging").glob(".stage-*"))
        elif (parent / "epics/epic-00057-new-epic").is_dir():
            directories = (parent / "epics",)
        else:
            return
        if not any((item.stat().st_dev, item.stat().st_ino) == (opened.st_dev, opened.st_ino) for item in directories):
            return
        parent.rename(detached)
        parent.mkdir()
        (parent / ".meta.json").write_bytes(metadata)
        (parent / "epics").mkdir()
        (parent / "epics/external.txt").write_bytes(b"external replacement")
        replacement_digest = tree_digest(parent)
        swapped = True

    monkeypatch.setattr(os, "fsync", sync)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "epic",
            "--backend",
            "github",
            "--parent",
            "init-00001",
            "--title",
            "New Epic",
            "--yes",
            "--json",
        ])
        == 6
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert swapped and output.err == "" and result["status"] == "partial"
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#57"
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", scaffold_status),
    ]
    assert result["error"] is not None
    assert tree_digest(parent) == replacement_digest
    assert (detached / ".meta.json").read_bytes() == metadata
    published = detached / "epics/epic-00057-new-epic"
    if phase == "before-publish":
        assert not published.exists()
    else:
        assert json.loads((published / ".meta.json").read_bytes())["id"] == "epic-00057"
    assert [(call["method"], call["endpoint"]) for call in map(json.loads, log.read_text().splitlines())] == [
        ("GET", "repos/example/repo/issues/1"),
        ("POST", "repos/example/repo/issues"),
    ]
    assert not (root / ".git/spec-dock").exists()


def test_create_uses_the_confirmed_github_number_without_control_or_a_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    existing = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = existing.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "succeeded"
    scope = root / "spec-dock/initiatives/init-00057-new-scope"
    metadata = json.loads((scope / ".meta.json").read_bytes())
    assert metadata["schema_version"] == 3 and metadata["id"] == "init-00057"
    assert metadata["backend"] == "github"
    assert metadata["github"] == {"issue_number": 57, "repo_owner": "example", "repo_name": "repo"}
    assert metadata["lifecycle"] is None and metadata["depends_on"] == []
    assert (scope / "requirement.md").is_file()
    assert (scope / "design.md").is_file() and (scope / "plan.md").is_file()
    assert (scope / "epics/rules.md").is_symlink() and (scope / "epics/rules.md").is_file()
    assert result["data"]["result"]["scope"]["id"] == "init-00057"
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "succeeded"),
    ]
    calls = list(map(json.loads, log.read_text().splitlines()))
    assert len(calls) == 1 and calls[0]["method"] == "POST"
    assert "spec-dock-operation" not in calls[0]["payload"]["body"]
    assert existing.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()
    assert "operation_id" not in result
    created = result["data"]["result"]["scope"]
    assert created["kind"] == "initiative" and created["title"] == "New Scope"
    assert created["backend"] == "github" and created["github_ref"] == "gh:example/repo#57"
    assert created["parent_id"] is None and created["revision"] == 0


@pytest.mark.parametrize("changed_identity", [False, True])
def test_confirmed_directory_publication_keeps_success_effect_after_descriptor_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], changed_identity: bool
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    published = root / "spec-dock/initiatives/init-00057-new-scope"
    real_close = os.close
    failed = False

    def close(descriptor):
        nonlocal failed
        observed = os.fstat(descriptor)
        final = published.stat() if published.exists() else None
        should_fail = (
            not failed and final is not None and (observed.st_dev, observed.st_ino) == (final.st_dev, final.st_ino)
        )
        real_close(descriptor)
        if should_fail:
            failed = True
            if changed_identity:
                metadata_path = published / ".meta.json"
                metadata = json.loads(metadata_path.read_bytes())
                metadata["github"]["issue_number"] = 99
                metadata_path.write_text(json.dumps(metadata))
            raise OSError("fixture: descriptor cleanup failed after confirmed publication")

    monkeypatch.setattr(os, "close", close)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert failed is True
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "succeeded"),
    ]
    assert json.loads((published / ".meta.json").read_bytes())["id"] == "init-00057"
    assert result["data"]["result"]["changed"] is True
    scope = result["data"]["result"]["scope"]
    if changed_identity:
        assert scope is None
        assert json.loads((published / ".meta.json").read_bytes())["github"]["issue_number"] == 99
    else:
        assert scope["id"] == "init-00057" and scope["github_ref"] == "gh:example/repo#57"
        assert scope["path"] == "spec-dock/initiatives/init-00057-new-scope"
        assert scope["kind"] == "initiative" and scope["title"] == "New Scope" and scope["parent_id"] is None
        assert scope["revision"] == 0 and scope["backend"] == "github"
        assert scope["status"]["state"] == "open" and scope["status"]["source"] == "github"
    assert len(log.read_text().splitlines()) == 1


def test_creation_refuses_unignored_staging_before_a_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    (root / "spec-dock/.gitignore").write_bytes(b"")
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert not log.exists() and not (root / "spec-dock/.agent").exists()
    assert "operation_id" not in result


@pytest.mark.parametrize("status", [400, 410, 422])
def test_confirmed_create_rejection_keeps_all_inputs_and_does_not_retry_or_allocate_an_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], status: int
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(executable.read_text().replace("HTTP/2.0 201 Created", f"HTTP/2.0 {status} Rejected"))
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "Rejected Scope",
            "--yes",
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["data"]["result"]["scope"] is None
    assert result["data"]["result"]["github_ref"] is None and result["data"]["result"]["changed"] is False
    assert result["effects"] == [
        {"kind": "github-create", "status": "failed", "target": "example/repo"},
        {"kind": "scaffold", "status": "not_attempted", "target": None},
    ]
    assert [row["method"] for row in map(json.loads, log.read_text().splitlines())] == ["POST"]
    assert tree_digest(root) == before and not (root / "spec-dock/.agent").exists()
    assert not (root / ".git/spec-dock").exists() and "operation_id" not in result


def test_unknown_create_response_keeps_scope_unpublished_and_never_retries_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(executable.read_text().replace("HTTP/2.0 201 Created", "HTTP/2.0 503 Unavailable"))
    before = {path: path.read_bytes() for path in root.glob("spec-dock/**/.meta.json")}
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["data"]["result"]["scope"] is None
    assert result["data"]["result"]["github_ref"] is None
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "unknown"),
        ("scaffold", "not_attempted"),
    ]
    assert result["recovery"]["can_resume"] is False and result["recovery"]["can_rollback"] is False
    assert all(path.read_bytes() == value for path, value in before.items())
    assert not (root / "spec-dock/initiatives/init-00057-new-scope").exists()
    assert len(log.read_text().splitlines()) == 1


def test_confirmed_create_number_already_linked_in_current_tree_is_not_published_twice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(executable.read_text().replace("number=57", "number=1").replace("issues/57", "issues/1"))
    existing = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = existing.read_bytes()
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#1"
    assert result["data"]["result"]["scope"] is None
    assert result["effects"][0]["status"] == "succeeded"
    assert result["effects"][1]["status"] == "not_attempted"
    assert not (root / "spec-dock/initiatives/init-00001-new-scope").exists()
    assert existing.read_bytes() == before
    assert len(log.read_text().splitlines()) == 1


def test_confirmed_remote_create_followed_by_local_input_change_reports_the_ref_and_keeps_the_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    executable = tmp_path / "gh-bin/gh"
    change = (
        f"with open({str(metadata)!r}) as stream: metadata=json.load(stream)\n"
        "metadata['title']='Actor Edit'; metadata['revision']+=1\n"
        f"with open({str(metadata)!r},'w') as stream: json.dump(metadata,stream)\n"
    )
    executable.write_text(executable.read_text().replace("print('HTTP/2.0 201", change + "print('HTTP/2.0 201"))
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["data"]["result"]["scope"] is None
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#57"
    assert [(effect["kind"], effect["status"]) for effect in result["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "not_attempted"),
    ]
    assert "import" in " ".join(result["recovery"]["instructions"])
    assert json.loads(metadata.read_bytes())["title"] == "Actor Edit"
    assert not (root / "spec-dock/initiatives/init-00057-new-scope").exists()
    assert len(log.read_text().splitlines()) == 1


def test_missing_template_is_rejected_before_github_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    shutil.rmtree(root / "spec-dock/templates/initiative")
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    assert not log.exists()
    assert not (root / "spec-dock/initiatives/init-00057-new-scope").exists()


def test_scaffold_temporary_directories_are_ignored_and_removed_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _ = publication_fixture(tmp_path, monkeypatch)
    real_mkdir = os.mkdir
    stages = []

    def mkdir(path, *args, **kwargs):
        result = real_mkdir(path, *args, **kwargs)
        candidate = Path(path)
        if candidate.name.startswith("."):
            if not candidate.is_absolute():
                descriptor = kwargs.get("dir_fd")
                parents = (
                    root / "spec-dock",
                    root / "spec-dock/initiatives",
                    root / "spec-dock/.agent",
                    root / "spec-dock/.agent/staging",
                )
                anchor = next(
                    (
                        parent
                        for parent in parents
                        if descriptor is not None
                        and parent.exists()
                        and (parent.stat().st_dev, parent.stat().st_ino)
                        == (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino)
                    ),
                    None,
                )
                if anchor is None:
                    return result
                candidate = anchor / candidate
            if not candidate.is_relative_to(root):
                return result
            if candidate.name != ".agent":
                relative = candidate.relative_to(root).as_posix()
                ignored = (
                    subprocess.run(
                        ["git", "-C", str(root), "check-ignore", "--no-index", "-q", "--", relative],
                        check=False,
                        capture_output=True,
                    ).returncode
                    == 0
                )
                stages.append((candidate, ignored))
        return result

    monkeypatch.setattr(os, "mkdir", mkdir)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    assert stages and all(ignored for _, ignored in stages)
    assert all(not path.exists() for path, _ in stages)
    assert not (root / ".git/spec-dock").exists()


def test_redirected_private_staging_is_rejected_before_remote_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "spec-dock/.agent").symlink_to(outside, target_is_directory=True)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert not log.exists() and list(outside.iterdir()) == []


@pytest.mark.parametrize("kind,prefix", [("initiative", "init"), ("epic", "epic"), ("issue", "iss")])
def test_all_three_scope_kinds_keep_github_numbered_hierarchy_and_live_parents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str, prefix: str
) -> None:
    from tests.cli_runtime.test_issue413_contract import add_scope

    root, log = publication_fixture(tmp_path, monkeypatch)
    parent = root / "spec-dock/initiatives/init-00001-fixture"
    options = []
    expected_gets = []
    if kind == "epic":
        options = ["--parent", "init-00001"]
        expected_gets = ["repos/example/repo/issues/1"]
        destination = parent / "epics/epic-00057-new-scope"
    elif kind == "issue":
        parent = add_scope(root, "epic-00002", "epic", "init-00001", parent)
        options = ["--parent", "epic-00002"]
        expected_gets = ["repos/example/repo/issues/2", "repos/example/repo/issues/1"]
        destination = parent / "issues/iss-00057-new-scope"
    else:
        destination = root / "spec-dock/initiatives/init-00057-new-scope"
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            kind,
            "--backend",
            "github",
            "--title",
            "New Scope",
            *options,
            "--yes",
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    metadata = json.loads((destination / ".meta.json").read_bytes())
    assert metadata["id"] == f"{prefix}-00057" and metadata["type"] == kind
    assert metadata["parent_id"] == (None if kind == "initiative" else options[1])
    assert metadata["initiative_id"] == (None if kind == "initiative" else "init-00001")
    assert metadata["epic_id"] == ("epic-00002" if kind == "issue" else None)
    assert metadata["github"]["issue_number"] == 57
    assert result["data"]["result"]["scope"]["id"] == f"{prefix}-00057"
    calls = list(map(json.loads, log.read_text().splitlines()))
    assert [row["endpoint"] for row in calls if row["method"] == "GET"] == expected_gets
    assert sum(row["method"] == "POST" for row in calls) == 1


@pytest.mark.parametrize("kind,closed_number", [("epic", 1), ("issue", 2), ("issue", 1)])
@pytest.mark.parametrize("reason", ["completed", "not_planned"])
def test_scope_create_rejects_a_live_closed_parent_or_ancestor_before_post_and_keeps_all_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    closed_number: int,
    reason: str,
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest
    from tests.cli_runtime.test_issue413_contract import add_scope

    root, log = publication_fixture(tmp_path, monkeypatch)
    parent = "init-00001"
    if kind == "issue":
        add_scope(root, "epic-00002", "epic", parent, root / "spec-dock/initiatives/init-00001-fixture")
        parent = "epic-00002"
    executable = tmp_path / "gh-bin/gh"
    executable.write_text(
        executable.read_text().replace(
            " print('HTTP/2.0 200 OK\\n\\n'+json.dumps(response)); sys.exit(0)\n",
            f" if number=={closed_number}: response.update(state='closed',state_reason={reason!r})\n"
            " print('HTTP/2.0 200 OK\\n\\n'+json.dumps(response)); sys.exit(0)\n",
        )
    )
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            kind,
            "--backend",
            "github",
            "--title",
            "Blocked Child",
            "--parent",
            parent,
            "--yes",
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["effects"] == []
    calls = list(map(json.loads, log.read_text().splitlines()))
    expected_numbers = [2, 1] if kind == "issue" and closed_number == 1 else [closed_number]
    assert [(row["method"], row["endpoint"]) for row in calls] == [
        ("GET", f"repos/example/repo/issues/{number}") for number in expected_numbers
    ]
    assert tree_digest(root) == before and not (root / "spec-dock/.agent").exists()
    assert not (root / ".git/spec-dock").exists()


def test_repository_change_during_create_keeps_the_confirmed_old_ref_without_local_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    executable = tmp_path / "gh-bin/gh"
    change = (
        f"subprocess.run(['git','-C',{str(root)!r},'remote','set-url','origin',"
        "'https://github.com/other/repository.git'],check=True,capture_output=True)\n"
    )
    executable.write_text(
        executable
        .read_text()
        .replace("import json,sys", "import json,sys,subprocess")
        .replace("print('HTTP/2.0 201", change + "print('HTTP/2.0 201")
    )
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 6
    )
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["github_ref"] == "gh:example/repo#57"
    assert result["effects"][0]["status"] == "succeeded"
    assert result["effects"][1]["status"] == "not_attempted"
    assert not (root / "spec-dock/initiatives/init-00057-new-scope").exists()
    assert len(log.read_text().splitlines()) == 1


def test_git_repository_lookup_failure_preserves_native_stderr_and_returncode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    real_git = shutil.which("git")
    assert real_git is not None
    executable = tmp_path / "gh-bin/git"
    original_error = "fatal: fixture remote lookup refused\nsecond original line\n"
    executable.write_text(
        f"#!{sys.executable}\nimport os,sys\n"
        "if 'remote' in sys.argv and 'get-url' in sys.argv:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    executable.chmod(0o755)
    assert (
        main([
            "--project",
            str(root),
            "scope",
            "create",
            "initiative",
            "--backend",
            "github",
            "--title",
            "New Scope",
            "--yes",
            "--json",
        ])
        == 5
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert result["error"]["details"]["git"]["stderr"] == original_error
    assert result["error"]["details"]["git"]["returncode"] == 73
    assert not log.exists()
