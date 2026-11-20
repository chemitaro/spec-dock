package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "canonical status の確かめと案内の文書を足す。ツールの設定は書き換えず、誤りは案内の誤りにとどまり、版を戻せば回復できる"
}

purpose: """
	作業用の worktree（linked worktree）で動く Antigravity（`agy`）のエージェントが、作業ディレクトリの外にある仕様のカタログを読み書きできるように、
	`canonical status` が要る設定の1行を示し、配る案内 `docs/canonical.md` に Antigravity の設定を書く（Epic epic-00672 の R-01、R-02、F-01、D-01）。
	"""

background: """
	タスク担当が 2026-11-20 に実物の `agy` 1.5.12（Homebrew の cask、macOS）で確かめた事実（手順と結果の全体は report.md の『実物での確かめ』）。
	確かめは、一時のリポジトリ（main のチェックアウトと linked worktree、linked の `spec-dock/initiatives` から main の `spec-dock/.canonical` への絶対のリンク）で、`agy -p`（print のモード）と、その回だけの `--settings` で行った。利用者の設定のファイルは書き換えていない。

	- linked worktree では、既定でカタログを読めない。ファイルの道具は許可を求め、print のモードでは自動で拒まれる（『a tool required the "read_file" permission that headless mode cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. read_file(<target>))』）。端末も既定で制限され、`touch spec-dock/initiatives/x` は `Operation not permitted` になる（`/tmp` と作業ディレクトリの中には書ける）。
	- main のチェックアウトでは、設定なしで、ファイルの道具でも端末でも読み書きできた（カタログが作業ディレクトリの中にある）。
	- その回だけの設定 `--settings '{"permissions":{"allow":["read_file(<カタログ>)","write_file(<カタログ>)"]}}'` で、ファイルの道具の読み書きと、端末からの書き込みの両方が通った。カタログの親のディレクトリを書いても通った。`--sandbox` を付けても同じだった。
	- 保存される設定の場所と形は、公式のスキーマ（https://antigravity.google/schemas/v1/settings.json 。利用者の設定のファイルの `$schema` が指す）が定める：『Settings for Antigravity CLI, stored in ~/.gemini/antigravity-cli/settings.json』。`permissions` は `allow`、`ask`、`deny` の規則の配列で、規則は `action(target)`（`read_file(/var/log)` など）、『A deny rule takes precedence over an ask rule, and an ask rule over an allow rule』。`--settings` の説明は『a JSON object of settings.json keys』で、`agy` のログは、保存された設定の `permissions` も `--settings` の `permissions` も、同じ形（`CLI settings initialized: permissions=&{Allow:[...] ...}`）で読み込む。利用者の設定のファイルを書き換えないため、保存された設定に規則を置いてカタログに書けることは、直接は確かめていない（推定）。
	- `ANTIGRAVITY_APP_DATA_DIR` を別のディレクトリにして起動しても、`agy` のログの app data directory は `~/.gemini/antigravity-cli` のままで、設定の場所を動かせなかった（入力としては効かない）。作業ディレクトリの `.agents/settings.json`、`.gemini/settings.json`、`.gemini/antigravity-cli/settings.json`、`.antigravity/settings.json` に置いた設定も効かなかった。
	- `--add-dir <カタログ>`（その回だけ）でも読み書きと端末の書き込みが通った。`allowNonWorkspaceAccess` は、スキーマでは『subject to toolPermission, agentMode, and your permission rules』。利用者の設定が権限の規則を持たなかったときは `--settings` の `allowNonWorkspaceAccess: true` で読み書きが通ったが、利用者の設定に `agentMode`・`ask`・`deny` などが足された後は、保存された `allowNonWorkspaceAccess: true` があっても、ファイルの道具の書き込みは許可を求めて拒まれた（ほかの設定によって結果が変わり、それだけでは当てにできない）。`additionalDirectories` は `--settings` が『unknown setting』で拒んだ。
	- Antigravity の端末で動くコマンドには、`ANTIGRAVITY_AGENT=1` などが渡る。
	- `--mode plan` では、許可の規則があっても、ファイルの作成と端末のコマンドが行われなかった（計画のモードは全体の書き込みをしない動き方で、カタログに限った制限ではない）。Claude Code の隔離セッション（`--worktree`）のような、設定を足しても書けない動き方は見つからなかった。

	このリポジトリの AGENTS.md の『仕様の扱い』は、配るスキル `install_root/.agents/skills/spec-dock/SKILL.md` の同じ節とバイトが同じだが、生成するコードはなく、手で写したもの（`git log -- AGENTS.md`）。この Issue では、どちらも変えない（R-02 の結果）。
	"""

