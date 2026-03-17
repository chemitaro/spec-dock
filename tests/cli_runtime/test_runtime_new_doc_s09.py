import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch


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
    def __init__(self, records):
        self._records = list(records)

    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)

    def write_meta(self, dest_dir, record):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / ".meta.json").write_text(f"id={record.id}\n", encoding="utf-8")
        self._records.append(record)


class _StubTemplateScaffolder:
    def __init__(self, events=None):
        self.events = events if events is not None else []

    def render_text(self, text, replacements):
        self.events.append("render_text")
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered

    def load_template_text(self, src_path):
        self.events.append("load_template_text")
        return src_path.read_text(encoding="utf-8")

    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(src_dir.rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dest_path = dest_dir / rel
            if dest_path.exists():
                raise RuntimeError(f"Destination already exists: {dest_path}")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            text = src_path.read_text(encoding="utf-8")
            dest_path.write_text(self.render_text(text, replacements), encoding="utf-8")
            created.append(dest_path)
        return created

    def write_text(self, dest_path, text):
        self.events.append("write_text")
        if dest_path.exists():
            raise RuntimeError(f"Destination already exists: {dest_path}")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8")


class _StubIssueGateway:
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []

    def issue_create(self, repo_root, title, body):
        del repo_root, title, body
        return 999


class _StubClock:
    def today(self):
        return "2026-03-12"


class TestRuntimeNewDocS09(unittest.TestCase):
    def _prepare_discussion_templates(self, specdock_dir: Path) -> None:
        templates_dir = specdock_dir / "templates" / "discussions"
        templates_dir.mkdir(parents=True, exist_ok=True)
        for doc_type in ("adr", "disc", "research", "note"):
            (templates_dir / f"{doc_type}.md").write_text(
                (
                    f"type={doc_type}\n"
                    "id=<ADR_ID>\n"
                    "title=<ADR_TITLE>\n"
                    "scope=<SCOPE_ID>\n"
                    "author=<YOUR_NAME>\n"
                    "date=YYYY-MM-DD\n"
                ),
                encoding="utf-8",
            )

    def _prepare_node_templates(self, specdock_dir: Path) -> None:
        issue_template = specdock_dir / "templates" / "issue"
        issue_template.mkdir(parents=True, exist_ok=True)
        (issue_template / "README.md").write_text(
            "issue=<ISS_ID> epic=<EPIC_ID> init=<INIT_ID>\n",
            encoding="utf-8",
        )

    def _ports(self, app_ports, *, specdock_dir: Path, records, events=None):
        return app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=_StubIssueGateway(),
            clock=_StubClock(),
            repo_root=specdock_dir.parent,
            specdock_dir=specdock_dir,
        )

    def _run_parallel_doc_create(self, create_fn, request_a, request_b):
        results = []
        errors = []
        lock = threading.Lock()

        def _worker(req):
            try:
                result = create_fn(req)
                with lock:
                    results.append(result)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        thread_a = threading.Thread(target=_worker, args=(request_a,))
        thread_b = threading.Thread(target=_worker, args=(request_b,))
        thread_a.start()
        thread_b.start()
        thread_a.join(timeout=5.0)
        thread_b.join(timeout=5.0)
        self.assertFalse(thread_a.is_alive(), "parallel new doc thread A did not finish")
        self.assertFalse(thread_b.is_alive(), "parallel new doc thread B did not finish")
        self.assertEqual(errors, [])
        return results

    def _issue_scope_record(self, infra_contracts, *, specdock_dir: Path):
        init_dir = specdock_dir / "initiatives" / "init-local-00001-auth"
        epic_dir = init_dir / "epics" / "epic-local-00001-login"
        issue_dir = epic_dir / "issues" / "iss-local-00001-refresh-token"
        return _record(
            infra_contracts,
            kind="issue",
            node_id="iss-local-00001",
            title="Refresh token",
            path=issue_dir,
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        )

    def test_sequence_regression_and_planning(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            graph = app_create_node.load_graph(ports, validate=False)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "adr-00001-legacy.md").write_text("legacy\n", encoding="utf-8")
            (discussions_dir / "foo.md").write_text("nonconforming\n", encoding="utf-8")
            (discussions_dir / "002-bogus-random.md").write_text("nonconforming type\n", encoding="utf-8")
            (discussions_dir / "009-disc-migrated.md").write_text("existing\n", encoding="utf-8")
            (discussions_dir / "1000-adr-legacy-overflow.md").write_text("ignored\n", encoding="utf-8")

            template_path, dest_path, replacements = app_create_node.plan_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="adr",
                    scope_node_id="iss-local-00001",
                    title="Decision one",
                    slug=None,
                ),
                graph,
                today="2026-03-12",
            )

            self.assertEqual(template_path, specdock_dir / "templates" / "discussions" / "adr.md")
            self.assertEqual(dest_path.name, "010-adr-decision-one.md")
            self.assertEqual(replacements["<ADR_ID>"], "010-adr")
            self.assertEqual(replacements["<SCOPE_ID>"], "iss-local-00001")

    def test_generated_path_name_content_regression(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="note",
                    scope_node_id="iss-local-00001",
                    title="Note one",
                    slug=None,
                ),
                ports,
            )

            self.assertEqual(result.doc_id, "001-note")
            self.assertEqual(result.doc_type, "note")
            self.assertTrue(result.path.name.startswith("001-note-note-one"))
            self.assertTrue(result.path.exists())
            self.assertEqual(events, ["load_template_text", "render_text", "write_text"])

            content = result.path.read_text(encoding="utf-8")
            self.assertIn("type=note", content)
            self.assertIn("id=001-note", content)
            self.assertIn("title=Note one", content)
            self.assertIn("scope=iss-local-00001", content)
            self.assertIn("date=2026-03-12", content)

    def test_doc_type_parity_template_selection_regression(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            expected_ids = {
                "adr": "001-adr",
                "disc": "002-disc",
                "research": "003-research",
                "note": "004-note",
            }
            for doc_type in ("adr", "disc", "research", "note"):
                result = app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type=doc_type,
                        scope_node_id="iss-local-00001",
                        title=f"{doc_type} title",
                        slug=None,
                    ),
                    ports,
                )
                self.assertEqual(result.doc_type, doc_type)
                self.assertEqual(result.doc_id, expected_ids[doc_type])
                content = result.path.read_text(encoding="utf-8")
                self.assertIn(f"type={doc_type}", content)
                self.assertIn(f"id={expected_ids[doc_type]}", content)

    def test_duplicate_sequence_fail_fast_no_write(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Duplicate discussion sequence"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="note",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            self.assertEqual(list(discussions_dir.glob("002-note-*.md")), [])

    def test_parallel_new_doc_allocates_unique_sequences(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            original_next = app_create_node._next_discussion_doc_seq
            first_call_pending = {"value": True}
            first_call_lock = threading.Lock()

            def _slow_next(discussions_dir):
                seq = original_next(discussions_dir)
                with first_call_lock:
                    if first_call_pending["value"]:
                        first_call_pending["value"] = False
                        time.sleep(0.1)
                return seq

            with patch.object(app_create_node, "_next_discussion_doc_seq", side_effect=_slow_next):
                results = self._run_parallel_doc_create(
                    lambda req: app_create_node.create_discussion_doc(req, ports),
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="adr",
                        scope_node_id="iss-local-00001",
                        title="Decision one",
                        slug=None,
                    ),
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="disc",
                        scope_node_id="iss-local-00001",
                        title="Discussion one",
                        slug=None,
                    ),
                )

            self.assertEqual(len(results), 2)
            seqs = sorted(int(result.doc_id.split("-", 1)[0]) for result in results)
            self.assertEqual(seqs, [1, 2])
            doc_types = sorted(result.doc_type for result in results)
            self.assertEqual(doc_types, ["adr", "disc"])

    def test_invalid_slug_fail_fast_no_write(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)
            discussions_dir = Path(issue_record.path) / "discussions"

            with self.assertRaisesRegex(RuntimeError, "--slug is invalid"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="adr",
                        scope_node_id="iss-local-00001",
                        title="Decision one",
                        slug="invalid_slug",
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            self.assertEqual(list(discussions_dir.glob("*.md")), [])

    def test_new_node_non_regression_for_shared_file_edits(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_discussion_templates(specdock_dir)

            init_dir = specdock_dir / "initiatives" / "init-local-00001-auth"
            epic_dir = init_dir / "epics" / "epic-local-00001-login"
            records = [
                _record(
                    infra_contracts,
                    kind="initiative",
                    node_id="init-local-00001",
                    title="Auth",
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
                    title="Login",
                    path=epic_dir,
                    parent_id="init-local-00001",
                    initiative_id="init-local-00001",
                    epic_id=None,
                    github_issue_number=None,
                ),
            ]
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records)
            result = app_create_node.create_issue(
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

            self.assertEqual(result.node.kind, "issue")
            self.assertEqual(result.node.parent_id, "epic-local-00001")
            self.assertTrue((result.node.path / "README.md").exists())

    def test_renderer_text_regression(self) -> None:
        _runtime_app, app_contracts, _app_create_node, _app_ports, _new_commands, _infra_contracts, presentation_cli_text = _runtime_modules()
        result = app_contracts.CreateDiscussionDocResult(
            doc_id="003-adr",
            doc_type="adr",
            scope_node_id="iss-local-00001",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                "issues/iss-local-00001-refresh-token/discussions/003-adr-decision-one.md"
            ),
            warnings=[],
        )
        text = presentation_cli_text.render_new_doc_text(result)
        self.assertEqual(
            text.stdout_lines,
            [
                (
                    "spec-dock: ok (new doc) "
                    "type=adr id=003-adr scope=iss-local-00001 "
                    "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                    "issues/iss-local-00001-refresh-token/discussions/003-adr-decision-one.md"
                )
            ],
        )

    def test_command_new_doc_smoke(self) -> None:
        _runtime_app, app_contracts, _app_create_node, _app_ports, new_commands, _infra_contracts, _presentation_cli_text = _runtime_modules()
        calls = []

        def _unexpected(_req):
            raise AssertionError("unexpected use case call")

        def _fake_create(req):
            calls.append(req)
            return app_contracts.CreateDiscussionDocResult(
                doc_id="001-adr",
                doc_type="adr",
                scope_node_id=req.scope_node_id,
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                    "issues/iss-local-00001-refresh-token/discussions/001-adr-decision-one.md"
                ),
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=_unexpected,
            create_epic=_unexpected,
            create_issue=_unexpected,
            create_discussion_doc=_fake_create,
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
        outcome = new_commands._run_new_doc(
            new_commands.NewDocArgs(
                doc_type="adr",
                scope_node_id="iss-local-00001",
                scope_kind="issue",
                title="Decision one",
                slug=None,
            ),
            use_cases,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].doc_type, "adr")
        self.assertEqual(calls[0].scope_node_id, "iss-local-00001")
        self.assertEqual(outcome.exit_code, 0)
        self.assertIn("spec-dock: ok (new doc) type=adr id=001-adr", "\n".join(outcome.text.stdout_lines))


if __name__ == "__main__":
    unittest.main()
