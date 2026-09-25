"""The complete vNext CLI leaf inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spec_dock_runtime.domain.operation import BLOCKING_COMMANDS, ROLLBACK_COMMANDS


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
    "scope create initiative": "Create Initiative files; GitHub backend also creates an Issue.",
    "scope create epic": "Create Epic files; GitHub backend also creates an Issue.",
    "scope create issue": "Create Issue files; GitHub backend also creates an Issue.",
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
    "active set": "Select a Scope and its ancestors; no branch or lifecycle change.",
    "active clear": "Clear the selected subtree or all active selection.",
    "work start": "Create or reuse a branch, checkout it, and select the ready Scope.",
    "work finish": "Complete the Scope and clear its selected subtree; Git delivery is separate.",
    "branch show": "Read the canonical Scope branch binding; no changes.",
    "branch create": "Create and bind a canonical Git branch without checkout.",
    "branch switch": "Checkout the bound Git branch; active selection stays set.",
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
    "workspace sync": "Publish a derived generation; do not alter primary Scope or active state.",
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
    "scope create initiative": (_required("--backend", choices=BACKENDS), _required("--title"), _arg("--slug")),
    "scope create epic": (
        _required("--backend", choices=BACKENDS),
        _required("--parent"),
        _required("--title"),
        _arg("--slug"),
    ),
    "scope create issue": (
        _required("--backend", choices=BACKENDS),
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
    "active set": (_arg("target", nargs="?"), _flag("--from-branch")),
    "active clear": (_arg("--from", dest="from_target"), _flag("--all")),
    "work start": (
        _arg("target"),
        _arg("--branch"),
        _arg("--base"),
        _flag("--switch-active"),
        _arg("--source", choices=SOURCES, default="github"),
        _flag("--allow-stale"),
    ),
    "work finish": (_arg("target"),),
    "branch show": (_arg("target"),),
    "branch create": (_arg("target"), _arg("--name"), _arg("--base")),
    "branch switch": (_arg("target"),),
    "dependency list": (_arg("target"), _arg("--view", choices=("declared", "effective"))),
    "dependency check": (_arg("target"), _arg("--source", choices=SOURCES, default="cache")),
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
    "workspace sync": (_arg("--source", choices=SOURCES, default="cache"), _flag("--allow-invalid")),
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
    **{f"scope create {kind}": "scope.create" for kind in KINDS},
    **{f"scope import github {kind}": "scope.import" for kind in KINDS},
    "scope close": "scope.close",
    "scope reopen": "scope.reopen",
    "scope delete": "scope.delete",
    "work start": "work.start",
    "work finish": "work.finish",
    "branch create": "branch.create",
    "workspace migrate": "workspace.migrate",
    "installation init": "installation.init",
    "installation update": "installation.update",
    "installation uninstall": "installation.uninstall",
}
if set(RECOVERY_LEAF_COMMANDS.values()) != BLOCKING_COMMANDS:
    raise RuntimeError("recovery CLI leaves do not match the D-16 command allowlist")
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
    "workspace sync",
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
    "branch": "Canonical branch registry, Git refs, and worktree branch ownership.",
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
    "active": "Focus, ancestor chain, source, revision, and before/after selection on changes.",
    "work": "Target, before/after state, selection, branch, readiness guards, and derived state.",
    "branch": "Canonical name, base commit, ownership, and registry revision.",
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
        "--backend": "local",
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
    if leaf in {"work start", "branch create", "worktree create"}:
        words.extend(("--base", "HEAD"))
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
    required = [arg.names[0] for arg in LEAF_ARGUMENTS[leaf] if arg.options.get("required")]
    preconditions = (
        "No project is required."
        if leaf in {"help", "completion"}
        else f"Resolve the target in the selected project; required inputs: {', '.join(required) or 'positional target/state guards'}."
    )
    if leaf.startswith("scope create"):
        confirmation = "GitHub creation requires confirmation; local creation does not."
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
        json=(
            "--json returns one specdock.cli/v1 envelope. Data: "
            + ("help text or shell script." if leaf in {"help", "completion"} else _JSON_DATA_BY_ROOT[root])
        ),
        examples=_example(leaf),
    )


HELP_SPECS: dict[str, HelpSpec] = {leaf: _help_spec(leaf) for leaf in LEAF_PATHS}
