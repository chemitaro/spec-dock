from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import cast

from spec_dock.provider_lifecycle.candidate import capture_packaged_candidate
from spec_dock.provider_lifecycle.contracts import CandidateDomain, CandidateIdentity
from tests.integration.test_epic_00343_distribution import (
    _assert_installed_asset_manifest,
    _expected_installed_asset_manifest,
    _provider_asset_manifest,
    _sdist_asset_manifest,
    _wheel_asset_manifest,
)
from tests.unit.infra.test_init_update import TestInitUpdate


@dataclass(frozen=True)
class _InstalledCandidate:
    identity: CandidateIdentity
    assets_dir: Path


def _tree_manifest(root: Path) -> dict[str, tuple[object, ...]]:
    manifest: dict[str, tuple[object, ...]] = {}
    for path in sorted(root.rglob("*")):
        if (
            "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
            or path.name == ".spec-dock-provider-slot.json"
        ):
            continue
        relative = path.relative_to(root).as_posix()
        info = path.lstat()
        if path.is_symlink():
            manifest[relative] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            manifest[relative] = ("file", info.st_mode & 0o777, path.read_bytes())
    return manifest


def _candidate_from_payload(payload: dict[str, object]) -> CandidateIdentity:
    raw_domains = payload.get("domains")
    assert isinstance(raw_domains, list)
    domains: list[CandidateDomain] = []
    for raw_domain in raw_domains:
        assert isinstance(raw_domain, dict)
        domains.append(
            CandidateDomain(
                kind=cast("str", raw_domain["kind"]),
                path=cast("str", raw_domain["path"]),
                tree_digest=cast("str", raw_domain["tree_digest"]),
                entry_count=cast("int", raw_domain["entry_count"]),
            )
        )
    return CandidateIdentity(
        schema_version=cast("int", payload["schema_version"]),
        version=cast("str", payload["version"]),
        aggregate_digest=cast("str", payload["aggregate_digest"]),
        domains=tuple(domains),
    )


def _install_artifact(
    helper: TestInitUpdate,
    *,
    repo_root: Path,
    artifact: Path,
    environment_root: Path,
) -> tuple[Path, Path]:
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(environment_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    venv_python = helper._issue_69_venv_python(environment_root)
    wheelhouse = helper._issue_69_resolve_wheelhouse(repo_root)
    site_packages = helper._issue_69_site_packages_dir(environment_root)
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=site_packages,
        requirements=list(helper._ISSUE_69_BUILD_BACKEND_REQUIREMENTS),
        wheelhouse=wheelhouse,
    )
    helper._issue_69_install_target_packages(
        python_executable=venv_python,
        target_dir=site_packages,
        requirements=[str(artifact)],
        wheelhouse=wheelhouse,
    )
    return venv_python, helper._issue_69_ensure_spec_dock_wrapper(venv_python)


def _read_installed_candidate(
    venv_python: Path,
    *,
    repo_root: Path,
    cwd: Path,
) -> _InstalledCandidate:
    repo_root_literal = json.dumps(str(repo_root.resolve()))
    script = (
        "from dataclasses import asdict\n"
        "import importlib.resources as resources\n"
        "import json\n"
        "from pathlib import Path\n"
        "import sys\n"
        "import spec_dock\n"
        "from spec_dock.provider_lifecycle.candidate import capture_packaged_candidate\n"
        f"repo_root = Path({repo_root_literal})\n"
        "def _under_repo(path_text):\n"
        "    if not path_text:\n"
        "        return False\n"
        "    try:\n"
        "        return Path(path_text).resolve().is_relative_to(repo_root)\n"
        "    except Exception:\n"
        "        return False\n"
        "candidate = capture_packaged_candidate()\n"
        "assets_dir = Path(str(resources.files('spec_dock').joinpath('assets'))).resolve()\n"
        "print(json.dumps({\n"
        "    'module_path': str(Path(spec_dock.__file__).resolve()),\n"
        "    'assets_dir': str(assets_dir),\n"
        "    'repo_on_sys_path': any(_under_repo(value) for value in sys.path),\n"
        "    'candidate': asdict(candidate),\n"
        "}))\n"
    )
    env = _environment_without_checkout_fallback()
    result = subprocess.run(
        [str(venv_python), "-c", script],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output_lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert output_lines, "installed candidate command produced no JSON output"
    payload = json.loads(output_lines[-1])
    assert isinstance(payload, dict)
    module_path = Path(cast("str", payload["module_path"])).resolve()
    assets_dir = Path(cast("str", payload["assets_dir"])).resolve()
    assert "site-packages" in module_path.as_posix()
    assert "site-packages" in assets_dir.as_posix()
    assert not module_path.is_relative_to(repo_root.resolve())
    assert not assets_dir.is_relative_to(repo_root.resolve())
    assert payload["repo_on_sys_path"] is False
    candidate_payload = payload.get("candidate")
    assert isinstance(candidate_payload, dict)
    return _InstalledCandidate(_candidate_from_payload(candidate_payload), assets_dir)


def _environment_without_checkout_fallback() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    return environment


def _dogfood_candidate(repo_root: Path, destination: Path) -> CandidateIdentity:
    mappings = (
        ("spec_dock/docs", repo_root / "spec-dock/docs"),
        ("spec_dock/templates", repo_root / "spec-dock/templates"),
        ("spec_dock/system", repo_root / "spec-dock/system"),
        ("spec_dock/scripts", repo_root / "spec-dock/scripts"),
        ("install_root/.agents/skills/spec-dock", repo_root / ".agents/skills/spec-dock"),
        (
            "install_root/.agents/skills/spec-dock-grill-with-docs",
            repo_root / ".agents/skills/spec-dock-grill-with-docs",
        ),
    )
    for relative, source in mappings:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, symlinks=True)
    return capture_packaged_candidate(destination)


