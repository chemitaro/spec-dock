import contextlib
from pathlib import Path
import re
import sys
import tempfile
import threading
import time

import pytest

_MISSING = object()


class _CallProbe:
    def __init__(self, *, side_effect=_MISSING, return_value=_MISSING):
        self.calls = []
        self._side_effect = side_effect
        self._return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self._side_effect is not _MISSING:
            if isinstance(self._side_effect, BaseException):
                raise self._side_effect
            return self._side_effect(*args, **kwargs)
        if self._return_value is not _MISSING:
            return self._return_value
        return None

    def assert_called_once_with(self, *args, **kwargs):
        assert self.calls == [(args, kwargs)]


@contextlib.contextmanager
def _patch_object(target, name, replacement=_MISSING, *, side_effect=_MISSING, return_value=_MISSING):
    original = getattr(target, name)
    if replacement is _MISSING:
        replacement = _CallProbe(side_effect=side_effect, return_value=return_value)
    setattr(target, name, replacement)
    try:
        yield replacement
    finally:
        setattr(target, name, original)


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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


class _SequenceClock:
    def __init__(self, *values: str):
        self._values = list(values)
        self.calls: list[str] = []

    def now_iso(self):
        value = self._values[len(self.calls)] if len(self.calls) < len(self._values) else self._values[-1]
        self.calls.append(value)
        return value

    def today(self):
        return "2026-03-12"


