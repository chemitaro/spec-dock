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
        self.loaded_paths: list[Path] = []

    def render_text(self, text, replacements):
        self.events.append("render_text")
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered

    def load_template_text(self, src_path):
        self.events.append("load_template_text")
        self.loaded_paths.append(src_path)
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


class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"


class _StubClock:
    def now_iso(self):
        return "2026-03-12T01:02:03+00:00"

    def today(self):
        return "2026-03-12"


class TestRuntimeNewDocS09(unittest.TestCase):
    def _create_lock_path(self, specdock_dir: Path) -> Path:
        return specdock_dir / "system" / ".runtime" / "create.lock"

    def _prepare_discussion_templates(self, specdock_dir: Path) -> None:
        templates_dir = specdock_dir / "templates" / "discussions"
        templates_dir.mkdir(parents=True, exist_ok=True)
        placeholders = {
            "adr": ("<ADR_ID>", "<ADR_TITLE>"),
            "disc": ("<DISC_ID>", "<DISC_TITLE>"),
            "research": ("<RESEARCH_ID>", "<RESEARCH_TITLE>"),
            "interview": ("<INTERVIEW_ID>", "<INTERVIEW_TITLE>"),
            "scratch": ("<SCRATCH_ID>", "<SCRATCH_TITLE>"),
        }
        for doc_type, (id_placeholder, title_placeholder) in placeholders.items():
            (templates_dir / f"{doc_type}.md").write_text(
                (
                    f"type={doc_type}\n"
                    f"id={id_placeholder}\n"
                    f"title={title_placeholder}\n"
                    "scope=<SCOPE_ID>\n"
                    "author=<YOUR_NAME>\n"
                    "date=YYYY-MM-DD\n"
                ),
                encoding="utf-8",
            )
        for scope_kind, id_placeholder, title_placeholder in (
            ("initiative", "<INIT_ID>", "<INIT_TITLE>"),
            ("epic", "<EPIC_ID>", "<EPIC_TITLE>"),
            ("issue", "<ISS_ID>", "<ISS_TITLE>"),
        ):
            scope_template_dir = specdock_dir / "templates" / scope_kind
            scope_template_dir.mkdir(parents=True, exist_ok=True)
            for target in ("requirement", "design", "plan"):
                (scope_template_dir / f"{target}.md").write_text(
                    (
                        "---\n"
                        f"kind={scope_kind}-{target}\n"
                        "---\n"
                        f"body={scope_kind}-{target} {id_placeholder} {title_placeholder}\n"
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
        rules_path = specdock_dir / "docs" / "rules" / "issue" / "discussions.md"
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("issue discussions rules\n", encoding="utf-8")

    def _ports(self, app_ports, *, specdock_dir: Path, records, events=None):
        return app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=_StubIssueGateway(),
            git_gateway=_StubGitGateway(),
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

    def _scope_records(self, infra_contracts, *, specdock_dir: Path):
        init_dir = specdock_dir / "initiatives" / "init-local-00001-auth"
        epic_dir = init_dir / "epics" / "epic-local-00001-login"
        issue_dir = epic_dir / "issues" / "iss-local-00001-refresh-token"
        return [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth platform",
                path=init_dir,
                parent_id=None,
                initiative_id="init-local-00001",
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
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Refresh token",
                path=issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            ),
        ]

    def test_timestamp_regression_and_planning(self) -> None:
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
                timestamp="20260312t010203z",
            )

            self.assertEqual(template_path, specdock_dir / "templates" / "discussions" / "adr.md")
            self.assertEqual(dest_path.name, "20260312t010203z-adr-decision-one.md")
            self.assertEqual(replacements["<ADR_ID>"], "20260312t010203z-adr")
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
                    doc_type="scratch",
                    scope_node_id="iss-local-00001",
                    title="Note one",
                    slug=None,
                ),
                ports,
            )

            self.assertEqual(result.doc_id, "20260312t010203z-scratch")
            self.assertEqual(result.doc_type, "scratch")
            self.assertEqual(result.path.name, "20260312t010203z-scratch-note-one.md")
            self.assertTrue(result.path.exists())
            self.assertEqual(events, ["load_template_text", "render_text", "write_text"])

            content = result.path.read_text(encoding="utf-8")
            self.assertIn("type=scratch", content)
            self.assertIn("id=20260312t010203z-scratch", content)
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
                "adr": "20260312t010203z-adr",
                "disc": "20260312t010203z-01-disc",
                "research": "20260312t010203z-02-research",
                "interview": "20260312t010203z-03-interview",
                "scratch": "20260312t010203z-04-scratch",
            }
            for doc_type in ("adr", "disc", "research", "interview", "scratch"):
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

    def test_report_and_reflection_are_not_creatable_discussion_doc_types(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            for doc_type in ("report", "reflection"):
                with self.subTest(doc_type=doc_type):
                    with self.assertRaisesRegex(RuntimeError, f"Unknown discussion doc type: {doc_type}"):
                        app_create_node.create_discussion_doc(
                            app_contracts.CreateDiscussionDocRequest(
                                doc_type=doc_type,
                                scope_node_id="iss-local-00001",
                                title=f"{doc_type} title",
                                slug=None,
                            ),
                            ports,
                        )

    def test_draft_doc_types_render_scope_specific_template_bodies(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            discussions_template_dir = specdock_dir / "templates" / "discussions"
            for doc_type in ("draft-requirement", "draft-design", "draft-plan"):
                (discussions_template_dir / f"{doc_type}.md").write_text(
                    f"type={doc_type}\nenvelope=discussion-draft-template\n",
                    encoding="utf-8",
                )
            records = self._scope_records(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records)

            scope_ids = {
                "initiative": "init-local-00001",
                "epic": "epic-local-00001",
                "issue": "iss-local-00001",
            }
            target_by_doc_type = {
                "draft-requirement": "requirement",
                "draft-design": "design",
                "draft-plan": "plan",
            }
            for scope_kind, scope_id in scope_ids.items():
                for doc_type, target in target_by_doc_type.items():
                    title = f"{scope_kind} {target}"
                    result = app_create_node.create_discussion_doc(
                        app_contracts.CreateDiscussionDocRequest(
                            doc_type=doc_type,
                            scope_node_id=scope_id,
                            title=title,
                            slug=None,
                        ),
                        ports,
                    )
                    self.assertRegex(
                        result.doc_id,
                        rf"^20260312t010203z(?:-[0-9]{{2}})?-{doc_type}$",
                    )
                    self.assertRegex(result.path.name, rf"^20260312t010203z(?:-[0-9]{{2}})?-{doc_type}-")
                    self.assertEqual(
                        ports.template_scaffolder.loaded_paths[-1],
                        specdock_dir / "templates" / scope_kind / f"{target}.md",
                    )
                    content = result.path.read_text(encoding="utf-8")
                    self.assertIn(f"kind={scope_kind}-{target}", content)
                    self.assertIn(f"body={scope_kind}-{target}", content)
                    self.assertNotIn(f"type={doc_type}", content)
                    self.assertNotIn("envelope=discussion-draft-template", content)
                    self.assertNotIn("template=templates/", content)
                    self.assertNotIn("target=", content)

            suffix_results = [
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type=doc_type,
                        scope_node_id="iss-local-00001",
                        title=f"{doc_type} collision",
                        slug=None,
                    ),
                    ports,
                )
                for doc_type in ("draft-requirement", "draft-design", "draft-plan")
            ]
            self.assertEqual(
                [result.doc_id for result in suffix_results],
                [
                    "20260312t010203z-03-draft-requirement",
                    "20260312t010203z-04-draft-design",
                    "20260312t010203z-05-draft-plan",
                ],
            )

    def test_suffix_exhaustion_fail_fast_no_write(self) -> None:
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
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")
            for nn in range(1, 100):
                (discussions_dir / f"20260312t010203z-{nn:02d}-disc-second-{nn:02d}.md").write_text(
                    "second\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(RuntimeError, "Discussion timestamp suffix exhaustion"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            self.assertEqual(list(discussions_dir.glob("20260312t010203z-*-scratch-*.md")), [])

    def test_duplicate_timestamp_corruption_fail_fast_no_write(self) -> None:
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
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260312t010203z-disc-second.md").write_text("second\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Duplicate discussion timestamp slot detected"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            lock_path = self._create_lock_path(specdock_dir)
            self.assertFalse(lock_path.exists())
            self.assertFalse(lock_path.parent.exists())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.glob("*.md")),
                [
                    "20260312t010203z-adr-first.md",
                    "20260312t010203z-disc-second.md",
                ],
            )

    def test_duplicate_timestamp_suffix_corruption_fail_fast_no_lock_no_write(self) -> None:
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
            (discussions_dir / "20260312t010203z-01-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260312t010203z-01-disc-second.md").write_text("second\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Duplicate discussion timestamp suffix detected"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            lock_path = self._create_lock_path(specdock_dir)
            self.assertFalse(lock_path.exists())
            self.assertFalse(lock_path.parent.exists())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.glob("*.md")),
                [
                    "20260312t010203z-01-adr-first.md",
                    "20260312t010203z-01-disc-second.md",
                ],
            )

    def test_duplicate_timestamp_corruption_post_lock_rescan_fail_no_write(self) -> None:
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
            first_name = "20260312t010203z-adr-first.md"
            second_name = "20260312t010203z-disc-second.md"
            lock_path = self._create_lock_path(specdock_dir)
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(app_create_node._build_create_lock_metadata("holder"), encoding="utf-8")
            self.assertTrue(lock_path.exists())

            scan_snapshots: list[list[str]] = []
            original_scan = app_create_node._scan_discussion_timestamp_duplicate_state

            def _wrapped_scan(target_dir):
                scan_snapshots.append(sorted(path.name for path in target_dir.glob("*.md")))
                return original_scan(target_dir)

            def _release_and_corrupt() -> None:
                time.sleep(0.1)
                (discussions_dir / first_name).write_text("first\n", encoding="utf-8")
                (discussions_dir / second_name).write_text("second\n", encoding="utf-8")
                lock_path.unlink()

            worker = threading.Thread(target=_release_and_corrupt)
            worker.start()
            try:
                with patch.object(
                    app_create_node,
                    "_scan_discussion_timestamp_duplicate_state",
                    side_effect=_wrapped_scan,
                ):
                    with self.assertRaisesRegex(RuntimeError, "Duplicate discussion timestamp slot detected"):
                        app_create_node.create_discussion_doc(
                            app_contracts.CreateDiscussionDocRequest(
                                doc_type="scratch",
                                scope_node_id="iss-local-00001",
                                title="Note one",
                                slug=None,
                            ),
                            ports,
                        )
            finally:
                worker.join(timeout=5.0)
            self.assertFalse(worker.is_alive(), "lock release worker did not finish")

            self.assertEqual(scan_snapshots, [[first_name, second_name]])
            self.assertEqual(events, [])
            self.assertFalse(lock_path.exists())
            self.assertEqual(
                sorted(path.name for path in discussions_dir.glob("*.md")),
                [first_name, second_name],
            )

    def test_malformed_discussion_candidate_fail_fast_pre_lock_no_write(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        cases = (
            "20260312t010203z-adr.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with self.subTest(malformed_name=malformed_name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    specdock_dir = repo_root / "spec-dock"
                    self._prepare_discussion_templates(specdock_dir)
                    issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
                    events: list[str] = []
                    ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

                    discussions_dir = Path(issue_record.path) / "discussions"
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    (discussions_dir / malformed_name).write_text("broken\n", encoding="utf-8")

                    with self.assertRaisesRegex(RuntimeError, "Malformed discussion document filename"):
                        app_create_node.create_discussion_doc(
                            app_contracts.CreateDiscussionDocRequest(
                                doc_type="scratch",
                                scope_node_id="iss-local-00001",
                                title="Note one",
                                slug=None,
                            ),
                            ports,
                        )

                    self.assertEqual(events, [])
                    lock_path = self._create_lock_path(specdock_dir)
                    self.assertFalse(lock_path.exists())
                    self.assertFalse(lock_path.parent.exists())
                    self.assertEqual(sorted(path.name for path in discussions_dir.glob("*.md")), [malformed_name])

    def test_malformed_timestamp_intent_variant_fail_fast_pre_lock_no_write(self) -> None:
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
            malformed_name = "20260329x-adr-kickoff.md"
            (discussions_dir / malformed_name).write_text("broken\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Malformed discussion document filename"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            self.assertEqual(events, [])
            lock_path = self._create_lock_path(specdock_dir)
            self.assertFalse(lock_path.exists())
            self.assertFalse(lock_path.parent.exists())
            self.assertEqual(sorted(path.name for path in discussions_dir.glob("*.md")), [malformed_name])

    def test_malformed_discussion_candidate_post_lock_rescan_fail_no_write(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        cases = (
            "20260329x-adr-kickoff.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with self.subTest(malformed_name=malformed_name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    specdock_dir = repo_root / "spec-dock"
                    self._prepare_discussion_templates(specdock_dir)
                    issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
                    events: list[str] = []
                    ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

                    discussions_dir = Path(issue_record.path) / "discussions"
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    lock_path = self._create_lock_path(specdock_dir)
                    lock_path.parent.mkdir(parents=True, exist_ok=True)
                    lock_path.write_text(app_create_node._build_create_lock_metadata("holder"), encoding="utf-8")
                    self.assertTrue(lock_path.exists())

                    scan_snapshots: list[list[str]] = []
                    original_scan = app_create_node._scan_discussion_timestamp_duplicate_state

                    def _wrapped_scan(target_dir):
                        scan_snapshots.append(sorted(path.name for path in target_dir.glob("*.md")))
                        return original_scan(target_dir)

                    def _release_and_corrupt() -> None:
                        time.sleep(0.1)
                        (discussions_dir / malformed_name).write_text("broken\n", encoding="utf-8")
                        lock_path.unlink()

                    worker = threading.Thread(target=_release_and_corrupt)
                    worker.start()
                    try:
                        with patch.object(
                            app_create_node,
                            "_scan_discussion_timestamp_duplicate_state",
                            side_effect=_wrapped_scan,
                        ):
                            with self.assertRaisesRegex(RuntimeError, "Malformed discussion document filename"):
                                app_create_node.create_discussion_doc(
                                    app_contracts.CreateDiscussionDocRequest(
                                        doc_type="scratch",
                                        scope_node_id="iss-local-00001",
                                        title="Note one",
                                        slug=None,
                                    ),
                                    ports,
                                )
                    finally:
                        worker.join(timeout=5.0)
                    self.assertFalse(worker.is_alive(), "lock release worker did not finish")

                    self.assertEqual(scan_snapshots, [[malformed_name]])
                    self.assertEqual(events, [])
                    self.assertFalse(lock_path.exists())
                    self.assertEqual(sorted(path.name for path in discussions_dir.glob("*.md")), [malformed_name])

    def test_parallel_new_doc_allocates_unique_suffixes(self) -> None:
        _runtime_app, app_contracts, app_create_node, app_ports, _new_commands, infra_contracts, _presentation_cli_text = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            original_allocate = app_create_node._allocate_discussion_doc_filename
            first_call_pending = {"value": True}
            first_call_lock = threading.Lock()

            def _slow_allocate(discussions_dir, *, timestamp, doc_type, slug):
                allocated = original_allocate(
                    discussions_dir,
                    timestamp=timestamp,
                    doc_type=doc_type,
                    slug=slug,
                )
                with first_call_lock:
                    if first_call_pending["value"]:
                        first_call_pending["value"] = False
                        time.sleep(0.1)
                return allocated

            with patch.object(app_create_node, "_allocate_discussion_doc_filename", side_effect=_slow_allocate):
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
            doc_ids = sorted(result.doc_id for result in results)
            self.assertEqual(len([doc_id for doc_id in doc_ids if "-01-" in doc_id]), 1)
            self.assertEqual(len([doc_id for doc_id in doc_ids if "-01-" not in doc_id]), 1)
            self.assertEqual(sorted(result.doc_type for result in results), ["adr", "disc"])

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
                    github_mode="create",
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
            doc_id="20260312t010203z-03-adr",
            doc_type="adr",
            scope_node_id="iss-local-00001",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                "issues/iss-local-00001-refresh-token/discussions/20260312t010203z-03-adr-decision-one.md"
            ),
            warnings=[],
        )
        text = presentation_cli_text.render_new_doc_text(result)
        self.assertEqual(
            text.stdout_lines,
            [
                (
                    "spec-dock: ok (new doc) "
                    "type=adr id=20260312t010203z-03-adr scope=iss-local-00001 "
                    "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                    "issues/iss-local-00001-refresh-token/discussions/20260312t010203z-03-adr-decision-one.md"
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
                doc_id="20260312t010203z-adr",
                doc_type="adr",
                scope_node_id=req.scope_node_id,
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                    "issues/iss-local-00001-refresh-token/discussions/20260312t010203z-adr-decision-one.md"
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
        self.assertIn(
            "spec-dock: ok (new doc) type=adr id=20260312t010203z-adr",
            "\n".join(outcome.text.stdout_lines),
        )


if __name__ == "__main__":
    unittest.main()
