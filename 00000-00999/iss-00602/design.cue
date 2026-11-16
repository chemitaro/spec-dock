package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"印の数の上限を、置き場の HTML ではなく、描くときの worktree のエージェントの数から決める",
	"構造の図の配置は純粋な計算のまま、印の行の数だけを入力に足す。行の数は画面が描いた印から測る",
	"エージェントのタブの直しは、iss-00601 の案どおり小さく、各点を node のテストで再現してから直す",
]

current: """
	- 置き場：`parts.js` の `orcaSlot(id, max)` が `<span class="sd-orca" data-orca-scope data-orca-max>`。`orca_marks.js` の `paintOrcaMarks` が `Number(slot.dataset.orcaMax)` を部品の `max` に渡す。
	- CSS：`app.css` の `.sd-orca { display: inline-flex; flex: none; margin-left: auto; }`。構造の図の箱の `.gx-marks` は折り返さない flex の行。入れ子の枠の見出し `.gx-fh` は flex の行で、題名が `flex: 1`。横の欄の見出し `.pn-head` は flex の行（`.pn-hl` は `display: contents`）。ボードの札の `.sd-card__meta` は折り返す flex の行。
	- 配置：`layout.js` の `boxBlock`、`tree` の `tbox`、`frameBlock` の `head` が、`SIZE` と線の口の分（`grow`）だけで高さを決める。`graph.js` の `render` は、構造の版・選び・幅・高さなどの鍵（`sig`）が変わったときだけ `buildWorld`（`routeLayout`）をやり直し、最後に `paintOrca` で印を描く。
	- エージェントのタブ：`agentsState` の `wanted = env.param("agent") ?? mem.last`。`pickAgent` は wanted が agents にいれば remember null。帯の捕捉の聞き手は修飾キーを見ずに `forgetGone`。`scopeAgents` は `agents` が並びでない worktree を数えずに飛ばす。欄の足は `params.get("agent") ?? null`。`graph.js` の `onTap` は、スマホで選んだ箱の2回目の押しを印の判定より先に見る。
	"""

target: """
	- 置き場は `orcaSlot(id)`（max なし）。`paintOrcaMarks` は worktree のエージェントの数を max に渡し、部品は全員の印を描く。
	- 置き場は縮み、部品の `.orca-marks` が置き場の中で折り返す。
	- 構造の図は、描いた後に置き場ごとの印の行の数を測り、2行以上の Scope の行の数を `routeLayout` の options の `orcaRows` に渡して配置し直す。配置は箱の高さと枠の見出しの高さに (行 − 1) × 18 を足す。
	- エージェントのタブの5点を直す（D-07〜D-10）。
	"""

