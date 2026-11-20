"""Judge the one tool-setting line each tool needs to reach the catalog; settings files are only read (R-B6)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import (
    CANONICAL_TOOL_SETTING_MISSING,
    CANONICAL_TOOL_SETTING_UNKNOWN,
)
from spec_dock.runtime.domain.canonical_tools import (
    ANTIGRAVITY_USER_SETTINGS_FILE,
    CLAUDE_CONFIG_DIR,
    CODEX_CONFIG_FILE,
    CODEX_SECTION,
    antigravity_allows,
    antigravity_setting_line,
    antigravity_user_settings,
    claude_allows,
    claude_setting_line,
    claude_user_settings,
    codex_setting_line,
)
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
    from collections.abc import Sequence

    from spec_dock.runtime.domain.canonical_layout import CatalogLayout
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment


def tool_findings(
    layout: CatalogLayout, environment: RuntimeEnvironment
) -> tuple[dict[str, object], tuple[Diagnostic, ...]]:
    """The `tools` status item and one warning per missing or unjudgeable setting; the main checkout needs none."""
    catalog = layout.catalog
    warnings: list[Diagnostic] = []
    codex: dict[str, object] = {
        "sandbox": environment.codex_sandbox,
        "writable": None,
        "needed": False,
        "file": CODEX_CONFIG_FILE,
        "section": CODEX_SECTION,
        "line": None,
    }
    if environment.codex_sandbox and not layout.is_main and _is_directory(catalog):
        writable = os.access(catalog, os.W_OK)
        codex["writable"] = writable
        if not writable:
            line = codex_setting_line(catalog)
            codex.update(needed=True, line=line)
            warnings.append(
                Diagnostic(
                    CANONICAL_TOOL_SETTING_MISSING,
                    f"Codex cannot write the catalog from this sandbox; add this line under {CODEX_SECTION} "
                    f"in {CODEX_CONFIG_FILE}: {line}",
                    {
                        "item": "tools",
                        "tool": "codex",
                        "file": CODEX_CONFIG_FILE,
                        "section": CODEX_SECTION,
                        "line": line,
                        "next_step": line,
                    },
                )
            )
    user_settings, user_settings_file = claude_user_settings(environment.environ, environment.home)
    claude: dict[str, object] = {
        "session": environment.claude_code,
        "needed": not layout.is_main,
        "configured": None,
        "sources": [],
        "file": user_settings_file,
        "line": None,
    }
    if not layout.is_main:
        payloads = _claude_settings(layout.checkout, user_settings)
        if user_settings is None and environment.environ.get(CLAUDE_CONFIG_DIR):
            payloads.insert(0, (Path(user_settings_file), None))  # a relative CLAUDE_CONFIG_DIR cannot be read
        claude["sources"] = [str(source) for source, _payload in payloads]
        configured = claude_allows(
            payloads,
            Path(os.path.realpath(catalog)),
            home=environment.home,
            resolve=lambda path: Path(os.path.realpath(path)),
        )
        claude["configured"] = configured
        if configured is False:
            line = claude_setting_line(catalog)
            claude["line"] = line
            warnings.append(
                Diagnostic(
                    CANONICAL_TOOL_SETTING_MISSING,
                    "Claude Code reads the specs of this linked worktree only through an additional directory; "
                    f"add this to {user_settings_file}: {line}",
                    {
                        "item": "tools",
                        "tool": "claude_code",
                        "file": user_settings_file,
                        "line": line,
                        "next_step": line,
                    },
                )
            )
        elif configured is None:
            step = f"Check that {user_settings_file} lists {catalog} in permissions.additionalDirectories."
            warnings.append(
                Diagnostic(
                    CANONICAL_TOOL_SETTING_UNKNOWN,
                    f"Could not judge whether Claude Code allows the catalog. {step}",
                    {"item": "tools", "tool": "claude_code", "sources": claude["sources"], "next_step": step},
                )
            )
    antigravity, antigravity_warning = _antigravity_findings(layout, environment)
    if antigravity_warning is not None:
        warnings.append(antigravity_warning)
    preferred_warning = antigravity_warning or (warnings[0] if warnings else None)
    item: dict[str, object] = {
        "status": "problem" if warnings else "ok",
        "next_step": preferred_warning.details["next_step"] if preferred_warning is not None else None,
        "codex": codex,
        "claude_code": claude,
        "antigravity": antigravity,
    }
    return item, tuple(warnings)


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(path.stat().st_mode)
    except OSError:
        return False


def _claude_settings(checkout: Path, user_settings: Path | None) -> list[tuple[Path, object]]:
    sources = [user_settings] if user_settings is not None else []
    sources += [checkout / ".claude/settings.json", checkout / ".claude/settings.local.json"]
    return _settings_payloads(sources)


def _settings_payloads(sources: Sequence[Path]) -> list[tuple[Path, object]]:
    payloads: list[tuple[Path, object]] = []
    for source in sources:
        try:
            text = source.read_text(encoding="utf-8")
        except (FileNotFoundError, NotADirectoryError):
            continue
        except (OSError, UnicodeDecodeError):
            payloads.append((source, None))
            continue
        try:
            payloads.append((source, json.loads(text)))
        except json.JSONDecodeError:
            payloads.append((source, None))
    return payloads


def _antigravity_findings(
    layout: CatalogLayout, environment: RuntimeEnvironment
) -> tuple[dict[str, object], Diagnostic | None]:
    file = ANTIGRAVITY_USER_SETTINGS_FILE
    item: dict[str, object] = {
        "session": environment.antigravity,
        "needed": not layout.is_main,
        "configured": None,
        "sources": [],
        "file": file,
        "line": None,
    }
    if layout.is_main:
        return item, None

    settings = antigravity_user_settings(environment.home)
    payloads = _settings_payloads([settings]) if settings is not None else [(Path(file), None)]
    sources = [str(source) for source, _payload in payloads]
    payload = payloads[0][1] if payloads else {}
    configured = antigravity_allows(
        payload, Path(os.path.realpath(layout.catalog)), resolve=lambda path: Path(os.path.realpath(path))
    )
    line = antigravity_setting_line(layout.catalog) if configured is False else None
    item.update(configured=configured, sources=sources, line=line)
    if not environment.antigravity or configured is True:
        return item, None
    if configured is None:
        step = (
            f"Check that {file} allows read_file({layout.catalog}) and write_file({layout.catalog}) "
            "in permissions.allow, and that no permissions.deny or permissions.ask rule covers the catalog."
        )
        return item, Diagnostic(
            CANONICAL_TOOL_SETTING_UNKNOWN,
            f"Could not judge whether Antigravity allows the catalog. {step}",
            {"item": "tools", "tool": "antigravity", "sources": sources, "next_step": step},
        )
    return item, Diagnostic(
        CANONICAL_TOOL_SETTING_MISSING,
        "Antigravity reads and writes the specs of this linked worktree only with an allow rule; "
        f"add this to {file}: {line}",
        {"item": "tools", "tool": "antigravity", "file": file, "line": line, "next_step": line},
    )
