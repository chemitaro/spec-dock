package spec

// 要件（Epic）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "仕様の読み書きの権限の確かめと案内、ダッシュボードの種類の名前を、Antigravity と Gemini に広げる。表示と案内の範囲で、誤りは版を戻せば回復できる"
}

purpose: """
	Orca に Antigravity CLI（`agy`）が入り、Gemini などのモデルのエージェントが SpecDock の作業者として動くようになった。
	Antigravity のエージェントが、Claude Code や Codex と同じように、作業用の worktree で仕様のカタログを読み書きでき、
	SpecDock のダッシュボードでも、種類の名前とアイコンが Claude・Codex と同じ扱いで見えるようにする。
	"""

background: """
	本人の依頼（2026-11-20）：Orca に Antigravity CLI を導入した。Gemini などの各モデルも動く。SpecDock が対応しているかを確かめ、足りないところを直す。

	統括が確かめた事実（2026-11-20、spec-dock main 83b8ee95f、orca-web main 58275ea、Orca 1.4.263、agy 1.5.12）：
	- Orca は Antigravity のエージェントを `agentType: "antigravity"`、Gemini CLI を `"gemini"` で報告する（Orca の配布物の `agent-hook-listener/providers/{antigravity,gemini}`）。モデル（Gemini 3.8 Flash など）は `agentType` に入らない。
	- ダッシュボードの稼働の印のアイコンは、SpecDock ではなく orca-web の部品（`/embed/agent-marks.js`、表は `web/embed/agent-marks-icons.js`）が決める。表には `claude`・`codex` しかなく、ほかは中立の『ほかの種類』になる。これは orca-web の epic-00065 が直す。
	- ダッシュボードは種類を `agentType` の生の文字列で出す（`views/_shared/agents_tab.js:130`、`agents_logic.js:93`、`graph/command_view.js:243`・`308`、`graph/unscoped.js:56`）。種類で処理を分けるところはない。
	- Antigravity は `.agents/skills/` と `AGENTS.md` を読む（公式の資料 https://antigravity.google/docs/skills ）。SpecDock の配るスキルと指示は、そのまま届く。
	- `canonical status` の `tools` と `docs/canonical.md` は、Codex（`CODEX_SANDBOX`、`writable_roots`）と Claude Code（`CLAUDECODE`、`permissions.additionalDirectories`）だけを扱う。作業用の worktree のカタログは作業ディレクトリの外にある。`agy` には作業範囲を足す `--add-dir` と、端末を制限する `--sandbox` がある。Antigravity が範囲の外への読み書きを拒むか、Antigravity の中だと分かる環境変数があるかは、まだ確かめていない。
	"""

includes: [
	"Antigravity のエージェントが作業用の worktree で仕様のカタログを読み書きするのに要る設定を確かめ、要るなら `canonical status` の `tools` に Antigravity の項目と設定の1行を足し、`docs/canonical.md` に案内を書く",
	"Antigravity の隔離・制限のモードで仕様を扱う決まり（今の『Claude Code の隔離セッションでは読むだけ』に当たるもの）を、要れば配るスキルと案内に足す",
	"ダッシュボードのエージェントの種類の名前を、orca-web の部品の名前（Claude、Codex、Antigravity、Gemini など）で出す",
	"両方を入れた版を出し、この PC に入れる（統括が行う）",
]

excludes: [
	"稼働の印のアイコンそのもの、送信と回答、状態の読み取り（orca-web の epic-00065）",
	"モデルごと（Gemini、Claude、GPT の系統）のアイコンや名前。Orca が種類に入れていないので、種類（道具）ごとにする（統括の決定、2026-11-20。decisions）",
	"Antigravity や Gemini CLI のツールの設定を SpecDock が書き換えること（今の Codex・Claude Code と同じく、1行を示すだけ）",
	"coding-task などの開発の仕組みで、Antigravity を実装担当の提供元に加えること",
]