design: {
	"D-01": {
		title: "置き場は max を持たず、描くときに全員の数を部品に渡す"
		text: """
			- `parts.js`：`orcaSlot(id)` は `<span class="sd-orca" data-orca-scope="<esc(id)>"></span>`（`data-orca-max` を消す）。呼ぶ側（`graph.js` の `boxHtml` の2か所と `frameHtml`、`panel.js` の `header`、`parts.js` の `card`）は id だけを渡す。
			- `orca_logic.js` に純粋な `markMax(worktree)` を足す：`Array.isArray(worktree?.agents) ? Math.max(1, worktree.agents.length) : 1`。部品の `max` は1以上の整数でないと4とみなされるので、0人でも1を渡す。
			- `orca_marks.js` の `paintOrcaMarks`：`max = markMax(worktree)` を `buildMarks` と `renderAgentMarks` の両方に渡す。比べの鍵（`marksKey`）、try と空の扱いは今のまま。`slotWorktree` が返す合わせた worktree（`mergedWorktree`）の agents は、複数の worktree の agents を連ねた並びなので、合わせた数が max になる。
			- エージェントのタブの帯の1人ずつの印（`agents_tab.js` の `paintMarks`、max 1）は変えない。
			"""
		satisfies: ["R-01", "F-03"]
	}
	"D-02": {
		title: "置き場が縮み、印は置き場の中で折り返す（CSS）"
		text: """
			- `app.css`：`.sd-orca { display: inline-flex; flex: 0 1 auto; min-width: 0; max-width: 100%; margin-left: auto; }`（`:empty` で消える規則は今のまま）。置き場は行の残りの幅まで縮み、中の部品の `.orca-marks`（orca-web の CSS が `flex-wrap: wrap; max-width: 100%` を持つ）が折り返す。部品は min-content（いちばん広い印1つ）より縮まない。
			- `graph.css`：`.gx .gx-fh .sd-orca { max-width: 50%; }`。入れ子の枠の見出しの題名は `flex: 1`（基準の幅0）なので、置き場に上限がないと題名が消える。
			- 構造の図の箱の `.gx-marks` は折り返さないまま（ほかの印の並びを変えない）。置き場が残りの幅まで縮み、1行目の印はほかの印と同じ行に、2行目以降はその下に並ぶ。`.gx-marks` の `align-items: center` のため、置き場が高くなると、ほかの印は置き場の高さの中ほどに来る。気になれば実機の写しで統括に問う。
			- 横の欄の見出しとボードの札は、上の `.sd-orca` の規則だけで折り返す（欄・札の高さはふつうの流れで伸びる）。
			- SpecDock の CSS に `.orca-` の選びを書かない（iss-00592 のテストの約束）。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "配置は印の行の数を受け、箱と枠の見出しの高さを決める（layout.js）"
		text: """
			- `layout.js` に `export const ORCA_ROW = 18;`（orca-web の小さい印の高さ 16 と行の間 2）。`SIZE` は変えない。
			- `layout(scopes, cleanup, options, gaps)` と `routeLayout` の options に `orcaRows`（Scope の id → 印の行の数。オブジェクト）を足す。ない、オブジェクトでない、値が2以上の整数でないときは、その Scope の足しは0。
			- 足しの高さ `orcaExtra(ctx, s) = (rows ≥ 2 ? (rows − 1) × ORCA_ROW : 0)`：`boxBlock` の `h`、`tree` の `tbox` の `h`（Issue の箱と木の枠の箱の両方）、`frameBlock` の `head`（入れ子の枠。compact でもそうでなくても）に、今の `SIZE` と `grow` の和へ足す。幅は足さない。
			- `layout` が中で呼ぶ `layout(scopes, cleanup, options, {})`（広げの前の棚）にも同じ options が渡るので、棚も同じ高さで決まる。`graphInput`・`gapFor`・`routeLayout` の広げは、そのまま箱と枠の新しい座標を使う。
			- `options.orcaRows` が空のときの結果は、今の結果と同じ（足しがすべて0）。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "印の行の数の測り（純粋な部分）"
		text: """
			- `orca_logic.js` に `markRows(tops)`：置き場の中の `.orca-mark` の `offsetTop`（px）の並びから行の数を返す。空なら0。数でない値を除いて小さい順に並べ、前の行の上端より 4px を超えて下の値で新しい行と数える（行の間は 18px、同じ行の印の上端は同じ）。
			- `rowsKey(rows)`：`orcaRows` のオブジェクトから、値が2以上の項目だけを id の順に `id:n` で連ね `,` で区切った文字列（空なら ""）。配置し直すかの比べに使う。
			"""
		satisfies: ["R-03", "F-01", "F-02"]
	}
	"D-05": {
		title: "構造の図は、描いた印の行を測り、行の数が変わったときだけ配置し直す（graph.js）"
		text: """
			- 状態に `V.orcaRows = {}`（2行以上の Scope だけ）、`V.orcaKey = ""`、`V.orcaPass = 0` を足す。`dispose` で `{}`・`""`・0 に戻す。
			- `render` の `sig` に `V.orcaKey` を足し、`buildWorld` は `routeLayout` の options に `orcaRows: V.orcaRows` を渡す。
			- `measureOrcaRows()`：`V.el.world` の `.gx-box[data-id]` は `:scope > .gx-marks > .sd-orca`、`.gx-frame[data-id]` は `:scope > .gx-fh > .sd-orca` を置き場とする。置き場が描かれていない（`offsetParent` が null）なら、前の `V.orcaRows[id]` を保つ。そうでなければ `markRows(置き場の .orca-mark の offsetTop)` を測り、2以上なら記す。置き場ごとに try で囲み、例外の置き場は前の値を保つ（F-01）。返すのは新しい `orcaRows`。
			- `paintOrca()`：今の `paintOrcaMarks` と `V.pn?.refreshOrca()` の後で `measureOrcaRows()` を呼び、`rowsKey` が `V.orcaKey` と違い、かつ `V.orcaPass < 2` なら、`V.orcaRows`・`V.orcaKey` を書き、`V.orcaPass` を1足して `render(V.root, V.ctx)` を呼び、終わったら1引く（F-02。`render` は `sig` が変わったので `buildWorld` をやり直し、最後の `paintOrca` で測り直す。行の数は箱の高さによらないので、2回目の測りは同じ鍵になる）。鍵が同じなら何もしない（経過の表記だけの変化では配置し直さない）。
			- `whenStyled` の終わり（画面の CSS が読めた後の `relayout` と `initialView` の後）でも `paintOrca()` を呼び、CSS の前に測った行を直す。
			- `edgeAudit` の返り値に `overflow` を足す：`.gx-box` のうち、置き場の下端（`getBoundingClientRect` を拡大率で戻した値）が箱の下端を 1px を超えて越える数。入れ子の枠の見出しは、今の `edgeAudit` が `.gx-fm` の下端から障害物を測るので、そのまま線の確かめに入る。
			"""
		satisfies: ["R-03", "F-01", "F-02", "F-03"]
	}
	"D-06": {
		title: "スマホの構造の図で、印の押しを2回目の押しより先に見る（graph.js の onTap）"
		text: """
			`onTap` の、`hit` と `id` を決めた後を次の順にする：
			1. `target.closest(".sd-orca")` なら、`V.sel !== id` のとき `select(id)`、続けて `V.pn?.preferTab("agents")` を呼んで終わる。
			2. `isPhone() && V.sel === id` なら `goDetail(id)`。
			3. `V.sel !== id` なら `select(id)`。
			今の静的なテストの「`select(id)` が `preferTab` より前」は成り立つ。
			"""
		satisfies: ["R-06"]
	}
	"D-07": {
		title: "覚えから開いた相手も agent として書く（agents_tab.js）"
		text: """
			- `agentsState`：`const asked = env.param("agent")`、`wanted = asked ?? mem.last`、state に `fromLast: asked == null && mem.last != null` を足す。
			- `agentsTab`：`const remember = pick.remember ?? (state.fromLast && pick.selected ? pick.selected.id : null)`、`if (remember) env.keep("agent", remember)`。いなくなった last（覚えの gone にある）は、今の pickAgent が `gone:<id>` を remember に返すので、その値が先（F-04）。
			- 詳しい画面の `keep` は `ctx.replaceParam`（履歴を増やさず `state.route` も書き換える）なので、その後の帯の今の相手の押しは `navigate` の比べで agent が同じになり、`dropAgentFrames` を呼ばない。欄の `keep` は欄の Map に書き、足のリンクにも入る。
			- 1人だけのとき（今の規則4の remember）と、問い合わせに agent があるとき（remember null、fromLast false）は今のまま。
			"""
		satisfies: ["R-04", "F-04"]
	}
	"D-08": {
		title: "欄の足のリンクが覚えを持つ（agents_logic.js、panel.js）"
		text: """
			- `agents_logic.js` に純粋な `lastChoice(mem, scopeId)`：`mem.scopeId !== scopeId` なら null（F-05）。`mem.last` があれば、`mem.gone` にあれば `gone:<last>`、なければ `<last>`。`mem.last` がなく `mem.gone` が空でなければ、最初に覚えた id の `gone:<id>`。ほかは null。
			- `panel.js` の `draw` の足：`withParam(..., "agent", params.get("agent") ?? lastChoice(mem, scope.id))`（`mem` は `agents_tab.js` の export）。足は中身を描いた後に作るので、同じ描きで覚えた last が入る。
			"""
		satisfies: ["R-05", "F-04", "F-05"]
	}
	"D-09": {
		title: "修飾キーのない主ボタンの押しだけが覚えを変える（agents_tab.js）"
		text: """
			`paintAgentList` の捕捉の段の聞き手：`if (item && event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) forgetGone(mem, item.dataset.agentPick)`。既定の動きは止めない（今のまま）。この判定は `panel.js` の `plainClick` と `app.js` の `interceptLinks` と同じ。iss-00593 の D-04 の「修飾キーの有無によらず」をここで改める。
			"""
		satisfies: ["R-07"]
	}
	"D-10": {
		title: "agents が並びでない worktree を形の違いに数える（agents_logic.js）"
		text: """
			`scopeAgents`：worktree がオブジェクトでなければ今のまま飛ばす。オブジェクトで `agents` が並びでなければ（欠け、null を含む）`invalid += 1` として次へ（id がないので `invalidIds` は変えない）。すると使える agents がなければ `agentsVisibility` の `noneUsable` で理由 shape になり、`agentsState` は覚えに足さない。
			"""
		satisfies: ["R-08"]
	}
	"D-11": {
		title: "配る文書（reference_cli.md）"
		text: """
			- 連携の節の「見え方」に：印はその worktree のエージェントを1人1つですべて出し（まとめない）、並びと経過の表記は orca-web の部品のとおり。入りきらなければ置き場の中で折り返し、構造の図の箱と枠の見出しは折り返した行の分だけ高くなる（幅は変わらない）。
			- エージェントのタブの節の「選び」と「いなくなったとき」に：欄の足の「詳しい画面」と「新しいタブで開く」は欄の今の選び（なければ同じ Scope の最後に開いた相手、いなくなっていれば `gone:<id>`）を持つ。修飾キーつきの押しで新しいタブに開いても、元の画面の覚えは変わらない。
			- 知らせの表の `orca-shape` の意味に：worktree の `agents` が並びでないときも形の違いに数える。
			- static-inventory.json の reference_cli.md の sha256 を合わせる。
			"""
		satisfies: ["R-09"]
	}
}

