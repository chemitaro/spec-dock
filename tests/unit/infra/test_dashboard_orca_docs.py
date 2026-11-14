"""The shipped reference explains the orca-web integration (iss-00592 T-05)."""

from __future__ import annotations

import ipaddress
from pathlib import Path
import re

REFERENCE = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/docs/reference_cli.md"
TAILNET = ipaddress.ip_network("100.64.0.0/10")


def test_reference_documents_the_orca_web_section_defaults_and_prerequisites() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert "**orca-web との連携**" in text
    assert '"orca_web": {"enabled": true, "port": 8791}' in text
    assert "`enabled: true`、`port: 8791`" in text
    assert "ORCA_WEB_READ_ORIGINS" in text
    assert "config_problems" in text
    assert "印もボタンも出ず、図とボードは今までどおり動きます" in text
    assert "幅390px以下と`?embed=1`の画面には出ません" in text


def test_reference_names_no_real_tailscale_address() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    for found in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
        try:
            address = ipaddress.ip_address(found)
        except ValueError:
            continue
        assert address not in TAILNET, found
