"""iss-00544 browser check: a temporary state root (the user's state is not touched).

  spec-dock  the real structure snapshot (tests/fixtures/issue532), catalog without CUE files
  sample     a small structure whose catalog is a git repository: iss-00002 (doing) has requirement.cue
             (standard) and a worktree on branch u/iss-00002; iss-00003 is a CUE Scope (strict), not doing
  empty      registered, with no structure snapshot
usage: python setup.py <state_root> <work_dir> <repo_root>
"""
import json, subprocess, sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

state, work, repo = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(repo))
from spec_dock.runtime.domain.dashboard_snapshot import parse_snapshot_document  # noqa: E402
from tests.support.dashboard import node, snapshot  # noqa: E402
from tests.support.dashboard_site import register, scope_dir, write_snapshot  # noqa: E402

fresh = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
payload = json.loads((repo / "tests/fixtures/issue532/spec-dock-snapshot.json").read_text())
real = parse_snapshot_document(payload, repository="github.com/chemitaro/spec-dock").snapshot
register(state, "github.com/chemitaro/spec-dock", work / "catalog-spec-dock")
write_snapshot(state, replace(real, fetched_at=fresh, fetch_started_at=fresh))

git = work / "sample-repo"
subprocess.run(["git", "init", "-q", "-b", "main", str(git)], check=True)
subprocess.run(["git", "-C", str(git), "-c", "user.name=t", "-c", "user.email=t@e", "commit", "-q", "--allow-empty", "-m", "x"], check=True)
subprocess.run(["git", "-C", str(git), "worktree", "add", "-q", "-b", "u/iss-00002", str(work / "sample-wt")], check=True)
catalog = git / "spec-dock" / ".canonical"
req = 'package spec\nschema: "specdock/v1"\nassurance: {{level: "{0}", reason: "r"}}\n'
(scope_dir(catalog, "iss-00002") / "requirement.cue").write_text(req.format("standard"))
(scope_dir(catalog, "iss-00003") / "requirement.cue").write_text(req.format("strict"))
register(state, "github.com/o/sample", catalog)
sample = snapshot(
    node(1, "epic", title="見本の Epic"),
    node(2, "issue", parent=1, in_progress=True, title="作業中の Issue"),
    node(3, "issue", parent=1, blocked_by=(2,), title="止められている Issue"),
    node(4, "issue", parent=1, title="着手できる Issue"),
    fetched_at=fresh,
)
write_snapshot(state, replace(sample, repository="github.com/o/sample"))
register(state, "github.com/o/empty", work / "catalog-empty")
print("ok")
