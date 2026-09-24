"""Public CLI inventory for the coordinated vNext cutover."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.parser import build_parser  # noqa: E402
from spec_dock_runtime.cli.registry import build_registry  # noqa: E402

LEGACY_MANIFEST = Path(__file__).resolve().parents[1] / "fixtures/cli_redesign/legacy_manifest.json"


def _leaf_paths(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> set[str]:
    result: set[str] = set()
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child in action.choices.items():
            path = (*prefix, name)
            if child.get_default("command_key"):
                result.add(" ".join(path))
            else:
                result.update(_leaf_paths(child, path))
    return result


def test_legacy_28_leaf_inventory_is_frozen_before_cutover() -> None:
    manifest = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "eeb3e5965f0cb42de9a24081bfaea15e27fd4451"
    assert len(manifest["leaf_paths"]) == 28
    assert len(set(manifest["leaf_paths"])) == 28
    assert _leaf_paths(build_parser(build_registry())) == set(manifest["leaf_paths"])