def test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    helper = TestInitUpdate()
    source_assets = repo_root / "src/spec_dock/assets"
    source_candidate = capture_packaged_candidate(source_assets)
    source_manifest = _provider_asset_manifest(repo_root)
    expected_installed = _expected_installed_asset_manifest(repo_root)
    fixture_source = source_assets / "provider_lifecycle/legacy-0.2.3.json"
    bootstrap_source = source_assets / "spec_dock/scripts/spec-dock"

    build_context = tmp_path / "build-context"
    wheel_dir = tmp_path / "wheelhouse"
    sdist_dir = tmp_path / "sdist"
    helper._issue_69_prepare_build_context(repo_root, build_context)
    wheel_path, sdist_path, _build_python = helper._issue_69_build_artifacts_with_local_wheelhouse(
        repo_root=repo_root,
        build_context=build_context,
        wheel_dir=wheel_dir,
        sdist_dir=sdist_dir,
    )

    assert _wheel_asset_manifest(wheel_path) == source_manifest
    assert _sdist_asset_manifest(sdist_path) == source_manifest
    installed_candidates: list[_InstalledCandidate] = []
    installed_wrappers: list[Path] = []
    isolated_cwd = tmp_path / "isolated-cwd"
    isolated_cwd.mkdir()
    for name, artifact in (("wheel", wheel_path), ("sdist", sdist_path)):
        venv_python, wrapper = _install_artifact(
            helper,
            repo_root=repo_root,
            artifact=artifact,
            environment_root=tmp_path / f"{name}-environment",
        )
        installed_candidates.append(
            _read_installed_candidate(
                venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
        )
        installed_wrappers.append(wrapper)

    for installed in installed_candidates:
        assert installed.identity == source_candidate
        fixture_installed = installed.assets_dir / "provider_lifecycle/legacy-0.2.3.json"
        bootstrap_installed = installed.assets_dir / "spec_dock/scripts/spec-dock"
        assert fixture_installed.read_bytes() == fixture_source.read_bytes()
        assert bootstrap_installed.read_bytes() == bootstrap_source.read_bytes()
        assert _tree_manifest(installed.assets_dir / "spec_dock/docs") == _tree_manifest(
            source_assets / "spec_dock/docs"
        )

    dogfood_mappings = (
        (source_assets / "spec_dock/docs", repo_root / "spec-dock/docs"),
        (source_assets / "spec_dock/templates", repo_root / "spec-dock/templates"),
        (source_assets / "spec_dock/system", repo_root / "spec-dock/system"),
        (source_assets / "spec_dock/scripts", repo_root / "spec-dock/scripts"),
        (source_assets / "install_root/.agents/skills/spec-dock", repo_root / ".agents/skills/spec-dock"),
        (
            source_assets / "install_root/.agents/skills/spec-dock-grill-with-docs",
            repo_root / ".agents/skills/spec-dock-grill-with-docs",
        ),
    )
    for provider, dogfood in dogfood_mappings:
        assert _tree_manifest(provider) == _tree_manifest(dogfood)

    dogfood_candidate = _dogfood_candidate(repo_root, tmp_path / "dogfood-candidate")
    assert dogfood_candidate == source_candidate

    fresh_target = tmp_path / "fresh-consumer"
    fresh_target.mkdir()
    install_result = subprocess.run(
        [str(installed_wrappers[0]), "init", str(fresh_target), "--json"],
        cwd=isolated_cwd,
        env=_environment_without_checkout_fallback(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert install_result.returncode == 0, install_result.stdout + install_result.stderr
    output_lines = [line for line in install_result.stdout.splitlines() if line.strip()]
    assert output_lines, "fresh install produced no JSON output"
    install_payload = json.loads(output_lines[-1])
    assert install_payload["candidate_digest"] == source_candidate.aggregate_digest
    _assert_installed_asset_manifest(fresh_target, expected_installed)
    assert (fresh_target / "spec-dock/scripts/spec-dock").read_bytes() == bootstrap_source.read_bytes()
    assert (repo_root / "spec-dock/spec-dock.version").read_bytes() == (
        fresh_target / "spec-dock/spec-dock.version"
    ).read_bytes()
    for relative_path in (
        ".agents/skills/spec-dock/.spec-dock-provider-slot.json",
        ".agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json",
    ):
        assert (repo_root / relative_path).read_bytes() == (fresh_target / relative_path).read_bytes()
