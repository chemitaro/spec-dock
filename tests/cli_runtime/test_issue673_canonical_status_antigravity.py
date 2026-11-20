"""Antigravity settings as reported by canonical status and link (iss-00673)."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra import runtime_environment
from tests.support.canonical_repo import add_worktree, bare_remote, clone, environment, isolate_user_state

if TYPE_CHECKING:
    from pathlib import Path

SETTINGS_FILE = "~/.gemini/antigravity-cli/settings.json"
needs_permissions = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")


def run(capsys: pytest.CaptureFixture[str], checkout: Path, command: str = "status") -> dict[str, Any]:
    code = main(["--project", str(checkout), "canonical", command, "--json"])
    result = json.loads(capsys.readouterr().out)
    assert code == 0, result
    return result


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    home = isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda: environment())
    return home


@pytest.fixture
def settings(isolated: Path) -> Path:
    path = isolated / ".gemini/antigravity-cli/settings.json"
    path.parent.mkdir(parents=True)
    return path


@pytest.fixture
def linked_clone(capsys: pytest.CaptureFixture[str], isolated: Path, tmp_path: Path) -> tuple[Path, Path]:
    checkout = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
    run(capsys, checkout, "link")
    linked = add_worktree(checkout, tmp_path / "linked", "feature")
    run(capsys, linked, "link")
    return checkout, linked


def test_missing_settings_show_the_line_and_give_it_priority(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout, linked = linked_clone
    catalog = checkout / "spec-dock/.canonical"
    line = f'{{ "permissions": {{ "allow": ["read_file({catalog})", "write_file({catalog})"] }} }}'
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "")
    result = run(capsys, linked)
    tools = result["data"]["tools"]
    assert tools["antigravity"] == {
        "session": True,
        "needed": True,
        "configured": False,
        "sources": [],
        "file": SETTINGS_FILE,
        "line": line,
    }
    assert tools["status"] == "problem" and tools["next_step"] == line
    claude, antigravity = result["warnings"]
    assert claude["details"]["tool"] == "claude_code"
    assert antigravity == {
        "code": "CANONICAL_TOOL_SETTING_MISSING",
        "message": (
            "Antigravity reads and writes the specs of this linked worktree only with an allow rule; "
            f"add this to {SETTINGS_FILE}: {line}"
        ),
        "details": {"item": "tools", "tool": "antigravity", "file": SETTINGS_FILE, "line": line, "next_step": line},
    }
    assert run(capsys, linked, "link")["warnings"] == result["warnings"]


@pytest.mark.parametrize("use_parent", [False, True])
def test_allow_rules_cover_the_catalog_without_rewriting_settings(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
    use_parent: bool,
) -> None:
    checkout, linked = linked_clone
    catalog = checkout / "spec-dock/.canonical"
    target = checkout if use_parent else catalog
    content = json.dumps({"permissions": {"allow": [f"read_file({target})", f"write_file({target})"]}}, indent=2)
    settings.write_text(content, encoding="utf-8")
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    result = run(capsys, linked)
    tools = result["data"]["tools"]
    assert tools["antigravity"]["configured"] is True
    assert tools["antigravity"]["sources"] == [str(settings)]
    assert tools["antigravity"]["line"] is None
    (claude,) = result["warnings"]
    assert claude["details"]["tool"] == "claude_code"
    assert tools["next_step"] == claude["details"]["next_step"]
    assert settings.read_bytes() == content.encode("utf-8")


@pytest.mark.parametrize(("policy", "action"), [("deny", "read_file"), ("ask", "write_file")])
def test_covering_deny_or_ask_requires_checking_the_rules(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
    policy: str,
    action: str,
) -> None:
    checkout, linked = linked_clone
    catalog = checkout / "spec-dock/.canonical"
    permissions = {
        "allow": [f"read_file({catalog})", f"write_file({catalog})"],
        policy: [f"{action}({checkout})"],
    }
    settings.write_text(json.dumps({"permissions": permissions}), encoding="utf-8")
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    result = run(capsys, linked)
    tools = result["data"]["tools"]
    assert tools["antigravity"]["configured"] is None
    assert tools["antigravity"]["line"] is None
    step = (
        f"Check that {SETTINGS_FILE} allows read_file({catalog}) and write_file({catalog}) in permissions.allow, "
        "and that no permissions.deny or permissions.ask rule covers the catalog."
    )
    assert tools["next_step"] == step
    assert result["warnings"][-1] == {
        "code": "CANONICAL_TOOL_SETTING_UNKNOWN",
        "message": f"Could not judge whether Antigravity allows the catalog. {step}",
        "details": {"item": "tools", "tool": "antigravity", "sources": [str(settings)], "next_step": step},
    }


@pytest.mark.parametrize("config", ["read-only", "unverified-rules", "broad-setting", "invalid-path"])
def test_settings_without_both_supported_allow_rules_are_missing(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
    config: str,
) -> None:
    checkout, linked = linked_clone
    catalog = checkout / "spec-dock/.canonical"
    payloads = {
        "read-only": {"permissions": {"allow": [f"read_file({catalog})"]}},
        "unverified-rules": {"permissions": {"allow": ["read_file(~/)", "read_file(spec-dock)", "write_file(/*)"]}},
        "broad-setting": {"allowNonWorkspaceAccess": True},
        "invalid-path": {"permissions": {"allow": [f"read_file({catalog})", "write_file(/\ud800)"]}},
    }
    settings.write_text(json.dumps(payloads[config]), encoding="utf-8")
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    result = run(capsys, linked)
    antigravity = result["data"]["tools"]["antigravity"]
    assert antigravity["configured"] is False and antigravity["sources"] == [str(settings)]
    warning = result["warnings"][-1]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_MISSING" and warning["details"]["tool"] == "antigravity"
    assert warning["details"]["line"] == antigravity["line"]


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"{ not JSON", id="invalid-json"),
        pytest.param(b'{"permissions": []}', id="invalid-permissions"),
        pytest.param(b'{"permissions": {"allow": "all"}}', id="invalid-allow"),
        pytest.param(b'{"permissions": {"ask": null}}', id="invalid-ask"),
        pytest.param(b'{"permissions": {"deny": [42]}}', id="invalid-deny"),
        pytest.param(b"\xff", id="invalid-utf8"),
    ],
)
def test_invalid_settings_are_unknown(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
    content: bytes,
) -> None:
    _, linked = linked_clone
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    settings.write_bytes(content)
    result = run(capsys, linked)
    assert result["data"]["tools"]["antigravity"]["configured"] is None
    warning = result["warnings"][-1]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_UNKNOWN"
    assert warning["details"]["tool"] == "antigravity" and warning["details"]["sources"] == [str(settings)]
    assert settings.read_bytes() == content


@needs_permissions
def test_an_unreadable_settings_file_is_unknown(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, linked = linked_clone
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    settings.write_text("{}", encoding="utf-8")
    settings.chmod(0o000)
    try:
        result = run(capsys, linked)
    finally:
        settings.chmod(0o600)
    assert result["data"]["tools"]["antigravity"]["configured"] is None
    warning = result["warnings"][-1]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_UNKNOWN"
    assert warning["details"]["tool"] == "antigravity" and warning["details"]["sources"] == [str(settings)]


def test_an_unknown_home_shows_the_default_settings_name(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, linked = linked_clone
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    # Inject the missing runtime fact while keeping the temporary HOME for Git subprocesses.
    values = dict(os.environ)
    values.pop("HOME")
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda: environment(environ=values))
    result = run(capsys, linked)
    assert result["data"]["tools"]["antigravity"] == {
        "session": True,
        "needed": True,
        "configured": None,
        "sources": [SETTINGS_FILE],
        "file": SETTINGS_FILE,
        "line": None,
    }
    warning = result["warnings"][-1]
    assert warning["code"] == "CANONICAL_TOOL_SETTING_UNKNOWN"
    assert warning["details"]["tool"] == "antigravity" and warning["details"]["sources"] == [SETTINGS_FILE]


def test_outside_antigravity_missing_settings_do_not_affect_claude_warning(
    capsys: pytest.CaptureFixture[str], linked_clone: tuple[Path, Path]
) -> None:
    _, linked = linked_clone
    result = run(capsys, linked)
    tools = result["data"]["tools"]
    assert tools["antigravity"]["session"] is False and tools["antigravity"]["configured"] is False
    assert tools["antigravity"]["line"] is not None
    (warning,) = result["warnings"]
    assert warning["details"]["tool"] == "claude_code"
    assert tools["status"] == "problem" and tools["next_step"] == tools["claude_code"]["line"]
    assert tools["next_step"] == warning["details"]["next_step"]


def test_main_checkout_needs_no_settings(
    capsys: pytest.CaptureFixture[str],
    linked_clone: tuple[Path, Path],
    settings: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkout, _ = linked_clone
    settings.write_bytes(b"broken")
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "1")
    result = run(capsys, checkout)
    tools = result["data"]["tools"]
    assert tools["antigravity"] == {
        "session": True,
        "needed": False,
        "configured": None,
        "sources": [],
        "file": SETTINGS_FILE,
        "line": None,
    }
    assert tools["status"] == "ok" and tools["next_step"] is None and result["warnings"] == []
