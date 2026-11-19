package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "版と配布資産の版だけを上げ、機能のコードは変えない。誤りは次の版で直せるが、全リポジトリの canonical check と CI の見本に効く"
}

purpose:    "SpecDock 0.9.9（指揮の帯を `Unscoped` の行に変え、主のチェックアウト（`Primary`）と Scope に紐づかない worktree（`Unlinked`）を並べる #669（iss-00668））を出し、本人の PC に配れるようにする。"
background: "0.9.8（v0.9.8 = 1cfce6f96、PR #666 のマージのコミット）の後に PR #669 だけが main に入った（`git log --first-parent v0.9.8..origin/main`、origin/main = c2163d912）。変わったのは dashboard の資産（views/_shared/orca_marks.js、views/allgraph*、views/graph*、views/graph/unscoped.js）、構造の API の `worktrees.items`（runtime の dashboard_http.py・dashboard_scope_details.py）とテストで、配る静的資産（`src/spec_dock/assets/spec_dock/`、static-inventory.json）は変わっていない（`git diff --stat v0.9.8 origin/main`）。構造の API は reference_cli.md で契約にしない画面の中の JSON とされている。手順は 0.9.8 のリリース（iss-00663、PR #666）と同じ。マージ、タグ、導入、配布は統括が行う。"
includes: ["版の番号", "migration.md の 0.9.9 の節（提供側と dogfood の写し）", "static-inventory.json の2行", "0.9.8 の旧資産の fixture（2つ）と統合テスト"]
excludes: ["機能のコードの変更", "reference_cli.md の変更（『指揮の帯』も構造の図の帯の札も書かれておらず、構造の API の JSON は契約にしないと書かれているので要らない）", "マージ、タグの作成、パッケージの導入、配布（統括）", "`work finish`（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.9 になる"
		text:  "`pyproject.toml`、`uv.lock` の spec-dock の版、`system/spec-dock-version`（提供側 `src/spec_dock/assets/spec_dock/system/` と dogfood `spec-dock/system/`）が 0.9.9 になる。0.9.8 の版を固定するテストは外す。"
		acceptance: [
			"4つの場所の版がすべて 0.9.9 で、統合テストが確かめる",
			"新しく作った wheel を隔離した venv に入れると `spec-dock --version` が `spec-dock 0.9.9` を返す",
		]
	}
	"R-02": {
		title: "migration.md が 0.9.9 の変更を説明する"
		text:  "提供側と dogfood の `docs/migration.md`（バイト一致）に「## 0.9.9 への更新」の節が「## 0.9.8 への更新」の直後にある。iss-00668 の report.md の「移行の案内に書く文」に沿って、帯が `Unscoped` の行になり先頭にいつも主のチェックアウト（`Primary`）が出ること（Orca がなくても、誰も指揮していなくても）、Scope に紐づかない worktree が `Unlinked` で並び `git worktree list` の worktree から見つけること（仕様の置き場・bare・prunable は出ない）、エージェントのいない worktree は薄く出て2つ以上は `+N` に畳まれること、1つの worktree は1つの項目で中にエージェントの印を並べること、項目を押すと詳細の欄が出ること、『これから』では指揮の線を引かず指揮している数を添えること、札「main のチェックアウト」がブランチ名と `Primary` に変わったこと、構造の API の `worktrees.items`、契約の変更がないこと、変わる配布資産は2つ、`installation update` の手順、0.9.8 以前の配布資産からも上がること、常駐の自動の起動し直し、戻し方を書く。"
		acceptance: [
			"見出しの順（0.9.8 の直後に 0.9.9）と、主な語（installation update、#669、Unscoped、Primary、Unlinked、git worktree list、薄く、+N、1つの項目、これから、指揮の線、数、main のチェックアウト、worktrees、items、契約、自動で起動し直、0.9.8 に戻）が節にあることを統合テストが確かめる",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.9.8..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.9.8 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `spec-dock/docs/migration.md` と `spec-dock/system/spec-dock-version` の行が今のハッシュと、0.9.8 のバイト（タグ v0.9.8）を既知の古い版として持つ。`spec-dock/docs/reference_cli.md` の行は 0.9.8 から変わらないので変えない。0.9.7〜0.9.0 のバイトも既知の古い版に残る。ほかの行は変えない。"
		acceptance: [
			"0.9.8 のバイトの fixture（migration.md、版のファイル）から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
			"0.9.7・0.9.6・0.9.5・0.9.4・0.9.3・0.9.2・0.9.1・0.9.0 の consumer の更新のテスト（test_issue663、test_issue645、test_issue634、test_issue623、test_issue609、test_issue599、test_issue594、test_issue585）も通る",
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
	"0.9.8 の節より前の本文（配布済みのバイト）は変えない",
]

decisions: [
	"実装は Codex GPT-6.1 Sol / medium を使い、要件・設計・計画と migration.md の節はタスク担当が書く（依頼書、本人の指示 2026-11-13）",
	"0.9.9 の節の中身は、依頼書の「移行の案内の 0.9.9 の節に必ず書くこと」と iss-00668 の report.md の「移行の案内に書く文」に従う（統括の依頼書、2026-11-19）",
	"reference_cli.md は変えない。reference_cli.md は『指揮の帯』や帯の札を書いておらず（`rg 指揮` で該当なし）、構造の API（`/api/v1/r/…/structure`）の JSON は契約にしないと書いている（126行目）。#669 は CLI の引数・CLI の JSON・画面の道・ブラウザーの保存のキーを変えない（`git diff v0.9.8 origin/main` に reference_cli.md とキーの追加がない）。タスク担当の判断",
]
