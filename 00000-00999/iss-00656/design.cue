package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"欄の見出しを『パンくずと今の ID の行』『題名』『（あれば）帯』にし、同じ情報を1回ずつにする",
	"帯を出すかどうかと帯の文を、DOM のない純粋な関数で決め、node のテストで確かめる",
	"枠を新しいタブで開く印を、SCOPE_TABS の行の1つの項目（`open`）にし、欄と詳しい画面が同じ口で置く",
	"見出しの札と印を、要約の更新で書き直さない今の仕組み（部分ごとの比べ）を保つ",
]

current: """
	- `panel.js` の `build()` は `.pn-top` に `<div class="pn-head"><span class="pn-hl"></span><span class="pn-orca"></span><button class="iconbtn pn-close">` と `<div class="pn-cover">` を置く。
	  `header(scope, byId)` が `{hl, cover}` を返し、`hl` は `stateChip`・`.pn-merge`（`mergeBadge`）・`orcaSlot(id, 4)`、`cover` は `.pn-kicker`（ID の札と `#番号・種類`）・`.pn-title`・`.pn-why`（`stateMark` と `reason.text`）・`.pn-idle`・`.pn-path`。`draw()` は `hl` と `cover` を、前と違うときだけ書く。
	- `.pn-tabs`（role tablist）に `put()` でタブのボタンを書く。中身は `.pn-body`。
	- `scope_tabs.js` の `frameBar(left, href)` が帯を返し、`explanationTab` は `frameBar(説明資料の名前, href)`、`docsTab` は `frameBar(文書の選び, selected.view)`、`agents_tab.js` は `frameBar(選び, null)`。
	- `scope.js` の `.sd-tabs-row` は、タブ（`.sd-tabs`）と `legend()`。
	- `panel.css` のスマートフォンの全体の段は、`.pn-top` を1行の flex にし、`.pn-head` を contents、`.pn-cover` を order 2 に、`.pn-merge, .pn-kind, .pn-why, .pn-idle, .pn-path` を隠す。
	"""

target: """
	- `panel_logic.js` に `headerBand(scope, {idle, label})`（純粋）。
	- `panel.js` の見出しを `.pn-head` = `.pn-crumb`（パンくずと今の ID）＋ `.pn-hl`（札と印）＋ `.pn-orca` ＋ 閉じる、`.pn-cover` = 題名＋帯（あるとき）にする。タブの行を `.pn-tabrow` = `.pn-tabs`（tablist）＋ `.pn-tabopen`（印の置き場）にする。
	- `scope_tabs.js` の SCOPE_TABS に任意の `open(env)`。`explanationTab` の帯をなくし、`docsTab` の帯から印を外す。
	- `scope.js` のタブの行に同じ印。
	- `panel.css`・`scope_tabs.css`・`scope.css` の規則。
	"""

