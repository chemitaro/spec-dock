import contextlib
import importlib
import os
from pathlib import Path
import re
import shutil
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


def _artifact_runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        app_create_artifact_doc = importlib.import_module("spec_dock_runtime.application.create_artifact_doc")
        from spec_dock_runtime.application import contracts as app_contracts, ports as app_ports
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return app_create_artifact_doc, app_contracts, app_ports, infra_contracts


def _snapshot_tree(root: Path) -> list[tuple[str, str, bytes | str]]:
    snapshot: list[tuple[str, str, bytes | str]] = []
    for path in sorted(root.rglob("*"), key=lambda candidate: candidate.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot.append((relative, "symlink", path.readlink().as_posix()))
        elif path.is_dir():
            snapshot.append((relative, "directory", ""))
        else:
            snapshot.append((relative, "file", path.read_bytes()))
    return snapshot


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

    def write_meta_at(self, dest_dir_fd, record):
        meta_fd = os.open(".meta.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644, dir_fd=dest_dir_fd)
        try:
            os.write(meta_fd, f"id={record.id}\n".encode())
        finally:
            os.close(meta_fd)
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

    def copy_scaffolded_tree_at(self, src_dir, dest_dir, dest_dir_fd, replacements):
        from spec_dock_runtime.infra import template_scaffolder

        self.events.append("copy_scaffolded_tree")
        return template_scaffolder.copy_scaffolded_tree_at(src_dir, dest_dir, dest_dir_fd, replacements)

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
        rules_dir = specdock_dir / "docs" / "rules" / "issue"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "artifacts.md").write_text("issue artifacts rules\n", encoding="utf-8")
        (rules_dir / "discussions.md").write_text("issue discussions rules\n", encoding="utf-8")

    def _prepare_blank_artifact_template(self, specdock_dir: Path) -> None:
        templates_dir = specdock_dir / "templates" / "artifacts"
        templates_dir.mkdir(parents=True, exist_ok=True)
        (templates_dir / "blank.md").write_text(
            "id=<ARTIFACT_ID>\ntitle=<ARTIFACT_TITLE>\nscope=<SCOPE_ID>\n",
            encoding="utf-8",
        )

    def _prepare_exhausted_artifact_slots(
        self,
        specdock_dir: Path,
        issue_record,
        *,
        include_rules: bool = True,
    ) -> Path:
        artifacts_dir = Path(issue_record.path) / "artifacts"
        artifacts_dir.mkdir(parents=True)
        if include_rules:
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
        timestamp = "20260312t010203z"
        (artifacts_dir / f"{timestamp}-existing.md").write_text("standard\n", encoding="utf-8")
        for suffix in range(1, 100):
            if suffix % 2:
                filename = f"{timestamp}-{suffix:02d}-adr-existing.md"
            else:
                filename = f"{timestamp}-{suffix:02d}-existing.md"
            (artifacts_dir / filename).write_text(f"suffix={suffix}\n", encoding="utf-8")
        return artifacts_dir

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

    def test_pr_repair_batch_continuation_fields_remain_markdown_only_and_runtime_opaque(self) -> None:
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
            template = specdock_dir / "templates" / "discussions" / "pr-repair-batch.md"
            template.write_text(
                (
                    "type=pr-repair-batch\n"
                    "id=<PR_REPAIR_BATCH_ID>\n"
                    "title=<PR_REPAIR_BATCH_TITLE>\n"
                    "scope=<SCOPE_ID>\n"
                    "author=<YOUR_NAME>\n"
                    "date=YYYY-MM-DD\n"
                    "## ChatGPT Consultation Gate\n"
                    "consultation_status: pending\n"
                    "## Integrated Repair Strategy\n"
                    "strategy_delta: pending\n"
                    "orchestrator_disposition: pending\n"
                    "## Iteration Ledger\n"
                    "iteration_count: telemetry only\n"
                ),
                encoding="utf-8",
            )
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            request = app_contracts.CreateDiscussionDocRequest(
                doc_type="pr-repair-batch",
                scope_node_id="iss-local-00001",
                title="PR Repair Batch",
                slug=None,
            )
            result = app_create_node.create_discussion_doc(request, ports)

            assert result.doc_type == "pr-repair-batch"
            assert result.doc_id == "20260312t010203z-pr-repair-batch"
            assert result.path.name == "20260312t010203z-pr-repair-batch-pr-repair-batch.md"
            content = result.path.read_text(encoding="utf-8")
            for marker in (
                "## ChatGPT Consultation Gate",
                "consultation_status: pending",
                "## Integrated Repair Strategy",
                "strategy_delta: pending",
                "orchestrator_disposition: pending",
                "## Iteration Ledger",
                "iteration_count: telemetry only",
            ):
                assert marker in content
            assert request.__dict__ == {
                "doc_type": "pr-repair-batch",
                "scope_node_id": "iss-local-00001",
                "title": "PR Repair Batch",
                "slug": None,
                "scope_kind": None,
            }

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

    def test_parallel_new_artifact_allocates_after_shared_create_lock(self, monkeypatch) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            Path(issue_record.path).mkdir(parents=True)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            acquire_barrier = threading.Barrier(2)
            original_acquire = app_create_artifact_doc._acquire_create_lock

            def _barrier_acquire(specdock_path):
                acquire_barrier.wait(timeout=5.0)
                return original_acquire(specdock_path)

            monkeypatch.setattr(app_create_artifact_doc, "_acquire_create_lock", _barrier_acquire)
            request = app_contracts.CreateArtifactDocRequest(
                artifact_type="blank",
                scope_node_id="iss-local-00001",
                title="ChatGPT Output Shared Slot",
                slug="chatgpt-output-shared-slot",
            )

            results = self._run_parallel_doc_create(
                lambda req: app_create_artifact_doc.create_artifact_doc(req, ports),
                request,
                request,
            )

            assert sorted(result.artifact_id for result in results) == [
                "20260312t010203z",
                "20260312t010203z-01",
            ]
            assert sorted(result.path.name for result in results) == [
                "20260312t010203z-01-chatgpt-output-shared-slot.md",
                "20260312t010203z-chatgpt-output-shared-slot.md",
            ]

    def test_new_artifact_reserves_existing_generic_import_slot(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            generic = artifacts_dir / "20260312t010203z--opaque.bin"
            generic.write_bytes(b"generic sentinel")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            result = app_create_artifact_doc.create_artifact_doc(
                app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="Shared Slot",
                    slug="shared-slot",
                ),
                ports,
            )

            assert result.artifact_id == "20260312t010203z-01"
            assert result.path.name == "20260312t010203z-01-shared-slot.md"
            assert generic.read_bytes() == b"generic sentinel"

    def test_new_artifact_rejects_scope_path_escape_and_symlink_without_write(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)

            outside_scope = repo_root / "outside-scope"
            outside_scope.mkdir()
            escaped_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Escaped issue",
                path=outside_scope,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            )
            escaped_ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[escaped_record])
            request = app_contracts.CreateArtifactDocRequest(
                artifact_type="blank",
                scope_node_id="iss-local-00001",
                title="Unsafe scope",
                slug="unsafe-scope",
            )

            with pytest.raises(RuntimeError, match="Scope path escapes spec-dock initiatives"):
                app_create_artifact_doc.create_artifact_doc(request, escaped_ports)

            assert not (outside_scope / "artifacts").exists()

            linked_scope = (
                specdock_dir
                / "initiatives"
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-login"
                / "issues"
                / "iss-local-00001-refresh-token"
            )
            linked_scope.parent.mkdir(parents=True)
            try:
                linked_scope.symlink_to(outside_scope, target_is_directory=True)
            except (NotImplementedError, OSError):
                return
            linked_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Linked issue",
                path=linked_scope,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=None,
            )
            linked_ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[linked_record])

            with pytest.raises(RuntimeError, match="Scope path escapes spec-dock initiatives"):
                app_create_artifact_doc.create_artifact_doc(request, linked_ports)

            assert not (outside_scope / "artifacts").exists()

    def test_new_artifact_rejects_symlinked_initiatives_root_without_external_write(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as repo_tmp, tempfile.TemporaryDirectory() as external_tmp:
            repo_root = Path(repo_tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)

            external_root = Path(external_tmp) / "external-initiatives"
            external_scope = (
                external_root
                / "init-local-00001-auth"
                / "epics"
                / "epic-local-00001-login"
                / "issues"
                / "iss-local-00001-refresh-token"
            )
            external_scope.mkdir(parents=True)
            sentinel = external_scope / "sentinel.txt"
            sentinel.write_bytes(b"external scope sentinel\n")
            before = _snapshot_tree(external_root)

            initiatives_root = specdock_dir / "initiatives"
            try:
                initiatives_root.symlink_to(external_root, target_is_directory=True)
            except (NotImplementedError, OSError):
                return
            try:
                issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
                ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
                request = app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="Unsafe initiatives root",
                    slug="unsafe-initiatives-root",
                )

                error: RuntimeError | None = None
                try:
                    app_create_artifact_doc.create_artifact_doc(request, ports)
                except RuntimeError as exc:
                    error = exc

                after = _snapshot_tree(external_root)
                assert after == before, f"external initiatives tree mutated: before={before!r}, after={after!r}"
                assert error is not None
                assert "Initiatives root is symlinked" in str(error)
                assert sentinel.read_bytes() == b"external scope sentinel\n"
                assert not (external_scope / "artifacts").exists()
            finally:
                initiatives_root.unlink(missing_ok=True)

    @pytest.mark.parametrize(
        ("failure_case", "error_pattern"),
        (
            ("suffix-exhaustion", "Artifact timestamp suffix exhaustion"),
            ("malformed-candidate", "Malformed artifact filename"),
        ),
    )
    def test_new_artifact_allocation_failure_does_not_materialize_missing_rules(
        self,
        failure_case: str,
        error_pattern: str,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            if failure_case == "suffix-exhaustion":
                artifacts_dir = self._prepare_exhausted_artifact_slots(
                    specdock_dir,
                    issue_record,
                    include_rules=False,
                )
            else:
                artifacts_dir = Path(issue_record.path) / "artifacts"
                artifacts_dir.mkdir(parents=True)
                (artifacts_dir / "20260312t01020x-adr-broken.md").write_text(
                    "malformed sentinel\n",
                    encoding="utf-8",
                )
            before = _snapshot_tree(artifacts_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            with pytest.raises(RuntimeError, match=error_pattern):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Rejected Allocation",
                        slug="rejected-allocation",
                    ),
                    ports,
                )

            assert _snapshot_tree(artifacts_dir) == before
            assert not (artifacts_dir / "rules.md").exists()
            assert not (artifacts_dir / "rules.md").is_symlink()

    def test_new_artifact_success_materializes_missing_rules_after_allocation(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            sentinel = artifacts_dir / "sentinel.bin"
            sentinel.write_bytes(b"existing artifact sentinel")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            result = app_create_artifact_doc.create_artifact_doc(
                app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="Successful Allocation",
                    slug="successful-allocation",
                ),
                ports,
            )

            rules_link = artifacts_dir / "rules.md"
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            assert rules_link.is_symlink()
            assert rules_link.resolve() == rules_source.resolve()
            assert result.path.read_text(encoding="utf-8") == (
                "id=20260312t010203z\ntitle=Successful Allocation\nscope=iss-local-00001\n"
            )
            assert sentinel.read_bytes() == b"existing artifact sentinel"

    def test_new_artifact_success_materializes_missing_directory_and_rules(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            result = app_create_artifact_doc.create_artifact_doc(
                app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="New Artifact Directory",
                    slug="new-artifact-directory",
                ),
                ports,
            )

            artifacts_dir = issue_dir / "artifacts"
            rules_link = artifacts_dir / "rules.md"
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            assert artifacts_dir.is_dir()
            assert rules_link.is_symlink()
            assert rules_link.resolve() == rules_source.resolve()
            assert result.path.is_file()
            assert not any(path.name.endswith(".tmp") for path in artifacts_dir.iterdir())

    def test_new_artifact_post_mkdir_directory_replacement_is_rejected_without_mutation(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            artifacts_dir = issue_dir / "artifacts"
            owned_backup = issue_dir / "artifacts.owned-backup"
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_open_directory = app_create_artifact_doc._open_artifacts_directory
            competitor_before: list[tuple[str, str, bytes | str]] | None = None
            owned_before: list[tuple[str, str, bytes | str]] | None = None
            replaced = False

            def _replace_created_directory_before_open(path, *, expected_identity):
                nonlocal competitor_before, owned_before, replaced
                assert path == artifacts_dir
                replaced = True
                artifacts_dir.rename(owned_backup)
                artifacts_dir.mkdir()
                (artifacts_dir / "competitor.bin").write_bytes(b"competitor directory sentinel")
                competitor_before = _snapshot_tree(artifacts_dir)
                owned_before = _snapshot_tree(owned_backup)
                return original_open_directory(path, expected_identity=expected_identity)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "_open_artifacts_directory",
                _replace_created_directory_before_open,
            )

            with pytest.raises(RuntimeError, match="Artifact directory identity changed"):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Post Mkdir Replacement",
                        slug="post-mkdir-replacement",
                    ),
                    ports,
                )

            assert replaced
            assert competitor_before is not None
            assert owned_before is not None
            assert _snapshot_tree(artifacts_dir) == competitor_before
            assert _snapshot_tree(owned_backup) == owned_before
            assert not (artifacts_dir / "20260312t010203z-post-mkdir-replacement.md").exists()
            assert not (owned_backup / "20260312t010203z-post-mkdir-replacement.md").exists()

    @pytest.mark.parametrize(
        ("failure_stage", "preexisting_artifacts", "preexisting_rules", "error_pattern"),
        (
            ("setup", False, False, "injected artifact rules setup failure"),
            ("renderer", False, False, "injected artifact renderer failure"),
            ("write-before", True, False, "injected artifact write-before failure"),
            ("write-partial", False, False, "injected artifact write-partial failure"),
            ("post-write-guard", True, True, "injected artifact post-write guard failure"),
        ),
    )
    def test_new_artifact_failure_rolls_back_only_attempt_paths(
        self,
        monkeypatch,
        failure_stage: str,
        preexisting_artifacts: bool,
        preexisting_rules: bool,
        error_pattern: str,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            artifacts_dir = issue_dir / "artifacts"
            if preexisting_artifacts:
                artifacts_dir.mkdir()
                (artifacts_dir / "sentinel.bin").write_bytes(b"pre-existing sentinel")
            if preexisting_rules:
                rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
                (artifacts_dir / "rules.md").symlink_to(rules_source)
            before = _snapshot_tree(issue_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            if failure_stage == "setup":
                original_symlink = os.symlink

                def _fail_rules_symlink(src, dst, target_is_directory=False, *, dir_fd=None):
                    if Path(dst).name == "rules.md":
                        raise OSError("injected artifact rules setup failure")
                    return original_symlink(
                        src,
                        dst,
                        target_is_directory=target_is_directory,
                        dir_fd=dir_fd,
                    )

                monkeypatch.setattr(os, "symlink", _fail_rules_symlink)
            elif failure_stage == "renderer":

                def _fail_render(_text, _replacements):
                    raise RuntimeError("injected artifact renderer failure")

                monkeypatch.setattr(ports.template_scaffolder, "render_text", _fail_render)
            elif failure_stage in ("write-before", "write-partial"):

                def _fail_write(descriptor, _text):
                    if failure_stage == "write-partial":
                        os.write(descriptor, b"partial artifact bytes")
                    raise OSError(f"injected artifact {failure_stage} failure")

                monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)
            else:
                original_scan = app_create_artifact_doc.scan_artifact_duplicate_state
                scan_calls = 0

                def _fail_post_write_guard(path):
                    nonlocal scan_calls
                    scan_calls += 1
                    if scan_calls == 2:
                        return "injected artifact post-write guard failure", set()
                    return original_scan(path)

                monkeypatch.setattr(
                    app_create_artifact_doc,
                    "scan_artifact_duplicate_state",
                    _fail_post_write_guard,
                )

            with pytest.raises((OSError, RuntimeError), match=error_pattern):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Transactional Artifact",
                        slug="transactional-artifact",
                    ),
                    ports,
                )

            assert _snapshot_tree(issue_dir) == before
            assert not any(path.name.endswith(".tmp") for path in issue_dir.rglob("*"))

    def test_new_artifact_atomic_publish_does_not_overwrite_or_rollback_competing_destination(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            rules_link = artifacts_dir / "rules.md"
            rules_link.symlink_to(rules_source)
            sentinel = artifacts_dir / "sentinel.bin"
            sentinel.write_bytes(b"pre-existing sentinel")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_publish = app_create_artifact_doc._publish_artifact_temp_no_replace
            competing_dest: Path | None = None

            def _inject_competing_destination(*, temp_path, dest_path, **kwargs):
                nonlocal competing_dest
                competing_dest = dest_path
                dest_path.write_bytes(b"competing writer bytes")
                return original_publish(temp_path=temp_path, dest_path=dest_path, **kwargs)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "_publish_artifact_temp_no_replace",
                _inject_competing_destination,
            )

            try:
                with pytest.raises(RuntimeError, match="Artifact already exists"):
                    app_create_artifact_doc.create_artifact_doc(
                        app_contracts.CreateArtifactDocRequest(
                            artifact_type="blank",
                            scope_node_id="iss-local-00001",
                            title="Publish Race",
                            slug="publish-race",
                        ),
                        ports,
                    )

                assert competing_dest is not None
                assert competing_dest.read_bytes() == b"competing writer bytes"
                assert sentinel.read_bytes() == b"pre-existing sentinel"
                assert rules_link.is_symlink()
                assert rules_link.resolve() == rules_source.resolve()
                assert not any(path.name.endswith(".tmp") for path in artifacts_dir.iterdir())
            finally:
                if competing_dest is not None:
                    competing_dest.unlink(missing_ok=True)

    @pytest.mark.parametrize("competitor_kind", ("regular", "dangling-symlink"))
    def test_new_artifact_temp_claim_race_preserves_competitor(
        self,
        monkeypatch,
        competitor_kind: str,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            external_target = repo_root / "external-temp-target.txt"
            competitor_path: Path | None = None
            original_open = os.open
            injected = False

            def _inject_temp_competitor(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal competitor_path, injected
                candidate = Path(path)
                if not injected and candidate.name.endswith(".tmp"):
                    injected = True
                    competitor_path = artifacts_dir / candidate.name if dir_fd is not None else candidate
                    if competitor_kind == "regular":
                        competitor_path.write_bytes(b"competing temp bytes")
                    else:
                        competitor_path.symlink_to(external_target)
                    raise FileExistsError("injected competing artifact temp")
                if dir_fd is None:
                    return original_open(path, flags, mode)
                return original_open(path, flags, mode, dir_fd=dir_fd)

            def _fail_write(_descriptor, _text):
                raise OSError("injected claimed temp write failure")

            monkeypatch.setattr(os, "open", _inject_temp_competitor)
            monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)

            with pytest.raises((OSError, RuntimeError)):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Temp Claim Race",
                        slug="temp-claim-race",
                    ),
                    ports,
                )

            assert competitor_path is not None
            if competitor_kind == "regular":
                assert competitor_path.read_bytes() == b"competing temp bytes"
            else:
                assert competitor_path.is_symlink()
                assert competitor_path.readlink() == external_target
                assert not external_target.exists()

    @pytest.mark.parametrize("replacement_kind", ("regular", "symlink"))
    def test_new_artifact_temp_replacement_before_publish_preserves_competitor(
        self,
        monkeypatch,
        replacement_kind: str,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            external_target = repo_root / "external-replacement-target.txt"
            original_publish = app_create_artifact_doc._publish_artifact_temp_no_replace
            competitor_path: Path | None = None
            owned_backup: Path | None = None
            dest_path: Path | None = None

            def _replace_before_publish(*, temp_path, dest_path: Path, **kwargs):
                nonlocal competitor_path, owned_backup
                competitor_path = temp_path
                owned_backup = temp_path.with_name(f"{temp_path.name}.owned-backup")
                temp_path.rename(owned_backup)
                if replacement_kind == "regular":
                    temp_path.write_bytes(b"replacement temp bytes")
                else:
                    temp_path.symlink_to(external_target)
                return original_publish(temp_path=temp_path, dest_path=dest_path, **kwargs)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "_publish_artifact_temp_no_replace",
                _replace_before_publish,
            )

            with pytest.raises(RuntimeError) as exc_info:
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Temp Replacement",
                        slug="temp-replacement",
                    ),
                    ports,
                )

            dest_path = artifacts_dir / "20260312t010203z-temp-replacement.md"
            assert competitor_path is not None
            assert owned_backup is not None
            assert owned_backup.read_bytes().startswith(b"id=20260312t010203z")
            if replacement_kind == "regular":
                assert competitor_path.read_bytes() == b"replacement temp bytes"
            else:
                assert competitor_path.is_symlink()
                assert competitor_path.readlink() == external_target
                assert not external_target.exists()
            assert not dest_path.exists()
            assert exc_info.value.__cause__ is not None
            assert "identity changed" in str(exc_info.value.__cause__)

    def test_new_artifact_directory_symlink_swap_before_temp_claim_never_publishes_external(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as external_tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            (artifacts_dir / "owned-sentinel.bin").write_bytes(b"owned sentinel")
            owned_before = _snapshot_tree(artifacts_dir)
            external_dir = Path(external_tmp) / "external-artifacts"
            external_dir.mkdir()
            (external_dir / "external-sentinel.bin").write_bytes(b"external sentinel")
            external_rules_target = external_dir / "external-rules-target.md"
            external_rules_target.write_bytes(b"external rules target")
            (external_dir / "rules.md").symlink_to(external_rules_target)
            external_before = _snapshot_tree(external_dir)
            owned_backup = artifacts_dir.with_name("artifacts.owned-backup")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_claim = app_create_artifact_doc._claim_artifact_temp_path
            swapped = False

            def _swap_directory_before_claim(dest_path, **kwargs):
                nonlocal swapped
                if not swapped:
                    swapped = True
                    artifacts_dir.rename(owned_backup)
                    artifacts_dir.symlink_to(external_dir, target_is_directory=True)
                return original_claim(dest_path, **kwargs)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "_claim_artifact_temp_path",
                _swap_directory_before_claim,
            )

            with pytest.raises(RuntimeError, match="Artifact directory identity changed"):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Directory Symlink Swap",
                        slug="directory-symlink-swap",
                    ),
                    ports,
                )

            assert swapped
            assert artifacts_dir.is_symlink()
            assert artifacts_dir.readlink() == external_dir
            assert _snapshot_tree(external_dir) == external_before
            assert _snapshot_tree(owned_backup) == owned_before
            assert not (external_dir / "20260312t010203z-directory-symlink-swap.md").exists()

    def test_new_artifact_directory_symlink_swap_before_rollback_preserves_external_hardlink(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as external_tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            (artifacts_dir / "owned-sentinel.bin").write_bytes(b"owned sentinel")
            owned_before = _snapshot_tree(artifacts_dir)
            external_dir = Path(external_tmp) / "external-artifacts"
            external_dir.mkdir()
            (external_dir / "external-sentinel.bin").write_bytes(b"external sentinel")
            owned_backup = artifacts_dir.with_name("artifacts.owned-backup")
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_rollback = app_create_artifact_doc._rollback_artifact_attempt
            external_temp: Path | None = None
            external_identity: tuple[int, int] | None = None

            def _fail_write(descriptor, _text):
                os.write(descriptor, b"owned partial temp")
                raise OSError("injected directory swap rollback failure")

            def _swap_directory_before_rollback(journal):
                nonlocal external_temp, external_identity
                assert journal.temp_path is not None
                external_temp = external_dir / journal.temp_path.name
                os.link(journal.temp_path, external_temp)
                external_stat = os.lstat(external_temp)
                external_identity = (external_stat.st_dev, external_stat.st_ino)
                artifacts_dir.rename(owned_backup)
                artifacts_dir.symlink_to(external_dir, target_is_directory=True)
                return original_rollback(journal)

            monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)
            monkeypatch.setattr(
                app_create_artifact_doc,
                "_rollback_artifact_attempt",
                _swap_directory_before_rollback,
            )

            with pytest.raises(OSError, match="injected directory swap rollback failure") as exc_info:
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Directory Rollback Swap",
                        slug="directory-rollback-swap",
                    ),
                    ports,
                )

            assert external_temp is not None
            assert external_identity is not None
            assert external_temp.read_bytes() == b"owned partial temp"
            external_stat = os.lstat(external_temp)
            assert (external_stat.st_dev, external_stat.st_ino) == external_identity
            assert (external_dir / "external-sentinel.bin").read_bytes() == b"external sentinel"
            assert artifacts_dir.is_symlink()
            assert artifacts_dir.readlink() == external_dir
            assert _snapshot_tree(owned_backup) == owned_before
            assert exc_info.value.__cause__ is not None
            assert "Artifact directory identity changed" in str(exc_info.value.__cause__)

    def test_new_artifact_directory_creation_race_does_not_claim_competitor(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            artifacts_dir = issue_dir / "artifacts"
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_mkdir = Path.mkdir
            injected = False

            def _race_mkdir(path, mode=0o777, parents=False, exist_ok=False):
                nonlocal injected
                if path == artifacts_dir and not injected:
                    injected = True
                    original_mkdir(path, mode=mode, parents=parents, exist_ok=False)
                    raise FileExistsError("injected competing artifact directory")
                return original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

            def _fail_write(_descriptor, _text):
                raise OSError("injected post-setup write failure")

            monkeypatch.setattr(Path, "mkdir", _race_mkdir)
            monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)

            with pytest.raises((OSError, RuntimeError)):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Directory Race",
                        slug="directory-race",
                    ),
                    ports,
                )

            assert artifacts_dir.is_dir()

    def test_new_artifact_directory_creation_race_replacement_before_open_is_rejected(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            artifacts_dir = issue_dir / "artifacts"
            competitor_backup = issue_dir / "artifacts.competitor-backup"
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_mkdir = Path.mkdir
            original_open_directory = app_create_artifact_doc._open_artifacts_directory
            competitor_before: list[tuple[str, str, bytes | str]] | None = None
            replacement_before: list[tuple[str, str, bytes | str]] | None = None
            injected = False

            def _race_mkdir(path, mode=0o777, parents=False, exist_ok=False):
                nonlocal injected
                if path == artifacts_dir and not injected:
                    injected = True
                    original_mkdir(path, mode=mode, parents=parents, exist_ok=False)
                    raise FileExistsError("injected competing artifact directory")
                return original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

            def _replace_competitor_before_open(path, *, expected_identity):
                nonlocal competitor_before, replacement_before
                assert path == artifacts_dir
                competitor_before = _snapshot_tree(artifacts_dir)
                artifacts_dir.rename(competitor_backup)
                artifacts_dir.mkdir()
                (artifacts_dir / "competitor.bin").write_bytes(b"replacement directory sentinel")
                replacement_before = _snapshot_tree(artifacts_dir)
                return original_open_directory(path, expected_identity=expected_identity)

            monkeypatch.setattr(Path, "mkdir", _race_mkdir)
            monkeypatch.setattr(
                app_create_artifact_doc,
                "_open_artifacts_directory",
                _replace_competitor_before_open,
            )

            with pytest.raises(RuntimeError, match="Artifact directory identity changed"):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Directory Race Replacement",
                        slug="directory-race-replacement",
                    ),
                    ports,
                )

            assert injected
            assert competitor_before is not None
            assert replacement_before is not None
            assert _snapshot_tree(competitor_backup) == competitor_before
            assert _snapshot_tree(artifacts_dir) == replacement_before
            assert not (artifacts_dir / "rules.md").exists()
            assert not any(path.name.endswith(".tmp") for path in artifacts_dir.iterdir())
            assert not (artifacts_dir / "20260312t010203z-directory-race-replacement.md").exists()

    def test_new_artifact_rules_creation_race_does_not_claim_competitor(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            rules_link = artifacts_dir / "rules.md"
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_symlink = os.symlink
            injected = False

            def _race_symlink(src, dst, target_is_directory=False, *, dir_fd=None):
                nonlocal injected
                if Path(dst).name == rules_link.name and dir_fd is not None and not injected:
                    injected = True
                    original_symlink(
                        src,
                        dst,
                        target_is_directory=target_is_directory,
                        dir_fd=dir_fd,
                    )
                    raise FileExistsError("injected competing artifact rules symlink")
                return original_symlink(
                    src,
                    dst,
                    target_is_directory=target_is_directory,
                    dir_fd=dir_fd,
                )

            def _fail_write(_descriptor, _text):
                raise OSError("injected post-setup write failure")

            monkeypatch.setattr(os, "symlink", _race_symlink)
            monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)

            with pytest.raises((OSError, RuntimeError)):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Rules Race",
                        slug="rules-race",
                    ),
                    ports,
                )

            assert rules_link.is_symlink()
            assert rules_link.resolve() == rules_source.resolve()

    @pytest.mark.parametrize("replaced_path", ("dest", "temp", "rules", "directory"))
    def test_new_artifact_rollback_identity_mismatch_preserves_replacement(
        self,
        monkeypatch,
        replaced_path: str,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_rollback = app_create_artifact_doc._rollback_artifact_attempt
            replacement_path: Path | None = None
            owned_backup: Path | None = None

            def _replace_before_rollback(journal):
                nonlocal replacement_path, owned_backup
                if replaced_path == "dest":
                    replacement_path = journal.dest_path
                elif replaced_path == "temp":
                    replacement_path = journal.temp_path
                elif replaced_path == "rules":
                    replacement_path = journal.rules_path
                else:
                    replacement_path = journal.artifacts_dir
                assert replacement_path is not None
                owned_backup = replacement_path.with_name(f"{replacement_path.name}.owned-backup")
                replacement_path.rename(owned_backup)
                if replaced_path == "directory":
                    replacement_path.mkdir()
                else:
                    replacement_path.write_bytes(b"replacement competitor bytes")
                return original_rollback(journal)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "_rollback_artifact_attempt",
                _replace_before_rollback,
            )

            if replaced_path == "dest":
                original_scan = app_create_artifact_doc.scan_artifact_duplicate_state
                scan_calls = 0

                def _fail_post_write_guard(path):
                    nonlocal scan_calls
                    scan_calls += 1
                    if scan_calls == 2:
                        return "injected replacement rollback failure", set()
                    return original_scan(path)

                monkeypatch.setattr(
                    app_create_artifact_doc,
                    "scan_artifact_duplicate_state",
                    _fail_post_write_guard,
                )
            else:

                def _fail_write(descriptor, _text):
                    os.write(descriptor, b"owned partial temp")
                    raise OSError("injected replacement rollback failure")

                monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)

            with pytest.raises((OSError, RuntimeError), match="injected replacement rollback failure") as exc_info:
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Rollback Replacement",
                        slug="rollback-replacement",
                    ),
                    ports,
                )

            assert replacement_path is not None
            assert owned_backup is not None
            if replaced_path == "directory":
                assert replacement_path.is_dir()
                assert owned_backup.is_dir()
            else:
                assert replacement_path.read_bytes() == b"replacement competitor bytes"
                assert os.path.lexists(owned_backup)
            assert exc_info.value.__cause__ is not None
            cleanup_diagnostic = str(exc_info.value.__cause__)
            assert "identity changed" in cleanup_diagnostic or "identity missing" in cleanup_diagnostic

    def test_new_artifact_rollback_failure_keeps_body_error_primary_and_reports_cleanup(
        self,
        monkeypatch,
    ) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            original_scan = app_create_artifact_doc.scan_artifact_duplicate_state
            scan_calls = 0

            def _fail_post_write_guard(path):
                nonlocal scan_calls
                scan_calls += 1
                if scan_calls == 2:
                    return "injected primary post-write guard failure", set()
                return original_scan(path)

            monkeypatch.setattr(
                app_create_artifact_doc,
                "scan_artifact_duplicate_state",
                _fail_post_write_guard,
            )
            dest_path = artifacts_dir / "20260312t010203z-rollback-failure.md"
            original_unlink = os.unlink

            def _fail_dest_rollback(path, *, dir_fd=None):
                if path == dest_path.name and dir_fd is not None:
                    raise OSError("injected artifact rollback unlink failure")
                if dir_fd is None:
                    return original_unlink(path)
                return original_unlink(path, dir_fd=dir_fd)

            monkeypatch.setattr(os, "unlink", _fail_dest_rollback)

            try:
                with pytest.raises(RuntimeError, match="injected primary post-write guard failure") as exc_info:
                    app_create_artifact_doc.create_artifact_doc(
                        app_contracts.CreateArtifactDocRequest(
                            artifact_type="blank",
                            scope_node_id="iss-local-00001",
                            title="Rollback Failure",
                            slug="rollback-failure",
                        ),
                        ports,
                    )

                assert exc_info.value.__cause__ is not None
                assert "Artifact rollback failed" in str(exc_info.value.__cause__)
                assert "injected artifact rollback unlink failure" in str(exc_info.value.__cause__)
            finally:
                if dest_path.exists():
                    original_unlink(dest_path)

    def test_new_artifact_preserves_typed_blank_suffix_exhaustion_semantics(self) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = self._prepare_exhausted_artifact_slots(specdock_dir, issue_record)
            before = {
                path.name: path.read_bytes()
                for path in artifacts_dir.iterdir()
                if path.is_file() and not path.is_symlink()
            }
            events: list[str] = []
            ports = self._ports(
                app_ports,
                specdock_dir=specdock_dir,
                records=[issue_record],
                events=events,
            )

            with pytest.raises(RuntimeError, match="Artifact timestamp suffix exhaustion"):
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Exhausted Slot",
                        slug="exhausted-slot",
                    ),
                    ports,
                )

            after = {
                path.name: path.read_bytes()
                for path in artifacts_dir.iterdir()
                if path.is_file() and not path.is_symlink()
            }
            assert after == before
            assert events == []
            lock_path = self._create_lock_path(specdock_dir)
            assert not lock_path.exists()
            reacquired_path, reacquired_token = app_create_artifact_doc._acquire_create_lock(specdock_dir)
            try:
                assert reacquired_path == lock_path
                assert lock_path.exists()
            finally:
                app_create_artifact_doc._release_create_lock(
                    reacquired_path,
                    reacquired_token,
                    specdock_dir=specdock_dir,
                )
            assert not lock_path.exists()

    def test_new_artifact_body_error_remains_primary_when_lock_release_fails(self, monkeypatch) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            self._prepare_exhausted_artifact_slots(specdock_dir, issue_record)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])

            original_release = app_create_artifact_doc._release_create_lock

            def _release_then_fail(lock_path, lock_token, *, specdock_dir):
                original_release(lock_path, lock_token, specdock_dir=specdock_dir)
                raise RuntimeError("injected create lock release failure")

            monkeypatch.setattr(app_create_artifact_doc, "_release_create_lock", _release_then_fail)

            with pytest.raises(RuntimeError, match="Artifact timestamp suffix exhaustion") as exc_info:
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Exhausted Slot",
                        slug="exhausted-slot",
                    ),
                    ports,
                )

            assert str(exc_info.value.__cause__) == "injected create lock release failure"
            assert not self._create_lock_path(specdock_dir).exists()

    def test_new_artifact_body_error_remains_primary_when_directory_close_fails(self, monkeypatch) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            artifacts_dir = Path(issue_record.path) / "artifacts"
            artifacts_dir.mkdir(parents=True)
            rules_source = specdock_dir / "docs" / "rules" / "issue" / "artifacts.md"
            (artifacts_dir / "rules.md").symlink_to(rules_source)
            before = _snapshot_tree(artifacts_dir)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_close = app_create_artifact_doc._close_artifacts_directory

            def _fail_write(_descriptor, _text):
                raise OSError("injected primary artifact write failure")

            def _close_then_fail(journal):
                original_close(journal)
                raise OSError("injected artifact directory close failure")

            monkeypatch.setattr(app_create_artifact_doc, "_write_claimed_artifact_temp", _fail_write)
            monkeypatch.setattr(app_create_artifact_doc, "_close_artifacts_directory", _close_then_fail)

            with pytest.raises(OSError, match="injected primary artifact write failure") as exc_info:
                app_create_artifact_doc.create_artifact_doc(
                    app_contracts.CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-local-00001",
                        title="Directory Close Failure",
                        slug="directory-close-failure",
                    ),
                    ports,
                )

            assert exc_info.value.__cause__ is not None
            assert "injected artifact directory close failure" in str(exc_info.value.__cause__)
            assert _snapshot_tree(artifacts_dir) == before
            assert not self._create_lock_path(specdock_dir).exists()

    def test_new_artifact_committed_directory_close_failure_returns_warning(self, monkeypatch) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_close = app_create_artifact_doc._close_artifacts_directory

            def _close_then_fail(journal):
                original_close(journal)
                raise OSError("injected committed artifact directory close failure")

            monkeypatch.setattr(app_create_artifact_doc, "_close_artifacts_directory", _close_then_fail)

            result = app_create_artifact_doc.create_artifact_doc(
                app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="Committed Directory Close Failure",
                    slug="committed-directory-close-failure",
                ),
                ports,
            )

            assert result.path.is_file()
            assert result.path.read_text(encoding="utf-8").startswith("id=20260312t010203z")
            assert len(result.warnings) == 1
            assert "artifact committed" in result.warnings[0]
            assert "directory close failed" in result.warnings[0]
            assert "injected committed artifact directory close failure" in result.warnings[0]
            assert "do not retry creation" in result.warnings[0]
            assert not self._create_lock_path(specdock_dir).exists()

    def test_new_artifact_committed_lock_release_failure_returns_warning(self, monkeypatch) -> None:
        app_create_artifact_doc, app_contracts, app_ports, infra_contracts = _artifact_runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._prepare_node_templates(specdock_dir)
            self._prepare_blank_artifact_template(specdock_dir)
            issue_record = self._issue_scope_record(infra_contracts, specdock_dir=specdock_dir)
            issue_dir = Path(issue_record.path)
            issue_dir.mkdir(parents=True)
            ports = self._ports(app_ports, specdock_dir=specdock_dir, records=[issue_record])
            original_release = app_create_artifact_doc._release_create_lock

            def _release_then_fail(lock_path, lock_token, *, specdock_dir):
                original_release(lock_path, lock_token, specdock_dir=specdock_dir)
                raise RuntimeError("injected committed create lock release failure")

            monkeypatch.setattr(app_create_artifact_doc, "_release_create_lock", _release_then_fail)

            result = app_create_artifact_doc.create_artifact_doc(
                app_contracts.CreateArtifactDocRequest(
                    artifact_type="blank",
                    scope_node_id="iss-local-00001",
                    title="Committed Lock Release Failure",
                    slug="committed-lock-release-failure",
                ),
                ports,
            )

            assert result.path.is_file()
            assert result.path.read_text(encoding="utf-8").startswith("id=20260312t010203z")
            assert len(result.warnings) == 1
            assert "artifact committed" in result.warnings[0]
            assert "create lock release failed" in result.warnings[0]
            assert "injected committed create lock release failure" in result.warnings[0]
            assert "do not retry creation" in result.warnings[0]
            assert not self._create_lock_path(specdock_dir).exists()

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

    def test_new_node_workbench_readme_matrix(self) -> None:
        (
            _runtime_app,
            app_contracts,
            app_create_node,
            app_ports,
            _new_commands,
            _infra_contracts,
            _presentation_cli_text,
        ) = _runtime_modules()
        template_scaffolder = importlib.import_module("spec_dock_runtime.infra.template_scaffolder")
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            provider_templates = (
                Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "templates"
            )
            for kind in ("initiative", "epic", "issue"):
                shutil.copytree(provider_templates / kind, specdock_dir / "templates" / kind)
                rules_dir = specdock_dir / "docs" / "rules" / kind
                rules_dir.mkdir(parents=True)
                for name in (
                    ("epics.md", "artifacts.md")
                    if kind == "initiative"
                    else ("issues.md", "artifacts.md")
                    if kind == "epic"
                    else ("artifacts.md",)
                ):
                    (rules_dir / name).write_text(f"{kind} {name}\n", encoding="utf-8")

            node_repo = _StubNodeRepo([])
            ports = app_ports.Ports(
                node_reader=_DummyNodeReader(),
                node_repo=node_repo,
                template_scaffolder=template_scaffolder,
                issue_gateway=_StubIssueGateway(),
                git_gateway=_StubGitGateway(),
                clock=_StubClock(),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            parent_id = None
            results = []
            for kind, issue_number, create_fn in (
                ("initiative", 1, app_create_node.create_initiative),
                ("epic", 2, app_create_node.create_epic),
                ("issue", 3, app_create_node.create_issue),
            ):
                request = app_contracts.CreateNodeRequest(
                    title=f"{kind} title",
                    slug=None,
                    parent_id=parent_id,
                    github_mode="link_existing",
                    github_issue_number=issue_number,
                )
                graph = app_create_node.load_graph(ports, validate=False)
                plan = app_create_node.plan_node_creation(
                    request,
                    graph,
                    kind=kind,
                    specdock_dir=specdock_dir,
                    today="2026-03-12",
                    current_repo_slug="example/repo",
                )
                expected_readme = plan.dest_dir / ".workbench" / "README.md"
                assert plan.planned_paths.count(expected_readme) == 1

                result = create_fn(request, ports)

                assert result.created_paths.count(expected_readme) == 1
                assert expected_readme.is_file()
                assert not (expected_readme.parent / ".gitkeep").exists()
                results.append(expected_readme.read_bytes())
                parent_id = result.node.id

            assert len(set(results)) == 1

    def test_new_artifact_renderer_text_regression(self) -> None:
        (
            _runtime_app,
            app_contracts,
            _app_create_node,
            _app_ports,
            _new_commands,
            _infra_contracts,
            presentation_cli_text,
        ) = _runtime_modules()
        result = app_contracts.CreateArtifactDocResult(
            artifact_id="20260312t010203z-03-adr",
            artifact_type="adr",
            scope_node_id="iss-local-00001",
            path=Path(
                "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                "issues/iss-local-00001-refresh-token/artifacts/20260312t010203z-03-adr-decision-one.md"
            ),
            warnings=[],
        )
        text = presentation_cli_text.render_new_artifact_text(result)
        assert text.stdout_lines == [
            (
                "spec-dock: ok (new artifact) "
                "type=adr id=20260312t010203z-03-adr scope=iss-local-00001 "
                "path=spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                "issues/iss-local-00001-refresh-token/artifacts/20260312t010203z-03-adr-decision-one.md"
            )
        ]

    def test_command_new_artifact_smoke(self) -> None:
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
            return app_contracts.CreateArtifactDocResult(
                artifact_id="20260312t010203z-adr",
                artifact_type="adr",
                scope_node_id=req.scope_node_id,
                path=Path(
                    "/repo/spec-dock/initiatives/init-local-00001-auth/epics/epic-local-00001-login/"
                    "issues/iss-local-00001-refresh-token/artifacts/20260312t010203z-adr-decision-one.md"
                ),
                warnings=[],
            )

        use_cases = app_contracts.UseCases(
            create_initiative=_unexpected,
            create_epic=_unexpected,
            create_issue=_unexpected,
            create_artifact_doc=_fake_create,
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
        outcome = new_commands._run_new_artifact(
            new_commands.NewArtifactArgs(
                artifact_type="adr",
                scope_node_id="iss-local-00001",
                scope_kind="issue",
                title="Decision one",
                slug=None,
            ),
            use_cases,
        )

        assert len(calls) == 1
        assert calls[0].artifact_type == "adr"
        assert calls[0].scope_node_id == "iss-local-00001"
        assert outcome.exit_code == 0
        assert "spec-dock: ok (new artifact) type=adr id=20260312t010203z-adr" in "\n".join(outcome.text.stdout_lines)
