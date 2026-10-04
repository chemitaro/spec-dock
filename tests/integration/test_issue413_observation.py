"""Same-clone observations inspect only the recorded target and its parents."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.application.worktree_observation import observe_worktrees
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from tests.cli_runtime.test_issue413_contract import make_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_unrelated_metadata_in_another_worktree_is_not_read(tmp_path: Path) -> None:
    root = make_workspace(tmp_path / "main")
    first = root / "spec-dock/initiatives/init-00001-fixture"
    second = root / "spec-dock/initiatives/init-00002-other"
    shutil.copytree(first, second)
    metadata = json.loads((second / ".meta.json").read_text())
    metadata.update(id="init-00002", slug="other")
    metadata["github"]["issue_number"] = 2
    (second / ".meta.json").write_text(json.dumps(metadata))
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "--detach", str(linked), "HEAD"], check=True, capture_output=True
    )
    context = resolve_context(str(linked), linked)
    record = WorkTarget(
        "specdock.work-target/v1",
        "init-00001",
        "gh:example/repo#1",
        "selected",
        "2026-09-30T00:00:00Z",
        context.clone_identity,
        context.worktree_identity,
    )
    with WorkTargetStore(linked) as store:
        store.publish(record)
    # This unrelated body is deliberately invalid; reading it would poison the row.
    (linked / "spec-dock/initiatives/init-00002-other/.meta.json").write_bytes(b"not JSON")
    rows = observe_worktrees(resolve_context(str(root), root))
    other = next(row for row in rows if row.path == str(linked))
    assert other.selection.status == "selected", other.selection.reason
    assert other.selection.record == record
    assert [view.id for view in other.views] == ["init-00001"]
    assert next(row for row in rows if row.path == str(root)).views == ()
    # Missing current target remains a stale reservation, not an empty row.
    shutil.rmtree(linked / "spec-dock/initiatives/init-00001-fixture")
    stale = next(row for row in observe_worktrees(resolve_context(str(root), root)) if row.path == str(linked))
    assert stale.selection.status == "stale"
    assert stale.selection.record == record
