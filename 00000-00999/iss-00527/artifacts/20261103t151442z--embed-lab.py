#!/usr/bin/env python3
"""iss-00527 試作：iframe 埋め込みの確かめ用の2つの手元のサーバー（製品のコードではない）。

親（company-os の代わり）= --parent-port、子（SpecDock の代わり）= --child-port。
起点が違うので、iframe は本物のクロスオリジンになる。

使い方:
  python3 embed-lab.py                          # 127.0.0.1 のみ（PC の確かめ）
  python3 embed-lab.py --bind 100.x.y.z         # Tailscale の IP で待ち受ける（iPhone の確かめ。終わったら Ctrl-C）
親の画面: http://<host>:<parent-port>/   子の画面を直接: http://<host>:<child-port>/embed?embed=1
"""
import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--bind", default="127.0.0.1")
ap.add_argument("--parent-port", type=int, default=18527)
ap.add_argument("--child-port", type=int, default=18528)
ap.add_argument("--tailscale-ip", default="100.85.74.8", help="frame-ancestors に入れる Tailscale の IP（D-09）")
A = ap.parse_args()

ALLOW = f"'self' http://127.0.0.1:* http://localhost:* http://{A.tailscale_ip}:*"
ORIGIN_RE = r"^http://(127\.0\.0\.1|localhost|" + re.escape(A.tailscale_ip) + r"):\d+$"

# ---------------------------------------------------------------- 親（company-os の代わり）
PARENT = r"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>親（company-os の代わり）</title>
<style>
body{margin:0;font:14px system-ui;display:flex;flex-direction:column;height:100vh;height:100dvh}
#bar{padding:6px;display:flex;flex-wrap:wrap;gap:6px;background:#eef;border-bottom:1px solid #99c}
#bar button{font-size:14px;padding:6px 8px}
iframe{flex:1;border:0;width:100%;min-height:0}
#log{height:22vh;overflow:auto;margin:0;padding:4px;font:11px/1.3 ui-monospace,monospace;background:#111;color:#8f8;white-space:pre-wrap}
</style></head><body>
<div id="bar">
 <button id="b-hello">hello</button><button id="b-nav">navigate /embed?page=2</button>
 <button id="b-dark">theme dark</button><button id="b-light">theme light</button>
 <button id="b-back">history.back()</button><span id="info"></span>
