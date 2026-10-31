"""Tests that need `cue` fail, never skip, when it is missing (iss-00472 RQ-17, AC-09)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.cue import PINNED_CUE_VERSION, cue_executable

if TYPE_CHECKING:
    from pathlib import Path


def test_a_missing_cue_fails_the_test_with_how_to_install_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(pytest.fail.Exception) as failure:
        cue_executable()
    message = str(failure.value)
    assert f"cuelang.org/go/cmd/cue@{PINNED_CUE_VERSION}" in message
    assert "PATH" in message
