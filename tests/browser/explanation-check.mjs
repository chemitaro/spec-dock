#!/usr/bin/env node
// iss-00475 R-08: browser rendering check for thin explanation documents (local and optional; not part of pytest).
//
// Usage:
//   node tests/browser/explanation-check.mjs                 # run every built-in scenario
//   node tests/browser/explanation-check.mjs --scenario local-http [--scenario ...]
//   node tests/browser/explanation-check.mjs --file PATH [--cdn-from-package]
// Options: --chrome PATH, --timeout SECONDS (default 90), --design-system DIR (default: provider assets).
//
// Every request leaving the machine is blocked (CDP Fetch + host resolver rules). Only file: URLs and this
// tool's own 127.0.0.1 server pass. When a scenario allows it, requests to the pinned CDN URLs that ds.js
// uses are answered with the parts bundled in the package (src/spec_dock/assets/vendor/).
// Chrome runs with --disable-features=MacAppCodeSignClone and is closed with CDP Browser.close.

import { spawn } from "node:child_process";
import { constants as fsConstants } from "node:fs";
import { access, cp, mkdir, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { dirname, join, normalize, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const VENDOR_ROOT = join(REPO, "src/spec_dock/assets/vendor");
const DEFAULT_DESIGN_SYSTEM = join(REPO, "src/spec_dock/assets/spec_dock/design-system");
const SCOPE_DIR = "spec-dock/.canonical/00000-00999";
const SCENARIOS = ["canonical-file", "initiatives-file", "local-http", "local-fallback", "offline-standalone", "missing-marked"];
const sleep = ms => new Promise(r => setTimeout(r, ms));

class CheckError extends Error {}

function parseArgs(argv) {
  const options = { scenarios: [], file: null, cdnFromPackage: false, chrome: null, timeout: 90, designSystem: DEFAULT_DESIGN_SYSTEM };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const value = () => {
      if (i + 1 >= argv.length) throw new CheckError(`${arg} needs a value`);
      return argv[++i];
    };
    if (arg === "--scenario") options.scenarios.push(value());
    else if (arg === "--file") options.file = resolve(value());
    else if (arg === "--cdn-from-package") options.cdnFromPackage = true;
    else if (arg === "--chrome") options.chrome = resolve(value());
    else if (arg === "--timeout") options.timeout = Number(value());
    else if (arg === "--design-system") options.designSystem = resolve(value());
    else throw new CheckError(`unknown argument: ${arg}`);
  }
  for (const name of options.scenarios) if (!SCENARIOS.includes(name)) throw new CheckError(`unknown scenario: ${name}`);
  if (!options.file && !options.scenarios.length) options.scenarios = [...SCENARIOS];
  return options;
}

async function findChrome(explicit) {
  const candidates = explicit ? [explicit] : [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ];
  for (const candidate of candidates) {
    try {
      await access(candidate, fsConstants.X_OK);
      return candidate;
    } catch {
      // try the next candidate
    }
  }
  throw new CheckError("Chrome or Chromium was not found; pass --chrome PATH");
}

/* ---------- bundled parts and the CDN substitute ---------- */

async function loadVendor() {
  const manifest = JSON.parse(await readFile(join(VENDOR_ROOT, "manifest.json"), "utf8"));
  const prefixes = manifest.packages.map(p => ({ cdn: `https://unpkg.com/${p.name}@${p.version}/`, directory: p.directory }));
  const types = new Map(manifest.files.map(f => [f.path, f.content_type]));
  return { prefixes, types };
}

async function vendorFile(vendor, relative) {
  if (!vendor.types.has(relative)) return null;
  return { body: await readFile(join(VENDOR_ROOT, ...relative.split("/"))), type: vendor.types.get(relative) };
}

function cdnToVendorPath(vendor, url) {
  for (const prefix of vendor.prefixes) {
    if (url.startsWith(prefix.cdn)) return `${prefix.directory}/${url.slice(prefix.cdn.length).split(/[?#]/)[0]}`;
  }
  return null;
}

/* ---------- fixture tree and local server ---------- */

async function buildFixture(base, designSystem) {
  const repo = join(base, "repo");
  await cp(designSystem, join(repo, "spec-dock/design-system"), { recursive: true });
  const skeleton = await readFile(join(designSystem, "explanation-skeleton.html"), "utf8");
  const withMeta = content => {
    const marker = '<link rel="stylesheet"';
    if (!skeleton.includes(marker)) throw new CheckError("skeleton has no stylesheet link to place the meta before");
    return skeleton.replace(marker, `<meta name="ds-vendor-base" content="${content}">\n${marker}`);
  };
  const pages = { "iss-00001": skeleton, "iss-00002": withMeta("/vendor/"), "iss-00003": withMeta("/missing-vendor/") };
  for (const [id, html] of Object.entries(pages)) {
    await mkdir(join(repo, SCOPE_DIR, id), { recursive: true });
    await writeFile(join(repo, SCOPE_DIR, id, "explanation.html"), html);
  }
  await symlink(".canonical", join(repo, "spec-dock/initiatives"));
  const broken = join(base, "broken");
  await cp(repo, broken, { recursive: true, verbatimSymlinks: true });
  await rm(join(broken, "spec-dock/design-system/vendor/marked.umd.js"));
  return { repo, broken };
}

const STATIC_TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".md": "text/plain; charset=utf-8" };

