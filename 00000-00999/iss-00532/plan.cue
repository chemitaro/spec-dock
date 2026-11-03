package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "構造の図と時間の軸を、試作 d2 の見た目と振る舞いで作り、線の検査を0件にして、マージできる PR にする。"

steps: {
	"S-01": {title: "構造の API に blocked_by、stage、rank、assurance、branch、weeks_by_kind を足す（テスト先行）", realizes: ["R-01", "R-05", "R-11"], status: "done", session: "impl"}
	"S-02": {title: "ROUTER を views/graph/router.js に移し、lane の障害物と trunkOverlaps を足す", realizes: ["R-02", "F-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "配置の計算 views/graph/layout.js と、隙間を広げる引き直し", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-13", "F-02"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "node の検査の仕組み（tests/js と pytest）と見本の構造で、検査を0件にする", realizes: ["R-02", "R-05"], status: "done", after: ["S-03"], session: "impl"}
	"S-05": {title: "図の画面 views/graph.js、graph.css、graph/marks.js（描画、印、選択、要点、絞り込み、凡例）", realizes: ["R-01", "R-03", "R-04", "R-06", "R-07", "R-09", "R-10", "R-12", "F-01"], status: "done", after: ["S-03"], session: "impl"}
	"S-06": {title: "拡大・縮小・移動と2本指のつまみ、gesturestart の抑止、帯の下の余白", realizes: ["R-08"], status: "done", after: ["S-05"], session: "impl"}
	"S-07": {title: "時間の軸 views/timeline.js、timeline.css、timeline/series.js", realizes: ["R-11", "R-12", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-08": {title: "PC のヘッドレスの Chrome での確かめ（PC と 390px、明暗、JS のエラー、edgeAudit、速さ、指の操作）と Artifact", realizes: ["R-07", "R-08", "R-12", "R-13"], status: "doing", after: ["S-06", "S-07"], session: "impl"}
	"S-09": {title: "コードのレビュー、最終品質ゲート、report.md、PR", realizes: ["R-02"], status: "todo", after: ["S-04", "S-08"], session: "impl"}
}

tests: {
	"T-01": {title: "構造の API の新しい項目（blocked_by、stage の all/open と循環、rank、assurance・branch が null、weeks_by_kind、scopes/<ID> の downstream_all）", verifies: ["R-01", "R-05", "R-07", "R-11"]}
	"T-02": {title: "node：代表のデータのすべての組み合わせで audit の数と trunkOverlaps が0、経路の失敗が0", verifies: ["R-02", "F-02"]}
	"T-03": {title: "node：配置で、待ち先が左の列、同じ列は rank の順、段が7つで折り返し、終わったものを隠し閉じた親を残す、片付けの候補を畳み keep_visible の親は畳まない、木では畳まない、focus で配下だけ", verifies: ["R-04", "R-05", "R-06", "R-01"]}
	"T-04": {title: "node：依存の線の3つの切り替えで、組の数が変わり、終わった依存に done が付く", verifies: ["R-03"]}
	"T-05": {title: "node：mergeWeeks が選んだ種類の累計を正しく足し、groupEvents が新しい順に日ごとに分ける", verifies: ["R-11"]}
	"T-06": {title: "node：250件の見本で、配置と経路の計算（引き直しを含む）が1秒以内", verifies: ["R-13"]}
	"T-07": {title: "ブラウザー（手元の確かめ）：選んだときの強調、要点、ダブルクリックと2回目のタップ、状態の印、凡例、変化の印、2本指のつまみ、帯の下の余白、PC と 390px と明暗、JS のエラー0、DOM の edgeAudit 0、速さ", verifies: ["R-01", "R-06", "R-07", "R-08", "R-09", "R-10", "R-12", "R-13", "F-01"]}
}

verification: "`spec-dock scope check iss-00532`、`make lint`、`uv run pytest`（全体。node の検査を含む）、PC のヘッドレスの Chrome での確かめ（結果は artifacts と report.md）。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。iPhone の Safari は #534 で利用者に頼む。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（画面のファイルと API の項目の追加だけなので、ほかに影響しない）。"
exit: "PR がマージできる状態（CI が通り、衝突がない）で、report.md にゲートの証拠と確かめの結果がある。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "epic-00427 plan.cue の session std（policy §4 standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-08", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-09", model: "opus", effort: "high"}
	}
}
