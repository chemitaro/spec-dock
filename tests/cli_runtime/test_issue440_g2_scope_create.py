"""Canonical `scope create` and `scope import github` contracts kept from the legacy-mode tests (iss-00440).

Replaces the common-contract tests of tests/cli_runtime/test_issue413_scope_publish.py,
tests/cli_runtime/test_issue413_scope_import.py, tests/cli_runtime/test_scope_create_commands_vnext.py and
tests/cli_runtime/test_scope_import_commands_vnext.py, which used a schema-3 `.meta.json` fixture.
"""

from __future__ import annotations

import io
import os
import shutil
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.fake_github import FakeGithub

ASSURANCE = ("--assurance", "standard", "--assurance-reason", "fixture reason")


class TerminalAnswer(io.StringIO):
    def isatty(self) -> bool:
        return True


def _world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "leaf", parent=2)
    world.edit(lambda fake: fake.add_issue(57, title="Existing Work"))
    return world


def _catalog_entries(world: WriteWorld) -> list[str]:
    return sorted(path.relative_to(world.catalog).as_posix() for path in world.catalog.rglob("*"))


def _command(operation: str, kind: str, *parent: str) -> list[str]:
    if operation == "create":
        return ["scope", "create", kind, "--backend", "github", *parent, "--title", "New Work", *ASSURANCE]
    return ["scope", "import", "github", kind, "gh:example/repo#57", *parent, "--title", "Existing Work", *ASSURANCE]


def _assert_nothing_written(world: WriteWorld, before: list[str]) -> None:
    assert world.writes() == [] and world.changesets() == []
    assert _catalog_entries(world) == before


@pytest.mark.parametrize("kind,parent", [("initiative", ()), ("epic", ("--parent", "init-00001"))])
def test_scope_import_dry_run_reads_the_issue_without_writing_then_publishes_without_a_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], kind: str, parent: Any
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    code, payload = world.run(*_command("import", kind, *parent), "--dry-run")
    assert (code, payload["status"]) == (0, "planned"), payload
    assert payload["data"]["result"]["can_apply"] is True and payload["data"]["result"]["blockers"] == []
    assert payload["effects"] and all(effect["status"] == "planned" for effect in payload["effects"])
    assert payload["effects"][-1]["kind"] == "scaffold"
    _assert_nothing_written(world, before)
    code, payload = world.run(*_command("import", kind, *parent))
    assert code == 0, payload
    assert ("POST", "repos/example/repo/issues") not in [(method, path) for method, path, _ in world.writes()]
    assert payload["data"]["result"]["scope"]["id"] == f"{'init' if kind == 'initiative' else 'epic'}-00057"


@pytest.mark.parametrize("operation", ["create", "import"])
@pytest.mark.parametrize("missing", ["platform", "native-symbol"])
def test_scope_publication_without_a_safe_primitive_stops_before_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], operation: str, missing: str
) -> None:
    from types import SimpleNamespace

    from spec_dock.runtime.infra import json_store

    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    if missing == "platform":
        monkeypatch.setattr(json_store, "sys", SimpleNamespace(platform="unavailable"))
    else:
        monkeypatch.setattr(json_store, "ctypes", SimpleNamespace(CDLL=lambda *args, **kwargs: SimpleNamespace()))
    for dry_run in ((), ("--dry-run",)):
        code, payload = world.write(*_command(operation, "epic", "--parent", "init-00001"), *dry_run)
        assert (code, payload["error"]["code"], payload["effects"]) == (5, "LOCAL_IO_FAILED", []), payload
    _assert_nothing_written(world, before)


@pytest.mark.parametrize("operation", ["create", "import"])
@pytest.mark.parametrize("guard", [("--expect-current", "init-00001"), ("--expect-backend", "local")])
def test_scope_publication_expectation_mismatch_stops_before_any_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    operation: str,
    guard: tuple[str, str],
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.select("iss-00003", 3)
    record = next((world.main / "spec-dock/.agent/work-target").iterdir())
    selected = record.read_bytes()
    before = _catalog_entries(world)
    # Canonical mode reads the structure snapshot before checking the guards (legacy checked them first); the
    # contract kept here is that nothing is written.
    code, payload = world.write(*_command(operation, "initiative"), *guard)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    _assert_nothing_written(world, before)
    assert record.read_bytes() == selected


