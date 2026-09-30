"""Credentials in rejected public input must not escape into diagnostics."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


@pytest.mark.parametrize("credential", ["github_pat_fixture_secret", "Bearer fixture_secret", "ghp_fixture_secret"])
@pytest.mark.parametrize("json_mode", [True, False])
def test_parse_error_redacts_credentials(credential: str, json_mode: bool, capsys: CaptureFixture[str]) -> None:
    assert main(["work", credential, *(["--json"] if json_mode else [])]) == 2
    output = capsys.readouterr()
    if json_mode:
        payload = json.loads(output.out)
        assert payload["schema_version"] == "specdock.cli/v2"
        assert payload["error"]["code"] == "USAGE_ERROR"
        assert payload["effects"] == []
    assert "[redacted]" in output.out + output.err
    assert credential not in output.out + output.err
    assert "fixture_secret" not in output.out + output.err


@pytest.mark.parametrize("json_mode", [True, False])
def test_parse_error_redacts_url_userinfo_and_keeps_host_and_path(json_mode: bool, capsys: CaptureFixture[str]) -> None:
    assert (
        main(["work", "https://fixture_user:fixture_secret@example.com/path", *(["--json"] if json_mode else [])]) == 2
    )
    output = capsys.readouterr()
    assert "fixture_user" not in output.out + output.err
    assert "fixture_secret" not in output.out + output.err
    assert "https://[redacted]@example.com/path" in output.out + output.err
