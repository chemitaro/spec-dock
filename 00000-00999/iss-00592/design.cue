package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"印とボタンは orca-web の部品をそのまま使い、SpecDock は置き場と描くときだけを決める",
	"置き場の HTML は Scope の ID だけで決まり、要約によらない（描き直しの比べと、今の画面の差分の扱いを崩さない）",
	"何を描くかの決め方（置き場ごとの worktree、作り直すかどうか、ボタンのねらい）は DOM を触らない純粋な関数にし、node のテストで確かめる",
	"要約の読みは iss-00591 の `ctx.orca` の1つだけを使う",
]

current: """
	- `core/orca.js` の `createOrca` が `ctx.orca` を作り、`status()`、`summary()`、`marks()`（読んだ部品の module。`renderAgentMarks`、`buildMarks` を持つ）、`origin`、`subscribe(fn)`、`forScope(structure, id)` を公開する（iss-00591 D-05）。どの画面もまだ使っていない。
	- 構造の図（`views/graph.js`）：`render` が構造の署名（revision、表示の選び、幅など）が変わったときだけ `buildWorld` で `.gx-world` の `innerHTML` を作り直し、毎回 `paint()` と `renderPanel()` を呼ぶ。箱は `boxHtml`（Issue の箱と、木の表示の枠の箱 `tframe`。下の段 `.gx-marks`）、枠は `frameHtml`（見出し `.gx-fh` と進み具合の行 `.gx-fm`）。箱と枠の見出しを押すと `onClick` が `select(id)` で選び、`renderPanel` が共有の横の欄を開く。
	- ボード（`views/board.js`）：`renderPage` が `root` の中のページを作り直し、札は `views/_shared/parts.js` の `card`（`<a class="sd-card" data-nav>`。下の段 `.sd-card__meta` は印があるときだけ）。札の素の左クリックは `onCardClick` が選びに変える。`card` は詳しい画面のタブの子の一覧でも使われる。
	- 横の欄（`views/_shared/panel.js` の `createScopePanel`）：`build()` が欄の骨（`.pn-grab`、`.pn-top`、`.pn-tabs`、`.pn-body`、`.pn-foot`）を作り、`draw()` が描くたびに `.pn-top` の `innerHTML`（見出しの行 `.pn-head`：状態の札、マージの札、閉じる。表紙 `.pn-cover`）を作り直す。中身（`.pn-body`）だけは HTML が同じなら書き換えない。人の選んだタブは `userTab` に持ち、`pickTab(userTab, TAB_KEYS, details)` が並びにないキーなら既定のタブを選ぶ。
	- 構造の図は、片付けの候補の一覧を同じ aside に `innerHTML` で描き、そのあと横の欄は `build()` から作り直す。
	"""

target: """
	- 新しい `views/_shared/orca_logic.js`（純粋）が、置き場ごとに描く worktree、作り直すかどうか、ボタンのねらいを決める。
	- 新しい `views/_shared/orca_marks.js`（DOM）が、root の中の置き場に印を描く `paintOrcaMarks` と、ボタンの置き場を保つ `createOpenButton` を持つ。
	- 構造の図、ボード、横の欄は、置き場の空の要素を HTML に持ち、自分の描き直しの直後と `ctx.orca.subscribe` の知らせで `paintOrcaMarks` を呼ぶ。横の欄は、見出しの行を作り直さない骨に持ち、ボタンの置き場をそこに置く。
	"""

