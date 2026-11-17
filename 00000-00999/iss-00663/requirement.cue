package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.8（指揮の線の動きを軽く #649（iss-00646）、上の縁から出て上の縁へ入るホップの弧 #658（iss-00648）、帯の印から開くチャットの欄を高さいっぱいに・スマホで指で動かす #659（iss-00650）、点を間 24px の頭と尾の組にしてゆっくり流す #660（iss-00657）、矢印キーとマウスのホイールの拡大・縮小 #661（iss-00655）、Scope の欄の見出しの重なりを除く #662（iss-00656））を出し、本人の PC に配れるようにする。"
background: "0.9.7（v0.9.7 = 60197049e、PR #647 のマージのコミット）の後に PR #649、#658、#659、#660、#661、#662 が main に入った（`git log --first-parent v0.9.7..origin/main`、origin/main = fa9824cb9）。変わったのは dashboard の資産（views/_shared/{agents_tab,panel,panel_logic,scope_tabs}.*、views/allgraph*、views/graph*、views/scope.*）とテストだけで、runtime と配る静的資産（`src/spec_dock/assets/spec_dock/`、static-inventory.json）は変わっていない（`git diff --stat v0.9.7 origin/main`）。手順は 0.9.7 のリリース（iss-00645、PR #647）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.8 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.7 の旧資産の fixture（2つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（0.9.7 から契約と画面の道が変わらず、書かれた操作（欄の下の行の『新しいタブで開く』など）も変わらないので要らない）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.8 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.8 になる。0.9.7 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.8 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.8` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.8 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.8 への更新」の節が「## 0.9.7 への更新」の直後にある。指揮の線の動きが軽くなった（動かす間・画面の外・裏で止まる）こと、線が上の縁から出て上の縁へ入るホップの弧になり子の端に矢じりが出ること、点が間 24px の大小の組でゆっくり流れ向きが分かること、帯の印から開くチャットが欄いっぱいに広がりスマホで引いて全面・閉じるができること（片付けの候補の欄も）、構造の図と横断の構造で矢印キーで動かし（Shift で大きく）、`+`・`-`・`0`、マウスのホイールで拡大・縮小（トラックパッドの2本指は動かす、ピンチは拡大・縮小のまま）、Scope の欄の見出しがパンくず・ID・状態の1行と題名にまとまり、足す情報があるときだけ帯が出ること、新しいタブで開く印がタブの行に移ったこと、契約の変更がないこと、変わる配布資産は2つ、`installation update` の手順、0.9.7 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.7 の直後に 0.9.8）と、主な語（installation update、#649、#658、#659、#660、#661、#662、指揮の線、画面の外、裏、ホップの弧、上の縁、矢じり、24px、向き、欄の高さいっぱい、全面、片付けの候補、矢印キー、Shift、`+`、`-`、`0`、マウスのホイール、トラックパッド、ピンチ、パンくず、題名、帯、新しいタブで開く、契約、自動で起動し直、0.9.7 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.7..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.7 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.7 のバイト（タグ v0.9.7）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は 0.9.7 から変わらないので変えない。0.9.6〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.7 のバイトの fixture（migration.md、版のファイル）から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
			"0.9.6・0.9.5・0.9.4・0.9.3・0.9.2・0.9.1・0.9.0 の consumer の更新のテスト（test_issue645、test_issue634、test_issue623、test_issue609、test_issue599、test_issue594、test_issue585）も通る",
			"inventory の差分は2行の sha256 と known_old_sha256 への追加だけ",
		]
	}
	"R-04": {
		title: "マージ、タグ、導入、配布は統括が行う"
		text:  "この Issue の PR では、マージ、タグ、道具の環境（uv tool）への導入、配布をしない。配布の手順は report.md と完了の報告に書く。"
		acceptance: ["PR にタグも機能のコード（src/spec_dock/runtime/、src/spec_dock/assets/dashboard/ など）の変更もない", "report.md に配布の手順がある"]
	}
}

failures: {}

constraints: [
	"書いてよいのは、pyproject.toml、uv.lock、src/spec_dock/assets/spec_dock/system/spec-dock-version、src/spec_dock/assets/spec_dock/docs/migration.md、src/spec_dock/assets/static-inventory.json、spec-dock/docs/migration.md、spec-dock/system/spec-dock-version、tests/、この Issue の Scope だけ",
	"0.9.7 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: [
	"実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）",
	"0.9.8 の節の中身は、依頼書の「移行の案内の 0.9.8 の節に必ず書くこと」に従う（統括の依頼書、2026-11-18）",
	"reference_cli.md は変えない。0.9.8 で CLI・ダッシュボードの JSON の契約と画面の道が変わらず、reference_cli.md に書かれた画面の操作（エージェントのタブの帯、欄の下の行の『詳しい画面』『新しいタブで開く』）も変わらないため（`git diff v0.9.7 origin/main` に reference_cli.md と runtime の変更がない。iss-00656 は欄の下の行を excludes にした。タスク担当の判断）",
]
