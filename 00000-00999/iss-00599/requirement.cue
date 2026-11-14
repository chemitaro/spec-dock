package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.3（orca-web の場所と Scope の対応 #596（iss-00591）、稼働の印と「Orca で開く」#597（iss-00592）、エージェントのタブとチャットの埋め込み #598（iss-00593））を出し、本人の PC に配れるようにする。"
background: "0.9.2（v0.9.2 = 2265e8fc1、PR #595 のマージのコミット）の後に PR #596、#597、#598 が main に入った（`git log --first-parent v0.9.2..origin/main`）。変わったのは dashboard の資産、runtime（dashboard_http、dashboard_scope_details、dashboard_site、domain/orca_web、infra/user_config、infra/worktree_signature、presentation/dashboard_api）、配る文書 `reference_cli.md`（#597 で inventory の sha256 も合わせ済み）とテスト。手順は 0.9.2 のリリース（iss-00594、PR #595）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.3 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.2 の旧資産の fixture（3つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（#597 で済み）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.3 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.3 になる。0.9.2 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.3 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.3` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.3 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.3 への更新」の節が「## 0.9.2 への更新」の直後にある。#596〜#598 の orca-web との連携（稼働の印、「Orca で開く」、エージェントのタブ、横の欄と文書のタブまわりの変化）、利用者の設定 `config.json` の新しい節 `orca_web`（`enabled`、`port`、既定）、orca-web の `ORCA_WEB_READ_ORIGINS` に SpecDock のオリジンが要ること、orca-web がないときは印もタブも出ず図とボードはそのまま動くこと、送信は orca-web の側の `sendEnabled` で決まること、コマンドの引数と CLI の JSON の契約の変更はないこと（ダッシュボードの JSON に項目が足されるだけ）、変わる配布資産は3つ、`installation update` の手順、0.9.2 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.2 の直後に 0.9.3）と、主な語（installation update、#596、#597、#598、orca_web、enabled、port、8791、ORCA_WEB_READ_ORIGINS、sendEnabled、契約、エージェント、自動で起動し直、0.9.2 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.2..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.2 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.2 のバイト（タグ v0.9.2）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は #597 で 0.9.2 のバイトを既知の古い版に持つので変えない。0.9.1 と 0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.2 のバイトの fixture（migration.md、版のファイル、reference_cli.md）から作った consumer が `installation update` で3つのファイルだけ変わって成功する",
			"0.9.1 と 0.9.0 の consumer の更新のテスト（test_issue594、test_issue585）も通る",
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
	"0.9.2 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: ["実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）"]
