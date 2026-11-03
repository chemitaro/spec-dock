// The screen slots (iss-00529 D-09). The shell imports this table and never the screens' insides.
//
// Each screen module exports:
//   export default {
//     id: "board",                 // the slot name; equals the route view
//     title: "ボード",             // used in the page title
//     icon: "table",               // an ICONS name of core/ui.js
//     styles: ["/assets/views/board.css"],  // optional CSS, loaded once when the screen is first shown
//     render(root, ctx) {},        // called on every data or route change; root is <main id="view">
//     dispose() {},                // optional; called before another screen takes root
//   };
//   ctx = {repository, route: {view, repository, scope, params, embed, path}, data (structure JSON),
//          scope (scope JSON on the detail screen), repositories, embed, navigate(path), href(path)}
//
// #531 (board, scope, overview) and #532 (graph, timeline) replace their own file (and add CSS) only.
import board from "./board.js";
import graph from "./graph.js";
import overview from "./overview.js";
import scope from "./scope.js";
import timeline from "./timeline.js";

export const VIEWS = { graph, board, timeline, scope, overview };
