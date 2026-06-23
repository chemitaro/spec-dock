from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.application.contracts import UseCases, WorkflowNextRequest, WorkflowStatusRequest
from spec_dock_runtime.commands.contracts import CommandArgs, CommandOutcome, CommandSpec
from spec_dock_runtime.presentation.contracts import CliText
from spec_dock_runtime.presentation.workflow import (
    render_workflow_json,
    render_workflow_markdown,
    render_workflow_text,
)

if TYPE_CHECKING:
    import argparse

WorkflowStatusFormat = Literal["text", "json"]
WorkflowNextFormat = Literal["markdown", "json"]
WorkflowTarget = Literal["issue-planning", "issue-execution"]


@dataclass(frozen=True)
class WorkflowStatusArgs(CommandArgs):
    output_format: WorkflowStatusFormat


@dataclass(frozen=True)
class WorkflowNextArgs(CommandArgs):
    workflow_target: WorkflowTarget
    output_format: WorkflowNextFormat


def command_specs() -> dict[str, CommandSpec]:
    return {
        "workflow_status": CommandSpec(
            add_arguments=_add_status_arguments,
            args_factory=_status_args,
            run=_run_status,
        ),
        "workflow_next": CommandSpec(
            add_arguments=_add_next_arguments,
            args_factory=_next_args,
            run=_run_next,
        ),
    }


def _add_status_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")


def _add_next_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("workflow_target", choices=("issue-planning", "issue-execution"), help="Workflow target")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")


def _status_args(ns: argparse.Namespace) -> CommandArgs:
    output_format = getattr(ns, "format", "text")
    return WorkflowStatusArgs(output_format="json" if output_format == "json" else "text")


def _next_args(ns: argparse.Namespace) -> CommandArgs:
    output_format = getattr(ns, "format", "markdown")
    return WorkflowNextArgs(
        workflow_target=ns.workflow_target,
        output_format="json" if output_format == "json" else "markdown",
    )


def _run_status(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_status_args(args)
    result = use_cases.workflow_status(WorkflowStatusRequest())
    if typed.output_format == "json":
        text = CliText(stdout_lines=[render_workflow_json(result)], stderr_lines=[], warnings=[])
    else:
        text = render_workflow_text(result)
    return CommandOutcome(exit_code=0, text=text)


def _run_next(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_next_args(args)
    result = use_cases.workflow_next(WorkflowNextRequest(workflow_target=typed.workflow_target))
    if typed.output_format == "json":
        text = CliText(stdout_lines=[render_workflow_json(result)], stderr_lines=[], warnings=[])
    else:
        text = render_workflow_markdown(result)
    return CommandOutcome(exit_code=0, text=text)


def _expect_status_args(args: CommandArgs) -> WorkflowStatusArgs:
    if not isinstance(args, WorkflowStatusArgs):
        raise RuntimeError("Invalid command args for workflow status")
    return args


def _expect_next_args(args: CommandArgs) -> WorkflowNextArgs:
    if not isinstance(args, WorkflowNextArgs):
        raise RuntimeError("Invalid command args for workflow next")
    return args
