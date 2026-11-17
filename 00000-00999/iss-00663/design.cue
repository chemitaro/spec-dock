package spec

current: "版は 0.9.7。migration.md の最後の版の節は「## 0.9.7 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.7 のバイト（`6ecfd102…`、`6c38d2d8…`）。reference_cli.md の行の sha256（`9375d7fd…`）は v0.9.7 と今のバイトで同じ。`tests/integration/test_issue645_release_0_9_7.py` が版 0.9.7 を固定する。"
target:  "版は 0.9.8。「## 0.9.8 への更新」が 0.9.7 の節の直後にあり、0.9.7 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.8\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue645_release_0_9_7.py` の `test_the_version_is_0_9_7_in_every_place` を消す（0.9.7 のときに 0.9.6 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.8 の節"
		text: """
			「## 0.9.7 への更新」の節の後、「## 新規導入」の前に「## 0.9.8 への更新」を足す。内容は iss-00646・00648・00650・00657・00655・00656 の report.md と仕様、`git diff v0.9.7 origin/main` で確かめる。

			- 冒頭：#649・#658・#660・#659・#661・#662 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーは変わらない（diff に保存のキーの追加がない）。変わる配布資産は migration.md と版のファイル（0.9.8）の2つ。
			- `installation update` の手順。0.9.7 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- 動きを軽く（#649）：線ごとの小さな絵、主スレッドで毎コマ描き直さない、動かす間（止めてから0.3秒）・画面の外・裏で止まる。減らす設定は今までどおり止まる。
			- ホップの弧（#658）：親の側の上の縁から出て子の側の上の縁へ入る上にふくらむ弧、下の回り込みと箱の中の短い線をやめた、子の端の下向きの矢じりと受けた印の縁の指揮の色、同じ箱は上の縁の小さな弧。色・状態・波紋・帯は同じ。
			- 点の組（#660）：間 24px の大小2つの点（頭と 6px 後ろの尾）、20px/秒、向きが分かる、波紋も遅く、減らす設定では止まった組。
			- 帯の印から開くチャット（#659）：欄の高さいっぱい、スマホの下からの欄で引いて全面・半分・閉じる、片付けの候補の欄も、描き直しで段が戻らない。
			- 図の操作（#661）：矢印キー 80px・Shift で4倍、`+`（`=`）・`-`・`0`、入力欄などのフォーカスと修飾キーでは働かない、マウスのホイールでカーソルの位置で拡大・縮小、Shift のホイールは横、トラックパッドの2本指は動かす・ピンチは拡大・縮小、見分けられないときは動かす。
			- Scope の欄の見出し（#662）：パンくず・ID・番号・種類・状態の札の1行目と題名の2行目、足す情報か『N分動きなし』があるときだけ1行の帯、マージの札は帯の理由に、説明資料の上の帯をなくし新しいタブで開く印をタブの行の右端に、欄の下の行は同じ。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.7 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.7 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.7 のバイトのハッシュ：migration.md `6ecfd102…`、版のファイル `6c38d2d8…`）を `known_old_sha256` の末尾に足す（0.9.6 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.7:src/spec_dock/assets/spec_dock/<道>` で migration.md と system/spec-dock-version を取り、`tests/fixtures/issue663/migration.md.0.9.7.txt`、`spec-dock-version.0.9.7.txt` に置く（reference_cli.md は 0.9.7 と同じバイトなので fixture を置かない）。統合テスト `tests/integration/test_issue663_release_0_9_8.py` を `test_issue645_release_0_9_7.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（2つの行が今のバイトと 0.9.7 のバイトを知る）、0.9.7 の資産を持つ consumer の `installation update`（2つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.7 の実際の手順（タグ v0.9.7 が PR #647 のマージのコミット 60197049e を指すこと、`.github/workflows/release-tag.yml`、iss-00645 の report.md、uv tool の receipt の wheel）から 0.9.8 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の JSON の契約、ダッシュボードの JSON、画面の道、ブラウザーの保存のキーの変更はない。0.9.7 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
