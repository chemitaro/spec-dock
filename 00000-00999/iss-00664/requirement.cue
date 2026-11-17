package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "0.9.8 のリリースを止めている不具合か不安定なテストかを見分ける"
}

purpose:    "0.9.8 のリリース（iss-00663）の最終品質ゲートで手元だけ落ちた、横断の構造の動きのテストの原因を見分け、時間に左右されずに毎回同じ結果を出す形に直す。"
background: "`tests/unit/presentation/test_dashboard_allgraph_command_screen.py::test_the_motion_stills_and_watches_on_the_cross_repository_structure`（iss-00646）が、macOS の手元で `shots[1].still` が True になって落ちる（main `fa9824cb9` で単独5回中4回）。provider CI（Linux）は通る。"

includes: ["原因の見分け（利用者に見える不具合か、テストの時間の決め方か）と、落ち始めたマージの特定", "テストまたは画面のコードの最小の修正", "1440×900 の Chrome での指揮の線の動きの確かめ"]
excludes: ["横断の構造の動きの仕組み（iss-00646・iss-00655・iss-00657）の変更", "構造のグラフ（graph.js）の側のハーネス"]

requirements: {
	"R-01": {
		title: "落ちる原因と、落ち始めたマージを記録する"
		text:  "92e26aff7（#649）、#658、#659、#660、#661、#662 の各マージで、このテストを単独に10回ずつ走らせた落ちる回数と、落ちる仕組みを report.md に残す。"
		acceptance: ["report.md に各マージの落ちた回数の表と、落ちる仕組み（どの呼び出しが、どの時計で、なぜ実時間に左右されるか）がある"]
	}
	"R-02": {
		title: "横断の構造の動きのテストが、時間に左右されずに毎回通る"
		text:  "テストの結果が、実時間の速さ（機械の負荷、先に走る run の長さ）で変わらない。不具合なら画面のコードを、テストの不安定さならテストを、最小に直す。"
		acceptance: ["修正の後、このテストを単独に20回走らせて0回落ちる", "`whenStyled` の打ち切りの時間を 0ms と 1e9ms に変えても、このテストのファイルが通る", "`make lint` と `uv run pytest`（全体）が通る"]
	}
	"R-03": {
		title: "利用者の画面で、指揮の線が動き始める"
		text:  "1440×900 の Chrome で、横断の構造の指揮の線が、読み込み後・ドラッグの後・ホイールの後・キーの後に、止めたままにならず流れ始める。"
		acceptance: ["実機で、各操作の後に `.gx-view` の is-still が外れ、流れる絵の opacity が切り替わり続けることを確かめ、report.md に記録する"]
	}
}

failures: {
	"F-01": {
		title: "原因が利用者に見える不具合だったときは、テストを緩めずに画面のコードを直す"
	}
}

constraints: ["書いてよいのは `src/spec_dock/assets/dashboard/`、`tests/`、`src/spec_dock/assets/static-inventory.json`、この Scope のディレクトリ"]
