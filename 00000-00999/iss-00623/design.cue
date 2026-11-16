package spec

current: "版は 0.9.4。migration.md の最後の版の節は「## 0.9.4 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.4 のバイト（`47902bb9…`、`a61cc7a9…`）。reference_cli.md の行は #619 で今のバイトと 0.9.4 のバイト（known_old、`4c4bbf4a…`）を持つ。`tests/integration/test_issue609_release_0_9_4.py` が版 0.9.4 を固定する。"
target:  "版は 0.9.5。「## 0.9.5 への更新」が 0.9.4 の節の直後にあり、0.9.4 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.5\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue609_release_0_9_4.py` の `test_the_version_is_0_9_4_in_every_place` を消す（0.9.4 のときに 0.9.3 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.5 の節"
		text: """
			「## 0.9.4 への更新」の節の後、「## 新規導入」の前に「## 0.9.5 への更新」を足す。内容は iss-00611・00613・00620 の report.md と仕様、`git diff v0.9.4 origin/main`、配る `reference_cli.md` で確かめる。

			- 冒頭：#618・#619・#622 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約は変わらない。ダッシュボードの JSON は `GET /api/v1/repositories` に項目が2つ増えるだけ。変わる配布資産は migration.md、版のファイル（0.9.5）、`docs/reference_cli.md`（`parent`・`tier` の説明）の3つ。
			- `installation update` の手順。0.9.4 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面と API の変更はパッケージが配る。
			- 『これから』（#618）：子を持つ Scope は、これからで見える子孫があるときだけ出る。中が終わったものと片付けの候補だけの開いた親（Initiative・Epic、子を持つ Issue）は出ない。開いた子があっても、その子自身が子を持ち中に見えるものがなければ、親も子も出ない。子のない開いた Scope、子のない開いた子孫を持つ親、選んだ（focus の）Scope は今どおり。全体・いまは変わらない。
			- リポジトリの一覧の API（#619）：各リポジトリの今の項目の後ろに `parent`（同じ応答のいちばん近い出す祖先のリポジトリの鍵か `null`）と `tier`（段の札の配列。`businesses`→事業、`products`→プロダクト、`services`→サービス）。チェックアウトとカタログの道は返さない。隠したもの、クローンが2つのものの扱いは reference_cli.md を指す。画面はまだ使わない（後の版）。
			- 構造の図の稼働の印（#622）：箱と枠のエージェントの印は、専用の行（エージェントの行。箱ではほかの印の下、入れ子の枠では見出しの行の下・要約の行の上）に左寄せで、上限なくすべて出し（前の上限 箱2・枠3 と『+N』はなくなる）、箱の幅で折り返し、行1つにつき箱（入れ子の枠では見出し）が縦に伸びる。エージェントのいない箱は前の高さ。『後に続く』の数はそのまま残る。ボードと横の欄の印（上限4）は変わらない。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.4 に戻す（API の2項目は消え、図は前の印に戻る。保存のキーは変わらない）。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.4 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.4 のバイトのハッシュ：migration.md `47902bb9…`、版のファイル `a61cc7a9…`）を `known_old_sha256` の末尾に足す（0.9.3 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.4:src/spec_dock/assets/spec_dock/<道>` で migration.md、system/spec-dock-version、docs/reference_cli.md を取り、`tests/fixtures/issue623/migration.md.0.9.4.txt`、`spec-dock-version.0.9.4.txt`、`reference_cli.md.0.9.4.txt` に置く。統合テスト `tests/integration/test_issue623_release_0_9_5.py` を `test_issue609_release_0_9_4.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（3つの行が今のバイトと 0.9.4 のバイトを知る）、0.9.4 の資産を持つ consumer の `installation update`（3つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.4 の実際の手順（タグ v0.9.4 が PR #610 のマージのコミット 2c7427a97 を指すこと、`.github/workflows/release-tag.yml`、iss-00609 の report.md、uv tool の receipt）から 0.9.5 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の JSON の契約の変更はない。ダッシュボードの `GET /api/v1/repositories` は項目が2つ増えるだけ。ブラウザーの保存は変わらない。0.9.4 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
