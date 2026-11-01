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
	"S-01": {title: "版を 0.4.2 にする", realizes: ["R-01"], status: "todo"}
	"S-02": {title: "migration.md に節を足す", realizes: ["R-02"], status: "todo"}
	"S-03": {title: "在庫とテストを直す", realizes: ["R-03"], status: "todo", after: ["S-01", "S-02"]}
}

// テスト。番号（T-01、…）をキーにする。title と verifies（確かめる要件・失敗の条件の番号）が必須。
// standard 以上では、すべての要件に、strict 以上では、すべての失敗の条件に、確かめるテストが要る。
tests: {
	"T-01": {title: "版の値が 0.4.2 でそろう", verifies: ["R-01"]}
	"T-02": {title: "0.4.1 の配布資産が installation update で上がる", verifies: ["R-03"]}
	"T-03": {title: "migration.md の節に要点が入る", verifies: ["R-02"]}
}

// 検証のしかた、戻し方、終わりの条件（任意）。critical では、手順があれば rollback が要る。
// verification: "..."
// rollback:     "..."
// exit:         "..."

// 実行の割り当て（任意）。手順の session は、ここのセッションの名前を指す。
// レビューの after は、どの手順の後かを指す。モデルと推論の名前は、どんな文字列でもよい。
// execution: {
// 	sessions: impl: {task: "仕様化と実装", model: "...", effort: "...", rationale: "..."}
// 	reviews: code: {role: "コードのレビュー", after: "S-01", model: "...", effort: "..."}
// }
