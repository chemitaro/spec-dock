package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"入れ子（親と段の札）はサーバーが1か所で決め、パスを出さずに一覧の API で返す",
	"各リポジトリの中は、今の配置（layout.js）と線（router.js）と部品をそのまま使い、リポジトリの枠の組み立てだけを新しく足す",
	"リポジトリの構造の図の見え方と動きは変えない",
]

current: """
	- `DashboardSite.repositories()` が、出す（登録され、分かり、隠していない）リポジトリを鍵の順に返す。各 `SiteRepository` は、1つのクローンなら `checkout`（登録の main のチェックアウト）を持ち、2つのクローンなら `catalog` と `checkout` が None で `problem` が `ambiguous`。
	- `GET /api/v1/repositories`（`dashboard_http.py` の `_repositories`）は、各リポジトリの `repository`、`host`、`owner`、`name`、`path`、`api`、`problem` を返す。
	- 横断の画面は `/`（`views/overview.js`）と `/todos`（`views/todos.js`）。上の帯のタブは `core/topbar.js` の `ALL_TABS`、道の読み取りは `core/route.js` の `parseRoute`、サーバーの殻の道は `dashboard_http.py` の `_get`、殻の中の移動は `app.js` の `interceptLinks`。
	- 構造の図（`views/graph.js`）は1つのリポジトリの構造（`ctx.data`）だけを描くモジュールで、箱・枠・塊の HTML（`boxHtml`、`frameHtml`、`chipHtml`）、線の SVG、横の欄（`_shared/panel.js` の `createScopePanel`）、稼働の印（`_shared/orca_marks.js`）を、モジュールの1つの状態 `V` で扱う。DOM の探しは `data-id` だけで行う。
	"""

target: """
	- サーバー：一覧の各リポジトリに `parent`（親のリポジトリの鍵か null）と `tier`（段の札の配列）。決め方は純粋な関数1つ。
	- 画面：`/graph` の新しい画面 `allgraph`。各リポジトリの構造を読み、リポジトリごとに今の `routeLayout` で配置と線を求め、新しい純粋な組み立て（`views/allgraph/compose.js`）でリポジトリの枠を入れ子に並べ、今の部品で描く。
	"""

