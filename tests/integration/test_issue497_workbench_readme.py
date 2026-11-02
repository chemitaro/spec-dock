"""Template Workbench READMEs stay committable under a root `.workbench/` ignore (iss-00497)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    from collections.abc import Sequence

ROOT = Path(__file__).resolve().parents[2]
GITIGNORE = "spec-dock/.gitignore"
PROVIDER = ROOT / "src/spec_dock/assets/spec_dock/.gitignore"
PREVIOUS = ROOT / "tests/fixtures/issue497/spec-dock-gitignore-0.4.2.txt"
KINDS = ("epic", "initiative", "issue")
READMES = [f"spec-dock/templates/cue/{kind}/.workbench/README.md" for kind in KINDS]


def _git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=cwd, text=True, capture_output=True, check=False)


def _ignored(cwd: Path, paths: Sequence[str]) -> dict[str, bool]:
    # --no-index: judge the ignore rules even for files that are already tracked.
    return {path: _git(cwd, "check-ignore", "-q", "--no-index", path).returncode == 0 for path in paths}


def _populate(repo: Path, *, root_ignore: bool) -> list[str]:
    if root_ignore:
        (repo / ".gitignore").write_text(".workbench/\n", encoding="utf-8")
    (repo / "spec-dock").mkdir(exist_ok=True)
    (repo / GITIGNORE).write_bytes(PROVIDER.read_bytes())
    others = []
    for readme in READMES:
        (repo / readme).parent.mkdir(parents=True, exist_ok=True)
        (repo / readme).write_text("readme\n", encoding="utf-8")
        other = str(Path(readme).with_name("note.md"))
        (repo / other).write_text("scratch\n", encoding="utf-8")
        others.append(other)
    return others


@pytest.mark.parametrize("root_ignore", [True, False])
def test_only_the_readme_is_trackable_with_or_without_a_root_workbench_ignore(
    tmp_path: Path, root_ignore: bool
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    others = _populate(repo, root_ignore=root_ignore)
    assert _ignored(repo, READMES) == dict.fromkeys(READMES, False)
    assert _ignored(repo, others) == dict.fromkeys(others, True)
    added = _git(repo, "add", "--", "spec-dock")
    assert added.returncode == 0, added.stderr
    staged = _git(repo, "diff", "--cached", "--name-only").stdout.split()
    assert sorted(staged) == sorted([GITIGNORE, *READMES])


def test_the_dogfood_copy_matches_the_provider_and_its_readmes_are_trackable() -> None:
    assert (ROOT / GITIGNORE).read_bytes() == PROVIDER.read_bytes()
    assert _ignored(ROOT, READMES) == dict.fromkeys(READMES, False)


def test_the_inventory_accepts_the_0_4_2_bytes() -> None:
    entries = {
        item["path"]: item
        for item in json.loads((ROOT / "src/spec_dock/assets/static-inventory.json").read_text("utf-8"))["files"]
    }
    entry = entries[GITIGNORE]
    assert entry["sha256"] == hashlib.sha256(PROVIDER.read_bytes()).hexdigest()
    assert hashlib.sha256(PREVIOUS.read_bytes()).hexdigest() in entry["known_old_sha256"]
    assert PREVIOUS.read_bytes() != PROVIDER.read_bytes()


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_4_2_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    (target / GITIGNORE).write_bytes(PREVIOUS.read_bytes())
    backup = tmp_path / "backup"
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes"
    )
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    assert applied["data"]["result"]["changed_paths"] == [GITIGNORE]
    assert (target / GITIGNORE).read_bytes() == PROVIDER.read_bytes()
    assert (backup / "static" / GITIGNORE).read_bytes() == PREVIOUS.read_bytes()
    (target / ".gitignore").write_text(".workbench/\n", encoding="utf-8")
    assert _ignored(target, READMES) == dict.fromkeys(READMES, False)
