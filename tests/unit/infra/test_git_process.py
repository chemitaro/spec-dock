"""Native Git failures retain both captured output streams."""

from pathlib import Path
import subprocess

import pytest

from spec_dock.runtime.infra.git_process import GitProcessError, run_git


def test_native_git_error_preserves_stdout_and_stderr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def rejected(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 19, stdout=b"fixture output\n", stderr=b"fixture error\n")

    monkeypatch.setattr(subprocess, "run", rejected)
    with pytest.raises(GitProcessError) as caught:
        run_git(tmp_path, "checkout", "requested", mutation=True)
    details = caught.value.details()["git"]
    assert details["stdout"] == "fixture output\n"
    assert details["stderr"] == "fixture error\n"
    assert details["returncode"] == 19


def test_missing_probe_does_not_hide_exit_one_with_native_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def rejected(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout=b"", stderr=b"fixture unavailable\n")

    monkeypatch.setattr(subprocess, "run", rejected)
    with pytest.raises(GitProcessError) as caught:
        run_git(tmp_path, "rev-parse", "--verify", "--quiet", "refs/heads/requested", missing_ok=True)
    assert caught.value.details()["git"]["stderr"] == "fixture unavailable\n"
    assert caught.value.returncode == 1
