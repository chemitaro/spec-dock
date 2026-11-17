package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.7（各リポジトリの構造の図の指揮の線と『指揮の帯』 #642（iss-00616）、『横断の構造』の指揮の線と枠ごとの帯と見出しの文字を線の上に #644（iss-00617）、横断の構造の知らせのまとめ #639（iss-00632）、横断の構造の帯の並び #643（iss-00640）、木の表示の線の通り道 #641（iss-00633））を出し、本人の PC に配れるようにする。"
background: "0.9.6（v0.9.6 = 4c49b68b6、PR #638 のマージのコミット）の後に PR #639、#641、#642、#643、#644 が main に入った（`git log --first-parent v0.9.6..origin/main`、origin/main = 2fa809271）。変わったのは dashboard の資産（app.css、views/_shared/logic.js、views/allgraph*、views/graph*）とテストだけで、runtime と配る静的資産（`src/spec_dock/assets/spec_dock/`、static-inventory.json）は変わっていない（`git diff --stat v0.9.6 origin/main`）。手順は 0.9.6 のリリース（iss-00634、PR #638）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.7 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.6 の旧資産の fixture（2つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（0.9.6 から契約と画面の道が変わらないので要らない）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.7 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.7 になる。0.9.6 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.7 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.7` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.7 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.7 への更新」の節が「## 0.9.6 への更新」の直後にある。構造の図と『横断の構造』に Orca の指揮の線（親のエージェントの印から子の印へ、黄色の点の流れ、同じ箱は弧、working は流れ・待ちは止まった点線・done は薄い線、動きを減らす設定で止まる）と『指揮の帯』（箱のない親と子。main のチェックアウト・ほかのリポジトリ・ほかの場所）が出ること、使うには orca-web の要約の parent が要ること（orca-web の iss-00043 以降）、エージェントの行が箱の底に寄ること、枠の見出しの文字が線の上に出ること、横断の構造の知らせのまとめと帯の並び、木の表示の線の直し、契約の変更がないこと、変わる配布資産は2つ、`installation update` の手順、0.9.6 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.6 の直後に 0.9.7）と、主な語（installation update、#639、#641、#642、#643、#644、指揮の線、指揮の帯、黄色、弧、working、waiting、done、prefers-reduced-motion、main のチェックアウト、ほかのリポジトリ、ほかの場所、parent、iss-00043、箱の底、見出しの文字、知らせ、帯の並び、木の表示、契約、自動で起動し直、0.9.6 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.6..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.6 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.6 のバイト（タグ v0.9.6）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は 0.9.6 から変わらないので変えない。0.9.5〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.6 のバイトの fixture（migration.md、版のファイル）から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
			"0.9.5・0.9.4・0.9.3・0.9.2・0.9.1・0.9.0 の consumer の更新のテスト（test_issue634、test_issue623、test_issue609、test_issue599、test_issue594、test_issue585）も通る",
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
	"0.9.6 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: [
	"実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）",
	"0.9.7 の節の中身は、依頼書の「移行の案内の 0.9.7 の節に必ず書くこと」に従う（統括の依頼書、2026-11-17）",
	"reference_cli.md は変えない。0.9.7 で CLI・ダッシュボードの JSON の契約と画面の道が変わらないため（`git diff v0.9.6 origin/main` に reference_cli.md と runtime の変更がない。タスク担当の判断）",
]
