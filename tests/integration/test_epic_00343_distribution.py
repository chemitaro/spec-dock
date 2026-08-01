from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
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


@dataclass(frozen=True)
class CandidateWheel:
    repo_root: Path
    wheel_path: Path
    venv_python: Path
    pre_head: str
    post_head: str
    pre_status: str
    post_status: str
    inventory: frozenset[str]
    sha256: str


FileSnapshot = tuple[tuple[str, bytes], ...]
PayloadState = tuple[bool, bytes | None, bool, str]


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
    wheel_path, _, venv_python = helper._issue_69_build_artifacts_with_local_wheelhouse(
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
        venv_python=venv_python,
        pre_head=pre_head,
        post_head=post_head,
        pre_status=pre_status,
        post_status=post_status,
        inventory=inventory,
        sha256=install_wheel_sha256,
    )


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


def _find_node(target: Path, node_id: str) -> Path:
    for meta_path in sorted((target / "spec-dock" / "initiatives").rglob(".meta.json")):
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
        if payload.get("id") == node_id:
            return meta_path.parent
    raise AssertionError(f"node not found: {node_id}")


def _wheel_asset_bytes(candidate_wheel: CandidateWheel, relative_path: str) -> bytes:
    with zipfile.ZipFile(candidate_wheel.wheel_path) as wheel_zip:
        return wheel_zip.read(relative_path)


def _snapshot_tree(root: Path) -> FileSnapshot:
    if not root.is_dir():
        return ()
    return tuple(
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
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
    present = [
        path.relative_to(consumer.target).as_posix()
        for path in consumer.existing_readmes
        if path.exists()
    ]
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

    existing_nodes = tuple(
        _find_node(target, node_id) for node_id in ("init-00401", "epic-00402", "iss-00403")
    )
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
    _update_existing_consumer(candidate_wheel, consumer)

    assert all(not path.exists() for path in consumer.existing_readmes)
    assert _payload_state(consumer.target, consumer.payload_path) == consumer.payload_before
    assert _snapshot_tree(consumer.target / "spec-dock" / "initiatives") == consumer.canonical_before
    assert _snapshot_graph(consumer.target) == consumer.graph_before
    assert consumer.guide_path.read_bytes() == consumer.guide_asset

    before = dict(consumer.managed_before)
    after = dict(_snapshot_managed_assets(consumer.target))
    changed_paths = sorted(
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )
    assert changed_paths == ["docs/guide.md"]


def test_tc_346_s02_003_existing_consumer_future_nodes_receive_workbench_shell(
    candidate_wheel: CandidateWheel,
) -> None:
    consumer = _prepare_existing_consumer(candidate_wheel, "s02-existing-003")
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
