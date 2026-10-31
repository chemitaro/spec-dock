"""The complete vNext CLI leaf inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
    "workbench copy",
    "workspace sync",
    "workspace validate",
    "workspace doctor",
    "workspace migrate",
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
    "scope list": "Read Scope metadata; no changes.",
    "scope show": "Read one Scope and its observed status; no changes.",
    "scope check": "Check one CUE Scope's documents and explanation offline; no changes.",
    "scope render": "Draw one CUE Scope's requirement, design and plan as HTML on standard output; no changes.",
    "scope edit": "Change the selected Scope title in local metadata.",
    "scope close": "Complete or cancel one Scope in its backend; active selection stays set.",
    "scope reopen": "Reopen one Scope in its backend; active selection stays set.",
    "scope delete": "Delete local Scope-owned files; GitHub and branches remain.",
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
    "dependency add": "Add a dependency edge to local Scope metadata.",
    "dependency remove": "Remove a dependency edge from local Scope metadata.",
    "artifact create": "Publish one complete Scope-owned or @root Markdown file without overwrite or a shared counter.",
    "artifact import file": "Publish one opaque regular file in the selected Scope or @root without overwrite or a shared counter.",
    "artifact list": "Read Artifact identifiers; no changes.",
    "artifact show": "Read Artifact metadata without exposing its content; no changes.",
    "worktree create": "Create branch worktree/NAME from the fixed base and attach root/NAME using native Git; bootstrap is separate.",
    "worktree list": "Read native Git worktree inventory; no changes.",
    "worktree show": "Read one absolute path in the native Git worktree inventory; no changes.",
    "worktree remove": "Remove one explicit native Git worktree directory; keep its branch.",
    "worktree bootstrap": "Run make init once in one explicit native worktree; hook output is omitted.",
    "workbench copy": "Copy one Scope Workbench into a selected worktree.",
    "workspace sync": "Observe current Scope lifecycle and same-clone worktree selections without writing files.",
    "workspace validate": "Validate working-tree structure; --ci checks a fixed HEAD without installation or execution state. No changes.",
    "workspace doctor": "Read current workspace evidence and explicit raw/legacy diagnostics; no repair.",
    "workspace migrate": "Preserve actual local work and switch only this workspace declaration after restore verification.",
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
    "help": "Print command help; no changes.",
    "completion": "Print shell completion without changing shell configuration.",
}
if set(HELP_EFFECTS) != set(LEAF_PATHS):
    raise RuntimeError("help effects do not match the public CLI leaves")


LEAF_ARGUMENTS: dict[str, tuple[ArgumentSpec, ...]] = {
    "scope create initiative": (_required("--backend", choices=("github",)), _required("--title"), _arg("--slug")),
    "scope create epic": (
        _required("--backend", choices=("github",)),
        _required("--parent"),
        _required("--title"),
        _arg("--slug"),
    ),
    "scope create issue": (
        _required("--backend", choices=("github",)),
        _required("--parent"),
        _required("--title"),
        _arg("--slug"),
    ),
    "scope import github initiative": (_arg("github_ref"), _required("--title"), _arg("--slug"), _arg("--github-repo")),
    "scope import github epic": (
        _arg("github_ref"),
        _required("--parent"),
        _required("--title"),
        _arg("--slug"),
        _arg("--github-repo"),
    ),
    "scope import github issue": (
        _arg("github_ref"),
        _required("--parent"),
        _required("--title"),
        _arg("--slug"),
        _arg("--github-repo"),
    ),
    "scope list": (_arg("--kind", choices=KINDS), _arg("--parent"), _arg("--state", choices=STATES)),
    "scope show": (_arg("target"),),
    "scope check": (_arg("target"),),
    "scope render": (_arg("target"),),
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
    "dependency check": (_arg("target"), _arg("--source", choices=("local", "github"))),
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
    "workbench copy": (
        _required("--scope"),
        _required("--to-worktree"),
        _arg("--on-conflict", choices=("error", "overwrite"), default="error"),
    ),
    "workspace sync": (_arg("--source", choices=("local", "github")), _flag("--allow-invalid")),
    "workspace validate": (_flag("--require-nodes"), _flag("--ci")),
    "workspace doctor": (
        _flag("--raw"),
        _flag("--legacy"),
        _arg("--github-repo"),
        _arg("--github-pr"),
        _arg("--github-head-sha"),
        _flag("--github-extended"),
    ),
    "workspace migrate": (
        _required("--to-schema"),
        _required("--to-writer-protocol"),
        _arg("--backup-dir"),
        _flag("--confirm-old-writers-stopped"),
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
    "help": (_arg("help_path", nargs="*"),),
    "completion": (_arg("shell", choices=("bash", "zsh", "fish")),),
}

# Temporary compatibility for the retired internal dispatcher, never public syntax.
RECOVERY_LEAF_COMMANDS: dict[str, str] = {
    "workspace migrate": "workspace.migrate",
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
    "workbench copy",
    "workspace migrate",
    "canonical link",
    "canonical sync",
    "canonical accept",
    "canonical restore",
    "canonical resume",
    "canonical remove",
    "installation init",
    "installation update",
    "installation uninstall",
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
    "scope create initiative": "Provide a title and backend; GitHub creation needs a reachable repository. Schema 4: the flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title; --slug stops with CANONICAL_NOT_APPLICABLE.",
    "scope create epic": "Provide a title and existing Initiative parent; GitHub creation needs a reachable repository. Schema 4: the flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title; --slug stops with CANONICAL_NOT_APPLICABLE.",
    "scope create issue": "Provide a title and existing Epic parent; GitHub creation needs a reachable repository. Schema 4: the flat catalog directory spec-dock/initiatives/<bucket>/<ID>/ is created (bucket = the thousand range of the number, e.g. 00000-00999); any language title; --slug stops with CANONICAL_NOT_APPLICABLE.",
    "scope import github initiative": "The GitHub reference must resolve to an Issue not already imported. Schema 4: adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --slug stops with CANONICAL_NOT_APPLICABLE and --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ).",
    "scope import github epic": "The GitHub Issue must exist and the Initiative parent must resolve. Schema 4: adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --slug stops with CANONICAL_NOT_APPLICABLE and --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ).",
    "scope import github issue": "The GitHub Issue must exist and the Epic parent must resolve. Schema 4: adds only what is missing (kind label, parent, spec-dock/initiatives/<bucket>/<ID>/); --slug stops with CANONICAL_NOT_APPLICABLE and --title is not used (GitHub's title wins; warning CANONICAL_TITLE_IGNORED when they differ).",
    "scope list": "The selected project must contain a readable Scope tree.",
    "scope show": "The Scope ID or @current selector must resolve in this worktree.",
    "scope check": "Schema 4 only (schema 3 stops with CANONICAL_NOT_MIGRATED). The Scope must have its catalog directory. A CUE Scope (requirement.cue) needs cue v0.17.1 or later on PATH (CUE_NOT_FOUND, CUE_VERSION_UNSUPPORTED) and a type version this SpecDock ships (CUE_SCHEMA_UNSUPPORTED); a Markdown Scope succeeds with checked=false and needs no cue.",
    "scope render": "Schema 4 only (schema 3 stops with CANONICAL_NOT_MIGRATED). The Scope must have its catalog directory and be a CUE Scope (a Markdown Scope stops with SCOPE_NOT_CUE). Needs cue v0.17.1 or later on PATH and a type version this SpecDock ships, like scope check. The page loads the checkout's spec-dock/design-system/ through a file: URL (warning DESIGN_SYSTEM_MISSING when it is absent) and diagram parts from the CDN.",
    "scope edit": "The target must resolve in the current workspace and its captured metadata must remain unchanged.",
    "scope close": "The Scope must resolve; its backend and expected state guards must match.",
    "scope reopen": "The Scope must resolve; its backend and expected state guards must match.",
    "scope delete": "Require --backup-dir ABS for a new real backup; descendants require --recursive, incoming edges require --detach-dependencies, and a selected descendant requires --clear-active.",
    "scope move": "A schema-4 checkout; --parent is required and must be the right kind and open, and not the Scope or one of its descendants.",
    "active show": "The selected worktree must have readable active-selection state.",
    "active set": "Only the same valid direct target is accepted; its selection stays unchanged. Use work start to acquire a selection.",
    "active clear": "--from requires a valid current chain; --all --yes permits discarding observed corrupt regular records. Unknown entries are preserved; ancestors are never promoted.",
    "work start": "The Scope must be ready, its dependencies satisfied, and branch base resolvable. Schema 4: the default branch name is <ID> (IDs may be given without zero padding, e.g. iss-454); an in-progress mark from another PC only warns SCOPE_IN_PROGRESS (ask the user); SCOPE_KIND_CHANGED and a base commit holding spec-dock/initiatives (CANONICAL_BASE_HAS_SPECS) stop.",
    "work finish": "The explicit Scope must resolve and its completion guards must pass. A Scope outside the active chain can be completed without changing the current selection. Schema 4: unsaved specs of the Scope and its descendants are saved and pushed first, waiting up to 180 seconds; unconfirmed, the Issue stays open with CANONICAL_SAVE_UNCONFIRMED, and held changes stop with CANONICAL_SAVE_HELD.",
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
    "workbench copy": "Both worktrees and the Scope Workbench must resolve; conflicts follow --on-conflict.",
    "workspace sync": "Unknown schemas and unsafe paths are refused even with --allow-invalid; incomplete observations return exit 7.",
    "workspace validate": "Readable schema-3 metadata and regular requirement.md/design.md/plan.md/report.md files are required for each Scope; document bodies are not judged. --ci requires an existing HEAD and cannot use --expect-current or --expect-backend. Invalid or incomplete structure returns exit 7.",
    "workspace doctor": "Use a Git worktree; --raw permits unknown workspace declarations and --legacy only inspects retired files. GitHub probes require a fixed repository, PR and head SHA.",
    "workspace migrate": "Known schema 3 and valid Scope structure are required. Apply requires a new external --backup-dir under an existing physical parent, --confirm-old-writers-stopped and --yes; --dry-run writes nothing.",
    "canonical link": "A schema-4 workspace in a clone with a main checkout and Git 2.38 or later. Stops before writing when the catalog path, a link path or the spec-dock/canonical checkout is occupied, when the checkout looks mounted from another machine, or when this process cannot write where it must (including the state root and the periodic job). --no-schedule records the baseline but registers no periodic job.",
    "canonical status": "A schema-4 workspace in a clone with a main checkout; it never contacts GitHub or the remote.",
    "installation show": "The selected target must be one exact Git worktree root; no workspace or control record is required.",
    "installation init": "PATH must be a Git worktree root eligible for initial installation.",
    "installation update": "A schema-3 or schema-4 worktree-writer workspace and known static hashes are required. Changes need a new external --backup-dir under an existing physical parent and --yes; --dry-run writes nothing. Modified or unknown files require manual merge.",
    "installation uninstall": "Use a schema-3 or schema-4 worktree-writer workspace. Remove only known static hashes after a new external --backup-dir and --yes; --dry-run writes nothing. Modified files stop before changes.",
    "canonical check": "A Git checkout containing the commit (default HEAD); no catalog, network, GitHub token or particular workspace mode is required. Any problem in the commit tree returns exit 7 with each path and its next step.",
    "canonical sync": "Without --registered: a schema-4 checkout whose catalog is linked. --registered needs no project and reads the registry of --state-root (default ${XDG_STATE_HOME:-~/.local/state}/spec-dock). --loop needs --registered and --detach needs --loop.",
    "canonical accept": "A linked schema-4 checkout; name existing catalog files (relative to spec-dock/initiatives) or --deletions for the held deletions.",
    "canonical restore": "A linked schema-4 checkout; every named path must be held (changes.holds) and exist in the catalog HEAD. Without paths, every held deletion is restored.",
    "canonical resume": "A linked schema-4 checkout whose catalog is paused; --adopt-remote for remote_rewritten or merge_failed, --push-local for remote_deleted.",
    "canonical remove": "A schema-4 checkout of a clone with a main checkout; stops before writing on unsaved or unpushed changes or on ignored files other than .runtime/ in the catalog. Without --yes it only reports the plan.",
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
    "workspace migrate",
    "installation init",
    "installation update",
    "installation uninstall",
})


def requires_confirmation(leaf: str, *, backend: str | None = None, on_conflict: str | None = None) -> bool:
    return (
        leaf in _CONFIRMATION_LEAVES
        or (leaf.startswith("scope create ") and backend == "github")
        or (leaf == "workbench copy" and on_conflict == "overwrite")
    )


_READS_BY_ROOT = {
    "scope": "Current Scope metadata and hierarchy, direct selection for selectors, and live GitHub only for an explicit remote operation.",
    "active": "This worktree's active selection and the local Scope hierarchy.",
    "work": "Current Scope hierarchy, direct selection, Git branch and HEAD, dependency evidence, and required live GitHub state.",
    "branch": "Current Scope metadata, Git refs, and Git worktree branch occupancy.",
    "dependency": "Declared Scope edges, inherited prerequisites, and status observations.",
    "artifact": "The selected Scope's Artifact catalog and safe file metadata.",
    "worktree": "Native Git worktree inventory, physical clone and path identity, branch and HEAD; Scope metadata only for --expect-current.",
    "workbench": "Source and destination worktree bindings, Scope identity, and Workbench entry types.",
    "workspace": "Workspace declaration, current Scope structure, and explicitly requested local or remote observations.",
    "installation": "Installed package inventory and the selected worktree's declaration and static file snapshots.",
    "canonical": "This clone's canonical catalog and checkout links, or one commit tree, as each command states.",
}

_DOES_NOT_BY_ROOT = {
    "scope": "Does not update other Scopes, change active selection, or implicitly switch branches.",
    "active": "Does not change lifecycle, dependencies, Git branch, or GitHub state.",
    "work": "Does not commit, push, merge, delete branches, or automatically roll back completed effects.",
    "branch": "Does not change Scope lifecycle or active selection.",
    "dependency": "Does not close a prerequisite or change GitHub issue state.",
    "artifact": "Does not print Artifact contents, source file hash, or external source path.",
    "worktree": "Does not mutate an independent repository or implicitly run project bootstrap.",
    "workbench": "Does not copy the root Workbench or start automatic synchronization.",
    "workspace": "Does not silently repair primary Scope data or active selection.",
    "installation": "Does not change other worktrees, Scope data, Artifacts, Workbenches, direct selections or Git metadata.",
    "canonical": "Does not change GitHub Issues or the default branch.",
}

_JSON_DATA_BY_ROOT = {
    "scope": "Scope identity, backend, status, revision, and snapshot or list filters.",
    "active": "Direct selection status/token, derived ancestors, selected/current branch, and branch_changed.",
    "work": "Direct Scope ID, started or completed result, before/after branch, selection token, and effect outcomes.",
    "branch": "Scope ID, candidate ref name, observed tip, created/switched, and binding_persisted=false.",
    "dependency": "Declared/effective edges, readiness, blockers, and status provenance.",
    "artifact": "artifact:{id,scope_id,path,type},changed; list returns scope_id,items. Bodies and external source paths remain private.",
    "worktree": "path, branch, head, changed, observed; list returns items with path, branch, head, bare, locked, prunable.",
    "workbench": "Source/destination worktree IDs, Scope, conflict policy, and mutation state.",
    "workspace": "Current observations, validity, findings, declaration changes, or verified preservation results.",
    "installation": "target, package_version, created_paths, changed_paths, retired_paths, backup_path and preservation checks.",
    "canonical": "The command's catalog, link, sync or check observations.",
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
        "--backend": "github",
        "--title": "'Example title'",
        "--parent": "<parent-id>",
        "--from": "<from-scope-id>",
        "--to": "<to-scope-id>",
        "--scope": "<scope-id>",
        "--type": "blank",
        "--base": "HEAD",
        "--to-worktree": "/absolute/worktree",
        "--to-schema": "3",
        "--to-writer-protocol": "specdock.worktree-writer/v1",
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
    if leaf in {"work start", "branch create"}:
        words.extend(("--base", "HEAD"))
    if leaf == "worktree create":
        words.extend(("--root", "/absolute/worktrees"))
    if leaf == "workspace migrate":
        words.extend(("--backup-dir", "/absolute/backup", "--confirm-old-writers-stopped", "--yes"))
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
    elif leaf in {"help", "completion"}:
        target = "The CLI catalog; no repository is required."
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
        does_not = (
            "Does not delete GitHub Issues or Git branches; only the explicitly authorized local subtree is removed."
        )
    elif leaf == "workspace migrate":
        does_not = "Does not rewrite Scope data, import legacy active, alter other worktrees or Git metadata, acquire a Start lock, or replay old records."
    preconditions = HELP_PRECONDITIONS[leaf]
    json_data = "help text or shell script." if leaf in {"help", "completion"} else _JSON_DATA_BY_ROOT[root]
    json_version = "specdock.cli/v2"
    if leaf == "workspace sync":
        target = "The current Scope tree and main/linked worktrees in this Git clone."
        reads = "Current metadata, Git worktree inventory, direct records and their ancestors; live GitHub only with --source github."
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
            " details.hint; CUE_INVALID adds line, column, field, cue_message, positions; SPEC_FINDINGS adds rule"
            " and id), findings, cue {version}, cue_output, snapshot. Errors exit 7 with SCOPE_CHECK_FAILED."
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
            " page; findings are drawn from the evaluation), design_system_base, vendor_base (null: CDN), html,"
            " snapshot. Text output is the HTML alone. A failed evaluation still succeeds with a page of check"
            " results and warning SCOPE_RENDER_INCOMPLETE; a Markdown Scope exits 7 with SCOPE_NOT_CUE."
        )
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf in ("scope list", "scope show"):
        reads = "Current metadata and this worktree's direct record for dynamic selectors; unobserved GitHub lifecycle is unknown."
        does_not = (
            "Does not contact GitHub, read a retired status cache, modify metadata or selection, or change Git refs."
        )
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
            writes = "Preserve and restore-check changed static bytes, add missing package assets, replace known old files and retire known legacy files only in this worktree."
        elif leaf == "installation uninstall":
            writes = "Preserve and restore-check known static bytes before removing only those files. Keep workspace declaration, ignore rules, user work, state and directories."
    elif leaf == "workspace validate":
        target = "The current working-tree structure, or one fixed HEAD with --ci."
        reads = "Workspace declaration, Scope metadata, dependencies and Artifact entry names/types; live direct selection only for an explicit --expect-current outside --ci."
        does_not = "Does not fetch Artifact bodies, contact GitHub, require installation control, acquire a Start lock, repair data, or write project state."
        json_data = "validation: valid, findings, snapshot_source, snapshot_oid and node_count."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "workspace doctor":
        reads = "Current workspace metadata and this worktree's direct record; safe file information in --raw mode, retired records only with --legacy, and GitHub only with explicit fixed probe arguments."
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
        json_data = "catalog, link, exclude, access, tools, sync, changes, format, git, snapshot, dashboard, structure; each has status and next_step."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "workspace migrate":
        target = "Only this worktree's spec-dock/workspace.json declaration."
        reads = "Current Scope structure, Git worktree inventory, retired record headers, and actual checkout/common-Git data for the external backup."
        json_data = "target, before_protocol, after_protocol, changed_paths, backup_path, backup_verified and restore_verified; legacy active is preserved without import."
        confirmation = "Apply requires --yes and --confirm-old-writers-stopped; the latter is a human operational confirmation, not a monitored guarantee. --dry-run needs neither."
    elif leaf == "canonical sync":
        target = "This clone's catalog, or with --registered every catalog in the registry of the state root."
        reads = "The registry and each catalog's state.json, the catalog work tree and changesets, origin's spec-dock/canonical, and the GitHub structure probe (conditional requests)."
        writes = "Catalog commits (save and merge, never forced), the push to origin, state.json and the sync log in the state root, the structure snapshot, and the five dashboard files of each main checkout when the structure changed or a file is missing."
        does_not = "Does not force-push, rebase, leave conflict markers, or save held changes (mass deletions, secrets, files over 10 MiB)."
        json_data = "catalogs[] (catalog, result, saved_commit, merged, pushed, conflicts, holds, blocking, skipped_reason, paused, error) and repositories[] (repository, probe, refreshed, dashboards_written)."
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
        writes = "Removes correct links, the catalog worktree, the dashboard files of the main checkout, the three info/exclude lines, the registry entry and state, and the periodic job when no other catalog is registered."
        does_not = "Does not delete the local or GitHub spec-dock/canonical branch, the structure snapshot or a real directory at a link path."
        json_data = "removed effects; without --yes the planned effects."
        confirmation = "Apply requires --yes; without it (or with --dry-run) only the plan is reported."
    elif leaf == "canonical check":
        target = "One commit of this checkout (--commit, default HEAD); the working tree and index are not read."
        reads = "The commit's tree listing, its workspace declaration, spec-dock/.gitignore, version file and static file blobs, and the installed package inventory."
        does_not = "Does not read the working tree, catalog, state directory, network or GitHub, and writes nothing."
        json_data = "commit, revision, valid, failures (code, message, details.path, details.next_step), entry_count, package_version, version_file; a version difference is a warning."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf == "work finish":
        reads = "Current metadata, required target and descendant lifecycle, and this worktree's captured direct record. GitHub-backed completion is confirmed completed by a live GET before clearing that record."
        does_not = "Keeps the current branch; no Start lock, automatic parent selection, child completion, commit, push, merge, or rollback. A Scope outside the active chain leaves the direct record unchanged."
        json_data = "kind=work-finish, scope_id, completed, branch_before, branch_after, selection_token; effects report completion and any captured-record clear separately."
        confirmation = "Apply requires --yes; --dry-run needs no confirmation."
    elif leaf.startswith("scope create"):
        reads = "Current metadata, templates, origin publication repository, and live GitHub ancestor state."
        json_version = "specdock.cli/v2"
        confirmation = "TTY prompts after planning; --yes confirms creation; JSON and non-interactive require --yes."
    elif leaf.startswith("scope import github"):
        reads = "Current metadata, templates, origin publication repository, the exact GitHub Issue and live ancestor state."
        json_version = "specdock.cli/v2"
        confirmation = "No final confirmation is required; import makes no remote mutation."
    elif leaf in ("scope close", "scope reopen"):
        reads = "Current metadata and the direct record for selectors; live GitHub states for the target and required descendants or ancestors."
        does_not = (
            "Does not change direct selection or Git checkout, automatically close children, or save a lifecycle cache."
        )
        json_version = "specdock.cli/v2"
        confirmation = (
            "TTY prompts after planning; JSON and non-interactive require --yes; dry-run needs no confirmation."
        )
    elif leaf == "scope edit":
        reads = "Current local metadata and the direct record for selectors and optional expectation guards."
        does_not = "Does not modify documents, GitHub state, direct selection or checkout, or acquire a Start lock."
        json_data = "scope, github_ref, changed; dry-run adds can_apply and blockers."
        confirmation = "No final confirmation is required for a local title edit."
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
        reads = "Current Scope subtree, incoming dependency metadata, and this worktree's captured direct selection."
        json_data = "removed_ids, changed_paths, remaining_paths, backup_path; dry-run adds can_apply and blockers."
        confirmation = (
            "TTY prompts after planning; JSON and non-interactive require --yes; dry-run needs no confirmation."
        )
    elif leaf.startswith("dependency "):
        reads = "Current metadata, inherited dependency edges, and the direct record for selectors; live GitHub only with --source github."
        does_not = "Does not change direct selection or Git checkout, acquire a Start lock, or persist GitHub state."
        json_version = "specdock.cli/v2"
        json_data = "scope_id, declared, effective, ready, blockers, changed; dry-run adds can_apply."
        confirmation = "No final confirmation is required for this leaf."
    elif leaf == "workbench copy":
        target = "One Scope Workbench in this worktree and the same Scope in another worktree of the same Git clone."
        reads = "Native Git worktree inventory, current Scope metadata, the direct record for dynamic selectors, and source/destination bytes and identities."
        does_not = "Does not remove destination-only files, acquire a Start lock, change selection, or automatically restore overwritten files."
        json_data = "scope_id, source_path, destination_path, copied_paths, remaining_paths; copied/remaining paths are relative to the Workbench root."
        confirmation = (
            "Overwrite prompts after planning; JSON and non-interactive require --yes; dry-run needs no confirmation."
        )
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
