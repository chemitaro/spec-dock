"""The screens stay out of orca-web's writes (iss-00593 T-07, D-07)."""

from __future__ import annotations

from pathlib import Path
import re

DASHBOARD = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard"
WRITES = ("/api/token", "/api/send/", "/api/open", "/api/settings")
SANDBOX = "allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"


def _orca_files() -> list[Path]:
    globs = ("core/orca*.js", "views/_shared/orca_*.js", "views/_shared/agents_*.js")
    return sorted({path for pattern in globs for path in DASHBOARD.glob(pattern)})


def test_the_orca_and_agents_files_name_no_write_path_and_no_post_message() -> None:
    files = _orca_files()
    names = {path.relative_to(DASHBOARD).as_posix() for path in files}
    assert {"views/_shared/agents_logic.js", "views/_shared/agents_tab.js", "core/orca.js"} <= names
    for path in files:
        text = path.read_text(encoding="utf-8")
        for word in (*WRITES, "postMessage"):
            assert word not in text, f"{path.name}: {word}"


def test_post_message_is_only_the_embed_notice_to_the_parent() -> None:
    found = [
        (path.relative_to(DASHBOARD).as_posix(), line.strip())
        for path in sorted(DASHBOARD.rglob("*.js"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if "postMessage" in line
    ]
    assert len(found) == 1
    assert found[0][0] == "core/embed.js" and found[0][1].startswith("window.parent.postMessage(")


def test_the_agent_frame_sandbox_is_the_designed_one() -> None:
    logic = (DASHBOARD / "views/_shared/agents_logic.js").read_text(encoding="utf-8")
    match = re.search(r'export const AGENT_SANDBOX = "([^"]*)";', logic)
    assert match is not None and match.group(1) == SANDBOX
    assert "allow-top-navigation" not in match.group(1) and "allow-forms" not in match.group(1)
    tab = (DASHBOARD / "views/_shared/agents_tab.js").read_text(encoding="utf-8")
    assert 'sandbox="${AGENT_SANDBOX}"' in tab and " allow=" not in tab
