"""A test parent page (a stand-in for company-os) on another port: embeds SpecDock's ?embed=1 screen."""
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
port, child = int(sys.argv[1]), sys.argv[2]
PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>parent</title>
<style>body{margin:0;display:flex;flex-direction:column;height:100vh}iframe{flex:1;border:0}</style></head><body>
<iframe id="f"></iframe><iframe id="rogue" style="height:0;border:0"></iframe><script>
const q=new URLSearchParams(location.search), CH=%r, f=document.getElementById('f');
window.__log=[]; const childOrigin=new URL(CH).origin;
const L=(k,o)=>window.__log.push({k,...o});
window.hello=()=>{f.contentWindow.postMessage({source:'host',v:1,type:'hello'},childOrigin);L('sent',{type:'hello'})};
window.send=(type,x)=>{f.contentWindow.postMessage({source:'host',v:1,type,...x},childOrigin);L('sent',{type,...x})};
f.addEventListener('load',()=>{L('load',{});if(q.get('nohello')!=='1')hello()});
addEventListener('message',e=>{if(e.source!==f.contentWindow||e.origin!==childOrigin){L('ignored',{origin:e.origin});return}
 const d=e.data||{}; if(d.source!=='specdock')return; L('recv',d); if(d.type==='navigated')history.replaceState(null,'','?p='+encodeURIComponent(d.path))});
window.rogue=()=>{document.getElementById('rogue').srcdoc="<script>parent.frames[0].postMessage({source:'host',v:1,type:'hello'},'*')<\\/script>";L('rogue',{})};
f.src=q.get('src')?new URL(q.get('src'),CH).href:CH;
</script></body></html>"""
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        b=(PAGE % child).encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
