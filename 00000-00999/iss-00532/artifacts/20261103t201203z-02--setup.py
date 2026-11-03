"""iss-00532 browser check: a temporary state root (no user state is touched) with three repositories.

  spec-dock  the real structure snapshot (tests/fixtures/issue532) with sample pull requests
  generated  the generated 250-Scope structure (tests/support/dashboard_graph.generated)
  sample     a small structure; mode "change" rewrites it so the change marks appear
usage: python setup.py <state_dir> <repo_root> [init|change]
"""
import json
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

state, repo = Path(sys.argv[1]), Path(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else "init"
sys.path.insert(0, str(repo))
from spec_dock.runtime.domain.dashboard_snapshot import parse_snapshot_document  # noqa: E402
from tests.support.dashboard import closed, node, pr, prs, snapshot  # noqa: E402
from tests.support.dashboard_graph import generated  # noqa: E402
from tests.support.dashboard_site import register, write_snapshot  # noqa: E402

root = state / "spec-dock"
now = datetime.now(timezone.utc)
stamp = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
fresh = stamp(now - timedelta(minutes=1))


def sample(changed: bool):
    nodes = [
        node(1, "epic", title="見本の Epic", created_at=stamp(now - timedelta(days=30))),
        node(2, "issue", parent=1, title="作業中の Issue", in_progress=True, created_at=stamp(now - timedelta(days=20))),
        node(3, "issue", parent=1, blocked_by=(2,), title="止められている Issue", created_at=stamp(now - timedelta(days=12))),
        node(4, "issue", parent=1, title="着手できる Issue", in_progress=changed, created_at=stamp(now - timedelta(days=5))),
    ]
    if changed:
        nodes.append(node(5, "issue", parent=1, title="新しい Issue", created_at=stamp(now - timedelta(hours=1))))
    return replace(snapshot(*nodes, fetched_at=fresh), repository="github.com/o/sample")


if mode == "init":
    payload = json.loads((repo / "tests/fixtures/issue532/spec-dock-snapshot.json").read_text())
    real = parse_snapshot_document(payload, repository="github.com/chemitaro/spec-dock").snapshot
    open_issues = sorted(n.number for n in real.scopes if n.state == "open" and n.kind == "issue")
    picks = open_issues[:6]
    items = [
        pr(900, f"chemitaro/iss-{picks[0]:05d}", checks="success", mergeable="mergeable", created_at=stamp(now - timedelta(hours=5))),
        pr(901, f"chemitaro/iss-{picks[1]:05d}", checks="failure", created_at=stamp(now - timedelta(hours=4))),
        pr(902, f"chemitaro/iss-{picks[2]:05d}", draft=True, checks="pending", created_at=stamp(now - timedelta(hours=3))),
        pr(903, f"chemitaro/iss-{picks[3]:05d}", mergeable="conflicting", created_at=stamp(now - timedelta(hours=2))),
        pr(904, f"chemitaro/iss-{picks[4]:05d}", state="merged", created_at=stamp(now - timedelta(days=1)), merged_at=stamp(now - timedelta(hours=1))),
    ]
    # the sample PRs' Scopes are in progress, as a worktree would make them
    nodes = [replace(n, in_progress=True) if n.number in picks[:4] else n for n in real.scopes]
    real = replace(snapshot(*nodes, fetched_at=fresh), repository="github.com/chemitaro/spec-dock")
    for name, structure in (("spec-dock", prs(real, *items, fetched_at=fresh)), ("generated", replace(generated(), fetched_at=fresh, fetch_started_at=fresh)), ("sample", sample(False))):
        catalog = state / f"catalog-{name}"
        register(root, structure.repository, catalog)
        write_snapshot(root, structure)
elif mode == "change":
    write_snapshot(root, sample(True))
print("ok")
