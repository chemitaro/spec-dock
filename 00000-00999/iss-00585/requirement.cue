package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.1（構造の図の配置の直し #584、iss-00583）を出し、本人の PC に配れるようにする。"
background: "0.9.0（v0.9.0 = 982932e47）の後に PR #584 だけが main に入った（`git log v0.9.0..origin/main`、変わったのは dashboard の layout.js・graph.js のコメントとテスト）。手順は 0.9.0 のリリース（iss-00580、PR #582、コミット 66175daa3）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.1 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.0 の旧資産の fixture と統合テスト"]
excludes: ["機能のコードの変更", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.1 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.1 になる。0.9.0 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.1 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.1` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.1 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.1 への更新」の節が「## 0.9.0 への更新」の直後にある。#584 の構造の図の配置の変更（塊を先に置き、つながりのない Scope を空きに詰める。最上位も見える幅で折り返す）、コマンド・API・JSON の契約の変更はないこと、変わる配布資産は2つ、`installation update` の手順、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.0 の直後に 0.9.1）と、主な語（installation update、#584、契約、見える幅、自動で起動し直、0.9.0 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.0..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.0 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.0 のバイト（タグ v0.9.0）を既知の古い版として持つ。ほかの行は変えない。"
		acceptance: [
			"0.9.0 のバイトの fixture から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
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
	"0.9.0 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: ["実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）"]
