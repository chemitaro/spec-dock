from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

import pytest

from tests.unit.infra.test_init_update import TestInitUpdate as _Issue69Harness

_WORKBENCH_TEMPLATE_READMES = (
    "README.md",
    "root/.workbench/README.md",
    "initiative/.workbench/README.md",
    "epic/.workbench/README.md",
    "issue/.workbench/README.md",
)
_REQUIRED_WHEEL_ASSETS = (
    "spec_dock/assets/spec_dock/scripts/spec-dock",
    "spec_dock/assets/spec_dock/docs/README.md",
    "spec_dock/assets/spec_dock/templates/root/.workbench/README.md",
)
_STALE_WHEEL_PATTERNS = (
    "spec_dock/assets/spec_dock/scripts/spec-dock-close*.sh",
    "spec_dock/assets/github/workflows/spec-dock-close.yml",
    "spec_dock/assets/spec_dock/templates/**/current/**",
    "spec_dock/assets/spec_dock/templates/**/completed/**",
    "spec_dock/assets/spec_dock/templates/adr.md",
    "spec_dock/assets/spec_dock/templates/**/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
    "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
    "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
    "spec_dock/assets/spec_dock/templates/design.md",
    "spec_dock/assets/spec_dock/templates/plan.md",
    "spec_dock/assets/spec_dock/templates/report.md",
    "spec_dock/assets/spec_dock/templates/requirement.md",
)
_S04_MANAGED_PROJECTION_ROOTS = ("docs", "templates", "scripts", "system")
# The clean candidate checkout already contains the current docs and provider
# projection, so update should not create a tracked status delta.
_S04_UPDATE_EXPECTED_STATUS: set[str] = set()


@dataclass(frozen=True)
class CandidateWheel:
    repo_root: Path
    wheel_path: Path
    sdist_path: Path
    venv_python: Path
    pre_head: str
    post_head: str
    pre_status: str
    post_status: str
    inventory: frozenset[str]
    sha256: str


FileSnapshot = tuple[tuple[str, bytes], ...]
PayloadState = tuple[bool, bytes | None, bool, str]

_FILE_IMPORT_PUBLIC_KEYS = {
    "status",
    "import_kind",
    "storage_identity",
    "target_kind",
    "target_id",
    "artifact_id",
    "source_visibility",
    "source",
    "destination",
    "committed",
    "publication_state",
    "cleanup_state",
    "warning_codes",
    "retry_disposition",
    "canonical",
}


@dataclass(frozen=True)
class ExistingConsumer:
    target: Path
    env: dict[str, str]
    installed_cli: Path
    existing_readmes: tuple[Path, ...]
    existing_nodes: tuple[Path, ...]
    payload_path: Path
    payload_body: bytes
    payload_before: PayloadState
    guide_path: Path
    guide_stale: bytes
    guide_asset: bytes
    canonical_before: FileSnapshot
    existing_scope_before: FileSnapshot
    graph_before: FileSnapshot
    managed_before: FileSnapshot


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


def _assert_candidate_inventory(inventory: set[str]) -> None:
    required = {
        *_REQUIRED_WHEEL_ASSETS,
        *(f"spec_dock/assets/spec_dock/templates/{path}" for path in _WORKBENCH_TEMPLATE_READMES),
    }
    missing = sorted(required - inventory)
    assert not missing, f"candidate wheel is missing required assets: {missing}"

    template_prefix = "spec_dock/assets/spec_dock/templates/"
    observed_template_readmes = {
        path.removeprefix(template_prefix)
        for path in inventory
        if path.startswith(template_prefix) and Path(path).name == "README.md"
    }
    assert observed_template_readmes == set(_WORKBENCH_TEMPLATE_READMES), (
        f"candidate wheel template README allowlist mismatch: {sorted(observed_template_readmes)}"
    )

    stale = sorted(
        path
        for path in inventory
        if "__pycache__" in path
        or path.endswith((".pyc", ".pyo"))
        or any(fnmatch.fnmatch(path, pattern) for pattern in _STALE_WHEEL_PATTERNS)
    )
    assert not stale, f"candidate wheel contains denied stale assets: {stale}"


@pytest.fixture(scope="module")
def candidate_wheel(tmp_path_factory: pytest.TempPathFactory) -> CandidateWheel:
    repo_root = Path(__file__).resolve().parents[2]
    helper = _Issue69Harness()
    pre_head = _git(repo_root, "rev-parse", "HEAD")
    pre_status = _git(repo_root, "status", "--porcelain=v1")

    temp_root = tmp_path_factory.mktemp("iss346-s01-candidate")
    build_context = temp_root / "build-context"
    wheel_dir = temp_root / "wheelhouse"
    sdist_dir = temp_root / "sdist"
    helper._issue_69_prepare_build_context(repo_root, build_context)
    wheel_path, sdist_path, venv_python = helper._issue_69_build_artifacts_with_local_wheelhouse(
        repo_root=repo_root,
        build_context=build_context,
        wheel_dir=wheel_dir,
        sdist_dir=sdist_dir,
    )
    install_wheel = wheel_path
    install_wheel_sha256 = hashlib.sha256(install_wheel.read_bytes()).hexdigest()
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=helper._issue_69_site_packages_dir(helper._issue_69_env_root(venv_python)),
        requirements=[str(install_wheel)],
        wheelhouse=helper._issue_69_resolve_wheelhouse(repo_root),
    )
    helper._issue_69_ensure_spec_dock_wrapper(venv_python)

    post_head = _git(repo_root, "rev-parse", "HEAD")
    post_status = _git(repo_root, "status", "--porcelain=v1")
    inventory = frozenset(helper._issue_69_collect_wheel_file_inventory(wheel_path))
    digest = hashlib.sha256(install_wheel.read_bytes()).hexdigest()
    assert digest == install_wheel_sha256
    return CandidateWheel(
        repo_root=repo_root,
        wheel_path=wheel_path,
        sdist_path=sdist_path,
        venv_python=venv_python,
        pre_head=pre_head,
        post_head=post_head,
        pre_status=pre_status,
        post_status=post_status,
        inventory=inventory,
        sha256=install_wheel_sha256,
    )


def _provider_asset_manifest(repo_root: Path) -> dict[str, tuple[bytes, int]]:
    source_root = repo_root / "src/spec_dock/assets"
    manifest: dict[str, tuple[bytes, int]] = {}
    for path in source_root.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        relative = path.relative_to(source_root).as_posix()
        package_path = f"spec_dock/assets/{relative}"
        template_prefix = "spec_dock/templates/"
        if relative.startswith(template_prefix) and path.name == "README.md":
            template_relative = relative.removeprefix(template_prefix)
            if template_relative not in _WORKBENCH_TEMPLATE_READMES:
                continue
        if any(fnmatch.fnmatch(package_path, pattern) for pattern in _STALE_WHEEL_PATTERNS):
            continue
        manifest[package_path] = (path.read_bytes(), path.stat().st_mode & 0o777)
    return manifest


def _wheel_asset_manifest(path: Path) -> dict[str, tuple[bytes, int]]:
    with zipfile.ZipFile(path) as archive:
        return {
            member.filename: (archive.read(member), (member.external_attr >> 16) & 0o777)
            for member in archive.infolist()
            if member.filename.startswith("spec_dock/assets/") and not member.is_dir()
        }


def _sdist_asset_manifest(path: Path) -> dict[str, tuple[bytes, int]]:
    manifest: dict[str, tuple[bytes, int]] = {}
    marker = "/src/spec_dock/assets/"
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or marker not in member.name:
                continue
            package_path = f"spec_dock/assets/{member.name.split(marker, 1)[1]}"
            extracted = archive.extractfile(member)
            assert extracted is not None
            manifest[package_path] = (extracted.read(), member.mode & 0o777)
    return manifest


def _install_candidate_artifact(candidate: CandidateWheel, artifact: Path, environment_root: Path) -> Path:
    helper = _Issue69Harness()
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(environment_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    venv_python = helper._issue_69_venv_python(environment_root)
    wheelhouse = helper._issue_69_resolve_wheelhouse(candidate.repo_root)
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=helper._issue_69_site_packages_dir(environment_root),
        requirements=list(helper._ISSUE_69_BUILD_BACKEND_REQUIREMENTS),
        wheelhouse=wheelhouse,
    )
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=helper._issue_69_site_packages_dir(environment_root),
        requirements=[str(artifact)],
        wheelhouse=wheelhouse,
    )
    return helper._issue_69_ensure_spec_dock_wrapper(venv_python)


