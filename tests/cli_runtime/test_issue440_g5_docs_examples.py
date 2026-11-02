"""The documented command examples run in canonical mode (iss-00440).

Replaces the executed-example tests of tests/integration/test_cli_docs_vnext.py, which ran them on the legacy
(schema-3) publication fixture: README creation examples, the documented Scope selector boundary, and the
root import example of docs/github-issue-integration.md.
"""

from __future__ import annotations

import json
from pathlib import Path
import shlex
import sys

import pytest

from spec_dock.cli import main
from tests.support.canonical_scopes import CanonicalWorld
from tests.support.canonical_writes import WriteWorld

ROOT = Path(__file__).resolve().parents[2]


def _commands(document: str, prefix: str) -> list[list[str]]:
    lines = (ROOT / document).read_text(encoding="utf-8").splitlines()
    return [shlex.split(line)[1:] for line in lines if line.startswith(f"spec-dock {prefix} ")]


def _files(root: Path) -> dict[str, object]:
    """Every path under the checkout (the catalog included) except Git's own data, with its bytes or link."""
    observed: dict[str, object] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            observed[relative.as_posix()] = path.readlink().as_posix()
        else:
            observed[relative.as_posix()] = path.read_bytes() if path.is_file() else None
    return observed


def test_readme_creation_examples_execute_noninteractively_and_keep_confirmation_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    commands = _commands("README.md", "scope create")
    assert [command[2] for command in commands] == ["initiative", "epic", "issue"]
    parent = None
    for index, command in enumerate(commands):
        if parent is not None:
            command[command.index("--parent") + 1] = parent
        # No flags are supplied by the test to rescue an incomplete published example.
        assert "--json" in command and "--yes" in command
        before = _files(world.main)
        writes = world.writes()
        assert main(["--project", str(world.main), *(word for word in command if word != "--yes")]) == 3
        rejected = json.loads(capsys.readouterr().out)
        assert rejected["error"]["code"] == "CONFIRMATION_REQUIRED" and rejected["effects"] == []
        assert _files(world.main) == before
        assert world.writes() == writes
        assert main(["--project", str(world.main), *command]) == 0
        result = json.loads(capsys.readouterr().out)
        scope = result["data"]["result"]["scope"]
        assert scope["parent_id"] == parent
        # The fake GitHub numbers new Issues from 1 (the legacy stub started at 501).
        assert scope["github_ref"] == f"gh:example/repo#{1 + index}"
        assert scope["id"] == f"{('init', 'epic', 'iss')[index]}-{1 + index:05d}"
        parent = scope["id"]
    created = [
        endpoint
        for method, endpoint, _ in world.writes()
        if (method, endpoint) == ("POST", "repos/example/repo/issues")
    ]
    assert len(created) == 3


@pytest.mark.parametrize(
    "selector", ["init-00001", "gh:example/repo#1", "@current", "1", "https://github.com/example/repo/issues/1"]
)
def test_documented_scope_selector_boundary_is_readonly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], selector: str
) -> None:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    world.select("init-00001", 1)
    before = _files(world.main)
    valid = selector in {"init-00001", "gh:example/repo#1", "@current"}
    code, result = world.run("scope", "show", selector)
    assert code == (0 if valid else 3)
    assert result["effects"] == []
    if valid:
        assert result["data"]["result"]["scope"]["id"] == "init-00001"
    assert _files(world.main) == before
    # Canonical reads fetch the structure snapshot from GitHub (the legacy fixture made no call); nothing is written.
    assert world.fake().writes() == []


def test_root_import_example_includes_repository_and_executes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Platform")
    world.scope("epic", 124, "Authentication", parent=1, directory=False)
    guide = (ROOT / "docs/github-issue-integration.md").read_text(encoding="utf-8")
    (command,) = _commands("docs/github-issue-integration.md", "scope import")
    assert "--github-repo" in command
    command[command.index("--github-repo") + 1] = "example/repo"
    command[command.index("--parent") + 1] = "init-00001"
    code, result = world.write(*command)
    assert code == 0, result
    assert result["data"]["result"]["scope"]["id"] == "epic-00124"
    # The Issue already carries its kind label and parent, so canonical import writes nothing to GitHub.
    assert world.writes() == []
    assert "固定外部エンジン" not in guide
