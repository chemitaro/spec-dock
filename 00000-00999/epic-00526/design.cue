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
	- iss-00589 は、文書の枠が残りの高さをすべて使う形（`.pn-body` の flex と、詳しい画面の高さの決め方）を作る。
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
		satisfies: ["R-01", "F-04", "F-07"]
		text: """
			`SCOPE_TABS` の説明資料と概要の間に `{key: "agents", label: "エージェント", visible, count, render}` を足す。ほかのタブは `visible` を持たない（いつも出す）。
			env に `orca`（`ctx.orca`）と `structure`（`ctx.data`）を足す（`pageEnv`、`panelEnv`）。

			`agentsVisibility(env)`（`agents_logic.js`、純粋）→ `{show: bool, reason: null | "loading" | "unreachable" | "orca-unreachable" | "orca-starting" | "config" | "embed", agents: [...]}`：
			上から順に決める。
			- `orca.status()` が off で、`server.orca_web.problem` がない（利用者が切った）→ show false（F-07）。
			- Scope の構造の項目の `worktrees`（epic-00471 D-03）が空 → show false（F-04：記録がなければ推し量らない）。
			- `server.orca_web.problem` がある（設定の節が壊れて off になった）→ show true、reason "config"（F-07）。
			- 埋め込みの画面（`ctx.embed`）→ show true、reason "embed"（F-05）。
			- status が ok → `forScope` の worktree の並びの agents を連ねたものが1つ以上なら show true（reason null）、なければ show false。
			- status が loading、unreachable、orca-unreachable、orca-starting → show true、reason にその状態。
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
			選びのキーは要約のエージェントの `id`。欄は欄の中の選びの Map（iss-00587 の `params`）に `agent` として、詳しい画面は問い合わせの `agent` に持つ（`env.param("agent")`、`env.paramLink("agent", id)`）。

			`pickAgent(agents, wanted)`（`agents_logic.js`、純粋）→ `{selected: agent | null, gone: bool}`：
			- wanted が agents の id にある → その agent。
			- wanted があるが agents にない → selected null、gone true（F-02：「このエージェントはいなくなった」と示し、一覧に戻す）。
			- wanted がなく agents が1人 → その agent（R-02：すぐに開く）。
			- ほか → selected null、gone false（「エージェントを選ぶ」）。
			一覧の各行は `<button data-pn-param="agent">`（欄）か `<a ... href="?agent=">`（詳しい画面）で、中に印の置き場 `<span class="sd-orca" data-orca-agent="<id>"></span>`、種類、ブランチ（`sd-mono`）を持つ。印は、中身を描いた直後と `ctx.orca.subscribe` の知らせのときに、`ctx.orca.marks().renderAgentMarks(slot, {agents: [agent]}, {size: "sm", max: 1})` で描く（iss-00592 の `paintOrcaMarks` を待たずに作れるよう、iss-00591 の `ctx.orca` だけを使う。iss-00592 が先に入っていれば、その関数に寄せてよい）。
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

			高さ：横の欄では `.pn-body[data-tab="agents"]` を、iss-00589 の文書のタブと同じ flex の列にし、`.sd-agent` は `flex: 1; min-height: 320px`。詳しい画面では、iss-00589 が文書の枠に使う高さの決め方を `.sd-agent` にも当てる。数値は iss-00589 の結果に合わせ、iss-00593 の担当が写しで確かめる。
			"""
	}
	"D-04": {
		title:     "描き直しで iframe を残し、Scope を変えたら外す"
		satisfies: ["R-05", "R-07", "F-02", "F-03"]
		text: """
			- タブの中身の HTML は、Scope の ID、一覧の項目（id、種類、ブランチ）、選び、明暗、reason だけで決まる。印は置き場に後から描くので、印や経過が変わっても HTML の文字列は変わらない。
			- 欄：今の `shownHtml` の比べ方で、同じ文字列なら中身を置き換えない。Scope が変われば一覧と title が変わるので、中身は置き換えられ、前の iframe は外れる（F-03）。
			- 詳しい画面：`scope.js` を、見出しとタブの帯と中身の3つの要素に分け、中身（`.sd-tabpanel`）は前の HTML の文字列と同じなら置き換えない（欄と同じ）。Scope の ID が変わったら（別の Scope へ移ったら）必ず置き換える。
			- 要約の読み直しで選んだエージェントがいなくなれば、`pickAgent` が gone を返し、HTML が変わって iframe が外れる（F-02）。
			- 明暗を変えたときは `theme` が変わるので、置き直しになる（R-07 が許す）。
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
			静的な確かめのテスト（Python、`tests/unit/infra/`）で、`src/spec_dock/assets/dashboard/` の JavaScript に、orca-web の書き込みの口の道（`/api/token`、`/api/send/`、`/api/open`、`/api/settings`）と `postMessage` の文字列がないことを確かめる。
			画面の確かめで、送信の間のネットワークの記録（headless Chrome の CDP の `Network.requestWillBeSent` の `frameId`）から、送信の口への要求がすべて iframe の文書から出ていることを report.md に残す。
			"""
	}
	"D-07": {
		title:     "配る文書"
		satisfies: ["R-08"]
		text: "epic-00471 D-08 で足した連携の説明の続きに、エージェントのタブの条件、送信は orca-web の中で行われ既定で止まっていること（`sendEnabled`）、知らせの言葉の意味を足す。"
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
