"""Decide whether a push to the default branch tags a new SpecDock release (Epic design chapter 8).

A tag v<version> is returned only when pyproject.toml's version changed between the pushed commits, the new
version is a plain X.Y.Z release of at least 0.3.0, and the tag does not exist yet. The script reads Git only;
it never imports the package, creates the tag or contacts the network.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # Python 3.10 uses tomli, the package's declared dependency there
    import tomli as tomllib

MINIMUM = (0, 3, 0)
_COMMIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
_RELEASE = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)\Z")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False, timeout=60)


def _version_at(repo: Path, commit: str) -> str | None:
    if _git(repo, "cat-file", "-e", f"{commit}^{{commit}}").returncode:
        return None
    shown = _git(repo, "show", f"{commit}:pyproject.toml")
    if shown.returncode:
        return None
    try:
        version = tomllib.loads(shown.stdout)["project"]["version"]
    except (tomllib.TOMLDecodeError, KeyError, TypeError):
        return None
    return version if isinstance(version, str) else None


def decide(repo: Path, before: str, after: str) -> dict[str, str | None]:
    version = _version_at(repo, after)
    if version is None:
        raise RuntimeError(f"cannot read the project version of the pushed commit {after}")
    previous = None if set(before) == {"0"} else _version_at(repo, before)
    decision: dict[str, str | None] = {"tag": None, "version": version, "previous": previous}
    release = _RELEASE.match(version)
    if previous is None:
        reason = "before-unavailable"
    elif previous == version:
        reason = "version-unchanged"
    elif release is None:
        reason = "not-a-release-version"
    elif tuple(int(part) for part in release.groups()) < MINIMUM:
        reason = "below-minimum"
    elif not _git(repo, "rev-parse", "--quiet", "--verify", f"refs/tags/v{version}").returncode:
        reason = "tag-exists"
    else:
        reason = "create"
        decision["tag"] = f"v{version}"
    decision["reason"] = reason
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    arguments = parser.parse_args(argv)
    for name in ("before", "after"):
        if _COMMIT_ID.match(getattr(arguments, name)) is None:
            parser.error(f"--{name} must be a complete lowercase Git commit ID")
    try:
        decision = decide(arguments.repo, arguments.before, arguments.after)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(decision))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as stream:
            stream.write(f"tag={decision['tag'] or ''}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
