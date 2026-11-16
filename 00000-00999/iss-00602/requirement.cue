package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル。正本はここだけ。
assurance: {
	level:  "strict"
	reason: "選びの直しは、違う相手のチャットが開く道を閉じるため。エージェントのタブの選びは、送信できる orca-web のチャットの相手を決める（iss-00593 と同じ考え）"
}

purpose: "iss-00601 が調べた、エージェントのタブ（iss-00593）と構造の図の印の押し（iss-00592）の5つの小さな点を、すべて直す。"

background: """
	親は epic-00526（ダッシュボードからエージェントを操作する）。エージェントのタブは iss-00593 が、印の押しで横の欄のエージェントのタブを開く口は iss-00592 が作った。iss-00593 の最終品質ゲートで「記録だけ」とした5点を、iss-00601 が main `16f0cf122` で読み直し、5点ともコードの筋道の上で起きると報告した（report.md）。どれも別の相手のチャットを開く・別の相手に送る道ではない（安全側）が、2点（1、3）は人が普通にする操作で起き、1点（2）は狭い条件で iss-00593 の R-05（いなくなった後に残った相手を自分で開かない）の意図に反しうる。

	統括の決定（依頼書 task_a02f6618c98b と、本人の判断の伝え msg_0b6b7a71a08b、2026-11-16）：

	- iss-00601 の report.md の5点をすべて直す（本人が了承）。直し方は調べの案を出発点にし、それぞれを再現するテストを足す。
	- 依頼書にあった「稼働しているエージェントをすべて印で出す」は、本人の判断で行わない。印の上限（構造の図の箱と枠、横の欄の見出し、ボードの札）、並び（orca-web の部品の順）、構造の図の箱の高さは今のまま。
	- 保証レベル strict、仕様のレビューと最終品質ゲートを省かない。

	今の状態（main `16f0cf122` を読んだ事実）：

	- `views/_shared/agents_tab.js` の `agentsState` は `wanted = env.param("agent") ?? mem.last`。`agents_logic.js` の `pickAgent` は、wanted が agents にいれば remember null を返す。`agentsTab` は `pick.remember` があるときだけ `env.keep("agent", …)` を呼ぶ。
	- 詳しい画面の `env.keep` は `ctx.replaceParam`（`app.js`。履歴を増やさず `state.route` も書き換える）、横の欄の `env.keep` は欄の Map（`params`）に書く。
	- `app.js` の `navigate` は、Scope か agent（問い合わせの `agent`）が前の道と違う移りで `dropAgentFrames()`（`iframe.sd-agent` を外す）を呼ぶ。
	- `views/_shared/panel.js` の足の「詳しい画面」と「新しいタブで開く」は `params.get("agent") ?? null`。`hide()` は `params` を空にする。覚え（`agents_tab.js` の `mem`）は同じ Scope の間は残る。
	- `paintAgentList` の帯の捕捉の段の聞き手は、修飾キーを見ずに `forgetGone(mem, id)` を呼ぶ（iss-00593 の D-04「修飾キーの有無によらず」）。
	- `agents_logic.js` の `scopeAgents` は、`agents` が並びでない worktree を数えずに飛ばす。
	- `views/graph.js` の `onTap` は、`isPhone() && V.sel === id` のとき `goDetail(id)` して戻り、その判定が印（`.sd-orca`）の判定より前にある。
	- orca-web の README の要約の契約：`summary.worktrees[i]` は `{ id, path, branch, project, issue, counts, agents }` で、`agents` は並び（エージェントが1人以上いる worktree だけが要約に入る）。
	"""

includes: [
	"iss-00601 の 1：覚え（last）から開いた相手を agent として書き、今の相手を帯で押しても枠を置き直さないこと",
	"iss-00601 の 2：横の欄の足のリンクが、欄の選びか、同じ Scope の覚えを持つこと",
	"iss-00601 の 3：スマホの構造の図で、選んだ箱の印の押しがエージェントのタブを開くこと",
	"iss-00601 の 4：修飾キーつきの押しが元の画面の覚えを変えないこと",
	"iss-00601 の 5：agents が並びでない worktree を形の違いに数えること",
	"それぞれを再現する node のテストと、配る文書（reference_cli.md）の説明の更新",
]

excludes: [
	"印の上限、並び、見た目、構造の図の箱の高さと幅を変えること（本人の判断で行わない）",
	"orca-web の側の変更（部品、要約、同じセッションの二重の数え。orca-web の iss-00039）",
	"エージェントのタブの帯の形、知らせの言葉と data-code を変えること",
	"SpecDock のサーバーと API の変更",
]

