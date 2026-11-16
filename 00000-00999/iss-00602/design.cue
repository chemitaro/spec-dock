package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"iss-00601 の案どおり、5点をそれぞれ数行で直す。決め方は純粋な関数に置き、node のテストで各点を再現してから直す",
	"選びの規則（pickAgent の規則、いなくなった印、ほかの相手に自動で移らないこと）は変えない",
]

current: """
	- `agentsState`（agents_tab.js）：`wanted = env.param("agent") ?? mem.last`。`agentsTab`：`if (pick.remember) env.keep("agent", pick.remember)`。
	- `pickAgent`（agents_logic.js）：wanted が gone:<id> → remember null、addGone。wanted が覚えの gone にある → remember gone:<id>。wanted が agents にいる → remember null。wanted が agents にいない → remember gone:<id>。wanted なしで gone がある → 選ばない。wanted なしで1人 → その人と remember id。
	- 欄の足（panel.js の draw）：`withParam(…, "agent", params.get("agent") ?? null)`。
	- 帯の捕捉（paintAgentList）：`if (item) forgetGone(mem, item.dataset.agentPick)`。
	- `scopeAgents`：`if (!worktree || typeof worktree !== "object" || !Array.isArray(worktree.agents)) continue;`。
	- `onTap`（graph.js）：`hit` と `id` の後、`if (isPhone() && V.sel === id) { goDetail(id); return; }`、`if (V.sel !== id) select(id);`、`if (target.closest(".sd-orca")) V.pn?.preferTab("agents");`。
	"""

target: "上の5か所を D-01〜D-05 のとおりに直し、配る文書を D-06 のとおりに直す。ほかの動きは変えない。"

design: {
	"D-01": {
		title: "スマホの構造の図で、印の押しを2回目の押しより先に見る（graph.js の onTap、iss-00601 の 3）"
		text: """
			`onTap` の、`hit` と `id` を決めた後を次の順にする：
			1. `target.closest(".sd-orca")` なら、`V.sel !== id` のとき `select(id)`、続けて `V.pn?.preferTab("agents")` を呼んで戻る。
			2. `isPhone() && V.sel === id` なら `goDetail(id)` して戻る。
			3. `V.sel !== id` なら `select(id)`。
			片付けの候補の押しと、箱の外の押しの扱いは今のまま。今の静的なテストの「`select(id)` が `preferTab` より前」は成り立つ。
			"""
		satisfies: ["R-03"]
	}
	"D-02": {
		title: "覚えから開いた相手も agent として書く（agents_tab.js、iss-00601 の 1）"
		text: """
			- `agentsState`：`const asked = env.param("agent")`、`wanted = asked ?? mem.last`、返す state に `fromLast: asked == null && mem.last != null` を足す（`states` の WeakMap に入るので、同じ env では1回だけ決まる）。
			- `agentsTab`：`const remember = pick.remember ?? (state.fromLast && pick.selected ? pick.selected.id : null)`、`if (remember) env.keep("agent", remember)`。
			- 覚えの last がいなくなっている（覚えの gone にある、または agents にいない）ときは、pickAgent が `gone:<id>` を remember に返し、その値が先になる（F-01）。
			- 詳しい画面の `keep` は `ctx.replaceParam` なので、その後の帯の今の相手の押しは、`navigate` の比べで agent が同じ（`state.route` も書き換わっている）になり、`dropAgentFrames` を呼ばない。欄の `keep` は欄の Map に書き、帯のリンクと足のリンクに入る。
			- 1人だけのとき（今の remember）と、問い合わせか欄の Map に agent があるとき（fromLast false）は今のまま。理由が null でないときは agentsTab が早く戻るので書かない（F-03）。
			"""
		satisfies: ["R-01", "F-01", "F-03"]
	}
	"D-03": {
		title: "欄の足のリンクが覚えを持つ（agents_logic.js の lastChoice、panel.js、iss-00601 の 2）"
		text: """
			- `agents_logic.js` に純粋な `lastChoice(mem, scopeId)`：`mem.scopeId !== scopeId` なら null（F-02）。`mem.last` があれば、`mem.gone.has(mem.last)` なら `"gone:" + mem.last`、なければ `mem.last`。`mem.last` がなく `mem.gone` が空でなければ、`mem.gone` の最初の id の `"gone:" + id`（Set の入れた順）。ほかは null。
			- `panel.js` の `draw` の足：`withParam(withParam(withoutEmbed(scope.path), "agent", params.get("agent") ?? lastChoice(mem, scope.id)), "tab", tab ?? "summary")`。`mem` は `agents_tab.js` の export を import する。足は中身を描いた後に作るので、同じ描きで覚えた last（noteShown）が入る。
			- 欄の Map が gone:<id> を持つとき（agentsTab の keep）は、Map が先（今のまま）。
			"""
		satisfies: ["R-02", "F-01", "F-02"]
	}
	"D-04": {
		title: "修飾キーのない主ボタンの押しだけが覚えを変える（agents_tab.js、iss-00601 の 4）"
		text: """
			`paintAgentList` の捕捉の段の聞き手：`if (item && event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) forgetGone(mem, item.dataset.agentPick)`。既定の動きは止めない（今のまま）。この判定は `panel.js` の `plainClick` と `app.js` の `interceptLinks` と同じ（その2つは修飾キーつきの押しを新しいタブの既定の動きに任せる）。iss-00593 の D-04 の「修飾キーの有無によらず」をここで改める。
			"""
		satisfies: ["R-04"]
	}
	"D-05": {
		title: "agents が並びでない worktree を形の違いに数える（agents_logic.js の scopeAgents、iss-00601 の 5）"
		text: """
			`scopeAgents`：worktree がオブジェクトでなければ（null を含む）今のまま飛ばす。オブジェクトで `agents` が並びでなければ（欠け、null を含む）`invalid += 1` として次へ（id がないので `invalidIds` は変えない）。使える agents がなく invalid があれば、`agentsVisibility` の `noneUsable` で理由 shape になり、`agentsState` は覚えに足さず、`agentsTab` は keep を呼ばない（F-03）。使える agents があれば、今の「形の違う N件は出していない」の注に、その worktree の1件が入る。
			"""
		satisfies: ["R-05", "F-03"]
	}
	"D-06": {
		title: "配る文書（reference_cli.md）"
		text: """
			- エージェントのタブの節の「選び」に：横の欄の足の「詳しい画面」と「新しいタブで開く」は、欄の今の選び（なければ同じ Scope の最後に開いた相手、いなくなっていれば `gone:<id>`）を持つ。問い合わせに `agent` がない詳しい画面で、最後に開いた相手を開いたときも、その相手を問い合わせに書く（履歴は増えない）。
			- 「いなくなったとき」の「人がその Scope で選ぶと覚えを捨てます」に：修飾キーつきの押しで新しいタブに開くときは、元の画面の覚えを変えない。
			- 知らせの表の `orca-shape` の意味に：対応した worktree の `agents` が並びでないときも形の違いに数える。
			- static-inventory.json の reference_cli.md の sha256 を合わせる。
			"""
		satisfies: ["R-06"]
	}
}

