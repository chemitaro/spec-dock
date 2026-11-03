"""iss-00529 browser check: a temporary state root with two repositories (no user state is touched)."""
import json, sys
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.support.dashboard import node, closed, snapshot, pr, prs
from tests.support.dashboard_site import register, write_snapshot, scope_dir
from datetime import datetime, timezone, timedelta

root = Path(sys.argv[1]) / "spec-dock"
mode = sys.argv[2] if len(sys.argv) > 2 else "init"
now = datetime.now(timezone.utc)
stamp = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
r = Path(sys.argv[1]) / "catalog-r"
s = Path(sys.argv[1]) / "catalog-s"
def struct_r(extra=()):
    return replace(snapshot(node(1, "epic", title="Epic one"), node(2, "issue", parent=1, in_progress=True, title="Doing issue"),
        node(3, "issue", parent=1, blocked_by=(2,), title="Blocked issue"), *extra, fetched_at=stamp(now - timedelta(minutes=2))), repository="github.com/o/r")
if mode == "init":
    register(root, "github.com/o/r", r)
    register(root, "github.com/o/s", s)
    write_snapshot(root, struct_r())
    write_snapshot(root, replace(snapshot(node(9, "issue", title="Old"), fetched_at=stamp(now - timedelta(hours=3))), repository="github.com/o/s"))
    d = scope_dir(r, "iss-00002")
    (d / "explanation.html").write_text("""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="../../../design-system/ds.css"><title>material</title></head><body><pre id="o">running</pre><script>
const R={origin:String(self.origin)};
try{R.parentDom=String(window.top.document.title)}catch(e){R.parentDom='BLOCKED '+e.name}
try{R.localStorage=String(localStorage.length)}catch(e){R.localStorage='BLOCKED '+e.name}
try{R.cookie=document.cookie;R.cookieOk='READ'}catch(e){R.cookieOk='BLOCKED '+e.name}
R.dsLoaded=getComputedStyle(document.documentElement).getPropertyValue('--ds-accent')||'no';
Promise.all([
 fetch('/api/v1/repositories').then(r=>'READABLE '+r.status).catch(e=>'BLOCKED '+e.name).then(v=>R.fetchApi=v),
 fetch('/api/v1/r/github.com/o/r/seen',{method:'POST',headers:{'Content-Type':'application/json','X-SpecDock-Dashboard':'1'},body:'{}'}).then(r=>'SENT '+r.status).catch(e=>'BLOCKED '+e.name).then(v=>R.postSeen=v),
 fetch('/ds/ds.css').then(r=>'OK '+r.status).catch(e=>'BLOCKED '+e.name).then(v=>R.fetchDs=v),
]).then(()=>{document.getElementById('o').textContent=JSON.stringify(R);document.title='done'});
</script></body></html>""")
elif mode == "change":
    write_snapshot(root, prs(struct_r((node(4, "issue", parent=1, title="New issue", created_at=stamp(now)),)), pr(20, "iss-00002"), fetched_at=stamp(now)))
print("ok")
