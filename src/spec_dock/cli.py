from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Iterator

from spec_dock import __version__

_SPEC_DOCK_DIRNAME = ".spec-dock"
_MANAGED_DIRS = ("docs", "templates", "scripts")

_INITIATIVES_DIRNAME = "initiatives"
_ACTIVE_DIRNAME = "active"
_WORK_DIRNAME = ".work"

_ID_RE = re.compile(r"^(?P<prefix>init|epic|iss|adr)-(?P<num>[0-9]+)$")


@dataclass(frozen=True)
class _Node:
    type: str
    id: str
    title: str
    slug: str
    path: Path
    parent_id: str | None
    initiative_id: str | None
    epic_id: str | None
    github_issue_number: int | None


@contextmanager
def _assets_dir() -> Iterator[Path]:
    assets = files("spec_dock") / "assets"
    with as_file(assets) as p:
        yield Path(p)


def _tool_version() -> str:
    if __version__ and __version__ != "0.0.0+unknown":
        return __version__

    # Fallback for dev usage when `spec-dock` isn't installed as a package.
    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return __version__

    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    return match.group(1) if match else __version__


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _today() -> str:
    return datetime.now().date().isoformat()


def _specdock_dir(target_root: Path) -> Path:
    return target_root / _SPEC_DOCK_DIRNAME


def _require_specdock(target_root: Path) -> Path:
    specdock_dir = _specdock_dir(target_root)
    if not specdock_dir.exists():
        raise RuntimeError("'.spec-dock' not found. Run 'spec-dock init' first.")
    return specdock_dir


def _initiatives_root(target_root: Path) -> Path:
    return _require_specdock(target_root) / _INITIATIVES_DIRNAME


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _sync_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Failed to read: {path}: {e}") from e


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate_lowercase(value: str, *, field: str) -> str:
    if value != value.lower():
        raise RuntimeError(f"{field} must be lowercase: {value}")
    return value


def _slugify(title: str) -> str:
    s = unicodedata.normalize("NFKC", title).strip().lower()

    # Normalize separators early.
    s = re.sub(r"[\\/]+", "-", s)
    s = re.sub(r"\s+", "-", s)

    # Replace Windows-forbidden characters and control chars.
    s = re.sub(r'[<>:"|?*]+', "-", s)
    s = re.sub(r"[\x00-\x1f\x7f]+", "-", s)

    out: list[str] = []
    for ch in s:
        if ch.isalnum() or ch in ("-", "_", "."):
            out.append(ch)
        else:
            out.append("-")

    s = "".join(out)
    s = re.sub(r"-{2,}", "-", s).strip("-.")
    if s in ("", ".", ".."):
        return ""
    return s


def _parse_id(value: str) -> tuple[str, int]:
    m = _ID_RE.match(value)
    if not m:
        raise RuntimeError(f"Invalid id: {value} (expected e.g. init-0001)")
    return (m.group("prefix"), int(m.group("num")))


def _format_id(prefix: str, num: int, *, width: int = 4) -> str:
    return f"{prefix}-{num:0{width}d}"


def _next_id(target_root: Path, prefix: str) -> str:
    initiatives_root = _initiatives_root(target_root)
    if not initiatives_root.exists():
        return _format_id(prefix, 1)

    max_num = 0
    for meta_path in initiatives_root.rglob("meta.json"):
        try:
            meta = _load_json(meta_path)
        except RuntimeError:
            continue
        node_id = str(meta.get("id", ""))
        m = _ID_RE.match(node_id)
        if not m:
            continue
        if m.group("prefix") != prefix:
            continue
        max_num = max(max_num, int(m.group("num")))

    if prefix == "adr":
        for adr_path in initiatives_root.rglob("adrs/adr-*.md"):
            m = re.search(r"\b(adr-[0-9]+)\b", adr_path.stem)
            if not m:
                continue
            try:
                _, num = _parse_id(m.group(1))
            except RuntimeError:
                continue
            max_num = max(max_num, num)

    return _format_id(prefix, max_num + 1)


def _render_text(text: str, replacements: dict[str, str]) -> str:
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _copy_template_tree(src_dir: Path, dest_dir: Path, *, replacements: dict[str, str]) -> None:
    if not src_dir.exists() or not src_dir.is_dir():
        raise RuntimeError(f"Missing template directory: {src_dir}")
    if dest_dir.exists():
        raise RuntimeError(f"Destination already exists: {dest_dir}")

    for src_path in sorted(src_dir.rglob("*")):
        rel = src_path.relative_to(src_dir)
        dest_path = dest_dir / rel
        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            raw = src_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src_path, dest_path)
            continue
        dest_path.write_text(_render_text(raw, replacements), encoding="utf-8")