design: {
	"D-01": {
		title: "帯の中身を決める純粋な関数（panel_logic.js の headerBand）"
		text: """
			`headerBand(scope, {idle = "", label = ""} = {})` → `null` か `{reason, idle, merge}`。DOM も import も使わない（`panel_logic.js` は今も依存のない純粋な関数の置き場）。`label` は状態の名前（呼ぶ側が `STATES[scope.state]?.label` を渡す）、`idle` は `idleText(scope, byId)` の結果（`""` か『N分動きなし』）。

			- `PLAIN_REASONS = new Set(["closed", "in_progress", "no_waits"])`。
			- `reason`：`scope.reason?.text` を前後の空白を除いて読み、空、`label` と同じ、または `PLAIN_REASONS.has(scope.reason?.code)` なら `""`、ほかはその文。
			- `idle`：引数のまま。
			- `merge`：`scope.merge` が `"needs_fix"` か `"mergeable"` ならその値、ほかは `null`。`merge` があり `reason` が空なら、`reason` を `MERGE_WORDS[merge]`（`needs_fix`『マージ待ち・直す必要あり』、`mergeable`『マージ待ち・マージできる』。`mergeBadge` と同じ言葉）にする（統括の条件：マージの状態は必ず帯に出る）。
			- `reason` と `idle` がどちらも空で `merge` もなければ `null`（帯を出さない）。
			"""
		satisfies: ["R-03", "R-04", "F-01"]
	}
	"D-02": {
		title: "見出しの HTML（panel.js の build と header）"
		text: """
			`build()` の `.pn-top`：`<div class="pn-head"><span class="pn-crumb"></span><span class="pn-hl"></span><span class="pn-orca"></span><button … class="iconbtn pn-close" …></button></div><div class="pn-cover"></div>`。`parts` に `crumb` を足す。

			`header(scope, byId)` → `{crumb, hl, cover}`：
			- `crumb`：`<nav class="pn-path" aria-label="親の道筋">` ＋ 祖先ごとに `<button type="button" data-pn-goto="<id>" title="<id> <題名>">id</button>` と `chevronRight` の印 ＋ `<span class="pn-self"><span class="ds-docid">今の ID</span><span class="pn-kind">#番号・種類</span></span></nav>`。祖先がないときは祖先の代わりに `<span class="pn-top-mark" role="img" aria-label="最上位" title="最上位">` ＋ `layers` の印 ＋ `</span>`。
			- `hl`：`stateChip(scope, byId, {motion: true})` ＋ `orcaSlot(scope.id, 4)`（`.pn-merge` と `mergeBadge` をやめる）。
			- `cover`：`<h2 class="pn-title" title="題名">題名</h2>` ＋ 帯。帯は `headerBand(scope, {idle: idleText(scope, byId), label: STATES[scope.state]?.label})`（`STATES` は `parts.js` から読む） が `null` でないとき `<p class="pn-why" data-st="<state>"[ data-merge="<merge>"] title="<見える文の全文>">` ＋（`merge` があれば `<span class="pn-merge-mark">` に `needs_fix` は `zap`、`mergeable` は `check`）＋（`reason` があれば `<span class="pn-reason">reason</span>`）＋（`idle` があれば `<span class="pn-idle">` ＋ `clock` ＋ idle ＋ `</span>`）＋ `</p>`。title の全文は、出す文を『・』でつないだもの。
			- `draw()` は今の `hl`・`cover` と同じく、`crumb` も前と違うときだけ書く（`shownCrumb`。`build()` で null に戻す）。
			- クリックの扱い：`[data-pn-goto]` は今のまま（場所が `.pn-head` の中に移るだけ）。スマートフォンの引っぱりは `.pn-top` の中でボタンとリンクを除く今の判定のままで、パンくずのボタンでは始まらない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-08"]
	}
	"D-03": {
		title: "枠を新しいタブで開く印（SCOPE_TABS の open と、タブの行）"
		text: """
			- `scope_tabs.js`：SCOPE_TABS の行に任意の `open(env)` → `{href, label}` か `null`。
			  - 説明資料：`explanationState(details)` が `written` で href があれば `{href, label: "説明資料"}`、ほかは `null`。
			  - 文書：`docsTab` と同じ選び（`selectedDoc(env)` に取り出し、`docsTab` もそれを使う）で、枠を出すとき（`selected` があり、`spec` の描画の失敗でない）`{href: selected.view, label: selected.label}`、ほかは `null`。
			  - ほかのタブは `open` を持たない。
			- 帯：`frameBar(left)`（印の引数をやめる）。`explanationTab` の `written` は `<div class="sd-framebox" data-frame="explanation"><iframe class="sd-explain" …></iframe></div>`（帯なし）。`docsTab` は `frameBar(文書の選び)`。`agents_tab.js` は `frameBar(選び)`。
			- 印の HTML（共通の関数 `tabOpenLink(open)` を `scope_tabs.js` から出す）：`open` が `null` なら `""`、ほかは `<a class="sd-tabopen" href="<href>" target="_blank" rel="noopener" aria-label="<label>を新しいタブで開く" title="<label>を新しいタブで開く">` ＋ `external` の印 ＋ `</a>`。
			- 欄（`panel.js`）：`build()` のタブの行を `<div class="pn-tabrow"><div class="pn-tabs" role="tablist" aria-label="欄のタブ"></div><span class="pn-tabopen"></span></div>` にする（`parts.tabs` は今の `.pn-tabs`、`parts.tabopen` を足す）。`draw()` で、`env` があり選んだタブの行に `open` があれば `put(parts.tabopen, tabOpenLink(row.open(env)))`、ほかは `put(parts.tabopen, "")`（F-02：読み込み中・前の Scope の印を残さない）。
			- 詳しい画面（`scope.js`）：`.sd-tabs-row` を `<nav class="sd-tabs" …>タブ</nav>` ＋ `tabOpenLink(選んだタブの open(env))` ＋ `legend()` にする（印はタブの並びのすぐ右、凡例は今のまま右端）。
			"""
		satisfies: ["R-05", "F-02"]
	}
	"D-04": {
		title: "CSS（panel.css・scope_tabs.css・scope.css）"
		text: """
			PC（panel.css）：
			- `.pn-head`：今の flex・中央そろえ・`gap: 8px`・`padding: 12px 10px 0 16px` に、`flex-wrap: wrap-reverse; row-gap: 4px;` を足す。`.pn-crumb { flex: 1 1 12em; min-width: 0; }`（12em より狭くなるときだけ、`.pn-crumb` が右の部品の下の行に送られる。`wrap-reverse` なので右の部品と閉じるは上の行に残り、閉じるは `margin-left: auto` で右端）。`.pn-hl` の中身・`.pn-orca`・閉じるは縮まない。
			- 今の `.pn-head .iconbtn { margin-left: auto; … }`・`.pn-orca:not(:empty) { margin-left: auto; }`・`.pn-orca:not(:empty) + .pn-close { margin-left: 0; }`・`.pn-orca:empty` の規則は消さない（同じ欄に描く『片付けの候補』の `.pn-head` は `.pn-crumb` を持たず、閉じるの右寄せをこの規則に頼る）。`.pn-crumb` がない見出しの見た目は今と同じ。
			- `.pn-path`（`.pn-crumb` の中の nav）：`display: flex; align-items: center; flex-wrap: nowrap; gap: 2px; min-width: 0; margin: 0; font-size: 12.5px; color: var(--ds-muted);`。祖先のボタンは今の見た目のまま `flex: 0 1 auto; min-width: 3ch;`（`max-width: 22ch`・省略記号は今のまま）。`.pn-self { flex: 0 1 auto; min-width: 0; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }`、`.pn-self .ds-docid { flex: none; }`、`.pn-kind { min-width: 0; overflow: hidden; text-overflow: ellipsis; }`。祖先のボタンは今の ID より先に縮む（`flex-shrink` の重みを祖先 4、`.pn-kind` 1 にする）。
			- `.pn-cover { padding: 4px 16px 0; }`、`.pn-title { margin: 0; font-size: 16px; line-height: 1.45; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }`（今の折り返しの規則は残す）。
			- `.pn-why`：今の左の線（`--st`）・地（`--st-bg`）・角を保ち、`margin: 6px 0 0; padding: 4px 10px; align-items: center; gap: 8px; white-space: nowrap; overflow: hidden; font-size: 12.5px;`。中の `.pn-reason { min-width: 0; overflow: hidden; text-overflow: ellipsis; }`、`.pn-idle`（帯の中）は `flex: none; display: inline-flex; gap: 4px; color: var(--ds-muted);`、`.pn-merge-mark` は `[data-merge="needs_fix"]` で `--ds-danger-ink`、`[data-merge="mergeable"]` で `--ds-ok-ink`（`mergeBadge` の札の文字と同じ色の変数）。今の `.pn-why .st-ico` と、別の行の `.pn-idle` の規則は消す。
			- タブの行：`.pn-tabrow { flex: none; display: flex; align-items: center; margin-top: 8px; border-bottom: 1px solid var(--ds-border); }`、`.pn-tabs` は今の規則から `margin-top` と `border-bottom` を外し `flex: 1; min-width: 0;`。`.pn-tabopen { flex: none; display: flex; padding-right: 8px; } .pn-tabopen:empty { display: none; }`。
			- 印（scope_tabs.css の `:is([data-view="scope"], .sd-pn)` の中）：`.sd-tabopen` は今の `.sd-framebar__open` と同じ 24px の四角・`--ds-muted`・hover。`.sd-framebar__open` と `.sd-framebar__name` の規則を消す。
			- 詳しい画面（scope.css）：`.sd-tabs-row .sd-tabopen { align-self: center; margin-bottom: 6px; }`（凡例の `margin-left: auto` は今のまま）。

			スマートフォン（panel.css の `@container app (max-width: 640px)`）の全体の段：
			- `.pn-top` の1行の flex と `.pn-head { display: contents; }` は今のまま（`.pn-hl` も今どおり `display: contents` で、札と印は order 0 の flex の項目）。`.pn-crumb { order: 1; flex: none; }`、`.pn-cover { order: 2; flex: 1; min-width: 0; padding: 0; }`、`.pn-orca, .pn-close { order: 3; }`。並びは今と同じ『札・印・今の ID・題名・Orca で開く・閉じる』。
			- 隠す：`.pn-path > button, .pn-path > .ds-icon, .pn-top-mark, .pn-kind, .pn-why`。`.pn-title` は今の1行と省略記号（`-webkit-line-clamp` を外し `white-space: nowrap; display: block;`）。今の `.pn-merge, .pn-idle, .pn-kicker` の規則は、要素がなくなるので消す。
			- タブの行：`.pn-tabrow { margin-top: 0; }`（今の `.pn-tabs { margin-top: 0 }` の置き換え）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07"]
	}
	"D-05": {
		title: "テストの直しと足し"
		text: """
			- 新しい node のテスト（`tests/js/` と `tests/unit/infra/` の pytest の包み。今の `test_dashboard_panel_logic_js.py` の形）：`headerBand` の表（T-01）。今の `test_dashboard_panel_logic_js.py` に足してよい。
			- 欄の偽の DOM のテスト（今の `test_dashboard_orca_views_js.py`・`test_dashboard_agents_tab_js.py` の欄の部品と、`tests/js/dashboard_allgraph_screen.mjs`）：`PARTS` に `.pn-crumb`・`.pn-tabopen` を足し、`top` の HTML の期待を D-02 の形にする。今の ID が1回、帯の出る・出ない、マージの札がない、タブの行の印（T-02・T-03）。
			- 静的な検査（`test_dashboard_state_marks.py` の `.pn-why` の場所の期待、`test_dashboard_scope_tabs_js.py` の説明資料の帯と印の期待）を D-02・D-03 の形に直す。CSS の静的な検査（題名の2行、帯の1行、スマートフォンの全体の段の隠す規則、`.sd-framebar__open` がない）。
			- 直す期待は、見出しとタブの行の形の変化によるものだけにし、ほかの期待は変えない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-08", "F-01", "F-02"]
	}
	"D-06": {
		title: "測りと実機の確かめ"
		text: """
			試しのサーバー：直す前は実装の開始のコミット（iss-00650 のマージ後の `origin/main`）を `git archive` して隔離した venv、直した後はこの worktree を隔離した venv に入れ、同じ状態の置き場の写し、別のポート（後は `--tailscale`）。常駐の 47800・8791 の設定と道具の環境に触れない。headless Chrome は `--disable-features=MacAppCodeSignClone`、閉じるのは CDP の `Browser.close`。

			- 画面：構造の図・横断の構造・ボードの欄（3つとも `createScopePanel`）。
			- 高さ：1440×900 と 1000×800 で、作業中の Issue の欄を説明資料のタブで開き、`getBoundingClientRect` で『欄の上端からタブの行の上端まで』（見出しの高さ）と『説明資料の枠（`.sd-explain`）の高さ』を、直す前と後で測る。止められている Scope と Epic でも同じ数を書く。
			- 1行目：1000×800 で、祖先2つの作業中の Issue の1行目の高さが閉じるのボタンの行の高さ（32px 前後）に収まり、`.pn-head` の `scrollWidth` が `clientWidth` を超えない。
			- 印が4つのとき：エージェントが4つある Scope があればそれで、なければ欄の `.sd-orca` の印の要素を DevTools（CDP の Runtime.evaluate）で4つに複製して、1000×800 の見出しが1行か、パンくずが下の行に送られ、`.pn-head` がはみ出さず閉じるが右上にあることを確かめ、写しを残す。
			- 片付けの候補の欄：見出しの閉じるが右端にあること（写し）。
			- 写し：Issue・Epic・Initiative・止められている Scope・マージ待ちの Scope（あれば）・エージェントのいる Scope の欄を、構造の図と横断の構造（ボードは作業中の Issue だけ）で、1440・1280・1000 × 明・暗、スマートフォン 390×844 の通常と全体の段。直す前と後を並べる。
			- 本人が見る試しの URL（tailnet）を report.md に書き、本人の確かめまで残す。
			"""
		satisfies: ["R-01", "R-06", "R-07"]
	}
}

compatibility: """
	API・保存・モデルは変わらない。欄の部品の class のうち `.pn-kicker`・`.pn-merge`・別の行の `.pn-idle`・`.sd-framebar__name`・`.sd-framebar__open` がなくなり、`.pn-crumb`・`.pn-self`・`.pn-top-mark`・`.pn-reason`・`.pn-merge-mark`・`.pn-tabrow`・`.pn-tabopen`・`.sd-tabopen` が足される。
	`frameBar` の2つ目の引数がなくなる（呼ぶ側は3つ、すべてこの Issue で直す）。これらを固定している今のテストは、この設計に合わせて直す。
	"""

risks: [
	"1000px の幅（欄 440px）で、祖先が2つとエージェントの印が4つあると、祖先の ID が強く縮む。title と押して開く動きで辿れ、今の ID は縮まない。実機の写しで確かめる。",
	"iss-00650 が同じ `panel.js`・`panel.css` を変える。実装はそのマージの後の `origin/main` から始め、引っぱりの判定（`.pn-top` の中のボタンとリンクを除く）を変えない。",
	"`-webkit-line-clamp` は今の主なブラウザーで使えるが、標準の `line-clamp` ではない。使えないブラウザーでは題名が切れずに全文が出る（害はない）。",
]
