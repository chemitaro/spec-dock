"""Dependency operations use current metadata and explicit live observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def dependency_workspace(tmp_path: Path) -> tuple[Path, Path, Path]:
    from tests.cli_runtime.test_issue413_contract import add_scope
    from tests.cli_runtime.test_issue413_work_start import committed_workspace

    root = committed_workspace(tmp_path / "consumer")
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    source = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    child = add_scope(root, "iss-00003", "issue", "epic-00002", source)
    add_scope(root, "epic-00004", "epic", "init-00001", initiative)
    return root, source / ".meta.json", child / ".meta.json"
