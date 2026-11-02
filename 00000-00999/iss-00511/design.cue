package spec

// 設計（Issue）。型 specdock/v1。

goals: ["文書の古い記述を直し、固定のしかたを文の数字ではなく実体（カタログ）にする", "撤去した案内の不在と、作った report.md のバイトを、テストで守る", "`canonical check` を業務コマンドと同じ宣言の読み方にそろえる"]
current: "README の数と `docs/github-issue-integration.md`、package-data に 0.5.0 の撤去の跡が残る。撤去の不在と 0.4.2 との report.md の一致を確かめるテストがなく、`canonical check` は重複したキーの宣言を通す。"
target:  "文書が現行の実体に合い、テストが撤去の不在とバイトを固定し、`canonical check` が重複したキーを失敗の1件にする。公開の契約は、R-03 のほかは変えない。"

design: {
	"D-01": {
		title:     "文書の直し"
		text:      "README.md の入口の数を `len(cli.catalog.LEAF_ARGUMENTS)`（今は 53）に直す。`tests/unit/infra/test_issue477_authoring_docs.py` は文の数字の固定をやめ、README の「全N コマンド」の N が `LEAF_ARGUMENTS` の数と等しいことを確かめる（D-06 の方針）。`docs/github-issue-integration.md:7` は local backend とローカル metadata の記述を消し、GitHub が状態の正本であることだけを書く。`pyproject.toml` の package-data から `templates/{initiative,epic,issue}/.workbench/README.md` の3行を外す（`cue/*/.workbench/README.md` と `root` は残す）。外してよいことは、そのディレクトリが `src/spec_dock/assets/` に無いことと、fresh wheel のファイル一覧の差で確かめる。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "撤去した案内の不在のテスト"
		text:      "`tests/unit/infra/test_issue511_removed_guidance.py` を足す。`src/spec_dock/assets/` の下の配布する文書とスキル（`*.md`、`*.html`、`SKILL.md`）を全部読み、禁止の語（`spec-dock workspace migrate`、`workbench copy`、`--ci`、`--source local`、`.meta.json` を作る案内）が無いことを確かめる。歴史として残す記述は許す範囲を表にする：`docs/migration.md` の「0.5.0 への更新」の節と、0.4.x への更新の節（撤去前の手順を歴史として書く）。表に無い箇所での出現は失敗にし、表の各項目が実在する（古い許可が残らない）ことも確かめる。`--ci` は `--cia` のような語の一部に当たらないよう、語の境界で数える。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "作った report.md のバイトのテスト"
		text:      "0.4.2 が作った `report.md` を、種類ごとに固定の入力（ID、日付の印）で再現した fixture として `tests/fixtures/issue511/report-0.4.2-<kind>.md` に置く。fixture は `git show v0.4.2:` の雛形に、0.4.2 の手順（`strip_structure_front_matter`、`rebase_spec_dock_links`、`_replacements`）を当てて作る。`scope create` を既存の `WriteWorld` で3種類について実行し、作られた `report.md`（日付の行は印にそろえる）が fixture とバイトで一致することを確かめる。0.4.2 から 0.5.0 での雛形の差は、0.4.2 が実行時に落としていた `タイトル:` と `親:` の行を雛形から外しただけで、出力は同じ。"
		satisfies: ["R-02"]
	}
	"D-04": {
		title:     "`canonical check` の重複キー"
		text:      "`application/canonical_check.py` の `_declaration_failure` が宣言を読むときに `object_pairs_hook` を渡し、同じキーが2回現れたら失敗の1件にする。`project_context._unique_members` は非公開で、変更は許可の範囲の外なので、同じ6行の小さな hook を `canonical_check.py` に持つ（業務コマンドと同じ判定）。失敗は既存の `WORKSPACE_DECLARATION_INVALID`（`path` は `spec-dock/workspace.json`、`details.reason` は新しい値 `duplicate-member`、`next_step` は他の宣言の失敗と同じ）。`canonical check` の終了コードは、失敗が1件以上のときの既存の値のまま（変えない）。新しいエラーのコードは足さない。JSON の形も変えず、`reason` の値が1つ増えるだけ。後ろのキーが勝つ読み方で通っていた宣言が、失敗になる。"
		satisfies: ["R-03"]
	}
	"D-05": {
		title:     "配布する文書の hash と、候補14の判断"
		text:      "配布する文書を変えたら `static-inventory.json` の今の hash を更新し、0.5.0 のバイト（`v0.5.0` のタグの内容）を既知の古い版として足す。#509 と #520 が足した古い版（`tests/fixtures/issue509`、`issue520`）とは、同じファイルでは両方残して食い違わないようにする。変えた文書は dogfood の写し（`spec-dock/` の下）にも同じ PR で反映する。候補14（入れたコンソールでの `work start`／`work finish` の e2e）は足さない。理由：本物の定期の実行（GitHub と定期のカタログの同期）に触れずに子のプロセスで動かす手段が無く、足すとテストが利用者の環境に作用するため。`work start`／`work finish` は、プロセス内のテスト（`tests/integration/test_issue440_g1_start_processes.py` など）と、入れたコンソールでの読むコマンドと `workspace sync` で確かめる。この判断は `report.md` に書く。"
		satisfies: ["R-01", "R-02"]
	}
}

compatibility: "R-03 は契約の変更：重複したキーを持つ版4の宣言が、`canonical check` で失敗（`WORKSPACE_DECLARATION_INVALID`、`details.reason=duplicate-member`）になる。#513 が `migration.md` の 0.5.1 の節に載せる。そのほかの契約は変えない。版は上げず、`migration.md` に節を足さない。"
risks: ["文書の禁止語のテストが、許可の表の外の正当な説明にも当たる。→ 許可の表を明示し、当たったら表か文書を直す", "fixture が 0.4.2 の出力と食い違う。→ `git show v0.4.2:` の雛形から手順で再現し、手順を test の docstring に残す"]
