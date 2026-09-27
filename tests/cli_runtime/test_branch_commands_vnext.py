"""Branch leaves use exact Scope bindings and preserve dry-run boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import cast

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.options import parse_vnext  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.commands.branch_vnext import run_branch_command  # noqa: E402
from spec_dock_runtime.commands.work_vnext import WorkContext  # noqa: E402
from tests.cli_runtime.test_branch_vnext import _committed_repo  # noqa: E402


def test_branch_adapter_create_show_switch_and_dry_run(tmp_path: Path) -> None:
    common, initiative = _committed_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    context = WorkContext(repo, cast("Path", common["common_dir"]), "main", "engine-a", 1)
    planned = run_branch_command(
        parse_vnext(["branch", "create", initiative.id, "--base", "HEAD", "--dry-run"]), context
    )
    assert planned.status == "planned" and planned.operation_id is None
    routed_plan = run_vnext(
        ["branch", "create", initiative.id, "--base", "HEAD", "--dry-run", "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert routed_plan.exit_code == 0 and json.loads(routed_plan.stdout)["status"] == "planned"
    assert parse_vnext(["branch", "create", initiative.id, "--resume", "a" * 32]).base is None
    assert (
        subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{planned.data.branch}"],
            cwd=repo,
            check=False,
        ).returncode
        == 1
    )
    created = run_branch_command(parse_vnext(["branch", "create", initiative.id, "--base", "HEAD"]), context)
    assert created.status == "succeeded"
    assert created.operation_id is not None
    shown = run_branch_command(parse_vnext(["branch", "show", initiative.id]), context)
    assert shown.data.branch == created.data.branch
    routed = run_vnext(
        ["branch", "show", initiative.id, "--json"],
        invocation_cwd=repo,
        engine_digest="engine-a",
        engine_version="0.2.4",
    )
    assert routed.exit_code == 0
    assert json.loads(routed.stdout)["data"]["branch"] == created.data.branch
    before = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    preview = run_branch_command(parse_vnext(["branch", "switch", initiative.id, "--dry-run"]), context)
    assert preview.status == "planned"
    assert (
        subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
        ).stdout.strip()
        == before
    )
    switched = run_branch_command(parse_vnext(["branch", "switch", initiative.id]), context)
    assert switched.status == "succeeded"
    assert switched.data.branch == shown.data.branch
