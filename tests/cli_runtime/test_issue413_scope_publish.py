"""Publish GitHub-numbered Scopes through the control-free public CLI."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


# TODO(iss-00440): remove after all groups migrate
def publication_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    from tests.cli_runtime.test_issue413_work_start import committed_workspace

    root = committed_workspace(tmp_path / "consumer")
    assets = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock"
    for relative in ("templates", "docs/rules"):
        shutil.copytree(assets / relative, root / "spec-dock" / relative)
    subprocess.run(
        ["git", "-C", str(root), "remote", "add", "origin", "https://github.com/example/repo.git"],
        check=True,
        capture_output=True,
    )
    bin_dir = tmp_path / "gh-bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-requests.jsonl"
    executable = bin_dir / "gh"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\n"
        "argv=sys.argv[1:]; method=argv[argv.index('--method')+1]; endpoint=argv[argv.index('--method')+2]\n"
        "assert argv[:5]==['api','--hostname','github.com','--include','--method']\n"
        "payload=json.load(sys.stdin) if '--input' in argv else None\n"
        f"with open({str(log)!r},'a') as stream: stream.write(json.dumps(dict(method=method,endpoint=endpoint,payload=payload))+'\\n')\n"
        "if method=='GET':\n"
        " number=int(endpoint.rsplit('/',1)[-1]); assert endpoint==f'repos/example/repo/issues/{number}'\n"
        " response=dict(number=number,repository_url='https://api.github.com/repos/example/repo',"
        "html_url=f'https://github.com/example/repo/issues/{number}',title='Existing Scope',"
        "state='open',state_reason=None,updated_at='2026-10-01T00:00:00Z')\n"
        " print('HTTP/2.0 200 OK\\n\\n'+json.dumps(response)); sys.exit(0)\n"
        "assert method=='POST' and endpoint=='repos/example/repo/issues'\n"
        "response=dict(number=57,repository_url='https://api.github.com/repos/example/repo',"
        "html_url='https://github.com/example/repo/issues/57',title=payload['title'],"
        "state='open',state_reason=None,updated_at='2026-10-01T00:00:00Z')\n"
        "print('HTTP/2.0 201 Created\\n\\n'+json.dumps(response))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    return root, log
