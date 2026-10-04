"""Branch commands observe Git refs without a shared binding registry."""

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
from tests.cli_runtime.test_issue413_work_start import committed_workspace, open_issue

if TYPE_CHECKING:
    from pathlib import Path


def test_branch_show_observes_default_candidate_without_binding_store(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    tip = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().removesuffix("\n")
    subprocess.run(["git", "-C", str(root), "branch", "init-00001-fixture", tip], check=True, capture_output=True)
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert output.err == ""
    assert result["data"] == {
        "kind": "branch",
        "result": {
            "scope_id": "init-00001",
            "name": "init-00001-fixture",
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    marker = tmp_path / "checkout-hook-ran"
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\ntouch {shlex.quote(str(marker))}\n")
    hook.chmod(0o755)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "main", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "unchanged"
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "unchanged", "target": "main"}]
    assert not marker.exists()
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
@pytest.mark.parametrize("tracked", [False, True])
def test_successful_checkout_hook_dirtying_the_workspace_keeps_checkout_effect_but_returns_partial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], tracked: bool
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    file = root / "hook-change.txt"
    if tracked:
        file.write_text("original tracked content\n")
        subprocess.run(["git", "-C", str(root), "add", "--", file.name], check=True, capture_output=True)
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
                "fixture tracked content",
            ],
            check=True,
            capture_output=True,
        )
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select_fixture(root)
    before = record.read_bytes()
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\nprintf 'hook change\\n' > {shlex.quote(str(file))}\n")
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert result["data"]["result"]["switched"] is False and record.read_bytes() == before
    assert file.read_text() == "hook change\n"
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"candidate\n"
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    assert not (root / ".git/spec-dock").exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
@pytest.mark.parametrize("change", ["remove", "replace", "rewrite"])
def test_checkout_hook_changing_ignored_direct_record_is_partial_without_restoration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], change: str
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select_fixture(root)
    before = record.read_bytes()
    replacement = record.parent / ("target-" + "b" * 32 + ".json")
    body = {
        "remove": f"rm {shlex.quote(str(record))}\n",
        "replace": f"mv {shlex.quote(str(record))} {shlex.quote(str(replacement))}\n",
        "rewrite": f"printf '\\n' >> {shlex.quote(str(record))}\n",
    }[change]
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\n" + body)
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert "direct selection changed" in result["error"]["message"]
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"candidate\n"
    assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "-z"])
    if change == "rewrite":
        assert record.read_bytes() == before + b"\n"
    else:
        assert not record.exists()
        if change == "replace":
            assert replacement.read_bytes() == before


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
def test_failed_checkout_hook_changing_direct_record_keeps_git_error_and_confirmed_checkout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select_fixture(root)
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\nrm {shlex.quote(str(record))}\nprintf 'hook failed\\nsecond line\\n' >&2\nexit 17\n")
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert result["error"]["code"] == "GIT_FAILED"
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert result["error"]["details"]["git"]["stderr"] == "Switched to branch 'candidate'\nhook failed\nsecond line\n"
    assert "direct selection changed" in result["error"]["details"]["verification_error"]
    assert not record.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX reference-transaction hook")
