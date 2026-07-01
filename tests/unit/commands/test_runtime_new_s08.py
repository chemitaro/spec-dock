from contextlib import contextmanager
import os
from pathlib import Path
import shlex
import sys
import tempfile
import threading
import time

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            create_node as app_create_node,
            ports as app_ports,
        )
        from spec_dock_runtime.commands import new as new_commands
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
    finally:
        sys.path.pop(0)
    return runtime_app, app_contracts, app_create_node, app_ports, new_commands, infra_contracts, presentation_cli_text


def _runtime_modules_import():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import (
            contracts as app_contracts,
            create_node as app_create_node,
            import_node as app_import_node,
            ports as app_ports,
        )
        from spec_dock_runtime.domain import models as domain_models
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_contracts, app_create_node, app_import_node, app_ports, domain_models, infra_contracts


def _quoted_runtime_entrypoint(specdock_dir: Path) -> str:
    return shlex.quote(str((specdock_dir / "scripts" / "spec-dock").resolve()))


@contextmanager
def _case_label(**labels):
    try:
        yield
    except AssertionError as exc:
        label = ", ".join(f"{key}={value!r}" for key, value in labels.items())
        raise AssertionError(f"case failed ({label}): {exc}") from exc


@contextmanager
def _patch_object(obj, name, *, new=None, side_effect=None):
    original = getattr(obj, name)
    if side_effect is not None:

        def replacement(*_args, **_kwargs):
            raise side_effect

    else:
        replacement = new
    setattr(obj, name, replacement)
    try:
        yield
    finally:
        setattr(obj, name, original)


@contextmanager
def _patch_dict(mapping, values, *, clear=False):
    original = dict(mapping) if clear else {key: mapping.get(key) for key in values}
    missing = {key for key in values if key not in mapping}
    if clear:
        mapping.clear()
    mapping.update(values)
    try:
        yield
    finally:
        if clear:
            mapping.clear()
            mapping.update(original)
        else:
            for key, value in original.items():
                if key in missing:
                    mapping.pop(key, None)
                else:
                    mapping[key] = value


def _record(
    infra_contracts,
    *,
    kind: str,
    node_id: str,
    title: str,
    path: Path,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
    github_issue_number: int | None,
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )


class _DummyNodeReader:
    def load_node_records(self):
        return []


class _StubNodeRepo:
    def __init__(self, records, events=None):
        self._records = list(records)
        self.events = events if events is not None else []

    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)

    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / ".meta.json").write_text(f"id={record.id}\n", encoding="utf-8")
        self._records.append(record)


class _RacyNodeRepo(_StubNodeRepo):
    def __init__(self, records, events=None, *, first_load_delay_seconds=0.1):
        super().__init__(records, events=events)
        self._first_load_delay_seconds = first_load_delay_seconds
        self._first_load_pending = True
        self._first_load_lock = threading.Lock()

    def load_node_records(self, specdock_dir):
        del specdock_dir
        snapshot = list(self._records)
        should_delay = False
        with self._first_load_lock:
            if self._first_load_pending:
                self._first_load_pending = False
                should_delay = True
        if should_delay:
            time.sleep(self._first_load_delay_seconds)
        return snapshot


class _StubTemplateScaffolder:
    def __init__(self, events=None):
        self.events = events if events is not None else []

    def render_text(self, text, replacements):
        rendered = text
        for k, v in replacements.items():
            rendered = rendered.replace(k, v)
        return rendered

    def load_template_text(self, src_path):
        return src_path.read_text(encoding="utf-8")

    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(src_dir.rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dest_path = dest_dir / rel
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            text = src_path.read_text(encoding="utf-8")
            dest_path.write_text(self.render_text(text, replacements), encoding="utf-8")
            created.append(dest_path)
        return created

    def write_text(self, dest_path, text):
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8")


class _StubIssueGateway:
    def __init__(self, created_numbers=None):
        self.created_numbers = list(created_numbers or [901])
        self.calls = []

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []

    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self.created_numbers:
            raise RuntimeError("no issue numbers configured")
        return self.created_numbers.pop(0)


class _StubGitGateway:
    def __init__(self, origin_repo_slug="Example/Repo", *, error=None):
        self.origin_repo_slug = origin_repo_slug
        self.error = error
        self.calls = []

    def origin_github_repo_slug(self, repo_root):
        self.calls.append(str(repo_root))
        if self.error is not None:
            raise RuntimeError(self.error)
        return self.origin_repo_slug


class _BlockingIssueGateway(_StubIssueGateway):
    def __init__(self, created_numbers, *, started_event: threading.Event, release_event: threading.Event):
        super().__init__(created_numbers)
        self._started_event = started_event
        self._release_event = release_event

    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        self._started_event.set()
        if not self._release_event.wait(timeout=5.0):
            raise RuntimeError("timed out waiting for release_event")
        if not self.created_numbers:
            raise RuntimeError("no issue numbers configured")
        return self.created_numbers.pop(0)


class _StubImportIssueGateway:
    def __init__(self, domain_models):
        self._domain_models = domain_models
        self.calls = []

    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []

    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        return self._domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="open",
            title=f"Imported #{int(issue_number)}",
            labels=[],
            updated_at="2026-03-12T00:00:00Z",
            url=f"https://github.com/example/repo/issues/{int(issue_number)}",
            repo_owner="example",
            repo_name="repo",
        )


class _StubClock:
    def today(self):
        return "2026-03-12"


