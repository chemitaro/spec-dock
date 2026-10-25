"""The default-branch check judges one commit tree by the six rules of Epic design chapter 8."""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application.canonical_check import evaluate_commit_tree
from spec_dock.runtime.infra.commit_tree import TreeEntry, TreeEntryKind
from spec_dock.runtime.infra.static_assets import StaticAsset

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.application.canonical_check import CheckOutcome

VERSION = "0.3.0"
IGNORE = b"# spec-dock runtime\n.agent/\n/.canonical/\n/initiatives\n!/initiatives/\n"
OLD_IGNORE = b"# spec-dock runtime\n.agent/\n"
DECLARATION = json.dumps({"schema_version": 4, "writer_protocol": "specdock.worktree-writer/v1"}).encode()


def _asset(path: str, payload: bytes, *, init_only: bool = False, old: tuple[bytes, ...] = ()) -> StaticAsset:
    digest = hashlib.sha256(payload).hexdigest()
    return StaticAsset(path, payload, digest, 0o644, init_only, tuple(hashlib.sha256(item).hexdigest() for item in old))


ASSETS = (
    _asset("spec-dock/.gitignore", IGNORE, old=(OLD_IGNORE,)),
    _asset("spec-dock/docs/README.md", b"current docs\n", old=(b"old docs\n",)),
    _asset("spec-dock/system/spec-dock-version", f"{VERSION}\n".encode(), old=(b"0.2.4\n",)),
    _asset("spec-dock/workspace.json", b'{"schema_version":4}\n', init_only=True),
)


def _valid_files() -> dict[str, bytes]:
    files = {asset.path: asset.payload for asset in ASSETS if not asset.init_only}
    files["spec-dock/workspace.json"] = DECLARATION
    files["src/app.py"] = b"print('code')\n"
    return files


def _evaluate(
    files: Mapping[str, bytes],
    kinds: Mapping[str, TreeEntryKind] | None = None,
    *,
    running_version: str = VERSION,
) -> CheckOutcome:
    kinds = kinds or {}
    blobs = {f"oid-{index}": payload for index, payload in enumerate(files.values())}
    entries = tuple(TreeEntry(path, kinds.get(path, "regular"), f"oid-{index}") for index, path in enumerate(files))
    ordered = tuple(sorted(entries, key=lambda entry: entry.path.encode()))
    return evaluate_commit_tree(
        ordered, lambda entry: blobs[entry.object_id], assets=ASSETS, running_version=running_version
    )


def test_a_tree_without_specs_and_with_intact_static_files_passes() -> None:
    outcome = _evaluate(_valid_files())
    assert outcome.failures == () and outcome.warnings == ()
    assert outcome.version_file == VERSION


def _codes(outcome: CheckOutcome) -> list[tuple[str, object]]:
    return [(failure.code, failure.details["path"]) for failure in outcome.failures]


@pytest.mark.parametrize(
    ("added", "kind"),
    [
        (("spec-dock/initiatives/init-00001-plan/requirement.md", "spec-dock/initiatives/README.md"), "regular"),
        (("spec-dock/initiatives",), "symlink"),
        (("spec-dock/initiatives",), "gitlink"),
    ],
)
def test_every_spec_path_is_one_failure_with_its_path_and_next_step(added: tuple[str, ...], kind: str) -> None:
    files = _valid_files()
    files.update(dict.fromkeys(added, b"spec\n"))
    outcome = _evaluate(files, dict.fromkeys(added, kind))  # type: ignore[arg-type]
    assert _codes(outcome) == [("SPEC_PATH_TRACKED", path) for path in sorted(added, key=str.encode)]
    for failure in outcome.failures:
        assert failure.details["entry"] == kind
        assert "git rm -r --cached -- spec-dock/initiatives" in str(failure.details["next_step"])


def test_catalog_paths_and_scope_metadata_are_reported_once_in_rule_order() -> None:
    files = _valid_files()
    files.update({
        "spec-dock/.canonical": b"",
        "spec-dock/.meta.json": b"{}",
        "spec-dock/artifacts/old/.meta.json": b"{}",
        "spec-dock/initiatives/init-00001-plan/.meta.json": b"{}",
        "src/.meta.json": b"{}",
        "spec-dock/.canonicalx/file": b"not the catalog",
    })
    outcome = _evaluate(files, {"spec-dock/.canonical": "gitlink"})
    assert _codes(outcome) == [
        ("SPEC_PATH_TRACKED", "spec-dock/initiatives/init-00001-plan/.meta.json"),
        ("CATALOG_PATH_TRACKED", "spec-dock/.canonical"),
        ("SCOPE_METADATA_TRACKED", "spec-dock/.meta.json"),
        ("SCOPE_METADATA_TRACKED", "spec-dock/artifacts/old/.meta.json"),
    ]
    catalog, metadata = outcome.failures[1], outcome.failures[2]
    assert catalog.details["entry"] == "gitlink"
    assert "git rm -r --cached -- spec-dock/.canonical" in str(catalog.details["next_step"])
    assert "git rm --cached" in str(metadata.details["next_step"])


