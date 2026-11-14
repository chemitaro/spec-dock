package spec

// 設計（Issue）。型 specdock/v1。
// Epic epic-00526 の design.cue の D-01〜D-07 を、ファイルと関数の粒度に落とした設計。Epic と食い違えば Epic が正しい。

goals: [
	"相手の選び（出す条件、自動の選び、いなくなった印、iframe の道）を、DOM に触れない純粋な関数に閉じ、node のテストで表のように確かめる",
	"タブは共有の並び（SCOPE_TABS）に1行足し、タブに任意の visible を足すだけで、横の欄と詳しい画面の両方に出す",
	"タブの中身の HTML は Scope、選んだエージェント（id・種類・ブランチ）、明暗、理由だけで決まる文字列にし、横の欄と詳しい画面の両方で、同じ文字列なら中身を置き換えない",
	"iframe の sandbox は、orca-web の画面が動く最小の許可にし、SpecDock の CSP とサーバーは変えない",
	"iss-00592 と同じファイルを触る箇所は、足すだけの小さな変更にして、後に入る方が合わせやすくする",
]

current: """
	- `views/_shared/scope_tabs.js`：`SCOPE_TABS`（7行、`{key, label, count, render}`）、`TAB_KEYS`、`pageEnv(ctx, scope, doc, byId)`、`panelEnv(ctx, scope, doc, byId, {params, tab})`、`frameBar(left, href)`（モジュールの中だけ）。`FRAME_SANDBOX = "allow-scripts allow-popups"` は SpecDock 自身の資料の枠のもの。
	- `views/_shared/panel.js`：`draw()` が `pickTab(userTab, TAB_KEYS, details)` でタブを選び、`SCOPE_TABS` の全部をボタンにし、中身の HTML が `shownHtml` と同じなら `.pn-body` を置き換えない。`show(state)` で Scope が変われば `params` を空にする。`hide()`、`destroy()` がある。
	- `views/scope.js`：`render(root, ctx)` が毎回 `root.innerHTML` で `.sd-page`（`newTabLink`、`.sd-back`、`header.sd-cover`、`.sd-tabs-row`、`.sd-tabpanel`）を作り直す。`dispose` はない。
	- `app.js`：`render()` がビューの `render(root, ctx)` を呼ぶ。ctx は `{repository, route, data, scope, repositories, embed, orca, baseline, navigate, href}`。`ctx.orca` の知らせで描き直す口と、明暗の変化で描き直す口はない。`setTheme` は埋め込みの橋だけが呼ぶ。
	- `core/orca.js`：`forScope(structure, scopeId)` は状態が ok のときだけ、その Scope に対応した要約の worktree の並び（各々 `{id, path, branch, project, issue, counts, agents}`）を返す。要約の `agents[]` は `{id, mark, workingMode, agentType, since, detail, elapsedFrom, elapsedBasis}`。`marks()` は読んだ部品のモジュール（`renderAgentMarks`、`buildMarks`）か null。
	- CSS：`scope_tabs.css` の `.sd-framebox`（flex の列）と `:is(.sd-docframe, .sd-explain)` の枠。`panel.css` の `.pn-body:is([data-tab="docs"], [data-tab="explanation"])`（flex の列）、`.sd-pn .sd-framebox { flex: 1 }`、`.sd-pn :is(.sd-docframe, .sd-explain) { flex: 1; min-height: 240px; height: auto }`。`scope.css` の `:is(.sd-docframe, .sd-explain) { flex: none; height: max(420px, calc(100dvh - 120px)) }`。
	"""

target: """
	- 新しい `views/_shared/agents_logic.js`（純粋。DOM と ctx を知らない）：`scopeAgents`、`agentsVisibility`、`pickAgent`、`stripForm`、`agentFrame`、覚えの関数（`createAgentMemory`、`memoryFor`、`noteGone`、`forgetGone`、`noteDrift`）、`AGENT_SANDBOX`。
	- 新しい `views/_shared/agents_tab.js`：覚えの置き場（`mem`）、env から入力を集める `agentsState(env)`、タブの中身の `agentsTab(env)`、帯を後から描く `paintAgentList(root, env)`、明暗の `currentTheme()`。
	- `scope_tabs.js`：`SCOPE_TABS` の2番目に `agents`、`visibleTabs(env)`、env に `keep(name, value)`。
	- `panel.js`・`scope.js`：見えるタブだけを描き、中身の HTML が同じなら置き換えず、描いた後に帯を描き、`ctx.orca` の知らせで描き直す。
	- `app.js`：ctx に `orcaProblem` と `replaceParam`。OS の明暗の変化と `setTheme` で描き直す。
	"""

