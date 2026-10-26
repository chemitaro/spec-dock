"""Fixtures for canonical check: committed code trees and the package assets with the canonical ignore rules.

I-2 ships the three ignore lines in spec-dock/.gitignore (contract C3), so the helpers below change nothing for the
current package; they overlay the lines only on a package whose .gitignore lacks them.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.application.canonical_check import SPEC_DOCK_GITIGNORE, SPEC_DOCK_IGNORE_LINES
from spec_dock.runtime.infra.static_assets import StaticAsset, package_static_assets

if TYPE_CHECKING:
    from collections.abc import Mapping

    import pytest

DECLARATION = {"schema_version": 4, "writer_protocol": "specdock.worktree-writer/v1"}


def gitignore_with_ignore_rules(payload: bytes) -> bytes:
    """Append the canonical ignore lines that the payload lacks, keeping every existing byte.

    A payload that already names the catalog or the link in another form would hide a contract C3 mismatch,
    so it is refused instead of overlaid.
    """
    lines = payload.decode("utf-8").split("\n")
    missing = [line for line in SPEC_DOCK_IGNORE_LINES if line not in lines]
    if missing and any(".canonical" in line or "initiatives" in line for line in lines):
        raise AssertionError("the shipped .gitignore names the catalog or link without the contract C3 lines")
    if not missing:
        return payload
    prefix = payload if payload.endswith(b"\n") or not payload else payload + b"\n"
    return prefix + "".join(f"{line}\n" for line in missing).encode("utf-8")


def assets_with_ignore_rules() -> tuple[StaticAsset, ...]:
    """The package assets with a .gitignore that carries the ignore lines (bytes without them become known-old)."""
    result = []
    for asset in package_static_assets():
        if asset.path == SPEC_DOCK_GITIGNORE:
            payload = gitignore_with_ignore_rules(asset.payload)
            if payload != asset.payload:
                asset = replace(
                    asset,
                    payload=payload,
                    sha256=hashlib.sha256(payload).hexdigest(),
                    known_old_sha256=(*asset.known_old_sha256, asset.sha256),
                )
        result.append(asset)
    return tuple(result)


def use_assets_with_ignore_rules(monkeypatch: pytest.MonkeyPatch) -> tuple[StaticAsset, ...]:
    assets = assets_with_ignore_rules()
    monkeypatch.setattr("spec_dock.runtime.application.canonical_check.package_static_assets", lambda: assets)
    return assets


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def code_repository(root: Path, assets: tuple[StaticAsset, ...], extra: Mapping[str, bytes] | None = None) -> Path:
    """A committed code tree holding the static assets, a schema-4 declaration and the given extra files."""
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "--local", "maintenance.auto", "false")
    files = {asset.path: asset.payload for asset in assets if not asset.init_only}
    files["spec-dock/workspace.json"] = json.dumps(DECLARATION).encode("utf-8")
    files["src/app.py"] = b"print('code')\n"
    files.update(extra or {})
    for relative, payload in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    for asset in assets:
        if asset.mode == 0o755 and (root / asset.path).exists():
            (root / asset.path).chmod(0o755)
    commit(root)
    return root


def commit(root: Path, message: str = "fixture", *, stage: bool = True) -> str:
    """Commit the working tree, or only what is already in the index when stage is false."""
    if stage:
        git(root, "add", "--all")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD").strip()


def stage_gitlink(root: Path, path: str) -> None:
    """Record a gitlink (what git add -A makes of a nested worktree) without a nested repository."""
    git(root, "update-index", "--add", "--cacheinfo", f"160000,{git(root, 'rev-parse', 'HEAD').strip()},{path}")


def provider_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_checkout_with_ignore_rules(root: Path) -> str:
    """A committed copy of this provider whose shipped .gitignore carries the canonical ignore rules."""
    provider = provider_root()
    (root / "src").mkdir(parents=True)
    shutil.copytree(
        provider / "src/spec_dock", root / "src/spec_dock", ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    for name in ("pyproject.toml", "README.md", "setup.py"):
        shutil.copy2(provider / name, root / name)
    assets = root / "src/spec_dock/assets"
    gitignore = assets / "spec_dock/.gitignore"
    before = gitignore.read_bytes()
    after = gitignore_with_ignore_rules(before)
    if after != before:
        gitignore.write_bytes(after)
        inventory_path = assets / "static-inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        entry = next(item for item in inventory["files"] if item["path"] == SPEC_DOCK_GITIGNORE)
        entry["known_old_sha256"].append(entry["sha256"])
        entry["sha256"] = hashlib.sha256(after).hexdigest()
        inventory_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "--local", "maintenance.auto", "false")
    return commit(root, "fixed source")