design: {
	"D-01": {
		title:     "決め方の純粋な部品：views/_shared/orca_logic.js"
		satisfies: ["R-01", "R-02", "R-04", "F-01", "F-02", "F-03", "F-04"]
		text: """
			DOM と時刻を触らない関数だけを置く（`core/orca_match.js` の `mergedWorktree` を import してよい）。

			- `slotWorktree(orca, structure, scopeId)` → 描く worktree か null。`orca` が null、`orca.status()` が ok でない、`forScope` が空なら null。そうでなければ `mergedWorktree(orca.forScope(structure, scopeId))`。
			- `marksKey(built)` → 文字列。部品の `buildMarks(worktree, {now, max})` の結果（`{marks, overflow}`）を `JSON.stringify` した値。null（描かない）は空の文字列。印の形が同じなら同じ値になり、経過の表記（`now`→`1m`）や状態や数が変われば変わる。
			- `openTarget({orca, structure, scopeId, embed, theme})` → `{key, worktreeId}`。
			  - 置けるのは：`orca` があり、`orca.status()` が ok、`embed` が真でない、`forScope` の最初の worktree の `id` が空でない文字列。
			  - 置けるとき `worktreeId` はその `id`、`key` は `${scopeId}|${worktreeId}|${theme}`。置けないとき `worktreeId` は null、`key` は空の文字列。
			- `themeOf(doc, matchMedia)` → `"light" | "dark"`。`doc.documentElement.dataset.theme` が light か dark ならそれ、ほかは `matchMedia("(prefers-color-scheme: dark)").matches` で dark か light。
			"""
	}
	"D-02": {
		title:     "印の置き場と描き方：views/_shared/orca_marks.js の paintOrcaMarks"
		satisfies: ["R-01", "R-02", "F-01", "F-02", "F-04"]
		text: """
			置き場は空の `<span class="sd-orca" data-orca-scope="<ID>" data-orca-max="<N>"></span>`（ID は `esc` を通す）。HTML の文字列は Scope の ID と max だけで決まる。

			`paintOrcaMarks(root, ctx, structure)`：
			- `ctx.orca?.marks()` を部品とする。root の中の `[data-orca-scope]` の置き場ごとに、`slotWorktree` で worktree を求め、worktree があり部品があれば `built = module.buildMarks(worktree, {now, max})`（`now` は呼び出しのはじめの `Date.now()` の1つの値）、なければ null。
			- `key = marksKey(built)` を、置き場ごとの覚え（`WeakMap<Element, string>`）と比べ、同じなら何もしない。
			- 違えば：key が空なら `slot.replaceChildren()`。そうでなければ `module.renderAgentMarks(slot, worktree, {size: "sm", max, now})`（同じ `now`。`onSelect` は渡さない）。覚えを key にする。
			- 置き場ごとの処理は try/catch で囲み、例外の置き場は空にして覚えを空の文字列にする（F-01）。
			- 新しく作られた置き場は覚えがないので、最初の呼び出しで必ず描く（R-02 の「同じ処理の中で描き直す」）。

			置き場の CSS は、構造の図、ボード、横の欄のすべてに効く1か所に置く：シェルの `app.css`（画面の範囲の入れ子の外。`views/_shared/parts.css` は全体が board・scope・overview・todos・`.sd-pn` の範囲の入れ子で、構造の図の `.gx-world` に効かないため使わない）。`.sd-orca { display: inline-flex; flex: none; margin-left: auto; }`、`.sd-orca:empty { display: none; }`（空の置き場は flex の子として消え、`.gx-marks` の gap の幅も取らない）。印の色、形、大きさの指定は置かない（部品の `agent-marks.css` のまま）。

			max の値：Issue の箱と木の表示の枠の箱は 2、枠の見出しは 3、ボードの札と横の欄の見出しは 4。実装の担当が写しで確かめ、箱からはみ出すときは小さくしてよい（記録する）。
			"""
	}
	"D-03": {
		title:     "構造の図とボードへの組み込みと、印を押したとき"
		satisfies: ["R-01", "R-02", "R-03"]
		text: """
			構造の図（`views/graph.js`）：
			- `boxHtml` の `.gx-marks` の末尾に置き場（max 2）を足す。`frameHtml` の `.gx-fh` の末尾に置き場（max 3）を足す。`SIZE` と配置の計算は変えない。
			- `render` の終わり（`paint()` と `renderPanel()` の後）で `paintOrcaMarks(V.el.world, V.ctx, V.data)` と、横の欄の見出しの印（D-04）を描く。
			- `mount` で `ctx.orca` を受けたとき（最初の `render`）に `ctx.orca.subscribe` で知らせを受け、知らせで world と横の欄の印を描き直す（構造は `V.data`）。`dispose` で外す。`ctx.orca` が変わったら外して付け直す。
			- `onClick`（と `onTap`）：押した要素が `.sd-orca` の中なら、箱や枠を選ぶ今の処理に加えて、横の欄に `preferTab("agents")` を伝える（D-04）。

			ボード（`views/board.js` と `parts.js` の `card`）：
			- `card(scope, ctx, {parent, orca})` に任意の `orca`（真なら置き場を足す）を足す。`orca` が真のとき、下の段 `.sd-card__meta` を必ず出し、その末尾に置き場（max 4）を置く。下の段にほかの印がなく置き場が空なら、下の段を出さない（CSS `.sd-card__meta:not(:has(> :not(.sd-orca:empty)))` で `display: none`）。詳しい画面のタブの子の一覧の札は `orca` を渡さない（今のまま）。
			- ボードの `renderPage` の後で `paintOrcaMarks(root のページ, ctx, ctx.data)` と横の欄の印を描く。知らせの受け方は構造の図と同じ。
			- `onCardClick`：押した要素が `.sd-orca` の中なら、選びに加えて `preferTab("agents")` を伝える。修飾つきの押しは今のまま（札の普通のリンク）。
			"""
	}
	"D-04": {
		title:     "横の欄の見出し：作り直さない見出しの行、印、Orca で開く"
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-02", "F-03"]
		text: """
			`createScopePanel` の `build()` が、`.pn-top` の中に作り直さない見出しの行を作る：
			`<div class="pn-head"><span class="pn-hl"></span><span class="pn-orca"></span><button class="iconbtn pn-close" data-pn-act="close" …></button></div><div class="pn-cover"></div>`（`.pn-cover` は今と同じく `.pn-top` の直接の子のまま。包みを足さない）。
			- `.pn-hl` の中身（状態の札、マージの札、印の置き場（max 4））と `.pn-cover` の中身は、`draw()` のたびに HTML を作り、前と同じなら書き換えない（R-02。覚えは `build()` で捨てる）。
			- `.pn-hl` は `display: contents`（今の `.pn-head` の flex の並びと、スマホの全画面の規則 `.pn-head { display: contents }` の並びを保つ）。
			- 閉じるの位置：今の `.sd-pn .pn-head .iconbtn { margin-left: auto }` を残す（ボタンがないとき、閉じるは今と同じく右端）。ボタンがあるときだけ `.pn-orca:not(:empty) { margin-left: auto }` と `.pn-orca:not(:empty) + .pn-close { margin-left: 0 }` で、ボタンを閉じるの左の右端に寄せる。`.pn-orca:empty { display: none }`。
			- 高さ：`.pn-orca` は `display: inline-flex; align-items: center; height: 24px; flex: none`（orca-web の sm のボタンの高さ 24px。2026-11-14 の統括の連絡）で、見出しの行の高さは今のまま（閉じるの 32px）。ボタンの幅は部品に任せ、SpecDock は幅を決めない（`data-width` を付けず、文字の長さに頼る配置にしない）。
			- スマホの全画面（`data-snap="full"`）では、今の規則（`.pn-merge` などを隠す、`.pn-cover` の order と flex、閉じるの order 3）のまま。`.pn-orca` は閉じるの左（order 3 の前）に来るよう、実装の担当が写しで確かめる。

			`draw()` の終わりに `paintOrcaMarks(parts.top, ctx, ctx.data)` と `openButton.update({orca: ctx.orca, structure: ctx.data, scopeId, embed: ctx.embed, theme})`。

			`createOpenButton(slot, {doc})`（`orca_marks.js`）：`update(input)` が `openTarget` で `{key, worktreeId}` を求め、前の key と同じなら何もしない。違えば `slot.replaceChildren()`、worktreeId があれば `doc.createElement("script")` に `src = <origin>/embed/open-button.js`、`dataset.worktree`、`dataset.theme`、`dataset.size = "sm"` を付けて（`data-width` と `data-label` は付けない。幅とラベルは部品の既定） slot に足す（`innerHTML` ではスクリプトが動かないため）。`reset()` は覚えを捨てて slot を空にする。
			- `build()` が走り直したら、新しい slot で `createOpenButton` を作り直す（覚えも捨てる。Epic のレビューの P2）。`hide()` で `reset()`。
			- 明暗の変化：横の欄は `matchMedia("(prefers-color-scheme: dark)")` の change と、`document.documentElement` の `data-theme` の属性の変化（MutationObserver）で、開いているときに `openButton.update` を呼び直す。`destroy()` で外す。
			- 要約の知らせ：構造の図とボードが知らせを受けたとき、横の欄に `refreshOrca()`（`paintOrcaMarks(parts.top, …)` と `openButton.update`）を呼ぶ。

			`preferTab(key)`：`TAB_KEYS` に key があれば `userTab = key`（人が選んだタブとして覚える）。なければ何もしない。開いていれば描き直す。構造の図とボードは、選びの後に呼ぶ（選びで欄が描かれた後でも、前でもよい）。
			"""
	}
	"D-05": {
		title:     "配る文書"
		satisfies: ["R-05"]
		text: """
			`src/spec_dock/assets/spec_dock/docs/` の中で、ダッシュボードの利用者の設定（`config.json` の `dashboard`・`todo` の節）を説明している文書の、その節の隣に `orca_web` の節を足す（どの文書かは今の文書の構成で決める。`reference_cli.md` の設定の節が第一の候補）。書くこと：
			- 書き方 `{"orca_web": {"enabled": true, "port": 8791}}`、既定（enabled true、port 8791）、設定はサーバーを起動し直さずに次の要求から効くこと、壊れたときは連携しない側に倒れ `config_problems` に出ること、port がダッシュボード自身のポートと同じなら無効。
			- orca-web は同じ PC で動き、画面を開いた Host の名前（127.0.0.1 か Tailscale の IP）の port を読むこと。orca-web の `ORCA_WEB_READ_ORIGINS` に SpecDock のオリジン（`http://127.0.0.1:47800` と Tailscale の IP の同じポート）が要ること。`localhost` や MagicDNS の名前で開くと読めないこと。
			- 見え方：印を出す場所（構造の図の箱と枠、ボードの札、横の欄の見出し）、「Orca で開く」は横の欄の見出しだけで、幅 390px 以下と埋め込みの画面では出ないこと、届かないときは印もボタンも出ず、図とボードは今までどおり動くこと。
			例の IP は 127.0.0.1 と 192.0.2.x だけ。変えた配る文書と静的な資産の sha256 を `static-inventory.json` に合わせる（今の検査のとおり）。
			"""
	}
}

