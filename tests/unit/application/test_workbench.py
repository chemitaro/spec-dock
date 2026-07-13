from pathlib import Path
import shutil
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import contracts, ports, workbench
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return contracts, ports, workbench, infra_contracts


class _NodeReader:
    def load_node_records(self):
        return []


class _EnvironmentGateway:
    def getenv(self, _name):
        return None


class _GitGateway:
    def __init__(self, records):
        self.records = records

    def worktree_list(self, _repo_root):
        return list(self.records)


class _NodeRepository:
    def __init__(self, records_by_root, failures_by_root=None):
        self.records_by_root = records_by_root
        self.failures_by_root = failures_by_root or {}
        self.calls = []

    def load_node_records(self, root):
        self.calls.append(root)
        if root in self.failures_by_root:
            raise RuntimeError(self.failures_by_root[root])
        return list(self.records_by_root.get(root, []))


class _FilesystemGateway:
    def __init__(self, kinds=None):
        self.kinds = kinds or {}
        self.copy_calls = []

    def path_exists(self, path):
        return path.exists()

    def remove_target(self, _path):
        raise AssertionError("not used")

    def path_kind(self, path):
        if path in self.kinds:
            return self.kinds[path]
        if path.is_symlink():
            return "symlink"
        if path.is_dir():
            return "directory"
        if path.is_file():
            return "file"
        return "missing"

    def copy_workbench(self, source, destination):
        self.copy_calls.append((source, destination))


def _record(infra_contracts, *, scope_id, path, slug):
    return infra_contracts.StoredMetaRecord(
        kind="issue",
        id=scope_id,
        title="Scope",
        slug=slug,
        path=str(path),
        parent_id="epic-00001",
        initiative_id="init-00001",
        epic_id="epic-00001",
        github_issue_number=3,
        meta_path=str(path / ".meta.json"),
    )


def _fixture(tmp_path, *, source_records=None, target_records=None, source_failure=None, target_failure=None):
    contracts, app_ports, workbench, infra_contracts = _runtime_modules()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    source_specdock = source / "spec-dock"
    target_specdock = target / "spec-dock"
    source_specdock.mkdir()
    target_specdock.mkdir()
    scope_id = "iss-00003"
    source_scope = source_specdock / "issues" / "iss-00003-alpha"
    target_scope = target_specdock / "issues" / "iss-00003-renamed"
    source_scope.mkdir(parents=True)
    target_scope.mkdir(parents=True)
    if source_records is None:
        source_records = [_record(infra_contracts, scope_id=scope_id, path=source_scope, slug="alpha")]
    if target_records is None:
        target_records = [_record(infra_contracts, scope_id=scope_id, path=target_scope, slug="renamed")]
    failures = {}
    if source_failure is not None:
        failures[source_specdock] = source_failure
    if target_failure is not None:
        failures[target_specdock] = target_failure
    node_repo = _NodeRepository(
        {source_specdock: source_records, target_specdock: target_records},
        failures,
    )
    filesystem = _FilesystemGateway({
        source_scope / ".workbench": "directory",
        target_scope / ".workbench": "missing",
    })
    ports = app_ports.Ports(
        node_reader=_NodeReader(),
        repo_root=source,
        specdock_dir=source_specdock,
        node_repo=node_repo,
        git_gateway=_GitGateway([
            contracts.GitWorktreeRecord(path=source, head="a", branch="refs/heads/main"),
            contracts.GitWorktreeRecord(path=target, head="b", branch="refs/heads/target"),
        ]),
        environment_gateway=_EnvironmentGateway(),
        filesystem_gateway=filesystem,
    )
    return contracts, workbench, ports, filesystem, node_repo, scope_id, source_scope, target_scope


def test_copy_resolves_same_scope_id_independently_when_slugs_differ(tmp_path):
    contracts, workbench, ports, filesystem, node_repo, scope_id, source_scope, target_scope = _fixture(tmp_path)

    result = workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert result.target_workbench_path == target_scope / ".workbench"
    assert filesystem.copy_calls == [(source_scope / ".workbench", target_scope / ".workbench")]
    assert node_repo.calls == [ports.specdock_dir, tmp_path / "target" / "spec-dock"]


