package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.4（エージェントのタブの直し #604・#605（iss-00602）、構造の図の見せる範囲の切り替え #606（iss-00603）、依存の線の切り替えの廃止 #608（iss-00607））を出し、本人の PC に配れるようにする。"
background: "0.9.3（v0.9.3 = 16f0cf122、PR #600 のマージのコミット）の後に PR #604、#606、#608、#605 が main に入った（`git log --first-parent v0.9.3..origin/main`）。変わったのは dashboard の資産（agents_logic.js、agents_tab.js、panel.js、graph.css、graph.js、graph/layout.js、graph/prefs.js）、配る文書 `reference_cli.md`（#604・#605 で inventory の sha256 と v0.9.3 のバイトの known_old も合わせ済み）とテスト。手順は 0.9.3 のリリース（iss-00599、PR #600）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.4 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.3 の旧資産の fixture（3つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（#604・#605 で済み）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.4 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.4 になる。0.9.3 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.4 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.4` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.4 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.4 への更新」の節が「## 0.9.3 への更新」の直後にある。構造の図の道具の帯の変更（「終わったものも」「片付けの候補を畳む」「待っている線｜すべての線｜線なし」がなくなり、「全体｜いま｜これから」の1つの切り替えと、画面に収めるボタンの文字「収める」になる）、ブラウザーの保存のキー `specdock.graph.v3` と前の選びの移し替え（showDone が真なら全体、それ以外はいま、線の選びは捨ててすべての線）、エージェントのタブの直し（iss-00602 の5点と欄の足のリンク）、コマンドの引数と JSON の契約の変更はないこと、変わる配布資産は3つ、`installation update` の手順、0.9.3 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.3 の直後に 0.9.4）と、主な語（installation update、#604、#605、#606、#608、全体、いま、これから、収める、終わったものも、片付けの候補を畳む、待っている線、specdock.graph.v3、showDone、すべての線、gone:、契約、自動で起動し直、0.9.3 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.3..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.3 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.3 のバイト（タグ v0.9.3）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は #604 で 0.9.3 のバイトを既知の古い版に持つので変えない。0.9.2〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.3 のバイトの fixture（migration.md、版のファイル、reference_cli.md）から作った consumer が `installation update` で3つのファイルだけ変わって成功する",
			"0.9.2・0.9.1・0.9.0 の consumer の更新のテスト（test_issue599、test_issue594、test_issue585）も通る",
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
	"0.9.3 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: [
	"実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）",
	"0.9.4 の節の中身は、依頼書の「移行の案内の 0.9.4 の節に必ず書くこと」に従う（統括の訂正 msg_deb57611cc88、2026-11-16）",
]