def test_a_schema_three_declaration_is_one_failure_and_the_other_rules_still_run() -> None:
    files = _valid_files()
    files["spec-dock/workspace.json"] = json.dumps({"schema_version": 3, "writer_protocol": "unknown/v0"}).encode()
    files["spec-dock/initiatives/init-00001-plan/.meta.json"] = b"{}"
    outcome = _evaluate(files)
    assert _codes(outcome) == [
        ("SPEC_PATH_TRACKED", "spec-dock/initiatives/init-00001-plan/.meta.json"),
        ("WORKSPACE_NOT_MIGRATED", "spec-dock/workspace.json"),
    ]
    migrated = outcome.failures[1]
    assert migrated.details["schema_version"] == 3
    assert "scripts/migrate-to-canonical/README.md" in str(migrated.details["next_step"])


@pytest.mark.parametrize(
    ("payload", "kind", "reason", "next_step"),
    [
        (None, "regular", "missing", "Commit spec-dock/workspace.json as"),
        (DECLARATION, "symlink", "not-regular", "Commit spec-dock/workspace.json as"),
        (b"{not json", "regular", "invalid-json", "Commit spec-dock/workspace.json as"),
        (b"\xff\xfe", "regular", "invalid-json", "Commit spec-dock/workspace.json as"),
        (b"[4]", "regular", "invalid-json", "Commit spec-dock/workspace.json as"),
        (
            b'{"schema_version": true, "writer_protocol": "specdock.worktree-writer/v1"}',
            "regular",
            "unknown-schema",
            "Commit spec-dock/workspace.json as",
        ),
        (
            b'{"schema_version": "4", "writer_protocol": "specdock.worktree-writer/v1"}',
            "regular",
            "unknown-schema",
            "Commit spec-dock/workspace.json as",
        ),
        (
            b'{"schema_version": 5, "writer_protocol": "specdock.worktree-writer/v1"}',
            "regular",
            "unknown-schema",
            "Install the SpecDock version named by spec-dock/system/spec-dock-version",
        ),
        (
            b'{"schema_version": 4, "writer_protocol": "specdock.unknown/v9"}',
            "regular",
            "unknown-writer-protocol",
            "Commit spec-dock/workspace.json as",
        ),
    ],
)
def test_an_unusable_declaration_names_its_reason_and_next_step(
    payload: bytes | None, kind: TreeEntryKind, reason: str, next_step: str
) -> None:
    files = _valid_files()
    if payload is None:
        del files["spec-dock/workspace.json"]
    else:
        files["spec-dock/workspace.json"] = payload
    outcome = _evaluate(files, {"spec-dock/workspace.json": kind})
    assert _codes(outcome) == [("WORKSPACE_DECLARATION_INVALID", "spec-dock/workspace.json")]
    assert outcome.failures[0].details["reason"] == reason
    assert str(outcome.failures[0].details["next_step"]).startswith(next_step)


def test_the_old_known_writer_protocol_is_accepted_like_the_declaration_reader() -> None:
    files = _valid_files()
    files["spec-dock/workspace.json"] = b'{"schema_version": 4, "writer_protocol": "specdock.writer/v1"}'
    assert _evaluate(files).failures == ()


@pytest.mark.parametrize(
    ("change", "classification"),
    [("modified", "unknown"), ("deleted", "missing"), ("symlink", "unsafe"), ("gitlink", "unsafe")],
)
def test_a_broken_static_asset_is_one_failure_with_its_classification(change: str, classification: str) -> None:
    files = _valid_files()
    kinds: dict[str, TreeEntryKind] = {}
    path = "spec-dock/docs/README.md"
    if change == "modified":
        files[path] = b"locally edited docs\n"
    elif change == "deleted":
        del files[path]
    else:
        kinds[path] = change  # type: ignore[assignment]
    outcome = _evaluate(files, kinds)
    assert _codes(outcome) == [("STATIC_ASSET_INVALID", path)]
    failure = outcome.failures[0]
    assert failure.details["classification"] == classification
    assert "spec-dock installation update" in str(failure.details["next_step"])


def test_known_old_assets_pass_and_init_only_assets_are_left_to_the_declaration_rule() -> None:
    files = _valid_files()
    files["spec-dock/docs/README.md"] = b"old docs\n"
    assert files["spec-dock/workspace.json"] != ASSETS[-1].payload
    assert _evaluate(files).failures == ()