design: {
	"D-01": {
		title:     "純粋な決め方：agents_logic.js"
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-07", "F-01", "F-02", "F-04", "F-05", "F-07", "F-08"]
		text: """
			`views/_shared/agents_logic.js` は import を持たない ES Module（node で直接読める）。

			**`scopeAgents(worktrees)`** → `{agents, invalid}`。`worktrees` は `ctx.orca.forScope` の結果（並びでなければ空として扱う）。worktree の順、その中の `agents` の順に、次の形の項目を作って `agents` に入れる：
			`{id, agentType, branch, worktreeId, detail, raw}`。入れるのは、`id` が空でない文字列で、`detail` が `"/embed/agent?id=" + encodeURIComponent(id)` と**完全に同じ**エージェントだけ（orca-web の `src/summary/build.ts` が作る形。iframe の宛先の id と、帯と title と選びの id が必ず同じになる。ChatGPT round-2 の P1）。ほかの項目（id がない、detail が違う道か違う id を指す、文字列でない）は使えないので入れず、`invalid` に数える（同じ id の2回目は数えずに捨てる）。`agentType` は文字列でなければ null、`branch` は worktree の `branch` が文字列でなければ null、`worktreeId` は worktree の `id`、`raw` は要約のエージェントそのもの（印を描くため）。同じ `id` が2回出たら最初だけを残す。

			**`agentsVisibility({status, problem, records, agents, wanted, goneIds, embed})`** → `{show, reason}`。`records` はその Scope の SpecDock の worktree の記録の数、`agents` は `scopeAgents` の結果、`wanted` は今の選び（文字列か null）、`goneIds` はその Scope のいなくなった覚え（id の Set。D-02）。出すかどうか（上から順。R-01）：
			1. `status === "off"` で `problem` がない → `{show: false, reason: null}`。
			2. `records` が 0 → `{show: false, reason: null}`（F-04）。
			3. `problem` がある、または `status` が `loading`・`unreachable`・`orca-unreachable`・`orca-starting` → 出す。
			4. `status === "ok"`：`agents.length > 0`、`wanted` がある、または `goneIds` が空でない → 出す。ほか → 出さない。
			5. ほかの `status` の値 → 出さない。
			4 の続き：`status === "ok"` で上のどれにも当たらず、`invalid > 0`（入力に `invalid` を足す）→ 出す（理由 `"shape"`。対応した worktree にエージェントがいるのに、どれも形が違う。F-01）。
			理由（出すときだけ、上から順）：`problem` があれば `"config"`、`embed` が真なら `"embed"`（F-05）、`status` が `ok` でなければその値、`ok` で `agents` が0人・`wanted` も `goneIds` もなく `invalid > 0` なら `"shape"`、ほかは null。形の違う項目が一部だけなら理由は null のままで、帯に1行の注を出す（D-04）。

			**`pickAgent(agents, wanted, goneIds)`** → `{selected, gone, remember, addGone}`（理由が null のときだけ呼ぶ。Epic D-02。`goneIds` は id の Set、なければ空として扱う）。上から順：
			1. `wanted` が `gone:` で始まる → `{selected: null, gone: true, remember: null, addGone: その後ろの id}`（同じ id が `agents` に戻っても開かない）。
			2. `wanted` が `goneIds` にある → `{selected: null, gone: true, remember: null, addGone: null}`（戻る操作などで、いなくなった id が選びとして戻ってきた）。
			3. `wanted` が `agents` のどれかの `id` → `{selected: その項目, gone: false, remember: null, addGone: null}`。
			4. `wanted` があるが `agents` にない → `{selected: null, gone: true, remember: "gone:" + wanted, addGone: wanted}`（F-02。残ったのが1人でも選ばない）。
			5. `wanted` がなく `goneIds` が空でない → `{selected: null, gone: true, remember: null, addGone: null}`（覚えがある間は自動で選ばない）。
			6. `wanted` がなく `agents` が1人 → `{selected: その項目, gone: false, remember: その id, addGone: null}`（R-02）。
			7. ほか → `{selected: null, gone: false, remember: null, addGone: null}`（「選ぶ」）。
			`gone` のときの、いなくなった相手の名前は出さない（id しか知らないため。知らせは「選んでいたエージェントはいなくなった」）。

			**`stripForm(agents, selected, gone)`** → `"label"` か `"switch"`：`agents.length === 1` で `selected` がその1人のときだけ `"label"`（押せない見出し）、ほかは `"switch"`（gone のときは残りが1人でも押せる項目。round-1 の P1）。

			**`agentFrame(origin, agent, theme)`** → `{src, title}` か null。`origin` が文字列でない、`agent` がない、`theme` が `light`・`dark` でないときは null。`src` は `origin + agent.detail + "&theme=" + theme`（`detail` をそのまま使い、id を符号にし直さない）。`title` は `"エージェント：" + (agentType ?? "種類不明") + "・" + (branch ?? "ブランチ不明")`。

			**いなくなった覚えと、移った覚え**（純粋な関数。状態は呼ぶ側が持つ1つのオブジェクト `mem = createAgentMemory()` = `{scopeId: null, gone: new Set(), picked: null, drift: null}`。R-05、F-08）：
			- `memoryFor(mem, scopeId)`：`mem.scopeId` が違えば `gone` を空、`picked` と `drift` を null にして `scopeId` を変える（別の Scope を示したら捨てる）。`mem` を返す。
			- `noteGone(mem, id, {stale})`：`stale` が真（問い合わせや Map に残った古い `gone:<id>` を読んだとき。pickAgent の規則1）で `id === mem.picked` なら足さない（人が選び直した直後の描き直しで、古い問い合わせが覚えを戻さない。spec-reviewer round-2 の P3）。ほかは `gone` に足し、`id === mem.picked` なら `picked` を null にする。
			- `forgetGone(mem, id)`：`gone` を空、`drift` を null、`picked` を `id` にする（人が切り替えの項目か、移った知らせの「戻す」を押したとき）。
			- `noteDrift(mem, id)`：`drift` を `id` にする（iframe の中で別の文書に移った。D-04）。
			pickAgent の結果の `addGone` は、規則1なら `{stale: true}`、規則4なら `{stale: false}` で `noteGone` に渡す（結果に `addGoneStale` を足す）。

			**`AGENT_SANDBOX`** = `"allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"`（D-03）。
			"""
	}
	"D-02": {
		title:     "タブの並びと env：scope_tabs.js と agents_tab.js の agentsState"
		satisfies: ["R-01", "R-02", "F-04", "F-07"]
		text: """
			`SCOPE_TABS` の `explanation` と `summary` の間に `{key: "agents", label: "エージェント", visible, count, render}` を足す。ほかのタブは `visible` を持たない（いつも出す）。`visibleTabs(env)` = `SCOPE_TABS.filter((tab) => !tab.visible || tab.visible(env))` を公開する。`TAB_KEYS` は全部のキーのまま（`?tab=` の解釈の互換のため）。

			`pageEnv` と `panelEnv` に `keep(name, value)` を足す（選びを、人の操作でなく覚える口）：
			- `pageEnv`：`env.param(name)` が value と違えば `ctx.route = ctx.replaceParam(name, value)`（D-06。履歴を増やさない。`param` と `paramLink` は呼ばれたときの `ctx.route` を読むので、以後の値と道は新しい問い合わせになる）。`ctx.replaceParam` がなければ何もしない。
			- `panelEnv`：`params.set(name, value)`（受けた `params` の Map をそのまま書き換える。iss-00587 の選びと同じ Map）。

			**覚えの置き場**：`agents_tab.js` のモジュールの中に `mem = createAgentMemory()` を1つ持つ（D-01）。横の欄と詳しい画面は同時に1つの Scope しか示さず、欄から詳しい画面へ同じ Scope で移っても、欄を閉じて開き直しても、戻る操作でも覚えは残る。ページを読み込み直すと消える。

			`agentsState(env)`（`agents_tab.js`）が、env から入力を集めて決め方を呼び、結果を env ごとに1回だけ覚える（WeakMap。同じ env の `visible`・`count`・`render` は同じ答え）。**`keep` は呼ばない**（ほかのタブを示す間に選びを書き換えないため。round-1 の P3）：
			- `status`：`env.ctx.orca?.status() ?? "off"`。`problem`：`env.ctx.orcaProblem ?? null`。`embed`：`env.ctx.embed === true`。
			- `records`：構造（`env.ctx.data`）の `worktrees.status` が `ok` なら、`env.byId.get(scope.id)?.worktrees` の数、ほかは 0（F-04）。
			- `agents`：`scopeAgents(env.ctx.orca?.forScope(env.ctx.data, env.scope.id) ?? [])`（状態が ok でなければ `forScope` は空を返す）。
			- `wanted`：`env.param("agent")`。`memoryFor(mem, env.scope.id)` を呼び、`goneIds` は `mem.gone`。
			- 状態が `ok` で、`wanted` が `gone:` で始まらない id で、`agents` にないときは、ここで `noteGone(mem, wanted, {stale: false})` を呼ぶ（覚えに足すだけで、`keep` は呼ばない。ほかのタブを見ている間に相手が消えて同じ id で戻っても、後でエージェントのタブを開いたときに開かない。spec-reviewer round-2 の P2）。
			- 結果：`{...agentsVisibility(...), agents, invalid, wanted, goneIds}`。
			`visible(env)` は `.show`。`count(env)` は理由が null のとき `agents.length`、ほかは null。
			`render(env)` は `agentsTab(env)`（D-03、D-05）：理由が null なら `pickAgent(agents, wanted, goneIds)` を呼び、`addGone` を `noteGone` で覚えに足し、`remember` があれば `env.keep("agent", remember)` を1回呼ぶ（エージェントのタブを描くときだけ）。結果は同じ env の `paintAgentList` が使えるよう env ごとに覚える。
			"""
	}
	"D-03": {
		title:     "タブの中身と iframe の形、sandbox"
		satisfies: ["R-02", "R-03", "R-04", "R-05", "R-07", "F-06", "F-08"]
		text: """
			`agentsTab(env)` は理由があれば D-05 の知らせだけを返す。理由が null なら、次の1つの文字列を返す（同じ入力なら同じ文字列。D-04）：
			`<div class="sd-framebox" data-frame="agents">` + `frameBar('<div class="sd-agents" data-orca-agents="<esc(ScopeID)>"></div>', null)` + 本体 + `</div>`。
			本体は次のどれか：
			- 選ばれている：`<iframe class="sd-agent" src="<esc(src)>" sandbox="<AGENT_SANDBOX>" referrerpolicy="no-referrer" title="<esc(title)>"></iframe>`（`agentFrame(ctx.orca.origin, selected, currentTheme())`。属性はこの順。`loading` は付けない）。
			- 移った（選ばれた項目の id が `mem.drift`）：iframe を置かず、`sd-callout`（`data-tone="warning"`、`data-code="orca-agent-drift"`）「チャットの中のリンクで、選んだのと別のエージェントに移ったので閉じた。このタブでは選んだエージェントだけを開く」と、`<a data-agent-pick="<esc(id)>" ${env.paramLink("agent", id)}>選んだエージェントに戻す</a>`（F-08）。
			- gone：`sd-callout`（`data-tone="warning"`、`data-code="orca-agent-gone"`）「選んでいたエージェントはいなくなった。上から選び直す」。
			- 選びがない（2人以上）：`sd-callout`（`data-tone="note"`、`data-code="orca-agent-choose"`）「エージェントを選ぶ」。
			`frameBar` は `scope_tabs.js` から export して使う（今の関数をそのまま公開するだけ）。

			**sandbox の値と理由**（統括の決定「最小の許可」。orca-web の main `1a2afed` の `web/embed/agent*.js`・`send-*.js` を読んだ事実に基づく）：
			- `allow-scripts`：orca-web の画面は ES Module で動く。
			- `allow-same-origin`：orca-web の送信の守り（同じオリジンの JSON、`POST /api/token` の短期のトークン、`Sec-Fetch-Site` の検査）と、会話の API（同じオリジンだけ、CORS なし）は、iframe の文書が orca-web のオリジンを持つことを前提にする。外すと文書のオリジンが不透明（`null`）になり、読みも送信も拒まれる。iframe の文書は SpecDock と別のオリジンなので、`allow-scripts` と並べても、親の DOM に触れて sandbox を外すことはできない（同じオリジンを置くときだけの危険）。
			- `allow-popups` と `allow-popups-to-escape-sandbox`：詳細の PR と CI のリンクは `target="_blank"` で開く。後者がないと、開いた GitHub の画面まで sandbox を受け継いで動かなくなる。
			- 付けないもの：`allow-forms`（`<form>` を使わず、送信は `fetch`）、`allow-top-navigation` 系（SpecDock の画面を移させない）、`allow-modals`、`allow-downloads`、`allow-storage-access-by-user-activation` ほか。`allow` 属性（カメラ、クリップボードなど）も付けない。
			- SpecDock の画面の CSP は変えない（`frame-src` に orca-web のオリジンがすでにある。iss-00591）。iframe の中の CSP と `frame-ancestors` は orca-web が持つ。
			- 実機の確かめ（S-04）で、この値のまま、会話の読み、送信、「Orca で開く」、PR のリンクの新しいタブが動くことを確かめる。どれかが動かないときは、許可を黙って足さず、タスク担当が仕様を直してレビューを通す（理由を書き足す）。

			`sendEnabled` が false のとき（F-06）、SpecDock は何も描き足さない。タブの中身の HTML は送れるかによらない。

			高さ（iss-00589 と同じ方針）：
			- `scope_tabs.css`：`:is(.sd-docframe, .sd-explain)` の枠の見た目（線、角、背景、`display: block; width: 100%`）の規則に `.sd-agent` を足す。帯の中の `.sd-agents` は `display: flex; gap; min-width: 0; overflow-x: auto; white-space: nowrap`（1行のまま横に動く）。各項目 `.sd-agentpick` は印・種類・ブランチ（`sd-mono`）を並べ、`aria-current="true"` の項目を今の `sd-seg` の選びと同じ色の言葉（既存の変数）で示す。新しい色を足さない。
			- `panel.css`：`.pn-body:is([data-tab="docs"], [data-tab="explanation"])` の2つの規則（広い画面とスマホ）に `[data-tab="agents"]` を足し、`.sd-pn :is(.sd-docframe, .sd-explain)` に `.sd-agent` を足す（`flex: 1; min-height: 240px; height: auto`）。
			- `scope.css`：`:is(.sd-docframe, .sd-explain) { flex: none; height: max(420px, calc(100dvh - 120px)) }` に `.sd-agent` を足す。
			"""
	}
	"D-04": {
		title:     "描き直しで iframe を残し、Scope を変えたら外す"
		satisfies: ["R-05", "R-07", "F-02", "F-03", "F-08"]
		text: """
			**中身の文字列に入れるもの**：Scope の ID、理由、選ばれた項目の `src` と `title`（id・種類・ブランチ・明暗）、gone か「選ぶ」か。ほかのエージェントの数・並び・印・経過は入れない（帯は置き場に後から描く）。そのため、ほかのエージェントの増減では文字列が変わらず、選んだエージェントの種類かブランチか明暗が変われば変わる（R-07 が許す置き直し）。

			**横の欄**（`panel.js`）：
			- `draw()` は、詳しい内容が読めていれば、まず `panelEnv(…, {params, tab: userTab})` で仮の env を作り（`visible` はタブによらない）、`visibleTabs(仮の env)` の並びのキーで `pickTab(userTab, キー, details)` を選び、選んだタブが `userTab` と違えば `panelEnv(…, {params, tab})` で env を作り直す（round-1 の P3：env を作るのにタブが要る順の循環を解く）。その並びでタブのボタンを描く。`env` がない（読み込み中）ときは `visible` を持つタブを除いた並びを描く。
			- 中身は今の `shownHtml` の比べ方のまま。Scope が変われば中身の文字列（`data-orca-agents` の ID を含む）が変わるので置き換えられ、前の iframe は外れる（F-03）。
			- 中身を描いた後（置き換えたかどうかによらず）、選んだタブが `agents` なら `paintAgentList(parts.body, env)` を呼ぶ。
			- 知らせ：`draw()` の中で、`state.ctx.orca` が今の購読の相手と違えば、前の購読を外し、`ctx.orca.subscribe(() => { if (current) draw(); })` で付け直す。`hide()` と `destroy()` で外す。

			**詳しい画面**（`scope.js`）：
			- 描く順を、見えるタブの並び（`visibleTabs(env)`）→ `pickTab` → 中身の HTML（`render(env)`。ここで `keep` が `ctx.route` を書き換えうる）→ 見出しとタブの帯の HTML（書き換えた後の `ctx.route.path` で道を作る）にする。
			- `.sd-page` の子を、見出し（`<div class="sd-scope-top">` に `newTabLink`・`.sd-back`・`header.sd-cover` を入れる。CSS で `display: contents` にして今の並びと見た目を保つ）、`.sd-tabs-row`、`.sd-tabpanel` の3つにする。`.sd-page` に `data-scope="<ID>"` を付ける。
			- 前に描いた `.sd-page` がこの root にあり、その `data-scope` が今の Scope の ID と同じなら、見出しと帯は `innerHTML` を書き換え、中身は前に描いた文字列（モジュールの中に覚える）と違うときだけ書き換える。`.sd-tabpanel` の `data-tab` は毎回合わせる。違う Scope、初めて、または Scope を読めないときの描き方（`emptyState`）では、今と同じく全体を書き換え、覚えた文字列を捨てる（F-03）。
			- 中身を描いた後、選んだタブが `agents` なら `paintAgentList(.sd-tabpanel, env)` を呼ぶ。
			- 知らせ：モジュールに最後の `{root, ctx}` を覚え、`ctx.orca` が今の購読の相手と違えば付け直す。知らせでは、覚えた root がまだ文書の中にあれば `render(root, ctx)` を呼ぶ。`dispose()` を足して購読を外し、覚えを捨てる（`app.js` は画面を替えるときに `dispose` を呼んでいる）。

			**帯**（`paintAgentList(root, env)`、`agents_tab.js`）：
			- `root.querySelector("[data-orca-agents]")` がなければ何もしない。`agentsState(env)` の `agents` と、同じ env の `render` が決めた選び（`pickAgent` の結果）から帯の HTML を作る：`stripForm` が `"label"` なら1つの `<span class="sd-agentpick" aria-current="true">`、`"switch"` なら項目ごとに `<a class="sd-agentpick" data-agent-pick="<esc(id)>" ${env.paramLink("agent", id)}>`（選ばれた項目にだけ `aria-current="true"`。gone のときはどれにも付けない）。中は `<span class="sd-agentpick__mark" data-orca-agent="<esc(id)>"></span>`、種類（なければ「種類不明」）、ブランチ（`sd-mono`。なければ「ブランチ不明」）。文字はすべて `esc` を通す。
			- 帯の文字列が前（置き場の `dataset` に覚える）と同じなら置き場の `innerHTML` を書き換えない。印は、各置き場について `marks.buildMarks({agents: [raw]}, {max: 1})` の結果の JSON を前の値と比べ、違うときだけ `marks.renderAgentMarks(slot, {agents: [raw]}, {size: "sm", max: 1})` で描く（作業中の弧が10秒ごとに回り始めに戻らない）。`marks()` が null か、部品が例外を投げたら、印は空のままにし、ほかは描く。
			- 置き場の `innerHTML` だけを書き換え、隣の iframe に触れない。
			- iframe の中での移り（F-08）：`paintAgentList` は枠の中の `iframe.sd-agent` に、`load` の聞き手を1つだけ付ける（iframe の `dataset` の印で二重に付けない）。聞き手は読み込みの回数を数え、2回目からは `noteDrift(mem, 選ばれた項目の id)` を呼び、`paintAgentList(root, env, {redraw})` で受けた `redraw()` を呼ぶ（中身の文字列が移った知らせに変わり、iframe が外れる）。orca-web の `/embed/agent` の画面は、自分で別の文書に移らない（`location` を書き換えず、移るのは同じ iframe で開く親と子のエージェントのリンクだけ。orca-web の main `1a2afed` の `web/embed/` を読んだ事実）ので、2回目の `load` は人がそのリンクを押したときに当たる。明暗の変化などで iframe が置き直されれば、新しい要素で数え直す。
			- `redraw` は、横の欄では `() => { if (current) draw(); }`、詳しい画面では覚えた `{root, ctx}` での `render`。
			- 形の違う項目が一部だけあるとき（`invalid > 0` で理由が null）、帯の終わりに `<span class="sd-muted">形の違う N件は出していない</span>` を足す（帯の文字列に入る。中身の文字列には入らない）。
			- 人の選び：枠（`.sd-framebox[data-frame="agents"]`）に、捕捉の段（capture）の `click` の聞き手を1つだけ付ける（枠の `dataset` に付けた印で二重に付けない。中身が置き換われば新しい枠に付く）。`[data-agent-pick]` の上の押しなら、修飾キーの有無によらず `forgetGone(mem, その id)` を呼ぶ。押しの既定の動き（欄の `data-pn-param` の処理、詳しい画面の `data-nav` の移動）は止めず、そのあとの描き直しで選んだ相手が開く（覚えを捨てた後なので、`wanted` が前にいなくなった id でも開ける）。

			**明暗**：`currentTheme()` = `document.documentElement.dataset.theme` が `light`・`dark` ならそれ、ほかは `matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"`。描き直しは D-06。
			"""
	}
	"D-05": {
		title:     "理由の知らせ"
		satisfies: ["R-06", "F-01", "F-05", "F-07"]
		text: """
			理由があるときは iframe も帯も描かず、`<div class="sd-callout" data-tone="warning" data-code="orca-<reason>">` の1つを返す（`loading` だけ `data-tone="note"`）。題名の1行と、必要なら確かめることの1行。言葉（Epic D-05）：
			- `loading`：「orca-web を読んでいる」。
			- `unreachable`：「orca-web（<esc(origin)>）に届かない」と「orca-web が動いているか、orca-web の ORCA_WEB_READ_ORIGINS がこの画面のオリジン（<esc(location.origin)>）を許しているかを確かめる」。`origin` は `ctx.orca.origin`。
			- `shape`：「orca-web の要約のエージェントの項目の形が違う（N件）。orca-web の版を確かめる」。
			- `orca-unreachable`：「orca-web は動いているが、Orca に届いていない（connection.state：unreachable）」。
			- `orca-starting`：「orca-web が Orca を読み始めたところ（connection.state：starting）」。
			- `config`：「設定の orca_web の節を読めない：<esc(problem)>」と「直すファイル：config.json（spec-dock dashboard list の config_problems に道が出る）」。埋め込みの画面なら、embed と同じリンクも添える。
			- `embed`：「埋め込みの画面ではチャットを開けない」と、`<a href="<esc(withoutEmbed(scope.path))>" target="_blank" rel="noopener">SpecDock を新しいタブで開く</a>`。
			状態が ok に戻れば理由が null になり、`pickAgent` は前の選び（欄の Map か問い合わせ）を使うので、同じエージェントの iframe に戻る（R-06）。理由がある間は `pickAgent` を呼ばないので、選びを変えない。
			"""
	}
	"D-06": {
		title:     "シェルの口：orcaProblem、replaceParam、明暗の変化"
		satisfies: ["R-02", "R-03", "R-06", "F-07"]
		text: """
			`app.js` の `render()` が作る ctx に2つを足す（ほかは変えない）：
			- `orcaProblem: state.server?.orca_web?.problem ?? null`。
			- `replaceParam(name, value)`：`const path = withParam(state.route.path, name, value)`（`views/_shared/logic.js` の `withParam`）。`history.replaceState(null, "", path)`、`state.route = parseRoute(new URL(path, location.origin).href)`、`return state.route`。描き直しも `bridge.navigated()` もしない（今の描きの中から呼ばれるため）。
			明暗の変化：`boot()` で `matchMedia("(prefers-color-scheme: dark)")` の `change` に `render` を付ける。`setTheme(scheme)` は値を変えた後に、起動が済んでいれば `render()` を呼ぶ。描き直しで中身の文字列の `theme` が変わり、iframe だけが置き直される。
			`ctx.orca` の知らせの購読は、横の欄と詳しい画面が自分で持つ（D-04）。`app.js` は購読しない（iss-00592 が構造の図とボードの購読を足すのと重ならない）。
			"""
	}
	"D-07": {
		title:     "書き込みに関わらないことの確かめ"
		satisfies: ["R-04"]
		text: """
			静的なテスト（Python、`tests/unit/infra/test_dashboard_agents_boundary.py`）：
			- 画面のファイルのうち、名前が `core/orca*.js`、`views/_shared/orca_*.js`（iss-00592 の `orca_marks.js`・`orca_logic.js` など、後で足すものを含む）、`views/_shared/agents_*.js` に当たるもの（テストが glob で集め、`agents_logic.js` と `agents_tab.js` と `core/orca.js` があることも確かめる）に、`/api/token`、`/api/send/`、`/api/open`、`/api/settings` と `postMessage` の文字列がない。
			- `src/spec_dock/assets/dashboard/` の全部の `.js` の `postMessage` の出現は、`core/embed.js` の `window.parent.postMessage` の1か所だけ。
			- `agents_logic.js` の `AGENT_SANDBOX` が D-01 の値と同じで、`allow-top-navigation` と `allow-forms` を含まない。
			実機の確かめ（S-04）で、確かめ専用の宛先へ iframe の中から送る間の CDP の `Network.requestWillBeSent`（要求の URL、`type`、`frameId`）と `Page.frameNavigated` を記録し、送信の口への要求がすべて iframe の frame から出て、親の frame（最上位）から出ないこと、親の frame から orca-web のオリジンへの要求が、要約の GET（`/api/worktrees/summary`）と、`/embed/` の下の静的な部品（`.js` と `.css`。`agent-marks*`、`elapsed.js` と、iss-00592 が置く `open-button.js` を含む）の読み込みだけで、ほかの `/api/` がないことを report.md に残す（iframe の文書 `/embed/agent?…` と `open-button` のボタンの枠の中の要求は、それぞれの frame の要求として数える）。
			"""
	}
	"D-08": {
		title:     "配る文書"
		satisfies: ["R-08"]
		text: """
			`src/spec_dock/assets/spec_dock/docs/reference_cli.md` に、エージェントのタブの説明を書く。iss-00592 の `orca_web` の節が `origin/main` にあればその節の中に、なければ `## 人のタスクの契約` の節（設定の3段を持つ）の後に `## orca-web との連携` の節を作って書く（後に入る方が1つの節にまとめる。Epic D-07）。
			書くこと：タブを出す条件（R-01 の4つ）、1人なら自動で開き選びを覚えること、選んだ相手がいなくなったら知らせて自動で移らないこと、選びの持ち方（欄の中、詳しい画面の `agent` の問い合わせ）、送信は orca-web の iframe の中だけで行われ orca-web の設定の `sendEnabled`（既定は止まっている）で止められ SpecDock は書き込みに関わらないこと、iframe の sandbox の値、知らせの5つの言葉の意味。例の IP は 127.0.0.1 と 192.0.2.x だけ。
			変えた配る文書と画面の資産の sha256 を `src/spec_dock/assets/static-inventory.json` に合わせる（今の検査のとおり。画面の資産が inventory に入っていなければ、入っているものだけ）。
			"""
	}
}

