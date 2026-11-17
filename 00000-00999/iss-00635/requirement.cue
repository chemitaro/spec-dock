package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの表示と一覧の API の項目を減らすだけで、データや操作には触れない"
}

purpose: """
	『横断の構造』（`/graph`）のリポジトリの枠の見出しから、段の札（`businesses` → 事業、`products` → プロダクト、`services` → サービス、ほかの途中のディレクトリの名前はそのまま）をなくす。
	SpecDock は、ディレクトリの名前に特別な意味を持たせず、どんな置き方のリポジトリでも同じに働く、普遍的でシンプルな決まり（チェックアウトのパスの包含による入れ子）だけで、リポジトリの入れ子を見せる。
	"""

background: """
	- 本人の指摘（2026-11-17）：横断の構造で、事業（businesses）に『事業』、プロダクト（products）に『プロダクト』の札が付いている。これは要らない。company-os・事業・プロダクトの構成は本人がたまたまそうしているだけで、SpecDock はほかの構成でも使う。本人の環境に特化した独自の決まりではなく、普遍的でシンプルな仕組みにしてほしい。
	- 段の札は iss-00613（一覧の API の `tier`、読み替えの表 `TIER_LABELS`）と iss-00614（画面の `sd-badge`）で入った。入れ子の親 `parent` は、チェックアウトのパスのいちばん近い祖先で決まり、ディレクトリの名前に依らない。
	- 0.9.5 で `tier` を配った。外の利用者（orca-web）は `tier` を読んでいない（2026-11-17 タスク担当の確かめ：orca-web の main のチェックアウト `27b01fe` で、`spec-dock/` と `node_modules` を除き、語 `tier` の検索が0件）。
	"""

includes: [
	"一覧の API（`GET /api/v1/repositories`）の各リポジトリの `tier` の項目と、それを決める仕組み（`TIER_LABELS`、札のための境界の入力）",
	"『横断の構造』の枠の見出しの札（`views/allgraph.js` の `headHtml`、`allgraph.css` の `.ax-tier`）",
	"配る側の契約の文書 `docs/reference_cli.md` の `tier` の記述、その目録（`static-inventory.json`）、dogfood の写し",
	"名前やディレクトリの名前に特別な意味を持たせる決まりがほかにないかの確かめと、あれば同じく外すこと（見つけたものと扱いを report.md に書く）",
	"Epic epic-00612 の仕様（requirement・design・plan）の `tier` の文を、外したことに合わせて直す",
]

excludes: [
	"入れ子の親 `parent` の決め方と、画面の枠の入れ子（そのまま残す）",
	"`docs/migration.md` の 0.9.5 の節（過去の記録として残す）と、外したことを書く新しい節（0.9.6 の版上げの Issue iss-00634 が書く）",
	"版の番号、版のファイル、リリースの手順",
	"各リポジトリの中の構造の図（`views/graph/`）の、Scope の活動の段（`layout.js` の `tier`。リポジトリの段の札とは別のもの）",
]

