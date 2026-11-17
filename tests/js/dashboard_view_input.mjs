// The graphs' wheel and key input as pure computation (iss-00655 D-01 to D-03). Run by
// tests/unit/presentation/test_dashboard_view_input.py:
//   node dashboard_view_input.mjs <assets/dashboard directory> <request.json>
// request.json:
//   kinds: [event, …]                   -> wheelKind of each
//   actions: [[event, last, now, page]]  -> wheelAction of each
//   keys: [event, …]                    -> keyAction of each
//   order: [event, …]                   -> the names wheelKind and wheelAction read from each, in order
//   owns: [target name, …]              -> ownsKey of a keydown whose target is that element of a fixed page
// Always: WHEEL and KEYS. Prints one JSON object; the Python test asserts on it.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const { Element, install } = await import(pathToFileURL(path.join(path.dirname(new URL(import.meta.url).pathname), "fake_dom.mjs")).href);
const M = await import(pathToFileURL(path.join(assets, "views/graph/view_input.js")).href);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = { WHEEL: M.WHEEL, KEYS: M.KEYS };

if (request.kinds) out.kinds = request.kinds.map((e) => M.wheelKind(e));
if (request.actions) out.actions = request.actions.map(([e, last, now, page]) => M.wheelAction(e, last, now, page));
if (request.keys) out.keys = request.keys.map((e) => M.keyAction(e));

// a wheel event that records the names read from it (Firefox turns deltaMode to pixels once wheelDelta* is read)
const recording = (e, reads) => new Proxy(e, { get: (t, k) => (typeof k === "string" && reads.push(k), t[k]) });
if (request.order)
  out.order = request.order.map((e) => {
    const kind = [];
    const action = [];
    M.wheelKind(recording(e, kind));
    M.wheelAction(recording(e, action), null, 0, 1000);
    return { kind, action };
  });

if (request.owns) {
  install();
  const html = document.documentElement;
  const body = new Element("body");
  html.append(body);
  body.innerHTML =
    `<main id="view" tabindex="-1"><section class="gx">` +
    `<div class="gx-view" id="gxview" tabindex="0"><div class="gx-world">` +
    `<div class="box" id="box" role="button" tabindex="0"><span id="inbox">x</span></div>` +
    `<input id="v-input"><textarea id="v-textarea"></textarea><select id="v-select"></select>` +
    `<button id="v-button">b</button><a id="v-link" href="#x">l</a><a id="v-anchor">n</a>` +
    `<details><summary id="v-summary">s</summary></details><iframe id="v-iframe"></iframe>` +
    `<div contenteditable="true" id="v-editable"><span id="v-in-editable">e</span></div>` +
    `<div contenteditable="false"><div id="v-not-editable">f</div></div>` +
    `</div></div>` +
    `<div class="gx-bar" id="bar"><div class="gx-tools" id="tools"></div></div>` +
    `<aside class="panel" id="panel"><div id="in-panel">p</div></aside>` +
    `</section></main>`;
  const view = body.querySelector(".gx-view");
  const named = { html, body, main: body.querySelector("#view"), none: null };
  out.owns = Object.fromEntries(request.owns.map((name) => {
    const target = name in named ? named[name] : body.querySelector(`#${name}`);
    if (target === undefined || (target === null && name !== "none")) throw new Error(`no element ${name}`);
    return [name, M.ownsKey({ target }, view)];
  }));
}

process.stdout.write(JSON.stringify(out));