includes: [
	"`canonical status`（と、同じ判定を使う `canonical link` の警告）の `data.tools` に `antigravity` の項目を足し、Antigravity の中で linked worktree のときに、要る1行と警告を示す",
	"`docs/canonical.md` のツールの設定の節に Antigravity を足す（提供側と dogfood の写しをバイト一致に）。`docs/reference_cli.md` の C45 の説明に対象のツールを書く",
	"`static-inventory.json` の該当の行の `sha256` を合わせ、前の版のバイトを既知の古い版に足す",
	"R-02 の確かめの結果を report.md に残す",
]

excludes: [
	"利用者の Antigravity・Codex・Claude Code の設定のファイルを書き換えること（読むだけ）",
	"`--add-dir` で起動された回を見分けること（起動の引数は SpecDock から見えない）",
	"作業ディレクトリの中の設定のファイル（効かないと確かめた）を読むこと",
	"`allowNonWorkspaceAccess`、`agentMode`、`toolPermission` で判定を変えること（それだけでは足りず、組み合わせは確かめていない）",
	"Codex・Claude Code の今の項目と警告と順の変更（Antigravity の外での Claude Code の警告の出方を含む）",
	"配るスキルと AGENTS.md の『仕様の扱い』の変更（R-02 の結果、足す決まりがない）",
	"Antigravity の中での Git の操作（linked worktree の Git の情報も作業ディレクトリの外にある）の扱い",
]

requirements: {
	"R-01": {
		title: "Antigravity の中の linked worktree で、`canonical status` が要る設定の1行と警告を示す"
		text: """
			`canonical status --json` の `data.tools.antigravity` に、Antigravity の中か（`session`）、設定が要るか（`needed`、linked worktree なら真）、設定があるか（`configured`：真、偽、分からない）、読んだ設定のファイル（`sources`）、示す設定のファイルの名前（`file`、`~/.gemini/antigravity-cli/settings.json`）、足す1行（`line`）を出す。
			Antigravity の中で、linked worktree で、設定がないときは、警告 `CANONICAL_TOOL_SETTING_MISSING`（`details.tool` は `antigravity`、`next_step` は1行）を出し、`tools.next_step` をその1行にする。判定できないときは `CANONICAL_TOOL_SETTING_UNKNOWN` を出す。
			1行は `{ "permissions": { "allow": ["read_file(<カタログ>)", "write_file(<カタログ>)"] } }` で、`<カタログ>` は今の Claude Code・Codex の1行と同じカタログの絶対パス。
			設定があるとは、`permissions.allow` に、カタログかその親を指す `read_file(...)` と `write_file(...)` が両方あり、`permissions.deny` と `permissions.ask` に、カタログかその親を指す `read_file(...)`・`write_file(...)` がないこと（deny と ask が allow より優先するため）。deny か ask がカタログを覆うときは、allow の1行を足しても直らないので、判定できない（`CANONICAL_TOOL_SETTING_UNKNOWN`）とし、`next_step` で deny と ask の規則を確かめるよう示す。deny か ask に、対象に `*` を含むか絶対のパスでない `read_file(...)`・`write_file(...)` が1つでもあれば、カタログを覆うかを確かめられないので、同じく判定できないとし、`next_step` でその形の規則も確かめるよう示す（公式の資料は `read_file(*)` などを全体に当たる規則とする。誤って『設定あり』と答えないため）。allow のそうした規則は、今どおり許す側に数えない。
			"""
		acceptance: [
			"`ANTIGRAVITY_AGENT` がある環境で、linked worktree の `canonical status --json` が、設定のファイルがないとき `tools.antigravity.configured` が偽、`line` が上の1行、警告 `CANONICAL_TOOL_SETTING_MISSING`（`details.tool` が `antigravity`）、`tools.next_step` がその1行になる",
			"設定のファイルの `permissions.allow` に、カタログかその親の `read_file(...)` と `write_file(...)` の両方があれば `configured` が真で、Antigravity の警告が出ない。片方だけ、`~`・相対のパス・`*` の規則だけ、`allowNonWorkspaceAccess` だけなら偽",
			"`deny` か `ask` にカタログかその親の `read_file`・`write_file` があれば、`allow` に両方があっても `configured` が null で、Antigravity の中なら `CANONICAL_TOOL_SETTING_UNKNOWN` の `next_step` が deny と ask の規則を確かめるよう示す",
			"`deny` か `ask` に、対象に `*` を含むか絶対のパスでない `read_file`・`write_file` の規則（`read_file(*)`、`write_file(/some/*)`、`read_file(~/x)` など）があれば、`allow` に両方があっても `configured` が null になる。`*` を含まない、カタログを覆わない絶対のパスの deny・ask の規則は判定に影響しない",
			"設定のファイルが壊れている（JSON でない、形が違う、権限や文字の符号で読めない）か、ホームのディレクトリが分からないときは、`configured` が分からない（null）で、Antigravity の中なら `CANONICAL_TOOL_SETTING_UNKNOWN` が出る",
			"main のチェックアウトでは `needed` が偽で、Antigravity の警告が出ない",
			"設定のファイルを読むだけで、書き換えない（実行の前後でバイトが同じ）",
			"Codex と Claude Code の今のテストが、そのまま通る",
		]
	}
	"R-02": {
		title: "Antigravity の設定と確かめた版が、配る案内にある"
		text: """
			`docs/canonical.md` の『ツールの設定』に、Antigravity の設定のファイル、1行、deny と ask が優先すること、足さないときの症状、要らない場合、その回だけの `--add-dir`、確かめた `agy` の版（1.5.12）と確かめ方（その回だけの `--settings` で確かめ、保存の場所は公式のスキーマによる）、`canonical status` の確かめ方を書く。
			Claude Code の隔離セッションに当たる、設定を足しても書けない動き方は Antigravity 1.5.12 に見つからなかったので、配るスキルの『仕様の扱い』には足さず、確かめた結果を report.md に残す（Epic の R-02）。
			"""
		acceptance: [
			"提供側の `docs/canonical.md` のツールの設定の節に Antigravity の項があり、設定のファイル、1行、`agy` 1.5.12 が書かれ、dogfood の写し `spec-dock/docs/canonical.md` とバイトが同じ",
			"提供側の `docs/reference_cli.md` の C45 の説明に、確かめるツール（Codex、Claude Code、Antigravity）が書かれ、dogfood の写しとバイトが同じ",
			"`static-inventory.json` の `canonical.md` と `reference_cli.md` の `sha256` が今のバイトと一致し、前の版（0.9.9）のバイトが既知の古い版にあり、資産の検査のテストが通る",
			"report.md に、確かめた版、手順、結果（Epic の R-01・R-02 の確かめ）と、直接は確かめていないこと（保存された設定での書き込み、対話のモードの画面）がある",
		]
	}
}