async function startServer(root, vendor) {
  const server = createServer(async (request, response) => {
    try {
      const path = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
      if (path.startsWith("/vendor/")) {
        const file = await vendorFile(vendor, path.slice("/vendor/".length));
        if (!file) throw new Error("not in manifest");
        response.writeHead(200, { "Content-Type": file.type });
        response.end(file.body);
        return;
      }
      const target = normalize(join(root, path));
      if (target !== root && !target.startsWith(root + sep)) throw new Error("outside root");
      const extension = target.slice(target.lastIndexOf("."));
      const body = await readFile(target);
      response.writeHead(200, { "Content-Type": STATIC_TYPES[extension] ?? "application/octet-stream" });
      response.end(body);
    } catch {
      response.writeHead(404, { "Content-Type": "text/plain" });
      response.end("not found");
    }
  });
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  return { server, origin: `http://127.0.0.1:${server.address().port}` };
}

/* ---------- Chrome and CDP ---------- */

async function connect(url) {
  const socket = new WebSocket(url);
  const pending = new Map();
  const listeners = new Map();
  let nextId = 1;
  await new Promise((resolveOpen, rejectOpen) => {
    socket.addEventListener("open", resolveOpen, { once: true });
    socket.addEventListener("error", () => rejectOpen(new CheckError(`cannot connect to ${url}`)), { once: true });
  });
  socket.addEventListener("message", event => {
    const message = JSON.parse(String(event.data));
    if (message.id && pending.has(message.id)) {
      const { resolve: ok, reject: fail } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) fail(new CheckError(message.error.message));
      else ok(message.result);
    } else if (message.method) {
      for (const listener of listeners.get(message.method) ?? []) listener(message.params);
    }
  });
  const send = (method, params = {}) => new Promise((ok, fail) => {
    const id = nextId++;
    pending.set(id, { resolve: ok, reject: fail });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const on = (method, listener) => listeners.set(method, [...(listeners.get(method) ?? []), listener]);
  return { socket, send, on };
}

async function launchChrome(chromePath, profile) {
  const child = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-features=MacAppCodeSignClone",
    "--no-first-run",
    "--no-default-browser-check",
    "--allow-file-access-from-files",
    "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
    "--remote-debugging-address=127.0.0.1",
    "--remote-debugging-port=0",
    `--user-data-dir=${profile}`,
    "about:blank",
  ], { stdio: ["ignore", "ignore", "ignore"] });
  const deadline = Date.now() + 20_000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) throw new CheckError(`Chrome exited during start (exit ${child.exitCode})`);
    try {
      const port = Number((await readFile(join(profile, "DevToolsActivePort"), "utf8")).split(/\r?\n/)[0]);
      if (port > 0) return { child, port };
    } catch {
      // not written yet
    }
    await sleep(50);
  }
  throw new CheckError("Chrome DevTools did not start");
}

async function closeChrome(child, port) {
  if (!child || child.exitCode !== null) return;
  try {
    const version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
    const browser = await connect(version.webSocketDebuggerUrl);
    await browser.send("Browser.close").catch(() => {});
    browser.socket.close();
  } catch {
    // fall through to the exit wait
  }
  const exited = await Promise.race([new Promise(r => child.once("exit", () => r(true))), sleep(10_000).then(() => false)]);
  if (!exited && child.exitCode === null) child.kill("SIGKILL");
}

/* ---------- one page check ---------- */

const SNAPSHOT = `(() => {
  const clone = value => value ? JSON.parse(JSON.stringify(value)) : null;
  const source = document.getElementById("ds-source")?.textContent ?? "";
  const figures = [...document.querySelectorAll(".ds-diagram")].map(f => ({
    id: f.id,
    status: f.dataset.status,
    svg: f.querySelectorAll(".ds-diagram__canvas svg").length,
    error: (f.querySelector(".ds-diagram__error")?.textContent ?? "").trim().slice(0, 300),
  }));
  return {
    ds: clone(window.__dsState),
    plantuml: clone(window.__plantumlDocumentState),
    fenced: (source.match(/^\`\`\`plantuml\\b/gm) ?? []).length,
    figures,
    unknown: document.querySelectorAll(".ds-unknown").length,
    fatal: document.querySelector(".ds-fatal")?.textContent?.trim() ?? null,
    title: document.title,
  };
})()`;

