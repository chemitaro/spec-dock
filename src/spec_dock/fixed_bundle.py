"""Build an isolated, hashable external engine from the installed package."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from spec_dock import __version__
from spec_dock.runtime_loader import digest_distribution


def _python_binary() -> Path:
    python = Path(sys.executable).resolve(strict=True)
    if not python.is_file() or not os.access(python, os.X_OK) or any(char.isspace() for char in str(python)):
        raise ValueError("fixed engine requires an executable Python path without whitespace")
    return python


def _source_checkout(package: Path) -> Path | None:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    try:
        result = subprocess.run(
            ["git", "-C", str(package), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (
        Path(result.stdout.strip()).resolve(strict=True) if result.returncode == 0 and result.stdout.strip() else None
    )


def build_fixed_engine(destination: Path) -> Path:
    """Copy only package bytes into a new directory outside the checkout."""
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+){2}(?:[a-zA-Z0-9._-]*)", __version__) is None:
        raise ValueError("installed package version is unavailable")
    package = Path(__file__).resolve(strict=True).parent
    if not destination.is_absolute() or destination.exists() or destination.is_symlink():
        raise ValueError("fixed engine destination must be a new absolute path")
    parent = destination.parent.resolve(strict=True)
    target = parent / destination.name
    if target.is_relative_to(package) or package.is_relative_to(target):
        raise ValueError("fixed engine destination overlaps its package source")
    checkout = _source_checkout(package)
    if checkout is not None and target.is_relative_to(checkout):
        raise ValueError("fixed engine destination must be outside the package checkout")
    for path in package.rglob("*"):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError("package contains an unsafe entry")
    python = _python_binary()
    stage = Path(tempfile.mkdtemp(prefix=".specdock-engine-", dir=parent))
    try:
        library = stage / "lib"
        library.mkdir()
        shutil.copytree(
            package,
            library / "spec_dock",
            symlinks=False,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
        (library / "spec_dock/version.txt").write_text(f"{__version__}\n", encoding="utf-8")
        executable = stage / "bin/spec-dock"
        executable.parent.mkdir()
        executable.write_text(
            f"#!{python} -IB\n"
            "from pathlib import Path\n"
            "import sys\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))\n"
            "from spec_dock.external_cli import main\n"
            "raise SystemExit(main())\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        digest_distribution(stage)
        if target.exists() or target.is_symlink():
            raise ValueError("fixed engine destination appeared during staging")
        stage.rename(target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return target / "bin/spec-dock"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a fixed SpecDock engine outside a project checkout")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    executable = build_fixed_engine(args.destination.expanduser())
    print(f"{executable} {digest_distribution(executable.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
