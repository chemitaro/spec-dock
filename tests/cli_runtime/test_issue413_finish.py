"""Legacy REST gh stub kept for other modules (iss-00440).

Its tests moved to tests/cli_runtime/test_issue440_g1_work_finish.py and test_issue440_g1_cli_parsing.py.
"""

from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


# TODO(iss-00440): remove after all groups migrate
def github_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, states: dict[str, str]) -> Path:
    bin_dir = tmp_path / "gh-bin"
    bin_dir.mkdir()
    state_file = tmp_path / "remote-states.json"
    state_file.write_text(json.dumps(states))
    log = tmp_path / "requests.jsonl"
    executable = bin_dir / "gh"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\nfrom pathlib import Path\n"
        f"states_path=Path({str(state_file)!r})\nlog=Path({str(log)!r})\n"
        "args=sys.argv[1:]\nmethod=args[args.index('--method')+1]\n"
        "endpoint=args[args.index('--method')+2]\nnumber=int(endpoint.rsplit('/',1)[1])\n"
        "assert endpoint==f'repos/example/repo/issues/{number}'\n"
        "assert method in ('GET','PATCH')\nbody=json.load(sys.stdin) if method=='PATCH' else None\n"
        "with log.open('a') as stream: stream.write(json.dumps({'method':method,'number':number,'body':body})+'\\n')\n"
        "states=json.loads(states_path.read_bytes())\n"
        "if method=='PATCH':\n"
        " assert body=={'state':'closed','state_reason':'completed'}\n"
        " states[str(number)]='completed'\n states_path.write_text(json.dumps(states))\n"
        "state=states[str(number)]\n"
        "payload={'number':number,'title':'Fixture','repository_url':'https://api.github.com/repos/example/repo',"
        "'html_url':f'https://github.com/example/repo/issues/{number}',"
        "'state':'unrecognized' if state=='unknown' else 'open' if state=='open' else 'closed',"
        "'state_reason':None if state=='open' else 'not_planned' if state=='not-planned' else 'completed',"
        "'updated_at':'2026-09-30T00:00:00Z'}\n"
        "print('HTTP/2.0 200 OK\\n\\n'+json.dumps(payload))\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    return log
