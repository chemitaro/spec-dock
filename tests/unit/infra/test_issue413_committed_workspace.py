"""Committed snapshots ignore non-Scope paths on supported POSIX filesystems."""

from pathlib import Path
import subprocess

from spec_dock.runtime.infra.committed_workspace import committed_workspace


def test_committed_reader_ignores_non_scope_path_without_materializing_it(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    directory = tmp_path / "spec-dock/initiatives/..\\escape"
    directory.mkdir(parents=True)
    (directory / ".meta.json").write_text("{}")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "unsafe path",
        ],
        check=True,
    )
    oid = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"]).decode().rstrip("\n")
    with committed_workspace(tmp_path, oid, timeout=30) as workspace:
        assert list((workspace / "initiatives").iterdir()) == []
        assert not (workspace.parent / "escape").exists()
    assert (directory / ".meta.json").read_text() == "{}"
