package spec

// 要件（Issue）。型 specdock/v1。親は epic-00612（plan.cue の slice iss-00613：R-01、R-02、R-03、F-02、F-03）。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの一覧の API に項目を足すだけで、既存の項目と順は変えず、PR を戻せば元に戻る"
}

purpose: """
	ダッシュボードの `GET /api/v1/repositories` が、各リポジトリの入れ子の親（`parent`）と段の札（`tier`）を返し、画面（iss-00614 の『横断の構造』）や Orca などの利用者が、会社の入れ子（company-os → 事業 → プロダクト …）を、チェックアウトのパスを受け取らずに読めるようにする。
	"""

background: """
	Epic epic-00612 の要件 R-01、R-02、R-03、F-02、F-03 を、この Issue が受け持つ（Epic の plan.cue の slice `iss-00613`）。画面は変えない（iss-00614 が受け持つ）。
	今の `GET /api/v1/repositories`（`dashboard_http.py` の `_repositories`）は、出すリポジトリを鍵の順に `repository`、`host`、`owner`、`name`、`path`、`api`、`problem` で返し、リポジトリどうしの入れ子は返さない。
	`DashboardSite` は、登録簿（`canonical-registry.json`）の各行の `main_checkout` を持ち、1つのクローンのリポジトリは `SiteRepository.checkout` にそれを覚えている（2つのクローンは `ambiguous` で None）。
	"""

includes: [
	"入れ子と段の札を決める純粋な関数（Epic の D-01）",
	"`DashboardSite` の一覧の読み直しでの計算と覚え（Epic の D-01）",
	"`GET /api/v1/repositories` の各リポジトリへの `parent` と `tier` の追加（Epic の D-02）",
	"配る側の契約の文書 `src/spec_dock/assets/spec_dock/docs/reference_cli.md` の更新と、`src/spec_dock/assets/static-inventory.json` の sha256 の更新",
]

excludes: [
	"画面（`/graph`、タブ、描画）の変更（iss-00614）",
	"`dashboard list` の出力、構造の API（`…/structure`）が返す worktree の道の変更",
	"dogfood の写し `spec-dock/docs/reference_cli.md` の更新（配布の更新で揃える）",
	"入れ子を決める設定のファイル",
	"リリースと配布",
]

requirements: {
	"R-01": {
		title: "リポジトリの入れ子を、登録された main のチェックアウトのパスで決める"
		text: """
			出すリポジトリ A の main のチェックアウトが、出す別のリポジトリ B の main のチェックアウトの中にあれば、A は B の子とする。候補が複数あれば、いちばん近い祖先（いちばん深い B）を採る。
			どの出すリポジトリの中にもないリポジトリは最上位（`parent` が null）に並ぶ。「中にある」はパスの部分で比べ、名前の頭が同じだけのものは含まない。同じパスは親子にしない。設定のファイルは足さない。
			"""
		acceptance: [
			"この PC の登録の形（9つ）の合成の入力で、company-os・spec-dock・orca-web の `parent` が null、housing-lifecycle と input-devices の `parent` が company-os、taikyohiyou_project の `parent` が housing-lifecycle、generic-mona・tenting-cradle・yubisaki の `parent` が input-devices になる",
			"名前の頭が同じだけの隣のディレクトリ（`<ws>/a` と `<ws>/a-b`）は親子にならない",
			"3段の入れ子（A の中に B、B の中に C）で、C の `parent` は B（いちばん近い祖先）",
		]
	}
	"R-02": {
		title: "親から子へのパスの途中のディレクトリの名前を、段の札にする"
		text: """
			親のチェックアウトから子のチェックアウトまでの、途中のディレクトリの名前（子のディレクトリ自身を除く）を、上から順に段の札にする。
			`businesses` → 事業、`products` → プロダクト、`services` → サービス。知らない名前はそのまま出す。親の直下なら札は空。最上位のリポジトリの札は空。
			"""
		acceptance: [
			"この PC の登録の形で、housing-lifecycle と input-devices の `tier` が `[\"事業\"]`、taikyohiyou_project・generic-mona・tenting-cradle・yubisaki の `tier` が `[\"プロダクト\"]`、最上位の3つの `tier` が `[]`",
			"途中が `groups/team` なら `tier` は `[\"groups\", \"team\"]`、親の直下なら `[]`、途中が `services` なら `[\"サービス\"]`",
		]
	}
	"R-03": {
		title: "入れ子と段の札は、サーバーが一覧の API で返し、パスはブラウザーに出さない"
		text: """
			`GET /api/v1/repositories` の各リポジトリに、`parent`（同じ応答の `repositories` にある親のリポジトリの鍵、なければ null）と `tier`（文字列の配列）を足す。
			今ある項目、その値、並び（鍵の順）、`schema`（`specdock.dashboard/v1`）は変えない。
			登録の `main_checkout` とカタログの道の文字列は応答に入れない（段の札に写る途中のディレクトリの名前を除き、ディレクトリの名前そのものも返さない）。
			"""
		acceptance: [
			"一覧の API の応答の各リポジトリに `parent` と `tier` があり、今の7つの項目の値と、リポジトリの並びが今と同じ",
			"各 `parent` が null か、同じ応答の `repositories` のいずれかの `repository` の値である",
			"応答の JSON の文字列のどこにも、登録の `main_checkout` とカタログの道（と、それらの親の作業の根の道）が現れない",
			"`src/spec_dock/assets/spec_dock/docs/reference_cli.md` のダッシュボードのサーバーの契約に、2つの項目と決め方と、道を返さないことが書かれ、`static-inventory.json` の sha256 がその内容と合う",
		]
	}
}