class TestRuntimeNewS08:
    def _prepare_templates(self, specdock_dir: Path) -> None:
        for kind in ("initiative", "epic", "issue"):
            template_root = specdock_dir / "templates" / kind
            (template_root / "docs").mkdir(parents=True, exist_ok=True)
            (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\n", encoding="utf-8")
            (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\n", encoding="utf-8")
        rules_docs = {
            ("initiative", "epics.md"): "initiative epics rules\n",
            ("initiative", "artifacts.md"): "initiative artifacts rules\n",
            ("epic", "issues.md"): "epic issues rules\n",
            ("epic", "artifacts.md"): "epic artifacts rules\n",
            ("issue", "artifacts.md"): "issue artifacts rules\n",
        }
        for (scope, name), content in rules_docs.items():
            rules_path = specdock_dir / "docs" / "rules" / scope / name
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            rules_path.write_text(content, encoding="utf-8")

    def _ports(
        self,
        app_ports,
        *,
        specdock_dir: Path,
        records,
        events=None,
        issue_gateway=None,
        git_gateway=None,
        node_repo=None,
        template_scaffolder=None,
    ):
        resolved_node_repo = node_repo if node_repo is not None else _StubNodeRepo(records, events=events)
        resolved_template_scaffolder = (
            template_scaffolder if template_scaffolder is not None else _StubTemplateScaffolder(events=events)
        )
        return app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=resolved_node_repo,
            template_scaffolder=resolved_template_scaffolder,
            issue_gateway=issue_gateway or _StubIssueGateway([501]),
            git_gateway=git_gateway or _StubGitGateway(),
            clock=_StubClock(),
            repo_root=specdock_dir.parent,
            specdock_dir=specdock_dir,
        )

    def _run_parallel_create(self, create_fn, request_a, request_b):
        node_ids = []
        errors = []
        lock = threading.Lock()

        def _worker(req):
            try:
                result = create_fn(req)
                with lock:
                    node_ids.append(result.node.id)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        thread_a = threading.Thread(target=_worker, args=(request_a,))
        thread_b = threading.Thread(target=_worker, args=(request_b,))
        thread_a.start()
        thread_b.start()
        thread_a.join(timeout=5.0)
        thread_b.join(timeout=5.0)
        assert not thread_a.is_alive(), "parallel create thread A did not finish"
        assert not thread_b.is_alive(), "parallel create thread B did not finish"
        assert errors == []
        return sorted(node_ids)

    def test_planning_regression_create_plan_contains_all_candidates(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            graph = app_create_node.load_graph(
                self._ports(app_ports, specdock_dir=specdock_dir, records=[]),
                validate=False,
            )
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )

            assert plan.meta.id == "init-00101"
            assert plan.meta.kind == "initiative"
            assert plan.dest_dir.as_posix().endswith("init-00101-auth-platform")
            assert plan.planned_paths[-1] == plan.dest_dir / ".meta.json"
            assert plan.dest_dir / "README.md" in plan.planned_paths
            assert plan.dest_dir / "docs" / "checklist.md" in plan.planned_paths
            assert plan.dest_dir / "epics" / "rules.md" in plan.planned_paths
            assert plan.dest_dir / "artifacts" / "rules.md" in plan.planned_paths
            assert plan.dest_dir / "discussions" / "rules.md" not in plan.planned_paths

    def test_execution_regression_and_write_order(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            records = []
            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records, events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )
            created_paths = app_create_node.execute_create_plan(plan, ports)

            assert events[:2] == ["copy_scaffolded_tree", "write_meta"]
            assert created_paths[-1] == plan.dest_dir / ".meta.json"
            assert created_paths[:-1] == sorted(created_paths[:-1], key=lambda p: p.as_posix())
            assert (plan.dest_dir / ".meta.json").exists()
            assert (plan.dest_dir / "README.md").exists()
            assert (plan.dest_dir / "epics" / "rules.md").is_symlink()
            assert (plan.dest_dir / "artifacts" / "rules.md").is_symlink()
            assert not (plan.dest_dir / "discussions").exists()

    def test_full_candidate_set_no_write_preflight_collision(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )
            collision = plan.dest_dir / "docs" / "checklist.md"
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_text("existing", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Destination already exists"):
                app_create_node.execute_create_plan(plan, ports)

            assert events == []
            assert not (plan.dest_dir / ".meta.json").exists()

    def test_collision_on_meta_is_no_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )
            plan.dest_dir.mkdir(parents=True, exist_ok=True)
            (plan.dest_dir / ".meta.json").write_text("stale", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Destination already exists"):
                app_create_node.execute_create_plan(plan, ports)

            assert events == []
            assert not (plan.dest_dir / "README.md").exists()

    def test_broken_rules_symlink_collision_is_no_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )
            broken_link = plan.dest_dir / "epics" / "rules.md"
            broken_link.parent.mkdir(parents=True, exist_ok=True)
            Path(broken_link).symlink_to("../../../docs/rules/initiative/missing.md")

            with pytest.raises(RuntimeError, match="Destination already exists"):
                app_create_node.execute_create_plan(plan, ports)

            assert events == []
            assert not (plan.dest_dir / "README.md").exists()
            assert not (plan.dest_dir / ".meta.json").exists()

    def test_empty_rules_parent_path_collision_is_no_write_preflight(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        def _records_for(kind: str, *, specdock_dir: Path):
            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = []
            if kind in ("epic", "issue"):
                records.append(
                    _record(
                        infra_contracts,
                        kind="initiative",
                        node_id="init-local-00001",
                        title="Auth platform",
                        path=init_dir,
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=None,
                    )
                )
            if kind == "issue":
                records.append(
                    _record(
                        infra_contracts,
                        kind="epic",
                        node_id="epic-local-00001",
                        title="JWT auth",
                        path=epic_dir,
                        parent_id="init-local-00001",
                        initiative_id="init-local-00001",
                        epic_id=None,
                        github_issue_number=None,
                    )
                )
            return records

        def _request_for(kind: str):
            if kind == "initiative":
                return app_contracts.CreateNodeRequest(
                    title="Auth platform",
                    slug=None,
                    parent_id=None,
                    github_mode="link_existing",
                    github_issue_number=101,
                )
            if kind == "epic":
                return app_contracts.CreateNodeRequest(
                    title="JWT auth",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode="link_existing",
                    github_issue_number=102,
                )
            return app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                github_mode="link_existing",
                github_issue_number=103,
            )

        collision_paths = {
            "initiative": ("epics", "README.md"),
            "epic": ("issues", "README.md"),
            "issue": ("artifacts", ".meta.json"),
        }

        for kind, (collision_name, sentinel_name) in collision_paths.items():
            with _case_label(kind=kind, collision=collision_name), tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                specdock_dir = repo_root / "spec-dock"
                self._prepare_templates(specdock_dir)

                events = []
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    records=_records_for(kind, specdock_dir=specdock_dir),
                    events=events,
                )
                graph = app_create_node.load_graph(ports, validate=False)
                plan = app_create_node.plan_node_creation(
                    _request_for(kind),
                    graph,
                    kind=kind,
                    specdock_dir=specdock_dir,
                    today="2026-03-12",
                    current_repo_slug="example/repo",
                )
                collision = plan.dest_dir / collision_name
                collision.parent.mkdir(parents=True, exist_ok=True)
                collision.write_text("existing", encoding="utf-8")

                with pytest.raises(RuntimeError, match=f"Destination already exists: .*{collision_name}"):
                    app_create_node.execute_create_plan(plan, ports)

                assert events == []
                assert collision.read_text(encoding="utf-8") == "existing"
                assert not (plan.dest_dir / sentinel_name).exists()

    def test_missing_rules_source_is_no_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )
            (specdock_dir / "docs" / "rules" / "initiative" / "epics.md").unlink()

            with pytest.raises(RuntimeError, match="Missing rules source"):
                app_create_node.execute_create_plan(plan, ports)

            assert events == []
            assert not (plan.dest_dir / "README.md").exists()
            assert not (plan.dest_dir / ".meta.json").exists()

    def test_symlink_creation_capability_preflight_fails_before_copy(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)
            graph = app_create_node.load_graph(ports, validate=False)
            req = app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                github_mode="link_existing",
                github_issue_number=101,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
                current_repo_slug="example/repo",
            )

            with (
                _patch_object(app_create_node.os, "symlink", side_effect=OSError("operation not permitted")),
                pytest.raises(RuntimeError, match="Symlink creation preflight failed"),
            ):
                app_create_node.execute_create_plan(plan, ports)

            assert events == []
            assert not (plan.dest_dir / "README.md").exists()
            assert not (plan.dest_dir / ".meta.json").exists()

    def test_symlinked_rules_parent_dir_collision_is_no_write_preflight(self) -> None:
        if os.name == "nt":
            pytest.skip("symlink parent collision semantics vary on Windows")

        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        def _records_for(kind: str, *, specdock_dir: Path):
            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = []
            if kind in ("epic", "issue"):
                records.append(
                    _record(
                        infra_contracts,
                        kind="initiative",
                        node_id="init-local-00001",
                        title="Auth platform",
                        path=init_dir,
                        parent_id=None,
                        initiative_id=None,
                        epic_id=None,
                        github_issue_number=None,
                    )
                )
            if kind == "issue":
                records.append(
                    _record(
                        infra_contracts,
                        kind="epic",
                        node_id="epic-local-00001",
                        title="JWT auth",
                        path=epic_dir,
                        parent_id="init-local-00001",
                        initiative_id="init-local-00001",
                        epic_id=None,
                        github_issue_number=None,
                    )
                )
            return records

        def _request_for(kind: str):
            if kind == "initiative":
                return app_contracts.CreateNodeRequest(
                    title="Auth platform",
                    slug=None,
                    parent_id=None,
                    github_mode="link_existing",
                    github_issue_number=101,
                )
            if kind == "epic":
                return app_contracts.CreateNodeRequest(
                    title="JWT auth",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode="link_existing",
                    github_issue_number=102,
                )
            return app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                github_mode="link_existing",
                github_issue_number=103,
            )

        collision_paths = {
            "initiative": "epics",
            "epic": "issues",
            "issue": "artifacts",
        }

        for kind, collision_name in collision_paths.items():
            with _case_label(kind=kind, collision=collision_name), tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                specdock_dir = repo_root / "spec-dock"
                self._prepare_templates(specdock_dir)

                events = []
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    records=_records_for(kind, specdock_dir=specdock_dir),
                    events=events,
                )
                graph = app_create_node.load_graph(ports, validate=False)
                plan = app_create_node.plan_node_creation(
                    _request_for(kind),
                    graph,
                    kind=kind,
                    specdock_dir=specdock_dir,
                    today="2026-03-12",
                    current_repo_slug="example/repo",
                )
                symlink_target = repo_root / "existing-target"
                symlink_target.mkdir(parents=True, exist_ok=True)
                collision = plan.dest_dir / collision_name
                collision.parent.mkdir(parents=True, exist_ok=True)
                Path(collision).symlink_to(symlink_target)

                with pytest.raises(RuntimeError, match=f"Destination already exists: .*{collision_name}"):
                    app_create_node.execute_create_plan(plan, ports)

                assert events == []
                assert not (symlink_target / "rules.md").exists()
                assert not (plan.dest_dir / "README.md").exists()
                assert not (plan.dest_dir / ".meta.json").exists()

    def test_per_kind_parity_create_local(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]

            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                issue_gateway=_StubIssueGateway([501, 502]),
            )
            init_result = app_create_node.create_initiative(
                app_contracts.CreateNodeRequest(
                    title="Payment platform",
                    slug=None,
                    parent_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            assert init_result.node.kind == "initiative"
            assert init_result.node.id == "init-00501"

            epic_result = app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="OAuth",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            assert epic_result.node.kind == "epic"
            assert epic_result.node.parent_id == "init-local-00001"
            assert epic_result.node.id == "epic-00502"

            issue_result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="link_existing",
                    github_issue_number=603,
                ),
                ports,
            )
            assert issue_result.node.kind == "issue"
            assert issue_result.node.parent_id == "epic-local-00001"
            assert issue_result.node.initiative_id == "init-local-00001"
            assert issue_result.node.id == "iss-00603"

    def test_parallel_create_initiative_allocates_unique_github_ids(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)

            node_repo = _RacyNodeRepo([], first_load_delay_seconds=0.1)
            issue_gateway = _StubIssueGateway([701, 702])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=[],
                node_repo=node_repo,
                issue_gateway=issue_gateway,
            )
            ids = self._run_parallel_create(
                lambda req: app_create_node.create_initiative(req, ports),
                app_contracts.CreateNodeRequest(
                    title="Auth platform A",
                    slug=None,
                    parent_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                app_contracts.CreateNodeRequest(
                    title="Auth platform B",
                    slug=None,
                    parent_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
            )

            assert ids == ["init-00701", "init-00702"]

    def test_parallel_create_epic_allocates_unique_github_ids(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                )
            ]
            node_repo = _RacyNodeRepo(records, first_load_delay_seconds=0.1)
            issue_gateway = _StubIssueGateway([701, 702])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                node_repo=node_repo,
                issue_gateway=issue_gateway,
            )
            ids = self._run_parallel_create(
                lambda req: app_create_node.create_epic(req, ports),
                app_contracts.CreateNodeRequest(
                    title="Epic A",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
                app_contracts.CreateNodeRequest(
                    title="Epic B",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
            )

            assert ids == ["epic-00701", "epic-00702"]

    def test_parallel_create_issue_allocates_unique_github_ids(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            node_repo = _RacyNodeRepo(records, first_load_delay_seconds=0.1)
            issue_gateway = _StubIssueGateway([701, 702])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                node_repo=node_repo,
                issue_gateway=issue_gateway,
            )
            ids = self._run_parallel_create(
                lambda req: app_create_node.create_issue(req, ports),
                app_contracts.CreateNodeRequest(
                    title="Issue A",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
                app_contracts.CreateNodeRequest(
                    title="Issue B",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
            )

            assert ids == ["iss-00701", "iss-00702"]

    def test_github_issue_create_delay_does_not_block_parallel_link_existing_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            started = threading.Event()
            release = threading.Event()
            issue_gateway = _BlockingIssueGateway([701], started_event=started, release_event=release)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            issue_result: dict[str, object] = {}
            issue_errors: list[Exception] = []

            def _run_issue_create() -> None:
                try:
                    issue_result["value"] = app_create_node.create_issue(
                        app_contracts.CreateNodeRequest(
                            title="Refresh token",
                            slug=None,
                            parent_id="epic-local-00001",
                            github_mode="create",
                            github_issue_number=None,
                        ),
                        ports,
                    )
                except Exception as exc:
                    issue_errors.append(exc)

            issue_thread = threading.Thread(target=_run_issue_create)
            with _patch_dict(
                os.environ,
                {
                    app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS: "0.02",
                    app_create_node._ENV_CREATE_LOCK_POLL_SECONDS: "0.005",
                    app_create_node._ENV_CREATE_LOCK_STALE_SECONDS: "3600",
                },
                clear=False,
            ):
                issue_thread.start()
                assert started.wait(timeout=1.0), "issue_create was not called"
                try:
                    local_result = app_create_node.create_initiative(
                        app_contracts.CreateNodeRequest(
                            title="Payments",
                            slug=None,
                            parent_id=None,
                            github_mode="link_existing",
                            github_issue_number=702,
                        ),
                        ports,
                    )
                finally:
                    release.set()
                issue_thread.join(timeout=5.0)

            assert not issue_thread.is_alive(), "github create thread did not finish"
            assert issue_errors == []
            assert local_result.node.id == "init-00702"
            assert "value" in issue_result
            assert issue_result["value"].node.id == "iss-00701"
            assert len(issue_gateway.calls) == 1
            body = issue_gateway.calls[0][2]
            assert "Type: issue" in body
            assert "Epic:" not in body
            assert "Initiative:" not in body

    def test_github_issue_create_pre_lock_window_rerevalidates_parent_state(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            node_repo = _StubNodeRepo(records, events=events)
            started = threading.Event()
            release = threading.Event()
            issue_gateway = _BlockingIssueGateway([702], started_event=started, release_event=release)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
                node_repo=node_repo,
            )

            errors: list[Exception] = []

            def _run_issue_create() -> None:
                try:
                    app_create_node.create_issue(
                        app_contracts.CreateNodeRequest(
                            title="Refresh token",
                            slug=None,
                            parent_id="epic-local-00001",
                            github_mode="create",
                            github_issue_number=None,
                        ),
                        ports,
                    )
                except Exception as exc:
                    errors.append(exc)

            issue_thread = threading.Thread(target=_run_issue_create)
            issue_thread.start()
            assert started.wait(timeout=1.0), "issue_create was not called"
            node_repo._records = [record for record in node_repo._records if record.id != "epic-local-00001"]
            release.set()
            issue_thread.join(timeout=5.0)

            assert not issue_thread.is_alive(), "github create thread did not finish"
            assert len(errors) == 1
            message = str(errors[0])
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Epic not found: epic-local-00001" in message
            assert "GitHub issue was created: #702" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" in message
            assert "--epic epic-local-00001" in message
            assert "--github-issue 702" in message
            assert events == []
            assert len(issue_gateway.calls) == 1

    def test_github_issue_create_pre_lock_window_rerevalidates_github_uniqueness_state(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            node_repo = _StubNodeRepo(records, events=events)
            started = threading.Event()
            release = threading.Event()
            issue_gateway = _BlockingIssueGateway([705], started_event=started, release_event=release)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
                node_repo=node_repo,
            )

            errors: list[Exception] = []

            def _run_issue_create() -> None:
                try:
                    app_create_node.create_issue(
                        app_contracts.CreateNodeRequest(
                            title="Refresh token",
                            slug=None,
                            parent_id="epic-local-00001",
                            github_mode="create",
                            github_issue_number=None,
                        ),
                        ports,
                    )
                except Exception as exc:
                    errors.append(exc)

            issue_thread = threading.Thread(target=_run_issue_create)
            issue_thread.start()
            assert started.wait(timeout=1.0), "issue_create was not called"
            node_repo._records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-00042",
                    title="Competing link",
                    path=epic_dir / "issues" / "iss-local-00042-competing-link",
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                    github_issue_number=705,
                )
            )
            release.set()
            issue_thread.join(timeout=5.0)

            assert not issue_thread.is_alive(), "github create thread did not finish"
            assert len(errors) == 1
            message = str(errors[0])
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "github linkage is already linked" in message
            assert "github.issue_number=705" in message
            assert "GitHub issue was created: #705" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" in message
            assert "--epic epic-local-00001" in message
            assert "--github-issue 705" in message
            assert "close/cleanup" in message
            assert events == []
            assert len(issue_gateway.calls) == 1
            assert not (epic_dir / "issues" / "iss-00705-refresh-token").exists()

    def test_issue_create_lock_failure_after_github_create_reports_retry_link_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([703])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "token=holder\npid=222\nuser=lock-holder\ncreated_unix=9999999999\ncreated_iso=2099-01-01\n",
                encoding="utf-8",
            )

            with (
                _patch_dict(
                    os.environ,
                    {
                        app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS: "0.02",
                        app_create_node._ENV_CREATE_LOCK_POLL_SECONDS: "0.005",
                        app_create_node._ENV_CREATE_LOCK_STALE_SECONDS: "3600",
                    },
                    clear=False,
                ),
                pytest.raises(RuntimeError, match="GitHub issue was created: #703") as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_remote_only_fail" in message
            assert "create lock acquisition failed" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" in message
            assert "--epic epic-local-00001" in message
            assert "--github-issue 703" in message
            assert "close/cleanup" in message
            assert len(issue_gateway.calls) == 1
            assert events == []
            assert not (epic_dir / "issues").exists()
            assert lock_path.exists()

    def test_issue_create_write_seam_failure_after_github_create_reports_retry_link_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([704])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            with (
                _patch_object(
                    app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated write failure")
                ),
                pytest.raises(RuntimeError, match="GitHub issue was created: #704") as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_local_write_fail" in message
            assert "simulated write failure" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" in message
            assert "--epic epic-local-00001" in message
            assert "--github-issue 704" in message
            assert "close/cleanup" in message
            assert len(issue_gateway.calls) == 1
            assert events == []

    def test_issue_create_partial_copy_failure_after_github_create_reports_doctor_first_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        class _PartialCopyFailureTemplateScaffolder(_StubTemplateScaffolder):
            def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
                self.events.append("copy_scaffolded_tree")
                created = []
                for src_path in sorted(src_dir.rglob("*"), key=lambda p: p.as_posix()):
                    if src_path.is_dir():
                        continue
                    rel = src_path.relative_to(src_dir)
                    dest_path = dest_dir / rel
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    text = src_path.read_text(encoding="utf-8")
                    dest_path.write_text(self.render_text(text, replacements), encoding="utf-8")
                    created.append(dest_path)
                    raise RuntimeError("simulated partial copy failure")
                return created

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([712])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
                template_scaffolder=_PartialCopyFailureTemplateScaffolder(events=events),
            )

            with pytest.raises(RuntimeError, match="GitHub issue was created: #712") as raised:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_local_write_fail" in message
            assert "simulated partial copy failure" in message
            assert "Do not rerun blindly" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message
            assert len(issue_gateway.calls) == 1
            assert (epic_dir / "issues" / "iss-00712-refresh-token").exists()
            assert not (epic_dir / "issues" / "iss-00712-refresh-token" / ".meta.json").exists()

    def test_issue_create_meta_write_failure_after_github_create_reports_doctor_first_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        class _MetaWriteFailureNodeRepo(_StubNodeRepo):
            def write_meta(self, dest_dir, record):
                self.events.append("write_meta")
                del dest_dir, record
                raise RuntimeError("simulated write_meta failure")

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([713])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
                node_repo=_MetaWriteFailureNodeRepo(records, events=events),
            )

            with pytest.raises(RuntimeError, match="GitHub issue was created: #713") as raised:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_local_write_fail" in message
            assert "simulated write_meta failure" in message
            assert "Do not rerun blindly" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message
            assert len(issue_gateway.calls) == 1
            assert (epic_dir / "issues" / "iss-00713-refresh-token" / "README.md").exists()
            assert not (epic_dir / "issues" / "iss-00713-refresh-token" / ".meta.json").exists()

    def test_import_partial_write_failure_reports_doctor_first_guidance(self) -> None:
        app_contracts, app_create_node, app_import_node, app_ports, domain_models, infra_contracts = (
            _runtime_modules_import()
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            for node_dir in (init_dir, epic_dir):
                node_dir.mkdir(parents=True, exist_ok=True)
                (node_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
                for name in ("requirement.md", "design.md", "plan.md", "report.md"):
                    (node_dir / name).write_text(f"{name}\n", encoding="utf-8")
            issue_gateway = _StubImportIssueGateway(domain_models)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            with (
                _patch_object(
                    app_import_node,
                    "execute_create_plan",
                    side_effect=app_create_node.CreatePlanExecutionError(
                        phase="scaffold_copied",
                        message="simulated import partial write",
                    ),
                ),
                pytest.raises(RuntimeError, match="Outcome: import_local_write_fail") as raised,
            ):
                app_import_node.import_issue(
                    app_contracts.ImportNodeRequest(
                        issue_number=714,
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "simulated import partial write" in message
            assert "Do not rerun blindly" in message
            assert "local node `iss-00714`" in message
            assert f"{runtime_cmd} doctor" in message
            assert "Recovery: rerun" not in message

    def test_issue_create_cleanup_failure_after_local_write_reports_doctor_first_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([708])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            original_unlink = app_create_node.Path.unlink

            def _unlink_with_failure(path_self, *args, **kwargs):
                if path_self == lock_path:
                    raise OSError("permission denied")
                return original_unlink(path_self, *args, **kwargs)

            with (
                _patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure),
                pytest.raises(
                    RuntimeError,
                    match="Outcome: post_github_local_write_success_cleanup_fail",
                ) as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "GitHub issue was created: #708" in message
            assert "create lock release failed" in message
            assert "Create may already have succeeded" in message
            assert "Do not rerun blindly" in message
            assert "local node `iss-00708`" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message
            assert len(issue_gateway.calls) == 1
            assert (epic_dir / "issues" / "iss-00708-refresh-token" / ".meta.json").exists()

    def test_issue_create_body_and_cleanup_failure_keeps_outcome_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([709])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            original_unlink = app_create_node.Path.unlink

            def _unlink_with_failure(path_self, *args, **kwargs):
                if path_self == lock_path:
                    raise OSError("permission denied")
                return original_unlink(path_self, *args, **kwargs)

            with (
                _patch_object(
                    app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated write failure")
                ),
                _patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure),
                pytest.raises(RuntimeError, match="Outcome: post_github_body_and_cleanup_fail") as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Primary local failure: simulated write failure" in message
            assert "Cleanup failure: create lock release failed" in message
            assert "GitHub issue was created: #709" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" in message
            assert "--epic epic-local-00001" in message
            assert "--github-issue 709" in message
            assert "close/cleanup" in message
            assert len(issue_gateway.calls) == 1
            assert events == []
            assert not (epic_dir / "issues" / "iss-00709-refresh-token").exists()

    def test_issue_create_post_write_guard_failure_after_local_write_reports_doctor_first_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([711])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            with (
                _patch_object(
                    app_create_node,
                    "_post_write_duplicate_guard",
                    side_effect=RuntimeError("simulated post-write duplicate guard failure"),
                ),
                pytest.raises(RuntimeError, match="Outcome: post_github_local_write_fail") as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "simulated post-write duplicate guard failure" in message
            assert "GitHub issue was created: #711" in message
            assert "Create may already have succeeded" in message
            assert "Do not rerun blindly" in message
            assert "local node `iss-00711`" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message
            assert "close/cleanup" not in message
            assert len(issue_gateway.calls) == 1
            assert (epic_dir / "issues" / "iss-00711-refresh-token" / ".meta.json").exists()

    def test_issue_create_post_write_guard_and_cleanup_failure_reports_doctor_first_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([710])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            original_unlink = app_create_node.Path.unlink

            def _unlink_with_failure(path_self, *args, **kwargs):
                if path_self == lock_path:
                    raise OSError("permission denied")
                return original_unlink(path_self, *args, **kwargs)

            with (
                _patch_object(
                    app_create_node,
                    "_post_write_duplicate_guard",
                    side_effect=RuntimeError("simulated post-write duplicate guard failure"),
                ),
                _patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure),
                pytest.raises(RuntimeError, match="Outcome: post_github_body_and_cleanup_fail") as raised,
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Primary local failure: simulated post-write duplicate guard failure" in message
            assert "Cleanup failure: create lock release failed" in message
            assert "GitHub issue was created: #710" in message
            assert "Create may already have succeeded" in message
            assert "Do not rerun blindly" in message
            assert "local node `iss-00710`" in message
            assert f"{runtime_cmd} doctor" in message
            assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message
            assert len(issue_gateway.calls) == 1
            assert (epic_dir / "issues" / "iss-00710-refresh-token" / ".meta.json").exists()

    def test_issue_create_pure_input_validation_fails_before_github_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            cases = [
                (
                    "missing-epic",
                    {
                        "parent_id": None,
                    },
                    "--epic is required",
                ),
                (
                    "partial-repo-identity",
                    {
                        "parent_id": "epic-local-00001",
                        "github_repo_owner": "chemitaro",
                        "github_repo_name": None,
                    },
                    "github_repo_owner and github_repo_name must be provided together",
                ),
            ]
            for case_name, overrides, expected_error in cases:
                with _case_label(case=case_name):
                    issue_gateway = _StubIssueGateway([799])
                    ports = self._ports(
                        app_ports,
                        specdock_dir=specdock_dir,
                        records=records,
                        events=events,
                        issue_gateway=issue_gateway,
                    )
                    request_kwargs = {
                        "title": "Refresh token",
                        "slug": None,
                        "parent_id": "epic-local-00001",
                        "github_mode": "create",
                        "github_issue_number": None,
                        "github_repo_owner": None,
                        "github_repo_name": None,
                    }
                    request_kwargs.update(overrides)
                    with pytest.raises(RuntimeError, match=expected_error) as raised:
                        app_create_node.create_issue(
                            app_contracts.CreateNodeRequest(**request_kwargs),
                            ports,
                        )
                    assert "Outcome: pre_github_fail" in str(raised.value)
                    assert "GitHub issue was created:" not in str(raised.value)
                    assert issue_gateway.calls == []

    def test_issue_create_repo_scope_precheck_failures_happen_before_github_create_or_local_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            cases = [
                (
                    "origin-missing",
                    "origin remote is missing; cannot resolve canonical GitHub repo scope.",
                ),
                (
                    "non-github-remote",
                    "origin remote is not a GitHub repository; cannot resolve canonical repo scope:",
                ),
                (
                    "fetch-push-mismatch",
                    "origin remote fetch/push mismatch; cannot resolve canonical repo scope:",
                ),
            ]
            for case_name, git_error in cases:
                with _case_label(case=case_name):
                    events: list[str] = []
                    issue_gateway = _StubIssueGateway([799])
                    git_gateway = _StubGitGateway(error=git_error)
                    ports = self._ports(
                        app_ports,
                        specdock_dir=specdock_dir,
                        records=records,
                        events=events,
                        issue_gateway=issue_gateway,
                        git_gateway=git_gateway,
                    )
                    with pytest.raises(RuntimeError, match=git_error):
                        app_create_node.create_issue(
                            app_contracts.CreateNodeRequest(
                                title="Refresh token",
                                slug=None,
                                parent_id="epic-local-00001",
                                github_mode="create",
                                github_issue_number=None,
                            ),
                            ports,
                        )
                    assert issue_gateway.calls == []
                    assert events == []
                    assert not (epic_dir / "issues").exists()
                    assert git_gateway.calls == [str(repo_root)]

    def test_issue_create_with_canonical_origin_scope_still_succeeds(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]

            issue_gateway = _StubIssueGateway([812])
            git_gateway = _StubGitGateway(origin_repo_slug="Example/Repo")
            node_repo = _StubNodeRepo(records)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                issue_gateway=issue_gateway,
                git_gateway=git_gateway,
                node_repo=node_repo,
            )

            result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )

            assert result.node.id == "iss-00812"
            assert result.node.github_issue_number == 812
            assert len(issue_gateway.calls) == 1
            assert issue_gateway.calls[0][0] == str(repo_root)
            assert issue_gateway.calls[0][1] == "Refresh token"
            assert "Type: issue" in issue_gateway.calls[0][2]
            assert git_gateway.calls[0] == str(repo_root)
            created_record = node_repo._records[-1]
            assert created_record.github_repo_owner == "example"
            assert created_record.github_repo_name == "repo"

    def test_initiative_link_existing_first_node_binds_current_repo_scope(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            git_gateway = _StubGitGateway(origin_repo_slug="Example/Repo")
            node_repo = _StubNodeRepo([])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=[],
                git_gateway=git_gateway,
                node_repo=node_repo,
            )

            result = app_create_node.create_initiative(
                app_contracts.CreateNodeRequest(
                    title="Auth platform",
                    slug=None,
                    parent_id=None,
                    github_mode="link_existing",
                    github_issue_number=811,
                ),
                ports,
            )

            assert result.node.id == "init-00811"
            created_record = node_repo._records[-1]
            assert created_record.github_issue_number == 811
            assert created_record.github_repo_owner == "example"
            assert created_record.github_repo_name == "repo"
            assert git_gateway.calls == [str(repo_root)]

    def test_issue_link_existing_same_repo_scope_succeeds_and_persists_canonical_scope(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            git_gateway = _StubGitGateway(origin_repo_slug="Example/Repo")
            node_repo = _StubNodeRepo(records)
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                git_gateway=git_gateway,
                node_repo=node_repo,
            )

            result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode="link_existing",
                    github_issue_number=812,
                    github_repo_owner="Example",
                    github_repo_name="Repo",
                ),
                ports,
            )

            assert result.node.id == "iss-00812"
            created_record = node_repo._records[-1]
            assert created_record.github_repo_owner == "example"
            assert created_record.github_repo_name == "repo"
            assert git_gateway.calls == [str(repo_root)]

    def test_issue_link_existing_rejects_explicit_cross_repo_target(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            git_gateway = _StubGitGateway(origin_repo_slug="example/repo")
            issue_gateway = _StubIssueGateway([812])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                git_gateway=git_gateway,
                issue_gateway=issue_gateway,
            )

            with pytest.raises(
                RuntimeError,
                match="cross-repo GitHub linkage is not supported: requested repo=other/repo current repo=example/repo",
            ):
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="link_existing",
                        github_issue_number=812,
                        github_repo_owner="other",
                        github_repo_name="repo",
                    ),
                    ports,
                )
            assert issue_gateway.calls == []
            assert git_gateway.calls == [str(repo_root)]

    def test_plan_node_creation_rejects_cross_repo_overlap_without_local_fallback(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-00812-auth-platform"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-00812",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=812,
                    github_repo_owner="other",
                    github_repo_name="repo",
                )
            ]
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records)
            graph = app_create_node.load_graph(ports, validate=False)

            with pytest.raises(RuntimeError, match="cross-repo GitHub linkage is not supported"):
                app_create_node.plan_node_creation(
                    app_contracts.CreateNodeRequest(
                        title="Payments",
                        slug=None,
                        parent_id=None,
                        github_mode="link_existing",
                        github_issue_number=812,
                    ),
                    graph,
                    kind="initiative",
                    specdock_dir=specdock_dir,
                    today="2026-03-12",
                    current_repo_slug="example/repo",
                )

    def test_issue_create_gateway_failure_is_pre_github_fail_without_created_issue_hint(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]

            class _IssueCreateFailureGateway(_StubIssueGateway):
                def issue_create(self, repo_root, title, body):
                    self.calls.append((str(repo_root), title, body))
                    raise RuntimeError("simulated issue_create failure")

            issue_gateway = _IssueCreateFailureGateway([799])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )
            with pytest.raises(RuntimeError, match="simulated issue_create failure") as raised:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            assert "Outcome: pre_github_fail" in str(raised.value)
            assert "GitHub issue was created:" not in str(raised.value)
            assert len(issue_gateway.calls) == 1
            assert events == []

    def test_github_create_parent_precheck_fails_before_github_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            cases = [
                (
                    "epic-missing-initiative",
                    app_create_node.create_epic,
                    {
                        "title": "JWT auth",
                        "slug": None,
                        "parent_id": "init-local-99999",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                    "Initiative not found: init-local-99999",
                ),
                (
                    "issue-missing-epic",
                    app_create_node.create_issue,
                    {
                        "title": "Refresh token",
                        "slug": None,
                        "parent_id": "epic-local-99999",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                    "Epic not found: epic-local-99999",
                ),
            ]
            for case_name, create_fn, request_kwargs, expected_error in cases:
                with _case_label(case=case_name):
                    issue_gateway = _StubIssueGateway([798])
                    ports = self._ports(
                        app_ports,
                        specdock_dir=specdock_dir,
                        records=records,
                        events=events,
                        issue_gateway=issue_gateway,
                    )
                    with pytest.raises(RuntimeError, match=expected_error) as raised:
                        create_fn(app_contracts.CreateNodeRequest(**request_kwargs), ports)
                    assert "Outcome: pre_github_fail" in str(raised.value)
                    assert "GitHub issue was created:" not in str(raised.value)
                    assert issue_gateway.calls == []

    def test_github_create_local_parent_path_collision_fails_before_github_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        for case_name in ("initiative", "epic", "issue"):
            with _case_label(case=case_name), tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                specdock_dir = repo_root / "spec-dock"
                self._prepare_templates(specdock_dir)

                init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
                epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
                initiative_record = _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                )
                epic_record = _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                )
                if case_name == "initiative":
                    create_fn = app_create_node.create_initiative
                    records = []
                    request = app_contracts.CreateNodeRequest(
                        title="Payments",
                        slug=None,
                        parent_id=None,
                        github_mode="create",
                        github_issue_number=None,
                    )
                    collision_path = specdock_dir / "initiatives"
                elif case_name == "epic":
                    create_fn = app_create_node.create_epic
                    records = [initiative_record]
                    request = app_contracts.CreateNodeRequest(
                        title="JWT auth",
                        slug=None,
                        parent_id="init-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    )
                    collision_path = init_dir / "epics"
                else:
                    create_fn = app_create_node.create_issue
                    records = [initiative_record, epic_record]
                    request = app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    )
                    collision_path = epic_dir / "issues"

                events: list[str] = []
                issue_gateway = _StubIssueGateway([794])
                ports = self._ports(
                    app_ports,
                    specdock_dir=specdock_dir,
                    records=records,
                    events=events,
                    issue_gateway=issue_gateway,
                )
                collision_path.parent.mkdir(parents=True, exist_ok=True)
                collision_path.write_text("existing-collision\n", encoding="utf-8")

                with pytest.raises(RuntimeError, match="Destination already exists") as raised:
                    create_fn(request, ports)

                assert "Outcome: pre_github_fail" in str(raised.value)
                assert "GitHub issue was created:" not in str(raised.value)
                assert issue_gateway.calls == []
                assert events == []
                assert collision_path.read_text(encoding="utf-8") == "existing-collision\n"
                assert not (specdock_dir / "system" / ".runtime" / "create.lock").exists()

    def test_github_create_missing_rules_source_fails_before_github_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            cases = [
                (
                    "initiative",
                    app_create_node.create_initiative,
                    {
                        "title": "Payments",
                        "slug": None,
                        "parent_id": None,
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                    specdock_dir / "docs" / "rules" / "initiative" / "artifacts.md",
                ),
                (
                    "epic",
                    app_create_node.create_epic,
                    {
                        "title": "JWT auth",
                        "slug": None,
                        "parent_id": "init-local-00001",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                    specdock_dir / "docs" / "rules" / "epic" / "artifacts.md",
                ),
                (
                    "issue",
                    app_create_node.create_issue,
                    {
                        "title": "Refresh token",
                        "slug": None,
                        "parent_id": "epic-local-00001",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                    specdock_dir / "docs" / "rules" / "issue" / "artifacts.md",
                ),
            ]
            for case_name, create_fn, request_kwargs, missing_rules_path in cases:
                with _case_label(case=case_name):
                    self._prepare_templates(specdock_dir)
                    missing_rules_path.unlink()
                    events: list[str] = []
                    issue_gateway = _StubIssueGateway([796])
                    ports = self._ports(
                        app_ports,
                        specdock_dir=specdock_dir,
                        records=records,
                        events=events,
                        issue_gateway=issue_gateway,
                    )

                    with pytest.raises(RuntimeError, match="Missing rules source") as raised:
                        create_fn(app_contracts.CreateNodeRequest(**request_kwargs), ports)

                    assert "Outcome: pre_github_fail" in str(raised.value)
                    assert "GitHub issue was created:" not in str(raised.value)
                    assert issue_gateway.calls == []
                    assert events == []

    def test_github_create_symlink_preflight_fails_before_github_create(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            epic_dir.mkdir(parents=True, exist_ok=True)

            initiative_record = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth platform",
                path=init_dir,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            )
            epic_record = _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                title="JWT auth",
                path=epic_dir,
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
                github_issue_number=None,
            )
            cases = [
                (
                    "initiative",
                    app_create_node.create_initiative,
                    [],
                    {
                        "title": "Payments",
                        "slug": None,
                        "parent_id": None,
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                ),
                (
                    "epic",
                    app_create_node.create_epic,
                    [initiative_record],
                    {
                        "title": "JWT auth",
                        "slug": None,
                        "parent_id": "init-local-00001",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                ),
                (
                    "issue",
                    app_create_node.create_issue,
                    [initiative_record, epic_record],
                    {
                        "title": "Refresh token",
                        "slug": None,
                        "parent_id": "epic-local-00001",
                        "github_mode": "create",
                        "github_issue_number": None,
                    },
                ),
            ]
            for case_name, create_fn, records, request_kwargs in cases:
                with _case_label(case=case_name):
                    events: list[str] = []
                    issue_gateway = _StubIssueGateway([795])
                    ports = self._ports(
                        app_ports,
                        specdock_dir=specdock_dir,
                        records=records,
                        events=events,
                        issue_gateway=issue_gateway,
                    )

                    with (
                        _patch_object(app_create_node.os, "symlink", side_effect=OSError("operation not permitted")),
                        pytest.raises(RuntimeError, match="Symlink creation preflight failed") as raised,
                    ):
                        create_fn(app_contracts.CreateNodeRequest(**request_kwargs), ports)

                    assert "Outcome: pre_github_fail" in str(raised.value)
                    assert "GitHub issue was created:" not in str(raised.value)
                    assert issue_gateway.calls == []
                    assert events == []

    def test_github_create_graph_preflight_fails_before_github_create_for_initiative(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []

            init_a = specdock_dir / "initiatives" / "init-local-00001-auth-platform-a"
            init_b = specdock_dir / "initiatives" / "init-local-00001-auth-platform-b"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform A",
                    path=init_a,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform B",
                    path=init_b,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]

            issue_gateway = _StubIssueGateway([797])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )
            with pytest.raises(RuntimeError, match=r"(?i)duplicate id") as raised:
                app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Payments",
                        slug=None,
                        parent_id=None,
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )
            assert "Outcome: pre_github_fail" in str(raised.value)
            assert "GitHub issue was created:" not in str(raised.value)
            assert issue_gateway.calls == []

    def test_initiative_and_epic_post_create_failures_report_retry_link_guidance(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events: list[str] = []
            issue_gateway = _StubIssueGateway([706])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=[],
                events=events,
                issue_gateway=issue_gateway,
            )

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "token=holder\npid=222\nuser=lock-holder\ncreated_unix=9999999999\ncreated_iso=2099-01-01\n",
                encoding="utf-8",
            )

            with (
                _patch_dict(
                    os.environ,
                    {
                        app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS: "0.02",
                        app_create_node._ENV_CREATE_LOCK_POLL_SECONDS: "0.005",
                        app_create_node._ENV_CREATE_LOCK_STALE_SECONDS: "3600",
                    },
                    clear=False,
                ),
                pytest.raises(RuntimeError, match="GitHub issue was created: #706") as raised,
            ):
                app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_remote_only_fail" in message
            assert "create lock acquisition failed" in message
            assert f"{runtime_cmd} new initiative --title 'Auth platform'" in message
            assert "--github-issue 706" in message
            assert "close/cleanup" in message
            assert len(issue_gateway.calls) == 1
            assert events == []

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            events = []
            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([707])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                events=events,
                issue_gateway=issue_gateway,
            )

            with (
                _patch_object(
                    app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated epic write failure")
                ),
                pytest.raises(RuntimeError, match="GitHub issue was created: #707") as raised,
            ):
                app_create_node.create_epic(
                    app_contracts.CreateNodeRequest(
                        title="JWT auth",
                        slug=None,
                        parent_id="init-local-00001",
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "Outcome: post_github_local_write_fail" in message
            assert "simulated epic write failure" in message
            assert f"{runtime_cmd} new epic --title 'JWT auth'" in message
            assert "--initiative init-local-00001" in message
            assert "--github-issue 707" in message
            assert "close/cleanup" in message
            assert len(issue_gateway.calls) == 1
            assert events == []

    def test_create_lock_contention_timeout_is_no_write_and_reports_metadata(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "token=holder\npid=222\nuser=lock-holder\ncreated_unix=9999999999\ncreated_iso=2099-01-01\n",
                encoding="utf-8",
            )

            with (
                _patch_dict(
                    os.environ,
                    {
                        app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS: "0.02",
                        app_create_node._ENV_CREATE_LOCK_POLL_SECONDS: "0.005",
                        app_create_node._ENV_CREATE_LOCK_STALE_SECONDS: "3600",
                    },
                    clear=False,
                ),
                pytest.raises(RuntimeError, match="create lock acquisition failed") as raised,
            ):
                app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        github_mode="link_existing",
                        github_issue_number=701,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "wait_s=" in message
            assert lock_path.as_posix() in message
            assert "user=lock-holder" in message
            assert f"{runtime_cmd} doctor" in message
            assert events == []
            assert not (specdock_dir / "initiatives").exists()
            assert lock_path.exists()

    def test_create_lock_stale_is_no_write_and_reports_metadata(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            events = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[], events=events)

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "token=stale-holder\npid=333\nuser=stale-holder\ncreated_unix=0\ncreated_iso=1970-01-01\n",
                encoding="utf-8",
            )

            with (
                _patch_dict(
                    os.environ,
                    {
                        app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS: "0.2",
                        app_create_node._ENV_CREATE_LOCK_POLL_SECONDS: "0.01",
                        app_create_node._ENV_CREATE_LOCK_STALE_SECONDS: "0",
                    },
                    clear=False,
                ),
                pytest.raises(RuntimeError, match="create lock acquisition failed") as raised,
            ):
                app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        github_mode="link_existing",
                        github_issue_number=701,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert "stale=true" in message
            assert lock_path.as_posix() in message
            assert "created_iso=1970-01-01" in message
            assert f"{runtime_cmd} doctor" in message
            assert events == []
            assert not (specdock_dir / "initiatives").exists()
            assert lock_path.exists()

    def test_create_lock_metadata_write_failure_cleans_orphan_lock(self) -> None:
        (
            _runtime_app,
            _app_contracts,
            app_create_node,
            _app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)

            def _raise_write_failure(fd, _payload):
                os.close(fd)
                raise OSError("disk full")

            with (
                _patch_object(app_create_node, "_write_create_lock_payload", side_effect=_raise_write_failure),
                pytest.raises(RuntimeError, match="create lock metadata write failed") as raised,
            ):
                app_create_node._acquire_create_lock(specdock_dir)

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert lock_path.as_posix() in message
            assert "cleanup_unlink=ok" in message
            assert f"{runtime_cmd} doctor" in message
            assert not lock_path.exists()

    def test_create_fails_when_release_unlink_fails(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            self._prepare_templates(specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[])

            lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
            original_unlink = app_create_node.Path.unlink

            def _unlink_with_failure(path_self, missing_ok=False):
                if path_self == lock_path:
                    raise OSError("permission denied")
                return original_unlink(path_self, missing_ok=missing_ok)

            with (
                _patch_object(app_create_node.Path, "unlink", new=_unlink_with_failure),
                pytest.raises(RuntimeError, match="create lock release failed") as raised,
            ):
                app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        github_mode="link_existing",
                        github_issue_number=701,
                    ),
                    ports,
                )

            message = str(raised.value)
            runtime_cmd = _quoted_runtime_entrypoint(specdock_dir)
            assert lock_path.as_posix() in message
            assert f"{runtime_cmd} doctor" in message
            assert (specdock_dir / "initiatives").exists()
            assert lock_path.exists()

    def test_github_mode_default_create_matrix(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
            epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth platform",
                    path=init_dir,
                    parent_id=None,
                    initiative_id=None,
                    epic_id=None,
                    github_issue_number=None,
                ),
                _record(
                    infra_contracts,
                    kind="epic",
                    node_id="epic-local-00001",
                    title="JWT auth",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            issue_gateway = _StubIssueGateway([701, 702, 703])
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=records,
                issue_gateway=issue_gateway,
            )

            app_create_node.create_initiative(
                app_contracts.CreateNodeRequest(
                    title="Payments",
                    slug=None,
                    parent_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="OAuth",
                    slug=None,
                    parent_id="init-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            assert len(issue_gateway.calls) == 2

            issue_result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            assert len(issue_gateway.calls) == 3
            assert issue_result.node.id == "iss-00703"

    def test_execute_create_plan_reuse_seam(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[])

            calls = []
            original_execute = app_create_node.execute_create_plan
            original_guard = app_create_node._post_write_duplicate_guard

            def _fake_execute(plan, ports_arg):
                calls.append((plan.meta.id, ports_arg))
                return [plan.dest_dir / "README.md", plan.dest_dir / ".meta.json"]

            app_create_node.execute_create_plan = _fake_execute
            app_create_node._post_write_duplicate_guard = lambda _ports_arg, *, node_id: None
            try:
                result = app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        github_mode="link_existing",
                        github_issue_number=701,
                    ),
                    ports,
                )
            finally:
                app_create_node.execute_create_plan = original_execute
                app_create_node._post_write_duplicate_guard = original_guard

            assert len(calls) == 1
            assert result.created_paths[-1].name == ".meta.json"

    def test_renderer_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_create_node,
            _app_ports,
            _new_commands,
            _infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        node = app_contracts.SpecNode(
            kind="issue",
            id="iss-00123",
            title="Add refresh token",
            slug="add-refresh-token",
            path=Path(
                "/repo/spec-dock/initiatives/init-00001-auth/epics/epic-00001-jwt/issues/iss-00123-add-refresh-token"
            ),
            meta_path=Path(
                "/repo/spec-dock/initiatives/init-00001-auth/epics/epic-00001-jwt/issues/iss-00123-add-refresh-token/.meta.json"
            ),
            parent_id="epic-00001",
            initiative_id="init-00001",
            epic_id="epic-00001",
            github_issue_number=123,
        )
        result = app_contracts.CreateNodeResult(node=node, created_paths=[], warnings=[])
        text = presentation_cli_text.render_new_node_text(result)
        assert text.stdout_lines == [
            (
                "spec-dock: ok (new issue) "
                "id=iss-00123 epic=epic-00001 initiative=init-00001 "
                "path=spec-dock/initiatives/init-00001-auth/epics/epic-00001-jwt/issues/iss-00123-add-refresh-token "
                "github=#123"
            )
        ]

    def test_command_new_initiative_smoke(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_create_node,
            _app_ports,
            new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        calls = []

        def _unexpected(_req):
            raise AssertionError("unexpected use case call")

        def _fake_create(req):
            calls.append(req)
            node = app_contracts.SpecNode(
                kind="initiative",
                id="init-local-00001",
                title=req.title,
                slug="auth-platform",
                path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform"),
                meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-auth-platform/.meta.json"),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=None,
            )
            return app_contracts.CreateNodeResult(node=node, created_paths=[], warnings=[])

        use_cases = app_contracts.UseCases(
            create_initiative=_fake_create,
            create_epic=_unexpected,
            create_issue=_unexpected,
            create_artifact_doc=_unexpected,
            import_initiative=_unexpected,
            import_epic=_unexpected,
            import_issue=_unexpected,
            set_active=_unexpected,
            show_active=_unexpected,
            clear_active=_unexpected,
            sync=_unexpected,
            check_deps=_unexpected,
            validate_tree=_unexpected,
        )
        outcome = new_commands._run_new_initiative(
            new_commands.NewInitiativeArgs(
                title="Auth platform",
                slug=None,
                create_github_issue=False,
                github_issue_number=None,
            ),
            use_cases,
        )

        assert len(calls) == 1
        assert calls[0].github_mode == "create"
        assert outcome.exit_code == 0
        assert "spec-dock: ok (new initiative)" in "\n".join(outcome.text.stdout_lines)
