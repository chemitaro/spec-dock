package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.2（横の欄に説明資料と詳しいタブ・スマホの3段のシート #588（iss-00587）、文書のタブを詰める #590（iss-00589））を出し、本人の PC に配れるようにする。"
background: "0.9.1（v0.9.1 = 928460f48、PR #586 のマージのコミット）の後に PR #588 と PR #590 が main に入った（`git log v0.9.1..origin/main`、変わったのは src/spec_dock/assets/dashboard/ と runtime/application/dashboard_scope_details.py とテスト）。手順は 0.9.1 のリリース（iss-00585、PR #586）と同じ。マージ、タグ、導入、配布は統括が行う。0.9.1 の配布では、ほかのリポジトリの配布資産は 0.9.0 のまま（2026-11-14 に各リポジトリの spec-dock/system/spec-dock-version を確かめた）。"
includes: ["版の番号", "migration.md の 0.9.2 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.1 の旧資産の fixture と統合テスト"]
excludes: ["機能のコードの変更", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.2 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.2 になる。0.9.1 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.2 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.2` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.2 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.2 への更新」の節が「## 0.9.1 への更新」の直後にある。#588 の欄（ボードと構造の図で同じ欄、説明資料が最初のタブ、詳しい画面と同じタブ、広い欄、詳しい画面へ移る道、スマホの3段のシート）と #590 の文書のタブ（仕様と報告の2つ、1行の切り替え、枠が残りの高さを使う）、コマンドの引数と CLI の JSON の契約の変更はないこと（ダッシュボードの Scope の JSON に項目が1つ足されるだけ）、変わる配布資産は2つ、`installation update` の手順、0.9.0 の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.1 の直後に 0.9.2）と、主な語（installation update、#588、#590、契約、説明資料、3段、仕様と報告、自動で起動し直、0.9.1 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.1..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.1 と 0.9.0 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.1 のバイト（タグ v0.9.1）を既知の古い版として持つ。0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.1 のバイトの fixture から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
			"0.9.0 のバイトの consumer の更新のテスト（test_issue585）も通る",
			"ほかの行のハッシュと既知の古い版は変わらない（inventory の差分は2行の sha256 と known_old_sha256 への追加だけ）",
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
	"0.9.1 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: ["実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）"]
