package spec

current: "版は 0.9.6。migration.md の最後の版の節は「## 0.9.6 への更新」。static-inventory.json の migration.md と版のファイルの行の sha256 は 0.9.6 のバイト（`8a16dc86…`、`fd512333…`）。reference_cli.md の行の sha256（`9375d7fd…`）は v0.9.6 と今のバイトで同じ。`tests/integration/test_issue634_release_0_9_6.py` が版 0.9.6 を固定する。"
target:  "版は 0.9.7。「## 0.9.7 への更新」が 0.9.6 の節の直後にあり、0.9.6 のバイトが known_old_sha256 に入る。"

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml` の `version`、`uv.lock` の `name = \"spec-dock\"` の `version`、提供側と dogfood の `system/spec-dock-version`（`0.9.7\\n`）を変える。`uv.lock` は手で1行を変え、`uv lock --check` で整合を確かめる。`test_issue634_release_0_9_6.py` の `test_the_version_is_0_9_6_in_every_place` を消す（0.9.6 のときに 0.9.5 のテストから同じものを消した形）。ほかのテストは残す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "migration.md の 0.9.7 の節"
		text: """
			「## 0.9.6 への更新」の節の後、「## 新規導入」の前に「## 0.9.7 への更新」を足す。内容は iss-00616・00617・00632・00640・00633 の report.md と仕様、`git diff v0.9.6 origin/main` で確かめる。

			- 冒頭：#642・#644・#639・#643・#641 を届ける版。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）、コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON（`specdock.dashboard/v1`）、画面の道は変わらない。変わる配布資産は migration.md と版のファイル（0.9.7）の2つ。
			- `installation update` の手順。0.9.6 以前（0.9.0 から）の配布資産のままでも動き、上がる。画面の変更はパッケージが配る。
			- 指揮の線（#642、#644）：親のエージェントの印から子の印への黄色の線。working は点の流れ、waiting などの待ちは止まった点線、done は薄い線。親の端の波紋。同じ箱（枠の見出し・帯の同じ項目）は外へふくらむ弧。`prefers-reduced-motion` で止まる。印を押すと線が目立つ。凡例の行。『横断の構造』では枠をまたぐ。
			- 『指揮の帯』（#642、#644）：箱のない親と子。構造の図はすべての Initiative の上の1行（札は main のチェックアウト・ブランチ名・ほかのリポジトリの「<名前> · <ブランチ>」）。『横断の構造』は各リポジトリの枠の見出しのすぐ下と、全体のいちばん上の『ほかの場所』。帯のエージェントを押すとチャットが開く。
			- 前提：orca-web の要約の `agents[].parent`（orca-web の iss-00043 以降）。ないときは線も帯も出ず、0.9.6 と同じ。
			- エージェントの行が箱の底に寄る（行のある箱は少し高く、題名2行でも切れない）。枠の見出しの文字が線の上に出る（#644）。
			- 横断の構造の知らせのまとめ（#639）、帯の並び（#643：札 → 道具 → まとめの行）、木の表示の線の通り道（#641）。
			- 常駐のダッシュボードの自動の起動し直し、前面の serve は自分で起動し直す。
			- 戻し方：パッケージを 0.9.6 に戻す。配布資産を上げた後なら、その PR を `git revert` する。

			0.9.6 までの節は変えない。提供側を書き、dogfood に同じバイトを写す。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json、fixture、統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、それぞれの前の `sha256`（v0.9.6 のバイトのハッシュ：migration.md `8a16dc86…`、版のファイル `fd512333…`）を `known_old_sha256` の末尾に足す（0.9.5 以前のハッシュは残す）。`reference_cli.md` の行は変えない。fixture は `git show v0.9.6:src/spec_dock/assets/spec_dock/<道>` で migration.md と system/spec-dock-version を取り、`tests/fixtures/issue645/migration.md.0.9.6.txt`、`spec-dock-version.0.9.6.txt` に置く（reference_cli.md は 0.9.6 と同じバイトなので fixture を置かない）。統合テスト `tests/integration/test_issue645_release_0_9_7.py` を `test_issue634_release_0_9_6.py` と同じ形で書き、版、節（見出しの順と R-02 の主な語）と写しの一致、inventory（2つの行が今のバイトと 0.9.6 のバイトを知る）、0.9.6 の資産を持つ consumer の `installation update`（2つのファイルだけ変わる）を確かめる。"
		satisfies: ["R-03", "R-01", "R-02"]
	}
	"D-04": {
		title:     "配布（統括）と手順の記録"
		text:      "R-04 のマージ、タグ、導入、配布はマージの後に統括が行う。タスク担当は 0.9.6 の実際の手順（タグ v0.9.6 が PR #638 のマージのコミット 4c49b68b6 を指すこと、`.github/workflows/release-tag.yml`、iss-00634 の report.md、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.6-dist/spec_dock-0.9.6-py3-none-any.whl`）から 0.9.7 の手順を report.md に書く。"
		satisfies: ["R-04"]
	}
}

compatibility: "CLI の JSON の契約、ダッシュボードの JSON、画面の道、ブラウザーの保存のキーの変更はない。0.9.6 以前の配布資産は known_old_sha256 で受け入れ、installation update で上がる。"
risks: ["inventory の sha256 を migration.md の最終のバイトより前に計算すると、canonical check と統合テストが落ちる。migration.md の節を先に確定する（S-01）。"]
