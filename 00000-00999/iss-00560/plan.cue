package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の入れ子の配置を、つながりの行をそろえ、つながっていないまとまりを幅で折り返す形に、テスト駆動で直し、実データで確かめ、マージできる PR にする。"

steps: {
	"S-01": {title: "node のテストに使える幅の選択と見本（つながり、分かれ、2つのつながり、独立した12件）を足し、失敗を確かめる", realizes: ["R-01", "R-02", "R-04"], status: "todo", session: "impl"}
	"S-02": {title: "`layout.js` にまとまりの分け方、格子、棚を入れ、最上位も同じ配置にする", realizes: ["R-01", "R-02", "F-01", "F-02"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "`graph.js` で見える幅を渡し、幅が変わったときだけ並べ直す", realizes: ["R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "線の検査の代表のデータ（幅を変えたものを含む）で違反0を確かめ、既存のテストの期待を新しい配置に合わせる", realizes: ["R-04"], status: "todo", after: ["S-02"], session: "impl"}
	"S-05": {title: "このPCの spec-dock の実際のスナップショットで、PC の幅と 390px の写し、幅を変えたときの並べ直し、`edgeAudit` を確かめ、report.md と artifacts に残す", realizes: ["R-01", "R-03", "R-04"], status: "todo", after: ["S-03", "S-04"], session: "impl"}
}

tests: {
	"T-01": {title: "見本の4つの Epic のつながりが同じ上端で左から右へ並ぶ。分かれで一方が前のものと同じ行。2つのつながりがそれぞれの行に並び交差しない（node）", verifies: ["R-01"]}
	"T-02": {title: "依存のない12件の Issue が幅 1400px で折り返し、各行が使える幅を超えない。使える幅より広いつながりは折り返されない。まとまりが活動順に並ぶ。幅が渡されないときは 1240px で折り返す（node）", verifies: ["R-02", "F-01"]}
	"T-03": {title: "段とずれた依存と依存の輪があっても配置が例外を出さず、すべての子を出す（node）", verifies: ["F-02"]}
	"T-04": {title: "線の検査の代表のデータのすべての表し方と、使える幅 1400px・374px の表し方で問題0件、種 532 が1秒以内（node）", verifies: ["R-04"]}
	"T-05": {title: "`graph.js` が見える幅を `width` で渡し、並べ直しの合図に幅を含め、`resize` で幅が変わったときだけ描き直す（静的）。ヘッドレスの Chrome で、窓の幅を変えると行数が変わり、拡大・縮小と「全体」では変わらない", verifies: ["R-03"]}
	"T-06": {title: "このPCの spec-dock の実際の構造で、init-00423 の 425 → 427 → 471 → 526 が1行に並び、PC の幅と 390px の `edgeAudit` の違反が0件（ヘッドレスの Chrome、report.md）", verifies: ["R-01", "R-04"]}
}

verification: "`spec-dock scope check iss-00560`、`make lint`、`uv run pytest`（全体）、PC のヘッドレスの Chrome（一時の状態の置き場、`--disable-features=MacAppCodeSignClone`、`Browser.close`）。実際のスナップショットは読むだけにし、テストには入れない。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（保存した見せ方と API は変えないので、戻しても害はない）。"
exit: "PR が CI を通り、マージできる状態で、report.md に検証とゲートの結果と写しがある。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-04", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート（最終のコミットで）", after: "S-05", model: "opus", effort: "high"}
	}
}