def _expected_installed_asset_manifest(repo_root: Path) -> dict[str, tuple[bytes, int]]:
    expected: dict[str, tuple[bytes, int]] = {}
    for package_path, identity in _provider_asset_manifest(repo_root).items():
        install_prefix = "spec_dock/assets/install_root/"
        scaffold_prefix = "spec_dock/assets/spec_dock/"
        if package_path.startswith(install_prefix):
            expected[package_path.removeprefix(install_prefix)] = identity
        elif package_path.startswith(scaffold_prefix):
            target_path = f"spec-dock/{package_path.removeprefix(scaffold_prefix)}"
            payload, mode = identity
            if target_path.startswith("spec-dock/system/active-none/"):
                mode = 0o444
            expected[target_path] = (payload, mode)
    return expected


def _assert_installed_asset_manifest(target: Path, expected: dict[str, tuple[bytes, int]]) -> None:
    mode_mismatches: list[tuple[str, int, int]] = []
    for relative_path, (payload, mode) in expected.items():
        observed = target / relative_path
        assert observed.is_file() and not observed.is_symlink(), f"installed asset is missing: {relative_path}"
        assert observed.read_bytes() == payload, f"installed asset bytes differ: {relative_path}"
        observed_mode = observed.stat().st_mode & 0o777
        if observed_mode != mode:
            mode_mismatches.append((relative_path, mode, observed_mode))
    assert not mode_mismatches, f"installed asset modes differ: {mode_mismatches}"


def _runtime_env(helper: _Issue69Harness, temp_root: Path) -> dict[str, str]:
    env = helper._issue_69_runtime_env_without_checkout_fallback()
    gh_bin = temp_root / "gh-bin"
    gh_bin.mkdir(parents=True, exist_ok=True)
    helper._make_default_gh_issue_list_stub(gh_bin)
    env["PATH"] = f"{gh_bin}{os.pathsep}{env.get('PATH', '')}"
    return env