def test_branch_creation_hook_changing_direct_record_is_partial_with_created_ref_retained(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    hook = root / ".git/hooks/reference-transaction"
    hook.write_text(f'#!/bin/sh\nif [ "$1" = committed ]; then rm {shlex.quote(str(record))}; fi\nexit 0\n')
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
    assert "direct selection changed" in result["error"]["message"]
    assert result["data"]["result"]["created"] is True and result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": "init-00001-fixture"}]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert subprocess.check_output(["git", "-C", str(root), "rev-parse", "refs/heads/init-00001-fixture"])
    assert not record.exists()


@pytest.mark.skipif(os.name != "posix", reason="native POSIX post-checkout hook")
def test_checkout_hook_acquiring_a_direct_record_from_empty_selection_returns_partial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    record = select_fixture(root)
    seed = tmp_path / "record-seed.json"
    seed.write_bytes(record.read_bytes())
    record.unlink()
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\ncp {shlex.quote(str(seed))} {shlex.quote(str(record))}\n")
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert record.read_bytes() == seed.read_bytes()


@pytest.mark.parametrize("leaf", ["create", "switch"])
def test_branch_mutation_refuses_unobservable_direct_record_before_git_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    directory = root / "spec-dock/.agent/work-target"
    directory.mkdir(parents=True)
    record = directory / ("target-" + "a" * 32 + ".json")
    record.write_bytes(b"invalid immutable selection")
    arguments = ["--base", "HEAD"] if leaf == "create" else ["--name", "candidate"]
    assert main(["--project", str(root), "branch", leaf, "init-00001", *arguments, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == [] and record.read_bytes() == b"invalid immutable selection"
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert (
        subprocess.run(
            ["git", "-C", str(root), "show-ref", "--verify", "--quiet", "refs/heads/init-00001-fixture"],
            capture_output=True,
        ).returncode
        == 1
    )


def test_branch_create_only_creates_ref_at_fixed_base(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = committed_workspace(tmp_path / "consumer")
    tip = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().removesuffix("\n")
    assert main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"] == {
        "scope_id": "init-00001",
        "name": "init-00001-fixture",
        "tip": tip,
        "created": True,
        "switched": False,
        "binding_persisted": False,
    }
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": "init-00001-fixture"}]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["tip"] == tip
    assert not (root / ".git/spec-dock").exists()
    assert not (root / "spec-dock/.agent").exists()


def test_branch_show_explicit_missing_ref_is_an_observation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = committed_workspace(tmp_path / "consumer")
    assert main(["--project", str(root), "branch", "show", "init-00001", "--name", "missing", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["name"] == "missing"
    assert result["data"]["result"]["tip"] is None
    assert result["data"]["result"]["binding_persisted"] is False
    assert result["effects"] == []


def test_branch_create_rejects_base_without_target_before_creating_ref(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "checkout", "-qb", "without-target"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "rm", "-r", "spec-dock/initiatives"], check=True, capture_output=True)
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
            "no target",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True, capture_output=True)
    assert main(["--project", str(root), "branch", "create", "init-00001", "--base", "without-target", "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert "candidate" in result["error"]["message"]
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["tip"] is None


def test_branch_switch_keeps_immutable_selection_and_changes_only_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_lifecycle.GithubIssueGateway.get", lambda _, *args: open_issue(*args)
    )
    assert (
        main([
            "--project",
            str(root),
            "work",
            "start",
            "init-00001",
            "--branch",
            "selected",
            "--base",
            "HEAD",
            "--json",
        ])
        == 0
    )
    capsys.readouterr()
    record = next((root / "spec-dock/.agent/work-target").glob("target-*.json"))
    before = record.read_bytes()
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["switched"] is True
    assert result["data"]["result"]["binding_persisted"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert record.read_bytes() == before
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"candidate\n"
    assert main(["--project", str(root), "active", "show", "--json"]) == 0
    selection = json.loads(capsys.readouterr().out)["data"]["selection"]
    assert selection["status"] == "selected"
    assert selection["selected_branch"] == "selected"
    assert selection["current_branch"] == "candidate"
    assert selection["branch_changed"] is True


@pytest.mark.skipif(os.name == "nt", reason="POSIX native checkout hook")
def test_branch_switch_hook_failure_retains_observed_checkout_and_git_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    hook = root / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nprintf 'fixture post-checkout failed\\n' >&2\nexit 1\n")
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["data"]["result"]["switched"] is True
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert (
        result["error"]["details"]["git"]["stderr"] == "Switched to branch 'candidate'\nfixture post-checkout failed\n"
    )
    assert result["error"]["details"]["git"]["returncode"] == 1
    assert not (root / "spec-dock/.agent").exists()


def test_branch_switch_confirmed_unchanged_after_index_lock_failure_is_failed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "branch", "candidate"], check=True, capture_output=True)
    (root / ".git/index.lock").write_text("fixture lock\n")
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 5
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "failed", "target": "candidate"}]
    assert "index.lock" in result["error"]["details"]["git"]["stderr"]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"


@pytest.mark.skipif(os.name == "nt", reason="POSIX native Git executable fixture")
@pytest.mark.parametrize("failure", ["exit19", "wrong-tip", "clone-switch"])
def test_branch_create_native_failure_does_not_hide_already_created_ref(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], failure: str
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    (root / "readme.md").write_text("second commit\n")
    subprocess.run(["git", "-C", str(root), "add", "readme.md"], check=True, capture_output=True)
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
            "second commit",
        ],
        check=True,
        capture_output=True,
    )
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
    assert main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial"
    assert result["data"]["result"]["created"] is True
    assert result["effects"] == [{"kind": "git.branch.create", "status": "succeeded", "target": "init-00001-fixture"}]
    if failure == "exit19":
        assert result["error"]["details"]["git"]["stderr"] == "fixture failure after ref creation\n"
        assert result["error"]["details"]["git"]["returncode"] == 19
    elif failure == "wrong-tip":
        assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
        assert result["data"]["result"]["tip"] == subprocess.check_output([
            real_git,
            "-C",
            str(root),
            "rev-parse",
            "HEAD~1",
        ]).decode().removesuffix("\n")
    else:
        assert result["error"]["code"] == "BRANCH_VERIFICATION_FAILED"
        assert "identity" in result["error"]["message"]
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["tip"] is not None


