package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"canonical の処理を、撤去の前に従来の処理が守っていた安全の水準に戻す",
	"直しを1回のリリースで5つのリポジトリに届け、配る手間を1回にする",
	"移行のために残したものを、戻す必要がないと確かめてから片付ける",
]
current: "0.5.0。canonical の処理には、確認の後の読み直し、途中の失敗の報告、unlock の後の無視されたファイルの判定に不足がある（`iss-00440/report.md` の後続の候補）。5つのリポジトリは 0.5.0。移行の控えと版3の worktree 2つが残る。"
target:  "0.5.1。不足を直し、5つのリポジトリが 0.5.1 にそろう。控えと版3の worktree は、利用者が決めたとおりに片付いている。"

design: {
	"D-01": {
		title:     "確認の後の読み直し"
		text:      "`scope close`／`reopen` は端末での確認の後に直接の選択を、`scope create` は確認の後と GitHub に書く前に `origin` を読み直す（application 層）。変わっていれば、何も書かずに止まる。作成の後にリポジトリが変わっていれば、カタログに公開しない。エラーのコードと次の1手は、従来の処理（撤去の前のテスト。`iss-00440/report.md` の候補 1〜3 に名前がある）を手本にし、#506 の設計で決める。"
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title:     "途中の失敗の報告"
		text:      "`scope delete` は、記録の削除が効いた後の後片付けの失敗を `selection.clear succeeded` として返し、ディレクトリの削除を試みたかを `TreeRemovalIncomplete.attempted` で判定する。`artifact create` は、`artifacts/` を作った後の失敗を `partial`（`artifact.directory unknown`）で返し、作ったディレクトリを残す。"
		satisfies: ["R-02", "F-01"]
	}
	"D-03": {
		title:     "unlock の後の判定"
		text:      "`worktree remove --unlock` は、unlock の後に、無視されたものがリンクだけかを判定する。ほかのものがあれば、`--discard-ignored` なしでは何も消さずに止まる。"
		satisfies: ["R-03", "F-01"]
	}
	"D-04": {
		title:     "Artifact の経路の検査"
		text:      "`finalize-artifact.py` は、`spec-dock/initiatives` がカタログ（`spec-dock/.canonical`）へのリンクのときだけ、そのリンクを安全な経路として扱う。ほかのリンクは今までどおり拒む。配布資産なので、`static-inventory.json` の既知の古い版に 0.5.0 のバイトを足す。"
		satisfies: ["R-04"]
	}
	"D-05": {
		title:     "宣言と観測の読み取り"
		text:      "宣言の読み取りで、重複キーを曖昧として扱う（終了コードと、`workspace doctor --raw` の観測の扱いは #510 の設計で決める）。`resolve_observed_context` は、2回の読み取りの間に消えた worktree を unavailable の行にする。"
		satisfies: ["R-05"]
	}
	"D-06": {
		title:     "文書とテストの整え"
		text:      "README のコマンドの数を、`cli/catalog.py` の葉の数から確かめるテストにする。撤去した案内（`workspace migrate`、`workbench copy`、`--ci`、`--source local`、`.meta.json`）の不在を、配布する文書の全体で確かめる。作った CUE の `report.md` を、0.4.2 の出力のバイトと比べる。#506〜#510 が変えた文書も含めて整えるので、最後に行う。"
		satisfies: ["R-06"]
	}
	"D-07": {
		title:     "リリースと配布"
		text:      "#501（0.4.2）と #440（0.5.0）と同じ手順。版を 0.5.1 にし、`migration.md` に「0.5.1 への更新」の節を足し、`static-inventory.json` に 0.5.0 のバイトを既知の古い版として足す。マージの後、統括が、タグの `git archive` から作った wheel を `uv tool install --force` で入れ、4つのリポジトリで一時の worktree を作って `installation update` を行い、`canonical check` を通して PR を作る（spec-dock の分はリリースの PR に含める）。input-devices の `README.md` と company-os の `contract.md` の古い版の記述も、同じ PR で直す。"
		satisfies: ["R-07", "F-02"]
	}
	"D-08": {
		title:     "控えと古い worktree の片付け"
		text:      "統括が、対象の一覧（パス、大きさ、作られた時期と理由、消したときに失うもの）を作って利用者に示す。対象：`worktrees/i12-prep/backups/`、`worktrees/i12-prep/migrate-to-canonical-state/`、`worktrees/spec-dock-042/backups/`、`worktrees/spec-dock-050/backups/`、`/private/tmp/spec-dock-v0.4.*` と `v0.5.0` の作業の置き場、版3の worktree `local-macos-vm-ci` と `schema1-preserving-migration-20261004`。版3の worktree は、#463（止めている）の再開のしかたと合わせて、main を取り込むか消すかを利用者が決める。worktree は `spec-dock worktree remove` で、正確な対象と結果を許可された後だけに消す。"
		satisfies: ["R-08", "F-03"]
	}
	"D-09": {
		title:     "完了の判定の子孫"
		text:      "`scope_completion_plan.py` と `canonical_work.py` の子孫の判定で、`completed` と `not-planned` を「閉じた子孫」として扱い、開いている子孫と状態が分からない子孫だけを止める。`DESCENDANT_NOT_COMPLETED` のコードと終了コードは変えない。"
		satisfies: ["R-09"]
	}
}

compatibility: "0.5.1 は、requirement.cue の constraints に挙げた直し（#506、#508、#510 の、誤って進んでいた操作を止めること、#507 の、途中の失敗を `partial`（終了コード6）で返すこと）のほかは、0.5.0 の公開の契約を変えない。変わる点は #513 が `migration.md` の 0.5.1 の節に書く。0.5.0 の配布資産を持つリポジトリは、`installation update` で上がる。"
risks: [
	"#506 と #507 は、scope のコマンドの近い所を直すので、ぶつかることがある。後にマージするほうが main を取り込む",
	"0.5.1 の配布の後、input-devices、company-os、housing-lifecycle で最初の実際の仕様の編集が起きる。同期の記録を見て、問題があれば F-01 の戻し方に従う",
]
