package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "light"
	reason: "配布するスキルと文書の文を足すだけで、コードは変えず、PR を戻せば元に戻る"
}

purpose:    "エージェントが人のタスクを、決まった場面で、決まった形で登録し、閉じられるようにする。配布するスキルと文書に規則と使い方を書く（Epic epic-00547 の R-05、R-14。設計 D-17）。"
background: "`spec-dock todo` の10のコマンドと集約は iss-00549（PR #558）と iss-00550（PR #559）でマージ済み。コマンドを使う側の規則（いつ登録し、いつ登録せず、誰がどう閉じるか）がまだ配布物にない。"

includes: [
	"`install_root/.agents/skills/spec-dock/SKILL.md` に「人のタスク」の節を足す",
	"配布する文書 `docs/todo.md` を足し、`docs/canonical.md`、`docs/README.md` を直す",
	"dogfood の写しと `static-inventory.json` の該当行、確かめるテスト",
]
excludes: [
	"コードの振る舞いの変更（`todo` のコマンド、契約）",
	"版の番号と `migration.md`（リリースの Issue #553）",
	"`reference_cli.md` の本文（iss-00549、iss-00550 で済み）",
]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "配布するスキルに、登録する場面と登録しない場面が書いてある"
		text:  "会話の中で答えが返るもの（Claude Code や Codex の複数の質問を含む）は登録しない。答えを待ったままターンを終えるとき、人しかできない操作をすぐにしてもらえないとき、数日かかる確かめ、期限のある行為は、`todo add --by agent --role <役割> --kind <種類>`（背景と問い、`--reply-to`、`--effort`、`decide` は選択肢と推奨）で登録してから、止まらない作業を続ける。止める Scope があれば `--blocks` を付ける。PR のマージ待ちは登録しない。作業者から統括への問いは Orca で行い、統括が答えられず人に上げるときだけ統括が `decide` で登録する。秘密の値を書かない。Claude Code の隔離セッション（`--worktree`）では読むだけにし、登録は統括に頼む。（Epic の R-14、D-17 の 1・2・4・7）"
		acceptance: ["`.agents/skills/spec-dock/SKILL.md`（提供側と dogfood の写し）にこの規則がある"]
	}
	"R-02": {
		title: "配布するスキルに、束とサブタスクの規則が書いてある"
		text:  "1回の会話で全部の答えが返らない2つ以上の項目は、あらかじめ `--kind checklist` と `--item` で束にして登録する。答えを受けるたびにサブタスクを閉じ、返事の終わりに `todo show <親>` の残りを示す。1回の会話で終わる複数の問いは登録しない。（Epic の R-05、D-17 の 3）"
		acceptance: ["スキルに、束にする場面と、束にしない場面と、返事の終わりに `todo show <親>` を示すことがある"]
	}
	"R-03": {
		title: "配布するスキルに、閉じ方と統括の読み方が書いてある"
		text:  "答えを受けた担当が `todo done --record <原文の記録>` で閉じ、原文の記録へのリンクを残す。統括は、始めるときに `todo list` を読み、答えが出たのに閉じていないものを閉じる。（Epic の R-14、D-17 の 5・6）"
		acceptance: ["スキルに `todo done --record` と、統括が始めるときに `todo list` を読むことがある"]
	}
	"R-04": {
		title: "人のタスクの使い方の文書を配る"
		text:  "`docs/todo.md` を足す。使い方、記録の形、設定の3段と見本、集約、外部の道具の読み方を書き、コマンドの仕様は `reference_cli.md` に任せる。`docs/README.md` から辿れ、`canonical.md` に、`todos/` がカタログにあることと、人のタスクのエラーと次の1手を足す。"
		acceptance: ["`docs/todo.md` が配布の一覧にあり、`docs/README.md` と `canonical.md` から辿れる", "`canonical.md` の説明が `reference_cli.md` のコードと合う"]
	}
	"R-05": {
		title: "配布物と dogfood の写しと一覧が合っている"
		text:  "提供側の資産、`spec-dock/` の写し、`static-inventory.json` の sha256 と `known_old_sha256` が合い、新しいスキルと文書が `installation init` で入る。"
		acceptance: ["提供側と写しの中身が一致する", "`static-inventory.json` の sha256 が実際の中身と合う", "新しいリポジトリの `installation init` で `todo.md` と更新したスキルが入る"]
	}
}

// 失敗・境界の条件。番号（F-01、…）をキーにする。
// title は必須。impact（起きたときの影響）と recovery（回復のしかた）は strict 以上で必須。
failures: {
	"F-01": {
		title: "規則の文が、コマンドの契約と食い違わない（食い違う語を書かない）"
	}
}

// 制約・前提、合意した判断、未解決事項（任意）。
// constraints: ["..."]
// decisions: ["..."]
// questions: ["..."]
