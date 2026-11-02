"""Public Scope close/reopen preserve existing data and direct selection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def existing_local_workspace(root: Path) -> tuple[Path, Path]:
    from tests.cli_runtime.test_issue413_work_start import committed_workspace

    committed_workspace(root)
    path = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(path.read_bytes())
    payload.update(
        backend="local",
        github=None,
        lifecycle={"state": "open", "revision": 0, "updated_at": "2026-09-30T00:00:00Z"},
    )
    path.write_text(json.dumps(payload))
    return root, path
