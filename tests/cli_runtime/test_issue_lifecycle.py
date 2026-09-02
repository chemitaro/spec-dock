import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            issue_lifecycle as app_issue_lifecycle,
            ports as app_ports,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts


class _StubNodeReader:
    def load_node_records(self):
        return []


class _StubActiveStateStore:
    def __init__(self, infra_contracts) -> None:
        self._infra_contracts = infra_contracts
        self.write_calls = []

    def load_active_manifest(self, specdock_dir: Path):
        del specdock_dir
        return self._infra_contracts.ActiveManifestLoadResult(
            manifest=self._infra_contracts.ActiveManifest(
                initiative=None,
                epic=None,
                issue=self._infra_contracts.ActiveManifestEntry(
                    id="iss-00101",
                    path="spec-dock/initiatives/init-00001/epics/epic-00002/issues/iss-00101",
                ),
            ),
            source="agent.active",
            warnings=[],
        )

    def write_active_manifest(self, specdock_dir: Path, manifest):
        del specdock_dir
        self.write_calls.append(manifest)
        return manifest


class TestIssueLifecycleApplication:
    def test_issue_start_orders_guard_deps_checkout_active_write_and_sync_once(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        events: list[str] = []
        requested = SimpleNamespace(id="iss-00102", kind="issue")
        active_node = SimpleNamespace(
            id="iss-00101",
            github_issue_number=101,
            github_repo_owner=None,
            github_repo_name=None,
        )
        graph = SimpleNamespace(nodes_by_id={"iss-00101": active_node, "iss-00102": requested})

        class ActiveStore:
            def load_active_manifest(self, specdock_dir: Path):
                del specdock_dir
                return infra_contracts.ActiveManifestLoadResult(
                    manifest=infra_contracts.ActiveManifest(
                        initiative=None,
                        epic=None,
                        issue=infra_contracts.ActiveManifestEntry(id="iss-00101", path="spec-dock/old"),
                    ),
                    source="agent.active",
                    warnings=[],
                )

        class GitGateway:
            def current_branch_or_none(self, repo_root: Path) -> str:
                del repo_root
                return "maintenance-check"

        requested_target = app_contracts.TargetRef(
            kind="github_issue",
            node_id=None,
            github_issue_number=102,
            github_repo_owner="foreign",
            github_repo_name="repo",
        )

        def resolve_target(graph_arg, target_arg, **kwargs):
            del kwargs
            events.append("target")
            assert graph_arg is graph
            assert target_arg == requested_target
            return requested

        def github_state(*args, **kwargs):
            del args, kwargs
            events.append("guard")
            return "CLOSED"

        def check_deps(req, ports):
            del ports
            events.append("deps")
            assert req.target == app_contracts.TargetRef(
                kind="node_id",
                node_id="iss-00102",
                github_issue_number=None,
            )
            assert req.use_github
            assert req.issue_limit == 37
            return SimpleNamespace(
                inspection=SimpleNamespace(
                    evaluation=SimpleNamespace(
                        ready=True,
                        guard_reason="ready",
                        blockers=[],
                        node_blockers=[],
                    )
                ),
                warnings=["deps-warning"],
            )

        checkout = domain_models.BranchDecision(
            desired="iss-00102-second-issue",
            candidates=("iss-00102-second-issue", "issue/iss-00102-second-issue"),
            warnings=(),
        )

        def checkout_target(*args, **kwargs):
            del args, kwargs
            events.append("checkout")
            return checkout

        def persist_active(req, ports):
            del ports
            events.append("active")
            assert req.target == app_contracts.TargetRef(
                kind="node_id",
                node_id="iss-00102",
                github_issue_number=None,
            )
            return app_contracts.ActiveSetResult(
                selection=domain_models.ActiveSelection(
                    initiative_id="init-00001",
                    epic_id="epic-00002",
                    issue_id="iss-00102",
                ),
                branch=None,
                manifest_written=True,
                pointer_updated=True,
                warnings=["active-warning"],
            )

        post_sync = app_contracts.PostMutationSyncOutcome.skipped("test sync")

        def sync_once(ports):
            del ports
            events.append("sync")
            return post_sync

        monkeypatch.setattr(app_issue_lifecycle, "_build_graph", lambda ports: graph)
        monkeypatch.setattr(app_issue_lifecycle, "_resolve_target_node", resolve_target)
        monkeypatch.setattr(app_issue_lifecycle, "_github_state_for_node", github_state)
        monkeypatch.setattr(app_issue_lifecycle, "check_deps", check_deps)
        monkeypatch.setattr(app_issue_lifecycle, "checkout_active_target", checkout_target)
        monkeypatch.setattr(app_issue_lifecycle, "set_active", persist_active)
        monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", sync_once)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=ActiveStore(),
                git_gateway=GitGateway(),
            )
            result = app_issue_lifecycle.issue_start(
                app_contracts.IssueStartRequest(
                    target=requested_target,
                    force=False,
                    issue_limit=37,
                ),
                ports,
            )

        assert events == ["target", "guard", "deps", "checkout", "active", "sync"]
        assert result.active_set.branch is checkout
        assert result.post_sync is post_sync
        assert result.warnings == ["deps-warning", "active-warning"]

    def test_issue_start_checkout_failure_does_not_write_active_or_sync(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        events: list[str] = []
        requested = SimpleNamespace(id="iss-00102", kind="issue")
        graph = SimpleNamespace(nodes_by_id={"iss-00102": requested})

        class ActiveStore:
            def load_active_manifest(self, specdock_dir: Path):
                del specdock_dir
                return infra_contracts.ActiveManifestLoadResult(
                    manifest=infra_contracts.ActiveManifest(initiative=None, epic=None, issue=None),
                    source="none",
                    warnings=[],
                )

        class GitGateway:
            def current_branch_or_none(self, repo_root: Path) -> str:
                del repo_root
                return "main"

        monkeypatch.setattr(app_issue_lifecycle, "_build_graph", lambda ports: graph)
        monkeypatch.setattr(app_issue_lifecycle, "_resolve_target_node", lambda *args, **kwargs: requested)
        monkeypatch.setattr(
            app_issue_lifecycle,
            "check_deps",
            lambda *args, **kwargs: SimpleNamespace(
                inspection=SimpleNamespace(
                    evaluation=SimpleNamespace(
                        ready=True,
                        guard_reason="ready",
                        blockers=[],
                        node_blockers=[],
                    )
                ),
                warnings=[],
            ),
        )

        def fail_checkout(*args, **kwargs):
            del args, kwargs
            events.append("checkout")
            raise RuntimeError("checkout failed")

        def unexpected_active(*args, **kwargs):
            del args, kwargs
            events.append("active")
            raise AssertionError("active write must not run")

        def unexpected_sync(*args, **kwargs):
            del args, kwargs
            events.append("sync")
            raise AssertionError("sync must not run")

        monkeypatch.setattr(app_issue_lifecycle, "checkout_active_target", fail_checkout)
        monkeypatch.setattr(app_issue_lifecycle, "set_active", unexpected_active)
        monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", unexpected_sync)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=ActiveStore(),
                git_gateway=GitGateway(),
            )
            with pytest.raises(RuntimeError) as raised:
                app_issue_lifecycle.issue_start(
                    app_contracts.IssueStartRequest(
                        target=app_contracts.TargetRef(
                            kind="node_id",
                            node_id="iss-00102",
                            github_issue_number=None,
                        ),
                        force=False,
                        issue_limit=100,
                    ),
                    ports,
                )

        assert events == ["checkout"]
        message = str(raised.value)
        assert "issue start failed during branch checkout" in message
        assert "Active selection was not changed" in message
        assert "Post-mutation sync was not run" in message
        assert "checkout failed" in message

    def test_issue_start_active_write_failure_reports_branch_side_effect_and_skips_sync(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        events: list[str] = []
        requested = SimpleNamespace(id="iss-00102", kind="issue")
        graph = SimpleNamespace(nodes_by_id={"iss-00102": requested})

        class ActiveStore:
            def load_active_manifest(self, specdock_dir: Path):
                del specdock_dir
                return infra_contracts.ActiveManifestLoadResult(
                    manifest=infra_contracts.ActiveManifest(initiative=None, epic=None, issue=None),
                    source="none",
                    warnings=[],
                )

        class GitGateway:
            branch = "main"

            def current_branch_or_none(self, repo_root: Path) -> str:
                del repo_root
                return self.branch

        git_gateway = GitGateway()

        monkeypatch.setattr(app_issue_lifecycle, "_build_graph", lambda ports: graph)
        monkeypatch.setattr(app_issue_lifecycle, "_resolve_target_node", lambda *args, **kwargs: requested)
        monkeypatch.setattr(
            app_issue_lifecycle,
            "check_deps",
            lambda *args, **kwargs: SimpleNamespace(
                inspection=SimpleNamespace(
                    evaluation=SimpleNamespace(
                        ready=True,
                        guard_reason="ready",
                        blockers=[],
                        node_blockers=[],
                    )
                ),
                warnings=[],
            ),
        )

        def checkout_target(*args, **kwargs):
            del args, kwargs
            events.append("checkout")
            git_gateway.branch = "iss-00102-second-issue"
            return domain_models.BranchDecision(
                desired=git_gateway.branch,
                candidates=(git_gateway.branch, "issue/iss-00102-second-issue"),
                warnings=(),
            )

        def fail_active(*args, **kwargs):
            del args, kwargs
            events.append("active")
            raise RuntimeError("write active failed")

        def unexpected_sync(*args, **kwargs):
            del args, kwargs
            events.append("sync")
            raise AssertionError("sync must not run")

        monkeypatch.setattr(app_issue_lifecycle, "checkout_active_target", checkout_target)
        monkeypatch.setattr(app_issue_lifecycle, "set_active", fail_active)
        monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", unexpected_sync)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=ActiveStore(),
                git_gateway=git_gateway,
            )
            with pytest.raises(RuntimeError) as raised:
                app_issue_lifecycle.issue_start(
                    app_contracts.IssueStartRequest(
                        target=app_contracts.TargetRef(
                            kind="node_id",
                            node_id="iss-00102",
                            github_issue_number=None,
                        ),
                        force=False,
                        issue_limit=100,
                    ),
                    ports,
                )

        assert events == ["checkout", "active"]
        message = str(raised.value)
        assert "issue start failed while persisting active selection after checkout" in message
        assert "branch side effect: main -> iss-00102-second-issue" in message
        assert "active rollback: restored" in message
        assert "Post-mutation sync was not run" in message
        assert "write active failed" in message

    def test_issue_finish_orders_close_clear_sync_and_returns_phase_state(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()

        for already_closed in (False, True):
            events: list[str] = []
            post_sync = app_contracts.PostMutationSyncOutcome.skipped("test lifecycle sync")

            def fake_close_node(req, ports, *, events=events, already_closed=already_closed):
                del ports
                events.append("close")
                assert not req.run_post_sync
                return app_contracts.CloseNodeResult(
                    node_id="iss-00101",
                    node_kind="issue",
                    github_issue_number=101,
                    issue_snapshot=domain_models.IssueSnapshot(
                        issue_number=101,
                        state="CLOSED",
                        title="First issue",
                        labels=[],
                        updated_at="2026-05-05T00:00:00Z",
                        url="https://github.com/example/repo/issues/101",
                    ),
                    already_closed=already_closed,
                    warnings=[],
                )

            def fake_clear_active(req, ports, *, events=events):
                del req, ports
                events.append("clear")
                return app_contracts.ActiveClearResult(cleared=True, previous=None, warnings=[])

            def fake_post_mutation_sync(ports, *, events=events, post_sync=post_sync):
                del ports
                events.append("sync")
                return post_sync

            monkeypatch.setattr(app_issue_lifecycle, "close_node", fake_close_node)
            monkeypatch.setattr(app_issue_lifecycle, "clear_active", fake_clear_active)
            monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", fake_post_mutation_sync)

            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                store = _StubActiveStateStore(infra_contracts)
                ports = app_ports.Ports(
                    node_reader=_StubNodeReader(),
                    repo_root=repo_root,
                    specdock_dir=repo_root / "spec-dock",
                    active_state_store=store,
                )
                result = app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

            assert events == ["close", "clear", "sync"]
            assert store.write_calls == []
            assert result.issue_id == "iss-00101"
            assert result.github_issue_number == 101
            assert result.already_closed is already_closed
            assert result.active_cleared
            assert result.post_sync is post_sync

    def test_issue_finish_close_failure_preserves_active_and_reports_retry(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, _domain_models, infra_contracts = _runtime_modules()
        events: list[str] = []

        def fake_close_node(req, ports):
            del req, ports
            events.append("close")
            raise RuntimeError("close failed")

        def unexpected_clear(req, ports):
            del req, ports
            events.append("clear")
            raise AssertionError("clear must not run")

        def unexpected_sync(ports):
            del ports
            events.append("sync")
            raise AssertionError("sync must not run")

        monkeypatch.setattr(app_issue_lifecycle, "close_node", fake_close_node)
        monkeypatch.setattr(app_issue_lifecycle, "clear_active", unexpected_clear)
        monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", unexpected_sync)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            store = _StubActiveStateStore(infra_contracts)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=store,
            )
            with pytest.raises(RuntimeError) as raised:
                app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

        assert events == ["close"]
        assert store.write_calls == []
        message = str(raised.value)
        assert "issue finish failed while closing GitHub issue" in message
        assert "github_closed=false" in message
        assert "active_cleared=false" in message
        assert "post_sync=not_run" in message
        assert "spec-dock/scripts/spec-dock issue finish" in message
        assert "close failed" in message

    def test_issue_finish_clear_failure_reports_confirmed_partial_state_and_skips_sync(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()

        for already_closed in (False, True):
            for error_type in (RuntimeError, PermissionError, OSError):
                events: list[str] = []

                def fake_close_node(req, ports, *, events=events, already_closed=already_closed):
                    del req, ports
                    events.append("close")
                    return app_contracts.CloseNodeResult(
                        node_id="iss-00101",
                        node_kind="issue",
                        github_issue_number=101,
                        issue_snapshot=domain_models.IssueSnapshot(
                            issue_number=101,
                            state="CLOSED",
                            title="First issue",
                            labels=[],
                            updated_at="2026-05-05T00:00:00Z",
                            url="https://github.com/example/repo/issues/101",
                        ),
                        already_closed=already_closed,
                        warnings=[],
                    )

                def fake_clear_active(req, ports, *, events=events, error_type=error_type):
                    del req, ports
                    events.append("clear")
                    raise error_type("clear active failed")

                def unexpected_sync(ports, *, events=events):
                    del ports
                    events.append("sync")
                    raise AssertionError("sync must not run")

                monkeypatch.setattr(app_issue_lifecycle, "close_node", fake_close_node)
                monkeypatch.setattr(app_issue_lifecycle, "clear_active", fake_clear_active)
                monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", unexpected_sync)

                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    store = _StubActiveStateStore(infra_contracts)
                    ports = app_ports.Ports(
                        node_reader=_StubNodeReader(),
                        repo_root=repo_root,
                        specdock_dir=repo_root / "spec-dock",
                        active_state_store=store,
                    )
                    with pytest.raises(RuntimeError) as raised:
                        app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

                assert events == ["close", "clear"]
                assert store.write_calls == []
                active_load = store.load_active_manifest(repo_root / "spec-dock")
                assert active_load.manifest is not None
                assert active_load.manifest.issue is not None
                assert active_load.manifest.issue.id == "iss-00101"
                message = str(raised.value)
                assert "github_issue_number=101" in message
                assert "github_closed=true" in message
                assert f"already_closed={'true' if already_closed else 'false'}" in message
                assert "active_cleared=false" in message
                assert "post_sync=not_run" in message
                assert "Active selection remains set." in message
                assert "spec-dock/scripts/spec-dock active show" in message
                assert "spec-dock/scripts/spec-dock issue finish" in message
                assert "spec-dock/scripts/spec-dock active set <issue-id>" in message
                assert "clear active failed" in message

    def test_issue_finish_sync_failure_returns_closed_cleared_stale_result(self, monkeypatch) -> None:
        app_contracts, app_issue_lifecycle, app_ports, domain_models, infra_contracts = _runtime_modules()
        events: list[str] = []
        post_sync = app_contracts.PostMutationSyncOutcome.from_exception(RuntimeError("sync failed"))

        def fake_close_node(req, ports):
            del req, ports
            events.append("close")
            return app_contracts.CloseNodeResult(
                node_id="iss-00101",
                node_kind="issue",
                github_issue_number=101,
                issue_snapshot=domain_models.IssueSnapshot(
                    issue_number=101,
                    state="CLOSED",
                    title="First issue",
                    labels=[],
                    updated_at="2026-05-05T00:00:00Z",
                    url="https://github.com/example/repo/issues/101",
                ),
                already_closed=False,
                warnings=[],
            )

        def fake_clear_active(req, ports):
            del req, ports
            events.append("clear")
            return app_contracts.ActiveClearResult(cleared=True, previous=None, warnings=[])

        def fake_post_mutation_sync(ports):
            del ports
            events.append("sync")
            return post_sync

        monkeypatch.setattr(app_issue_lifecycle, "close_node", fake_close_node)
        monkeypatch.setattr(app_issue_lifecycle, "clear_active", fake_clear_active)
        monkeypatch.setattr(app_issue_lifecycle, "post_mutation_sync", fake_post_mutation_sync)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            store = _StubActiveStateStore(infra_contracts)
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(),
                repo_root=repo_root,
                specdock_dir=repo_root / "spec-dock",
                active_state_store=store,
            )
            result = app_issue_lifecycle.issue_finish(app_contracts.IssueFinishRequest(), ports)

        assert events == ["close", "clear", "sync"]
        assert store.write_calls == []
        assert result.already_closed is False
        assert result.active_cleared is True
        assert result.post_sync is post_sync
        assert result.post_sync.failed
        assert any("derived artifacts may be stale" in line for line in result.post_sync.guidance)


class TestCliIssueLifecycle(CliRuntimeHarness):
    def _commit_all(self, target: Path, message: str) -> None:
        self._run_git(target, ["add", "-A"])
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", message],
        )

    def _prepare_clean_repo_with_two_issues(self, target: Path) -> None:
        assert main(["init", str(target)]) == 0
        self._init_origin_repo(target)
        self._run_git(
            target,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-m", "init"],
        )
        self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
        self._run_runtime(target, ["new", "issue", "--epic", "2", "--title", "Second issue", "--github-issue", "102"])
        self._commit_all(target, "spec tree")

    def _make_gh_stub(
        self,
        bin_dir: Path,
        *,
        states: dict[int, str],
        fail_view_numbers: set[int] | None = None,
        fail_close_numbers: set[int] | None = None,
    ) -> Path:
        state_path = bin_dir / "gh-state.json"
        log_path = bin_dir / "gh-calls.log"
        all_states = {1: "OPEN", 2: "OPEN", **states}
        payload = {
            str(number): {
                "number": int(number),
                "state": state,
                "title": f"Issue {number}",
                "labels": [],
                "updatedAt": "2026-05-05T00:00:00Z",
                "url": f"https://github.com/example/repo/issues/{number}",
            }
            for number, state in all_states.items()
        }
        state_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        fail_numbers = sorted(int(number) for number in (fail_view_numbers or set()))
        fail_close = sorted(int(number) for number in (fail_close_numbers or set()))
        gh_path = bin_dir / "gh"
        gh_path.write_text(
            (
                "#!/usr/bin/env python3\n"
                "import json\n"
                "import sys\n"
                "from pathlib import Path\n\n"
                f"STATE_PATH = Path({state_path.as_posix()!r})\n"
                f"LOG_PATH = Path({log_path.as_posix()!r})\n"
                f"FAIL_VIEW = {fail_numbers!r}\n"
                f"FAIL_CLOSE = {fail_close!r}\n"
                "args = sys.argv[1:]\n"
                "state = json.loads(STATE_PATH.read_text(encoding='utf-8'))\n"
                "LOG_PATH.write_text(LOG_PATH.read_text(encoding='utf-8') + ' '.join(args) + '\\n' if LOG_PATH.exists() else ' '.join(args) + '\\n', encoding='utf-8')\n"
                "if args[:2] == ['issue', 'list']:\n"
                "    print(json.dumps(list(state.values())))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'view']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_VIEW:\n"
                "        print(f'view failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    print(json.dumps(state[str(number)]))\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['issue', 'close']:\n"
                "    number = int(args[2])\n"
                "    if number in FAIL_CLOSE:\n"
                "        print(f'close failed: {number}', file=sys.stderr)\n"
                "        raise SystemExit(1)\n"
                "    item = state[str(number)]\n"
                "    item['state'] = 'CLOSED'\n"
                "    STATE_PATH.write_text(json.dumps(state) + '\\n', encoding='utf-8')\n"
                "    raise SystemExit(0)\n"
                "print(f'unexpected gh args: {args}', file=sys.stderr)\n"
                "raise SystemExit(99)\n"
            ),
            encoding="utf-8",
        )
        gh_path.chmod(0o755)
        return state_path

    def _active_issue_id(self, target: Path) -> str | None:
        active_path = target / "spec-dock" / ".agent" / "active.json"
        if not active_path.exists():
            return None
        active = json.loads(active_path.read_text(encoding="utf-8"))
        issue = active.get("issue")
        if not isinstance(issue, dict):
            return None
        return issue.get("id")

    def _active_issue_pointer_text(self, target: Path) -> str:
        issue_pointer = target / "spec-dock" / "active" / "issue"
        if issue_pointer.is_symlink():
            return str(issue_pointer.readlink())
        path_file = issue_pointer.with_name("issue.path")
        if path_file.is_file():
            return path_file.read_text(encoding="utf-8").strip()
        return ""

    def test_issue_start_sets_active_and_checks_out_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "iss-00101"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00101" in p.stdout
            assert "spec-dock: ok (issue checkout) branch=iss-00101-first-issue" in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            issue = active["issue"]
            assert set(issue) == {"id", "path"}
            assert issue["id"] == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_rejects_non_issue_node(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "start", "--id", "epic-00002"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start only accepts issue nodes" in p.stderr
            assert self._active_issue_id(target) is None

    def test_issue_start_force_cannot_bypass_invalid_target_for_any_selector(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            active_path = target / "spec-dock" / ".agent" / "active.json"
            before_active = active_path.read_bytes() if active_path.exists() else None
            before_pointer = self._active_issue_pointer_text(target)
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            cases = (
                ["issue", "start", "iss-00999", "--force"],
                ["issue", "start", "--id", "iss-00999", "--force"],
                ["issue", "start", "--github-issue", "999", "--force"],
            )
            for args in cases:
                p = self._run_runtime_capture(target, args, env=test_env)
                assert p.returncode != 0, p.stdout + p.stderr
                assert "issue start forced=true" not in p.stderr
                assert self._active_issue_id(target) is None

            after_active = active_path.read_bytes() if active_path.exists() else None
            assert after_active == before_active
            assert self._active_issue_pointer_text(target) == before_pointer
            assert self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() == before_branch
            assert not (bin_dir / "gh-calls.log").exists()

    def test_issue_start_blocks_different_open_issue_from_active_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue" in p.stderr
            assert "current active issue: iss-00101" in p.stderr
            assert "current branch: iss-00101-first-issue" in p.stderr
            assert "requested issue: iss-00102" in p.stderr
            assert "github state: OPEN" in p.stderr
            assert "issue finish" in p.stderr
            assert "issue start iss-00102 -f" in p.stderr
            assert "active set iss-00102" in p.stderr
            assert (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8") == before
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert after_branch == before_branch

    def test_issue_start_allows_different_issue_from_closed_active_issue_branch(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active closed issue")
            active_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert active_branch == "iss-00101-first-issue"
            assert self._active_issue_id(target) == "iss-00101"
            self._make_gh_stub(bin_dir, states={101: "CLOSED", 102: "OPEN"})

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode == 0, p.stdout + p.stderr
            assert "issue start blocked" not in p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00102" in p.stdout
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_blocks_when_active_issue_github_state_unknown(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            before = (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8")
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            unknown_bin_dir = Path(bin_tmp)
            self._make_gh_stub(unknown_bin_dir, states={101: "OPEN", 102: "OPEN"}, fail_view_numbers={101})
            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue" in p.stderr
            assert "github state: UNKNOWN" in p.stderr
            assert "Next commands:" in p.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in p.stderr
            assert "spec-dock/scripts/spec-dock issue start iss-00102 -f" in p.stderr
            assert "spec-dock/scripts/spec-dock active set iss-00102" in p.stderr
            assert (target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8") == before
            after_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert after_branch == before_branch

    def test_issue_start_force_bypasses_unknown_active_guard_when_dependencies_are_ready(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"}, fail_view_numbers={101})
            p = self._run_runtime_capture(target, ["issue", "start", "102", "--force"], env=test_env)

            assert p.returncode == 0, p.stdout + p.stderr
            assert "issue start forced=true" in p.stderr
            assert "issue start blocked" not in p.stderr
            assert self._active_issue_id(target) == "iss-00102"
            assert self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() == (
                "iss-00102-second-issue"
            )

    def test_issue_start_blocks_when_active_issue_has_no_github_link(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00101-first-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta.pop("github", None)
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "remove active issue github link")
            before_active = (target / "spec-dock" / ".agent" / "active.json").read_bytes()
            before_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue" in p.stderr
            assert "github state: UNKNOWN" in p.stderr
            assert "active node resolution: resolved" in p.stderr
            assert (target / "spec-dock" / ".agent" / "active.json").read_bytes() == before_active
            assert self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() == before_branch

    def test_issue_start_force_bypasses_only_lifecycle_guard_not_dependency_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["depends_on"] = ["iss-00101"]
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "add dependency")

            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "102", "-f"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: dependency readiness failed" in p.stderr
            assert "iss-00101" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_force_does_not_bypass_node_level_dependency_guard(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            self._run_runtime(
                target,
                ["new", "epic", "--initiative", "1", "--title", "Empty blocker", "--github-issue", "202"],
            )
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00102-second-issue"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["depends_on"] = ["epic-00202"]
            self._write_json_force(issue_meta, meta)
            self._commit_all(target, "add node dependency")

            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN", 202: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "102", "--force"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: dependency readiness failed" in p.stderr
            assert "epic-00202" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00101-first-issue"

    def test_issue_start_rejects_legacy_force_short_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            uppercase = self._run_runtime_capture(target, ["issue", "start", "102", "-F"])
            old_t = self._run_runtime_capture(target, ["issue", "start", "102", "-t"])

            assert uppercase.returncode != 0, uppercase.stdout + uppercase.stderr
            assert "unrecognized arguments: -F" in uppercase.stderr
            assert old_t.returncode != 0, old_t.stdout + old_t.stderr
            assert "unrecognized arguments: -t" in old_t.stderr

    def test_issue_start_force_switches_when_dependency_ready_and_warns(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            self._run_runtime(target, ["issue", "start", "101"], env=test_env)
            self._commit_all(target, "active first issue")

            p = self._run_runtime_capture(target, ["issue", "start", "--github-issue", "102", "--force"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue start)" in p.stdout
            assert "issue=iss-00102" in p.stdout
            assert "issue start forced=true" in p.stderr
            assert self._active_issue_id(target) == "iss-00102"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "iss-00102-second-issue"

    def test_issue_start_from_main_still_blocks_different_open_active_but_same_issue_restarts(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            initial_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert first.returncode == 0, first.stdout + first.stderr
            self._commit_all(target, "active first issue")
            issue_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            same = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert same.returncode == 0, same.stdout + same.stderr
            assert "issue start blocked" not in same.stderr
            same_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert same_branch == issue_branch
            self._commit_all(target, "same issue restart")

            self._run_git(target, ["checkout", initial_branch])
            main_start = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert main_start.returncode != 0, main_start.stdout + main_start.stderr
            assert "issue start blocked: unfinished active issue" in main_start.stderr
            assert "current branch:" in main_start.stderr
            assert self._active_issue_id(target) == "iss-00101"

    def test_issue_start_from_non_issue_branch_blocks_switching_open_active_issue(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert first.returncode == 0, first.stdout + first.stderr
            self._commit_all(target, "active first issue")
            self._run_git(target, ["checkout", "-b", "maintenance-check"])

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)
            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue" in p.stderr
            assert "current branch: maintenance-check" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "maintenance-check"

    def test_issue_start_from_detached_head_blocks_switching_open_active_issue(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self._run_runtime_capture(target, ["issue", "start", "101"], env=test_env)
            assert first.returncode == 0, first.stdout + first.stderr
            self._commit_all(target, "active first issue")
            self._run_git(target, ["checkout", "--detach", "HEAD"])

            p = self._run_runtime_capture(target, ["issue", "start", "102"], env=test_env)

            assert p.returncode != 0, p.stdout + p.stderr
            assert "issue start blocked: unfinished active issue" in p.stderr
            assert "current branch: (detached)" in p.stderr
            assert "spec-dock: ok (issue start)" not in p.stdout
            assert self._active_issue_id(target) == "iss-00101"
            current = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert current == "HEAD"

    def test_issue_finish_after_issue_start_then_finish_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            self._prepare_clean_repo_with_two_issues(target)
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN", 102: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            started = self._run_runtime_capture(target, ["issue", "start", "--id", "iss-00101"], env=test_env)
            assert started.returncode == 0, started.stdout + started.stderr
            assert "spec-dock: ok (issue start)" in started.stdout
            assert "issue=iss-00101" in started.stdout
            assert "spec-dock: ok (issue checkout) branch=iss-00101-first-issue" in started.stdout
            assert self._active_issue_id(target) == "iss-00101"
            active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            assert set(active["issue"]) == {"id", "path"}
            started_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert started_branch == "iss-00101-first-issue"
            list_count_before_finish = (bin_dir / "gh-calls.log").read_text(encoding="utf-8").count("issue list")

            finished = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)

            assert finished.returncode == 0, finished.stdout + finished.stderr
            assert "spec-dock: ok (issue finish)" in finished.stdout
            assert "issue=iss-00101" in finished.stdout
            assert "github=#101" in finished.stdout
            assert "active_cleared=true" in finished.stdout
            assert "already_closed=false" in finished.stdout
            assert self._active_issue_id(target) is None
            assert "system/active-none/issue" in self._active_issue_pointer_text(target)
            finished_branch = self._run_git(target, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
            assert finished_branch == "iss-00101-first-issue"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["101"]["state"] == "CLOSED"
            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00101"]["status"] == "done"
            log = (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
            assert log.count("issue list") == list_count_before_finish + 1

    def test_issue_finish_closes_open_issue_and_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101"])
            bin_dir = Path(bin_tmp)
            state_path = self._make_gh_stub(bin_dir, states={101: "OPEN"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok (issue finish)" in p.stdout
            assert "issue=iss-00101" in p.stdout
            assert "github=#101" in p.stdout
            assert "active_cleared=true" in p.stdout
            assert "already_closed=false" in p.stdout
            assert self._active_issue_id(target) is None
            state = json.loads(state_path.read_text(encoding="utf-8"))
            assert state["101"]["state"] == "CLOSED"

    def test_issue_finish_already_closed_clears_active(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            self._run_runtime(target, ["active", "set", "--id", "iss-00101"])
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "CLOSED"})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            p = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert p.returncode == 0, p.stdout + p.stderr
            assert "already_closed=true" in p.stdout
            assert self._active_issue_id(target) is None
            assert "system/active-none/issue" in self._active_issue_pointer_text(target)
            index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
            assert index_all["nodes"]["iss-00101"]["status"] == "done"
            log = (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
            assert log.count("issue list") == 1

    def test_issue_finish_failures_leave_active_unchanged(self) -> None:
        if os.name == "nt":
            pytest.skip("This test uses a python gh stub with shebang; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            no_active = self._run_runtime_capture(target, ["issue", "finish"])
            assert no_active.returncode != 0, no_active.stdout + no_active.stderr
            assert "issue finish requires an active issue" in no_active.stderr
            assert "Recovery:" in no_active.stderr
            assert "issue start <issue>" in no_active.stderr
            assert "active set <issue>" in no_active.stderr
            assert self._active_issue_id(target) is None

            self._create_same_repo_linked_hierarchy(target, issue_issue_number=101, issue_title="First issue")
            linked_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00101-first-issue"
                / ".meta.json"
            )
            linked_meta = json.loads(linked_meta_path.read_text(encoding="utf-8"))
            unlinked_meta = dict(linked_meta)
            unlinked_meta.pop("github", None)
            self._write_json_force(linked_meta_path, unlinked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101"])
            no_link = self._run_runtime_capture(target, ["issue", "finish"])
            assert no_link.returncode != 0, no_link.stdout + no_link.stderr
            assert "issue finish failed while closing GitHub issue" in no_link.stderr
            assert "Active selection was not cleared." in no_link.stderr
            assert "Recovery:" in no_link.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in no_link.stderr
            assert "spec-dock/scripts/spec-dock active show" in no_link.stderr
            assert "Node is not linked to a GitHub issue" in no_link.stderr
            assert self._active_issue_id(target) == "iss-00101"
            active_path = target / "spec-dock" / ".agent" / "active.json"
            stale_active = json.loads(active_path.read_text(encoding="utf-8"))
            stale_active["issue"]["id"] = "iss-00999"
            self._write_json_force(active_path, stale_active)
            stale_active_bytes = active_path.read_bytes()
            node_not_found = self._run_runtime_capture(target, ["issue", "finish"])
            assert node_not_found.returncode != 0, node_not_found.stdout + node_not_found.stderr
            assert "issue finish failed while closing GitHub issue" in node_not_found.stderr
            assert "Node not found: iss-00999" in node_not_found.stderr
            assert "Recovery:" in node_not_found.stderr
            assert self._active_issue_id(target) == "iss-00999"
            assert active_path.read_bytes() == stale_active_bytes

            self._write_json_force(linked_meta_path, linked_meta)
            self._run_runtime(target, ["active", "set", "--id", "iss-00101"])
            bin_dir = Path(bin_tmp)
            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_view_numbers={101})
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            close_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert close_failure.returncode != 0, close_failure.stdout + close_failure.stderr
            assert "issue finish failed while closing GitHub issue" in close_failure.stderr
            assert "Active selection was not cleared." in close_failure.stderr
            assert "Recovery:" in close_failure.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in close_failure.stderr
            assert "spec-dock/scripts/spec-dock active show" in close_failure.stderr
            assert "view failed: 101" in close_failure.stderr
            assert self._active_issue_id(target) == "iss-00101"
            assert set(json.loads((target / "spec-dock" / ".agent" / "active.json").read_text())["issue"]) == {
                "id",
                "path",
            }
            assert "issue list" not in (bin_dir / "gh-calls.log").read_text(encoding="utf-8")

            self._make_gh_stub(bin_dir, states={101: "OPEN"}, fail_close_numbers={101})
            close_command_failure = self._run_runtime_capture(target, ["issue", "finish"], env=test_env)
            assert close_command_failure.returncode != 0, close_command_failure.stdout + close_command_failure.stderr
            assert "issue finish failed while closing GitHub issue" in close_command_failure.stderr
            assert "Active selection was not cleared." in close_command_failure.stderr
            assert "Recovery:" in close_command_failure.stderr
            assert "spec-dock/scripts/spec-dock issue finish" in close_command_failure.stderr
            assert "spec-dock/scripts/spec-dock active show" in close_command_failure.stderr
            assert "close failed: 101" in close_command_failure.stderr
            assert self._active_issue_id(target) == "iss-00101"
            assert set(json.loads((target / "spec-dock" / ".agent" / "active.json").read_text())["issue"]) == {
                "id",
                "path",
            }
            assert "issue list" not in (bin_dir / "gh-calls.log").read_text(encoding="utf-8")
