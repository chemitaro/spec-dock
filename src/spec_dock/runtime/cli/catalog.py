"""The complete vNext CLI leaf inventory."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from spec_dock.runtime.domain.assurance import ASSURANCE_LEVELS


@dataclass(frozen=True)
class ArgumentSpec:
    names: tuple[str, ...]
    options: dict[str, Any]


def _arg(name: str, **options: Any) -> ArgumentSpec:
    return ArgumentSpec((name,), options)


def _required(name: str, **options: Any) -> ArgumentSpec:
    return _arg(name, required=True, **options)


def _flag(name: str) -> ArgumentSpec:
    return _arg(name, action="store_true")


KINDS = ("initiative", "epic", "issue")
STATES = ("open", "completed", "not-planned", "unknown")
ARTIFACT_TYPES = ("blank", "research", "interview", "disc", "decision-candidate", "adr")
TODO_KINDS = ("decide", "check", "operate", "act", "todo", "checklist")
TODO_STATUSES = ("open", "snoozed", "done", "cancelled", "all")

LEAF_PATHS: tuple[str, ...] = (
    "scope create initiative",
    "scope create epic",
    "scope create issue",
    "scope import github initiative",
    "scope import github epic",
    "scope import github issue",
    "scope list",
    "scope show",
    "scope check",
    "scope render",
    "scope edit",
    "scope close",
    "scope reopen",
    "scope delete",
    "scope move",
    "active show",
    "active set",
    "active clear",
    "work start",
    "work finish",
    "branch show",
    "branch create",
    "branch switch",
    "dependency list",
    "dependency check",
    "dependency add",
    "dependency remove",
    "artifact create",
    "artifact import file",
    "artifact list",
    "artifact show",
    "worktree create",
    "worktree list",
    "worktree show",
    "worktree remove",
    "worktree bootstrap",
    "workspace sync",
    "workspace validate",
    "workspace doctor",
    "canonical link",
    "canonical status",
    "installation show",
    "installation init",
    "installation update",
    "installation uninstall",
    "canonical check",
    "canonical sync",
    "canonical accept",
    "canonical restore",
    "canonical resume",
    "canonical remove",
    "dashboard summary",
    "dashboard serve",
    "dashboard hide",
    "dashboard show",
    "dashboard list",
    "dashboard service install",
    "dashboard service status",
    "dashboard service uninstall",
    "todo add",
    "todo list",
    "todo show",
    "todo update",
    "todo done",
    "todo snooze",
    "todo cancel",
    "todo reopen",
    "todo check",
    "todo settings",
    "help",
    "completion",
)

HELP_EFFECTS: dict[str, str] = {
    "scope create initiative": "Create a GitHub Issue, then publish Initiative files using its confirmed number.",
    "scope create epic": "Create a GitHub Issue, then publish Epic files using its confirmed number.",
    "scope create issue": "Create a GitHub Issue, then publish Issue files using its confirmed number.",
    "scope import github initiative": "Read a GitHub Issue and create linked Initiative files.",
    "scope import github epic": "Read a GitHub Issue and create linked Epic files.",
    "scope import github issue": "Read a GitHub Issue and create linked Issue files.",
    "scope list": "Read Scopes from the GitHub structure snapshot and the catalog; no changes.",
    "scope show": "Read one Scope and its observed status; no changes.",
    "scope check": "Check one CUE Scope's documents and explanation offline; no changes.",
    "scope render": "Draw one CUE Scope's requirement, design and plan as HTML on standard output; no changes.",
    "scope edit": "Change the Scope's GitHub Issue title; catalog files are unchanged.",
    "scope close": "Complete or cancel one Scope's GitHub Issue; active selection stays set.",
    "scope reopen": "Reopen one Scope's GitHub Issue; active selection stays set.",
    "scope delete": "Detach the Scope in GitHub and delete its catalog directory; the Issue and branches remain.",
    "scope move": "Change a Scope parent in GitHub; the flat catalog directory does not move.",
    "active show": "Read this worktree's active selection; no changes.",
    "active set": "Keep the same valid direct selection unchanged and repair only its spec-dock/active navigation links; acquiring another selection requires work start.",
    "active clear": "Remove only observed local direct records and point spec-dock/active links at the fallback when none remains; never promote an ancestor.",
    "work start": "Create or reuse a branch, checkout it, select the ready Scope, and point spec-dock/active links at its chain.",
    "work finish": "Complete the Scope, then clear the captured direct record only if it selects that Scope or a descendant and point spec-dock/active links at the fallback; keep the current branch.",
    "branch show": "Observe the explicit or default candidate Git ref; no binding is persisted.",
    "branch create": "Create only a new Git branch at a fixed base; no checkout or binding record.",
    "branch switch": "Checkout an existing Git branch under the clone Start lock; the direct selection record stays unchanged.",
    "dependency list": "Read declared or effective dependency edges; no changes.",
    "dependency check": "Read dependency readiness and status evidence; no changes.",
    "dependency add": "Add a blocked-by dependency between two Scope Issues in GitHub.",
    "dependency remove": "Remove a blocked-by dependency between two Scope Issues in GitHub.",
    "artifact create": "Publish one complete Scope-owned or @root Markdown file without overwrite or a shared counter.",
    "artifact import file": "Publish one opaque regular file in the selected Scope or @root without overwrite or a shared counter.",
    "artifact list": "Read Artifact identifiers; no changes.",
    "artifact show": "Read Artifact metadata without exposing its content; no changes.",
    "worktree create": "Create branch worktree/NAME from the fixed base and attach root/NAME using native Git; bootstrap is separate.",
    "worktree list": "Read native Git worktree inventory; no changes.",
    "worktree show": "Read one absolute path in the native Git worktree inventory; no changes.",
    "worktree remove": "Remove one explicit native Git worktree directory; keep its branch.",
    "worktree bootstrap": "Run make init once in one explicit native worktree; hook output is omitted.",
    "workspace sync": "Observe current Scope lifecycle and same-clone worktree selections without writing files.",
    "workspace validate": "Validate the GitHub structure snapshot against the catalog directories and documents; no changes.",
    "workspace doctor": "Read current workspace evidence and explicit raw/legacy diagnostics; no repair.",
    "canonical link": "Find or create this clone's catalog, link this checkout, and register periodic sync.",
    "canonical status": "Read catalog, link, access, tool settings and sync state; no changes.",
    "installation show": "Read the package version and static resources in one Git worktree; no changes.",
    "installation init": "Place package static resources and a new schema-4 workspace declaration in one Git worktree.",
    "installation update": "Update package static resources in one Git worktree after verified external preservation.",
    "installation uninstall": "Remove known package static resources from one Git worktree while preserving user work and state.",
    "canonical check": "Check that a commit of the code tree holds no specs and has intact SpecDock files; for CI.",
    "canonical sync": "Save, merge and push the catalog once; `--registered` processes every registered catalog; `--loop` keeps running as the resident runner where systemd is unavailable.",
    "canonical accept": "Allow held changes to be saved by the next sync.",
    "canonical restore": "Restore held deletions or paths from the catalog HEAD; no commit.",
    "canonical resume": "Resume a paused catalog after the user decided how to treat the remote.",
    "canonical remove": "Remove this clone's catalog, links and sync registration after confirming nothing is unsaved.",
    "dashboard summary": "Read one repository's dashboard summary (specdock.dashboard-summary/v1), with its human-task counts, from local files; no changes.",
    "dashboard serve": "Serve the read-only dashboard of every shown registered repository in the foreground until Ctrl-C or SIGTERM.",
    "dashboard hide": "Hide one repository from the dashboard; the periodic sync continues.",
    "dashboard show": "Show a hidden repository on the dashboard again.",
    "dashboard list": "List the registered repositories, whether each is shown or hidden, and the server URL; no changes.",
    "dashboard service install": "Install the per-user service that starts the dashboard server at login and keeps it running (launchd or a systemd user service).",
    "dashboard service status": "Show whether the dashboard service is installed and loaded, whether a server runs, its URL and versions; no changes.",
    "dashboard service uninstall": "Stop and remove the dashboard service, its job file and its log; the periodic sync is untouched.",
    "todo add": "Write one new human task (or a subtask into its task's file) under the catalog's todos/<YYYY-MM>/; nothing goes to GitHub.",
    "todo list": "List this repository's human tasks from the catalog's todos/, or every registered repository's with --all-repositories (specdock.todo-list/v1); no changes.",
    "todo show": "Read one human task (by ID here, or by REF owner/name/t-xxxx from the registry) with its subtasks, remaining items and derived states; no changes.",
    "todo update": "Change fields of one human task or a subtask's title in its file, recording the changed field names in history.",
    "todo done": "Close one human task or subtask as done, writing its resolution and history; the file stays in place.",
    "todo snooze": "Hide one open human task from the default list until a time; its file stays in place.",
    "todo cancel": "Close one human task or subtask as cancelled with a reason; the file stays in place.",
    "todo reopen": "Reopen a closed human task or subtask; the earlier answer stays in history.",
    "todo check": "Check every file under the catalog's todos/ with the Python rules and, when cue is on PATH, cue vet; no changes.",
    "todo settings": "Show the effective human-task settings and the layer each comes from (default, user, repository); no changes.",
    "help": "Print command help; no changes.",
    "completion": "Print shell completion without changing shell configuration.",
}
if set(HELP_EFFECTS) != set(LEAF_PATHS):
    raise RuntimeError("help effects do not match the public CLI leaves")


# Optional to the parser so a missing value stops with ASSURANCE_REQUIRED before any read (iss-00474, Q1).
_ASSURANCE_ARGUMENTS = (_arg("--assurance", choices=ASSURANCE_LEVELS), _arg("--assurance-reason"))

LEAF_ARGUMENTS: dict[str, tuple[ArgumentSpec, ...]] = {
    "scope create initiative": (
        _required("--backend", choices=("github",)),
        _required("--title"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope create epic": (
        _required("--backend", choices=("github",)),
        _required("--parent"),
        _required("--title"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope create issue": (
        _required("--backend", choices=("github",)),
        _required("--parent"),
        _required("--title"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope import github initiative": (
        _arg("github_ref"),
        _required("--title"),
        _arg("--github-repo"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope import github epic": (
        _arg("github_ref"),
        _required("--parent"),
        _required("--title"),
        _arg("--github-repo"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope import github issue": (
        _arg("github_ref"),
        _required("--parent"),
        _required("--title"),
        _arg("--github-repo"),
        *_ASSURANCE_ARGUMENTS,
    ),
    "scope list": (_arg("--kind", choices=KINDS), _arg("--parent"), _arg("--state", choices=STATES)),
    "scope show": (_arg("target"),),
    "scope check": (_arg("target"),),
    "scope render": (_arg("target"), _arg("--design-system", choices=("file", "inline"), default="file")),
    "scope edit": (_arg("target"), _required("--title")),
    "scope close": (_arg("target"), _arg("--reason", choices=("completed", "not-planned"), default="completed")),
    "scope reopen": (_arg("target"),),
    "scope delete": (
        _arg("target"),
        _flag("--recursive"),
        _flag("--clear-active"),
        _flag("--detach-dependencies"),
        _arg("--backup-dir"),
    ),
    "scope move": (_arg("target"), _required("--parent")),
    "active show": (),
    "active set": (_arg("target"),),
    "active clear": (_arg("--from", dest="from_target"), _flag("--all")),
    "work start": (
        _arg("target"),
        _arg("--branch"),
        _arg("--base"),
        _flag("--switch-active"),
        _arg("--source", choices=("github",), default="github"),
    ),
    "work finish": (_arg("target"),),
    "branch show": (_arg("target"), _arg("--name")),
    "branch create": (_arg("target"), _arg("--name"), _arg("--base")),
    "branch switch": (_arg("target"), _arg("--name")),
    "dependency list": (_arg("target"), _arg("--view", choices=("declared", "effective"))),
    "dependency check": (_arg("target"), _arg("--source", choices=("github",))),
    "dependency add": (_required("--from", dest="from_target"), _required("--to", dest="to_target")),
    "dependency remove": (
        _required("--from", dest="from_target"),
        _required("--to", dest="to_target"),
        _flag("--missing-ok"),
    ),
    "artifact create": (
        _required("--scope"),
        _required("--type", choices=ARTIFACT_TYPES),
        _required("--title"),
        _arg("--slug"),
    ),
    "artifact import file": (_arg("path"), _required("--scope")),
    "artifact list": (_required("--scope"),),
    "artifact show": (_arg("artifact_id"), _required("--scope")),
    "worktree create": (_arg("name"), _required("--base"), _arg("--root")),
    "worktree list": (),
    "worktree show": (_arg("worktree_ref"),),
    "worktree remove": (_arg("worktree_ref"), _flag("--unlock"), _flag("--discard-ignored")),
    "worktree bootstrap": (_arg("worktree_ref"),),
    "workspace sync": (_arg("--source", choices=("github",)), _flag("--allow-invalid")),
    "workspace validate": (_flag("--require-nodes"),),
    "workspace doctor": (
        _flag("--raw"),
        _flag("--legacy"),
        _arg("--github-repo"),
        _arg("--github-pr"),
        _arg("--github-head-sha"),
        _flag("--github-extended"),
    ),
    "canonical link": (_flag("--no-schedule"),),
    "canonical status": (_flag("--structure"),),
    "installation show": (_arg("--target"),),
    "installation init": (_arg("path"),),
    "installation update": (_arg("--target"), _arg("--backup-dir")),
    "installation uninstall": (_arg("--target"), _arg("--backup-dir")),
    "canonical check": (_arg("--commit", default="HEAD"),),
    "canonical sync": (_flag("--registered"), _arg("--state-root"), _flag("--loop"), _flag("--detach")),
    "canonical accept": (_arg("paths", nargs="*"), _flag("--deletions")),
    "canonical restore": (_arg("paths", nargs="*"),),
    "canonical resume": (_flag("--adopt-remote"), _flag("--push-local")),
    "canonical remove": (),
    "dashboard summary": (_arg("repository", nargs="?"),),
    "dashboard serve": (
        _arg("--port", type=int),
        _flag("--tailscale"),
        _arg("--state-root"),
        _arg("--service", action="store_true", help=argparse.SUPPRESS),
    ),
    "dashboard hide": (_arg("repository", nargs="?"),),
    "dashboard show": (_arg("repository", nargs="?"),),
    "dashboard list": (),
    "dashboard service install": (_arg("--port", type=int), _flag("--tailscale")),
    "dashboard service status": (),
    "dashboard service uninstall": (),
    "todo add": (
        _required("--title"),
        _arg("--kind", choices=TODO_KINDS),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
        _arg("--body"),
        _arg("--body-file"),
        _arg("--option", action="append", metavar="KEY=TEXT"),
        _arg("--recommend", metavar="KEY"),
        _arg("--reason"),
        _arg("--reply-to"),
        _arg("--effort"),
        _arg("--due", metavar="WHEN"),
        _arg("--scope", action="append", metavar="ID"),
        _arg("--blocks", action="append", metavar="ID"),
        _arg("--link", action="append"),
        _arg("--tag", action="append"),
        _arg("--parent", metavar="ID"),
        _arg("--item", action="append", metavar="TITLE"),
    ),
    "todo list": (
        _arg("--status", choices=TODO_STATUSES, default="open"),
        _arg("--scope", metavar="ID"),
        _arg("--kind", choices=TODO_KINDS),
        _arg("--tag"),
        _flag("--blocking"),
        _flag("--overdue"),
        _flag("--all-repositories"),
        _arg("--repository", action="append", metavar="REPOSITORY"),
    ),
    "todo show": (_arg("id", metavar="ID|REF"),),
    "todo update": (
        _arg("id"),
        _arg("--title"),
        _arg("--body"),
        _arg("--body-file"),
        _arg("--kind", choices=TODO_KINDS),
        _arg("--due", metavar="WHEN"),
        _arg("--reply-to"),
        _arg("--effort"),
        _arg("--option", action="append", metavar="KEY=TEXT"),
        _arg("--recommend", metavar="KEY"),
        _arg("--reason"),
        _arg("--add-scope", action="append", metavar="ID"),
        _arg("--remove-scope", action="append", metavar="ID"),
        _arg("--add-blocks", action="append", metavar="ID"),
        _arg("--remove-blocks", action="append", metavar="ID"),
        _arg("--add-tag", action="append"),
        _arg("--remove-tag", action="append"),
        _arg("--add-link", action="append"),
        _arg("--remove-link", action="append"),
        _arg("--note"),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
    ),
    "todo done": (
        _arg("id"),
        _arg("--choice", metavar="KEY"),
        _arg("--note"),
        _arg("--record", metavar="PATH_OR_URL"),
        _flag("--include-subtasks"),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
    ),
    "todo snooze": (
        _arg("id"),
        _required("--until", metavar="WHEN"),
        _arg("--due", metavar="WHEN"),
        _arg("--note"),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
    ),
    "todo cancel": (
        _arg("id"),
        _required("--reason"),
        _flag("--include-subtasks"),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
    ),
    "todo reopen": (
        _arg("id"),
        _arg("--due", metavar="WHEN"),
        _arg("--note"),
        _arg("--by", choices=("agent", "human")),
        _arg("--role"),
    ),
    "todo check": (),
    "todo settings": (),
    "help": (_arg("help_path", nargs="*"),),
    "completion": (_arg("shell", choices=("bash", "zsh", "fish")),),
}

# Temporary compatibility for the retired internal dispatcher, never public syntax.
RECOVERY_LEAF_COMMANDS: dict[str, str] = {
    "installation init": "installation.init",
    "installation update": "installation.update",
    "installation uninstall": "installation.uninstall",
}
MUTATING_LEAF_PATHS = frozenset({
    "scope create initiative",
    "scope create epic",
    "scope create issue",
    "scope import github initiative",
    "scope import github epic",
    "scope import github issue",
    "scope edit",
    "scope close",
    "scope reopen",
    "scope delete",
    "scope move",
    "active set",
    "active clear",
    "work start",
    "work finish",
    "branch create",
    "branch switch",
    "dependency add",
    "dependency remove",
    "artifact create",
    "artifact import file",
    "worktree create",
    "worktree remove",
    "worktree bootstrap",
    "canonical link",
    "canonical sync",
    "canonical accept",
    "canonical restore",
    "canonical resume",
    "canonical remove",
    "installation init",
    "installation update",
    "installation uninstall",
    "todo add",
    "todo update",
    "todo done",
    "todo snooze",
    "todo cancel",
    "todo reopen",
})


@dataclass(frozen=True)
class HelpSpec:
    target: str
    reads: str
    writes: str
    does_not: str
    preconditions: str
    confirmation: str
    json: str
    examples: str


HELP_PRECONDITIONS: dict[str, str] = {
    "scope create initiative": "Provide a title and backend; GitHub creation needs a reachable repository. The flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title. --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update).",
    "scope create epic": "Provide a title and existing Initiative parent; GitHub creation needs a reachable repository. The flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title. --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update).",
    "scope create issue": "Provide a title and existing Epic parent; GitHub creation needs a reachable repository. The flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title. --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update).",
    "scope import github initiative": "The GitHub reference must resolve to an Issue not already imported. Adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ). --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update). An existing Scope directory is kept as it is (warning ASSURANCE_NOT_WRITTEN).",
    "scope import github epic": "The GitHub Issue must exist and the Initiative parent must resolve. Adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ). --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update). An existing Scope directory is kept as it is (warning ASSURANCE_NOT_WRITTEN).",
    "scope import github issue": "The GitHub Issue must exist and the Epic parent must resolve. Adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ). --assurance LEVEL (light|standard|strict|critical) and a non-blank --assurance-reason TEXT are required (otherwise ASSURANCE_REQUIRED, nothing is read or written); the files come from spec-dock/templates/cue/<kind>/ (otherwise SCOPE_TEMPLATES_OUTDATED: run spec-dock installation update). An existing Scope directory is kept as it is (warning ASSURANCE_NOT_WRITTEN).",
    "scope list": "A schema-4 checkout whose catalog is linked; the structure snapshot is read (GitHub only when it is missing or outdated).",
    "scope show": "The Scope ID or @current selector must resolve in this worktree.",
    "scope check": "The Scope must have its catalog directory. A CUE Scope (requirement.cue) needs cue v0.17.1 or later on PATH (CUE_NOT_FOUND, CUE_VERSION_UNSUPPORTED) and a type version this SpecDock ships (CUE_SCHEMA_UNSUPPORTED); a Markdown Scope succeeds with checked=false and needs no cue.",
    "scope render": "The Scope must have its catalog directory and be a CUE Scope (a Markdown Scope stops with SCOPE_NOT_CUE). Needs cue v0.17.1 or later on PATH and a type version this SpecDock ships, like scope check. The page loads the checkout's spec-dock/design-system/ through a file: URL (warning DESIGN_SYSTEM_MISSING when it is absent) and diagram parts from the CDN. --design-system inline carries ds.css, ds.js and marked inside the page instead, so it keeps its style on another machine (about 400KB; DESIGN_SYSTEM_MISSING stops with exit 3 when they are absent).",
    "scope edit": "The target must resolve in the GitHub structure; a non-blank title of at most 256 characters in any language.",
    "scope close": "The Scope must resolve; completion requires every descendant to be completed or not planned (an open or unknown one stops it) and the expected state guards must match.",
    "scope reopen": "The Scope must resolve and its expected state guards must match.",
    "scope delete": "Require --backup-dir ABS for a new real backup; descendants require --recursive, incoming edges require --detach-dependencies, and a selected descendant requires --clear-active.",
    "scope move": "--parent is required and must be the right kind and open, and not the Scope or one of its descendants.",
    "active show": "The selected worktree must have readable active-selection state.",
    "active set": "Only the same valid direct target is accepted; its selection stays unchanged. Use work start to acquire a selection.",
    "active clear": "--from requires a valid current chain; --all --yes permits discarding observed corrupt regular records. Unknown entries are preserved; ancestors are never promoted.",
    "work start": "The Scope must be ready, its dependencies satisfied, and branch base resolvable. The default branch name is <ID> (IDs may be given without zero padding, e.g. iss-454); an in-progress mark from another PC only warns SCOPE_IN_PROGRESS (ask the user); SCOPE_KIND_CHANGED and a base commit holding spec-dock/initiatives (CANONICAL_BASE_HAS_SPECS) stop.",
    "work finish": "The explicit Scope must resolve and its completion guards must pass. A Scope outside the active chain can be completed without changing the current selection. Unsaved specs of the Scope and its descendants are saved and pushed first, waiting up to 180 seconds; unconfirmed, the Issue stays open with CANONICAL_SAVE_UNCONFIRMED, and held changes stop with CANONICAL_SAVE_HELD.",
    "branch show": "The Scope must resolve; the candidate Git ref may be absent.",
    "branch create": "The Scope must resolve, Git base must exist, and branch ownership must be free.",
    "branch switch": "The existing branch must contain the target and ancestors; the worktree must be clean; the clone Start lock must be free within --lock-timeout, else START_LOCK_BUSY.",
    "dependency list": "The selected Scope must resolve in the current hierarchy.",
    "dependency check": "The selected Scope must resolve; --source github requires remote access.",
    "dependency add": "Both endpoints must resolve and the edge must preserve dependency rules.",
    "dependency remove": "Both endpoints must resolve; --missing-ok permits an absent declared edge.",
    "artifact create": "The owner must be an existing Scope or @root, and the Artifact type must be supported.",
    "artifact import file": "The owner must be an existing Scope or @root, and the regular source file must exist.",
    "artifact list": "The owner must be an existing Scope or @root, and its catalog must be readable.",
    "artifact show": "The owner must be an existing Scope or @root, and the Artifact ID must resolve.",
    "worktree create": "A clean source, explicit lowercase NAME and fixed Git base are required. Placement uses --root, then SPEC_DOCK_WORKTREE_ROOT; the path and branch must be absent.",
    "worktree list": "The current clone must have readable native Git worktree inventory.",
    "worktree show": "An absolute worktree path must resolve in the same physical Git clone; aliases were retired.",
    "worktree remove": "Use an absolute path in the same clone. Main/current/bare or dirty worktrees cannot be removed. Locked and ignored content require explicit opt-ins and confirmation.",
    "worktree bootstrap": "Use an absolute path in the same clone, a project-owned regular makefile, and --yes. Dry-run never runs make; offline apply is refused.",
    "workspace sync": "Unknown schemas and unsafe paths are refused even with --allow-invalid; incomplete observations return exit 7.",
    "workspace validate": "A schema-4 checkout whose catalog is linked; each Scope needs its spec-dock/initiatives/<bucket>/<ID>/ directory and documents, and document bodies are not judged. In CI, use canonical check instead. Invalid or incomplete structure returns exit 7.",
    "workspace doctor": "Use a Git worktree; --raw reports an unreadable workspace declaration instead of stopping, and --legacy only inspects retired files. GitHub probes require a fixed repository, PR and head SHA.",
    "canonical link": "A schema-4 workspace in a clone with a main checkout and Git 2.38 or later. Stops before writing when the catalog path, a link path or the spec-dock/canonical checkout is occupied, when the checkout looks mounted from another machine, or when this process cannot write where it must (including the state root and the periodic job). --no-schedule records the baseline but registers no periodic job.",
    "canonical status": "A schema-4 workspace in a clone with a main checkout; it never contacts GitHub or the remote.",
    "installation show": "The selected target must be one exact Git worktree root; no workspace or control record is required.",
    "installation init": "PATH must be a Git worktree root eligible for initial installation.",
    "installation update": "A schema-4 worktree-writer workspace and known static hashes are required. Changes need a new external --backup-dir under an existing physical parent and --yes; --dry-run writes nothing. Modified or unknown files require manual merge.",
    "installation uninstall": "Use a schema-4 worktree-writer workspace. Remove only known static hashes after a new external --backup-dir and --yes; --dry-run writes nothing. Modified files stop before changes.",
    "canonical check": "A Git checkout containing the commit (default HEAD); no catalog, network or GitHub token is required, and a schema-3 declaration is reported as one problem. Any problem in the commit tree returns exit 7 with each path and its next step.",
    "canonical sync": "Without --registered: a schema-4 checkout whose catalog is linked. --registered needs no project and reads the registry of --state-root (default ${XDG_STATE_HOME:-~/.local/state}/spec-dock). --loop needs --registered and --detach needs --loop.",
    "canonical accept": "A linked schema-4 checkout; name existing catalog files (relative to spec-dock/initiatives) or --deletions for the held deletions.",
    "canonical restore": "A linked schema-4 checkout; every named path must be held (changes.holds) and exist in the catalog HEAD. Without paths, every held deletion is restored.",
    "canonical resume": "A linked schema-4 checkout whose catalog is paused; --adopt-remote for remote_rewritten or merge_failed, --push-local for remote_deleted.",
    "canonical remove": "A schema-4 checkout of a clone with a main checkout; stops before writing on unsaved or unpushed changes or on ignored files other than .runtime/ in the catalog. Without --yes it only reports the plan.",
    "dashboard summary": "Inside a schema-4 checkout REPOSITORY may be omitted (it comes from the origin remote); elsewhere pass owner/name or github.com/owner/name. The repository's structure snapshot must exist and be readable (DASHBOARD_SNAPSHOT_MISSING, DASHBOARD_SNAPSHOT_UNREADABLE, DASHBOARD_SNAPSHOT_UNSUPPORTED stop with exit 3). Works without a running dashboard server and for hidden repositories; it never contacts GitHub or the server. todos counts the repository's open (snoozed included), blocking and overdue parent tasks: inside a checkout whose link is correct from its catalog, otherwise from the registry's catalog; when they cannot be read todos.status is unavailable with a problem and the summary still succeeds.",
    "dashboard serve": "No project is required. Listens on 127.0.0.1 only, port 47800 by default (--port N; 0 picks a free port); --tailscale also listens on this PC's Tailscale IPv4 address from `tailscale ip -4` (DASHBOARD_TAILSCALE_UNAVAILABLE exits 3 when there is none). A used port stops with DASHBOARD_PORT_IN_USE (exit 3). When a server already runs, its URL is shown and the command exits 0.",
    "dashboard hide": "Inside a schema-4 checkout REPOSITORY may be omitted (it comes from the origin remote); elsewhere pass owner/name or github.com/owner/name. An unreadable marks file stops with DASHBOARD_STATE_UNREADABLE (exit 3) and is not overwritten.",
    "dashboard show": "Inside a schema-4 checkout REPOSITORY may be omitted (it comes from the origin remote); elsewhere pass owner/name or github.com/owner/name. An unreadable marks file stops with DASHBOARD_STATE_UNREADABLE (exit 3) and is not overwritten.",
    "dashboard list": "No project is required; it reads the registry of the state root.",
    "dashboard service install": "No project is required. macOS (launchd) or Linux with a working systemd user manager; elsewhere DASHBOARD_SERVICE_UNSUPPORTED (exit 3) points to `spec-dock dashboard serve`. --port N is 1-65535 (default 47800). A launchctl/systemctl failure stops with DASHBOARD_SERVICE_FAILED (exit 3). Run it again to change --port or --tailscale.",
    "dashboard service status": "No project is required; on a PC without a service manager it reports supported=false.",
    "dashboard service uninstall": "No project is required; nothing installed is a success with removed=false.",
    "todo add": "A schema-4 checkout whose catalog is linked (CANONICAL_NOT_LINKED otherwise). A person (--by human, the default) needs only --title; an agent (--by agent) also needs --role, --kind, --body or --body-file, --reply-to and --effort, and decide needs two --option KEY=TEXT and --recommend KEY --reason TEXT (TODO_INVALID, exit 2, lists details.missing). --due takes 30m, 4h, 2d (up to 30d), YYYY-MM-DD or ISO 8601 with a zone; without it the default_due setting applies. --parent ID adds a subtask (only --title; a subtask's subtask stops with TODO_NESTING_TOO_DEEP); --item TITLE needs --kind checklist. A Scope ID not in the saved snapshot warns TODO_SCOPE_UNKNOWN; going over a limit warns TODO_LIMIT_EXCEEDED and still writes.",
    "todo list": "A schema-4 checkout whose catalog is linked, except with --all-repositories or --repository REPOSITORY (repeatable; implies --all-repositories), which read every catalog of this PC's registry without a checkout: a catalog that cannot be read is a row with status unreadable (TODO_REPOSITORY_UNREADABLE), a second clone a row with status duplicate (TODO_REPOSITORY_DUPLICATE), an unregistered --repository warns TODO_REPOSITORY_UNKNOWN, an unreadable registry stops with TODO_REGISTRY_UNREADABLE (exit 3) and a malformed REPOSITORY with TODO_REPOSITORY_INVALID (exit 2). --status open (the default) hides snoozed tasks until their time; --scope ID matches related or blocking Scopes. Broken records and conflict copies are warnings (TODO_RECORD_INVALID, TODO_CONFLICT_COPY) and never stop the list.",
    "todo show": "A schema-4 checkout whose catalog is linked; ID is t-xxxx or a subtask t-xxxx.N (its task is shown). REF (owner/name/t-xxxx or github.com/owner/name/t-xxxx) needs no checkout and reads the registry's catalog of that repository: TODO_REPOSITORY_UNKNOWN, TODO_REPOSITORY_UNREADABLE and TODO_REGISTRY_UNREADABLE exit 3, TODO_REPOSITORY_INVALID exits 2. TODO_NOT_FOUND, TODO_ID_AMBIGUOUS and TODO_RECORD_INVALID exit 3.",
    "todo update": "A schema-4 checkout whose catalog is linked and a valid record (TODO_RECORD_INVALID, TODO_SCHEMA_UNSUPPORTED exit 3). A subtask ID takes only --title and --note. Nothing changed is reported as unchanged.",
    "todo done": "A schema-4 checkout whose catalog is linked; the task must be open or snoozed (TODO_STATE_INVALID). Open subtasks stop it with TODO_SUBTASKS_OPEN unless --include-subtasks; --choice must be one of the options.",
    "todo snooze": "A schema-4 checkout whose catalog is linked; only an open or snoozed task, never a subtask. --until takes the same forms as --due and must be in the future.",
    "todo cancel": "A schema-4 checkout whose catalog is linked; --reason is required. Open subtasks stop it with TODO_SUBTASKS_OPEN unless --include-subtasks.",
    "todo reopen": "A schema-4 checkout whose catalog is linked; only a done or cancelled task or subtask. A subtask of a closed task stops with TODO_PARENT_CLOSED.",
    "todo check": "A schema-4 checkout whose catalog is linked. cue v0.17.1 or later on PATH adds cue vet; without it the warning TODO_CUE_SKIPPED says so and the Python check alone decides. Any error exits 7 with TODO_CHECK_FAILED.",
    "todo settings": "No checkout is required. Inside a schema-4 checkout the link must be correct (CANONICAL_NOT_LINKED) and todos/settings.json is read; outside one the repository layer is not_applicable. The user layer is $XDG_CONFIG_HOME/spec-dock/config.json (or ~/.config/spec-dock/config.json); SpecDock never creates it.",
    "help": "No project is required.",
    "completion": "No project is required; choose bash, zsh, or fish.",
}
if set(HELP_PRECONDITIONS) != set(LEAF_PATHS):
    raise RuntimeError("help preconditions do not match the public CLI leaves")


_CONFIRMATION_LEAVES = frozenset({
    "canonical remove",
    "scope close",
    "scope reopen",
    "scope delete",
    "work finish",
    "worktree remove",
    "worktree bootstrap",
    "installation init",
    "installation update",
    "installation uninstall",
})


_READS_BY_ROOT = {
    "scope": "The GitHub structure snapshot, the Scope's catalog directory, direct selection for selectors, and live GitHub for writes.",
    "active": "This worktree's active selection and the Scope hierarchy in the GitHub structure snapshot.",
    "work": "Current Scope hierarchy, direct selection, Git branch and HEAD, dependency evidence, and required live GitHub state.",
    "branch": "The Scope in the GitHub structure snapshot, Git refs, and Git worktree branch occupancy.",
    "dependency": "Blocked-by edges and inherited prerequisites in the GitHub structure snapshot, and status observations.",
    "artifact": "The selected Scope's Artifact catalog and safe file metadata.",
    "worktree": "Native Git worktree inventory, physical clone and path identity, branch and HEAD; the GitHub structure only for --expect-current.",
    "workspace": "Workspace declaration, the GitHub structure snapshot, the catalog, and explicitly requested remote observations.",
    "installation": "Installed package inventory and the selected worktree's declaration and static file snapshots.",
    "canonical": "This clone's canonical catalog and checkout links, or one commit tree, as each command states.",
    "dashboard": "The repository's structure snapshot, the dashboard hidden marks, the server location record (only whether its pid is alive) and, for summary, the catalog registry and the catalog's todos/ records.",
    "todo": "The catalog's todos/ records and todos/settings.json, the user settings file, the origin remote, the saved structure snapshot, the dashboard hidden marks and, for list --all-repositories/--repository and show REF, the catalog registry and every registered catalog's todos/.",
}

_DOES_NOT_BY_ROOT = {
    "scope": "Does not update other Scopes, change active selection, or implicitly switch branches.",
    "active": "Does not change lifecycle, dependencies, Git branch, or GitHub state.",
    "work": "Does not commit, push, merge, delete branches, or automatically roll back completed effects.",
    "branch": "Does not change Scope lifecycle or active selection.",
    "dependency": "Does not close a prerequisite or change GitHub issue state.",
    "artifact": "Does not print Artifact contents, source file hash, or external source path.",
    "worktree": "Does not mutate an independent repository or implicitly run project bootstrap.",
    "workspace": "Does not silently repair primary Scope data or active selection.",
    "installation": "Does not change other worktrees, Scope data, Artifacts, Workbenches, direct selections or Git metadata.",
    "canonical": "Does not change GitHub Issues or the default branch.",
    "dashboard": "Does not contact GitHub or the dashboard server, refresh the snapshot, or write any file.",
    "todo": "Does not contact GitHub, refresh the structure snapshot, change Scope state, dependencies or work start, move or delete a record, or write the user settings file.",
}

_JSON_DATA_BY_ROOT = {
    "scope": "Scope identity, backend, status, revision, and snapshot or list filters.",
    "active": "Direct selection status/token, derived ancestors, selected/current branch, and branch_changed.",
    "work": "Direct Scope ID, started or completed result, before/after branch, selection token, and effect outcomes.",
    "branch": "Scope ID, candidate ref name, observed tip, created/switched, and binding_persisted=false.",
    "dependency": "Declared/effective edges, readiness, blockers, and status provenance.",
    "artifact": "artifact:{id,scope_id,path,type},changed; list returns scope_id,items. Bodies and external source paths remain private.",
    "worktree": "path, branch, head, changed, observed; list returns items with path, branch, head, bare, locked, prunable.",
    "workspace": "Current observations, validity and findings.",
    "installation": "target, package_version, created_paths, changed_paths, retired_paths, backup_path and preservation checks.",
    "canonical": "The command's catalog, link, sync or check observations.",
    "todo": "kind=todo. One task: todo (specdock.todo/v1 record), derived (effective_status, overdue, due_soon, blocking, parent_closable, open_subtasks, subtask_counts), ref, repository, path, warnings_detail. list: specdock.todo-list/v1 (schema, generated_at, mode, filters, repositories, items). check: valid, checked_files, errors (code, file, field, message, source), warnings, cue. settings: values {key: {value, source}}, layers.",
    "dashboard": "result is the specdock.dashboard-summary/v1 document: schema, repository, fetched_at, stale, counts, completion_ratio, awaiting_merge, in_progress, ready, blocked, cleanup, anomaly_count, pull_requests, paths, hidden, server, todos {status, open, blocking, overdue, problem}.",
}


def _example(leaf: str) -> str:
    if leaf == "installation init":
        return "spec-dock installation init /absolute/worktree --yes"
    if leaf == "installation show":
        return "spec-dock installation show --target /absolute/worktree"
    if leaf in ("installation update", "installation uninstall"):
        return f"spec-dock {leaf} --target /absolute/worktree --backup-dir /absolute/backup --yes"
    if leaf == "scope delete":
        return "spec-dock scope delete <scope-id> --backup-dir /absolute/backup --yes"
    if leaf == "help":
        return "spec-dock help work start"
    if leaf == "completion":
        return "spec-dock completion zsh"
    words = ["spec-dock", *leaf.split()]
    placeholders = {
        "target": "<scope-id>",
        "github_ref": "gh:OWNER/REPO#NUMBER",
        "path": "<path>",
        "worktree_ref": "/absolute/worktree",
        "artifact_id": "<artifact-id>",
        "id": "<task-id>",
        "--until": "1d",
        "--reason": "'<reason>'",
        "--backend": "github",
        "--title": "'Example title'",
        "--parent": "<parent-id>",
        "--from": "<from-scope-id>",
        "--to": "<to-scope-id>",
        "--scope": "<scope-id>",
        "--type": "blank",
        "--base": "HEAD",
        "--to-worktree": "/absolute/worktree",
    }
    for argument in LEAF_ARGUMENTS[leaf]:
        name = argument.names[0]
        if not name.startswith("-"):
            if argument.options.get("nargs") != "?":
                words.append(placeholders.get(name, f"<{name}>"))
            elif name == "target" and leaf == "active set":
                words.append("<scope-id>")
        elif argument.options.get("required"):
            words.extend((name, placeholders.get(name, f"<{name.lstrip('-')}>")))
    if leaf.startswith(("scope create ", "scope import github ")):
        words.extend(("--assurance", "standard", "--assurance-reason", "'<reason>'"))
    if leaf in {"work start", "branch create"}:
        words.extend(("--base", "HEAD"))
    if leaf == "worktree create":
        words.extend(("--root", "/absolute/worktrees"))
    if leaf == "active clear":
        words.append("--all")
    return " ".join(words)


def _help_spec(leaf: str) -> HelpSpec:
    arguments = {name for argument in LEAF_ARGUMENTS[leaf] for name in argument.names}
    if leaf.startswith(("scope create", "scope import")):
        target = f"New {leaf.split()[-1]} Scope; parent is --parent where required."
    elif leaf.startswith("installation "):
        target = "The selected Git common-directory installation and its registered worktrees."
    elif leaf.startswith("worktree "):
        target = "The explicit absolute path in this clone's native Git inventory; create uses root/NAME."
    elif leaf in ("dashboard summary", "dashboard hide", "dashboard show"):
        target = "REPOSITORY (owner/name or github.com/owner/name), or this checkout's origin repository when omitted."
    elif leaf == "dashboard serve":
        target = "Every repository of the registry in the state root that is known and not hidden."
    elif leaf == "dashboard list":
        target = (
            "Every row of the registry in the state root, hidden ones and rows whose repository is unknown included."
        )
    elif leaf in {"help", "completion"}:
        target = "The CLI catalog; no repository is required."
    elif leaf == "todo settings":
        target = "The user settings file and, inside a checkout, this checkout's catalog todos/settings.json."
    elif leaf == "todo list":
        target = "This checkout's catalog todos/, or with --all-repositories/--repository every catalog of the registry in the state root."
    elif leaf == "todo show":
        target = "One task by ID in this checkout's catalog todos/, or by REF in that repository's registered catalog."
    elif leaf.startswith("todo "):
        target = "This checkout's catalog todos/ (one task by ID where the usage line has ID)."
    elif "target" in arguments:
        target = "The explicit Scope selector (or @current selection) in this worktree."
    elif "--scope" in arguments:
        target = (
            "The Scope or @root owner selected by --scope in this worktree."
            if leaf.startswith("artifact ")
            else "The Scope selected by --scope in this worktree."
        )
    elif leaf.startswith("active "):
        target = "This worktree's active Scope selection."
    else:
        target = "The current project or the selectors shown in the usage line."
    root = leaf.split()[0]
    reads = "CLI catalog and arguments only." if leaf in {"help", "completion"} else _READS_BY_ROOT[root]
    writes = HELP_EFFECTS[leaf] if leaf in MUTATING_LEAF_PATHS else "None; this command only reads."
    does_not = "Does not read or write project data." if leaf in {"help", "completion"} else _DOES_NOT_BY_ROOT[root]
    if leaf == "scope delete":
        does_not = "Does not close or delete GitHub Issues or Git branches; only the explicitly authorized catalog directories are removed."
    preconditions = HELP_PRECONDITIONS[leaf]
    json_data = "help text or shell script." if leaf in {"help", "completion"} else _JSON_DATA_BY_ROOT[root]
    json_version = "specdock.cli/v2"
    if leaf == "workspace sync":
        target = "The current Scope tree and main/linked worktrees in this Git clone."
        reads = "The GitHub structure snapshot, Git worktree inventory, direct records and their ancestors; --source github refetches the structure first."
        does_not = "Does not save derived state, acquire a Start lock, repair selections, or inspect Codex processes."
        json_version = "specdock.cli/v2"
        json_data = "observed_at, source, complete, worktrees, scopes, counts, findings; process_state=not_observed."
    if leaf == "scope check":
        reads = (
            "The Scope's requirement.cue, design.cue, plan.cue and explanation.html, the shipped type of its schema,"
            " the checkout's spec-dock/cue/*.cue, and the structure snapshot for its kind (stale when GitHub cannot"
            " be read; --offline sends nothing)."
        )
        does_not = "Does not write the catalog, the checkout or GitHub, and does not change selection or branches."
        json_data = (
            "kind=scope-check: scope_id, kind, path, format (cue|markdown|conflict), checked, valid, schema,"
            " assurance {level, reason, source, problem}, errors and warnings (code, message, details.file,"
            " details.hint; CUE_INVALID adds line, column, field, cue_message, positions and, when a clash with a"
            " default was folded into it, cue_related; SPEC_FINDINGS adds rule and id; warning SPEC_NO_TESTS marks a"
            " light Issue without tests), findings, cue {version}, cue_output, snapshot. Errors exit 7 with"
            " SCOPE_CHECK_FAILED."
        )
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "scope render":
        reads = (
            "The Scope's requirement.cue, design.cue and plan.cue (evaluated as scope check does), the shipped type"
            " of its schema, the checkout's spec-dock/cue/*.cue, and the structure snapshot for its kind and title."
        )
        does_not = (
            "Does not write a file, the catalog, the checkout or GitHub, and does not draw explanation.html,"
            " report.md or a Markdown Scope."
        )
        json_data = (
            "kind=scope-render: scope_id, kind, path, format (cue|conflict), complete, valid, errors (shown on the"
            " page; findings are drawn from the evaluation), design_system (file|inline), design_system_base"
            " (null when inline), vendor_base (null: CDN), html,"
            " snapshot. Text output is the HTML alone. A failed evaluation still succeeds with a page of check"
            " results and warning SCOPE_RENDER_INCOMPLETE; a Markdown Scope exits 7 with SCOPE_NOT_CUE."
        )
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf in ("scope list", "scope show"):
        reads = (
            "The GitHub structure snapshot (refreshed only when it is missing or outdated), the catalog directory,"
            " and this worktree's direct record for dynamic selectors."
        )
        does_not = "Does not write GitHub, the catalog or selection, or change Git refs."
        json_data = "items, unknown_filtered_count." if leaf == "scope list" else "scope, github_ref, changed=false."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf.startswith("installation "):
        target = (
            "Only one explicit Git worktree root: PATH for init, --target or --project/current root for other leaves."
        )
        reads = "The installed package resource inventory and selected worktree's declaration and static asset bytes; native Git inventory only for the external backup boundary."
        does_not = "Does not contact GitHub, write Git metadata, install a runtime copy, change other worktrees, acquire a Start lock, or manage shared control."
        json_data = "installation: target, package_version, created_paths, changed_paths, retired_paths, backup_path."
        confirmation = (
            "No final confirmation is required for this read-only leaf."
            if leaf == "installation show"
            else "Changes require --yes; --dry-run needs no confirmation. Update/uninstall also require a new external --backup-dir."
        )
        if leaf == "installation init":
            writes = "Only previously absent package-owned static files and a new workspace declaration; conflicts stop before changes."
        elif leaf == "installation update":
            writes = (
                "Preserve and restore-check changed static bytes, add missing package assets, replace known old files and"
                " retire known legacy files only in this worktree. A retired .claude/skills slot without a link warns"
                " CLAUDE_SKILL_LINK_MISSING with how to place it; the link is never created."
            )
        elif leaf == "installation uninstall":
            writes = "Preserve and restore-check known static bytes before removing only those files. Keep workspace declaration, ignore rules, user work, state and directories."
    elif leaf == "workspace validate":
        target = "The GitHub structure snapshot and this clone's catalog."
        reads = "Workspace declaration, the GitHub structure snapshot, the catalog's Scope directories and documents, and the direct selection only for an explicit --expect-current."
        does_not = (
            "Does not fetch Artifact bodies, write GitHub, acquire a Start lock, repair data, or write project state."
        )
        json_data = "validation: valid, findings, snapshot_source, snapshot_oid and node_count."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "workspace doctor":
        reads = "The workspace declaration, the canonical status items, the GitHub structure snapshot and this worktree's direct record; with --raw and an unreadable declaration only safe file information, retired records only with --legacy, and GitHub probes only with explicit fixed probe arguments."
        does_not = "Does not execute the retired engine, repair control, resume journals, acquire a Start lock, or write any project state."
        json_data = "findings and unverified observations; unsafe, unknown or incomplete evidence returns exit 7."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "canonical link":
        does_not = "Does not commit or push spec changes, prune worktrees, delete files or rewrite tool settings."
        target = "This clone's catalog at <main checkout>/spec-dock/.canonical and the links of the main checkout and this checkout."
        reads = "Git worktree inventory, the catalog, the links, info/exclude, spec-dock/.gitignore, tool settings files, and origin only when the catalog must be created."
        writes = "The catalog worktree and its lock, info/exclude, the fetch refspec of origin (git remote set-branches --add origin spec-dock/canonical), the local spec-dock/canonical branch (update-ref to the fetched commit), the spec-dock/initiatives links, and, unless --no-schedule, the registry, the periodic job and its first run; the baseline in the state root always. When GitHub has no canonical yet, one parentless commit with the format-1 files is pushed."
        confirmation = "No final confirmation is required; --dry-run reports the plan without writing."
    elif leaf == "canonical status":
        target = "This clone's catalog and the links of the main checkout and this checkout."
        reads = "Git worktree inventory and catalog status with --no-optional-locks, the links, ignore rules and tool settings files; GitHub's structure snapshot only with --structure, never the remote."
        does_not = "Does not write the repository, the catalog, .git or GitHub; --structure may refresh only the structure snapshot in the state root."
        json_data = "catalog, link, exclude, access, tools, sync, changes, format, git, snapshot, structure; each has status and next_step."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "canonical sync":
        target = "This clone's catalog, or with --registered every catalog in the registry of the state root."
        reads = "The registry and each catalog's state.json, the catalog work tree and changesets, origin's spec-dock/canonical, and the GitHub structure probe (conditional requests)."
        writes = "Catalog commits (save and merge, never forced), the push to origin, state.json and the sync log in the state root, and the structure snapshot."
        does_not = "Does not force-push, rebase, leave conflict markers, or save held changes (mass deletions, secrets, files over 10 MiB)."
        json_data = "catalogs[] (catalog, result, saved_commit, merged, pushed, conflicts, holds, blocking, skipped_reason, paused, error) and repositories[] (repository, probe, refreshed, dashboards_written (always 0; kept for compatibility))."
        confirmation = "No final confirmation is required; the periodic job runs this leaf."
    elif leaf == "canonical accept":
        target = "Held paths of this clone's catalog."
        reads = "The catalog files named and the held deletions in state.json."
        writes = "Only <catalog>/.runtime/accepted.json; nothing is committed."
        does_not = "Does not commit, push or change state.json; a changed file is judged again."
        json_data = "accepted paths with their blob values and accepted deletions."
        confirmation = "No final confirmation is required; the user names what to allow."
    elif leaf == "canonical restore":
        target = "Held paths of this clone's catalog."
        reads = "The holds in state.json and the catalog HEAD."
        writes = (
            "The named held files (or every held deletion) in the catalog work tree, from HEAD; nothing is committed."
        )
        does_not = "Does not touch a path that is not held, delete a file HEAD lacks, commit or push."
        json_data = "restored paths."
        confirmation = "No final confirmation is required; only held paths are restored."
    elif leaf == "canonical resume":
        target = "This clone's paused catalog."
        reads = "The pause reason in state.json and origin's spec-dock/canonical."
        writes = (
            "state.json (pause cleared, baseline set); --push-local also pushes the local canonical to recreate it."
        )
        does_not = "Does not force-push or delete local commits; local-only commits are merged by the next sync."
        json_data = "catalog, paused_before, baseline, pushed."
        confirmation = "No final confirmation is required; the option names the user's decision."
    elif leaf == "canonical remove":
        target = "This clone's catalog, the links of its checkouts and its sync registration."
        reads = "The catalog status and ignored files, Git worktree inventory, info/exclude, the registry and the periodic job."
        writes = "Removes correct links, the catalog worktree, the three info/exclude lines, the registry entry and state, and the periodic job when no other catalog is registered."
        does_not = "Does not delete the local or GitHub spec-dock/canonical branch, the structure snapshot or a real directory at a link path."
        json_data = "removed effects; without --yes the planned effects."
        confirmation = "Apply requires --yes; without it (or with --dry-run) only the plan is reported."
    elif leaf == "dashboard serve":
        reads = (
            "The registry, each shown repository's structure snapshot and catalog files, the hidden marks, the"
            " dashboard seen records, and `tailscale ip -4`/`tailscale status --json` only with --tailscale."
        )
        writes = (
            "<state root>/dashboard/server.lock (held while running), server.json (removed on stop) and"
            " seen.json when a dashboard page records what was seen."
        )
        does_not = (
            "Does not contact GitHub or the network, write the catalog, the repository or the registry, change"
            " the Tailscale configuration, or listen on 0.0.0.0."
        )
        json_data = (
            "On stop: already_running=false, stopped, urls {local, tailscale}, repositories. When a server already"
            " runs: already_running=true, urls, pid. The server's HTTP contracts are in reference_cli.md."
        )
        confirmation = "No final confirmation is required; the command runs until Ctrl-C or SIGTERM."
    elif leaf in ("dashboard hide", "dashboard show"):
        reads = "The hidden marks and the registry of the state root."
        writes = "Only <state root>/dashboard/repositories.json (specdock.dashboard-repositories/v1), atomically under a lock."
        does_not = (
            "Does not stop the periodic sync, change the registry, the catalog or the repository, or contact GitHub."
        )
        json_data = "repository, hidden, changed, registered."
        confirmation = "No final confirmation is required; show undoes hide."
    elif leaf == "dashboard service install":
        target = "This user's dashboard service: ~/Library/LaunchAgents/io.github.chemitaro.spec-dock.dashboard.plist or ${XDG_CONFIG_HOME:-~/.config}/systemd/user/spec-dock-dashboard.service."
        reads = "The platform and systemd user manager, the registry and the periodic sync job (to reuse its executable), and PATH for git and tailscale."
        writes = (
            "The job file and its launchctl bootstrap (bootout first when it changed) or systemctl --user daemon-reload,"
            " enable --now and restart when it changed; <state root>/dashboard/ for the launchd log."
        )
        does_not = "Does not change the periodic sync job, the registry, a repository or the network; nothing else installs this service."
        json_data = (
            "scheduler, path, outcome (created, updated, unchanged), port, tailscale, state_root, executable, url, log."
        )
        confirmation = (
            "No final confirmation is required; the user runs it to install the service and `uninstall` undoes it."
        )
    elif leaf == "dashboard service status":
        target = "This user's dashboard service and the server location record of its state root."
        reads = "The job file, launchctl print or systemctl --user is-active, the server location record (only whether its pid is alive) and the installed package version."
        does_not = "Does not contact the server or GitHub, or write any file."
        json_data = (
            "supported, scheduler, path, installed, loaded, detail, port, tailscale, state_root, server"
            " {pid, urls, version, started_at} or null, running, package_version, restart_pending."
        )
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "dashboard service uninstall":
        target = "This user's dashboard service."
        reads = "The job file and its recorded state root."
        writes = "launchctl bootout or systemctl --user disable --now and daemon-reload; removes the job file and <state root>/dashboard/service.log."
        does_not = "Does not change the periodic sync job, the registry, the hidden marks or the seen records."
        json_data = "scheduler, removed, path, log_removed."
        confirmation = "No final confirmation is required; `install` puts it back."
    elif leaf == "dashboard list":
        reads = "The registry, the hidden marks and the server location record (only whether its pid is alive)."
        does_not = "Does not contact GitHub or the dashboard server, or write any file."
        json_data = (
            "repositories[] (repository or null, catalog, main_checkout, hidden, served, problem, path, url),"
            " server, registry_error, marks_unreadable (true: every repository is kept hidden)."
        )
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "canonical check":
        target = "One commit of this checkout (--commit, default HEAD); the working tree and index are not read."
        reads = "The commit's tree listing, its workspace declaration, spec-dock/.gitignore, version file and static file blobs, and the installed package inventory."
        does_not = "Does not read the working tree, catalog, state directory, network or GitHub, and writes nothing."
        json_data = "commit, revision, valid, failures (code, message, details.path, details.next_step), entry_count, package_version, version_file; a version difference is a warning."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "work finish":
        reads = "The GitHub structure snapshot and the target and descendant Issues, the catalog's unsaved changes and sync state, and this worktree's captured direct record. Completion is confirmed by a live GET before clearing that record."
        does_not = "Keeps the current branch; no Start lock, automatic parent selection, child completion, commit, push, merge, or rollback. A Scope outside the active chain leaves the direct record unchanged."
        json_data = "kind=work-finish, scope_id, completed, branch_before, branch_after, selection_token; effects report completion and any captured-record clear separately."
        confirmation = "Apply requires --yes; --dry-run needs no confirmation."
    elif leaf.startswith("scope create"):
        reads = "The GitHub structure snapshot and live parent Issues, spec-dock/templates/cue/<kind>/, the rules sources and the origin repository."
        json_version = "specdock.cli/v2"
        confirmation = "TTY prompts after planning; --yes confirms creation; JSON and non-interactive require --yes."
    elif leaf.startswith("scope import github"):
        reads = "The exact GitHub Issue and its parent, the GitHub structure snapshot, spec-dock/templates/cue/<kind>/, the rules sources and the origin repository."
        json_version = "specdock.cli/v2"
        confirmation = "No final confirmation is required; import only adds the missing kind label, parent link and catalog directory."
    elif leaf in ("scope close", "scope reopen"):
        reads = "The GitHub structure snapshot and the direct record for selectors; live GitHub states for the target and required descendants or ancestors."
        does_not = (
            "Does not change direct selection or Git checkout, automatically close children, or save a lifecycle cache."
        )
        json_version = "specdock.cli/v2"
        confirmation = (
            "TTY prompts after planning; JSON and non-interactive require --yes; dry-run needs no confirmation."
        )
    elif leaf == "scope edit":
        reads = "The GitHub structure snapshot and the live Issue, and the direct record for selectors and optional expectation guards."
        does_not = "Does not modify catalog files, Issue state, direct selection or checkout, or acquire a Start lock."
        json_data = "scope, github_ref, changed; dry-run adds can_apply and blockers."
        confirmation = "No final confirmation is required for a title edit."
    elif leaf == "scope move":
        reads = (
            "The GitHub structure snapshot checked at decision freshness and the target and new parent Issues"
            " and parents read again."
        )
        writes = (
            "The GitHub parent of the Scope (sub-issue with replace_parent); this checkout's spec-dock/active"
            " links when it selects the Scope or a descendant."
        )
        does_not = (
            "Does not write the catalog, move directories, edit documents, close or reopen Issues, or change"
            " selection or branches."
        )
        json_data = (
            "scope, github_ref, changed, parent_before, parent_after, snapshot; dry-run adds can_apply and blockers."
        )
        confirmation = "No final confirmation is required for this leaf."
    elif leaf == "scope delete":
        reads = "The Scope subtree and incoming dependencies in the GitHub structure snapshot and live Issues, the catalog directories, and this worktree's captured direct selection."
        json_data = "removed_ids, changed_paths, remaining_paths, backup_path; dry-run adds can_apply and blockers."
        confirmation = (
            "TTY prompts after planning; JSON and non-interactive require --yes; dry-run needs no confirmation."
        )
    elif leaf.startswith("dependency "):
        reads = "Blocked-by and inherited edges in the GitHub structure snapshot, and the direct record for selectors; --source github refetches the structure first."
        does_not = "Does not change direct selection or Git checkout, acquire a Start lock, or persist GitHub state."
        json_version = "specdock.cli/v2"
        json_data = "scope_id, declared, effective, ready, blockers, changed; dry-run adds can_apply."
        confirmation = "No final confirmation is required for this leaf."
    elif leaf in _CONFIRMATION_LEAVES:
        confirmation = (
            "TTY prompts after planning; --yes skips only confirmation; JSON and non-interactive require --yes."
        )
    else:
        confirmation = "No final confirmation is required for this leaf."
    return HelpSpec(
        target=target,
        reads=reads,
        writes=writes,
        does_not=does_not,
        preconditions=preconditions,
        confirmation=confirmation,
        json=f"--json returns one {json_version} envelope. Data: {json_data}",
        examples=_example(leaf),
    )


HELP_SPECS: dict[str, HelpSpec] = {leaf: _help_spec(leaf) for leaf in LEAF_PATHS}