requirements: {
	"R-01": {
		title: "一覧の API は段の札を返さず、入れ子の親だけを返す"
		text: """
			`GET /api/v1/repositories` の各リポジトリは、`repository` から `problem` までの今の7つの項目と、その後ろの `parent` だけを持つ。`tier` の項目はない。
			`parent` の値（同じ応答の `repositories` にある、チェックアウトのパスのいちばん近い出す祖先の鍵か `null`）と、隠したもの・クローンが2つのもの・絶対の道でない行の扱いは、今と同じ。
			サーバーの側には、ディレクトリの名前を読み替える表も、ディレクトリの名前で分かれる処理もない。
			"""
		acceptance: [
			"一覧の API の応答の各リポジトリの項目が、順に `repository`・`host`・`owner`・`name`・`path`・`api`・`problem`・`parent` で、`tier` がない",
			"この PC の登録の形の合成（9つ）で、各 `parent` が今と同じ（company-os の入れ子と、外の spec-dock・orca-web が最上位）",
			"`businesses`・`products`・`services` を途中に持つ道と、別の名前（例 `groups/team`）を途中に持つ道で、`parent` の決まり方が同じ（名前に依らない）",
			"`src/spec_dock/runtime/` に `TIER_LABELS`、`事業`、`プロダクト`、`サービス`、`businesses`、`products` の文字列がない",
		]
	}
	"R-02": {
		title: "横断の構造の枠の見出しは、リポジトリの名前だけになる"
		text: """
			リポジトリの枠の見出しは、folder のアイコン、`owner/name`、構造の図への移動のリンクだけを持つ。段の札（`sd-badge` の並び）とその入れ物（`.ax-tier`）はなく、CSS にもその規則がない。
			札がなくなった分は、名前が使える（見出しの最小の幅 `REPO.headW` は名前とリンクの分として今のまま）。枠の入れ子（親の枠の中に子の枠）は今と同じ。
			API が古いサーバー（`tier` を返す 0.9.5）でも、画面は `tier` を読まない。
			"""
		acceptance: [
			"偽の DOM のテストで、`tier` を持つ入力を与えても、どの枠の見出しにも `sd-badge`・`ax-tier` がなく、名前 `owner/name` とリンクがある",
			"`allgraph.css` と `allgraph.js` に `ax-tier` と `tier` の文字列がない",
			"compose の入れ子のテスト（この PC の登録の形の9つ）が今どおり通る",
			"実機の写し（1440・390、明・暗）で、枠の見出しに札がなく、入れ子が今どおり（report.md）",
		]
	}
	"R-03": {
		title: "契約の文書から段の札の記述を消す"
		text: """
			配る側の `docs/reference_cli.md` の「orca-web との連携」の API の行から、`tier` と段の札の決め方の記述を消し、`parent` の記述だけを残す。契約の版 `specdock.dashboard/v1` は変えず、版の規則（「消すか意味を変えるときは版を上げます」）の例外として、API の行に「0.9.5 だけで配った `tier` は、使う者がなく、0.9.6 で消した（版の規則の例外）」の1文を書く。目録 `static-inventory.json` の sha256 を新しい内容にし、今の値（0.9.5 の後に iss-00614 で入った、まだ配っていない内容。0.9.5 で配った値は既に `known_old_sha256` にある）を `known_old_sha256` に足す。dogfood の写し `spec-dock/docs/reference_cli.md` を同じバイトにする。
			"""
		acceptance: [
			"配る側と dogfood の `reference_cli.md` が同じバイトで、API の行が `段の札`・`businesses` を含まず、`parent` の決め方（いちばん近い出す祖先、隠したもの、クローンが2つのもの、道を返さない）と、`tier` を 0.9.6 で消した版の規則の例外の1文を含む",
			"目録の sha256 が内容と合い、前の sha256 が `known_old_sha256` にある（今の目録のテストを含む）",
		]
	}
	"R-04": {
		title: "名前に特別な意味を持たせる決まりがほかにないことを確かめる"
		text: """
			`src/spec_dock/`（vendor を除く）で、company-os・businesses・products・services・本人のリポジトリの名前など、特定の置き方や名前を前提にした分岐や読み替えを探し、あれば外す。決まりではない記述（コメントや文書の例）は、決まりと誤読されるものを一般の言い方に直し、ほかは report.md に扱いを書く。
			"""
		acceptance: [
			"report.md に、探した語と範囲、見つけたもの、それぞれの扱い（外した・直した・残した理由）がある",
		]
	}
}

failures: {
	"F-01": {
		title: "古い API の応答（`tier` を持つ）を画面が受けても、札を出さず、壊れない"
		text:  "0.9.5 のサーバーと新しい画面の組は起きない（同じパッケージで配る）が、偽の DOM のテストで `tier` を持つ入力を与え、札が出ないことを確かめる。"
	}
}

constraints: [
	"入れ子の親の決まり（パスの部分で比べる包含、いちばん近い出す祖先、隠したもの・クローンが2つのもの・絶対の道でない行の扱い）は変えない",
	"`docs/migration.md` は変えない（0.9.5 の節は過去の記録。新しい節は iss-00634）",
	"一覧の API の契約の版 `specdock.dashboard/v1` は変えない（decisions の統括の判断 2026-11-17）",
]

decisions: [
	"2026-11-17 統括（依頼書の決定1〜4）：段の札をなくす。入れ子 `parent` は残す。見出しはリポジトリの名前だけにし、札の分の余白も詰める。名前やディレクトリの名前に特別な意味を持たせる決まりがほかにあれば同じく外し、report.md に書く。",
	"2026-11-17 統括（仕様レビューの P1 への答え）：配る側の契約は「消すか意味を変えるときは版を上げます」と定めるが、`tier` は 0.9.5 だけで配り、使う者は SpecDock の画面だけで orca-web も読まない（schema の文字列も検査しない）。版を v2 に上げる波及や、使わない項目を残すことより、規則の例外を reference_cli.md に1文で明記して消すほうが単純で正しい。版は `specdock.dashboard/v1` のまま。",
	"タスク担当（2026-11-17）：`REPO.headW`（280）は、札の分ではなく、名前とリンクの見出しの最小の幅（iss-00614 D-01）なので変えない。札の `.ax-tier` は `flex: none` で名前を省略させていたので、札を消すと、その分を名前が使う（『札の分の余白を詰める』は、札の入れ物と間（gap）を消すことで満たす）。headW を変えると、読み込み中・Scope のない枠の幅が変わり、iss-00629 の並びの測りが変わるので、この Issue の範囲の外とする。",
	"タスク担当（2026-11-17）：`canonical.md` の設定の例のパス（`/path/to/taikyohiyou_project/...` など本人のリポジトリの名前）は、決まりではなく例なので、この Issue では変えず、report.md に後続の候補として書く（変えると配る資産と目録が増え、版上げの Issue と重なる）。",
]
