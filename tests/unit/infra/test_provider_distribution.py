"""Shipped static assets match a fresh installation before dogfood cutover."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    }


def test_provider_matches_fresh_consumer_managed_assets(installed_static_consumer: Path) -> None:
    for provider, consumer in (
        ("src/spec_dock/assets/spec_dock/docs", "spec-dock/docs"),
        ("src/spec_dock/assets/install_root/.agents/skills", ".agents/skills"),
    ):
        assert _files(ROOT / provider) == _files(installed_static_consumer / consumer)


def test_provider_scripts_contain_only_the_static_entrypoint_assets() -> None:
    provider = _files(ROOT / "src/spec_dock/assets/spec_dock/scripts")
    assert set(provider) == {"README.md", "spec-dock"}


def test_provider_shim_matches_the_standalone_external_console_delegator() -> None:
    assert (ROOT / "src/spec_dock/assets/spec_dock/scripts/spec-dock").read_bytes() == (
        ROOT / "src/spec_dock/shim_vnext.py"
    ).read_bytes()
