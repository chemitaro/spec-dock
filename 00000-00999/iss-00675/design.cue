package spec

current: "版は 0.9.9。migration.md の最後の版の節は「## 0.9.9 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.9 のバイト。canonical.md と reference_cli.md の行は #677 の後の今のバイトで、0.9.9 のバイトを known_old_sha256 に持つ。`tests/integration/test_issue670_release_0_9_9.py` が版 0.9.9 を固定する。"
target:  "版は 0.9.10。「## 0.9.10 への更新」が 0.9.9 の節の直後にあり、0.9.9 の節の『これから』の項目の後に注がある。0.9.9 のバイトが migration.md と版のファイルの known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.10\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue670_release_0_9_9.py` の `test_the_version_is_0_9_9_in_every_place` を消す（0.9.9 のときに 0.9.8 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.10 の節と 0.9.9 の節の注"
		text: """
			「## 0.9.9 への更新」の節の後、「## 新規導入」の前に「## 0.9.10 への更新」を足す。内容は iss-00673・iss-00674・iss-00676 の report.md の案内の文と、`git diff v0.9.9 origin/main` で確かめる。

			- 冒頭：#677・#678・#679 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、ダッシュボードの JSON の版（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーは変わらない。CLI の JSON は `canonical status` の `data.tools` に `antigravity` が増えるだけ（項目の追加）。変わる配布資産は canonical.md、reference_cli.md、migration.md、版のファイル（0.9.10）の4つ。
			- `installation update` の手順。0.9.9 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- Antigravity（#677）：作業用のworktreeの Antigravity（`agy`）がカタログに読み書きするには、ユーザーの設定 `~/.gemini/antigravity-cli/settings.json` の `permissions.allow` に `read_file(<カタログ>)` と `write_file(<カタログ>)` を1回だけ足す（`canonical status` が示す1行、`docs/canonical.md` の『ツールの設定』）。`canonical status --json` の `data.tools.antigravity`（`session`、`needed`、`configured`、`sources`、`file`、`line`）。`ANTIGRAVITY_AGENT` があるとき、規則がないと警告 `CANONICAL_TOOL_SETTING_MISSING`（`details.tool` は `antigravity`）。deny・ask がカタログを覆うか確かめられないときは `CANONICAL_TOOL_SETTING_UNKNOWN`。Antigravity の外では警告と `tools.status`・`tools.next_step` は前と同じ。配るスキルと AGENTS.md の『仕様の扱い』は変わらない。
			- 種類の名前（#678）：ダッシュボードはエージェントの種類を orca-web の部品の名前（Claude、Codex、Antigravity、Gemini など）で出す。知らない種類は今までどおり種類の文字列。Antigravity と Gemini の名前には orca-web main `4ad7471` 以降が要る。利用者がすることはない。
			- 『これから』の指揮の線（#679）：『これから』でも、指揮の黄色い点線、同じ箱の親子の弧、動き、波紋、`Unscoped` の行が『いま』と同じ規則で出る。隠れた Scope の worktree のエージェントの線は、いちばん近い見える祖先の枠に落ちる。子の数の札はなくなる。既定が『これから』の『横断の構造』でも線が出る。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.9 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.9 の節の『これから』の項目の直後に、1項目の注を足す（例：「0.9.10 の注：0.9.10 から『これから』でも指揮の線と `Unscoped` の行（並ぶ worktree を含む）が『いま』と同じ規則で出て、子の数は出なくなりました（『0.9.10 への更新』）」）。0.9.9 の節の今の本文の行と、それより前の節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.9 のバイトのハッシュ）を `known_old_sha256` の末尾に足す（0.9.8 以前のハッシュは残す）。`canonical.md` と `reference_cli.md` の行は変えない。fixture は `git show v0.9.9:src/spec_dock/assets/spec_dock/<道>` で docs/migration.md、system/spec-dock-version、docs/canonical.md、docs/reference_cli.md を取り、`tests/fixtures/issue675/` に `<名前>.0.9.9.txt` で置く。統合テスト `tests/integration/test_issue675_release_0_9_10.py` を `test_issue670_release_0_9_9.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）、0.9.9 の節の注と、fixture の 0.9.9 の節の各行が今の 0.9.9 の節にそのまま残ること、写しの一致、inventory（4つの行が今のバイトと 0.9.9 のバイトを知る）、0.9.9 の資産を持つ consumer の `installation update`（4つのファイルだけ変わり、バックアップに 0.9.9 のバイト）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.9 の実際の手順（タグ v0.9.9 が PR #671 のマージのコミット 83b8ee95f を指すこと、`.github/workflows/release-tag.yml` の実行、iss-00670 の report.md、uv tool の receipt の wheel）から 0.9.10 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "コマンドの引数、ダッシュボードの JSON の版、画面の道、ブラウザーの保存のキーの変更はない。CLI の JSON は `canonical status` の `data.tools.antigravity` の追加（#677）。0.9.9 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md を先に確定する（S-01）。"]
