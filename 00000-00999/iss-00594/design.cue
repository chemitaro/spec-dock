package spec

current: "版は 0.9.1。migration.md の最後の版の節は「## 0.9.1 への更新」。static-inventory.json の2行の sha256 は 0.9.1 のバイト。`tests/integration/test_issue585_release_0_9_1.py` が版 0.9.1 を固定する。"
target:  "版は 0.9.2。「## 0.9.2 への更新」が 0.9.1 の節の直後にあり、0.9.1 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.2\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue585_release_0_9_1.py` の `test_the_version_is_0_9_1_in_every_place` を消す（0.9.1 のときに 0.9.0 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.2 の節"
		text: """
			「## 0.9.1 への更新」の節の後、「## 新規導入」の前に「## 0.9.2 への更新」を足す。内容は iss-00587・iss-00589 の requirement.cue・report.md と `git log v0.9.1..origin/main` で確かめる。

			- 冒頭：#588 と #590 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約は変わらない。ダッシュボードの Scope の JSON の文書の説明資料の項目に `skeleton`（雛形のままか）が足されるだけ。変わる配布資産は migration.md と版のファイル（0.9.2）の2つ。
			- `installation update` の手順。0.9.1 と 0.9.0 の配布資産のままでも動き、どちらからも上がる。画面の変更はパッケージが配るので、パッケージの更新だけで届く。
			- 欄（#588）：ボードの札と構造の図の箱で同じ欄が開く（修飾キー・中クリックは詳しい画面を新しいタブ）。タブは説明資料・概要・依存・配下・文書・Artifact・人のタスク。説明資料が書かれていれば最初に説明資料、雛形のままなら概要。欄は広くなり（見える幅の 44%、380〜720px）、詳しい画面へ同じタブでも新しいタブでも移れる。詳しい画面にも説明資料のタブが最初に出る。スマホでは下からの欄を取っ手のスワイプで最小・通常・全体の3段に動かせる。
			- 文書のタブ（#590）：選べるのは仕様と報告の2つ（説明資料は専用のタブ）。1行の切り替えと右端の新しいタブで開くリンク。検査の帯は誤りがあるときだけ1行、計画の進み具合は概要だけ。枠が残りの高さを使う。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.1 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.1 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.1 のバイトのハッシュ）を `known_old_sha256` の末尾に足す（0.9.0 のハッシュは残す）。fixture は `git show v0.9.1:src/spec_dock/assets/spec_dock/docs/migration.md` と同じく `system/spec-dock-version` から取り、`tests/fixtures/issue594/migration.md.0.9.1.txt`、`spec-dock-version.0.9.1.txt` に置く。統合テスト `tests/integration/test_issue594_release_0_9_2.py` を `test_issue585_release_0_9_1.py` と同じ形で書き、版、節（見出しの順と主な語）と写しの一致、inventory、0.9.1 の資産を持つ consumer の `installation update` を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.1 の実際の手順（タグ v0.9.1 は PR #586 のマージのコミット 928460f48 に `.github/workflows/release-tag.yml` が自動で作った軽いタグ（run 43531042874）、uv tool の receipt の wheel の道 `/private/tmp/spec-dock-v0.9.1-dist/spec_dock-0.9.1-py3-none-any.whl`、iss-00585 の report.md）から 0.9.2 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の契約の変更はない。ダッシュボードの Scope の JSON に項目が1つ足される（追加だけ）。0.9.1 と 0.9.0 の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
