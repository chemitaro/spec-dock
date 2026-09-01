from __future__ import annotations

import ast
from dataclasses import replace
import errno
import hashlib
import inspect
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import TYPE_CHECKING, cast

import pytest

import spec_dock.cli as cli
import spec_dock.managed_distribution as managed_distribution
from spec_dock.managed_distribution import (
    DistributionAction,
    DistributionAdmissionError,
    DistributionApplyError,
    DistributionAsset,
    DistributionIdentity,
    DistributionManifestError,
    DistributionPlan,
    DistributionPlanError,
    DistributionResult,
    DistributionRetryMarker,
    DistributionRootIdentity,
    DistributionStageOwnership,
    DistributionTargetSnapshot,
    OperationJournalStore,
    PathIdentitySnapshot,
    admit_distribution_operation,
    apply_distribution_plan,
    build_distribution_plan,
    build_executable_mutation_plan,
    build_workspace_assessment,
    execute_fresh_distribution,
    execute_recognized_distribution,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALL_ROOT = REPO_ROOT / "src" / "spec_dock" / "assets" / "install_root"
MANIFEST_PATH = REPO_ROOT / "src" / "spec_dock" / "assets" / "managed_distribution.json"
HISTORICAL_COMMIT = "948d0cf0dedb84ca34e51a4adc0995820aa011f6"

EXPECTED_CURRENT_PATHS = frozenset({
    ".agents/skills/spec-dock/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    ".agents/skills/spec-dock-grill-with-docs/agents/openai.yaml",
    ".agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py",
    ".github/workflows/ci.yml",
})


def test_issue_368_generated_link_target_enforces_repository_root_boundary() -> None:
    checker = managed_distribution._generated_link_target_is_within_root

    assert checker("spec-dock/active/issue", "../../outside") is True
    assert checker("spec-dock/active/issue", "../../../outside") is False
    assert checker("spec-dock/active/issue", "../../..") is False


EXPECTED_OBSOLETE_SKILL_PATHS = frozenset(
    f".agents/skills/{name}/SKILL.md"
    for name in (
        "spec-dock-hub",
        "spec-dock-initiative-planning",
        "spec-dock-epic-planning",
        "spec-dock-epic-execution",
        "spec-dock-issue-planning",
        "spec-dock-issue-execution",
        "spec-dock-chatgpt-authoring",
        "spec-dock-initiative-planning-manual",
        "spec-dock-epic-planning-manual",
        "spec-dock-issue-planning-manual",
        "spec-dock-clarification",
        "spec-dock-adr-facilitation",
        "spec-dock-codex-adapter",
        "spec-dock-copilot-adapter",
        "git-commit-conventional-ja",
        "github-pr-observation",
        "github-pr-creator",
        "github-pr-merge-preparer",
        "spec-driven-tdd-workflow",
        "spec-dock-system-architect",
        "spec-dock-implementation-planner",
    )
)
EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS = frozenset(
    f"spec-dock/current-{scope}{suffix}" for scope in ("initiative", "epic", "issue") for suffix in ("", ".path")
)
MANIFEST_FIELDS = {
    "schema_version",
    "recognized_workspace_versions",
    "historical_current_identities",
    "trusted_consumer_manifests",
    "obsolete_exact_files",
    "historical_shortcuts",
}
EXPECTED_HISTORICAL_CURRENT_IDENTITY = {
    "path": ".agents/skills/spec-dock-grill-with-docs/SKILL.md",
    "kind": "regular",
    "sha256": "7182c1156bcf3635ffd3113cdcfb1d507c819b6aba6982673c0b10166f5da40c",
    "mode": 0o644,
    "source": {"kind": "git-provider-source", "ref": HISTORICAL_COMMIT},
}


_RECOVERY_PATHNAMES = (".distribution-retry.json", ".distribution-journal.json", ".uninstall-retry.json")
_RECOVERY_PATH_MUTATORS = frozenset({"rename", "replace", "touch", "unlink", "write_bytes", "write_text"})
_RECOVERY_OS_MUTATORS = frozenset({"open", "remove", "rename", "replace", "unlink"})
_RECOVERY_SAFE_SERVICE_CALLS = frozenset({
    "execute_deprovision_distribution",
    "execute_explicit_spec_history_purge_distribution",
    "execute_fresh_distribution",
    "execute_recognized_distribution",
})


def _has_recovery_path_role(node: ast.AST, roles: set[str] | frozenset[str]) -> bool:
    return any(
        (isinstance(child, ast.Name) and child.id in roles)
        or (
            isinstance(child, ast.Constant)
            and isinstance(child.value, str)
            and child.value.endswith(_RECOVERY_PATHNAMES)
        )
        for child in ast.walk(node)
    )


def _cli_recovery_writer_roles(source: str) -> tuple[str, ...]:
    """Return CLI functions that mutate a managed recovery pathname."""

    tree = ast.parse(source)
    module_roles: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and _has_recovery_path_role(node.value, module_roles):
            module_roles.update(target.id for target in node.targets if isinstance(target, ast.Name))

    functions = tuple(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    role_factories = frozenset(
        function.name
        for function in functions
        if any(
            isinstance(node, ast.Return)
            and node.value is not None
            and not isinstance(node.value, ast.Call)
            and _has_recovery_path_role(node.value, module_roles)
            for node in ast.walk(function)
        )
    )
    violations: set[str] = set()
    for function in functions:
        role_names = set(module_roles | role_factories)
        for assignment in (node for node in ast.walk(function) if isinstance(node, ast.Assign)):
            if _has_recovery_path_role(assignment.value, role_names):
                role_names.update(target.id for target in assignment.targets if isinstance(target, ast.Name))

        for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
            arguments = (*call.args, *(keyword.value for keyword in call.keywords))
            has_role_argument = any(_has_recovery_path_role(value, role_names) for value in arguments)
            if isinstance(call.func, ast.Name):
                if has_role_argument and call.func.id not in role_factories | _RECOVERY_SAFE_SERVICE_CALLS:
                    violations.add(f"{function.name}:{call.func.id}")
            elif isinstance(call.func, ast.Attribute):
                if (
                    isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "os"
                    and call.func.attr in _RECOVERY_OS_MUTATORS
                    and has_role_argument
                ):
                    violations.add(f"{function.name}:os.{call.func.attr}")
                    continue
                if not _has_recovery_path_role(call.func.value, role_names):
                    continue
                mode = (
                    call.args[0]
                    if call.func.attr == "open" and call.args
                    else next((keyword.value for keyword in call.keywords if keyword.arg == "mode"), None)
                )
                writable_open = (
                    isinstance(mode, ast.Constant)
                    and isinstance(mode.value, str)
                    and bool(set(mode.value) & set("wax+"))
                )
                if call.func.attr in _RECOVERY_PATH_MUTATORS or writable_open:
                    violations.add(f"{function.name}:{call.func.attr}")

    return tuple(sorted(violations))


def test_i372_reference_github_uses_current_uninstall_recovery_metadata() -> None:
    """I372-T-DOC-001: docs name current writers without promoting legacy evidence."""

    provider = (REPO_ROOT / "src/spec_dock/assets/spec_dock/docs/reference_github.md").read_text(encoding="utf-8")
    dogfood = (REPO_ROOT / "spec-dock/docs/reference_github.md").read_text(encoding="utf-8")

    assert dogfood == provider
    assert "current schema 2 の forward guard `spec-dock/.distribution-retry.json`" in provider
    assert "current journal `spec-dock/.distribution-journal.json`" in provider
    assert "legacy `spec-dock/.uninstall-retry.json` は reader-only / manual evidence" in provider
    assert "自動作成も current recovery state への自動変換も行いません" in provider


_RENAMED_RECOVERY_CLI_PREFIX = """
RETRY_PATH = Path("spec-dock/.distribution-retry.json")
def _renamed_recovery_path(root): return root / RETRY_PATH
def _renamed_recovery_reader(root): return os.lstat(_renamed_recovery_path(root))
def _renamed_service_coordinator(root): return execute_recognized_distribution(root, legacy_marker=_renamed_recovery_path(root))
"""


def test_i372_cli_recovery_writer_guard_is_role_based() -> None:
    """I372-T-AUTH-002: renaming a CLI-owned recovery writer cannot evade the guard."""

    writer_source = """
def _renamed_atomic_writer(path, payload): path.write_text(payload)
def _renamed_recovery_publisher(root, payload):
    marker = _renamed_recovery_path(root)
    _renamed_atomic_writer(marker, payload)
def _renamed_recovery_remover(root): os.unlink(_renamed_recovery_path(root))
def _renamed_recovery_stream_writer(root): _renamed_recovery_path(root).open(mode="w")
def _renamed_fd_writer(root): os.open(_renamed_recovery_path(root), os.O_WRONLY)
"""

    assert _cli_recovery_writer_roles(_RENAMED_RECOVERY_CLI_PREFIX + writer_source) == (
        "_renamed_fd_writer:os.open",
        "_renamed_recovery_publisher:_renamed_atomic_writer",
        "_renamed_recovery_remover:os.unlink",
        "_renamed_recovery_stream_writer:open",
    )


def test_i372_cli_has_no_legacy_distribution_writer_or_kernel_seam() -> None:
    """I372-T-AUTH-001: CLI remains an adapter, not a second distribution owner."""

    assert _cli_recovery_writer_roles(inspect.getsource(cli)) == ()

    tree = ast.parse(inspect.getsource(cli))
    definitions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    forbidden_writer_definitions = {
        "_write_atomic_regular_file",
        "_write_active_pathfile",
        "_write_spec_dock_version",
        "_write_distribution_retry_marker",
        "_remove_distribution_retry_marker",
        "_install_repo_root_shortcut",
    }
    assert definitions.isdisjoint(forbidden_writer_definitions)

    forbidden_kernel_edges = {
        "_rename_distribution_no_replace",
        "_swap_regular_distribution_target_if_bound",
        "_remove_distribution_target_if_bound",
        "DistributionStageOwnership",
        "apply_distribution_plan",
    }
    imported_from_managed_distribution = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "spec_dock.managed_distribution"
        for alias in node.names
    }
    assert imported_from_managed_distribution.isdisjoint(forbidden_kernel_edges)

    direct_private_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in forbidden_writer_definitions | forbidden_kernel_edges
    }
    assert not direct_private_calls

    managed_tree = ast.parse(inspect.getsource(managed_distribution))
    managed_definitions = {
        node.name for node in managed_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert {
        "execute_fresh_distribution",
        "execute_recognized_distribution",
        "execute_deprovision_distribution",
        "execute_explicit_spec_history_purge_distribution",
        "apply_distribution_plan",
    }.issubset(managed_definitions)
    assert any(
        isinstance(node, ast.ClassDef) and node.name == "DistributionStageOwnership" for node in managed_tree.body
    )


def _manifest_with(**overrides: object) -> dict[str, object]:
    manifest: dict[str, object] = {
        "schema_version": 1,
        "recognized_workspace_versions": [],
        "historical_current_identities": [],
        "trusted_consumer_manifests": [],
        "obsolete_exact_files": [],
        "historical_shortcuts": [],
    }
    manifest.update(overrides)
    return manifest


def _write_manifest(tmp_path: Path, manifest: dict[str, object]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "managed_distribution.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _regular_record(
    path: str,
    content: bytes,
    *,
    source_kind: str = "test-fixture",
    mode: int | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "path": path,
        "kind": "regular",
        "sha256": hashlib.sha256(content).hexdigest(),
        "source": {"kind": source_kind, "ref": "issue-360-test"},
    }
    if mode is not None:
        record["mode"] = mode
    return record


def _minimal_install_root(tmp_path: Path, content: bytes = b"current\n") -> Path:
    install_root = tmp_path / "install-root"
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    return install_root


def _minimal_scaffold_root(tmp_path: Path) -> Path:
    scaffold_root = tmp_path / "scaffold"
    for root in ("docs", "templates", "scripts", "system"):
        (scaffold_root / root).mkdir(parents=True)
    (scaffold_root / ".gitignore").write_text(".agent/\n", encoding="utf-8")
    runtime = scaffold_root / "scripts" / "spec-dock"
    runtime.write_text("#!/bin/sh\n", encoding="utf-8")
    runtime.chmod(0o755)
    seed = scaffold_root / "templates" / "root" / ".workbench" / "README.md"
    seed.parent.mkdir(parents=True)
    seed.write_text("workbench\n", encoding="utf-8")
    return scaffold_root


def _prepare_guarded_journal(
    store: OperationJournalStore,
    executable,
    *,
    package_version: str = "1.2.3",
):
    marker = store.prepare_legacy_guard(executable, package_version=package_version)
    store.bind_forward_guard(marker)
    return store.prepare(executable, package_version=package_version)


def _i370_tree_evidence(root: Path) -> dict[str, tuple[object, ...]]:
    """Capture no-follow identity and content evidence for a focused mutation test."""

    evidence: dict[str, tuple[object, ...]] = {}
    for path in (root, *root.rglob("*")):
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            payload: bytes | str | None = path.read_bytes()
        elif stat.S_ISLNK(info.st_mode):
            payload = str(path.readlink())
        else:
            payload = None
        relative = "." if path == root else path.relative_to(root).as_posix()
        evidence[relative] = (
            info.st_dev,
            info.st_ino,
            info.st_ctime_ns,
            info.st_mode,
            info.st_nlink,
            info.st_size,
            payload,
        )
    return evidence


def _i371_late_legacy_fixture(tmp_path: Path):
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    legacy_path = target_root / "spec-dock" / ".uninstall-retry.json"
    legacy_bytes = (json.dumps(managed_distribution._UNINSTALL_RETRY_MARKER_PAYLOAD, sort_keys=True) + "\n").encode()
    return install_root, scaffold_root, manifest_path, target_root, managed, root_identity, legacy_path, legacy_bytes


def _i371_recovery_fixture(tmp_path: Path, intent: str):
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        _managed,
        root_identity,
        _legacy_path,
        _legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    if intent == "purge":
        history_file = target_root / "spec-dock" / "initiatives" / "history.md"
        history_file.parent.mkdir(parents=True)
        history_file.write_bytes(b"history\n")
        assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    else:
        assessment = managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    marker = store.prepare_legacy_guard(executable, package_version="1.2.3")
    prepared = store.prepare(executable, package_version="1.2.3")
    return (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        root_identity,
        assessment,
        executable,
        store,
        marker,
        prepared,
        target_root / "spec-dock/.distribution-retry.json",
        target_root / "spec-dock/.distribution-journal.json",
    )


def test_s20_public_catalog_is_derived_from_physical_install_root() -> None:
    plan = build_distribution_plan(INSTALL_ROOT, manifest_path=MANIFEST_PATH)

    assert {asset.path for asset in plan.current_assets} == EXPECTED_CURRENT_PATHS
    assert plan.actions == ()
    assert plan.manifest.schema_version == 1
    assert plan.manifest.historical_current_identities == (EXPECTED_HISTORICAL_CURRENT_IDENTITY,)
    obsolete_paths = {item["path"] for item in plan.manifest.obsolete_exact_files}
    assert len(obsolete_paths) == 81
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert obsolete_paths >= EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert ".agents/host-adapters/meta.json" in obsolete_paths
    assert any(path.startswith(".codex/") for path in obsolete_paths)
    assert any(path.startswith(".github/agents/") for path in obsolete_paths)
    for asset in plan.current_assets:
        source = INSTALL_ROOT / asset.path
        assert asset.identity.kind == "regular"
        assert asset.identity.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
        assert asset.identity.mode == stat.S_IMODE(source.stat().st_mode)


def test_s20_current_catalog_bytes_are_not_duplicated_in_historical_manifest() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert set(raw) == MANIFEST_FIELDS
    assert not any(key in raw for key in {"current", "current_assets", "current_catalog"})
    assert raw["historical_current_identities"] == [EXPECTED_HISTORICAL_CURRENT_IDENTITY]
    current_identities = {
        path.relative_to(INSTALL_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in INSTALL_ROOT.rglob("*")
        if path.is_file()
    }
    assert all(
        identity["sha256"] != current_identities[identity["path"]] for identity in raw["historical_current_identities"]
    )
    obsolete_paths = {item["path"] for item in raw["obsolete_exact_files"]}
    assert len(obsolete_paths) == 81
    assert obsolete_paths >= EXPECTED_OBSOLETE_SKILL_PATHS
    assert obsolete_paths >= EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert not any(item["path"] in EXPECTED_CURRENT_PATHS for item in raw["obsolete_exact_files"])
    unproven_entrypoints = {
        item["path"]: item
        for item in raw["obsolete_exact_files"]
        if item["path"] in EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    }
    assert set(unproven_entrypoints) == EXPECTED_UNPROVEN_LEGACY_ENTRYPOINT_PATHS
    assert all(item["identities"] == [] for item in unproven_entrypoints.values())
    assert all(item["on_unknown"] == "preserve-and-block" for item in unproven_entrypoints.values())


def test_s55_historical_catalog_is_bound_to_reproducible_git_source() -> None:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = list(raw["historical_current_identities"])
    records.extend(identity for item in raw["obsolete_exact_files"] for identity in item["identities"])

    assert records
    assert {identity["source"]["ref"] for identity in records} == {HISTORICAL_COMMIT}
    source_available = subprocess.run(
        ["git", "cat-file", "-e", f"{HISTORICAL_COMMIT}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    assert source_available.returncode == 0, "historical source commit is unavailable in this checkout"
    for identity in records:
        path = identity["path"]
        provider_path = f"src/spec_dock/assets/install_root/{path}"
        content = subprocess.check_output(["git", "show", f"{HISTORICAL_COMMIT}:{provider_path}"])
        tree = subprocess.check_output(
            ["git", "ls-tree", HISTORICAL_COMMIT, "--", provider_path],
            text=True,
        )
        mode = tree.split(maxsplit=1)[0]
        assert mode in {"100644", "100755"}
        assert identity["sha256"] == hashlib.sha256(content).hexdigest()
        assert identity["mode"] == int(mode, 8) & 0o777


def test_s20_build_is_read_only(tmp_path: Path) -> None:
    install_root = tmp_path / "install_root"
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"ci\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    before = {
        path.relative_to(tmp_path): (path.read_bytes() if path.is_file() else None)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    build_distribution_plan(install_root, manifest_path=manifest_path)

    after = {
        path.relative_to(tmp_path): (path.read_bytes() if path.is_file() else None)
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_i368_workspace_assessment_is_read_only_and_binds_contract(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    before = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="update",
    )

    after = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before
    assert assessment.intent == "update"
    assert assessment.blockers == ()
    assert len(assessment.contract_identity) == 64
    assert {action.action for action in assessment.actions} == {"create"}


def test_i368_blocked_assessment_cannot_issue_executable_authority(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    collision = target_root / ".github" / "workflows" / "ci.yml"
    collision.parent.mkdir(parents=True)
    collision.write_bytes(b"user-owned\n")

    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="init-force",
    )

    assert assessment.blockers
    with pytest.raises(DistributionPlanError, match="blocker"):
        build_executable_mutation_plan(assessment)


def test_i370_deprovision_intent_maps_to_uninstall_plan_and_removal_grammar(
    tmp_path: Path,
) -> None:
    """I370-T-DOM-001: deprovision is the journal intent for uninstall plans."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")

    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert assessment.intent == "deprovision"
    assert assessment.distribution_plan.operation == "uninstall"
    assert {action.action for action in assessment.actions} == {"prune", "remove-empty-directory"}
    executable = build_executable_mutation_plan(assessment)
    assert {action.action for action in executable.actions} == {"prune", "remove-empty-directory"}
    assert any(action.path == ".github/workflows/ci.yml" for action in executable.actions)

    forged_action = replace(
        assessment.actions[0],
        action="create",
        provenance="missing",
        reason="forged-deprovision-create",
    )
    forged_assessment = replace(
        assessment,
        distribution_plan=replace(assessment.distribution_plan, actions=(forged_action,)),
        actions=(forged_action,),
    )
    with pytest.raises(DistributionPlanError, match="not allowed"):
        build_executable_mutation_plan(forged_assessment)


def test_i371_purge_assessment_is_typed_and_write_free(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history = target_root / "spec-dock" / "initiatives"
    history.mkdir(parents=True)
    history_file = history / "unknown-name.bin"
    history_file.write_bytes(b"arbitrary history\n")
    workbench = target_root / "spec-dock" / ".workbench" / "sentinel.txt"
    workbench.parent.mkdir(parents=True)
    workbench.write_bytes(b"preserve\n")
    before = _i370_tree_evidence(target_root)
    root_info = target_root.stat()

    assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert assessment.intent == "purge"
    assert assessment.explicit_spec_history_purge_contract is not None
    purge_contract = assessment.explicit_spec_history_purge_contract
    assert purge_contract.authority == "explicit-spec-history-purge"
    assert purge_contract.history_root == "spec-dock/initiatives"
    assert purge_contract.history_entries[0].relative_path == "spec-dock/initiatives/unknown-name.bin"
    assert any(action.path == "spec-dock/initiatives/unknown-name.bin" for action in assessment.actions)
    assert _i370_tree_evidence(target_root) == before


def test_i371_purge_assessment_reuses_one_coherent_history_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "history.md"
    history_file.parent.mkdir(parents=True)
    original_content = b"history-before-second-observation\n"
    history_file.write_bytes(original_content)
    root_info = target_root.stat()
    original_observe = managed_distribution._observe_target
    root_observations = 0

    def observe_with_changed_second_root_observation(root: Path, relative_path: str):
        nonlocal root_observations
        observed = original_observe(root, relative_path)
        if relative_path == "spec-dock/initiatives":
            root_observations += 1
            if root_observations == 2:
                history_file.write_bytes(b"history-after-second-observation\n")
        return observed

    monkeypatch.setattr(managed_distribution, "_observe_target", observe_with_changed_second_root_observation)
    assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    purge_contract = assessment.explicit_spec_history_purge_contract
    assert purge_contract is not None
    entry = next(
        item for item in purge_contract.history_entries if item.relative_path == "spec-dock/initiatives/history.md"
    )
    snapshot = dict(assessment.distribution_plan.target_snapshots)[entry.relative_path].target
    assert root_observations == 1
    assert assessment.blockers == ()
    assert entry.sha256 == hashlib.sha256(original_content).hexdigest()
    assert snapshot.identity is not None
    assert snapshot.identity.sha256 == entry.sha256
    assert snapshot.device == entry.device
    assert snapshot.inode == entry.inode
    assert snapshot.ctime_ns == entry.ctime_ns


def test_i371_purge_assessment_registers_nested_empty_history_directories(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_root = target_root / "spec-dock" / "initiatives"
    (history_root / "empty-leaf").mkdir(parents=True)
    (history_root / "nested" / "empty-nested").mkdir(parents=True)
    (history_root / "nested" / "history.md").write_bytes(b"history\n")
    workbench = target_root / "spec-dock" / ".workbench" / "sentinel.txt"
    workbench.parent.mkdir(parents=True)
    workbench.write_bytes(b"preserve\n")
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )

    history_directories = {
        "spec-dock/initiatives",
        "spec-dock/initiatives/empty-leaf",
        "spec-dock/initiatives/nested",
        "spec-dock/initiatives/nested/empty-nested",
    }
    assert assessment.blockers == ()
    assert history_directories <= {
        action.path for action in assessment.actions if action.action == "remove-empty-directory"
    }

    result = managed_distribution.execute_explicit_spec_history_purge_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "completed", result.reason
    assert not history_root.exists()
    assert workbench.read_bytes() == b"preserve\n"
    assert outside.read_bytes() == b"outside\n"


def test_i371_purge_apply_removes_history_and_preserves_workbench(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "arbitrary.md"
    history_file.parent.mkdir(parents=True)
    history_file.write_bytes(b"history\n")
    workbench = target_root / "spec-dock" / ".workbench" / "sentinel.txt"
    workbench.parent.mkdir(parents=True)
    workbench.write_bytes(b"preserve\n")
    root_info = target_root.stat()

    result = managed_distribution.execute_explicit_spec_history_purge_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert result.status == "completed"
    assert result.intent == "purge"
    assert not history_file.exists()
    assert workbench.read_bytes() == b"preserve\n"
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()
    history_actions = [action for action in result.action_outcomes if action.category == "spec_history"]
    assert len(history_actions) == 1
    assert history_actions[0].path == "spec-dock/initiatives"
    assert history_actions[0].status == "removed"


def test_i371_purge_forward_recovers_same_plan_after_history_checkpoint_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "history.md"
    history_file.parent.mkdir(parents=True)
    history_file.write_bytes(b"history\n")
    workbench = target_root / "spec-dock" / ".workbench" / "sentinel.txt"
    workbench.parent.mkdir(parents=True)
    workbench.write_bytes(b"preserve\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def fail_after_history_checkpoint(self, journal, completed_paths):
        nonlocal interrupted
        result = original_checkpoint(self, journal, completed_paths)
        if not interrupted and history_file.relative_to(target_root).as_posix() in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected purge checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_history_checkpoint)
    first = managed_distribution.execute_explicit_spec_history_purge_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert first.status == "recovery_required", first.reason
    assert first.intent == "purge"
    assert interrupted is True
    assert not history_file.exists()
    assert (target_root / "spec-dock/.distribution-retry.json").is_file()
    assert (target_root / "spec-dock/.distribution-journal.json").is_file()

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = managed_distribution.execute_explicit_spec_history_purge_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert second.status == "completed", second.reason
    assert second.intent == "purge"
    assert workbench.read_bytes() == b"preserve\n"
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()


def test_i371_late_legacy_before_guard_publish_is_manual_and_write_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    original = OperationJournalStore.prepare_legacy_guard
    injected = False

    def create_legacy_before_guard(self, plan, **kwargs):
        nonlocal injected
        legacy_path.write_bytes(legacy_bytes)
        injected = True
        return original(self, plan, **kwargs)

    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", create_legacy_before_guard)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.reason == "legacy-marker-unconvertible"
    assert result.retry_policy == "manual-recovery"
    assert legacy_path.read_bytes() == legacy_bytes
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()
    assert managed.read_bytes() == b"managed\n"


def test_i371_late_legacy_after_guard_publish_is_dual_and_journal_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    original = OperationJournalStore.prepare_legacy_guard
    injected = False

    def create_legacy_after_guard(self, plan, **kwargs):
        nonlocal injected
        marker = original(self, plan, **kwargs)
        legacy_path.write_bytes(legacy_bytes)
        injected = True
        return marker

    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", create_legacy_after_guard)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert result.retry_policy == "manual-recovery"
    assert managed.read_bytes() == b"managed\n"
    assert legacy_path.read_bytes() == legacy_bytes
    assert (target_root / "spec-dock/.distribution-retry.json").is_file()
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()


def test_i371_late_legacy_after_journal_prepare_preserves_prepared_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    original = OperationJournalStore.prepare
    injected = False

    def create_legacy_after_journal(self, plan, **kwargs):
        nonlocal injected
        journal = original(self, plan, **kwargs)
        legacy_path.write_bytes(legacy_bytes)
        injected = True
        return journal

    monkeypatch.setattr(OperationJournalStore, "prepare", create_legacy_after_journal)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert result.retry_policy == "manual-recovery"
    assert managed.read_bytes() == b"managed\n"
    assert legacy_path.read_bytes() == legacy_bytes
    journal = OperationJournalStore(target_root)._read(root_identity)
    assert journal.status == "prepared"
    assert all(action.checkpoint == "pending" for action in journal.actions)


@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_guard_only_prepare_race_before_journal_is_manual_and_write_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    intent: str,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    if intent == "purge":
        history_file = target_root / "spec-dock" / "initiatives" / "history.md"
        history_file.parent.mkdir(parents=True)
        history_file.write_bytes(b"history\n")
        assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    else:
        assessment = managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    store.prepare_legacy_guard(executable, package_version="1.2.3")
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    guard_bytes = guard_path.read_bytes()
    original_write = OperationJournalStore._write
    injected = False

    def inject_before_journal_write(self, journal, **kwargs):
        nonlocal injected
        if not injected:
            legacy_path.write_bytes(legacy_bytes)
            injected = True
        return original_write(self, journal, **kwargs)

    monkeypatch.setattr(OperationJournalStore, "_write", inject_before_journal_write)
    execute = (
        managed_distribution.execute_explicit_spec_history_purge_distribution
        if intent == "purge"
        else managed_distribution.execute_deprovision_distribution
    )
    result = execute(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.intent == intent
    assert result.reason == "dual-recovery-state"
    assert result.retry_policy == "manual-recovery"
    assert result.applied_paths == ()
    assert result.pending_paths == ()
    managed_distribution._validate_deprovision_process_result(result, intent=intent)
    assert managed.read_bytes() == b"managed\n"
    assert guard_path.read_bytes() == guard_bytes
    assert legacy_path.read_bytes() == legacy_bytes
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()


@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_guard_only_prepare_race_after_journal_publish_is_journal_progress_manual(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    intent: str,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    if intent == "purge":
        history_file = target_root / "spec-dock" / "initiatives" / "history.md"
        history_file.parent.mkdir(parents=True)
        history_file.write_bytes(b"history\n")
        assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    else:
        assessment = managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    store.prepare_legacy_guard(executable, package_version="1.2.3")
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    guard_bytes = guard_path.read_bytes()
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    original_rename = managed_distribution._rename_distribution_no_replace
    injected = False

    def inject_after_journal_publish(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal injected
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not injected and destination_name == journal_path.name:
            legacy_path.write_bytes(legacy_bytes)
            injected = True

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", inject_after_journal_publish)
    execute = (
        managed_distribution.execute_explicit_spec_history_purge_distribution
        if intent == "purge"
        else managed_distribution.execute_deprovision_distribution
    )
    result = execute(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.intent == intent
    assert result.reason == "dual-recovery-state"
    assert result.retry_policy == "manual-recovery"
    assert result.applied_paths == ()
    assert result.pending_paths == tuple(sorted((action.path for action in executable.actions), key=os.fsencode))
    managed_distribution._validate_deprovision_process_result(result, intent=intent)
    assert managed.read_bytes() == b"managed\n"
    assert guard_path.read_bytes() == guard_bytes
    assert legacy_path.read_bytes() == legacy_bytes
    journal = OperationJournalStore(target_root)._read(root_identity)
    assert journal.status == "prepared"
    assert all(action.checkpoint == "pending" for action in journal.actions)


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("displacement", ["rename-aside", "unlink"])
@pytest.mark.parametrize("with_recorder", [False, True])
def test_i371_remove_target_post_rename_foreign_quarantine_is_never_rolled_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    displacement: str,
    with_recorder: bool,
) -> None:
    target = tmp_path / "target"
    foreign_source = tmp_path / "foreign-source"
    aside = tmp_path / "operation-owned-aside"
    quarantine_name = "target.remove"
    payload = b"operation-owned\n"
    link_target = "history-entry"
    if kind == "regular":
        target.write_bytes(payload)
        foreign_source.write_bytes(payload)
        target.chmod(0o640)
        foreign_source.chmod(0o640)
    else:
        target.symlink_to(link_target)
        foreign_source.symlink_to(link_target)
    expected = target.lstat()
    foreign_before = foreign_source.lstat()
    parent_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    held_fd: int | None = None
    if kind == "regular":
        held_fd = os.open(
            target.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
    original_rename = managed_distribution._rename_distribution_no_replace
    injected = False
    restore_attempts = 0
    recorded: list[DistributionStageOwnership] = []
    held_identity = (os.fstat(held_fd).st_dev, os.fstat(held_fd).st_ino) if held_fd is not None else None

    def interpose_after_real_rename(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal injected, restore_attempts
        if source_name == quarantine_name and destination_name == target.name:
            restore_attempts += 1
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not injected and source_name == target.name and destination_name == quarantine_name:
            if displacement == "rename-aside":
                os.rename(
                    quarantine_name,
                    aside.name,
                    src_dir_fd=destination_parent_fd,
                    dst_dir_fd=destination_parent_fd,
                )
            else:
                os.unlink(quarantine_name, dir_fd=destination_parent_fd)
            os.rename(
                foreign_source.name,
                quarantine_name,
                src_dir_fd=destination_parent_fd,
                dst_dir_fd=destination_parent_fd,
            )
            injected = True

    monkeypatch.setattr(
        managed_distribution,
        "_rename_distribution_no_replace",
        interpose_after_real_rename,
    )
    try:
        with pytest.raises(DistributionApplyError, match="identity"):
            managed_distribution._remove_distribution_target_if_bound(
                parent_fd,
                target.name,
                expected,
                held_fd=held_fd,
                identity_message="identity",
                transition_path="target" if with_recorder else None,
                transition_name=quarantine_name,
                transition_recorder=recorded.append if with_recorder else None,
            )
    finally:
        if held_fd is not None:
            os.close(held_fd)
        os.close(parent_fd)

    assert injected is True
    assert restore_attempts == 0
    assert not target.exists() and not target.is_symlink()
    foreign_quarantine = tmp_path / quarantine_name
    current_foreign = foreign_quarantine.lstat()
    assert (current_foreign.st_dev, current_foreign.st_ino) == (foreign_before.st_dev, foreign_before.st_ino)
    assert current_foreign.st_mode == foreign_before.st_mode
    if kind == "regular":
        assert foreign_quarantine.read_bytes() == payload
    else:
        assert foreign_quarantine.readlink() == Path(link_target)
    if displacement == "rename-aside":
        assert (aside.lstat().st_dev, aside.lstat().st_ino) == (expected.st_dev, expected.st_ino)
        if kind == "regular":
            assert held_identity is not None
            assert (aside.lstat().st_dev, aside.lstat().st_ino) == held_identity
    else:
        assert not aside.exists() and not aside.is_symlink()
    assert not foreign_source.exists() and not foreign_source.is_symlink()
    if with_recorder:
        assert len(recorded) == 1
        lease = recorded[0]
        assert lease.path == "target"
        assert lease.stage_name == quarantine_name
        assert lease.role == "predecessor-quarantine"
        assert (lease.device, lease.inode, lease.ctime_ns) == (0, 0, 0)
        assert lease.file_type == kind


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("with_recorder", [False, True])
def test_i371_cleanup_failure_after_bound_quarantine_never_pathname_rolls_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    with_recorder: bool,
) -> None:
    target = tmp_path / "target"
    foreign_source = tmp_path / "foreign-source"
    aside = tmp_path / "operation-owned-aside"
    quarantine_name = "target.remove"
    payload = b"operation-owned\n"
    link_target = "history-entry"
    if kind == "regular":
        target.write_bytes(payload)
        foreign_source.write_bytes(payload)
        target.chmod(0o640)
        foreign_source.chmod(0o640)
    else:
        target.symlink_to(link_target)
        foreign_source.symlink_to(link_target)
    expected = target.lstat()
    foreign_before = foreign_source.lstat()
    parent_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    held_fd: int | None = None
    if kind == "regular":
        held_fd = os.open(
            target.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
    recorded: list[DistributionStageOwnership] = []
    original_cleanup = managed_distribution._remove_distribution_stage_if_owned
    original_backup_cleanup = managed_distribution._unlink_distribution_quarantine_with_backup
    injected = False

    def replace_quarantine_with_foreign() -> None:
        nonlocal injected
        if injected:
            return
        os.rename(quarantine_name, aside.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.rename(
            foreign_source.name,
            quarantine_name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
        injected = True
        raise DistributionApplyError("injected cleanup failure")

    def fail_direct_cleanup(parent, stage_name, created, *, strict=False, **kwargs):
        if stage_name == quarantine_name:
            replace_quarantine_with_foreign()
        return original_cleanup(parent, stage_name, created, strict=strict, **kwargs)

    def fail_backup_cleanup(parent, stage_name, *args, **kwargs):
        if stage_name == quarantine_name:
            replace_quarantine_with_foreign()
        return original_backup_cleanup(parent, stage_name, *args, **kwargs)

    if with_recorder:
        monkeypatch.setattr(
            managed_distribution,
            "_unlink_distribution_quarantine_with_backup",
            fail_backup_cleanup,
        )
    else:
        monkeypatch.setattr(
            managed_distribution,
            "_remove_distribution_stage_if_owned",
            fail_direct_cleanup,
        )
    try:
        with pytest.raises(DistributionApplyError, match="identity"):
            managed_distribution._remove_distribution_target_if_bound(
                parent_fd,
                target.name,
                expected,
                held_fd=held_fd,
                identity_message="identity",
                transition_path="target" if with_recorder else None,
                transition_name=quarantine_name,
                transition_recorder=recorded.append if with_recorder else None,
            )
    finally:
        if held_fd is not None:
            os.close(held_fd)
        os.close(parent_fd)

    assert injected is True
    assert not target.exists() and not target.is_symlink()
    foreign_quarantine = tmp_path / quarantine_name
    current_foreign = foreign_quarantine.lstat()
    assert (current_foreign.st_dev, current_foreign.st_ino) == (foreign_before.st_dev, foreign_before.st_ino)
    assert current_foreign.st_mode == foreign_before.st_mode
    if kind == "regular":
        assert foreign_quarantine.read_bytes() == payload
    else:
        assert foreign_quarantine.readlink() == Path(link_target)
    assert (aside.lstat().st_dev, aside.lstat().st_ino) == (expected.st_dev, expected.st_ino)
    assert not foreign_source.exists() and not foreign_source.is_symlink()
    if with_recorder:
        assert [lease.role for lease in recorded] == ["predecessor-quarantine", "predecessor-quarantine"]
        assert (recorded[0].device, recorded[0].inode, recorded[0].ctime_ns) == (0, 0, 0)
        assert (recorded[1].device, recorded[1].inode) == (expected.st_dev, expected.st_ino)


@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_journal_post_rename_foreign_quarantine_preserves_intent_and_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    intent: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    if intent == "purge":
        history_file = target_root / "spec-dock" / "initiatives" / "history.md"
        history_file.parent.mkdir(parents=True)
        history_file.write_bytes(b"history\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    foreign_source = tmp_path / "foreign-source"
    foreign_source.write_bytes(b"managed\n")
    expected = managed.lstat()
    foreign_before = foreign_source.lstat()
    aside = managed.parent / "operation-owned-aside"
    original_rename = managed_distribution._rename_distribution_no_replace
    injected = False
    quarantine_path: Path | None = None

    def interpose_after_real_rename(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal injected, quarantine_path
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not injected and source_name == managed.name and destination_name.startswith(".spec-dock-file-"):
            quarantine_path = managed.parent / destination_name
            quarantine_path.rename(aside)
            foreign_source.rename(quarantine_path)
            injected = True

    monkeypatch.setattr(
        managed_distribution,
        "_rename_distribution_no_replace",
        interpose_after_real_rename,
    )
    execute = (
        managed_distribution.execute_explicit_spec_history_purge_distribution
        if intent == "purge"
        else managed_distribution.execute_deprovision_distribution
    )
    result = execute(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert quarantine_path is not None
    assert result.status == "recovery_required", result.reason
    assert result.intent == intent
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    assert guard_path.is_file()
    assert journal_path.is_file()
    guard = managed_distribution._read_distribution_retry_marker(target_root, expected_intent=intent)
    assert guard is not None
    assert guard.operation == intent
    assert guard.purpose == managed_distribution._journal_guard_purpose_for_intent(intent)
    journal = OperationJournalStore(target_root)._read(root_identity, expected_intent=intent)
    assert journal.intent == intent
    assert journal.authority == managed_distribution._journal_authority_for_intent(intent)
    predecessor_leases = tuple(
        lease
        for lease in journal.staging_leases
        if lease.path == managed.relative_to(target_root).as_posix() and lease.role == "predecessor-quarantine"
    )
    assert predecessor_leases
    assert all((lease.device, lease.inode, lease.ctime_ns) == (0, 0, 0) for lease in predecessor_leases)
    assert all(
        not (lease.device == foreign_before.st_dev and lease.inode == foreign_before.st_ino)
        for lease in predecessor_leases
    )
    assert not managed.exists() and not managed.is_symlink()
    foreign_quarantine = quarantine_path.lstat()
    assert (foreign_quarantine.st_dev, foreign_quarantine.st_ino) == (foreign_before.st_dev, foreign_before.st_ino)
    assert foreign_quarantine.st_mode == foreign_before.st_mode
    assert quarantine_path.read_bytes() == b"managed\n"
    aside_info = aside.lstat()
    assert (aside_info.st_dev, aside_info.st_ino) == (expected.st_dev, expected.st_ino)
    assert aside.read_bytes() == b"managed\n"
    assert not foreign_source.exists() and not foreign_source.is_symlink()


def test_i371_stage_cleanup_has_no_direct_unlink_escape() -> None:
    source = inspect.getsource(managed_distribution._remove_distribution_stage_if_owned)
    signature = inspect.signature(managed_distribution._remove_distribution_stage_if_owned)

    assert "direct_unlink" not in signature.parameters
    assert "direct_unlink" not in source
    assert "os.unlink(stage_name" not in source


def test_i371_recovery_has_no_restore_or_private_publish_authority() -> None:
    recovery_source = inspect.getsource(OperationJournalStore._recover_quarantined_recovery_entry)
    quarantine_source = inspect.getsource(OperationJournalStore._quarantine_and_remove)

    assert not hasattr(OperationJournalStore, "_restore_quarantined_entry")
    assert not hasattr(OperationJournalStore, "_publish_exact_recovery_bytes_no_replace")
    assert "_restore_quarantined_entry" not in recovery_source
    assert "_publish_exact_recovery_bytes_no_replace" not in recovery_source
    assert "_restore_quarantined_entry" not in quarantine_source


def test_i371_recovery_is_observation_only_for_exact_quarantine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An exact quarantine is evidence for manual recovery, never a restore source."""

    canonical = tmp_path / "entry.json"
    quarantine = tmp_path / "entry.json.remove"
    raw = b"exact recovery evidence\n"
    canonical.write_bytes(raw)
    canonical.chmod(0o640)
    parent_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    held_fd = os.open(
        canonical.name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    expected = os.fstat(held_fd)
    os.rename(canonical.name, quarantine.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    original_rename = managed_distribution._rename_distribution_no_replace
    rename_calls: list[tuple[str, str]] = []

    def observe_rename(source_parent_fd, source_name, destination_parent_fd, destination_name):
        rename_calls.append((source_name, destination_name))
        return original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", observe_rename)
    try:
        outcome = OperationJournalStore(tmp_path)._recover_quarantined_recovery_entry(
            parent_fd,
            canonical.name,
            quarantine.name,
            held_fd,
            raw,
            expected,
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            failure_reason="recovery-failed",
            pre_delete_check=None,
        )
    finally:
        os.close(held_fd)
        os.close(parent_fd)

    assert outcome == "manual-conflict"
    assert rename_calls == []
    assert not canonical.exists() and not canonical.is_symlink()
    quarantine_info = quarantine.lstat()
    assert (quarantine_info.st_dev, quarantine_info.st_ino) == (expected.st_dev, expected.st_ino)
    assert quarantine.read_bytes() == raw


@pytest.mark.parametrize("foreign_kind", ["regular", "symlink"])
def test_i371_recovery_foreign_canonical_never_creates_private_restore(
    tmp_path: Path,
    foreign_kind: str,
) -> None:
    """Foreign canonical evidence is preserved without creating a candidate .restore path."""

    canonical = tmp_path / "entry.json"
    aside = tmp_path / "entry.json.aside"
    raw = b"owned recovery evidence\n"
    canonical.write_bytes(raw)
    canonical.chmod(0o640)
    parent_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    held_fd = os.open(
        canonical.name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    expected = os.fstat(held_fd)
    os.rename(canonical.name, aside.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    if foreign_kind == "regular":
        canonical.write_bytes(b"foreign canonical\n")
        canonical.chmod(0o640)
    else:
        canonical.symlink_to("foreign-target")
    foreign_before = canonical.lstat()
    try:
        outcome = OperationJournalStore(tmp_path)._recover_quarantined_recovery_entry(
            parent_fd,
            canonical.name,
            "entry.json.remove",
            held_fd,
            raw,
            expected,
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            failure_reason="recovery-failed",
            pre_delete_check=None,
        )
    finally:
        os.close(held_fd)
        os.close(parent_fd)

    assert outcome == "manual-conflict"
    current = canonical.lstat()
    assert (current.st_dev, current.st_ino, current.st_mode, current.st_nlink) == (
        foreign_before.st_dev,
        foreign_before.st_ino,
        foreign_before.st_mode,
        foreign_before.st_nlink,
    )
    if foreign_kind == "regular":
        assert canonical.read_bytes() == b"foreign canonical\n"
    else:
        assert canonical.readlink() == Path("foreign-target")
    assert aside.read_bytes() == raw
    assert tuple(tmp_path.glob("*.restore")) == ()


@pytest.mark.parametrize("displacement", ["rename-aside", "unlink"])
def test_i371_exact_recovery_hardlink_is_preserved_without_pathname_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    displacement: str,
) -> None:
    """A canonical/quarantine hardlink pair is manual, never auto-cleaned."""

    canonical = tmp_path / "entry.json"
    quarantine = tmp_path / "entry.json.remove"
    foreign_source = tmp_path / "foreign-source"
    aside = tmp_path / "operation-owned-aside"
    raw = b"exact recovery evidence\n"
    canonical.write_bytes(raw)
    canonical.chmod(0o640)
    os.link(canonical, quarantine)
    foreign_source.write_bytes(raw)
    foreign_source.chmod(0o640)

    parent_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    held_fd = os.open(
        canonical.name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    expected = os.fstat(held_fd)
    original_unlink = managed_distribution.os.unlink
    unlink_calls: list[str] = []

    def interpose_private_quarantine_unlink(name, *args, **kwargs):
        if name == quarantine.name:
            unlink_calls.append(name)
            if displacement == "rename-aside":
                os.rename(quarantine.name, aside.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            else:
                original_unlink(quarantine.name, dir_fd=parent_fd)
            os.rename(
                foreign_source.name,
                quarantine.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", interpose_private_quarantine_unlink)
    try:
        outcome = OperationJournalStore(tmp_path)._recover_quarantined_recovery_entry(
            parent_fd,
            canonical.name,
            quarantine.name,
            held_fd,
            raw,
            expected,
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            failure_reason="recovery-failed",
            pre_delete_check=None,
        )
    finally:
        os.close(held_fd)
        os.close(parent_fd)

    assert outcome == "manual-conflict"
    assert unlink_calls == []
    canonical_info = canonical.lstat()
    quarantine_info = quarantine.lstat()
    assert (canonical_info.st_dev, canonical_info.st_ino) == (
        quarantine_info.st_dev,
        quarantine_info.st_ino,
    )
    assert canonical_info.st_nlink == quarantine_info.st_nlink == 2
    assert canonical.read_bytes() == quarantine.read_bytes() == raw
    assert foreign_source.read_bytes() == raw
    assert not aside.exists()


@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_quarantine_preserved_durable_journal_maps_to_same_intent_recovery(
    tmp_path: Path,
    intent: Literal["deprovision", "purge"],
) -> None:
    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        assessment,
        executable,
        _store,
        _marker,
        prepared,
        _guard_path,
        _journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)

    result = managed_distribution._distribution_process_result_from_state(
        assessment,
        prepared,
        state="quarantine-preserved",
        executable=executable,
        intent=intent,
    )

    assert result.status == "recovery_required"
    assert result.reason == f"{intent}-recovery-required"
    assert result.retry_policy == "manual-recovery"
    assert tuple(error.code for error in result.errors) == (f"{intent}-recovery-required",)
    assert result.reason != "dual-recovery-state"


@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_quarantine_preserved_guard_only_maps_to_guard_recovery_semantics(
    tmp_path: Path,
    intent: Literal["deprovision", "purge"],
) -> None:
    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        assessment,
        executable,
        _store,
        _marker,
        _prepared,
        _guard_path,
        _journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)

    result = managed_distribution._distribution_process_result_from_state(
        assessment,
        None,
        state="quarantine-preserved",
        executable=executable,
        intent=intent,
    )

    assert result.status == "recovery_required"
    assert result.reason == f"{intent}-guard-only"
    assert result.phase == "marker-write"
    assert result.retry_policy == "manual-recovery"
    assert tuple(error.code for error in result.errors) == (f"{intent}-recovery-required",)
    assert result.reason != "dual-recovery-state"


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_terminal_metadata_post_unlink_fsync_failure_is_typed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
) -> None:
    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    if entry == "guard":
        selected_path = guard_path

        def operation() -> None:
            store.remove_legacy_marker(marker)

    else:
        completed = store.write(
            replace(
                prepared,
                status="completed",
                actions=tuple(replace(action, checkpoint="verified") for action in prepared.actions),
                created_parent_bindings=(),
            )
        )
        selected_path = journal_path

        def operation() -> None:
            store.remove_completed(completed)

    original_unlink = managed_distribution.os.unlink
    original_fsync = managed_distribution.os.fsync
    unlinked = False
    fsync_failed = False

    def observe_unlink(name, *args, **kwargs):
        nonlocal unlinked
        result = original_unlink(name, *args, **kwargs)
        if isinstance(name, str) and name == selected_path.name:
            unlinked = True
        return result

    def fail_once_after_unlink(fd: int) -> None:
        nonlocal fsync_failed
        if unlinked and not fsync_failed:
            fsync_failed = True
            raise OSError(errno.EIO, "injected post-unlink fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    monkeypatch.setattr(managed_distribution.os, "fsync", fail_once_after_unlink)
    with pytest.raises(DistributionApplyError) as raised:
        operation()

    assert unlinked is True
    assert fsync_failed is True
    assert raised.value.recovery_metadata_state == "metadata-cleanup-conflict"
    assert not selected_path.exists() and not selected_path.is_symlink()
    assert not tuple(target_root.joinpath("spec-dock").glob("*.remove"))
    assert not tuple(target_root.joinpath("spec-dock").glob("*.gc"))
    assert not tuple(target_root.joinpath("spec-dock").glob("*.restore"))


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_terminal_cleanup_state_less_failure_is_manual_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        _managed,
        root_identity,
        _legacy_path,
        _legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    if intent == "purge":
        history_file = target_root / "spec-dock" / "initiatives" / "history.md"
        history_file.parent.mkdir(parents=True)
        history_file.write_bytes(b"history\n")
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    selected_path = guard_path if entry == "guard" else journal_path
    original_unlink = managed_distribution.os.unlink
    original_fsync = managed_distribution.os.fsync
    unlinked = False
    fsync_failed = False

    def observe_unlink(name, *args, **kwargs):
        nonlocal unlinked
        result = original_unlink(name, *args, **kwargs)
        if isinstance(name, str) and name == selected_path.name:
            unlinked = True
        return result

    def fail_once_after_unlink(fd: int) -> None:
        nonlocal fsync_failed
        if unlinked and not fsync_failed:
            fsync_failed = True
            raise OSError(errno.EIO, "injected terminal post-unlink fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    monkeypatch.setattr(managed_distribution.os, "fsync", fail_once_after_unlink)
    execute = (
        managed_distribution.execute_explicit_spec_history_purge_distribution
        if intent == "purge"
        else managed_distribution.execute_deprovision_distribution
    )
    result = execute(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert unlinked is True
    assert fsync_failed is True
    assert result.status == "recovery_required"
    assert result.phase == "marker-finalization"
    assert result.pending_paths == ()
    assert result.retry_policy == "manual-recovery"
    assert result.last_completed_phase == "marker-finalized"
    assert "spec-dock/.distribution-journal.json" in result.failed_paths
    assert not any(name in str(result) for name in (".remove", ".restore", ".stage"))


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_late_legacy_after_metadata_swap_cleans_swapped_out_predecessor_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
) -> None:
    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    legacy_path = target_root / "spec-dock/.uninstall-retry.json"
    legacy_bytes = (json.dumps(managed_distribution._UNINSTALL_RETRY_MARKER_PAYLOAD, sort_keys=True) + "\n").encode()
    canonical_path = guard_path if entry == "guard" else journal_path
    original_swap = managed_distribution._swap_regular_distribution_target_if_bound
    injected = False
    successor_bytes: bytes | None = None

    def inject_after_selected_swap(*args, **kwargs):
        nonlocal injected, successor_bytes
        result = original_swap(*args, **kwargs)
        destination = args[2]
        if destination == canonical_path.name and not injected:
            successor_bytes = canonical_path.read_bytes()
            legacy_path.write_bytes(legacy_bytes)
            injected = True
        return result

    monkeypatch.setattr(
        managed_distribution,
        "_swap_regular_distribution_target_if_bound",
        inject_after_selected_swap,
    )
    with pytest.raises(DistributionApplyError) as raised:
        if entry == "guard":
            store.prepare_legacy_guard(
                None,
                package_version=marker.package_version,
                replace_marker=marker,
            )
        else:
            store.mark_executing(prepared)

    assert injected is True
    assert successor_bytes is not None
    assert raised.value.recovery_metadata_state == "dual-recovery-state"
    assert canonical_path.read_bytes() == successor_bytes
    assert legacy_path.read_bytes() == legacy_bytes
    assert not tuple(target_root.joinpath("spec-dock").glob(".distribution-journal-*.stage"))
    assert not tuple(target_root.joinpath("spec-dock").glob(".distribution-retry-*.stage"))


def test_i371_late_legacy_after_target_unlink_leaves_action_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        install_root,
        scaffold_root,
        manifest_path,
        target_root,
        managed,
        root_identity,
        legacy_path,
        legacy_bytes,
    ) = _i371_late_legacy_fixture(tmp_path)
    original = managed_distribution._remove_distribution_target_if_bound
    injected = False

    def create_legacy_after_unlink(*args, **kwargs):
        nonlocal injected
        result = original(*args, **kwargs)
        if not injected and args[1] == managed.name:
            legacy_path.write_bytes(legacy_bytes)
            injected = True
        return result

    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", create_legacy_after_unlink)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert result.retry_policy == "manual-recovery"
    assert not managed.exists()
    assert legacy_path.read_bytes() == legacy_bytes
    journal = OperationJournalStore(target_root)._read(root_identity)
    managed_distribution._validate_deprovision_process_result(result, intent="deprovision")
    assert result.phase == "uninstall-apply"
    assert result.last_completed_phase == "marker-written"
    assert result.plan_digest == journal.plan_digest
    target_record = next(action for action in journal.actions if action.path == ".github/workflows/ci.yml")
    assert target_record.checkpoint == "pending"
    expected_pending = tuple(
        sorted(
            (action.path for action in journal.actions if action.checkpoint == "pending"),
            key=os.fsencode,
        )
    )
    assert result.pending_paths == expected_pending
    assert set(result.pending_paths).issubset(result.failed_paths)
    outcome_by_path = {outcome.path: outcome for outcome in result.action_outcomes}
    assert all(outcome_by_path[path].status == "pending" for path in expected_pending)


@pytest.mark.parametrize(
    ("journal_intent", "request_intent", "journal_authority"),
    (
        ("purge", "deprovision", "explicit-spec-history-purge"),
        ("deprovision", "purge", "managed-distribution-deprovision"),
        ("deprovision", "deprovision", "arbitrary-invalid-authority"),
    ),
)
def test_i371_cross_intent_recovery_mismatch_is_manual_and_write_free(
    tmp_path: Path,
    journal_intent: str,
    request_intent: str,
    journal_authority: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "history.md"
    history_file.parent.mkdir(parents=True)
    history_file.write_bytes(b"history\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    if journal_intent == "purge":
        journal_assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    else:
        journal_assessment = managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    executable = build_executable_mutation_plan(journal_assessment)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    assert journal.intent == journal_intent
    if journal_authority != managed_distribution._journal_authority_for_intent(
        cast("managed_distribution.JournaledDistributionIntent", journal_intent)
    ):
        raw = json.loads(store.path.read_text(encoding="utf-8"))
        raw["authority"] = journal_authority
        store.path.write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
    journal_bytes = store.path.read_bytes()
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    guard_bytes = guard_path.read_bytes()
    before = _i370_tree_evidence(target_root)

    if request_intent == "purge":
        result = managed_distribution.execute_explicit_spec_history_purge_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            package_version="1.2.3",
            apply=True,
            expected_root_identity=root_identity,
        )
    else:
        result = managed_distribution.execute_deprovision_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            package_version="1.2.3",
            apply=True,
            expected_root_identity=root_identity,
        )

    assert result.status == "recovery_required"
    assert result.intent == request_intent
    assert result.reason == f"{request_intent}-recovery-mismatch"
    assert result.retry_policy == "manual-recovery"
    assert result.pending_paths == ()
    assert _i370_tree_evidence(target_root) == before
    assert store.path.read_bytes() == journal_bytes
    assert guard_path.read_bytes() == guard_bytes


@pytest.mark.parametrize("binding_field", ("root_binding", "workspace_binding"))
def test_i371_cross_intent_journal_binding_mismatch_is_classified_before_binding_read(
    tmp_path: Path,
    binding_field: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "history.md"
    history_file.parent.mkdir(parents=True)
    history_file.write_bytes(b"history\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    raw = json.loads(store.path.read_text(encoding="utf-8"))
    if binding_field == "root_binding":
        raw[binding_field] = {"device": root_info.st_dev, "inode": root_info.st_ino + 1}
    else:
        raw[binding_field]["inode"] += 1
    store.path.write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
    journal_bytes = store.path.read_bytes()
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    guard_bytes = guard_path.read_bytes()
    before = _i370_tree_evidence(target_root)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert journal.intent == "purge"
    assert result.status == "recovery_required"
    assert result.retry_policy == "manual-recovery"
    assert _i370_tree_evidence(target_root) == before
    assert store.path.read_bytes() == journal_bytes
    assert guard_path.read_bytes() == guard_bytes


def test_i371_canonical_cross_discriminator_precedes_malformed_journal_fields() -> None:
    raw = {
        "schema_version": 2,
        "protocol_version": 2,
        "intent": "purge",
        "authority": "explicit-spec-history-purge",
        "root_binding": "malformed-later-field",
    }

    with pytest.raises(DistributionApplyError) as raised:
        managed_distribution._parse_operation_journal(
            json.dumps(raw).encode("utf-8"),
            expected_intent="deprovision",
        )

    assert raised.value.recovery_mismatch_kind == "intent-authority"


def test_i371_unsupported_journal_intent_does_not_infer_authority_mismatch() -> None:
    raw = {
        "schema_version": 2,
        "protocol_version": 2,
        "intent": {"malformed": True},
        "authority": "explicit-spec-history-purge",
    }

    with pytest.raises(DistributionApplyError) as raised:
        managed_distribution._parse_operation_journal(json.dumps(raw).encode("utf-8"), expected_intent="deprovision")

    assert raised.value.recovery_mismatch_kind is None


def test_i371_cross_intent_guard_only_is_manual_without_journal_creation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history_file = target_root / "spec-dock" / "initiatives" / "history.md"
    history_file.parent.mkdir(parents=True)
    history_file.write_bytes(b"history\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_explicit_spec_history_purge_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    marker = store.prepare_legacy_guard(executable, package_version="1.2.3")
    guard_path = target_root / "spec-dock/.distribution-retry.json"
    guard_bytes = guard_path.read_bytes()
    before = _i370_tree_evidence(target_root)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert marker.operation == "purge"
    assert result.status == "recovery_required"
    assert result.retry_policy == "manual-recovery"
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()
    assert guard_path.read_bytes() == guard_bytes
    assert _i370_tree_evidence(target_root) == before


def test_i368_forged_assessment_cannot_prune_outside_manifest_authority(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    sentinel = target_root / "user-owned.txt"
    sentinel.parent.mkdir()
    sentinel.write_text("keep\n", encoding="utf-8")
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="update",
    )
    forged_action = DistributionAction(
        path="user-owned.txt",
        operation="update",
        action="prune",
        provenance="historical",
        reason="obsolete-exact",
    )
    original_snapshot = assessment.distribution_plan.target_snapshots[0][1]
    forged_plan = managed_distribution.replace(
        assessment.distribution_plan,
        actions=(forged_action,),
        target_snapshots=((forged_action.path, original_snapshot),),
    )
    forged_assessment = managed_distribution.replace(
        assessment,
        distribution_plan=forged_plan,
        actions=(forged_action,),
        blockers=(),
    )

    with pytest.raises(DistributionPlanError, match="outside obsolete authority"):
        build_executable_mutation_plan(forged_assessment)

    assert sentinel.read_text(encoding="utf-8") == "keep\n"


@pytest.mark.parametrize("forged_action_name", ["upgrade", "prune"])
def test_i369_fresh_action_grammar_is_enforced_at_every_mutation_boundary(
    tmp_path: Path,
    forged_action_name: Literal["upgrade", "prune"],
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    sentinel = target_root / "user-owned.txt"
    sentinel.write_text("keep\n", encoding="utf-8")
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="fresh",
    )
    original_action = next(action for action in assessment.actions if action.action == "create")
    forged_action = replace(
        original_action,
        action=forged_action_name,
        provenance="historical" if forged_action_name == "prune" else "current",
        reason=f"forged-fresh-{forged_action_name}",
    )
    forged_plan = replace(assessment.distribution_plan, actions=(forged_action,))
    forged_assessment = replace(
        assessment,
        distribution_plan=forged_plan,
        actions=(forged_action,),
    )

    with pytest.raises(DistributionPlanError, match="not allowed for its intent"):
        build_executable_mutation_plan(forged_assessment)

    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    original_record = next(record for record in journal.actions if record.path == original_action.path)
    forged_record = replace(original_record, action=forged_action_name)
    forged_journal = replace(
        journal,
        actions=tuple(forged_record if record.path == original_action.path else record for record in journal.actions),
    )
    with pytest.raises(DistributionApplyError, match="journal-plan-mismatch"):
        managed_distribution._assert_journal_action_contract(assessment, forged_journal)

    with pytest.raises(DistributionApplyError, match="not allowed for its intent"):
        apply_distribution_plan(forged_plan)

    assert sentinel.read_text(encoding="utf-8") == "keep\n"


def test_i368_executable_plan_digest_is_stable_for_equivalent_assessment(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    first = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    second = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )

    assert first.plan_digest == second.plan_digest
    assert len(first.plan_digest) == 64
    assert first.root_identity == second.root_identity


def test_i369_legacy_create_upgrade_fixed_link_count_guard_migrates(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec-dock").mkdir()
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    legacy_digest = managed_distribution._executable_plan_digest(
        executable,
        legacy_adopt_postconditions=True,
        legacy_adopt_fixed_link_count=True,
        legacy_create_upgrade_fixed_link_count=True,
    )

    assert legacy_digest != executable.plan_digest
    assert legacy_digest in managed_distribution._executable_plan_digest_candidates(executable)

    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    legacy_guard = store.prepare_legacy_guard(
        None,
        package_version="1.2.3",
        replace_marker=guard,
        plan_digest_override=legacy_digest,
    )
    store.bind_forward_guard(legacy_guard)
    journal = store.prepare(executable, package_version="1.2.3")

    assert journal.plan_digest == executable.plan_digest
    marker = json.loads((target_root / "spec-dock/.distribution-retry.json").read_text(encoding="utf-8"))
    assert marker["plan_digest"] == executable.plan_digest


def test_i368_generated_asset_path_must_be_canonical_and_repository_relative(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    content = b"outside\n"
    generated = DistributionAsset(
        path="../outside.txt",
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=0o644,
        ),
        generated_content=content,
    )

    with pytest.raises(DistributionPlanError, match="repository-relative"):
        build_distribution_plan(
            install_root,
            manifest_path=manifest_path,
            generated_assets=(generated,),
        )


def test_i368_journal_prepare_records_bound_actions_before_target_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )

    journal = OperationJournalStore(target_root).prepare(executable, package_version="1.2.3")

    assert journal.status == "prepared"
    assert journal.plan_digest == executable.plan_digest
    assert journal.actions
    assert {action.checkpoint for action in journal.actions} == {"pending"}
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()


def test_i369_fresh_journal_uses_isolated_authority_and_directory_actions(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="fresh",
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    assert guard.purpose == "fresh-journal-forward-only"
    store.bind_forward_guard(guard)
    journal = store.prepare(executable, package_version="1.2.3")
    payload = json.loads((target_root / "spec-dock/.distribution-journal.json").read_text(encoding="utf-8"))

    assert journal.intent == "fresh"
    assert journal.authority == "fresh-distribution-provisioning"
    assert payload["schema_version"] == managed_distribution._DISTRIBUTION_JOURNAL_SCHEMA_VERSION
    assert {action.action for action in journal.actions} >= {"ensure-directory", "create"}
    assert payload["authority"] == "fresh-distribution-provisioning"
    assert {binding.relative_path for binding in journal.created_parent_bindings} >= {
        "spec-dock/.agent",
        "spec-dock/initiatives",
    }


def test_i370_deprovision_guard_and_journal_use_exact_authority_pair(tmp_path: Path) -> None:
    """I370-T-JRN-001: deprovision guard and journal cannot use another authority."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    executable = build_executable_mutation_plan(
        managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        )
    )

    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    assert guard.operation == "deprovision"
    assert guard.purpose == "deprovision-journal-forward-only"
    store.bind_forward_guard(guard)
    journal = store.prepare(executable, package_version="1.2.3")

    assert journal.intent == "deprovision"
    assert journal.authority == "managed-distribution-deprovision"
    resumed = OperationJournalStore(target_root).resume(executable, package_version="1.2.3")
    assert resumed == journal


def test_i370_deprovision_journal_has_strict_wire_and_reachable_state_table(
    tmp_path: Path,
) -> None:
    """I370-T-JRN-001: protocol-2 persists authority and only reachable checkpoints."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    executable = build_executable_mutation_plan(
        managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=DistributionRootIdentity(
                device=root_info.st_dev,
                inode=root_info.st_ino,
            ),
        )
    )
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    payload = managed_distribution._journal_payload(journal)

    assert payload["authority"] == "managed-distribution-deprovision"
    assert set(payload) >= {
        "preservation_witnesses",
        "absence_witnesses",
        "source_semantic_identities",
        "generated_state_contract_digest",
    }
    assert managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(journal)) == journal

    all_published = tuple(replace(action, checkpoint="published") for action in journal.actions)
    verifying = replace(journal, status="verifying", actions=all_published)
    assert managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(verifying)) == verifying
    completed = replace(
        verifying,
        status="completed",
        actions=tuple(replace(action, checkpoint="verified") for action in all_published),
    )
    assert managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(completed)) == completed

    unreachable = (
        replace(journal, actions=(replace(journal.actions[0], checkpoint="published"), *journal.actions[1:])),
        replace(
            journal,
            status="executing",
            actions=(replace(journal.actions[0], checkpoint="verified"), *journal.actions[1:]),
        ),
        replace(journal, status="verifying"),
        replace(verifying, actions=(replace(verifying.actions[0], checkpoint="verified"), *verifying.actions[1:])),
        replace(verifying, status="completed"),
    )
    for forged in unreachable:
        with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
            managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(forged))

    forged_provenance = replace(
        journal,
        actions=(replace(journal.actions[0], provenance="unknown"), *journal.actions[1:]),
    )
    with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
        managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(forged_provenance))

    physical_source = json.loads(json.dumps(payload))
    physical_source["source_semantic_identities"][0]["device"] = 99
    with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
        managed_distribution._parse_operation_journal(
            (json.dumps(physical_source, sort_keys=True, separators=(",", ":")) + "\n").encode()
        )

    parent_index = next(index for index, action in enumerate(journal.actions) if action.path == ".github")
    parent_action = journal.actions[parent_index]
    evidence = parent_action.precondition["immediate_child_evidence"][0]
    descendant_evidence = {
        **evidence,
        "child_path": ".github/workflows/ci.yml",
        "child_kind": "leaf",
        "action_path": ".github/workflows/ci.yml",
        "expected_postcondition": {"path": ".github/workflows/ci.yml", "exists": False},
    }
    forged_parent = replace(
        parent_action,
        precondition={
            **parent_action.precondition,
            "immediate_child_evidence": [descendant_evidence],
        },
    )
    forged_subsumption = replace(
        journal,
        actions=tuple(
            forged_parent if index == parent_index else action for index, action in enumerate(journal.actions)
        ),
    )
    with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
        managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(forged_subsumption))


def test_i370_deprovision_journal_accepts_independent_nonprefix_leaf_progress(
    tmp_path: Path,
) -> None:
    """I370-T-JRN-001: executing persists any proved leaf subset, not an artificial prefix."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    second_source = install_root / ".agents" / "skills" / "example" / "SKILL.md"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    first_target = target_root / ".github" / "workflows" / "ci.yml"
    first_target.parent.mkdir(parents=True)
    first_target.write_bytes(b"managed\n")
    second_target = target_root / ".agents" / "skills" / "example" / "SKILL.md"
    second_target.parent.mkdir(parents=True)
    second_target.write_bytes(b"second\n")
    root_info = target_root.stat()
    executable = build_executable_mutation_plan(
        managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=DistributionRootIdentity(
                device=root_info.st_dev,
                inode=root_info.st_ino,
            ),
        )
    )
    journal = _prepare_guarded_journal(OperationJournalStore(target_root), executable)
    leaf_indexes = [index for index, action in enumerate(journal.actions) if action.action == "prune"]
    assert len(leaf_indexes) == 2
    later_leaf_index = leaf_indexes[1]
    executing = replace(
        journal,
        status="executing",
        actions=tuple(
            replace(action, checkpoint="published") if index == later_leaf_index else action
            for index, action in enumerate(journal.actions)
        ),
    )

    assert managed_distribution._parse_operation_journal(managed_distribution._journal_bytes(executing)) == executing


def test_i370_deprovision_typed_result_maps_every_reachable_durable_state(
    tmp_path: Path,
) -> None:
    """I370-T-RESULT-001: one typed builder maps the reachable durable state table."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(
            device=root_info.st_dev,
            inode=root_info.st_ino,
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    prepared = store.prepare(executable, package_version="1.2.3")
    executing = replace(prepared, status="executing")
    leaf_path = next(action.path for action in executing.actions if action.action == "prune")
    leaf_published = replace(
        executing,
        actions=tuple(
            replace(action, checkpoint="published") if action.path == leaf_path else action
            for action in executing.actions
        ),
    )
    all_published = replace(
        executing,
        actions=tuple(replace(action, checkpoint="published") for action in executing.actions),
    )
    verifying = replace(all_published, status="verifying")
    completed = replace(
        verifying,
        status="completed",
        actions=tuple(replace(action, checkpoint="verified") for action in verifying.actions),
    )

    state_table = (
        (prepared, "uninstall-apply", "marker-written"),
        (executing, "uninstall-apply", "marker-written"),
        (leaf_published, "root-cleanup", "uninstall-applied"),
        (all_published, "post-verify", "uninstall-applied"),
        (verifying, "post-verify", "uninstall-applied"),
    )
    for journal, expected_phase, expected_last_completed in state_table:
        result = managed_distribution._distribution_process_result_from_state(
            assessment,
            journal,
            failure_paths=(leaf_path,) if journal is executing else (),
        )
        expected_pending = tuple(
            sorted(
                {action.path for action in journal.actions if action.checkpoint == "pending"},
                key=os.fsencode,
            )
        )
        assert result.status == "recovery_required"
        assert result.phase == expected_phase
        assert result.last_completed_phase == expected_last_completed
        assert result.pending_paths == expected_pending
        assert set(expected_pending).issubset(result.failed_paths)
        assert result.errors
        assert result.retry_policy == "same-keep-command"
        if journal is executing:
            leaf_outcome = next(outcome for outcome in result.action_outcomes if outcome.path == leaf_path)
            assert leaf_outcome.status == "failed"
            assert leaf_outcome.error == "Managed distribution deprovision action failed."

    completed_with_guard = managed_distribution._distribution_process_result_from_state(
        assessment,
        completed,
    )
    assert completed_with_guard.phase == "marker-finalization"
    assert completed_with_guard.last_completed_phase == "post-verified"
    assert completed_with_guard.pending_paths == ()
    assert completed_with_guard.failed_paths == ("spec-dock/.distribution-retry.json",)

    store.remove_legacy_marker(guard)
    completed_only = managed_distribution._distribution_process_result_from_state(
        assessment,
        completed,
    )
    assert completed_only.phase == "marker-finalization"
    assert completed_only.last_completed_phase == "marker-finalized"
    assert completed_only.pending_paths == ()
    assert completed_only.failed_paths == ("spec-dock/.distribution-journal.json",)
    assert "DistributionProcessResult(" not in inspect.getsource(managed_distribution.execute_deprovision_distribution)
    assert "DistributionProcessResult(" not in inspect.getsource(managed_distribution._execute_deprovision_journal_plan)


def test_i370_generated_state_producer_accepts_exact_active_state_and_blocks_unknown(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: one producer proves current slots and blocks unknown entries."""

    target_root = tmp_path / "consumer"
    active_dir = target_root / "spec-dock" / "active"
    agent_dir = target_root / "spec-dock" / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()
    for layer in ("initiative", "epic", "issue"):
        placeholder = target_root / "spec-dock" / "system" / "active-none" / layer
        placeholder.mkdir(parents=True)
        (active_dir / layer).symlink_to(Path("../system/active-none") / layer)
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": None,
            "epic": None,
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=root_identity,
    )

    assert contract.blockers == ()
    assert {entry.path for entry in contract.entries} == {
        "spec-dock/active/initiative",
        "spec-dock/active/epic",
        "spec-dock/active/issue",
        "spec-dock/.agent/active.json",
    }
    assert len(contract.contract_digest) == 64

    (active_dir / "unknown.txt").write_text("user owned\n", encoding="utf-8")
    blocked = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=root_identity,
    )
    assert [action.path for action in blocked.blockers] == ["spec-dock/active/unknown.txt"]
    assert blocked.blockers[0].reason == "unknown-generated-state-entry"


def test_i370_generated_state_regular_read_rejects_same_bytes_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-OWN-001/I370-T-ID-001: producer bytes stay bound to one observed inode."""

    target_root = tmp_path / "consumer"
    agent_dir = target_root / "spec-dock" / ".agent"
    agent_dir.mkdir(parents=True)
    active = agent_dir / "active.json"
    active.write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": None,
            "epic": None,
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    original_generated_entry = managed_distribution._generated_entry
    observed_inode: int | None = None
    replacement_inode: int | None = None

    def replace_after_observation(*args, **kwargs):
        nonlocal observed_inode, replacement_inode
        entry = original_generated_entry(*args, **kwargs)
        if kwargs.get("expected_kind") == "regular" and args[1] == "spec-dock/.agent/active.json":
            assert entry is not None
            observed_inode = entry.observed.inode
            replacement = active.with_name("active.replacement")
            replacement.write_bytes(active.read_bytes())
            replacement.chmod(active.stat().st_mode)
            replacement.replace(active)
            replacement_inode = active.stat().st_ino
        return entry

    monkeypatch.setattr(managed_distribution, "_generated_entry", replace_after_observation)
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert observed_inode is not None
    assert replacement_inode is not None
    assert replacement_inode != observed_inode
    assert all(entry.path != "spec-dock/.agent/active.json" for entry in contract.entries)
    assert any(
        action.path == "spec-dock/.agent/active.json" and action.reason == "generated-state-invalid"
        for action in contract.blockers
    )


def test_i370_generated_state_replacement_before_classification_blocks_apply(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-OWN-001/I370-T-RACE-001: producer identity reaches first mutation."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    agent_dir = target_root / "spec-dock" / ".agent"
    agent_dir.mkdir(parents=True)
    active = agent_dir / "active.json"
    active.write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": None,
            "epic": None,
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    original_classify_target = managed_distribution._classify_target
    original_inode = active.stat().st_ino
    replacement_inode: int | None = None

    def replace_before_classification(*args, **kwargs):
        nonlocal replacement_inode
        if replacement_inode is None:
            replacement = tmp_path / "active-classification-replacement"
            replacement.write_bytes(active.read_bytes())
            replacement.chmod(stat.S_IMODE(active.stat().st_mode))
            replacement.replace(active)
            replacement_inode = active.stat().st_ino
        return original_classify_target(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_classify_target", replace_before_classification)
    root_info = target_root.stat()
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert replacement_inode is not None
    assert replacement_inode != original_inode
    assert result.status == "blocked"
    assert result.reason == "deprovision-preflight-blocked"
    assert "spec-dock/.agent/active.json" in result.failed_paths
    active_action = next(action for action in result.actions if action.path == "spec-dock/.agent/active.json")
    assert active_action.action == "preserve"
    assert active_action.blocked is True
    assert active.stat().st_ino == replacement_inode
    assert active.read_bytes().endswith(b"\n")
    assert managed.read_bytes() == b"managed\n"
    assert outside.read_bytes() == b"outside\n"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_generated_state_producer_blocks_cross_artifact_batch_conflict(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: present index/tree artifacts must be one coherent batch."""

    target_root = tmp_path / "consumer"
    active_dir = target_root / "spec-dock" / "active"
    agent_dir = target_root / "spec-dock" / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()
    for layer in ("initiative", "epic", "issue"):
        placeholder = target_root / "spec-dock" / "system" / "active-none" / layer
        placeholder.mkdir(parents=True)
        (active_dir / layer).symlink_to(Path("../system/active-none") / layer)
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": None,
            "epic": None,
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    common: dict[str, object] = {
        "schema_version": 2,
        "active": None,
        "warnings": [],
        "root": "spec-dock/initiatives",
        "deps": {
            "valid": True,
            "error": None,
            "issue_edges": [],
            "edge_direction": "depends_on (dependent -> prerequisite)",
        },
    }
    (agent_dir / "index-all.json").write_text(
        json.dumps({**common, "generated_at": "2026-08-25T12:00:00+09:00", "projection": "full-history", "nodes": {}})
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree-all.json").write_text(
        json.dumps({**common, "generated_at": "2026-08-25T12:00:01+09:00", "tree": []}) + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert {action.reason for action in contract.blockers} == {"generated-state-batch-conflict"}
    assert {action.path for action in contract.blockers} == {
        "spec-dock/.agent/index-all.json",
        "spec-dock/.agent/tree-all.json",
    }


def test_i370_generated_state_rejects_impossible_issue_status_pair(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001/I370-T-BLK-001: producer-impossible issue state blocks both projections."""

    target_root = tmp_path / "consumer"
    agent_dir = target_root / "spec-dock" / ".agent"
    agent_dir.mkdir(parents=True)
    document_surfaces = {
        "canonical_docs": [
            {
                "kind": kind,
                "path": "spec-dock/initiatives/init-local-00001/requirement.md",
                "present": True,
            }
            for kind in ("requirement", "design", "plan", "report")
        ],
        "future_artifacts": {
            "path": "spec-dock/initiatives/init-local-00001/artifacts",
            "present": False,
        },
        "legacy_discussions": {
            "path": "spec-dock/initiatives/init-local-00001/discussions",
            "present": False,
        },
    }
    initiative = {
        "id": "init-local-00001",
        "type": "initiative",
        "title": "Initiative",
        "path": "spec-dock/initiatives/init-local-00001",
        "document_surfaces": document_surfaces,
        "parent_id": None,
        "initiative_id": None,
        "epic_id": None,
        "children": ["epic-00001"],
    }
    epic = {
        "id": "epic-00001",
        "type": "epic",
        "title": "Epic",
        "path": "spec-dock/initiatives/init-local-00001/epics/epic-00001",
        "document_surfaces": document_surfaces,
        "parent_id": "init-local-00001",
        "initiative_id": "init-local-00001",
        "epic_id": None,
        "children": ["iss-00001"],
    }
    issue = {
        "id": "iss-00001",
        "type": "issue",
        "title": "Issue",
        "path": "spec-dock/initiatives/init-local-00001/epics/epic-00001/issues/iss-00001",
        "document_surfaces": document_surfaces,
        "parent_id": "epic-00001",
        "initiative_id": "init-local-00001",
        "epic_id": "epic-00001",
        "children": [],
        "status": "open",
        "authority": "github",
        "effective_status": "open",
        "source": "github",
        "stale": False,
        "last_sync_at": None,
        "deps": None,
    }
    nodes = {item["id"]: item for item in (initiative, epic, issue)}
    common = {
        "schema_version": 2,
        "generated_at": "2026-08-25T12:00:00+09:00",
        "active": None,
        "warnings": [],
        "root": "spec-dock/initiatives",
        "deps": {
            "valid": True,
            "error": None,
            "issue_edges": [],
            "edge_direction": "depends_on (dependent -> prerequisite)",
        },
    }
    (agent_dir / "index-all.json").write_text(
        json.dumps({
            **common,
            "projection": "full-history",
            "nodes": {node_id: {**payload, "depends_on": []} for node_id, payload in nodes.items()},
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree-all.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()
    valid = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert valid.blockers == ()

    issue["status"] = "done"
    (agent_dir / "index-all.json").write_text(
        json.dumps({
            **common,
            "projection": "full-history",
            "nodes": {node_id: {**payload, "depends_on": []} for node_id, payload in nodes.items()},
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree-all.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )

    blocked = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert {action.path for action in blocked.blockers} == {
        "spec-dock/.agent/index-all.json",
        "spec-dock/.agent/tree-all.json",
    }
    assert all(
        entry.path not in {"spec-dock/.agent/index-all.json", "spec-dock/.agent/tree-all.json"}
        for entry in blocked.entries
    )

    issue["status"] = "open"
    issue["effective_status"] = "open"
    (agent_dir / "index-all.json").write_text(
        json.dumps({
            **common,
            "projection": "full-history",
            "nodes": {node_id: {**payload, "depends_on": []} for node_id, payload in nodes.items()},
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree-all.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )
    current_nodes = {
        node_id: {key: value for key, value in payload.items() if key != "depends_on"}
        for node_id, payload in nodes.items()
    }
    (agent_dir / "index.json").write_text(
        json.dumps({
            **common,
            "projection": "current-future",
            "nodes": current_nodes,
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )

    valid_current_pair = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert not any(
        blocker.path in {"spec-dock/.agent/index.json", "spec-dock/.agent/tree.json"}
        for blocker in valid_current_pair.blockers
    )

    tree_issue = {
        **issue,
        "status": "done",
        "effective_status": "done",
    }
    (agent_dir / "tree.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [tree_issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )
    mismatched_tree = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert any(
        blocker.path == "spec-dock/.agent/tree.json" and blocker.reason == "generated-state-invalid"
        for blocker in mismatched_tree.blockers
    )
    assert all(entry.path != "spec-dock/.agent/tree.json" for entry in mismatched_tree.entries)

    issue["status"] = "done"
    issue["effective_status"] = "done"
    current_nodes["iss-00001"] = {
        **current_nodes["iss-00001"],
        "status": "done",
        "effective_status": "done",
    }
    (agent_dir / "index.json").write_text(
        json.dumps({
            **common,
            "projection": "current-future",
            "nodes": current_nodes,
        })
        + "\n",
        encoding="utf-8",
    )

    impossible_pair = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert any(
        blocker.path == "spec-dock/.agent/index.json" and blocker.reason == "generated-state-invalid"
        for blocker in impossible_pair.blockers
    )
    assert all(entry.path != "spec-dock/.agent/index.json" for entry in impossible_pair.entries)

    issue["status"] = "open"
    issue["effective_status"] = "open"
    current_nodes["iss-00001"] = {
        **current_nodes["iss-00001"],
        "status": "open",
        "effective_status": "open",
    }
    (agent_dir / "index-all.json").unlink()
    (agent_dir / "tree-all.json").unlink()
    (agent_dir / "index.json").write_text(
        json.dumps({
            **common,
            "projection": "current-future",
            "nodes": current_nodes,
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree.json").write_text(
        json.dumps({
            **common,
            "tree": [
                {
                    **initiative,
                    "epics": [{**epic, "issues": [issue]}],
                }
            ],
        })
        + "\n",
        encoding="utf-8",
    )
    current_only = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert not any(
        blocker.path in {"spec-dock/.agent/index.json", "spec-dock/.agent/tree.json"}
        for blocker in current_only.blockers
    )


def test_i370_current_future_deps_include_only_todo_issue_endpoints() -> None:
    full_nodes: dict[str, dict[str, object]] = {
        "iss-open": {
            "type": "issue",
            "status": "open",
            "parent_id": None,
            "children": [],
            "depends_on": [],
        },
        "iss-done": {
            "type": "issue",
            "status": "done",
            "parent_id": None,
            "children": [],
            "depends_on": [],
        },
    }
    full_deps: dict[str, object] = {
        "valid": True,
        "error": None,
        "edge_direction": "depends_on (dependent -> prerequisite)",
        "issue_edges": [
            {"from": "iss-open", "to": "iss-open"},
            {"from": "iss-open", "to": "iss-done"},
        ],
    }
    full: dict[str, object] = {"nodes": full_nodes, "deps": full_deps}
    current_deps: dict[str, object] = {
        **full_deps,
        "issue_edges": [{"from": "iss-open", "to": "iss-open"}],
    }
    current: dict[str, object] = {
        "nodes": {"iss-open": {key: value for key, value in full_nodes["iss-open"].items() if key != "depends_on"}},
        "deps": current_deps,
    }

    assert managed_distribution._generated_current_future_matches_full_history(full, current)
    current_with_done_edge: dict[str, object] = {
        **current,
        "deps": {
            **current_deps,
            "issue_edges": full_deps["issue_edges"],
        },
    }
    assert not managed_distribution._generated_current_future_matches_full_history(full, current_with_done_edge)


def test_i370_deps_issues_rejects_impossible_issue_status_pair_without_writes(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001/I370-T-BLK-001: deps-issues keeps producer status authority narrow."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    deps_path = target_root / "spec-dock" / ".agent" / "deps-issues.json"
    deps_path.parent.mkdir(parents=True)
    issue_node: dict[str, object] = {
        "id": "iss-00001",
        "type": "issue",
        "title": "Issue",
        "parent_id": None,
        "initiative_id": None,
        "epic_id": None,
        "status": "open",
        "authority": "github",
        "effective_status": "open",
        "source": "github",
        "stale": False,
        "last_sync_at": None,
        "ready": True,
        "depends_on": [],
        "issue_blockers": [],
        "node_blockers": [],
        "state": "open",
    }
    payload = {
        "schema_version": 2,
        "generated_at": "2026-08-25T12:00:00+09:00",
        "projection": "issue-readiness-with-dependency-context",
        "source": {"sync_state": "readiness_evaluation", "schema_version": 2},
        "deps": {"valid": True, "error": None},
        "nodes": {"iss-00001": issue_node},
        "edges": [],
        "dependency_contexts": [],
        "edge_direction": "depends_on (dependent -> prerequisite)",
    }
    deps_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    valid = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=root_identity,
    )
    assert "spec-dock/.agent/deps-issues.json" in {entry.path for entry in valid.entries}
    issue_node["effective_status"] = "done"
    deps_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    before = _i370_tree_evidence(target_root)

    blocked = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=root_identity,
    )
    assert {
        (action.path, action.reason)
        for action in blocked.blockers
        if action.path == "spec-dock/.agent/deps-issues.json"
    } == {("spec-dock/.agent/deps-issues.json", "generated-state-invalid")}
    assert "spec-dock/.agent/deps-issues.json" not in {entry.path for entry in blocked.entries}

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    assert result.status == "blocked"
    assert result.reason == "deprovision-preflight-blocked"
    assert "spec-dock/.agent/deps-issues.json" in result.failed_paths
    assert _i370_tree_evidence(target_root) == before
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_generated_state_producer_rejects_malformed_nested_node_shape(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: a top-level discriminator cannot prove malformed nested state."""

    target_root = tmp_path / "consumer"
    agent_dir = target_root / "spec-dock" / ".agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "index-all.json").write_text(
        json.dumps({
            "schema_version": 2,
            "generated_at": "2026-08-25T12:00:00+09:00",
            "active": None,
            "warnings": [],
            "root": "spec-dock/initiatives",
            "projection": "full-history",
            "deps": {
                "valid": True,
                "error": None,
                "issue_edges": [],
                "edge_direction": "depends_on (dependent -> prerequisite)",
            },
            "nodes": {
                "init-local-00001": None,
            },
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert all(entry.path != "spec-dock/.agent/index-all.json" for entry in contract.entries)
    assert any(
        action.path == "spec-dock/.agent/index-all.json" and action.reason == "generated-state-invalid"
        for action in contract.blockers
    )


def test_i370_version_marker_read_rejects_observation_to_read_rebind(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-RACE-001: version bytes remain bound to the observed filesystem object."""

    target_root = tmp_path / "consumer"
    version_path = target_root / "spec-dock" / "spec-dock.version"
    version_path.parent.mkdir(parents=True)
    version_path.write_text("9.9.9\n", encoding="ascii")
    manifest = managed_distribution.DistributionManifest(
        schema_version=1,
        recognized_workspace_versions=({"version": "0.2.3"},),
        historical_current_identities=(),
        trusted_consumer_manifests=(),
        obsolete_exact_files=(),
        historical_shortcuts=(),
    )
    original_read_fd_bytes = managed_distribution._read_fd_bytes
    switched = False

    def replace_before_read(fd: int) -> bytes:
        nonlocal switched
        if not switched:
            switched = True
            replacement = version_path.with_name("spec-dock.version.replacement")
            replacement.write_text("0.2.3\n", encoding="ascii")
            replacement.replace(version_path)
        return original_read_fd_bytes(fd)

    monkeypatch.setattr(managed_distribution, "_read_fd_bytes", replace_before_read)

    with pytest.raises(managed_distribution.DistributionPlanError, match="identity"):
        managed_distribution._deprovision_version_asset(target_root, manifest)

    assert switched


def test_i370_generated_state_producer_blocks_index_tree_node_set_conflict(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: an index and its tree must describe the same node set."""

    target_root = tmp_path / "consumer"
    active_dir = target_root / "spec-dock" / "active"
    agent_dir = target_root / "spec-dock" / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()
    for layer in ("initiative", "epic", "issue"):
        placeholder = target_root / "spec-dock" / "system" / "active-none" / layer
        placeholder.mkdir(parents=True)
        (active_dir / layer).symlink_to(Path("../system/active-none") / layer)
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": None,
            "epic": None,
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    common = {
        "schema_version": 2,
        "generated_at": "2026-08-25T12:00:00+09:00",
        "active": None,
        "warnings": [],
        "root": "spec-dock/initiatives",
        "deps": {
            "valid": True,
            "error": None,
            "issue_edges": [],
            "edge_direction": "depends_on (dependent -> prerequisite)",
        },
    }
    (agent_dir / "index-all.json").write_text(
        json.dumps({
            **common,
            "projection": "full-history",
            "nodes": {
                "init-local-00001": {
                    "id": "init-local-00001",
                    "type": "initiative",
                    "title": "Test initiative",
                    "path": "spec-dock/initiatives/init-local-00001-test-initiative",
                    "document_surfaces": {
                        "canonical_docs": [
                            {
                                "kind": kind,
                                "path": f"spec-dock/initiatives/init-local-00001-test-initiative/{kind}.md",
                                "present": True,
                            }
                            for kind in ("requirement", "design", "plan", "report")
                        ],
                        "future_artifacts": {
                            "path": "spec-dock/initiatives/init-local-00001-test-initiative/artifacts",
                            "present": True,
                        },
                        "legacy_discussions": {
                            "path": "spec-dock/initiatives/init-local-00001-test-initiative/discussions",
                            "present": False,
                        },
                    },
                    "parent_id": None,
                    "initiative_id": None,
                    "epic_id": None,
                    "children": [],
                    "progress": {"total": 0, "done": 0, "open": 0, "unknown": 0},
                    "depends_on": [],
                }
            },
        })
        + "\n",
        encoding="utf-8",
    )
    (agent_dir / "tree-all.json").write_text(json.dumps({**common, "tree": []}) + "\n", encoding="utf-8")
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert {action.reason for action in contract.blockers} == {"generated-state-node-set-conflict"}
    assert {action.path for action in contract.blockers} == {
        "spec-dock/.agent/index-all.json",
        "spec-dock/.agent/tree-all.json",
    }


def test_i370_generated_state_producer_rejects_active_parent_chain_mismatch(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: active issue hierarchy is proved, never inferred from non-null fields."""

    target_root = tmp_path / "consumer"
    initiatives_root = target_root / "spec-dock" / "initiatives"
    init_a = initiatives_root / "init-a"
    init_b = initiatives_root / "init-b"
    epic_a = init_a / "epics" / "epic-a"
    for path, kind, node_id in (
        (init_a, "initiative", "init-00001"),
        (init_b, "initiative", "init-00002"),
        (epic_a, "epic", "epic-00001"),
    ):
        path.mkdir(parents=True)
        (path / ".meta.json").write_text(
            json.dumps({"type": kind, "id": node_id}) + "\n",
            encoding="utf-8",
        )
    active_dir = target_root / "spec-dock" / "active"
    agent_dir = target_root / "spec-dock" / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()
    issue_none = target_root / "spec-dock" / "system" / "active-none" / "issue"
    issue_none.mkdir(parents=True)
    (active_dir / "initiative").symlink_to(os.path.relpath(init_b, active_dir))
    (active_dir / "epic").symlink_to(os.path.relpath(epic_a, active_dir))
    (active_dir / "issue").symlink_to(Path("../system/active-none/issue"))
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            "initiative": {
                "id": "init-00002",
                "path": init_b.relative_to(target_root).as_posix(),
            },
            "epic": {
                "id": "epic-00001",
                "path": epic_a.relative_to(target_root).as_posix(),
            },
            "issue": None,
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_generated_state_contract(
        target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert any(
        action.path == "spec-dock/.agent/active.json" and action.reason == "generated-state-invalid"
        for action in contract.blockers
    )


def test_i370_contract_adopts_legacy_generated_entry_only_by_historical_exact_identity(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: legacy generated names require manifest-backed exact identity."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    legacy_bytes = b'{"schema_version":1}\n'
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "spec-dock/.agent/deps.json",
                    "surface": "legacy-generated-state",
                    "identities": [
                        _regular_record(
                            "spec-dock/.agent/deps.json",
                            legacy_bytes,
                            mode=0o644,
                        )
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    legacy_path = target_root / "spec-dock" / ".agent" / "deps.json"
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_bytes(legacy_bytes)
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert all(action.path != "spec-dock/.agent/deps.json" for action in contract.generated_state.blockers)
    adopted = next(entry for entry in contract.generated_state.entries if entry.path == "spec-dock/.agent/deps.json")
    assert adopted.origin == "historical-exact"


def test_i370_historical_generated_trusted_claim_requires_envelope_mode_authority(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    legacy_bytes = b'{"schema_version":1}\n'
    manifest_bytes = b'{"managed":true}\n'
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes)
    trusted_manifest["claims"] = [
        _regular_record("spec-dock/.agent/deps.json", legacy_bytes, mode=0o644),
    ]
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(trusted_consumer_manifests=[trusted_manifest]),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    legacy_path = target_root / "spec-dock" / ".agent" / "deps.json"
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_bytes(legacy_bytes)
    legacy_path.chmod(0o644)
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert all(entry.path != "spec-dock/.agent/deps.json" for entry in contract.generated_state.entries)
    assert any(
        blocker.path == "spec-dock/.agent/deps.json" and blocker.reason == "legacy-generated-identity-unproven"
        for blocker in contract.generated_state.blockers
    )


@pytest.mark.parametrize("historical_mode", [None, 0o600])
def test_i370_historical_generated_adoption_requires_mode_authority(
    tmp_path: Path,
    historical_mode: int | None,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    legacy_bytes = b'{"schema_version":1}\n'
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "spec-dock/.agent/deps.json",
                    "surface": "legacy-generated-state",
                    "identities": [
                        _regular_record(
                            "spec-dock/.agent/deps.json",
                            legacy_bytes,
                            mode=historical_mode,
                        )
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    legacy_path = target_root / "spec-dock" / ".agent" / "deps.json"
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_bytes(legacy_bytes)
    legacy_path.chmod(0o644)
    root_info = target_root.stat()

    contract = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert all(entry.path != "spec-dock/.agent/deps.json" for entry in contract.generated_state.entries)
    assert any(
        blocker.path == "spec-dock/.agent/deps.json" and blocker.reason == "legacy-generated-identity-unproven"
        for blocker in contract.generated_state.blockers
    )


def test_i370_context_pack_has_one_provider_renderer_with_cli_byte_parity() -> None:
    """I370-T-OWN-001: installer and deprovision share exact context-pack bytes."""

    from spec_dock import cli

    selections = (
        (None, None, None),
        ("init-local-00003", "epic-00365", "iss-00370"),
    )
    for initiative_id, epic_id, issue_id in selections:
        expected = cli._render_context_pack(
            initiative_id=initiative_id,
            epic_id=epic_id,
            issue_id=issue_id,
        )
        assert (
            managed_distribution._render_context_pack(
                initiative_id=initiative_id,
                epic_id=epic_id,
                issue_id=issue_id,
            )
            == expected
        )


def test_i370_deprovision_contract_uses_semantic_source_identity_across_physical_roots(
    tmp_path: Path,
) -> None:
    """I370-T-SRC-001: physical provider identity is not durable contract identity."""

    package_a = tmp_path / "package-a"
    package_b = tmp_path / "package-b"
    install_a = _minimal_install_root(package_a, b"same managed bytes\n")
    install_b = _minimal_install_root(package_b, b"same managed bytes\n")
    scaffold_a = _minimal_scaffold_root(package_a)
    scaffold_b = _minimal_scaffold_root(package_b)
    manifest_a = _write_manifest(package_a / "manifest", _manifest_with())
    manifest_b = _write_manifest(package_b / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    root_info = target_root.stat()
    expected_root = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    contract_a = managed_distribution.build_deprovision_contract(
        install_a,
        manifest_path=manifest_a,
        scaffold_root=scaffold_a,
        target_root=target_root,
        expected_root_identity=expected_root,
    )
    contract_b = managed_distribution.build_deprovision_contract(
        install_b,
        manifest_path=manifest_b,
        scaffold_root=scaffold_b,
        target_root=target_root,
        expected_root_identity=expected_root,
    )

    assert contract_a.contract_digest == contract_b.contract_digest
    assert contract_a.source_semantic_identities == contract_b.source_semantic_identities
    assert contract_a.source_snapshots != contract_b.source_snapshots
    assert all("package-a" not in item.canonical_source_path for item in contract_a.source_semantic_identities)
    assert all("package-b" not in item.canonical_source_path for item in contract_b.source_semantic_identities)


def test_i370_deprovision_assessment_captures_exact_preserve_witnesses(
    tmp_path: Path,
) -> None:
    """I370-T-PRES-001: initiatives and Workbench topology are durable witnesses."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    initiatives = target_root / "spec-dock" / "initiatives"
    nested = initiatives / "init-local-00001" / "epics"
    nested.mkdir(parents=True)
    requirement = initiatives / "init-local-00001" / "requirement.md"
    requirement.write_bytes(b"preserve exact bytes\n")
    requirement.chmod(0o600)
    (initiatives / "selected").symlink_to("init-local-00001")
    (nested / "empty").mkdir()
    workbench = target_root / "spec-dock" / ".workbench"
    workbench.mkdir()
    (workbench / "notes.txt").write_bytes(b"keep workbench\n")
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    root_info = target_root.stat()

    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert assessment.blockers == ()
    assert tuple(witness.relative_root for witness in assessment.preservation_witnesses) == (
        "spec-dock/.workbench",
        "spec-dock/initiatives",
    )
    initiative_witness = next(
        witness for witness in assessment.preservation_witnesses if witness.relative_root == "spec-dock/initiatives"
    )
    entries = {entry.relative_path: entry for entry in initiative_witness.entries}
    assert (
        entries["spec-dock/initiatives/init-local-00001/requirement.md"].sha256
        == hashlib.sha256(b"preserve exact bytes\n").hexdigest()
    )
    assert entries["spec-dock/initiatives/init-local-00001/requirement.md"].mode == 0o600
    assert entries["spec-dock/initiatives/selected"].link_target == "init-local-00001"
    assert "spec-dock/initiatives/init-local-00001/epics/empty" in entries
    assert all(action.path != "outside-sentinel.txt" for action in assessment.actions)

    repeated = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    assert repeated.preservation_witnesses == assessment.preservation_witnesses


def test_i370_deprovision_assessment_has_no_independent_generated_asset_edge(
    tmp_path: Path,
) -> None:
    """I370-T-OWN-001: generated ownership has one producer and no caller input."""

    assert (
        "generated_assets"
        not in inspect.signature(managed_distribution.build_deprovision_workspace_assessment).parameters
    )
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    with pytest.raises(DistributionPlanError, match="dedicated deprovision assessment"):
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="deprovision",
        )


def test_i370_missing_owned_subtree_collapses_and_reanchors_above_deletion_closure(
    tmp_path: Path,
) -> None:
    """I370-T-TREE-001: one absence witness replaces descendants and survives rmdir."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / ".github").mkdir(parents=True)
    root_info = target_root.stat()

    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    witness = next(item for item in assessment.absence_witnesses if item.relative_root == ".github/workflows")
    assert witness.anchor_path == "."
    assert witness.missing_suffix == (".github", "workflows")
    assert witness.surviving_anchor.relative_path == "."
    assert [action.path for action in assessment.actions if action.path.startswith(".github/workflows/")] == []
    assert any(action.path == ".github" and action.action == "remove-empty-directory" for action in assessment.actions)


def test_i370_semantic_source_drift_and_invocation_replacement_are_distinct_guards(
    tmp_path: Path,
) -> None:
    """I370-T-SRC-001: durable semantics detect drift; full snapshots detect replacement."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed_target = target_root / ".github" / "workflows" / "ci.yml"
    managed_target.parent.mkdir(parents=True)
    managed_target.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    original_contract = assessment.deprovision_contract
    assert original_contract is not None

    source = install_root / ".github" / "workflows" / "ci.yml"
    source.unlink()
    source.write_bytes(b"managed\n")
    with pytest.raises(DistributionPlanError, match="source snapshot changed"):
        build_executable_mutation_plan(assessment)

    source.write_bytes(b"semantic drift\n")
    drifted = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    assert drifted.source_semantic_identities != original_contract.source_semantic_identities
    assert drifted.contract_digest != original_contract.contract_digest


def test_i370_source_semantics_include_mode_and_symlink_target_drift(
    tmp_path: Path,
) -> None:
    """I370-T-SRC-001: source kind, mode, and link text are durable semantics."""

    install_root = _minimal_install_root(tmp_path)
    symlink_source = install_root / ".agents" / "managed-link"
    symlink_source.parent.mkdir(parents=True)
    symlink_source.symlink_to("skill-a")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    original = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    link_identity = next(
        identity
        for identity in original.source_semantic_identities
        if identity.canonical_source_path == "install-root/.agents/managed-link"
    )
    assert link_identity.kind == "symlink"
    assert link_identity.link_target == "skill-a"

    regular_source = install_root / ".github" / "workflows" / "ci.yml"
    regular_source.chmod(0o600)
    mode_drift = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    assert mode_drift.contract_digest != original.contract_digest

    regular_source.chmod(0o644)
    symlink_source.unlink()
    symlink_source.symlink_to("skill-b")
    target_drift = managed_distribution.build_deprovision_contract(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    assert target_drift.contract_digest != original.contract_digest


def test_i370_preserve_hardlink_blocks_without_witness_or_safe_subset_authority(
    tmp_path: Path,
) -> None:
    """I370-T-PRES-001: unproven preservation link topology blocks the operation."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    initiatives = target_root / "spec-dock" / "initiatives"
    initiatives.mkdir(parents=True)
    first = initiatives / "first.md"
    first.write_bytes(b"linked\n")
    os.link(first, initiatives / "second.md")
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"current\n")
    root_info = target_root.stat()

    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert any(action.reason == "preservation-hardlink-unsafe" for action in assessment.blockers)
    assert all(witness.relative_root != "spec-dock/initiatives" for witness in assessment.preservation_witnesses)
    with pytest.raises(DistributionPlanError, match="blocker"):
        build_executable_mutation_plan(assessment)


def test_i370_tree_observation_is_bounded_to_contract_and_preservation_roots(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-OPS-001: unrelated repository subtrees are never enumerated."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    outside = target_root / "large-user-tree"
    outside.mkdir(parents=True)
    for index in range(50):
        (outside / f"user-{index:03d}.txt").write_text("outside\n", encoding="utf-8")
    observed: list[str] = []
    original = managed_distribution._capture_immediate_directory_entries

    def record(target: Path, relative_path: str):
        observed.append(relative_path)
        return original(target, relative_path)

    monkeypatch.setattr(managed_distribution, "_capture_immediate_directory_entries", record)
    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )

    assert "large-user-tree" not in observed
    assert all(not action.path.startswith("large-user-tree") for action in assessment.actions)


def test_i370_plan_rejects_descendant_as_immediate_directory_evidence(
    tmp_path: Path,
) -> None:
    """I370-T-PLAN-001: directory evidence names only an exact immediate child action."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
    )
    parent_snapshot = next(
        snapshot for snapshot in assessment.directory_snapshots if snapshot.relative_path == ".github"
    )
    assert len(parent_snapshot.immediate_child_evidence) == 1
    forged_evidence = replace(
        parent_snapshot.immediate_child_evidence[0],
        child_path=".github/workflows/ci.yml",
        action_path=".github/workflows/ci.yml",
        child_kind="leaf",
    )
    forged_snapshot = replace(parent_snapshot, immediate_child_evidence=(forged_evidence,))
    forged = replace(
        assessment,
        directory_snapshots=tuple(
            forged_snapshot if item.relative_path == ".github" else item for item in assessment.directory_snapshots
        ),
    )

    with pytest.raises(DistributionPlanError, match="immediate child evidence"):
        build_executable_mutation_plan(forged)


def test_i370_directory_semantic_digest_ignores_only_authorized_directory_metadata(
    tmp_path: Path,
) -> None:
    """I370-T-DIR-001: durable child equality excludes only directory ctime/link count."""

    directory = managed_distribution.DistributionTreeEntrySnapshot(
        relative_path=".github/workflows",
        kind="directory",
        device=7,
        inode=11,
        ctime_ns=13,
        mode=0o755,
        link_count=3,
    )
    digest = managed_distribution._directory_child_digest(((directory, "authorized-child", "deprovision-contract"),))
    assert (
        managed_distribution._directory_child_digest((
            (replace(directory, ctime_ns=99, link_count=20), "authorized-child", "deprovision-contract"),
        ))
        == digest
    )
    assert (
        managed_distribution._directory_child_digest((
            (replace(directory, inode=12), "authorized-child", "deprovision-contract"),
        ))
        != digest
    )
    assert (
        managed_distribution._directory_child_digest((
            (replace(directory, mode=0o700), "authorized-child", "deprovision-contract"),
        ))
        != digest
    )

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(
            device=root_info.st_dev,
            inode=root_info.st_ino,
        ),
    )
    snapshot = next(item for item in assessment.directory_snapshots if item.relative_path == ".github/workflows")
    forged = replace(
        assessment,
        directory_snapshots=tuple(
            replace(item, initial_child_digest="0" * 64) if item == snapshot else item
            for item in assessment.directory_snapshots
        ),
    )

    with pytest.raises(DistributionPlanError, match="semantic digest"):
        build_executable_mutation_plan(forged)


def test_i370_plan_rejects_forged_witness_and_digest_binds_semantic_metadata(
    tmp_path: Path,
) -> None:
    """I370-T-PLAN-001: canonical digest binds witnesses, sources, and directory semantics."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    history = target_root / "spec-dock" / "initiatives" / "history.md"
    history.parent.mkdir(parents=True)
    history.write_text("preserve\n", encoding="utf-8")
    root_info = target_root.stat()
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=DistributionRootIdentity(
            device=root_info.st_dev,
            inode=root_info.st_ino,
        ),
    )
    witness = assessment.preservation_witnesses[0]
    forged_assessment = replace(
        assessment,
        preservation_witnesses=(
            replace(witness, tree_digest="0" * 64),
            *assessment.preservation_witnesses[1:],
        ),
    )
    with pytest.raises(DistributionPlanError, match="preservation witness"):
        build_executable_mutation_plan(forged_assessment)

    executable = build_executable_mutation_plan(assessment)
    baseline = managed_distribution._executable_plan_digest(executable)
    source = executable.source_semantic_identities[0]
    assert (
        managed_distribution._executable_plan_digest(
            replace(
                executable,
                source_semantic_identities=(
                    replace(source, mode=(source.mode or 0) ^ 0o100),
                    *executable.source_semantic_identities[1:],
                ),
            )
        )
        != baseline
    )
    assert (
        managed_distribution._executable_plan_digest(replace(executable, generated_state_contract_digest="f" * 64))
        != baseline
    )
    absence = executable.absence_witnesses[0]
    assert (
        managed_distribution._executable_plan_digest(
            replace(
                executable,
                absence_witnesses=(
                    replace(
                        absence,
                        surviving_anchor=replace(
                            absence.surviving_anchor,
                            mode=(absence.surviving_anchor.mode or 0) ^ 0o100,
                        ),
                    ),
                    *executable.absence_witnesses[1:],
                ),
            )
        )
        != baseline
    )


def test_i370_empty_directory_kernel_is_bottom_up_bound_and_fail_closed(
    tmp_path: Path,
) -> None:
    """I370-T-KRN-001: exact rmdir uses immediate children and preserves raced names."""

    target_root = tmp_path / "consumer"
    deepest = target_root / "managed" / "a" / "b"
    deepest.mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    bindings = {
        path: managed_distribution._capture_immediate_directory_entries(target_root, path)[0]
        for path in ("managed", "managed/a", "managed/a/b")
    }
    empty_digest = managed_distribution._directory_child_digest(())

    managed_distribution._remove_distribution_directory_if_bound(
        target_root,
        Path("managed/a/b"),
        expected_root_identity=root_identity,
        expected_directory_binding=bindings["managed/a/b"],
        immediate_child_evidence=(),
        expected_remaining_child_digest=empty_digest,
    )
    managed_distribution._remove_distribution_directory_if_bound(
        target_root,
        Path("managed/a"),
        expected_root_identity=root_identity,
        expected_directory_binding=bindings["managed/a"],
        immediate_child_evidence=(
            managed_distribution.DistributionImmediateChildEvidence(
                child_path="managed/a/b",
                child_kind="directory",
                action_path="managed/a/b",
                required_checkpoint="published",
                expected_postcondition={"path": "managed/a/b", "exists": False},
            ),
        ),
        expected_remaining_child_digest=empty_digest,
    )
    managed_distribution._remove_distribution_directory_if_bound(
        target_root,
        Path("managed"),
        expected_root_identity=root_identity,
        expected_directory_binding=bindings["managed"],
        immediate_child_evidence=(
            managed_distribution.DistributionImmediateChildEvidence(
                child_path="managed/a",
                child_kind="directory",
                action_path="managed/a",
                required_checkpoint="published",
                expected_postcondition={"path": "managed/a", "exists": False},
            ),
        ),
        expected_remaining_child_digest=empty_digest,
    )
    assert not (target_root / "managed").exists()

    rebound_parent = target_root / "rebound"
    rebound_target = rebound_parent / "child"
    rebound_target.mkdir(parents=True)
    rebound_parent_binding = managed_distribution._capture_immediate_directory_entries(
        target_root,
        "rebound",
    )[0]
    rebound_target_binding = managed_distribution._capture_immediate_directory_entries(
        target_root,
        "rebound/child",
    )[0]
    rebound_parent.rename(target_root / "rebound-original")
    rebound_target.parent.mkdir()
    rebound_target.mkdir()
    with pytest.raises(DistributionApplyError, match="managed directory"):
        managed_distribution._remove_distribution_directory_if_bound(
            target_root,
            Path("rebound/child"),
            expected_root_identity=root_identity,
            expected_parent_bindings=(rebound_parent_binding,),
            expected_directory_binding=rebound_target_binding,
            immediate_child_evidence=(),
            expected_remaining_child_digest=empty_digest,
        )
    assert rebound_target.exists()
    assert (target_root / "rebound-original" / "child").is_dir()

    appeared = target_root / "appeared"
    appeared.mkdir()
    appeared_binding = managed_distribution._capture_immediate_directory_entries(
        target_root,
        "appeared",
    )[0]

    def appear_unknown() -> None:
        (appeared / "unknown.txt").write_text("preserve\n", encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="managed directory"):
        managed_distribution._remove_distribution_directory_if_bound(
            target_root,
            Path("appeared"),
            expected_root_identity=root_identity,
            expected_directory_binding=appeared_binding,
            immediate_child_evidence=(),
            expected_remaining_child_digest=empty_digest,
            before_mutation=appear_unknown,
        )
    assert (appeared / "unknown.txt").read_text(encoding="utf-8") == "preserve\n"

    replaced = target_root / "replaced"
    replaced.mkdir()
    replaced_binding = managed_distribution._capture_immediate_directory_entries(
        target_root,
        "replaced",
    )[0]

    def replace_directory() -> None:
        replaced.rename(target_root / "replaced-original")
        replaced.mkdir()

    with pytest.raises(DistributionApplyError, match="managed directory"):
        managed_distribution._remove_distribution_directory_if_bound(
            target_root,
            Path("replaced"),
            expected_root_identity=root_identity,
            expected_directory_binding=replaced_binding,
            immediate_child_evidence=(),
            expected_remaining_child_digest=empty_digest,
            before_mutation=replace_directory,
        )
    assert replaced.is_dir()
    assert (target_root / "replaced-original").is_dir()


def test_i370_directory_marker_replacement_is_checked_before_rmdir(
    tmp_path: Path,
) -> None:
    """I370-T-RACE-001: deprovision rmdir rechecks its final marker boundary."""

    target_root = tmp_path / "consumer"
    directory = target_root / "managed"
    directory.mkdir(parents=True)
    marker = target_root / "marker"
    marker.write_bytes(b"marker\n")
    original_marker = marker.lstat()
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    binding = managed_distribution._capture_immediate_directory_entries(target_root, "managed")[0]
    calls = 0

    def replace_marker() -> None:
        replacement = target_root / "marker-replacement"
        replacement.write_bytes(b"marker\n")
        marker.unlink()
        replacement.rename(marker)

    def validate_final_boundary() -> None:
        nonlocal calls
        calls += 1
        if marker.lstat().st_ino != original_marker.st_ino:
            raise DistributionApplyError("deprovision marker mismatch")

    with pytest.raises(DistributionApplyError, match="deprovision marker mismatch"):
        managed_distribution._remove_distribution_directory_if_bound(
            target_root,
            Path("managed"),
            expected_root_identity=root_identity,
            expected_directory_binding=binding,
            immediate_child_evidence=(),
            expected_remaining_child_digest=managed_distribution._directory_child_digest(()),
            before_mutation=replace_marker,
            final_mutation_validator=validate_final_boundary,
        )

    assert calls == 1
    assert directory.is_dir()
    assert marker.read_bytes() == b"marker\n"
    assert marker.lstat().st_ino != original_marker.st_ino


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i370_existing_backup_is_retained_when_validator_fails(
    tmp_path: Path,
    kind: str,
) -> None:
    """I370-T-REC-001: failed cleanup cannot unlink a pre-existing backup."""

    parent = tmp_path / kind
    parent.mkdir()
    quarantine = parent / "quarantine.remove"
    if kind == "regular":
        quarantine.write_bytes(b"managed\n")
    else:
        quarantine.symlink_to("managed-target")
    backup_name = managed_distribution._distribution_quarantine_backup_name(quarantine.name)
    backup = parent / backup_name
    os.link(quarantine, backup, follow_symlinks=False)
    expected = quarantine.lstat()
    quarantine_before = (quarantine.lstat(), quarantine.read_bytes() if kind == "regular" else quarantine.readlink())
    backup_before = (backup.lstat(), backup.read_bytes() if kind == "regular" else backup.readlink())
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
            managed_distribution._unlink_distribution_quarantine_with_backup(
                parent_fd,
                quarantine.name,
                "stage",
                expected,
                canonical_validator=lambda: (_ for _ in ()).throw(DistributionApplyError("injected validator failure")),
                mutation_validator=None,
                allow_existing_backup=True,
            )
    finally:
        os.close(parent_fd)

    assert quarantine.exists() or quarantine.is_symlink()
    assert backup.exists() or backup.is_symlink()
    assert (
        quarantine.lstat(),
        quarantine.read_bytes() if kind == "regular" else quarantine.readlink(),
    ) == quarantine_before
    assert (
        backup.lstat(),
        backup.read_bytes() if kind == "regular" else backup.readlink(),
    ) == backup_before


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("rebind_ordinal", [2, 3])
def test_i370_gc_ordinal_reservation_rechecks_before_rename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    rebind_ordinal: int,
) -> None:
    """I370-T-RACE-001: GC reservation writes cannot authorize a stale-FD rename."""

    parent = tmp_path / f"{kind}-{rebind_ordinal}"
    parent.mkdir()
    stage = parent / "stage"
    if kind == "regular":
        stage.write_bytes(b"managed\n")
    else:
        stage.symlink_to("managed-target")
    created = stage.lstat()
    original_parent = parent.lstat()
    displaced = parent.with_name(f"{parent.name}-displaced")
    leases: list[DistributionStageOwnership] = []
    reserved_names: dict[int, str] = {}
    injected = False

    def record_gc(lease: DistributionStageOwnership) -> None:
        nonlocal injected
        leases.append(lease)
        if lease.role == "gc-reserved" and lease.gc_ordinal == rebind_ordinal and not injected:
            reserved_names[rebind_ordinal] = lease.stage_name
            parent.rename(displaced)
            parent.mkdir()
            injected = True

    def validate_parent() -> None:
        if parent.lstat().st_ino != original_parent.st_ino:
            raise DistributionApplyError("deprovision-visible-parent-chain-mismatch")

    original_rename = managed_distribution._rename_distribution_no_replace
    ordinal_rename_calls = 0

    def count_ordinal_rename(*args, **kwargs):
        nonlocal ordinal_rename_calls
        if args[3] in reserved_names.values():
            ordinal_rename_calls += 1
        return original_rename(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_ordinal_rename)
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError, match="deprovision-visible-parent-chain-mismatch"):
            managed_distribution._remove_distribution_stage_if_owned(
                parent_fd,
                stage.name,
                created,
                strict=True,
                mutation_validator=validate_parent,
                gc_path="managed/target",
                gc_recorder=record_gc,
            )
    finally:
        os.close(parent_fd)

    assert injected is True
    assert any(lease.role == "gc-reserved" and lease.gc_ordinal == rebind_ordinal for lease in leases)
    assert ordinal_rename_calls == 0
    assert displaced.is_dir()
    preserved_entries = tuple(displaced.iterdir())
    assert preserved_entries
    if kind == "regular":
        assert any(entry.read_bytes() == b"managed\n" for entry in preserved_entries)
    else:
        assert any(entry.is_symlink() and entry.readlink() == Path("managed-target") for entry in preserved_entries)


def test_i370_prune_kernel_removes_exact_regular_and_symlink_but_not_replacement(
    tmp_path: Path,
) -> None:
    """I370-T-KRN-001/I370-T-ID-001: leaf prune rejects replacement and link drift."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())

    def executable_for(target_root: Path):
        managed = target_root / ".github" / "workflows" / "ci.yml"
        managed.parent.mkdir(parents=True)
        managed.write_bytes(b"managed\n")
        runtime = target_root / "spec-dock" / "scripts" / "spec-dock"
        runtime.parent.mkdir(parents=True)
        runtime.write_text("#!/bin/sh\n", encoding="utf-8")
        runtime.chmod(0o755)
        (target_root / "spec").symlink_to("spec-dock/scripts/spec-dock")
        root_info = target_root.stat()
        executable = build_executable_mutation_plan(
            managed_distribution.build_deprovision_workspace_assessment(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                expected_root_identity=DistributionRootIdentity(
                    device=root_info.st_dev,
                    inode=root_info.st_ino,
                ),
            )
        )
        leaf_actions = tuple(action for action in executable.actions if action.action == "prune")
        return executable, replace(executable.distribution_plan, actions=leaf_actions), managed

    target_root = tmp_path / "success"
    _executable, leaf_plan, managed = executable_for(target_root)
    apply_distribution_plan(leaf_plan)
    assert not managed.exists()
    assert not (target_root / "spec").exists()

    raced_root = tmp_path / "raced"
    _executable, raced_plan, raced = executable_for(raced_root)
    raced.unlink()
    raced.write_bytes(b"managed\n")
    with pytest.raises(DistributionApplyError, match="managed target identity changed"):
        apply_distribution_plan(raced_plan)
    assert raced.read_bytes() == b"managed\n"
    assert (raced_root / "spec").is_symlink()

    hardlink_root = tmp_path / "hardlink-race"
    _executable, hardlink_plan, hardlinked = executable_for(hardlink_root)
    os.link(hardlinked, hardlinked.with_name("ci-linked.yml"))
    hardlink_action = next(action for action in hardlink_plan.actions if action.path.endswith("ci.yml"))
    with pytest.raises(DistributionApplyError, match="managed target identity changed"):
        apply_distribution_plan(replace(hardlink_plan, actions=(hardlink_action,)))
    assert hardlinked.exists()
    assert hardlinked.with_name("ci-linked.yml").exists()

    symlink_root = tmp_path / "symlink-race"
    _executable, symlink_plan, _managed = executable_for(symlink_root)
    shortcut = symlink_root / "spec"
    shortcut.unlink()
    shortcut.symlink_to("different-target")
    symlink_action = next(action for action in symlink_plan.actions if action.path == "spec")
    with pytest.raises(DistributionApplyError, match="managed target identity changed"):
        apply_distribution_plan(replace(symlink_plan, actions=(symlink_action,)))
    assert shortcut.readlink() == Path("different-target")


def test_i370_deprovision_dry_run_is_fully_typed_and_write_free(
    tmp_path: Path,
) -> None:
    """I370-T-DRY-001: the service plans one deprovision contract without writes."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    sentinel = target_root / "outside-sentinel.txt"
    sentinel.write_bytes(b"outside\n")
    before = {
        path.relative_to(target_root).as_posix(): (
            path.lstat().st_dev,
            path.lstat().st_ino,
            path.lstat().st_ctime_ns,
            path.read_bytes() if path.is_file() and not path.is_symlink() else None,
        )
        for path in target_root.rglob("*")
    }

    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=False,
    )
    second = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=False,
    )
    root_info = target_root.stat()
    expected_executable = build_executable_mutation_plan(
        managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=DistributionRootIdentity(
                device=root_info.st_dev,
                inode=root_info.st_ino,
            ),
        )
    )

    assert first == second
    assert first.status == "planned"
    assert first.plan_digest == expected_executable.plan_digest
    assert first.phase == "preflight"
    assert first.last_completed_phase == "preflight-complete"
    assert first.retry_policy == "same-keep-command"
    assert first.failed_paths == first.pending_paths == ()
    assert first.errors == ()
    assert any(
        outcome.path == ".github/workflows/ci.yml" and outcome.status == "would_remove"
        for outcome in first.action_outcomes
    )
    assert sentinel.read_bytes() == b"outside\n"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()
    assert not (target_root / "spec-dock" / ".uninstall-retry.json").exists()
    assert before == {
        path.relative_to(target_root).as_posix(): (
            path.lstat().st_dev,
            path.lstat().st_ino,
            path.lstat().st_ctime_ns,
            path.read_bytes() if path.is_file() and not path.is_symlink() else None,
        )
        for path in target_root.rglob("*")
    }


def test_i370_deprovision_no_op_apply_collapses_absence_without_protocol_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-NOOP-001: an absent managed tree completes without mutation authority."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    workbench_seed = target_root / "spec-dock" / ".workbench" / "README.md"
    workbench_seed.parent.mkdir(parents=True)
    workbench_seed.write_bytes(b"workbench\n")
    sentinel = target_root / "outside-sentinel.txt"
    sentinel.write_bytes(b"outside\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_prepare_guard = OperationJournalStore.prepare_legacy_guard
    original_prepare = OperationJournalStore.prepare

    def reject_guard(*_args, **_kwargs):
        raise AssertionError("no-op apply must not prepare a forward guard")

    def reject_journal(*_args, **_kwargs):
        raise AssertionError("no-op apply must not prepare a journal")

    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", reject_guard)
    monkeypatch.setattr(OperationJournalStore, "prepare", reject_journal)
    try:
        result = managed_distribution.execute_deprovision_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            package_version="1.2.3",
            apply=True,
            expected_root_identity=root_identity,
        )
    finally:
        monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", original_prepare_guard)
        monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)

    assert result.status == "completed"
    assert result.phase == "complete"
    assert result.last_completed_phase == "post-verified"
    assert result.retry_policy == "same-keep-command"
    assert result.applied_paths == result.failed_paths == result.pending_paths == ()
    assert result.errors == ()
    already_removed = tuple(outcome.path for outcome in result.action_outcomes if outcome.status == "already_removed")
    assert already_removed
    assert all(
        not any(other != path and other.startswith(f"{path}/") for other in already_removed) for path in already_removed
    )
    assert sentinel.read_bytes() == b"outside\n"
    assert sorted(path.relative_to(target_root).as_posix() for path in target_root.rglob("*")) == [
        "outside-sentinel.txt",
        "spec-dock",
        "spec-dock/.workbench",
        "spec-dock/.workbench/README.md",
    ]


def test_i370_deprovision_requires_exact_managed_workspace_evidence(
    tmp_path: Path,
) -> None:
    """I370-T-DRY-001/I370-T-NOOP-001: absence alone never proves a managed workspace."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    sentinel = target_root / "outside-sentinel.txt"
    sentinel.write_bytes(b"outside\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    dry_run = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=False,
    )
    apply = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    for result in (dry_run, apply):
        assert result.status == "error"
        assert result.phase == "preflight"
        assert result.last_completed_phase == "not-started"
        assert result.reason == "managed-workspace-evidence-missing"
        assert result.errors[0].code == "managed-workspace-evidence-missing"
    assert sentinel.read_bytes() == b"outside\n"
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()


def test_i370_deprovision_blocker_is_diagnostic_in_dry_run_and_write_free_on_apply(
    tmp_path: Path,
) -> None:
    """I370-T-BLK-001: one unsafe owned path blocks every apply mutation."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    modified = target_root / ".github" / "workflows" / "ci.yml"
    modified.parent.mkdir(parents=True)
    modified.write_bytes(b"user modified\n")
    workbench_seed = target_root / "spec-dock" / ".workbench" / "README.md"
    workbench_seed.parent.mkdir(parents=True)
    workbench_seed.write_bytes(b"workbench\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    planned = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=False,
    )
    blocked = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert planned.status == "planned"
    assert planned.failed_paths == planned.errors == ()
    assert any(
        outcome.path == ".github/workflows/ci.yml" and outcome.status == "preserved"
        for outcome in planned.action_outcomes
    )
    assert blocked.status == "blocked"
    assert blocked.phase == "preflight"
    assert blocked.last_completed_phase == "preflight-complete"
    assert ".github/workflows/ci.yml" in blocked.failed_paths
    assert blocked.pending_paths == ()
    assert blocked.errors
    assert modified.read_bytes() == b"user modified\n"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_deprovision_no_op_appearance_blocks_without_issuing_a_new_prune(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-NOOP-001: an appearance after collapse is preserved and blocks no-op."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    workbench_seed = target_root / "spec-dock" / ".workbench" / "README.md"
    workbench_seed.parent.mkdir(parents=True)
    workbench_seed.write_bytes(b"workbench\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_assessment = managed_distribution.build_deprovision_workspace_assessment
    assessment_count = 0

    def appear_after_collapse(*args, **kwargs):
        nonlocal assessment_count
        assessment = original_assessment(*args, **kwargs)
        assessment_count += 1
        if assessment_count == 1:
            appeared = target_root / ".github" / "workflows" / "ci.yml"
            appeared.parent.mkdir(parents=True)
            appeared.write_bytes(b"managed\n")
        return assessment

    monkeypatch.setattr(
        managed_distribution,
        "build_deprovision_workspace_assessment",
        appear_after_collapse,
    )
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    appeared = target_root / ".github" / "workflows" / "ci.yml"
    assert assessment_count == 2
    assert result.status == "blocked"
    assert result.reason == "deprovision-no-op-postcondition-changed"
    assert result.pending_paths == ()
    assert ".github/workflows/ci.yml" in result.failed_paths
    assert appeared.read_bytes() == b"managed\n"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_missing_root_shortcut_appearance_blocks_completion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-NOOP-001/I370-T-RACE-001: a missing root leaf is a durable absence witness."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock").mkdir()
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    root_witness = next(witness for witness in assessment.absence_witnesses if witness.relative_root == "spec")
    assert root_witness.anchor_path == "."
    assert root_witness.missing_suffix == ("spec",)
    assert next(action for action in assessment.actions if action.path == "spec").provenance == "missing"
    build_executable_mutation_plan(assessment)

    original_mark_verified = OperationJournalStore.mark_verified

    def appear_after_verifying(self, journal):
        verifying = original_mark_verified(self, journal)
        (target_root / "spec").symlink_to("spec-dock/scripts/spec-dock")
        return verifying

    monkeypatch.setattr(OperationJournalStore, "mark_verified", appear_after_verifying)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required", result.reason
    assert result.phase == "post-verify"
    assert "spec" in result.failed_paths
    assert (target_root / "spec").is_symlink()
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_missing_leaf_appearance_between_classification_and_witness_blocks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-RACE-001/I370-T-NOOP-001: first missing observation remains authoritative."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock").mkdir()
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_augment = managed_distribution._augment_deprovision_tree
    injected = False

    def appear_before_witness(*args, **kwargs):
        nonlocal injected
        if not injected:
            (target_root / "spec").symlink_to("spec-dock")
            injected = True
        return original_augment(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_augment_deprovision_tree", appear_before_witness)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )

    assert injected is True
    witness = next(witness for witness in assessment.absence_witnesses if witness.relative_root == "spec")
    assert witness.anchor_path == "."
    assert witness.missing_suffix == ("spec",)
    with pytest.raises(DistributionApplyError, match="deprovision-absence-witness-mismatch"):
        managed_distribution._assert_deprovision_invocation_state(assessment)
    assert managed.read_bytes() == b"managed\n"
    assert (target_root / "spec").is_symlink()
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_deprovision_service_journals_nested_prune_and_completes(
    tmp_path: Path,
) -> None:
    """I370-T-REC-001: leaf and immediate-parent checkpoints complete forward-only."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    initiatives = target_root / "spec-dock" / "initiatives"
    initiatives.mkdir(parents=True)
    preserved = initiatives / "requirement.md"
    preserved.write_bytes(b"keep\n")
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    root_info = target_root.stat()

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=DistributionRootIdentity(
            device=root_info.st_dev,
            inode=root_info.st_ino,
        ),
    )

    assert result.status == "completed"
    assert result.phase == "complete"
    assert result.last_completed_phase == "marker-finalized"
    assert result.failed_paths == result.pending_paths == result.errors == ()
    assert not (target_root / ".github").exists()
    assert preserved.read_bytes() == b"keep\n"
    assert outside.read_bytes() == b"outside\n"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()
    outcomes = {outcome.path: outcome.status for outcome in result.action_outcomes}
    assert outcomes[".github/workflows/ci.yml"] == "removed"
    assert outcomes[".github/workflows"] == "empty_dir_removed"
    assert outcomes[".github"] == "empty_dir_removed"
    assert outcomes["spec-dock/initiatives"] == "preserved"


@pytest.mark.parametrize(
    ("crash_path", "expected_phase", "expected_pending"),
    [
        (
            ".github/workflows/ci.yml",
            "root-cleanup",
            (".github", ".github/workflows"),
        ),
        (".github/workflows", "root-cleanup", (".github",)),
        (".github", "post-verify", ()),
    ],
)
def test_i370_deprovision_retry_resumes_each_nested_publish_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    crash_path: str,
    expected_phase: str,
    expected_pending: tuple[str, ...],
) -> None:
    """I370-T-REC-001: each leaf/directory publish crash resumes the same plan."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def fail_after_durable_publish(self, journal, completed_paths):
        nonlocal interrupted
        published = original_checkpoint(self, journal, completed_paths)
        if not interrupted and crash_path in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected publish interruption")
        return published

    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        fail_after_durable_publish,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        original_checkpoint,
    )

    assert interrupted is True
    assert first.status == "recovery_required"
    assert first.phase == expected_phase
    assert first.last_completed_phase == "uninstall-applied"
    assert first.pending_paths == expected_pending
    assert set(first.pending_paths).issubset(first.failed_paths)
    journal_payload = json.loads((target_root / "spec-dock" / ".distribution-journal.json").read_text(encoding="utf-8"))
    checkpoints = {action["path"]: action["checkpoint"] for action in journal_payload["actions"]}
    assert checkpoints[crash_path] == "published"

    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert retry.last_completed_phase == "marker-finalized"
    assert not (target_root / ".github").exists()
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_deprovision_verifying_resume_never_reopens_removed_descendants(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-REC-001: verifying resumes postconditions without target replay."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_mark_completed = OperationJournalStore.mark_completed

    def interrupt_verifying(_self, _journal):
        raise DistributionApplyError("injected verifying interruption")

    monkeypatch.setattr(
        OperationJournalStore,
        "mark_completed",
        interrupt_verifying,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "mark_completed",
        original_mark_completed,
    )

    assert first.status == "recovery_required"
    assert first.phase == "post-verify"
    assert first.last_completed_phase == "uninstall-applied"
    assert first.pending_paths == ()
    verifying = json.loads((target_root / "spec-dock" / ".distribution-journal.json").read_text(encoding="utf-8"))
    assert verifying["status"] == "verifying"
    assert {action["checkpoint"] for action in verifying["actions"]} == {"published"}

    original_observe = managed_distribution._observe_target
    observed: list[str] = []

    def reject_removed_descendant(target: Path, relative_path: str):
        observed.append(relative_path)
        if relative_path.startswith(".github/"):
            raise AssertionError("verifying reopened a removed subtree descendant")
        return original_observe(target, relative_path)

    def reject_target_replay(*_args, **_kwargs):
        raise AssertionError("verifying must not replay a target action")

    monkeypatch.setattr(managed_distribution, "_observe_target", reject_removed_descendant)
    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", reject_target_replay)
    monkeypatch.setattr(
        managed_distribution,
        "_remove_distribution_directory_if_bound",
        reject_target_replay,
    )
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert retry.last_completed_phase == "marker-finalized"
    assert ".github" in observed
    assert not any(path.startswith(".github/") for path in observed)


def test_i370_deprovision_retry_reuses_published_generated_contract_after_active_manifest_removal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-KRN-001/I370-T-REC-001: published generated state is durable recovery evidence."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(
            recognized_workspace_versions=[
                {"version": "1.2.3", "anchors": [_regular_record("legacy-anchor", b"legacy\n")]},
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    spec_dock = target_root / "spec-dock"
    active_dir = spec_dock / "active"
    agent_dir = spec_dock / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()
    (spec_dock / "spec-dock.version").write_text("1.2.3\n", encoding="ascii")

    node_paths = {
        "initiative": "spec-dock/initiatives/init-local-00001-active",
        "epic": "spec-dock/initiatives/init-local-00001-active/epics/epic-00001-active",
        "issue": ("spec-dock/initiatives/init-local-00001-active/epics/epic-00001-active/issues/iss-00001-active"),
    }
    node_ids = {
        "initiative": "init-local-00001",
        "epic": "epic-00001",
        "issue": "iss-00001",
    }
    for layer, node_path in node_paths.items():
        node = target_root / node_path
        node.mkdir(parents=True)
        (node / ".meta.json").write_text(
            json.dumps({"id": node_ids[layer], "type": layer}) + "\n",
            encoding="utf-8",
        )
        relative_target = os.path.relpath(node, active_dir)
        (active_dir / layer).symlink_to(relative_target)
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            **{layer: {"id": node_ids[layer], "path": node_paths[layer]} for layer in ("initiative", "epic", "issue")},
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def interrupt_after_active_manifest_publish(self, journal, completed_paths):
        nonlocal interrupted
        published = original_checkpoint(self, journal, completed_paths)
        if not interrupted and "spec-dock/.agent/active.json" in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected active manifest publish interruption")
        return published

    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        interrupt_after_active_manifest_publish,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert interrupted is True, first.reason
    assert first.status == "recovery_required"
    journal_payload = json.loads((spec_dock / ".distribution-journal.json").read_text(encoding="utf-8"))
    assert (
        next(
            action["checkpoint"]
            for action in journal_payload["actions"]
            if action["path"] == "spec-dock/.agent/active.json"
        )
        == "published"
    )
    assert not (agent_dir / "active.json").exists()
    assert (active_dir / "initiative").is_symlink()

    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed", retry.reason
    assert not active_dir.exists()
    assert not agent_dir.exists()
    assert not (spec_dock / ".distribution-retry.json").exists()
    assert not (spec_dock / ".distribution-journal.json").exists()


@pytest.mark.parametrize("path_layer", [None, "initiative"])
def test_i370_deprovision_retry_reuses_pending_active_selection_after_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path_layer: str | None,
) -> None:
    """A pre-checkpoint generated unlink keeps the journal's active witness authoritative."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    spec_dock = target_root / "spec-dock"
    active_dir = spec_dock / "active"
    agent_dir = spec_dock / ".agent"
    active_dir.mkdir(parents=True)
    agent_dir.mkdir()

    node_paths = {
        "initiative": "spec-dock/initiatives/init-local-00001-active",
        "epic": "spec-dock/initiatives/init-local-00001-active/epics/epic-00001-active",
        "issue": "spec-dock/initiatives/init-local-00001-active/epics/epic-00001-active/issues/iss-00001-active",
    }
    node_ids = {
        "initiative": "init-local-00001",
        "epic": "epic-00001",
        "issue": "iss-00001",
    }
    for layer, node_path in node_paths.items():
        node = target_root / node_path
        node.mkdir(parents=True)
        (node / ".meta.json").write_text(
            json.dumps({"id": node_ids[layer], "type": layer}) + "\n",
            encoding="utf-8",
        )
        relative_target = os.path.relpath(node, active_dir)
        if layer == path_layer:
            (active_dir / f"{layer}.path").write_text(relative_target + "\n", encoding="utf-8")
        else:
            (active_dir / layer).symlink_to(relative_target)
    (agent_dir / "active.json").write_text(
        json.dumps({
            "schema_version": 2,
            "updated_at": "2026-08-25T12:00:00+09:00",
            **{layer: {"id": node_ids[layer], "path": node_paths[layer]} for layer in node_paths},
        })
        + "\n",
        encoding="utf-8",
    )
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    crash_path = "spec-dock/.agent/active.json" if path_layer is None else f"spec-dock/active/{path_layer}.path"
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def interrupt_before_checkpoint(self, journal, completed_paths):
        nonlocal interrupted
        if not interrupted and crash_path in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected pre-checkpoint interruption")
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", interrupt_before_checkpoint)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)

    assert interrupted is True, first.reason
    assert first.status == "recovery_required"
    journal_payload = json.loads((spec_dock / ".distribution-journal.json").read_text(encoding="utf-8"))
    assert next(action["checkpoint"] for action in journal_payload["actions"] if action["path"] == crash_path) == (
        "pending"
    )
    assert not (target_root / crash_path).exists()

    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed", retry.reason
    assert not active_dir.exists()
    assert not agent_dir.exists()
    assert not (spec_dock / ".distribution-retry.json").exists()
    assert not (spec_dock / ".distribution-journal.json").exists()


def test_i370_deprovision_recovery_does_not_list_published_generated_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-KRN-001: published generated roots subsume descendants durably."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    spec_dock = target_root / "spec-dock"
    (spec_dock / "active").mkdir(parents=True)
    (spec_dock / ".agent").mkdir()
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def interrupt_after_agent_root_publish(self, journal, completed_paths):
        nonlocal interrupted
        published = original_checkpoint(self, journal, completed_paths)
        if not interrupted and "spec-dock/.agent" in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected generated root publish interruption")
        return published

    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        interrupt_after_agent_root_publish,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)

    assert interrupted is True
    assert first.status == "recovery_required"
    journal_payload = json.loads((spec_dock / ".distribution-journal.json").read_text(encoding="utf-8"))
    assert (
        next(action["checkpoint"] for action in journal_payload["actions"] if action["path"] == "spec-dock/.agent")
        == "published"
    )
    assert not (spec_dock / ".agent").exists()

    original_list = managed_distribution._list_generated_root
    listed: list[str] = []

    def reject_published_root(target: Path, relative_root: str):
        listed.append(relative_root)
        if relative_root == "spec-dock/.agent":
            raise AssertionError("recovery reopened a published generated root")
        return original_list(target, relative_root)

    monkeypatch.setattr(managed_distribution, "_list_generated_root", reject_published_root)
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed", retry.reason
    assert "spec-dock/.agent" not in listed
    assert not (spec_dock / ".distribution-retry.json").exists()
    assert not (spec_dock / ".distribution-journal.json").exists()


def test_i370_deprovision_completed_with_guard_retries_cleanup_without_target_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-REC-001: completed+guard retries only exact guard/journal cleanup."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_remove_guard = OperationJournalStore.remove_legacy_marker

    def interrupt_before_guard_cleanup(_self, _guard):
        raise DistributionApplyError("sensitive absolute /tmp/provider token=secret")

    monkeypatch.setattr(
        OperationJournalStore,
        "remove_legacy_marker",
        interrupt_before_guard_cleanup,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "remove_legacy_marker",
        original_remove_guard,
    )

    assert first.status == "recovery_required"
    assert first.phase == "marker-finalization"
    assert first.last_completed_phase == "post-verified"
    assert first.pending_paths == ()
    assert first.failed_paths == ("spec-dock/.distribution-retry.json",)
    assert all("/tmp/provider" not in error.message for error in first.errors)
    assert all("token=secret" not in error.message for error in first.errors)
    assert "/tmp/provider" not in repr(first)
    assert "token=secret" not in repr(first)
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()
    completed_payload = json.loads(
        (target_root / "spec-dock" / ".distribution-journal.json").read_text(encoding="utf-8")
    )
    assert completed_payload["status"] == "completed"
    assert {action["checkpoint"] for action in completed_payload["actions"]} == {"verified"}

    def reject_target_replay(*_args, **_kwargs):
        raise AssertionError("terminal cleanup must not replay a target action")

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", reject_target_replay)
    monkeypatch.setattr(
        managed_distribution,
        "_remove_distribution_directory_if_bound",
        reject_target_replay,
    )
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert retry.last_completed_phase == "marker-finalized"
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_deprovision_completed_only_retries_journal_cleanup_without_target_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-REC-001: completed-only retries exact journal cleanup."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_remove_completed = OperationJournalStore.remove_completed

    def interrupt_before_journal_cleanup(_self, _journal, *, guard_already_removed=False):
        assert guard_already_removed is True
        raise DistributionApplyError("sensitive absolute /tmp/provider token=secret")

    monkeypatch.setattr(
        OperationJournalStore,
        "remove_completed",
        interrupt_before_journal_cleanup,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "remove_completed",
        original_remove_completed,
    )

    assert first.status == "recovery_required"
    assert first.phase == "marker-finalization"
    assert first.last_completed_phase == "marker-finalized"
    assert first.pending_paths == ()
    assert first.failed_paths == ("spec-dock/.distribution-journal.json",)
    assert all("/tmp/provider" not in error.message for error in first.errors)
    assert all("token=secret" not in error.message for error in first.errors)
    assert "/tmp/provider" not in repr(first)
    assert "token=secret" not in repr(first)
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()

    def reject_target_replay(*_args, **_kwargs):
        raise AssertionError("terminal cleanup must not replay a target action")

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", reject_target_replay)
    monkeypatch.setattr(
        managed_distribution,
        "_remove_distribution_directory_if_bound",
        reject_target_replay,
    )
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert retry.last_completed_phase == "marker-finalized"
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_deprovision_post_verify_rejects_unknown_remaining_namespace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-RACE-001: unknown remaining child blocks atomic completed publication."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_mark_verified = OperationJournalStore.mark_verified
    original_mark_completed = OperationJournalStore.mark_completed
    completed_calls = 0

    def appear_after_verifying(self, journal):
        verifying = original_mark_verified(self, journal)
        (target_root / "spec-dock" / "unexpected.txt").write_bytes(b"preserve me\n")
        return verifying

    def count_completed(self, journal):
        nonlocal completed_calls
        completed_calls += 1
        return original_mark_completed(self, journal)

    monkeypatch.setattr(OperationJournalStore, "mark_verified", appear_after_verifying)
    monkeypatch.setattr(OperationJournalStore, "mark_completed", count_completed)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    unexpected = target_root / "spec-dock" / "unexpected.txt"
    assert result.status == "recovery_required"
    assert result.phase == "post-verify"
    assert result.last_completed_phase == "uninstall-applied"
    assert result.pending_paths == ()
    assert result.failed_paths == ("spec-dock/unexpected.txt",)
    assert completed_calls == 0
    assert unexpected.read_bytes() == b"preserve me\n"
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize(
    ("race_kind", "expected_failed_path"),
    [
        ("preservation", "spec-dock/initiatives"),
        ("absence", "spec-dock/.agent"),
    ],
)
def test_i370_deprovision_post_verify_rejects_witness_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    race_kind: str,
    expected_failed_path: str,
) -> None:
    """I370-T-PRES-001/I370-T-RACE-001: durable witnesses fail closed after apply."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    preserved = target_root / "spec-dock" / "initiatives" / "requirement.md"
    preserved.parent.mkdir(parents=True)
    preserved.write_bytes(b"keep\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_mark_verified = OperationJournalStore.mark_verified
    original_mark_completed = OperationJournalStore.mark_completed
    completed_calls = 0

    def drift_after_verifying(self, journal):
        verifying = original_mark_verified(self, journal)
        if race_kind == "preservation":
            preserved.write_bytes(b"changed but preserved\n")
        else:
            appeared = target_root / "spec-dock" / ".agent"
            appeared.mkdir()
            (appeared / "unknown.json").write_bytes(b"preserve me\n")
        return verifying

    def count_completed(self, journal):
        nonlocal completed_calls
        completed_calls += 1
        return original_mark_completed(self, journal)

    monkeypatch.setattr(OperationJournalStore, "mark_verified", drift_after_verifying)
    monkeypatch.setattr(OperationJournalStore, "mark_completed", count_completed)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.phase == "post-verify"
    assert result.last_completed_phase == "uninstall-applied"
    assert result.pending_paths == ()
    assert result.failed_paths == (expected_failed_path,)
    assert completed_calls == 0
    if race_kind == "preservation":
        assert preserved.read_bytes() == b"changed but preserved\n"
    else:
        assert (target_root / "spec-dock" / ".agent" / "unknown.json").read_bytes() == (b"preserve me\n")
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize("binding_path", [".", "spec-dock"])
def test_i370_deprovision_post_verify_rejects_remaining_binding_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    binding_path: str,
) -> None:
    """I370-T-RACE-001: terminal root and surviving parent bindings stay exact."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(
            recognized_workspace_versions=[
                {"version": "1.2.3", "anchors": [_regular_record("legacy-anchor", b"legacy\n")]},
            ],
        ),
    )
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    version = target_root / "spec-dock" / "spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("1.2.3\n", encoding="ascii")
    for relative_path in (
        "spec-dock/active",
        "spec-dock/.agent",
        "spec-dock/docs",
        "spec-dock/templates",
        "spec-dock/scripts",
        "spec-dock/system",
    ):
        (target_root / relative_path).mkdir(parents=True, exist_ok=True)
    (target_root / "spec").symlink_to("spec-dock/scripts/spec-dock")
    (target_root / "spec-dock" / ".gitignore").write_text(".agent/\n", encoding="utf-8")
    runtime_target = target_root / "spec-dock" / "scripts" / "spec-dock"
    runtime_target.write_text("#!/bin/sh\n", encoding="utf-8")
    runtime_target.chmod(0o755)
    workbench_seed = target_root / "spec-dock" / "templates" / "root" / ".workbench" / "README.md"
    workbench_seed.parent.mkdir(parents=True, exist_ok=True)
    workbench_seed.write_text("workbench\n", encoding="utf-8")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_mark_verified = OperationJournalStore.mark_verified
    original_mark_completed = OperationJournalStore.mark_completed
    completed_calls = 0

    def drift_after_verifying(self, journal):
        verifying = original_mark_verified(self, journal)
        path = target_root if binding_path == "." else target_root / binding_path
        mode = stat.S_IMODE(path.stat().st_mode)
        path.chmod(mode ^ 0o1)
        return verifying

    def count_completed(self, journal):
        nonlocal completed_calls
        completed_calls += 1
        return original_mark_completed(self, journal)

    monkeypatch.setattr(OperationJournalStore, "mark_verified", drift_after_verifying)
    monkeypatch.setattr(OperationJournalStore, "mark_completed", count_completed)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.phase == "post-verify"
    assert result.last_completed_phase == "uninstall-applied"
    assert result.pending_paths == ()
    assert result.failed_paths == (binding_path,), result.errors
    assert completed_calls == 0
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize(
    "crash_path",
    [".github/workflows/ci.yml", ".github/workflows", ".github"],
)
def test_i370_deprovision_retry_reconstructs_publish_from_exact_absence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    crash_path: str,
) -> None:
    """I370-T-REC-001: removal-before-checkpoint advances only from exact absence."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def fail_before_publish(self, journal, completed_paths):
        nonlocal interrupted
        if not interrupted and crash_path in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected pre-checkpoint interruption")
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        fail_before_publish,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "checkpoint_published",
        original_checkpoint,
    )

    assert interrupted is True
    assert first.status == "recovery_required"
    assert crash_path in first.pending_paths
    assert crash_path in first.failed_paths
    journal_payload = json.loads((target_root / "spec-dock" / ".distribution-journal.json").read_text(encoding="utf-8"))
    checkpoint = next(action["checkpoint"] for action in journal_payload["actions"] if action["path"] == crash_path)
    assert checkpoint == "pending"
    assert not (target_root / crash_path).exists()

    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert not (target_root / ".github").exists()
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i370_recovery_rejects_manifest_contract_drift_without_target_mutation(
    tmp_path: Path,
) -> None:
    """I370-T-SRC-001/I370-T-REC-001: pending recovery cannot outlive manifest authority."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest = _manifest_with(
        recognized_workspace_versions=[
            {
                "version": "1.2.3",
                "anchors": [_regular_record("legacy-anchor", b"legacy\n")],
            }
        ]
    )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    version = target_root / "spec-dock" / "spec-dock.version"
    version.parent.mkdir(parents=True)
    version.write_text("1.2.3\n", encoding="ascii")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    journal = store.prepare(executable, package_version="1.2.3")
    before = (managed.read_bytes(), version.read_bytes())

    drifted_manifest = _manifest_with(
        recognized_workspace_versions=[
            {
                "version": "1.2.3",
                "anchors": [_regular_record("legacy-anchor", b"legacy\n")],
            },
            {
                "version": "1.2.4",
                "anchors": [_regular_record("new-authority", b"new\n")],
            },
        ]
    )
    manifest_path.write_text(json.dumps(drifted_manifest), encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="journal-contract-mismatch"):
        managed_distribution._build_deprovision_recovery_contract_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
            journal=journal,
        )

    assert (managed.read_bytes(), version.read_bytes()) == before


def test_i370_recovery_contract_drift_precedes_checkpoint_reconciliation(
    tmp_path: Path,
) -> None:
    """I370-T-REC-001: source drift is rejected before pending absence is checkpointed."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    journal = store.prepare(executable, package_version="1.2.3")
    journal = store.mark_executing(journal)
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    journal_before = journal_path.read_bytes()

    # This is the state after the target mutation but before its durable
    # checkpoint: the pending target is absent while the journal is executing.
    managed.unlink()
    manifest_path.write_text(
        json.dumps(
            _manifest_with(
                recognized_workspace_versions=[
                    {
                        "version": "1.2.3",
                        "anchors": [_regular_record("legacy-anchor", b"legacy\n")],
                    }
                ]
            )
        ),
        encoding="utf-8",
    )

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert journal_path.read_bytes() == journal_before


@pytest.mark.parametrize("rehash", [False, True], ids=["stale-digest", "self-rehashed"])
def test_i370_deprovision_resume_rejects_journal_action_drift_against_canonical_plan(
    tmp_path: Path,
    rehash: bool,
) -> None:
    """I370-T-REC-001: journal action metadata must remain same-plan exact."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    forged_action = next(record for record in journal.actions if record.action == "prune")
    forged = replace(
        journal,
        actions=tuple(
            replace(record, reason="forged-action-reason") if record.path == forged_action.path else record
            for record in journal.actions
        ),
    )
    if rehash:
        forged = replace(
            forged,
            plan_digest=managed_distribution._deprovision_journal_plan_digest(forged),
        )
        marker = managed_distribution._read_distribution_retry_marker(target_root)
        assert marker is not None
        rebound_marker = store.prepare_legacy_guard(
            None,
            package_version="1.2.3",
            replace_marker=marker,
            plan_digest_override=forged.plan_digest,
            stage_ownership=marker.stage_ownership,
        )
        store.bind_forward_guard(rebound_marker)
    store.write(forged, predecessor=journal)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert managed.read_bytes() == b"managed\n"


def test_i370_deprovision_parent_rebind_fails_closed_before_target_write(
    tmp_path: Path,
) -> None:
    """I370-T-REC-001: a rebound directory parent cannot inherit prune authority."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    store.prepare(executable, package_version="1.2.3")

    rebound = target_root / ".github.rebound"
    (target_root / ".github").rename(rebound)
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert managed.read_bytes() == b"managed\n"
    assert rebound.is_dir()


def test_i370_recovery_absent_target_parent_rebind_fails_before_checkpoint(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    journal = store.mark_executing(store.prepare(executable, package_version="1.2.3"))
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    journal_before = journal_path.read_bytes()

    managed.unlink()
    rebound = target_root / ".github.rebound"
    (target_root / ".github").rename(rebound)
    managed.parent.mkdir(parents=True)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert journal_path.read_bytes() == journal_before
    assert rebound.is_dir()
    assert managed.parent.is_dir()
    assert journal.status == "executing"


def test_i370_reconcile_pending_absence_rebind_fails_before_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A parent rebind between reconciliation proof and checkpoint is not cleanup authority."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    journal = store.mark_executing(store.prepare(executable, package_version="1.2.3"))
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    original_checkpoint = OperationJournalStore.checkpoint_published
    interrupted = False

    def interrupt_before_publish(self, active, completed_paths):
        nonlocal interrupted
        if not interrupted and ".github/workflows/ci.yml" in completed_paths:
            interrupted = True
            raise DistributionApplyError("injected pre-checkpoint interruption")
        return original_checkpoint(self, active, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", interrupt_before_publish)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    assert interrupted is True
    assert first.status == "recovery_required"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    displaced = target_root / ".github" / "workflows-displaced"
    original_validator = managed_distribution._validate_deprovision_recovery_leaf_parent_namespaces
    validation_calls = 0
    checkpoint_calls = 0
    rebound = False

    def rebind_after_reconcile_validation(*args, **kwargs):
        nonlocal validation_calls, rebound
        result = original_validator(*args, **kwargs)
        validation_calls += 1
        # The first call is the pre-reconciliation contract check, the second
        # is reconciliation's initial summary, and the third is the pending
        # action's immediate pre-checkpoint validation.
        if validation_calls == 3:
            managed.parent.rename(displaced)
            managed.parent.mkdir(parents=True)
            rebound = True
        return result

    def count_checkpoint(*args, **kwargs):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(*args, **kwargs)

    monkeypatch.setattr(
        managed_distribution,
        "_validate_deprovision_recovery_leaf_parent_namespaces",
        rebind_after_reconcile_validation,
    )
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert rebound is True, (validation_calls, result.status, result.reason, result.errors, result.failed_paths)
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert checkpoint_calls == 0
    assert displaced.is_dir()
    assert managed.parent.is_dir()
    assert not managed.exists()
    assert journal.status == "executing"


@pytest.mark.parametrize("replacement_kind", ["regular", "symlink"])
def test_i370_marker_replacement_fails_before_leaf_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement_kind: str,
) -> None:
    """A retry-marker identity rebind cannot authorize a deprovision mutation."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    specdock = target_root / "spec-dock"
    specdock.mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"managed\n")
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    journal_path = specdock / ".distribution-journal.json"
    marker_path = specdock / ".distribution-retry.json"
    replacement = specdock / ".replacement-marker"
    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    injected = False
    post_reservation_state: tuple[bytes, bytes] | None = None
    target_rename_calls = 0
    leaf_parent_fd: int | None = None
    leaf_unlink_calls = 0
    checkpoint_calls = 0

    def replace_marker_after_reservation(self, journal, lease):
        nonlocal injected, post_reservation_state
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == ".github/workflows/ci.yml"
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            marker_bytes = marker_path.read_bytes()
            replacement.write_bytes(marker_bytes)
            marker_path.unlink()
            if replacement_kind == "regular":
                marker_path.write_bytes(marker_bytes)
            else:
                marker_path.symlink_to(replacement.name)
            post_reservation_state = (journal_path.read_bytes(), marker_path.read_bytes())
        return updated

    def count_rename(*args, **kwargs):
        nonlocal target_rename_calls
        if args[1] == target.name and args[3] != target.name:
            target_rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_remove(*args, **kwargs):
        nonlocal leaf_parent_fd
        leaf_parent_fd = args[0]
        return original_remove(*args, **kwargs)

    def count_unlink(path, *args, **kwargs):
        nonlocal leaf_unlink_calls
        if kwargs.get("dir_fd") == leaf_parent_fd:
            leaf_unlink_calls += 1
        return original_unlink(path, *args, **kwargs)

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    target_before = (target.lstat(), target.read_bytes())
    outside_before = outside.read_bytes()
    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", replace_marker_after_reservation)
    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert post_reservation_state is not None
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-required"
    assert target.lstat() == target_before[0]
    assert target.read_bytes() == target_before[1]
    assert outside.read_bytes() == outside_before
    assert journal_path.read_bytes() == post_reservation_state[0]
    assert marker_path.read_bytes() == post_reservation_state[1]
    assert marker_path.is_symlink() if replacement_kind == "symlink" else marker_path.is_file()
    assert replacement.is_file()
    assert target_rename_calls == 0
    assert leaf_unlink_calls == 0
    assert checkpoint_calls == 0


def test_i370_roleless_backup_promotion_rejects_rebound_parent_before_journal_write(
    tmp_path: Path,
) -> None:
    """Legacy backup promotion must not rewrite the journal after a parent rebind."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    specdock = target_root / "spec-dock"
    specdock.mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    target_rel = ".github/workflows/ci.yml"
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, target_rel)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(target_rel, expected)
    quarantine_name = f"{stage_name}.fixture.remove"
    backup_name = managed_distribution._distribution_quarantine_backup_name(quarantine_name)
    target.unlink()
    displaced = target_root / ".github" / "workflows-displaced"
    target.parent.rename(displaced)
    target.parent.mkdir()
    backup = target.parent / backup_name
    backup.write_bytes(b"managed\n")
    backup_info = backup.lstat()
    quarantine = DistributionStageOwnership(
        path=target_rel,
        stage_name=quarantine_name,
        device=backup_info.st_dev,
        inode=backup_info.st_ino,
        ctime_ns=backup_info.st_ctime_ns,
        file_type="regular",
        role="predecessor-quarantine",
    )
    roleless_backup = DistributionStageOwnership(
        path=target_rel,
        stage_name=backup_name,
        device=backup_info.st_dev,
        inode=backup_info.st_ino,
        ctime_ns=backup_info.st_ctime_ns,
        file_type="regular",
        role="stage",
    )
    journal = store.write(
        managed_distribution.replace(
            journal,
            actions=tuple(
                managed_distribution.replace(action, checkpoint="published") if action.path == target_rel else action
                for action in journal.actions
            ),
            staging_leases=(quarantine, roleless_backup),
        ),
        predecessor=journal,
    )
    journal_path = specdock / ".distribution-journal.json"
    marker_path = specdock / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    validator = managed_distribution._deprovision_recovery_leaf_mutation_validator(
        store,
        journal,
        forward_guard=store._forward_guard,
    )

    with pytest.raises(DistributionApplyError, match="deprovision-visible-parent-chain-mismatch"):
        store._resume_displaced_quarantine_cleanup(
            journal,
            {target_rel},
            leaf_mutation_validator=validator,
        )

    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert backup.read_bytes() == b"managed\n"
    assert not target.exists()
    assert displaced.is_dir()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("replacement_kind", ["regular", "symlink"])
@pytest.mark.parametrize("race", ["parent-rebind", "marker-replacement"])
def test_i370_roleless_backup_promotion_rechecks_marker_before_journal_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    replacement_kind: str,
    race: str,
) -> None:
    """I370-T-REC-001: roleless promotion binds current recovery state immediately before writing."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    target_root = tmp_path / "consumer"
    specdock = target_root / "spec-dock"
    specdock.mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    if kind == "regular":
        target.write_bytes(b"managed\n")
    else:
        source.unlink()
        source.symlink_to("managed-target")
        target.symlink_to("managed-target")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    target_rel = ".github/workflows/ci.yml"
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, target_rel)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(target_rel, expected)
    quarantine_name = f"{stage_name}.fixture.remove"
    backup_name = managed_distribution._distribution_quarantine_backup_name(quarantine_name)
    target.unlink()
    if kind == "regular":
        backup = target.parent / backup_name
        backup.write_bytes(b"managed\n")
    else:
        backup = target.parent / backup_name
        backup.symlink_to("managed-target")
    backup_info = backup.lstat()
    quarantine = DistributionStageOwnership(
        path=target_rel,
        stage_name=quarantine_name,
        device=backup_info.st_dev,
        inode=backup_info.st_ino,
        ctime_ns=backup_info.st_ctime_ns,
        file_type=("regular" if kind == "regular" else "symlink"),
        role="predecessor-quarantine",
    )
    roleless_backup = DistributionStageOwnership(
        path=target_rel,
        stage_name=backup_name,
        device=backup_info.st_dev,
        inode=backup_info.st_ino,
        ctime_ns=backup_info.st_ctime_ns,
        file_type=("regular" if kind == "regular" else "symlink"),
        role="stage",
    )
    journal = store.write(
        managed_distribution.replace(
            journal,
            actions=tuple(
                managed_distribution.replace(action, checkpoint="published") if action.path == target_rel else action
                for action in journal.actions
            ),
            staging_leases=(quarantine, roleless_backup),
        ),
        predecessor=journal,
    )
    journal_path = specdock / ".distribution-journal.json"
    marker_path = specdock / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    replacement = specdock / ".marker-replacement"
    displaced = target_root / ".github" / "workflows-displaced"
    injected = False
    promotion_phase = False
    original_promote = OperationJournalStore._promote_roleless_backup_leases

    def mark_promotion(self, active, **kwargs):
        nonlocal promotion_phase
        promotion_phase = True
        try:
            return original_promote(self, active, **kwargs)
        finally:
            promotion_phase = False

    actual_validator = managed_distribution._deprovision_recovery_leaf_mutation_validator

    def validate_promotion_boundary(path: str, parent_chain: tuple[int, ...]) -> None:
        nonlocal injected
        if promotion_phase and not injected:
            if race == "parent-rebind":
                target.parent.rename(displaced)
                target.parent.mkdir()
            else:
                replacement.write_bytes(marker_before)
                marker_path.unlink()
                if replacement_kind == "regular":
                    replacement.rename(marker_path)
                else:
                    marker_path.symlink_to(replacement.name)
            injected = True
        actual_validator(store, journal, forward_guard=store._forward_guard)(path, parent_chain)

    monkeypatch.setattr(OperationJournalStore, "_promote_roleless_backup_leases", mark_promotion)

    with pytest.raises(DistributionApplyError):
        store._resume_displaced_quarantine_cleanup(
            journal,
            {target_rel},
            leaf_mutation_validator=validate_promotion_boundary,
        )

    assert injected is True
    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    if race == "marker-replacement":
        assert marker_path.is_symlink() if replacement_kind == "symlink" else marker_path.is_file()
        assert backup.exists() or backup.is_symlink()
    else:
        assert displaced.is_dir()
        assert (displaced / backup.name).exists() or (displaced / backup.name).is_symlink()
    assert not target.exists() and not target.is_symlink()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i370_resume_displaced_backup_only_marker_rebind_stops_before_gc(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    """Backup-only deprovision recovery validates the guard before GC cleanup."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    if kind == "regular":
        target.write_bytes(b"managed\n")
    else:
        source.unlink()
        source.symlink_to("managed-target")
        target.symlink_to("managed-target")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    class SimulatedProcessCrash(BaseException):
        pass

    original_record = OperationJournalStore.record_staging_lease
    interrupted = False

    def crash_after_backup_only(self, journal, lease):
        nonlocal interrupted
        updated = original_record(self, journal, lease)
        if not interrupted and lease.role == "backup-only":
            interrupted = True
            raise SimulatedProcessCrash
        return updated

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", crash_after_backup_only)
    with pytest.raises(SimulatedProcessCrash):
        managed_distribution.execute_deprovision_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            package_version="1.2.3",
            apply=True,
            expected_root_identity=root_identity,
        )
    assert interrupted is True
    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", original_record)

    target_rel = ".github/workflows/ci.yml"
    specdock = target_root / "spec-dock"
    journal_path = specdock / ".distribution-journal.json"
    marker_path = specdock / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    payload = json.loads(journal_before)
    backup_leases = [
        lease for lease in payload["staging_leases"] if lease["path"] == target_rel and lease["role"] == "backup-only"
    ]
    assert len(backup_leases) == 1
    backup = target.parent / backup_leases[0]["stage_name"]
    assert backup.exists() or backup.is_symlink()
    backup_before = backup.lstat()
    backup_payload = backup.read_bytes() if kind == "regular" else backup.readlink()
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    outside_before = (outside.read_bytes(), outside.lstat())

    replacement = specdock / ".marker-replacement"
    marker_rebound: os.stat_result | None = None
    original_namespace_validator = managed_distribution._validate_deprovision_recovery_leaf_parent_namespaces
    injected = False

    def replace_marker_after_namespace_validation(*args, **kwargs):
        nonlocal injected, marker_rebound
        result = original_namespace_validator(*args, **kwargs)
        if not injected:
            replacement.write_bytes(marker_before)
            marker_path.unlink()
            replacement.rename(marker_path)
            marker_rebound = marker_path.lstat()
            injected = True
        return result

    original_rename = managed_distribution._rename_distribution_no_replace
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    rename_calls = 0
    unlink_calls = 0
    checkpoint_calls = 0

    def count_rename(*args, **kwargs):
        nonlocal rename_calls
        rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_unlink(*args, **kwargs):
        nonlocal unlink_calls
        if kwargs.get("dir_fd") is not None:
            unlink_calls += 1
        return original_unlink(*args, **kwargs)

    def count_checkpoint(*args, **kwargs):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    monkeypatch.setattr(
        managed_distribution,
        "_validate_deprovision_recovery_leaf_parent_namespaces",
        replace_marker_after_namespace_validation,
    )
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert marker_rebound is not None
    assert result.status == "recovery_required"
    assert result.reason in {"deprovision-recovery-required", "deprovision-recovery-mismatch"}
    assert not target.exists() and not target.is_symlink()
    assert backup.lstat() == backup_before
    assert (backup.read_bytes() if kind == "regular" else backup.readlink()) == backup_payload
    assert outside.lstat() == outside_before[1]
    assert outside.read_bytes() == outside_before[0]
    assert journal_path.read_bytes() == journal_before
    assert marker_path.lstat() == marker_rebound
    assert marker_path.read_bytes() == marker_before
    assert rename_calls == 0
    assert unlink_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize(
    ("kind", "ordinal", "rebind"),
    [(kind, ordinal, True) for kind in ("regular", "symlink") for ordinal in (1, 2, 3)]
    + [("regular", 3, False), ("symlink", 3, False)],
    ids=[
        *(f"{kind}-ordinal-{ordinal}-rebind" for kind in ("regular", "symlink") for ordinal in (1, 2, 3)),
        "regular-terminal-complete",
        "symlink-terminal-complete",
    ],
)
def test_i370_resume_gc_cleanup_deprovision_boundary_is_parent_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    ordinal: int,
    rebind: bool,
) -> None:
    """GC ordinal transitions must use the deprovision attachment boundary."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    if kind == "regular":
        target.write_bytes(b"managed\n")
    else:
        source.unlink()
        source.symlink_to("managed-target")
        target.symlink_to("managed-target")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    target_rel = ".github/workflows/ci.yml"
    target.unlink()
    parent = target.parent

    def create_payload(path: Path) -> None:
        if kind == "regular":
            path.write_bytes(b"managed\n")
        else:
            path.symlink_to("managed-target")

    def lease_for(
        path: str,
        info: os.stat_result,
        *,
        role: Literal[
            "stage",
            "predecessor-quarantine",
            "backup-reserved",
            "backup-dual",
            "backup-only-reserved",
            "backup-only",
            "gc-reserved",
            "gc-exact",
        ],
        predecessor: str | None = None,
    ):
        return DistributionStageOwnership(
            path=target_rel,
            stage_name=path,
            device=info.st_dev,
            inode=info.st_ino,
            ctime_ns=info.st_ctime_ns,
            file_type=("regular" if kind == "regular" else "symlink"),
            role=role,
            gc_predecessor_name=predecessor,
            gc_ordinal=ordinal if predecessor is not None else None,
        )

    if ordinal == 1:
        source_name = ".spec-dock-gc-source.remove"
        gc_name = ".spec-dock-gc-ordinal-1.gc"
        create_payload(parent / source_name)
        os.link(parent / source_name, parent / gc_name, follow_symlinks=False)
        source_info = (parent / source_name).lstat()
        leases = (
            lease_for(source_name, source_info, role="stage"),
            lease_for(gc_name, source_info, role="gc-exact", predecessor=source_name),
        )
    elif ordinal == 2:
        predecessor_name = ".spec-dock-gc-ordinal-1.gc"
        backup_name = managed_distribution._distribution_quarantine_backup_name(predecessor_name)
        gc_name = ".spec-dock-gc-ordinal-2.gc"
        create_payload(parent / backup_name)
        os.link(parent / backup_name, parent / gc_name, follow_symlinks=False)
        backup_info = (parent / backup_name).lstat()
        leases = (
            lease_for(backup_name, backup_info, role="backup-dual"),
            lease_for(gc_name, backup_info, role="gc-exact", predecessor=predecessor_name),
        )
    else:
        predecessor_name = ".spec-dock-gc-terminal-backup"
        gc_name = ".spec-dock-gc-ordinal-3.gc"
        create_payload(parent / gc_name)
        gc_info = (parent / gc_name).lstat()
        leases = (
            lease_for(predecessor_name, gc_info, role="backup-dual"),
            lease_for(gc_name, gc_info, role="gc-exact", predecessor=predecessor_name),
        )
    journal = store.write(
        managed_distribution.replace(journal, staging_leases=leases),
        predecessor=journal,
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    outside_before = (outside.read_bytes(), outside.lstat())

    def stable_entry_state(path: Path) -> tuple[tuple[int, ...], bytes | Path]:
        info = path.lstat()
        # Reading a symlink can update st_atime under Linux relatime; it is not a mutation.
        stat_fields = (
            info.st_mode,
            info.st_ino,
            info.st_dev,
            info.st_nlink,
            info.st_uid,
            info.st_gid,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        )
        payload = path.read_bytes() if kind == "regular" else path.readlink()
        return stat_fields, payload

    private_entries = {path.name: stable_entry_state(path) for path in parent.iterdir()}
    displaced = target_root / ".github" / "workflows-displaced"
    injected = False

    def validate_boundary(path: str, parent_chain: tuple[int, ...]) -> None:
        nonlocal injected
        managed_distribution._assert_deprovision_recovery_marker_bound(store, store._forward_guard)
        if rebind and not injected:
            parent.rename(displaced)
            parent.mkdir()
            injected = True
        managed_distribution._assert_visible_distribution_chain_exactly_bound(target_root, path, parent_chain)

    original_rename = managed_distribution._rename_distribution_no_replace
    original_unlink = managed_distribution.os.unlink
    rename_calls = 0
    unlink_calls = 0

    def count_rename(*args, **kwargs):
        nonlocal rename_calls
        rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_unlink(*args, **kwargs):
        nonlocal unlink_calls
        if kwargs.get("dir_fd") is not None:
            unlink_calls += 1
        return original_unlink(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    if rebind:
        with pytest.raises(DistributionApplyError, match="deprovision-visible-parent-chain-mismatch"):
            store._resume_gc_cleanup(journal, leaf_mutation_validator=validate_boundary)
        assert injected is True
        assert journal_path.read_bytes() == journal_before
        assert marker_path.read_bytes() == marker_before
        assert target.exists() is False and target.is_symlink() is False
        assert outside.lstat() == outside_before[1]
        assert outside.read_bytes() == outside_before[0]
        assert rename_calls == 0
        assert unlink_calls == 0
        assert {path.name: stable_entry_state(path) for path in displaced.iterdir()} == private_entries
    else:
        completed = store._resume_gc_cleanup(journal, leaf_mutation_validator=validate_boundary)
        assert completed.status == "executing"
        assert not any((parent / name).exists() or (parent / name).is_symlink() for name in private_entries)
        assert not target.exists() and not target.is_symlink()
        if kind == "symlink":
            assert private_entries[".spec-dock-gc-ordinal-3.gc"][1] == Path("managed-target")
        current_marker = managed_distribution._read_distribution_retry_marker(target_root)
        assert current_marker is not None
        assert current_marker.operation == "deprovision"
        assert current_marker.operation_id == completed.operation_id
        assert current_marker.plan_digest == completed.plan_digest
        assert current_marker.journal_digest == completed.source_sha256
        assert journal_path.read_bytes() == managed_distribution._journal_bytes(completed)
        assert not any(lease.path == target_rel for lease in completed.staging_leases)
        assert rename_calls > 0
        assert unlink_calls > 0


def test_i370_pending_directory_reappearance_fails_before_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pending directory rebind cannot be published by recovery reconciliation."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    store = OperationJournalStore(target_root)
    executable = build_executable_mutation_plan(
        managed_distribution.build_deprovision_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            expected_root_identity=root_identity,
        )
    )
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    store.prepare(executable, package_version="1.2.3")
    original_remove_directory = managed_distribution._remove_distribution_directory_if_bound
    interrupted = False

    def remove_directory_then_interrupt(*args, **kwargs):
        nonlocal interrupted
        result = original_remove_directory(*args, **kwargs)
        if not interrupted and args[1].as_posix() == ".github/workflows":
            interrupted = True
            raise DistributionApplyError("injected after pending directory removal")
        return result

    monkeypatch.setattr(
        managed_distribution, "_remove_distribution_directory_if_bound", remove_directory_then_interrupt
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    assert interrupted is True
    assert first.status == "recovery_required"
    monkeypatch.setattr(managed_distribution, "_remove_distribution_directory_if_bound", original_remove_directory)

    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()
    original_validator = managed_distribution._validate_deprovision_recovery_leaf_parent_namespaces
    validation_calls = 0
    rebound = False
    checkpoint_calls = 0
    original_checkpoint = OperationJournalStore.checkpoint_published

    def reappear_after_pending_validation(*args, **kwargs):
        nonlocal validation_calls, rebound
        result = original_validator(*args, **kwargs)
        validation_calls += 1
        if validation_calls == 3:
            managed.parent.mkdir(parents=True)
            rebound = True
        return result

    def count_checkpoint(*args, **kwargs):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(*args, **kwargs)

    monkeypatch.setattr(
        managed_distribution,
        "_validate_deprovision_recovery_leaf_parent_namespaces",
        reappear_after_pending_validation,
    )
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert rebound is True, (validation_calls, result.status, result.reason, result.errors)
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert checkpoint_calls == 0
    assert managed.parent.is_dir()
    assert not managed.exists()


def test_i370_deprovision_parent_mode_drift_fails_closed_before_target_write(
    tmp_path: Path,
) -> None:
    """I370-T-REC-001: parent mode drift is part of the immutable prune binding."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    managed.parent.chmod(0o755)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    store.prepare(executable, package_version="1.2.3")

    managed.parent.chmod(0o700)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-mismatch"
    assert managed.read_bytes() == b"managed\n"


@pytest.mark.parametrize("target_kind", ["regular", "symlink"])
def test_i370_zero_predecessor_reservation_collision_is_not_operation_owned(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
) -> None:
    """A zero lease cannot hide an external same-name stage entry."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    if target_kind == "regular":
        target_rel = ".github/workflows/ci.yml"
        target = target_root / target_rel
        target.parent.mkdir(parents=True)
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target_rel = "legacy-shortcut"
        target = target_root / target_rel
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_record = OperationJournalStore.record_staging_lease
    injected = False

    def inject_external_stage(self, journal, lease):
        nonlocal injected
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            stage = target.parent / lease.stage_name
            if target_kind == "regular":
                stage.write_bytes(b"external\n")
            else:
                stage.symlink_to("external-target")
        return updated

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", inject_external_stage)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert first.status == "recovery_required"
    target_payload = target.read_bytes() if target_kind == "regular" else target.readlink()
    target_stat = target.lstat()
    stage = next(target.parent.glob(".spec-dock-*"))
    stage_payload = stage.read_bytes() if target_kind == "regular" else stage.readlink()
    stage_stat = stage.lstat()
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", original_record)
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_checkpoint = OperationJournalStore.checkpoint_published
    remove_calls = 0
    checkpoint_calls = 0

    def count_remove(*args, **kwargs):
        nonlocal remove_calls
        remove_calls += 1
        return original_remove(*args, **kwargs)

    def count_checkpoint(*args, **kwargs):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "recovery_required"
    assert retry.reason == "deprovision-recovery-mismatch"
    assert (target.read_bytes() if target_kind == "regular" else target.readlink()) == target_payload
    assert target.lstat() == target_stat
    assert (stage.read_bytes() if target_kind == "regular" else stage.readlink()) == stage_payload
    assert stage.lstat() == stage_stat
    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert remove_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize("target_kind", ["regular", "symlink"])
def test_i370_zero_predecessor_reservation_after_rename_remains_recoverable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
) -> None:
    """A zero lease with the canonical target already absent may be resumed."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    if target_kind == "regular":
        target_rel = ".github/workflows/ci.yml"
        target = target_root / target_rel
        target.parent.mkdir(parents=True)
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target_rel = "legacy-shortcut"
        target = target_root / target_rel
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_rename = managed_distribution._rename_distribution_no_replace
    crashed = False

    def rename_then_interrupt(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal crashed
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if source_name == target.name and destination_name.startswith((".spec-dock-file-", ".spec-dock-symlink-")):
            crashed = True
            raise OSError("injected post-rename interruption")

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", rename_then_interrupt)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert crashed is True
    assert first.status == "recovery_required"
    assert not target.exists()
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    lease = next(item for item in journal_payload["staging_leases"] if item["path"] == target_rel)
    assert lease["device"] == lease["inode"] == lease["ctime_ns"] == 0
    stage = target.parent / lease["stage_name"]
    assert stage.exists() or stage.is_symlink()

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", original_rename)
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed", retry.reason
    assert not target.exists()
    assert not stage.exists()


@pytest.mark.parametrize("target_kind", ["regular", "symlink"])
def test_i370_zero_predecessor_reservation_before_rename_is_reusable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
) -> None:
    """A durable zero lease before rename can be retried without a stage entry."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    if target_kind == "regular":
        target_rel = ".github/workflows/ci.yml"
        target = target_root / target_rel
        target.parent.mkdir(parents=True)
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target_rel = "legacy-shortcut"
        target = target_root / target_rel
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_record = OperationJournalStore.record_staging_lease
    injected = False

    def record_then_interrupt(self, journal, lease):
        nonlocal injected
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            raise OSError("injected pre-rename interruption")
        return updated

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", record_then_interrupt)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert first.status == "recovery_required"
    assert target.exists() if target_kind == "regular" else target.is_symlink()
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    lease = next(item for item in journal_payload["staging_leases"] if item["path"] == target_rel)
    assert lease["device"] == lease["inode"] == lease["ctime_ns"] == 0
    stage = target.parent / lease["stage_name"]
    assert not stage.exists() and not stage.is_symlink()

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", original_record)
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed", retry.reason
    assert not target.exists() and not target.is_symlink()
    assert not stage.exists() and not stage.is_symlink()
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()


@pytest.mark.parametrize(
    ("target_kind", "target_rel"),
    [
        ("regular", ".github/workflows/ci.yml"),
        ("symlink", "legacy-shortcut"),
    ],
)
def test_i370_zero_predecessor_reservation_reissue_rejects_old_stage_appearance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
    target_rel: str,
) -> None:
    """A retry must not issue a new stage name after reusing a zero lease."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if target_kind == "regular":
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_record = OperationJournalStore.record_staging_lease
    interrupted = False

    def record_then_interrupt(self, journal, lease):
        nonlocal interrupted
        updated = original_record(self, journal, lease)
        if (
            not interrupted
            and lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            interrupted = True
            raise OSError("injected pre-rename interruption")
        return updated

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", record_then_interrupt)
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert interrupted is True
    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    old_stage_name = next(
        item["stage_name"]
        for item in journal_payload["staging_leases"]
        if item["path"] == target_rel and item["role"] == "predecessor-quarantine"
    )
    old_stage = target.parent / old_stage_name
    assert not old_stage.exists() and not old_stage.is_symlink()
    target_before = (
        target.lstat(),
        target.read_bytes() if target_kind == "regular" else target.readlink(),
    )
    journal_before = journal_path.read_bytes()
    marker_before = marker_path.read_bytes()

    original_checkpoint = OperationJournalStore.checkpoint_published
    original_unlink = managed_distribution.os.unlink
    checkpoint_calls = 0
    remove_calls = 0

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    def count_remove(*args, **kwargs):
        nonlocal remove_calls
        remove_calls += 1
        return original_unlink(*args, **kwargs)

    def expose_old_stage_after_reservation(self, journal, lease):
        updated = original_record(self, journal, lease)
        if (
            lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            if target_kind == "regular":
                old_stage.write_bytes(b"external\n")
            else:
                old_stage.symlink_to("external-target")
        return updated

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", expose_old_stage_after_reservation)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_remove)
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "recovery_required"
    assert retry.reason == "deprovision-recovery-required"
    assert (
        target.lstat(),
        target.read_bytes() if target_kind == "regular" else target.readlink(),
    ) == target_before
    assert (old_stage.read_bytes() if target_kind == "regular" else old_stage.readlink()) == (
        b"external\n" if target_kind == "regular" else Path("external-target")
    )
    assert journal_path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert remove_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize(
    ("target_kind", "unknown_kind"),
    [
        ("regular", "regular"),
        ("regular", "symlink"),
        ("symlink", "regular"),
        ("symlink", "symlink"),
    ],
)
def test_i370_leaf_prune_rejects_unknown_nested_parent_sibling_after_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
    unknown_kind: str,
) -> None:
    """I370-T-RACE-001: a new nested sibling cannot pass the prune lease boundary."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target_rel = ".github/workflows/ci.yml" if target_kind == "regular" else ".github/workflows/legacy-shortcut"
    target = target_root / target_rel
    target.parent.mkdir(parents=True)
    if target_kind == "regular":
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "nested-legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    unknown = target.parent / "unexpected-sibling"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    injected = False
    post_reservation_state: tuple[bytes, bytes] | None = None
    target_rename_calls = 0
    leaf_parent_fd: int | None = None
    leaf_unlink_calls = 0
    checkpoint_calls = 0

    def inject_unknown_sibling(self, journal, lease):
        nonlocal injected, post_reservation_state
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            if unknown_kind == "regular":
                unknown.write_bytes(b"user-owned\n")
            else:
                unknown.symlink_to("user-owned-target")
            post_reservation_state = (journal_path.read_bytes(), marker_path.read_bytes())
        return updated

    def count_rename(*args, **kwargs):
        nonlocal target_rename_calls
        if args[1] == target.name and args[3] != target.name:
            target_rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_remove(*args, **kwargs):
        nonlocal leaf_parent_fd
        leaf_parent_fd = args[0]
        return original_remove(*args, **kwargs)

    def count_unlink(path, *args, **kwargs):
        nonlocal leaf_unlink_calls
        if kwargs.get("dir_fd") == leaf_parent_fd:
            leaf_unlink_calls += 1
        return original_unlink(path, *args, **kwargs)

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", inject_unknown_sibling)
    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)
    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert post_reservation_state is not None
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-required"
    assert unknown.is_symlink() if unknown_kind == "symlink" else unknown.is_file()
    assert target.is_symlink() if target_kind == "symlink" else target.is_file()
    assert (
        unknown.readlink() == Path("user-owned-target")
        if unknown_kind == "symlink"
        else unknown.read_bytes() == b"user-owned\n"
    )
    assert (
        target.readlink() == Path("legacy-target") if target_kind == "symlink" else target.read_bytes() == b"managed\n"
    )
    assert target.parent.relative_to(target_root).as_posix() in result.failed_paths
    assert journal_path.read_bytes() == post_reservation_state[0]
    assert marker_path.read_bytes() == post_reservation_state[1]
    assert target_rename_calls == 0
    assert leaf_unlink_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize("sibling_kind", ["regular", "symlink"])
def test_i370_leaf_prune_rejects_unknown_nonremovable_parent_sibling_after_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sibling_kind: str,
) -> None:
    """I370-T-RACE-001: a non-removable bounded parent still has a namespace witness."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path / "manifest",
        _manifest_with(
            recognized_workspace_versions=[
                {"version": "1.2.3", "anchors": [_regular_record("legacy-anchor", b"legacy\n")]}
            ],
        ),
    )
    target_root = tmp_path / "consumer"
    specdock = target_root / "spec-dock"
    specdock.mkdir(parents=True)
    target = specdock / "spec-dock.version"
    target.write_text("1.2.3\n", encoding="ascii")
    sibling = specdock / "external-sibling"
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    journal_path = specdock / ".distribution-journal.json"
    marker_path = specdock / ".distribution-retry.json"
    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    injected = False
    post_reservation_state: tuple[bytes, bytes] | None = None
    target_rename_calls = 0
    leaf_parent_fd: int | None = None
    leaf_unlink_calls = 0
    checkpoint_calls = 0

    def inject_unknown_sibling(self, journal, lease):
        nonlocal injected, post_reservation_state
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == "spec-dock/spec-dock.version"
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            if sibling_kind == "regular":
                sibling.write_bytes(b"user-owned\n")
            else:
                sibling.symlink_to("user-owned-target")
            post_reservation_state = (journal_path.read_bytes(), marker_path.read_bytes())
        return updated

    def count_rename(*args, **kwargs):
        nonlocal target_rename_calls
        if args[1] == target.name and args[3] != target.name:
            target_rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_remove(*args, **kwargs):
        nonlocal leaf_parent_fd
        leaf_parent_fd = args[0]
        return original_remove(*args, **kwargs)

    def count_unlink(path, *args, **kwargs):
        nonlocal leaf_unlink_calls
        if kwargs.get("dir_fd") == leaf_parent_fd:
            leaf_unlink_calls += 1
        return original_unlink(path, *args, **kwargs)

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    target_before = (target.lstat(), target.read_bytes())
    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", inject_unknown_sibling)
    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert post_reservation_state is not None
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-required"
    assert target.lstat() == target_before[0]
    assert target.read_bytes() == target_before[1]
    assert sibling.is_symlink() if sibling_kind == "symlink" else sibling.is_file()
    assert (
        sibling.readlink() == Path("user-owned-target")
        if sibling_kind == "symlink"
        else sibling.read_bytes() == b"user-owned\n"
    )
    assert "spec-dock" in result.failed_paths
    assert journal_path.read_bytes() == post_reservation_state[0]
    assert marker_path.read_bytes() == post_reservation_state[1]
    assert target_rename_calls == 0
    assert leaf_unlink_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize("replacement_kind", ["regular", "symlink"])
def test_i370_leaf_prune_rejects_known_sibling_identity_replacement_after_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement_kind: str,
) -> None:
    """I370-T-RACE-001: an existing removable parent compares sibling identity, not names."""

    install_root = _minimal_install_root(tmp_path, b"first-managed\n")
    second_source = install_root / ".github" / "workflows" / "second.yml"
    second_source.write_bytes(b"second-managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target_parent = target_root / ".github" / "workflows"
    target_parent.mkdir(parents=True)
    target = target_parent / "ci.yml"
    sibling = target_parent / "second.yml"
    target.write_bytes(b"first-managed\n")
    sibling.write_bytes(b"second-managed\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    injected = False
    post_reservation_state: tuple[bytes, bytes] | None = None
    target_rename_calls = 0
    leaf_parent_fd: int | None = None
    leaf_unlink_calls = 0
    checkpoint_calls = 0

    def replace_known_sibling(self, journal, lease):
        nonlocal injected, post_reservation_state
        updated = original_record(self, journal, lease)
        if (
            not injected
            and lease.path == ".github/workflows/ci.yml"
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            injected = True
            sibling.unlink()
            if replacement_kind == "regular":
                sibling.write_bytes(b"rebound-identity\n")
            else:
                sibling.symlink_to("external-target")
            post_reservation_state = (journal_path.read_bytes(), marker_path.read_bytes())
        return updated

    def count_rename(*args, **kwargs):
        nonlocal target_rename_calls
        if args[1] == target.name and args[3] != target.name:
            target_rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_remove(*args, **kwargs):
        nonlocal leaf_parent_fd
        leaf_parent_fd = args[0]
        return original_remove(*args, **kwargs)

    def count_unlink(path, *args, **kwargs):
        nonlocal leaf_unlink_calls
        if kwargs.get("dir_fd") == leaf_parent_fd:
            leaf_unlink_calls += 1
        return original_unlink(path, *args, **kwargs)

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    target_before = (target.lstat(), target.read_bytes())
    sibling_before = (sibling.lstat(), sibling.read_bytes())
    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", replace_known_sibling)
    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert injected is True
    assert post_reservation_state is not None
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-required"
    assert target.lstat() == target_before[0]
    assert target.read_bytes() == target_before[1]
    if replacement_kind == "regular":
        assert sibling.read_bytes() == b"rebound-identity\n"
    else:
        assert sibling.is_symlink()
        assert sibling.readlink() == Path("external-target")
    assert sibling.lstat() != sibling_before[0]
    assert ".github/workflows" in result.failed_paths
    assert journal_path.read_bytes() == post_reservation_state[0]
    assert marker_path.read_bytes() == post_reservation_state[1]
    assert target_rename_calls == 0
    assert leaf_unlink_calls == 0
    assert checkpoint_calls == 0


@pytest.mark.parametrize("target_kind", ["regular", "symlink"])
@pytest.mark.parametrize("rebind_kind", ["parent", "ancestor"])
def test_i370_leaf_prune_rejects_visible_parent_rebind_after_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target_kind: str,
    rebind_kind: str,
) -> None:
    """I370-T-RACE-001: a held parent cannot authorize a rebound visible parent."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    if target_kind == "regular":
        target_rel = ".github/workflows/ci.yml"
        target = target_root / target_rel
        target.parent.mkdir(parents=True)
        target.write_bytes(b"managed\n")
        manifest = _manifest_with()
    else:
        target_rel = ".github/workflows/legacy-shortcut"
        target = target_root / target_rel
        target.parent.mkdir(parents=True)
        target.symlink_to("legacy-target")
        manifest = _manifest_with(
            obsolete_exact_files=[
                {
                    "path": target_rel,
                    "surface": "nested-legacy-shortcut",
                    "identities": [
                        {
                            "path": target_rel,
                            "kind": "symlink",
                            "target": "legacy-target",
                            "source": {"kind": "test-fixture", "ref": "issue-370-test"},
                        }
                    ],
                    "on_unknown": "preserve-and-block",
                }
            ]
        )
    manifest_path = _write_manifest(tmp_path / "manifest", manifest)
    outside = target_root / "outside-sentinel.txt"
    outside.write_bytes(b"outside\n")
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    displaced = (
        target_root / ".github" / "workflows-displaced"
        if rebind_kind == "parent"
        else target_root / ".github-displaced"
    )
    displaced_target = displaced / target.name if rebind_kind == "parent" else displaced / "workflows" / target.name
    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_remove = managed_distribution._remove_distribution_target_if_bound
    original_unlink = managed_distribution.os.unlink
    original_checkpoint = OperationJournalStore.checkpoint_published
    rebound = False
    post_reservation_state: tuple[bytes, bytes] | None = None
    rebound_target_state: tuple[os.stat_result, bytes | Path] | None = None
    displaced_target_state: tuple[os.stat_result, bytes | Path] | None = None
    target_rename_calls = 0
    leaf_parent_fd: int | None = None
    leaf_unlink_calls = 0
    checkpoint_calls = 0

    def rebind_visible_parent(self, journal, lease):
        nonlocal rebound, post_reservation_state, rebound_target_state, displaced_target_state
        updated = original_record(self, journal, lease)
        if (
            not rebound
            and lease.path == target_rel
            and lease.role == "predecessor-quarantine"
            and lease.device == lease.inode == lease.ctime_ns == 0
        ):
            rebound = True
            rebound_path = target.parent if rebind_kind == "parent" else target_root / ".github"
            rebound_path.rename(displaced)
            displaced_target_state = (
                displaced_target.lstat(),
                displaced_target.read_bytes() if target_kind == "regular" else displaced_target.readlink(),
            )
            target.parent.mkdir(parents=True)
            if target_kind == "regular":
                target.write_bytes(b"managed\n")
            else:
                target.symlink_to("legacy-target")
            rebound_target_state = (
                target.lstat(),
                target.read_bytes() if target_kind == "regular" else target.readlink(),
            )
            post_reservation_state = (journal_path.read_bytes(), marker_path.read_bytes())
        return updated

    def count_rename(*args, **kwargs):
        nonlocal target_rename_calls
        if args[1] == target.name and args[3] != target.name:
            target_rename_calls += 1
        return original_rename(*args, **kwargs)

    def count_remove(*args, **kwargs):
        nonlocal leaf_parent_fd
        leaf_parent_fd = args[0]
        return original_remove(*args, **kwargs)

    def count_unlink(path, *args, **kwargs):
        nonlocal leaf_unlink_calls
        if kwargs.get("dir_fd") == leaf_parent_fd:
            leaf_unlink_calls += 1
        return original_unlink(path, *args, **kwargs)

    def count_checkpoint(self, journal, completed_paths):
        nonlocal checkpoint_calls
        checkpoint_calls += 1
        return original_checkpoint(self, journal, completed_paths)

    outside_before = outside.read_bytes()
    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", rebind_visible_parent)
    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", count_rename)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_target_if_bound", count_remove)
    monkeypatch.setattr(managed_distribution.os, "unlink", count_unlink)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", count_checkpoint)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert rebound is True
    assert post_reservation_state is not None
    assert rebound_target_state is not None
    assert displaced_target_state is not None
    assert result.status == "recovery_required"
    assert result.reason == "deprovision-recovery-required"
    assert target_rename_calls == 0, target_rename_calls
    assert target.lstat() == rebound_target_state[0]
    assert (target.read_bytes() if target_kind == "regular" else target.readlink()) == rebound_target_state[1]
    assert displaced_target.lstat() == displaced_target_state[0]
    assert (displaced_target.read_bytes() if target_kind == "regular" else displaced_target.readlink()) == (
        displaced_target_state[1]
    )
    assert outside.read_bytes() == outside_before
    assert displaced.is_dir()
    assert journal_path.read_bytes() == post_reservation_state[0]
    assert marker_path.read_bytes() == post_reservation_state[1]
    assert leaf_unlink_calls == 0
    assert checkpoint_calls == 0


def test_i370_deprovision_guard_only_resumes_from_semantic_equal_physical_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-SRC-001: compatible newer recovery ignores physical install roots."""

    install_a = _minimal_install_root(tmp_path / "provider-a", b"managed\n")
    scaffold_a = _minimal_scaffold_root(tmp_path / "provider-a")
    install_b = _minimal_install_root(tmp_path / "provider-b", b"managed\n")
    scaffold_b = _minimal_scaffold_root(tmp_path / "provider-b")
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_prepare = OperationJournalStore.prepare

    def interrupt_after_guard(*_args, **_kwargs):
        raise DistributionApplyError("injected guard-only interruption")

    monkeypatch.setattr(OperationJournalStore, "prepare", interrupt_after_guard)
    first = managed_distribution.execute_deprovision_distribution(
        install_a,
        manifest_path=manifest_path,
        scaffold_root=scaffold_a,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)

    assert first.status == "recovery_required"
    assert first.phase == "marker-write"
    assert first.last_completed_phase == "marker-written"
    assert first.pending_paths
    assert len(first.pending_paths) == len(set(first.pending_paths))
    assert set(first.pending_paths).issubset(first.failed_paths)
    assert "spec-dock/.distribution-journal.json" in first.failed_paths
    assert (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()
    retry = managed_distribution.execute_deprovision_distribution(
        install_b,
        manifest_path=manifest_path,
        scaffold_root=scaffold_b,
        target_root=target_root,
        package_version="2.0.0",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == "completed"
    assert retry.last_completed_phase == "marker-finalized"
    assert not (target_root / ".github").exists()


def test_i370_deprovision_guard_only_semantic_drift_is_write_free_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-SRC-001: semantic drift cannot acquire the stored deprovision plan."""

    install_a = _minimal_install_root(tmp_path / "provider-a", b"managed\n")
    scaffold_a = _minimal_scaffold_root(tmp_path / "provider-a")
    install_b = _minimal_install_root(tmp_path / "provider-b", b"drifted\n")
    scaffold_b = _minimal_scaffold_root(tmp_path / "provider-b")
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_prepare = OperationJournalStore.prepare

    def interrupt_after_guard(*_args, **_kwargs):
        raise DistributionApplyError("injected guard-only interruption")

    monkeypatch.setattr(OperationJournalStore, "prepare", interrupt_after_guard)
    first = managed_distribution.execute_deprovision_distribution(
        install_a,
        manifest_path=manifest_path,
        scaffold_root=scaffold_a,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)
    assert first.status == "recovery_required"
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    guard_before = guard_path.read_bytes()
    guard_stat = guard_path.stat()
    target_stat = managed.stat()

    mismatch = managed_distribution.execute_deprovision_distribution(
        install_b,
        manifest_path=manifest_path,
        scaffold_root=scaffold_b,
        target_root=target_root,
        package_version="2.0.0",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert mismatch.status == "recovery_required"
    assert mismatch.reason == "deprovision-recovery-mismatch"
    assert guard_path.read_bytes() == guard_before
    assert guard_path.stat().st_ino == guard_stat.st_ino
    assert managed.stat().st_ino == target_stat.st_ino
    assert managed.read_bytes() == b"managed\n"
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize(
    ("provider_b_content", "expected_status"),
    [
        (b"managed\n", "completed"),
        (b"drifted\n", "recovery_required"),
    ],
)
def test_i370_deprovision_prepared_journal_admits_only_semantic_equal_newer_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    provider_b_content: bytes,
    expected_status: str,
) -> None:
    """I370-T-SRC-001/I370-T-REC-001: journal resume uses semantic source equality."""

    install_a = _minimal_install_root(tmp_path / "provider-a", b"managed\n")
    scaffold_a = _minimal_scaffold_root(tmp_path / "provider-a")
    install_b = _minimal_install_root(tmp_path / "provider-b", provider_b_content)
    scaffold_b = _minimal_scaffold_root(tmp_path / "provider-b")
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    original_mark_executing = OperationJournalStore.mark_executing

    def interrupt_after_prepared(_self, _journal):
        raise DistributionApplyError("injected prepared-journal interruption")

    monkeypatch.setattr(
        OperationJournalStore,
        "mark_executing",
        interrupt_after_prepared,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_a,
        manifest_path=manifest_path,
        scaffold_root=scaffold_a,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "mark_executing",
        original_mark_executing,
    )

    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert first.phase == "uninstall-apply"
    assert json.loads(journal_path.read_text(encoding="utf-8"))["status"] == "prepared"
    guard_before = (guard_path.read_bytes(), guard_path.stat().st_ino)
    journal_before = (journal_path.read_bytes(), journal_path.stat().st_ino)
    managed_before = (managed.read_bytes(), managed.stat().st_ino)

    retry = managed_distribution.execute_deprovision_distribution(
        install_b,
        manifest_path=manifest_path,
        scaffold_root=scaffold_b,
        target_root=target_root,
        package_version="2.0.0",
        apply=True,
        expected_root_identity=root_identity,
    )

    assert retry.status == expected_status
    if expected_status == "completed":
        assert not (target_root / ".github").exists()
        assert not guard_path.exists()
        assert not journal_path.exists()
    else:
        assert retry.reason == "deprovision-recovery-mismatch"
        assert (guard_path.read_bytes(), guard_path.stat().st_ino) == guard_before
        assert (journal_path.read_bytes(), journal_path.stat().st_ino) == journal_before
        assert (managed.read_bytes(), managed.stat().st_ino) == managed_before


def test_i370_deprovision_same_invocation_source_replacement_stops_before_target_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I370-T-SRC-001: physical source replacement is an invocation-local guard."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    target_before = managed.stat()
    source = install_root / ".github" / "workflows" / "ci.yml"
    source_before = source.stat()
    displaced_source = source.with_suffix(".yml.displaced")
    original_mark_executing = OperationJournalStore.mark_executing
    replaced = False

    def replace_source_after_journal(self, journal):
        nonlocal replaced
        executing = original_mark_executing(self, journal)
        source.rename(displaced_source)
        source.write_bytes(b"managed\n")
        replaced = True
        return executing

    monkeypatch.setattr(
        OperationJournalStore,
        "mark_executing",
        replace_source_after_journal,
    )
    first = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    monkeypatch.setattr(
        OperationJournalStore,
        "mark_executing",
        original_mark_executing,
    )

    assert replaced is True
    assert source.stat().st_ino != source_before.st_ino
    assert first.status == "recovery_required"
    assert first.phase == "uninstall-apply"
    assert managed.stat().st_ino == target_before.st_ino
    assert managed.read_bytes() == b"managed\n"
    displaced_source.unlink()
    retry = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=True,
        expected_root_identity=root_identity,
    )
    assert retry.status == "completed"


def test_i370_legacy_marker_only_and_copied_bytes_remain_unconvertible_and_unchanged(
    tmp_path: Path,
) -> None:
    """I370-T-LEG-001/I370-T-AUTH-001: legacy bytes prove no root, mode, or plan."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    marker_bytes = b'{"managed_by": "spec-dock", "purpose": "uninstall-rerun", "schema_version": 1}\n'
    roots: list[Path] = []
    for name in ("original", "copied"):
        target_root = tmp_path / name
        workspace = target_root / "spec-dock"
        workspace.mkdir(parents=True)
        (workspace / ".uninstall-retry.json").write_bytes(marker_bytes)
        (target_root / "outside-sentinel.txt").write_bytes(b"outside\n")
        roots.append(target_root)

    assert (
        roots[0].joinpath("spec-dock/.uninstall-retry.json").stat().st_ino
        != roots[1].joinpath("spec-dock/.uninstall-retry.json").stat().st_ino
    )
    for target_root in roots:
        before = _i370_tree_evidence(target_root)
        root_info = target_root.stat()
        root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
        for apply in (False, True):
            result = managed_distribution.execute_deprovision_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                package_version="1.2.3",
                apply=apply,
                expected_root_identity=root_identity if apply else None,
            )

            assert result.status == "recovery_required"
            assert result.reason == "legacy-marker-unconvertible"
            assert result.phase == "preflight"
            assert result.last_completed_phase == "not-started"
            assert result.failed_paths == ("spec-dock/.uninstall-retry.json",)
            assert result.pending_paths == ()
            assert tuple(error.code for error in result.errors) == ("legacy-marker-unconvertible",)
            assert result.retry_policy == "manual-recovery"
            assert _i370_tree_evidence(target_root) == before


@pytest.mark.parametrize("apply", (False, True), ids=("dry-run", "apply"))
@pytest.mark.parametrize("marker_kind", ("malformed", "symlink", "hardlink", "fifo"))
def test_i370_legacy_marker_invalid_evidence_fails_closed_before_write(
    tmp_path: Path,
    marker_kind: str,
    apply: bool,
) -> None:
    """I370-T-LEG-001/I370-T-ID-001: hardlink and special evidence stays immutable."""

    install_root = _minimal_install_root(tmp_path)
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    marker = workspace / ".uninstall-retry.json"
    external = tmp_path / "external-marker-evidence"
    if marker_kind == "malformed":
        marker.write_bytes(b'{"schema_version":')
    elif marker_kind == "symlink":
        external.write_bytes(b"outside\n")
        marker.symlink_to(external)
    elif marker_kind == "hardlink":
        peer = workspace / "legacy-marker-peer.json"
        peer.write_bytes(b'{"managed_by": "spec-dock", "purpose": "uninstall-rerun", "schema_version": 1}\n')
        os.link(peer, marker)
    else:
        os.mkfifo(marker, 0o600)
    (target_root / "outside-sentinel.txt").write_bytes(b"outside\n")
    before = _i370_tree_evidence(target_root)
    external_before = (
        (external.lstat().st_dev, external.lstat().st_ino, external.lstat().st_ctime_ns, external.read_bytes())
        if external.exists()
        else None
    )
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)

    result = managed_distribution.execute_deprovision_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        apply=apply,
        expected_root_identity=root_identity if apply else None,
    )

    assert result.status == "error"
    assert result.reason == "legacy-marker-invalid"
    assert result.phase == "preflight"
    assert result.last_completed_phase == "not-started"
    assert result.failed_paths == ("spec-dock/.uninstall-retry.json",)
    assert result.pending_paths == ()
    assert tuple(error.code for error in result.errors) == ("legacy-marker-invalid",)
    assert result.retry_policy == "manual-recovery"
    assert _i370_tree_evidence(target_root) == before
    if external_before is not None:
        assert (
            external.lstat().st_dev,
            external.lstat().st_ino,
            external.lstat().st_ctime_ns,
            external.read_bytes(),
        ) == external_before


def test_i370_legacy_marker_with_schema2_deprovision_state_is_immutable_dual_recovery(
    tmp_path: Path,
) -> None:
    """I370-T-LEG-001/I370-T-AUTH-001: legacy and schema-2 authority never merge."""

    install_root = _minimal_install_root(tmp_path, b"managed\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    target_root = tmp_path / "consumer"
    managed = target_root / ".github" / "workflows" / "ci.yml"
    managed.parent.mkdir(parents=True)
    managed.write_bytes(b"managed\n")
    (target_root / "spec-dock" / "initiatives").mkdir(parents=True)
    root_info = target_root.stat()
    root_identity = DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino)
    assessment = managed_distribution.build_deprovision_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        expected_root_identity=root_identity,
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    assert json.loads(guard_path.read_text(encoding="utf-8"))["schema_version"] == 2
    assert journal.protocol_version == 2
    assert journal.intent == "deprovision"
    legacy_path = target_root / "spec-dock" / ".uninstall-retry.json"
    legacy_path.write_bytes(b'{"managed_by": "spec-dock", "purpose": "uninstall-rerun", "schema_version": 1}\n')
    before = _i370_tree_evidence(target_root)
    expected_failed = tuple(
        sorted(
            (
                "spec-dock/.distribution-journal.json",
                "spec-dock/.distribution-retry.json",
                "spec-dock/.uninstall-retry.json",
            ),
            key=os.fsencode,
        )
    )

    for apply in (False, True):
        result = managed_distribution.execute_deprovision_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            package_version="1.2.3",
            apply=apply,
            expected_root_identity=root_identity if apply else None,
        )

        assert result.status == "recovery_required"
        assert result.reason == "dual-recovery-state"
        assert result.phase == "preflight"
        assert result.last_completed_phase == "not-started"
        assert result.failed_paths == expected_failed
        assert result.pending_paths == ()
        assert tuple(error.code for error in result.errors) == ("dual-recovery-state",)
        assert result.retry_policy == "manual-recovery"
        assert _i370_tree_evidence(target_root) == before


def test_i369_standalone_directory_binding_recovers_after_mkdir_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_record = OperationJournalStore.record_created_parent_bindings
    failed = False

    def fail_after_mkdir(self, journal, bindings):
        nonlocal failed
        if not failed and any(item.relative_path == "spec-dock/.agent" and item.exists for item in bindings):
            failed = True
            raise DistributionApplyError("injected standalone binding publish failure")
        return original_record(self, journal, bindings)

    monkeypatch.setattr(OperationJournalStore, "record_created_parent_bindings", fail_after_mkdir)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    bindings = {item["relative_path"]: item for item in payload["created_parent_bindings"]}
    assert bindings["spec-dock/.agent"]["exists"] is False
    assert (target_root / "spec-dock/.agent").is_dir()

    monkeypatch.setattr(OperationJournalStore, "record_created_parent_bindings", original_record)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()


def test_i369_standalone_directory_closed_set_rejects_unknown_child_after_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_directory_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec-dock/.agent" in completed_paths:
            failed = True
            raise DistributionApplyError("injected standalone checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_directory_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    assert journal_path.exists()
    (target_root / "spec-dock/.agent/foreign").write_text("user\n", encoding="utf-8")

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason == "journal-precondition-mismatch"
    assert journal_path.exists()


def test_i368_journal_resume_rejects_intent_mismatch_without_rewrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    update = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    init_force = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="init-force",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(update, package_version="1.2.3")
    before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-intent-mismatch"):
        store.resume(init_force, package_version="1.2.3")

    assert store.path.read_bytes() == before


def test_i368_journal_resume_rejects_cross_root_replay_without_rewrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    (first_root / "spec-dock").mkdir(parents=True)
    (second_root / "spec-dock").mkdir(parents=True)
    first = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=first_root,
            intent="update",
        )
    )
    first_store = OperationJournalStore(first_root)
    first_store.prepare(first, package_version="1.2.3")
    replay = second_root / "spec-dock" / ".distribution-journal.json"
    replay.write_bytes(first_store.path.read_bytes())
    second = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=second_root,
            intent="update",
        )
    )
    before = replay.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-root-mismatch"):
        OperationJournalStore(second_root).resume(second, package_version="1.2.3")

    assert replay.read_bytes() == before


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("authority", "different-authority", "journal-authority-mismatch"),
        ("protocol_version", 999, "journal-protocol-incompatible"),
        ("plan_digest", "0" * 64, "journal-plan-mismatch"),
    ],
)
def test_i368_journal_resume_rejects_binding_mismatch_without_rewrite(
    tmp_path: Path,
    field: str,
    value: object,
    reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(executable, package_version="1.2.3")
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    payload[field] = value
    store.path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match=reason):
        store.resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == before


def test_i368_journal_resume_rejects_recomputed_digest_for_changed_action(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    changed = list(journal.actions)
    changed[0] = managed_distribution.replace(changed[0], action="prune")
    tampered = managed_distribution.replace(journal, actions=tuple(changed))
    tampered = managed_distribution.replace(
        tampered,
        plan_digest=managed_distribution._journal_digest(tampered),
    )
    store.write(tampered)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"


def test_i368_journal_resume_rejects_recomputed_digest_with_incomplete_parent_chain(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    changed = list(journal.actions)
    parents = changed[0].precondition["parents"]
    assert isinstance(parents, list) and parents
    changed[0] = managed_distribution.replace(
        changed[0],
        precondition={**changed[0].precondition, "parents": parents[1:]},
    )
    tampered = managed_distribution.replace(journal, actions=tuple(changed))
    tampered = managed_distribution.replace(
        tampered,
        plan_digest=managed_distribution._journal_digest(tampered),
    )
    store.write(tampered)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"


@pytest.mark.parametrize(
    "missing_fields",
    (("device",), ("inode",), ("ctime_ns",), ("device", "inode", "ctime_ns")),
)
def test_i368_journal_resume_rejects_recomputed_digest_with_incomplete_target_identity(
    tmp_path: Path,
    missing_fields: tuple[str, ...],
) -> None:
    content = b"current\n"
    install_root = _minimal_install_root(tmp_path, content)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(content)
    (target_root / "spec-dock").mkdir()
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    original: Path | None = None
    if len(missing_fields) > 1:
        original = target.with_name("ci-original.yml")
        target.rename(original)
        target.write_bytes(content)
        target.chmod(stat.S_IMODE(original.stat().st_mode))
    changed = list(journal.actions)
    action_index = next(index for index, action in enumerate(changed) if action.path == ".github/workflows/ci.yml")
    precondition = dict(changed[action_index].precondition)
    for missing_field in missing_fields:
        del precondition[missing_field]
    changed[action_index] = managed_distribution.replace(changed[action_index], precondition=precondition)
    tampered = managed_distribution.replace(journal, actions=tuple(changed))
    tampered = managed_distribution.replace(
        tampered,
        plan_digest=managed_distribution._journal_digest(tampered),
    )
    store.write(tampered)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"
    assert target.read_bytes() == content
    if original is not None:
        assert original.read_bytes() == content


def test_i368_journal_resume_rejects_recomputed_digest_with_incomplete_post_parent_chain(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    changed = list(journal.actions)
    parents = changed[0].postcondition["parents"]
    assert isinstance(parents, list) and parents
    changed[0] = managed_distribution.replace(
        changed[0],
        postcondition={**changed[0].postcondition, "parents": parents[1:]},
    )
    tampered = managed_distribution.replace(journal, actions=tuple(changed))
    tampered = managed_distribution.replace(
        tampered,
        plan_digest=managed_distribution._journal_digest(tampered),
    )
    store.write(tampered)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"


def test_i368_journal_resume_rejects_existing_parent_rebind(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    (target_root / "spec-dock").mkdir()
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    _prepare_guarded_journal(OperationJournalStore(target_root), build_executable_mutation_plan(assessment))
    parent.rename(target_root / ".github" / "workflows-old")
    parent.mkdir()
    sentinel = parent / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (parent / "ci.yml").exists()


def test_i368_journal_resume_rejects_unbound_parent_authorized_before_creation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    _prepare_guarded_journal(OperationJournalStore(target_root), build_executable_mutation_plan(assessment))
    appeared = target_root / ".github" / "workflows"
    appeared.mkdir(parents=True)
    sentinel = appeared / "sentinel.txt"
    sentinel.write_text("user-owned\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert sentinel.read_text(encoding="utf-8") == "user-owned\n"
    assert not (appeared / "ci.yml").exists()


def test_i368_journal_resume_rejects_forged_nonempty_created_parent_binding(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    appeared = target_root / ".github" / "workflows"
    appeared.mkdir(parents=True)
    sentinel = appeared / "sentinel.txt"
    sentinel.write_text("user-owned\n", encoding="utf-8")
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    forged_bindings = []
    for binding in payload["created_parent_bindings"]:
        path = target_root / binding["relative_path"]
        if path.exists():
            info = path.lstat()
            binding = {
                "relative_path": binding["relative_path"],
                "exists": True,
                "device": info.st_dev,
                "inode": info.st_ino,
                "ctime_ns": info.st_ctime_ns,
                "file_type": "directory",
                "link_count": info.st_nlink,
            }
        forged_bindings.append(binding)
    payload["created_parent_bindings"] = forged_bindings
    payload["created_parent_bindings_digest"] = managed_distribution._created_parent_bindings_digest(
        operation_id=payload["operation_id"],
        bindings=forged_bindings,
    )
    store.path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert sentinel.read_text(encoding="utf-8") == "user-owned\n"
    assert not (appeared / "ci.yml").exists()


@pytest.mark.parametrize("kind", ["regular", "symlink", "fifo", "unleased-stage"])
def test_i368_created_parent_held_descriptor_rejects_unknown_child_before_target_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_assert = managed_distribution._assert_created_parent_binding_fd_closed_set
    injected = False

    def validate_then_inject_unknown_child(parent_fd, relative_path, binding, journal):
        nonlocal injected
        original_assert(parent_fd, relative_path, binding, journal)
        if injected or relative_path != ".github/workflows":
            return
        injected = True
        parent = target_root / ".github" / "workflows"
        name = ".spec-dock-file-unleased" if kind == "unleased-stage" else f"unknown-{kind}"
        unknown = parent / name
        if kind in {"regular", "unleased-stage"}:
            unknown.write_bytes(b"third-party\n")
        elif kind == "symlink":
            unknown.symlink_to("third-party-target")
        else:
            os.mkfifo(unknown)

    monkeypatch.setattr(
        managed_distribution,
        "_assert_created_parent_binding_fd_closed_set",
        validate_then_inject_unknown_child,
    )

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert injected is True
    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()


def test_i368_preserved_validator_repeats_until_first_operation_owned_parent_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    created_parent = target_root / ".github"
    observations: list[bool] = []

    def validate_preserved_state() -> None:
        appeared = created_parent.exists()
        observations.append(appeared)
        if appeared:
            raise DistributionApplyError("preserved validator ran after first target mutation")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        preserved_state_validator=validate_preserved_state,
    )

    assert result.status == "completed", result.reason
    assert len(observations) >= 3
    assert not any(observations)
    assert created_parent.is_dir()


def test_i368_preserved_validator_deactivates_only_after_existing_parent_stage_create(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    observations: list[bool] = []

    def validate_preserved_state() -> None:
        observations.append(target.exists())
        if target.exists():
            raise DistributionApplyError("preserved validator ran after target publication")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        preserved_state_validator=validate_preserved_state,
    )

    assert result.status == "completed", result.reason
    assert target.exists()
    assert len(observations) > 1
    assert not any(observations)


def test_i368_parent_creation_crash_resumes_from_durable_parent_intent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_bind = managed_distribution._bind_created_parent_identities

    class SimulatedProcessCrash(BaseException):
        pass

    def crash_before_parent_binding(*_args, **_kwargs) -> None:
        raise SimulatedProcessCrash

    monkeypatch.setattr(managed_distribution, "_bind_created_parent_identities", crash_before_parent_binding)
    with pytest.raises(SimulatedProcessCrash):
        execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
            package_version="1.2.3",
        )

    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["created_parent_bindings"]
    bindings = {binding["relative_path"]: binding for binding in payload["created_parent_bindings"]}
    assert bindings[".github"]["exists"] is True
    assert bindings[".github/workflows"]["exists"] is True
    assert (target_root / ".github" / "workflows").is_dir()

    monkeypatch.setattr(managed_distribution, "_bind_created_parent_identities", original_bind)
    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert retry.status == "completed", retry.reason
    assert not journal_path.exists()


def test_i368_journal_publish_retry_uses_a_fresh_stage_after_crash(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_rename = managed_distribution._rename_distribution_swap
    crashed_stage: str | None = None

    class SimulatedProcessCrash(BaseException):
        pass

    def crash_before_journal_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal crashed_stage
        crashed_stage = source_name
        raise SimulatedProcessCrash

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", crash_before_journal_swap)
    with pytest.raises(SimulatedProcessCrash):
        execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
            package_version="1.2.3",
        )

    assert crashed_stage is not None
    assert (target_root / "spec-dock" / crashed_stage).is_file()
    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", original_rename)

    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert retry.status == "completed", retry.reason
    assert (target_root / "spec-dock" / crashed_stage).is_file()


def test_i368_journal_guard_is_rejected_by_the_legacy_marker_contract(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="update",
    )
    marker = OperationJournalStore(target_root).prepare_legacy_guard(
        build_executable_mutation_plan(assessment),
        package_version="1.2.3",
    )
    payload = json.loads((target_root / "spec-dock" / ".distribution-retry.json").read_text(encoding="utf-8"))

    assert marker.purpose == "recognized-journal-forward-only"
    assert (payload["schema_version"], payload["purpose"]) == (
        managed_distribution._DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION,
        managed_distribution._DISTRIBUTION_JOURNAL_GUARD_PURPOSE,
    )
    assert (payload["schema_version"], payload["purpose"]) != (
        managed_distribution._DISTRIBUTION_RETRY_SCHEMA_VERSION,
        managed_distribution._DISTRIBUTION_RETRY_PURPOSE,
    )
    assert managed_distribution._read_distribution_retry_marker(target_root) == marker


def test_i368_schema_2_guard_without_initial_journal_timestamp_remains_readable(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        intent="update",
    )
    marker = OperationJournalStore(target_root).prepare_legacy_guard(
        build_executable_mutation_plan(assessment),
        package_version="1.2.3",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    payload = json.loads(marker_path.read_text(encoding="utf-8"))
    payload.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    admitted = managed_distribution._read_distribution_retry_marker(target_root)

    assert admitted is not None
    assert admitted.journal_digest == marker.journal_digest
    assert admitted.journal_predecessor_digest == marker.journal_predecessor_digest
    assert admitted.journal_created_at_ns is None


@pytest.mark.parametrize("guard_state", ("absent", "schema-1", "replaced"))
def test_i368_journal_resume_requires_exact_schema_2_forward_guard(
    tmp_path: Path,
    guard_state: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    _prepare_guarded_journal(store, build_executable_mutation_plan(assessment))
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    admitted_guard = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted_guard is not None
    journal_before = store.path.read_bytes()
    marker_bytes = marker_path.read_bytes()
    if guard_state == "absent":
        marker_path.unlink()
    elif guard_state == "schema-1":
        root_info = target_root.stat()
        marker_path.write_text(
            json.dumps({
                "schema_version": 1,
                "operation": "update",
                "package_version": "1.2.3",
                "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
                "last_completed_phase": "preflight-complete",
                "purpose": "distribution-rerun",
                "stage_ownership": [],
            }),
            encoding="utf-8",
        )
    else:
        marker_path.unlink()
        marker_path.write_bytes(marker_bytes)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=admitted_guard,
    )

    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert store.path.read_bytes() == journal_before
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()


def test_i368_journal_publish_preserves_ambiguous_pair_after_stage_replacement(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")
    before = store.path.read_bytes()
    original_swap = managed_distribution._rename_distribution_swap
    replacement = b"concurrent replacement\n"
    replaced_stage: Path | None = None

    def replace_before_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal replaced_stage
        if replaced_stage is None and source_name.startswith(".distribution-journal-"):
            replaced_stage = target_root / "spec-dock" / source_name
            replaced_stage.unlink()
            replaced_stage.write_bytes(replacement)
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", replace_before_swap)

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        store.mark_executing(prepared)

    assert replaced_stage is not None
    assert store.path.read_bytes() == replacement
    assert replaced_stage.read_bytes() == before


def test_i368_journal_publish_restores_raced_canonical_predecessor(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")
    original_swap = managed_distribution._rename_distribution_swap
    replacement = b"raced canonical journal\n"
    replaced = False

    def replace_canonical_before_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal replaced
        if not replaced and destination_name == store.path.name:
            replaced = True
            store.path.unlink()
            store.path.write_bytes(replacement)
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", replace_canonical_before_swap)

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        store.mark_executing(prepared)

    assert replaced is True
    assert store.path.read_bytes() == replacement


def test_i368_journal_transition_rejects_same_bytes_predecessor_replacement(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")
    same_bytes = store.path.read_bytes()
    store.path.unlink()
    store.path.write_bytes(same_bytes)

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        store.mark_executing(prepared)

    assert store.path.read_bytes() == same_bytes


def test_i368_forward_guard_publish_restores_raced_legacy_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    original_swap = managed_distribution._rename_distribution_swap
    replacement = marker_path.read_bytes()
    replaced = False

    def replace_marker_before_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal replaced
        if not replaced and destination_name == marker_path.name:
            replaced = True
            marker_path.unlink()
            marker_path.write_bytes(replacement)
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", replace_marker_before_swap)

    with pytest.raises(DistributionApplyError, match="legacy-marker-unconvertible"):
        OperationJournalStore(target_root).prepare_legacy_guard(
            executable,
            package_version="1.3.0",
            replace_marker=admitted,
        )

    assert replaced is True
    assert marker_path.read_bytes() == replacement


def test_i368_journal_resume_allows_newer_package_for_same_plan(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")

    resumed = store.resume(executable, package_version="1.3.0")

    assert resumed == prepared


def test_i368_journal_resume_rejects_older_package(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(executable, package_version="1.2.3")

    with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
        store.resume(executable, package_version="1.2.2")


def test_i368_newer_package_finishes_original_journal_then_refreshes_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_mark_completed = OperationJournalStore.mark_completed

    def interrupt_before_completed(*_args, **_kwargs):
        raise DistributionApplyError("injected terminal interruption")

    monkeypatch.setattr(OperationJournalStore, "mark_completed", interrupt_before_completed)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert json.loads(journal_path.read_text(encoding="utf-8"))["package_version"] == "1.2.3"

    monkeypatch.setattr(OperationJournalStore, "mark_completed", original_mark_completed)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
    )

    assert second.status == "completed", second.reason
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.3.0\n"
    assert not journal_path.exists()
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()


def test_i369_fresh_completed_journal_does_not_reenter_for_newer_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_mark_completed = OperationJournalStore.mark_completed

    def interrupt_before_completed(*_args, **_kwargs):
        raise DistributionApplyError("injected terminal interruption")

    monkeypatch.setattr(OperationJournalStore, "mark_completed", interrupt_before_completed)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert json.loads(journal_path.read_text(encoding="utf-8"))["package_version"] == "1.2.3"

    monkeypatch.setattr(OperationJournalStore, "mark_completed", original_mark_completed)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.3.0",
    )

    assert second.status == "completed", second.reason
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"
    assert not journal_path.exists()


def test_i369_fresh_executing_journal_does_not_reenter_for_newer_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_mark_verified = OperationJournalStore.mark_verified

    def interrupt_before_verified(*_args, **_kwargs):
        raise DistributionApplyError("injected verification interruption")

    monkeypatch.setattr(OperationJournalStore, "mark_verified", interrupt_before_verified)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert journal["status"] == "executing"
    assert journal["package_version"] == "1.2.3"

    monkeypatch.setattr(OperationJournalStore, "mark_verified", original_mark_verified)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.3.0",
    )

    assert second.status == "completed", second.reason
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"
    assert not journal_path.exists()


def test_i369_fresh_journal_retry_rejects_new_workspace_root_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_mark_completed = OperationJournalStore.mark_completed

    def interrupt_before_completed(*_args, **_kwargs):
        raise DistributionApplyError("injected terminal interruption")

    monkeypatch.setattr(OperationJournalStore, "mark_completed", interrupt_before_completed)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert journal_path.exists()
    (target_root / "spec-dock" / "foreign").write_text("user\n", encoding="utf-8")

    monkeypatch.setattr(OperationJournalStore, "mark_completed", original_mark_completed)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason == "journal-parent-mismatch"
    assert journal_path.exists()


def test_i368_journal_rejects_rebound_workspace_parent(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    journal = store.prepare(executable, package_version="1.2.3")
    journal_bytes = store.path.read_bytes()
    workspace.rename(target_root / "spec-dock-displaced")
    workspace.mkdir()
    store.path.write_bytes(journal_bytes)

    with pytest.raises(DistributionApplyError, match="journal-parent-mismatch"):
        store.write(journal)

    assert store.path.read_bytes() == journal_bytes


def test_i368_completed_journal_rejects_pending_actions(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(executable, package_version="1.2.3")
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    payload["status"] = "completed"

    with pytest.raises(DistributionApplyError, match="journal-protocol-incompatible"):
        managed_distribution._parse_operation_journal(
            (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
        )


def test_i368_journal_rejects_unbound_staging_lease_without_deleting_stage(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    (target_root / "spec-dock").mkdir()
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    store.prepare(executable, package_version="1.2.3")
    action = next(item for item in executable.actions if item.path == ".github/workflows/ci.yml")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    stage_name = managed_distribution._distribution_stage_name(action.path, expected)
    stage = parent / stage_name
    stage.write_bytes(b"desired\n")
    stage_info = stage.stat(follow_symlinks=False)
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    payload["staging_leases"].append({
        "path": action.path,
        "stage_name": stage_name,
        "device": stage_info.st_dev,
        "inode": stage_info.st_ino,
        "ctime_ns": stage_info.st_ctime_ns,
        "file_type": "regular",
    })
    store.path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-protocol-incompatible"
    assert stage.read_bytes() == b"desired\n"


def test_i368_recognized_service_executes_and_finalizes_journal(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"desired\n"
    assert (target_root / "spec-dock" / ".gitignore").read_text(encoding="utf-8") == ".agent/\n"
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_legacy_guard_remains_visible_for_the_entire_journal_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_apply = managed_distribution._apply_distribution_action
    observed = False

    def assert_recovery_authorities(*args, **kwargs):
        nonlocal observed
        observed = True
        assert (target_root / "spec-dock" / ".distribution-retry.json").is_file()
        assert (target_root / "spec-dock" / ".distribution-journal.json").is_file()
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", assert_recovery_authorities)
    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert observed
    assert not (target_root / "spec-dock" / ".distribution-retry.json").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_recognized_noop_does_not_prepare_a_journal(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "completed", first.reason
    prepared = False
    original_prepare = OperationJournalStore.prepare

    def record_prepare(*args, **kwargs):
        nonlocal prepared
        prepared = True
        return original_prepare(*args, **kwargs)

    monkeypatch.setattr(OperationJournalStore, "prepare", record_prepare)

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not prepared
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_recognized_service_upgrades_a_recognized_workspace_version(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            recognized_workspace_versions=[
                {"version": "1.1.0", "anchors": [_regular_record("legacy-anchor", b"legacy\n")]}
            ]
        ),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    specdock_dir = target_root / "spec-dock"
    specdock_dir.mkdir(parents=True)
    (specdock_dir / "spec-dock.version").write_text("1.1.0\n", encoding="utf-8")

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert (specdock_dir / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"


def test_i368_generated_state_asset_failure_retains_journal_and_resumes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    content = b"generated context\n"
    generated_asset = DistributionAsset(
        path="spec-dock/active/context-pack.md",
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=0o644,
        ),
        generated_content=content,
    )
    original_apply = managed_distribution._apply_distribution_action

    def fail_generated_action(*args, **kwargs):
        action = kwargs["action"]
        if action.path == generated_asset.path:
            raise DistributionApplyError("injected generated-state failure")
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_generated_action)

    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        generated_assets=(generated_asset,),
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert journal_path.is_file()
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert generated_asset.path in {action["path"] for action in journal["actions"]}

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        generated_assets=(generated_asset,),
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()
    assert (target_root / generated_asset.path).read_bytes() == content


@pytest.mark.parametrize(
    ("phase", "expected_status"),
    [("preflight-complete", "completed"), ("managed-scaffold-refreshed", "recovery_required")],
)
def test_i368_legacy_marker_conversion_is_limited_to_prewrite_state(
    tmp_path: Path,
    phase: str,
    expected_status: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase=phase,
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    before = marker_path.read_bytes()

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=marker,
    )

    assert result.status == expected_status
    if expected_status == "completed":
        assert not marker_path.exists()
    else:
        assert marker_path.read_bytes() == before
        assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_newer_package_converts_prewrite_legacy_marker_and_refreshes_version(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase="preflight-complete",
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
        legacy_marker=marker,
    )

    assert result.status == "completed", result.reason
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.3.0\n"
    assert not marker_path.exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_legacy_guard_removal_failure_retains_completed_targets_for_retry(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase="preflight-complete",
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    original_remove = OperationJournalStore.remove_legacy_marker

    def fail_marker_removal(*_args, **_kwargs) -> None:
        raise DistributionApplyError("legacy-marker-unconvertible")

    monkeypatch.setattr(OperationJournalStore, "remove_legacy_marker", fail_marker_removal)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=marker,
    )

    assert first.status == "recovery_required"
    assert first.reason == "legacy-marker-unconvertible"
    guard = json.loads(marker_path.read_text(encoding="utf-8"))
    assert guard["schema_version"] == 2
    assert guard["purpose"] == "recognized-journal-forward-only"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert json.loads(journal_path.read_text(encoding="utf-8"))["status"] == "completed"
    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"desired\n"

    monkeypatch.setattr(OperationJournalStore, "remove_legacy_marker", original_remove)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not marker_path.exists()
    assert not journal_path.exists()


def test_i368_terminal_journal_without_guard_finishes_cleanup_without_reapplying(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    original_remove = OperationJournalStore.remove_completed

    def fail_journal_removal(*_args, **_kwargs) -> None:
        raise DistributionApplyError("injected completed journal removal failure")

    monkeypatch.setattr(OperationJournalStore, "remove_completed", fail_journal_removal)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    assert not marker_path.exists()
    assert json.loads(journal_path.read_text(encoding="utf-8"))["status"] == "completed"
    installed = target_root / ".github" / "workflows" / "ci.yml"
    before = installed.stat()

    monkeypatch.setattr(OperationJournalStore, "remove_completed", original_remove)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    after = installed.stat()
    assert second.status == "completed", second.reason
    assert (after.st_dev, after.st_ino, after.st_ctime_ns) == (before.st_dev, before.st_ino, before.st_ctime_ns)
    assert not marker_path.exists()
    assert not journal_path.exists()


def test_i368_admission_allows_only_terminal_journal_without_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_remove = OperationJournalStore.remove_completed

    def fail_journal_removal(*_args, **_kwargs) -> None:
        raise DistributionApplyError("injected completed journal removal failure")

    monkeypatch.setattr(OperationJournalStore, "remove_completed", fail_journal_removal)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    admission = admit_distribution_operation(
        target_root,
        operation="update",
        package_version="1.2.3",
        manifest_path=manifest_path,
    )

    assert admission.status == "retry"
    assert admission.marker is None
    monkeypatch.setattr(OperationJournalStore, "remove_completed", original_remove)


def test_i368_admission_rejects_nonterminal_journal_without_guard(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    store.prepare(executable, package_version="1.2.3")
    (target_root / "spec-dock" / ".distribution-retry.json").unlink()

    with pytest.raises(DistributionAdmissionError, match="dual-marker"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )


def test_i368_legacy_conversion_rejects_marker_replaced_after_admission(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    replacement = marker_path.read_bytes()
    marker_path.unlink()
    marker_path.write_bytes(replacement)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
        legacy_marker=admitted,
    )

    assert result.status == "recovery_required"
    assert result.reason == "legacy-marker-unconvertible"
    assert marker_path.read_bytes() == replacement
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_legacy_conversion_rejects_marker_replaced_between_stat_and_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    replacement = marker_path.read_bytes()
    original_path = marker_path.with_name(".distribution-retry-original.json")
    original_open = managed_distribution.os.open
    replaced = False

    def replace_marker_before_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        if not replaced and path == marker_path.name and dir_fd is not None:
            marker_path.rename(original_path)
            marker_path.write_bytes(replacement)
            replaced = True
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(managed_distribution.os, "open", replace_marker_before_open)
    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
        legacy_marker=admitted,
    )

    assert replaced is True
    assert result.status == "recovery_required"
    assert result.reason == "legacy-marker-unconvertible"
    assert marker_path.read_bytes() == replacement
    assert original_path.read_bytes() == replacement
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()


def test_i368_legacy_conversion_failure_leaves_forward_only_guard_for_newer_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    original_prepare = OperationJournalStore.prepare

    def fail_journal_publish(*_args, **_kwargs):
        raise DistributionApplyError("injected journal publish failure")

    monkeypatch.setattr(OperationJournalStore, "prepare", fail_journal_publish)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
        legacy_marker=admitted,
    )

    assert first.status == "recovery_required"
    guard = json.loads(marker_path.read_text(encoding="utf-8"))
    assert guard["schema_version"] == 2
    assert guard["purpose"] == "recognized-journal-forward-only"
    assert guard["package_version"] == "1.3.0"
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()

    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
    )

    assert second.status == "completed", second.reason
    assert not marker_path.exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize("retry_version", ["1.3.0", "1.4.0"])
def test_i368_guard_only_retry_rejects_plan_drift_and_preserves_exact_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    retry_version: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    original_prepare = OperationJournalStore.prepare

    def fail_journal_publish(*_args, **_kwargs):
        raise DistributionApplyError("injected journal publish failure")

    monkeypatch.setattr(OperationJournalStore, "prepare", fail_journal_publish)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
    )
    assert first.status == "recovery_required"
    assert json.loads(marker_path.read_text(encoding="utf-8"))["purpose"] == "recognized-journal-forward-only"
    guard_before = marker_path.read_bytes()
    guard_stat_before = marker_path.stat()

    (install_root / ".github" / "workflows" / "ci.yml").write_bytes(b"different-plan\n")
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version=retry_version,
    )

    guard_stat_after = marker_path.stat()
    assert second.status == "recovery_required"
    assert second.reason == "forward-guard-plan-mismatch"
    assert marker_path.read_bytes() == guard_before
    assert (guard_stat_after.st_dev, guard_stat_after.st_ino, guard_stat_after.st_ctime_ns) == (
        guard_stat_before.st_dev,
        guard_stat_before.st_ino,
        guard_stat_before.st_ctime_ns,
    )
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_ambiguous_terminal_guard_only_state_is_preserved_without_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    original_prepare = OperationJournalStore.prepare

    def fail_journal_publish(*_args, **_kwargs):
        raise DistributionApplyError("injected journal publish failure")

    monkeypatch.setattr(OperationJournalStore, "prepare", fail_journal_publish)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
    )
    assert first.status == "recovery_required"
    guard_before = marker_path.read_bytes()
    guard_stat_before = marker_path.stat()

    installed = target_root / ".github" / "workflows" / "ci.yml"
    installed.parent.mkdir(parents=True)
    installed.write_bytes(b"desired\n")
    version_path = target_root / "spec-dock" / "spec-dock.version"
    version_path.write_text("1.3.0\n", encoding="utf-8")
    installed_before = installed.stat()
    version_before = version_path.stat()
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
    )

    guard_stat_after = marker_path.stat()
    installed_after = installed.stat()
    version_after = version_path.stat()
    assert second.status == "recovery_required"
    assert second.reason == "forward-guard-plan-mismatch"
    assert marker_path.read_bytes() == guard_before
    assert (guard_stat_after.st_dev, guard_stat_after.st_ino, guard_stat_after.st_ctime_ns) == (
        guard_stat_before.st_dev,
        guard_stat_before.st_ino,
        guard_stat_before.st_ctime_ns,
    )
    assert (installed_after.st_dev, installed_after.st_ino, installed_after.st_ctime_ns) == (
        installed_before.st_dev,
        installed_before.st_ino,
        installed_before.st_ctime_ns,
    )
    assert (version_after.st_dev, version_after.st_ino, version_after.st_ctime_ns) == (
        version_before.st_dev,
        version_before.st_ino,
        version_before.st_ctime_ns,
    )
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_journal_publish_revalidates_exact_forward_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    original_prepare = OperationJournalStore.prepare
    replaced = False

    def replace_guard_before_journal_publish(self, plan, *, package_version):
        nonlocal replaced
        guard_bytes = marker_path.read_bytes()
        marker_path.unlink()
        marker_path.write_bytes(guard_bytes)
        replaced = True
        return original_prepare(self, plan, package_version=package_version)

    monkeypatch.setattr(OperationJournalStore, "prepare", replace_guard_before_journal_publish)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.3.0",
        legacy_marker=admitted,
    )

    assert replaced is True
    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert json.loads(marker_path.read_text(encoding="utf-8"))["schema_version"] == 2
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize("terminal_status", ["verifying", "completed"])
def test_i368_terminal_journal_rejects_tampered_digest_before_finalization(
    tmp_path: Path,
    monkeypatch,
    terminal_status: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / terminal_status
    (target_root / "spec-dock").mkdir(parents=True)
    method_name = "mark_completed" if terminal_status == "verifying" else "remove_completed"
    original = getattr(OperationJournalStore, method_name)

    def fail_terminal_transition(*_args, **_kwargs):
        raise DistributionApplyError("injected terminal transition failure")

    monkeypatch.setattr(OperationJournalStore, method_name, fail_terminal_transition)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["status"] == terminal_status
    payload["plan_digest"] = "0" * 64
    journal_path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    before = journal_path.read_bytes()

    monkeypatch.setattr(OperationJournalStore, method_name, original)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason == "journal-plan-mismatch"
    assert journal_path.read_bytes() == before


def test_i368_completed_journal_retains_recovery_authority_after_target_gains_hardlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_remove = OperationJournalStore.remove_completed

    def interrupt_after_completed(*_args, **_kwargs):
        raise DistributionApplyError("injected completed-journal interruption")

    monkeypatch.setattr(OperationJournalStore, "remove_completed", interrupt_after_completed)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert json.loads(journal_path.read_text(encoding="utf-8"))["status"] == "completed"
    managed_target = target_root / ".github" / "workflows" / "ci.yml"
    (target_root / "managed-target-alias").hardlink_to(managed_target)

    monkeypatch.setattr(OperationJournalStore, "remove_completed", original_remove)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason in {"journal-precondition-mismatch", "distribution postcondition failed"}
    assert journal_path.exists()


def test_i368_terminal_journal_finalizes_after_completed_prune_disappears_from_assessment(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old, mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    (target_root / "spec-dock").mkdir()
    original_remove = OperationJournalStore.remove_completed

    def fail_finalization(*_args, **_kwargs):
        raise DistributionApplyError("injected terminal finalization failure")

    monkeypatch.setattr(OperationJournalStore, "remove_completed", fail_finalization)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert not target.exists()
    assert journal_path.is_file()

    monkeypatch.setattr(OperationJournalStore, "remove_completed", original_remove)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()


def test_i368_journal_finalization_preserves_concurrent_replacement_quarantine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")
    completed = managed_distribution.replace(
        prepared,
        status="completed",
        actions=tuple(managed_distribution.replace(action, checkpoint="verified") for action in prepared.actions),
        created_parent_bindings=(),
    )
    completed = store.write(completed)
    original_rename = managed_distribution._rename_distribution_no_replace
    replacement = b"user-owned replacement\n"
    replaced = False

    def replace_before_quarantine(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal replaced
        if not replaced and source_name == store.path.name and destination_name.endswith(".remove"):
            replaced = True
            store.path.unlink()
            store.path.write_bytes(replacement)
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_before_quarantine)

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        store.remove_completed(completed)

    assert replaced is True
    assert not store.path.exists() and not store.path.is_symlink()
    quarantines = tuple(store.path.parent.glob(f".{store.path.name}.*.remove"))
    assert len(quarantines) == 1
    assert quarantines[0].read_bytes() == replacement


def test_i368_legacy_marker_removal_preserves_concurrent_replacement_quarantine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase="preflight-complete",
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    admitted = managed_distribution._read_distribution_retry_marker(target_root)
    assert admitted is not None
    store = OperationJournalStore(target_root)
    original_rename = managed_distribution._rename_distribution_no_replace
    replacement = b"user-owned replacement\n"
    replaced = False

    def replace_before_quarantine(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal replaced
        if not replaced and source_name == marker_path.name and destination_name.endswith(".remove"):
            replaced = True
            marker_path.unlink()
            marker_path.write_bytes(replacement)
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_before_quarantine)

    with pytest.raises(DistributionApplyError, match="legacy-marker-unconvertible"):
        store.remove_legacy_marker(admitted)

    assert replaced is True
    assert not marker_path.exists() and not marker_path.is_symlink()
    quarantines = tuple(marker_path.parent.glob(f".{marker_path.name}.*.remove"))
    assert len(quarantines) == 1
    assert quarantines[0].read_bytes() == replacement


def test_i368_journal_cleanup_failure_preserves_quarantine_recovery_authority(
    tmp_path: Path,
    monkeypatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    prepared = store.prepare(executable, package_version="1.2.3")
    completed = managed_distribution.replace(
        prepared,
        status="completed",
        actions=tuple(managed_distribution.replace(action, checkpoint="verified") for action in prepared.actions),
        created_parent_bindings=(),
    )
    completed = store.write(completed)
    before = store.path.read_bytes()
    original_remove = managed_distribution._remove_distribution_stage_if_owned

    def fail_quarantine_cleanup(parent_fd, stage_name, created, *, strict=False, **kwargs):
        if stage_name.endswith(".remove"):
            raise DistributionApplyError("simulated quarantine cleanup failure")
        return original_remove(parent_fd, stage_name, created, strict=strict, **kwargs)

    monkeypatch.setattr(managed_distribution, "_remove_distribution_stage_if_owned", fail_quarantine_cleanup)

    with pytest.raises(DistributionApplyError, match="journal finalization failed"):
        store.remove_completed(completed)

    assert not store.path.exists() and not store.path.is_symlink()
    quarantines = list(store.path.parent.glob(f".{store.path.name}.*.remove"))
    assert len(quarantines) == 1
    assert quarantines[0].read_bytes() == before


def test_i368_legacy_marker_quarantine_fsync_failure_restores_marker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="update",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase="preflight-complete",
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    before = marker_path.read_bytes()
    original_fsync = managed_distribution.os.fsync
    failed = False

    def fail_quarantine_fsync_once(fd: int) -> None:
        nonlocal failed
        if not failed:
            failed = True
            raise OSError("simulated quarantine fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(managed_distribution.os, "fsync", fail_quarantine_fsync_once)

    with pytest.raises(DistributionApplyError, match="legacy-marker-unconvertible"):
        OperationJournalStore(target_root).remove_legacy_marker(marker)

    assert marker_path.read_bytes() == before
    assert not list(marker_path.parent.glob(f".{marker_path.name}.*.remove"))


def test_i368_same_plan_partial_failure_resumes_from_journal_checkpoint(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    second_source = install_root / ".agents" / "skills" / "example" / "SKILL.md"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_apply = managed_distribution._apply_distribution_action
    calls = 0

    def fail_second_action(
        plan: DistributionPlan,
        action_target_root: Path,
        action: DistributionAction,
        snapshot: DistributionTargetSnapshot,
        created_parent_bindings: dict[str, PathIdentitySnapshot],
        stage_ownership_recorder: Callable[[DistributionStageOwnership], None] | None = None,
    ) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise DistributionApplyError("injected partial failure")
        original_apply(
            plan,
            action_target_root,
            action,
            snapshot,
            created_parent_bindings,
            stage_ownership_recorder,
        )

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", fail_second_action)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    assert (target_root / "spec-dock" / ".distribution-journal.json").is_file()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", original_apply)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert second_source.relative_to(install_root).as_posix() in {
        path.relative_to(target_root).as_posix() for path in target_root.rglob("*") if path.is_file()
    }
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_checkpoint_write_failure_recovers_from_exact_postcondition(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_first_checkpoint(
        self: OperationJournalStore,
        journal: managed_distribution.OperationJournal,
        completed_paths: tuple[str, ...],
    ) -> managed_distribution.OperationJournal:
        nonlocal failed
        if not failed and completed_paths:
            failed = True
            raise DistributionApplyError("injected checkpoint failure")
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_first_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    assert first.status == "recovery_required"
    assert journal_path.is_file()
    failed_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert {item["relative_path"] for item in failed_payload["created_parent_bindings"]} >= {
        ".github",
        ".github/workflows",
    }

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not journal_path.exists()


def test_i369_published_fresh_create_rejects_same_semantics_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    replaced = False

    def replace_after_create_checkpoint(self, journal, completed_paths):
        nonlocal replaced
        result = original_checkpoint(self, journal, completed_paths)
        if not replaced and ".github/workflows/ci.yml" in completed_paths:
            target = target_root / ".github/workflows/ci.yml"
            replacement = target.with_name("ci.yml.external")
            replacement.write_bytes(target.read_bytes())
            replacement.chmod(target.stat().st_mode & 0o777)
            target.unlink()
            replacement.rename(target)
            replaced = True
            raise DistributionApplyError("injected post-checkpoint create replacement")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", replace_after_create_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    assert replaced is True, first.reason
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    record = next(item for item in journal_payload["actions"] if item["path"] == ".github/workflows/ci.yml")
    assert record["action"] == "create"
    assert record["checkpoint"] == "published"
    assert all(field in record["postcondition"] for field in ("device", "inode", "ctime_ns", "link_count"))
    assert record["postcondition"]["inode"] != (target_root / ".github/workflows/ci.yml").stat().st_ino

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason in {"journal-plan-mismatch", "journal-precondition-mismatch"}
    assert journal_path.exists()


def test_i369_published_recognized_upgrade_rejects_same_semantics_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github/workflows/ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    original_checkpoint = OperationJournalStore.checkpoint_published
    replaced = False

    def replace_after_upgrade_checkpoint(self, journal, completed_paths):
        nonlocal replaced
        result = original_checkpoint(self, journal, completed_paths)
        if not replaced and ".github/workflows/ci.yml" in completed_paths:
            replacement = target.with_name("ci.yml.external")
            replacement.write_bytes(target.read_bytes())
            replacement.chmod(target.stat().st_mode & 0o777)
            target.unlink()
            replacement.rename(target)
            replaced = True
            raise DistributionApplyError("injected post-checkpoint upgrade replacement")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", replace_after_upgrade_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    assert replaced is True
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    record = next(item for item in journal_payload["actions"] if item["path"] == ".github/workflows/ci.yml")
    assert record["action"] == "upgrade"
    assert record["checkpoint"] == "published"
    assert all(field in record["postcondition"] for field in ("device", "inode", "ctime_ns", "link_count"))
    assert record["postcondition"]["inode"] != target.stat().st_ino

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason in {"journal-plan-mismatch", "journal-precondition-mismatch"}
    assert journal_path.exists()


def test_i369_same_run_fresh_create_rejects_same_semantics_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    replaced = False

    def replace_after_create_checkpoint(self, journal, completed_paths):
        nonlocal replaced
        result = original_checkpoint(self, journal, completed_paths)
        if not replaced and ".github/workflows/ci.yml" in completed_paths:
            target = target_root / ".github/workflows/ci.yml"
            replacement = target.with_name("ci.yml.external")
            replacement.write_bytes(target.read_bytes())
            replacement.chmod(target.stat().st_mode & 0o777)
            target.unlink()
            replacement.rename(target)
            replaced = True
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", replace_after_create_checkpoint)
    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert replaced is True
    assert (target_root / "spec-dock/.distribution-journal.json").exists()


def test_i369_same_run_recognized_upgrade_rejects_same_semantics_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github/workflows/ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    original_checkpoint = OperationJournalStore.checkpoint_published
    replaced = False

    def replace_after_upgrade_checkpoint(self, journal, completed_paths):
        nonlocal replaced
        result = original_checkpoint(self, journal, completed_paths)
        if not replaced and ".github/workflows/ci.yml" in completed_paths:
            replacement = target.with_name("ci.yml.external")
            replacement.write_bytes(target.read_bytes())
            replacement.chmod(target.stat().st_mode & 0o777)
            target.unlink()
            replacement.rename(target)
            replaced = True
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", replace_after_upgrade_checkpoint)
    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason in {"journal-plan-mismatch", "journal-precondition-mismatch"}
    assert replaced is True
    assert (target_root / "spec-dock/.distribution-journal.json").exists()


@pytest.mark.parametrize("divergence", ("replacement", "hard-link", "mutate-restore"))
def test_i369_fresh_workbench_retry_binds_exact_external_seed_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    divergence: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_apply = managed_distribution.apply_distribution_plan
    failed = False

    def fail_once(plan, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise DistributionApplyError("injected fresh seed interruption")
        return original_apply(plan, **kwargs)

    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", fail_once)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    monkeypatch.setattr(managed_distribution, "apply_distribution_plan", original_apply)

    source = scaffold_root / "templates/root/.workbench/README.md"
    target = target_root / "spec-dock/.workbench/README.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    target.chmod(stat.S_IMODE(source.stat().st_mode))
    original_identity = target.stat()
    extra_link = tmp_path / "external-workbench-link"

    original_write = OperationJournalStore.write
    injected = False

    def diverge_after_seed_reconciliation(self, journal, *, predecessor=None):
        nonlocal injected
        result = original_write(self, journal, predecessor=predecessor)
        seed_record = next(
            (
                record
                for record in result.actions
                if record.path == "spec-dock/.workbench/README.md"
                and record.checkpoint == "published"
                and all(field in record.postcondition for field in ("device", "inode", "ctime_ns", "link_count"))
            ),
            None,
        )
        if not injected and seed_record is not None:
            injected = True
            if divergence == "replacement":
                replacement = target.with_name("README.external")
                replacement.write_bytes(target.read_bytes())
                replacement.chmod(stat.S_IMODE(target.stat().st_mode))
                target.unlink()
                replacement.rename(target)
            elif divergence == "hard-link":
                os.link(target, extra_link)
            else:
                original_mode = stat.S_IMODE(target.stat().st_mode)
                target.chmod(original_mode ^ 0o100)
                target.chmod(original_mode)
        return result

    monkeypatch.setattr(OperationJournalStore, "write", diverge_after_seed_reconciliation)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert injected is True
    assert second.status == "recovery_required"
    assert second.reason in {"journal-plan-mismatch", "journal-precondition-mismatch"}
    assert (target_root / "spec-dock/.distribution-journal.json").exists()
    assert (target_root / "spec-dock/.distribution-retry.json").exists()
    assert target.read_bytes() == source.read_bytes()
    if divergence == "replacement":
        assert target.stat().st_ino != original_identity.st_ino
    elif divergence == "hard-link":
        assert target.stat().st_ino == original_identity.st_ino
        assert target.stat().st_nlink == 2
        assert extra_link.exists()
    else:
        assert target.stat().st_ino == original_identity.st_ino
        assert target.stat().st_ctime_ns != original_identity.st_ctime_ns


def _rewrite_published_successors_as_protocol1(target_root: Path) -> None:
    store = OperationJournalStore(target_root)
    journal = store._read(managed_distribution._root_identity_for_assessment(target_root))
    marker = managed_distribution._read_distribution_retry_marker(target_root)
    if marker is not None:
        store.bind_forward_guard(marker)
    legacy_actions = tuple(
        replace(
            record,
            postcondition={
                key: value for key, value in record.postcondition.items() if key not in {"device", "inode", "ctime_ns"}
            },
        )
        if record.action in {"create", "upgrade"} and record.checkpoint != "pending"
        else record
        for record in journal.actions
    )
    store.write(
        replace(
            journal,
            protocol_version=managed_distribution._DISTRIBUTION_LEGACY_JOURNAL_PROTOCOL_VERSION,
            actions=legacy_actions,
        ),
        predecessor=journal,
    )


def test_i369_protocol1_published_create_without_witness_refuses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    stopped = False

    def stop_after_create_checkpoint(self, journal, completed_paths):
        nonlocal stopped
        result = original_checkpoint(self, journal, completed_paths)
        if not stopped and ".github/workflows/ci.yml" in completed_paths:
            stopped = True
            raise DistributionApplyError("injected protocol-1 create stop")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", stop_after_create_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    _rewrite_published_successors_as_protocol1(target_root)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason == "journal-protocol-incompatible"
    assert (target_root / "spec-dock/.distribution-journal.json").exists()
    assert (target_root / "spec-dock/.distribution-retry.json").exists()


def test_i369_protocol1_published_upgrade_without_witness_refuses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github/workflows/ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    original_checkpoint = OperationJournalStore.checkpoint_published
    stopped = False

    def stop_after_upgrade_checkpoint(self, journal, completed_paths):
        nonlocal stopped
        result = original_checkpoint(self, journal, completed_paths)
        if not stopped and ".github/workflows/ci.yml" in completed_paths:
            stopped = True
            raise DistributionApplyError("injected protocol-1 upgrade stop")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", stop_after_upgrade_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert first.status == "recovery_required"
    _rewrite_published_successors_as_protocol1(target_root)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason == "journal-protocol-incompatible"
    assert (target_root / "spec-dock/.distribution-journal.json").exists()
    assert (target_root / "spec-dock/.distribution-retry.json").exists()


def test_i369_protocol1_completed_journal_only_cleans_up_semantic_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_remove_marker = OperationJournalStore.remove_legacy_marker
    stopped = False

    def stop_after_guard_removal(self, marker):
        nonlocal stopped
        original_remove_marker(self, marker)
        if not stopped:
            stopped = True
            raise DistributionApplyError("injected terminal journal-only stop")

    monkeypatch.setattr(OperationJournalStore, "remove_legacy_marker", stop_after_guard_removal)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    assert (target_root / "spec-dock/.distribution-journal.json").exists()
    assert not (target_root / "spec-dock/.distribution-retry.json").exists()
    _rewrite_published_successors_as_protocol1(target_root)

    monkeypatch.setattr(OperationJournalStore, "remove_legacy_marker", original_remove_marker)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert not (target_root / "spec-dock/.distribution-journal.json").exists()


def test_i368_retry_cleans_exact_stage_created_after_write_ahead_reservation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset("spec-dock/spec-dock.version", b"1.2.3\n", mode=0o644),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    expected = next(
        item.identity for item in executable.distribution_plan.current_assets if item.path == ".github/workflows/ci.yml"
    )
    stage_name = managed_distribution._new_distribution_stage_name(".github/workflows/ci.yml", expected)
    store.record_staging_lease(
        journal,
        managed_distribution._reserved_distribution_stage_ownership(".github/workflows/ci.yml", stage_name, "regular"),
    )
    stage = parent / stage_name
    stage.write_bytes(b"desired\n")
    stage.chmod(0o644)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert (parent / "ci.yml").read_bytes() == b"desired\n"
    assert not stage.exists()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("outcome", ["converges", "mismatch"])
def test_i368_zero_reserved_created_parent_stage_crash_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    outcome: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target_rel = ".github/workflows/ci.yml" if kind == "regular" else "spec"

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    original_symlink = managed_distribution.os.symlink
    crashed = False

    def crash_after_regular_stage_create(path, flags, *args, **kwargs):
        nonlocal crashed
        fd = original_open(path, flags, *args, **kwargs)
        if kind == "regular" and not crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    def crash_after_symlink_stage_create(source, destination, *args, **kwargs):
        nonlocal crashed
        original_symlink(source, destination, *args, **kwargs)
        if (
            kind == "symlink"
            and not crashed
            and isinstance(destination, str)
            and destination.startswith(".spec-dock-symlink-")
        ):
            crashed = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_after_regular_stage_create)
        fault.setattr(managed_distribution.os, "symlink", crash_after_symlink_stage_create)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    assert crashed is True
    journal_path = target_root / "spec-dock" / ".distribution-journal.json"
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    reserved = next(
        lease
        for lease in payload["staging_leases"]
        if lease["path"] == target_rel and lease["device"] == lease["inode"] == lease["ctime_ns"] == 0
    )
    stage = target_root / Path(target_rel).parent / reserved["stage_name"]
    assert stage.exists() or stage.is_symlink()
    if outcome == "mismatch":
        stage.unlink()
        if kind == "regular":
            stage.symlink_to("third-party-target")
        else:
            stage.write_bytes(b"third-party\n")

    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    if outcome == "converges":
        assert retry.status == "completed", retry.reason
        assert not stage.exists() and not stage.is_symlink()
    else:
        assert retry.status == "recovery_required"
        assert retry.reason in {"journal-precondition-mismatch", "managed staging identity changed"}
        assert stage.exists() or stage.is_symlink()
        assert journal_path.exists()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize(
    "recovery_role",
    [
        "predecessor-quarantine",
        "backup-reserved",
        "backup-dual",
        "backup-only-reserved",
        "backup-only",
        "gc-reserved",
        "gc-exact",
    ],
)
def test_i368_pending_create_stale_cleanup_roles_resume_before_action(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    recovery_role: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target_rel = ".github/workflows/ci.yml" if kind == "regular" else "spec"

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    original_symlink = managed_distribution.os.symlink
    stage_crashed = False

    def crash_after_regular_stage_create(path, flags, *args, **kwargs):
        nonlocal stage_crashed
        fd = original_open(path, flags, *args, **kwargs)
        if kind == "regular" and not stage_crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            stage_crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    def crash_after_symlink_stage_create(source, destination, *args, **kwargs):
        nonlocal stage_crashed
        original_symlink(source, destination, *args, **kwargs)
        if (
            kind == "symlink"
            and not stage_crashed
            and isinstance(destination, str)
            and destination.startswith(".spec-dock-symlink-")
        ):
            stage_crashed = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_after_regular_stage_create)
        fault.setattr(managed_distribution.os, "symlink", crash_after_symlink_stage_create)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    original_record = OperationJournalStore.record_staging_lease
    recovery_crashed = False

    def crash_after_recovery_role(self, journal, lease):
        nonlocal recovery_crashed
        updated = original_record(self, journal, lease)
        if lease.path == target_rel and lease.role == recovery_role and not recovery_crashed:
            recovery_crashed = True
            raise SimulatedProcessCrash
        return updated

    with monkeypatch.context() as fault:
        fault.setattr(OperationJournalStore, "record_staging_lease", crash_after_recovery_role)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    assert recovery_crashed is True
    if kind == "regular":
        unknown = target_root / ".github" / "workflows" / "third-party.txt"
        unknown.write_bytes(b"third-party\n")
        blocked = execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
            package_version="1.2.3",
        )
        assert blocked.status == "recovery_required"
        assert unknown.read_bytes() == b"third-party\n"
        assert not (target_root / target_rel).exists()
        unknown.unlink()
    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert retry.status == "completed", retry.reason
    target = target_root / target_rel
    assert target.exists() or target.is_symlink()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("fault_point", ["second-reservation", "second-rename", "first-unlink"])
def test_i368_multi_name_gc_checkpoint_retry_converges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    fault_point: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    original_symlink = managed_distribution.os.symlink
    stage_crashed = False

    def crash_after_regular_stage_create(path, flags, *args, **kwargs):
        nonlocal stage_crashed
        fd = original_open(path, flags, *args, **kwargs)
        if kind == "regular" and not stage_crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            stage_crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    def crash_after_symlink_stage_create(source, destination, *args, **kwargs):
        nonlocal stage_crashed
        original_symlink(source, destination, *args, **kwargs)
        if (
            kind == "symlink"
            and not stage_crashed
            and isinstance(destination, str)
            and destination.startswith(".spec-dock-symlink-")
        ):
            stage_crashed = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_after_regular_stage_create)
        fault.setattr(managed_distribution.os, "symlink", crash_after_symlink_stage_create)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_unlink = managed_distribution.os.unlink
    gc_reserved = 0
    gc_exact = 0
    injected = False

    def record_and_fault(self, journal, lease):
        nonlocal gc_reserved, gc_exact, injected
        updated = original_record(self, journal, lease)
        if lease.role == "gc-reserved":
            gc_reserved += 1
            if fault_point == "second-reservation" and gc_reserved == 2 and not injected:
                injected = True
                raise SimulatedProcessCrash
        elif lease.role == "gc-exact":
            gc_exact += 1
        return updated

    def rename_and_fault(source_fd, source_name, destination_fd, destination_name):
        nonlocal injected
        original_rename(source_fd, source_name, destination_fd, destination_name)
        if fault_point == "second-rename" and gc_reserved >= 2 and not injected:
            injected = True
            raise SimulatedProcessCrash

    def unlink_and_fault(name, *args, **kwargs):
        nonlocal injected
        original_unlink(name, *args, **kwargs)
        if fault_point == "first-unlink" and gc_exact >= 3 and not injected:
            injected = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(OperationJournalStore, "record_staging_lease", record_and_fault)
        fault.setattr(managed_distribution, "_rename_distribution_no_replace", rename_and_fault)
        fault.setattr(managed_distribution.os, "unlink", unlink_and_fault)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    assert injected is True
    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert retry.status == "completed", retry.reason


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize(
    "fault_point",
    [
        "third-reservation",
        "retained-rename",
        "exact-promotion",
        "first-data-gc-unlink",
        "retained-only-promotion",
    ],
)
def test_i368_retained_gc_transition_graph_resumes_without_name_ordering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    fault_point: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    original_symlink = managed_distribution.os.symlink
    stage_crashed = False

    def crash_after_regular_stage_create(path, flags, *args, **kwargs):
        nonlocal stage_crashed
        fd = original_open(path, flags, *args, **kwargs)
        if kind == "regular" and not stage_crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            stage_crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    def crash_after_symlink_stage_create(source, destination, *args, **kwargs):
        nonlocal stage_crashed
        original_symlink(source, destination, *args, **kwargs)
        if (
            kind == "symlink"
            and not stage_crashed
            and isinstance(destination, str)
            and destination.startswith(".spec-dock-symlink-")
        ):
            stage_crashed = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_after_regular_stage_create)
        fault.setattr(managed_distribution.os, "symlink", crash_after_symlink_stage_create)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_unlink = managed_distribution.os.unlink
    gc_names: list[str] = []
    injected = False
    next_token = (1 << 128) - 1

    def descending_token(_size: int = 16) -> str:
        nonlocal next_token
        token = f"{next_token:032x}"
        next_token -= 1
        return token

    def record_and_fault(self, journal, lease):
        nonlocal injected
        updated = original_record(self, journal, lease)
        if lease.role == "gc-reserved" and lease.stage_name not in gc_names:
            gc_names.append(lease.stage_name)
            if fault_point == "third-reservation" and len(gc_names) == 3 and not injected:
                injected = True
                raise SimulatedProcessCrash
        if (
            fault_point == "exact-promotion"
            and len(gc_names) == 3
            and lease.role == "gc-exact"
            and lease.stage_name == gc_names[2]
            and not injected
        ):
            injected = True
            raise SimulatedProcessCrash
        if (
            fault_point == "retained-only-promotion"
            and len(gc_names) == 3
            and lease.role == "backup-only"
            and lease.stage_name == gc_names[2]
            and not injected
        ):
            injected = True
            raise SimulatedProcessCrash
        return updated

    def rename_and_fault(source_fd, source_name, destination_fd, destination_name):
        nonlocal injected
        original_rename(source_fd, source_name, destination_fd, destination_name)
        if fault_point == "retained-rename" and len(gc_names) == 3 and destination_name == gc_names[2] and not injected:
            injected = True
            raise SimulatedProcessCrash

    def unlink_and_fault(name, *args, **kwargs):
        nonlocal injected
        original_unlink(name, *args, **kwargs)
        if fault_point == "first-data-gc-unlink" and len(gc_names) == 3 and name == gc_names[1] and not injected:
            injected = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.secrets, "token_hex", descending_token)
        fault.setattr(OperationJournalStore, "record_staging_lease", record_and_fault)
        fault.setattr(managed_distribution, "_rename_distribution_no_replace", rename_and_fault)
        fault.setattr(managed_distribution.os, "unlink", unlink_and_fault)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    assert injected is True
    assert len(gc_names) == 3
    assert gc_names[1] > gc_names[2]
    persisted = OperationJournalStore(target_root)._read(
        managed_distribution._root_identity_for_assessment(target_root)
    )
    graph = tuple(
        lease
        for lease in persisted.staging_leases
        if lease.path == ".github/workflows/ci.yml" and lease.gc_ordinal is not None
    )
    if kind == "symlink":
        graph = tuple(
            lease for lease in persisted.staging_leases if lease.path == "spec" and lease.gc_ordinal is not None
        )
    ordered = managed_distribution._ordered_gc_transition_leases(persisted)
    ordered = tuple(lease for lease in ordered if lease.path == graph[0].path)
    assert [lease.gc_ordinal for lease in ordered] == sorted(
        lease.gc_ordinal for lease in ordered if lease.gc_ordinal is not None
    )
    assert [lease.gc_ordinal for lease in sorted(ordered, key=lambda lease: lease.stage_name)] != [
        lease.gc_ordinal for lease in ordered
    ]
    ordinal_three = next(lease for lease in graph if lease.gc_ordinal == 3)
    expected_role = {
        "third-reservation": "gc-reserved",
        "retained-rename": "gc-reserved",
        "exact-promotion": "gc-exact",
        "first-data-gc-unlink": "gc-exact",
        "retained-only-promotion": "backup-only",
    }[fault_point]
    assert ordinal_three.role == expected_role
    ordinal_three_path = target_root / Path(ordinal_three.path).parent / ordinal_three.stage_name
    assert (ordinal_three_path.exists() or ordinal_three_path.is_symlink()) is (fault_point != "third-reservation")
    if fault_point in {"first-data-gc-unlink", "retained-only-promotion"}:
        ordinal_two = next(lease for lease in graph if lease.gc_ordinal == 2)
        ordinal_two_path = target_root / Path(ordinal_two.path).parent / ordinal_two.stage_name
        assert not ordinal_two_path.exists() and not ordinal_two_path.is_symlink()
    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )
    assert retry.status == "completed", retry.reason


@pytest.mark.parametrize(
    "forgery",
    [
        "duplicate-ordinal",
        "ambiguous-successor",
        "missing-predecessor",
        "canonical-predecessor",
        "canonical-stage",
        "foreign-predecessor",
    ],
)
def test_i368_gc_graph_forgery_is_rejected_before_namespace_mutation(
    tmp_path: Path,
    forgery: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    assert expected.kind in {"regular", "symlink"}
    expected_kind: Literal["regular", "symlink"] = "regular" if expected.kind == "regular" else "symlink"
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    first_name = f"{stage_name}.00000000000000000000000000000003.gc"
    second_name = f"{stage_name}.00000000000000000000000000000002.gc"
    third_name = f"{stage_name}.00000000000000000000000000000001.gc"
    first = managed_distribution._reserved_distribution_stage_ownership(
        action.path,
        first_name,
        expected_kind,
        role="gc-reserved",
        gc_predecessor_name=stage_name,
        gc_ordinal=1,
    )
    second = managed_distribution._reserved_distribution_stage_ownership(
        action.path,
        second_name,
        expected_kind,
        role="gc-reserved",
        gc_predecessor_name=first_name,
        gc_ordinal=2,
    )
    if forgery == "duplicate-ordinal":
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            third_name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=first_name,
            gc_ordinal=2,
        )
    elif forgery == "ambiguous-successor":
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            third_name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=first_name,
            gc_ordinal=3,
        )
    elif forgery == "missing-predecessor":
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            second_name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=f"{stage_name}.foreign.gc",
            gc_ordinal=2,
        )
    elif forgery == "canonical-predecessor":
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            second_name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=Path(action.path).name,
            gc_ordinal=2,
        )
    elif forgery == "canonical-stage":
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            Path(action.path).name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=first_name,
            gc_ordinal=2,
        )
    else:
        foreign_action = next(
            item
            for item in journal.actions
            if item.path != action.path
            and managed_distribution._expected_target_identity(executable.distribution_plan, item.path) is not None
        )
        foreign_expected = managed_distribution._expected_target_identity(
            executable.distribution_plan, foreign_action.path
        )
        assert foreign_expected is not None
        assert foreign_expected.kind in {"regular", "symlink"}
        foreign_kind: Literal["regular", "symlink"] = "regular" if foreign_expected.kind == "regular" else "symlink"
        foreign_name = managed_distribution._new_distribution_stage_name(foreign_action.path, foreign_expected)
        foreign = managed_distribution._reserved_distribution_stage_ownership(
            foreign_action.path,
            foreign_name,
            foreign_kind,
        )
        forged = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            second_name,
            expected_kind,
            role="gc-reserved",
            gc_predecessor_name=foreign_name,
            gc_ordinal=2,
        )
    if forgery in {"duplicate-ordinal", "ambiguous-successor"}:
        leases: tuple[DistributionStageOwnership, ...] = (first, second, forged)
    elif forgery == "foreign-predecessor":
        leases = (first, foreign, forged)
    else:
        leases = (first, forged)
    journal = store.write(
        managed_distribution.replace(journal, staging_leases=leases),
        predecessor=journal,
    )
    journal_before = store.path.read_bytes()
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    guard_before = guard_path.read_bytes()
    namespace_before = sorted(
        (path.relative_to(target_root).as_posix(), path.is_symlink(), path.read_bytes() if path.is_file() else None)
        for path in target_root.rglob("*")
    )

    with pytest.raises(DistributionApplyError, match="journal-plan-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == journal_before
    assert guard_path.read_bytes() == guard_before
    assert (
        sorted(
            (path.relative_to(target_root).as_posix(), path.is_symlink(), path.read_bytes() if path.is_file() else None)
            for path in target_root.rglob("*")
        )
        == namespace_before
    )


def test_i368_production_retry_validates_gc_graph_before_guard_or_workspace_reads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
        )
    )
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    assert expected.kind in {"regular", "symlink"}
    expected_kind: Literal["regular", "symlink"] = "regular" if expected.kind == "regular" else "symlink"
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    forged = managed_distribution._reserved_distribution_stage_ownership(
        action.path,
        Path(action.path).name,
        expected_kind,
        role="gc-reserved",
        gc_predecessor_name=stage_name,
        gc_ordinal=1,
    )
    store.write(managed_distribution.replace(journal, staging_leases=(forged,)), predecessor=journal)

    def forbidden_read(*_args, **_kwargs):
        raise AssertionError("managed namespace read preceded GC graph validation")

    monkeypatch.setattr(OperationJournalStore, "_assert_guard_anchors_journal", forbidden_read)
    monkeypatch.setattr(managed_distribution, "build_workspace_assessment", forbidden_read)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-plan-mismatch"


def test_i368_reserved_ordinal_three_rejects_unrelated_ordinal_two_inode(
    tmp_path: Path,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    assert expected.kind == "regular"
    parent = target_root / Path(action.path).parent
    parent.mkdir(parents=True, exist_ok=True)
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    predecessor_name = f"{stage_name}.predecessor.remove"
    backup_name = managed_distribution._distribution_quarantine_backup_name(predecessor_name)
    ordinal_two_name = f"{stage_name}.00000000000000000000000000000002.gc"
    ordinal_three_name = f"{stage_name}.00000000000000000000000000000001.gc"
    predecessor = parent / predecessor_name
    backup = parent / backup_name
    ordinal_two = parent / ordinal_two_name
    ordinal_three = parent / ordinal_three_name
    predecessor.write_bytes(b"inode-b\n")
    os.link(predecessor, backup)
    ordinal_two.write_bytes(b"inode-a\n")
    os.link(ordinal_two, ordinal_three)
    predecessor_info = predecessor.lstat()
    ordinal_two_info = ordinal_two.lstat()
    leases = (
        DistributionStageOwnership(
            path=action.path,
            stage_name=predecessor_name,
            device=predecessor_info.st_dev,
            inode=predecessor_info.st_ino,
            ctime_ns=predecessor_info.st_ctime_ns,
            file_type="regular",
            role="predecessor-quarantine",
        ),
        managed_distribution._distribution_stage_ownership(
            action.path,
            backup_name,
            backup.lstat(),
            role="backup-dual",
        ),
        DistributionStageOwnership(
            path=action.path,
            stage_name=ordinal_two_name,
            device=ordinal_two_info.st_dev,
            inode=ordinal_two_info.st_ino,
            ctime_ns=ordinal_two_info.st_ctime_ns,
            file_type="regular",
            role="gc-exact",
            gc_predecessor_name=predecessor_name,
            gc_ordinal=2,
        ),
        managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            ordinal_three_name,
            "regular",
            role="gc-reserved",
            gc_predecessor_name=backup_name,
            gc_ordinal=3,
        ),
    )
    journal = store.write(managed_distribution.replace(journal, staging_leases=leases), predecessor=journal)
    journal_before = store.path.read_bytes()
    namespace_before = {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()}

    with pytest.raises(DistributionApplyError, match="journal-plan-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == journal_before
    assert {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()} == namespace_before


@pytest.mark.parametrize("forgery", ["ordinal-two-unrelated-backup", "backup-reserved-wrong-predecessor"])
def test_i368_reserved_companion_requires_exact_named_predecessor(
    tmp_path: Path,
    forgery: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.path == ".github/workflows/ci.yml")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    predecessor_name = f"{stage_name}.predecessor.gc"
    predecessor = parent / predecessor_name
    predecessor.write_bytes(b"inode-b\n")
    predecessor_info = predecessor.lstat()
    predecessor_lease = DistributionStageOwnership(
        path=action.path,
        stage_name=predecessor_name,
        device=predecessor_info.st_dev,
        inode=predecessor_info.st_ino,
        ctime_ns=predecessor_info.st_ctime_ns,
        file_type="regular",
        role="gc-exact" if forgery == "ordinal-two-unrelated-backup" else "predecessor-quarantine",
        gc_predecessor_name=stage_name if forgery == "ordinal-two-unrelated-backup" else None,
        gc_ordinal=1 if forgery == "ordinal-two-unrelated-backup" else None,
    )
    unrelated_name = f"{stage_name}.unrelated"
    unrelated = parent / unrelated_name
    unrelated.write_bytes(b"inode-a\n")
    if forgery == "ordinal-two-unrelated-backup":
        support_lease = None
        reserved_name = f"{stage_name}.reserved.gc"
        reserved = parent / reserved_name
        os.link(unrelated, reserved)
        unrelated_info = unrelated.lstat()
        unrelated_lease = DistributionStageOwnership(
            path=action.path,
            stage_name=unrelated_name,
            device=unrelated_info.st_dev,
            inode=unrelated_info.st_ino,
            ctime_ns=unrelated_info.st_ctime_ns,
            file_type="regular",
            role="backup-dual",
        )
        reserved_lease = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            reserved_name,
            "regular",
            role="gc-reserved",
            gc_predecessor_name=predecessor_name,
            gc_ordinal=2,
        )
    else:
        predecessor.unlink()
        unrelated.rename(predecessor)
        reserved_name = managed_distribution._distribution_quarantine_backup_name(f"{stage_name}.other.remove")
        reserved = parent / reserved_name
        os.link(predecessor, reserved)
        unrelated_info = predecessor.lstat()
        predecessor_lease = managed_distribution.replace(
            predecessor_lease,
            device=unrelated_info.st_dev,
            inode=unrelated_info.st_ino,
            ctime_ns=unrelated_info.st_ctime_ns,
        )
        unrelated_lease = None
        support_lease = managed_distribution.replace(
            predecessor_lease,
            stage_name=f"{stage_name}.recorded-backup",
            role="backup-dual",
        )
        reserved_lease = managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            reserved_name,
            "regular",
            role="backup-reserved",
        )
    bindings = tuple(
        managed_distribution._snapshot_from_stat(binding.relative_path, (target_root / binding.relative_path).lstat())
        if (target_root / binding.relative_path).is_dir()
        else binding
        for binding in journal.created_parent_bindings
    )
    if unrelated_lease is not None:
        leases = (predecessor_lease, unrelated_lease, reserved_lease)
    else:
        assert support_lease is not None
        leases = (predecessor_lease, support_lease, reserved_lease)
    journal = store.write(
        managed_distribution.replace(journal, staging_leases=leases, created_parent_bindings=bindings),
        predecessor=journal,
    )
    journal_before = store.path.read_bytes()
    namespace_before = {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()}
    if forgery == "ordinal-two-unrelated-backup":
        assert unrelated_lease is not None
        assert reserved.lstat().st_ino == unrelated_lease.inode
        assert reserved.lstat().st_ino != predecessor_lease.inode
    else:
        assert reserved_name != managed_distribution._distribution_quarantine_backup_name(predecessor_name)
        assert reserved.lstat().st_ino == predecessor_lease.inode

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        managed_distribution._assert_created_parent_bindings_closed_set(target_root, journal)

    assert store.path.read_bytes() == journal_before
    assert {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()} == namespace_before


@pytest.mark.parametrize("ambiguous", [False, True])
def test_i368_resume_ordinal_two_ignores_unrelated_leading_backup_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambiguous: bool,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.path == ".github/workflows/ci.yml")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    predecessor_name = f"{stage_name}.missing-predecessor.gc"
    derived_backup_name = managed_distribution._distribution_quarantine_backup_name(predecessor_name)
    derived_backup = parent / derived_backup_name
    derived_support_name = f"{stage_name}.derived-support.remove"
    derived_support = parent / derived_support_name
    derived_backup.write_bytes(b"inode-b\n")
    os.link(derived_backup, derived_support)
    derived_info = derived_backup.lstat()
    unrelated_backup_name = f"{stage_name}.unrelated-backup"
    unrelated_backup = parent / unrelated_backup_name
    reserved_name = f"{stage_name}.reserved-ordinal-two.gc"
    reserved = parent / reserved_name
    unrelated_backup.write_bytes(b"inode-a\n")
    os.link(unrelated_backup, reserved)
    unrelated_info = unrelated_backup.lstat()
    extra_candidate = (
        (
            managed_distribution._reserved_distribution_stage_ownership(
                action.path,
                predecessor_name.removesuffix(".gc"),
                "regular",
                role="backup-reserved",
            ),
        )
        if ambiguous
        else ()
    )
    leases = (
        managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            unrelated_backup_name,
            "regular",
            role="backup-reserved",
        ),
        managed_distribution._distribution_stage_ownership(
            action.path,
            derived_backup_name,
            derived_info,
            role="backup-dual",
        ),
        DistributionStageOwnership(
            path=action.path,
            stage_name=derived_support_name,
            device=derived_info.st_dev,
            inode=derived_info.st_ino,
            ctime_ns=derived_info.st_ctime_ns,
            file_type="regular",
            role="predecessor-quarantine",
        ),
        managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            reserved_name,
            "regular",
            role="gc-reserved",
            gc_predecessor_name=predecessor_name,
            gc_ordinal=2,
        ),
        *extra_candidate,
    )
    bindings = tuple(
        managed_distribution._snapshot_from_stat(binding.relative_path, (target_root / binding.relative_path).lstat())
        if (target_root / binding.relative_path).is_dir()
        else binding
        for binding in journal.created_parent_bindings
    )
    journal = store.write(
        managed_distribution.replace(journal, staging_leases=leases, created_parent_bindings=bindings),
        predecessor=journal,
    )
    journal_before = store.path.read_bytes()
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    guard_before = guard_path.read_bytes()
    namespace_before = {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()}
    assert reserved.lstat().st_ino == unrelated_info.st_ino
    assert reserved.lstat().st_ino != derived_info.st_ino

    def forbidden_write(*_args, **_kwargs):
        raise AssertionError("unrelated backup was promoted to GC authority")

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", forbidden_write)

    expected_error = "journal-plan-mismatch" if ambiguous else "managed staging cleanup failed"
    with pytest.raises(DistributionApplyError, match=expected_error):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == journal_before
    assert guard_path.read_bytes() == guard_before
    assert {path.name: (path.lstat().st_ino, path.read_bytes()) for path in parent.iterdir()} == namespace_before


def test_i368_gc_backup_source_ambiguity_is_rejected_before_earlier_path_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    earlier_action = next(item for item in journal.actions if item.path == ".github/workflows/ci.yml")
    later_action = next(item for item in journal.actions if item.path == "spec")
    earlier_expected = managed_distribution._expected_target_identity(
        executable.distribution_plan,
        earlier_action.path,
    )
    later_expected = managed_distribution._expected_target_identity(executable.distribution_plan, later_action.path)
    assert earlier_expected is not None and earlier_expected.kind == "regular"
    assert later_expected is not None and later_expected.kind == "symlink"
    earlier_parent = target_root / ".github" / "workflows"
    earlier_parent.mkdir(parents=True)
    earlier_predecessor_name = managed_distribution._new_distribution_stage_name(
        earlier_action.path,
        earlier_expected,
    )
    earlier_gc_name = f"{earlier_predecessor_name}.earlier.gc"
    earlier_gc = earlier_parent / earlier_gc_name
    earlier_gc.write_bytes(b"earlier\n")
    earlier_info = earlier_gc.lstat()
    earlier_predecessor = DistributionStageOwnership(
        path=earlier_action.path,
        stage_name=earlier_predecessor_name,
        device=earlier_info.st_dev,
        inode=earlier_info.st_ino,
        ctime_ns=earlier_info.st_ctime_ns,
        file_type="regular",
    )
    earlier_reserved = managed_distribution._reserved_distribution_stage_ownership(
        earlier_action.path,
        earlier_gc_name,
        "regular",
        role="gc-reserved",
        gc_predecessor_name=earlier_predecessor_name,
        gc_ordinal=1,
    )
    later_stage_name = managed_distribution._new_distribution_stage_name(later_action.path, later_expected)
    later_predecessor_name = f"{later_stage_name}.missing-predecessor.gc"
    later_derived_name = managed_distribution._distribution_quarantine_backup_name(later_predecessor_name)
    later_prefix_name = later_predecessor_name.removesuffix(".gc")
    later_derived = DistributionStageOwnership(
        path=later_action.path,
        stage_name=later_derived_name,
        device=1,
        inode=2,
        ctime_ns=3,
        file_type="symlink",
        role="backup-dual",
    )
    later_prefix = managed_distribution._reserved_distribution_stage_ownership(
        later_action.path,
        later_prefix_name,
        "symlink",
        role="backup-reserved",
    )
    later_reserved = managed_distribution._reserved_distribution_stage_ownership(
        later_action.path,
        f"{later_stage_name}.reserved.gc",
        "symlink",
        role="gc-reserved",
        gc_predecessor_name=later_predecessor_name,
        gc_ordinal=2,
    )
    journal = store.write(
        managed_distribution.replace(
            journal,
            staging_leases=(
                earlier_predecessor,
                earlier_reserved,
                later_derived,
                later_prefix,
                later_reserved,
            ),
        ),
        predecessor=journal,
    )
    journal_before = store.path.read_bytes()
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    guard_before = guard_path.read_bytes()
    namespace_before = sorted(
        (path.relative_to(target_root).as_posix(), path.is_symlink(), path.read_bytes() if path.is_file() else None)
        for path in target_root.rglob("*")
    )

    def forbidden_write(*_args, **_kwargs):
        raise AssertionError("earlier GC path mutated before graph-wide ambiguity rejection")

    monkeypatch.setattr(OperationJournalStore, "record_staging_lease", forbidden_write)

    with pytest.raises(DistributionApplyError, match="journal-plan-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == journal_before
    assert guard_path.read_bytes() == guard_before
    assert (
        sorted(
            (path.relative_to(target_root).as_posix(), path.is_symlink(), path.read_bytes() if path.is_file() else None)
            for path in target_root.rglob("*")
        )
        == namespace_before
    )


@pytest.mark.parametrize(
    ("kind", "race"),
    [("regular", "replacement"), ("symlink", "replacement"), ("regular", "unknown-child")],
)
def test_i368_resumed_final_retained_transition_preserves_interposed_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    race: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    original_symlink = managed_distribution.os.symlink
    stage_crashed = False

    def crash_regular(path, flags, *args, **kwargs):
        nonlocal stage_crashed
        fd = original_open(path, flags, *args, **kwargs)
        if kind == "regular" and not stage_crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            stage_crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    def crash_symlink(source, destination, *args, **kwargs):
        nonlocal stage_crashed
        original_symlink(source, destination, *args, **kwargs)
        if (
            kind == "symlink"
            and not stage_crashed
            and isinstance(destination, str)
            and destination.startswith(".spec-dock-symlink-")
        ):
            stage_crashed = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_regular)
        fault.setattr(managed_distribution.os, "symlink", crash_symlink)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    original_rename = managed_distribution._rename_distribution_no_replace
    transition_count = 0
    injected = False
    unknown: Path | None = None
    replacement: Path | None = None

    def interpose_retained(source_fd, source_name, destination_fd, destination_name):
        nonlocal transition_count, injected, unknown, replacement
        if isinstance(source_name, str) and source_name.startswith((
            ".spec-dock-file-",
            ".spec-dock-symlink-",
            ".spec-dock-backup-",
        )):
            transition_count += 1
        source = target_root / Path(".github/workflows" if kind == "regular" else ".") / source_name
        if not injected and transition_count >= 3 and (source.exists() or source.is_symlink()):
            injected = True
            if race == "replacement":
                source.unlink()
                if kind == "regular":
                    source.write_bytes(b"third-party\n")
                else:
                    source.symlink_to("third-party-target")
                replacement = source
            else:
                unknown = source.parent / "unknown-child"
                unknown.write_bytes(b"third-party\n")
        return original_rename(source_fd, source_name, destination_fd, destination_name)

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution, "_rename_distribution_no_replace", interpose_retained)
        blocked = execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
            package_version="1.2.3",
        )

    assert injected is True
    assert blocked.status == "recovery_required"
    if replacement is not None:
        if kind == "regular":
            assert replacement.read_bytes() == b"third-party\n"
        else:
            assert replacement.readlink() == Path("third-party-target")
    else:
        assert unknown is not None
        assert unknown.read_bytes() == b"third-party\n"


@pytest.mark.parametrize("unknown_kind", ["regular", "symlink", "fifo", "unleased-stage"])
def test_i368_stale_cleanup_final_backup_unlink_revalidates_held_created_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    unknown_kind: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)

    class SimulatedProcessCrash(BaseException):
        pass

    original_open = managed_distribution.os.open
    crashed = False

    def crash_after_stage_create(path, flags, *args, **kwargs):
        nonlocal crashed
        fd = original_open(path, flags, *args, **kwargs)
        if not crashed and isinstance(path, str) and path.startswith(".spec-dock-file-"):
            crashed = True
            os.close(fd)
            raise SimulatedProcessCrash
        return fd

    with monkeypatch.context() as fault:
        fault.setattr(managed_distribution.os, "open", crash_after_stage_create)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    parent = target_root / ".github" / "workflows"
    original_remove = managed_distribution._remove_distribution_stage_if_owned
    injected: Path | None = None

    def inject_before_final_backup_unlink(parent_fd, stage_name, created, **kwargs):
        nonlocal injected
        if injected is None and isinstance(stage_name, str) and stage_name.startswith(".spec-dock-backup-"):
            name = ".unknown" if unknown_kind != "unleased-stage" else ".spec-dock-file-unleased"
            injected = parent / name
            if unknown_kind == "symlink":
                injected.symlink_to("third-party")
            elif unknown_kind == "fifo":
                os.mkfifo(injected)
            else:
                injected.write_bytes(b"third-party\n")
        return original_remove(parent_fd, stage_name, created, **kwargs)

    monkeypatch.setattr(
        managed_distribution,
        "_remove_distribution_stage_if_owned",
        inject_before_final_backup_unlink,
    )
    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert injected is not None
    assert result.status == "recovery_required"
    assert result.reason == "journal-precondition-mismatch"
    assert injected.exists() or injected.is_symlink()
    assert not (parent / "ci.yml").exists()


def test_i368_abrupt_swap_requires_exact_post_swap_successor_lease(tmp_path: Path) -> None:
    old = b"old\n"
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset("spec-dock/spec-dock.version", b"1.2.3\n", mode=0o644),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    expected = next(
        item.identity for item in executable.distribution_plan.current_assets if item.path == ".github/workflows/ci.yml"
    )
    stage_name = managed_distribution._new_distribution_stage_name(".github/workflows/ci.yml", expected)
    stage = target.parent / stage_name
    stage.write_bytes(b"desired\n")
    stage.chmod(0o644)
    journal = store.record_staging_lease(
        journal,
        managed_distribution._distribution_stage_ownership(".github/workflows/ci.yml", stage_name, stage.lstat()),
    )
    parent_fd = os.open(target.parent, os.O_RDONLY)
    try:
        managed_distribution._rename_distribution_swap(parent_fd, stage_name, parent_fd, target.name)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "managed staging cleanup failed"
    assert target.read_bytes() == b"desired\n"
    assert stage.read_bytes() == old
    assert store.path.exists()

    current_journal = store.load_for_assessment(assessment, package_version="1.2.3")
    store.record_staging_lease(
        current_journal,
        managed_distribution._distribution_stage_ownership(
            ".github/workflows/ci.yml",
            stage_name,
            target.lstat(),
        ),
    )
    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert retry.status == "completed", retry.reason
    assert not stage.exists()


def test_i368_retry_removes_reserved_quarantine_after_abrupt_prune(tmp_path: Path) -> None:
    old = b"obsolete\n"
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old, mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset("spec-dock/spec-dock.version", b"1.2.3\n", mode=0o644),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    obsolete_identity = dict(executable.distribution_plan.target_snapshots)[".codex/config.toml"].target.identity
    assert obsolete_identity is not None
    quarantine_name = managed_distribution._new_distribution_stage_name(".codex/config.toml", obsolete_identity)
    journal = store.record_staging_lease(
        journal,
        managed_distribution._reserved_distribution_stage_ownership(".codex/config.toml", quarantine_name, "regular"),
    )
    parent_fd = os.open(target.parent, os.O_RDONLY)
    try:
        managed_distribution._rename_distribution_no_replace(parent_fd, target.name, parent_fd, quarantine_name)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert not target.exists()
    assert not (target.parent / quarantine_name).exists()


def test_i368_forward_guard_rejects_reordered_self_rehashed_journal(tmp_path: Path) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    assert len(journal.actions) > 1
    reordered = managed_distribution.replace(journal, actions=tuple(reversed(journal.actions)))
    reordered = managed_distribution.replace(
        reordered,
        plan_digest=managed_distribution._journal_digest(reordered),
    )
    store.write(reordered, predecessor=journal)

    with pytest.raises(DistributionApplyError, match="journal-plan-mismatch"):
        store.resume(executable, package_version="1.2.3")


def test_i368_guard_anchor_rejects_self_rehashed_zero_reservation_journal(tmp_path: Path) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    stage = target_root / Path(action.path).parent / stage_name
    stage.parent.mkdir(parents=True, exist_ok=True)
    if expected.kind == "regular":
        stage.write_bytes(b"syntactically-valid-stage\n")
    else:
        stage.symlink_to(expected.target)

    payload = json.loads(store.path.read_text(encoding="utf-8"))
    forged_lease = {
        "path": action.path,
        "stage_name": stage_name,
        "device": 0,
        "inode": 0,
        "ctime_ns": 0,
        "file_type": expected.kind,
    }
    payload["staging_leases"] = [forged_lease]
    payload["staging_leases_digest"] = managed_distribution._staging_leases_digest(
        operation_id=journal.operation_id,
        leases=[forged_lease],
    )
    store.path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        store.resume(executable, package_version="1.2.3")

    assert stage.exists() or stage.is_symlink()


def test_i368_guard_write_ahead_crash_accepts_exact_journal_predecessor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    original_swap = managed_distribution._rename_distribution_swap
    crashed = False

    def crash_before_journal_swap(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal crashed
        if not crashed and destination_name == store.path.name:
            crashed = True
            raise KeyboardInterrupt("crash after guard write-ahead")
        return original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", crash_before_journal_swap)
    with pytest.raises(KeyboardInterrupt, match="guard write-ahead"):
        store.mark_executing(journal)
    assert crashed is True

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", original_swap)
    retry_store = OperationJournalStore(target_root)
    resumed = retry_store.resume(executable, package_version="1.2.3")
    assert resumed.status == journal.status
    assert retry_store.mark_executing(resumed).status == "executing"


def test_i368_initial_guard_only_crash_reconstructs_exact_prepared_journal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    original_write = OperationJournalStore._write
    crashed = False

    def crash_before_initial_publish(self, journal, *, predecessor=None, require_absent=False):
        nonlocal crashed
        if require_absent and not crashed:
            crashed = True
            raise KeyboardInterrupt("guard-only crash")
        return original_write(
            self,
            journal,
            predecessor=predecessor,
            require_absent=require_absent,
        )

    monkeypatch.setattr(OperationJournalStore, "_write", crash_before_initial_publish)
    with pytest.raises(KeyboardInterrupt, match="guard-only"):
        store.prepare(executable, package_version="1.2.3")
    assert crashed is True
    assert not store.path.exists()
    guard = managed_distribution._read_distribution_retry_marker(target_root)
    assert guard is not None
    assert guard.journal_digest is not None
    assert guard.journal_created_at_ns is not None

    monkeypatch.setattr(OperationJournalStore, "_write", original_write)
    resumed = OperationJournalStore(target_root).prepare(executable, package_version="1.2.3")
    assert resumed.status == "prepared"
    assert resumed.source_sha256 == guard.journal_digest


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i368_prepared_journal_resumes_exact_guard_inherited_stage_lease(
    tmp_path: Path,
    kind: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    action = next(
        item
        for item in executable.actions
        if (expected := managed_distribution._expected_target_identity(executable.distribution_plan, item.path))
        is not None
        and expected.kind == kind
    )
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    stage = target_root / Path(action.path).parent / stage_name
    stage.parent.mkdir(parents=True, exist_ok=True)
    if kind == "regular":
        stage.write_bytes(b"current\n")
        stage.chmod(expected.mode or 0o644)
    else:
        assert expected.target is not None
        stage.symlink_to(expected.target)
    lease = managed_distribution._distribution_stage_ownership(
        action.path,
        stage_name,
        stage.lstat(),
    )
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(
        executable,
        package_version="1.2.3",
        stage_ownership=(lease,),
    )
    store.bind_forward_guard(guard)
    prepared = store.prepare(executable, package_version="1.2.3")
    assert prepared.status == "prepared"
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    resumed = OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert resumed.status == "prepared"
    assert resumed.staging_leases == (lease,)
    assert stage.exists() or stage.is_symlink()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i368_digestless_prepared_journal_rejects_guard_inherited_lease_mismatch(
    tmp_path: Path,
    kind: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    action = next(
        item
        for item in executable.actions
        if (expected := managed_distribution._expected_target_identity(executable.distribution_plan, item.path))
        is not None
        and expected.kind == kind
    )
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    stage = target_root / Path(action.path).parent / stage_name
    stage.parent.mkdir(parents=True, exist_ok=True)
    if kind == "regular":
        stage.write_bytes(b"current\n")
        stage.chmod(expected.mode or 0o644)
    else:
        assert expected.target is not None
        stage.symlink_to(expected.target)
    lease = managed_distribution._distribution_stage_ownership(action.path, stage_name, stage.lstat())
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(
        executable,
        package_version="1.2.3",
        stage_ownership=(lease,),
    )
    store.bind_forward_guard(guard)
    prepared = store.prepare(executable, package_version="1.2.3")
    journal_before = store.path.read_bytes()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker["stage_ownership"][0]["ctime_ns"] += 1
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    marker_before = marker_path.read_bytes()

    with pytest.raises(DistributionApplyError):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert store.path.read_bytes() == journal_before
    assert marker_path.read_bytes() == marker_before
    assert prepared.staging_leases == (lease,)


def test_i368_initial_guard_rejects_self_rehashed_executing_zero_lease_before_mutation(
    tmp_path: Path,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    forged_lease = {
        "path": action.path,
        "stage_name": stage_name,
        "device": 0,
        "inode": 0,
        "ctime_ns": 0,
        "file_type": expected.kind,
    }
    payload["status"] = "executing"
    payload["staging_leases"] = [forged_lease]
    payload["staging_leases_digest"] = managed_distribution._staging_leases_digest(
        operation_id=journal.operation_id,
        leases=[forged_lease],
    )
    store.path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert not (target_root / Path(action.path)).exists()
    assert not (target_root / Path(action.path).parent / stage_name).exists()


def test_i368_digestless_schema_2_guard_migrates_only_exact_initial_journal(
    tmp_path: Path,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    resumed = OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    migrated = managed_distribution._read_distribution_retry_marker(target_root)
    assert migrated is not None
    assert migrated.journal_digest == journal.source_sha256
    assert resumed.source_sha256 == journal.source_sha256


def test_i368_digestless_schema_2_guard_rejects_executing_zero_lease_without_writes(
    tmp_path: Path,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    action = next(item for item in journal.actions if item.action == "create")
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, action.path)
    assert expected is not None
    assert expected.kind == "regular"
    journal = store.record_staging_lease(
        journal,
        managed_distribution._reserved_distribution_stage_ownership(
            action.path,
            managed_distribution._new_distribution_stage_name(action.path, expected),
            "regular",
        ),
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    marker_before = marker_path.read_bytes()
    journal_before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert marker_path.read_bytes() == marker_before
    assert store.path.read_bytes() == journal_before


@pytest.mark.parametrize("mutation", ["omit", "add", "reorder"])
def test_i368_digestless_guard_rejects_forged_initial_created_parent_inventory(
    tmp_path: Path,
    mutation: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    bindings = payload["created_parent_bindings"]
    assert len(bindings) > 1
    if mutation == "omit":
        bindings = bindings[1:]
    elif mutation == "add":
        bindings = [
            *bindings,
            {
                "relative_path": ".forged-parent",
                "exists": False,
                "device": None,
                "inode": None,
                "ctime_ns": None,
                "file_type": None,
                "link_count": None,
            },
        ]
    else:
        bindings = list(reversed(bindings))
    payload["created_parent_bindings"] = bindings
    payload["created_parent_bindings_digest"] = managed_distribution._created_parent_bindings_digest(
        operation_id=journal.operation_id,
        bindings=bindings,
    )
    store.path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    marker_before = marker_path.read_bytes()
    journal_before = store.path.read_bytes()

    with pytest.raises(DistributionApplyError, match="journal-precondition-mismatch"):
        OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert marker_path.read_bytes() == marker_before
    assert store.path.read_bytes() == journal_before


def test_i368_digestless_guard_accepts_initial_inventory_after_owned_parent_mkdir_crash(
    tmp_path: Path,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = _prepare_guarded_journal(store, executable)
    binding = next(item for item in journal.created_parent_bindings if "/" not in item.relative_path)
    (target_root / binding.relative_path).mkdir()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.pop("journal_digest")
    marker.pop("journal_predecessor_digest")
    marker.pop("journal_created_at_ns")
    marker_path.write_text(
        json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    resumed = OperationJournalStore(target_root).resume(executable, package_version="1.2.3")

    assert resumed.status == "prepared"


@pytest.mark.parametrize(
    "legacy_state",
    [
        "dual-link",
        "backup-only",
        "dual-link-stale-ctime",
        "backup-only-stale-ctime",
    ],
)
def test_i368_roleless_backup_fixture_promotes_and_resumes(
    tmp_path: Path,
    legacy_state: str,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target_rel = ".github/workflows/ci.yml"
    target = target_root / target_rel
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    record = next(action for action in journal.actions if action.path == target_rel)
    assert record.action == "upgrade"
    target.write_bytes(desired)
    target.chmod(0o644)
    expected = managed_distribution._expected_target_identity(executable.distribution_plan, target_rel)
    assert expected is not None
    stage_name = managed_distribution._new_distribution_stage_name(target_rel, expected)
    quarantine_name = f"{stage_name}.fixture.remove"
    quarantine = target.parent / quarantine_name
    quarantine.write_bytes(old)
    pre_link_info = quarantine.lstat()
    backup_name = managed_distribution._distribution_quarantine_backup_name(quarantine_name)
    backup = target.parent / backup_name
    os.link(quarantine, backup)
    two_link_info = backup.lstat()
    if legacy_state.startswith("backup-only"):
        quarantine.unlink()
    successor = managed_distribution._distribution_stage_ownership(
        target_rel,
        stage_name,
        target.lstat(),
    )
    if legacy_state == "dual-link-stale-ctime":
        predecessor_info = pre_link_info
    elif legacy_state == "backup-only-stale-ctime":
        predecessor_info = two_link_info
    else:
        predecessor_info = backup.lstat() if legacy_state == "backup-only" else quarantine.lstat()
    predecessor = managed_distribution.DistributionStageOwnership(
        path=target_rel,
        stage_name=quarantine_name,
        device=predecessor_info.st_dev,
        inode=predecessor_info.st_ino,
        ctime_ns=predecessor_info.st_ctime_ns,
        file_type="regular",
        role="predecessor-quarantine",
    )
    journal = store.write(
        managed_distribution.replace(
            journal,
            actions=tuple(
                managed_distribution.replace(action, checkpoint="published") if action.path == target_rel else action
                for action in journal.actions
            ),
            staging_leases=(successor, predecessor),
        ),
        predecessor=journal,
    )
    payload = json.loads(store.path.read_text(encoding="utf-8"))
    for lease in payload["staging_leases"]:
        lease.pop("role", None)
    payload["staging_leases_digest"] = managed_distribution._staging_leases_digest(
        operation_id=journal.operation_id,
        leases=payload["staging_leases"],
    )
    roleless_bytes = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    store.path.write_bytes(roleless_bytes)
    guard = managed_distribution._read_distribution_retry_marker(target_root)
    assert guard is not None
    store.bind_forward_guard(guard)
    guard = store.prepare_legacy_guard(
        None,
        package_version=guard.package_version,
        replace_marker=guard,
        journal_digest=hashlib.sha256(roleless_bytes).hexdigest(),
        journal_predecessor_digest=None,
        journal_created_at_ns=journal.created_at_ns,
    )
    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=guard,
    )

    assert result.status == "completed", result.reason
    assert target.read_bytes() == desired
    assert not backup.exists()
    assert not quarantine.exists()


@pytest.mark.parametrize(
    "record",
    [
        {"path": "/.agents/old", "kind": "regular", "sha256": "a" * 64},
        {"path": "../.agents/old", "kind": "regular", "sha256": "a" * 64},
        {"path": r".agents\\old", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/*", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/old/", "kind": "regular", "sha256": "a" * 64},
        {"path": ".agents/old", "kind": "directory", "sha256": "a" * 64},
        {"path": ".agents/old", "kind": "regular", "sha256": "A" * 64},
        {"path": ".agents/old", "kind": "regular", "sha256": "not-a-digest"},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 63},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": "0644"},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": -1},
        {"path": ".agents/old", "kind": "regular", "sha256": "a" * 64, "mode": 0o100644},
    ],
)
def test_s20_invalid_historical_record_is_rejected(tmp_path: Path, record: dict[str, object]) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[record]),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_duplicate_and_current_obsolete_overlap_are_rejected(tmp_path: Path) -> None:
    duplicate = {
        "path": ".agents/legacy.md",
        "surface": "legacy-test",
        "identities": [_regular_record(".agents/legacy.md", b"legacy\n")],
        "on_unknown": "preserve-and-block",
    }
    duplicate_manifest = _write_manifest(
        tmp_path / "duplicate",
        _manifest_with(obsolete_exact_files=[duplicate, duplicate.copy()]),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=duplicate_manifest)

    overlap_manifest = _write_manifest(
        tmp_path / "overlap",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".agents/skills/spec-dock/SKILL.md",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=overlap_manifest)

    shortcut_overlap_manifest = _write_manifest(
        tmp_path / "shortcut-overlap",
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "spec",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=shortcut_overlap_manifest)


@pytest.mark.parametrize(
    "protected_path",
    (
        "spec-dock/docs/README.md",
        "spec-dock/initiatives/user-owned/requirement.md",
        "spec-dock/active/issue/requirement.md",
        "spec-dock/.workbench/README.md",
    ),
)
def test_s20_protected_workspace_overlap_is_rejected(tmp_path: Path, protected_path: str) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": protected_path,
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )

    with pytest.raises(DistributionManifestError, match="protected workspace surface"):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_physical_current_catalog_cannot_overlap_protected_workspace(tmp_path: Path) -> None:
    install_root = tmp_path / "install_root"
    protected = install_root / "spec-dock/initiatives/user-owned/requirement.md"
    protected.parent.mkdir(parents=True)
    protected.write_text("must remain user-owned\n", encoding="utf-8")
    manifest_path = _write_manifest(tmp_path, _manifest_with())

    with pytest.raises(DistributionManifestError, match="protected workspace surface"):
        build_distribution_plan(install_root, manifest_path=manifest_path)


def test_s20_ancestor_overlap_between_historical_records_is_rejected(tmp_path: Path) -> None:
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[{"path": ".agents/legacy.md", "kind": "regular", "sha256": "a" * 64}],
            obsolete_exact_files=[{"path": ".agents/legacy.md/child", "kind": "regular", "sha256": "b" * 64}],
        ),
    )

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_nested_historical_records_cannot_overlap_current_or_each_other(tmp_path: Path) -> None:
    current_overlap = _write_manifest(
        tmp_path / "current-overlap",
        _manifest_with(
            recognized_workspace_versions=[
                {
                    "version": "0.1.0",
                    "anchors": [
                        {
                            "path": ".agents/skills/spec-dock",
                            "kind": "regular",
                            "sha256": "a" * 64,
                            "source": {"kind": "git-blob", "ref": "old"},
                        }
                    ],
                }
            ]
        ),
    )
    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=current_overlap)

    nested_overlap = _write_manifest(
        tmp_path / "nested-overlap",
        _manifest_with(
            trusted_consumer_manifests=[
                {
                    "path": ".agents/legacy-manifest.json",
                    "kind": "regular",
                    "sha256": "a" * 64,
                    "source": {"kind": "git-blob", "ref": "old"},
                    "claims": [
                        {
                            "path": ".agents/legacy-manifest.json/child",
                            "kind": "regular",
                            "sha256": "b" * 64,
                            "source": {"kind": "git-blob", "ref": "old"},
                        }
                    ],
                }
            ]
        ),
    )
    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=nested_overlap)


def test_s20_historical_schema_requires_all_named_sections(tmp_path: Path) -> None:
    manifest = _manifest_with()
    del manifest["historical_shortcuts"]
    manifest_path = _write_manifest(tmp_path, manifest)

    with pytest.raises(DistributionManifestError):
        build_distribution_plan(INSTALL_ROOT, manifest_path=manifest_path)


def test_s20_scaffold_is_a_source_root_not_a_second_current_catalog(tmp_path: Path) -> None:
    scaffold_root = _minimal_scaffold_root(tmp_path)
    (scaffold_root / "docs" / "README.md").write_text("docs\n", encoding="utf-8")

    plan = build_distribution_plan(
        INSTALL_ROOT,
        manifest_path=MANIFEST_PATH,
        scaffold_root=scaffold_root,
    )

    assert {asset.path for asset in plan.current_assets} == EXPECTED_CURRENT_PATHS
    assert plan.scaffold_root == scaffold_root


def test_s25_fresh_classifies_missing_and_current_identical_without_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    by_path = {action.path: action for action in plan.actions}
    assert by_path[".github/workflows/ci.yml"].action == "adopt"
    assert by_path[".github/workflows/ci.yml"].provenance == "current"
    assert by_path[".github/workflows/ci.yml"].blocked is False
    assert by_path[".github/workflows/ci.yml"].reason == "current-identity-match"
    assert by_path["spec"].action == "create"
    assert by_path[".github"].action == "adopt"
    assert by_path[".github/workflows"].action == "adopt"
    assert by_path["spec-dock"].action == "ensure-directory"
    assert set(by_path) == {
        ".github",
        ".github/workflows",
        ".github/workflows/ci.yml",
        "spec",
        "spec-dock",
        "spec-dock/.agent",
        "spec-dock/initiatives",
    }
    assert target.read_bytes() == b"current\n"


def test_i369_fresh_required_directories_are_top_down_and_non_destructive(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    nested_source = install_root / "zz" / "nested" / "asset.txt"
    nested_source.parent.mkdir(parents=True)
    nested_source.write_bytes(b"nested\n")
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        operation="fresh",
    )

    required_paths = tuple(item.path for item in plan.required_directories)
    assert required_paths == tuple(sorted(required_paths, key=lambda path: (len(Path(path).parts), path)))
    assert required_paths[:3] == (".github", "spec-dock", "zz")
    actions = {action.path: action for action in plan.actions}
    assert all(actions[path].action == "ensure-directory" for path in required_paths)
    assert {action.action for action in plan.actions} <= {"create", "ensure-directory"}
    assert "spec-dock/.workbench/README.md" in actions


def test_i369_required_directory_collisions_are_blocked_without_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / ".github").write_text("user-owned\n", encoding="utf-8")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github")
    assert action.action == "preserve"
    assert action.blocked is True
    assert action.reason == "required-directory-file"
    assert (target_root / ".github").read_text(encoding="utf-8") == "user-owned\n"


def test_i369_fresh_scaffold_seed_uses_template_source_and_update_does_not_backfill(
    tmp_path: Path,
) -> None:
    scaffold_root = _minimal_scaffold_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    install_root = _minimal_install_root(tmp_path)
    fresh = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        operation="fresh",
    )
    fresh_seed = next(asset for asset in fresh.scaffold_assets if asset.path == "spec-dock/.workbench/README.md")
    assert fresh_seed.source_path == "templates/root/.workbench/README.md"

    update = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        operation="update",
    )
    assert all(asset.path != "spec-dock/.workbench/README.md" for asset in update.scaffold_assets)


def test_i369_update_missing_and_empty_workspace_admit_fresh(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    for target_root, create_workspace in (
        (tmp_path / "missing", False),
        (tmp_path / "empty", True),
    ):
        target_root.mkdir()
        if create_workspace:
            (target_root / "spec-dock").mkdir()
        admission = admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )
        assert admission.status == "fresh"
        assert admission.intent == "fresh"


def test_i369_created_fresh_workspace_rejects_foreign_root_child_before_journal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    workspace_info = workspace.stat()
    original_prepare_legacy_guard = OperationJournalStore.prepare_legacy_guard

    def inject_foreign_child(self, plan, **kwargs):
        (self.target_root / "spec-dock" / "foreign").write_text("user\n", encoding="utf-8")
        return original_prepare_legacy_guard(self, plan, **kwargs)

    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", inject_foreign_child)
    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
        created_workspace_identity=(workspace_info.st_dev, workspace_info.st_ino),
    )

    assert result.status == "recovery_required"
    assert result.reason == "journal-parent-mismatch"
    assert (workspace / "foreign").exists()
    assert (workspace / ".distribution-retry.json").exists()
    assert not (workspace / ".distribution-journal.json").exists()

    marker_before_retry = (workspace / ".distribution-retry.json").read_bytes()
    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", original_prepare_legacy_guard)
    retry = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert retry.status == "recovery_required"
    assert retry.reason == "journal-parent-mismatch"
    assert (workspace / ".distribution-retry.json").read_bytes() == marker_before_retry
    assert not (workspace / ".distribution-journal.json").exists()

    (workspace / "foreign").unlink()
    original_prepare = OperationJournalStore.prepare

    def inject_foreign_child_after_guard(self, plan, *, package_version):
        (workspace / "late-foreign").write_text("user\n", encoding="utf-8")
        return original_prepare(self, plan, package_version=package_version)

    monkeypatch.setattr(OperationJournalStore, "prepare", inject_foreign_child_after_guard)
    late_retry = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert late_retry.status == "recovery_required"
    assert late_retry.reason == "journal-precondition-mismatch"
    assert (workspace / "late-foreign").exists()
    assert (workspace / ".distribution-retry.json").read_bytes() == marker_before_retry
    assert not (workspace / ".distribution-journal.json").exists()


def test_i369_existing_required_directory_adopt_checkpoint_retries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    initiatives = target_root / "spec-dock" / "initiatives"
    initiatives.mkdir(parents=True)
    (initiatives / "preserved.md").write_text("history\n", encoding="utf-8")
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_adopt_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec-dock/initiatives" in completed_paths:
            failed = True
            raise DistributionApplyError("injected existing directory checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_adopt_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    assert journal_path.exists()
    assert any(
        item["path"] == "spec-dock/initiatives" and item["checkpoint"] == "published"
        for item in json.loads(journal_path.read_text(encoding="utf-8"))["actions"]
    )

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert (initiatives / "preserved.md").read_text(encoding="utf-8") == "history\n"
    assert not journal_path.exists()


def test_i369_fresh_workbench_hard_link_adopt_checkpoint_retries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    seed_source = scaffold_root / "templates/root/.workbench/README.md"
    seed_target = workspace / ".workbench/README.md"
    seed_target.parent.mkdir()
    seed_target.hardlink_to(seed_source)
    alias = tmp_path / "workbench-seed-alias"
    alias.hardlink_to(seed_target)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_workbench_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec-dock/.workbench/README.md" in completed_paths:
            failed = True
            raise DistributionApplyError("injected Workbench checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_workbench_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = workspace / ".distribution-journal.json"
    assert journal_path.exists()
    assert seed_target.lstat().st_nlink == 3

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert seed_target.lstat().st_nlink == 3
    assert alias.is_file()
    assert not journal_path.exists()


def test_i369_protocol1_adopt_postcondition_journal_retry_compatibility(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    (target_root / "spec-dock").mkdir()
    original_payload = managed_distribution._action_postcondition_payload

    def legacy_payload(plan, action):
        payload = original_payload(plan, action)
        if action.action == "adopt" and payload.get("file_type") != "directory":
            return {key: value for key, value in payload.items() if key not in {"device", "inode", "ctime_ns"}}
        return payload

    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_legacy_adopt_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and ".github/workflows/ci.yml" in completed_paths:
            failed = True
            raise DistributionApplyError("injected protocol-1 journal stop")
        return result

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", legacy_payload)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_legacy_adopt_checkpoint)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    assert first.reason == "injected protocol-1 journal stop"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    adopted = next(item for item in journal["actions"] if item["path"] == ".github/workflows/ci.yml")
    assert adopted["action"] == "adopt"
    assert adopted["checkpoint"] == "published"
    assert all(field not in adopted["postcondition"] for field in ("device", "inode", "ctime_ns"))

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", original_payload)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert target.read_bytes() == b"current\n"
    assert not journal_path.exists()


def test_i369_protocol1_adopt_postcondition_guard_only_migrates_compatibility(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    (target_root / "spec-dock").mkdir()
    original_payload = managed_distribution._action_postcondition_payload

    def legacy_payload(plan, action):
        payload = original_payload(plan, action)
        if action.action == "adopt" and payload.get("file_type") != "directory":
            return {key: value for key, value in payload.items() if key not in {"device", "inode", "ctime_ns"}}
        return payload

    original_prepare = OperationJournalStore.prepare

    def stop_after_legacy_guard(self, plan, *, package_version):
        raise DistributionApplyError("injected protocol-1 guard-only stop")

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", legacy_payload)
    monkeypatch.setattr(OperationJournalStore, "prepare", stop_after_legacy_guard)
    first = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    assert first.reason == "injected protocol-1 guard-only stop"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    marker_path = target_root / "spec-dock/.distribution-retry.json"
    assert not journal_path.exists()
    marker_before = json.loads(marker_path.read_text(encoding="utf-8"))
    assert marker_before["purpose"] == "fresh-journal-forward-only"

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", original_payload)
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)
    second = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert target.read_bytes() == b"current\n"
    assert not journal_path.exists()
    assert not marker_path.exists()


def test_i369_protocol1_fixed_link_count_symlink_journal_retry_compatibility(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec-dock").mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    original_payload = managed_distribution._action_postcondition_payload

    def fixed_link_count_payload(plan, action):
        payload = original_payload(plan, action)
        if action.action == "adopt" and payload.get("file_type") != "directory":
            payload = {**payload, "link_count": 1}
            return {key: value for key, value in payload.items() if key not in {"device", "inode", "ctime_ns"}}
        return payload

    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_shortcut_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec" in completed_paths:
            failed = True
            raise DistributionApplyError("injected fixed-link-count protocol-1 stop")
        return result

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", fixed_link_count_payload)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_shortcut_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    adopted = next(item for item in journal_payload["actions"] if item["path"] == "spec")
    assert adopted["action"] == "adopt"
    assert adopted["postcondition"]["link_count"] == 1
    assert all(field not in adopted["postcondition"] for field in ("device", "inode", "ctime_ns"))

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", original_payload)
    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert shortcut.lstat().st_nlink == 2
    assert alias.is_symlink()
    assert not journal_path.exists()


def test_i369_protocol1_fixed_link_count_symlink_guard_only_migrates_compatibility(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec-dock").mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    original_payload = managed_distribution._action_postcondition_payload

    def fixed_link_count_payload(plan, action):
        payload = original_payload(plan, action)
        if action.action == "adopt" and payload.get("file_type") != "directory":
            payload = {**payload, "link_count": 1}
            return {key: value for key, value in payload.items() if key not in {"device", "inode", "ctime_ns"}}
        return payload

    original_prepare = OperationJournalStore.prepare

    def stop_after_fixed_link_count_guard(self, plan, *, package_version):
        raise DistributionApplyError("injected fixed-link-count guard-only stop")

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", fixed_link_count_payload)
    monkeypatch.setattr(OperationJournalStore, "prepare", stop_after_fixed_link_count_guard)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required", first.reason
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    marker_path = target_root / "spec-dock/.distribution-retry.json"
    assert not journal_path.exists()
    marker_before = json.loads(marker_path.read_text(encoding="utf-8"))
    assert marker_before["purpose"] == "recognized-journal-forward-only"

    monkeypatch.setattr(managed_distribution, "_action_postcondition_payload", original_payload)
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert shortcut.lstat().st_nlink == 2
    assert alias.is_symlink()
    assert not journal_path.exists()
    assert not marker_path.exists()


@pytest.mark.parametrize(
    "phase",
    (
        "managed-scaffold-refreshed",
        "current-external-materialized",
        "obsolete-pruned",
        "post-verified",
        "version-written",
    ),
)
def test_i369_fresh_legacy_later_phase_reassesses_and_converts_without_checkpoint_skip(
    tmp_path: Path,
    phase: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "fresh",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": phase,
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )

    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert not marker_path.exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()
    assert (target_root / "spec-dock" / "spec-dock.version").read_text(encoding="utf-8") == "1.2.3\n"


def test_i369_fresh_schema1_marker_rejects_newer_package_conversion(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    root_info = target_root.stat()
    marker = DistributionRetryMarker(
        operation="fresh",
        package_version="1.2.3",
        target_root=DistributionRootIdentity(device=root_info.st_dev, inode=root_info.st_ino),
        last_completed_phase="preflight-complete",
        purpose="distribution-rerun",
    )
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": marker.operation,
            "package_version": marker.package_version,
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": marker.last_completed_phase,
            "purpose": marker.purpose,
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )

    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.3.0",
        legacy_marker=marker,
    )

    assert result.status == "recovery_required"
    assert result.reason == "legacy-marker-unconvertible"
    assert marker_path.exists()
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i369_fresh_schema1_conversion_preserves_legacy_marker_when_journal_appears(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = workspace / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "fresh",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    legacy_bytes = marker_path.read_bytes()
    original_prepare = OperationJournalStore.prepare

    def publish_raced_journal(self, plan, *, package_version):
        self.path.write_bytes(b"raced journal\n")
        return original_prepare(self, plan, package_version=package_version)

    monkeypatch.setattr(OperationJournalStore, "prepare", publish_raced_journal)
    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert marker_path.read_bytes() == legacy_bytes
    assert (workspace / ".distribution-journal.json").read_bytes() == b"raced journal\n"


def test_i369_fresh_schema1_conversion_restores_marker_after_digest_anchor_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    workspace = target_root / "spec-dock"
    workspace.mkdir(parents=True)
    root_info = target_root.stat()
    marker_path = workspace / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "fresh",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [],
        }),
        encoding="utf-8",
    )
    legacy_bytes = marker_path.read_bytes()
    original_prepare_legacy_guard = OperationJournalStore.prepare_legacy_guard

    def publish_raced_journal_after_anchor(self, plan, **kwargs):
        marker = original_prepare_legacy_guard(self, plan, **kwargs)
        if plan is not None and kwargs.get("replace_marker") is not None and marker.journal_digest is not None:
            marker_path = self.target_root / managed_distribution._DISTRIBUTION_RETRY_MARKER_REL
            payload = json.loads(marker_path.read_text(encoding="utf-8"))
            payload.pop("journal_digest", None)
            payload.pop("journal_predecessor_digest", None)
            payload.pop("journal_created_at_ns", None)
            marker_path.write_text(
                json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            restored = managed_distribution._read_distribution_retry_marker(self.target_root)
            assert restored is not None
            marker = restored
        if plan is None and kwargs.get("journal_digest") is not None:
            self.path.write_bytes(b"raced after digest anchor\n")
        return marker

    monkeypatch.setattr(OperationJournalStore, "prepare_legacy_guard", publish_raced_journal_after_anchor)
    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert result.status == "recovery_required"
    assert result.reason == "dual-recovery-state"
    assert marker_path.read_bytes() == legacy_bytes
    assert (workspace / ".distribution-journal.json").read_bytes() == b"raced after digest anchor\n"


def test_s25_missing_current_target_is_create(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "missing-consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "create"
    assert action.provenance == "missing"
    assert action.blocked is False
    assert not target_root.exists()


def test_s25_uninstall_missing_current_target_is_already_absent(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "missing-consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "prune"
    assert action.provenance == "missing"
    assert action.reason == "already-absent"
    assert action.blocked is False
    assert not target_root.exists()


def test_s25_unknown_current_collision_is_preserved_and_diagnostic_is_sanitized(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    secret = "token=super-secret"
    external_path = "/private/host/private-repository/source.py"
    target.write_text(f"{secret}\n{external_path}\n", encoding="utf-8")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "unknown"
    assert action.blocked is True
    assert action.reason == "unknown-current-collision"
    assert secret not in action.reason
    assert external_path not in action.reason
    diagnostic = action.diagnostic()
    assert diagnostic["path"] == ".github/workflows/ci.yml"
    assert secret not in repr(diagnostic)
    assert external_path not in repr(diagnostic)
    assert "inspect ownership" in str(diagnostic["operator_action"])
    assert target.read_text(encoding="utf-8") == f"{secret}\n{external_path}\n"


def test_s25_preflight_does_not_follow_final_component_swapped_to_symlink(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github/workflows/ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"user-owned\n")
    external = tmp_path / "external.yml"
    external.write_bytes(b"current\n")
    real_open = managed_distribution.os.open
    swapped = False

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal swapped
        if path == "ci.yml" and dir_fd is not None and not swapped:
            swapped = True
            target.unlink()
            target.symlink_to(external)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(managed_distribution.os, "open", swap_before_open)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.blocked
    assert action.reason == "unsafe-target-path"
    assert target.is_symlink()


def test_s25_preflight_does_not_follow_parent_swapped_to_symlink(tmp_path: Path, monkeypatch) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    workflows = target_root / ".github/workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_bytes(b"user-owned\n")
    external = tmp_path / "external-workflows"
    external.mkdir()
    (external / "ci.yml").write_bytes(b"current\n")
    displaced = tmp_path / "displaced-workflows"
    real_open = managed_distribution.os.open
    swapped = False

    def swap_before_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal swapped
        if path == "workflows" and dir_fd is not None and not swapped:
            swapped = True
            workflows.rename(displaced)
            workflows.symlink_to(external, target_is_directory=True)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(managed_distribution.os, "open", swap_before_open)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.blocked
    assert action.reason == "unsafe-target-path"
    assert workflows.is_symlink()


def test_s25_update_upgrades_direct_historical_identity(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False
    assert action.reason == "direct-historical-identity-match"
    assert target.read_bytes() == old


def test_i368_regular_upgrade_restores_replacement_raced_at_atomic_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    replacement = b"user-owned replacement\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_swap = managed_distribution._rename_distribution_swap
    raced = False

    def race_before_first_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal raced
        if destination_name == "ci.yml" and not raced:
            raced = True
            target.unlink()
            target.write_bytes(replacement)
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", race_before_first_swap)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == replacement
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s25_fresh_historical_identity_is_preserved_and_blocked(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "historical"
    assert action.reason == "historical-identity-fresh-preserve"
    assert action.blocked is True
    assert target.read_bytes() == old


def test_s25_trusted_manifest_requires_manifest_and_claim_identity(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_bytes = b'{"managed":true}\n'
    old_target = b"legacy\n"
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes)
    trusted_manifest["claims"] = [_regular_record(".codex/config.toml", old_target, mode=0o644)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            trusted_consumer_manifests=[trusted_manifest],
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ],
        ),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    claim_target = target_root / ".codex" / "config.toml"
    claim_target.parent.mkdir(parents=True)
    claim_target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.provenance == "historical"
    assert action.reason == "trusted-manifest-identity-match"
    assert action.blocked is False


def test_s25_trusted_manifest_can_prove_historical_current_path(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_bytes = b'{"managed":true}\n'
    old_target = b"legacy\n"
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes)
    trusted_manifest["claims"] = [_regular_record(".github/workflows/ci.yml", old_target)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(trusted_consumer_manifests=[trusted_manifest]),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.reason == "trusted-manifest-identity-match"


def test_s55_uninstall_trusted_manifest_requires_envelope_mode_authority(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_bytes = b'{"managed":true}\n'
    old_target = b"legacy\n"
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", manifest_bytes, mode=0o644)
    trusted_manifest.pop("mode")
    trusted_manifest["claims"] = [_regular_record(".codex/config.toml", old_target, mode=0o644)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            trusted_consumer_manifests=[trusted_manifest],
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-test",
                    "identities": [],
                    "on_unknown": "preserve-and-block",
                }
            ],
        ),
    )
    target_root = tmp_path / "consumer"
    manifest_target = target_root / ".agents" / "host-adapters" / "meta.json"
    manifest_target.parent.mkdir(parents=True)
    manifest_target.write_bytes(manifest_bytes)
    claim_target = target_root / ".codex" / "config.toml"
    claim_target.parent.mkdir(parents=True)
    claim_target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "preserve"
    assert action.reason == "obsolete-identity-unknown"
    assert action.blocked is True


@pytest.mark.parametrize("operation", ["update", "init-force"])
def test_s55_obsolete_legacy_identity_remains_compatible_for_non_uninstall(
    tmp_path: Path,
    operation: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    old_target = b"legacy\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "legacy-managed.md",
                    "surface": "legacy-test-surface",
                    "identities": [_regular_record("legacy-managed.md", old_target)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / "legacy-managed.md"
    target_root.mkdir()
    target.write_bytes(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation=operation,  # type: ignore[arg-type]
    )

    action = next(item for item in plan.actions if item.path == "legacy-managed.md")
    assert action.action == "prune"
    assert action.provenance == "historical"
    assert action.reason == "direct-obsolete-identity-match"
    assert action.blocked is False


@pytest.mark.parametrize(
    ("setup", "expected_reason"),
    [
        ("exact-directory", "exact-path-directory"),
        ("exact-symlink", "exact-path-symlink"),
        ("parent-symlink", "symlink-container"),
    ],
)
def test_s25_path_type_collisions_block_before_any_mutation(
    tmp_path: Path,
    setup: str,
    expected_reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    if setup == "exact-directory":
        target.mkdir(parents=True)
    elif setup == "exact-symlink":
        target.parent.mkdir(parents=True)
        target.symlink_to("somewhere")
    else:
        (target_root / ".github").mkdir(parents=True)
        (target_root / "outside").mkdir()
        (target_root / ".github" / "workflows").symlink_to(target_root / "outside")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.blocked is True
    assert action.reason == expected_reason


def test_s25_historical_hard_link_is_blocked_for_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.provenance == "historical"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


@pytest.mark.parametrize("operation", ["fresh", "update", "init-force", "uninstall"])
def test_s25_current_hard_link_is_blocked_for_mutation(
    tmp_path: Path,
    operation: managed_distribution.DistributionOperation,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation=operation,
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "block"
    assert action.provenance == "current"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_i369_required_directory_classification_reuses_captured_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observation = managed_distribution._TargetObservation("missing")

    def fail_reobserve(*_args, **_kwargs):
        raise AssertionError("required directory was observed twice")

    monkeypatch.setattr(managed_distribution, "_observe_target", fail_reobserve)

    action = managed_distribution._classify_required_directory(
        target_root=tmp_path,
        path="spec-dock/initiatives",
        operation="fresh",
        observation=observation,
    )

    assert action.action == "ensure-directory"
    assert action.reason == "required-directory-missing"


def test_s25_current_mode_mismatch_is_preserved_and_blocked_for_uninstall(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.chmod(0o755)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    target.chmod(0o600)
    before = target.read_bytes(), stat.S_IMODE(target.stat().st_mode)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.provenance == "current"
    assert action.reason == "current-mode-mismatch"
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)
    assert (target.read_bytes(), stat.S_IMODE(target.stat().st_mode)) == before


@pytest.mark.parametrize(
    ("operation", "expected_action"),
    [("fresh", "block"), ("update", "adopt"), ("init-force", "adopt"), ("uninstall", "block")],
)
def test_s25_current_hard_linked_shortcut_is_blocked_for_mutation(
    tmp_path: Path,
    operation: managed_distribution.DistributionOperation,
    expected_action: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    assert shortcut.lstat().st_nlink == 2

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation=operation,
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == expected_action
    assert action.provenance == "current"
    if expected_action == "block":
        assert action.reason == "hard-link-mutation-unsafe"
        assert action.blocked is True
    else:
        assert action.reason == "current-identity-match"
        assert action.blocked is False


def test_i369_recognized_symlink_adopt_checkpoint_retry_preserves_link_topology(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec-dock").mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_shortcut_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec" in completed_paths:
            failed = True
            raise DistributionApplyError("injected recognized shortcut checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_shortcut_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    assert journal_path.exists()
    journal_payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert any(item["path"] == "spec" and item["checkpoint"] == "published" for item in journal_payload["actions"])

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", original_checkpoint)
    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "completed", second.reason
    assert shortcut.lstat().st_nlink == 2
    assert alias.is_symlink()
    assert not journal_path.exists()


def test_i369_recognized_adopt_rejects_same_semantics_new_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec-dock").mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    original_checkpoint = OperationJournalStore.checkpoint_published
    failed = False

    def fail_after_shortcut_checkpoint(self, journal, completed_paths):
        nonlocal failed
        result = original_checkpoint(self, journal, completed_paths)
        if not failed and "spec" in completed_paths:
            failed = True
            raise DistributionApplyError("injected recognized shortcut checkpoint failure")
        return result

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", fail_after_shortcut_checkpoint)
    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert first.status == "recovery_required"
    journal_path = target_root / "spec-dock/.distribution-journal.json"
    assert journal_path.exists()
    original_inode = shortcut.lstat().st_ino

    shortcut.unlink()
    shortcut.symlink_to("spec-dock/scripts/spec-dock")
    alias.unlink()
    os.link(shortcut, alias, follow_symlinks=False)
    assert shortcut.lstat().st_ino != original_inode
    assert shortcut.lstat().st_nlink == 2

    second = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert second.status == "recovery_required"
    assert second.reason in {"journal-plan-mismatch", "journal-precondition-mismatch"}
    assert journal_path.exists()
    assert shortcut.is_symlink()
    assert alias.is_symlink()


def test_s25_historical_hard_linked_shortcut_is_blocked_for_update(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": old_target,
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to(old_target)
    alias = target_root / "shortcut-alias"
    os.link(shortcut, alias, follow_symlinks=False)
    assert shortcut.lstat().st_nlink == 2

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "block"
    assert action.provenance == "historical"
    assert action.reason == "hard-link-mutation-unsafe"
    assert action.blocked is True


def test_s25_shortcut_uses_link_identity_without_following_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    shortcut = {
        "path": "spec",
        "kind": "symlink",
        "target": "spec-dock/scripts/spec-dock",
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to("spec-dock/scripts/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "adopt"
    assert action.provenance == "current"
    assert action.blocked is False


def test_s25_update_can_classify_a_proven_historical_shortcut(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_current_identities=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": old_target,
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False
    assert (target_root / "spec").is_symlink()


def test_s25_historical_shortcut_record_proves_canonical_shortcut(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old_target = "legacy/spec-dock"
    shortcut = {
        "path": "spec",
        "kind": "symlink",
        "target": old_target,
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    (target_root / "spec").symlink_to(old_target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == "spec")
    assert action.action == "upgrade"
    assert action.provenance == "historical"
    assert action.blocked is False


def test_s25_noncanonical_historical_shortcut_is_evidence_only(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    shortcut = {
        "path": "legacy-spec",
        "kind": "symlink",
        "target": "legacy/spec-dock",
        "source": {"kind": "test-fixture", "ref": "issue-360-test"},
    }
    manifest_path = _write_manifest(tmp_path, _manifest_with(historical_shortcuts=[shortcut]))
    target_root = tmp_path / "consumer"

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert "legacy-spec" not in {action.path for action in plan.actions}


def test_s30_apply_materializes_missing_regular_target_without_replacing_existing_path(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / ".github" / "workflows").mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    result = apply_distribution_plan(plan)

    assert isinstance(result, DistributionResult)
    assert result.status == "complete"
    target = target_root / ".github" / "workflows" / "ci.yml"
    assert target.read_bytes() == b"current\n"
    assert target.stat().st_nlink == 1


def test_i369_apply_observation_count_scales_linearly_for_adopt_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = tmp_path / "install-root"
    target_root = tmp_path / "consumer"
    for index in range(40):
        relative_path = Path(".github") / "generated" / f"asset-{index:03d}.txt"
        source = install_root / relative_path
        target = target_root / relative_path
        source.parent.mkdir(parents=True, exist_ok=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = f"asset {index}\n".encode()
        source.write_bytes(content)
        target.write_bytes(content)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    real_observe_target = managed_distribution._observe_target
    observation_count = 0

    def counted_observe_target(root: Path, relative_path: str):
        nonlocal observation_count
        observation_count += 1
        return real_observe_target(root, relative_path)

    monkeypatch.setattr(managed_distribution, "_observe_target", counted_observe_target)

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert observation_count <= len(plan.actions) * 4


def test_i369_fresh_checkpoints_are_bounded_by_phase_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    original_checkpoint = OperationJournalStore.checkpoint_published
    checkpoints: list[tuple[str, ...]] = []

    def capture_checkpoint(self, journal, completed_paths):
        checkpoints.append(completed_paths)
        return original_checkpoint(self, journal, completed_paths)

    monkeypatch.setattr(OperationJournalStore, "checkpoint_published", capture_checkpoint)

    result = execute_fresh_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        package_version="1.2.3",
    )

    assert result.status == "completed", result.reason
    assert len(checkpoints) <= 4
    assert any(len(completed_paths) > 1 for completed_paths in checkpoints)


def test_s30_apply_upgrades_historical_regular_target_atomically(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    before_inode = target.stat().st_ino

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert target.read_bytes() == b"new\n"
    assert target.stat().st_ino != before_inode


def test_s25_update_repairs_mode_when_content_is_current(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    source.chmod(0o755)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    target.chmod(0o600)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "upgrade"
    assert action.reason == "current-mode-mismatch"

    apply_distribution_plan(plan)

    assert target.read_bytes() == b"current\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o755


@pytest.mark.parametrize("historical_mode", [None, 0o644])
def test_s55_uninstall_requires_historical_mode_authority(
    tmp_path: Path,
    historical_mode: int | None,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    old = b"legacy\n"
    record = _regular_record(".github/workflows/ci.yml", old, mode=historical_mode)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[record]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    target.chmod(0o755)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "preserve"
    assert action.reason == "unknown-current-collision"
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)
    assert target.read_bytes() == old


def test_s55_obsolete_identity_ownership_requires_mode_match(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    obsolete = tmp_path / "legacy-managed.md"
    obsolete.write_bytes(b"legacy\n")
    obsolete.chmod(0o755)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": "legacy-managed.md",
                    "surface": "legacy-test-surface",
                    "identities": [_regular_record("legacy-managed.md", b"legacy\n", mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / "legacy-managed.md"
    target_root.mkdir()
    target.write_bytes(obsolete.read_bytes())
    target.chmod(0o755)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    action = next(item for item in plan.actions if item.path == "legacy-managed.md")
    assert action.action == "preserve"
    assert action.reason == "obsolete-identity-unknown"
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)
    assert target.exists()


def test_s30_apply_rejects_provider_mode_change_after_plan(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    source = install_root / ".github/workflows/ci.yml"
    source.chmod(0o755)

    with pytest.raises(DistributionApplyError, match="provider Current asset identity changed"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old


def test_s30_apply_rejects_provider_content_change_with_same_planned_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_source = managed_distribution._source_asset_bytes

    def changed_source(path: Path) -> tuple[bytes, managed_distribution.DistributionSourceSnapshot]:
        _content, snapshot = original_source(path)
        return b"unplanned\n", snapshot

    monkeypatch.setattr(managed_distribution, "_source_asset_bytes", changed_source)

    with pytest.raises(DistributionApplyError, match="provider Current asset content changed"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old


def test_s30_apply_retries_cleanup_of_known_stale_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_unlink = managed_distribution.os.unlink

    def fail_stage_cleanup(name, *args, **kwargs):
        if isinstance(name, str) and name.startswith(".spec-dock-file-"):
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan)
    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert target.read_bytes() == b"new\n"

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    stage_ownership = managed_distribution._distribution_stage_ownership(
        ".github/workflows/ci.yml",
        stage_files[0].name,
        stage_files[0].lstat(),
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_rebinds_stage_ownership_after_swap_for_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    failed = False

    def fail_once_after_swap(name, *args, **kwargs):
        nonlocal failed
        if not failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_once_after_swap)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert target.read_bytes() == b"new\n"
    assert len(recorded) == 3
    rebound = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (rebound.device, rebound.inode, rebound.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_recovers_when_rebind_record_and_cleanup_both_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    record_calls = 0
    original_unlink = managed_distribution.os.unlink
    cleanup_failures = 0

    def fail_post_swap_record(record: managed_distribution.DistributionStageOwnership) -> None:
        nonlocal record_calls
        record_calls += 1
        if record_calls == 2:
            raise RuntimeError("simulated post-swap marker write failure")
        recorded.append(record)

    def fail_stage_cleanup_twice(name, *args, **kwargs):
        nonlocal cleanup_failures
        if isinstance(name, str) and name.startswith(".spec-dock-file-") and cleanup_failures < 2:
            cleanup_failures += 1
            raise OSError("simulated repeated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_twice)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=fail_post_swap_record)

    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) == 3
    rebound = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (rebound.device, rebound.inode, rebound.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )
    assert target.read_bytes() == b"new\n"

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_i368_post_swap_same_content_replacement_preserves_displaced_predecessor(
    tmp_path: Path,
) -> None:
    desired = b"new\n"
    old = b"old\n"
    install_root = _minimal_install_root(tmp_path, content=desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    replaced = False

    def replace_canonical_after_successor_record(lease: managed_distribution.DistributionStageOwnership) -> None:
        nonlocal replaced
        recorded.append(lease)
        if replaced or lease.inode == 0 or target.read_bytes() != desired:
            return
        canonical = target.lstat()
        if (canonical.st_dev, canonical.st_ino) != (lease.device, lease.inode):
            return
        replacement = target.with_name("ci.concurrent")
        replacement.write_bytes(desired)
        replacement.chmod(stat.S_IMODE(canonical.st_mode))
        replacement.replace(target)
        replaced = True

    with pytest.raises(DistributionApplyError, match="managed target identity changed"):
        apply_distribution_plan(
            plan,
            stage_ownership_recorder=replace_canonical_after_successor_record,
            write_ahead_stage_reservations=True,
        )

    assert replaced is True
    assert target.read_bytes() == desired
    stages = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stages) == 1
    assert stages[0].read_bytes() == old
    successor = recorded[-1]
    canonical = target.lstat()
    assert (canonical.st_dev, canonical.st_ino) != (successor.device, successor.inode)


def test_s30_apply_cleans_rebound_stage_when_marker_update_fails(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []

    def fail_marker_update(record: managed_distribution.DistributionStageOwnership) -> None:
        if recorded:
            raise RuntimeError("simulated retry marker write failure")
        recorded.append(record)

    with pytest.raises(RuntimeError, match="retry marker write failure"):
        apply_distribution_plan(plan, stage_ownership_recorder=fail_marker_update)

    assert target.read_bytes() == b"new\n"
    assert not list(target.parent.glob(".spec-dock-file-*"))

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )


def test_s30_apply_retries_stage_cleanup_for_trusted_manifest_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    trusted_bytes = b'{"managed":true}\n'
    trusted_manifest = _regular_record(".agents/host-adapters/meta.json", trusted_bytes)
    trusted_manifest["claims"] = [_regular_record(".github/workflows/ci.yml", old)]
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(trusted_consumer_manifests=[trusted_manifest]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    trusted_target = target_root / ".agents" / "host-adapters" / "meta.json"
    trusted_target.parent.mkdir(parents=True)
    trusted_target.write_bytes(trusted_bytes)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert next(item for item in plan.actions if item.path == ".github/workflows/ci.yml").action == "upgrade"
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    failed = False

    def fail_stage_cleanup(name, *args, **kwargs):
        nonlocal failed
        if not failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup)
    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)
    assert list(target.parent.glob(".spec-dock-file-*"))

    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=tuple(recorded),
        ).status
        == "complete"
    )
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_historical_stage_identities_include_recognized_anchor(
    tmp_path: Path,
) -> None:
    old = b"old\n"
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            recognized_workspace_versions=[
                {
                    "version": "0.1.0",
                    "anchors": [_regular_record("legacy.txt", old)],
                }
            ]
        ),
    )
    plan = build_distribution_plan(install_root, manifest_path=manifest_path)

    historical = managed_distribution._historical_stage_identities(plan, "legacy.txt")

    assert historical == (
        managed_distribution.DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(old).hexdigest(),
            mode=None,
        ),
    )


def test_s30_apply_refreshes_snapshots_after_stale_stage_cleanup_for_later_action(
    tmp_path: Path,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    second_source = install_root / ".github" / "workflows" / "second.yml"
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    first_target = target_root / ".github" / "workflows" / "ci.yml"
    first_target.parent.mkdir(parents=True)
    first_target.write_bytes(b"current\n")
    source = install_root / ".github" / "workflows" / "ci.yml"
    stale_identity = managed_distribution.DistributionIdentity(
        kind="regular",
        sha256=hashlib.sha256(b"current\n").hexdigest(),
        mode=stat.S_IMODE(source.stat().st_mode),
    )
    stale_stage = first_target.parent / managed_distribution._distribution_stage_name(
        ".github/workflows/ci.yml",
        stale_identity,
    )
    stale_stage.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    stage_ownership = managed_distribution._distribution_stage_ownership(
        ".github/workflows/ci.yml",
        stale_stage.name,
        stale_stage.lstat(),
    )
    assert (
        apply_distribution_plan(
            plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert first_target.read_bytes() == b"current\n"
    assert (target_root / ".github/workflows/second.yml").read_bytes() == b"second\n"
    assert not list(first_target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_rejects_external_parent_created_after_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"first\n")
    second_source = install_root / "zz" / "second.yml"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    original_apply = managed_distribution._apply_distribution_action
    injected = False

    def apply_then_create_external_parent(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal injected
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not injected and getattr(action, "path", "") == ".github":
            injected = True
            (root / "zz").mkdir()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", apply_then_create_external_parent)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / ".github").is_dir()
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()
    assert not (target_root / "zz" / "second.yml").exists()


def test_s30_apply_rejects_external_nested_parent_after_operation_parent_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"first\n")
    first_source = install_root / "zz" / "first.yml"
    first_source.parent.mkdir(parents=True)
    first_source.write_bytes(b"first nested\n")
    second_source = install_root / "zz" / "yy" / "second.yml"
    second_source.parent.mkdir(parents=True)
    second_source.write_bytes(b"second nested\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    original_apply = managed_distribution._apply_distribution_action
    injected = False

    def apply_then_create_external_nested_parent(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal injected
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not injected and getattr(action, "path", "") == "zz":
            injected = True
            (root / "zz" / "yy").mkdir()

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", apply_then_create_external_nested_parent)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert not (target_root / "zz" / "first.yml").exists()
    assert (target_root / "zz" / "yy").is_dir()
    assert not (target_root / "zz" / "yy" / "second.yml").exists()


def test_s30_apply_upgrade_keeps_target_unchanged_when_staging_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)

    with pytest.raises(DistributionApplyError, match=r"apply failed|staging"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == old
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_records_partial_stage_identity_when_cleanup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_write = managed_distribution._write_fd_bytes
    original_unlink = managed_distribution.os.unlink
    cleanup_failed = False

    def fail_stage_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            cleanup_failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    assert target.read_bytes() == old
    stage_files = list(target.parent.glob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) >= 2
    refreshed = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (refreshed.device, refreshed.inode, refreshed.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", original_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(refreshed,),
        ).status
        == "complete"
    )
    assert target.read_bytes() == b"new\n"
    assert not list(target.parent.glob(".spec-dock-file-*"))


def test_s30_apply_create_cleans_stage_when_staging_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    def fail_staging_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)

    with pytest.raises(DistributionApplyError, match=r"apply failed|staging"):
        apply_distribution_plan(plan)

    assert not list(target_root.rglob(".spec-dock-file-*"))


def test_s30_apply_create_records_partial_stage_identity_when_cleanup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"new\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_write = managed_distribution._write_fd_bytes
    original_unlink = managed_distribution.os.unlink
    cleanup_failed = False

    def fail_stage_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-file-"):
            cleanup_failed = True
            raise OSError("simulated stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    def fail_staging_write(fd: int, *_args: object, **_kwargs: object) -> None:
        os.write(fd, b"partial\n")
        raise OSError("no space left on device")

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", fail_staging_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", fail_stage_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=recorded.append)

    stage_files = list(target_root.rglob(".spec-dock-file-*"))
    assert len(stage_files) == 1
    assert len(recorded) >= 2
    refreshed = recorded[-1]
    stage_stat = stage_files[0].lstat()
    assert (refreshed.device, refreshed.inode, refreshed.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", original_write)
    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(refreshed,),
        ).status
        == "complete"
    )
    assert (target_root / ".github" / "workflows" / "ci.yml").read_bytes() == b"new\n"
    assert not list(target_root.rglob(".spec-dock-file-*"))


def test_s30_apply_prunes_historical_target_without_following_symlink(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"old\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".agents/skills/legacy/SKILL.md",
                    "surface": "legacy-test",
                    "identities": [_regular_record(".agents/skills/legacy/SKILL.md", old, mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".agents" / "skills" / "legacy" / "SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert not target.exists()


def test_s55_apply_prunes_proven_obsolete_target_during_update(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old, mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.provenance == "historical"
    assert action.blocked is False

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert not target.exists()


def test_i368_prune_preserves_replacement_raced_at_final_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    replacement = b"user-owned replacement\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old, mode=0o644)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_rename = managed_distribution._rename_distribution_no_replace
    raced = False
    replacement_identity: tuple[int, int] | None = None
    quarantine_path: Path | None = None

    def race_before_quarantine(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal raced, replacement_identity, quarantine_path
        if source_name == "config.toml" and destination_name.startswith(".spec-dock-file-") and not raced:
            raced = True
            target.unlink()
            target.write_bytes(replacement)
            replacement_info = target.lstat()
            replacement_identity = (replacement_info.st_dev, replacement_info.st_ino)
            quarantine_path = target.parent / destination_name
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", race_before_quarantine)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert raced is True
    assert replacement_identity is not None
    assert quarantine_path is not None
    assert not target.exists() and not target.is_symlink()
    quarantined = quarantine_path.lstat()
    assert (quarantined.st_dev, quarantined.st_ino) == replacement_identity
    assert quarantine_path.read_bytes() == replacement
    assert not list(target.parent.glob(".*.remove"))


def test_s55_mode_mismatch_still_prunes_obsolete_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    record = _regular_record(".codex/config.toml", old)
    record["mode"] = 0o644
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [record],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    target.chmod(0o755)
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == "prune"
    assert action.reason == "direct-obsolete-identity-match"
    assert action.blocked is False
    assert apply_distribution_plan(plan).status == "complete"
    assert not target.exists()


@pytest.mark.parametrize(
    ("target_kind", "expected_reason"),
    [
        ("modified", "obsolete-identity-unknown"),
        ("symlink", "obsolete-identity-unknown"),
        ("directory", "exact-path-directory"),
    ],
)
def test_s55_unknown_or_unsafe_obsolete_target_blocks_before_mutation(
    tmp_path: Path,
    target_kind: str,
    expected_reason: str,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    old = b"legacy-managed\n"
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            obsolete_exact_files=[
                {
                    "path": ".codex/config.toml",
                    "surface": "legacy-codex-surface",
                    "identities": [_regular_record(".codex/config.toml", old)],
                    "on_unknown": "preserve-and-block",
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target = target_root / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    if target_kind == "modified":
        target.write_bytes(b"user-owned\n")
    elif target_kind == "symlink":
        outside = tmp_path / "outside.txt"
        outside.write_bytes(b"outside\n")
        target.symlink_to(outside)
    else:
        target.mkdir()
    before = target_root / ".codex"
    before_snapshot = (
        target.lstat(),
        tuple(sorted(path.relative_to(before).as_posix() for path in before.rglob("*"))),
    )

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    action = next(item for item in plan.actions if item.path == ".codex/config.toml")
    assert action.action == ("block" if target_kind == "directory" else "preserve")
    assert action.reason == expected_reason
    assert action.blocked is True
    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)

    assert target.exists() or target.is_symlink()
    assert (
        target.lstat(),
        tuple(sorted(path.relative_to(before).as_posix() for path in before.rglob("*"))),
    ) == before_snapshot


def test_s30_apply_blocks_root_rebind_before_any_write(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / ".github" / "workflows").mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    target_root.rename(displaced)
    target_root.mkdir()
    sentinel = target_root / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github" / "workflows" / "ci.yml").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_root_rebind_after_preflight_before_parent_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    original_open = managed_distribution._open_distribution_parent_chain
    switched = False

    def switch_root_before_open(
        root: Path,
        relative_path: str,
        *,
        create_missing: bool = False,
        expected_snapshot: DistributionTargetSnapshot | None = None,
        created_parent_bindings: dict[str, PathIdentitySnapshot] | None = None,
        created_parent_recorder: object = None,
    ) -> tuple[int, ...]:
        nonlocal switched
        if not switched:
            switched = True
            root.rename(displaced)
            root.mkdir()
            (root / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
        return original_open(
            root,
            relative_path,
            create_missing=create_missing,
            expected_snapshot=expected_snapshot,
            created_parent_bindings=created_parent_bindings,
            created_parent_recorder=created_parent_recorder,  # type: ignore[arg-type]
        )

    monkeypatch.setattr(managed_distribution, "_open_distribution_parent_chain", switch_root_before_open)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_root_rebind_during_data_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = tmp_path / "displaced-consumer"
    original_write = managed_distribution._write_fd_bytes
    switched = False

    def switch_root_before_write(fd: int, content: bytes, *, before_mutation: object = None) -> None:
        nonlocal switched
        if not switched:
            switched = True
            target_root.rename(displaced)
            target_root.mkdir()
            (target_root / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
        original_write(fd, content, before_mutation=before_mutation)  # type: ignore[arg-type]

    monkeypatch.setattr(managed_distribution, "_write_fd_bytes", switch_root_before_write)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".github").exists()
    assert not (displaced / ".github" / "workflows" / "ci.yml").exists()


def test_s30_apply_blocks_replaced_ancestor_created_by_prior_action(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    extra_source = install_root / ".agents" / "skills" / "legacy" / "SKILL.md"
    extra_source.parent.mkdir(parents=True)
    extra_source.write_bytes(b"legacy\n")
    (extra_source.parent / "README.md").write_bytes(b"legacy-readme\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    original_apply = managed_distribution._apply_distribution_action
    replaced = False

    def replace_created_ancestor(
        current_plan: object,
        root: Path,
        action: object,
        snapshot: object,
        bindings: dict[str, object],
    ) -> None:
        nonlocal replaced
        original_apply(current_plan, root, action, snapshot, bindings)  # type: ignore[arg-type]
        if not replaced and getattr(action, "path", "").startswith(".agents/"):
            ancestor = root / ".agents"
            displaced = root / ".agents-old"
            ancestor.rename(displaced)
            ancestor.mkdir()
            (ancestor / "sentinel.txt").write_text("replacement\n", encoding="utf-8")
            replaced = True

    monkeypatch.setattr(managed_distribution, "_apply_distribution_action", replace_created_ancestor)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert (target_root / ".agents" / "sentinel.txt").read_text(encoding="utf-8") == "replacement\n"
    assert not (target_root / ".agents" / "skills").exists()


def test_s30_apply_blocks_parent_rebind_before_any_write(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    displaced = target_root / ".github" / "workflows-old"
    parent.rename(displaced)
    parent.mkdir()
    sentinel = parent / "sentinel.txt"
    sentinel.write_text("replacement\n", encoding="utf-8")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert sentinel.read_text(encoding="utf-8") == "replacement\n"
    assert not (parent / "ci.yml").exists()
    assert not (displaced / "ci.yml").exists()


def test_s30_apply_blocks_destination_appearance_without_overwrite(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    parent = target_root / ".github" / "workflows"
    parent.mkdir(parents=True)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    target = parent / "ci.yml"
    target.write_bytes(b"user-owned\n")

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == b"user-owned\n"


def test_s30_apply_blocks_hard_link_prune_without_mutation(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"current\n")
    alias = target_root / "alias"
    alias.hardlink_to(target)

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="uninstall",
    )

    with pytest.raises(DistributionApplyError, match="blocked"):
        apply_distribution_plan(plan)

    assert target.read_bytes() == b"current\n"
    assert alias.read_bytes() == b"current\n"


def test_s30_apply_materializes_canonical_shortcut_without_following_target(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    shortcut = target_root / "spec"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"


def test_s30_apply_retries_symlink_create_stage_record_and_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    recorded: list[managed_distribution.DistributionStageOwnership] = []
    original_unlink = managed_distribution.os.unlink
    recorder_failed = False
    cleanup_failed = False

    def record_stage(record: managed_distribution.DistributionStageOwnership) -> None:
        nonlocal recorder_failed
        if record.file_type == "symlink" and record.device != 0 and not recorder_failed:
            recorder_failed = True
            raise OSError("simulated symlink stage recorder failure")
        recorded.append(record)

    def fail_symlink_cleanup_once(name, *args, **kwargs):
        nonlocal cleanup_failed
        if not cleanup_failed and isinstance(name, str) and name.startswith(".spec-dock-symlink-"):
            cleanup_failed = True
            raise OSError("simulated symlink stage cleanup failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_symlink_cleanup_once)

    with pytest.raises(DistributionApplyError, match="staging cleanup"):
        apply_distribution_plan(plan, stage_ownership_recorder=record_stage)

    stage_files = list(target_root.rglob(".spec-dock-symlink-*"))
    assert len(stage_files) == 1
    symlink_record = next(item for item in reversed(recorded) if item.file_type == "symlink" and item.device != 0)
    stage_stat = stage_files[0].lstat()
    assert (symlink_record.device, symlink_record.inode, symlink_record.ctime_ns) == (
        stage_stat.st_dev,
        stage_stat.st_ino,
        stage_stat.st_ctime_ns,
    )

    monkeypatch.setattr(managed_distribution.os, "unlink", original_unlink)
    retry_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    assert (
        apply_distribution_plan(
            retry_plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(symlink_record,),
        ).status
        == "complete"
    )
    shortcut = target_root / "spec"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.rglob(".spec-dock-symlink-*"))


def test_s30_apply_upgrades_canonical_shortcut_with_no_replace_publish(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    result = apply_distribution_plan(plan)

    assert result.status == "complete"
    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def test_s30_apply_retries_cleanup_of_known_stale_symlink_stage(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")
    stale_stage = target_root / managed_distribution._distribution_stage_name(
        "spec",
        managed_distribution.DistributionIdentity(kind="symlink", target="spec-dock/scripts/spec-dock"),
    )
    stale_stage.symlink_to("spec-dock/scripts/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    stage_ownership = managed_distribution._distribution_stage_ownership("spec", stale_stage.name, stale_stage.lstat())
    assert (
        apply_distribution_plan(
            plan,
            allow_stale_stage_cleanup=True,
            stage_ownership=(stage_ownership,),
        ).status
        == "complete"
    )
    assert shortcut.readlink().as_posix() == "spec-dock/scripts/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def test_s30_apply_preserves_unknown_stage_like_sibling(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    unknown = target_root / ".github" / "workflows" / ".spec-dock-file-user"
    unknown.parent.mkdir(parents=True)
    unknown.write_bytes(b"current\n")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert apply_distribution_plan(plan).status == "complete"
    assert unknown.read_bytes() == b"current\n"


def test_s30_apply_ignores_and_preserves_unrecorded_legacy_stage_collision(tmp_path: Path) -> None:
    install_root = _minimal_install_root(tmp_path, content=b"current\n")
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    initial_plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )
    action = next(item for item in initial_plan.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "create"
    expected = next(item.identity for item in initial_plan.current_assets if item.path == action.path)
    stage = target_root / ".github" / "workflows" / managed_distribution._distribution_stage_name(action.path, expected)
    stage.parent.mkdir(parents=True, exist_ok=True)
    stage.write_bytes(b"current\n")
    before = stage.lstat()
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="fresh",
    )

    assert next(item for item in plan.actions if item.path == ".github/workflows/ci.yml").action == "create"
    assert stage.name == managed_distribution._distribution_stage_name(
        action.path,
        next(item.identity for item in plan.current_assets if item.path == action.path),
    )
    assert apply_distribution_plan(plan, allow_stale_stage_cleanup=True).status == "complete"

    after = stage.lstat()
    assert (after.st_dev, after.st_ino, after.st_ctime_ns) == (before.st_dev, before.st_ino, before.st_ctime_ns)
    assert stage.read_bytes() == b"current\n"
    assert (target_root / action.path).read_bytes() == b"current\n"


def test_s30_symlink_upgrade_blocks_before_unlink_without_no_replace_support(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")

    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )

    def unsupported_no_replace() -> tuple[object, int]:
        raise DistributionApplyError("platform lacks required atomic replace support")

    monkeypatch.setattr(
        managed_distribution,
        "_resolve_distribution_swap_rename",
        unsupported_no_replace,
    )

    with pytest.raises(DistributionApplyError, match="atomic replace"):
        apply_distribution_plan(plan)

    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "legacy/spec-dock"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def test_i368_symlink_upgrade_restores_replacement_raced_at_atomic_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(
            historical_shortcuts=[
                {
                    "path": "spec",
                    "kind": "symlink",
                    "target": "legacy/spec-dock",
                    "source": {"kind": "test-fixture", "ref": "issue-360-test"},
                }
            ]
        ),
    )
    target_root = tmp_path / "consumer"
    target_root.mkdir()
    shortcut = target_root / "spec"
    shortcut.symlink_to("legacy/spec-dock")
    plan = build_distribution_plan(
        install_root,
        manifest_path=manifest_path,
        target_root=target_root,
        operation="update",
    )
    original_swap = managed_distribution._rename_distribution_swap
    raced = False

    def race_before_first_swap(
        source_parent_fd: int,
        source_name: str,
        destination_parent_fd: int,
        destination_name: str,
    ) -> None:
        nonlocal raced
        if destination_name == "spec" and not raced:
            raced = True
            shortcut.unlink()
            shortcut.symlink_to("user/owned")
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", race_before_first_swap)

    with pytest.raises(DistributionApplyError, match="identity"):
        apply_distribution_plan(plan)

    assert shortcut.is_symlink()
    assert shortcut.readlink().as_posix() == "user/owned"
    assert not list(target_root.glob(".spec-dock-symlink-*"))


def _s35_version_manifest(tmp_path: Path, *, version: str = "1.2.3") -> Path:
    target_root = tmp_path / "consumer"
    scripts = target_root / "spec-dock" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "spec-dock").write_bytes(b"runtime\n")
    (target_root / "spec-dock" / ".gitignore").write_bytes(b"ignore\n")
    (target_root / "spec-dock" / "spec-dock.version").write_text(f"{version}\n", encoding="ascii")
    manifest = _manifest_with(
        recognized_workspace_versions=[
            {
                "version": version,
                "anchors": [
                    _regular_record("spec-dock/scripts/spec-dock", b"runtime\n"),
                    _regular_record("spec-dock/.gitignore", b"ignore\n"),
                ],
            }
        ]
    )
    return _write_manifest(tmp_path / "manifest", manifest)


def test_s35_admission_accepts_fresh_and_recognized_workspace_without_writes(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    target_root = tmp_path / "consumer"
    before = {path.relative_to(tmp_path): path.read_bytes() for path in target_root.rglob("*") if path.is_file()}

    admission = admit_distribution_operation(
        target_root,
        operation="update",
        package_version="1.2.4",
        manifest_path=manifest_path,
    )

    assert admission.status == "recognized"
    assert admission.target_version == "1.2.3"
    after = {path.relative_to(tmp_path): path.read_bytes() for path in target_root.rglob("*") if path.is_file()}
    assert after == before


@pytest.mark.parametrize(
    ("version_bytes", "reason"),
    [
        (b"1.2.3", "invalid-version"),
        (b"1.2.3\r\n", "invalid-version"),
        (b"\xef\xbb\xbf1.2.3\n", "invalid-version"),
        (b"1.2.3\nextra\n", "invalid-version"),
    ],
)
def test_s35_admission_rejects_noncanonical_version_before_mutation(
    tmp_path: Path,
    version_bytes: bytes,
    reason: str,
) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    version_path = tmp_path / "consumer" / "spec-dock" / "spec-dock.version"
    version_path.write_bytes(version_bytes)
    before = {
        path.relative_to(tmp_path): path.read_bytes() for path in (tmp_path / "consumer").rglob("*") if path.is_file()
    }

    with pytest.raises(DistributionAdmissionError) as exc_info:
        admit_distribution_operation(
            tmp_path / "consumer",
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    assert exc_info.value.reason == reason
    after = {
        path.relative_to(tmp_path): path.read_bytes() for path in (tmp_path / "consumer").rglob("*") if path.is_file()
    }
    assert after == before


def test_s35_admission_rejects_hard_link_and_newer_workspace(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path, version="1.2.4")
    target_root = tmp_path / "consumer"
    version_path = target_root / "spec-dock" / "spec-dock.version"
    external = tmp_path / "external-version"
    external.write_bytes(b"1.2.4\n")
    version_path.unlink()
    version_path.hardlink_to(external)
    with pytest.raises(DistributionAdmissionError, match="hard-link"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.5",
            manifest_path=manifest_path,
        )

    version_path.unlink()
    version_path.write_text("1.2.4\n", encoding="ascii")
    with pytest.raises(DistributionAdmissionError, match="downgrade-blocked"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )


def test_s35_admission_rejects_anchor_mismatch_and_symlink_version(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    target_root = tmp_path / "consumer"
    runtime = target_root / "spec-dock" / "scripts" / "spec-dock"
    runtime.write_bytes(b"edited\n")

    with pytest.raises(DistributionAdmissionError, match="anchor-mismatch"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    version_path = target_root / "spec-dock" / "spec-dock.version"
    version_path.unlink()
    external = tmp_path / "external-version"
    external.write_bytes(b"1.2.3\n")
    version_path.symlink_to(external)
    with pytest.raises(DistributionAdmissionError, match="symlink"):
        admit_distribution_operation(
            target_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )


def test_s35_cross_root_retry_replay_and_dual_marker_are_blocked(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    source_root = tmp_path / "consumer"
    marker = source_root / "spec-dock" / ".distribution-retry.json"
    source_stat = source_root.stat()
    marker.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.4",
            "target_root": {"device": source_stat.st_dev, "inode": source_stat.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
        }),
        encoding="utf-8",
    )
    admission = admit_distribution_operation(
        source_root,
        operation="update",
        package_version="1.2.4",
        manifest_path=manifest_path,
    )
    assert admission.status == "retry"
    replay_root = tmp_path / "replay"
    replay_root.mkdir()
    (replay_root / "spec-dock").mkdir()
    (replay_root / "spec-dock" / ".distribution-retry.json").write_bytes(marker.read_bytes())

    with pytest.raises(DistributionAdmissionError, match="cross-root-replay"):
        admit_distribution_operation(
            replay_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )

    (replay_root / "spec-dock" / ".uninstall-retry.json").write_text(
        json.dumps({"schema_version": 1, "managed_by": "spec-dock", "purpose": "uninstall-rerun"}),
        encoding="utf-8",
    )
    with pytest.raises(DistributionAdmissionError, match="dual-marker"):
        admit_distribution_operation(
            replay_root,
            operation="update",
            package_version="1.2.4",
            manifest_path=manifest_path,
        )


def test_s35_admission_allows_newer_package_for_prewrite_legacy_marker(tmp_path: Path) -> None:
    manifest_path = _s35_version_manifest(tmp_path)
    target_root = tmp_path / "consumer"
    marker = target_root / "spec-dock" / ".distribution-retry.json"
    root_info = target_root.stat()
    marker.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
        }),
        encoding="utf-8",
    )

    admission = admit_distribution_operation(
        target_root,
        operation="update",
        package_version="1.2.4",
        manifest_path=manifest_path,
    )

    assert admission.status == "retry"
    assert admission.marker is not None
    assert admission.marker.package_version == "1.2.3"


def test_s35_legacy_uninstall_marker_remains_admissible_without_version(tmp_path: Path) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    (target_root / "spec-dock" / ".uninstall-retry.json").write_text(
        json.dumps({"schema_version": 1, "managed_by": "spec-dock", "purpose": "uninstall-rerun"}),
        encoding="utf-8",
    )
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())

    admission = admit_distribution_operation(
        target_root,
        operation="uninstall",
        package_version="1.2.3",
        manifest_path=manifest_path,
    )

    assert admission.status == "uninstall-retry"


def test_s35_retry_marker_authority_precedes_empty_workspace_fast_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    manifest_path = _write_manifest(tmp_path / "manifest", _manifest_with())
    monkeypatch.setattr(
        managed_distribution,
        "_read_uninstall_retry_marker_for_admission",
        lambda _target_root: True,
    )

    with pytest.raises(DistributionAdmissionError, match="uninstall-retry-present"):
        admit_distribution_operation(
            target_root,
            operation="fresh",
            package_version="1.2.3",
            manifest_path=manifest_path,
        )


def _i368_minimal_executable(tmp_path: Path):
    install_root = _minimal_install_root(tmp_path)
    manifest_path = _write_manifest(tmp_path, _manifest_with())
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    executable = build_executable_mutation_plan(
        build_workspace_assessment(
            install_root,
            manifest_path=manifest_path,
            target_root=target_root,
            intent="update",
        )
    )
    return target_root, executable


def test_i368_journal_create_revalidates_guard_at_publish_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    store.bind_forward_guard(guard)
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    replacement = guard_path.read_bytes()
    original_rename = managed_distribution._rename_distribution_no_replace
    replaced = False

    def replace_guard_after_precheck(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal replaced
        if not replaced and destination_name == store.path.name:
            guard_path.unlink()
            guard_path.write_bytes(replacement)
            replaced = True
        return original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_guard_after_precheck)

    with pytest.raises(DistributionApplyError, match="dual-recovery-state"):
        store.prepare(executable, package_version="1.2.3")

    assert replaced is True
    assert guard_path.read_bytes() == replacement
    assert not store.path.exists()


def test_i368_journal_swap_revalidates_guard_at_publish_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    prepared = _prepare_guarded_journal(store, executable)
    before = store.path.read_bytes()
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    replacement = guard_path.read_bytes()
    original_swap = managed_distribution._rename_distribution_swap
    replaced = False

    def replace_guard_after_precheck(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal replaced
        if not replaced and destination_name == store.path.name:
            guard_path.unlink()
            guard_path.write_bytes(replacement)
            replaced = True
        return original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", replace_guard_after_precheck)

    with pytest.raises(DistributionApplyError, match="dual-recovery-state"):
        store.mark_executing(prepared)

    assert replaced is True
    assert guard_path.read_bytes() == replacement
    assert store.path.read_bytes() == before


def test_i368_journal_finalization_preserves_quarantine_when_guard_races(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    prepared = _prepare_guarded_journal(store, executable)
    completed = store.write(
        managed_distribution.replace(
            prepared,
            status="completed",
            actions=tuple(managed_distribution.replace(action, checkpoint="verified") for action in prepared.actions),
            created_parent_bindings=(),
        ),
        predecessor=prepared,
    )
    journal_bytes = store.path.read_bytes()
    guard_path = target_root / "spec-dock" / ".distribution-retry.json"
    replacement = guard_path.read_bytes()
    original_rename = managed_distribution._rename_distribution_no_replace
    replaced = False

    def replace_guard_after_journal_quarantine(
        source_parent_fd,
        source_name,
        destination_parent_fd,
        destination_name,
    ):
        nonlocal replaced
        result = original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not replaced and source_name == store.path.name and destination_name.endswith(".remove"):
            guard_path.unlink()
            guard_path.write_bytes(replacement)
            replaced = True
        return result

    monkeypatch.setattr(
        managed_distribution,
        "_rename_distribution_no_replace",
        replace_guard_after_journal_quarantine,
    )

    with pytest.raises(DistributionApplyError, match="journal finalization failed"):
        store.remove_completed(completed)

    assert replaced is True
    assert guard_path.read_bytes() == replacement
    assert not store.path.exists()
    quarantine = tuple(store.path.parent.glob(f".{store.path.name}.*.remove"))
    assert len(quarantine) == 1
    assert quarantine[0].read_bytes() == journal_bytes


@pytest.mark.parametrize("entry", ["journal", "guard"])
def test_i368_published_successor_rejects_same_byte_replacement_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    original_assert = OperationJournalStore._assert_bound_regular_entry
    replaced = False
    expected_name = store.path.name if entry == "journal" else ".distribution-retry.json"
    expected_path = target_root / "spec-dock" / expected_name
    replacement_identity: tuple[int, int] | None = None
    replacement_content: bytes | None = None

    def replace_before_acceptance(
        self,
        parent_fd,
        name,
        held_fd,
        expected_snapshot,
        expected_sha256,
        *,
        identity_error,
    ):
        nonlocal replaced, replacement_identity, replacement_content
        if not replaced and name == expected_name:
            content = managed_distribution._read_fd_bytes(held_fd)
            expected_path.unlink()
            expected_path.write_bytes(content)
            replacement_info = expected_path.lstat()
            replacement_identity = (replacement_info.st_dev, replacement_info.st_ino)
            replacement_content = content
            replaced = True
        return original_assert(
            parent_fd,
            name,
            held_fd,
            expected_snapshot,
            expected_sha256,
            identity_error=identity_error,
        )

    monkeypatch.setattr(OperationJournalStore, "_assert_bound_regular_entry", replace_before_acceptance)

    with pytest.raises(
        DistributionApplyError,
        match=r"journal-precondition-mismatch|legacy-marker-unconvertible",
    ):
        if entry == "journal":
            store.prepare(executable, package_version="1.2.3")
        else:
            store.prepare_legacy_guard(executable, package_version="1.2.3")

    assert replaced is True
    assert replacement_identity is not None
    assert replacement_content is not None
    if entry == "journal":
        assert not expected_path.exists() and not expected_path.is_symlink()
        quarantine_paths = tuple(expected_path.parent.glob(f".{expected_name}.*.remove"))
        assert len(quarantine_paths) == 1
        quarantine_path = quarantine_paths[0]
        quarantined = quarantine_path.lstat()
        assert (quarantined.st_dev, quarantined.st_ino) == replacement_identity
        assert quarantined.st_nlink == 1
        assert quarantine_path.read_bytes() == replacement_content
    else:
        assert expected_path.exists()
        current = expected_path.lstat()
        assert (current.st_dev, current.st_ino) == replacement_identity
        assert expected_path.read_bytes() == replacement_content


@pytest.mark.parametrize("entry", ["journal", "guard"])
@pytest.mark.parametrize("same_bytes", [True, False])
def test_i368_finalization_rejects_replacement_before_authority_reacquisition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    same_bytes: bool,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    guard = store.prepare_legacy_guard(executable, package_version="1.2.3")
    if entry == "journal":
        journal = store.prepare(executable, package_version="1.2.3")
        journal = store.write(
            managed_distribution.replace(
                journal,
                status="completed",
                actions=tuple(
                    managed_distribution.replace(action, checkpoint="verified") for action in journal.actions
                ),
                created_parent_bindings=(),
            ),
            predecessor=journal,
        )
        target = store.path
    else:
        journal = None
        target = target_root / "spec-dock" / ".distribution-retry.json"
    original_open_parent = OperationJournalStore._open_parent
    replacement = target.read_bytes() if same_bytes else b"concurrent replacement\n"
    replaced = False

    def replace_before_stat(self, expected_root, expected_workspace=None):
        nonlocal replaced
        result = original_open_parent(self, expected_root, expected_workspace)
        if not replaced:
            target.unlink()
            target.write_bytes(replacement)
            replaced = True
        return result

    monkeypatch.setattr(OperationJournalStore, "_open_parent", replace_before_stat)

    with pytest.raises(
        DistributionApplyError,
        match=r"journal-precondition-mismatch|legacy-marker-unconvertible",
    ):
        if entry == "journal":
            assert journal is not None
            store.remove_completed(journal)
        else:
            store.remove_legacy_marker(guard)

    assert replaced is True
    assert target.read_bytes() == replacement


def test_i368_legacy_marker_with_exact_partial_stage_converts_and_resumes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset("spec-dock/spec-dock.version", b"1.2.3\n", mode=0o644),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    expected = next(
        item.identity for item in executable.distribution_plan.current_assets if item.path == ".github/workflows/ci.yml"
    )
    stage_name = managed_distribution._new_distribution_stage_name(".github/workflows/ci.yml", expected)
    stage = target.parent / stage_name
    stage.write_bytes(b"partial\n")
    stage_stat = stage.lstat()
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "operation": "update",
                "package_version": "1.2.3",
                "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
                "last_completed_phase": "preflight-complete",
                "purpose": "distribution-rerun",
                "stage_ownership": [
                    {
                        "path": ".github/workflows/ci.yml",
                        "stage_name": stage_name,
                        "device": stage_stat.st_dev,
                        "inode": stage_stat.st_ino,
                        "ctime_ns": stage_stat.st_ctime_ns,
                        "file_type": "regular",
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    marker = managed_distribution._read_distribution_retry_marker(target_root)
    assert marker is not None
    original_prepare = OperationJournalStore.prepare
    interrupted = False

    def interrupt_before_initial_journal(self, plan, *, package_version):
        nonlocal interrupted
        interrupted = True
        raise DistributionApplyError("injected pre-journal interruption")

    monkeypatch.setattr(OperationJournalStore, "prepare", interrupt_before_initial_journal)

    first = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=marker,
    )

    assert first.status == "recovery_required"
    assert interrupted is True
    converted = managed_distribution._read_distribution_retry_marker(target_root)
    assert converted is not None
    assert converted.purpose == "recognized-journal-forward-only"
    assert converted.stage_ownership == marker.stage_ownership
    monkeypatch.setattr(OperationJournalStore, "prepare", original_prepare)

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=converted,
    )

    assert result.status == "completed", result.reason
    assert target.read_bytes() == b"desired\n"
    assert not stage.exists()


def test_i368_legacy_post_swap_stage_converts_as_adopt_cleanup(tmp_path: Path) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(desired)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset("spec-dock/spec-dock.version", b"1.2.3\n", mode=0o644),
        ),
    )
    executable = build_executable_mutation_plan(assessment)
    action = next(item for item in executable.actions if item.path == ".github/workflows/ci.yml")
    assert action.action == "adopt"
    expected = next(item.identity for item in executable.distribution_plan.current_assets if item.path == action.path)
    stage_name = managed_distribution._new_distribution_stage_name(action.path, expected)
    stage = target.parent / stage_name
    stage.write_bytes(old)
    stage_stat = stage.lstat()
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps({
            "schema_version": 1,
            "operation": "update",
            "package_version": "1.2.3",
            "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
            "last_completed_phase": "preflight-complete",
            "purpose": "distribution-rerun",
            "stage_ownership": [
                {
                    "path": action.path,
                    "stage_name": stage_name,
                    "device": stage_stat.st_dev,
                    "inode": stage_stat.st_ino,
                    "ctime_ns": stage_stat.st_ctime_ns,
                    "file_type": "regular",
                }
            ],
        }),
        encoding="utf-8",
    )
    marker = managed_distribution._read_distribution_retry_marker(target_root)
    assert marker is not None

    result = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
        legacy_marker=marker,
    )

    assert result.status == "completed", result.reason
    assert target.read_bytes() == desired
    assert not stage.exists()


def test_i368_checkpoint_rejects_same_bytes_different_inode_create_successor(tmp_path: Path) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, executable))
    record = next(item for item in journal.actions if item.action == "create")
    target = target_root / record.path
    target.parent.mkdir(parents=True, exist_ok=True)
    post_identity = record.postcondition["identity"]
    assert isinstance(post_identity, dict)
    asset = next(asset for asset in executable.distribution_plan.current_assets if asset.path == record.path)
    assert executable.distribution_plan.install_root is not None
    source = executable.distribution_plan.install_root / (asset.source_path or asset.path)
    target.write_bytes(source.read_bytes())
    target.chmod(post_identity["mode"])
    exact_successor = target.lstat()
    lease = managed_distribution._distribution_stage_ownership(
        record.path,
        managed_distribution._new_distribution_stage_name(
            record.path,
            managed_distribution.DistributionIdentity(
                kind="regular",
                sha256=post_identity["sha256"],
                mode=post_identity["mode"],
            ),
        ),
        exact_successor,
    )
    journal = store.record_staging_lease(journal, lease)
    replacement = target.read_bytes()
    target.unlink()
    target.write_bytes(replacement)
    target.chmod(post_identity["mode"])

    with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
        store.checkpoint_published(journal, (record.path,))


def test_i368_checkpoint_revalidates_successor_immediately_before_predecessor_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, build_executable_mutation_plan(assessment)))
    record = next(action for action in journal.actions if action.path == ".github/workflows/ci.yml")
    assert record.action == "upgrade"
    expected = next(
        asset.identity for asset in assessment.distribution_plan.current_assets if asset.path == record.path
    )
    stage_name = managed_distribution._new_distribution_stage_name(record.path, expected)
    stage = target.parent / stage_name
    target.replace(stage)
    target.write_bytes(desired)
    target.chmod(expected.mode or 0o644)
    journal = store.record_staging_lease(
        journal,
        managed_distribution._distribution_stage_ownership(record.path, stage_name, target.lstat()),
    )
    original_rename = managed_distribution._rename_distribution_no_replace
    replacement = b"third-party\n"
    replaced = False

    def replace_successor_after_quarantine(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal replaced
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not replaced and source_name == stage_name and destination_name.endswith(".remove"):
            target.unlink()
            target.write_bytes(replacement)
            replaced = True

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_successor_after_quarantine)

    with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
        store.checkpoint_published(journal, (record.path,))

    assert replaced is True
    assert target.read_bytes() == replacement
    assert stage.read_bytes() == old
    assert store.path.exists()


def test_i368_checkpoint_quarantine_unlink_fault_restores_and_converges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, build_executable_mutation_plan(assessment)))
    record = next(action for action in journal.actions if action.path == ".github/workflows/ci.yml")
    expected = next(
        asset.identity for asset in assessment.distribution_plan.current_assets if asset.path == record.path
    )
    stage_name = managed_distribution._new_distribution_stage_name(record.path, expected)
    stage = target.parent / stage_name
    target.replace(stage)
    target.write_bytes(desired)
    target.chmod(expected.mode or 0o644)
    journal = store.record_staging_lease(
        journal,
        managed_distribution._distribution_stage_ownership(record.path, stage_name, target.lstat()),
    )
    original_unlink = managed_distribution.os.unlink
    failed = False

    def fail_quarantine_unlink_once(name, *args, **kwargs):
        nonlocal failed
        if not failed and isinstance(name, str) and name.startswith(stage_name) and name.endswith(".remove"):
            failed = True
            raise OSError("injected quarantine unlink failure")
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution.os, "unlink", fail_quarantine_unlink_once)

    with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
        store.checkpoint_published(journal, (record.path,))

    assert failed is True
    assert target.read_bytes() == desired
    assert stage.read_bytes() == old
    assert store.path.exists()

    completed = store.checkpoint_published(journal, (record.path,))
    assert not stage.exists()
    assert next(action for action in completed.actions if action.path == record.path).checkpoint == "published"


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize(
    "fault_point",
    [
        "reservation-after",
        "rename-after",
        "exact-before",
        "exact-after",
        "backup-link-after",
        "unlink-before",
        "quarantine-unlink-after",
    ],
)
def test_i368_displaced_quarantine_write_ahead_crash_retry_converges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    fault_point: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    if kind == "regular":
        manifest_path = _write_manifest(
            tmp_path,
            _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", b"old\n")]),
        )
        target_rel = ".github/workflows/ci.yml"
    else:
        manifest_path = _write_manifest(
            tmp_path,
            _manifest_with(
                historical_shortcuts=[
                    {
                        "path": "spec",
                        "kind": "symlink",
                        "target": "legacy/spec-dock",
                        "source": {"kind": "test-fixture", "ref": "issue-368-test"},
                    }
                ]
            ),
        )
        target_rel = "spec"
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if kind == "regular":
        target.write_bytes(b"old\n")
    else:
        target.symlink_to("legacy/spec-dock")

    class SimulatedProcessCrash(BaseException):
        pass

    original_record = OperationJournalStore.record_staging_lease
    original_rename = managed_distribution._rename_distribution_no_replace
    original_link = managed_distribution.os.link
    original_unlink = managed_distribution.os.unlink
    injected = False

    with monkeypatch.context() as faults:

        def crash_during_record(self, journal, lease):
            nonlocal injected
            is_quarantine = lease.path == target_rel and lease.stage_name.endswith(".remove")
            is_reserved = lease.device == lease.inode == lease.ctime_ns == 0
            if is_quarantine and fault_point == "exact-before" and not is_reserved and not injected:
                injected = True
                raise SimulatedProcessCrash
            updated = original_record(self, journal, lease)
            if (
                is_quarantine
                and not injected
                and (
                    (fault_point == "reservation-after" and is_reserved)
                    or (fault_point == "exact-after" and not is_reserved)
                )
            ):
                injected = True
                raise SimulatedProcessCrash
            return updated

        def crash_after_rename(source_parent_fd, source_name, destination_parent_fd, destination_name):
            nonlocal injected
            original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
            if fault_point == "rename-after" and destination_name.endswith(".remove") and not injected:
                injected = True
                raise SimulatedProcessCrash

        def crash_after_backup_link(source_name, destination_name, *args, **kwargs):
            nonlocal injected
            result = original_link(source_name, destination_name, *args, **kwargs)
            if (
                fault_point == "backup-link-after"
                and isinstance(destination_name, str)
                and destination_name.startswith(".spec-dock-backup-")
                and not injected
            ):
                injected = True
                raise SimulatedProcessCrash
            return result

        def crash_before_unlink(name, *args, **kwargs):
            nonlocal injected
            if fault_point == "unlink-before" and isinstance(name, str) and name.endswith(".remove") and not injected:
                injected = True
                raise SimulatedProcessCrash
            result = original_unlink(name, *args, **kwargs)
            if (
                fault_point == "quarantine-unlink-after"
                and isinstance(name, str)
                and name.endswith(".remove")
                and not injected
            ):
                injected = True
                raise SimulatedProcessCrash
            return result

        faults.setattr(OperationJournalStore, "record_staging_lease", crash_during_record)
        faults.setattr(managed_distribution, "_rename_distribution_no_replace", crash_after_rename)
        faults.setattr(managed_distribution.os, "link", crash_after_backup_link)
        faults.setattr(managed_distribution.os, "unlink", crash_before_unlink)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

        assert injected is True
        crashed_payload = json.loads(
            (target_root / "spec-dock" / ".distribution-journal.json").read_text(encoding="utf-8")
        )
        crashed_roles = {
            lease.get("role", "stage") for lease in crashed_payload["staging_leases"] if lease["path"] == target_rel
        }
        assert "predecessor-quarantine" in crashed_roles
        if fault_point in {"unlink-before", "quarantine-unlink-after"}:
            assert {"backup-dual", "backup-only-reserved"} <= crashed_roles
            backup_lease = next(
                lease
                for lease in crashed_payload["staging_leases"]
                if lease.get("role") == "backup-dual" and lease["path"] == target_rel
            )
            assert backup_lease["stage_name"].startswith(".spec-dock-backup-")
        elif fault_point == "backup-link-after":
            assert "backup-reserved" in crashed_roles
        retry = execute_recognized_distribution(
            install_root,
            manifest_path=manifest_path,
            scaffold_root=scaffold_root,
            target_root=target_root,
            intent="update",
            package_version="1.2.3",
        )

    assert retry.status == "completed", retry.reason
    if kind == "regular":
        assert target.read_bytes() == b"desired\n"
    else:
        assert target.readlink() == Path("spec-dock/scripts/spec-dock")
    assert not list(target.parent.glob("*.remove"))
    assert not (target_root / "spec-dock" / ".distribution-journal.json").exists()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i368_reserved_displaced_quarantine_mismatch_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    install_root = _minimal_install_root(tmp_path, b"desired\n")
    if kind == "regular":
        manifest_path = _write_manifest(
            tmp_path,
            _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", b"old\n")]),
        )
        target_rel = ".github/workflows/ci.yml"
    else:
        manifest_path = _write_manifest(
            tmp_path,
            _manifest_with(
                historical_shortcuts=[
                    {
                        "path": "spec",
                        "kind": "symlink",
                        "target": "legacy/spec-dock",
                        "source": {"kind": "test-fixture", "ref": "issue-368-test"},
                    }
                ]
            ),
        )
        target_rel = "spec"
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if kind == "regular":
        target.write_bytes(b"old\n")
    else:
        target.symlink_to("legacy/spec-dock")

    class SimulatedProcessCrash(BaseException):
        pass

    original_rename = managed_distribution._rename_distribution_no_replace
    injected = False

    def crash_after_quarantine_rename(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal injected
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if destination_name.endswith(".remove") and not injected:
            injected = True
            raise SimulatedProcessCrash

    with monkeypatch.context() as faults:
        faults.setattr(managed_distribution, "_rename_distribution_no_replace", crash_after_quarantine_rename)
        with pytest.raises(SimulatedProcessCrash):
            execute_recognized_distribution(
                install_root,
                manifest_path=manifest_path,
                scaffold_root=scaffold_root,
                target_root=target_root,
                intent="update",
                package_version="1.2.3",
            )

    quarantine = next(target.parent.glob("*.remove"))
    quarantine.unlink()
    if kind == "regular":
        quarantine.write_bytes(b"third-party\n")
    else:
        quarantine.symlink_to("third-party-target")

    retry = execute_recognized_distribution(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        package_version="1.2.3",
    )

    assert retry.status == "recovery_required"
    assert retry.reason == "managed staging cleanup failed"
    if kind == "regular":
        assert target.read_bytes() == b"desired\n"
        assert quarantine.read_bytes() == b"third-party\n"
    else:
        assert target.readlink() == Path("spec-dock/scripts/spec-dock")
        assert quarantine.readlink() == Path("third-party-target")
    assert (target_root / "spec-dock" / ".distribution-journal.json").exists()


def test_i368_checkpoint_rejects_same_inode_successor_mutate_restore(
    tmp_path: Path,
) -> None:
    old = b"old\n"
    desired = b"desired\n"
    install_root = _minimal_install_root(tmp_path, desired)
    manifest_path = _write_manifest(
        tmp_path,
        _manifest_with(historical_current_identities=[_regular_record(".github/workflows/ci.yml", old)]),
    )
    scaffold_root = _minimal_scaffold_root(tmp_path)
    target_root = tmp_path / "consumer"
    (target_root / "spec-dock").mkdir(parents=True)
    target = target_root / ".github" / "workflows" / "ci.yml"
    target.parent.mkdir(parents=True)
    target.write_bytes(old)
    assessment = build_workspace_assessment(
        install_root,
        manifest_path=manifest_path,
        scaffold_root=scaffold_root,
        target_root=target_root,
        intent="update",
        generated_assets=(
            managed_distribution._generated_regular_asset(
                "spec-dock/spec-dock.version",
                b"1.2.3\n",
                mode=0o644,
            ),
        ),
    )
    store = OperationJournalStore(target_root)
    journal = store.mark_executing(_prepare_guarded_journal(store, build_executable_mutation_plan(assessment)))
    record = next(action for action in journal.actions if action.path == ".github/workflows/ci.yml")
    expected = next(
        asset.identity for asset in assessment.distribution_plan.current_assets if asset.path == record.path
    )
    stage_name = managed_distribution._new_distribution_stage_name(record.path, expected)
    stage = target.parent / stage_name
    target.replace(stage)
    target.write_bytes(desired)
    target.chmod(expected.mode or 0o644)
    successor_before = target.lstat()
    journal = store.record_staging_lease(
        journal,
        managed_distribution._distribution_stage_ownership(record.path, stage_name, successor_before),
    )
    with target.open("r+b") as stream:
        stream.write(b"tampered")
        stream.flush()
        os.fsync(stream.fileno())
        stream.seek(0)
        stream.write(desired)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
    successor_after = target.lstat()
    assert successor_after.st_ino == successor_before.st_ino
    assert successor_after.st_ctime_ns != successor_before.st_ctime_ns
    assert target.read_bytes() == desired

    with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
        store.checkpoint_published(journal, (record.path,))

    assert target.read_bytes() == desired
    assert stage.read_bytes() == old
    assert store.path.exists()


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i368_displaced_cleanup_revalidates_both_namespace_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    parent = tmp_path / kind
    parent.mkdir()
    target = parent / "target"
    stage = parent / "stage"
    if kind == "regular":
        target.write_bytes(b"desired\n")
        stage.write_bytes(b"old\n")
        successor_identity = DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(b"desired\n").hexdigest(),
            mode=stat.S_IMODE(target.lstat().st_mode),
        )
        predecessor_identity = DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(b"old\n").hexdigest(),
            mode=stat.S_IMODE(stage.lstat().st_mode),
        )
    else:
        target.symlink_to("desired-target")
        stage.symlink_to("old-target")
        successor_identity = DistributionIdentity(kind="symlink", target="desired-target")
        predecessor_identity = DistributionIdentity(kind="symlink", target="old-target")
    successor = managed_distribution._distribution_stage_ownership("target", stage.name, target.lstat())
    predecessor = stage.lstat()
    original_rename = managed_distribution._rename_distribution_no_replace
    replaced = False

    def replace_successor_after_quarantine(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal replaced
        original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not replaced and source_name == stage.name and destination_name.endswith(".remove"):
            target.unlink()
            if kind == "regular":
                target.write_bytes(b"third-party\n")
            else:
                target.symlink_to("third-party-target")
            replaced = True

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_successor_after_quarantine)
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
            managed_distribution._remove_distribution_stage_if_owned(
                parent_fd,
                stage.name,
                predecessor,
                strict=True,
                transition_path="target",
                canonical_name=target.name,
                canonical_ownership=successor,
                canonical_condition={
                    "identity": managed_distribution._distribution_identity_payload(successor_identity)
                },
                stage_condition={
                    "device": predecessor.st_dev,
                    "inode": predecessor.st_ino,
                    "file_type": managed_distribution._file_type(predecessor.st_mode),
                    "link_count": predecessor.st_nlink,
                    "identity": managed_distribution._distribution_identity_payload(predecessor_identity),
                },
            )
    finally:
        os.close(parent_fd)

    assert replaced is True
    assert stage.exists() or stage.is_symlink()
    if kind == "regular":
        assert target.read_bytes() == b"third-party\n"
        assert stage.read_bytes() == b"old\n"
    else:
        assert target.readlink() == Path("third-party-target")
        assert stage.readlink() == Path("old-target")


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("race_point", ["after-final-stat", "post-unlink-canonical"])
def test_i368_quarantine_backup_preserves_replacement_and_restores_predecessor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    race_point: str,
) -> None:
    parent = tmp_path / f"{kind}-{race_point}"
    parent.mkdir()
    target = parent / "target"
    stage = parent / "stage"
    if kind == "regular":
        target.write_bytes(b"desired\n")
        stage.write_bytes(b"old\n")
        successor_identity = DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(b"desired\n").hexdigest(),
            mode=stat.S_IMODE(target.lstat().st_mode),
        )
        predecessor_identity = DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(b"old\n").hexdigest(),
            mode=stat.S_IMODE(stage.lstat().st_mode),
        )
    else:
        target.symlink_to("desired-target")
        stage.symlink_to("old-target")
        successor_identity = DistributionIdentity(kind="symlink", target="desired-target")
        predecessor_identity = DistributionIdentity(kind="symlink", target="old-target")
    successor = managed_distribution._distribution_stage_ownership("target", stage.name, target.lstat())
    predecessor = stage.lstat()
    original_stat = managed_distribution.os.stat
    original_unlink = managed_distribution.os.unlink
    replaced = False

    def install_third_party(path: Path) -> None:
        nonlocal replaced
        path.unlink(missing_ok=True)
        if kind == "regular":
            path.write_bytes(b"third-party\n")
        else:
            path.symlink_to("third-party-target")
        replaced = True

    def replace_quarantine_after_final_stat(name, *args, **kwargs):
        result = original_stat(name, *args, **kwargs)
        if (
            race_point == "after-final-stat"
            and not replaced
            and isinstance(name, str)
            and name.endswith(".remove")
            and (
                (parent / managed_distribution._distribution_quarantine_backup_name(name)).exists()
                or (parent / managed_distribution._distribution_quarantine_backup_name(name)).is_symlink()
            )
        ):
            install_third_party(parent / name)
        return result

    def replace_canonical_after_quarantine_unlink(name, *args, **kwargs):
        result = original_unlink(name, *args, **kwargs)
        if (
            race_point == "post-unlink-canonical"
            and not replaced
            and isinstance(name, str)
            and name.endswith(".remove")
        ):
            install_third_party(target)
        return result

    monkeypatch.setattr(managed_distribution.os, "stat", replace_quarantine_after_final_stat)
    monkeypatch.setattr(managed_distribution.os, "unlink", replace_canonical_after_quarantine_unlink)
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError, match="managed staging cleanup failed"):
            managed_distribution._remove_distribution_stage_if_owned(
                parent_fd,
                stage.name,
                predecessor,
                strict=True,
                transition_path="target",
                canonical_name=target.name,
                canonical_ownership=successor,
                canonical_condition={
                    "identity": managed_distribution._distribution_identity_payload(successor_identity)
                },
                stage_condition={
                    "device": predecessor.st_dev,
                    "inode": predecessor.st_ino,
                    "file_type": managed_distribution._file_type(predecessor.st_mode),
                    "link_count": predecessor.st_nlink,
                    "identity": managed_distribution._distribution_identity_payload(predecessor_identity),
                },
            )
    finally:
        os.close(parent_fd)

    assert replaced is True
    assert stage.exists() or stage.is_symlink()
    if kind == "regular":
        assert stage.read_bytes() == b"old\n"
        replacement_path = target if race_point == "post-unlink-canonical" else next(parent.glob("*.remove"))
        assert replacement_path.read_bytes() == b"third-party\n"
    else:
        assert stage.readlink() == Path("old-target")
        replacement_path = target if race_point == "post-unlink-canonical" else next(parent.glob("*.remove"))
        assert replacement_path.readlink() == Path("third-party-target")


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("race", ["replacement", "unknown-child"])
def test_i368_final_gc_preserves_exact_source_across_delete_interposition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    race: str,
) -> None:
    parent = tmp_path / f"{kind}-{race}"
    parent.mkdir()
    stage = parent / "stage"
    if kind == "regular":
        stage.write_bytes(b"owned\n")
    else:
        stage.symlink_to("owned-target")
    created = stage.lstat()
    leases: list[DistributionStageOwnership] = []
    original_stat = managed_distribution.os.stat
    injected = False
    unknown = parent / "unknown-child"

    def interpose_after_final_gc_stat(name, *args, **kwargs):
        nonlocal injected
        result = original_stat(name, *args, **kwargs)
        if (
            not injected
            and isinstance(name, str)
            and name.endswith(".gc")
            and any(lease.role == "gc-exact" and lease.stage_name == name for lease in leases)
        ):
            injected = True
            if race == "replacement":
                (parent / name).unlink()
                if kind == "regular":
                    (parent / name).write_bytes(b"third-party\n")
                else:
                    (parent / name).symlink_to("third-party-target")
            else:
                unknown.write_bytes(b"third-party\n")
        return result

    def validate_namespace() -> None:
        if unknown.exists():
            raise DistributionApplyError("journal-precondition-mismatch")

    monkeypatch.setattr(managed_distribution.os, "stat", interpose_after_final_gc_stat)
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError):
            managed_distribution._remove_distribution_stage_if_owned(
                parent_fd,
                stage.name,
                created,
                strict=True,
                mutation_validator=validate_namespace,
                gc_path="managed/target",
                gc_recorder=leases.append,
            )
    finally:
        os.close(parent_fd)

    assert injected is True
    gc_name = next(lease.stage_name for lease in leases if lease.role == "gc-exact")
    gc = parent / gc_name
    if race == "replacement":
        if kind == "regular":
            assert gc.read_bytes() == b"third-party\n"
        else:
            assert gc.readlink() == Path("third-party-target")
    else:
        assert unknown.read_bytes() == b"third-party\n"
    owned_candidates = [path for path in (stage, gc) if path.exists() or path.is_symlink()]
    assert owned_candidates
    if kind == "regular":
        assert any(path.read_bytes() == b"owned\n" for path in owned_candidates)
    else:
        assert any(path.readlink() == Path("owned-target") for path in owned_candidates)


@pytest.mark.parametrize("kind", ["regular", "symlink"])
@pytest.mark.parametrize("race", ["replacement", "unknown-child"])
def test_i368_final_retained_witness_is_not_unlinked_after_authority_interposition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    race: str,
) -> None:
    parent = tmp_path / f"final-{kind}-{race}"
    parent.mkdir()
    stage = parent / "stage"
    if kind == "regular":
        stage.write_bytes(b"owned\n")
    else:
        stage.symlink_to("owned-target")
    created = stage.lstat()
    leases: list[DistributionStageOwnership] = []
    original_rename = managed_distribution._rename_distribution_no_replace
    injected = False
    unknown = parent / "unknown-child"

    def interpose_before_retained_transition(source_fd, source_name, destination_fd, destination_name):
        nonlocal injected
        if not injected and source_name == stage.name and any(lease.role == "backup-dual" for lease in leases):
            injected = True
            if race == "replacement":
                stage.unlink()
                if kind == "regular":
                    stage.write_bytes(b"third-party\n")
                else:
                    stage.symlink_to("third-party-target")
            else:
                unknown.write_bytes(b"third-party\n")
        return original_rename(source_fd, source_name, destination_fd, destination_name)

    def validate_namespace() -> None:
        if unknown.exists():
            raise DistributionApplyError("journal-precondition-mismatch")

    monkeypatch.setattr(
        managed_distribution,
        "_rename_distribution_no_replace",
        interpose_before_retained_transition,
    )
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError):
            managed_distribution._remove_distribution_stage_if_owned(
                parent_fd,
                stage.name,
                created,
                strict=True,
                mutation_validator=validate_namespace,
                gc_path="managed/target",
                gc_recorder=leases.append,
            )
    finally:
        os.close(parent_fd)

    assert injected is True
    if race == "replacement":
        if kind == "regular":
            assert stage.read_bytes() == b"third-party\n"
        else:
            assert stage.readlink() == Path("third-party-target")
    else:
        assert unknown.read_bytes() == b"third-party\n"
    owned = [path for path in parent.iterdir() if path.name != unknown.name and (path.exists() or path.is_symlink())]
    if kind == "regular":
        assert any(path.read_bytes() == b"owned\n" for path in owned)
    else:
        assert any(path.readlink() == Path("owned-target") for path in owned)


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i371_generic_stage_default_keeps_issue370_restore(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    """Non-Issue-371 callers retain the historical generic stage rollback."""

    parent = tmp_path / f"default-{kind}"
    parent.mkdir()
    stage = parent / "stage"
    aside = parent / "operation-owned-aside"
    if kind == "regular":
        stage.write_bytes(b"owned\n")
    else:
        stage.symlink_to("owned-target")
    created = stage.lstat()
    original_rename = managed_distribution._rename_distribution_no_replace
    original_restore = managed_distribution._restore_distribution_quarantine
    restore_attempts = 0
    injected = False
    foreign_path: Path | None = None

    def replace_first_gc_after_rename(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal injected, foreign_path
        result = original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not injected and source_name == stage.name and destination_name.endswith(".gc"):
            foreign_path = parent / destination_name
            (parent / destination_name).rename(aside)
            if kind == "regular":
                foreign_path.write_bytes(b"foreign\n")
            else:
                foreign_path.symlink_to("foreign-target")
            injected = True
        return result

    def observe_restore(*args, **kwargs):
        nonlocal restore_attempts
        restore_attempts += 1
        return original_restore(*args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", replace_first_gc_after_rename)
    monkeypatch.setattr(managed_distribution, "_restore_distribution_quarantine", observe_restore)
    parent_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        with pytest.raises(DistributionApplyError, match="identity"):
            managed_distribution._remove_distribution_stage_if_owned(parent_fd, stage.name, created, strict=True)
    finally:
        os.close(parent_fd)

    assert injected is True
    assert restore_attempts == 1
    assert foreign_path is not None
    if kind == "regular":
        assert stage.read_bytes() == b"foreign\n"
        assert aside.read_bytes() == b"owned\n"
    else:
        assert stage.readlink() == Path("foreign-target")
        assert aside.readlink() == Path("owned-target")


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
@pytest.mark.parametrize("foreign_kind", ["regular", "symlink"])
def test_i371_destructive_metadata_success_path_does_not_mutate_foreign_rebind(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
    foreign_kind: str,
) -> None:
    """Destructive metadata cleanup must not enter the generic multi-stage GC path."""

    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    metadata_path = guard_path if entry == "guard" else journal_path
    parent = metadata_path.parent
    foreign_source = parent / f"foreign-{foreign_kind}"
    if foreign_kind == "regular":
        foreign_source.write_bytes(b"foreign\n")
    else:
        foreign_source.symlink_to("foreign-target")
    foreign_before = (
        foreign_source.lstat().st_dev,
        foreign_source.lstat().st_ino,
        foreign_source.lstat().st_mode,
        foreign_source.lstat().st_nlink,
        foreign_source.read_bytes() if foreign_kind == "regular" else str(foreign_source.readlink()),
    )
    original_rename = managed_distribution._rename_distribution_no_replace
    original_link = managed_distribution.os.link
    original_unlink = managed_distribution.os.unlink
    rename_calls: list[tuple[str, str]] = []
    link_calls: list[str] = []
    unlink_calls: list[str] = []
    injected = False
    operation_owned_aside: Path | None = None

    def interpose_first_gc_to_delete(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal injected, operation_owned_aside
        result = original_rename(source_parent_fd, source_name, destination_parent_fd, destination_name)
        rename_calls.append((source_name, destination_name))
        if not injected and source_name.endswith(".gc") and destination_name.endswith(".gc"):
            operation_owned_aside = parent / f"operation-owned-{entry}-aside"
            (parent / destination_name).rename(operation_owned_aside)
            foreign_source.rename(parent / destination_name)
            injected = True
        return result

    def observe_link(source, destination, *args, **kwargs):
        link_calls.append(str(destination))
        return original_link(source, destination, *args, **kwargs)

    def observe_unlink(name, *args, **kwargs):
        if isinstance(name, str):
            unlink_calls.append(name)
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(managed_distribution, "_rename_distribution_no_replace", interpose_first_gc_to_delete)
    monkeypatch.setattr(managed_distribution.os, "link", observe_link)
    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    if entry == "guard":
        store.remove_legacy_marker(marker)
    else:
        store.discard_prepared(prepared)

    assert injected is False
    assert rename_calls == []
    assert link_calls == []
    assert unlink_calls == [metadata_path.name]
    assert not metadata_path.exists() and not metadata_path.is_symlink()
    current_foreign = foreign_source.lstat()
    assert (
        current_foreign.st_dev,
        current_foreign.st_ino,
        current_foreign.st_mode,
        current_foreign.st_nlink,
        foreign_source.read_bytes() if foreign_kind == "regular" else str(foreign_source.readlink()),
    ) == foreign_before
    assert operation_owned_aside is None


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
@pytest.mark.parametrize("foreign_kind", ["regular", "symlink"])
def test_i371_destructive_metadata_final_check_rejects_pre_delete_rebind(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
    foreign_kind: str,
) -> None:
    """A pathname rebound by the pre-delete callback is never unlinked."""

    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    metadata_path = guard_path if entry == "guard" else journal_path
    metadata_bytes = metadata_path.read_bytes()
    parent = metadata_path.parent
    aside = parent / f"{metadata_path.name}.owned-aside"
    foreign_source = parent / f"foreign-{foreign_kind}"
    foreign_target = parent / "foreign-target"
    if foreign_kind == "regular":
        foreign_source.write_bytes(b"foreign metadata\n")
    else:
        foreign_target.write_bytes(b"foreign target\n")
        foreign_source.symlink_to(foreign_target.name)
    foreign_before = foreign_source.lstat()
    foreign_payload = foreign_source.read_bytes() if foreign_kind == "regular" else foreign_source.readlink()
    original_assert = OperationJournalStore._assert_destructive_recovery_metadata_bound
    original_unlink = managed_distribution.os.unlink
    checks = 0
    unlink_calls: list[str] = []

    def rebind_after_pre_delete_check(self, expected_root):
        nonlocal checks
        result = original_assert(self, expected_root)
        checks += 1
        if checks == 2:
            metadata_path.rename(aside)
            foreign_source.rename(metadata_path)
        return result

    def observe_unlink(name, *args, **kwargs):
        if isinstance(name, str):
            unlink_calls.append(name)
        return original_unlink(name, *args, **kwargs)

    monkeypatch.setattr(
        OperationJournalStore,
        "_assert_destructive_recovery_metadata_bound",
        rebind_after_pre_delete_check,
    )
    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    operation = (
        (lambda: store.remove_legacy_marker(marker)) if entry == "guard" else (lambda: store.discard_prepared(prepared))
    )
    with pytest.raises(DistributionApplyError) as raised:
        operation()

    assert checks == 2
    assert raised.value.recovery_metadata_state == "metadata-cleanup-conflict"
    assert unlink_calls == []
    current_metadata = metadata_path.lstat()
    assert (
        current_metadata.st_dev,
        current_metadata.st_ino,
        current_metadata.st_mode,
        current_metadata.st_nlink,
    ) == (
        foreign_before.st_dev,
        foreign_before.st_ino,
        foreign_before.st_mode,
        foreign_before.st_nlink,
    )
    assert (metadata_path.read_bytes() if foreign_kind == "regular" else metadata_path.readlink()) == foreign_payload
    assert aside.read_bytes() == metadata_bytes
    assert not foreign_source.exists() and not foreign_source.is_symlink()
    assert not tuple(parent.glob("*.remove"))
    assert not tuple(parent.glob("*.gc"))
    assert not tuple(parent.glob("*.restore"))


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_destructive_metadata_finalizer_uses_one_terminal_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
) -> None:
    """Normal destructive cleanup bypasses all generic pathname compensation."""

    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    metadata_path = guard_path if entry == "guard" else journal_path
    original_assert = OperationJournalStore._assert_bound_regular_entry
    original_unlink = managed_distribution.os.unlink
    events: list[str] = []
    unlink_calls: list[str] = []

    def observe_bound(self, parent_fd, name, held_fd, expected_snapshot, expected_sha256, *, identity_error):
        events.append("bound-check")
        return original_assert(
            parent_fd,
            name,
            held_fd,
            expected_snapshot,
            expected_sha256,
            identity_error=identity_error,
        )

    def observe_unlink(name, *args, **kwargs):
        if isinstance(name, str):
            events.append("unlink")
            unlink_calls.append(name)
        return original_unlink(name, *args, **kwargs)

    def fail_generic(*args, **kwargs):
        raise AssertionError("destructive metadata cleanup entered generic stage GC")

    monkeypatch.setattr(OperationJournalStore, "_assert_bound_regular_entry", observe_bound)
    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    monkeypatch.setattr(managed_distribution, "_remove_distribution_stage_if_owned", fail_generic)
    monkeypatch.setattr(
        managed_distribution,
        "_rename_distribution_no_replace",
        fail_generic,
    )
    monkeypatch.setattr(managed_distribution.os, "link", fail_generic)
    if entry == "guard":
        store.remove_legacy_marker(marker)
    else:
        store.discard_prepared(prepared)

    assert events[-2:] == ["bound-check", "unlink"]
    assert unlink_calls == [metadata_path.name]
    assert not metadata_path.exists() and not metadata_path.is_symlink()
    assert not tuple(metadata_path.parent.glob("*.remove"))
    assert not tuple(metadata_path.parent.glob("*.gc"))
    assert not tuple(metadata_path.parent.glob("*.restore"))


@pytest.mark.parametrize("entry", ["guard", "journal"])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_destructive_metadata_fsync_failure_requires_manual_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry: str,
    intent: str,
) -> None:
    """A post-unlink fsync fault never attempts rollback or private publication."""

    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        _target_root,
        _root_identity,
        _assessment,
        _executable,
        store,
        marker,
        prepared,
        guard_path,
        journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    metadata_path = guard_path if entry == "guard" else journal_path
    counterpart = journal_path if entry == "guard" else guard_path
    original_unlink = managed_distribution.os.unlink
    original_fsync = managed_distribution.os.fsync
    unlink_calls: list[str] = []
    unlinked = False
    fsync_failed = False

    def observe_unlink(name, *args, **kwargs):
        nonlocal unlinked
        if isinstance(name, str):
            unlink_calls.append(name)
            if name == metadata_path.name:
                unlinked = True
        return original_unlink(name, *args, **kwargs)

    def fail_after_terminal_unlink(fd: int) -> None:
        nonlocal fsync_failed
        if unlinked and not fsync_failed:
            fsync_failed = True
            raise OSError(errno.EIO, "injected metadata fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(managed_distribution.os, "unlink", observe_unlink)
    monkeypatch.setattr(managed_distribution.os, "fsync", fail_after_terminal_unlink)
    operation = (
        (lambda: store.remove_legacy_marker(marker)) if entry == "guard" else (lambda: store.discard_prepared(prepared))
    )
    with pytest.raises(DistributionApplyError) as raised:
        operation()

    assert unlinked is True
    assert fsync_failed is True
    assert raised.value.recovery_metadata_state == "metadata-cleanup-conflict"
    assert unlink_calls == [metadata_path.name]
    assert not metadata_path.exists() and not metadata_path.is_symlink()
    assert counterpart.is_file()
    assert not tuple(metadata_path.parent.glob("*.remove"))
    assert not tuple(metadata_path.parent.glob("*.gc"))
    assert not tuple(metadata_path.parent.glob("*.restore"))


@pytest.mark.parametrize("journal_backed", [False, True])
@pytest.mark.parametrize("intent", ["deprovision", "purge"])
def test_i371_metadata_cleanup_conflict_maps_to_public_manual_recovery(
    tmp_path: Path,
    journal_backed: bool,
    intent: Literal["deprovision", "purge"],
) -> None:
    (
        _install_root,
        _scaffold_root,
        _manifest_path,
        target_root,
        _root_identity,
        assessment,
        executable,
        _store,
        _marker,
        prepared,
        _guard_path,
        _journal_path,
    ) = _i371_recovery_fixture(tmp_path, intent)
    result = managed_distribution._destructive_recovery_boundary_result(
        assessment,
        prepared if journal_backed else None,
        executable=executable,
        intent=intent,
        error=DistributionApplyError(
            "metadata cleanup failed",
            recovery_metadata_state="metadata-cleanup-conflict",
        ),
        failure_paths=("spec-dock/.distribution-journal.json",),
    )
    assert result is not None
    assert result.status == "recovery_required"
    assert result.retry_policy == "manual-recovery"
    if journal_backed:
        assert result.reason == f"{intent}-recovery-required"
    else:
        assert result.reason == f"{intent}-guard-only"
        assert result.phase == "marker-write"
    managed_distribution._validate_deprovision_process_result(result, intent=intent)
    payload = cli._uninstall_payload_from_result(
        result,
        target_root=target_root,
        apply=True,
        specs_mode="remove" if intent == "purge" else "keep",
    )
    assert payload["status"] == "partial_failure"
    assert payload["retry_command"] is None
    assert cli._uninstall_exit_code_from_result(result) == 1


@pytest.mark.parametrize("kind", ["regular", "symlink"])
def test_i368_post_exchange_race_preserves_third_party_canonical(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    parent = tmp_path / kind
    parent.mkdir()
    target = parent / "target"
    stage = parent / "stage"
    if kind == "regular":
        target.write_bytes(b"old\n")
        stage.write_bytes(b"new\n")
    else:
        target.symlink_to("old-target")
        stage.symlink_to("new-target")
    target_before = target.lstat()
    stage_before = stage.lstat()
    original_swap = managed_distribution._rename_distribution_swap
    swapped = False

    def replace_after_exchange(source_parent_fd, source_name, destination_parent_fd, destination_name):
        nonlocal swapped
        original_swap(source_parent_fd, source_name, destination_parent_fd, destination_name)
        if not swapped:
            swapped = True
            target.unlink()
            if kind == "regular":
                target.write_bytes(b"third-party\n")
            else:
                target.symlink_to("third-party-target")

    monkeypatch.setattr(managed_distribution, "_rename_distribution_swap", replace_after_exchange)
    parent_fd = os.open(parent, os.O_RDONLY)
    try:
        with pytest.raises(DistributionApplyError, match="raced"):
            if kind == "regular":
                target_fd = os.open(target.name, os.O_RDONLY, dir_fd=parent_fd)
                stage_fd = os.open(stage.name, os.O_RDONLY, dir_fd=parent_fd)
                try:
                    managed_distribution._swap_regular_distribution_target_if_bound(
                        parent_fd,
                        stage.name,
                        target.name,
                        target_fd=target_fd,
                        staging_fd=stage_fd,
                        expected_target=target_before,
                        identity_message="raced",
                    )
                finally:
                    os.close(stage_fd)
                    os.close(target_fd)
            else:
                expected_snapshot = managed_distribution.replace(
                    managed_distribution._snapshot_from_stat("target", target_before),
                    identity=managed_distribution.DistributionIdentity(kind="symlink", target="old-target"),
                )
                managed_distribution._swap_symlink_distribution_target_if_bound(
                    parent_fd,
                    stage.name,
                    target.name,
                    expected_target=expected_snapshot,
                    staging_stat=stage_before,
                    identity_message="raced",
                )
    finally:
        os.close(parent_fd)

    if kind == "regular":
        assert target.read_bytes() == b"third-party\n"
        assert stage.read_bytes() == b"old\n"
    else:
        assert target.readlink() == Path("third-party-target")
        assert stage.readlink() == Path("old-target")


def test_i368_guard_conversion_failure_retains_legacy_predecessor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_root, executable = _i368_minimal_executable(tmp_path)
    store = OperationJournalStore(target_root)
    root_info = target_root.stat()
    marker_path = target_root / "spec-dock" / ".distribution-retry.json"
    marker_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "operation": "update",
                "package_version": "1.2.3",
                "target_root": {"device": root_info.st_dev, "inode": root_info.st_ino},
                "last_completed_phase": "preflight-complete",
                "purpose": "distribution-rerun",
                "stage_ownership": [],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    legacy_bytes = marker_path.read_bytes()
    marker = managed_distribution._read_distribution_retry_marker(target_root)
    assert marker is not None
    original_assert = OperationJournalStore._assert_bound_regular_entry

    def replace_guard_before_acceptance(
        self, parent_fd, name, held_fd, expected_snapshot, expected_sha256, *, identity_error
    ):
        marker_path.unlink()
        marker_path.write_bytes(b"third-party\n")
        return original_assert(
            parent_fd,
            name,
            held_fd,
            expected_snapshot,
            expected_sha256,
            identity_error=identity_error,
        )

    monkeypatch.setattr(OperationJournalStore, "_assert_bound_regular_entry", replace_guard_before_acceptance)

    with pytest.raises(DistributionApplyError, match="legacy-marker-unconvertible"):
        store.prepare_legacy_guard(executable, package_version="1.2.3", replace_marker=marker)

    assert marker_path.read_bytes() == b"third-party\n"
    recovery_entries = list(marker_path.parent.glob(".distribution-retry-*.stage"))
    assert any(path.read_bytes() == legacy_bytes for path in recovery_entries)
