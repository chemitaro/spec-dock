package spec

current: "版は 0.9.5。migration.md の最後の版の節は「## 0.9.5 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.5 のバイト（`9ea0ec4a…`、`8780409d…`）。reference_cli.md の行は #628・#636 で今のバイトと 0.9.5 のバイト（known_old、`249f76e9…`）を持つ。`tests/integration/test_issue623_release_0_9_5.py` が版 0.9.5 を固定する。"
target:  "版は 0.9.6。「## 0.9.6 への更新」が 0.9.5 の節の直後にあり、0.9.5 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.6\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue623_release_0_9_5.py` の `test_the_version_is_0_9_5_in_every_place` を消す（0.9.5 のときに 0.9.4 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.6 の節"
		text: """
			「## 0.9.5 への更新」の節の後、「## 新規導入」の前に「## 0.9.6 への更新」を足す。内容は iss-00614・00627・00629・00635・00624 の report.md と仕様、`git diff v0.9.5 origin/main`、配る `reference_cli.md` で確かめる。

			- 冒頭：#628・#630・#631・#636 を届ける版（#626 はテストだけ）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約は変わらない。ダッシュボードの JSON は `GET /api/v1/repositories` から `tier` がなくなるだけ（0.9.5 だけで配り使う者がないので v1 のまま消す版の規則の例外。`parent` は残る）。変わる配布資産は migration.md、版のファイル（0.9.6）、`docs/reference_cli.md`（画面の道に `/graph`・`/todos`、API の説明から `tier` を消す）の3つ。
			- `installation update` の手順。0.9.5 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- 『横断の構造』（#628、#631）：横断の画面のタブ『横断の概況』『横断の構造』『人のタスク』。`/graph` に表示しているすべてのリポジトリの構造の図を、`parent` に従うチェックアウトの入れ子の枠のまま1枚に描く。枠の見出しは名前だけで、段の札は出さない（#636）。子の枠は親の図の右に入れば同じ行、入らなければ次の行。『全体・いま・これから』をすべての枠に当て、既定は『これから』。選びは `specdock.allgraph.v1`（`specdock.graph.v3` に触れない）。最初の表示は PC では幅に合わせ左上から縦に読む、スマホは 74% で左寄せ。『収める』、箱を押すと横の欄、稼働の印はエージェントの行。
			- 構造の図の枠と線（#630）：見出しの行の高さが少し詰まる（題名 22px、要約 18px、Epic の上の余白 8px）。見込みと実寸がそろい、線が箱や見出しに重ならず、線どうしも 8px より近づかない。2行の縮めた枠は描いた後に測り直す。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.5 に戻す（タブと /graph が消え、`tier` が戻り、図の見出しと線は前に戻る。`specdock.graph.v3` は変わらない）。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.5 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.5 のバイトのハッシュ：migration.md `9ea0ec4a…`、版のファイル `8780409d…`）を `known_old_sha256` の末尾に足す（0.9.4 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.5:src/spec_dock/assets/spec_dock/<道>` で migration.md、system/spec-dock-version、docs/reference_cli.md を取り、`tests/fixtures/issue634/migration.md.0.9.5.txt`、`spec-dock-version.0.9.5.txt`、`reference_cli.md.0.9.5.txt` に置く。統合テスト `tests/integration/test_issue634_release_0_9_6.py` を `test_issue623_release_0_9_5.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（3つの行が今のバイトと 0.9.5 のバイトを知る）、0.9.5 の資産を持つ consumer の `installation update`（3つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.5 の実際の手順（タグ v0.9.5 が PR #625 のマージのコミット 0c0e06951 を指すこと、`.github/workflows/release-tag.yml`、iss-00623 の report.md、uv tool の receipt）から 0.9.6 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の JSON の契約の変更はない。ダッシュボードの `GET /api/v1/repositories` から `tier` がなくなる（版の規則の例外、reference_cli.md に明記）。画面の道 `/graph` が増える。ブラウザーの保存のキー `specdock.allgraph.v1` が増え、`specdock.graph.v3` は変わらない。0.9.5 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
