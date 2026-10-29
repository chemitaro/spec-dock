"""The shared SpecDock runner shell helpers behave as the runner VMs rely on (iss-00463)."""

from __future__ import annotations

import hashlib
import os
import subprocess
from typing import TYPE_CHECKING

from tests.support.canonical_check import provider_root

if TYPE_CHECKING:
    from pathlib import Path

PROVIDER = provider_root()
RUNNER = PROVIDER / ".github/runner"


def _sh(script: str, *arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run a /bin/sh snippet that has sourced lib.sh, with positional arguments."""
    return subprocess.run(
        ["/bin/sh", "-c", f'. "{RUNNER / "lib.sh"}"\n{script}', "sh", *arguments],
        env=os.environ | (env or {}),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _source(tmp_path: Path, content: bytes) -> tuple[str, str]:
    source = tmp_path / "source.tar.gz"
    source.write_bytes(content)
    return source.as_uri(), hashlib.sha256(content).hexdigest()


def test_fetch_verified_replaces_a_corrupt_cached_file(tmp_path: Path) -> None:
    url, digest = _source(tmp_path, b"good archive")
    cached = tmp_path / "cache/archive.tar.gz"
    cached.parent.mkdir()
    cached.write_bytes(b"truncated")
    completed = _sh('fetch_verified "$1" "$2" "$3"', url, str(cached), digest)
    assert completed.returncode == 0, completed.stderr
    assert cached.read_bytes() == b"good archive"


def test_fetch_verified_keeps_nothing_when_the_download_does_not_match(tmp_path: Path) -> None:
    url, _ = _source(tmp_path, b"tampered archive")
    cached = tmp_path / "archive.tar.gz"
    completed = _sh('fetch_verified "$1" "$2" "$3"', url, str(cached), "0" * 64)
    assert completed.returncode != 0 and "SHA256" in completed.stderr
    assert not cached.exists() and not (tmp_path / "archive.tar.gz.part").exists()


def test_set_env_lines_replaces_a_changed_value_and_reports_only_a_change(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("LANG=C.UTF-8\nAGENT_TOOLSDIRECTORY=/old\n", encoding="utf-8")
    setting = (
        "AGENT_TOOLSDIRECTORY=/opt/hostedtoolcache",
        "ACTIONS_RUNNER_HOOK_JOB_STARTED=/opt/spec-dock-ci/job-started.sh",
    )
    first = _sh('set_env_lines "$@"', str(env_file), *setting)
    assert first.returncode == 0, first.stderr
    assert first.stdout == "changed\n"
    assert env_file.read_text(encoding="utf-8").splitlines() == ["LANG=C.UTF-8", *setting]
    again = _sh('set_env_lines "$@"', str(env_file), *setting)
    assert again.returncode == 0 and again.stdout == ""
    assert env_file.read_text(encoding="utf-8").splitlines() == ["LANG=C.UTF-8", *setting]


def test_set_env_lines_creates_a_missing_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    completed = _sh('set_env_lines "$@"', str(env_file), "A=1")
    assert completed.returncode == 0 and completed.stdout == "changed\n"
    assert env_file.read_text(encoding="utf-8") == "A=1\n"


def _copy(tmp_path: Path) -> Path:
    copy = tmp_path / "spec-dock-runner"
    copy.parent.mkdir(exist_ok=True)
    copy.mkdir(mode=0o700)
    for name in ("guest-setup.sh", "settings.sh"):
        (copy / name).write_text("#", encoding="utf-8")
        (copy / name).chmod(0o644)
    return copy


def test_require_private_copy_accepts_a_copy_only_its_owner_can_write(tmp_path: Path) -> None:
    completed = _sh('require_private_copy "$1" "$2"', str(_copy(tmp_path)), str(os.getuid()))
    assert completed.returncode == 0, completed.stderr


def test_require_private_copy_refuses_a_copy_others_could_have_replaced(tmp_path: Path) -> None:
    writable = _copy(tmp_path / "writable")
    (writable / "settings.sh").chmod(0o664)
    linked = _copy(tmp_path / "linked")
    (linked / "lib.sh").symlink_to(writable / "settings.sh")
    for copy, owner in ((writable, os.getuid()), (linked, os.getuid()), (_copy(tmp_path / "foreign"), 54321)):
        completed = _sh('require_private_copy "$1" "$2"', str(copy), str(owner))
        assert completed.returncode == 1 and "refusing to run from" in completed.stderr


def test_check_root_tree_reports_entries_that_are_not_roots_alone(tmp_path: Path) -> None:
    (tmp_path / "tool").mkdir()
    completed = _sh('check_root_tree "$1"', str(tmp_path))
    assert completed.returncode == 1 and str(tmp_path / "tool") in completed.stderr
    assert _sh('check_root_tree "$1"', "/bin").returncode == 0


TOKEN = "AAAATESTREGISTRATIONTOKEN"


def _stub(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(0o755)


def _prepare_registration(tmp_path: Path, script: str) -> Path:
    """Copy a register-runner.sh with stub sudo, config.sh and service tools that log their arguments."""
    log = tmp_path / "log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # The stub sudo drops "-u USER" and runs the rest, recording only its own arguments.
    _stub(bin_dir / "sudo", f'echo "sudo $*" >> "{log}"\n[ "$1" = -u ] && shift 2\nexec "$@"\n')
    for tool in ("systemctl", "launchctl"):
        _stub(bin_dir / tool, f'echo "{tool} $*" >> "{log}"\n')
    root = tmp_path / "opt"
    root.mkdir()
    home = tmp_path / "home"
    copy = root / "register-runner.sh"
    copy.write_text((RUNNER / script).read_text(encoding="utf-8"), encoding="utf-8")
    settings = ((RUNNER / script).parent / "settings.sh").read_text(encoding="utf-8")
    (root / "settings.sh").write_text(settings + f'\nRUNNER_HOME="{home}"\n', encoding="utf-8")
    users = subprocess.run(
        ["/bin/sh", "-c", f'. "{root / "settings.sh"}"; echo $RUNNER_USERS'], capture_output=True, text=True, check=True
    ).stdout.split()
    for user in users:
        runner = home / user / "actions-runner"
        runner.mkdir(parents=True)
        _stub(
            runner / "config.sh",
            f'echo "config.sh $* token=${{ACTIONS_RUNNER_INPUT_TOKEN:+set}}" >> "{log}"\n'
            f'[ "$ACTIONS_RUNNER_INPUT_TOKEN" = "{TOKEN}" ] && touch .runner\n',
        )
    return copy


def _register(tmp_path: Path, copy: Path, stdin: str) -> tuple[subprocess.CompletedProcess[str], str]:
    log = tmp_path / "log"
    log.unlink(missing_ok=True)
    completed = subprocess.run(
        ["/bin/sh", str(copy)],
        input=stdin,
        env=os.environ | {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    return completed, log.read_text(encoding="utf-8") if log.exists() else ""


def test_register_runner_passes_the_token_only_through_a_pipe(tmp_path: Path) -> None:
    completed, log = _register(tmp_path, _prepare_registration(tmp_path, "register-runner.sh"), TOKEN + "\n")
    assert completed.returncode == 0, completed.stderr
    assert log.count("token=set") == 2 and log.count("systemctl enable --now") == 2
    assert TOKEN not in log + completed.stdout + completed.stderr


def test_register_runner_can_run_again_without_registering_twice(tmp_path: Path) -> None:
    copy = _prepare_registration(tmp_path, "register-runner.sh")
    assert _register(tmp_path, copy, TOKEN + "\n")[0].returncode == 0
    # The runners exist now, so a second run needs no token and only makes sure the services run.
    again, log = _register(tmp_path, copy, "")
    assert again.returncode == 0, again.stderr
    assert "config.sh" not in log and log.count("systemctl enable --now") == 2


def test_register_runner_refuses_to_register_without_a_token(tmp_path: Path) -> None:
    completed, log = _register(tmp_path, _prepare_registration(tmp_path, "register-runner.sh"), "")
    assert completed.returncode == 1 and "no registration token" in completed.stderr and "config.sh" not in log


def _host_install(tmp_path: Path, script: Path, *arguments: str) -> tuple[subprocess.CompletedProcess[str], str]:
    """Run a Mac-side install script with HOME in tmp_path and stub launchctl, plutil and curl."""
    log = tmp_path / "log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for tool in ("launchctl", "plutil"):
        _stub(bin_dir / tool, f'echo "{tool} $*" >> "{log}"\n')
    _stub(bin_dir / "curl", f'echo "curl $*" >> "{log}"\nexit 22\n')
    (tmp_path / "home").mkdir(exist_ok=True)
    completed = subprocess.run(
        ["/bin/sh", str(script), *arguments],
        env=os.environ | {"HOME": str(tmp_path / "home"), "PATH": f"{bin_dir}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    return completed, log.read_text(encoding="utf-8") if log.exists() else ""


def test_the_linux_vm_agent_installs_into_a_fresh_home_and_keeps_the_vm_when_its_job_ends(tmp_path: Path) -> None:
    completed, log = _host_install(tmp_path, RUNNER / "host-install.sh", "agent")
    assert completed.returncode == 0, completed.stderr
    plist = (tmp_path / "home/Library/LaunchAgents/com.chemitaro.spec-dock-ci-vm.plist").read_text(encoding="utf-8")
    # launchd would otherwise kill what the job started, including the Lima host agent, when the job exits (T-6).
    assert "<key>AbandonProcessGroup</key><true/>" in plist
    assert "launchctl bootstrap gui/" in log


def test_a_failed_lima_download_leaves_nothing_behind(tmp_path: Path) -> None:
    completed, _ = _host_install(tmp_path, RUNNER / "host-install.sh", "lima")
    assert completed.returncode != 0
    assert not (tmp_path / "home/Library/Application Support/spec-dock-ci-vm/lima").exists()
