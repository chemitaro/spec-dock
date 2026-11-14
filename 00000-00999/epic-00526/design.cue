package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"送信の守りは orca-web の iframe の中に任せ、SpecDock は相手を正しく選ぶことと、選びが古くならないことに責任を持つ",
	"タブは共有の並び（SCOPE_TABS）に1つ足すだけで、横の欄と詳しい画面の両方に出す",
	"orca-web の場所、要約、対応、状態は iss-00591 の core/orca.js を使い、二重に読まない",
	"iframe の HTML は、Scope、エージェント、明暗だけで決まる文字列にし、描き直しで読み込み直さない",
]

current: """
	- `views/_shared/scope_tabs.js` の `SCOPE_TABS` は `[{key, label, count(env), render(env)}]` の固定の並びで、`TAB_KEYS` がキーの並び。`panel_logic.js` の `pickTab(wanted, keys, details)` が、wanted が keys になければ既定のタブ（説明資料か概要）を選ぶ。
	- 横の欄（`views/_shared/panel.js`）は、タブの中身の HTML が前と同じなら中身を置き換えない（`shownHtml`）。描き直しは、構造の改訂が変わったとき（`app.js` の `refresh`、5 秒ごとの確かめ）と、選びが変わったとき。
	- 詳しい画面（`views/scope.js`）は、描くたびに `root.innerHTML` で全体を置き換える（中の iframe は読み込み直しになる）。
	- iss-00589（完了、PR #590）が、文書と説明資料のタブを `<div class="sd-framebox">` の中の `frameBar(left, href)`（1行の帯）と枠（`.sd-docframe`、`.sd-explain`）の形にした。横の欄は `panel.css` の `.pn-body:is([data-tab="docs"], [data-tab="explanation"])` の flex の列と枠の `flex: 1; min-height: 240px`、詳しい画面は `scope.css` の `height: max(420px, calc(100dvh - 120px))`。
	- epic-00471 の iss-00591 が `ctx.orca`（`status()`、`summary()`、`marks()`、`origin`、`subscribe(fn)`、`forScope(structure, id)`）を作る。iss-00592 は印の置き場の描き方（`views/_shared/orca_marks.js` の `paintOrcaMarks`）と、欄の見出しの「Orca で開く」を作るが、この Epic はそれに頼らない（並べて進められる）。
	"""

target: """
	- `SCOPE_TABS` の2番目に `agents` のタブ。タブに任意の `visible(env)` を足し、欄と詳しい画面はタブの並びを `visible` で絞ってから描き、`pickTab` に絞った後のキーを渡す。
	- 新しい `views/_shared/agents_tab.js` が、タブを出す条件、一覧、選び、iframe の HTML、理由の知らせを作る。決め方の純粋な部分は `views/_shared/agents_logic.js`（node のテスト）。
	- 詳しい画面は、タブの中身の HTML が前と同じなら中身の要素を置き換えない（欄と同じ比べ方）。
	"""

