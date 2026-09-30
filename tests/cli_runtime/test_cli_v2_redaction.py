"""Credentials in rejected public input must not escape into diagnostics."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.mark.parametrize("credential", ["github_pat_fixture_secret", "Bearer fixture_secret", "ghp_fixture_secret"])
def test_json_parse_error_redacts_credentials(credential: str, capsys: CaptureFixture[str]) -> None:
    assert main(["work", credential, "--json"]) == 2
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["schema_version"] == "specdock.cli/v2"
    assert payload["error"]["code"] == "USAGE_ERROR"
    assert "[redacted]" in payload["error"]["message"]
    assert credential not in output.out + output.err
    assert "fixture_secret" not in output.out + output.err
    assert payload["effects"] == []
