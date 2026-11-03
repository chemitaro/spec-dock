"""iss-00531 browser check: a temporary state root with five repositories (no user state is touched).

o/r  rich: PRs (mergeable, needs fix, draft), unknown, cleanup, a closed parent with open children, changes since
     the last "seen", catalog files and Artifacts for some Scopes and none for others.
o/s  three hours stale, no pull request data (PR unknown).
o/m  registered, no snapshot (missing).
o/a  anomalies.
o/big  ~250 Scopes for the 2-second board check.
"""
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, sys.argv[2])
from spec_dock.runtime.domain.canonical_structure import ExternalIssue, StructureAnomaly
from spec_dock.runtime.domain.dashboard_model import build_model, seen_scopes, SeenScope
from spec_dock.runtime.infra.dashboard_store import append_seen
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.dashboard import closed, node, pr, prs, snapshot
from tests.support.dashboard_site import register, scope_dir, write_snapshot

base = Path(sys.argv[1])
root = base / "spec-dock"
now = datetime.now(timezone.utc)
stamp = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")


def repo(name, structure):
    return replace(structure, repository=f"github.com/o/{name}")


r = repo("r", snapshot(
    node(1, "initiative", title="Dashboard initiative"),
    node(2, "epic", parent=1, title="Board and details <script>alert(1)</script>"),
    node(3, "issue", parent=2, title="Ready and waited for by two", created_at="2026-10-20T00:00:00Z"),
    node(4, "issue", parent=2, blocked_by=(3,), title="Waits for #3"),
    node(5, "issue", parent=2, blocked_by=(4,), title="Waits for #4"),
    node(6, "issue", parent=2, title="Ready alone"),
    node(7, "issue", parent=2, in_progress=True, title="Mergeable PR"),
    node(8, "issue", parent=2, in_progress=True, title="PR with failing CI"),
    node(9, "issue", parent=2, in_progress=True, title="Draft PR stays doing"),
    node(10, "issue", parent=2, in_progress=True, title="Conflicting PR"),
    closed(11, "issue", parent=2, title="Finished issue", closed_at="2026-11-01T00:00:00Z"),
    node(12, "epic", parent=1, blocked_by=(3, 90), title="Epic waiting for #3 and an outside issue"),
    node(13, "issue", parent=12, title="Inherits the Epic's waits"),
    closed(14, "epic", parent=1, title="Closed epic with an open child"),
    node(15, "issue", parent=14, title="Open under a closed epic"),
    node(16, "epic", parent=1, title="Every child finished"),
    closed(17, "issue", parent=16, title="Done child"),
    node(18, "issue", parent=2, title="Unknown: two kind labels"),
    node(20, "epic", parent=1, title="Epic another waits for"),
    node(21, "issue", parent=20, title="Ready child of the awaited Epic"),
    node(22, "issue", parent=2, blocked_by=(20,), title="Waits for an Epic"),
    external=(ExternalIssue(90, "Outside issue", "open"),),
    anomalies=(StructureAnomaly(18, "KIND_LABEL_MULTIPLE", "two kind labels"),),
    fetched_at=stamp(now - timedelta(minutes=2)),
))
r = prs(r, pr(40, "iss-00007"), pr(41, "chemitaro/iss-00008", checks="failure"), pr(42, "iss-00009", draft=True),
        pr(43, "iss-00010", mergeable="conflicting", checks="pending"), fetched_at=stamp(now - timedelta(minutes=2)))
s = repo("s", snapshot(node(1, "epic", title="Old epic"), node(2, "issue", parent=1, in_progress=True, title="Old doing"),
                        node(3, "issue", parent=1, title="Old ready"), fetched_at=stamp(now - timedelta(hours=3))))
a = repo("a", snapshot(node(1, "epic", title="Anomalous epic"), node(2, "issue", parent=1, title="Odd"),
                        anomalies=(StructureAnomaly(2, "KIND_LABEL_MULTIPLE", "two kind labels"),), fetched_at=stamp(now - timedelta(minutes=1))))
nodes = []
number = 1
for i in range(10):
    epic = number; nodes.append(node(epic, "epic", title=f"Big epic {i}")); number += 1
    prev = None
    for j in range(24):
        kind_state = (j % 6 == 5)
        item = (closed(number, "issue", parent=epic, title=f"Big issue {i}-{j}") if kind_state else
                node(number, "issue", parent=epic, title=f"Big issue {i}-{j}", in_progress=(j % 7 == 3),
                     blocked_by=((prev,) if prev and j % 3 == 1 else ())))
        nodes.append(item); prev = number; number += 1
big = repo("big", snapshot(*nodes, fetched_at=stamp(now - timedelta(minutes=1))))

for name, structure in (("r", r), ("s", s), ("a", a), ("big", big)):
    register(root, f"github.com/o/{name}", base / f"catalog-{name}")
    write_snapshot(root, structure)
register(root, "github.com/o/m", base / "catalog-m")

# Catalog files for o/r: iss-00003 has documents and Artifacts; iss-00005 has no directory.
catalog = base / "catalog-r"
d = scope_dir(catalog, "iss-00003")
(d / "requirement.cue").write_text('package spec\nschema: "specdock/v1"\nassurance: {level: "standard", reason: "check"}\n')
(d / "design.cue").write_text("package spec\n")
(d / "explanation.html").write_text("<!doctype html><title>explanation</title><p>material</p>")
(d / "artifacts").mkdir()
(d / "artifacts" / "20261104t000000z--prototype.html").write_text("<!doctype html><title>proto</title><p>proto</p>")
(d / "artifacts" / "20261104t000001z--notes <b>.md").write_text("# notes")
scope_dir(catalog, "epic-00002")

# A "seen" record that differs: #6 was blocked, #8's PR was open (now needs fix), #18 did not exist.
model = build_model(r, now=now)
before = dict(seen_scopes(model))
before["iss-00006"] = SeenScope("blocked", before["iss-00006"].pr)
before["iss-00008"] = SeenScope("doing", "open")
before.pop("iss-00004")
append_seen(root, GithubRepository("o", "r"), before, now=now - timedelta(hours=1))
print("ok")
