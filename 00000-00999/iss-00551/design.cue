package spec

// 設計（Issue）。型 specdock/v1。

// 設計目標、今の状態と、この Issue の後の状態（任意）。
// goals: ["..."]
// current: "..."
// target:  "..."

// 設計の単位（責務、interface、data など）。番号（D-01、…）をキーにする。
// title と satisfies（満たす要件・失敗の条件の番号）が必須。
// standard 以上では、すべての要件に、それを満たす設計が要る。
design: {
	"D-01": {
		title: "スキルの「人のタスク」の節"
		text: """
			`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md` に「人のタスク」の節を足す（「Documents and Artifacts」の前）。使い方の詳細は `docs/todo.md` に任せ、節は規則だけを短く並べる。
			- 登録しない：会話の中で答えが返るもの（複数の質問も）、PR のマージ待ち（ダッシュボードの表示を使う）。
			- 登録する場面と形：`todo add --by agent --role <役割> --kind <種類>`。`decide` は選択肢と推奨、`--reply-to`、`--effort`。止める Scope には `--blocks`。登録してから止まらない作業を続ける。
			- 束：2つ以上で全部の答えが返らないものは `--kind checklist --item`。答えのたびにサブタスクを閉じ、返事の終わりに `todo show <親>`。
			- 閉じる：答えを受けた担当が `todo done --record <原文の記録>`。統括は始めるときに `todo list` を読み、答えが出たものを閉じる。
			- 作業者から統括への問いは Orca。統括が人に上げるときだけ `decide`。
			- 秘密の値を書かない。`--worktree` の隔離セッションでは読むだけにし、登録は統括に頼む。
			- 層：配布の資産だけ。既存の節を変えない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01"]
	}
	"D-02": {
		title: "配布する文書"
		text: """
			- `src/spec_dock/assets/spec_dock/docs/todo.md` を足す：人のタスクの使い方（登録・一覧・閉じ方）、記録の形、設定の3段と見本、集約（`--all-repositories`）、外部の道具の読み方（`todos/` の JSON を読む側が守ること）。コマンドの引数と契約は `reference_cli.md` に任せてリンクする。
			- `docs/README.md` と `docs/guide.md` の Current に `todo.md` を足す（Current の一覧を縛るテストの一覧にも足す）。
			- `docs/canonical.md` に、カタログに `todos/<YYYY-MM>/` があること（Scope ではない）、`todos/settings.json`、エラーと次の1手の表に人のタスクのコード（`TODO_*`）を足す。コードの名前と意味は `reference_cli.md` の契約の節と合わせる。
			"""
		satisfies: ["R-04", "F-01"]
	}
	"D-03": {
		title: "写しと一覧とテスト"
		text: """
			- `spec-dock/docs/` と `.agents/skills/spec-dock/SKILL.md` の写しを同じ内容にする。
			- `src/spec_dock/assets/static-inventory.json`：`todo.md` を新しい項目として足し（`known_old_sha256` は空）、`SKILL.md`、`canonical.md`、`README.md` は sha256 を更新して前の値を `known_old_sha256` に足す。ほかの行は変えない。
			- テスト（`tests/unit/infra/`）：スキルの「人のタスク」の節の中に規則の語（`--kind checklist`、`todo done --record`、`todo list`、`--blocks`、`--worktree`）があること（節の外の既存の文では満たさない）、`todo.md` が配布され `README.md`／`canonical.md` から辿れること、`canonical.md` の `TODO_*` が `reference_cli.md` にあること、提供側と写しが一致すること、新しいリポジトリの `installation init` で入ること。
			"""
		satisfies: ["R-05"]
	}
}

// 移行・互換性、リスク（任意）。
// compatibility: "..."
// risks: ["..."]
