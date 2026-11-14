"""orca-web settings and origins; independent of repository visibility (iss-00591)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from spec_dock.runtime.domain.dashboard_visibility import _document
from spec_dock.runtime.domain.todo_settings import USER_SCHEMA


@dataclass(frozen=True)
class OrcaWebSettings:
    enabled: bool = True
    port: int = 8791
    problem: str | None = None
    section_problem: bool = False


def parse_orca_web(payload: bytes | None, *, read_error: str | None = None) -> OrcaWebSettings:
    """A missing file or section enables the defaults; unreadable input disables integration."""
    if read_error is not None:
        return OrcaWebSettings(False, problem=read_error)
    if payload is None:
        return OrcaWebSettings()
    try:
        document = _document(payload)
        if not isinstance(document, dict) or document.get("schema") != USER_SCHEMA:
            raise ValueError(f"schema must be {USER_SCHEMA}")
    except ValueError as error:
        return OrcaWebSettings(False, problem=str(error))
    if "orca_web" not in document:
        return OrcaWebSettings()
    section = document["orca_web"]
    if not isinstance(section, dict):
        return OrcaWebSettings(False, problem="orca_web must be an object", section_problem=True)
    unknown = set(section) - {"enabled", "port"}
    if unknown:
        return OrcaWebSettings(False, problem=f"orca_web.{sorted(unknown)[0]} is unknown", section_problem=True)
    enabled, port = section.get("enabled", True), section.get("port", 8791)
    if not isinstance(enabled, bool):
        return OrcaWebSettings(False, problem="orca_web.enabled must be true or false", section_problem=True)
    if type(port) is not int or not 1 <= port <= 65535:
        return OrcaWebSettings(False, problem="orca_web.port must be an integer from 1 to 65535", section_problem=True)
    return OrcaWebSettings(enabled, port)


class OrcaWebOrigin(TypedDict):
    enabled: bool
    origin: str | None
    port: int
    problem: str | None


def orca_web_origin(settings: OrcaWebSettings, host_name: str, own_port: int) -> OrcaWebOrigin:
    """Build an origin only from a host name already admitted by the HTTP server."""
    problem = settings.problem
    enabled = settings.enabled
    if enabled and settings.port == own_port:
        enabled = False
        problem = f"orca_web.port must differ from the dashboard's own port {own_port}"
    return {
        "enabled": enabled,
        "origin": f"http://{host_name.lower()}:{settings.port}" if enabled else None,
        "port": settings.port,
        "problem": None if enabled else problem,
    }
