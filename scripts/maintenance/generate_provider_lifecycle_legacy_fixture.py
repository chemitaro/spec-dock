#!/usr/bin/env python3
"""Generate the exact-clean 0.2.3 fixture from immutable Git objects."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "dc638e936e763cc7a6087f258201ed9ed654e7fb"
SOURCE_REPOSITORY = "chemitaro/spec-dock"
OUTPUT_DEFAULT = REPOSITORY_ROOT / "src" / "spec_dock" / "assets" / "provider_lifecycle" / "legacy-0.2.3.json"
DOMAINS = (
    ("root", "spec-dock/docs", "src/spec_dock/assets/spec_dock/docs"),
    ("root", "spec-dock/templates", "src/spec_dock/assets/spec_dock/templates"),
    ("root", "spec-dock/system", "src/spec_dock/assets/spec_dock/system"),
    ("root", "spec-dock/scripts", "src/spec_dock/assets/spec_dock/scripts"),
    (
        "slot",
        ".agents/skills/spec-dock",
        "src/spec_dock/assets/install_root/.agents/skills/spec-dock",
    ),
    (
        "slot",
        ".agents/skills/spec-dock-grill-with-docs",
        "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs",
    ),
)
VERSION_PATH = "spec-dock/spec-dock.version"
LEGACY_MAGIC = b"spec-dock-exact-legacy-fixture-v1\0"


class FixtureGenerationError(ValueError):
    """The verified Git closure is not the expected legacy source."""


def _git(*arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), *arguments],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise FixtureGenerationError(f"Git object read failed: {' '.join(arguments)}") from exc
    return result.stdout


def _verify_commit() -> None:
    value = _git("cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}")
    if value:
        raise FixtureGenerationError("unexpected output while verifying source commit")


def _ls_tree() -> list[tuple[str, str, str, str]]:
    paths = [source_path for _, _, source_path in DOMAINS] + ["spec-dock/spec-dock.version"]
    raw = _git("ls-tree", "-rz", "-t", SOURCE_COMMIT, "--", *paths)
    records: list[tuple[str, str, str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, encoded_path = record.split(b"\t", 1)
            mode, object_type, object_id = header.split(b" ")
            path = encoded_path.decode("utf-8")
            records.append((mode.decode("ascii"), object_type.decode("ascii"), object_id.decode("ascii"), path))
        except (UnicodeDecodeError, ValueError) as exc:
            raise FixtureGenerationError("malformed git ls-tree record") from exc
    if not records:
        raise FixtureGenerationError("source Git tree is empty")
    return records


def _blob_contents(object_ids: set[str]) -> dict[str, bytes]:
    if not object_ids:
        return {}
    request = b"".join(object_id.encode("ascii") + b"\n" for object_id in sorted(object_ids))
    try:
        result = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "cat-file", "--batch"],
            input=request,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise FixtureGenerationError("Git blob batch read failed") from exc
    output = result.stdout
    cursor = 0
    contents: dict[str, bytes] = {}
    for object_id in sorted(object_ids):
        header_end = output.find(b"\n", cursor)
        if header_end < 0:
            raise FixtureGenerationError("truncated git cat-file --batch header")
        header = output[cursor:header_end].split()
        cursor = header_end + 1
        if len(header) != 3 or header[0].decode("ascii") != object_id or header[1] != b"blob":
            raise FixtureGenerationError(f"expected blob object {object_id}")
        try:
            size = int(header[2])
        except ValueError as exc:
            raise FixtureGenerationError("invalid git blob size") from exc
        content = output[cursor : cursor + size]
        if len(content) != size or cursor + size >= len(output) or output[cursor + size : cursor + size + 1] != b"\n":
            raise FixtureGenerationError("truncated git blob body")
        contents[object_id] = content
        cursor += size + 1
    if cursor != len(output):
        raise FixtureGenerationError("unexpected trailing git cat-file output")
    return contents


def _entry_bytes(kind: str, path: str, mode: str | None, digest: str | None, target: str | None) -> bytes:
    encoded_path = path.encode("utf-8")
    if kind == "directory":
        return b"D\0" + encoded_path + b"\0"
    if kind == "regular":
        assert mode is not None and digest is not None
        return b"F\0" + encoded_path + b"\0" + mode.encode("ascii") + b"\0" + digest.encode("ascii") + b"\0"
    if kind == "symlink":
        assert target is not None
        return b"L\0" + encoded_path + b"\0" + target.encode("utf-8") + b"\0"
    raise FixtureGenerationError(f"unsupported fixture entry kind: {kind}")


def _build_fixture() -> dict[str, object]:
    _verify_commit()
    records = _ls_tree()
    version_records = [record for record in records if record[3] == VERSION_PATH and record[1] == "blob"]
    if len(version_records) != 1:
        raise FixtureGenerationError("legacy version record is missing or ambiguous")
    blob_ids = {record[2] for record in records if record[1] == "blob"}
    blobs = _blob_contents(blob_ids)
    version_blob = blobs[version_records[0][2]]
    if version_blob != b"0.2.3\n":
        raise FixtureGenerationError("verified legacy version bytes are not exact 0.2.3 LF")

    fixture_domains: list[dict[str, object]] = []
    aggregate = bytearray(LEGACY_MAGIC + b"0.2.3\0")
    for kind, public_path, source_path in DOMAINS:
        selected = [record for record in records if record[3] == source_path or record[3].startswith(source_path + "/")]
        if not any(record[3] == source_path and record[1] == "tree" for record in selected):
            raise FixtureGenerationError(f"missing source domain tree: {source_path}")
        entries: list[dict[str, object]] = []
        stream = bytearray()
        for mode, object_type, object_id, git_path in sorted(selected, key=lambda row: row[3].encode("utf-8")):
            if git_path == source_path:
                continue
            relative = git_path[len(source_path) + 1 :]
            entry: dict[str, object]
            if object_type == "tree":
                entry = {"kind": "directory", "path": relative}
                stream.extend(_entry_bytes("directory", relative, None, None, None))
            elif mode in {"100644", "100755"} and object_type == "blob":
                digest = hashlib.sha256(blobs[object_id]).hexdigest()
                mode_value = f"{int(mode[-3:], 8):04o}"
                entry = {"kind": "regular", "path": relative, "mode": mode_value, "sha256": digest}
                stream.extend(_entry_bytes("regular", relative, mode_value, digest, None))
            elif mode == "120000" and object_type == "blob":
                try:
                    target = blobs[object_id].decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise FixtureGenerationError(f"symlink target is not UTF-8: {git_path}") from exc
                if target.endswith("\n"):
                    target = target[:-1]
                if not target or target.startswith("/") or "\x00" in target:
                    raise FixtureGenerationError(f"unsafe legacy symlink target: {git_path}")
                entry = {"kind": "symlink", "path": relative, "target": target}
                stream.extend(_entry_bytes("symlink", relative, None, None, target))
            else:
                raise FixtureGenerationError(f"unsupported source entry {mode} {object_type} {git_path}")
            entries.append(entry)
        tree_digest = hashlib.sha256(stream).hexdigest()
        fixture_domains.append({
            "kind": kind,
            "path": public_path,
            "source_path": source_path,
            "tree_digest": tree_digest,
            "entries": entries,
        })
        aggregate.extend(b"DOMAIN\0" + kind.encode() + b"\0" + public_path.encode() + b"\0" + stream)

    return {
        "schema_version": 1,
        "legacy_version": "0.2.3",
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": SOURCE_COMMIT,
        "version_record": {
            "path": VERSION_PATH,
            "kind": "regular",
            "mode": "0644",
            "sha256": hashlib.sha256(version_blob).hexdigest(),
            "bytes_base64": base64.b64encode(version_blob).decode("ascii"),
        },
        "domains": fixture_domains,
        "aggregate_digest": hashlib.sha256(aggregate).hexdigest(),
    }


def _render() -> bytes:
    return json.dumps(_build_fixture(), ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = _render()
    except (OSError, UnicodeError, FixtureGenerationError) as exc:
        print(f"generate_provider_lifecycle_legacy_fixture.py: {exc}", file=sys.stderr)
        return 1
    if args.check:
        try:
            actual = args.output.read_bytes()
        except OSError as exc:
            print(f"generate_provider_lifecycle_legacy_fixture.py: {exc}", file=sys.stderr)
            return 1
        if actual != expected:
            print(f"generated output differs: {args.output}", file=sys.stderr)
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
