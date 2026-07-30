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


def test_artifact_import_file_help_and_minimal_parser_contract(capsys) -> None:
    cli_parser, cli_registry, artifact_import_commands = _runtime_modules()
    parser = cli_parser.build_parser(cli_registry.build_registry())

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["artifact", "import", "file", "--help"])

    assert exc_info.value.code == 0
    help_text = capsys.readouterr().out
    for required in ("--file", "--root", "--initiative", "--epic", "--issue", "--json"):
        assert required in help_text
    for forbidden in ("--title", "--slug", "--mime", "--encoding", "--move", "--overwrite"):
        assert forbidden not in help_text

    ns = parser.parse_args([
        "artifact",
        "import",
        "file",
        "--issue",
        "345",
        "--file",
        "evidence/Report FINAL.PDF",
        "--json",
    ])
    args = cli_registry.build_registry().items[ns.command_key].args_factory(ns)
    assert isinstance(args, artifact_import_commands.ArtifactImportFileArgs)
    assert args.target_kind == "issue"
    assert args.target_value == "345"
    assert args.source_path == "evidence/Report FINAL.PDF"
    assert args.json is True


@pytest.mark.parametrize(
    "argv",
    [
        ["artifact", "import", "file", "--file", "a.bin"],
        ["artifact", "import", "file", "--root", "--issue", "345", "--file", "a.bin"],
        ["artifact", "import", "file", "--root"],
        ["artifact", "import", "file", "--root", "--file", "a.bin", "--title", "A"],
    ],
)
def test_artifact_import_file_rejects_missing_or_ambiguous_target(argv) -> None:
    cli_parser, cli_registry, _commands = _runtime_modules()
    parser = cli_parser.build_parser(cli_registry.build_registry())

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["artifact", "import", "file", "--file", "source.bin"],
        ["artifact", "import", "file", "--root", "--issue", "345", "--file", "source.bin"],
    ],
)
def test_zero_or_multiple_targets_never_dispatch_or_mutate_source_and_destination(tmp_path, argv) -> None:
    cli_parser, cli_registry, _commands = _runtime_modules()
    registry = cli_registry.build_registry()
    original = registry.items["artifact_import_file"]
    calls = []

    def unexpected_run(args, use_cases):
        calls.append((args, use_cases))
        return original.run(args, use_cases)

    registry.items["artifact_import_file"] = type(original)(
        add_arguments=original.add_arguments,
        args_factory=original.args_factory,
        run=unexpected_run,
    )
    parser = cli_parser.build_parser(registry)
    source = tmp_path / "source.bin"
    body = b"must remain unopened and unchanged"
    source.write_bytes(body)
    artifacts_dir = tmp_path / "spec-dock" / "artifacts"

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)

    assert exc_info.value.code == 2
    assert calls == []
    assert source.read_bytes() == body
    assert not artifacts_dir.exists()


def test_artifact_import_file_run_uses_separate_request_and_renderer() -> None:
    _cli_parser, _cli_registry, commands = _runtime_modules()
    captured = []
    args = commands.ArtifactImportFileArgs(
        target_kind="root",
        target_value=None,
        source_path="evidence.bin",
        json=True,
    )

    def import_file(request):
        captured.append(request)
        return SimpleNamespace(
            import_kind="file",
            storage_identity="generic",
            target_kind="root",
            target_id="root",
            artifact_id="20260730t010203z--evidence.bin",
            source_visibility="repo_relative",
            source="evidence.bin",
            destination=Path("spec-dock/artifacts/20260730t010203z--evidence.bin"),
            committed=True,
            publication_state="committed",
            cleanup_state="removed",
            warning_codes=(),
            retry_disposition="not_needed",
            canonical=False,
        )

    outcome = commands._run_file(args, SimpleNamespace(import_file_artifact=import_file))

    assert outcome.exit_code == 0
    assert captured[0].target_kind == "root"
    assert captured[0].target_value is None
    assert captured[0].source_path == Path("evidence.bin")
    assert '"canonical": false' in "\n".join(outcome.text.stdout_lines)
