"""`spec-dock dashboard service install`, `status` and `uninstall` (iss-00530 D-03; Epic D-01, D-14, R-28).

The service exists only after the user runs `install`: launchd on macOS, a systemd user service on Linux with
a user manager. It is separate from the periodic sync job (its own label and file), records the same
executable as the sync job while that one still works, and `uninstall` leaves nothing behind (job file and
service log). None of them contacts GitHub or the server.
"""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.application.dashboard_commands import stop_on_schema_three
from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
from spec_dock.runtime.domain.dashboard_service import DEFAULT_SERVICE_PORT, SERVICE_LOG, DashboardServiceSpec
from spec_dock.runtime.infra import canonical_scheduling, dashboard_service, runtime_environment
from spec_dock.runtime.infra.canonical_registry import RegistryUnreadable, read_registry
from spec_dock.runtime.infra.dashboard_files import pid_alive
from spec_dock.runtime.infra.dashboard_store import dashboard_dir, read_server_record
from spec_dock.runtime.infra.state_root import resolve_state_root
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Effect, OperationResult

if TYPE_CHECKING:
    import argparse

    from spec_dock.runtime.infra.dashboard_service import DashboardService, ServiceKind
    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment

DASHBOARD_SERVICE_UNSUPPORTED = "DASHBOARD_SERVICE_UNSUPPORTED"
DASHBOARD_SERVICE_FAILED = "DASHBOARD_SERVICE_FAILED"
SERVE_INSTEAD = "spec-dock dashboard serve"


def detect_environment() -> RuntimeEnvironment:
    """This PC's platform and, on Linux, its systemd user manager; tests replace it."""
    environment = runtime_environment.detect_runtime_environment()
    return runtime_environment.detect_service_manager(environment)


def service_kind(environment: RuntimeEnvironment) -> ServiceKind | None:
    """launchd on macOS, systemd with a working user manager on Linux; otherwise no service (serve instead)."""
    if environment.system == "darwin":
        return "launchd"
    if environment.systemd_present and environment.systemd_user:
        return "systemd"
    return None


def _installed_kind(environment: RuntimeEnvironment) -> ServiceKind | None:
    """The manager to inspect or remove from: also systemd when its user manager is unknown now but the unit exists.

    `systemctl --user` can be unreachable for a while (right after boot, under su); an installed unit must
    still be visible and removable then (the removal's systemctl failure is reported, not hidden).
    """
    kind = service_kind(environment)
    if (
        kind is None
        and environment.system == "linux"
        and dashboard_service.dashboard_service_for("systemd", environment=environment).path.exists()
    ):
        return "systemd"
    return kind


def _home(environment: RuntimeEnvironment) -> Path:
    return environment.home or Path.home()


def _probe(root: Path, environment: RuntimeEnvironment) -> DashboardServiceSpec:
    return DashboardServiceSpec(Path("/"), root, Path("/"), _home(environment))


def _result(command: str, data: dict[str, object], effects: tuple[Effect, ...] = ()) -> OperationResult[object]:
    return OperationResult(command, "succeeded", FamilyData("dashboard", data), 0, effects=effects)


def _failed(error: canonical_scheduling.SchedulerError, path: Path) -> CanonicalCommandError:
    return CanonicalCommandError(
        DASHBOARD_SERVICE_FAILED,
        str(error),
        recovery=("spec-dock dashboard service install", "spec-dock dashboard service uninstall"),
        details={"path": str(path)},
    )


# --- install -----------------------------------------------------------------------------------------------------


def _executable(kind: ServiceKind, root: Path, environment: RuntimeEnvironment) -> Path:
    """The sync job's executable while it still runs (one Full Disk Access grant for both); else this spec-dock."""
    try:
        registry = read_registry(root)
    except (RegistryUnreadable, OSError):
        registry = None
    if registry is not None and registry.scheduler == kind:
        scheduler = canonical_scheduling.scheduler_for(kind, state_root=root, environment=environment)
        recorded = scheduler.recorded_executable(SchedulerSpec(Path("/"), root, Path("/"), _home(environment)))
        if canonical_scheduling.usable_executable(recorded):
            assert recorded is not None
            return recorded
    return canonical_scheduling.spec_dock_executable()


def _git_dir(root: Path, environment: RuntimeEnvironment) -> Path:
    try:
        catalogs = read_registry(root).catalogs
    except (RegistryUnreadable, OSError):
        catalogs = ()
    for entry in catalogs:
        if entry.git and Path(entry.git).is_absolute():
            return Path(entry.git).parent
    found = shutil.which("git", path=environment.environ.get("PATH", ""))
    return Path(found).parent if found else Path("/usr/bin")


def _tailscale_dir(environment: RuntimeEnvironment) -> Path | None:
    found = shutil.which("tailscale", path=environment.environ.get("PATH", ""))
    return Path(found).parent if found else None


