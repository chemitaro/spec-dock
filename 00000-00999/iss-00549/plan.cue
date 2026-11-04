package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "人のタスクの記録の形、2段の検査、置き場、設定、`todo` の10のコマンド（集約なし）と、その文書を、テスト駆動で作り、レビューとゲートを通して main への PR をマージできる状態にする。"

steps: {
	"S-01": {title: "仕様を書き、仕様のレビューを通す", realizes: ["R-11"], status: "doing", session: "impl"}
	"S-02": {title: "記録の形、ID、移り変わり、検査（`domain/todo_record.py`）", realizes: ["R-03", "R-04", "F-01"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "期限、派生の状態、並び、件数、絞り込み（`domain/todo_model.py`）", realizes: ["R-06", "R-07", "R-09"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "3段の設定（`domain/todo_settings.py`、`infra/user_config.py`）", realizes: ["R-08"], status: "todo", after: ["S-01"], session: "impl"}
	"S-05": {title: "置き場と読み書き（`infra/todo_store.py`）", realizes: ["R-01", "F-02"], status: "todo", after: ["S-02"], session: "impl"}
	"S-06": {title: "CUE の型と見本、`CueTool.vet`、`todo check`", realizes: ["R-02", "F-02"], status: "todo", after: ["S-02", "S-05"], session: "impl"}
	"S-07": {title: "書くコマンド（add、update、done、snooze、cancel、reopen）と読むコマンド（list、show）、`todo settings`", realizes: ["R-01", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-03"], status: "todo", after: ["S-03", "S-04", "S-05"], session: "impl"}
	"S-08": {title: "CLI の葉、ヘルプ、ディスパッチ、テキストの出力", realizes: ["R-11", "F-03"], status: "todo", after: ["S-07"], session: "impl"}
	"S-09": {title: "カタログの検査が `todos/` を取り違えないことと、Scope の判定が変わらないことのテスト", realizes: ["R-09", "R-10"], status: "todo", after: ["S-07"], session: "impl"}
	"S-10": {title: "文書（`reference_cli.md`、`docs/README.md`、`cli-redesign-guide.html`）、inventory、dogfood の写し", realizes: ["R-11"], status: "todo", after: ["S-08"], session: "impl"}
	"S-11": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-01", "R-02", "R-11"], status: "todo", after: ["S-09", "S-10"], session: "impl"}
}

tests: {
	"T-01": {title: "main で登録したタスクが別の worktree の一覧に出て、`done` の後もファイルが同じ道に残り、changeset が残る", verifies: ["R-01"]}
	"T-02": {title: "すべての `todo` のコマンドで `gh` の stub が呼ばれない", verifies: ["R-01"]}
	"T-03": {title: "見本の valid／invalid が、Python の検査と `cue vet` でファイルごとに一致する", verifies: ["R-02"]}
	"T-04": {title: "`todo check` が形の誤りをファイル、欄、出どころつきで示して7で止まり、`cue` がなければ `TODO_CUE_SKIPPED` で Python だけで決める", verifies: ["R-02", "F-02"]}
	"T-05": {title: "エージェントの必須の欄が欠けた `todo add` が `details.missing` つきの `TODO_INVALID` で何も書かず、人は題名だけで登録できる", verifies: ["R-03", "F-01"]}
	"T-06": {title: "ID の形と重ならないこと、20回の重なりで `TODO_ID_EXHAUSTED`", verifies: ["R-03"]}
	"T-07": {title: "`todo done` が `resolution` と `history` を書き、閉じた記録の `done` は `TODO_STATE_INVALID`、`reopen` で開き直せる", verifies: ["R-03"]}
	"T-08": {title: "サブタスクの追加と1つずつの完了、孫の拒否、`parent_closable`、`TODO_SUBTASKS_OPEN` と `--include-subtasks`", verifies: ["R-04"]}
	"T-09": {title: "`--kind checklist --item` で親と項目を1回で書き、`todo show` に残りが出る", verifies: ["R-05"]}
	"T-10": {title: "既定の期限（4時間）、`--due` の書き方と過去の拒否、期限切れの印と並び、延期で隠れて期限で戻る", verifies: ["R-06"]}
	"T-11": {title: "目安を超える登録が `TODO_LIMIT_EXCEEDED` を出して成功し、人・束・サブタスクは数えない", verifies: ["R-07"]}
	"T-12": {title: "利用者の設定とリポジトリの設定の重なり、壊れた設定の警告と飛ばし、`todo settings` の出どころとチェックアウトの外での `not_applicable`", verifies: ["R-08"]}
	"T-13": {title: "`--scope`／`--blocks` の0埋めと形の拒否と `TODO_SCOPE_UNKNOWN`、`todo list --scope`／`--blocking`", verifies: ["R-09"]}
	"T-14": {title: "人のタスクがあっても `dependency check` の結果が同じで、readiness のコードが `todo` を参照しない", verifies: ["R-09"]}
	"T-15": {title: "`todos/` のあるカタログで `workspace validate` と `scope list` と `scope check` が変わらない", verifies: ["R-10"]}
	"T-16": {title: "71の葉、各葉のヘルプ、`reference_cli.md` と HTML の案内の表と数、inventory の sha256 と dogfood の写し", verifies: ["R-11"]}
	"T-17": {title: "衝突の写しが `TODO_CONFLICT_COPY` で示され、年月の違う同じ ID が `TODO_ID_DUPLICATE` と `TODO_ID_AMBIGUOUS` になる", verifies: ["F-02"]}
	"T-18": {title: "リンクがないチェックアウトで `todo` のコマンドが `CANONICAL_NOT_LINKED` で止まり、何も書かない", verifies: ["F-03"]}
	"T-19": {title: "壊れた記録と版の違う記録の書き換えが `TODO_RECORD_INVALID`／`TODO_SCHEMA_UNSUPPORTED` で断られ、ロックが取れなければ `CANONICAL_LOCK_BUSY`", verifies: ["F-01"]}
}

verification: "`make lint` と `uv run pytest`（全体）を通す。`cue` v0.17.1 のある環境で T-03 を必ず動かす。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通し、結果を report.md に書く。PR の CI（Provider CI）の通過を確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。カタログの `todos/` は前の版のコマンドに影響しない（Epic D-19）。"
exit: "S-01〜S-11 が done、PR がマージできる状態で CI が通り、report.md にゲートの合格の証拠と、0.6.0 の次の版の移行の注記に要る契約の変更がある。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "epic-00547 の plan.cue の session std（policy の standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-10", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-11", model: "opus", effort: "high"}
	}
}