@pytest.mark.parametrize("kind,parent,created", [("epic", "@initiative", "epic"), ("issue", "@epic", "iss")])
@pytest.mark.parametrize("operation", ["create", "import"])
def test_scope_publication_accepts_canonical_current_and_backend_guards_with_dynamic_parents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    parent: str,
    created: str,
    operation: str,
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    world.select("iss-00003", 3)
    record = next((world.main / "spec-dock/.agent/work-target").iterdir())
    selected = record.read_bytes()
    # Canonical create/import pass no existing target to the guard check, so --expect-backend (even "github")
    # stops before any write; legacy mode accepted it. Only the --expect-current guard can pass here.
    code, payload = world.write(*_command(operation, kind, "--parent", parent), "--expect-backend", "github")
    assert (code, payload["error"]["code"]) == (3, "PRECONDITION_FAILED"), payload
    assert "requires one existing Scope target" in payload["error"]["message"] and world.writes() == []
    code, payload = world.write(*_command(operation, kind, "--parent", parent), "--expect-current", "gh:example/repo#3")
    assert code == 0, payload
    scope = payload["data"]["result"]["scope"]
    number = 57 if operation == "import" else 58
    assert scope["id"] == f"{created}-{number:05d}"
    assert scope["parent_id"] == ("init-00001" if kind == "epic" else "epic-00002")
    posts = [path for method, path, _ in world.writes() if method == "POST" and path == "repos/example/repo/issues"]
    assert len(posts) == (0 if operation == "import" else 1)
    assert record.read_bytes() == selected


@pytest.mark.parametrize("answer", ["yes\n", "no\n"])
def test_scope_create_accepts_a_terminal_confirmation_after_planning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], answer: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    monkeypatch.setattr(sys, "stdin", TerminalAnswer(answer))
    code = main(["--project", str(world.main), *_command("create", "initiative")])
    output = capsys.readouterr()
    assert "Confirm [yes/no]" in output.err and "example/repo" in output.err
    if answer == "yes\n":
        assert code == 0, output
        assert world.find("init-00058").is_dir()
    else:
        assert code == 3, output
        assert "CONFIRMATION_DECLINED" in output.err
        _assert_nothing_written(world, before)


def _fail_once(monkeypatch: pytest.MonkeyPatch, name: str, condition: Any, error: OSError) -> list[bool]:
    """Replace os.<name>: the first call that meets `condition` runs and then raises `error`."""
    original = getattr(os, name)
    fired: list[bool] = []

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        hit = not fired and condition(*args, **kwargs)
        result = original(*args, **kwargs)
        if hit:
            fired.append(True)
            raise error
        return result

    monkeypatch.setattr(os, name, wrapper)
    return fired


