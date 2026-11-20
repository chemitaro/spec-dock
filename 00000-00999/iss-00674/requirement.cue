package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの表示だけを変える。誤りは名前の誤りにとどまり、版を戻せば回復できる"
}

purpose: """
	ダッシュボードで、エージェントの種類を、orca-web の部品が書き出す名前（Claude、Codex、Antigravity、Gemini など）で出す（親 epic-00672 の R-03、F-02、D-02）。
	"""

background: """
	統括が確かめた事実（epic-00672 の background、2026-11-20、spec-dock main 83b8ee95f、orca-web main 58275ea）：
	- ダッシュボードは種類を `agentType` の生の文字列で出す。該当は、エージェントのタブの選び（`views/_shared/agents_tab.js` の `stripHtml`）、
	  横の欄の iframe の title（`views/_shared/agents_logic.js` の `agentFrame`）、構造の図の指揮の帯のエージェントの詳細の欄の見出し（`views/graph/command_view.js` の `renderAgentPanel`）と
	  worktree の詳細の欄のエージェントの一覧（同 `renderWorktreePanel`）、未対応の行の数の札の title（`views/graph/unscoped.js` の `countTitle`）の5か所。
	- orca-web の部品 `/embed/agent-marks.js` は `AGENT_ICONS`（鍵 → `{label, viewBox, paths}`）と `iconKey(agentType)`（`claude`・`codex`・`other`・`none`）を書き出す。
	  ダッシュボードは `core/orca.js` でこれを読み、`orca.marks()` が部品（読めていなければ null）を返す。部品は要約より先に入る（`load` が `module` を置いてから要約を見張る）ので、エージェントが画面に出るときには部品がある。
	- orca-web の iss-00066（epic-00065）が、`iconKey` に `antigravity`・`gemini` を、`AGENT_ICONS` にその `label`（『Antigravity』『Gemini』）を、書き出しの形を変えずに足す。並んで進んでいる。
	"""

includes: [
	"`views/_shared/agents_logic.js`（import のない純粋な部品）に、部品から種類の名前を引く関数を1つ置き、上の5か所がそれを通す",
	"名前の関数の node のテストと、5か所が名前を出すことのテスト（合成の部品で）",
	"orca-web の iss-00066 のマージと常駐の orca-web の立て直しの後に、実データで Antigravity のエージェントが『Antigravity』と出ることの確かめ（report.md に残す）",
]

excludes: [
	"稼働の印のアイコンそのもの（orca-web が描く。epic-00065）",
	"名前の表を SpecDock に写して持つこと",
	"モデルごとの名前（Orca が種類に入れていない。epic-00672 の decisions）",
	"`aria-label` など、今 `agentType` を使っていない所に名前を足すこと",
]

requirements: {
	"R-01": {
		title: "5か所で、種類が部品の名前で出る"
		text: """
			部品が `AGENT_ICONS` と `iconKey` を書き出していて、`iconKey(agentType)` が `other`・`none` でない表の鍵を返し、その項目に空でない `label` があるとき、
			エージェントのタブの選び、横の欄の iframe の title、指揮の帯のエージェントの詳細の欄の見出し、worktree の詳細の欄のエージェントの一覧、未対応の行の数の札の title で、
			`agentType` の文字列の代わりにその `label` を出す。
			"""
		acceptance: [
			"表に `antigravity`（label『Antigravity』）を持つ合成の部品で、`agentType` が `antigravity` のエージェントが、5か所それぞれで『Antigravity』と出る",
			"`agentType` が `claude` のエージェントが、今の部品（orca-web main 58275ea の表）の形の合成の部品で『Claude』と出る",
			"orca-web の iss-00066 の後の常駐の orca-web で、実際の Antigravity のエージェントがダッシュボードで『Antigravity』と出る（統括の知らせの後に確かめ、report.md に残す）",
		]
	}
	"R-02": {
		title: "名前を引けないときは、今の文字を出す"
		text: """
			部品が知らない種類（`iconKey` が `other`）、表に鍵がない、`label` がない、のときは `agentType` の文字列を出す。
			`agentType` がない（null、空の文字列、文字列でない）ときは、各所の今の既定の文字（『種類不明』、未対応の行の数の札は `agent`）を出す。
			"""
		acceptance: [
			"表に `antigravity` のない合成の部品（今の orca-web の形）で、`agentType` が `antigravity` なら `antigravity` と出る",
			"`agentType` がないエージェントは『種類不明』（数の札は `agent`）と出る",
			"部品を渡さない、または部品が null の今のダッシュボードのテストが、変えずにそのまま通る",
		]
	}
}

failures: {
	"F-01": {
		title: "部品がない、表がない、部品が壊れているときは、今どおり描く"
		text:  "部品が null、`AGENT_ICONS` か `iconKey` を書き出していない古い部品、`iconKey` が例外を投げる部品のときは、名前を引かず、`agentType`（なければ既定の文字）で描き、エラーにしない（epic-00672 の F-02）。"
	}
}

constraints: [
	"名前の正本は orca-web の `AGENT_ICONS`（`web/embed/agent-marks-icons.js`）の1か所。SpecDock は部品の書き出しを読むだけで、表を写さない（epic-00672 の constraints）",
	"名前の関数は純粋（import なし、DOM・window・fetch を使わない）。純粋な部品（`agents_logic.js`、`unscoped.js` など）には、呼ぶ側から部品を渡す",
	"今の関数の呼び方を壊さない：部品の引数は省けて、省けば今の表示になる",
	"環境に固有の名前で規則を分けない。公開の文書とテストに、この PC の実際のパスやセッションの id を書かない",
]

decisions: [
	"2026-11-20 統括（依頼書）：名前の正本は orca-web の `AGENT_ICONS`。`views/_shared/` に純粋な関数を1つ（例 `agentTypeLabel(marks, agentType, fallback)`）置き、5か所がそれを通す。知らない種類・部品なし・表なしは今の文字。",
	"2026-11-20 統括（依頼書）：作るのは orca-web の iss-00066 を待たずに始め、node のテストは合成の部品で確かめる。実データの確かめは統括の知らせの後。",
	"2026-11-20 タスク担当：『`agentType` がない』は、null・undefined・空の文字列・文字列でない値とする。今の5か所のうち、`agents_tab.js`・`agents_logic.js` は `scopeAgents` の `text()` で空を null にした値を受けるので、表示は変わらない。",
]
