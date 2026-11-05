// Small CDP helper for the iss-00532/iss-00560 browser check (headless Chrome, closed with Browser.close).
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export async function launch(port = 19544) {
  const dir = mkdtempSync(join(tmpdir(), "iss574-"));
  const proc = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${dir}`, "--disable-features=MacAppCodeSignClone", "--no-first-run", "--no-default-browser-check", "about:blank"], { stdio: "ignore" });
  let ws;
  for (let i = 0; i < 80; i++) {
    try { const j = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json(); ws = new WebSocket(j.webSocketDebuggerUrl); break; } catch { await sleep(200); }
  }
  await new Promise((r) => ws.addEventListener("open", r));
  let id = 0; const pend = new Map(); const listeners = [];
  ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } else listeners.forEach((f) => f(d)); });
  const cmd = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
  const pages = [];
  async function page({ mobile = false, dark = false, width = 1440, height = 900 } = {}) {
    const { targetId } = await cmd("Target.createTarget", { url: "about:blank" });
    const { sessionId } = await cmd("Target.attachToTarget", { targetId, flatten: true });
    const errors = [];
    listeners.push((d) => {
      if (d.sessionId !== sessionId) return;
      if (d.method === "Runtime.exceptionThrown") errors.push(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text);
      if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") errors.push("console.error " + d.params.args.map((a) => a.value ?? a.description).join(" "));
      if (d.method === "Log.entryAdded" && d.params.entry.level === "error") errors.push("log " + d.params.entry.text + " " + (d.params.entry.url || ""));
    });
    await cmd("Page.enable", {}, sessionId);
    await cmd("Runtime.enable", {}, sessionId);
    await cmd("Log.enable", {}, sessionId);
    await cmd("Emulation.setDeviceMetricsOverride", mobile ? { width: 390, height: 844, deviceScaleFactor: 3, mobile: true } : { width, height, deviceScaleFactor: 1, mobile: false }, sessionId);
    if (mobile) await cmd("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 }, sessionId);
    await cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }] }, sessionId);
    const evalErrors = [];
    const evRaw = async (expr) => { const r = await cmd("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sessionId); if (r.exceptionDetails) throw new Error((r.exceptionDetails.exception?.description || r.exceptionDetails.text).slice(0, 300)); return r.result.value; };
    const ev = async (expr) => { try { return await evRaw(expr); } catch (e) { evalErrors.push(expr.slice(0, 120) + " => " + e.message); return null; } };
    const go = async (url, until = "document.querySelector('.gx-edges') || document.querySelector('.tl') || document.querySelector('.gx-empty:not([hidden])')", max = 8000) => {
      try { await evRaw("window.__oldPage = 1"); } catch {}
      const t0 = Date.now(); await cmd("Page.navigate", { url }, sessionId);
      while (Date.now() - t0 < max) { try { if (await evRaw(`!window.__oldPage && document.readyState !== "loading" && !!(${until})`)) break; } catch {} await sleep(30); }
      return Date.now() - t0;
    };
    const shot = async (file) => { front = false; await toFront(); await sleep(150); const r = await cmd("Page.captureScreenshot", { format: "png" }, sessionId); writeFileSync(file, Buffer.from(r.data, "base64")); };
    let front = false;
    const toFront = async () => { if (!front) { for (const q of pages) q.markBack(); await cmd("Page.bringToFront", {}, sessionId); front = true; } };
    const touch = async (type, points) => { await toFront(); return cmd("Input.dispatchTouchEvent", { type, touchPoints: points.map(([x, y], i) => ({ x, y, id: i })) }, sessionId); };
    const mouse = async (type, x, y, clickCount = 1) => { await toFront(); return cmd("Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount, buttons: type === "mouseReleased" ? 0 : 1 }, sessionId); };
    // iss-00560: change the window's size (fires resize in the page)
    const resize = (w, h) => cmd("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false }, sessionId);
    const pg = { ev, go, shot, touch, mouse, resize, errors, evalErrors, sessionId, markBack: () => { front = false; } };
    pages.push(pg);
    return pg;
  }
  const close = async () => { try { await cmd("Browser.close"); } catch {} await sleep(500); try { proc.kill(0); } catch {} };
  return { page, close, cmd };
}