@pytest.mark.skipif(os.name != "posix", reason="native FIFO boundary")
def test_scope_create_rejects_an_injected_fifo_without_blocking_directory_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    staging = world.catalog / ".runtime/staging"
    original = os.listdir
    injected: list[bool] = []

    def listing(path: Any = ".") -> list[str]:
        if isinstance(path, int) and not injected and staging.is_dir():
            for stage in staging.glob(".stage-*"):
                if stage.stat().st_ino == os.fstat(path).st_ino:
                    os.mkfifo("fixture.pipe", dir_fd=path)
                    injected.append(True)
                    break
        return original(path)

    monkeypatch.setattr(os, "listdir", listing)
    code, payload = world.write(*_command("create", "initiative"))
    assert injected and (code, payload["status"]) == (6, "partial"), payload
    assert [(effect["kind"], effect["status"]) for effect in payload["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "failed"),
    ]
    assert "unsupported entry" in payload["error"]["message"]
    assert [path for method, path, _ in world.writes() if method == "POST"] == ["repos/example/repo/issues"]
    assert not (world.catalog / "00000-00999/init-00058").exists() and world.changesets() == []


def test_confirmed_directory_publication_keeps_success_effect_after_descriptor_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    published = world.catalog / "00000-00999/init-00058"

    def is_published(descriptor: int) -> bool:
        if not published.exists():
            return False
        observed, final = os.fstat(descriptor), published.stat()
        return (observed.st_dev, observed.st_ino) == (final.st_dev, final.st_ino)

    fired = _fail_once(monkeypatch, "close", is_published, OSError("fixture: descriptor cleanup failed"))
    code, payload = world.write(*_command("create", "initiative"))
    assert fired and (code, payload["status"]) == (6, "partial"), payload
    assert [(effect["kind"], effect["status"]) for effect in payload["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "succeeded"),
    ]
    assert payload["data"]["result"]["changed"] is True
    assert payload["data"]["result"]["github_ref"] == "gh:example/repo#58"
    assert (published / "requirement.cue").is_file()
    (changeset,) = world.changesets()
    assert changeset["paths"] == ["00000-00999/init-00058"]


@pytest.mark.parametrize("status", [400, 410, 422])
def test_confirmed_create_rejection_keeps_all_inputs_and_does_not_retry_or_allocate_an_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], status: int
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    world.edit(
        lambda fake: fake.inject(
            status=status, body={"message": "no"}, method="POST", endpoint="repos/example/repo/issues"
        )
    )
    code, payload = world.write(*_command("create", "initiative"))
    assert (code, payload["status"]) == (5, "failed"), payload
    result = payload["data"]["result"]
    assert (result["scope"], result["github_ref"], result["changed"]) == (None, None, False)
    # Canonical mode drops not_attempted steps from a failure that applied nothing (legacy listed scaffold).
    assert [(effect["kind"], effect["status"]) for effect in payload["effects"]] == [("github-create", "failed")]
    posts = [
        item for item in world.fake().requests if item.method == "POST" and item.endpoint == "repos/example/repo/issues"
    ]
    assert len(posts) == 1
    assert [issue.number for issue in world.fake().issues.values() if issue.number > 57] == []
    _assert_nothing_written_but(world, before, posts=1)


def _assert_nothing_written_but(world: WriteWorld, before: list[str], *, posts: int) -> None:
    assert len(world.writes()) == posts and world.changesets() == []
    assert _catalog_entries(world) == before


def test_unknown_create_response_never_retries_the_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    world.edit(
        lambda fake: fake.inject(status=503, body={"message": "x"}, method="POST", endpoint="repos/example/repo/issues")
    )
    code, payload = world.write(*_command("create", "initiative"))
    assert (code, payload["status"]) == (6, "partial"), payload
    assert [(effect["kind"], effect["status"]) for effect in payload["effects"]] == [
        ("github-create", "unknown"),
        ("scaffold", "not_attempted"),
    ]
    assert payload["data"]["result"]["github_ref"] is None
    _assert_nothing_written_but(world, before, posts=1)


def test_scaffold_temporary_directories_are_removed_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    original = os.mkdir
    stages: list[str] = []

    def mkdir(path: Any, *args: Any, **kwargs: Any) -> None:
        original(path, *args, **kwargs)
        if os.fspath(path).startswith(".stage-"):
            stages.append(os.fspath(path))

    monkeypatch.setattr(os, "mkdir", mkdir)
    code, payload = world.write(*_command("create", "initiative"))
    assert code == 0, payload
    assert stages
    staging = world.catalog / ".runtime/staging"
    assert not staging.exists() or list(staging.iterdir()) == []


def test_redirected_private_staging_is_rejected_before_writing_through_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    outside = tmp_path / "outside"
    outside.mkdir()
    runtime = world.catalog / ".runtime"
    runtime.mkdir(exist_ok=True)
    staging = runtime / "staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.symlink_to(outside, target_is_directory=True)
    code, payload = world.write(*_command("create", "initiative"))
    # Canonical staging lives in the catalog and is first opened after the GitHub create (legacy checked its
    # in-checkout staging before the POST), so the result is partial; nothing is written through the redirect.
    assert (code, payload["status"], payload["error"]["code"]) == (6, "partial", "SCOPE_PUBLICATION_INCOMPLETE")
    assert [(effect["kind"], effect["status"]) for effect in payload["effects"]] == [
        ("github-create", "succeeded"),
        ("scaffold", "failed"),
    ]
    assert list(outside.iterdir()) == []
    assert not (world.catalog / "00000-00999/init-00058").exists()


@pytest.mark.parametrize("closed,reason", [(1, "completed"), (1, "not_planned"), (2, "not_planned")])
def test_scope_create_rejects_a_live_closed_parent_or_ancestor_before_post_and_keeps_all_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    closed: int,
    reason: str,
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    assert world.run("scope", "show", "epic-00002")[0] == 0  # a fresh snapshot that still shows both open
    before = _catalog_entries(world)

    def close(fake: FakeGithub) -> None:
        fake.issue(closed).state, fake.issue(closed).state_reason = "closed", reason

    world.edit(close)
    code, payload = world.write(*_command("create", "issue", "--parent", "epic-00002"))
    assert (code, payload["status"], payload["error"]["code"], payload["effects"]) == (
        3,
        "failed",
        "PRECONDITION_FAILED",
        [],
    ), payload
    _assert_nothing_written(world, before)


def test_git_repository_lookup_failure_preserves_native_stderr_and_returncode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    real_git = shutil.which("git")
    assert real_git is not None
    wrapper = tmp_path / "git-bin/git"
    wrapper.parent.mkdir()
    original_error = "fatal: fixture remote lookup refused\nsecond original line\n"
    wrapper.write_text(
        f"#!{sys.executable}\nimport os,sys\n"
        "if 'remote' in sys.argv and 'get-url' in sys.argv:\n"
        f" sys.stderr.write({original_error!r}); sys.exit(73)\n"
        f"os.execv({real_git!r},['git',*sys.argv[1:]])\n"
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", f"{wrapper.parent}{os.pathsep}{os.environ['PATH']}")
    code, payload = world.write(*_command("create", "initiative"))
    assert (code, payload["error"]["code"], payload["effects"]) == (5, "GIT_FAILED", []), payload
    assert payload["error"]["details"]["git"]["stderr"] == original_error
    assert payload["error"]["details"]["git"]["returncode"] == 73
    _assert_nothing_written(world, before)


def test_github_scope_create_rejects_missing_parent_before_remote_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    code, payload = world.write(*_command("create", "epic", "--parent", "init-00999"))
    assert (code, payload["error"]["code"], payload["effects"]) == (4, "SCOPE_NOT_FOUND", []), payload
    _assert_nothing_written(world, before)


@pytest.mark.parametrize(
    "reference,hint",
    [("https://github.com/example/repo/issues/57", ()), ("57", ("--github-repo", "EXAMPLE/REPO"))],
)
def test_import_accepts_existing_exact_reference_forms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], reference: str, hint: Any
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    code, payload = world.run(
        "scope", "import", "github", "initiative", reference, *hint, "--title", "Existing Work", *ASSURANCE
    )
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["id"] == "init-00057"
    assert payload["data"]["result"]["github_ref"] == "gh:example/repo#57"


@pytest.mark.parametrize(
    "reference,extra",
    [
        ("gh:other/repo#57", ()),
        ("https://github.com/other/repo/issues/57", ()),
        ("57", ("--github-repo", "other/repo")),
        ("gh:example/repo#57", ("--offline",)),
    ],
)
def test_import_rejects_unbound_or_offline_refs_before_github_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], reference: str, extra: Any
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    code, payload = world.run(
        "scope", "import", "github", "initiative", reference, *extra, "--title", "Existing Work", *ASSURANCE
    )
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "PRECONDITION_FAILED", []), payload
    _assert_nothing_written(world, before)


