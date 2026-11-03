// The embedding contract specdock.embed/v1 (Epic D-15; #527 P-1).
// Messages: {source: "specdock"|"host", v: 1, type, …}. The parent sends `hello` on every frame load;
// SpecDock answers `ready {repository, path, title, capabilities}` and then one `navigated` for the current
// screen, and later `navigated {path, title, scope}` on each move. The parent may send `navigate {path}` and
// `theme {scheme}`. Nothing is sent before `hello`; only the remembered origin is used, never "*".

const CAPABILITIES = ["navigate", "theme"];

export function createEmbedBridge({ getState, navigate, setTheme }) {
  let parentOrigin = null;
  let allowedHosts = null; // filled from /api/v1/repositories (server.embed_hosts)
  const pending = [];
  const framed = window.parent !== window;

  function originAllowed(origin) {
    try {
      const url = new URL(origin);
      return url.protocol === "http:" && /^\d+$/.test(url.port || "80") && allowedHosts.includes(url.hostname);
    } catch {
      return false;
    }
  }

  function send(type, payload) {
    if (!framed || !parentOrigin) return false;
    window.parent.postMessage({ source: "specdock", v: 1, type, ...payload }, parentOrigin);
    return true;
  }

  function navigated() {
    const state = getState();
    send("navigated", { path: state.path, title: document.title, scope: state.scope });
  }

  function accept(event) {
    const data = event.data;
    if (data.type === "hello") {
      if (parentOrigin === null) {
        if (!originAllowed(event.origin)) return;
        parentOrigin = event.origin;
      } else if (event.origin !== parentOrigin) {
        return;
      }
      const state = getState();
      send("ready", { repository: state.repository, path: state.path, title: document.title, capabilities: CAPABILITIES });
      navigated();
      return;
    }
    if (parentOrigin === null || event.origin !== parentOrigin) return;
    if (data.type === "navigate" && typeof data.path === "string" && data.path.startsWith("/")) navigate(data.path);
    else if (data.type === "theme" && ["light", "dark", "auto"].includes(data.scheme)) setTheme(data.scheme);
  }

  window.addEventListener("message", (event) => {
    if (!framed || event.source !== window.parent) return;
    const data = event.data;
    if (!data || typeof data !== "object" || data.source !== "host" || data.v !== 1) return;
    if (allowedHosts === null) pending.push(event);
    else accept(event);
  });

  return {
    setAllowedHosts(hosts) {
      allowedHosts = Array.isArray(hosts) ? hosts : [];
      pending.splice(0).forEach(accept);
    },
    navigated,
    get origin() {
      return parentOrigin;
    },
  };
}