design: {
	"D-01": {
		title: "入れ子と段の札を決める純粋な関数"
		text: """
			`runtime/application/dashboard_nesting.py`（新しい、DOM・ファイル・ネットワークに触れない）に、
			`repository_nesting(shown: Sequence[tuple[str, str | None]], boundaries: Sequence[str]) -> dict[str, Nesting]` を置く。
			`shown` は出すリポジトリの（鍵、ただ1つの main のチェックアウトか None）、`boundaries` は登録簿のすべての行の main のチェックアウト（隠したもの、リポジトリの分からない行、2つ目のクローンを含む）。`Nesting` は `parent: str | None` と `tier: tuple[str, ...]`。

			- 道の比べ方：呼ぶ側が `os.path.realpath` で正規化した絶対の道を渡す（関数の中ではファイルを見ない）。「中にある」は、道の部分（`PurePath.parts`）で、親の部分が子の部分の真の頭であること（文字の頭ではない。R-01 の2つ目）。同じ道は親子にしない。
			- 親：チェックアウトが None でない出すリポジトリのうち、子のチェックアウトを中に持つ、いちばん深いもの（R-01）。None のリポジトリは親にならず、自身も最上位（F-02）。
			- 段の札：子のチェックアウトを中に持つ境界（boundaries と、出すリポジトリのチェックアウト）のうち、いちばん深いものから子までの相対の部分の、最後（子のディレクトリ）を除いた並び。各部分を `{"businesses": "事業", "products": "プロダクト", "services": "サービス"}` で写し、ないものはそのまま。中に持つ境界がないか、親がないなら空（R-02、F-03）。親が隠したリポジトリを飛び越すときも、札はいちばん近い境界（隠したもの）から数えるので、隠したもののディレクトリの名前は現れない。
			- 返す順と鍵は `shown` のまま。

			`DashboardSite` は、一覧を読み直すとき（`_refresh_listing`）にこの関数を呼び、結果を `_Listing` に覚える（登録簿と印が変わったときだけ計算し直す）。`realpath` は、その時の1回だけ。
			"""
		satisfies: ["R-01", "R-02", "F-02", "F-03"]
	}
	"D-02": {
		title: "一覧の API に `parent` と `tier` を足す"
		text: """
			`_repositories` の各リポジトリに `"parent": <鍵か null>` と `"tier": [<札>…]` を足す。今の項目、並び（鍵の順）、`schema` は変えない。
			`parent` は、同じ応答の `repositories` にある鍵だけを指す（出さないリポジトリを指さない）。道とカタログの文字列は応答に入れない。
			`reference_cli.md` の「ダッシュボードのサーバーの契約」の API の行に、2つの項目、決め方（チェックアウトの道のいちばん近い祖先、段の札の写し、隠したものと ambiguous の扱い）、道を返さないことを書く。
			"""
		satisfies: ["R-03", "F-02", "F-03"]
	}
	"D-03": {
		title: "画面の道とタブ"
		text: """
			- `core/route.js`：`parts` がちょうど `["graph"]` なら view `allgraph`（リポジトリなし）。`allGraphPath = "/graph"` を足す。
			- `core/topbar.js` の `ALL_TABS` を ［overview `/` 横断の概況 globe］［allgraph `/graph` 横断の構造 layers］［todos `/todos` 人のタスク person］にする。
			- `views/index.js` の `VIEWS` に `allgraph` を足す。`app.js` の `title` に「横断の構造 · すべてのリポジトリ · SpecDock」、`interceptLinks` の殻の道に `/graph` を足す。
			- サーバーの `_get` で、`graph` だけの道を殻（`_shell`）にする。
			- `reference_cli.md` の「画面の道」に `/graph`（と今ある `/todos`）を書く。
			"""
		satisfies: ["R-04"]
	}
	"D-04": {
		title: "リポジトリの枠の組み立て（純粋な計算）"
		text: """
			`views/allgraph/compose.js`（DOM なし）に `compose(repos, sizes, options)` を置く。

			- 入力：`repos` は一覧の API の並びの `[{repository, parent, tier, owner, name}]`。`sizes` は鍵ごとの `{status: "loading"|"failed"|"ok", w, h, shown}`（ok のとき `w`・`h` はそのリポジトリの `layout` の幅と高さ、`shown` は見える箱・枠・塊の数）。`options` は `{range, width}`（width は図の領域の 100% での幅）。
			- 木：`parent` が同じ一覧にあればその子、なければ最上位。循環は起こらないが、たどった鍵を覚えて二度目は最上位に置く。兄弟は一覧の並び。
			- 出すか：`all`・`now` ではすべて。`next` では、`status` が ok で `shown` が0のリポジトリは、出す子がなければ出さない（R-06）。`loading` と `failed` は出す（F-01）。
			- 枠の形：見出しの行（高さ `REPO.head`）、中の構造の図（`w × h`。`next` で `shown` が0の入れ物、Scope のないリポジトリ、読み込み中、読めない、のときは、1行の文の高さか0）、その下に子の枠の棚。子の枠は、親の中の使える幅（`width − 2·REPO.pad·深さ`、下限 `REPO.minW`）で左から右へ詰め、入らなければ次の行へ。枠の幅は、見出しの最小の幅、中の図の幅、子の棚の幅の最大に左右の余白を足したもの。
			- 最上位も同じ詰め方で、図の領域の幅で折り返す。
			- 出力：鍵ごとの `{x1, y1, x2, y2, depth, body: {x, y}}`（body は中の構造の図の原点）と、出した鍵の並び、全体の幅と高さ。
			- 寸法の定数（`REPO`）は `layout.js` の `SIZE` と同じ単位（px）で、枠の外側の余白は線の通り道と重ならない（中の図の `layout` は自分の余白 `SIZE.margin` を持つ）。
			"""
		satisfies: ["R-05", "R-06", "R-08"]
	}
	"D-05": {
		title: "『横断の構造』の画面（views/allgraph.js）"
		text: """
			- 読み込み：`ctx.repositories`（殻が読んだ一覧）の各リポジトリの構造を `api.structure(repo, null)` で並べて読み、届いたものから描く。各リポジトリについて `routeLayout(scopes, cleanup, {mode: "nest", range, width: その深さで使える幅})` を求め、鍵ごとに（revision、range、幅、30分の動きの印）の組で覚える。組が同じなら計算し直さない（R-09）。重い計算で画面が固まらないよう、リポジトリの間で一度描画に戻す（`requestAnimationFrame` か `setTimeout(0)`）。
			- 更新：5秒ごと（`document.hidden` でないとき）に各リポジトリの `api.revision` を読み、変わったものだけ構造を読み直す（R-09）。「見た」は送らない。
			- 描画：`compose` の結果で、リポジトリごとに `<section class="ax-repo" data-repo="<鍵>">` を置き、見出し（folder のアイコン、`owner/name`、段の札を `sd-badge` で、札が2つ以上なら「 › 」でつなぐ。読めないときは理由）と、中の構造の図の層（今の箱・枠・塊・線の HTML を、そのリポジトリの `layout` の座標で、body の原点だけずらして置く）を描く。拡大・移動は全体の1つの世界（`gx-world` と同じ transform）で行う。
			- 部品の共有：`graph.js` の箱・枠・塊・線の HTML を作る関数（`boxHtml`、`frameHtml`、`chipHtml` と、線の class の決め方）を `views/graph/draw.js` に取り出し、構造（`data`、`ix`、`desc`、`cleanup`、range）を引数で受けるようにする。`graph.js` はそれを呼ぶだけにし、出す HTML を変えない（今のテストと写しの比べで確かめる）。
			- リポジトリの枠の見え方：Initiative の枠と違う形（例：見出しに folder のアイコンと名前の帯、2px の線や二重線、角の丸みの違い）を、今の色の札（`--sd-*`、`--ds-*`）だけで作る。新しい色の値は足さない（R-05）。
			- 見せる範囲：道具の帯に、構造の図と同じ『全体・いま・これから』と、状態で目立たせる札、凡例、収める、拡大・縮小を置く。入れ子と木の切り替えはない。範囲の覚えは `localStorage` の `specdock.allgraph.v1`（`{range}`、読めなければ既定の `next`）。構造の図の `specdock.graph.v3` には触れない（R-06）。
			- 空のとき：表示しているリポジトリが0なら概況と同じ知らせ。`next` で出す枠がなければ F-04 の知らせ。
			"""
		satisfies: ["R-05", "R-06", "R-09", "F-01", "F-04"]
	}
	"D-06": {
		title: "選び・横の欄・稼働の印を、リポジトリの文脈で扱う"
		text: """
			- 選びの鍵は（リポジトリ、Scope の ID）の組。DOM の探しは、まずリポジトリの枠（`data-repo`）、その中で `data-id` で行う（R-05 の「ほかのリポジトリの箱と混ざらない」）。
			- 横の欄：`createScopePanel` を1つ置き、選んだリポジトリの文脈 `{...ctx, repository: 鍵, data: そのリポジトリの構造}` で `show` する。スコープの API は `api.scope(鍵, ID, null)`。『詳しい画面』は `scope.path`（`/r/<鍵>/scopes/<ID>`）で、殻の `interceptLinks` が別のリポジトリへのページの読み込みにする。『この範囲に絞る』は、そのリポジトリの構造の図 `/r/<鍵>/?focus=<ID>` へ移る。
			- 上流・下流の目立たせと依存の線は、そのリポジトリの `layout` と線の中だけで行う（ほかのリポジトリの枠は目立たせない）。
			- 稼働の印：`paintOrcaMarks(リポジトリの枠の要素, ctx, そのリポジトリの構造)` を、描くたびと orca-web の知らせのたびに、リポジトリごとに呼ぶ。
			- 状態で目立たせる札の数は、出しているすべてのリポジトリの合計。
			"""
		satisfies: ["R-07", "R-05"]
	}
	"D-07": {
		title: "広さ、初めの見え方、線の検査"
		text: """
			- 初めの見え方と『収める』は、構造の図の `initialView` と `fit` と同じ式を、組み立ての全体の幅と高さに当てる（最小の倍率の下限も同じ）。窓の大きさが変わり終わったとき（200ms）だけ、幅を変えて組み立て直す。
			- 390px 以下では、横の欄は今の下からのシートになり、道具の帯は今の構造の図のスマホの形に従う。
			- `window.specdockEdgeAudit` に、リポジトリごとの `edgeAudit` の結果（DOM から測った四角と線、今の `audit`）と合計を返す関数を置く（R-08）。
			- 確かめ：この PC の状態の置き場を写した別の状態の置き場で、`dashboard serve --offline --state-root` を別のポートで立て、headless Chrome で 1440・1000・390 × 明・暗 × 3つの範囲を写し、edgeAudit とブラウザーのエラーを数える。常駐のダッシュボードには触れない。
			"""
		satisfies: ["R-08"]
	}
}

compatibility: """
	一覧の API は項目を足すだけ（版は変えない）。リポジトリの画面、概況、人のタスクの見え方と道は変わらず、横断の画面のタブが1つ増える。保存は新しい鍵 `specdock.allgraph.v1` を足すだけ。
	PR を戻すと、`parent`・`tier` と `/graph` がなくなり、今の画面に戻る。
	"""

risks: [
	"すべてのリポジトリの配置と線を1枚で求めるので、初めの描画が遅くなりうる。リポジトリごとに覚え、届いた順に描き、計算の間に描画へ戻す。実データでの時間を report に残す",
	"大文字と小文字を区別しないファイルシステムで、登録の道の大文字が違うと、親子を見落としうる。realpath で揃え、それでも違うものは最上位に並ぶ（表示が平らになるだけで、誤った親にはならない）",
	"深い入れ子で中の図の使える幅が狭くなる。下限 `REPO.minW` を置き、超える分は横に広がる（『収める』で収まる）",
	"`graph.js` からの部品の取り出しで、構造の図の見え方が変わりうる。今のテストと、取り出す前後の DOM の比べで確かめる",
]