compatibility: """
	- `TAB_KEYS` は8つになるが、`?tab=` の解釈は今のまま（並びにないキーは既定のタブ）。ほかのタブの中身と問い合わせは変えない。連携を切っているか worktree のない Scope では、タブの帯は今と同じ7つ。
	- 詳しい画面の DOM に `.sd-scope-top`（`display: contents`）の包みと `.sd-page` の `data-scope` が足される。見た目は変えない（iss-00589 の写しと比べる）。今のテストの目印（`.sd-cover`、`.sd-tabs-row`、`.sd-tabpanel` など）は保つ。
	- サーバー、API、CSP、`core/orca.js`、`core/orca_match.js` は変えない。
	- iss-00592 とは `panel.js`（購読と見出し）、`app.js`、`reference_cli.md` で重なりうる。PR の前に `origin/main` を取り込み、重なりを直してから、テストとゲートを最終のコミットでやり直す。
	"""

risks: [
	"orca-web の `/embed/agent` の契約（`detail` の道、`theme`）が変わるとチャットが出なくなる。SpecDock は `detail` をそのまま使い、形が違えばそのエージェントを出さない",
	"orca-web の画面の中の、親と子のエージェントのリンクは同じ iframe の中で開く（orca-web の動き）。SpecDock はその移りを止められないので、2回目の `load` で iframe を外して知らせる（D-04、F-08）。移った先の画面は一瞬だけ見えうるが、外すまでの間に送る操作を終えるのは難しい。orca-web が将来、自分で文書を移すようになると（例：自動の読み直し）、この知らせが誤って出る。そのときは orca-web の README の契約に従って見直す",
	"`allow-same-origin` と `allow-scripts` を並べるので、iframe の中の orca-web の画面は自分のオリジンの力をすべて持つ。orca-web は同じ PC の信頼するサービスで、`frame-ancestors` で置き場を SpecDock のオリジンに限っている（Epic の risks）",
	"要約の知らせのたびに横の欄と詳しい画面が描き直す（10 秒ごと）。中身は同じ文字列なら置き換えないが、見出しと帯は書き換える。重さは写しと操作で確かめ、目立てば見出しも比べる",
	"orca-web の要約は、同じセッションを2つのエージェント（`chat:agent-session:…` と `structured-agent-session-…`）として返すことがある。SpecDock は要約のまま2つを並べる（どちらを選んでも同じセッションに届く。orca-web の側の課題）",
]