failures: {
	"F-01": {
		title: "Antigravity の中と分からないときは、Antigravity の警告を出さない"
		text:  "`ANTIGRAVITY_AGENT` がないときは、`tools.antigravity` に `session` 偽と判定の結果を示すだけで、`CANONICAL_TOOL_SETTING_MISSING`・`CANONICAL_TOOL_SETTING_UNKNOWN` を Antigravity について出さない（Codex の `CODEX_SANDBOX` がないときと同じ）。`tools.status` と `tools.next_step` は今の Codex・Claude Code の警告だけで決まる。"
	}
}

constraints: [
	"SpecDock は、ツールの設定のファイルを書き換えない。読むだけにする",
	"本人の環境に特化した決まりを入れない。公開の文書とテストに、この PC のパスやセッションの id を書かない",
	"確かめていない設定の形（`~` で始まる規則、相対のパス、`*`、作業ディレクトリの中の設定のファイル、`allowNonWorkspaceAccess`）を、許す側に数えない。deny・ask にそうした形があれば、判定できないとする",
]

decisions: [
	"2026-11-20 タスク担当（統括の進め方の2、依頼書）：実物で設定が要ると分かったので、`tools` に `antigravity` の項目と検出と1行と警告を、今の `codex`・`claude_code` と同じ形で足す。",
	"2026-11-20 タスク担当：勧める1行は、カタログに限る `permissions.allow` の `read_file`・`write_file` にする。`allowNonWorkspaceAccess` は、ほかの設定によって書き込みが通らないことがあり、作業ディレクトリの外のすべてに及ぶので、判定にも案内にも使わない。",
	"2026-11-20 タスク担当：設定のファイルは `~/.gemini/antigravity-cli/settings.json` だけを読む。`ANTIGRAVITY_APP_DATA_DIR` は入力として効かなかったので使わない（Claude Code の `CLAUDE_CONFIG_DIR` に当たるものはない）。",
	"2026-11-20 タスク担当：R-02 は、設定を足しても書けない動き方が見つからなかったので、配るスキルと AGENTS.md を変えない。`--mode plan` は全体の書き込みをしない計画のモードで、カタログに限った決まりは要らない。",
	"2026-11-20 統括（最終品質ゲートの2人目の P2 を受けて、今の PR で直すと決定）：deny か ask に、対象に `*` を含むか絶対のパスでない `read_file`・`write_file` の規則が1つでもあれば、判定できない（null、`CANONICAL_TOOL_SETTING_UNKNOWN`）とする。allow のそうした規則は今どおり数えない（偽、1行を示す）。",
	"2026-11-20 タスク担当：Antigravity の中では、`tools.next_step` を Antigravity の警告の1行にする（その中のエージェントに要る1行を先に示すため）。Antigravity の外の出力は変えない。",
]
