package spec

current: "版は 0.9.8。migration.md の最後の版の節は「## 0.9.8 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.8 のバイト（`ae9e47b6…`、`ff35aa97…`）。reference_cli.md の行の sha256（`9375d7fd…`）は v0.9.8 と今のバイトで同じ。`tests/integration/test_issue663_release_0_9_8.py` が版 0.9.8 を固定する。"
target:  "版は 0.9.9。「## 0.9.9 への更新」が 0.9.8 の節の直後にあり、0.9.8 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.9\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue663_release_0_9_8.py` の `test_the_version_is_0_9_8_in_every_place` を消す（0.9.8 のときに 0.9.7 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.9 の節"
		text: """
			「## 0.9.8 への更新」の節の後、「## 新規導入」の前に「## 0.9.9 への更新」を足す。内容は iss-00668 の report.md（「移行の案内に書く文」と実機の確かめ）と仕様、`git diff v0.9.8 origin/main` で確かめる。

			- 冒頭：#669 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON の版（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーは変わらない。変わる配布資産は migration.md と版のファイル（0.9.9）の2つ。
			- `installation update` の手順。0.9.8 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- `Unscoped` の行：構造の図と『横断の構造』の『指揮の帯』が `Unscoped` の行になり、先頭にいつも主のチェックアウト（印 `Primary`）が出る。Orca を使わなくても、誰も指揮していなくても出る。
			- `Unlinked`：`git worktree list` に出る worktree のうち、どの Scope にも紐づかないものが `Unlinked` で並び、`spec-dock work start` をせずに作業している worktree に気づける。エージェントのいない worktree は薄く出て、2つ以上は `+N` に畳まれる（押すと一覧）。仕様の置き場の worktree、bare、prunable は出ない。
			- 1つの worktree は1つの項目で、エージェントの印をすべて並べる（1行4つ、多いと項目の中で折り返す）。項目を押すとブランチ・パス・エージェント・『Orca で開く』の詳細の欄。
			- 『これから』：指揮の線を引かず、主のチェックアウトと指揮している `Unlinked` の worktree に子の数を添える（title に内訳）。全体・いまの線は今までどおり。
			- 札「main のチェックアウト」はブランチ名と `Primary` の印に変わった。
			- 構造の API（`/api/v1/r/<repo>/structure`）の `worktrees` に `items`（`path`・`branch`・`head`・`main`・`detached`・`locked`）が加わった。`status` と `paths` は変わらない。画面の中の JSON で契約ではない。
			- エージェントの印と線は、今までどおり orca-web の要約が要る（Orca がないときは行と worktree の項目だけが出る）。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.8 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.8 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.8 のバイトのハッシュ：migration.md `ae9e47b6…`、版のファイル `ff35aa97…`）を `known_old_sha256` の末尾に足す（0.9.7 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.8:src/spec_dock/assets/spec_dock/<道>` で migration.md と system/spec-dock-version を取り、`tests/fixtures/issue670/migration.md.0.9.8.txt`、`spec-dock-version.0.9.8.txt` に置く。統合テスト `tests/integration/test_issue670_release_0_9_9.py` を `test_issue663_release_0_9_8.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（2つの行が今のバイトと 0.9.8 のバイトを知る）、0.9.8 の資産を持つ consumer の `installation update`（2つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.8 の実際の手順（タグ v0.9.8 が PR #666 のマージのコミット 1cfce6f96 を指すこと、`.github/workflows/release-tag.yml`、iss-00663 の report.md、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.8-dist/…`）から 0.9.9 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の JSON の契約、ダッシュボードの JSON の版、画面の道、ブラウザーの保存のキーの変更はない。構造の API の `worktrees.items` の追加は、契約にしない画面の中の JSON への項目の追加。0.9.8 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
