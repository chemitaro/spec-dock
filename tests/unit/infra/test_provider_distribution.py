"""Static assets retain parity; the retired dogfood runtime awaits cutover."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    }


def test_provider_matches_dogfood_managed_assets() -> None:
    for provider, dogfood in (
        ("src/spec_dock/assets/spec_dock/docs", "spec-dock/docs"),
        ("src/spec_dock/assets/install_root/.agents/skills", ".agents/skills"),
    ):
        assert _files(ROOT / provider) == _files(ROOT / dogfood)


def test_provider_scripts_contain_only_the_static_entrypoint_assets() -> None:
    provider = _files(ROOT / "src/spec_dock/assets/spec_dock/scripts")
    assert set(provider) == {"README.md", "spec-dock"}


def test_provider_shim_matches_the_standalone_external_console_delegator() -> None:
    assert (ROOT / "src/spec_dock/assets/spec_dock/scripts/spec-dock").read_bytes() == (
        ROOT / "src/spec_dock/shim_vnext.py"
    ).read_bytes()
