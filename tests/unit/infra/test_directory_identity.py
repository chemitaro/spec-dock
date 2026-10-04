"""A held physical identity must detect path replacement without writing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.identity import DirectoryIdentity

if TYPE_CHECKING:
    from pathlib import Path


def test_held_directory_detects_same_path_different_object(tmp_path: Path) -> None:
    directory = tmp_path / "root"
    directory.mkdir()
    with DirectoryIdentity(directory) as held:
        assert held.identity.platform == "posix"
        before = held.identity
        held.verify()
        directory.rename(tmp_path / "old")
        directory.mkdir()
        with DirectoryIdentity(directory) as replacement:
            assert replacement.identity != before
        with pytest.raises(ValueError, match="identity changed"):
            held.verify()
    assert list(directory.iterdir()) == []
