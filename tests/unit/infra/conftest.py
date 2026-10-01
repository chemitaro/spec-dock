"""Fresh static consumers verify distribution separately from dogfood cutover."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.git_process import run_git


@pytest.fixture(scope="session")
def installed_static_consumer(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("installed-static-consumer").resolve()
    run_git(root, "init", "-q", "--initial-branch=main", mutation=True)
    output = io.StringIO()
    with redirect_stdout(output):
        code = main(["installation", "init", str(root), "--yes", "--json"])
    result = json.loads(output.getvalue())
    assert code == 0 and result["status"] == "succeeded", result
    assert result["data"]["kind"] == "installation"
    assert not (root / "spec-dock/scripts/spec_dock_runtime").exists()
    return root
