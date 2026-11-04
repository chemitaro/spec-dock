package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の既定の表示と並びを、テスト駆動で直し、このPCの実際のスナップショットで確かめ、マージできる PR にする。"

steps: {
	"S-01": {title: "構造の API に `active_at` を足す", realizes: ["R-04", "F-01"], status: "done", session: "impl"}
	"S-02": {title: "可視の判定を、親が開いていれば終わった Scope も出す形にする", realizes: ["R-01"], status: "done", session: "impl"}
	"S-03": {title: "依存の線の既定を「すべての線」にする", realizes: ["R-02"], status: "done", session: "impl"}
	"S-04": {title: "段の中と最上位の並びを活動順にする", realizes: ["R-03", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "見せ方の保存を v2 にし、`prefs.js` で v1 から一部だけ引き継ぐ", realizes: ["R-05", "F-02"], status: "done", session: "impl"}
	"S-06": {title: "ボードの「終わった」の列の並びを、既存のテスト（`test_board_columns_follow_lanes_and_rank` の newest first）で確かめる", realizes: ["R-06"], status: "done", session: "impl"}
	"S-07": {title: "PC のヘッドレスの Chrome で、このPCの spec-dock の実際のスナップショットを PC の幅と 390px で写し、`edgeAudit` を確かめ、report.md と artifacts に残す。移行の注記の材料を PR の本文と統括への報告に書く", realizes: ["R-01", "R-02", "R-03"], status: "done", after: ["S-02", "S-03", "S-04", "S-05"], session: "impl"}
	"S-08": {title: "折り返しをやめ（`wrapBlock`、`colsBlock`）、経路の寄せを4回にし、「全体」と拡大縮小の下限を収めるのに要る倍率まで下げる", realizes: ["R-07"], status: "done", session: "impl"}
	"S-09": {title: "このPCの実際の構造で、PC と 390px の初めの表示・「全体」・横のドラッグと `edgeAudit` を確かめ、写しを report.md に足し、テストとゲートを最終のコミットでやり直す", realizes: ["R-07"], status: "todo", after: ["S-08"], session: "impl"}
}

tests: {
	"T-01": {title: "`active_at` が、作成だけ、完了、PR のマージ、Issue の更新の各場合に最も新しい時刻になり、読めない時刻を使わない（pytest）", verifies: ["R-04", "F-01"]}
	"T-02": {title: "見本の既定の表示（入れ子と木）で、開いた親の終わった Scope が出て、終わった親の終わった子と親のない終わった Scope が出ない。R-12 の親と片付けの候補は今までどおり。配下がすべて終わった開いた Epic の終わった子は木と畳まない表示でも出ない。終わった Epic と片付けの候補の Epic に絞ると子が出る（node）", verifies: ["R-01"]}
	"T-03": {title: "既定の表示で、出ている終わった Issue からの依存が `done: true` の線になり、`deps: wait` では消える（node）", verifies: ["R-02"]}
	"T-04": {title: "線の検査の代表のデータのすべての表し方で問題0件（今のテストを新しい既定と可視の判定で通す）", verifies: ["R-02"]}
	"T-05": {title: "最上位の枠が4つの組と最近の順に並び、Epic の段の中で開いた箱が推奨順で上、終わった箱が最近終わった順で下。`active_at` のない Scope は最も古い扱い。既定の表示で、終わった Issue がそれを待つ開いた Issue の左の段に入り、開いた子孫を持つ閉じた親の中は開いたものだけの段（node）", verifies: ["R-03", "F-01"]}
	"T-06": {title: "`restorePrefs` が v1 から `mode`・`fold`・`legend` だけ引き継ぎ、v2 の値を守り、壊れた値と型の違う値を既定にする（node）。`graph.js` が v2 のキーに保存する（静的）", verifies: ["R-05", "F-02"]}
	"T-07": {title: "ボードの「終わった」の列の先頭が最も新しく終わった Scope（既存の node のテスト `test_board_columns_follow_lanes_and_rank`）", verifies: ["R-06"]}
	"T-09": {title: "依存のない12件の Issue の Epic と親のない12件の Issue が1行で幅 1240px を超え、7段の依存が1行に並び、代表のデータの線の検査が0件（node）", verifies: ["R-07"]}
	"T-10": {title: "このPCの spec-dock の実際の構造で、PC と 390px の「全体」で図が収まり、ドラッグで横に動き、ページのはみ出しがなく、`edgeAudit` の違反0（ヘッドレスの Chrome、report.md）", verifies: ["R-07"]}
	"T-08": {title: "このPCの spec-dock の実際のスナップショットで、構造の図の既定の表示を PC の幅と 390px で写し、`window.specdockEdgeAudit()` の違反0を記録する（ヘッドレスの Chrome、report.md）", verifies: ["R-01", "R-02", "R-03"]}
}

verification: "`spec-dock scope check iss-00556`、`make lint`、`uv run pytest`（全体）、PC のヘッドレスの Chrome（一時の状態の置き場、`--disable-features=MacAppCodeSignClone`、`Browser.close`）。実際のスナップショットは読むだけにし、テストには入れない。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（v2 の保存は残るが、前の版の画面は v1 を読むので害はない）。"
exit: "PR が CI を通り、マージできる状態で、report.md に検証とゲートの結果と写しがある。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-07", model: "opus", effort: "high"}
	}
}
