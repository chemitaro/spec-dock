package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版の番号、移行の案内、配る資産の一覧を上げる。誤りは配布の不整合にとどまり、前の版に戻せば回復できる"
}

purpose:    "SpecDock 0.9.10（Antigravity での canonical の読み書きの確かめと案内 #677（iss-00673）、ダッシュボードのエージェントの種類の名前 #678（iss-00674）、『これから』でも指揮の線 #679（iss-00676））を出し、本人の PC に配れるようにする。"
background: "0.9.9（v0.9.9 = 83b8ee95f、PR #671 のマージのコミット）の後に、PR #678、#677、#679 が main に入った（`git log --first-parent v0.9.9..origin/main`、origin/main = a6000d8cd）。配る静的資産では、#677 が `docs/canonical.md`（Antigravity の項）と `docs/reference_cli.md`（C45）を変え、`static-inventory.json` の2行にすでに 0.9.9 のバイトを `known_old_sha256` として足した（`git diff --stat v0.9.9 origin/main -- src/spec_dock/assets`）。#678 と #679 は、パッケージが配るダッシュボードの資産とランタイムだけを変えた。手順は 0.9.9 のリリース（iss-00670、PR #671）と同じ。親は epic-00672 の R-04・D-03。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.10 の節と、0.9.9 の節の『これから』への注（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.9 の旧資産の fixture（4つ）と統合テスト"]
excludes: ["機能のコードの変更", "canonical.md と reference_cli.md の変更（#677 で済み）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.10 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.10 になる。0.9.9 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.10 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.10` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.10 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.10 への更新」の節が「## 0.9.9 への更新」の直後にある。iss-00673・iss-00674・iss-00676 の report.md の案内の文に沿って、Antigravity の作業用のworktreeでユーザーの設定 `~/.gemini/antigravity-cli/settings.json` の `permissions.allow` に `read_file(<カタログ>)` と `write_file(<カタログ>)` の1行を足すこと、`canonical status --json` の `data.tools.antigravity` と警告 `CANONICAL_TOOL_SETTING_MISSING`（`ANTIGRAVITY_AGENT` があるときだけ）、ダッシュボードがエージェントの種類を orca-web の部品の名前で出し Antigravity と Gemini の名前には orca-web main `4ad7471` 以降が要ること、『これから』でも指揮の線が出て子の数の札がなくなること、契約の変更、変わる配布資産は4つ、`installation update` の手順、0.9.9 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。0.9.9 の節の『これから』の記述の後に、0.9.10 で変わったことが分かる注を1つ足す（0.9.9 の節の今の本文は書き換えない）。"
		acceptance: [
			"見出しの順（0.9.9 の直後に 0.9.10）と、主な語（installation update、#677、#678、#679、Antigravity、~/.gemini/antigravity-cli/settings.json、permissions.allow、read_file、write_file、tools.antigravity、CANONICAL_TOOL_SETTING_MISSING、ANTIGRAVITY_AGENT、Gemini、4ad7471、これから、指揮の線、子の数、canonical.md、reference_cli.md、契約、自動で起動し直、0.9.9 に戻）が節にあることを統合テストが確かめる",
			"0.9.9 の節に 0.9.10 を指す注があり、0.9.9 の節の今の本文（v0.9.9 の行）がそのまま残ることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.9..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.9 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.9 のバイト（タグ v0.9.9）を既知の古い版として持つ。`canonical.md` と `reference_cli.md` の行は #677 で 0.9.9 のバイトを既知にしたので変えない。0.9.8〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.9 のバイトの fixture（migration.md、版のファイル、canonical.md、reference_cli.md）から作った consumer が `installation update` で4つのファイルだけ変わって成功する",
			"0.9.8〜0.9.0 の consumer の更新のテスト（test_issue670、test_issue663、test_issue645、test_issue634、test_issue623、test_issue609、test_issue599、test_issue594、test_issue585）も通る",
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
	"0.9.9 の節の今の本文と、それより前の節は変えない（0.9.9 の節には注の1項目を足すだけ）",
]

decisions: [
	"実装は Codex GPT-6.2 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13、方針の表は 2026-11-19 から GPT-6.2 Sol）",
	"0.9.10 の節の中身は、依頼書の「移行の案内の 0.9.10 の節に必ず書くこと」と、iss-00673・iss-00674・iss-00676 の report.md の案内の文に従う（統括の依頼書、2026-11-20）",
	"0.9.9 の節の『これから』の記述には、本文を書き換えず、0.9.10 で変わったことを示す注を足す（iss-00676 の report.md の提案、統括の依頼書 2026-11-20）",
	"fixture には、0.9.9 の consumer が持つ4つのファイルを置く。canonical.md と reference_cli.md は 0.9.10 の consumer で変わるので、0.9.9 からの更新の確かめに要る（タスク担当の判断、`git diff --stat v0.9.9 origin/main`）",
]