design: {
	"D-01": {
		title:     "タブの並びと、出す条件：visible(env)"
		satisfies: ["R-01", "F-04", "F-05", "F-07"]
		text: """
			`SCOPE_TABS` の説明資料と概要の間に `{key: "agents", label: "エージェント", visible, count, render}` を足す。ほかのタブは `visible` を持たない（いつも出す）。
			env に `orca`（`ctx.orca`）、`structure`（`ctx.data`）、`embed`（`ctx.embed`）と、その Scope の今の選び（`env.param("agent")`）を足す（`pageEnv`、`panelEnv`）。

			`agentsVisibility(input)`（`agents_logic.js`、純粋。input は `{status, problem, records, agents, wanted, embed}`）→ `{show: bool, reason: null | "loading" | "unreachable" | "orca-unreachable" | "orca-starting" | "config" | "embed", agents: [...]}`。
			出すかどうかを先に決め、出すときに理由を決める。

			出すかどうか（上から順）：
			- status が off で problem がない（利用者が切った）→ 出さない（F-07）。
			- records（Scope の構造の項目の `worktrees`、epic-00471 D-03）が空 → 出さない（F-04：記録がなければ推し量らない）。
			- problem がある、または status が loading・unreachable・orca-unreachable・orca-starting → 出す。
			- status が ok：agents が1人以上 → 出す。agents が0人で wanted がある（選んでいたエージェントがいなくなった。R-05）→ 出す。ほか → 出さない。

			理由（出すときだけ、上から順）：problem があれば "config"、埋め込みの画面なら "embed"（F-05）、status が ok でなければその状態、ok なら null。
			`visible(env)` は `.show`、`count(env)` は reason が null のときだけ agents の数（ほかは null）。

			欄（`panel.js` の `draw`）と詳しい画面（`scope.js`）は、`SCOPE_TABS.filter(tab => !tab.visible || tab.visible(env))` の並びでタブの帯を描き、そのキーを `pickTab` に渡す（タブが消えたら既定のタブへ戻る。R-01）。
			`ctx.orca.subscribe` の知らせで、欄と詳しい画面は描き直す（タブの出し入れと数の札のため）。
			"""
	}
	"D-02": {
		title:     "一覧と選び"
		satisfies: ["R-02", "R-05", "F-02"]
		text: """
			一覧の項目は、`forScope` の worktree の並びの順、その中の要約の `agents` の順で、`{id, agentType, mark, worktreeId, branch, detail}`。
			選びのキーは要約のエージェントの `id`。欄は欄の中の選びの Map（iss-00587 の `params`。Scope を変えると空になる）に `agent` として、詳しい画面は問い合わせの `agent` に持つ（`env.param("agent")`、`env.paramLink("agent", id)`）。

			`pickAgent(agents, wanted)`（`agents_logic.js`、純粋）→ `{selected: agent | null, gone: bool, remember: string | null}`：
			- wanted が agents の id にある → その agent。
			- wanted があるが agents にない → selected null、gone true（F-02：「このエージェントはいなくなった」と示し、一覧を出す。残ったエージェントが1人でも自動で選ばない）。
			- wanted がなく agents が1人 → その agent、remember にその id（R-02：すぐに開き、選びとして覚える）。
			- ほか → selected null、gone false（「エージェントを選ぶ」）。

			remember があれば、描いた側がその場で選びを覚える：欄は `params.set("agent", id)`、詳しい画面は `history.replaceState` で問い合わせに `agent=<id>` を足す（シェルに、履歴を増やさずに今の道の問い合わせを1つ書き換え、`ctx.route` も合わせる口 `ctx.replaceParam(name, value)` を足す）。
			こうして、自動で開いた後は wanted があるので、そのエージェントが消えれば gone になり、別のエージェントへ移らない。人数が増えても選びは変わらない。
			gone の知らせは、人が一覧から選ぶ（wanted が変わる）か、別のタブ、別の Scope に移る（欄の Map が空になる、詳しい画面の道が変わる）まで残る。

			一覧の行と印は、タブの中身の HTML には入れず、置き場に後から描く（D-04）。各行は `env.paramLink("agent", id)` の `<a>`（欄は欄の中の選び、詳しい画面は問い合わせ。iss-00587 の文書の選びと同じ）で、中に印の置き場 `<span class="sd-orca" data-orca-agent="<id>"></span>`、種類、ブランチ（`sd-mono`）を持つ。文字は `esc` を通す。
			印は `ctx.orca.marks().renderAgentMarks(slot, {agents: [agent]}, {size: "sm", max: 1})` で描く（iss-00592 の `paintOrcaMarks` を待たずに作れるよう、iss-00591 の `ctx.orca` だけを使う。iss-00592 が先に入っていれば、その関数に寄せてよい）。
			エージェントが1人で選ばれているときは、一覧を1行の見出し（印、種類、ブランチ）にする。
			"""
	}
	"D-03": {
		title:     "詳細とチャットの iframe"
		satisfies: ["R-03", "R-04", "R-05", "R-07"]
		text: """
			選ばれたエージェントがあり reason が null のときだけ、次の文字列を描く（属性の順も決めておく。同じ入力なら同じ文字列）：
			`<iframe class="sd-agent" src="<origin><detail>&theme=<明暗>" title="エージェント：<種類>・<ブランチ>" referrerpolicy="no-referrer"></iframe>`。
			`<detail>` は要約の `agents[].detail`（`/embed/agent?id=<符号にした id>`）をそのまま使い、SpecDock が id を符号にし直さない。`<origin>` は `ctx.orca.origin`。明暗は `document.documentElement.dataset.theme`、なければ `prefers-color-scheme`。
			`sandbox` は付けない（orca-web の画面は同じオリジンの読み、トークン、送信を使うので、`allow-same-origin` と `allow-scripts` と `allow-forms` が要る。試しの画面（orca-web iss-00014）と同じ置き方。orca-web は `frame-ancestors` で置ける画面を SpecDock のオリジンに限っている）。
			iss-00593 の担当は、付けない形と、`allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox` を付けた形の両方で、読み、送信、「Orca で開く」が動くかを試し、付けても全部動くなら付ける。決めた形と理由を report.md に残す。
			SpecDock は iframe に `postMessage` しない。iframe の URL には `id` と `theme` のほかを載せない（R-04）。

			形と高さ：iss-00589 の文書と説明資料のタブと同じく、`<div class="sd-framebox" data-frame="agents">` の中に、`frameBar(<一覧の置き場>, null)` と iframe を並べる（一覧の置き場は D-04）。
			横の欄では `panel.css` の `.pn-body:is([data-tab="docs"], [data-tab="explanation"])` の規則に `[data-tab="agents"]` を足し、`.sd-agent` を `.sd-docframe, .sd-explain` と同じ規則に足す（`flex: 1; min-height: 240px`）。詳しい画面では `scope.css` の枠の高さの規則に `.sd-agent` を足す。
			理由の知らせ（D-05）と gone の知らせのときは枠を出さない。
			"""
	}
	"D-04": {
		title:     "描き直しで iframe を残し、Scope を変えたら外す"
		satisfies: ["R-05", "R-07", "F-02", "F-03"]
		text: """
			- タブの中身の HTML は、Scope の ID、選んだエージェントの（id、種類、ブランチ）、gone か「選ぶ」か、明暗、reason だけで決まる。ほかのエージェントの増減、一覧の並び、印や経過は入れない。
			  一覧は、中身の中の置き場 `<div class="sd-agents" data-orca-agents="<ScopeID>"></div>` に、`paintAgentList(root, env)`（`agents_tab.js`）が後から描く（置き場の `innerHTML` だけを書き換え、隣の iframe に触れない）。
			  `paintAgentList` は、欄と詳しい画面の描き直しの直後と、`ctx.orca.subscribe` の知らせのときに呼ぶ。
			- 欄：今の `shownHtml` の比べ方で、同じ文字列なら中身を置き換えない。Scope が変われば中身の文字列が変わるので、中身は置き換えられ、前の iframe は外れる（F-03）。
			- 詳しい画面：今の `scope.js` は描くたびに `root.innerHTML` で全体を置き換え、構造の改訂が変わるたび（`app.js` の `refresh`）と `ctx.orca` の知らせのたびに中の iframe が読み込み直しになる。`scope.js` を、見出しとタブの帯と中身の3つの要素に分け、中身（`.sd-tabpanel`）は前の HTML の文字列と同じで同じ Scope なら置き換えない（欄と同じ比べ方）。Scope の ID が変わったら（別の Scope へ移ったら）必ず置き換える。
			- 要約の読み直しで選んだエージェントがいなくなれば、`pickAgent` が gone を返し、HTML が変わって iframe が外れる（F-02）。
			- 明暗を変えたときは `theme` が変わるので、置き直しになる（R-07 が許す）。
			- node のテストで、同じ選びのまま一覧の項目が増えたり減ったりしても、タブの中身の HTML の文字列が同じであることを確かめる。
			"""
	}
	"D-05": {
		title:     "理由の知らせ"
		satisfies: ["R-06", "F-01", "F-05", "F-06", "F-07"]
		text: """
			reason があるときは iframe を描かず、タブの中に1つの `sd-callout`（`data-code="orca-<reason>"`）を描く。言葉：
			- loading：「orca-web を読んでいる」。
			- unreachable：「orca-web（<origin>）に届かない」と、確かめること「orca-web が動いているか、orca-web の ORCA_WEB_READ_ORIGINS がこの画面のオリジン（<location.origin>）を許しているか」。
			- orca-unreachable：「orca-web は動いているが、Orca に届いていない（connection.state：unreachable）」。orca-starting：「orca-web が Orca を読み始めたところ（connection.state：starting）」。
			- config：「設定の orca_web の節を読めない：<problem>」と、直すファイル（`config.json`）。
			- embed：「埋め込みの画面ではチャットを開けない」と、同じ道を埋め込みでなく開くリンク（`withoutEmbed(scope.path)`、`target="_blank"`）。
			状態が ok に戻れば reason が null になり、`pickAgent` は前の選び（欄の Map か問い合わせ）をそのまま使うので、同じエージェントのチャットに戻る（R-06）。
			`sendEnabled` が false のとき（F-06）、SpecDock は何も描き足さない（orca-web の画面が入力欄の下に理由を出す）。
			"""
	}
	"D-06": {
		title:     "書き込みに関わらないことの確かめ"
		satisfies: ["R-04"]
		text: """
			静的な確かめのテスト（Python、`tests/unit/infra/`）で、次の2つを確かめる。
			- この Epic と epic-00471 で足す画面のファイル（`core/orca.js`、`core/orca_match.js`、`views/_shared/orca_marks.js`、`views/_shared/agents_tab.js`、`views/_shared/agents_logic.js`。実装で名前が変われば、その名前の並び）に、orca-web の書き込みの口の道（`/api/token`、`/api/send/`、`/api/open`、`/api/settings`）と `postMessage` の文字列がない。
			- `src/spec_dock/assets/dashboard/` の JavaScript の `postMessage` は、今ある埋め込みの知らせ（`core/embed.js` の `window.parent.postMessage`、specdock.embed/v1）の1か所だけである。
			画面の確かめで、送信の間のネットワークの記録（headless Chrome の CDP の `Network.requestWillBeSent` の `frameId`）から、送信の口への要求がすべて iframe の文書から出ていることを report.md に残す。送る相手は plan.cue の確かめ専用の宛先だけ。
			"""
	}
	"D-07": {
		title:     "配る文書"
		satisfies: ["R-08"]
		text: "epic-00471 D-08 の連携の説明と同じ文書の同じ節に、エージェントのタブの条件、送信は orca-web の中で行われ既定で止まっていること（`sendEnabled`）、知らせの言葉の意味を足す。iss-00592 の節がまだなければ、iss-00593 が `docs/reference_cli.md` の設定の3段の節の後に「orca-web との連携」の節を作り、後に入る方が1つの節にまとめる。"
	}
}

compatibility: """
	- 共有のタブの並びに1つ足し、タブに任意の `visible` を足すだけで、ほかのタブの中身と問い合わせは変えない。`?tab=agents` でタブが出ない Scope を開くと、既定のタブになる。
	- 詳しい画面の描き方を3つの要素に分けるが、見た目は変えない（iss-00589 の写しと比べる）。
	"""

risks: [
	"orca-web の `/embed/agent` の契約（`id`、`theme`、`detail` の道）が変わるとチャットが出なくなる。SpecDock は `detail` をそのまま使うので、道の変更には追従する",
	"sandbox を付けない iframe は、利用者の操作があれば最上位の画面を移せる。orca-web は同じ PC の信頼するサービスで、frame-ancestors で置き場を限っている。D-03 で、付けても動く形なら付ける",
	"エージェントが多い worktree では一覧が長くなる。一覧は欄の中で上に置き、iframe の高さを残りで取るので、10人を超える場合は一覧を畳むかを iss-00593 の担当が写しで決める",
	"orca-web の宛先の指紋は、表示を固定した後の宛先の変化を止めるが、SpecDock が最初から別のエージェントを開けば守れない。そのため R-05 と F-02・F-03 を、SpecDock の側の失敗の条件として確かめる",
]
