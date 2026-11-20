package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"ツールごとの設定の確かめは、今の `canonical_tools.py`（domain）と `canonical_tools_check.py`（application）の形に、Antigravity の項目を同じ形で足す",
	"種類の名前は orca-web の部品の1か所から引き、SpecDock の画面の各所は同じ小さな関数を通す",
]

current: """
	- `runtime/infra/runtime_environment.py` は `CODEX_SANDBOX` と `CLAUDECODE` で、Codex のサンドボックスと Claude Code の中を見分ける。
	- `runtime/domain/canonical_tools.py` は、Codex（`~/.codex/config.toml` の `[sandbox_workspace_write]` の `writable_roots`）と Claude Code（`permissions.additionalDirectories`）の1行と、Claude Code の設定の読み取りの判定を持つ。
	- `runtime/application/canonical_tools_check.py` は、`data.tools` に `codex` と `claude_code` の項目を作り、要るときに `CANONICAL_TOOL_SETTING_MISSING`・`CANONICAL_TOOL_SETTING_UNKNOWN` を出す。
	- 配る案内 `assets/spec_dock/docs/canonical.md` の42〜71行が、2つのツールの設定の1行と、足さないときの症状と確かめ方を書く。配るスキル `assets/install_root/.agents/skills/spec-dock/SKILL.md` の『仕様の扱い』が、Claude Code の隔離セッションの決まりを持つ。
	- ダッシュボードは `core/orca.js` で orca-web の `/embed/agent-marks.js` を読み、`orca.marks()` がその部品（`AGENT_ICONS`、`iconKey`、`renderAgentMarks` などを書き出す）を返す。種類の文字列は上の5か所で、そのまま文字にしている。
	"""

target: """
	- iss-00673：実物の `agy` で確かめた結果に従い、Antigravity の項目（要れば検出・1行・警告）と案内を足す。
	- iss-00674：ダッシュボードに、部品から種類の名前を引く1つの関数を置き、上の5か所がそれを通す。
	"""

design: {
	"D-01": {
		title: "Antigravity の設定の確かめ（iss-00673）"
		text: """
			まず実物で確かめる（タスク担当が仕様を書く前に）：
			1. 作業用の worktree を作業ディレクトリにした `agy` が、そのクローンのカタログ（作業ディレクトリの外）を読めるか、書けるか。確かめは一時のリポジトリと一時のカタログで行い、本物のカタログに書かない。
			2. 読み書きを許す設定（`--add-dir` に当たる、保存される設定の項目。`~/.gemini/antigravity-cli/settings.json`、`~/.gemini/config/`、プロジェクトの設定など）の有無と書き方。
			3. Antigravity の中で動くコマンドに渡る環境変数（`agy` の端末の道具で `env` を見る）。
			4. `--sandbox` などの制限のモードで、カタログに書けるか。
			設定が要るなら、`canonical_tools.py` に Antigravity の設定のファイルと1行を作る関数、`runtime_environment.py` に検出、`canonical_tools_check.py` に `antigravity` の項目を、今の `codex`・`claude_code` と同じ形（`needed`、`line`、`file`、`next_step`）で足す。読める設定のファイルなら、Claude Code と同じく読み取りで判定してよい（判定できなければ UNKNOWN）。
			公開の JSON の形を足すので、`presentation` と `docs/reference_cli.md` の `tools` の説明も合わせる。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-02": {
		title: "種類の名前を部品から引く関数（iss-00674）"
		text: """
			`views/_shared/` に、`agentTypeLabel(marks, agentType)` のような純粋な関数を1つ置く。
			`marks`（`orca.marks()` の部品、なければ null）が `AGENT_ICONS` と `iconKey` を書き出していて、`iconKey(agentType)` が `other`・`none` でなければ `AGENT_ICONS[key].label`、そうでなければ今の表示の文字列（`agentType`、なければ呼ぶ側の既定の文字）を返す。
			上の5か所（エージェントのタブの選び、`agents_logic.js` の title、`command_view.js` の2か所、`unscoped.js` の数の札）がこの関数を通す。`agents_logic.js` のように部品を持たない純粋な部品には、呼ぶ側から部品を渡す。
			"""
		satisfies: ["R-03", "F-02"]
	}
	"D-03": {
		title: "リリース（iss-00675）"
		text: """
			0.9.9 のリリース（iss-00670、PR #671）と同じ形で版を上げる。移行の案内の 0.9.10 の節には、iss-00673 と iss-00674 の report.md に用意された案内の文を使う。
			マージの後、統括がタグ `v0.9.10` を付け、そのタグから作った wheel だけをこの PC の道具の環境に入れる（リリース前の main を入れない）。
			"""
		satisfies: ["R-04"]
	}
}

compatibility: """
	`data.tools` に項目を足すだけで、今の `codex` と `claude_code` の項目は変えない。部品の名前の表がない古い orca-web では、ダッシュボードは今の表示のまま。
	"""

risks: [
	"Antigravity CLI は新しく、設定の場所や名前が版で変わりうる（資料でも食い違いがある）。確かめた `agy` の版を案内に書き、検出が外れたときは警告を出さない側に倒す（F-01）",
	"Antigravity が範囲の外への書き込みを確かめなしに許す場合、設定の1行は要らないが、利用者の確かめの画面で止まる可能性がある。確かめの画面の有無も、実物で確かめて案内に書く",
]