def install(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]:
    stop_on_schema_three(namespace, cwd)
    command = namespace.command_path
    port = namespace.port if namespace.port is not None else DEFAULT_SERVICE_PORT
    if not 1 <= port <= 65535:
        raise CanonicalCommandError(
            "DASHBOARD_PORT_INVALID", f"{port} is not a port number from 1 to 65535 for the service", exit_code=2
        )
    environment = detect_environment()
    kind = service_kind(environment)
    if kind is None:
        raise CanonicalCommandError(
            DASHBOARD_SERVICE_UNSUPPORTED,
            "this PC has no launchd and no working systemd user manager, so no service is installed",
            recovery=(SERVE_INSTEAD,),
        )
    root = resolve_state_root()
    service = dashboard_service.dashboard_service_for(kind, environment=environment)
    try:
        spec = DashboardServiceSpec(
            _executable(kind, root, environment),
            root,
            _git_dir(root, environment),
            _home(environment),
            port=port,
            tailscale=bool(namespace.tailscale),
            tailscale_dir=_tailscale_dir(environment),
            config_home=_config_home(environment),
        )
        dashboard_dir(root).mkdir(parents=True, exist_ok=True)  # launchd does not create the log's directory
        outcome = service.ensure(spec)
    except canonical_scheduling.SchedulerError as error:
        raise _failed(error, service.path) from None
    data: dict[str, object] = {
        "scheduler": kind,
        "path": str(service.path),
        "outcome": outcome,
        "port": port,
        "tailscale": bool(namespace.tailscale),
        "state_root": str(root),
        "executable": str(spec.executable),
        "url": f"http://127.0.0.1:{port}/",
        "log": str(spec.log) if kind == "launchd" else None,
    }
    effect = Effect("dashboard.service", "unchanged" if outcome == "unchanged" else "succeeded", str(service.path))
    return _result(command, data, (effect,))


# --- status ------------------------------------------------------------------------------------------------------


def _server(root: Path) -> dict[str, object] | None:
    record = read_server_record(root)
    if record is None:
        return None
    pid = record.get("pid")
    if type(pid) is not int or pid <= 0 or not pid_alive(pid):
        return None
    return {key: record.get(key) for key in ("pid", "urls", "version", "started_at")}


def status(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]:
    stop_on_schema_three(namespace, cwd)
    environment = detect_environment()
    kind = _installed_kind(environment)
    root = resolve_state_root()
    package = dashboard_service.installed_version()
    data: dict[str, object] = {
        "supported": service_kind(environment) is not None,
        "scheduler": kind,
        "path": None,
        "installed": False,
        "loaded": None,
        "detail": None,
        "port": None,
        "tailscale": None,
        "state_root": None,
        "package_version": package,
    }
    record_root = root
    if kind is not None:
        service: DashboardService = dashboard_service.dashboard_service_for(kind, environment=environment)
        observation = service.observe(_probe(root, environment))
        settings = service.recorded_settings()
        data.update(path=str(service.path), installed=bool(observation.installed), loaded=observation.active)
        data["detail"] = observation.detail
        if settings is not None:
            data.update(port=settings.port, tailscale=settings.tailscale)
            data["state_root"] = str(settings.state_root) if settings.state_root else None
            record_root = settings.state_root or root
    server = _server(record_root)
    data["server"] = server
    data["running"] = server is not None
    running_version = server.get("version") if server else None
    data["restart_pending"] = bool(server and package and running_version and running_version != package)
    return _result(namespace.command_path, data)


# --- uninstall ---------------------------------------------------------------------------------------------------


def uninstall(namespace: argparse.Namespace, cwd: Path) -> OperationResult[object]:
    stop_on_schema_three(namespace, cwd)
    command = namespace.command_path
    environment = detect_environment()
    kind = _installed_kind(environment)
    root = resolve_state_root()
    if kind is None:
        return _result(command, {"scheduler": None, "removed": False, "path": None, "log_removed": False})
    service = dashboard_service.dashboard_service_for(kind, environment=environment)
    settings = service.recorded_settings()
    log = ((settings.state_root if settings and settings.state_root else None) or root) / SERVICE_LOG
    try:
        removed = service.remove(_probe(root, environment))
    except canonical_scheduling.SchedulerError as error:
        raise _failed(error, service.path) from None
    log_removed = log.is_file()
    log.unlink(missing_ok=True)
    data: dict[str, object] = {
        "scheduler": kind,
        "removed": removed,
        "path": str(service.path),
        "log_removed": log_removed,
    }
    effect = Effect("dashboard.service", "succeeded" if removed else "unchanged", str(service.path))
    return _result(command, data, (effect,))


def _config_home(environment: RuntimeEnvironment) -> Path | None:
    """The absolute XDG_CONFIG_HOME of this install, which the server must read its settings under (iss-00552)."""
    value = environment.environ.get("XDG_CONFIG_HOME", "")
    return Path(value) if value and Path(value).is_absolute() else None
