"""REST Issue lifecycle gateway, with no live network dependency."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError  # noqa: E402


def _reply(status: int, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        ["gh"],
        0 if status < 400 else 1,
        f"HTTP/2.0 {status} Test\r\ncontent-type: application/json\r\n\r\n{json.dumps(payload)}",
        "",
    )


def _issue(*, state: str = "open", reason: str | None = None, number: int = 8) -> dict[str, object]:
    return {
        "number": number,
        "title": "Plan",
        "state": state,
        "state_reason": reason,
        "updated_at": "2026-09-24T00:00:00Z",
        "html_url": f"https://github.com/example/product/issues/{number}",
        "repository_url": "https://api.github.com/repos/example/product",
    }


class FakeRun:
    def __init__(self, *outcomes: subprocess.CompletedProcess[str] | BaseException) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((argv, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def test_get_distinguishes_completed_not_planned_duplicate_and_missing_reason(tmp_path: Path) -> None:
    runner = FakeRun(
        _reply(200, _issue(state="closed", reason="completed")),
        _reply(200, _issue(state="closed", reason="not_planned")),
        _reply(200, _issue(state="closed", reason="duplicate")),
        _reply(200, _issue(state="closed", reason=None)),
    )
    gateway = GithubIssueGateway(runner=runner)
    assert [gateway.get(tmp_path, "example/product", 8).state for _ in range(4)] == [
        "completed",
        "not-planned",
        "unknown",
        "unknown",
    ]
    assert all("repos/example/product/issues/8" in call[0] for call in runner.calls)
    assert all("--include" in call[0] for call in runner.calls)


def test_get_rejects_pull_requests_foreign_repository_and_number(tmp_path: Path) -> None:
    pr = _issue()
    pr["pull_request"] = {"url": "https://api.github.com/repos/example/product/pulls/8"}
    foreign = _issue()
    foreign["repository_url"] = "https://api.github.com/repos/other/product"
    runner = FakeRun(_reply(200, pr), _reply(200, foreign), _reply(200, _issue(number=9)))
    gateway = GithubIssueGateway(runner=runner)
    for _ in range(3):
        with pytest.raises(RemoteIssueError) as caught:
            gateway.get(tmp_path, "example/product", 8)
        assert caught.value.exit_code == 5


@pytest.mark.parametrize("status", [401, 403, 404])
def test_read_permission_or_missing_error_is_code_five(tmp_path: Path, status: int) -> None:
    gateway = GithubIssueGateway(runner=FakeRun(_reply(status, {"message": "credential token value"})))
    with pytest.raises(RemoteIssueError) as caught:
        gateway.get(tmp_path, "example/product", 8)
    assert caught.value.exit_code == 5
    assert "token value" not in str(caught.value)


def test_close_sends_only_state_and_reason_then_observes(tmp_path: Path) -> None:
    runner = FakeRun(
        _reply(200, _issue()),
        _reply(200, _issue(state="closed", reason="not_planned")),
        _reply(200, _issue(state="closed", reason="not_planned")),
    )
    gateway = GithubIssueGateway(runner=runner)
    result = gateway.set_state(tmp_path, "example/product", 8, state="closed", reason="not_planned")
    assert result.state == "not-planned"
    patch_argv, patch_kwargs = runner.calls[1]
    assert "PATCH" in patch_argv
    assert json.loads(str(patch_kwargs["input"])) == {"state": "closed", "state_reason": "not_planned"}
    assert "Plan" not in str(patch_kwargs["input"])
    assert "GET" in runner.calls[0][0]
    assert "GET" in runner.calls[2][0]


def test_patch_timeout_observes_once_and_never_blindly_retries(tmp_path: Path) -> None:
    runner = FakeRun(
        _reply(200, _issue()),
        subprocess.TimeoutExpired(["gh"], 0.1),
        _reply(200, _issue(state="closed", reason="completed")),
    )
    gateway = GithubIssueGateway(runner=runner)
    assert gateway.set_state(tmp_path, "example/product", 8, state="closed", reason="completed").state == "completed"
    assert len(runner.calls) == 3
    assert sum("PATCH" in args for args, _ in runner.calls) == 1


def test_patch_timeout_with_observation_mismatch_is_unknown_code_six(tmp_path: Path) -> None:
    runner = FakeRun(_reply(200, _issue()), subprocess.TimeoutExpired(["gh"], 0.1), _reply(200, _issue()))
    with pytest.raises(RemoteIssueError) as caught:
        GithubIssueGateway(runner=runner).set_state(tmp_path, "example/product", 8, state="closed", reason="completed")
    assert caught.value.exit_code == 6
    assert caught.value.uncertain


def test_preflight_rejects_pr_without_patching(tmp_path: Path) -> None:
    pr = _issue()
    pr["pull_request"] = {"url": "https://api.github.com/repos/example/product/pulls/8"}
    runner = FakeRun(_reply(200, pr))
    with pytest.raises(RemoteIssueError, match="GITHUB_PULL_REQUEST_REJECTED"):
        GithubIssueGateway(runner=runner).set_state(tmp_path, "example/product", 8, state="closed", reason="completed")
    assert len(runner.calls) == 1


def test_same_reason_is_noop_and_reason_change_requires_reopen(tmp_path: Path) -> None:
    same = FakeRun(_reply(200, _issue(state="closed", reason="completed")))
    assert (
        GithubIssueGateway(runner=same)
        .set_state(tmp_path, "example/product", 8, state="closed", reason="completed")
        .state
        == "completed"
    )
    assert len(same.calls) == 1
    change = FakeRun(_reply(200, _issue(state="closed", reason="not_planned")))
    with pytest.raises(RemoteIssueError, match="GITHUB_REASON_CHANGE_REQUIRES_REOPEN"):
        GithubIssueGateway(runner=change).set_state(tmp_path, "example/product", 8, state="closed", reason="completed")
    assert len(change.calls) == 1


def test_reopen_sends_only_open_state_and_reopened_reason(tmp_path: Path) -> None:
    runner = FakeRun(
        _reply(200, _issue(state="closed", reason="completed")),
        _reply(200, _issue()),
        _reply(200, _issue()),
    )
    assert (
        GithubIssueGateway(runner=runner).set_state(tmp_path, "example/product", 8, state="open", reason=None).state
        == "open"
    )
    assert json.loads(str(runner.calls[1][1]["input"])) == {"state": "open", "state_reason": "reopened"}


def test_create_has_fixed_repository_minimal_payload_and_no_timeout_retry(tmp_path: Path) -> None:
    runner = FakeRun(_reply(201, _issue(number=21)))
    created = GithubIssueGateway(runner=runner).create(tmp_path, "example/product", title="Plan", body="body")
    assert created.number == 21
    argv, kwargs = runner.calls[0]
    assert "POST" in argv
    assert "repos/example/product/issues" in argv
    assert json.loads(str(kwargs["input"])) == {"title": "Plan", "body": "body"}
    timed_out = FakeRun(subprocess.TimeoutExpired(["gh"], 0.1))
    with pytest.raises(RemoteIssueError) as caught:
        GithubIssueGateway(runner=timed_out).create(tmp_path, "example/product", title="Plan", body="body")
    assert caught.value.exit_code == 6
    assert len(timed_out.calls) == 1


def test_create_success_response_without_identity_is_unknown_effect(tmp_path: Path) -> None:
    payload = _issue(number=21)
    payload["repository_url"] = "https://api.github.com/repos/other/product"
    with pytest.raises(RemoteIssueError) as caught:
        GithubIssueGateway(runner=FakeRun(_reply(201, payload))).create(
            tmp_path, "example/product", title="Plan", body="body"
        )
    assert caught.value.exit_code == 6