def test_a_known_old_gitignore_without_the_three_lines_is_one_failure() -> None:
    files = _valid_files()
    files["spec-dock/.gitignore"] = OLD_IGNORE
    outcome = _evaluate(files)
    assert _codes(outcome) == [("IGNORE_RULES_MISSING", "spec-dock/.gitignore")]
    failure = outcome.failures[0]
    assert failure.details["missing_lines"] == ["/.canonical/", "/initiatives", "!/initiatives/"]
    assert failure.details["misordered"] is False
    assert "/.canonical/, /initiatives, !/initiatives/" in str(failure.details["next_step"])


def test_the_negation_must_follow_the_link_rule_or_real_spec_directories_would_be_ignored() -> None:
    files = _valid_files()
    files["spec-dock/.gitignore"] = b".agent/\n!/initiatives/\n/.canonical/\n/initiatives\n"
    outcome = _evaluate(files)
    assert _codes(outcome) == [
        ("STATIC_ASSET_INVALID", "spec-dock/.gitignore"),
        ("IGNORE_RULES_MISSING", "spec-dock/.gitignore"),
    ]
    assert outcome.failures[1].details["missing_lines"] == []
    assert outcome.failures[1].details["misordered"] is True


def test_line_endings_and_trailing_spaces_do_not_hide_the_three_lines() -> None:
    files = _valid_files()
    files["spec-dock/.gitignore"] = IGNORE.replace(b"\n", b"  \r\n")
    assert _codes(_evaluate(files)) == [("STATIC_ASSET_INVALID", "spec-dock/.gitignore")]


def test_a_missing_gitignore_is_reported_once_as_a_missing_asset() -> None:
    files = _valid_files()
    del files["spec-dock/.gitignore"]
    assert _codes(_evaluate(files)) == [("STATIC_ASSET_INVALID", "spec-dock/.gitignore")]


def test_a_different_running_version_is_a_warning_not_a_failure() -> None:
    outcome = _evaluate(_valid_files(), running_version="0.4.0")
    assert outcome.failures == ()
    (warning,) = outcome.warnings
    assert warning.code == "SPEC_DOCK_VERSION_MISMATCH"
    assert warning.details["path"] == "spec-dock/system/spec-dock-version"
    assert (warning.details["expected"], warning.details["actual"]) == ("0.4.0", VERSION)
    assert "spec-dock/system/spec-dock-version" in str(warning.details["next_step"])


def test_a_missing_version_file_fails_as_an_asset_without_a_version_warning() -> None:
    files = _valid_files()
    del files["spec-dock/system/spec-dock-version"]
    outcome = _evaluate(files, running_version="0.4.0")
    assert _codes(outcome) == [("STATIC_ASSET_INVALID", "spec-dock/system/spec-dock-version")]
    assert outcome.warnings == () and outcome.version_file is None


def test_an_unreadable_version_file_warns_with_no_actual_version() -> None:
    files = _valid_files()
    files["spec-dock/system/spec-dock-version"] = b"\xff\n"
    outcome = _evaluate(files)
    assert _codes(outcome) == [("STATIC_ASSET_INVALID", "spec-dock/system/spec-dock-version")]
    (warning,) = outcome.warnings
    assert warning.details["actual"] is None and outcome.version_file is None


def test_a_known_older_version_file_is_only_a_warning_and_an_unknown_one_also_fails() -> None:
    files = _valid_files()
    files["spec-dock/system/spec-dock-version"] = b"0.2.4\n"
    outcome = _evaluate(files)
    assert outcome.failures == () and [warning.details["actual"] for warning in outcome.warnings] == ["0.2.4"]
    files["spec-dock/system/spec-dock-version"] = b"0.2.9\n"
    outcome = _evaluate(files)
    assert _codes(outcome) == [("STATIC_ASSET_INVALID", "spec-dock/system/spec-dock-version")]
    assert [warning.details["actual"] for warning in outcome.warnings] == ["0.2.9"]


def test_a_deeply_nested_declaration_is_one_invalid_declaration_not_a_crash() -> None:
    files = _valid_files()
    files["spec-dock/workspace.json"] = b"[" * 100_000
    files["spec-dock/initiatives/README.md"] = b"spec"
    outcome = _evaluate(files)
    assert _codes(outcome) == [
        ("SPEC_PATH_TRACKED", "spec-dock/initiatives/README.md"),
        ("WORKSPACE_DECLARATION_INVALID", "spec-dock/workspace.json"),
    ]
    assert outcome.failures[1].details["reason"] == "invalid-json"
