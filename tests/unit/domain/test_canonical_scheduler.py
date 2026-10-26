"""Choosing the periodic mechanism and the job files it installs (Epic ch. 5, iss-00430)."""

from __future__ import annotations

from pathlib import Path
import plistlib

import pytest

from spec_dock.runtime.domain.canonical_scheduler import (
    LAUNCHD_LABEL,
    SchedulerSpec,
    launchd_plist,
    recorded_head,
    restart_line,
    select_scheduler,
    systemd_quote,
    systemd_units,
)

SPEC = SchedulerSpec(
    executable=Path("/opt/tools/spec-dock/bin/spec-dock"),
    state_root=Path("/home/u/.local/state/spec-dock"),
    git_dir=Path("/opt/homebrew/bin"),
    home=Path("/home/u"),
)


@pytest.mark.parametrize(
    ("system", "present", "user", "previous", "expected"),
    [
        ("darwin", None, None, None, "launchd"),
        ("linux", True, True, None, "systemd"),
        ("linux", True, False, None, "loop"),
        ("linux", False, None, None, "loop"),
        ("linux", True, True, "loop", "loop"),
        ("linux", False, None, "systemd", "loop"),
        ("darwin", None, None, "loop", "launchd"),
    ],
)
def test_the_scheduler_is_chosen_in_the_epic_order_and_kept_while_usable(
    system: str, present: bool | None, user: bool | None, previous: str | None, expected: str
) -> None:
    chosen = select_scheduler(system, systemd_present=present, systemd_user=user, previous=previous)  # type: ignore[arg-type]
    assert chosen == expected


def test_the_launchd_job_runs_registered_sync_every_60_seconds_with_the_recorded_root() -> None:
    plist = plistlib.loads(launchd_plist(SPEC, label=LAUNCHD_LABEL))
    assert plist == {
        "Label": "io.github.chemitaro.spec-dock.canonical-sync",
        "ProgramArguments": [
            "/opt/tools/spec-dock/bin/spec-dock",
            "canonical",
            "sync",
            "--registered",
            "--state-root",
            "/home/u/.local/state/spec-dock",
        ],
        "WorkingDirectory": "/home/u",
        "StartInterval": 60,
        "RunAtLoad": True,
        "StandardOutPath": "/home/u/.local/state/spec-dock/canonical-sync.log",
        "StandardErrorPath": "/home/u/.local/state/spec-dock/canonical-sync.log",
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
    }


def test_the_systemd_units_follow_the_epic_shape() -> None:
    service, timer = systemd_units(SPEC)
    assert service == (
        "[Unit]\n"
        "Description=SpecDock canonical sync\n"
        "[Service]\n"
        "Type=oneshot\n"
        "WorkingDirectory=%h\n"
        "Environment=PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin\n"
        "ExecStart=/opt/tools/spec-dock/bin/spec-dock canonical sync --registered --state-root "
        "/home/u/.local/state/spec-dock\n"
    )
    assert timer == (
        "[Unit]\n"
        "Description=SpecDock canonical sync timer\n"
        "[Timer]\n"
        "OnActiveSec=10s\n"
        "OnUnitActiveSec=60s\n"
        "AccuracySec=5s\n"
        "[Install]\n"
        "WantedBy=timers.target\n"
    )


def test_systemd_values_escape_percent_and_quote_spaces() -> None:
    assert systemd_quote("/a/b") == "/a/b"
    assert systemd_quote("/a/100%") == "/a/100%%"
    assert systemd_quote('/my dir/x"y\\z') == '"/my dir/x\\"y\\\\z"'
    spaced = SchedulerSpec(Path("/My Tools/spec-dock"), Path("/s 1"), Path("/g%"), Path("/h"))
    service, _timer = systemd_units(spaced)
    assert 'ExecStart="/My Tools/spec-dock" canonical sync --registered --state-root "/s 1"\n' in service
    assert "Environment=PATH=/g%%:/usr/local/bin:/usr/bin:/bin\n" in service


def test_the_restart_line_starts_a_detached_runner_with_the_recorded_root() -> None:
    assert restart_line(Path("/s/spec dock")) == (
        "spec-dock canonical sync --registered --loop --detach --state-root '/s/spec dock'"
    )


def test_the_job_path_adds_the_gh_directory_after_git() -> None:
    spec = SchedulerSpec(SPEC.executable, SPEC.state_root, Path("/usr/bin"), SPEC.home, gh_dir=Path("/opt/gh/bin"))
    plist = plistlib.loads(launchd_plist(spec))
    assert plist["EnvironmentVariables"] == {"PATH": "/usr/bin:/opt/gh/bin:/usr/bin:/bin:/usr/sbin:/sbin"}
    service, _timer = systemd_units(spec)
    assert "Environment=PATH=/usr/bin:/opt/gh/bin:/usr/local/bin:/usr/bin:/bin\n" in service
    same = SchedulerSpec(
        SPEC.executable, SPEC.state_root, Path("/opt/homebrew/bin"), SPEC.home, Path("/opt/homebrew/bin")
    )
    assert plistlib.loads(launchd_plist(same))["EnvironmentVariables"]["PATH"].count("/opt/homebrew/bin") == 1


def test_an_unknown_user_manager_keeps_a_previous_systemd_choice() -> None:
    assert select_scheduler("linux", systemd_present=True, systemd_user=None, previous="systemd") == "systemd"
    assert select_scheduler("linux", systemd_present=True, systemd_user=None, previous=None) == "loop"
    assert select_scheduler("linux", systemd_present=False, systemd_user=None, previous="systemd") == "loop"
    assert systemd_quote("/a/$HOME", command=True) == "/a/$$HOME" and systemd_quote("/a/$HOME") == "/a/$HOME"


@pytest.mark.parametrize(
    ("search_path", "head"),
    [
        ("/opt/git/bin:/usr/bin:/bin", ["/opt/git/bin"]),
        ("/opt/git/bin:/opt/gh/bin:/usr/bin:/bin", ["/opt/git/bin", "/opt/gh/bin"]),
        ("/usr/bin:/usr/bin:/bin", ["/usr/bin"]),  # git in /usr/bin, gh beside it
        ("/usr/bin:/bin", []),
        ("/opt/git/bin:/usr/local/bin:/usr/bin", None),  # another tail: written by another version
    ],
)
def test_recorded_head_reads_only_what_comes_before_the_fixed_tail(search_path: str, head: list[str] | None) -> None:
    assert recorded_head(search_path, "/usr/bin:/bin") == head
