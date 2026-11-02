"""Legacy schema-3 selection fixture kept for other modules (iss-00440).

Its tests moved to tests/cli_runtime/test_issue440_g1_active.py and test_issue440_g1_cli_parsing.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.work_target_store import WorkTargetStore

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def select_fixture(root: Path, *, scope_id: str = "init-00001", number: int = 1) -> Path:
    context = resolve_context(str(root), root)
    with WorkTargetStore(root) as store:
        handle = store.publish(
            WorkTarget(
                "specdock.work-target/v1",
                scope_id,
                f"gh:example/repo#{number}",
                "main",
                "2026-09-30T00:00:00Z",
                context.clone_identity,
                context.worktree_identity,
            )
        )
        return store.path / handle.basename
