package spec

// 計画（Epic）。型 specdock/v1。
// 切り分けのキーは、子の Issue を作るまでの仮の番号（iss-999xx）。作った後に本当の ID に直す。

goal: "人のタスクの記録の形と `todo` の CLI、全リポジトリの集約と `dashboard summary` の数、配布するスキルの規則を、epic-00427 を待たずに先に出して spec-dock で使い始め、epic-00427 の完了の後に、ダッシュボードの画面と印を足して出す。"

slices: {
	"iss-99901": {
		covers: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-02", "F-03"]
		text:   "第1波。記録の形と型と設定、CLI の中核。D-01〜D-12 と D-18：置き場と `todo_store`、`specdock.todo/v1` の Python の型と書く前の検査、CUE の型 `#Todo` と `cue vet`、`todo check`、ID の採番、ロックと原子的な書き込みと衝突の写しの警告、サブタスクと束、期限と延期と並び、件数の警告、3段の設定と `todo settings`、Scope との結び付き（`evaluate_readiness` を変えないことの確かめを含む）、チェックアウトの中の `todo add|list|show|update|done|snooze|cancel|reopen|check|settings`（集約なし）と、1件の結果の形（D-13 の1件の部分）。`todos/` を Scope と取り違えないことのテスト（D-18）。`reference_cli.md` に10のコマンドと `specdock.todo/v1` を書く。epic-00427 に依存しない。"
		session: "std"
	}
	"iss-99902": {
		covers: ["R-10", "R-11", "F-03"]
		text:   "第2波。集約と要約。D-13 の `specdock.todo-list/v1`、D-14 の `todo list --all-repositories`／`--repository` と `todo show <REF>`（登録簿を読み、リポジトリごとの失敗を閉じ込める）、D-15 の `dashboard summary` の `todos`（サーバーの summary の API も同じ数を返すこと）。`reference_cli.md` に契約を書く。epic-00427 の既存の `dashboard summary` を拡張するが、epic-00427 の残りの Issue には依存しない。"
		after: ["iss-99901"]
		session: "std"
	}
	"iss-99903": {
		covers: ["R-05", "R-14"]
		text:   "第3波。D-17 の配布するスキルの規則（`install_root/.agents/skills/spec-dock/SKILL.md` と `static-inventory.json`）と、配布する文書（`docs/todo.md` を足し、`canonical.md` を直す）。新しい候補の wheel と、隔離した利用者のリポジトリで、スキルと文書が入ることと、規則のとおりの登録・完了が動くことを確かめる。"
		after: ["iss-99901", "iss-99902"]
		session: "light"
	}
	"iss-99904": {
		covers: ["R-01", "R-10", "R-14"]
		text:   "第4波。CLI の版（次の minor の版。番号は統括が決める）を出し、5つのリポジトリに配る。D-19 の `migration.md`。マージの後の導入と配布は統括が行い、spec-dock の main のチェックアウトで `installation update` をしてから dogfooding を始める：別の worktree で登録したタスクが見えること（R-01）、2つのリポジトリの集約（R-10）、統括と作業者がスキルの規則で登録・完了すること（R-14）を、利用者の PC で確かめて報告に残す。"
		after: ["iss-99901", "iss-99902", "iss-99903"]
		session: "light"
	}
	"iss-99905": {
		covers: ["R-12", "R-13"]
		text:   "第5波。D-16 のダッシュボードの API と画面（全リポジトリとリポジトリごとの人のタスクの画面、1件の詳しい画面、構造の図の箱とボードのカードの印、Epic と Initiative の配下を含む数、Scope の詳しい画面のタブ、横断の概況の札の数、revision）と、D-11 の親への集計（`scope_marks`）。見るだけ（epic-00427 R-04）。GitHub の依存で epic-00427 の完了を待つ（利用者の決定、2026-11-04）。PC のブラウザーでの確かめを報告に残し、iPhone の Safari の確かめは利用者に頼む。"
		after: ["iss-99902"]
		session: "std"
	}
	"iss-99906": {
		covers: ["R-12", "R-13"]
		text:   "第6波。画面の版を出し、5つのリポジトリに配る。`migration.md` に画面が足されることを書く。利用者の PC と iPhone から、人のタスクの画面と、構造の図・ボード・詳しい画面・横断の概況の印を確かめる。"
		after: ["iss-99904", "iss-99905"]
		session: "light"
	}
}

verification: "各 Issue の PR で `make lint` と `uv run pytest`（全体）と CI を通す。standard の Issue は、仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通す。light の Issue は、仕様のレビュー opus/medium、コードのレビュー sonnet/high、最終品質ゲート opus/high（1人）。2つの型（Python と CUE）が同じ見本で一致するテストは、`cue` のある環境で必ず動かす（D-05）。`gh` の stub で、`todo` のコマンドが GitHub に要求を送らないことを確かめる（R-01）。CLI の版の配布の後、spec-dock で dogfooding し、5つのリポジトリで `todo list --all-repositories` と `dashboard summary` を確かめる。画面の Issue は PC のブラウザーでの確かめを報告に残し、iPhone の Safari の確かめは利用者に頼む。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。配った後なら、パッケージを前の版に戻し、各リポジトリの配布の PR を `git revert` する。カタログの `todos/` のファイルは残してよい（前の版のほかのコマンドに影響せず、版を上げ直せばそのまま読める。D-19）。"
exit: "6つの子の Issue が閉じ、5つのリポジトリが画面の版で、spec-dock で人のタスクを使っており、利用者の PC と iPhone から人のタスクの画面と印が見えることを確かめ、この Epic の report.md に結果と、Company OS の受付簿を移すかの判断の材料をまとめた。"

execution: {
	sessions: {
		coord: {task: "統括（計画、配布、利用者への報告）", model: "opus", effort: "high", rationale: "policy の統括役"}
		std: {task: "standard の Issue の実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy の standard の実装"}
		light: {task: "light の Issue の実装（Orca の worker）", model: "sonnet", effort: "medium", rationale: "policy の light の実装"}
	}
	reviews: {
		"std-spec": {role: "standard の Issue の仕様のレビュー", after: "iss-99901", model: "opus", effort: "high"}
		"std-code": {role: "standard の Issue のコードのレビュー", after: "iss-99901", model: "opus", effort: "high"}
		"std-gate": {role: "standard の Issue の最終品質ゲート", after: "iss-99901", model: "opus", effort: "high"}
		"light-spec": {role: "light の Issue の仕様のレビュー", after: "iss-99903", model: "opus", effort: "medium"}
		"light-code": {role: "light の Issue のコードのレビュー", after: "iss-99903", model: "sonnet", effort: "high"}
		"light-gate": {role: "light の Issue の最終品質ゲート", after: "iss-99903", model: "opus", effort: "high"}
	}
}
