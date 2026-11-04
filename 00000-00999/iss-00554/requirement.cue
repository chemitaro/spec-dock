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
	reason: "見るだけの画面と API を足すが、書く口は作らず、版を戻せば元に戻る"
}

purpose: "ダッシュボードで、全リポジトリとリポジトリごとの人のタスクを見られるようにし、構造の図・ボード・Scope の詳しい画面・横断の概況に、人のタスクが Scope を止めていることを印と数で示す（epic-00547 の R-12、R-13。設計は Epic の D-16 と D-11）。"

background: """
	- 親は epic-00547（#547）。記録の形と CLI（#549）、集約と `dashboard summary` の `todos`（#550）はマージ済み。この Issue は画面の版の分（Epic の plan の slice `iss-00554`）。
	- 画面は epic-00427 の骨組み（`src/spec_dock/assets/dashboard/`、差し込み口 `views/<名前>.js`、共有の部品 `views/_shared/`、`core/ui.js` の印）に足す。見た目は試作 d2（`epic-00427/artifacts/20261103t150110z--dashboard-design-d2.html`）と既存の画面にそろえる。#556 で構造の図の既定と並び（活動順、折り返さない）が変わったので、箱の中の印はその並びを崩さない。
	- 部品は作り直さない：`todo_store`、`todo_aggregate`（`select_catalogs`、`catalog_for`、`read_catalog`）、`todo_list`（`classify`、`counts_of`、`show_from_store`）、`todo_model`（`derived`、`order`、`matches`、`tally`）、`todo_document`（`list_item`、`repository_row`、`todo_list_document`）。
	"""

includes: [
	"サーバーの API：`/api/v1/todos`、`/api/v1/todos/revision`、`/api/v1/r/<repo>/todos`、`/api/v1/r/<repo>/todos/<ID>`",
	"`structure` と `scopes/<ID>` の応答への、Scope ごとの人のタスクの印と、詳しい画面のための一覧",
	"`revision` への `todos/` の時刻の反映と、サーバーのリポジトリごとの読み取りの覚え",
	"画面：`/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>` と上の帯の入り口",
	"構造の図の箱と枠、ボードのカード、Scope の詳しい画面のタブ、横断の概況の札への印と数",
	"純粋な関数 `domain/todo_model.scope_marks`",
]

excludes: [
	"画面からの書き込み（登録、完了、延期）。写せるコマンドや完了のボタンも置かない（epic-00427 R-04）",
	"`todo` の CLI の振る舞いの変更",
	"版の番号と `migration.md`（リリースの Issue #553、#555 が行う）",
	"iPhone の Safari での確かめ（統括が利用者に頼む）",
]

