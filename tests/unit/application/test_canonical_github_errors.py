"""GitHub failures in canonical commands: the result builder and the dispatch catch (iss-00431, from iss-00428)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.application.canonical_errors import github_error_result
from spec_dock.runtime.commands import canonical_dispatch
from spec_dock.runtime.infra.github_structure import GithubStructureError
from spec_dock.runtime.presentation.envelope import RecoveryInstructions
from tests.support.canonical_repo import bare_remote, clone, isolate_user_state

if TYPE_CHECKING:
    from pathlib import Path


def test_a_certain_failure_is_failed_with_exit_five_and_the_network_next_step() -> None:
    result = github_error_result(
        "scope show", GithubStructureError("GITHUB_UNAVAILABLE", "offline", endpoint="graphql")
    )
    assert (result.status, result.exit_code, result.effects) == ("failed", 5, ())
    assert result.error is not None and result.error.code == "GITHUB_UNAVAILABLE"
    assert isinstance(result.recovery, RecoveryInstructions)
    assert "gh auth status" in result.recovery.instructions[0]


def test_an_uncertain_write_is_partial_with_exit_six_and_an_unknown_effect() -> None:
    error = GithubStructureError("GITHUB_EFFECT_UNKNOWN", "lost", uncertain=True, endpoint="repos/o/r/issues/3")
    result = github_error_result("scope close", error)
    assert (result.status, result.exit_code) == ("partial", 6)
    assert [(effect.kind, effect.status, effect.target) for effect in result.effects] == [
        ("github.write", "unknown", "repos/o/r/issues/3")
    ]


def test_a_rate_limit_names_the_retry_time() -> None:
    error = GithubStructureError("GITHUB_RATE_LIMITED", "limit", retry_at="2026-10-26T01:00:00Z", status=429)
    result = github_error_result("scope list", error)
    assert result.exit_code == 5 and result.error is not None
    assert result.error.details["retry_at"] == "2026-10-26T01:00:00Z"
    assert isinstance(result.recovery, RecoveryInstructions)
    assert result.recovery.instructions == ("Run the same command after 2026-10-26T01:00:00Z.",)


@pytest.mark.parametrize(
    ("error", "status", "exit_code"),
    [
        (GithubStructureError("GITHUB_UNAVAILABLE", "offline"), "failed", 5),
        (GithubStructureError("GITHUB_EFFECT_UNKNOWN", "lost", uncertain=True, endpoint="x"), "partial", 6),
        (GithubStructureError("GITHUB_RATE_LIMITED", "limit", retry_at="2026-10-26T01:00:00Z"), "failed", 5),
    ],
)
def test_dispatch_renders_an_uncaught_github_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: GithubStructureError,
    status: str,
    exit_code: int,
) -> None:
    isolate_user_state(monkeypatch, tmp_path)
    checkout = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")

    def raising(namespace: object, context: object) -> object:
        raise error

    monkeypatch.setitem(canonical_dispatch.CANONICAL_HANDLERS, "scope list", raising)
    code = main(["--project", str(checkout), "scope", "list", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["status"], payload["exit_code"]) == (exit_code, status, exit_code)
    assert payload["error"]["code"] == error.code
    if error.retry_at is not None:
        assert payload["error"]["details"]["retry_at"] == error.retry_at
        assert error.retry_at in payload["recovery"]["instructions"][0]
