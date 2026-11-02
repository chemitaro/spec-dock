"""iss-00511: the README count, package-data, and what 0.5.0 removed stay in line with the shipped documents."""

from __future__ import annotations

from pathlib import Path
import re

import tomllib

from spec_dock.runtime.cli.catalog import LEAF_ARGUMENTS

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets"
DOCS = ASSETS / "spec_dock/docs"
MIGRATION = "spec_dock/docs/migration.md"
CANONICAL = "spec_dock/docs/canonical.md"


def test_the_readme_command_count_is_the_cli_catalog_leaf_count() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    counts = re.findall(r"全(\d+)コマンド", readme)
    assert counts == [str(len(LEAF_ARGUMENTS))]


def test_the_github_integration_doc_no_longer_describes_a_local_backend() -> None:
    text = (ROOT / "docs/github-issue-integration.md").read_text(encoding="utf-8")
    assert "local backend" not in text.lower() and "ローカルmetadata" not in text and "--backend local" not in text


def test_package_data_lists_only_templates_that_exist() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    patterns = pyproject["tool"]["setuptools"]["package-data"]["spec_dock"]
    missing = [
        pattern for pattern in patterns if "*" not in pattern and not (ROOT / "src/spec_dock" / pattern).exists()
    ]
    assert missing == []
    assert not [p for p in patterns if re.search(r"templates/(initiative|epic|issue)/\.workbench", p)]


# (term, document relative to assets) pairs where the term may appear: the 0.5.0 removal notes and detections.
REMOVED = {
    "workspace migrate": re.compile(r"spec-dock workspace migrate"),
    "workbench copy": re.compile(r"workbench copy"),
    "--ci": re.compile(r"(?<![\w-])--ci(?![\w-])"),
    "--source local": re.compile(r"--source local"),
    ".meta.json": re.compile(r"\.meta\.json"),
}
ALLOWED = {
    ("workspace migrate", MIGRATION),
    ("--source local", MIGRATION),
    ("workbench copy", MIGRATION),
    ("workbench copy", CANONICAL),
    ("--ci", MIGRATION),
    ("--ci", CANONICAL),
    (".meta.json", MIGRATION),
    (".meta.json", CANONICAL),
    (".meta.json", "spec_dock/docs/reference_cli.md"),
    (".meta.json", "spec_dock/docs/cli-redesign-guide.html"),
}
CREATING = re.compile(r"(作成|作る|書き込|写)(する|します|してください)")


def _shipped_documents() -> list[Path]:
    return sorted(path for path in ASSETS.rglob("*") if path.suffix in {".md", ".html"} and path.is_file())


def test_removed_guidance_appears_only_where_it_is_kept_as_history() -> None:
    seen: set[tuple[str, str]] = set()
    stray: list[str] = []
    for path in _shipped_documents():
        relative = path.relative_to(ASSETS).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for term, pattern in REMOVED.items():
                if not pattern.search(line):
                    continue
                seen.add((term, relative))
                if (term, relative) not in ALLOWED:
                    stray.append(f"{relative}:{number}: {term}")
                elif term == ".meta.json" and CREATING.search(line):
                    stray.append(f"{relative}:{number}: instructs creating {term}")
    assert stray == []
    assert ALLOWED - seen == set(), "an allowance no longer matches any document; remove it"