</div>
<iframe id="f"></iframe><pre id="log"></pre>
<script>
const q=new URLSearchParams(location.search);
const CH=+q.get('cport')||__CPORT__;
const childHost=q.get('childhost')||location.hostname;
const childOrigin=location.protocol+'//'+childHost+':'+CH;
const src=q.get('src')||'/embed?embed=1';
const f=document.getElementById('f'), logEl=document.getElementById('log');
window.__log=[]; window.__hellos=0; window.__loads=0; window.__autoHello = q.get('autohello')!=='0';
const L=(k,o)=>{const r={t:Math.round(performance.now()),k,...o};window.__log.push(r);logEl.textContent+=JSON.stringify(r)+'\n';logEl.scrollTop=1e9};
function hello(){window.__hellos++;f.contentWindow.postMessage({source:'host',v:1,type:'hello'},childOrigin);L('sent',{type:'hello'})}
function send(type,x){f.contentWindow.postMessage({source:'host',v:1,type,...x},childOrigin);L('sent',{type,...x})}
window.__send=send; window.__hello=hello;
f.addEventListener('load',()=>{window.__loads++;L('iframe-load',{n:window.__loads});if(window.__autoHello)hello()});
f.src=childOrigin+src;
addEventListener('message',e=>{
  if(e.source!==f.contentWindow){L('ignored-non-child',{origin:e.origin});return}
  if(e.origin!==childOrigin){L('ignored-origin',{origin:e.origin});return}
  const d=e.data||{}; if(d.source!=='specdock'){L('ignored-shape',{});return}
  L('recv',d);
  if(d.type==='navigated'){history.replaceState(null,'','?p='+encodeURIComponent(d.path)+(location.search.includes('cport')?'':''))}
});
document.getElementById('b-hello').onclick=hello;
document.getElementById('b-nav').onclick=()=>send('navigate',{path:'/embed?page=2&embed=1'});
document.getElementById('b-dark').onclick=()=>send('theme',{scheme:'dark'});
document.getElementById('b-light').onclick=()=>send('theme',{scheme:'light'});
document.getElementById('b-back').onclick=()=>{history.back();L('top-history-back',{})};
document.getElementById('info').textContent='child='+childOrigin+src;
if(q.get('rogue')==='1'){const r=document.createElement('iframe');r.src='/rogue';r.style.cssText='height:0;flex:none';document.body.append(r)}
</script></body></html>""".replace("__CPORT__", str(A.child_port))

ROGUE = """<!doctype html><script>
// 親と同じ起点の、きょうだいの枠からの偽の hello（event.source が親ではない）
setTimeout(()=>{try{window.parent.frames[0].postMessage({source:'host',v:1,type:'hello'},'*');window.parent.__log.push({k:'rogue-sent'})}catch(e){window.parent.__log.push({k:'rogue-err',e:String(e)})}},1500)
</script>"""

# ---------------------------------------------------------------- 子（SpecDock の代わり）
CHILD = r"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>子 __PAGE__（SpecDock の代わり）</title>
<style>
html,body{margin:0;height:100%;font:13px system-ui;overflow:hidden}
body[data-theme=dark]{background:#111;color:#eee}
#bar{position:absolute;z-index:9;top:4px;left:4px;right:4px;display:flex;gap:4px;flex-wrap:wrap;pointer-events:none}
#bar>*{pointer-events:auto;font-size:13px;padding:4px 7px}
#view{position:absolute;inset:0;overflow:hidden;touch-action:none;background:#f4f6fb;cursor:grab}
body[data-theme=dark] #view{background:#222}
#world{position:absolute;left:0;top:0;transform-origin:0 0;width:900px;height:600px}
.n{position:absolute;width:120px;height:50px;border:2px solid #357;border-radius:8px;background:#fff;color:#000;display:grid;place-items:center;user-select:none;-webkit-user-select:none}
.n.sel{background:#fd8;border-color:#a50}
#st{position:absolute;bottom:2px;left:4px;z-index:9;font:11px ui-monospace,monospace;background:#fffc;color:#000;padding:2px 4px;pointer-events:none}
</style></head><body>
<div id="bar"><button id="zin">＋</button><button id="zout">－</button><button id="fit">全体を収める</button>
<a id="l-next" href="/embed?page=2&embed=1">通常のリンク（全画面遷移）</a>
<button id="b-spa">pushState で移る</button><a href="https://example.com/" target="_blank" rel="noopener">外へ(_blank)</a>
<button id="b-files">資料を開く</button></div>
<div id="view"><div id="world"></div></div><div id="st"></div>
<iframe id="doc" style="display:none;position:absolute;inset:40px 4px 4px 4px;width:calc(100% - 8px);height:calc(100% - 44px);z-index:20;background:#fff;border:2px solid #a50"></iframe>
<script>
const ALLOW_RE=new RegExp(__ORIGIN_RE__);
const q=new URLSearchParams(location.search);
const G=window.__g={scale:1,tx:0,ty:0,taps:0,selected:null,navs:0,pinches:0,drags:0,gs:0,gsPrevented:0,ptrMax:0,vv:1,log:[]};
let parentOrigin=null;
function dbg(m){G.log.push(m);const msg={source:'specdock',v:1,type:'debug',m,g:{...G,log:undefined}};
  try{parent.postMessage(msg,parentOrigin||'*')}catch(e){}}
function send(type,x){if(!parentOrigin)return false;parent.postMessage({source:'specdock',v:1,type,...x},parentOrigin);return true}
function scopeInfo(){return {id:q.get('sel')||null}}
function navigated(){send('navigated',{path:location.pathname+location.search,title:document.title,scope:scopeInfo()})}
addEventListener('message',e=>{
  if(e.data&&e.data.source==='lab-file'){dbg('file '+JSON.stringify(e.data));return}
  if(e.source!==window.parent){dbg('drop:not-parent '+e.origin);return}
  const d=e.data;if(!d||d.source!=='host'||d.v!==1){dbg('drop:shape');return}
  if(d.type==='hello'){
    if(!ALLOW_RE.test(e.origin)){dbg('drop:origin-not-allowed '+e.origin);return}
    parentOrigin=e.origin;
    send('ready',{repository:'lab/repo',path:location.pathname+location.search,title:document.title,capabilities:['navigate','theme']});
    navigated();dbg('hello-accepted '+e.origin);return}
  if(!parentOrigin||e.origin!==parentOrigin){dbg('drop:before-hello-or-origin '+e.origin);return}
  if(d.type==='navigate'){spa(d.path);dbg('navigate '+d.path)}
  else if(d.type==='theme'){document.body.dataset.theme=d.scheme==='auto'?'':d.scheme;dbg('theme '+d.scheme)}
});
function spa(p){history.pushState(null,'',p);G.navs++;const u=new URL(p,location.href);document.title='子 '+(u.searchParams.get('page')||'1');render();navigated()}
document.getElementById('b-spa').onclick=()=>spa('/embed?page=3&embed=1');
document.getElementById('b-files').onclick=()=>{const d=document.getElementById('doc');d.style.display='block';d.src='/r/h/o/n/files/iss-1/doc.html'};
addEventListener('popstate',()=>{dbg('popstate '+location.search);render();navigated()});
// ---- 図
const world=document.getElementById('world'),view=document.getElementById('view'),st=document.getElementById('st');
function render(){world.innerHTML='';for(let i=0;i<12;i++){const n=document.createElement('div');n.className='n'+(G.selected==='n'+i?' sel':'');n.dataset.id='n'+i;n.textContent='Scope '+i;n.style.left=(20+(i%4)*210)+'px';n.style.top=(90+Math.floor(i/4)*180)+'px';world.append(n)}apply()}
function apply(){const r=world.querySelector('.n');if(r){const b=r.getBoundingClientRect();G.r0=[b.left+b.width/2,b.top+b.height/2]}world.style.transform=`translate(${G.tx}px,${G.ty}px) scale(${G.scale})`;G.vv=window.visualViewport?visualViewport.scale:1;st.textContent=`scale=${G.scale.toFixed(2)} t=${G.tx|0},${G.ty|0} taps=${G.taps} vv=${G.vv}`}
function zoomAt(f,cx,cy){const s=Math.max(.3,Math.min(4,G.scale*f));const k=s/G.scale;G.tx=cx-(cx-G.tx)*k;G.ty=cy-(cy-G.ty)*k;G.scale=s;apply()}
const P=new Map();let g0=null,tapSt=null;
function two(){const [a,b]=[...P.values()];return {d:Math.hypot(a.x-b.x,a.y-b.y),cx:(a.x+b.x)/2,cy:(a.y+b.y)/2}}
view.addEventListener('pointerdown',e=>{view.setPointerCapture(e.pointerId);P.set(e.pointerId,{x:e.clientX,y:e.clientY});G.ptrMax=Math.max(G.ptrMax,P.size);
  if(P.size===1)tapSt={x:e.clientX,y:e.clientY,t:performance.now(),target:e.target.closest('.n'),moved:false};
  if(P.size===2){tapSt&&(tapSt.moved=true);g0=two()}});
view.addEventListener('pointermove',e=>{const p=P.get(e.pointerId);if(!p)return;
  if(P.size===1){const dx=e.clientX-p.x,dy=e.clientY-p.y;if(tapSt&&Math.hypot(e.clientX-tapSt.x,e.clientY-tapSt.y)>6){if(!tapSt.moved){G.drags++}tapSt.moved=true}
    if(tapSt&&tapSt.moved){G.tx+=dx;G.ty+=dy;apply()}}
  p.x=e.clientX;p.y=e.clientY;
  if(P.size===2&&g0){const n=two();if(!g0.counted){G.pinches++;g0.counted=1}G.tx+=n.cx-g0.cx;G.ty+=n.cy-g0.cy;zoomAt(n.d/g0.d,n.cx,n.cy);g0.d=n.d;g0.cx=n.cx;g0.cy=n.cy}});
function up(e){if(!P.has(e.pointerId))return;P.delete(e.pointerId);
  if(P.size===0&&tapSt&&!tapSt.moved&&performance.now()-tapSt.t<600&&e.type==='pointerup'){G.taps++;const id=tapSt.target&&tapSt.target.dataset.id;
    if(id){if(G.selected===id){const p='/embed?page=2&sel='+id+'&embed=1';spa(p);dbg('second-tap-navigate '+id)}else{G.selected=id;render();dbg('tap-select '+id)}}}
  if(P.size<2)g0=null;if(P.size===0)tapSt=null;apply();dbg('up '+e.type)}
view.addEventListener('pointerup',up);view.addEventListener('pointercancel',up);
// Safari: ページ全体の拡大と競合させない
for(const t of ['gesturestart','gesturechange','gestureend'])document.addEventListener(t,e=>{G.gs++;if(e.cancelable){e.preventDefault();G.gsPrevented++}},{passive:false});
view.addEventListener('wheel',e=>{e.preventDefault();zoomAt(e.deltaY<0?1.1:1/1.1,e.clientX,e.clientY)},{passive:false});
document.getElementById('zin').onclick=()=>zoomAt(1.25,innerWidth/2,innerHeight/2);
document.getElementById('zout').onclick=()=>zoomAt(.8,innerWidth/2,innerHeight/2);
document.getElementById('fit').onclick=()=>{G.scale=Math.min(innerWidth/900,innerHeight/600);G.tx=0;G.ty=0;apply()};
if(window.visualViewport)visualViewport.addEventListener('resize',()=>{apply();dbg('visualViewport-resize '+visualViewport.scale)});
if(q.get('autodoc')==='1')document.getElementById('b-files').click();
render();dbg('loaded '+location.pathname+location.search+' top='+(window.top===window.self?'self':'framed'));
</script></body></html>"""