requirements: {
	"R-01": {
		title: "詳しい画面で、覚えから開いた今の相手を帯で押しても、チャットの枠を置き直さない（iss-00601 の 1、FQG-003）"
		text: """
			問い合わせや欄の Map に `agent` がなく、同じ Scope で最後に開いた相手（覚えの last）を開いたときは、その相手の id を `agent` として書く（詳しい画面は履歴を増やさない問い合わせの書き換え、欄は欄の Map）。すると、帯の今の相手を押す移りは Scope も agent も変わらない移りになり、`iframe.sd-agent` を外さない。書きかけの本文は消えない。
			"""
		acceptance: [
			"agent のない env（詳しい画面の道に agent がない、欄の Map が空）で、覚えの last の A が agents にいて2人以上いるとき、agentsTab が keep を (\"agent\", \"A\") で1回呼び、iframe が A",
			"同じ条件で A が1人だけのときも keep を (\"agent\", \"A\") で呼ぶ（今のまま）",
			"agent が問い合わせか欄の Map にある env では、keep を呼ばない（今のまま）",
			"実機で、欄を閉じて開き直す → 足の「詳しい画面」→ 帯の今の相手 A を押す、の後で、iframe の読み込みの回数が増えず、入力欄の書きかけの本文が残る",
		]
	}
	"R-02": {
		title: "横の欄の足のリンクが、欄の今の選びか、同じ Scope の覚えを持つ（iss-00601 の 2）"
		text: """
			横の欄の足の「詳しい画面」と「新しいタブで開く」は、欄の Map の `agent`（ただし、それが生の id で、同じ Scope の覚えがその id をいなくなったと知っていれば `gone:<id>`）を、なければ同じ Scope の覚え（最後に開いた相手。それがいなくなっていれば `gone:<id>`。最後に開いた相手がなく、いなくなった相手だけを覚えていれば、最初に覚えた1人の `gone:<id>`）を、`agent` として持つ。覚えが別の Scope のものなら持たない。欄が今どのタブを見ているかによらない。
			"""
		acceptance: [
			"欄の Map が空で、覚えが同じ Scope の last A（いなくなっていない）なら、足の2つのリンクに `agent=A` がある",
			"同じで A がいなくなった覚えなら `agent=gone%3AA`（`gone:A`）",
			"覚えが別の Scope なら、足のリンクに agent がない",
			"欄が概要のタブを見ていても、上の3つが同じ",
			"欄の Map に agent があれば、それが覚えより先",
			"欄の Map が生の id A を持ち、同じ Scope の覚えが A をいなくなったと知っていれば（ほかのタブを見ている間に A がいなくなった）、足のリンクは `agent=gone%3AA`。その後 A が戻っても、そのリンクの新しいタブで A が開かない（最終品質ゲートの ChatGPT の FQG-00602-01、主の FQG-001）",
			"実機で、残り1人の B だけがいて A がいなくなった覚えのある Scope の欄を概要のタブで開き、足の「新しいタブで開く」の道をエージェントのタブで開くと、B が自動で開かず「いなくなった」の知らせが出る",
		]
	}
	"R-03": {
		title: "スマホの構造の図で、選んだ箱の印を押すと、詳しい画面に移らずエージェントのタブを開く（iss-00601 の 3）"
		text: "幅 640px 以下で、すでに選んだ箱（または枠の見出し）の印の置き場を押したときも、1回目と同じく、その Scope を選んだまま横の欄のエージェントのタブを選ぶ。印の外の2回目の押しは、今のまま詳しい画面へ移る。PC の幅の動き（印を押すと選んでエージェントのタブ）は変わらない。"
		acceptance: [
			"`onTap` で、印の置き場の判定が「スマホで選んだ箱の2回目の押し」の判定より前にあり、選んでいない箱なら select の後に preferTab(\"agents\") を呼んで戻る",
			"実機（390px）で、選んだ箱の印をもう一度押すと、道が変わらず、欄のエージェントのタブが選ばれる。印の外を押すと詳しい画面に移る",
		]
	}
	"R-04": {
		title: "修飾キーつきの押しで新しいタブに開くとき、元の画面の覚えを変えない（iss-00601 の 4）"
		text: "帯の項目と「選んだエージェントに戻す」の押しのうち、主ボタンで修飾キー（Ctrl・Cmd・Shift・Alt）のない押しだけが、その Scope のいなくなった覚えを捨て、選びを覚える。修飾キーつきの押しや主ボタンでない押しは覚えを変えない。iss-00593 の D-04 の「修飾キーの有無によらず」を、この要件で改める。"
		acceptance: [
			"帯の捕捉の聞き手が、button 0 で修飾キーのない押しでだけ forgetGone を呼ぶ（Ctrl・Cmd・Shift・Alt のそれぞれと button 1 では呼ばず、覚えの gone・picked・last・drift が変わらない）",
			"修飾キーのない押しでは、今のまま forgetGone を呼び、既定の動きを止めない",
			"実機で、帯の別の相手を Cmd で押した後、元のページで欄を閉じて開き直しても、前の相手（または選ぶの知らせ）のままで、押した相手が開かない",
		]
	}
	"R-05": {
		title: "agents が並びでない worktree を、形の違いとして数える（iss-00601 の 5）"
		text: "対応した worktree のうち、オブジェクトで `agents` が並びでない（欠け、null、オブジェクト、文字など）ものは、形の違う項目1件として数える。使えるエージェントがなく形の違いだけがあれば、エージェントのタブは「形が違う」の知らせ（orca-shape）を出し、選んでいた相手がいなくなったとは決めない（覚えにも問い合わせにも gone を足さない）。"
		acceptance: [
			"`scopeAgents([{id: \"w1\", agents: {id: \"A\"}}])` の invalid が1、agents が空、invalidIds が空",
			"agents の欠け・null・文字の worktree も invalid が1",
			"その要約で wanted が A のとき、agentsVisibility の理由が shape で、agentsState の後で覚えの gone に A がなく、agentsTab が keep を呼ばない",
			"並びの agents を持つ worktree（使える2人）と並びでない worktree が混ざるときは、使える agents が2、invalid が1",
			"実機で、要約の応答の agents をオブジェクトに差し替えると、選んでいた相手のタブに orca-shape の知らせが出て、差し替えを外すと同じ相手に戻る",
		]
	}
	"R-06": {
		title: "配る文書が、選びの持ち方の直しを説明する"
		text: "`reference_cli.md` のエージェントのタブの節に、欄の足のリンクが欄の選び（なければ同じ Scope の覚え、いなくなっていれば `gone:<id>`）を持つこと、修飾キーつきの押しが元の画面の覚えを変えないこと、`agents` が並びでない worktree が形の違い（orca-shape）に数えられることを書く。実際の Tailscale の IP と利用者の絶対パスを書かない。"
		acceptance: [
			"reference_cli.md のエージェントのタブの節に、上の各点の文がある（Python のテスト）",
			"static-inventory.json の sha256 が合う（今の inventory のテスト）",
		]
	}
}

