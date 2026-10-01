"""The complete vNext CLI leaf inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Syntax-only compatibility data for the internal pre-cutover dispatcher.
# The public utility path must not load the journal/domain implementation.
ROLLBACK_COMMANDS = frozenset({
    "scope.delete",
    "workspace.migrate",
    "installation.init",
    "installation.update",
    "installation.uninstall",
})


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
BACKENDS = ("github", "local")
STATES = ("open", "completed", "not-planned", "unknown")
SOURCES = ("github", "cache")
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
    "scope edit",
    "scope close",
    "scope reopen",
    "scope delete",
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
    "installation show",
    "installation init",
    "installation update",
    "installation uninstall",
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
    "scope edit": "Change the selected Scope title in local metadata.",
    "scope close": "Complete or cancel one Scope in its backend; active selection stays set.",
    "scope reopen": "Reopen one Scope in its backend; active selection stays set.",
    "scope delete": "Delete local Scope-owned files; GitHub and branches remain.",
    "active show": "Read this worktree's active selection; no changes.",
    "active set": "Return unchanged for the same valid direct selection; acquiring another selection requires work start.",
    "active clear": "Remove only observed local direct records; never promote an ancestor.",
    "work start": "Create or reuse a branch, checkout it, and select the ready Scope.",
    "work finish": "Complete the Scope and clear its selected subtree; Git delivery is separate.",
    "branch show": "Observe the explicit or default candidate Git ref; no binding is persisted.",
    "branch create": "Create only a new Git branch at a fixed base; no checkout or binding record.",
    "branch switch": "Checkout an existing Git branch; the direct selection record stays unchanged.",
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
    "installation show": "Read the package version and static resources in one Git worktree; no changes.",
    "installation init": "Place package static resources and a new workspace declaration in one Git worktree.",
    "installation update": "Replace managed tooling from one pinned source; --finalize verifies all targets and leaves maintenance.",
    "installation uninstall": "Remove managed tooling while preserving Scope data.",
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
    "dependency check": (_arg("target"), _arg("--source", choices=("local", "github"), default="local")),
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
    "workspace sync": (_arg("--source", choices=("local", "github"), default="local"), _flag("--allow-invalid")),
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
    "installation show": (_arg("--target"),),
    "installation init": (_arg("path"),),
    "installation update": (
        _arg("--target"),
        _arg("--version"),
        _arg("--commit"),
        _flag("--maintenance"),
        _flag("--finalize"),
        _flag("--activate-engine"),
        _arg("--from-update"),
    ),
    "installation uninstall": (_arg("--target"),),
    "help": (_arg("help_path", nargs="*"),),
    "completion": (_arg("shell", choices=("bash", "zsh", "fish")),),
}

RECOVERY_LEAF_COMMANDS: dict[str, str] = {
    "workspace migrate": "workspace.migrate",
    "installation init": "installation.init",
    "installation update": "installation.update",
    "installation uninstall": "installation.uninstall",
}
for _leaf, _command in RECOVERY_LEAF_COMMANDS.items():
    if _leaf == "installation init":
        continue
    LEAF_ARGUMENTS[_leaf] += (_arg("--resume"),)
    if _command in ROLLBACK_COMMANDS:
        LEAF_ARGUMENTS[_leaf] += (_arg("--rollback"),)


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
    "scope create initiative": "Provide a title and backend; GitHub creation needs a reachable repository.",
    "scope create epic": "Provide a title and existing Initiative parent; GitHub creation needs a reachable repository.",
    "scope create issue": "Provide a title and existing Epic parent; GitHub creation needs a reachable repository.",
    "scope import github initiative": "The GitHub reference must resolve to an Issue not already imported.",
    "scope import github epic": "The GitHub Issue must exist and the Initiative parent must resolve.",
    "scope import github issue": "The GitHub Issue must exist and the Epic parent must resolve.",
    "scope list": "The selected project must contain a readable Scope tree.",
    "scope show": "The Scope ID or @current selector must resolve in this worktree.",
    "scope edit": "The target must resolve in the current workspace and its captured metadata must remain unchanged.",
    "scope close": "The Scope must resolve; its backend and expected state guards must match.",
    "scope reopen": "The Scope must resolve; its backend and expected state guards must match.",
    "scope delete": "Require --backup-dir ABS for a new real backup; descendants require --recursive, incoming edges require --detach-dependencies, and a selected descendant requires --clear-active.",
    "active show": "The selected worktree must have readable active-selection state.",
    "active set": "Only the same valid direct target is unchanged; use work start to acquire a selection.",
    "active clear": "--from requires a valid current chain; --all --yes permits discarding observed corrupt regular records. Unknown entries are preserved; ancestors are never promoted.",
    "work start": "The Scope must be ready, its dependencies satisfied, and branch base resolvable.",
    "work finish": "The explicit Scope must resolve and its completion guards must pass. A Scope outside the active chain can be completed without changing the current selection.",
    "branch show": "The Scope must resolve; the candidate Git ref may be absent.",
    "branch create": "The Scope must resolve, Git base must exist, and branch ownership must be free.",
    "branch switch": "The existing branch must contain the target and ancestors; the worktree must be clean.",
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
    "workspace validate": "Readable schema-3 metadata is required; --ci requires an existing HEAD and cannot use --expect-current or --expect-backend. Invalid or incomplete structure returns exit 7.",
    "workspace doctor": "Use a Git worktree; --raw permits unknown workspace declarations and --legacy only inspects retired files. GitHub probes require a fixed repository, PR and head SHA.",
    "workspace migrate": "Known schema 3 and valid Scope structure are required. Apply requires a new external --backup-dir under an existing physical parent, --confirm-old-writers-stopped and --yes; --dry-run writes nothing.",
    "installation show": "The selected target must be one exact Git worktree root; no workspace or control record is required.",
    "installation init": "PATH must be a Git worktree root eligible for initial installation.",
    "installation update": "Ordinary apply needs one pinned --version or --commit. --finalize verifies the maintained group without a new source. --activate-engine needs the recorded --from-update. --resume and --rollback require their fixed operation ID and mode-specific guards.",
    "installation uninstall": "The installed worktree group must satisfy uninstall safety guards.",
    "help": "No project is required.",
    "completion": "No project is required; choose bash, zsh, or fish.",
}
if set(HELP_PRECONDITIONS) != set(LEAF_PATHS):
    raise RuntimeError("help preconditions do not match the public CLI leaves")


_CONFIRMATION_LEAVES = frozenset({
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
    "scope": "Scope metadata, hierarchy, cached state, and active selection; GitHub only for the named remote operation.",
    "active": "This worktree's active selection and the local Scope hierarchy.",
    "work": "Scope hierarchy and descendants, active selection, canonical branch, Git HEAD, and dependency status.",
    "branch": "Current Scope metadata, Git refs, and Git worktree branch occupancy.",
    "dependency": "Declared Scope edges, inherited prerequisites, and status observations.",
    "artifact": "The selected Scope's Artifact catalog and safe file metadata.",
    "worktree": "Native Git worktree inventory, physical clone and path identity, branch and HEAD; Scope metadata only for --expect-current.",
    "workbench": "Source and destination worktree bindings, Scope identity, and Workbench entry types.",
    "workspace": "Workspace schema, Scope data, derived generation, control, and pending records.",
    "installation": "Pinned engine, control record, managed asset inventory, and the selected Git worktree group.",
}

_DOES_NOT_BY_ROOT = {
    "scope": "Does not update other Scopes, change active selection, or implicitly switch branches.",
    "active": "Does not change lifecycle, dependencies, Git branch, or GitHub state.",
    "work": "Does not commit, push, merge, or delete the canonical branch.",
    "branch": "Does not change Scope lifecycle or active selection.",
    "dependency": "Does not close a prerequisite or change GitHub issue state.",
    "artifact": "Does not print Artifact contents, source file hash, or external source path.",
    "worktree": "Does not mutate an independent repository or implicitly run project bootstrap.",
    "workbench": "Does not copy the root Workbench or start automatic synchronization.",
    "workspace": "Does not silently repair primary Scope data or active selection.",
    "installation": "Does not update any independent repository outside the selected Git common directory.",
}

_JSON_DATA_BY_ROOT = {
    "scope": "Scope identity, backend, status, revision, and snapshot or list filters.",
    "active": "Direct selection status/token, derived ancestors, selected/current branch, and branch_changed.",
    "work": "Target, before/after state, selection, branch, readiness guards, and derived state.",
    "branch": "Scope ID, candidate ref name, observed tip, created/switched, and binding_persisted=false.",
    "dependency": "Declared/effective edges, readiness, blockers, and status provenance.",
    "artifact": "artifact:{id,scope_id,path,type},changed; list returns scope_id,items. Bodies and external source paths remain private.",
    "worktree": "path, branch, head, changed, observed; list returns items with path, branch, head, bare, locked, prunable.",
    "workbench": "Source/destination worktree IDs, Scope, conflict policy, and mutation state.",
    "workspace": "Snapshot, generation, validity, findings, status source, and pending recovery.",
    "installation": "Inventory, schema/protocol, engine digest, phase, backups, and journal IDs.",
}


def _example(leaf: str) -> str:
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
    if leaf == "installation update":
        words.extend(("--commit", "<fixed-commit-sha>"))
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
    if leaf in ("scope list", "scope show"):
        reads = "Current metadata and this worktree's direct record for dynamic selectors; unobserved GitHub lifecycle is unknown."
        does_not = (
            "Does not contact GitHub, read a retired status cache, modify metadata or selection, or change Git refs."
        )
        json_data = "items, unknown_filtered_count." if leaf == "scope list" else "scope, github_ref, changed=false."
        confirmation = "No final confirmation is required for this read-only leaf."
    elif leaf in ("installation init", "installation show"):
        target = "Only one explicit Git worktree root: PATH for init, --target or --project/current root for show."
        reads = "The installed package resource inventory and selected worktree's declaration and static asset bytes."
        does_not = "Does not contact GitHub, write Git metadata, install a runtime copy, inspect other worktrees, acquire a Start lock, or manage shared control."
        json_data = "installation: target, package_version, created_paths, changed_paths, retired_paths, backup_path."
        confirmation = (
            "Apply requires --yes; --dry-run needs no confirmation."
            if leaf == "installation init"
            else "No final confirmation is required for this read-only leaf."
        )
        if leaf == "installation init":
            writes = "Only previously absent package-owned static files and a new workspace declaration; conflicts stop before changes."
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
    elif leaf == "workspace migrate":
        target = "Only this worktree's spec-dock/workspace.json declaration."
        reads = "Current Scope structure, Git worktree inventory, retired record headers, and actual checkout/common-Git data for the external backup."
        json_data = "target, before_protocol, after_protocol, changed_paths, backup_path, backup_verified and restore_verified; legacy active is preserved without import."
        confirmation = "Apply requires --yes and --confirm-old-writers-stopped; the latter is a human operational confirmation, not a monitored guarantee. --dry-run needs neither."
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
