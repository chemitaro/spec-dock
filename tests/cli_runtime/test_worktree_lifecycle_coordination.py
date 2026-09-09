from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestWorktreeLifecycleCoordination(CliRuntimeHarness):
    def test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        (target / "README.md").write_text("baseline\n", encoding="utf-8")
        (target / "Makefile").write_text("init:\n\t@printf 'initialized\\n' > make-init-marker\n", encoding="utf-8")
        (target / ".gitignore").write_text("make-init-marker\n", encoding="utf-8")
        self._run_git(target, ["add", "-A"])
        self._run_git(target, ["commit", "-m", "baseline"])
        worktree_root = tmp_path / "worktrees"
        worktree_root.mkdir()
        created = self._run_runtime_capture(
            target,
            ["worktree", "create", "demo"],
            env={"SPEC_DOCK_WORKTREE_ROOT": str(worktree_root)},
        )
        assert created.returncode == 0, created.stderr
        assert "worktree bootstrap status=succeeded" in created.stdout
        worktree_path = worktree_root / target.name / f"{target.name}-demo"
        assert (worktree_path / "spec-dock/scripts/spec-dock").is_file()
        assert (worktree_path / "make-init-marker").read_text(encoding="utf-8") == "initialized\n"
        assert self._run_git(worktree_path, ["status", "--porcelain"]).stdout == ""

        listing = self._run_runtime_capture(
            target,
            ["worktree", "list", "--json"],
            env={"SPEC_DOCK_WORKTREE_ROOT": str(worktree_root)},
        )
        assert listing.returncode == 0, listing.stderr
        payload = json.loads(listing.stdout)
        managed = [item for item in payload["worktrees"] if item["path"] == str(worktree_path)]
        assert len(managed) == 1
        worktree_id = managed[0]["id"]

        outside = tmp_path / "outside"
        outside.mkdir()
        replacement = worktree_path
        real_git = shutil.which("git")
        assert real_git is not None
        fake_bin = tmp_path / "fake-bin"
        fake_bin.mkdir()
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            'if [ "$1" = worktree ] && [ "$2" = remove ]; then\n'
            f'  /bin/mv "$3" "$3.original"\n  /bin/ln -s {outside} "$3"\n'
            "  exit 0\n"
            "fi\n"
            f'exec {real_git} "$@"\n',
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
        env = {"SPEC_DOCK_WORKTREE_ROOT": str(worktree_root), "PATH": str(fake_bin)}
        # The fake Git removes the record's directory and replaces it after the
        # helper starts; cleanup must reject the different inode and preserve C.
        removed = self._run_runtime_capture(
            target,
            ["worktree", "remove", worktree_id],
            env=env,
        )
        assert removed.returncode != 0
        assert "post-remove target cleanup failed" in removed.stderr
        assert replacement.is_symlink()
        assert outside.is_dir()

    def test_t11_cross_filesystem_worktree_admission_is_rejected_before_git_mutation(self, monkeypatch) -> None:
        runtime_scripts_dir = (
            Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
        )
        sys.path.insert(0, str(runtime_scripts_dir))
        try:
            from spec_dock_runtime.application import worktree as app_worktree

            monkeypatch.setattr(
                app_worktree.os,
                "fstat",
                lambda fd: SimpleNamespace(st_dev={10: 1, 11: 2}[fd]),
            )
            with pytest.raises(RuntimeError, match="share a filesystem"):
                app_worktree._require_same_filesystem(10, 11)
        finally:
            sys.path.pop(0)

    def test_t11_original_worktree_inode_is_removed_through_bound_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_scripts_dir = (
                Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
            )
            sys.path.insert(0, str(runtime_scripts_dir))
            try:
                from spec_dock_runtime.application import (
                    contracts as app_contracts,
                    ports as app_ports,
                    worktree as app_worktree,
                )
            finally:
                sys.path.pop(0)

            root = Path(tmp)
            repo_root = root / "repo"
            central_root = root / "central"
            worktree_path = central_root / "repo" / "repo-stable"
            repo_root.mkdir()
            worktree_path.mkdir(parents=True)

            class FakeGitGateway:
                def worktree_list(self, repo_root_arg):
                    return [
                        app_contracts.GitWorktreeRecord(path=repo_root, head="abc", branch="main"),
                        app_contracts.GitWorktreeRecord(path=worktree_path, head="def", branch="main-stable"),
                    ]

                def require_clean_working_tree(self, repo_root_arg, *, allowed_missing_paths=()):
                    return None

                def remove_worktree(self, repo_root_arg, *, path, force, source_fd=None, target_fd=None):
                    # Simulate Git removing only its record while leaving the
                    # original empty directory for descriptor-bound cleanup.
                    return None

            class FakeEnvironmentGateway:
                def getenv(self, name):
                    return str(central_root)

            ports = app_ports.Ports(
                node_reader=object(),
                repo_root=repo_root,
                git_gateway=FakeGitGateway(),
                environment_gateway=FakeEnvironmentGateway(),
            )

            result = app_worktree.worktree_remove(app_contracts.WorktreeRemoveRequest(target="stable"), ports)

            assert result.removed_record
            assert result.removed_directory
            assert not worktree_path.exists()