failures: {
	"F-01": {
		title: "覚えの last がいなくなっているときは、`agent` に id ではなく `gone:<id>` を書き、足のリンクも `gone:<id>` を持つ"
		impact: "いなくなった相手の id をそのまま書くと、新しいタブでその id が戻ったときに開く。足のリンクに何も書かないと、新しいタブで残った1人が自動で開く（iss-00593 の R-05 の意図に反する）"
		recovery: "今の pickAgent の規則（覚えの gone にある id は remember に gone:<id>）を保ち、その値を keep に先に使う。足のリンクは footChoice が、欄の Map の生の id でも覚えの gone にあれば gone:<id> を、Map がなければ lastChoice の gone:<id> を返す"
	}
	"F-02": {
		title: "覚えが別の Scope のものなら、足のリンクに使わない"
		impact: "前の Scope の相手の id を別の Scope の足のリンクに付けると、新しいタブで、その Scope に関係のない選びが付く"
		recovery: "lastChoice は覚えの scopeId が欄の Scope と同じときだけ値を返す。agentsState は memoryFor で別の Scope の覚えを捨てる（今のまま）"
	}
	"F-03": {
		title: "形の違いの知らせの間は、選びを書き換えない"
		impact: "形の違う要約の間に keep で `agent` や `gone:<id>` を書くと、orca-web が直った後も選びがずれる、またはいなくなったと残る"
		recovery: "理由が null でないとき agentsTab は pickAgent も keep も呼ばない（今のまま）。D-05 で並びでない agents が理由 shape になるので、その間は書かない"
	}
}

constraints: [
	"orca-web のファイルを変えない",
	"印の上限・並び・見た目と、構造の図の配置（`layout.js`、`SIZE`）を変えない",
	"書いてよいのは src/spec_dock/（ダッシュボードの資産と配る文書）、tests/、src/spec_dock/assets/static-inventory.json、この Issue の Scope のディレクトリ",
	"常駐のダッシュボード（47800）と常駐の orca-web（8791）の設定を変えず、止めない。送信しない",
]

decisions: [
	"iss-00601 の5点をすべて直す：統括（依頼書 task_a02f6618c98b、2026-11-16。本人が了承）",
	"「すべての印を出す」は行わず、印の上限・並び・箱の高さは今のまま：本人の判断（統括の伝え msg_0b6b7a71a08b、2026-11-16）",
	"`agents` の欠けと null も形の違い：タスク担当（orca-web の README の契約で agents は必ずある並び。iss-00601 の項目5の残り）",
	"iss-00593 の D-04 の「修飾キーの有無によらず」を R-04 で改める：統括の「5点をすべて直す」の項目4の直し",
	"欄の足のリンクで、last がなく gone だけを覚えているときは最初に覚えた1人の gone:<id>：タスク担当（新しいタブで残った1人が自動で開くのを防ぐ最小の印。どの id でも新しいタブの pickAgent は gone として扱う）",
	"欄の Map の生の id も、同じ Scope の覚えがいなくなったと知っていれば足のリンクで gone:<id> にする：タスク担当（2026-11-16、最終品質ゲートの ChatGPT の P1 FQG-00602-01 と主の P3 FQG-001 の同じ根。iss-00593 の R-05「同じ id が戻っても人が選び直すまで開かない」と F-01 に合わせる仕様の直し）",
]

questions: []
