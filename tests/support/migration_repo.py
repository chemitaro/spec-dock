"""A schema-3 repository, its bare origin and a fake GitHub for the throwaway migration script (Issue 435).

legacy = build_legacy(tmp_path, monkeypatch)       # origin (bare), main checkout, fake GitHub, state dir
result = legacy.run("plan")                         # in-process migrate.main with the fake gh and an injected clock
"""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib.util
import io
import json
import os
from pathlib import Path
import posixpath
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.infra.static_assets import package_static_assets
from tests.support.canonical_repo import _clean_environment, clone, configure, git, isolate_user_state
from tests.support.fake_github import FakeClock, FakeGithub

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import ModuleType

    import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/migrate-to-canonical/migrate.py"
REPOSITORY = "example/repo"
LEGACY_DECLARATION = b'{\n  "schema_version": 3,\n  "writer_protocol": "specdock.worktree-writer/v1"\n}\n'
CI_WORKFLOW = b"""name: CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SpecDock
        run: uvx --from git+https://github.com/chemitaro/spec-dock@4d25a8b4 spec-dock workspace validate --ci --json
      - name: Tests
        run: make test
"""

_MODULE: ModuleType | None = None


def migrate_module() -> ModuleType:
    """Load migrate.py by path, as the package never imports it."""
    global _MODULE
    if _MODULE is None:
        spec = importlib.util.spec_from_file_location("spec_dock_migrate_script", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _MODULE = module
    return _MODULE


def meta(
    kind: str,
    scope_id: str,
    title: str,
    slug: str,
    number: int | None,
    *,
    parent: str | None = None,
    initiative: str | None = None,
    epic: str | None = None,
    depends_on: tuple[str, ...] = (),
    compact: bool = False,
) -> bytes:
    payload: dict[str, Any] = {
        "schema_version": 3,
        "type": kind,
        "id": scope_id,
        "title": title,
        "slug": slug,
        "parent_id": parent,
        "initiative_id": initiative,
        "epic_id": epic,
        "depends_on": list(depends_on),
        "backend": "github",
        "github": {"issue_number": number, "repo_owner": "example", "repo_name": "repo"},
        "lifecycle": None,
        "revision": 2,
    }
    if compact:
        payload = {
            "_spec_dock": {"do_not_edit": True, "edit_via": "spec-dock", "managed": True},
            **payload,
            "created_at": "2026-03-26T12:26:40+09:00",
            "updated_at": "2026-03-26T12:26:40+09:00",
        }
        return json.dumps(dict(sorted(payload.items())), separators=(",", ":")).encode()
    return (json.dumps(payload, indent=2) + "\n").encode()


INIT = "spec-dock/initiatives/init-00001-alpha"
EPIC = f"{INIT}/epics/epic-00002-beta"
ISSUE3 = f"{EPIC}/issues/iss-00003-gamma"
ISSUE4 = f"{EPIC}/issues/iss-00004-delta"
LOCAL2 = "spec-dock/initiatives/init-local-00002-proto"
LOCAL2_EPIC = f"{LOCAL2}/epics/epic-00005-under-proto"
LOCAL3 = "spec-dock/initiatives/init-local-00003-architecture"
# Where register and build-canonical put each fixture Scope (#40 is the Issue register creates for LOCAL3).
FLAT = {
    INIT: "00000-00999/init-00001",
    EPIC: "00000-00999/epic-00002",
    ISSUE3: "00000-00999/iss-00003",
    ISSUE4: "00000-00999/iss-00004",
    LOCAL2: "00000-00999/init-00039",
    LOCAL2_EPIC: "00000-00999/epic-00005",
    LOCAL3: "00000-00999/init-00040",
}


class Symlink(str):
    """A file content written as a symbolic link with this target."""


def flat_path(path: str) -> str:
    """The catalog path of a nested fixture path (spec-dock/initiatives/... -> <bucket>/<ID>/...)."""
    scope = max((s for s in FLAT if path == s or path.startswith(f"{s}/")), key=len)
    return FLAT[scope] + path[len(scope) :]


REQUIRED_DOCUMENTS = ("requirement.md", "design.md", "plan.md", "report.md")


def legacy_specs() -> dict[str, bytes]:
    files = _legacy_specs()
    for path in [p for p in files if p.endswith("/.meta.json")]:
        directory = path.removesuffix("/.meta.json")
        for name in REQUIRED_DOCUMENTS:
            files.setdefault(f"{directory}/{name}", f"# {name}\n".encode())
    return files


def _legacy_specs() -> dict[str, bytes]:
    return {
        f"{INIT}/.meta.json": meta("initiative", "init-00001", "Alpha", "alpha", 1, compact=True),
        f"{INIT}/requirement.md": b"# Alpha\n",
        f"{EPIC}/.meta.json": meta(
            "epic", "epic-00002", "Beta", "beta", 2, parent="init-00001", initiative="init-00001"
        ),
        f"{EPIC}/design.md": b"# Beta design\n",
        f"{ISSUE3}/.meta.json": meta(
            "issue",
            "iss-00003",
            "Gamma",
            "gamma",
            3,
            parent="epic-00002",
            initiative="init-00001",
            epic="epic-00002",
            depends_on=("iss-00004",),
        ),
        f"{ISSUE3}/plan.md": b"# Gamma plan\n",
        f"{ISSUE3}/.workbench/README.md": b"scratch\n",
        f"{ISSUE4}/.meta.json": meta(
            "issue", "iss-00004", "Delta", "delta", 4, parent="epic-00002", initiative="init-00001", epic="epic-00002"
        ),
        f"{ISSUE4}/requirement.md": b"# Delta\n",
        f"{LOCAL2}/.meta.json": meta("initiative", "init-local-00002", "Proto", "proto", 39, compact=True),
        f"{LOCAL2}/requirement.md": b"# Proto\n",
        f"{LOCAL2_EPIC}/.meta.json": meta(
            "epic",
            "epic-00005",
            "Under Proto",
            "under-proto",
            5,
            parent="init-local-00002",
            initiative="init-local-00002",
        ),
        f"{LOCAL2_EPIC}/design.md": b"# Under proto\n",
        f"{LOCAL3}/.meta.json": meta(
            "initiative", "init-local-00003", "Architecture", "architecture", 31, compact=True
        ),
        f"{LOCAL3}/requirement.md": b"# Architecture\n",
    }


SCOPE_KINDS = {
    INIT: "initiative",
    EPIC: "epic",
    ISSUE3: "issue",
    ISSUE4: "issue",
    LOCAL2: "initiative",
    LOCAL2_EPIC: "epic",
    LOCAL3: "initiative",
}
LINKED_EXTRA: dict[str, bytes] = {"docs/guide.md": b"# Repository guide\n"}


def linked_specs() -> dict[str, bytes | Symlink]:
    """legacy_specs with the relative links a real spec tree has: rule symlinks, Markdown and HTML links."""
    files: dict[str, bytes | Symlink] = dict(legacy_specs())

    def link(path: str, target: str) -> None:
        files[path] = Symlink(posixpath.relpath(target, posixpath.dirname(path)))

    rules = "spec-dock/docs/rules"
    for scope, kind in SCOPE_KINDS.items():
        link(f"{scope}/artifacts/rules.md", f"{rules}/{kind}/artifacts.md")
        link(f"{scope}/discussions/rules.md", f"{rules}/{kind}/discussions.md")
    for scope in (INIT, LOCAL2):
        link(f"{scope}/epics/rules.md", f"{rules}/initiative/epics.md")
    for scope in (EPIC, LOCAL2_EPIC):
        link(f"{scope}/issues/rules.md", f"{rules}/epic/issues.md")
    files[f"{ISSUE3}/design.md"] = (
        "# Gamma design\n\n"
        "詳細: [Design Guide](../../../../../../docs/authoring/design.md)\n\n"
        "- [Epic requirement](../../requirement.md#scope)\n"
        "- [Epic note](../../artifacts/note.md)\n"
        "- [siblings](../)\n"
        "- [Delta](../iss-00004-delta/requirement.md)\n"
        "- [Proto epic](../../../../../init-local-00002-proto/epics/epic-00005-under-proto/design.md)\n"
        "- [Repository guide](../../../../../../../docs/guide.md)\n"
        "- [Own plan](plan.md)\n\n"
        "```text\n[example](../../requirement.md)\n```\n"
    ).encode()
    files[f"{EPIC}/artifacts/note.md"] = (
        b"[issues](../issues) [rules](../issues/rules.md) [initiative](../../../requirement.md)\n"
    )
    files[f"{ISSUE3}/discussions/iss-00099-topic/notes.md"] = b"[plan](../../plan.md)\n"
    files[f"{ISSUE3}/artifacts/guide.html"] = (
        b'<a href="../../../requirement.md">Epic</a> <img src=\'../plan.md\'> <a href="#top">top</a>\n'
    )
    return files


def static_files(declaration: bytes = LEGACY_DECLARATION) -> dict[str, bytes]:
    files = {asset.path: asset.payload for asset in package_static_assets()}
    files["spec-dock/workspace.json"] = declaration
    return files


def legacy_github(clock: FakeClock) -> FakeGithub:
    fake = FakeGithub(REPOSITORY, clock=clock)
    for number, title in ((1, "Alpha"), (2, "Beta"), (3, "Gamma"), (4, "Delta"), (5, "Under Proto")):
        fake.add_issue(number, title=title, body=f"{title} body.")
    fake.add_issue(31, title="Old Thing", body="unrelated", state="closed", state_reason="completed")
    fake.add_issue(39, title="Proto", body="")
    return fake


@dataclass
class Legacy:
    root: Path
    remote: Path
    main: Path
    github: FakeGithub
    clock: FakeClock
    state: Path
    default_branch: str
    outputs: list[dict[str, Any]] = field(default_factory=list)

    def run(
        self, command: str, *args: str, apply: bool = False, project: Path | None = None
    ) -> tuple[int, dict[str, Any]]:
        argv = [
            command,
            "--project",
            str(project or self.main),
            "--repo",
            REPOSITORY,
            "--state-dir",
            str(self.state),
            "--json",
            *args,
        ]
        if apply:
            argv.append("--apply")
        stream = io.StringIO()
        code = migrate_module().main(argv, runner=self.github, clock=self.clock, stdout=stream)
        result = json.loads(stream.getvalue())
        self.outputs.append(result)
        return code, result

    @property
    def records(self) -> Path:
        return self.state / "example-repo"

    def remote_refs(self) -> dict[str, str]:
        return refs(self.remote)

    def commit_to_origin(self, files: Mapping[str, bytes | Symlink | None], message: str) -> str:
        """Commit on origin's default branch through a separate clone, then fetch it into the main checkout."""
        other = self.root / f"pusher-{len(self.outputs)}-{message.replace(' ', '-')}"
        if not other.exists():
            clone(self.remote, other)
        git(other, "pull", "-q", "origin", self.default_branch)
        write_files(other, files)
        git(other, "add", "-A")
        git(other, "commit", "-qm", message)
        git(other, "push", "-q", "origin", f"HEAD:{self.default_branch}")
        git(self.main, "fetch", "-q", "origin")
        return git(other, "rev-parse", "HEAD")


def write_files(root: Path, files: Mapping[str, bytes | Symlink | None]) -> None:
    for relative, payload in files.items():
        target = root / relative
        if payload is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, Symlink):
            if target.is_symlink() or target.exists():
                target.unlink()
            os.symlink(str(payload), target)
        else:
            target.write_bytes(payload)