requirements: {
	"R-01": {
		title: "Antigravity のエージェントが、作業用の worktree で仕様のカタログを読み書きできるための案内がある"
		text: """
			作業用の worktree で動く Antigravity のエージェントが、カタログ（`<main のチェックアウト>/spec-dock/.canonical`）を読み書きできるかを、実物の `agy` で確かめる。
			設定が要るなら、`canonical status` の `tools` に Antigravity の項目を足し、Antigravity の中で実行したと分かるときに、その1行と警告 `CANONICAL_TOOL_SETTING_MISSING`（今の約束の形）を示す。
			設定が要らないなら、その事実と確かめた版を `docs/canonical.md` に書き、`tools` には足さない。
			"""
		acceptance: [
			"`docs/canonical.md` のツールの設定の節に Antigravity の行があり、要る設定（または要らないこと）と、確かめた `agy` の版が書かれている",
			"設定が要る場合：Antigravity の中を模した環境（テストの環境変数）で、設定がないと `canonical status --json` の `data.tools` に Antigravity の項目と1行と警告が出て、設定があると警告が出ない",
			"Codex と Claude Code の今の項目と出力が変わらない（今のテストがそのまま通る）",
		]
	}
	"R-02": {
		title: "Antigravity の制限のモードで仕様を扱う決まりが、配るスキルと案内にある"
		text: """
			Antigravity に、Claude Code の隔離セッション（`--worktree`）のように、カタログに書けない動き方（`--sandbox` など）があるかを確かめる。
			あれば、配るスキル（`.agents/skills/spec-dock/SKILL.md`）の『仕様の扱い』と `docs/canonical.md` に、その動き方での扱いを足す。なければ足さず、確かめた結果を報告書に残す。
			"""
		acceptance: [
			"確かめた結果（動き方の有無、確かめた版、確かめ方）が iss-00673 の報告書にある",
			"足した場合、配るスキルと静的な資産の一覧（`static-inventory.json`）が一致し、資産の検査のテストが通る",
		]
	}
	"R-03": {
		title: "ダッシュボードのエージェントの種類の名前が、orca-web の部品の名前で出る"
		text: """
			エージェントのタブの選び、横の欄の見出しの title、構造の図の指揮の帯と詳細の欄、未対応の行の数の札で、種類を orca-web の部品が書き出す名前（`AGENT_ICONS[iconKey(agentType)].label`。Claude、Codex、Antigravity、Gemini など）で出す。
			部品が知らない種類（`iconKey` が `other`）は、今どおり `agentType` の文字列を出す。名前の表を SpecDock に写して持たない。
			"""
		acceptance: [
			"`agentType` が `antigravity` のエージェントが、上の各所で『Antigravity』と出る（orca-web の epic-00065 の後の部品で）",
			"`agentType` が部品の知らない文字列なら、その文字列が出る。`agentType` がなければ、今どおり『種類不明』（未対応の行は `agent`）",
			"部品が名前の表を書き出していない古い orca-web でも、今どおり `agentType` の文字列が出て、エラーにならない",
		]
	}
}

requirements: "R-04": {
	title: "両方を入れた版が出て、この PC に入る"
	text: """
		iss-00673 と iss-00674 を入れた SpecDock の版（0.9.10）を、今までのリリースと同じ形（版の番号、移行の案内の節、配る資産の一覧、前の版からの `installation update` の統合テスト）で出す。
		統括がタグを付け、そのタグの wheel をこの PC に入れる。
		"""
	acceptance: [
		"`spec-dock --version` が 0.9.10 を返し、移行の案内に 0.9.10 の節（Antigravity の案内と種類の名前）がある",
		"0.9.9 の配布資産からの `installation update` の統合テストが通る",
	]
}

failures: {
	"F-01": {
		title: "Antigravity の中か分からないときは、Antigravity の警告を出さない"
		text:  "Antigravity の中だと分かる手がかり（環境変数など）がないときは、Antigravity の項目に分からないことを示すだけにし、`CANONICAL_TOOL_SETTING_MISSING` を出さない（Codex の `CODEX_SANDBOX` がないときと同じ）。"
	}
	"F-02": {
		title: "orca-web の部品が読めないときは、今どおり種類の文字列を出す"
		text:  "部品が読めない、または名前の表がないときは、種類の名前を引かず、今の表示のまま描く。"
	}
}

constraints: [
	"SpecDock は、Antigravity・Gemini CLI・Codex・Claude Code のツールの設定のファイルを書き換えない（`docs/canonical.md` の今の約束）",
	"種類の名前の正本は orca-web の部品の表（`web/embed/agent-marks-icons.js`）の1か所にする。SpecDock は書き出しを読むだけ",
	"環境に固有の名前（この PC のパス、会社やプロダクトの名前）で規則を分けない。公開の文書とテストに、この PC の実際のパスやセッションの id を書かない",
	"利用者の PC には、リリースしたタグの wheel だけを入れる",
]

decisions: [
	"2026-11-20 本人：統括の推奨のとおり、orca-web と SpecDock の両方で Antigravity と Gemini への対応を行う。Epic を作り、統括が全体を計画して作業者に進めさせる。",
	"2026-11-20 統括：アイコンと名前は、モデルではなく種類（道具、`agentType`）ごとにする。Orca が種類だけを報告し、Antigravity の中で動くモデル（Gemini、Claude など）を印の単位では知れないため。モデルの表示は orca-web の iss-00068 が状態に出すところまでにする。",
	"2026-11-20 統括：SpecDock 側は2つの Issue に分ける。iss-00673（カタログの権限の確かめと案内。Python の実行時と配る文書）と iss-00674（ダッシュボードの種類の名前。画面の JS）。書く範囲が重ならないので、並べて進める。",
	"2026-11-20 統括：iss-00674 は、orca-web の iss-00066（名前の表に Antigravity と Gemini を足す）が orca-web の main に入り、常駐の orca-web を立て直した後に、実データで確かめる。作るのは待たずに始めてよい（部品の書き出しを読むだけなので、古い表でも作れる）。",
]
