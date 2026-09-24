"""Thin read-only adapter for installation inventory."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.installation_vnext import InstallationView, show_installation
from spec_dock_runtime.presentation.envelope import OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.commands.work_vnext import WorkContext


def run_installation_show(
    ns: argparse.Namespace, context: WorkContext, *, engine_version: str, invocation_cwd: Path
) -> OperationResult[InstallationView]:
    target = Path(ns.target).expanduser() if ns.target else None
    if target is not None and not target.is_absolute():
        target = invocation_cwd / target
    view = show_installation(
        repo_root=context.repo_root,
        common_dir=context.common_dir,
        engine_version=engine_version,
        engine_digest=context.engine_digest,
        target=target,
    )
    return OperationResult(command=ns.command_path, status="succeeded", data=view, exit_code=0)