seams: """
	- D-01、D-04、D-08、D-10：node で純粋な関数を呼ぶ（`test_dashboard_orca_logic_js.py`、`test_dashboard_agents_logic_js.py`）。`paintOrcaMarks` は偽の置き場と偽の部品（渡された max を記す）で呼ぶ（`test_dashboard_orca_marks_js.py`）。
	- D-03：`tests/js/dashboard_graph_check.mjs` と `tests/unit/presentation/test_dashboard_graph_js.py` に、`orcaRows` を渡す確かめ（箱と枠の高さ、幅、行0・1で同じ結果、代表の構造での audit の0）。
	- D-07、D-09：`test_dashboard_agents_tab_js.py` の偽の env と偽の root（keep の呼び、捕捉の聞き手の修飾キー）。
	- D-08：`test_dashboard_orca_views_js.py` の欄の偽の DOM（PANEL_DOM）で、足の HTML の agent。
	- D-02、D-05、D-06：静的な目印（CSS の規則、`render` の sig と `paintOrca` の測りと上限、`onTap` の順）と、実機の写しと `specdockEdgeAudit()`（overflow を含む）。
	- D-11：`test_issue593_agents_docs.py` に足すか、この Issue のテストのファイル。
	"""

compatibility: "置き場の HTML から `data-orca-max` が消える（画面の中だけの約束で、外の利用者はない）。`routeLayout` の options の `orcaRows` は省けて、省けば今と同じ配置。エージェントのタブの選びは、覚えからの選びを問い合わせに書くようになる（履歴は増えない）。"

risks: [
	"構造の図の箱の `.gx-marks` にほかの印が多いと、置き場が印1つより狭くなり、印が1列に縦に並んで箱が高くなる、または右にはみ出す。実機の写しで確かめ、はみ出しの数を edgeAudit の overflow で見る",
	"画面の CSS やフォントの読み込みの前に測った行の数がずれる。whenStyled の後と、次の要約（10秒）で測り直す",
	"orca-web が小さい印の高さか行の間を変えると、ORCA_ROW の 18 と合わず、箱から印がはみ出すか余る。edgeAudit の overflow が見つける",
	"印の行の数が変わるたびに線の計算をやり直す。大きな構造（250 の Scope）では1回 1 秒ほどかかりうるが、行の数が変わるのはエージェントの増減のときだけ",
]
