"""GitHub Scope create records the remote effect before local publication."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.github_create_effect import create_github_issue_effect  # noqa: E402
from spec_dock_runtime.application.operation_executor import prepare_operation  # noqa: E402
from spec_dock_runtime.infra.contracts import GithubIssueRecord  # noqa: E402
from spec_dock_runtime.infra.github_lifecycle import RemoteIssueError  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402


class FakeGateway:
    def __init__(self, result: GithubIssueRecord | Exception) -> None:
        self.result = result
        self.calls = 0

    def create(self, repo_root: Path, repository: str, *, title: str, body: str) -> GithubIssueRecord:
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        assert repository == "example/repo"
        assert title == "Plan"
        assert body == "Created by SpecDock."
        return self.result


def _prepared(store: JournalStore):
    operation = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/repo", "title": "Plan"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=1,
        effect_plan=("github-create", "scaffold"),
    )
    store.create(operation)
    return operation


def _issue() -> GithubIssueRecord:
    return GithubIssueRecord(
        47,
        "example/repo",
        "Plan",
        "open",
        "open",
        None,
        "2026-09-24T00:00:00Z",
        "https://github.com/example/repo/issues/47",
    )


def test_remote_receipt_is_durable_before_local_scaffold_and_cannot_be_replayed(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    operation = _prepared(store)
    gateway = FakeGateway(_issue())
    advanced, created = create_github_issue_effect(
        operation=operation,
        journal=store,
        gateway=gateway,
        repo_root=tmp_path,
        repository="example/repo",
        title="Plan",
        body="Created by SpecDock.",
    )
    assert created.number == 47
    assert advanced.effects[0].remote_ref == "gh:example/repo#47"
    assert store.load(operation.operation_id) == advanced
    assert advanced.terminal_status == "pending"
    with pytest.raises(ValueError, match="already sent"):
        create_github_issue_effect(
            operation=advanced,
            journal=store,
            gateway=gateway,
            repo_root=tmp_path,
            repository="example/repo",
            title="Plan",
            body="Created by SpecDock.",
        )
    assert gateway.calls == 1


@pytest.mark.parametrize("uncertain", [False, True])
def test_remote_failure_records_confirmed_or_unknown_outcome(tmp_path: Path, uncertain: bool) -> None:
    store = JournalStore(tmp_path)
    operation = _prepared(store)
    gateway = FakeGateway(RemoteIssueError("INJECTED", uncertain=uncertain))
    with pytest.raises(RemoteIssueError, match="INJECTED"):
        create_github_issue_effect(
            operation=operation,
            journal=store,
            gateway=gateway,
            repo_root=tmp_path,
            repository="example/repo",
            title="Plan",
            body="Created by SpecDock.",
        )
    saved = store.load(operation.operation_id)
    assert saved.effects[0].status == ("unknown" if uncertain else "failed")
    assert saved.terminal_status == ("pending" if uncertain else "failed")
    assert gateway.calls == 1
