from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.domain.authoring_pack.source_manifest import build_source_manifest  # noqa: E402

DEFAULT_INFRA_SOURCE_PATHS = (
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/authoring_pack/git_fetch.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/authoring_pack/preflight_receipt_writer.py",
    "spec-dock/scripts/spec_dock_runtime/infra/authoring_pack/git_fetch.py",
    "spec-dock/scripts/spec_dock_runtime/infra/authoring_pack/preflight_receipt_writer.py",
)


def _write_source(repo: Path, relative_path: str, content: str = "VALUE = 1\n") -> None:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_default_source_manifest_includes_fetch_and_receipt_infra_for_provider_and_dogfood(
    tmp_path: Path,
) -> None:
    for relative_path in DEFAULT_INFRA_SOURCE_PATHS:
        _write_source(tmp_path, relative_path)

    manifest = build_source_manifest(tmp_path, ())

    assert set(DEFAULT_INFRA_SOURCE_PATHS).issubset(manifest.source_paths)
    assert set(DEFAULT_INFRA_SOURCE_PATHS).issubset(manifest.source_hashes)


@pytest.mark.parametrize("relative_path", DEFAULT_INFRA_SOURCE_PATHS)
def test_default_source_manifest_hash_changes_with_each_fetch_or_receipt_infra_source(
    tmp_path: Path,
    relative_path: str,
) -> None:
    for source_path in DEFAULT_INFRA_SOURCE_PATHS:
        _write_source(tmp_path, source_path)
    baseline = build_source_manifest(tmp_path, ())

    _write_source(tmp_path, relative_path, "VALUE = 2\n")
    changed = build_source_manifest(tmp_path, ())

    assert changed.source_manifest_hash != baseline.source_manifest_hash


def test_explicit_source_paths_do_not_expand_to_default_infra_sources(tmp_path: Path) -> None:
    explicit_path = "chosen/source.py"
    _write_source(tmp_path, explicit_path)
    for relative_path in DEFAULT_INFRA_SOURCE_PATHS:
        _write_source(tmp_path, relative_path)

    manifest = build_source_manifest(tmp_path, (explicit_path,))

    assert manifest.source_paths == (explicit_path,)
    assert set(manifest.source_hashes) == {explicit_path}