def _scan_nodes(target_root: Path) -> dict[str, _Node]:
    initiatives_root = _initiatives_root(target_root)
    nodes: dict[str, _Node] = {}
    if not initiatives_root.exists():
        return nodes

    for meta_path in initiatives_root.rglob("meta.json"):
        meta = _load_json(meta_path)
        node_type = str(meta.get("type", "")).strip()
        node_id = str(meta.get("id", "")).strip()
        title = str(meta.get("title", "")).strip()
        slug = str(meta.get("slug", "")).strip()
        if not node_type or not node_id:
            continue
        if node_id in nodes:
            raise RuntimeError(f"Duplicate id detected: {node_id} ({meta_path})")

        parent_id = meta.get("parent_id") or None
        initiative_id = meta.get("initiative_id") or None
        epic_id = meta.get("epic_id") or None

        github_issue_number: int | None = None
        github = meta.get("github")
        if isinstance(github, dict) and github.get("issue_number") is not None:
            try:
                github_issue_number = int(github.get("issue_number"))
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Invalid github.issue_number in {meta_path}: {github.get('issue_number')}") from e

        nodes[node_id] = _Node(
            type=node_type,
            id=node_id,
            title=title,
            slug=slug,
            path=meta_path.parent,
            parent_id=str(parent_id) if parent_id else None,
            initiative_id=str(initiative_id) if initiative_id else None,
            epic_id=str(epic_id) if epic_id else None,
            github_issue_number=github_issue_number,
        )
    return nodes


def _write_meta(
    dest_dir: Path,
    *,
    node_type: str,
    node_id: str,
    title: str,
    slug: str,
    parent_id: str | None = None,
    initiative_id: str | None = None,
    epic_id: str | None = None,
    github_issue_number: int | None = None,
) -> None:
    meta: dict[str, Any] = {
        "schema_version": 1,
        "type": node_type,
        "id": node_id,
        "title": title,
        "slug": slug,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "parent_id": parent_id,
        "initiative_id": initiative_id,
        "epic_id": epic_id,
    }
    if github_issue_number is not None:
        meta["github"] = {"issue_number": int(github_issue_number)}
    _write_json(dest_dir / "meta.json", meta)


def _install_spec_dock(
    target_root: Path,
    *,
    force: bool,
) -> None:
    specdock_dir = _specdock_dir(target_root)
    if specdock_dir.exists() and not force:
        raise RuntimeError("'.spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'.")

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"
        specdock_dir.mkdir(parents=True, exist_ok=True)

        for name in _MANAGED_DIRS:
            src = src_spec_dock / name
            dest = specdock_dir / name
            if not src.exists():
                raise RuntimeError(f"Missing asset directory: {src}")
            _sync_tree(src, dest) if (dest.exists() or force) else shutil.copytree(src, dest)

        src_gitignore = src_spec_dock / ".gitignore"
        if src_gitignore.exists():
            _copy_file(src_gitignore, specdock_dir / ".gitignore")

        (specdock_dir / _INITIATIVES_DIRNAME).mkdir(parents=True, exist_ok=True)
        (specdock_dir / _ACTIVE_DIRNAME).mkdir(parents=True, exist_ok=True)
        (specdock_dir / _WORK_DIRNAME).mkdir(parents=True, exist_ok=True)

        (specdock_dir / "spec-dock.version").write_text(f"{_tool_version()}\n", encoding="utf-8")


def _install_skill(target_root: Path, *, force: bool) -> None:
    with _assets_dir() as assets_dir:
        src_skill = assets_dir / "codex_skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        if not src_skill.exists():
            raise RuntimeError(f"Missing asset file: {src_skill}")

        dest_skill = target_root / ".codex" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        if dest_skill.exists() and not force:
            print(
                f"spec-dock: skill already exists (skipped): {dest_skill} (use --force to overwrite)",
                file=sys.stderr,
            )
            return
        _copy_file(src_skill, dest_skill)


def _ensure_gh_available() -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("'gh' CLI not found. Install GitHub CLI (gh) or run without '--github'.")


