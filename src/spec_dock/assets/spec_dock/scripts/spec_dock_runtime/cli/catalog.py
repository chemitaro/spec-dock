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
    "worktree create": (_arg("name", nargs="?"), _required("--base"), _arg("--root")),
    "worktree list": (),
    "worktree show": (_arg("worktree_ref"),),
    "worktree remove": (_arg("worktree_ref"), _flag("--unlock"), _flag("--discard-ignored")),
    "worktree bootstrap": (_arg("worktree_ref"),),
    "workbench copy": (
        _required("--scope"),
        _required("--to-worktree"),
        _arg("--on-conflict", choices=("error", "overwrite"), default="error"),
    ),
    "workspace sync": (_arg("--source", choices=SOURCES, default="cache"), _flag("--allow-invalid")),
    "workspace validate": (_flag("--require-nodes"),),
    "workspace doctor": (
        _arg("--github-repo"),
        _arg("--github-pr"),
        _arg("--github-head-sha"),
        _flag("--github-extended"),
    ),
    "workspace migrate": (_required("--to-schema"), _arg("--mapping-file")),
    "installation show": (_arg("--target"),),
    "installation init": (_arg("path"),),
    "installation update": (_arg("--target"), _arg("--version"), _arg("--commit"), _flag("--maintenance")),
    "installation uninstall": (_arg("--target"),),
    "help": (_arg("command_path", nargs="*"),),
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