const LAYOUT = `(() => ({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }))()`;

async function checkPage({ port, url, vendor, cdnFromPackage, origin, timeout, settle }) {
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
  const page = await connect(target.webSocketDebuggerUrl);
  const exceptions = [];
  const blocked = [];
  const substituted = [];
  page.on("Runtime.exceptionThrown", p => exceptions.push(p?.exceptionDetails?.exception?.description ?? p?.exceptionDetails?.text ?? "exception"));
  page.on("Fetch.requestPaused", async p => {
    const requestUrl = p.request.url;
    try {
      if (requestUrl.startsWith("file:") || (origin && requestUrl.startsWith(`${origin}/`))) {
        await page.send("Fetch.continueRequest", { requestId: p.requestId });
        return;
      }
      const vendorPath = cdnFromPackage ? cdnToVendorPath(vendor, requestUrl) : null;
      const file = vendorPath ? await vendorFile(vendor, vendorPath) : null;
      if (file) {
        substituted.push(requestUrl);
        await page.send("Fetch.fulfillRequest", {
          requestId: p.requestId,
          responseCode: 200,
          responseHeaders: [{ name: "Content-Type", value: file.type }, { name: "Access-Control-Allow-Origin", value: "*" }],
          body: file.body.toString("base64"),
        });
        return;
      }
      blocked.push(requestUrl);
      await page.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "InternetDisconnected" });
    } catch {
      // the page may have navigated away
    }
  });
  await page.send("Runtime.enable");
  await page.send("Page.enable");
  await page.send("Fetch.enable", { patterns: [{ urlPattern: "*" }] });
  await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
  await page.send("Page.navigate", { url });

  const evaluate = async expression => (await page.send("Runtime.evaluate", { expression, returnByValue: true })).result.value;
  const deadline = Date.now() + timeout * 1000;
  let snapshot = null;
  while (Date.now() < deadline) {
    snapshot = await evaluate(SNAPSHOT).catch(() => null);
    if (snapshot?.ds?.error || snapshot?.plantuml?.completed) break;
    await sleep(250);
  }
  // highlight.js loads independently of the diagrams; give it a short moment to report its source.
  const settleDeadline = Date.now() + settle;
  while (Date.now() < settleDeadline && snapshot?.ds && snapshot.ds.vendor?.hljs == null && !snapshot.ds.error) {
    await sleep(250);
    snapshot = await evaluate(SNAPSHOT).catch(() => snapshot);
  }
  await page.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await sleep(500);
  const layout = await evaluate(LAYOUT);
  await page.send("Fetch.disable").catch(() => {});
  page.socket.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${target.id}`).catch(() => {});
  return { snapshot, layout, exceptions, blocked, substituted };
}

function fullRenderFailures({ snapshot, layout, exceptions }) {
  const failures = [];
  if (!snapshot) return ["the page state could not be read"];
  const { ds, plantuml, figures } = snapshot;
  if (!ds?.ready) failures.push(`design system is not ready${ds?.error ? `: ${ds.error}` : ""}`);
  if (!plantuml?.completed) failures.push("diagram rendering did not complete");
  if (exceptions.length) failures.push(`uncaught exceptions: ${exceptions.join(" | ")}`);
  if (snapshot.unknown) failures.push(`${snapshot.unknown} unknown component element(s)`);
  const counts = [snapshot.fenced, plantuml?.expected, plantuml?.rendered, figures.length];
  if (new Set(counts).size !== 1) failures.push(`diagram counts differ (fenced, expected, rendered, figures) = ${counts.join(", ")}`);
  if (plantuml?.errors?.length) failures.push(`diagram errors: ${plantuml.errors.join(" | ")}`);
  for (const figure of figures) {
    if (figure.status !== "success" || figure.svg !== 1) failures.push(`figure ${figure.id} is ${figure.status} with ${figure.svg} svg ${figure.error}`);
  }
  if (layout.scrollWidth > layout.width + 1) failures.push(`page overflows at 390px (scrollWidth ${layout.scrollWidth}px)`);
  return failures;
}

function expectVendor(result, plantuml, hljs) {
  const vendor = result.snapshot?.ds?.vendor ?? {};
  const failures = [];
  if (vendor.plantuml !== plantuml) failures.push(`PlantUML loaded from ${vendor.plantuml}, expected ${plantuml}`);
  if (hljs !== undefined && vendor.hljs !== hljs) failures.push(`highlight.js loaded from ${vendor.hljs}, expected ${hljs}`);
  return failures;
}

/* ---------- scenarios ---------- */

async function runScenario(name, context) {
  const { fixture, origin } = context;
  const fileUrl = (root, link, id) => pathToFileURL(join(root, link ? "spec-dock/initiatives/00000-00999" : SCOPE_DIR, id, "explanation.html")).href;
  const httpUrl = id => `${origin}/${SCOPE_DIR}/${id}/explanation.html`;
  const check = options => checkPage({ ...context, settle: 5000, ...options });
  if (name === "canonical-file" || name === "initiatives-file") {
    const result = await check({ url: fileUrl(fixture.repo, name === "initiatives-file", "iss-00001"), cdnFromPackage: true });
    return { result, failures: [...fullRenderFailures(result), ...expectVendor(result, "cdn", "cdn")] };
  }
  if (name === "local-http") {
    const result = await check({ url: httpUrl("iss-00002"), cdnFromPackage: false });
    return { result, failures: [...fullRenderFailures(result), ...expectVendor(result, "local", "local")] };
  }
  if (name === "local-fallback") {
    const result = await check({ url: httpUrl("iss-00003"), cdnFromPackage: true });
    return { result, failures: [...fullRenderFailures(result), ...expectVendor(result, "cdn", "cdn")] };
  }
  if (name === "offline-standalone") {
    const result = await check({ url: fileUrl(fixture.repo, false, "iss-00001"), cdnFromPackage: false, settle: 1000 });
    const { snapshot } = result;
    const failures = [];
    if (!snapshot?.ds?.ready) failures.push("the body did not render without the network");
    if (result.exceptions.length) failures.push(`uncaught exceptions: ${result.exceptions.join(" | ")}`);
    if (!snapshot?.plantuml?.completed || snapshot.plantuml.rendered !== 0) failures.push("diagram state should complete with nothing rendered");
    if (!snapshot?.figures?.length || snapshot.figures.some(f => f.status !== "error" || !f.error)) failures.push("each diagram should show why it could not load");
    if (!result.blocked.some(u => u.startsWith("https://unpkg.com/@plantuml/core@"))) failures.push("the CDN request was not attempted");
    return { result, failures };
  }
  if (name === "missing-marked") {
    const result = await check({ url: fileUrl(fixture.broken, false, "iss-00001"), cdnFromPackage: false, settle: 0 });
    const { snapshot } = result;
    const failures = [];
    if (snapshot?.ds?.ready !== false) failures.push("__dsState.ready should stay false");
    if (!snapshot?.ds?.error) failures.push("__dsState.error should explain the failure");
    if (!snapshot?.fatal?.includes("installation update")) failures.push("the page should tell the reader to run installation update");
    if (result.exceptions.length) failures.push(`uncaught exceptions: ${result.exceptions.join(" | ")}`);
    return { result, failures };
  }
  throw new CheckError(`unknown scenario ${name}`);
}

function summary(result) {
  const s = result.snapshot ?? {};
  return {
    ready: s.ds?.ready ?? null,
    error: s.ds?.error ?? null,
    vendor: s.ds?.vendor ?? null,
    plantuml: s.plantuml ? { expected: s.plantuml.expected, rendered: s.plantuml.rendered, errors: s.plantuml.errors.length } : null,
    fenced: s.fenced ?? null,
    layout: result.layout,
    exceptions: result.exceptions.length,
    blocked: result.blocked.length,
    substituted: result.substituted.length,
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const chromePath = await findChrome(options.chrome);
  const vendor = await loadVendor();
  const base = await mkdtemp(join(tmpdir(), "spec-dock-explanation-check-"));
  let chrome = null;
  let server = null;
  let ok = true;
  try {
    const fixture = await buildFixture(base, options.designSystem);
    const started = await startServer(fixture.repo, vendor);
    server = started.server;
    chrome = await launchChrome(chromePath, join(base, "profile"));
    const context = { port: chrome.port, vendor, origin: started.origin, fixture, timeout: options.timeout };
    const runs = options.file
      ? [["file", () => checkPage({ ...context, origin: null, url: pathToFileURL(options.file).href, cdnFromPackage: options.cdnFromPackage, settle: 5000 })
        .then(result => ({ result, failures: fullRenderFailures(result) }))]]
      : options.scenarios.map(name => [name, () => runScenario(name, context)]);
    for (const [name, run] of runs) {
      const { result, failures } = await run();
      ok &&= failures.length === 0;
      console.log(JSON.stringify({ scenario: name, passed: failures.length === 0, failures, ...summary(result) }));
    }
  } finally {
    if (chrome) await closeChrome(chrome.child, chrome.port);
    if (server) await new Promise(r => server.close(r));
    await rm(base, { recursive: true, force: true });
  }
  console.log(ok ? "VALIDATED" : "FAILED");
  process.exitCode = ok ? 0 : 1;
}

main().catch(error => {
  console.error(error instanceof CheckError ? error.message : error);
  console.log("FAILED");
  process.exitCode = 2;
});
