"""A fixed repository, pinned revision, and inert complete bundle are required."""

from __future__ import annotations

from io import BytesIO
import subprocess
import tarfile
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from spec_dock.installation.source import (
    PinnedSource,
    assert_disjoint_source_target,
    download_pinned_archive,
    fixed_archive_url,
    resolve_fixed_source,
    resolve_source,
    verify_pinned_archive,
)


def _archive(files: dict[str, bytes], *, special: tuple[str, bytes] | None = None) -> bytes:
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, content in files.items():
            item = tarfile.TarInfo(f"chemitaro-spec-dock-fixed/{name}")
            item.size = len(content)
            item.mode = 0o644
            archive.addfile(item, BytesIO(content))
        if special is not None:
            name, content = special
            item = tarfile.TarInfo(f"chemitaro-spec-dock-fixed/{name}")
            item.size = len(content)
            item.mode = 0o644
            archive.addfile(item, BytesIO(content))
    return buffer.getvalue()


def _minimal_files() -> dict[str, bytes]:
    return {
        "pyproject.toml": b'[project]\nname = "spec-dock"\n',
        "src/spec_dock/assets/spec_dock/.gitignore": b".agent/\n",
        "src/spec_dock/assets/spec_dock/workspace.json": b'{"schema_version":3}',
        "src/spec_dock/assets/spec_dock/docs/readme.md": b"docs",
        "src/spec_dock/assets/spec_dock/templates/readme.md": b"templates",
        "src/spec_dock/assets/spec_dock/system/readme.md": b"system",
        "src/spec_dock/assets/spec_dock/scripts/spec-dock": b"#!/usr/bin/env python3\n",
        "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md": b"skill",
        "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md": b"grill",
    }


def test_version_resolution_pins_one_fixed_commit() -> None:
    commit = "a" * 40
    tag_object = "b" * 40
    refs = f"{tag_object}\trefs/tags/v1.2.3\n{commit}\trefs/tags/v1.2.3^{{}}\n"
    source = resolve_source(version="1.2.3", commit=None, ls_remote_tags=refs)
    assert source.commit == commit
    assert fixed_archive_url(source).endswith(f"/chemitaro/spec-dock/tarball/{commit}")
    with pytest.raises(ValueError, match="exactly one"):
        resolve_source(version="1.2.3", commit=commit, ls_remote_tags=refs)
    with pytest.raises(ValueError, match="exactly one"):
        resolve_source(version="1.2.3", commit=None, ls_remote_tags=refs + f"{commit}\trefs/tags/1.2.3\n")
    with pytest.raises(ValueError, match="complete"):
        resolve_source(version=None, commit="a" * 12)


def test_fixed_source_resolves_tags_once_without_local_git_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        environment = kwargs["env"]
        assert isinstance(environment, dict)
        assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
        assert "GIT_CONFIG_COUNT" not in environment
        return subprocess.CompletedProcess(argv, 0, f"{'a' * 40}\trefs/tags/v1.2.3\n", "")

    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setattr("spec_dock.installation.source.subprocess.run", fake_run)
    pinned = resolve_fixed_source(version="1.2.3", commit=None)
    assert pinned.commit == "a" * 40
    assert calls == [["git", "ls-remote", "--tags", "https://github.com/chemitaro/spec-dock.git"]]


def test_verified_bundle_includes_hidden_assets_and_has_stable_digest(tmp_path: Path) -> None:
    source = PinnedSource("chemitaro/spec-dock", "a" * 40, None)
    archive = _archive(_minimal_files())
    first = verify_pinned_archive(source, archive, tmp_path / "first")
    second = verify_pinned_archive(source, archive, tmp_path / "second")
    assert first.digest == second.digest and len(first.digest) == 64
    assert "src/spec_dock/assets/spec_dock/.gitignore" in first.tooling_paths
    assert "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md" in first.tooling_paths
    assert (first.root / "src/spec_dock/assets/spec_dock/workspace.json").is_file()
    altered = _minimal_files()
    altered["src/spec_dock/cli.py"] = b"changed external engine"
    third = verify_pinned_archive(source, _archive(altered), tmp_path / "third")
    assert third.digest != first.digest


def test_archive_download_checks_fixed_redirect_host(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PinnedSource("chemitaro/spec-dock", "a" * 40, None)

    class FakeResponse:
        def __init__(self, url: str) -> None:
            self.url = url

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

        def geturl(self) -> str:
            return self.url

        def read(self, _limit: int) -> bytes:
            return b"pinned bytes"

    monkeypatch.setattr(
        "spec_dock.installation.source.urlopen",
        lambda _request, **_kwargs: FakeResponse(f"https://codeload.github.com/chemitaro/spec-dock/tar.gz/{'a' * 40}"),
    )
    assert download_pinned_archive(source) == b"pinned bytes"
    monkeypatch.setattr(
        "spec_dock.installation.source.urlopen",
        lambda _request, **_kwargs: FakeResponse("https://example.invalid/archive"),
    )
    with pytest.raises(ValueError, match="redirected"):
        download_pinned_archive(source)
    monkeypatch.setattr(
        "spec_dock.installation.source.urlopen",
        lambda _request, **_kwargs: FakeResponse("https://codeload.github.com/other/repo/tar.gz/sha"),
    )
    with pytest.raises(ValueError, match="redirected"):
        download_pinned_archive(source)


def test_archive_traversal_links_and_missing_hidden_assets_are_rejected(tmp_path: Path) -> None:
    source = PinnedSource("chemitaro/spec-dock", "a" * 40, None)
    with pytest.raises(ValueError, match="path is unsafe"):
        verify_pinned_archive(source, _archive(_minimal_files(), special=("../escape", b"x")), tmp_path / "bad")
    files = _minimal_files()
    del files["src/spec_dock/assets/spec_dock/.gitignore"]
    with pytest.raises(ValueError, match="lacks packaged file"):
        verify_pinned_archive(source, _archive(files), tmp_path / "missing")
    assert not (tmp_path / "missing").exists()
    wrong_project = _minimal_files()
    wrong_project["pyproject.toml"] = b'[project]\nname = "other"\n'
    with pytest.raises(ValueError, match="not SpecDock"):
        verify_pinned_archive(source, _archive(wrong_project), tmp_path / "wrong-project")
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        item = tarfile.TarInfo("chemitaro-spec-dock-fixed/link")
        item.type = tarfile.SYMTYPE
        item.linkname = "../outside"
        archive.addfile(item)
    with pytest.raises(ValueError, match="link or special"):
        verify_pinned_archive(source, buffer.getvalue(), tmp_path / "link")
    with pytest.raises(ValueError, match="capitalization collides"):
        verify_pinned_archive(source, _archive(_minimal_files(), special=("PYPROJECT.toml", b"x")), tmp_path / "case")


def test_source_identity_and_target_overlap_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fixed"):
        fixed_archive_url(PinnedSource("other/repo", "a" * 40, None))
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="overlap"):
        assert_disjoint_source_target(source, source / "consumer")
    assert_disjoint_source_target(source, tmp_path / "separate")


def test_pinned_version_requires_matching_package_version(tmp_path: Path) -> None:
    source = PinnedSource("chemitaro/spec-dock", "a" * 40, "1.2.3")
    with pytest.raises(ValueError, match="version differs"):
        verify_pinned_archive(source, _archive(_minimal_files()), tmp_path / "mismatch")
    assert not (tmp_path / "mismatch").exists()
