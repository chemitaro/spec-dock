from __future__ import annotations

from ..commands import (
    active as active_commands,
    close as close_commands,
    delegated_authoring as delegated_authoring_commands,
    delete as delete_commands,
    deps as deps_commands,
    doctor as doctor_commands,
    import_cmd as import_commands,
    issue as issue_commands,
    new as new_commands,
    sync as sync_commands,
    uninstall as uninstall_commands,
    update as update_commands,
    validate as validate_commands,
    worktree as worktree_commands,
)
from ..commands.contracts import CommandRegistry, CommandSpec


def build_registry() -> CommandRegistry:
    items: dict[str, CommandSpec] = {}
    items.update(new_commands.command_specs())
    items.update(import_commands.command_specs())
    items.update(active_commands.command_specs())
    items.update(delete_commands.command_specs())
    items.update(close_commands.command_specs())
    items.update(delegated_authoring_commands.command_specs())
    items.update(update_commands.command_specs())
    items.update(uninstall_commands.command_specs())
    items.update(issue_commands.command_specs())
    items.update(worktree_commands.command_specs())
    items.update(sync_commands.command_specs())
    items.update(deps_commands.command_specs())
    items.update(validate_commands.command_specs())
    items.update(doctor_commands.command_specs())
    return CommandRegistry(items=items)
