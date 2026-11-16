package spec

current: "版は 0.9.3。migration.md の最後の版の節は「## 0.9.3 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.3 のバイト。reference_cli.md の行は #604・#605 で今のバイトと 0.9.3 のバイト（known_old、`6b8066f2…`）を持つ。`tests/integration/test_issue599_release_0_9_3.py` が版 0.9.3 を固定する。"
target:  "版は 0.9.4。「## 0.9.4 への更新」が 0.9.3 の節の直後にあり、0.9.3 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.4\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue599_release_0_9_3.py` の `test_the_version_is_0_9_3_in_every_place` を消す（0.9.3 のときに 0.9.2 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.4 の節"
		text: """
			「## 0.9.3 への更新」の節の後、「## 新規導入」の前に「## 0.9.4 への更新」を足す。内容は iss-00602・00603・00607 の report.md と仕様、`git diff v0.9.3 origin/main` の graph.js・prefs.js、配る `reference_cli.md` で確かめる。

			- 冒頭：#604〜#608 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI とダッシュボードの JSON の契約は変わらない。変わる配布資産は migration.md、版のファイル（0.9.4）、`docs/reference_cli.md`（エージェントのタブの選びと `orca-shape` の説明）の3つ。
			- `installation update` の手順。0.9.3 以前の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- 道具の帯：「終わったものも」「片付けの候補を畳む」「待っている線｜すべての線｜線なし」がなくなり、「全体｜いま｜これから」の1つの切り替えになる。各範囲の意味（全体＝0.9.3 の終わったものも＋畳まない、いま＝0.9.3 の既定、これから＝終わったもの・候補を出さず枠としてだけ親を出し、終わったものとの線も出さない）。線はいつもすべての線の描き方。fit の文字は「全体」から「収める」（title「画面に収める」）。
			- 保存：キー `specdock.graph.v3`、`{mode, range, legend}`。版2から一度だけ移し替え（mode と legend を引き継ぎ、showDone が真なら全体、それ以外はいま。fold と線の選びは捨て、線はすべての線）。版1だけなら mode と legend。古いキーは消さない。
			- エージェントのタブの直し（iss-00602 の report.md の5点と footChoice）：最後に開いた相手を問い合わせに書く、欄の足のリンクが選びか覚え（`gone:<id>`）を持つ、修飾キーつきの押しは覚えを変えない、スマホの図で選んだ箱の印を押すとエージェントのタブ、並びでない `agents` は `orca-shape`。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.3 に戻す（0.9.3 は版2の保存を読むので 0.9.4 の範囲の選びは引き継がれない）。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.3 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.3 のバイトのハッシュ：migration.md `8c598cf0…`、版のファイル `38ecaa1e…`）を `known_old_sha256` の末尾に足す（0.9.2 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.3:src/spec_dock/assets/spec_dock/<道>` で migration.md、system/spec-dock-version、docs/reference_cli.md を取り、`tests/fixtures/issue609/migration.md.0.9.3.txt`、`spec-dock-version.0.9.3.txt`、`reference_cli.md.0.9.3.txt` に置く。統合テスト `tests/integration/test_issue609_release_0_9_4.py` を `test_issue599_release_0_9_3.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（3つの行が今のバイトと 0.9.3 のバイトを知る）、0.9.3 の資産を持つ consumer の `installation update`（3つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.3 の実際の手順（タグ v0.9.3 が PR #600 のマージのコミット 16f0cf122 を指すこと、`.github/workflows/release-tag.yml`、iss-00599 の report.md、uv tool の receipt）から 0.9.4 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI とダッシュボードの JSON の契約の変更はない。ブラウザーの保存は版2から版3へ一度だけ移し替える。0.9.3 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