def refs(repository: Path) -> dict[str, str]:
    output = git(repository, "for-each-ref", "--format=%(refname) %(objectname)")
    return {name: oid for name, _, oid in (line.partition(" ") for line in output.splitlines() if line)}


def build_legacy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    default_branch: str = "main",
    specs: Mapping[str, bytes | Symlink] | None = None,
    declaration: bytes = LEGACY_DECLARATION,
    extra: Mapping[str, bytes] | None = None,
) -> Legacy:
    isolate_user_state(monkeypatch, tmp_path)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root = tmp_path.resolve()
    remote = root / "origin.git"
    subprocess.run(
        ["git", "init", "-q", "--bare", f"--initial-branch={default_branch}", str(remote)],
        check=True,
        env=_clean_environment(),
    )
    seed = root / "seed"
    subprocess.run(
        ["git", "init", "-q", f"--initial-branch={default_branch}", str(seed)], check=True, env=_clean_environment()
    )
    configure(seed)
    files: dict[str, bytes | Symlink] = {**static_files(declaration), ".github/workflows/ci.yml": CI_WORKFLOW}
    files.update(legacy_specs() if specs is None else specs)
    files.update(extra or {})
    write_files(seed, files)
    git(seed, "add", "-A")
    git(seed, "commit", "-qm", "legacy seed")
    git(seed, "push", "-q", str(remote), f"HEAD:refs/heads/{default_branch}")
    main = clone(remote, root / "main")
    clock = FakeClock()
    return Legacy(root, remote, main, legacy_github(clock), clock, root / "migrate-state", default_branch)


