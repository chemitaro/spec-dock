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
    "artifact create": "Create one Scope-owned Markdown Artifact.",
    "artifact import file": "Copy one regular file into a Scope-owned Artifact.",
    "artifact list": "Read Artifact identifiers; no changes.",
    "artifact show": "Read Artifact metadata without exposing its content; no changes.",
    "worktree create": "Create and register one Git worktree; bootstrap is separate.",
    "worktree list": "Read registered Git worktrees; no changes.",
    "worktree show": "Read one worktree and its removal blockers; no changes.",
    "worktree remove": "Remove one worktree directory and registration; keep its branch.",
    "worktree bootstrap": "Run the selected worktree's project-owned make init.",
    "workbench copy": "Copy one Scope Workbench into a selected worktree.",
    "workspace sync": "Observe current Scope lifecycle and same-clone worktree selections without writing files.",
    "workspace validate": "Read and validate the workspace; --ci checks committed data without installation state. No changes.",
    "workspace doctor": "Read installation and journal diagnostics; no repair.",
    "workspace migrate": "Migrate registered worktrees and control under maintenance.",
    "installation show": "Read installed engine and worktree inventory; no changes.",
    "installation init": "Install managed tooling and initial control in a Git repository.",
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
    "scope delete": (_arg("target"), _flag("--recursive"), _flag("--clear-active"), _flag("--detach-dependencies")),
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
    "worktree create": (_arg("name", nargs="?"), _required("--base"), _arg("--root"), _arg("--recover")),
    "worktree list": (),
    "worktree show": (_arg("worktree_ref"),),
    "worktree remove": (_arg("worktree_ref"), _flag("--unlock"), _flag("--discard-ignored")),
    "worktree bootstrap": (_arg("worktree_ref"), _flag("--recover")),
    "workbench copy": (
        _required("--scope"),
        _required("--to-worktree"),
        _arg("--on-conflict", choices=("error", "overwrite"), default="error"),
    ),
    "workspace sync": (_arg("--source", choices=("local", "github"), default="local"), _flag("--allow-invalid")),
    "workspace validate": (_flag("--require-nodes"), _flag("--ci")),
    "workspace doctor": (
        _arg("--github-repo"),
        _arg("--github-pr"),
        _arg("--github-head-sha"),
        _flag("--github-extended"),
    ),
    "workspace migrate": (_required("--to-schema"), _arg("--mapping-file")),
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
    "scope delete": "scope.delete",
    "workspace migrate": "workspace.migrate",
    "installation init": "installation.init",
    "installation update": "installation.update",
    "installation uninstall": "installation.uninstall",
}
for _leaf, _command in RECOVERY_LEAF_COMMANDS.items():
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
    "scope edit": "The Scope must resolve and its backend and revision guards must match.",
    "scope close": "The Scope must resolve; its backend and expected state guards must match.",
    "scope reopen": "The Scope must resolve; its backend and expected state guards must match.",
    "scope delete": "Select the exact local Scope subtree and satisfy deletion safety guards.",
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
    "artifact create": "The owner Scope must resolve and the Artifact type must be supported.",
    "artifact import file": "The owner Scope and regular source file must exist.",
    "artifact list": "The owner Scope must resolve and its catalog must be readable.",
    "artifact show": "The owner Scope and Artifact ID must resolve.",
    "worktree create": "The path must be available and the requested Git base must resolve.",
    "worktree list": "The installation control must be readable.",
    "worktree show": "The worktree ID or path must resolve in installation control.",
    "worktree remove": "The target must be registered and pass active, branch, and path safety guards.",
    "worktree bootstrap": "The target must be registered and have a project-owned make init target.",
    "workbench copy": "Both worktrees and the Scope Workbench must resolve; conflicts follow --on-conflict.",
    "workspace sync": "Unknown schemas and unsafe paths are refused even with --allow-invalid; incomplete observations return exit 7.",
    "workspace validate": "A readable workspace is required; --ci validates committed data without installation state.",
    "workspace doctor": "The selected repository and its control records must be readable.",
    "workspace migrate": "Inspection with --dry-run can inventory without --mapping-file. Applying a migration requires an inventory-bound --mapping-file, maintenance state, and valid migration guards.",
    "installation show": "The selected repository must have readable installation control.",
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
    "worktree": "Git worktree registration, target path, branch, HEAD, and control state.",
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
    "artifact": "Artifact ID, owning Scope, relative path, creation type, and observed authority.",
    "worktree": "Worktree ID, path, HEAD, branch, registration, blockers, and operation outcome.",
    "workbench": "Source/destination worktree IDs, Scope, conflict policy, and mutation state.",
    "workspace": "Snapshot, generation, validity, findings, status source, and pending recovery.",
    "installation": "Inventory, schema/protocol, engine digest, phase, backups, and journal IDs.",
}


def _example(leaf: str) -> str:
    if leaf == "help":
        return "spec-dock help work start"
    if leaf == "completion":
        return "spec-dock completion zsh"
    words = ["spec-dock", *leaf.split()]
    placeholders = {
        "target": "<scope-id>",
        "github_ref": "gh:OWNER/REPO#NUMBER",
        "path": "<path>",
        "worktree_ref": "<worktree-id>",
        "artifact_id": "<artifact-id>",
        "--backend": "github",
        "--title": "'Example title'",
        "--parent": "<parent-id>",
        "--from": "<from-scope-id>",
        "--to": "<to-scope-id>",
        "--scope": "<scope-id>",
        "--type": "blank",
        "--base": "HEAD",
        "--to-worktree": "<worktree-id>",
        "--to-schema": "3",
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
    if leaf == "workspace migrate":
        words.extend(("--mapping-file", "<mapping.json>"))
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
        target = "The selected registered worktree; create allocates a new worktree."
    elif leaf in {"help", "completion"}:
        target = "The CLI catalog; no repository is required."
    elif "target" in arguments:
        target = "The explicit Scope selector (or @current selection) in this worktree."
    elif "--scope" in arguments:
        target = "The Scope selected by --scope in this worktree."
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
        does_not = "Does not migrate independent repositories outside the selected Git common directory."
    preconditions = HELP_PRECONDITIONS[leaf]
    json_data = "help text or shell script." if leaf in {"help", "completion"} else _JSON_DATA_BY_ROOT[root]
    json_version = "specdock.cli/v1"
    if leaf == "workspace sync":
        target = "The current Scope tree and main/linked worktrees in this Git clone."
        reads = "Current metadata, Git worktree inventory, direct records and their ancestors; live GitHub only with --source github."
        does_not = "Does not save derived state, acquire a Start lock, repair selections, or inspect Codex processes."
        json_version = "specdock.cli/v2"
        json_data = "observed_at, source, complete, worktrees, scopes, counts, findings; process_state=not_observed."
    if leaf.startswith("scope create"):
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
    elif leaf.startswith("dependency "):
        reads = "Current metadata, inherited dependency edges, and the direct record for selectors; live GitHub only with --source github."
        does_not = "Does not change direct selection or Git checkout, acquire a Start lock, or persist GitHub state."
        json_version = "specdock.cli/v2"
        json_data = "scope_id, declared, effective, ready, blockers, changed; dry-run adds can_apply."
        confirmation = "No final confirmation is required for this leaf."
    elif leaf == "workbench copy":
        confirmation = "--on-conflict overwrite requires confirmation; the default error policy does not."
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
