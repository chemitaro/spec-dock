# Browser check for explanation documents

`explanation-check.mjs` checks, in a real headless Chrome with the network blocked, that thin explanation
documents render with the shipped design system (`src/spec_dock/assets/spec_dock/design-system/`) and the
diagram parts bundled in the package (`src/spec_dock/assets/vendor/`). It is a local, optional check
(Epic epic-00425 R-E4); it is not collected by pytest and does not run in CI.

Requirements: Node.js 22 or later (built-in `WebSocket` and `fetch`) and Chrome or Chromium.

```sh
node tests/browser/explanation-check.mjs                       # all scenarios
node tests/browser/explanation-check.mjs --scenario local-http # one scenario
node tests/browser/explanation-check.mjs --design-system spec-dock/design-system  # the dogfood copy
node tests/browser/explanation-check.mjs --file PATH/explanation.html --cdn-from-package
```

Every request that leaves the machine is blocked. Only `file:` URLs and the tool's own `127.0.0.1` server
pass. `--cdn-from-package` (and the scenarios marked below) answer requests to the pinned CDN URLs used by
`ds.js` with the bundled parts, so the standalone-file path is checked without the internet.

| Scenario | Opens | Diagram parts | Expected |
|---|---|---|---|
| `canonical-file` | `file:` under `spec-dock/.canonical/…` | CDN answered from the package | renders; parts from `cdn` |
| `initiatives-file` | `file:` under the `spec-dock/initiatives` link | same | renders |
| `local-http` | local server, page with `<meta name="ds-vendor-base" content="/vendor/">` | served at `/vendor/`; CDN blocked | renders; parts from `local` |
| `local-fallback` | local server, meta pointing to a missing place | CDN answered from the package | renders; parts from `cdn` |
| `offline-standalone` | `file:` | everything blocked | body renders; each diagram shows why it could not load |
| `missing-marked` | tree without `vendor/marked.umd.js` | everything blocked | `__dsState.ready` stays false; the page asks for `installation update` |

A rendering pass requires: `__dsState.ready` and `__plantumlDocumentState.completed`, no uncaught exception,
no `.ds-unknown`, equal counts of fenced `plantuml` blocks, expected, rendered, and figures with one SVG each,
no diagram error, and no horizontal overflow at 390px. Output is one JSON line per scenario and a final
`VALIDATED` or `FAILED`. Chrome is started with `--disable-features=MacAppCodeSignClone` and closed with CDP
`Browser.close`.