def migrated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **options: Any) -> Legacy:
    """register, build-canonical and cut applied against the bare origin."""
    from spec_dock.runtime.infra import runtime_environment
    from tests.support.canonical_repo import environment

    legacy = build_legacy(tmp_path, monkeypatch, **options)
    monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: environment())
    for command in ("register", "build-canonical", "cut"):
        code, result = legacy.run(command, apply=True)
        assert code == 0, (command, result)
    return legacy


CUT = "spec-dock/migrate-to-canonical"


def merge_cut(legacy: Legacy) -> None:
    """The human PR merge: origin's default branch takes the cut branch."""
    git(legacy.main, "fetch", "-q", "origin")
    git(legacy.main, "merge", "-q", "--ff-only", f"origin/{CUT}")
    git(legacy.main, "push", "-q", "origin", f"HEAD:{legacy.default_branch}")
    git(legacy.main, "fetch", "-q", "origin")


def snapshot(legacy: Legacy) -> dict[str, Any]:
    """Everything a read-only run must leave unchanged."""
    status = git(legacy.main, "status", "--porcelain", "--ignored", "--untracked-files=all")
    files = (
        sorted((str(p.relative_to(legacy.root)), p.read_bytes()) for p in legacy.records.rglob("*") if p.is_file())
        if legacy.records.exists()
        else []
    )
    return {
        "refs": refs(legacy.main),
        "status": status,
        "config": (legacy.main / ".git/config").read_bytes(),
        "remote": refs(legacy.remote),
        "records": files,
        "writes": len(legacy.github.writes()),
    }
