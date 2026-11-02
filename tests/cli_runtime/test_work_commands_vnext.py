"""Legacy schema-3 three-kind fixture kept for other modules (iss-00440).

Its tests moved to tests/cli_runtime/test_issue440_g1_work_finish.py.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from tests.cli_runtime.test_issue413_contract import add_scope, make_workspace

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def three_kind_workspace(root: Path) -> Path:
    make_workspace(root)
    initiative = root / "spec-dock/initiatives/init-00001-fixture"
    epic = add_scope(root, "epic-00002", "epic", "init-00001", initiative)
    add_scope(root, "iss-00003", "issue", "epic-00002", epic)
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
    return root