@pytest.mark.parametrize("case", ["pull-request", "unavailable"])
def test_import_stops_on_a_rejected_or_unverified_get_without_publishing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], case: str
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    if case == "pull-request":
        world.edit(lambda fake: fake.add_issue(60, title="A pull request", pull_request=True))
    else:
        world.edit(lambda fake: fake.add_issue(60, title="Later"))
        world.edit(
            lambda fake: fake.inject(status=503, body={"message": "x"}, method="GET", endpoint="issues/60", times=10)
        )
    code, payload = world.run(
        "scope", "import", "github", "initiative", "gh:example/repo#60", "--title", "Later", *ASSURANCE
    )
    assert code != 0 and payload["status"] == "failed" and payload["effects"] == [], payload
    _assert_nothing_written(world, before)


@pytest.mark.parametrize("mode", [(), ("--non-interactive",)])
def test_create_json_without_yes_stops_before_github_or_local_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: tuple[str, ...]
) -> None:
    world = _world(tmp_path, monkeypatch, capsys)
    before = _catalog_entries(world)
    code, payload = world.run(*_command("create", "initiative"), *mode)
    assert (code, payload["error"]["code"], payload["effects"]) == (3, "CONFIRMATION_REQUIRED", []), payload
    _assert_nothing_written(world, before)
