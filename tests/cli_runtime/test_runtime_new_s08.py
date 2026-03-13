import tempfile
import sys
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import create_node as app_create_node
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.commands import new as new_commands
        from spec_dock_runtime.infra import contracts as infra_contracts
        from spec_dock_runtime.presentation import cli_text as presentation_cli_text
    finally:
        sys.path.pop(0)
    return runtime_app, app_contracts, app_create_node, app_ports, new_commands, infra_contracts, presentation_cli_text


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


class _StubClock:
    def today(self):
        return "2026-03-12"


class TestRuntimeNewS08(unittest.TestCase):
    def _prepare_templates(self, specdock_dir: Path) -> None:
        for kind in ("initiative", "epic", "issue"):
            template_root = specdock_dir / "templates" / kind
            (template_root / "docs").mkdir(parents=True, exist_ok=True)
            (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\n", encoding="utf-8")
            (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\n", encoding="utf-8")

    def _ports(self, app_ports, *, specdock_dir: Path, records, events=None, issue_gateway=None):
        return app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records, events=events),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=issue_gateway or _StubIssueGateway([501]),
            clock=_StubClock(),
            repo_root=specdock_dir.parent,
            specdock_dir=specdock_dir,
        )

    def test_planning_regression_create_plan_contains_all_candidates(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
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
                requested_node_id=None,
                github_mode="local_only",
                github_issue_number=None,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
            )

            self.assertEqual(plan.meta.id, "init-local-00001")
            self.assertEqual(plan.meta.kind, "initiative")
            self.assertTrue(plan.dest_dir.as_posix().endswith("init-local-00001-auth-platform"))
            self.assertEqual(plan.planned_paths[-1], plan.dest_dir / ".meta.json")
            self.assertIn(plan.dest_dir / "README.md", plan.planned_paths)
            self.assertIn(plan.dest_dir / "docs" / "checklist.md", plan.planned_paths)

    def test_execution_regression_and_write_order(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
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
                requested_node_id=None,
                github_mode="local_only",
                github_issue_number=None,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
            )
            created_paths = app_create_node.execute_create_plan(plan, ports)

            self.assertEqual(events[:2], ["copy_scaffolded_tree", "write_meta"])
            self.assertEqual(created_paths[-1], plan.dest_dir / ".meta.json")
            self.assertEqual(created_paths[:-1], sorted(created_paths[:-1], key=lambda p: p.as_posix()))
            self.assertTrue((plan.dest_dir / ".meta.json").exists())
            self.assertTrue((plan.dest_dir / "README.md").exists())

    def test_full_candidate_set_no_write_preflight_collision(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
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
                requested_node_id=None,
                github_mode="local_only",
                github_issue_number=None,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
            )
            collision = plan.dest_dir / "docs" / "checklist.md"
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_text("existing", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Destination already exists"):
                app_create_node.execute_create_plan(plan, ports)

            self.assertEqual(events, [])
            self.assertFalse((plan.dest_dir / ".meta.json").exists())

    def test_collision_on_meta_is_no_write(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
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
                requested_node_id=None,
                github_mode="local_only",
                github_issue_number=None,
            )
            plan = app_create_node.plan_node_creation(
                req,
                graph,
                kind="initiative",
                specdock_dir=specdock_dir,
                today="2026-03-12",
            )
            plan.dest_dir.mkdir(parents=True, exist_ok=True)
            (plan.dest_dir / ".meta.json").write_text("stale", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Destination already exists"):
                app_create_node.execute_create_plan(plan, ports)

            self.assertEqual(events, [])
            self.assertFalse((plan.dest_dir / "README.md").exists())

    def test_per_kind_parity_create_local(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
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

            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records)
            init_result = app_create_node.create_initiative(
                app_contracts.CreateNodeRequest(
                    title="Payment platform",
                    slug=None,
                    parent_id=None,
                    requested_node_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            self.assertEqual(init_result.node.kind, "initiative")
            self.assertEqual(init_result.node.id, "init-local-00002")

            epic_result = app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="OAuth",
                    slug=None,
                    parent_id="init-local-00001",
                    requested_node_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            self.assertEqual(epic_result.node.kind, "epic")
            self.assertEqual(epic_result.node.parent_id, "init-local-00001")

            issue_result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="local_only",
                    github_issue_number=None,
                ),
                ports,
            )
            self.assertEqual(issue_result.node.kind, "issue")
            self.assertEqual(issue_result.node.parent_id, "epic-local-00001")
            self.assertEqual(issue_result.node.initiative_id, "init-local-00001")

    def test_github_mode_default_no_side_effect_matrix(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
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
            issue_gateway = _StubIssueGateway([777])
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
                    requested_node_id=None,
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
                    requested_node_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            self.assertEqual(issue_gateway.calls, [])

            issue_result = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode=None,
                    github_issue_number=None,
                ),
                ports,
            )
            self.assertEqual(len(issue_gateway.calls), 1)
            self.assertEqual(issue_result.node.id, "iss-00777")

    def test_execute_create_plan_reuse_seam(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_templates(specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[])

            calls = []
            original_execute = app_create_node.execute_create_plan

            def _fake_execute(plan, ports_arg):
                calls.append((plan.meta.id, ports_arg))
                return [plan.dest_dir / "README.md", plan.dest_dir / ".meta.json"]

            app_create_node.execute_create_plan = _fake_execute
            try:
                result = app_create_node.create_initiative(
                    app_contracts.CreateNodeRequest(
                        title="Auth platform",
                        slug=None,
                        parent_id=None,
                        requested_node_id=None,
                        github_mode=None,
                        github_issue_number=None,
                    ),
                    ports,
                )
            finally:
                app_create_node.execute_create_plan = original_execute

            self.assertEqual(len(calls), 1)
            self.assertEqual(result.created_paths[-1].name, ".meta.json")

    def test_renderer_text_regression(self) -> None:
        _runtime_app, app_contracts, _app_create_node, _app_ports, _new_commands, _infra_contracts, presentation_cli_text = _runtime_modules()
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
        self.assertEqual(
            text.stdout_lines,
            [
                (
                    "spec-dock: ok (new issue) "
                    "id=iss-00123 epic=epic-00001 initiative=init-00001 "
                    "path=spec-dock/initiatives/init-00001-auth/epics/epic-00001-jwt/issues/iss-00123-add-refresh-token "
                    "github=#123"
                )
            ],
        )

    def test_command_new_initiative_smoke(self) -> None:
        _runtime_app, app_contracts, _app_create_node, _app_ports, new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
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
            create_discussion_doc=_unexpected,
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
                node_id=None,
                create_github_issue=False,
                github_issue_number=None,
                no_github=True,
            ),
            use_cases,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].github_mode, "local_only")
        self.assertEqual(outcome.exit_code, 0)
        self.assertIn("spec-dock: ok (new initiative)", "\n".join(outcome.text.stdout_lines))


if __name__ == "__main__":
    unittest.main()
