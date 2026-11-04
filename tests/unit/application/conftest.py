"""Keep the user's own SpecDock settings file out of the application tests (iss-00552).

The dashboard reads `$XDG_CONFIG_HOME/spec-dock/config.json`; a developer's real `dashboard.visible: false`
would otherwise hide every repository in these tests. Only the SpecDock file moves: HOME stays, and git keeps
reading `~/.gitconfig`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)  # noqa: RUF076 -- keeps every application test hermetic
def _no_user_settings(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> Path:
    config = tmp_path_factory.mktemp("xdg-config")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config))
    return config
