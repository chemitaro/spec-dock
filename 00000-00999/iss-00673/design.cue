package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"今の Claude Code の判定（domain の純粋な関数と、application の読み取り）と同じ形で、Antigravity の項目を足す",
	"Antigravity の外の出力（Codex・Claude Code の項目、警告、その順、`tools.status`、`tools.next_step`）を変えない",
]

current: """
	- `runtime/infra/runtime_environment.py` の `RuntimeEnvironment` が `codex_sandbox`（`CODEX_SANDBOX`）と `claude_code`（`CLAUDECODE`）を持つ。
	- `runtime/domain/canonical_tools.py` が、Claude Code のユーザーの設定のファイル（`claude_user_settings`）、1行（`codex_setting_line`、`claude_setting_line`）、判定（`claude_allows`）を持つ。
	- `runtime/application/canonical_tools_check.py` の `tool_findings` が `tools` の項目（`status`、`next_step`、`codex`、`claude_code`）と警告を作る。`canonical status` と `canonical link` が使う。`presentation` の `CanonicalStatusData.tools` は `dict[str, object]` で、形を持たない。
	- `tests/support/canonical_repo.py` の `isolate_user_state` が、道具のセッションの印（`CODEX_SANDBOX`、`CLAUDECODE`、`CLAUDE_CONFIG_DIR`）を消す。
	"""

target: """
	`tools` に `antigravity` の項目が並び、Antigravity の中（`ANTIGRAVITY_AGENT`）の linked worktree では、その1行と警告が出る。案内に Antigravity の項がある。
	"""

