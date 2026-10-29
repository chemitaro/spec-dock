"""The values migrate.py copies are the package's contract values (AC-435-13, AC-456-08)."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from spec_dock.runtime.application import canonical_check, scope_scaffold
from spec_dock.runtime.application.project_context import NEW_WRITER_PROTOCOL
from spec_dock.runtime.domain import canonical_content, canonical_layout, canonical_structure
from spec_dock.runtime.domain.ids import CANONICAL_ID_RE, INPUT_TITLE_RE, derive_input_slug_from_title
from spec_dock.runtime.infra.canonical_git import HOOKLESS_CONFIG, PASSED_GIT_VARIABLES
from tests.support.migration_repo import ROOT, SCRIPT, migrate_module

ASSETS = ROOT / "src/spec_dock/assets"


def test_c1_kind_labels_definitions_and_ids() -> None:
    module = migrate_module()
    assert dict(canonical_structure.KIND_LABELS) == module.KIND_LABELS
    assert dict(canonical_structure.ID_PREFIXES) == module.ID_PREFIXES
    assert dict(canonical_structure.PARENT_KINDS) == module.PARENT_KINDS
    kinds = [
        item for item in canonical_structure.LABEL_DEFINITIONS if item.name in canonical_structure.KIND_LABELS.values()
    ]
    assert tuple((item.name, item.color, item.description) for item in kinds) == module.LABEL_DEFINITIONS
    assert module.CANONICAL_ID_RE.pattern == CANONICAL_ID_RE.pattern
    assert not hasattr(module, "SLUG_RE") and not hasattr(module, "read_slug_marker")
    for kind in ("initiative", "epic", "issue"):
        for number in (1, 39, 424, 123456):
            assert module.scope_id(kind, number) == canonical_structure.scope_id(kind, number)


@pytest.mark.parametrize(
    ("number", "bucket"),
    [
        (1, "00000-00999"),
        (454, "00000-00999"),
        (999, "00000-00999"),
        (1000, "01000-01999"),
        (2114, "02000-02999"),
        (99999, "99000-99999"),
        (100000, "100000-100999"),
        (100454, "100000-100999"),
        (1000000, "1000000-1000999"),
    ],
)
def test_c3_buckets_follow_the_number_rule(number: int, bucket: str) -> None:
    module = migrate_module()
    assert module.BUCKET_SIZE == 1000
    assert module.scope_bucket(number) == bucket
    assert module.scope_relative(module.scope_id("issue", number)) == f"{bucket}/{module.scope_id('issue', number)}"


def test_c3_bucket_inputs_outside_the_rule_are_refused() -> None:
    module = migrate_module()
    for number in (0, -1):
        with pytest.raises(ValueError):
            module.scope_bucket(number)
    for value in ("iss-454", "iss-000454", "ISS-00454", "iss-00454-foo", "adr-00001"):
        with pytest.raises(ValueError):
            module.scope_relative(value)


def test_legacy_title_slug_and_child_rule_links() -> None:
    module = migrate_module()
    assert module.LEGACY_TITLE_RE.pattern == INPUT_TITLE_RE.pattern
    for title in ("Add Refresh Token", "JWT Auth 2", " Spaced Title "):
        assert module.legacy_slug(title) == derive_input_slug_from_title(title.strip())
    for title in ("日本語の題名", "Add-Token", "Add  Token", "", "Add_Token"):
        assert module.legacy_slug(title) == "untitled"
    spec_dock = ROOT / "spec-dock"
    for kind, (directory, target) in module.LEGACY_CHILD_RULES.items():
        sources = scope_scaffold._rules_source_paths(kind=kind, specdock_dir=spec_dock)
        assert (ROOT / target) == sources[0]
        assert sources[0].parent.name == kind and directory in ("epics", "issues")
        assert sources[0].stem == directory
    assert set(module.LEGACY_CHILD_RULES) == {"initiative", "epic"}


def test_c2_declaration_bytes_and_writer_protocol() -> None:
    module = migrate_module()
    assert module.NEW_WRITER_PROTOCOL == NEW_WRITER_PROTOCOL
    assert (ASSETS / "spec_dock/workspace.json").read_bytes() == module.WORKSPACE_V4_BYTES
    inventory = json.loads((ASSETS / "static-inventory.json").read_text())
    entry = next(item for item in inventory["files"] if item["path"] == "spec-dock/workspace.json")
    assert hashlib.sha256(module.WORKSPACE_V3_BYTES).hexdigest() in entry["known_old_sha256"]


def test_c3_catalog_link_branch_and_ignore_lines() -> None:
    module = migrate_module()
    assert module.CANONICAL_BRANCH == canonical_layout.CANONICAL_BRANCH
    assert module.CANONICAL_REF == canonical_layout.CANONICAL_REF
    assert module.CANONICAL_TRACKING_REF == canonical_layout.CANONICAL_TRACKING_REF
    assert str(canonical_layout.CATALOG_RELATIVE) == module.CATALOG_RELATIVE
    assert str(canonical_layout.LINK_RELATIVE) == module.LINK_RELATIVE
    assert module.CATALOG_LOCK_REASON == canonical_layout.CATALOG_LOCK_REASON
    assert module.GITIGNORE_PATH == canonical_layout.GITIGNORE_PATH
    assert module.GITIGNORE_LINES == canonical_layout.GITIGNORE_LINES


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        "/.canonical/\n/initiatives\n!/initiatives/\n",
        "/.canonical/\n!/initiatives/\n/initiatives\n",
        "/initiatives\n!/initiatives/\n",
        "/.canonical/  \r\n/initiatives\r\n!/initiatives/\r\n",
        "!/initiatives/\n/.canonical/\n/initiatives\n!/initiatives/\n",
    ],
)
def test_c3_effective_ignore_rules_match_the_package(text: str | None) -> None:
    module = migrate_module()
    expected = not canonical_layout.missing_lines(text, canonical_layout.GITIGNORE_LINES)
    assert module.ignore_rules_effective(text) is expected


def test_c5_canonical_root_files() -> None:
    module = migrate_module()
    assert dict(canonical_content.CANONICAL_ROOT_FILES) == module.CANONICAL_ROOT_FILES
    assert module.FORMAT_FILE == canonical_content.FORMAT_FILE
    assert module.RUNTIME_DIRECTORY == canonical_content.RUNTIME_DIRECTORY


def test_c6_hookless_git_settings_and_passed_variables() -> None:
    assert migrate_module().HOOKLESS_CONFIG == HOOKLESS_CONFIG
    assert migrate_module().PASSED_GIT_VARIABLES == PASSED_GIT_VARIABLES


def test_c7_version_file_workflow_sample_and_branch_rule() -> None:
    module = migrate_module()
    assert module.CI_VERSION_FILE == canonical_check.CI_VERSION_FILE
    assert module.WORKFLOW_SAMPLE == canonical_check.WORKFLOW_SAMPLE
    assert module.WORKFLOW_DESTINATION == canonical_check.WORKFLOW_DESTINATION
    assert module.WORKFLOW_BRANCH_LINE == canonical_check.WORKFLOW_BRANCH_LINE
    assert (ASSETS / "spec_dock/docs/ci/spec-dock-check.yml").read_bytes() == module.WORKFLOW_SAMPLE_BYTES
    assert module.WORKFLOW_SAMPLE_BYTES.count(module.WORKFLOW_BRANCH_LINE.encode()) == 1
    for name, valid in (("main", True), ("develop", True), ("release/1.0", True), ("1.0", False), ("a b", False)):
        assert (module.WORKFLOW_BRANCH_NAME_RE.fullmatch(name) is not None) is valid


@pytest.mark.parametrize(
    ("host", "expected"),
    [("MacBook-Pro.local", "macbook-pro"), ("my_box", "my-box"), ("--", "pc"), ("A" * 40, "a" * 32), ("", "pc")],
)
def test_conflict_names_follow_the_epic_rule(host: str, expected: str) -> None:
    module = migrate_module()
    assert module.pc_name(host) == expected
    tag = module.conflict_tag("box", datetime(2026, 10, 26, 1, 2, 3, tzinfo=timezone.utc))
    assert tag == "conflict-box-20261026T010203Z"
    taken = {"plan.conflict-box-20261026T010203Z.md"}
    assert module.alternate_name("plan.md", tag, taken.__contains__) == "plan.conflict-box-20261026T010203Z-2.md"
    assert module.alternate_name(".gitignore", tag, lambda _: False) == ".gitignore.conflict-box-20261026T010203Z"
    assert module.alternate_name("Makefile", tag, lambda _: False) == "Makefile.conflict-box-20261026T010203Z"


def test_the_script_never_imports_the_package() -> None:
    import ast

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not {name for name in imported if name.split(".")[0] == "spec_dock"}
    assert Path(SCRIPT).stat().st_mode & 0o111
