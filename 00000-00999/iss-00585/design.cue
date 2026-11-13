package spec

current: "版は 0.9.0。migration.md の最後の版の節は「## 0.9.0 への更新」。static-inventory.json の2行の sha256 は 0.9.0 のバイト。`tests/integration/test_issue580_release_0_9_0.py` が版 0.9.0 を固定する。"
target:  "版は 0.9.1。「## 0.9.1 への更新」が 0.9.0 の節の直後にあり、0.9.0 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.1\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check`（あれば）で整合を確かめる。`test_issue580_release_0_9_0.py` の `test_the_version_is_0_9_0_in_every_place` を消す（0.9.0 のときに 0.8.0 のテストから同じものを消した形）。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.1 の節"
		text: """
			「## 0.9.0 への更新」の節の後、「## 新規導入」の前に「## 0.9.1 への更新」を足す。内容は iss-00583 の requirement.cue・report.md と `git log v0.9.0..origin/main` で確かめる。

			- 冒頭：#584 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、API と JSON の契約は変わらない。変わる配布資産は migration.md と版のファイル（0.9.1）の2つ。
			- `installation update` の手順。0.9.0 の配布資産のままでも動く。構造の図の直しはパッケージが配る画面なので、パッケージの更新だけで届く。
			- 構造の図（#584）：依存でつながった塊を先に（左に）置き、つながりのない Scope を塊の右や下の空きに詰める（塊どうし、1つどうしの活動順は保つ。塊のない段は今までと同じ）。最上位の Initiative も見える幅で折り返す（0.9.0 の節の「倍率が最大になる行の幅」を改める）。大きさが変わり終わったときだけ並べ直すのは同じ。1つで見える幅より広い Initiative の行だけは見える幅を超える。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.0 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.0 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.0 のバイトのハッシュ）を `known_old_sha256` の末尾に足す。fixture は `git show v0.9.0:src/spec_dock/assets/spec_dock/docs/migration.md` と同じく `system/spec-dock-version` から取り、`tests/fixtures/issue585/migration.md.0.9.0.txt`、`spec-dock-version.0.9.0.txt` に置く。統合テスト `tests/integration/test_issue585_release_0_9_1.py` を `test_issue580_release_0_9_0.py` と同じ形で書き、版、節（見出しの順と主な語）と写しの一致、inventory、0.9.0 の資産を持つ consumer の `installation update` を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.0 の実際の手順（タグ v0.9.0 は PR #582 のマージのコミット 982932e47 の軽いタグ、uv tool の receipt の wheel の道 `/private/tmp/spec-dock-v0.9.0-dist/spec_dock-0.9.0-py3-none-any.whl`、epic-00573 の report.md の配布の記録）から 0.9.1 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "契約の変更はない。0.9.0 の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