design: {
	"D-01": {
		title: "Antigravity の検出（infra）"
		text: """
			`RuntimeEnvironment` に、`codex_sandbox`・`claude_code` と同じ形の property `antigravity` を足す：`"ANTIGRAVITY_AGENT" in self.environ`（値は見ない。1.5.12 は `1` を渡す）。
			`tests/support/canonical_repo.py` の `isolate_user_state` が消す印に `ANTIGRAVITY_AGENT` と `ANTIGRAVITY_APP_DATA_DIR` を足す（Antigravity の中でテストを走らせても結果が変わらないように）。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "設定のファイル、1行、判定（domain の純粋な関数）"
		text: """
			`canonical_tools.py` に足す：
			- 定数 `ANTIGRAVITY_USER_SETTINGS_FILE = "~/.gemini/antigravity-cli/settings.json"`、`ANTIGRAVITY_APP_DATA_DIR = "ANTIGRAVITY_APP_DATA_DIR"`。
			- `antigravity_user_settings(environ, home) -> tuple[Path | None, str]`：`claude_user_settings` と同じ形。環境変数があれば `Path(値) / "settings.json"`（絶対でなければ道は None、名前は `str(道)`）、なければ `home / ".gemini/antigravity-cli/settings.json"`（home が None なら None）と名前 `ANTIGRAVITY_USER_SETTINGS_FILE`。
			- `antigravity_setting_line(catalog) -> str`：`{ "permissions": { "allow": [<read>, <write>] } }`。`<read>` は `json.dumps(f"read_file({catalog})", ensure_ascii=False)`、`<write>` は同じく `write_file(...)`。区切りは `claude_setting_line` と同じ（`{ "permissions": { "allow": ["read_file(/a)", "write_file(/a)"] } }`）。
			- `antigravity_allows(payload, catalog, *, resolve=lambda path: path) -> bool | None`：`payload` は JSON を読んだ値（読めなければ None）。
			  1. dict でなければ None。`allowNonWorkspaceAccess` が `True`（真偽の値）なら True。
			  2. `permissions` の既定は `{}`、dict でなければ None。`allow` の既定は `[]`、文字列のリストでなければ None。
			  3. 各規則を `^(read_file|write_file)\\((.+)\\)$` で読み、中が絶対のパスのものだけを、`os.path.normpath` してから `resolve` して数える。`~`、相対のパス、`*`、ほかの道具の規則は数えない（確かめていない形）。
			  4. カタログ（`catalog` は実のパス）と等しいか、その親を指す `read_file` と `write_file` が両方あれば True、なければ False。
			"""
		satisfies: ["R-01"]
	}
	"D-03": {
		title: "`tools.antigravity` の項目と警告（application）"
		text: """
			`tool_findings` で、Claude Code の項目の後に作る：
			```
			"antigravity": {"session": environment.antigravity, "needed": not layout.is_main, "configured": None, "sources": [], "file": <名前>, "line": None}
			```
			linked worktree（`not layout.is_main`）のときだけ判定する：
			- 道が None：`sources` を `[<名前>]`、`configured` を None。
			- ファイルがない（`FileNotFoundError`、`NotADirectoryError`）：`sources` は空、`antigravity_allows({}, ...)` と同じく False。
			- 読めない（ほかの `OSError`、`UnicodeDecodeError`）か JSON でない：`sources` を `[<道>]`、payload None で None。
			- 読めた：`sources` を `[<道>]`、`antigravity_allows(payload, realpath(catalog), resolve=realpath)`。
			`configured` が False なら `line` に1行を入れる（Antigravity の外でも入れる。情報なので）。
			警告は `environment.antigravity` が真のときだけ足す（F-01）：
			- False：`CANONICAL_TOOL_SETTING_MISSING`、message `Antigravity reads and writes the specs of this linked worktree only with an allow rule; add this to <名前>: <1行>`、details `{item: "tools", tool: "antigravity", file, line, next_step: line}`。
			- None：`CANONICAL_TOOL_SETTING_UNKNOWN`、next_step `Check that <名前> allows read_file(<カタログ>) and write_file(<カタログ>) in permissions.allow.`、details `{item: "tools", tool: "antigravity", sources, next_step}`。
			警告は今の Codex・Claude Code の後に並べる。`tools.status` は今どおり警告があれば `problem`。`tools.next_step` は、Antigravity の警告があればその `next_step`、なければ今どおり最初の警告の `next_step`。
			`canonical link` は同じ `tool_findings` を使うので、同じ警告が出る（追加の作業はない）。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-04": {
		title: "配る案内（タスク担当が書く）"
		text: """
			`src/spec_dock/assets/spec_dock/docs/canonical.md` の『## ツールの設定』：
			- 冒頭の文の対象を『Claude Code、Codex、Antigravity』にする。
			- **Antigravity** の項：ユーザーの設定 `~/.gemini/antigravity-cli/settings.json`（Antigravity の中では `ANTIGRAVITY_APP_DATA_DIR` が指すディレクトリの `settings.json`）の `permissions.allow` に `read_file(<カタログ>)` と `write_file(<カタログ>)` を加える1行の例。複数のクローンを並べる例。既にある `permissions.allow` には加える（置き換えない）。
			- 足さないと：ファイルの道具は許可を求めるか拒まれ（print のモードでは自動で拒まれる）、端末の書き込みは `Operation not permitted`。
			- その回だけなら `agy --add-dir <カタログ>` でも通るが、SpecDock からは見えないので `canonical status` は警告を出す。`allowNonWorkspaceAccess` は作業ディレクトリの外のすべてを許すので勧めない。
			- 確かめた版：`agy` 1.5.12（2026-11-20）。設定の場所と名前は版で変わりうる。
			- 確かめ方の項に、Antigravity は `ANTIGRAVITY_AGENT` があるときに、ユーザーの設定のファイルを読むだけ読んで判定することを足す。
			`src/spec_dock/assets/spec_dock/docs/reference_cli.md` の C45 の『ツールの設定の1行』を『ツールの設定の1行（Codex、Claude Code、Antigravity）』にする。
			両方の dogfood の写し（`spec-dock/docs/`）を同じバイトにし、`static-inventory.json` の2行の `sha256` を今のバイトにし、前のバイトのハッシュを `known_old_sha256` の末尾に足す（すでにあれば足さない）。
			"""
		satisfies: ["R-02"]
	}
}

compatibility: """
	`data.tools` に `antigravity` の鍵が増えるだけ。Antigravity の外（`ANTIGRAVITY_AGENT` なし）では、警告、その順、`tools.status`、`tools.next_step` は今と同じ。
	`installation update` は、前の版の `canonical.md`・`reference_cli.md` を既知の古い版として上書きできる。
	"""

risks: [
	"Antigravity CLI は新しく、設定の場所や規則の書き方が版で変わりうる。確かめた版を案内に書き、検出が外れたとき（`ANTIGRAVITY_AGENT` がない）は警告を出さない（F-01）",
	"`--add-dir` で起動した回は SpecDock から見えず、要らない警告が出る。案内に書く",
	"Antigravity の中の linked worktree では、今の Claude Code の警告（Antigravity の外でも出る今の動き）も並ぶ。順と出方は変えず、`tools.next_step` だけを Antigravity の1行にする",
]
