from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.cli import parser as cli_parser, registry as cli_registry
        from spec_dock_runtime.commands import artifact_import as artifact_import_commands
    finally:
        sys.path.pop(0)
    return cli_parser, cli_registry, artifact_import_commands


def test_artifact_import_chatgpt_output_help_and_minimal_parser_contract(capsys) -> None:
    cli_parser, cli_registry, artifact_import_commands = _runtime_modules()
    parser = cli_parser.build_parser(cli_registry.build_registry())

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["artifact", "import", "chatgpt-output", "--help"])

    assert exc_info.value.code == 0
    help_text = capsys.readouterr().out
    assert "--initiative" in help_text
    assert "--epic" in help_text
    assert "--issue" in help_text
    assert "--file" in help_text
    assert "--title" in help_text
    assert "--slug" in help_text
    assert "--json" in help_text
    for forbidden in ("--destination", "--encoding", "--template", "--frontmatter", "--move", "--overwrite"):
        assert forbidden not in help_text

    ns = parser.parse_args([
        "artifact",
        "import",
        "chatgpt-output",
        "--issue",
        "317",
        "--file",
        "spec-dock/.workbench/report.md",
        "--title",
        "Raw report",
        "--slug",
        "raw-report",
        "--json",
    ])
    args = cli_registry.build_registry().items[ns.command_key].args_factory(ns)
    assert isinstance(args, artifact_import_commands.ArtifactImportChatGptOutputArgs)
    assert args.scope_kind == "issue"
    assert args.scope_node_id == "317"
    assert args.source_path == "spec-dock/.workbench/report.md"
    assert args.title == "Raw report"
    assert args.slug == "raw-report"
    assert args.json is True


@pytest.mark.parametrize(
    "argv",
    [
        ["artifact", "import", "chatgpt-output", "--file", "a.md", "--title", "A"],
        [
            "artifact",
            "import",
            "chatgpt-output",
            "--issue",
            "317",
            "--epic",
            "312",
            "--file",
            "a.md",
            "--title",
            "A",
        ],
        ["artifact", "import", "chatgpt-output", "--issue", "317", "--title", "A"],
        ["artifact", "import", "chatgpt-output", "--issue", "317", "--file", "a.md"],
        [
            "artifact",
            "import",
            "chatgpt-output",
            "--issue",
            "317",
            "--file",
            "a.md",
            "--title",
            "A",
            "--encoding",
            "utf-8",
        ],
    ],
)
def test_artifact_import_chatgpt_output_rejects_non_minimal_or_ambiguous_args(argv) -> None:
    cli_parser, cli_registry, _artifact_import_commands = _runtime_modules()
    parser = cli_parser.build_parser(cli_registry.build_registry())

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)

    assert exc_info.value.code == 2


def test_existing_new_artifact_and_top_level_node_import_grammar_remain_available() -> None:
    cli_parser, cli_registry, _artifact_import_commands = _runtime_modules()
    parser = cli_parser.build_parser(cli_registry.build_registry())

    new_ns = parser.parse_args([
        "new",
        "artifact",
        "blank",
        "--issue",
        "317",
        "--title",
        "Raw",
        "--slug",
        "chatgpt-output-raw",
    ])
    node_import_ns = parser.parse_args(["import", "issue", "318", "--title", "Existing import", "--epic", "312"])

    assert new_ns.command_key == "new_artifact"
    assert node_import_ns.command_key == "import_issue"


def test_artifact_import_command_redacts_unexpected_runtime_failure() -> None:
    _cli_parser, _cli_registry, artifact_import_commands = _runtime_modules()
    args = artifact_import_commands.ArtifactImportChatGptOutputArgs(
        scope_node_id="317",
        scope_kind="issue",
        source_path="spec-dock/.workbench/raw.md",
        title="Raw",
        slug=None,
        json=True,
    )

    def fail(_request):
        raise RuntimeError("OSError /private/tmp/secret sk-secret")

    outcome = artifact_import_commands._run(args, SimpleNamespace(import_artifact=fail))

    assert outcome.exit_code == 1
    rendered = "\n".join(outcome.text.stdout_lines)
    assert '"code": "runtime_failed"' in rendered
    assert "/private/tmp" not in rendered
    assert "sk-secret" not in rendered
    assert "OSError" not in rendered