compatibility: """
	- サーバー、API、`core/orca.js`、`core/orca_match.js` は変えない。
	- 連携を切っている、または orca-web に届かないとき、置き場は空で幅を取らず、見た目は今と同じ。札の下の段は、ほかの印がなければ今と同じく出ない。
	- 横の欄の見出しの行の DOM は、`.pn-hl` の包みと `.pn-orca` が足される。`.pn-head` の中の状態の札、マージの札、閉じるのクラスと属性は今のまま（今のテストの目印を保つ）。
	- 共有のタブの並びは変えない（`preferTab` は並びにあるキーだけを選ぶ）。iss-00593 がタブを足すと、印を押したときにそのタブが開く。
	"""

risks: [
	"iss-00593 も `views/_shared/panel.js` を変える。PR の前に `origin/main` を取り込み、衝突を直してからテストとゲートをやり直す",
	"部品の `buildMarks` の結果の形が変わっても、比べの key が変わるだけで描きは部品のまま。部品が `buildMarks` を export しなくなれば、F-01 のとおり印が空になる（壊れない）",
	"構造の図の箱は狭い。max と置き場の CSS で収まらなければ、実装の担当が写しで max を小さくする",
	"orca-web の iss-00035（並行）が「Orca で開く」を小さなボタン（アイコンと Open、sm で高さ 24px、中身に合う既定の幅）に作り直す。SpecDock は幅を部品に任せるので、どちらの版でも置ける。実機の確かめは、そのときの orca-web の main の `dist/` で行い、版を report に書く",
]