def _gh_issue_index(target_root: Path, *, limit: int) -> dict[int, dict[str, Any]]:
    _ensure_gh_available()
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        "all",
        "--limit",
        str(limit),
        "--json",
        "number,state,title,labels,updatedAt,url",
    ]
    try:
        p = subprocess.run(cmd, cwd=str(target_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gh failed: {' '.join(cmd)}\n{e.stderr.strip()}") from e

    data = json.loads(p.stdout)
    index: dict[int, dict[str, Any]] = {}
    for item in data:
        try:
            number = int(item.get("number"))
        except (TypeError, ValueError):
            continue
        index[number] = item
    return index


def _new_initiative(
    target_root: Path,
    *,
    title: str,
    slug: str | None,
    node_id: str | None,
    github_issue_number: int | None,
) -> None:
    title = title.strip()
    if not title:
        raise RuntimeError("--title is required")

    if node_id is None:
        node_id = _next_id(target_root, "init")
    node_id = _validate_lowercase(node_id.strip(), field="id")
    _parse_id(node_id)

    if slug is None:
        slug = _slugify(title)
    if not slug:
        raise RuntimeError("Failed to derive slug from title. Pass --slug explicitly.")
    slug = _validate_lowercase(slug.strip(), field="slug")

    specdock_dir = _require_specdock(target_root)
    templates_dir = specdock_dir / "templates" / "initiative"
    initiatives_root = specdock_dir / _INITIATIVES_DIRNAME
    dest_dir = initiatives_root / f"{node_id}-{slug}"

    replacements = {
        "<INIT_ID>": node_id,
        "<INIT_TITLE>": title,
        "<GITHUB_ISSUE_NUMBER_OR_URL>": f"#{github_issue_number}" if github_issue_number else "",
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": _today(),
    }
    _copy_template_tree(templates_dir, dest_dir, replacements=replacements)
    _write_meta(
        dest_dir,
        node_type="initiative",
        node_id=node_id,
        title=title,
        slug=slug,
        github_issue_number=github_issue_number,
    )


def _new_epic(
    target_root: Path,
    *,
    initiative_id: str,
    title: str,
    slug: str | None,
    node_id: str | None,
    github_issue_number: int | None,
) -> None:
    initiative_id = _validate_lowercase(initiative_id.strip(), field="initiative")
    _parse_id(initiative_id)

    nodes = _scan_nodes(target_root)
    initiative = nodes.get(initiative_id)
    if not initiative or initiative.type != "initiative":
        raise RuntimeError(f"Initiative not found: {initiative_id}")

    title = title.strip()
    if not title:
        raise RuntimeError("--title is required")

    if node_id is None:
        node_id = _next_id(target_root, "epic")
    node_id = _validate_lowercase(node_id.strip(), field="id")
    _parse_id(node_id)

    if slug is None:
        slug = _slugify(title)
    if not slug:
        raise RuntimeError("Failed to derive slug from title. Pass --slug explicitly.")
    slug = _validate_lowercase(slug.strip(), field="slug")

    specdock_dir = _require_specdock(target_root)
    templates_dir = specdock_dir / "templates" / "epic"
    dest_dir = initiative.path / "epics" / f"{node_id}-{slug}"

    replacements = {
        "<EPIC_ID>": node_id,
        "<EPIC_TITLE>": title,
        "<INIT_ID>": initiative.id,
        "<GITHUB_ISSUE_NUMBER_OR_URL>": f"#{github_issue_number}" if github_issue_number else "",
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": _today(),
    }
    _copy_template_tree(templates_dir, dest_dir, replacements=replacements)
    _write_meta(
        dest_dir,
        node_type="epic",
        node_id=node_id,
        title=title,
        slug=slug,
        parent_id=initiative.id,
        initiative_id=initiative.id,
        github_issue_number=github_issue_number,
    )


def _new_issue(
    target_root: Path,
    *,
    epic_id: str,
    title: str,
    slug: str | None,
    node_id: str | None,
    github_issue_number: int | None,
) -> None:
    epic_id = _validate_lowercase(epic_id.strip(), field="epic")
    _parse_id(epic_id)

    nodes = _scan_nodes(target_root)
    epic = nodes.get(epic_id)
    if not epic or epic.type != "epic":
        raise RuntimeError(f"Epic not found: {epic_id}")
    if not epic.initiative_id:
        raise RuntimeError(f"Epic meta missing initiative_id: {epic_id}")

    title = title.strip()
    if not title:
        raise RuntimeError("--title is required")

    if node_id is None:
        if github_issue_number is not None:
            node_id = f"iss-{github_issue_number:04d}" if github_issue_number < 10000 else f"iss-{github_issue_number}"
        else:
            node_id = _next_id(target_root, "iss")
    node_id = _validate_lowercase(node_id.strip(), field="id")
    _parse_id(node_id)

    if slug is None:
        slug = _slugify(title)
    if not slug:
        raise RuntimeError("Failed to derive slug from title. Pass --slug explicitly.")
    slug = _validate_lowercase(slug.strip(), field="slug")

    specdock_dir = _require_specdock(target_root)
    templates_dir = specdock_dir / "templates" / "issue"
    dest_dir = epic.path / "issues" / f"{node_id}-{slug}"

    replacements = {
        "<ISS_ID>": node_id,
        "<ISS_TITLE>": title,
        "<EPIC_ID>": epic.id,
        "<INIT_ID>": epic.initiative_id,
        "<GITHUB_ISSUE_NUMBER_OR_URL>": f"#{github_issue_number}" if github_issue_number else "",
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": _today(),
    }
    _copy_template_tree(templates_dir, dest_dir, replacements=replacements)
    _write_meta(
        dest_dir,
        node_type="issue",
        node_id=node_id,
        title=title,
        slug=slug,
        parent_id=epic.id,
        initiative_id=epic.initiative_id,
        epic_id=epic.id,
        github_issue_number=github_issue_number,
    )


def _new_adr(
    target_root: Path,
    *,
    scope_id: str,
    title: str,
    slug: str | None,
    node_id: str | None,
) -> None:
    scope_id = _validate_lowercase(scope_id.strip(), field="scope")
    _parse_id(scope_id)

    nodes = _scan_nodes(target_root)
    scope = nodes.get(scope_id)
    if not scope:
        raise RuntimeError(f"Scope node not found: {scope_id}")

    title = title.strip()
    if not title:
        raise RuntimeError("--title is required")

    if node_id is None:
        node_id = _next_id(target_root, "adr")
    node_id = _validate_lowercase(node_id.strip(), field="id")
    _parse_id(node_id)

    if slug is None:
        slug = _slugify(title)
    if not slug:
        raise RuntimeError("Failed to derive slug from title. Pass --slug explicitly.")
    slug = _validate_lowercase(slug.strip(), field="slug")

    specdock_dir = _require_specdock(target_root)
    template_path = specdock_dir / "templates" / "adr.md"
    if not template_path.exists():
        raise RuntimeError(f"Missing ADR template: {template_path}")

    adrs_dir = scope.path / "adrs"
    adrs_dir.mkdir(parents=True, exist_ok=True)
    dest_path = adrs_dir / f"{node_id}-{slug}.md"
    if dest_path.exists():
        raise RuntimeError(f"ADR already exists: {dest_path}")

    raw = template_path.read_text(encoding="utf-8")
    replacements = {
        "<ADR_ID>": node_id,
        "<ADR_TITLE>": title,
        "<SCOPE_ID>": scope.id,
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": _today(),
    }
    dest_path.write_text(_render_text(raw, replacements), encoding="utf-8")


def _active_set(target_root: Path, *, issue_id: str) -> None:
    issue_id = _validate_lowercase(issue_id.strip(), field="issue")
    _parse_id(issue_id)

    nodes = _scan_nodes(target_root)
    issue = nodes.get(issue_id)
    if not issue or issue.type != "issue":
        raise RuntimeError(f"Issue not found: {issue_id}")
    if not issue.epic_id or not issue.initiative_id:
        raise RuntimeError(f"Issue meta missing epic_id/initiative_id: {issue_id}")

    epic = nodes.get(issue.epic_id)
    initiative = nodes.get(issue.initiative_id)
    if not epic or epic.type != "epic":
        raise RuntimeError(f"Epic not found: {issue.epic_id}")
    if not initiative or initiative.type != "initiative":
        raise RuntimeError(f"Initiative not found: {issue.initiative_id}")

    specdock_dir = _require_specdock(target_root)
    work_dir = specdock_dir / _WORK_DIRNAME
    active_dir = specdock_dir / _ACTIVE_DIRNAME
    work_dir.mkdir(parents=True, exist_ok=True)
    active_dir.mkdir(parents=True, exist_ok=True)

    def rel(p: Path) -> str:
        return p.relative_to(target_root).as_posix()

    current = {
        "schema_version": 1,
        "updated_at": _now_iso(),
        "initiative": {"id": initiative.id, "path": rel(initiative.path)},
        "epic": {"id": epic.id, "path": rel(epic.path)},
        "issue": {"id": issue.id, "path": rel(issue.path)},
    }
    _write_json(work_dir / "current.json", current)

    # Remove existing pointers.
    for name in ("initiative", "epic", "issue", "context-pack.md"):
        p = active_dir / name
        if p.is_symlink() or p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)

    def symlink(name: str, target: Path) -> None:
        link = active_dir / name
        rel_target = os.path.relpath(target, start=active_dir)
        os.symlink(rel_target, link)

    symlink("initiative", initiative.path)
    symlink("epic", epic.path)
    symlink("issue", issue.path)

    ctx = (
        "# Context Pack (generated)\n\n"
        "## Active\n"
        f"- initiative: {initiative.id}\n"
        f"- epic: {epic.id}\n"
        f"- issue: {issue.id}\n\n"
        "## Read order\n"
        "- `.spec-dock/active/initiative/README.md`\n"
        "- `.spec-dock/active/epic/README.md`\n"
        "- `.spec-dock/active/issue/README.md`\n"
        "- `.spec-dock/active/issue/requirement.md`\n"
        "- `.spec-dock/active/issue/design.md`\n"
        "- `.spec-dock/active/issue/plan.md`\n\n"
        "## Commands\n"
        "- state (local): `spec-dock sync`\n"
        "- state (github): `spec-dock sync --github`\n"
    )
    (active_dir / "context-pack.md").write_text(ctx, encoding="utf-8")


def _active_show(target_root: Path) -> None:
    specdock_dir = _require_specdock(target_root)
    current_path = specdock_dir / _WORK_DIRNAME / "current.json"
    if not current_path.exists():
        print("spec-dock: active: (not set)")
        return

    current = _load_json(current_path)
    print(f"initiative: {current.get('initiative', {}).get('id')} ({current.get('initiative', {}).get('path')})")
    print(f"epic: {current.get('epic', {}).get('id')} ({current.get('epic', {}).get('path')})")
    print(f"issue: {current.get('issue', {}).get('id')} ({current.get('issue', {}).get('path')})")


def _active_clear(target_root: Path) -> None:
    specdock_dir = _require_specdock(target_root)
    current_path = specdock_dir / _WORK_DIRNAME / "current.json"
    if current_path.exists():
        current_path.unlink()

    active_dir = specdock_dir / _ACTIVE_DIRNAME
    for name in ("initiative", "epic", "issue", "context-pack.md"):
        p = active_dir / name
        if p.is_symlink() or p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)


