"""iss-00556 browser check: a temporary state root with this PC's real spec-dock structure snapshot.

The user's snapshot (~/.local/state/spec-dock/github/github.com/chemitaro/spec-dock/snapshot.json) is only read;
fetched_at is moved to now so that no stale notice covers the graph. The catalog is an empty temporary directory.
usage: python setup.py <state_root> <work_dir> <repo_root> <user_snapshot>
"""
import json, sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

state, work, repo, source = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
sys.path.insert(0, str(repo))
from spec_dock.runtime.domain.dashboard_snapshot import parse_snapshot_document  # noqa: E402
from tests.support.dashboard_site import register, write_snapshot  # noqa: E402

fresh = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
payload = json.loads(source.read_text())
real = parse_snapshot_document(payload, repository="github.com/chemitaro/spec-dock").snapshot
print("source fetched_at", real.fetched_at, "scopes", len(real.scopes))
register(state, "github.com/chemitaro/spec-dock", work / "catalog-spec-dock")
write_snapshot(state, replace(real, fetched_at=fresh, fetch_started_at=fresh))
print("ok")