class TestRuntimeNewDocS09:
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
            "pr-repair-batch": ("<PR_REPAIR_BATCH_ID>", "<PR_REPAIR_BATCH_TITLE>"),
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

    def _ports(self, app_ports, *, specdock_dir: Path, records, events=None, clock=None):
        return app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records),
            template_scaffolder=_StubTemplateScaffolder(events=events),
            issue_gateway=_StubIssueGateway(),
            git_gateway=_StubGitGateway(),
            clock=clock if clock is not None else _StubClock(),
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
        assert not thread_a.is_alive(), "parallel new doc thread A did not finish"
        assert not thread_b.is_alive(), "parallel new doc thread B did not finish"
        assert errors == []
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

            assert template_path == specdock_dir / "templates" / "discussions" / "adr.md"
            assert dest_path.name == "20260312t010203z-adr-decision-one.md"
            assert replacements["<ADR_ID>"] == "20260312t010203z-adr"
            assert replacements["<SCOPE_ID>"] == "iss-local-00001"

    def test_generated_path_name_content_regression(self) -> None:
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

            assert result.doc_id == "20260312t010203z-scratch"
            assert result.doc_type == "scratch"
            assert result.path.name == "20260312t010203z-scratch-note-one.md"
            assert result.path.exists()
            assert events == ["load_template_text", "render_text", "write_text"]

            content = result.path.read_text(encoding="utf-8")
            assert "type=scratch" in content
            assert "id=20260312t010203z-scratch" in content
            assert "title=Note one" in content
            assert "scope=iss-local-00001" in content
            assert "date=2026-03-12" in content

    def test_doc_type_parity_template_selection_regression(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            expected_ids = {
                "adr": "20260312t010203z-adr",
                "disc": "20260312t010203z-01-disc",
                "research": "20260312t010203z-02-research",
                "interview": "20260312t010203z-03-interview",
                "scratch": "20260312t010203z-04-scratch",
                "pr-repair-batch": "20260312t010203z-05-pr-repair-batch",
            }
            for doc_type in ("adr", "disc", "research", "interview", "scratch", "pr-repair-batch"):
                result = app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type=doc_type,
                        scope_node_id="iss-local-00001",
                        title=f"{doc_type} title",
                        slug=None,
                    ),
                    ports,
                )
                assert result.doc_type == doc_type
                assert result.doc_id == expected_ids[doc_type]
                content = result.path.read_text(encoding="utf-8")
                assert f"type={doc_type}" in content
                assert f"id={expected_ids[doc_type]}" in content

    def test_report_and_reflection_are_not_creatable_discussion_doc_types(self) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            for doc_type in ("report", "reflection"):
                with pytest.raises(RuntimeError, match=f"Unknown discussion doc type: {doc_type}"):
                    app_create_node.create_discussion_doc(
                        app_contracts.CreateDiscussionDocRequest(
                            doc_type=doc_type,
                            scope_node_id="iss-local-00001",
                            title=f"{doc_type} title",
                            slug=None,
                        ),
                        ports,
                    )

    def test_draft_doc_types_render_scope_specific_template_bodies(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            discussions_template_dir = specdock_dir / "templates" / "discussions"
            for doc_type in ("draft-requirement", "draft-design", "draft-plan"):
                (discussions_template_dir / f"{doc_type}.md").write_text(
                    f"type={doc_type}\nenvelope=discussion-draft-template\n",
                    encoding="utf-8",
                )
            records = self._scope_records(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=records)
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

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
                    assert re.search(rf"^20260312t010203z(?:-[0-9]{{2}})?-{doc_type}$", result.doc_id)
                    assert re.search(rf"^20260312t010203z(?:-[0-9]{{2}})?-{doc_type}-", result.path.name)
                    assert (
                        ports.template_scaffolder.loaded_paths[-1]
                        == specdock_dir / "templates" / scope_kind / f"{target}.md"
                    )
                    content = result.path.read_text(encoding="utf-8")
                    assert f"kind={scope_kind}-{target}" in content
                    assert f"body={scope_kind}-{target}" in content
                    assert f"type={doc_type}" not in content
                    assert "envelope=discussion-draft-template" not in content
                    assert "template=templates/" not in content
                    assert "target=" not in content

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
            assert [result.doc_id for result in suffix_results] == [
                "20260312t010203z-03-draft-requirement",
                "20260312t010203z-04-draft-design",
                "20260312t010203z-05-draft-plan",
            ]

    def test_occupied_timestamp_with_advancing_clock_uses_later_unsuffixed_doc(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            clock = _SequenceClock("2026-03-12T01:02:03+00:00", "2026-03-12T01:02:04+00:00")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], clock=clock)
            sleep_calls: list[float] = []

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")

            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", sleep_calls.append)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="scratch",
                    scope_node_id="iss-local-00001",
                    title="Later slot",
                    slug=None,
                ),
                ports,
            )

            assert result.doc_id == "20260312t010204z-scratch"
            assert result.path.name == "20260312t010204z-scratch-later-slot.md"
            assert sleep_calls == [0.05]
            assert clock.calls == ["2026-03-12T01:02:03+00:00", "2026-03-12T01:02:04+00:00"]

    def test_retry_day_rollover_renders_date_from_allocated_timestamp(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            clock = _SequenceClock("2026-03-12T23:59:59+00:00", "2026-03-13T00:00:00+00:00")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], clock=clock)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t235959z-adr-first.md").write_text("first\n", encoding="utf-8")

            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="pr-repair-batch",
                    scope_node_id="iss-local-00001",
                    title="PR Repair Batch",
                    slug=None,
                ),
                ports,
            )

            assert result.doc_id == "20260313t000000z-pr-repair-batch"
            assert result.path.name == "20260313t000000z-pr-repair-batch-pr-repair-batch.md"
            content = result.path.read_text(encoding="utf-8")
            assert "date=2026-03-13" in content
            assert "id=20260313t000000z-pr-repair-batch" in content

    def test_draft_retry_day_rollover_renders_date_from_allocated_timestamp(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            (specdock_dir / "templates" / "issue" / "plan.md").write_text(
                'ID: "<ISS_ID>"\n最終更新: "YYYY-MM-DD"\n',
                encoding="utf-8",
            )
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            clock = _SequenceClock("2026-03-12T23:59:59+00:00", "2026-03-13T00:00:00+00:00")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], clock=clock)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t235959z-adr-first.md").write_text("first\n", encoding="utf-8")

            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="draft-plan",
                    scope_node_id="iss-local-00001",
                    title="Draft Plan",
                    slug=None,
                ),
                ports,
            )

            assert result.doc_id == "20260313t000000z-draft-plan"
            assert result.path.name == "20260313t000000z-draft-plan-draft-plan.md"
            content = result.path.read_text(encoding="utf-8")
            assert 'ID: "iss-local-00001"' in content
            assert '最終更新: "2026-03-13"' in content

    def test_frozen_clock_uses_suffix_after_bounded_wait(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            clock = _SequenceClock(
                "2026-03-12T01:02:03+00:00",
                "2026-03-12T01:02:03+00:00",
                "2026-03-12T01:02:03+00:00",
            )
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], clock=clock)
            sleep_calls: list[float] = []

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")

            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "0.1")
            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "0.05")
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", sleep_calls.append)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="scratch",
                    scope_node_id="iss-local-00001",
                    title="Frozen slot",
                    slug=None,
                ),
                ports,
            )

            assert result.doc_id == "20260312t010203z-01-scratch"
            assert result.path.name == "20260312t010203z-01-scratch-frozen-slot.md"
            assert sleep_calls == [0.05, 0.05]

    def test_later_occupied_timestamp_exhaustion_falls_back_to_original_family(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            clock = _SequenceClock(
                "2026-03-12T01:02:03+00:00",
                "2026-03-12T01:02:04+00:00",
                "2026-03-12T01:02:04+00:00",
            )
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], clock=clock)
            sleep_calls: list[float] = []

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260312t010204z-adr-later.md").write_text("later\n", encoding="utf-8")
            for nn in range(1, 100):
                (discussions_dir / f"20260312t010204z-{nn:02d}-disc-later-{nn:02d}.md").write_text(
                    "later suffix\n",
                    encoding="utf-8",
                )

            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "0.1")
            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "0.05")
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", sleep_calls.append)

            result = app_create_node.create_discussion_doc(
                app_contracts.CreateDiscussionDocRequest(
                    doc_type="scratch",
                    scope_node_id="iss-local-00001",
                    title="Original family fallback",
                    slug=None,
                ),
                ports,
            )

            assert result.doc_id == "20260312t010203z-01-scratch"
            assert result.path.name == "20260312t010203z-01-scratch-original-family-fallback.md"
            assert sleep_calls == [0.05, 0.05]

    @pytest.mark.parametrize(
        ("env_name", "value"),
        (
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "0"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "-0.1"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "not-a-number"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "0"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "-0.1"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "0.0005"),
            ("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "not-a-number"),
        ),
    )
    def test_invalid_discussion_timestamp_wait_env_fails_fast(self, monkeypatch, env_name, value) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")

            monkeypatch.setenv(env_name, value)
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            with pytest.raises(RuntimeError, match=f"Invalid {env_name}"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Invalid env",
                        slug=None,
                    ),
                    ports,
                )

            assert list(discussions_dir.glob("*scratch-invalid-env.md")) == []

    def test_suffix_exhaustion_fail_fast_no_write(self, monkeypatch) -> None:
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

            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_WAIT_SECONDS", "0.01")
            monkeypatch.setenv("SPEC_DOCK_DISCUSSION_TIMESTAMP_POLL_SECONDS", "0.005")
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            with pytest.raises(RuntimeError, match="Discussion timestamp suffix exhaustion"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            assert events == []
            assert list(discussions_dir.glob("20260312t010203z-*-scratch-*.md")) == []

    def test_duplicate_timestamp_corruption_fail_fast_no_write(self) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260312t010203z-disc-second.md").write_text("second\n", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Duplicate discussion timestamp slot detected"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            assert events == []
            lock_path = self._create_lock_path(specdock_dir)
            assert not lock_path.exists()
            assert not lock_path.parent.exists()
            assert sorted(path.name for path in discussions_dir.glob("*.md")) == [
                "20260312t010203z-adr-first.md",
                "20260312t010203z-disc-second.md",
            ]

    def test_duplicate_timestamp_suffix_corruption_fail_fast_no_lock_no_write(self) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260312t010203z-01-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260312t010203z-01-disc-second.md").write_text("second\n", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Duplicate discussion timestamp suffix detected"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            assert events == []
            lock_path = self._create_lock_path(specdock_dir)
            assert not lock_path.exists()
            assert not lock_path.parent.exists()
            assert sorted(path.name for path in discussions_dir.glob("*.md")) == [
                "20260312t010203z-01-adr-first.md",
                "20260312t010203z-01-disc-second.md",
            ]

    def test_duplicate_timestamp_corruption_post_lock_rescan_fail_no_write(self) -> None:
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
            assert lock_path.exists()

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
                with (
                    _patch_object(
                        app_create_node,
                        "_scan_discussion_timestamp_duplicate_state",
                        side_effect=_wrapped_scan,
                    ),
                    pytest.raises(RuntimeError, match="Duplicate discussion timestamp slot detected"),
                ):
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
            assert not worker.is_alive(), "lock release worker did not finish"

            assert scan_snapshots == [[first_name, second_name]]
            assert events == []
            assert not lock_path.exists()
            assert sorted(path.name for path in discussions_dir.glob("*.md")) == [first_name, second_name]

    def test_malformed_discussion_candidate_fail_fast_pre_lock_no_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        cases = (
            "20260312t010203z-adr.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
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

                with pytest.raises(RuntimeError, match="Malformed discussion document filename"):
                    app_create_node.create_discussion_doc(
                        app_contracts.CreateDiscussionDocRequest(
                            doc_type="scratch",
                            scope_node_id="iss-local-00001",
                            title="Note one",
                            slug=None,
                        ),
                        ports,
                    )

                assert events == []
                lock_path = self._create_lock_path(specdock_dir)
                assert not lock_path.exists()
                assert not lock_path.parent.exists()
                assert sorted(path.name for path in discussions_dir.glob("*.md")) == [malformed_name]

    def test_malformed_timestamp_intent_variant_fail_fast_pre_lock_no_write(self) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)

            discussions_dir = Path(issue_record.path) / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            malformed_name = "20260329x-adr-kickoff.md"
            (discussions_dir / malformed_name).write_text("broken\n", encoding="utf-8")

            with pytest.raises(RuntimeError, match="Malformed discussion document filename"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="scratch",
                        scope_node_id="iss-local-00001",
                        title="Note one",
                        slug=None,
                    ),
                    ports,
                )

            assert events == []
            lock_path = self._create_lock_path(specdock_dir)
            assert not lock_path.exists()
            assert not lock_path.parent.exists()
            assert sorted(path.name for path in discussions_dir.glob("*.md")) == [malformed_name]

    def test_malformed_discussion_candidate_post_lock_rescan_fail_no_write(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        cases = (
            "20260329x-adr-kickoff.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
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
                assert lock_path.exists()

                scan_snapshots: list[list[str]] = []
                original_scan = app_create_node._scan_discussion_timestamp_duplicate_state

                def _wrapped_scan(target_dir, *, scan_snapshots=scan_snapshots, original_scan=original_scan):
                    scan_snapshots.append(sorted(path.name for path in target_dir.glob("*.md")))
                    return original_scan(target_dir)

                def _release_and_corrupt(
                    *,
                    discussions_dir=discussions_dir,
                    malformed_name=malformed_name,
                    lock_path=lock_path,
                ) -> None:
                    time.sleep(0.1)
                    (discussions_dir / malformed_name).write_text("broken\n", encoding="utf-8")
                    lock_path.unlink()

                worker = threading.Thread(target=_release_and_corrupt)
                worker.start()
                try:
                    with (
                        _patch_object(
                            app_create_node,
                            "_scan_discussion_timestamp_duplicate_state",
                            side_effect=_wrapped_scan,
                        ),
                        pytest.raises(RuntimeError, match="Malformed discussion document filename"),
                    ):
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
                assert not worker.is_alive(), "lock release worker did not finish"

                assert scan_snapshots == [[malformed_name]]
                assert events == []
                assert not lock_path.exists()
                assert sorted(path.name for path in discussions_dir.glob("*.md")) == [malformed_name]

    def test_parallel_new_doc_allocates_unique_suffixes(self, monkeypatch) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            monkeypatch.setattr(app_create_node, "_sleep_discussion_timestamp_poll", lambda _seconds: None)

            original_allocate = app_create_node._allocate_discussion_doc_filename
            first_call_pending = {"value": True}
            first_call_lock = threading.Lock()

            def _slow_allocate(discussions_dir, *, timestamp, doc_type, slug, **kwargs):
                allocated = original_allocate(
                    discussions_dir,
                    timestamp=timestamp,
                    doc_type=doc_type,
                    slug=slug,
                    **kwargs,
                )
                with first_call_lock:
                    if first_call_pending["value"]:
                        first_call_pending["value"] = False
                        time.sleep(0.1)
                return allocated

            with _patch_object(app_create_node, "_allocate_discussion_doc_filename", side_effect=_slow_allocate):
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

            assert len(results) == 2
            doc_ids = sorted(result.doc_id for result in results)
            assert len([doc_id for doc_id in doc_ids if "-01-" in doc_id]) == 1
            assert len([doc_id for doc_id in doc_ids if "-01-" not in doc_id]) == 1
            assert sorted(result.doc_type for result in results) == ["adr", "disc"]

    def test_invalid_slug_fail_fast_no_write(self) -> None:
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
            self._prepare_discussion_templates(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            events: list[str] = []
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record], events=events)
            discussions_dir = Path(issue_record.path) / "discussions"

            with pytest.raises(RuntimeError, match="--slug is invalid"):
                app_create_node.create_discussion_doc(
                    app_contracts.CreateDiscussionDocRequest(
                        doc_type="adr",
                        scope_node_id="iss-local-00001",
                        title="Decision one",
                        slug="invalid_slug",
                    ),
                    ports,
                )

            assert events == []
            assert list(discussions_dir.glob("*.md")) == []

    def test_new_node_non_regression_for_shared_file_edits(self) -> None:
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
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )

            assert result.node.kind == "issue"
            assert result.node.parent_id == "epic-local-00001"
            assert (result.node.path / "README.md").exists()

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
        assert text.stdout_lines == [
            (
                "spec-dock: ok (new doc) "
                "type=adr id=20260312t010203z-03-adr scope=iss-local-00001 "
                "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                "issues/iss-local-00001-refresh-token/discussions/20260312t010203z-03-adr-decision-one.md"
            )
        ]

    def test_command_new_doc_smoke(self) -> None:
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

        assert len(calls) == 1
        assert calls[0].doc_type == "adr"
        assert calls[0].scope_node_id == "iss-local-00001"
        assert outcome.exit_code == 0
        assert "spec-dock: ok (new doc) type=adr id=20260312t010203z-adr" in "\n".join(outcome.text.stdout_lines)
