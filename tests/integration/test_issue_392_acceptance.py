from __future__ import annotations

import inspect
import json
from pathlib import Path

from spec_dock import cli


def test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent(tmp_path: Path, capsys) -> None:
    repository = Path(__file__).parents[2]
    production = repository / "src" / "spec_dock"
    source = inspect.getsource(cli)
    assert "managed_distribution" not in source
    assert not (production / "managed_distribution.py").exists()
    assert not (production / "assets" / "managed_distribution.json").exists()
    assert all("managed_distribution" not in path.read_text(encoding="utf-8") for path in production.rglob("*.py"))

    target = (tmp_path / "consumer").resolve()
    target.mkdir()
    assert cli.main(["init", str(target), "--json"]) == 0
    install_output = capsys.readouterr().out
    install = json.loads(install_output)
    assert install["code"] == "install-completed"
    assert install["candidate_digest"]

    before_rejected_purge = {
        path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
    }
    assert cli.main(["uninstall", str(target), "--apply", "--remove-specs", "--json"]) == 2
    rejected_output = capsys.readouterr().out
    rejected = json.loads(rejected_output)
    assert rejected["code"] == "spec-history-purge-removed"
    assert {
        path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
    } == before_rejected_purge

    assert cli.main(["uninstall", str(target), "--apply", "--keep-specs", "--json"]) == 0
    uninstall = json.loads(capsys.readouterr().out)
    assert uninstall["code"] == "uninstall-completed"
    assert (target / "spec-dock/spec-dock.version").is_file()