@pytest.mark.parametrize("scope_id", ["init-local-00003", "task-00003", "3"])
def test_invalid_scope_identifier_is_stable_and_precedes_inventory(tmp_path, scope_id):
    contracts, workbench, ports, filesystem, node_repo, _, _, _ = _fixture(tmp_path)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "invalid_scope"
    assert captured.value.side is None
    assert captured.value.mutation_started is False
    assert node_repo.calls == []
    assert filesystem.copy_calls == []


@pytest.mark.parametrize(
    ("side", "records_override", "failure"),
    [
        ("source", [], None),
        ("target", [], None),
        ("source", "duplicate", None),
        ("target", "duplicate", None),
        ("source", None, "malformed metadata body"),
        ("target", None, "malformed metadata body"),
    ],
)
def test_scope_failure_is_side_specific_and_precedes_copy(tmp_path, side, records_override, failure):
    _, _, _, infra_contracts = _runtime_modules()
    scope_id = "iss-00003"
    kwargs = {}
    if records_override == "duplicate":
        root = tmp_path / side / "spec-dock" / "issues" / "dup"
        records_override = [
            _record(infra_contracts, scope_id=scope_id, path=root / "a", slug="a"),
            _record(infra_contracts, scope_id=scope_id, path=root / "b", slug="b"),
        ]
    if records_override is not None:
        kwargs[f"{side}_records"] = records_override
    if failure is not None:
        kwargs[f"{side}_failure"] = failure
    contracts, workbench, ports, filesystem, _, scope_id, _, _ = _fixture(tmp_path, **kwargs)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "invalid_scope"
    assert captured.value.side == side
    assert captured.value.mutation_started is False
    assert filesystem.copy_calls == []
    assert "malformed metadata body" not in str(captured.value)


@pytest.mark.parametrize("target_case", ["current", "bare", "path_missing"])
def test_target_ineligibility_precedes_scope_loading_and_copy(tmp_path, target_case):
    contracts, workbench, ports, filesystem, node_repo, scope_id, _, _ = _fixture(tmp_path)
    target_record = ports.git_gateway.records[1]
    selector = "target"
    if target_case == "current":
        selector = "source"
    elif target_case == "bare":
        ports.git_gateway.records[1] = contracts.GitWorktreeRecord(
            path=target_record.path,
            head=target_record.head,
            branch=target_record.branch,
            bare=True,
        )
    else:
        shutil.rmtree(target_record.path)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target=selector), ports)

    assert captured.value.code == "target_ineligible"
    assert captured.value.side == "target"
    assert captured.value.mutation_started is False
    assert node_repo.calls == []
    assert filesystem.copy_calls == []


@pytest.mark.parametrize("target_kind", ["missing", "directory"])
def test_missing_source_workbench_is_no_source_without_target_mutation(tmp_path, target_kind):
    contracts, workbench, ports, filesystem, _, scope_id, source_scope, target_scope = _fixture(tmp_path)
    filesystem.kinds[source_scope / ".workbench"] = "missing"
    filesystem.kinds[target_scope / ".workbench"] = target_kind

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "no_source"
    assert captured.value.side == "source"
    assert captured.value.mutation_started is False
    assert filesystem.copy_calls == []


def test_empty_source_workbench_is_success_and_enters_copy_after_preflight(tmp_path):
    contracts, workbench, ports, filesystem, _, scope_id, source_scope, target_scope = _fixture(tmp_path)

    result = workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert result.target_workbench_path == target_scope / ".workbench"
    assert filesystem.copy_calls == [(source_scope / ".workbench", target_scope / ".workbench")]


@pytest.mark.parametrize(
    ("side", "kind"),
    [("source", "file"), ("source", "symlink"), ("target", "file"), ("target", "symlink")],
)
def test_malformed_workbench_root_fails_before_copy(tmp_path, side, kind):
    contracts, workbench, ports, filesystem, _, scope_id, source_scope, target_scope = _fixture(tmp_path)
    root = source_scope / ".workbench" if side == "source" else target_scope / ".workbench"
    filesystem.kinds[root] = kind

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "invalid_workbench_root"
    assert captured.value.side == side
    assert captured.value.mutation_started is False
    assert filesystem.copy_calls == []
