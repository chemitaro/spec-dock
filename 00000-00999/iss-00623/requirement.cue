package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.5（『これから』で中に見える Scope がない親を出さない #618（iss-00611）、ダッシュボードのリポジトリの一覧の parent・tier #619（iss-00613）、構造の図の稼働の印を専用の行に移す #622（iss-00620））を出し、本人の PC に配れるようにする。"
background: "0.9.4（v0.9.4 = 2c7427a97、PR #610 のマージのコミット）の後に PR #618、#619、#622 が main に入った（`git log --first-parent v0.9.4..origin/main`）。変わったのは dashboard の資産（graph.css、graph.js、graph/layout.js、_shared/orca_marks.js、_shared/parts.js）、runtime の dashboard_http.py・dashboard_nesting.py・dashboard_site.py、配る文書 `reference_cli.md`（#619 で inventory の sha256 と v0.9.4 のバイトの known_old も合わせ済み）とテスト。手順は 0.9.4 のリリース（iss-00609、PR #610）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.5 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.4 の旧資産の fixture（3つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（#619 で済み）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.5 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.5 になる。0.9.4 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.5 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.5` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.5 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.5 への更新」の節が「## 0.9.4 への更新」の直後にある。『これから』で中に見える Scope がない親（Initiative・Epic、子を持つ Issue）を出さないこと（子のない開いた Scope は出す、全体・いまは変わらない）、`GET /api/v1/repositories` の各リポジトリの `parent`・`tier`（チェックアウトの入れ子と段の札。道は返さない。画面はまだ使わない）、構造の図の稼働の印が専用の行（エージェントの行）に移り、上限なくすべて出して箱の幅で折り返し、行の数だけ箱と枠が縦に伸びること（『後に続く』は残る。ボードと横の欄は変わらない）、コマンドの引数と CLI の JSON の契約の変更はなくダッシュボードの JSON は項目が増えるだけなこと、変わる配布資産は3つ、`installation update` の手順、0.9.4 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.4 の直後に 0.9.5）と、主な語（installation update、#618、#619、#622、これから、parent、tier、エージェントの行、折り返、後に続く、契約、自動で起動し直、0.9.4 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.4..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.4 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.4 のバイト（タグ v0.9.4）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は #619 で 0.9.4 のバイトを既知の古い版に持つので変えない。0.9.3〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.4 のバイトの fixture（migration.md、版のファイル、reference_cli.md）から作った consumer が `installation update` で3つのファイルだけ変わって成功する",
			"0.9.3・0.9.2・0.9.1・0.9.0 の consumer の更新のテスト（test_issue609、test_issue599、test_issue594、test_issue585）も通る",
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
	"0.9.4 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: [
	"実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）",
	"0.9.5 の節の中身は、依頼書の「移行の案内の 0.9.5 の節に必ず書くこと」に従う（統括の依頼書、2026-11-17）",
]