requirements: {
	"R-01": {
		title: "全リポジトリの人のタスクの画面がある"
		text:  "`/todos` に、表示中（隠していない）の全リポジトリの開いているタスクを、Epic の D-08 の並び（期限切れ、期限の近いもの、止めているもの、あとで）で、リポジトリの名前つきで並べる。横断の概況と同じ層（1画面に1リポジトリの例外）。リポジトリ、タグ、種類で絞れ、絞り込みは URL の問い合わせに持つ。延期中と閉じたものは切り替えで出す。"
		acceptance: [
			"登録簿の2つのリポジトリのタスクが、`GET /api/v1/todos` の `items` と `/todos` の画面に、リポジトリの名前つきで並ぶ",
			"`?repo=`、`?tag=`、`?kind=` で絞ると、合うものだけが並び、URL を開き直しても同じ絞り込みになる",
			"隠したリポジトリのタスクは、API にも画面にも出ない",
		]
	}
	"R-02": {
		title: "期限切れのタスクが、先頭に目立つ印で並ぶ"
		text:  "期限切れは、色（danger）、記号、言葉（「期限切れ」と経過の時間）の3つで示し、一覧の先頭の組に置く（epic-00427 R-11 の決まり）。"
		acceptance: ["期限切れのタスクが一覧の最初の組に、danger の色と記号と「期限切れ（n時間超過）」の言葉つきで出る"]
	}
	"R-03": {
		title: "リポジトリごとの人のタスクの画面と、1件の詳しい画面がある"
		text:  "`/r/<repo>/todos` はそのリポジトリだけの一覧。`/r/<repo>/todos/<ID>` は、題名、種類、状態、期限、依頼者、本文（Markdown を安全に描く）、選択肢と推奨、答える場所、サブタスクと残りの数、止めている・関係する Scope へのリンク、経緯、閉じたときの答えと原文の記録を出す。上の帯から入れ、道は `?embed=1` を引き継ぐ。"
		acceptance: [
			"`GET /api/v1/r/<repo>/todos/<ID>` が CLI の `todo show` と同じ1件の形（`todo`、`derived`、`ref` など）を返し、ない ID は 404 になる",
			"1件の画面に、本文が `<script>` などを実行しない形で描かれ、止めている Scope の詳しい画面へのリンクがある",
			"上の帯に「人のタスク」の入り口があり、埋め込みの `?embed=1` が道に残る",
		]
	}
	"R-04": {
		title: "構造の図の箱とボードのカードに、人が止めている件数の印が出る"
		text:  "Issue の箱とカードには、`blocks` に直接その ID を持つ開いたタスクの数を「人 n」で出す。Epic と Initiative の枠とカードには、自分と配下の全 Scope を止めている開いたタスクを重ねずに数えた数を、配下を含むことが分かる形で出す。0件なら出さない。"
		acceptance: [
			"止めている人のタスクのある Issue の箱とカードに「人 n」の印が出る",
			"その Issue の親の Epic の枠に、配下を含む数の印が出る",
		]
	}
	"R-05": {
		title: "Scope の詳しい画面に、人のタスクのタブがある"
		text:  "止めているもの、関係するもの（Epic と Initiative では配下を止めているものも）を、題名と期限つきで並べ、1件の画面へリンクする。"
		acceptance: ["止めている人のタスクのある Issue の詳しい画面の「人のタスク」のタブに、そのタスクの題名と期限が出る"]
	}
	"R-06": {
		title: "横断の概況の札に、開いている数と期限切れの数が出る"
		text:  "数は `dashboard summary` の `todos` と同じ数え方。読めないときは「人のタスクが読めない」の印を出す。"
		acceptance: [
			"札に、開いている数と期限切れの数が出て、`dashboard summary` の `todos` と同じ値になる",
			"カタログが読めないリポジトリの札に「人のタスクが読めない」の印が出る",
		]
	}
	"R-07": {
		title: "CLI で書いたタスクが、5秒ごとの更新で画面に出る"
		text:  "`revision` に `todos/` と年月のディレクトリと `settings.json` の時刻を足す。横断の人のタスクの画面は、全リポジトリの分を合わせた `revision` で更新を知る。サーバーは、リポジトリごとに読み取りを覚え、時刻が変わったときだけ読み直す。"
		acceptance: [
			"タスクを足すと、そのリポジトリの `revision` と `/api/v1/todos/revision` が変わる",
			"`todos/` が変わらない間は、記録のファイルを読み直さない",
		]
	}
	"R-08": {
		title: "画面と API は見るだけで、1つのリポジトリの失敗は、その分にだけ出る"
		text:  "人のタスクの API と画面は、カタログにも GitHub にも書かず、要求も送らない。カタログか `todos/` が読めないリポジトリは、その行を `unreadable` にして、ほかのリポジトリの分を返す。形の正しくない記録と衝突の写しは、`todo check` を次の1手として示し、ほかの記録を返す。"
		acceptance: [
			"API と画面を全部開いても、カタログと状態の置き場の中身が変わらない（「見た」の記録を除く）",
			"1つのリポジトリの `todos` がファイルのとき、`/api/v1/todos` はそのリポジトリを `unreadable` とし、もう1つのリポジトリのタスクを返す",
		]
	}
}

failures: {
	"F-01": {
		title: "カタログが選べない、読めないリポジトリでは、人のタスクの印は0とし、読めないことを知らせる"
		text:  "構造の図、ボード、詳しい画面は、人のタスクが読めなくても今までどおり描く。`structure` の `todos.status` を `unavailable` にし、詳しい画面のタブと概況の札で知らせる。"
	}
	"F-02": {
		title: "見つからない ID、形の違う ID、壊れた記録の1件の要求は、決まったコードの JSON の誤りで返す"
	}
}

constraints: [
	"epic-00427 の R-04（画面は見るだけ）を保つ。書く口、写せるコマンド、完了のボタンを置かない",
	"`todo` の CLI の振る舞いと出力を変えない",
	"`evaluate_readiness` と Scope の状態を変えない。印は表示だけ",
	"Epic の compatibility のとおり、契約にするのは API の `/api/v1/todos` と `/api/v1/r/<repo>/todos[/<ID>]`（中身は `specdock.todo-list/v1` と1件の形）だけ。`structure` と `scopes/<ID>` の中の印の形は契約にしない",
	"速さ：250件の構造と100件のタスクで、今の画面の速さの目安（epic-00427 D-07）を崩さない",
]

decisions: [
	"2026-11-04：横断の画面の更新のため `/api/v1/todos/revision` を足す（Epic の D-16 の「全リポジトリの revision を合わせる」の置き場。契約にしない）",
	"2026-11-04：詳しい画面には Markdown を描く道具がないため、1件の本文は、すべてを先にエスケープしてから段落、箇条、コード、`http(s)` のリンクだけを描く小さな関数で描く（生の HTML を通さない）",
	"2026-11-04：API の `status` の問い合わせは `todo list --status` と同じ値（既定 `open`）。画面の「延期中と閉じたものも」の切り替えは `status=all` で読む",
	"2026-11-04：2つのクローンがあるリポジトリは、`todo list --all-repositories` と同じく、`main_checkout` の道の順で最初のカタログを読む",
]

questions: []