def test_branch_create_dry_run_does_not_reserve_ref(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = committed_workspace(tmp_path / "consumer")
    assert (
        main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", "--dry-run", "--json"]) == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "planned"
    assert result["data"]["result"]["can_apply"] is True and result["data"]["result"]["blockers"] == []
    assert result["data"]["result"]["created"] is False
    assert result["effects"] == [{"kind": "git.branch.create", "status": "planned", "target": "init-00001-fixture"}]
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["tip"] is None


@pytest.mark.parametrize("option", ["--resume", "--rollback"])
def test_branch_rejects_retired_journal_inputs_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], option: str
) -> None:
    assert (
        main(["--project", str(tmp_path / "missing"), "branch", "create", "init-00001", option, "0" * 32, "--json"])
        == 2
    )
    result = json.loads(capsys.readouterr().out)
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
    tmp_path: Path, capsys: pytest.CaptureFixture[str], dry_run: bool
) -> None:
    root = committed_workspace(tmp_path / "main")
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "candidate", str(tmp_path / "linked"), "HEAD"],
        check=True,
        capture_output=True,
    )
    assert (
        main([
            "--project",
            str(root),
            "branch",
            "switch",
            "init-00001",
            "--name",
            "candidate",
            *(["--dry-run"] if dry_run else []),
            "--json",
        ])
        == 3
    )
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert "another worktree" in result["error"]["message"]
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"


@pytest.mark.skipif(os.name == "nt", reason="POSIX native Git directory replacement hook")
def test_branch_switch_does_not_confirm_checkout_from_a_replacement_clone(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "main")
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
    hook = root / ".git/hooks/post-checkout"
    hook.write_text(
        f"#!/bin/sh\nmv {shlex.quote(str(root / '.git'))} {shlex.quote(str(displaced))}\nmv {shlex.quote(str(second_common))} {shlex.quote(str(root / '.git'))}\n"
    )
    hook.chmod(0o700)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 6
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["switched"] is False
    assert result["effects"] == [{"kind": "git.checkout", "status": "succeeded", "target": "candidate"}]
    assert result["error"]["code"] == "CHECKOUT_VERIFICATION_FAILED"
    assert "identity" in result["error"]["message"]
    assert displaced.is_dir()


@pytest.mark.skipif(os.name == "nt", reason="POSIX native directory flock boundary")
def test_branch_create_proceeds_while_start_exclusion_is_held(tmp_path: Path) -> None:
    import fcntl

    root = committed_workspace(tmp_path / "consumer")
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
                "init-00001",
                "--base",
                "HEAD",
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == ""
        assert json.loads(result.stdout)["data"]["result"]["created"] is True
    finally:
        os.close(fd)


@pytest.mark.parametrize("guard", [["--expect-current", "init-00001"], ["--expect-backend", "local"]])
def test_branch_create_expectation_mismatch_has_no_git_effects(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], guard: list[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    assert main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", *guard, "--json"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    assert main(["--project", str(root), "branch", "show", "init-00001", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["result"]["tip"] is None


@pytest.mark.parametrize("name", ["existing", "日本語"])
def test_branch_create_preserves_existing_refs_and_rejects_non_ascii_names_before_any_effect(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], name: str
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root = committed_workspace(tmp_path / "consumer")
    if name == "existing":
        subprocess.run(["git", "-C", str(root), "branch", name, "HEAD"], check=True, capture_output=True)
    before = tree_digest(root)
    assert (
        main(["--project", str(root), "branch", "create", "init-00001", "--base", "HEAD", "--name", name, "--json"])
        == 3
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and result["status"] == "failed" and not output.err
    assert tree_digest(root) == before and not (root / ".git/spec-dock").exists()


@pytest.mark.parametrize("tracked", [False, True])
def test_branch_switch_refuses_unfinished_changes_and_preserves_the_direct_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], tracked: bool
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    exact_record = record.read_bytes()
    subprocess.run(["git", "-C", str(root), "branch", "candidate", "HEAD"], check=True, capture_output=True)
    changed = root / "spec-dock/.gitignore" if tracked else root / "unfinished.txt"
    changed.write_bytes(changed.read_bytes() + b"# unfinished tracked change\n" if tracked else b"unfinished payload")
    before = tree_digest(root)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "candidate", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and "clean" in result["error"]["message"] and not output.err
    assert record.read_bytes() == exact_record and tree_digest(root) == before
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"


def test_branch_switch_refuses_a_moved_ref_without_the_scope_and_keeps_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest
    from tests.cli_runtime.test_issue413_active import select_fixture

    root = committed_workspace(tmp_path / "consumer")
    subprocess.run(["git", "-C", str(root), "switch", "-c", "without-target"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "rm", "-r", "--", "spec-dock/initiatives"], check=True, capture_output=True)
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
            "candidate without target",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(root), "switch", "main"], check=True, capture_output=True)
    record = select_fixture(root)
    exact_record = record.read_bytes()
    before = tree_digest(root)
    assert main(["--project", str(root), "branch", "switch", "init-00001", "--name", "without-target", "--json"]) == 3
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and "candidate" in result["error"]["message"] and not output.err
    assert record.read_bytes() == exact_record and tree_digest(root) == before
    assert subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"]) == b"main\n"
