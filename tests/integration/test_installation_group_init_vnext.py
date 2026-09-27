"""Fresh installation coordinates every Git worktree before admitting a writer."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock.installation.source import packaged_bundle  # noqa: E402
from spec_dock.installer import ASSETS  # noqa: E402
from spec_dock.runtime_loader import EnginePin, digest_distribution, read_engine_pin, verify_engine_pin  # noqa: E402
from spec_dock_runtime.application.installation_update_vnext import (  # noqa: E402
    init_installation_group,
    resume_init_installation_group,
    rollback_init_installation_group,
)
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.control_store import load_control  # noqa: E402
from spec_dock_runtime.infra.installation_group_store import pending_installation_groups  # noqa: E402
from tests.integration.test_installation_journal_vnext import _bundle  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _fresh_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("consumer\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-qm", "initial")
    second = tmp_path / "planning"
    _git(repo, "worktree", "add", "-qb", "planning", str(second))
    return repo, second


def test_init_installs_all_worktrees_and_marks_control_ready(tmp_path: Path) -> None:
    repo, second = _fresh_repo(tmp_path)

    result = init_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        engine_digest="e" * 64,
        bundle=_bundle(tmp_path),
    )
    assert result.phase == "committed" and len(result.targets) == 2
    assert load_control(repo / ".git").mode == "ready"
    for target in (repo, second):
        assert (target / "README.md").read_text(encoding="utf-8") == "consumer\n"
        assert (target / "spec-dock/workspace.json").is_file()
        assert (target / "spec-dock/docs/source.txt").is_file()


def test_init_resumes_after_first_worktree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, second = _fresh_repo(tmp_path)
    bundle = _bundle(tmp_path)
    import spec_dock_runtime.application.installation_update_vnext as module

    real_apply = module.apply_installation
    attempts = 0

    def stop_second(*args: object, **kwargs: object):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("stopped")
        return real_apply(*args, **kwargs)

    monkeypatch.setattr(module, "apply_installation", stop_second)
    with pytest.raises(RuntimeError, match="stopped"):
        init_installation_group(repo_root=repo, common_dir=repo / ".git", engine_digest="e" * 64, bundle=bundle)
    (operation_id,) = pending_installation_groups(repo / ".git")
    assert load_control(repo / ".git").mode == "maintenance"
    monkeypatch.setattr(module, "apply_installation", real_apply)
    result = resume_init_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        engine_digest="e" * 64,
        operation_id=operation_id,
        bundle=bundle,
    )
    assert result.phase == "committed" and pending_installation_groups(repo / ".git") == ()
    for target in (repo, second):
        assert (target / "spec-dock/workspace.json").is_file()


def test_init_rollback_restores_fresh_state_and_allows_retry(tmp_path: Path) -> None:
    repo, second = _fresh_repo(tmp_path)
    bundle = _bundle(tmp_path)
    first = init_installation_group(repo_root=repo, common_dir=repo / ".git", engine_digest="e" * 64, bundle=bundle)
    rolled_back = rollback_init_installation_group(
        repo_root=repo,
        common_dir=repo / ".git",
        engine_digest="e" * 64,
        operation_id=first.operation_id,
    )
    assert rolled_back.phase == "rolled-back"
    assert load_control(repo / ".git").mode == "uninitialized"
    for target in (repo, second):
        assert not (target / "spec-dock/workspace.json").exists()
        assert (target / "README.md").read_text(encoding="utf-8") == "consumer\n"
    again = init_installation_group(repo_root=repo, common_dir=repo / ".git", engine_digest="e" * 64, bundle=bundle)
    assert again.phase == "committed"


def test_init_rollback_refuses_later_consumer_changes(tmp_path: Path) -> None:
    repo, _ = _fresh_repo(tmp_path)
    record = init_installation_group(
        repo_root=repo, common_dir=repo / ".git", engine_digest="e" * 64, bundle=_bundle(tmp_path)
    )
    changed = repo / "spec-dock/workspace.json"
    changed.write_text('{"custom":true}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="later changes"):
        rollback_init_installation_group(
            repo_root=repo,
            common_dir=repo / ".git",
            engine_digest="e" * 64,
            operation_id=record.operation_id,
        )
    assert changed.read_text(encoding="utf-8") == '{"custom":true}\n'
    assert load_control(repo / ".git").mode == "ready"


def test_init_accepts_the_executing_packaged_assets(tmp_path: Path) -> None:
    repo, second = _fresh_repo(tmp_path)
    bundle = packaged_bundle(assets_root=ASSETS, destination=tmp_path / "package", version="0.2.4")
    assert bundle.source.commit is None
    result = init_installation_group(repo_root=repo, common_dir=repo / ".git", engine_digest="e" * 64, bundle=bundle)
    assert result.source_commit is None and result.phase == "committed"
    for target in (repo, second):
        assert (target / "spec-dock/workspace.json").is_file()


def test_installation_init_cli_previews_and_requires_confirmation(tmp_path: Path) -> None:
    repo, second = _fresh_repo(tmp_path)
    distribution = tmp_path / "engine"
    executable = distribution / "bin/spec-dock"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    pin = verify_engine_pin(EnginePin(executable, distribution, digest_distribution(distribution)), checkout_root=repo)
    command = ["installation", "init", str(repo), "--json"]
    preview = run_vnext(
        [*command, "--dry-run"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
    )
    assert preview.exit_code == 0 and not (repo / "spec-dock/workspace.json").exists()
    refused = run_vnext(command, invocation_cwd=repo, engine_digest=pin.distribution_digest, engine_version="0.2.4")
    assert refused.exit_code == 3 and "--yes" in refused.stdout
    result = run_vnext(
        [*command, "--yes"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert result.exit_code == 0
    assert read_engine_pin(repo / ".git", checkout_root=repo) == pin
    for target in (repo, second):
        assert (target / "spec-dock/workspace.json").is_file()
    operation_id = json.loads(result.stdout)["operation_id"]
    rollback = run_vnext(
        [*command, "--rollback", operation_id, "--yes"],
        invocation_cwd=repo,
        engine_digest=pin.distribution_digest,
        engine_version="0.2.4",
        engine_pin=pin,
    )
    assert rollback.exit_code == 0
    assert load_control(repo / ".git").mode == "uninitialized"
