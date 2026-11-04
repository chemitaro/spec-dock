"""Every public command runs canonical handling only (iss-00436, Epic G7; 53 leaves since 0.5.0, iss-00440; 54 with `dashboard summary`, iss-00528; 58 with `dashboard serve`, `hide`, `show`, `list`, iss-00529; 61 with `dashboard service install`, `status`, `uninstall`, iss-00530; 71 with the ten `todo` leaves, iss-00549).

One linked schema-4 clone with the fake GitHub runs all 71 leaves once; no leaf answers with a refusal-only code. GitHub is the fake on PATH, the catalog
pushes to the temporary bare remote and the save wait of `work finish` runs on an injected clock.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.commands.canonical_dispatch import CANONICAL_HANDLERS, REPOSITORY_INDEPENDENT_HANDLERS
from spec_dock.runtime.infra import github_structure
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import REPOSITORY
from tests.support.canonical_writes import WriteWorld

if TYPE_CHECKING:
    from pathlib import Path

# Routed by dispatch() before resolve_context: they read the declaration themselves or need none.
MODE_INDEPENDENT = {
    "installation show",
    "installation init",
    "installation update",
    "installation uninstall",
    "help",
    "completion",
}


def _canonical_code(code: object) -> bool:
    """Codes of the canonical mode carry a next step (R-H2); the generic codes shared with schema 3 keep their form."""
    return isinstance(code, str) and code.startswith(("CANONICAL_", "GITHUB_", "SCOPE_KIND_CHANGED"))


class _Clock:
    def __init__(self) -> None:
        self.offset = 0.0

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=self.offset)

    def monotonic(self) -> float:
        return self.offset

    def sleep(self, seconds: float) -> None:
        self.offset += seconds


def test_every_leaf_has_a_route_in_canonical_mode() -> None:
    unrouted = [
        path
        for path in LEAF_PATHS
        if path not in CANONICAL_HANDLERS
        and path not in REPOSITORY_INDEPENDENT_HANDLERS
        and path not in MODE_INDEPENDENT
    ]
    assert len(LEAF_PATHS) == 71
    assert unrouted == []
    # `dashboard serve`, `list` and `service` need no checkout: only the repository-independent table routes them.
    independent_only = {
        "canonical check",
        "dashboard serve",
        "dashboard list",
        "dashboard service install",
        "dashboard service status",
        "dashboard service uninstall",
        "todo settings",
    }
    assert set(CANONICAL_HANDLERS) == set(LEAF_PATHS) - MODE_INDEPENDENT - independent_only
    assert len(CANONICAL_HANDLERS) == 58


# Removed in 0.5.0 (iss-00440, R-440-02): commands and arguments that canonical mode only refused.
REMOVED_COMMANDS = (
    ("workspace", "migrate", "--to-schema", "3", "--to-writer-protocol", "specdock.worktree-writer/v1"),
    ("workbench", "copy", "--scope", "iss-00003", "--to-worktree", "/tmp/x"),
)
REMOVED_ARGUMENTS = (
    ("workspace", "validate", "--ci"),
    ("workspace", "sync", "--source", "local"),
    ("dependency", "check", "iss-00003", "--source", "local"),
    *(
        ("scope", "create", kind, "--backend", "github", *parent, "--title", "x", "--slug", "x")
        for kind, parent in (("initiative", ()), ("epic", ("--parent", "init-00001")), ("issue", ("--parent", "e")))
    ),
    *(
        ("scope", "import", "github", kind, "7", *parent, "--title", "x", "--slug", "x")
        for kind, parent in (("initiative", ()), ("epic", ("--parent", "init-00001")), ("issue", ("--parent", "e")))
    ),
)


@pytest.mark.parametrize("argv", [*REMOVED_COMMANDS, *REMOVED_ARGUMENTS])
def test_removed_commands_and_arguments_are_usage_errors(
    argv: tuple[str, ...], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([*argv, "--json"]) == 2
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["error"]["code"] == "USAGE_ERROR" and envelope["effects"] == []


def test_removed_commands_are_absent_from_help_and_completion(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (["help"], ["completion", "bash"], ["completion", "zsh"], ["completion", "fish"]):
        assert main(argv) == 0
        text = capsys.readouterr().out
        assert "migrate" not in text and "workbench" not in text, argv


def test_refusal_only_codes_are_gone_from_the_runtime() -> None:
    from pathlib import Path

    import spec_dock.runtime

    root = Path(spec_dock.runtime.__file__).parent
    for code in ("CANONICAL_NOT_APPLICABLE", "CANONICAL_WORKBENCH_SHARED", "BUSINESS_NOT_CONNECTED"):
        offenders = [str(path) for path in root.rglob("*.py") if code in path.read_text(encoding="utf-8")]
        assert offenders == [], code


def test_no_runtime_source_returns_not_implemented() -> None:
    from pathlib import Path

    import spec_dock.runtime

    root = Path(spec_dock.runtime.__file__).parent
    offenders = [str(path) for path in root.rglob("*.py") if "NOT_IMPLEMENTED" in path.read_text(encoding="utf-8")]
    assert offenders == []


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> WriteWorld:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    git(world.main, "remote", "set-url", "origin", str(tmp_path / "remote.git"))
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", _Clock())
    world.scope("initiative", 1, "計画")
    world.scope("epic", 2, "中核", parent=1)
    world.scope("issue", 3, "葉", parent=2)
    world.edit(lambda fake: [fake.add_issue(number, title=f"Plain {number}") for number in (10, 11, 12)])
    return world


def _argv(world: WriteWorld, tmp_path: Path) -> list[tuple[str, list[str]]]:
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("evidence\n", encoding="utf-8")
    other = tmp_path / "wt-every"
    return [
        (
            "scope create initiative",
            [
                "--backend",
                "github",
                "--title",
                "新しい計画",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        (
            "scope create epic",
            [
                "--backend",
                "github",
                "--parent",
                "init-1",
                "--title",
                "新しい束",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        (
            "scope create issue",
            [
                "--backend",
                "github",
                "--parent",
                "epic-2",
                "--title",
                "新しい作業",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        (
            "scope import github initiative",
            [
                "10",
                "--github-repo",
                REPOSITORY,
                "--title",
                "x",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        (
            "scope import github epic",
            [
                "11",
                "--github-repo",
                REPOSITORY,
                "--parent",
                "init-1",
                "--title",
                "x",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        (
            "scope import github issue",
            [
                "12",
                "--github-repo",
                REPOSITORY,
                "--parent",
                "epic-2",
                "--title",
                "x",
                "--yes",
                "--assurance",
                "standard",
                "--assurance-reason",
                "既定の理由",
            ],
        ),
        ("scope list", []),
        ("scope show", ["iss-3"]),
        ("scope check", ["iss-3"]),
        ("scope render", ["iss-3"]),
        ("scope edit", ["iss-3", "--title", "葉を直す", "--yes"]),
        ("scope close", ["iss-12", "--yes"]),
        ("scope reopen", ["iss-12", "--yes"]),
        ("scope move", ["iss-3", "--parent", "epic-11", "--yes"]),
        ("dependency add", ["--from", "iss-3", "--to", "iss-12", "--yes"]),
        ("dependency list", ["iss-3"]),
        ("dependency check", ["iss-3"]),
        ("dependency remove", ["--from", "iss-3", "--to", "iss-12", "--yes"]),
        ("artifact create", ["--scope", "iss-3", "--type", "blank", "--title", "Memo", "--yes"]),
        ("artifact import file", [str(evidence), "--scope", "iss-3", "--yes"]),
        ("artifact list", ["--scope", "iss-3"]),
        ("artifact show", ["art-00000000t000000z-missing", "--scope", "iss-3"]),
        ("active show", []),
        ("active set", ["iss-3"]),
        ("branch show", ["iss-3"]),
        ("branch create", ["iss-12", "--base", "main"]),
        ("branch switch", ["iss-12"]),
        ("branch switch", ["iss-3", "--name", "main"]),
        ("work start", ["iss-3", "--base", "main", "--yes"]),
        ("active clear", ["--all", "--yes"]),
        ("worktree create", ["wt-every", "--base", "main", "--root", str(tmp_path), "--yes"]),
        ("worktree list", []),
        ("worktree show", [str(other)]),
        ("worktree bootstrap", [str(other), "--dry-run"]),
        ("worktree remove", [str(other), "--dry-run"]),
        ("workspace sync", []),
        ("workspace validate", []),
        ("workspace doctor", []),
        ("canonical link", []),
        ("canonical status", []),
        ("canonical check", []),
        ("canonical sync", []),
        ("canonical accept", ["00000-00999/iss-00003/design.md"]),
        ("canonical restore", ["00000-00999/iss-00003/design.md"]),
        ("canonical resume", []),
        ("canonical remove", []),
        ("dashboard summary", []),
        ("dashboard serve", ["--port", "70000"]),  # a usage error: the run must not wait for Ctrl-C
        ("dashboard hide", []),
        ("dashboard show", []),
        ("dashboard list", []),
        ("dashboard service install", []),  # the suite's fake platform has no service manager: it stops, writes nothing
        ("dashboard service status", []),
        ("dashboard service uninstall", []),
        ("todo add", ["--title", "人のタスク"]),
        ("todo list", []),
        ("todo show", ["t-0000"]),  # TODO_NOT_FOUND: the random ID of the add is not known here
        ("todo update", ["t-0000", "--title", "x"]),
        ("todo done", ["t-0000"]),
        ("todo snooze", ["t-0000", "--until", "1d"]),
        ("todo cancel", ["t-0000", "--reason", "x"]),
        ("todo reopen", ["t-0000"]),
        ("todo check", []),
        ("todo settings", []),
        ("installation show", []),
        ("installation init", [str(tmp_path / "fresh-install"), "--dry-run"]),
        ("installation update", ["--dry-run"]),
        ("installation uninstall", ["--dry-run"]),
        ("scope delete", ["iss-12", "--backup-dir", str(tmp_path / "delete-backup"), "--dry-run"]),
        ("work finish", ["iss-3", "--yes"]),
    ]


def test_every_leaf_runs_on_a_linked_schema4_clone(
    world: WriteWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "fresh-install").mkdir()
    runs = _argv(world, tmp_path)
    assert {path for path, _ in runs} | {"help", "completion"} == set(LEAF_PATHS)
    problems: list[str] = []
    for path, arguments in runs:
        capsys.readouterr()
        code = main(["--project", str(world.main), *path.split(), *arguments, "--json"])
        output = capsys.readouterr()
        try:
            envelope = json.loads(output.out)
        except json.JSONDecodeError:
            problems.append(f"{path}: exit {code}, no JSON envelope: {output.out[-300:]} {output.err[-300:]}")
            continue
        error = envelope.get("error") or {}
        if code == 1 or envelope.get("command") != path:
            problems.append(f"{path}: exit {code}, {envelope.get('command')!r}, {error}")
        elif error.get("code") in (
            "CANONICAL_NOT_IMPLEMENTED",
            "CANONICAL_NOT_APPLICABLE",
            "CANONICAL_WORKBENCH_SHARED",
        ):
            problems.append(f"{path}: refusal-only {error['code']}")
        elif _canonical_code(error.get("code")) and not envelope.get("recovery"):
            problems.append(f"{path}: {envelope['status']} without recovery: {error}")
    for path, arguments in (("help", ["canonical", "status"]), ("completion", ["bash"])):
        capsys.readouterr()
        assert main([*path.split(), *arguments]) == 0, path
    assert problems == [], "\n".join(problems)
