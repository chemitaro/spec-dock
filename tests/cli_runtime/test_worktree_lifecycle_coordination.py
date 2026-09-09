from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING

from tests.cli_runtime.harness import CliRuntimeHarness, main

if TYPE_CHECKING:
    from pathlib import Path


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
            f'  /bin/mv "$5" "$5.original"\n  /bin/ln -s {outside} "$5"\n'
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
