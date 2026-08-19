from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


LEDGER = Path(__file__).with_name("full-regression-ledger.json")


def _normalize(message: str, repository: Path) -> str:
    message = message.split(" +  where ", 1)[0]
    message = message.replace(str(repository), "<repo>")
    message = re.sub(
        r"/(?:private/)?var/folders/[^/]+/[^/]+/T/tmp[^/`'\"\\ ]*",
        "<tmp>",
        message,
    )
    message = re.sub(r"/(?:private/)?var/folders/[^'\" ,]+", "<tmp-runtime-path>", message)
    message = message.replace("<repo>/.venv/bin/python3", "<python>")
    message = message.replace("<repo>/.venv/bin/python", "<python>")
    return " ".join(message.split())


def _failure_signatures(junit_path: Path, repository: Path) -> tuple[dict[str, str], list[str]]:
    failures: dict[str, str] = {}
    errors: list[str] = []
    for testcase in ET.parse(junit_path).getroot().iter("testcase"):
        parts = testcase.attrib["classname"].split(".")
        class_parts: list[str] = []
        while parts and parts[-1][:1].isupper():
            class_parts.insert(0, parts.pop())
        nodeid = "/".join(parts) + ".py::" + "::".join((*class_parts, testcase.attrib["name"]))
        failure = testcase.find("failure")
        if failure is not None:
            normalized = _normalize(failure.attrib.get("message", ""), repository)
            failures[nodeid] = hashlib.sha256(normalized.encode()).hexdigest()
        if testcase.find("error") is not None:
            errors.append(nodeid)
    return failures, errors


def main() -> int:
    repository = Path.cwd().resolve()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    observed = ledger.get("current_head_sha")
    if not isinstance(observed, str):
        print("full-regression ledger has no observation SHA", file=sys.stderr)
        return 2
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", observed, head],
        cwd=repository,
        check=False,
    )
    if ancestry.returncode != 0:
        print("full-regression ledger observation is not an ancestor of HEAD", file=sys.stderr)
        return 2
    expected = {
        entry["nodeid"]: entry["fixed_point_signature_sha256"]
        for entry in ledger.get("failure_paths", [])
        if entry.get("current_status") == "failed"
        and entry.get("fixed_point_status") == "failed"
        and entry.get("disposition") == "approved-no-op"
        and entry.get("failure_signature_match") is True
        and entry.get("current_signature_sha256") == entry.get("fixed_point_signature_sha256")
    }
    if len(expected) != len(ledger.get("failure_paths", [])) or not expected:
        print("full-regression ledger contains incomplete failure signatures", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="issue368-full-regression-") as temporary:
        junit_path = Path(temporary) / "junit.xml"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--run-full-regression",
                "-q",
                f"--junitxml={junit_path}",
            ],
            cwd=repository,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(completed.stdout, end="")
        if completed.returncode != 1 or not junit_path.is_file():
            print(f"unexpected pytest exit code: {completed.returncode}", file=sys.stderr)
            return 1
        actual, errors = _failure_signatures(junit_path, repository)
    if errors or actual != expected:
        print(
            json.dumps(
                {
                    "candidate_sha": head,
                    "unexpected_errors": sorted(errors),
                    "missing_failures": sorted(set(expected) - set(actual)),
                    "unexpected_failures": sorted(set(actual) - set(expected)),
                    "signature_mismatches": sorted(
                        nodeid for nodeid in set(actual) & set(expected) if actual[nodeid] != expected[nodeid]
                    ),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(f"verified {len(actual)} approved failure signatures on candidate {head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