failures: {
	"F-02": {
		title: "1つのチェックアウトに決まらないリポジトリは、最上位に並び、親にならない"
		text:  "同じリポジトリの2つのクローンを登録している（`problem` が `ambiguous`）など、main のチェックアウトが1つに決まらないリポジトリは、`parent` が null、`tier` が空で、ほかのリポジトリの親にならない（そのクローンの中にある出すリポジトリは、さらに外の出す祖先の子になるか、最上位）。"
	}
	"F-03": {
		title: "隠したリポジトリは出さず、その中のリポジトリは、出す祖先の子になる。隠したものの名前は札に出ない"
		text: """
			隠したリポジトリ（隠す印、または設定で見せないもの）は一覧に出ず、親にもならない。その中にあるリポジトリは、いちばん近い出す祖先の子になる（なければ最上位）。
			段の札は、いちばん近い登録されたチェックアウト（隠したもの、リポジトリの分からない行、ambiguous のクローンの行を含む、登録簿のすべての行）から子までのパスで決めるので、隠したリポジトリのディレクトリの名前とその上の途中の名前は札に現れない。親がなければ札は空。
			"""
	}
	"F-05": {
		title: "絶対の道でない登録の行は、入れ子に使わない"
		text:  "登録簿の `main_checkout` が絶対の道でない（空を含む）行は、境界にも親にも使わない。その行のリポジトリが出すものなら、最上位で札は空。応答は失敗にしない。"
	}
}

constraints: [
	"入れ子の決め方は、ファイル・ネットワーク・時刻に触れない純粋な関数1つに置き、Python の単体テストで確かめる",
	"道の正規化（`os.path.realpath`）は、一覧を読み直すとき（登録簿・隠す印・設定が変わったとき）に1回だけ行い、要求ごとには行わない",
	"公開のリポジトリの文書とテストに、この PC の実際のパスを書かない（合成のパス、`tmp_path` を使う）",
	"契約の版 `specdock.dashboard/v1` は変えない（項目を足すだけ）",
]

decisions: [
	"2026-11-16 統括（Epic の決定1・2・7、依頼書）：入れ子は登録された main のチェックアウトのパスのいちばん近い祖先で決め、段の札は途中のディレクトリの名前（businesses → 事業、products → プロダクト、services → サービス、知らない名前はそのまま）。サーバーが返し、入れ子のためにパスをブラウザーへ新しく渡さない。",
	"2026-11-16 統括（依頼書で確かめた Epic の細部）：新しい API は足さず `GET /api/v1/repositories` に `parent` と `tier` を足す。隠したリポジトリの中のものは出す祖先の子にし、段の札は最も近い登録から数える。チェックアウトが1つに決まらないものは最上位。",
	"2026-11-16 タスク担当（この Issue の細部）：境界は登録簿のすべての行の `main_checkout`（隠したもの、リポジトリの分からない行、ambiguous の各クローン）。絶対の道でない行は使わない（F-05）。並びと鍵は今の一覧のまま、応答の各リポジトリの末尾に `parent`、`tier` の順で足す。",
	"2026-11-16 タスク担当：一覧と入れ子は同じ一覧の読み（同じ鍵の内側）から返し、1つの応答の中で `parent` が出さない鍵を指さないようにする。",
]
