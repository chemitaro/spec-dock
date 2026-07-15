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
    def __init__(
        self,
        kinds=None,
        *,
        guard_failure=None,
        guard_failures_by_endpoint=None,
        inventory_guard=None,
        copy_failure=None,
    ):
        self.kinds = kinds or {}
        self.guard_failure = guard_failure
        self.guard_failures_by_endpoint = guard_failures_by_endpoint or {}
        self.inventory_guard = inventory_guard
        self.copy_failure = copy_failure
        self.guard_calls = []
        self.inventory_guard_calls = []
        self.kind_calls = []
        self.copy_calls = []

    def path_exists(self, path):
        return path.exists()

    def remove_target(self, _path):
        raise AssertionError("not used")

    def path_kind(self, path):
        self.kind_calls.append(path)
        if path in self.kinds:
            return self.kinds[path]
        if path.is_symlink():
            return "symlink"
        if path.is_dir():
            return "directory"
        if path.is_file():
            return "file"
        return "missing"

    def guard_workbench_ancestry(self, root, endpoint, *, allow_missing_leaf=False):
        self.guard_calls.append((root, endpoint, allow_missing_leaf))
        if endpoint in self.guard_failures_by_endpoint:
            raise self.guard_failures_by_endpoint[endpoint]
        if self.guard_failure is not None:
            raise self.guard_failure

    def guard_workbench_inventory(self, specdock_dir):
        self.inventory_guard_calls.append(specdock_dir)
        if self.inventory_guard is not None:
            self.inventory_guard(specdock_dir)

    def copy_workbench(self, source, destination):
        self.copy_calls.append((source, destination))
        if self.copy_failure is not None:
            raise self.copy_failure


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


def test_copy_normalizes_trimmed_uppercase_scope_id(tmp_path):
    contracts, workbench, ports, filesystem, _, scope_id, source_scope, target_scope = _fixture(tmp_path)

    result = workbench.workbench_copy(
        contracts.WorkbenchCopyRequest(scope_id=f"  {scope_id.upper()}  ", target="target"),
        ports,
    )

    assert result.scope_id == scope_id
    assert filesystem.copy_calls == [(source_scope / ".workbench", target_scope / ".workbench")]


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


def test_ancestry_guard_failure_is_unsafe_path_before_copy(tmp_path):
    contracts, workbench, ports, filesystem, _, scope_id, _, _ = _fixture(tmp_path)
    filesystem.guard_failure = contracts.WorkbenchFilesystemError(mutation_started=False)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "unsafe_path"
    assert captured.value.mutation_started is False
    assert filesystem.copy_calls == []
    assert filesystem.guard_calls


@pytest.mark.parametrize("linked_level", ["initiative", "epic", "issue"])
def test_scope_ancestor_symlink_is_rejected_before_external_metadata_reader_runs(tmp_path, linked_level):
    contracts, workbench, ports, filesystem, node_repo, scope_id, _, _ = _fixture(tmp_path)
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import fs_cli
    finally:
        sys.path.pop(0)

    initiatives = ports.specdock_dir / "initiatives"
    initiatives.mkdir()
    initiative = initiatives / "init-00001-scope"
    epic = initiative / "epics" / "epic-00001-scope"
    external = tmp_path / "external-metadata"
    external.mkdir()
    (external / ".meta.json").write_text('{"id":"iss-99999"}', encoding="utf-8")
    try:
        if linked_level == "initiative":
            initiative.symlink_to(external, target_is_directory=True)
        elif linked_level == "epic":
            (initiative / "epics").mkdir(parents=True)
            epic.symlink_to(external, target_is_directory=True)
        else:
            (epic / "issues").mkdir(parents=True)
            (epic / "issues" / "iss-00003-scope").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    filesystem.inventory_guard = fs_cli.guard_workbench_inventory

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "unsafe_path"
    assert captured.value.side == "source"
    assert captured.value.mutation_started is False
    assert node_repo.calls == []
    assert filesystem.copy_calls == []


@pytest.mark.parametrize("meta_parent", ["initiatives-root", "unexpected-directory"])
def test_unexpected_metadata_symlink_is_rejected_before_external_reader_runs(tmp_path, meta_parent):
    contracts, workbench, ports, filesystem, node_repo, scope_id, _, _ = _fixture(tmp_path)
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import fs_cli
    finally:
        sys.path.pop(0)

    initiatives = ports.specdock_dir / "initiatives"
    initiatives.mkdir()
    parent = initiatives if meta_parent == "initiatives-root" else initiatives / "misc"
    parent.mkdir(exist_ok=True)
    external = tmp_path / f"external-{meta_parent}.json"
    external.write_bytes(b"external metadata must not be read or changed")
    try:
        (parent / ".meta.json").symlink_to(external)
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    filesystem.inventory_guard = fs_cli.guard_workbench_inventory

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "unsafe_path"
    assert captured.value.side == "source"
    assert captured.value.mutation_started is False
    assert external.read_bytes() == b"external metadata must not be read or changed"
    assert node_repo.calls == []
    assert filesystem.copy_calls == []


@pytest.mark.parametrize("mutation_started", [False, True])
def test_copy_failure_is_mapped_without_raw_error_or_success(tmp_path, mutation_started):
    contracts, workbench, ports, filesystem, _, scope_id, _, _ = _fixture(tmp_path)
    filesystem.copy_failure = contracts.WorkbenchFilesystemError(mutation_started=mutation_started)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "copy_failed"
    assert captured.value.side is None
    assert captured.value.mutation_started is mutation_started
    assert "secret" not in str(captured.value)


@pytest.mark.parametrize("side", ["source", "target"])
def test_scope_outside_its_worktree_is_rejected_before_scope_path_inspection(tmp_path, side):
    contracts, workbench, ports, filesystem, node_repo, scope_id, _, _ = _fixture(tmp_path)
    outside_scope = tmp_path / f"outside-{side}"
    outside_scope.mkdir()
    _, _, _, infra_contracts = _runtime_modules()
    replacement = _record(infra_contracts, scope_id=scope_id, path=outside_scope, slug="outside")
    specdock_root = ports.specdock_dir if side == "source" else tmp_path / "target" / "spec-dock"
    node_repo.records_by_root[specdock_root] = [replacement]
    filesystem.guard_failures_by_endpoint[outside_scope] = contracts.WorkbenchFilesystemError(mutation_started=False)

    with pytest.raises(contracts.WorkbenchCopyError) as captured:
        workbench.workbench_copy(contracts.WorkbenchCopyRequest(scope_id=scope_id, target="target"), ports)

    assert captured.value.code == "unsafe_path"
    assert captured.value.side == side
    assert captured.value.mutation_started is False
    assert outside_scope not in filesystem.kind_calls
    assert outside_scope / ".workbench" not in filesystem.kind_calls
    assert filesystem.copy_calls == []
