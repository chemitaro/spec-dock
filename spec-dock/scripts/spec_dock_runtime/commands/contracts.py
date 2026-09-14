from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable

    from spec_dock_runtime.application.contracts import UseCases
    from spec_dock_runtime.presentation.contracts import CliText


@dataclass(frozen=True)
class InstallerExecRequest:
    kind: Literal["installer-exec"]
    argv: tuple[str, ...]
    environment_policy: Literal["inherit-without-lock-bypass"]


@dataclass(frozen=True)
class ConsumerHookRequest:
    kind: Literal["consumer-hook"]
    bound_cwd_fd: int
    bound_device: int
    bound_inode: int
    detection_argv: tuple[str, ...]
    execution_argv: tuple[str, ...]
    result_format: Literal["worktree-create-text-v1", "worktree-create-json-v1"]
    result_payload: dict[str, object]


TerminalRequest = InstallerExecRequest | ConsumerHookRequest


@dataclass(frozen=True)
class CommandArgs:
    """Marker base type for command-specific typed args."""


@dataclass(frozen=True)
class CommandOutcome:
    exit_code: int
    text: CliText
    terminal: TerminalRequest | None = None


RuntimeProgramOutcome = CommandOutcome


@dataclass(frozen=True)
class CommandSpec:
    add_arguments: Callable[[argparse.ArgumentParser], None]
    args_factory: Callable[[argparse.Namespace], CommandArgs]
    run: Callable[[CommandArgs, UseCases], CommandOutcome]


@dataclass(frozen=True)
class CommandRegistry:
    items: dict[str, CommandSpec]
