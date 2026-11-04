package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

// 目標（任意）。
// goal: "..."

// 実装の手順。番号（S-01、…）をキーにし、番号の順に並べる。
// title と realizes（満たす要件・失敗の条件の番号）が必須。
// status は todo（既定）、doing、done、dropped。after は先に済ませる手順の番号。
// 1手順を1行に書き、status は title と realizes のすぐ後に置く。status の位置がそろうので一括で書き換えやすく、
// 同じ手順に status を2つ書く誤りも防げる（同じ値の2つは CUE が黙ってまとめ、違う値なら誤りになる）。
// すべての要件に、それを満たす手順が要る（dropped の手順は数えない）。
// strict 以上では、dropped でない手順のすべてが、いずれかの番号に結び付く。
steps: {
	"S-01": {title: "版を 0.7.0 にする", realizes: ["R-01"], status: "doing", session: "impl"}
	"S-02": {title: "migration.md に 0.7.0 の節を足す", realizes: ["R-02"], status: "doing", after: ["S-01"], session: "impl"}
	"S-03": {title: "static-inventory.json と fixture とテストを足す", realizes: ["R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "R-04 はマージの後に統括が行う", realizes: ["R-04"], status: "todo", after: ["S-03"]}
}

tests: {
	"T-01": {title: "版が 0.7.0 の全部の場所でそろう", verifies: ["R-01"]}
	"T-02": {title: "migration.md に 0.7.0 の節があり、dogfood の写しと一致する", verifies: ["R-02"]}
	"T-03": {title: "inventory が 0.6.0 のバイトを知り、0.6.0 の consumer が installation update で上がる", verifies: ["R-03"]}
}

execution: {
	sessions: impl: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "light。版の番号と文書だけの変更で、0.6.0 を入れ直せば戻る。"}
}
