"""orca-web configuration and request origins (iss-00591 T-01)."""

from __future__ import annotations

import json

import pytest


def payload(section: object) -> bytes:
    return json.dumps({"schema": "specdock.config/v1", "orca_web": section}).encode()


def test_defaults_and_valid_settings() -> None:
    from spec_dock.runtime.domain.orca_web import OrcaWebSettings, parse_orca_web

    default = OrcaWebSettings(True, 8791, None, False)
    assert parse_orca_web(None) == default
    assert parse_orca_web(b'{"schema":"specdock.config/v1"}') == default
    assert parse_orca_web(payload({})) == default
    assert parse_orca_web(payload({"enabled": False, "port": 9001})) == OrcaWebSettings(False, 9001, None, False)


INVALID_SECTIONS: tuple[object, ...] = (
    None,
    [],
    1,
    {"unknown": True},
    {"enabled": 0},
    {"enabled": "yes"},
    {"enabled": None},
    {"port": True},
    {"port": False},
    {"port": 0},
    {"port": 65536},
    {"port": "9001"},
    {"port": 1.5},
    {"port": None},
)


@pytest.mark.parametrize(
    ("data", "error", "section_problem"),
    [
        *[(payload(value), None, True) for value in INVALID_SECTIONS],
        *[(value, None, False) for value in (b"{", b"[]", b"null", b"{}", b'{"schema":"other"}', b"\xff")],
        (None, "cannot be read", False),
    ],
)
def test_invalid_settings_disable_only_the_integration(
    data: bytes | None, error: str | None, section_problem: bool
) -> None:
    from spec_dock.runtime.domain.orca_web import parse_orca_web

    result = parse_orca_web(data, read_error=error)
    assert (result.enabled, result.port, result.section_problem) == (False, 8791, section_problem)
    assert result.problem
    if section_problem:
        assert result.problem.startswith("orca_web")


def test_origin_uses_admitted_host_and_rejects_its_own_port() -> None:
    from spec_dock.runtime.domain.orca_web import OrcaWebSettings, orca_web_origin, parse_orca_web

    assert orca_web_origin(OrcaWebSettings(), "LOCALHOST", 47800) == {
        "enabled": True,
        "origin": "http://localhost:8791",
        "port": 8791,
        "problem": None,
    }
    assert orca_web_origin(OrcaWebSettings(False, 9001), "192.0.2.10", 47800) == {
        "enabled": False,
        "origin": None,
        "port": 9001,
        "problem": None,
    }
    assert orca_web_origin(OrcaWebSettings(True, 47800), "127.0.0.1", 47800) == {
        "enabled": False,
        "origin": None,
        "port": 47800,
        "problem": "orca_web.port must differ from the dashboard's own port 47800",
    }
    invalid = parse_orca_web(payload({"port": 0}))
    assert orca_web_origin(invalid, "127.0.0.1", 47800)["problem"] == invalid.problem
    for port in (1, 65535):
        assert parse_orca_web(payload({"port": port})) == OrcaWebSettings(True, port)
