package spec

current: "版は 0.9.2。migration.md の最後の版の節は「## 0.9.2 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.2 のバイト。reference_cli.md の行は #597 で今のバイトと 0.9.2 のバイト（known_old）を持つ。`tests/integration/test_issue594_release_0_9_2.py` が版 0.9.2 を固定する。"
target:  "版は 0.9.3。「## 0.9.3 への更新」が 0.9.2 の節の直後にあり、0.9.2 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.3\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue594_release_0_9_2.py` の `test_the_version_is_0_9_2_in_every_place` を消す（0.9.2 のときに 0.9.1 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.3 の節"
		text: """
			「## 0.9.2 への更新」の節の後、「## 新規導入」の前に「## 0.9.3 への更新」を足す。内容は iss-00591〜00593 の report.md、配る文書 `reference_cli.md` の「orca-web との連携」の節、`git log v0.9.2..origin/main` で確かめる。

			- 冒頭：#596〜#598 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約は変わらない。ダッシュボードの JSON に項目が足されるだけ（`/api/v1/repositories` の `server.orca_web`、構造の JSON の Scope ごとの `worktrees` と全体の `worktrees`）。変わる配布資産は migration.md、版のファイル（0.9.3）、`docs/reference_cli.md`（orca-web との連携の節）の3つ。
			- `installation update` の手順。0.9.2 以前の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- orca-web との連携：同じ PC の orca-web を画面が直接読み、構造の図・ボード・横の欄の見出しに稼働の印、横の欄の見出しに「Orca で開く」、横の欄と詳しい画面に「エージェント」のタブ（説明資料の次）で orca-web の詳細とチャットを埋め込む。対応は worktree のパス、なければブランチ名。
			- 設定：`config.json` の最上位の節 `orca_web`（`enabled` 既定 true、`port` 既定 8791、1〜65535）。省けば既定で連携。壊れた節は連携しない側に倒れ、理由は `dashboard list` の `config_problems` と画面に出る。起動し直さずに効く。
			- 前提：orca-web の `ORCA_WEB_READ_ORIGINS` に SpecDock のオリジン（`http://127.0.0.1:47800` と Tailscale の IP の同じ番号）。`localhost` や MagicDNS の名前では読めない。
			- orca-web がないとき・届かないときは、印もボタンも出ず、図とボードはそのまま動く。止めるには `"orca_web": {"enabled": false}`。
			- 送信：枠の中の orca-web だけが送る。送れるかは orca-web の設定の `sendEnabled`（既定は止まっている）で決まり、SpecDock は上書きしない。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.2 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.2 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.2 のバイトのハッシュ）を `known_old_sha256` の末尾に足す（0.9.1 と 0.9.0 のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.2:src/spec_dock/assets/spec_dock/<道>` で migration.md、system/spec-dock-version、docs/reference_cli.md を取り、`tests/fixtures/issue599/migration.md.0.9.2.txt`、`spec-dock-version.0.9.2.txt`、`reference_cli.md.0.9.2.txt` に置く。統合テスト `tests/integration/test_issue599_release_0_9_3.py` を `test_issue594_release_0_9_2.py` と同じ形で書き、版、節（見出しの順と主な語）と写しの一致、inventory（3つの行が今のバイトと 0.9.2 のバイトを知る）、0.9.2 の資産を持つ consumer の `installation update`（3つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.2 の実際の手順（タグ v0.9.2 が PR #595 のマージのコミット 2265e8fc1 を指すこと、`.github/workflows/release-tag.yml`、iss-00594 の report.md、uv tool の receipt）から 0.9.3 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の契約の変更はない。ダッシュボードの JSON に項目が足される（追加だけ）。0.9.2 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
