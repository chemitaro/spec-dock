"""iss-00574 browser check: a temporary state root and catalog with Scopes in every state.

usage: python setup.py <state_root> <work_dir> <repo_root>
Nothing is read from or written to the user's state (~/.local/state/spec-dock/).
"""
import os, sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

state, work, repo = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(repo))
from spec_dock.runtime.domain.canonical_structure import StructureAnomaly  # noqa: E402
from spec_dock.runtime.domain.todo_record import new_record  # noqa: E402
from spec_dock.runtime.infra.todo_store import TodoStore, encode  # noqa: E402
from tests.support.dashboard import closed, node, snapshot  # noqa: E402
from tests.support.dashboard_site import register, scope_dir, write_snapshot  # noqa: E402

now = datetime.now(timezone.utc)
at = lambda minutes: (now - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
catalog = work / "catalog"
register(state, "github.com/o/r", catalog)


def plan(scope_id, statuses, minutes):
    steps = "\n".join(
        f'\t"S-{i:02d}": {{title: "手順 {i}", realizes: ["R-01"], status: "{s}"}}' for i, s in enumerate(statuses, 1)
    )
    path = scope_dir(catalog, scope_id) / "plan.cue"
    path.write_text(f"package spec\n\nsteps: {{\n{steps}\n}}\n")
    t = (now - timedelta(minutes=minutes)).timestamp()
    os.utime(path, (t, t))


T = lambda n, d, rest="todo": ["done"] * d + [rest] * (n - d)
plan("iss-00003", T(8, 4), 5)            # moving (plan written 5 minutes ago)
plan("iss-00004", T(5, 2) + ["dropped"], 130)  # 2 hours idle
plan("iss-00009", T(14, 9), 70)          # more than 12 steps
plan("iss-00012", T(3, 3), 3)            # every step done, moving
old = at(60 * 24 * 3)
nodes = [
    node(1, "initiative", title="ダッシュボードの改善", updated_at=old),
    node(2, "epic", parent=1, title="状態の色とアイコン", updated_at=old),
    node(3, "issue", parent=2, in_progress=True, title="作業中・動いている（4／8）", updated_at=at(240)),
    node(4, "issue", parent=2, in_progress=True, title="作業中・2時間動きなし（2／5）", updated_at=at(130)),
    closed(5, "issue", parent=2, title="終わった", closed_at=at(600)),
    node(6, "issue", parent=2, title="着手できる", updated_at=old),
    node(7, "issue", parent=2, title="止められている（#6 を待つ）", blocked_by=(6,), updated_at=old),
    node(8, "issue", parent=2, in_progress=True, title="作業中・計画なし・動いている", updated_at=at(10)),
    node(9, "issue", parent=2, in_progress=True, title="作業中・14手順（9 終わった）・1時間動きなし", updated_at=at(70)),
    node(10, "epic", parent=1, title="別の Epic", updated_at=old),
    node(11, "issue", parent=10, title="不明（記録の食い違い）", updated_at=old),
    node(12, "issue", parent=10, in_progress=True, title="作業中・手順すべて終わった・動いている", updated_at=at(240)),
]
structure = snapshot(*nodes, anomalies=(StructureAnomaly(11, "KIND_LABEL_MISSING", "種類のラベルがない"),), fetched_at=at(1))
write_snapshot(state, replace(structure, repository="github.com/o/r", fetch_started_at=at(1)))
record = new_record("t-0001", title="#6 の方針を決める", by="human", role=None, kind=None, now=at(60), due=at(-60 * 24 * 3))
record["scopes"] = {"related": [], "blocks": ["iss-00007"]}
store = TodoStore(catalog)
path = store.record_path("t-0001", at(60))
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(encode(record))
print("ok", catalog)