def _sync(target_root: Path, *, github: bool, gh_limit: int) -> None:
    nodes = _scan_nodes(target_root)
    if not nodes:
        raise RuntimeError("No nodes found. Create at least one initiative/epic/issue.")

    issue_index: dict[int, dict[str, Any]] = {}
    if github:
        issue_index = _gh_issue_index(target_root, limit=gh_limit)

    children: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        if node.parent_id and node.parent_id in children:
            children[node.parent_id].append(node.id)

    progress: dict[str, dict[str, int]] = {}
    for node in nodes.values():
        if node.type in ("initiative", "epic"):
            progress[node.id] = {"total": 0, "done": 0, "open": 0, "unknown": 0}

    for node in nodes.values():
        if node.type != "issue":
            continue

        status = "unknown"
        if github and node.github_issue_number is not None:
            gh = issue_index.get(node.github_issue_number)
            if gh:
                status = "done" if str(gh.get("state", "")).upper() == "CLOSED" else "open"

        for parent in filter(None, (node.epic_id, node.initiative_id)):
            if parent not in progress:
                continue
            progress[parent]["total"] += 1
            progress[parent][status] += 1

    specdock_dir = _require_specdock(target_root)
    state_path = specdock_dir / _WORK_DIRNAME / "state.json"
    current_path = specdock_dir / _WORK_DIRNAME / "current.json"
    current = _load_json(current_path) if current_path.exists() else None

    out_nodes: dict[str, Any] = {}
    for node in nodes.values():
        item: dict[str, Any] = {
            "type": node.type,
            "id": node.id,
            "title": node.title,
            "path": node.path.relative_to(target_root).as_posix(),
            "parent_id": node.parent_id,
            "initiative_id": node.initiative_id,
            "epic_id": node.epic_id,
            "children": sorted(children.get(node.id, [])),
        }

        if node.github_issue_number is not None:
            item["github"] = {"issue_number": node.github_issue_number}
            if github:
                gh = issue_index.get(node.github_issue_number)
                if gh:
                    item["github"].update(
                        {
                            "state": gh.get("state"),
                            "url": gh.get("url"),
                            "updated_at": gh.get("updatedAt"),
                            "labels": [lbl.get("name") for lbl in (gh.get("labels") or []) if isinstance(lbl, dict)],
                        }
                    )

        if node.id in progress:
            item["progress"] = progress[node.id]

        out_nodes[node.id] = item

    state = {
        "schema_version": 1,
        "generated_at": _now_iso(),
        "root": f"{_SPEC_DOCK_DIRNAME}/{_INITIATIVES_DIRNAME}",
        "active": current,
        "nodes": out_nodes,
    }
    _write_json(state_path, state)


