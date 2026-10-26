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
    CLAUDE_USER_SETTINGS_FILE,
    CODEX_CONFIG_FILE,
    CODEX_SECTION,
    claude_allows,
    claude_setting_line,
    codex_setting_line,
)
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
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
    claude: dict[str, object] = {
        "session": environment.claude_code,
        "needed": not layout.is_main,
        "configured": None,
        "sources": [],
        "file": CLAUDE_USER_SETTINGS_FILE,
        "line": None,
    }
    if not layout.is_main:
        payloads = _claude_settings(layout.checkout, environment.home)
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
                    f"add this to {CLAUDE_USER_SETTINGS_FILE}: {line}",
                    {
                        "item": "tools",
                        "tool": "claude_code",
                        "file": CLAUDE_USER_SETTINGS_FILE,
                        "line": line,
                        "next_step": line,
                    },
                )
            )
        elif configured is None:
            step = f"Check that {CLAUDE_USER_SETTINGS_FILE} lists {catalog} in permissions.additionalDirectories."
            warnings.append(
                Diagnostic(
                    CANONICAL_TOOL_SETTING_UNKNOWN,
                    f"Could not judge whether Claude Code allows the catalog. {step}",
                    {"item": "tools", "tool": "claude_code", "sources": claude["sources"], "next_step": step},
                )
            )
    item: dict[str, object] = {
        "status": "problem" if warnings else "ok",
        "next_step": warnings[0].details["next_step"] if warnings else None,
        "codex": codex,
        "claude_code": claude,
    }
    return item, tuple(warnings)


def _is_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(path.stat().st_mode)
    except OSError:
        return False


def _claude_settings(checkout: Path, home: Path | None) -> list[tuple[Path, object]]:
    sources = [home / ".claude/settings.json"] if home is not None else []
    sources += [checkout / ".claude/settings.json", checkout / ".claude/settings.local.json"]
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
