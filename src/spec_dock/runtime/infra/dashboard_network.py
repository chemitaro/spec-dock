"""This PC's Tailscale address and MagicDNS name, read with the local `tailscale` command (Epic D-02).

Only local commands run (`tailscale ip -4`, `tailscale status --json`); the Tailscale configuration is never
changed and Tailscale Serve is not used. Tests replace the probe.
"""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
from pathlib import Path
import shutil
import subprocess
from typing import Final, Protocol

_MAC_APP: Final = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"


class TailscaleProbe(Protocol):
    def ipv4(self) -> str | None: ...

    def dns_name(self) -> str | None: ...


def _executable() -> str | None:
    found = shutil.which("tailscale")
    if found:
        return found
    return _MAC_APP if Path(_MAC_APP).is_file() else None


@dataclass(frozen=True)
class LocalTailscale:
    timeout: float = 5.0

    def _run(self, *argv: str) -> str | None:
        executable = _executable()
        if executable is None:
            return None
        try:
            completed = subprocess.run(
                [executable, *argv], capture_output=True, text=True, timeout=self.timeout, check=False
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return completed.stdout if completed.returncode == 0 else None

    def ipv4(self) -> str | None:
        output = self._run("ip", "-4")
        for line in (output or "").splitlines():
            value = line.strip()
            try:
                address = ipaddress.IPv4Address(value)
            except ValueError:
                continue
            if address in ipaddress.IPv4Network("100.64.0.0/10"):
                return value
        return None

    def dns_name(self) -> str | None:
        output = self._run("status", "--json")
        try:
            status = json.loads(output or "")
        except ValueError:
            return None
        name = status.get("Self", {}).get("DNSName") if isinstance(status, dict) else None
        if not isinstance(name, str) or not name.strip(".") or any(c in name for c in "/:\\ "):
            return None
        return name.rstrip(".").lower()