FILE_HTML = """<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>資料</title>
<link rel="stylesheet" href="../../../design-system/ds.css"></head>
<body><h1 id="h">sandbox の資料</h1><pre id="o"></pre>
<script>
const R={};const o=document.getElementById('o');
function done(){const m={source:'lab-file',results:R};document.getElementById('o').textContent=JSON.stringify(R,null,1);
  try{parent.postMessage(m,'*')}catch(e){}}
R.origin=String(self.origin);
try{R.parentDom=String(parent.document.title)}catch(e){R.parentDom='BLOCKED '+e.name}
try{R.localStorage=String(localStorage.length)}catch(e){R.localStorage='BLOCKED '+e.name}
R.cssApplied=getComputedStyle(document.body).getPropertyValue('--lab-ds')||'no';
const T=[
 ['fetchApi', fetch('__CHILD__/api/secret').then(r=>'READABLE '+r.status).catch(e=>'BLOCKED '+e.name)],
 ['fetchDsCss', fetch('__CHILD__/ds/ds.css').then(r=>'OK '+r.status).catch(e=>'BLOCKED '+e.name)],
 ['importDsJs', import('__CHILD__/ds/ds.js').then(m=>'OK '+m.ok).catch(e=>'BLOCKED '+e.name)],
 ['importApiAsJs', import('__CHILD__/api/secret.js').then(m=>'READABLE').catch(e=>'BLOCKED '+e.name)],
];
Promise.all(T.map(([k,p])=>p.then(v=>{R[k]=v}))).then(done);
</script></body></html>"""

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="50" height="20"><script>try{parent.postMessage({source:'lab-file',svg:(function(){try{return String(parent.document.title)}catch(e){return 'BLOCKED '+e.name}})()},'*')}catch(e){}</script><text y="15">svg</text></svg>"""


def child_page(page):
    return CHILD.replace("__PAGE__", page).replace("__ORIGIN_RE__", json.dumps(ORIGIN_RE))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype, headers=None):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = self.path.split("?")[0]
        port = self.server.server_address[1]
        if port == A.parent_port:
            if path == "/":
                return self.send(200, PARENT, "text/html; charset=utf-8")
            if path == "/rogue":
                return self.send(200, ROGUE, "text/html; charset=utf-8")
            return self.send(404, "nf", "text/plain")
        # ---- 子
        if path in ("/embed", "/embed-strict"):
            q = self.path.split("?", 1)[1] if "?" in self.path else ""
            page = (re.search(r"page=(\w+)", q) or [None, "1"])[1]
            csp = f"frame-ancestors {ALLOW}" if path == "/embed" else "frame-ancestors 'self'"
            return self.send(200, child_page(page), "text/html; charset=utf-8", {"Content-Security-Policy": csp})
        if path == "/":
            return self.send(200, child_page("normal"), "text/html; charset=utf-8", {"Content-Security-Policy": "frame-ancestors 'self'"})
        if path.startswith("/r/") and "/files/" in path:
            sb = {"Content-Security-Policy": f"sandbox allow-scripts allow-popups; frame-ancestors {ALLOW}", "X-Content-Type-Options": "nosniff"}
            if path.endswith(".html"):
                return self.send(200, FILE_HTML.replace("__CHILD__", f"http://{self.headers.get('Host')}"), "text/html; charset=utf-8", sb)
            if path.endswith(".svg"):
                return self.send(200, SVG, "image/svg+xml", sb)
        m = re.search(r"/design-system/(ds\.css|ds\.js)$", path) or re.match(r"^/ds/(ds\.css|ds\.js)$", path)
        if m:
            cors = {"Access-Control-Allow-Origin": "*"} if path.startswith("/ds/") else {}
            # 相対の道（../../../design-system/）はサーバーが /ds/ に写す。写した先の応答にだけ CORS を付ける
            cors = {"Access-Control-Allow-Origin": "*"}
            if m.group(1) == "ds.css":
                return self.send(200, ":root{--lab-ds:'ds-loaded'}body{font-family:system-ui;background:#e8ffe8}", "text/css", cors)
            return self.send(200, "export const ok='ds-js'", "text/javascript", cors)
        if path in ("/api/secret", "/api/secret.js"):
            return self.send(200, json.dumps({"secret": "repo-data"}) if path == "/api/secret" else "export default 1", "application/json" if path == "/api/secret" else "text/javascript")
        return self.send(404, "nf", "text/plain")


def main():
    servers = [ThreadingHTTPServer((A.bind, p), H) for p in (A.parent_port, A.child_port)]
    import threading
    for s in servers:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    print(f"parent http://{A.bind}:{A.parent_port}/  child http://{A.bind}:{A.child_port}/embed?embed=1  (Ctrl-C で止める)", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    for s in servers:
        s.shutdown()


main()