def _validate(target_root: Path) -> None:
    nodes = _scan_nodes(target_root)
    for node_id, node in nodes.items():
        _validate_lowercase(node_id, field="id")
        _parse_id(node_id)
        if not node.title:
            raise RuntimeError(f"Missing title in meta.json: {node.path / 'meta.json'}")

        if node.type == "initiative":
            continue

        if node.type == "epic":
            if not node.initiative_id:
                raise RuntimeError(f"epic missing initiative_id: {node.path / 'meta.json'}")
            parent = nodes.get(node.initiative_id)
            if not parent or parent.type != "initiative":
                raise RuntimeError(f"epic points to invalid initiative_id: {node.initiative_id}")
            continue

        if node.type == "issue":
            if not node.initiative_id or not node.epic_id:
                raise RuntimeError(f"issue missing initiative_id/epic_id: {node.path / 'meta.json'}")
            epic = nodes.get(node.epic_id)
            if not epic or epic.type != "epic":
                raise RuntimeError(f"issue points to invalid epic_id: {node.epic_id}")
            initiative = nodes.get(node.initiative_id)
            if not initiative or initiative.type != "initiative":
                raise RuntimeError(f"issue points to invalid initiative_id: {node.initiative_id}")
            continue

        raise RuntimeError(f"Unknown node type: {node.type} ({node.path / 'meta.json'})")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_init_update_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
        p.add_argument("--no-skill", action="store_true", help="Do not install the Codex skill into '.codex/skills/'")

    def add_workspace_root_opt(p: argparse.ArgumentParser) -> None:
        p.add_argument("--path", default=".", help="Target project path (default: current directory)")

    p_init = sub.add_parser("init", help="Scaffold .spec-dock into a project")
    add_init_update_common(p_init)
    p_init.add_argument("--force", action="store_true", help="Overwrite managed files if '.spec-dock' already exists")

    p_update = sub.add_parser("update", help="Update managed files (docs/templates/scripts/skill) in an existing project")
    add_init_update_common(p_update)

    p_new = sub.add_parser("new", help="Create a new node (initiative/epic/issue/adr)")
    new_sub = p_new.add_subparsers(dest="new_kind", required=True)

    p_new_init = new_sub.add_parser("initiative", help="Create a new initiative")
    add_workspace_root_opt(p_new_init)
    p_new_init.add_argument("--title", required=True)
    p_new_init.add_argument("--slug")
    p_new_init.add_argument("--id")
    p_new_init.add_argument("--github-issue", type=int)

    p_new_epic = new_sub.add_parser("epic", help="Create a new epic under an initiative")
    add_workspace_root_opt(p_new_epic)
    p_new_epic.add_argument("--initiative", required=True, help="Parent initiative id (e.g. init-0001)")
    p_new_epic.add_argument("--title", required=True)
    p_new_epic.add_argument("--slug")
    p_new_epic.add_argument("--id")
    p_new_epic.add_argument("--github-issue", type=int)

    p_new_issue = new_sub.add_parser("issue", help="Create a new issue under an epic")
    add_workspace_root_opt(p_new_issue)
    p_new_issue.add_argument("--epic", required=True, help="Parent epic id (e.g. epic-0001)")
    p_new_issue.add_argument("--title", required=True)
    p_new_issue.add_argument("--slug")
    p_new_issue.add_argument("--id")
    p_new_issue.add_argument("--github-issue", type=int)

    p_new_adr = new_sub.add_parser("adr", help="Create a new ADR under a scope (initiative/epic/issue)")
    add_workspace_root_opt(p_new_adr)
    scope = p_new_adr.add_mutually_exclusive_group(required=True)
    scope.add_argument("--initiative", help="Scope initiative id (e.g. init-0001)")
    scope.add_argument("--epic", help="Scope epic id (e.g. epic-0001)")
    scope.add_argument("--issue", help="Scope issue id (e.g. iss-0001)")
    p_new_adr.add_argument("--title", required=True)
    p_new_adr.add_argument("--slug")
    p_new_adr.add_argument("--id")

    p_active = sub.add_parser("active", help="Manage the active pointers")
    active_sub = p_active.add_subparsers(dest="active_cmd", required=True)

    p_active_set = active_sub.add_parser("set", help="Set the active issue")
    add_workspace_root_opt(p_active_set)
    p_active_set.add_argument("--issue", required=True, help="Issue id (e.g. iss-0001)")

    p_active_show = active_sub.add_parser("show", help="Show current active pointers")
    add_workspace_root_opt(p_active_show)

    p_active_clear = active_sub.add_parser("clear", help="Clear active pointers")
    add_workspace_root_opt(p_active_clear)

    p_sync = sub.add_parser("sync", help="Generate state.json (optionally enrich from GitHub)")
    add_workspace_root_opt(p_sync)
    p_sync.add_argument("--github", action="store_true", help="Fetch GitHub issue states via gh CLI")
    p_sync.add_argument("--gh-limit", type=int, default=10000, help="gh issue list limit (default: 10000)")

    p_validate = sub.add_parser("validate", help="Validate the spec tree structure")
    add_workspace_root_opt(p_validate)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    target_root = Path(getattr(ns, "path", ".")).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        print(f"error: target path is not a directory: {target_root}", file=sys.stderr)
        return 2

    try:
        if ns.command == "init":
            _install_spec_dock(target_root, force=bool(ns.force))
            if not ns.no_skill:
                _install_skill(target_root, force=bool(ns.force))
        elif ns.command == "update":
            _install_spec_dock(target_root, force=True)
            if not ns.no_skill:
                _install_skill(target_root, force=True)
        elif ns.command == "new":
            new_root = Path(ns.path).expanduser().resolve()
            if ns.new_kind == "initiative":
                _new_initiative(
                    new_root,
                    title=str(ns.title),
                    slug=getattr(ns, "slug", None),
                    node_id=getattr(ns, "id", None),
                    github_issue_number=getattr(ns, "github_issue", None),
                )
            elif ns.new_kind == "epic":
                _new_epic(
                    new_root,
                    initiative_id=str(ns.initiative),
                    title=str(ns.title),
                    slug=getattr(ns, "slug", None),
                    node_id=getattr(ns, "id", None),
                    github_issue_number=getattr(ns, "github_issue", None),
                )
            elif ns.new_kind == "issue":
                _new_issue(
                    new_root,
                    epic_id=str(ns.epic),
                    title=str(ns.title),
                    slug=getattr(ns, "slug", None),
                    node_id=getattr(ns, "id", None),
                    github_issue_number=getattr(ns, "github_issue", None),
                )
            elif ns.new_kind == "adr":
                scope_id = getattr(ns, "initiative", None) or getattr(ns, "epic", None) or getattr(ns, "issue", None)
                _new_adr(
                    new_root,
                    scope_id=str(scope_id),
                    title=str(ns.title),
                    slug=getattr(ns, "slug", None),
                    node_id=getattr(ns, "id", None),
                )
            else:
                raise RuntimeError(f"Unknown new kind: {ns.new_kind}")
        elif ns.command == "active":
            active_root = Path(ns.path).expanduser().resolve()
            if ns.active_cmd == "set":
                _active_set(active_root, issue_id=str(ns.issue))
            elif ns.active_cmd == "show":
                _active_show(active_root)
            elif ns.active_cmd == "clear":
                _active_clear(active_root)
            else:
                raise RuntimeError(f"Unknown active command: {ns.active_cmd}")
        elif ns.command == "sync":
            sync_root = Path(ns.path).expanduser().resolve()
            _sync(sync_root, github=bool(ns.github), gh_limit=int(ns.gh_limit))
        elif ns.command == "validate":
            validate_root = Path(ns.path).expanduser().resolve()
            _validate(validate_root)
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