def _run_installed_runtime(
    venv_python: Path,
    target: Path,
    args: list[str],
    *,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    script = target / "spec-dock" / "scripts" / "spec-dock"
    assert script.is_file(), f"projected runtime script is missing: {script}"
    return subprocess.run(
        [str(venv_python), str(script), *args],
        cwd=target,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_installed_runtime_at_cwd(
    venv_python: Path,
    target: Path,
    cwd: Path,
    args: list[str],
    *,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    script = target / "spec-dock" / "scripts" / "spec-dock"
    assert script.is_file(), f"projected runtime script is missing: {script}"
    return subprocess.run(
        [str(venv_python), str(script), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _find_node(target: Path, node_id: str) -> Path:
    for meta_path in sorted((target / "spec-dock" / "initiatives").rglob(".meta.json")):
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
        if payload.get("id") == node_id:
            return meta_path.parent
    raise AssertionError(f"node not found: {node_id}")


def _write_s03_runtime_clock(target: Path) -> None:
    clock_path = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "clock.py"
    clock_path.write_text(
        (
            "from __future__ import annotations\n\n"
            "def now_iso() -> str:\n    return '2026-07-30T01:02:03+00:00'\n\n"
            "def today() -> str:\n    return '2026-07-30'\n"
        ),
        encoding="utf-8",
    )


def _prepare_s03_consumer(
    candidate_wheel: CandidateWheel,
    suffix: str,
    *,
    hierarchy: bool = True,
) -> tuple[Path, dict[str, str]]:
    helper = _Issue69Harness()
    temp_root = candidate_wheel.wheel_path.parent
    target = temp_root / suffix
    target.mkdir()
    helper._init_origin_repo(target)
    env = _runtime_env(helper, temp_root)
    installed_cli = helper._issue_69_venv_spec_dock(candidate_wheel.venv_python)
    assert installed_cli.is_file()
    init_result = subprocess.run(
        [str(installed_cli), "init", str(target)],
        cwd=temp_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr
    if hierarchy:
        for args in (
            ["new", "initiative", "--title", "S03 platform", "--github-issue", "601"],
            ["new", "epic", "--initiative", "601", "--title", "S03 import", "--github-issue", "612"],
            ["new", "issue", "--epic", "612", "--title", "S03 payload", "--github-issue", "645"],
        ):
            result = _run_installed_runtime(candidate_wheel.venv_python, target, args, env=env)
            assert result.returncode == 0, result.stdout + result.stderr
    _write_s03_runtime_clock(target)
    return target, env


def _assert_s03_json_payload(payload: dict[str, object], *, target_kind: str, target_id: str) -> None:
    assert set(payload) == _FILE_IMPORT_PUBLIC_KEYS
    assert payload["status"] == "ok"
    assert payload["import_kind"] == "file"
    assert payload["storage_identity"] == "generic"
    assert payload["target_kind"] == target_kind
    assert payload["target_id"] == target_id
    assert payload["committed"] is True
    assert payload["publication_state"] in {"committed", "committed_with_warning"}
    assert payload["canonical"] is False


def _s03_privacy_forbidden_values(source: Path, body: bytes) -> tuple[str, ...]:
    body_text = body.decode("ascii", errors="ignore").lower()
    digest = hashlib.sha256(body).hexdigest().lower()
    derived = f"derived-{hashlib.sha1(body).hexdigest()[:16]}"
    return (
        str(source).lower(),
        str(source.parent).lower(),
        source.parent.name.lower(),
        body_text,
        digest,
        derived,
        "sha256",
        "byte_count",
        "mime",
        "encoding",
        "content_id",
    )


def _s03_import_owned_public_files(target: Path, destination: Path) -> tuple[Path, ...]:
    """Return the bounded public/tracked surfaces owned by this import fixture.

    The generic artifact body is deliberately excluded. Canonical docs, planning
    reports, and wheel receipts are outside this oracle's authority boundary.
    """
    public_root = target / "spec-dock" / ".agent"
    paths = {path for path in public_root.rglob("*") if path.is_file()}
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=target,
        capture_output=True,
        check=False,
    )
    assert tracked.returncode == 0, tracked.stdout + tracked.stderr
    paths.update(
        target / relative
        for raw in tracked.stdout.split(b"\0")
        if raw
        for relative in (Path(os.fsdecode(raw)),)
        if (target / relative).is_file()
    )
    return tuple(sorted(path for path in paths if path != destination))


def _flatten_s03_public_values(value: object) -> tuple[str, ...]:
    if isinstance(value, dict):
        return tuple(item for key, nested in value.items() for item in (str(key), *_flatten_s03_public_values(nested)))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(item for nested in value for item in _flatten_s03_public_values(nested))
    return (str(value),)


def _assert_s03_privacy_output(
    output: subprocess.CompletedProcess[str],
    *,
    source: Path,
    body: bytes,
    payload: object | None = None,
    public_files: tuple[Path, ...] = (),
) -> None:
    forbidden = _s03_privacy_forbidden_values(source, body)
    observed = [f"{output.stdout}\n{output.stderr}"]
    if payload is not None:
        observed.extend(_flatten_s03_public_values(payload))
    for path in public_files:
        assert path != source
        assert path.is_file(), f"privacy scan target disappeared: {path}"
        observed.append(path.read_bytes().decode("utf-8", errors="ignore"))
    combined = "\n".join(observed).lower()
    for value in forbidden:
        assert value not in combined, f"privacy sentinel leaked in import public surface: {value!r}"
    assert source.name.lower() in f"{output.stdout}\n{output.stderr}".lower()


def _flatten_s04_scalars(value: object) -> tuple[object, ...]:
    if isinstance(value, dict):
        return tuple(scalar for nested in value.values() for scalar in _flatten_s04_scalars(nested))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(scalar for nested in value for scalar in _flatten_s04_scalars(nested))
    return (value,)


def _assert_s04_dogfood_privacy_output(
    output: subprocess.CompletedProcess[str],
    *,
    checkout: Path,
    source: Path,
    body: bytes,
    payload: dict[str, object],
    destination: Path,
) -> None:
    expected_relative_source = source.relative_to(checkout).as_posix()
    assert payload.get("source") in {expected_relative_source, source.name}
    observed = [f"{output.stdout}\n{output.stderr}"]
    observed.extend(_flatten_s03_public_values(payload))
    public_root = checkout / "spec-dock" / ".agent"
    for path in public_root.rglob("*") if public_root.is_dir() else ():
        if path.is_file() and path != destination:
            observed.append(path.read_bytes().decode("utf-8", errors="ignore"))
    combined = "\n".join(observed).lower()
    digest = hashlib.sha256(body).hexdigest().lower()
    derived = f"derived-{hashlib.sha1(body).hexdigest()[:16]}"
    printable_body = "".join(
        character for character in body.decode("utf-8", errors="ignore") if character.isprintable()
    ).lower()
    count_tokens = (
        f"count={len(body)}",
        f"byte-count={len(body)}",
        f"byte_count={len(body)}",
    )
    forbidden_text = (
        str(checkout.resolve()).lower(),
        str(source.resolve()).lower(),
        str(source.parent.resolve()).lower(),
        body.decode("ascii", errors="ignore").lower(),
        printable_body,
        digest,
        derived,
        "sha256",
        "byte_count",
        "mime",
        "encoding",
        "content_id",
        *count_tokens,
    )
    for sentinel in forbidden_text:
        assert sentinel not in combined, f"dogfood privacy sentinel leaked: {sentinel!r}"
    assert all(scalar != len(body) for scalar in _flatten_s04_scalars(payload))


def _wheel_asset_bytes(candidate_wheel: CandidateWheel, relative_path: str) -> bytes:
    with zipfile.ZipFile(candidate_wheel.wheel_path) as wheel_zip:
        return wheel_zip.read(relative_path)


def _s04_wheel_managed_manifest(candidate_wheel: CandidateWheel) -> dict[str, bytes]:
    prefix = "spec_dock/assets/spec_dock/"
    with zipfile.ZipFile(candidate_wheel.wheel_path) as wheel_zip:
        return {
            member.removeprefix(prefix): wheel_zip.read(member)
            for member in wheel_zip.namelist()
            if member.startswith(prefix)
            and any(member.removeprefix(prefix).startswith(f"{root}/") for root in _S04_MANAGED_PROJECTION_ROOTS)
            and not member.endswith("/")
            and "__pycache__" not in Path(member).parts
            and not member.endswith((".pyc", ".pyo"))
        }


def _s04_projected_managed_manifest(target: Path) -> dict[str, bytes]:
    specdock_dir = target / "spec-dock"
    return {
        path.relative_to(specdock_dir).as_posix(): path.read_bytes()
        for root in _S04_MANAGED_PROJECTION_ROOTS
        for path in (specdock_dir / root).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and not path.name.endswith((".pyc", ".pyo"))
    }


def _assert_s04_provider_projection_parity(candidate_wheel: CandidateWheel, target: Path) -> None:
    expected = _s04_wheel_managed_manifest(candidate_wheel)
    observed = _s04_projected_managed_manifest(target)
    assert set(observed) == set(expected)
    assert observed == expected


def _assert_exact_status_manifest(target: Path, expected: set[str]) -> None:
    assert set(_git_status_paths(target)) == expected


def _snapshot_tree(root: Path, *, include_symlinks: bool = True) -> FileSnapshot:
    if not root.is_dir():
        return ()
    return tuple(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and (include_symlinks or not path.is_symlink())
    )


def _snapshot_existing_scopes(existing_nodes: tuple[Path, ...]) -> FileSnapshot:
    entries: list[tuple[str, bytes]] = []
    for node in existing_nodes:
        for relative_path, payload in _snapshot_tree(node):
            entries.append((f"{node.name}/{relative_path}", payload))
    return tuple(sorted(entries))


def _snapshot_graph(target: Path) -> FileSnapshot:
    specdock_dir = target / "spec-dock"
    entries: list[tuple[str, bytes]] = []
    agent_root = specdock_dir / ".agent"
    if agent_root.is_dir():
        entries.extend(
            (f".agent/{path.relative_to(agent_root).as_posix()}", path.read_bytes())
            for path in sorted(agent_root.rglob("*"))
            if path.is_file()
        )
    for relative_path in (
        "tree-all.puml",
        "tree.puml",
        "deps-issues.puml",
        "deps-raw.puml",
        "dashboard.md",
    ):
        path = specdock_dir / relative_path
        if path.is_file():
            entries.append((relative_path, path.read_bytes()))
    return tuple(sorted(entries))


def _snapshot_managed_assets(target: Path) -> FileSnapshot:
    specdock_dir = target / "spec-dock"
    entries: list[tuple[str, bytes]] = []
    for directory_name in ("docs", "templates", "scripts", "system"):
        root = specdock_dir / directory_name
        entries.extend(
            (f"{directory_name}/{path.relative_to(root).as_posix()}", path.read_bytes())
            for path in sorted(root.rglob("*"))
            if path.is_file()
        )
    for relative_path in (".gitignore", "spec-dock.version"):
        path = specdock_dir / relative_path
        if path.is_file():
            entries.append((relative_path, path.read_bytes()))
    # `_install_skill` applies every provider `install_root` file to these
    # bounded repository-root trees. Keep the update oracle scoped to this
    # managed surface, excluding unrelated root files and canonical specs.
    for directory_name in (".agents", ".codex", ".github"):
        root = target / directory_name
        if not root.is_dir():
            continue
        entries.extend(
            (f"{directory_name}/{path.relative_to(root).as_posix()}", path.read_bytes())
            for path in sorted(root.rglob("*"))
            if path.is_file()
        )
    return tuple(sorted(entries))


def _payload_state(target: Path, payload_path: Path) -> PayloadState:
    relative_path = payload_path.relative_to(target).as_posix()
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", relative_path],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = subprocess.run(
        ["git", "ls-files", "--", relative_path],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tracked.returncode == 0, tracked.stdout + tracked.stderr
    return (
        payload_path.is_file(),
        payload_path.read_bytes() if payload_path.is_file() else None,
        ignored.returncode == 0,
        tracked.stdout.strip(),
    )


def _existing_readme_paths(target: Path) -> tuple[Path, ...]:
    return (
        target / "spec-dock" / ".workbench" / "README.md",
        _find_node(target, "init-00401") / ".workbench" / "README.md",
        _find_node(target, "epic-00402") / ".workbench" / "README.md",
        _find_node(target, "iss-00403") / ".workbench" / "README.md",
    )


def _assert_existing_fixture_preflight(consumer: ExistingConsumer) -> None:
    present = [path.relative_to(consumer.target).as_posix() for path in consumer.existing_readmes if path.exists()]
    assert not present, f"existing consumer fixture has preexisting README: {present}"
    assert consumer.payload_before == (
        True,
        consumer.payload_body,
        True,
        "",
    )
    assert consumer.guide_path.read_bytes() == consumer.guide_stale
    assert consumer.guide_stale != consumer.guide_asset


def _prepare_existing_consumer(candidate_wheel: CandidateWheel, suffix: str) -> ExistingConsumer:
    helper = _Issue69Harness()
    temp_root = candidate_wheel.wheel_path.parent
    target = temp_root / suffix
    target.mkdir()
    helper._init_origin_repo(target)
    env = _runtime_env(helper, temp_root)
    installed_cli = helper._issue_69_venv_spec_dock(candidate_wheel.venv_python)
    assert installed_cli.is_file()

    init_result = subprocess.run(
        [str(installed_cli), "init", str(target)],
        cwd=temp_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr
    for args in (
        ["new", "initiative", "--title", "Existing platform", "--github-issue", "401"],
        ["new", "epic", "--initiative", "401", "--title", "Existing update", "--github-issue", "402"],
        ["new", "issue", "--epic", "402", "--title", "Existing consumer", "--github-issue", "403"],
    ):
        result = _run_installed_runtime(candidate_wheel.venv_python, target, args, env=env)
        assert result.returncode == 0, result.stdout + result.stderr

    existing_nodes = tuple(_find_node(target, node_id) for node_id in ("init-00401", "epic-00402", "iss-00403"))
    existing_readmes = _existing_readme_paths(target)
    for readme in existing_readmes:
        assert readme.is_file(), f"synthetic consumer did not create expected README: {readme}"
        readme.unlink()
        assert not readme.exists()

    payload_path = existing_nodes[-1] / ".workbench" / "s02-opaque.bin"
    payload_body = b"S02 existing ignored payload\x00\xff\n"
    payload_path.write_bytes(payload_body)
    assert payload_path.is_file()

    guide_path = target / "spec-dock" / "docs" / "guide.md"
    guide_asset = _wheel_asset_bytes(candidate_wheel, "spec_dock/assets/spec_dock/docs/guide.md")
    guide_stale = b"# S02 pre-candidate guide fixture\n"
    assert guide_stale != guide_asset
    guide_path.write_bytes(guide_stale)

    preflight_validate = _run_installed_runtime(candidate_wheel.venv_python, target, ["validate"], env=env)
    assert preflight_validate.returncode == 0, preflight_validate.stdout + preflight_validate.stderr
    preflight_sync = _run_installed_runtime(
        candidate_wheel.venv_python,
        target,
        ["sync", "--no-github"],
        env=env,
    )
    assert preflight_sync.returncode == 0, preflight_sync.stdout + preflight_sync.stderr

    consumer = ExistingConsumer(
        target=target,
        env=env,
        installed_cli=installed_cli,
        existing_readmes=existing_readmes,
        existing_nodes=existing_nodes,
        payload_path=payload_path,
        payload_body=payload_body,
        payload_before=_payload_state(target, payload_path),
        guide_path=guide_path,
        guide_stale=guide_stale,
        guide_asset=guide_asset,
        canonical_before=_snapshot_tree(target / "spec-dock" / "initiatives"),
        existing_scope_before=_snapshot_existing_scopes(existing_nodes),
        graph_before=_snapshot_graph(target),
        managed_before=_snapshot_managed_assets(target),
    )
    _assert_existing_fixture_preflight(consumer)
    assert consumer.graph_before
    assert consumer.canonical_before
    return consumer


def _update_existing_consumer(candidate_wheel: CandidateWheel, consumer: ExistingConsumer) -> None:
    update_result = subprocess.run(
        [str(consumer.installed_cli), "update", str(consumer.target)],
        cwd=candidate_wheel.wheel_path.parent,
        env=consumer.env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert update_result.returncode == 0, update_result.stdout + update_result.stderr


def _clone_exact_candidate_checkout(
    candidate_wheel: CandidateWheel,
    suffix: str,
) -> tuple[Path, dict[str, str], Path]:
    checkout = candidate_wheel.wheel_path.parent / suffix
    source_repo = candidate_wheel.repo_root.resolve()
    clone_result = subprocess.run(
        ["git", "clone", "--no-hardlinks", "--no-checkout", str(source_repo), str(checkout)],
        cwd=candidate_wheel.wheel_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert clone_result.returncode == 0, clone_result.stdout + clone_result.stderr
    assert _git(checkout, "checkout", "--detach", candidate_wheel.post_head) == ""
    assert _git(checkout, "remote", "set-url", "origin", "https://github.com/chemitaro/spec-dock.git") == ""
    assert _git(checkout, "rev-parse", "HEAD") == candidate_wheel.post_head
    assert _git(checkout, "status", "--porcelain=v1") == ""
    helper = _Issue69Harness()
    env = _runtime_env(helper, candidate_wheel.wheel_path.parent)
    installed_cli = helper._issue_69_venv_spec_dock(candidate_wheel.venv_python)
    assert installed_cli.is_file()
    return checkout, env, installed_cli


def _epic_00343_readme(target: Path) -> Path:
    return _find_node(target, "epic-00343") / ".workbench" / "README.md"


def _assert_epic_00343_unbackfilled(target: Path) -> None:
    readme = _epic_00343_readme(target)
    assert not readme.exists(), f"existing epic-00343 received a Workbench README: {readme}"


def _next_unused_github_issue_number(target: Path) -> int:
    observed: set[int] = set()
    for meta_path in (target / "spec-dock" / "initiatives").rglob(".meta.json"):
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
        github = payload.get("github")
        if isinstance(github, dict) and isinstance(github.get("issue_number"), int):
            observed.add(int(github["issue_number"]))
    candidate = max(observed, default=0) + 1
    while candidate in observed:
        candidate += 1
    return candidate


def _git_status_paths(target: Path) -> tuple[str, ...]:
    status = _git(target, "status", "--short", "--untracked-files=all")
    paths: list[str] = []
    for line in status.splitlines():
        if len(line) >= 3:
            paths.append(line[2:].strip())
    return tuple(sorted(paths))


def test_tc_346_s01_001_candidate_wheel_receipt(candidate_wheel: CandidateWheel) -> None:
    assert candidate_wheel.pre_head == candidate_wheel.post_head
    assert candidate_wheel.pre_status == candidate_wheel.post_status == ""
    assert candidate_wheel.wheel_path.is_file()
    wheel_name, wheel_version, wheel_tag = candidate_wheel.wheel_path.name.split("-", 2)
    assert wheel_name == "spec_dock"
    version_match = re.search(
        r'(?m)^version\s*=\s*"([^"]+)"\s*$', (candidate_wheel.repo_root / "pyproject.toml").read_text()
    )
    assert version_match is not None
    assert wheel_version == version_match.group(1)
    assert wheel_tag.endswith(".whl")
    assert len(list(candidate_wheel.wheel_path.parent.glob("*.whl"))) == 1
    assert len(candidate_wheel.sha256) == 64
    assert hashlib.sha256(candidate_wheel.wheel_path.read_bytes()).hexdigest() == candidate_wheel.sha256


def test_tc_346_s01_002_candidate_wheel_inventory(candidate_wheel: CandidateWheel) -> None:
    inventory = set(candidate_wheel.inventory)
    _assert_candidate_inventory(inventory)

    missing_readme = "spec_dock/assets/spec_dock/templates/issue/.workbench/README.md"
    assert missing_readme in inventory
    with pytest.raises(AssertionError, match="missing required assets"):
        _assert_candidate_inventory(inventory - {missing_readme})

    forbidden_nested_readme = "spec_dock/assets/spec_dock/templates/issue/legacy/README.md"
    with pytest.raises(AssertionError, match="allowlist mismatch"):
        _assert_candidate_inventory(inventory | {forbidden_nested_readme})

    forbidden_cache = "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/__pycache__/probe.pyc"
    with pytest.raises(AssertionError, match="denied stale assets"):
        _assert_candidate_inventory(inventory | {forbidden_cache})


def test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider(
    candidate_wheel: CandidateWheel,
) -> None:
    expected = _provider_asset_manifest(candidate_wheel.repo_root)

    assert _wheel_asset_manifest(candidate_wheel.wheel_path) == expected
    assert _sdist_asset_manifest(candidate_wheel.sdist_path) == expected


def test_tc_360_s80_wheel_and_sdist_fresh_and_updated_consumers_match_provider(
    candidate_wheel: CandidateWheel,
) -> None:
    expected = _expected_installed_asset_manifest(candidate_wheel.repo_root)
    temp_root = candidate_wheel.wheel_path.parent
    for artifact_kind, artifact in (
        ("wheel", candidate_wheel.wheel_path),
        ("sdist", candidate_wheel.sdist_path),
    ):
        environment_root = temp_root / f"s80-{artifact_kind}-venv"
        command = _install_candidate_artifact(candidate_wheel, artifact, environment_root)
        target = temp_root / f"s80-{artifact_kind}-target"
        target.mkdir()
        init_result = subprocess.run(
            [str(command), "init", str(target)],
            cwd=temp_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert init_result.returncode == 0, init_result.stdout + init_result.stderr
        _assert_installed_asset_manifest(target, expected)

        missing = target / ".github/workflows/ci.yml"
        missing.unlink()
        mode_drift = target / ".agents/skills/spec-dock/SKILL.md"
        mode_drift.chmod(0o600 if (mode_drift.stat().st_mode & 0o777) != 0o600 else 0o644)
        update_result = subprocess.run(
            [str(command), "update", str(target)],
            cwd=temp_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update_result.returncode == 0, update_result.stdout + update_result.stderr
        _assert_installed_asset_manifest(target, expected)


def test_tc_372_m3_wheel_and_sdist_packaged_deprovision_and_purge_preserve_boundary(
    candidate_wheel: CandidateWheel,
) -> None:
    """Packaged public uninstall routes preserve the accepted consumer boundary."""

    helper = _Issue69Harness()
    temp_root = candidate_wheel.wheel_path.parent
    for artifact_kind, artifact, existing_venv_python in (
        ("wheel", candidate_wheel.wheel_path, candidate_wheel.venv_python),
        ("sdist", candidate_wheel.sdist_path, None),
    ):
        environment_root = temp_root / f"m3-{artifact_kind}-venv"
        if existing_venv_python is None:
            installed_cli = _install_candidate_artifact(candidate_wheel, artifact, environment_root)
            venv_python = helper._issue_69_venv_python(environment_root)
        else:
            venv_python = existing_venv_python
            installed_cli = helper._issue_69_ensure_spec_dock_wrapper(venv_python)
        isolated_cwd = temp_root / f"m3-{artifact_kind}-isolated-cwd"
        isolated_cwd.mkdir()
        snapshot = helper._issue_69_collect_isolated_installed_runtime_snapshot(
            venv_python=venv_python,
            repo_root=candidate_wheel.repo_root,
            cwd=isolated_cwd,
        )
        helper._issue_69_assert_runtime_snapshot_uses_installed_package(
            snapshot=snapshot,
            repo_root=candidate_wheel.repo_root,
        )
        env = _runtime_env(helper, temp_root)

        keep_target = temp_root / f"m3-{artifact_kind}-keep"
        keep_target.mkdir()
        helper._init_origin_repo(keep_target)
        init_result = subprocess.run(
            [str(installed_cli), "init", str(keep_target)],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert init_result.returncode == 0, init_result.stdout + init_result.stderr
        keep_workbench = keep_target / "spec-dock" / ".workbench"
        keep_readme = keep_workbench / "README.md"
        keep_readme_before = keep_readme.read_bytes()
        keep_payload = keep_workbench / "m3-opaque.bin"
        keep_payload_bytes = b"M3 keep-specs payload\x00\xff\n"
        keep_payload.write_bytes(keep_payload_bytes)
        keep_marker = keep_target / "spec-dock" / "initiatives" / "m3-keep-marker.txt"
        keep_marker_bytes = b"M3 preserved spec history\n"
        keep_marker.write_bytes(keep_marker_bytes)

        keep_result = subprocess.run(
            [
                str(installed_cli),
                "uninstall",
                str(keep_target),
                "--json",
                "--apply",
                "--keep-specs",
            ],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert keep_result.returncode == 0, keep_result.stdout + keep_result.stderr
        assert keep_result.stderr == ""
        assert keep_result.stdout.count("\n") == 1
        keep_payload_json = json.loads(keep_result.stdout)
        assert keep_payload_json["status"] == "completed"
        assert keep_payload_json["specs_mode"] == "keep"
        keep_actions = {str(action["path"]): action for action in keep_payload_json["actions"]}
        assert keep_actions["spec-dock/initiatives"]["status"] == "preserved"
        assert keep_actions["spec-dock/initiatives"]["category"] == "spec_history"
        assert keep_marker.read_bytes() == keep_marker_bytes
        assert keep_readme.read_bytes() == keep_readme_before
        assert keep_payload.read_bytes() == keep_payload_bytes
        assert keep_workbench.is_dir()
        assert not (keep_target / ".agents" / "skills" / "spec-dock" / "SKILL.md").exists()
        assert not (keep_target / "spec-dock" / "scripts" / "spec-dock").exists()
        assert not (keep_target / "spec-dock" / ".uninstall-retry.json").exists()

        purge_target = temp_root / f"m3-{artifact_kind}-purge"
        purge_target.mkdir()
        helper._init_origin_repo(purge_target)
        init_result = subprocess.run(
            [str(installed_cli), "init", str(purge_target)],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert init_result.returncode == 0, init_result.stdout + init_result.stderr
        purge_workbench = purge_target / "spec-dock" / ".workbench"
        purge_readme = purge_workbench / "README.md"
        purge_readme_before = purge_readme.read_bytes()
        purge_payload = purge_workbench / "m3-opaque.bin"
        purge_payload_bytes = b"M3 remove-specs payload\x00\xff\n"
        purge_payload.write_bytes(purge_payload_bytes)
        purge_marker = purge_target / "spec-dock" / "initiatives" / "m3-purge-marker.txt"
        purge_marker.write_bytes(b"M3 removed spec history\n")

        purge_result = subprocess.run(
            [
                str(installed_cli),
                "uninstall",
                str(purge_target),
                "--json",
                "--apply",
                "--remove-specs",
            ],
            cwd=temp_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert purge_result.returncode == 0, purge_result.stdout + purge_result.stderr
        assert purge_result.stderr == ""
        assert purge_result.stdout.count("\n") == 1
        purge_payload_json = json.loads(purge_result.stdout)
        assert purge_payload_json["status"] == "completed"
        assert purge_payload_json["specs_mode"] == "remove"
        purge_actions = {str(action["path"]): action for action in purge_payload_json["actions"]}
        purge_history_action = purge_actions["spec-dock/initiatives"]
        assert purge_history_action["category"] == "spec_history"
        assert purge_history_action["error"] is None
        assert "remove-specs" in str(purge_history_action["reason"])
        assert purge_history_action["status"] == "removed"
        assert not purge_marker.exists()
        assert not (purge_target / "spec-dock" / "initiatives").exists()
        assert purge_readme.read_bytes() == purge_readme_before
        assert purge_payload.read_bytes() == purge_payload_bytes
        assert purge_workbench.is_dir()
        assert purge_target.joinpath("spec-dock").is_dir()
        assert not (purge_target / ".agents" / "skills" / "spec-dock" / "SKILL.md").exists()
        assert not (purge_target / "spec-dock" / "scripts" / "spec-dock").exists()
        assert not (purge_target / "spec-dock" / ".uninstall-retry.json").exists()


def test_tc_346_s01_003_isolated_wheel_origin_rejects_checkout_fallback(candidate_wheel: CandidateWheel) -> None:
    helper = _Issue69Harness()
    isolated_cwd = candidate_wheel.wheel_path.parent / "isolated-cwd"
    isolated_cwd.mkdir()

    snapshot = helper._issue_69_collect_isolated_installed_runtime_snapshot(
        venv_python=candidate_wheel.venv_python,
        repo_root=candidate_wheel.repo_root,
        cwd=isolated_cwd,
    )
    helper._issue_69_assert_runtime_snapshot_uses_installed_package(
        snapshot=snapshot,
        repo_root=candidate_wheel.repo_root,
    )

    source_env = helper._issue_69_runtime_env_without_checkout_fallback()
    source_env["PYTHONPATH"] = str(candidate_wheel.repo_root / "src")
    source_probe = subprocess.run(
        [str(candidate_wheel.venv_python), "-c", "import spec_dock; print(spec_dock.__file__)"],
        cwd=isolated_cwd,
        env=source_env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert source_probe.returncode == 0, source_probe.stdout + source_probe.stderr
    assert str(candidate_wheel.repo_root / "src") in source_probe.stdout
    with pytest.raises(AssertionError, match="expected installed package module path"):
        helper._issue_69_assert_runtime_snapshot_uses_installed_package(
            snapshot={
                "spec_dock_file": source_probe.stdout.strip(),
                "assets_dir": str(candidate_wheel.repo_root / "src" / "spec_dock" / "assets"),
                "sys_path_has_repo_root": True,
            },
            repo_root=candidate_wheel.repo_root,
        )


def test_tc_346_s01_004_fresh_consumer_installed_shell_and_generic_import(candidate_wheel: CandidateWheel) -> None:
    helper = _Issue69Harness()
    temp_root = candidate_wheel.wheel_path.parent
    target = temp_root / "fresh-consumer"
    target.mkdir()
    helper._init_origin_repo(target)
    env = _runtime_env(helper, temp_root)
    installed_cli = helper._issue_69_venv_spec_dock(candidate_wheel.venv_python)
    assert installed_cli.is_file()

    init_result = subprocess.run(
        [str(installed_cli), "init", str(target)],
        cwd=temp_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert init_result.returncode == 0, init_result.stdout + init_result.stderr

    for args in (
        ["new", "initiative", "--title", "Auth platform", "--github-issue", "301"],
        ["new", "epic", "--initiative", "301", "--title", "Explicit import", "--github-issue", "312"],
        ["new", "issue", "--epic", "312", "--title", "Generic file", "--github-issue", "345"],
    ):
        result = _run_installed_runtime(candidate_wheel.venv_python, target, args, env=env)
        assert result.returncode == 0, result.stdout + result.stderr

    template_root = candidate_wheel.repo_root / "src" / "spec_dock" / "assets" / "spec_dock" / "templates"
    canonical_readme = (template_root / "root" / ".workbench" / "README.md").read_bytes()
    node_ids = ("init-00301", "epic-00312", "iss-00345")
    scope_paths = [target / "spec-dock" / ".workbench"]
    scope_paths.extend(_find_node(target, node_id) / ".workbench" for node_id in node_ids)
    for workbench in scope_paths:
        assert (workbench / "README.md").read_bytes() == canonical_readme

    issue_workbench = scope_paths[-1]
    source = issue_workbench / "opaque.bin"
    body = b"S01 opaque bytes\x00\xff"
    source.write_bytes(body)
    source_rel = source.relative_to(target).as_posix()
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", source_rel],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ignored.returncode == 0, ignored.stdout + ignored.stderr

    import_result = _run_installed_runtime(
        candidate_wheel.venv_python,
        target,
        ["artifact", "import", "file", "--issue", "iss-00345", "--file", source_rel, "--json"],
        env=env,
    )
    assert import_result.returncode == 0, import_result.stdout + import_result.stderr
    payload = json.loads(import_result.stdout)
    assert payload["canonical"] is False
    assert payload["target_kind"] == "issue"
    assert payload["source"] == source_rel
    destination = target / payload["destination"]
    assert destination.is_file()
    assert destination.read_bytes() == body
    assert source.read_bytes() == body

    validate_result = _run_installed_runtime(candidate_wheel.venv_python, target, ["validate"], env=env)
    assert validate_result.returncode == 0, validate_result.stdout + validate_result.stderr

    assert source.is_file()
    assert source.read_bytes() == body
    assert destination.is_file()
    assert destination.read_bytes() == body
    ignored_after_validate = subprocess.run(
        ["git", "check-ignore", "--no-index", source_rel],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ignored_after_validate.returncode == 0, ignored_after_validate.stdout + ignored_after_validate.stderr
    tracked_source = subprocess.run(
        ["git", "ls-files", "--", source_rel],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tracked_source.returncode == 0, tracked_source.stdout + tracked_source.stderr
    assert tracked_source.stdout.strip() == ""

    private_paths = (str(target.resolve()), str(source.resolve()))
    for output_name, output in (
        ("import stdout", import_result.stdout),
        ("import stderr", import_result.stderr),
        ("validate stdout", validate_result.stdout),
        ("validate stderr", validate_result.stderr),
    ):
        for private_path in private_paths:
            assert private_path not in output, f"{output_name} leaked private path: {private_path}"


def test_tc_346_s02_001_existing_consumer_fixture_is_valid_without_readmes(
    candidate_wheel: CandidateWheel,
) -> None:
    consumer = _prepare_existing_consumer(candidate_wheel, "s02-existing-001")

    _assert_existing_fixture_preflight(consumer)
    assert all(not path.exists() for path in consumer.existing_readmes)
    assert consumer.payload_before == (True, consumer.payload_body, True, "")
    assert consumer.guide_path.read_bytes() == consumer.guide_stale
    assert consumer.guide_stale != consumer.guide_asset
    assert consumer.canonical_before
    assert consumer.graph_before


def test_tc_346_s02_002_existing_consumer_update_preserves_data_without_backfill(
    candidate_wheel: CandidateWheel,
) -> None:
    consumer = _prepare_existing_consumer(candidate_wheel, "s02-existing-002")
    update_result = subprocess.run(
        [str(consumer.installed_cli), "update", str(consumer.target)],
        cwd=candidate_wheel.wheel_path.parent,
        env=consumer.env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert update_result.returncode == 1
    assert "spec-dock/docs/guide.md: unknown-current-collision" in update_result.stderr
    assert all(not path.exists() for path in consumer.existing_readmes)
    assert _payload_state(consumer.target, consumer.payload_path) == consumer.payload_before
    assert _snapshot_tree(consumer.target / "spec-dock" / "initiatives") == consumer.canonical_before
    assert _snapshot_graph(consumer.target) == consumer.graph_before
    assert consumer.guide_path.read_bytes() == consumer.guide_stale
    assert _snapshot_managed_assets(consumer.target) == consumer.managed_before


def test_tc_346_s02_003_existing_consumer_future_nodes_receive_workbench_shell(
    candidate_wheel: CandidateWheel,
) -> None:
    consumer = _prepare_existing_consumer(candidate_wheel, "s02-existing-003")
    consumer.guide_path.write_bytes(consumer.guide_asset)
    _update_existing_consumer(candidate_wheel, consumer)

    for args in (
        ["new", "initiative", "--title", "Future platform", "--github-issue", "501"],
        ["new", "epic", "--initiative", "501", "--title", "Future update", "--github-issue", "502"],
        ["new", "issue", "--epic", "502", "--title", "Future consumer", "--github-issue", "503"],
    ):
        result = _run_installed_runtime(candidate_wheel.venv_python, consumer.target, args, env=consumer.env)
        assert result.returncode == 0, result.stdout + result.stderr

    future_readmes = (
        (_find_node(consumer.target, "init-00501") / ".workbench" / "README.md", "initiative"),
        (_find_node(consumer.target, "epic-00502") / ".workbench" / "README.md", "epic"),
        (_find_node(consumer.target, "iss-00503") / ".workbench" / "README.md", "issue"),
    )
    for readme, scope in future_readmes:
        assert readme.read_bytes() == _wheel_asset_bytes(
            candidate_wheel,
            f"spec_dock/assets/spec_dock/templates/{scope}/.workbench/README.md",
        )
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", readme.relative_to(consumer.target).as_posix()],
            cwd=consumer.target,
            capture_output=True,
            text=True,
            check=False,
        )
        assert ignored.returncode == 1, ignored.stdout + ignored.stderr
        status = subprocess.run(
            ["git", "status", "--short", "--untracked-files=all"],
            cwd=consumer.target,
            capture_output=True,
            text=True,
            check=False,
        )
        assert status.returncode == 0, status.stdout + status.stderr
        assert f"?? {readme.relative_to(consumer.target).as_posix()}" in status.stdout

    assert all(not path.exists() for path in consumer.existing_readmes)
    assert _payload_state(consumer.target, consumer.payload_path) == consumer.payload_before
    assert _snapshot_existing_scopes(consumer.existing_nodes) == consumer.existing_scope_before


def test_tc_346_s02_004_existing_consumer_illegal_preexisting_readme_is_rejected(
    candidate_wheel: CandidateWheel,
) -> None:
    consumer = _prepare_existing_consumer(candidate_wheel, "s02-existing-004")
    illegal_readme = consumer.existing_readmes[-1]
    illegal_readme.write_bytes(b"preexisting README fixture\n")
    relative_path = illegal_readme.relative_to(consumer.target).as_posix()

    with pytest.raises(AssertionError, match=re.escape(relative_path)):
        _assert_existing_fixture_preflight(consumer)


def test_tc_346_s03_001_wheel_installed_four_target_import(candidate_wheel: CandidateWheel) -> None:
    target, env = _prepare_s03_consumer(candidate_wheel, "s03-four-target")
    target_nodes = (
        ("root", None, "root", target / "spec-dock" / "artifacts"),
        ("initiative", "601", "init-00601", _find_node(target, "init-00601") / "artifacts"),
        ("epic", "612", "epic-00612", _find_node(target, "epic-00612") / "artifacts"),
        ("issue", "645", "iss-00645", _find_node(target, "iss-00645") / "artifacts"),
    )
    collision_path = target / "spec-dock" / "artifacts" / "20260730t010203z--root-opaque.bin"
    collision_path.parent.mkdir(parents=True, exist_ok=True)
    rules_source = target / "spec-dock" / "docs" / "rules" / "root" / "artifacts.md"
    (collision_path.parent / "rules.md").symlink_to(os.path.relpath(rules_source, start=collision_path.parent))
    collision_body = b"existing collision bytes\x00\xff"
    collision_path.write_bytes(collision_body)

    for target_kind, target_value, target_id, artifacts_dir in target_nodes:
        source = target / f"{target_kind}-opaque.bin"
        body = (f"s03-{target_kind}-opaque-body-" + "x" * 47).encode() + b"\x00\xff"
        source.write_bytes(body)
        before = source.read_bytes()
        command = ["artifact", "import", "file", f"--{target_kind}"]
        if target_value is not None:
            command.append(target_value)
        command.extend(["--file", source.name, "--json"])
        result = _run_installed_runtime(candidate_wheel.venv_python, target, command, env=env)
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        _assert_s03_json_payload(payload, target_kind=target_kind, target_id=target_id)
        assert payload["source_visibility"] == "repo_relative"
        assert payload["source"] == source.name
        destination = target / str(payload["destination"])
        assert destination.parent == artifacts_dir
        assert destination.read_bytes() == body
        assert source.read_bytes() == before
        assert source.read_bytes() == body
        assert "sha256" not in result.stdout.lower()
        assert "byte_count" not in result.stdout.lower()
        if target_kind == "root":
            assert destination != collision_path
            assert collision_path.read_bytes() == collision_body


def test_tc_346_s03_002_external_and_nested_cwd_privacy(candidate_wheel: CandidateWheel) -> None:
    target, env = _prepare_s03_consumer(candidate_wheel, "s03-external-privacy")
    temp_root = candidate_wheel.wheel_path.parent
    external_parent = temp_root / "s03-private-parent-sentinel"
    external_parent.mkdir()
    nested_cwd = target / "nested" / "cwd"
    nested_cwd.mkdir(parents=True)
    agent_before = _snapshot_tree(target / "spec-dock" / ".agent")
    cases = (
        ("root", None, "root", "text", external_parent / "path-hash-count-text.bin", target),
        ("initiative", "601", "init-00601", "json", external_parent / "path-hash-count-json.bin", target),
        ("epic", "612", "epic-00612", "text", external_parent / "path-hash-count-nested-text.bin", nested_cwd),
        ("issue", "645", "iss-00645", "json", external_parent / "path-hash-count-nested-json.bin", nested_cwd),
    )
    for index, (target_kind, target_value, target_id, output_mode, source, cwd) in enumerate(cases):
        body = (f"s03-body-hash-count-sentinel-{index}-" + "y" * 49).encode() + b"\x00\xff"
        source.write_bytes(body)
        selected = source
        if cwd == nested_cwd:
            # The installed runtime resolves relative sources from the
            # consumer repository root even when the process CWD is nested.
            selected = Path(os.path.relpath(source, start=target))
        command = ["artifact", "import", "file", f"--{target_kind}"]
        if target_value is not None:
            command.append(target_value)
        command.extend(["--file", str(selected)])
        if output_mode == "json":
            command.append("--json")
        result = _run_installed_runtime_at_cwd(
            candidate_wheel.venv_python,
            target,
            cwd,
            command,
            env=env,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        payload: object | None = None
        if output_mode == "json":
            decoded = json.loads(result.stdout)
            assert isinstance(decoded, dict)
            payload = decoded
            _assert_s03_json_payload(decoded, target_kind=target_kind, target_id=target_id)
            assert decoded["source_visibility"] == "basename_only"
            assert decoded["source"] == source.name
            destination = target / str(decoded["destination"])
        else:
            assert f'source="{source.name}"' in result.stdout
            assert "canonical=true" not in result.stdout
            destination_text = next(
                field.removeprefix("destination=").strip('"')
                for field in result.stdout.split()
                if field.startswith("destination=")
            )
            destination = target / destination_text
        assert destination.is_file()
        assert destination.read_bytes() == body
        assert source.read_bytes() == body
        _assert_s03_privacy_output(
            result,
            source=source,
            body=body,
            payload=payload,
            public_files=_s03_import_owned_public_files(target, destination),
        )

    # Keep the privacy oracle sensitive to every forbidden-value class. Each
    # injected sentinel retains a valid basename in the captured output so a
    # failure cannot be attributed to an unrelated shape check.
    probe_source = cases[0][4]
    probe_body = b"s03 privacy oracle body sentinel\x00\xff"
    allowed_output = f'source="{probe_source.name}"'
    for sentinel in _s03_privacy_forbidden_values(probe_source, probe_body):
        injected = subprocess.CompletedProcess(
            args=["privacy-negative"],
            returncode=0,
            stdout=f"{allowed_output} injected={sentinel}",
            stderr="",
        )
        with pytest.raises(AssertionError, match="privacy sentinel leaked"):
            _assert_s03_privacy_output(injected, source=probe_source, body=probe_body)

    injected_payload = {"derived": _s03_privacy_forbidden_values(probe_source, probe_body)[-1]}
    with pytest.raises(AssertionError, match="privacy sentinel leaked"):
        _assert_s03_privacy_output(
            subprocess.CompletedProcess(
                args=["privacy-negative-json"],
                returncode=0,
                stdout=allowed_output,
                stderr="",
            ),
            source=probe_source,
            body=probe_body,
            payload=injected_payload,
        )

    public_probe = target / "spec-dock" / ".agent" / "s03-privacy-negative.txt"
    public_probe.parent.mkdir(parents=True, exist_ok=True)
    try:
        public_probe.write_text(
            _s03_privacy_forbidden_values(probe_source, probe_body)[0],
            encoding="utf-8",
        )
        with pytest.raises(AssertionError, match="privacy sentinel leaked"):
            _assert_s03_privacy_output(
                subprocess.CompletedProcess(
                    args=["privacy-negative-public"],
                    returncode=0,
                    stdout=allowed_output,
                    stderr="",
                ),
                source=probe_source,
                body=probe_body,
                public_files=(public_probe,),
            )
    finally:
        public_probe.unlink(missing_ok=True)
    assert _snapshot_tree(target / "spec-dock" / ".agent") == agent_before


def test_tc_346_s03_003_actual_cross_filesystem_source(candidate_wheel: CandidateWheel) -> None:
    helper = _Issue69Harness()
    target: Path | None = None
    source_parent: Path | None = None
    try:
        # Keep the same-device target invisible to concurrent Git status
        # assertions while another full-regression shard executes this test.
        target_root = candidate_wheel.repo_root / "spec-dock" / ".workbench"
        target_root.mkdir(parents=True, exist_ok=True)
        target = Path(tempfile.mkdtemp(prefix="iss346-cross-fs-", dir=str(target_root)))
        source_root = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp")
        if not source_root.is_dir() or not os.access(source_root, os.W_OK):
            pytest.skip("portable temporary source root is unavailable")
        source_parent = Path(tempfile.mkdtemp(prefix="iss346-cross-fs-source-", dir=str(source_root)))
        helper._init_origin_repo(target)
        env = _runtime_env(helper, candidate_wheel.wheel_path.parent)
        installed_cli = helper._issue_69_venv_spec_dock(candidate_wheel.venv_python)
        init_result = subprocess.run(
            [str(installed_cli), "init", str(target)],
            cwd=candidate_wheel.wheel_path.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert init_result.returncode == 0, init_result.stdout + init_result.stderr
        source = source_parent / "cross-filesystem.bin"
        body = b"s03 cross-filesystem body sentinel\x00\xff\n"
        source.write_bytes(body)
        source_device = source.stat().st_dev
        destination_root_device = target.stat().st_dev
        if source_device == destination_root_device:
            pytest.skip("actual cross-filesystem source is unavailable")
        result = _run_installed_runtime(
            candidate_wheel.venv_python,
            target,
            ["artifact", "import", "file", "--root", "--file", str(source), "--json"],
            env=env,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        _assert_s03_json_payload(payload, target_kind="root", target_id="root")
        assert payload["source_visibility"] == "basename_only"
        assert payload["source"] == source.name
        destination = target / str(payload["destination"])
        assert destination.is_file()
        assert destination.read_bytes() == body
        assert source.read_bytes() == body
        assert destination.parent.stat().st_dev == destination_root_device
        assert source.stat().st_dev != destination.parent.stat().st_dev
        _assert_s03_privacy_output(
            result,
            source=source,
            body=body,
            payload=payload,
            public_files=_s03_import_owned_public_files(target, destination),
        )
    finally:
        if target is not None:
            shutil.rmtree(target, ignore_errors=True)
        if source_parent is not None:
            shutil.rmtree(source_parent, ignore_errors=True)


def test_tc_346_s04_004_disposable_exact_dogfood_update_keeps_epic_00343_unbackfilled(
    candidate_wheel: CandidateWheel,
) -> None:
    provider_head = _git(candidate_wheel.repo_root, "rev-parse", "HEAD")
    provider_status = _git(candidate_wheel.repo_root, "status", "--porcelain=v1")
    checkout: Path | None = None
    try:
        checkout, env, installed_cli = _clone_exact_candidate_checkout(candidate_wheel, "s04-dogfood-no-backfill")
        assert _git(checkout, "rev-parse", "HEAD") == candidate_wheel.post_head
        _assert_epic_00343_unbackfilled(checkout)
        canonical_before = _snapshot_tree(checkout / "spec-dock" / "initiatives", include_symlinks=False)
        provider_before = _snapshot_tree(checkout / "src" / "spec_dock" / "assets" / "spec_dock")
        update_result = subprocess.run(
            [str(installed_cli), "update", str(checkout)],
            cwd=candidate_wheel.wheel_path.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update_result.returncode == 0, update_result.stdout + update_result.stderr
        assert _git(checkout, "rev-parse", "HEAD") == candidate_wheel.post_head
        _assert_epic_00343_unbackfilled(checkout)
        _assert_s04_provider_projection_parity(candidate_wheel, checkout)
        assert _snapshot_tree(checkout / "spec-dock" / "initiatives", include_symlinks=False) == canonical_before
        assert _snapshot_tree(checkout / "src" / "spec_dock" / "assets" / "spec_dock") == provider_before
        _assert_exact_status_manifest(checkout, _S04_UPDATE_EXPECTED_STATUS)

        forbidden_readme = _epic_00343_readme(checkout)
        forbidden_readme.parent.mkdir(parents=True, exist_ok=True)
        forbidden_readme.write_bytes(b"forbidden backfill fixture\n")
        with pytest.raises(AssertionError, match=re.escape(forbidden_readme.as_posix())):
            _assert_epic_00343_unbackfilled(checkout)
        forbidden_readme.unlink()
        _assert_epic_00343_unbackfilled(checkout)
    finally:
        if checkout is not None:
            shutil.rmtree(checkout, ignore_errors=True)
            assert not checkout.exists()
        assert _git(candidate_wheel.repo_root, "rev-parse", "HEAD") == provider_head
        assert _git(candidate_wheel.repo_root, "status", "--porcelain=v1") == provider_status


def test_tc_346_s04_005_disposable_dogfood_future_shell_and_generic_import(
    candidate_wheel: CandidateWheel,
) -> None:
    provider_head = _git(candidate_wheel.repo_root, "rev-parse", "HEAD")
    provider_status = _git(candidate_wheel.repo_root, "status", "--porcelain=v1")
    checkout: Path | None = None
    try:
        checkout, env, installed_cli = _clone_exact_candidate_checkout(candidate_wheel, "s04-dogfood-future-import")
        assert _git(checkout, "rev-parse", "HEAD") == candidate_wheel.post_head
        _assert_epic_00343_unbackfilled(checkout)
        update_result = subprocess.run(
            [str(installed_cli), "update", str(checkout)],
            cwd=candidate_wheel.wheel_path.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update_result.returncode == 0, update_result.stdout + update_result.stderr
        _assert_epic_00343_unbackfilled(checkout)
        _assert_s04_provider_projection_parity(candidate_wheel, checkout)
        future_number = _next_unused_github_issue_number(checkout)
        create_result = _run_installed_runtime(
            candidate_wheel.venv_python,
            checkout,
            [
                "new",
                "issue",
                "--epic",
                "343",
                "--title",
                "S04 future dogfood",
                "--github-issue",
                str(future_number),
            ],
            env=env,
        )
        assert create_result.returncode == 0, create_result.stdout + create_result.stderr
        future_meta = next(
            meta_path
            for meta_path in (checkout / "spec-dock" / "initiatives").rglob(".meta.json")
            if json.loads(meta_path.read_text(encoding="utf-8")).get("github", {}).get("issue_number") == future_number
        )
        future_node = future_meta.parent
        future_payload = json.loads(future_meta.read_text(encoding="utf-8"))
        future_id = str(future_payload["id"])
        future_readme = future_node / ".workbench" / "README.md"
        assert future_readme.read_bytes() == _wheel_asset_bytes(
            candidate_wheel,
            "spec_dock/assets/spec_dock/templates/issue/.workbench/README.md",
        )
        readme_relative = future_readme.relative_to(checkout).as_posix()
        ignored_readme = subprocess.run(
            ["git", "check-ignore", "--no-index", readme_relative],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )
        assert ignored_readme.returncode == 1, ignored_readme.stdout + ignored_readme.stderr
        payload_source = future_node / ".workbench" / "s04-opaque.bin"
        payload_body = b"S04 dogfood generic payload\x00\xff\n"
        payload_source.write_bytes(payload_body)
        payload_relative = payload_source.relative_to(checkout).as_posix()
        ignored_source = subprocess.run(
            ["git", "check-ignore", "--no-index", payload_relative],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )
        assert ignored_source.returncode == 0, ignored_source.stdout + ignored_source.stderr
        tracked_source = subprocess.run(
            ["git", "ls-files", "--", payload_relative],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )
        assert tracked_source.returncode == 0, tracked_source.stdout + tracked_source.stderr
        assert tracked_source.stdout.strip() == ""

        import_result = _run_installed_runtime(
            candidate_wheel.venv_python,
            checkout,
            ["artifact", "import", "file", "--issue", future_id, "--file", payload_relative, "--json"],
            env=env,
        )
        assert import_result.returncode == 0, import_result.stdout + import_result.stderr
        payload = json.loads(import_result.stdout)
        _assert_s03_json_payload(payload, target_kind="issue", target_id=future_id)
        assert "sha256" not in import_result.stdout.lower()
        assert "byte_count" not in import_result.stdout.lower()
        assert str(checkout.resolve()) not in f"{import_result.stdout}\n{import_result.stderr}"
        destination = checkout / str(payload["destination"])
        assert destination.parent == future_node / "artifacts"
        _assert_s04_dogfood_privacy_output(
            import_result,
            checkout=checkout,
            source=payload_source,
            body=payload_body,
            payload=payload,
            destination=destination,
        )
        printable_body = "".join(
            character for character in payload_body.decode("utf-8", errors="ignore") if character.isprintable()
        )
        for leaked_token in (printable_body, f"count={len(payload_body)}", f"byte-count={len(payload_body)}"):
            with pytest.raises(AssertionError, match="dogfood privacy sentinel leaked"):
                _assert_s04_dogfood_privacy_output(
                    subprocess.CompletedProcess(
                        args=["synthetic-privacy-negative"],
                        returncode=0,
                        stdout=leaked_token,
                        stderr="",
                    ),
                    checkout=checkout,
                    source=payload_source,
                    body=payload_body,
                    payload=payload,
                    destination=destination,
                )
        assert destination.read_bytes() == payload_body
        assert payload_source.read_bytes() == payload_body

        for args in (("validate",), ("sync", "--no-github")):
            result = _run_installed_runtime(candidate_wheel.venv_python, checkout, list(args), env=env)
            assert result.returncode == 0, result.stdout + result.stderr
        _assert_epic_00343_unbackfilled(checkout)
        assert future_readme.read_bytes() == _wheel_asset_bytes(
            candidate_wheel,
            "spec_dock/assets/spec_dock/templates/issue/.workbench/README.md",
        )
        assert payload_source.read_bytes() == payload_body
        assert (
            subprocess.run(
                ["git", "check-ignore", "--no-index", payload_relative],
                cwd=checkout,
                capture_output=True,
                text=True,
                check=False,
            ).returncode
            == 0
        )
        future_relative = future_node.relative_to(checkout).as_posix()
        expected_status = {
            *_S04_UPDATE_EXPECTED_STATUS,
            f"{future_relative}/.meta.json",
            f"{future_relative}/.workbench/README.md",
            f"{future_relative}/design.md",
            f"{future_relative}/plan.md",
            f"{future_relative}/report.md",
            f"{future_relative}/requirement.md",
            f"{future_relative}/artifacts/rules.md",
            f"{future_relative}/artifacts/{destination.name}",
        }
        _assert_exact_status_manifest(checkout, expected_status)
        assert _git(checkout, "rev-parse", "HEAD") == candidate_wheel.post_head
    finally:
        if checkout is not None:
            shutil.rmtree(checkout, ignore_errors=True)
            assert not checkout.exists()
        assert _git(candidate_wheel.repo_root, "rev-parse", "HEAD") == provider_head
        assert _git(candidate_wheel.repo_root, "status", "--porcelain=v1") == provider_status
