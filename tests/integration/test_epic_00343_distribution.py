from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

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
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=helper._issue_69_site_packages_dir(helper._issue_69_env_root(venv_python)),
        requirements=[str(wheel_path)],
        wheelhouse=helper._issue_69_resolve_wheelhouse(repo_root),
    )
    helper._issue_69_ensure_spec_dock_wrapper(venv_python)

    post_head = _git(repo_root, "rev-parse", "HEAD")
    post_status = _git(repo_root, "status", "--porcelain=v1")
    inventory = frozenset(helper._issue_69_collect_wheel_file_inventory(wheel_path))
    digest = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
    return CandidateWheel(
        repo_root=repo_root,
        wheel_path=wheel_path,
        venv_python=venv_python,
        pre_head=pre_head,
        post_head=post_head,
        pre_status=pre_status,
        post_status=post_status,
        inventory=inventory,
        sha256=digest,
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
    assert str(target) not in import_result.stdout
    destination = target / payload["destination"]
    assert destination.read_bytes() == body
    assert source.read_bytes() == body
