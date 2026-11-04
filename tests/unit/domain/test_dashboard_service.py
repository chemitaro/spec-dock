"""The dashboard service's job files (iss-00530 D-01, T-01)."""

from __future__ import annotations

from pathlib import Path
import plistlib

from spec_dock.runtime.domain.dashboard_service import (
    DASHBOARD_LAUNCHD_LABEL,
    DashboardServiceSpec,
    ServiceSettings,
    dashboard_launchd_plist,
    dashboard_systemd_unit,
    service_settings,
)

STATE = Path("/home/u/.local/state/spec-dock")


def _spec(**changes: object) -> DashboardServiceSpec:
    values: dict[str, object] = {
        "executable": Path("/opt/tools/bin/spec-dock"),
        "state_root": STATE,
        "git_dir": Path("/opt/homebrew/bin"),
        "home": Path("/home/u"),
        "port": 47800,
        "tailscale": False,
        "tailscale_dir": None,
    }
    values.update(changes)
    return DashboardServiceSpec(**values)  # type: ignore[arg-type]


def test_launchd_plist_keeps_the_server_alive_with_the_service_arguments() -> None:
    document = plistlib.loads(dashboard_launchd_plist(_spec(tailscale=True, tailscale_dir=Path("/usr/local/bin"))))

    assert document["Label"] == DASHBOARD_LAUNCHD_LABEL == "io.github.chemitaro.spec-dock.dashboard"
    assert document["ProgramArguments"] == [
        "/opt/tools/bin/spec-dock",
        "dashboard",
        "serve",
        "--service",
        "--port",
        "47800",
        "--tailscale",
        "--state-root",
        str(STATE),
    ]
    assert document["KeepAlive"] is True
    assert document["RunAtLoad"] is True
    assert document["ThrottleInterval"] == 10
    assert "StartInterval" not in document
    assert document["StandardOutPath"] == document["StandardErrorPath"] == str(STATE / "dashboard/service.log")
    assert document["EnvironmentVariables"] == {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }
    assert document["WorkingDirectory"] == "/home/u"


def test_systemd_unit_restarts_always_and_logs_to_the_journal() -> None:
    unit = dashboard_systemd_unit(_spec(port=47801, state_root=Path("/home/u/my state/spec-dock")))

    lines = unit.splitlines()
    assert "Type=simple" in lines
    assert "Restart=always" in lines
    assert "RestartSec=10" in lines
    assert "WantedBy=default.target" in lines
    assert "[Timer]" not in unit
    assert (
        'ExecStart=/opt/tools/bin/spec-dock dashboard serve --service --port 47801 --state-root "/home/u/my state/spec-dock"'
        in lines
    )
    assert "StandardOutput" not in unit  # the journal keeps the output; append: paths take no quoting
    assert "Environment=PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" in lines


def test_service_settings_reads_back_the_recorded_arguments() -> None:
    spec = _spec(port=47805, tailscale=True)

    assert service_settings(spec.arguments()) == ServiceSettings(47805, True, STATE)
    assert service_settings(_spec().arguments()) == ServiceSettings(47800, False, STATE)
    assert service_settings(["/x/spec-dock", "canonical", "sync", "--registered"]) is None
    assert service_settings(["/x/spec-dock", "dashboard", "serve", "--service", "--port", "nope"]) is None
    assert service_settings([]) is None


def test_the_settings_directory_of_the_install_reaches_the_server() -> None:
    """The server reads the same `$XDG_CONFIG_HOME/spec-dock/config.json` as the CLI that installed it (iss-00552)."""
    spec = _spec(config_home=Path("/home/u/my config"))
    document = plistlib.loads(dashboard_launchd_plist(spec))
    assert document["EnvironmentVariables"]["XDG_CONFIG_HOME"] == "/home/u/my config"
    assert 'Environment="XDG_CONFIG_HOME=/home/u/my config"' in dashboard_systemd_unit(spec).splitlines()
    assert "XDG_CONFIG_HOME" not in plistlib.loads(dashboard_launchd_plist(_spec()))["EnvironmentVariables"]
    assert "XDG_CONFIG_HOME" not in dashboard_systemd_unit(_spec())
