"""`branch show/create/switch` in canonical mode observe Git refs without a binding registry (iss-00440).

Replaces tests/cli_runtime/test_issue413_branch.py and tests/cli_runtime/test_branch_commands_vnext.py, which ran
on the retired schema-3 committed workspace. The default branch name is now the Scope ID alone (`init-00001`,
formerly `init-00001-fixture`).
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.legacy_contracts_g3 import WORK_TARGET, cli, git_out, has_branch, make_world, select

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld

NAME = "init-00001"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    return make_world(tmp_path, monkeypatch, capsys)


def _branch(capsys: pytest.CaptureFixture[str], root: Path, leaf: str, *options: str) -> tuple[int, dict]:
    return cli(capsys, "--project", str(root), "branch", leaf, NAME, *options, "--json")


def _commit(root: Path, message: str, *paths: str) -> None:
    if paths:
        subprocess.run(["git", "-C", str(root), "add", "--", *paths], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True, capture_output=True)


def _current(root: Path) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"])


def _hook(root: Path, name: str, body: str) -> None:
    hook = root / ".git/hooks" / name
    hook.write_text("#!/bin/sh\n" + body)
    hook.chmod(0o700)


def test_branch_show_observes_default_candidate_without_binding_store(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    tip = git_out(root, "rev-parse", "HEAD")
    subprocess.run(["git", "-C", str(root), "branch", NAME, tip], check=True, capture_output=True)
    assert main(["--project", str(root), "branch", "show", NAME, "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["data"] == {
        "kind": "branch",
        "result": {
            "scope_id": NAME,
            "name": NAME,
            "tip": tip,
            "created": False,
            "switched": False,
            "binding_persisted": False,
        },
    }
    assert result["effects"] == []
    assert not (root / "spec-dock/.agent").exists()
    assert not (root / ".git/spec-dock").exists()


def test_switch_current_branch_is_unchanged_and_does_not_run_checkout_hook(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    marker = tmp_path / "checkout-hook-ran"
    _hook(root, "post-checkout", f"touch {shlex.quote(str(marker))}\n")
    code, result = _branch(capsys, root, "switch", "--name", "main")
    assert code == 0, result
    assert result["status"] == "unchanged"
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "unchanged", "target": "main"}]
    assert not marker.exists()
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
@pytest.mark.parametrize("tracked", [False, True])
def test_successful_checkout_hook_dirtying_the_workspace_keeps_checkout_effect_but_returns_partial(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], tracked: bool
) -> None:
    root = world.main
    file = root / "hook-change.txt"
    if tracked:
        file.write_text("original tracked content\n")
        _commit(root, "fixture tracked content", file.name)
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select(world)
    before = record.read_bytes()
    _hook(root, "post-checkout", f"printf 'hook change\\n' > {shlex.quote(str(file))}\n")
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    assert result["status"] == "partial" and result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    # canonical mode reports the confirmed checkout as switched (legacy reported switched=False)
    assert result["data"]["result"]["switched"] is True and record.read_bytes() == before
    assert file.read_text() == "hook change\n"
    assert _current(root) == b"candidate\n"
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
@pytest.mark.parametrize("change", ["remove", "replace", "rewrite"])
def test_checkout_hook_changing_ignored_direct_record_is_partial_without_restoration(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select(world)
    before = record.read_bytes()
    replacement = record.parent / ("target-" + "b" * 32 + ".json")
    body = {
        "remove": f"rm {shlex.quote(str(record))}\n",
        "replace": f"mv {shlex.quote(str(record))} {shlex.quote(str(replacement))}\n",
        "rewrite": f"printf '\\n' >> {shlex.quote(str(record))}\n",
    }[change]
    _hook(root, "post-checkout", body)
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    assert result["status"] == "partial" and result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert "direct selection changed" in result["error"]["message"]
    # canonical mode reports the confirmed checkout as switched (legacy reported switched=False)
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert _current(root) == b"candidate\n"
    assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    if change == "rewrite":
        assert record.read_bytes() == before + b"\n"
    else:
        assert not record.exists()
        if change == "replace":
            assert replacement.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
def test_failed_checkout_hook_changing_direct_record_keeps_git_error_and_confirmed_checkout(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select(world)
    _hook(root, "post-checkout", f"rm {shlex.quote(str(record))}\nprintf 'hook failed\\nsecond line\\n' >&2\nexit 17\n")
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    # canonical mode reports the confirmed checkout as switched (legacy reported switched=False)
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert result["error"]["details"]["git"]["stderr"] == "Switched to branch 'candidate'\nhook failed\nsecond line\n"
    assert "direct selection changed" in result["error"]["details"]["verification_error"]
    assert not record.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX reference-transaction hook")
def test_branch_creation_hook_changing_direct_record_is_partial_with_created_ref_retained(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    record = select(world)
    _hook(root, "reference-transaction", f'if [ "$1" = committed ]; then rm {shlex.quote(str(record))}; fi\nexit 0\n')
    code, result = _branch(capsys, root, "create", "--base", "HEAD")
    assert code == 6, result
    assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
    assert "direct selection changed" in result["error"]["message"]
    assert result["data"]["result"]["created"] is True and result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": NAME}]
    assert _current(root) == b"main\n"
    assert has_branch(root, NAME)
    assert not record.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
def test_checkout_hook_acquiring_a_direct_record_from_empty_selection_returns_partial(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select(world)
    seed = tmp_path / "record-seed.json"
    seed.write_bytes(record.read_bytes())
    record.unlink()
    _hook(root, "post-checkout", f"cp {shlex.quote(str(seed))} {shlex.quote(str(record))}\n")
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    assert result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    # canonical mode reports the confirmed checkout as switched (legacy reported switched=False)
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert record.read_bytes() == seed.read_bytes()


@pytest.mark.parametrize("leaf", ["create", "switch"])
def test_branch_mutation_refuses_unobservable_direct_record_before_git_changes(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    directory = root / WORK_TARGET
    directory.mkdir(parents=True)
    record = directory / ("target-" + "a" * 32 + ".json")
    record.write_bytes(b"invalid immutable selection")
    arguments = ["--base", "HEAD"] if leaf == "create" else ["--name", "candidate"]
    code, result = _branch(capsys, root, leaf, *arguments)
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == b"invalid immutable selection"
    assert _current(root) == b"main\n"
    assert not has_branch(root, NAME)


def test_branch_create_only_creates_ref_at_fixed_base(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    tip = git_out(root, "rev-parse", "HEAD")
    code, result = _branch(capsys, root, "create", "--base", "HEAD")
    assert code == 0, result
    assert result["data"]["result"] == {
        "scope_id": NAME,
        "name": NAME,
        "tip": tip,
        "created": True,
        "switched": False,
        "binding_persisted": False,
    }
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": NAME}]
    assert _current(root) == b"main\n"
    code, shown = _branch(capsys, root, "show")
    assert code == 0 and shown["data"]["result"]["tip"] == tip
    assert not (root / ".git/spec-dock").exists()
    assert not (root / "spec-dock/.agent").exists()


def test_branch_show_explicit_missing_ref_is_an_observation(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    code, result = _branch(capsys, world.main, "show", "--name", "missing")
    assert code == 0, result
    assert result["data"]["result"]["name"] == "missing"
    assert result["data"]["result"]["tip"] is None
    assert result["data"]["result"]["binding_persisted"] is False
    assert result["effects"] == []


def test_branch_switch_keeps_immutable_selection_and_changes_only_checkout(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    record = select(world)  # selected on main, as `work start` would have recorded it
    before = record.read_bytes()
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 0, result
    assert result["data"]["result"]["switched"] is True
    assert result["data"]["result"]["binding_persisted"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert record.read_bytes() == before
    assert _current(root) == b"candidate\n"
    code, shown = cli(capsys, "--project", str(root), "active", "show", "--json")
    assert code == 0, shown
    selection = shown["data"]["selection"]
    assert selection["status"] == "selected"
    assert selection["selected_branch"] == "main"
    assert selection["current_branch"] == "candidate"
    assert selection["branch_changed"] is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX native checkout hook")
def test_branch_switch_hook_failure_retains_observed_checkout_and_git_stderr(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    _hook(root, "post-checkout", "printf 'fixture post-checkout failed\\n' >&2\nexit 1\n")
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert (
        result["error"]["details"]["git"]["stderr"] == "Switched to branch 'candidate'\nfixture post-checkout failed\n"
    )
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert not (root / "spec-dock/.agent").exists()


def test_branch_switch_confirmed_unchanged_after_index_lock_failure_is_failed(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    (root / ".git/index.lock").write_text("fixture lock\n")
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 5, result
    assert result["status"] == "failed"
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "failed", "target": "candidate"}]
    assert "index.lock" in result["error"]["details"]["git"]["stderr"]
    assert _current(root) == b"main\n"


@pytest.mark.skipif(os.name == "nt", reason="POSIX native Git executable fixture")
@pytest.mark.parametrize("failure", ["exit19", "wrong-tip", "clone-switch"])
def test_branch_create_native_failure_does_not_hide_already_created_ref(
    world: CanonicalWorld,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failure: str,
) -> None:
    root = world.main
    (root / "readme.md").write_text("second commit\n")
    _commit(root, "second commit", "readme.md")
    real_git = shutil.which("git")
    assert real_git
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    redirected = ""
    if failure == "clone-switch":
        second_common = tmp_path / "second-common"
        subprocess.run([real_git, "clone", "--bare", str(root), str(second_common)], check=True, capture_output=True)
        subprocess.run(
            [real_git, "--git-dir", str(second_common), "config", "core.bare", "false"], check=True, capture_output=True
        )
        shutil.copy2(root / ".git/index", second_common / "index")
        redirected = (
            f" subprocess.run([{real_git!r}, '--git-dir', {str(second_common)!r}, *sys.argv[3:]], check=True)\n"
            f" os.rename({str(root / '.git')!r}, {str(tmp_path / 'displaced-common')!r})\n"
            f" os.rename({str(second_common)!r}, {str(root / '.git')!r}); sys.exit(0)\n"
        )
    git.write_text(
        f"#!{sys.executable}\nimport os, subprocess, sys\n"
        "if len(sys.argv)==6 and sys.argv[3] == 'branch':\n"
        + (
            f" subprocess.run([{real_git!r}, *sys.argv[1:5], 'HEAD~1'], check=True); sys.exit(0)\n"
            if failure == "wrong-tip"
            else f" subprocess.run([{real_git!r}, *sys.argv[1:]], check=True)\n"
            + (redirected or " sys.stderr.write('fixture failure after ref creation\\n'); sys.exit(19)\n")
        )
        + f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n"
    )
    git.chmod(0o700)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ.get("PATH", ""))
    code, result = _branch(capsys, root, "create", "--base", "HEAD")
    assert code == 6, result
    assert result["status"] == "partial"
    assert result["data"]["result"]["created"] is True
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": NAME}]
    if failure == "exit19":
        assert result["error"]["details"]["git"]["stderr"] == "fixture failure after ref creation\n"
        assert result["error"]["details"]["git"]["returncode"] == 19
    elif failure == "wrong-tip":
        assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
        # canonical mode reports the fixed base as the result tip (legacy reported the observed tip); the ref
        # itself still points where the native step left it
        assert git_out(root, "rev-parse", f"refs/heads/{NAME}") == git_out(root, "rev-parse", "HEAD~1")
    else:
        assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
        assert "identity" in result["error"]["message"]
        # the replacement common directory's origin is a local path, so canonical reads refuse it; read the ref
        assert has_branch(root, NAME)
        return
    code, shown = _branch(capsys, root, "show")
    assert code == 0 and shown["data"]["result"]["tip"] is not None


def test_branch_create_dry_run_does_not_reserve_ref(world: CanonicalWorld, capsys: pytest.CaptureFixture[str]) -> None:
    root = world.main
    code, result = _branch(capsys, root, "create", "--base", "HEAD", "--dry-run")
    assert code == 0, result
    assert result["status"] == "planned"
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["created"] is False
    assert result["effects"] == [{"kind": "git.branch.create", "status": "planned", "target": NAME}]
    code, shown = _branch(capsys, root, "show")
    assert code == 0 and shown["data"]["result"]["tip"] is None


@pytest.mark.parametrize("option", ["--resume", "--rollback"])
def test_branch_rejects_retired_journal_inputs_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, result = cli(
        capsys, "--project", str(tmp_path / "missing"), "branch", "create", "init-00001", option, "0" * 32, "--json"
    )
    assert code == 2
    assert result["error"]["code"] == "ARGUMENT_RETIRED"
    assert result["effects"] == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("leaf", ["show", "create", "switch"])
def test_branch_help_describes_refs_and_no_journal(leaf: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["help", "branch", leaf]) == 0
    output = capsys.readouterr().out
    assert "registry" not in output
    assert "--resume" not in output
    assert "--rollback" not in output
    assert "--name" in output


@pytest.mark.parametrize("dry_run", [False, True])
def test_branch_switch_other_worktree_occupancy_is_checked_before_checkout(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root = world.main
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "candidate", str(tmp_path / "linked"), "HEAD"],
        check=True,
        capture_output=True,
    )
    code, result = _branch(capsys, root, "switch", "--name", "candidate", *(["--dry-run"] if dry_run else []))
    assert code == 3, result
    assert result["effects"] == []
    assert "another worktree" in result["error"]["message"]
    assert _current(root) == b"main\n"


@pytest.mark.skipif(os.name == "nt", reason="POSIX native Git directory replacement hook")
def test_branch_switch_does_not_confirm_checkout_from_a_replacement_clone(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    second_common = tmp_path / "second-common"
    subprocess.run(["git", "clone", "--bare", str(root), str(second_common)], check=True, capture_output=True)
    subprocess.run(
        ["git", "--git-dir", str(second_common), "config", "core.bare", "false"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "--git-dir", str(second_common), "symbolic-ref", "HEAD", "refs/heads/candidate"],
        check=True,
        capture_output=True,
    )
    shutil.copy2(root / ".git/index", second_common / "index")
    displaced = tmp_path / "displaced-common"
    _hook(
        root,
        "post-checkout",
        f"mv {shlex.quote(str(root / '.git'))} {shlex.quote(str(displaced))}\n"
        f"mv {shlex.quote(str(second_common))} {shlex.quote(str(root / '.git'))}\n",
    )
    code, result = _branch(capsys, root, "switch", "--name", "candidate")
    assert code == 6, result
    # canonical mode reports the confirmed checkout as switched (legacy reported switched=False)
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert "identity" in result["error"]["message"]
    assert displaced.is_dir()


@pytest.mark.skipif(os.name == "nt", reason="POSIX native directory flock boundary")
def test_branch_create_proceeds_while_start_exclusion_is_held(world: CanonicalWorld) -> None:
    import fcntl

    root = world.main
    fd = os.open(root / ".git", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; from spec_dock.cli import main; sys.exit(main(sys.argv[1:]))",
                "--project",
                str(root),
                "branch",
                "create",
                NAME,
                "--base",
                "HEAD",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == ""
        assert json.loads(result.stdout)["data"]["result"]["created"] is True
    finally:
        os.close(fd)


@pytest.mark.parametrize("guard", [["--expect-current", "init-00001"], ["--expect-backend", "local"]])
def test_branch_create_expectation_mismatch_has_no_git_effects(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root = world.main
    code, result = _branch(capsys, root, "create", "--base", "HEAD", *guard)
    assert code == 3, result
    assert result["effects"] == []
    code, shown = _branch(capsys, root, "show")
    assert code == 0 and shown["data"]["result"]["tip"] is None


@pytest.mark.parametrize("name", ["existing", "日本語"])
def test_branch_create_preserves_existing_refs_and_rejects_non_ascii_names_before_any_effect(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], name: str
) -> None:
    root = world.main
    if name == "existing":
        subprocess.run(["git", "-C", str(root), "branch", name, "HEAD"], check=True, capture_output=True)
    before = tree_digest(root)
    assert main(["--project", str(root), "branch", "create", NAME, "--base", "HEAD", "--name", name, "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and result["status"] == "failed" and not output.err
    assert tree_digest(root) == before and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("tracked", [False, True])
def test_branch_switch_refuses_unfinished_changes_and_preserves_the_direct_record(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], tracked: bool
) -> None:
    root = world.main
    record = select(world)
    exact_record = record.read_bytes()
    subprocess.run(["git", "-C", str(root), "branch", "candidate", "HEAD"], check=True, capture_output=True)
    changed = root / "spec-dock/.gitignore" if tracked else root / "unfinished.txt"
    changed.write_bytes(changed.read_bytes() + b"# unfinished tracked change\n" if tracked else b"unfinished payload")
    before = tree_digest(root)
    assert main(["--project", str(root), "branch", "switch", NAME, "--name", "candidate", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and "clean" in result["error"]["message"] and not output.err
    assert record.read_bytes() == exact_record and tree_digest(root) == before
    assert _current(root) == b"main\n"


# --- from tests/cli_runtime/test_branch_commands_vnext.py ---


def test_branch_adapter_create_show_switch_and_dry_run(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    root = world.main
    arguments = ["--project", str(root), "branch"]
    before = tree_digest(root)
    tip = git_out(root, "rev-parse", "HEAD")
    code, planned = cli(capsys, *arguments, "create", NAME, "--base", "HEAD", "--dry-run", "--json")
    assert code == 0, planned
    assert planned["status"] == "planned" and tree_digest(root) == before
    assert planned["data"]["result"]["name"] == NAME
    assert not has_branch(root, NAME)
    code, created = cli(capsys, *arguments, "create", NAME, "--base", "HEAD", "--json")
    assert code == 0, created
    assert created["data"]["result"] == {
        "scope_id": NAME,
        "name": NAME,
        "tip": tip,
        "created": True,
        "switched": False,
        "binding_persisted": False,
    }
    assert created["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": NAME}]
    assert _current(root) == b"main\n"
    code, shown = cli(capsys, *arguments, "show", NAME, "--json")
    assert code == 0 and shown["data"]["result"]["tip"] == tip and shown["effects"] == []
    before = tree_digest(root)
    code, preview = cli(capsys, *arguments, "switch", NAME, "--dry-run", "--json")
    assert code == 0 and preview["status"] == "planned" and tree_digest(root) == before
    code, switched = cli(capsys, *arguments, "switch", NAME, "--json")
    assert code == 0 and switched["data"]["result"]["switched"] is True
    assert _current(root) == (NAME + "\n").encode()
    refs_before = subprocess.check_output(["git", "-C", str(root), "show-ref"])
    code, rejected = cli(capsys, *arguments, "create", NAME, "--base", "HEAD", "--json")
    assert code == 3
    assert rejected["effects"] == [] and "already exists" in rejected["error"]["message"]
    assert subprocess.check_output(["git", "-C", str(root), "show-ref"]) == refs_before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