seams: """
	- D-02、D-04：`tests/unit/infra/test_dashboard_agents_tab_js.py` の偽の env と偽の root（keep の呼び、捕捉の聞き手の修飾キー）。
	- D-03：`tests/unit/infra/test_dashboard_agents_logic_js.py`（lastChoice）と、`tests/unit/infra/test_dashboard_orca_views_js.py` の欄の偽の DOM（PANEL_DOM）で足の HTML の agent。
	- D-05：`test_dashboard_agents_logic_js.py`（scopeAgents）と `test_dashboard_agents_tab_js.py`（agentsState と agentsTab の shape）。
	- D-01：`test_dashboard_orca_views_js.py` の onTap の静的な目印と、実機の 390px の押し。
	- D-06：`tests/unit/infra/test_issue593_agents_docs.py` に足す。
	"""

compatibility: "エージェントのタブの選びは、覚えからの選びを問い合わせ（詳しい画面、履歴は増えない）か欄の Map に書くようになる。欄の足のリンクに agent が付く場面が増える。修飾キーつきの押しが元の画面の覚えを変えなくなる（iss-00593 の D-04 からの変更）。agents が並びでない要約では、いなくなったの代わりに形の違いの知らせが出る。API とサーバーは変わらない。"

risks: [
	"覚えからの選びを問い合わせに書くので、詳しい画面の URL に agent が付く場面が増える。共有した URL を開いた人には、その相手が選ばれる（今も agent の付いた URL は同じ動き）",
	"lastChoice が gone だけを覚えているときの id は最初の1人だけで、ほかのいなくなった id は新しいタブに伝わらない。新しいタブでは gone:<id> で自動の選びが止まるので、別の相手は開かない",
]
