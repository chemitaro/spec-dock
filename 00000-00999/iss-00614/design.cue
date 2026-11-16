package spec

// 設計（Issue）。型 specdock/v1。Epic epic-00612 の design.cue の D-03〜D-07 を、この Issue で実装できる細さにする。

goals: [
	"各リポジトリの中は、今の配置（layout.js の routeLayout）と線（router.js）と部品（draw.js に取り出した箱・枠・塊）をそのまま使い、リポジトリの枠の組み立て（compose.js）だけを新しく足す",
	"組み立ては DOM のない純粋な計算にして、入れ子、出すかどうか、寸法、後から足す帯を node のテストで確かめる",
	"構造の図（graph.js）の見え方と動きは変えない",
]

current: """
	- 横断の画面は `/`（overview）と `/todos`。タブは `core/topbar.js` の `ALL_TABS`、道は `core/route.js` の `parseRoute`、殻の道はサーバーの `_get`（`dashboard_http.py`）と `app.js` の `interceptLinks`、題名は `app.js` の `title()`。
	- `GET /api/v1/repositories` の各リポジトリは `repository`・`host`・`owner`・`name`・`path`・`api`・`problem`・`parent`・`tier` を持つ（iss-00613）。殻は `ctx.repositories` で画面に渡す。
	- `views/graph.js` は1つのリポジトリ（`ctx.data`）を、モジュールの状態 `V` で描く。`boxHtml`・`frameHtml`・`chipHtml`・`clnMark`・`edgeClass`・`tally`・`maxOpenStage`・`pos` は `V.ix`・`V.desc`・`V.data`・`V.path`・`V.sel` を直接読む。
	- iss-00620：`measureMarks` が置き場（`[data-orca-scope]`）の印の幅を測り、`checkRows` が `nodeMarkRows` で行の数を比べ、違えば `V.marks` を渡して配置し直す（1回の知らせか描画につき2回まで）。
	"""

target: """
	- `views/graph/draw.js`：箱・枠・塊の HTML と線の class を、引数の「描く文脈」で作る純粋な関数。graph.js はそれを呼ぶだけ。
	- `views/allgraph/compose.js`：リポジトリの枠の組み立て（純粋）。
	- `views/allgraph.js` と `views/allgraph.css`：`/graph` の画面。殻の構造と graph.css を使い、リポジトリごとの状態を `Map` で持つ。
	- 道・タブ・題名・殻の道・サーバーの `_get`・契約の文書に `/graph`。
	"""

design: {
	"D-01": {
		title: "道、タブ、題名、殻の道、サーバー"
		text: """
			- `core/route.js` の `parseRoute`：`parts` がちょうど `["graph"]` なら `view: "allgraph"`（repository・scope・todo は null）。`export const allGraphPath = "/graph"` を足し、先頭のコメントに道を足す。
			- `core/topbar.js` の `ALL_TABS`：［overview `/` 横断の概況 globe］［allgraph `/graph` 横断の構造 layers］［todos `/todos` 人のタスク person］。
			- `views/index.js` の `VIEWS` に `allgraph` を足す（先頭のコメントの ctx の説明も合わせる）。
			- `app.js`：`title()` で、repository なしで view が `allgraph` なら「横断の構造 · すべてのリポジトリ · SpecDock」。`interceptLinks` の殻の道の判定に `url.pathname === "/graph"` を足す（リポジトリのない道なので、今と同じくページの読み込みで移る）。
			- `dashboard_http.py` の `_get`：`head == "graph" and not rest` なら `_shell`（`/graph/` は末尾の空を除いて同じ）。`/graph/x` は今どおり 404。
			- 配る側の `src/spec_dock/assets/spec_dock/docs/reference_cli.md` の「画面の道」の行に `/graph`（横断の構造）と `/todos`（人のタスク）を足す。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "描く部品の取り出し（views/graph/draw.js）"
		text: """
			graph.js の `clnMark`・`boxHtml`・`frameHtml`・`chipHtml`・`pos`・`edgeClass` と、それらが使う `tally`・`maxOpenStage`・`cleanupOf` の中身を draw.js に移し、モジュールの状態を読まず、次の「描く文脈」を引数で受ける：

			`dc = {data, ix, desc, cleanup, range, path, sel}`（`data` は構造の JSON、`ix` は `index(data.scopes)`、`desc` は graph.js の `descendants(ix)` と同じ関数、`cleanup` は `Map`（id → 片付けの候補）、`range` は layout の `opts.range`、`path` と `sel` は線の class のための選びの状態）。

			draw.js の公開：`descendants(ix)`、`cleanupMap(data)`、`tally(dc, id)`、`boxHtml(dc, s, n)`、`frameHtml(dc, s, n)`、`chipHtml(dc, g)`、`edgeClass(dc, e)`、`pos(r)`、`treeSvgPaths(trunks)`（今の `buildWorld` の trunks の path の文字列）。文字列の組み立ては1文字も変えない。
			graph.js は `V` から `dc` を作って呼ぶだけにする（`V.desc` は `descendants(V.ix)`）。draw.js の関数の中で描く文脈を受ける引数の名前は `V` にし（例 `boxHtml(V, s, n)`）、`V.ix.byId` などのソースの文字列がそのまま残るようにする（ソースの文字列のテストの文字列を変えないため）。`buildWorld`・`paint`・`renderBar`・`renderLegend`・`edgeAudit` などのほかの部分は graph.js に残す。

			確かめ（R-02）：取り出す前（開始のコミット）の graph.js を、`tests/js/dashboard_graph_toolbar.mjs` と同じ偽の DOM で、複数の構造（入れ子・木 × 全体・いま・これから、focus、片付けの候補、稼働の印の行の寸法、選びと状態の札）に描き、世界・道具の帯・状態の札・凡例の HTML を、テストの資料（`tests/fixtures/dashboard/graph_dom_golden.json` などの、合成の構造だけを持つ固定の写し）に残す。取り出した後の graph.js が同じ HTML を出すことをテストで確かめる。
			graph.js のソースの文字列を調べる今のテスト（`test_dashboard_orca_views_js.py`、`test_dashboard_shell_polish.py`、`test_dashboard_state_marks.py`、`test_dashboard_scope_tabs_js.py` のうち、移した関数の中を調べるもの）は、調べるファイルを draw.js に移し、確かめる文字列と数を変えない。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "リポジトリの枠の組み立て（views/allgraph/compose.js）"
		text: """
			DOM なし。`layout.js` と同じ px の単位。公開：

			- `REPO`（寸法の定数）：`head: 40`（見出しの行）、`warn: 24`（警告1件の行）、`line: 28`（文1行の中身：読み込み中、Scope がない）、`pad: 16`（枠の内側の左右と下の余白、中身と子の棚の間の余白。見出しと中身の間には置かない）、`gap: 16`（兄弟の枠の間、縦と横）、`minW: 360`（中身の使える幅の下限）、`headW: 280`（見出しの最小の幅）、`margin: 8`（世界の外側）。値は CSS（allgraph.css）と一緒に変える（コメントで互いを指す）。
			- `bodyWidth(width, depth)`：深さ `depth`（最上位が0）の枠の中身が使える幅 `max(REPO.minW, width − 2·REPO.margin − 2·REPO.pad·(depth + 1))`。最上位の枠の外の幅の上限が `width − 2·REPO.margin`、子の枠の外の幅の上限が親の中身の使える幅、という決まりから出る式。画面はこの値を、そのリポジトリの `routeLayout` の `width` に渡す。
			- `compose(repos, sizes, options)`：
			  - `repos`：一覧の API の並びの `[{repository, parent, tier, owner, name}]`。
			  - `sizes`：鍵 → `{status: "loading"|"failed"|"ok", w, h, shown, scopes, warns, alerts}`。`ok` のとき `w`・`h` はそのリポジトリの routeLayout の `layout.width`・`layout.height`（Scope がないときは 0・0）、`shown` は `layout.nodes.length + layout.groups.length`、`scopes` はそのリポジトリの Scope の数。`warns` は警告の行の数（枠を出すときに並べる数で、info を含む）、`alerts` はそのうち info でない警告の数（Epic D-04 の `warn` に当たり、出すかの判定だけに使う）。鍵がなければ `loading`。
			  - `options`：`{range, width, bands}`。`width` は図の領域の 100% での幅、`bands` は鍵 → 帯の高さ（px、既定は {}、ない鍵は 0）。
			- 木：`parent` が同じ `repos` にあればその子、なければ最上位。親をたどって自分に戻るものは最上位（F-03）。兄弟は `repos` の並び。
			- 出すか：`all`・`now` ではすべて。`next` では、`status` が ok、`shown` が0、`alerts` が0のリポジトリは、出す子が1つもなければ出さない（子から先に決める）。`loading`・`failed`・`alerts` が1以上は出す。info だけの警告（例：PR の状態が分からない）は、出すかを変えない。
			- 中身の種類 `body.kind`（上から順に最初に当たるもの）：`loading`（読み込み中：`REPO.line` の高さ、「読み込んでいます…」）、`failed`（高さ0。理由は警告の行）、`graph`（ok で shown が1以上：`w × h`）、`empty`（ok で Scope が0：all・now では `REPO.line` の高さで「Scope はまだありません」、next で出すとき（子か alerts のため）は高さ0）、`quiet`（ok で Scope が1以上で shown が0：all・now では `REPO.line` の高さで「この範囲で見せる Scope はありません」、next で出すとき（子か alerts のため）は高さ0）。next で高さ0の枠は、見える子があれば入れ物、なければ alerts のための枠である。`kind` と `h` はこの表だけで決まり、どの（範囲、status、shown、scopes）の組にも1つ当たる。
			- 枠の縦の並び：見出し `REPO.head`、警告 `warns × REPO.warn`、帯 `bands[key]`、中身（ここまで余白なしで積む。中身の図は自分の余白 `SIZE.margin` を持つ）、（出す子があれば）`REPO.pad` を空けて子の棚、下の余白 `REPO.pad`。中身の高さが0のときは中身と棚の間の余白を入れない。帯の四角は、見出しと警告の行のすぐ下から `bands[key]` の高さ。
			- 子の棚：子の枠を、その親の中身が使える幅 `bodyWidth(width, 親の深さ)`（中身の実際の幅ではない）で左から右へ `REPO.gap` を空けて詰め、入らなければ次の行。行の高さはその行のいちばん高い枠。
			- 枠の幅：`max(REPO.headW, 中身の幅, 棚の幅) + 2·REPO.pad`。最上位も同じ詰め方で `options.width − 2·REPO.margin` で折り返す。
			- 出力：`{frames: Map(鍵 → {key, depth, x1, y1, x2, y2, head: {x1,y1,x2,y2}, warn: {x1,y1,x2,y2}, band: {x1,y1,x2,y2}, body: {kind, x, y, w, h}（w は graph では layout の幅、ほかは 0）}), order: [出す鍵（深さ優先、親が子の前）], width, height}`。座標は世界の左上が原点。`band` の高さは `bands[key]`（0 なら高さ0の四角）。
			- 帯の高さを渡さないときと全部 0 のときの出力は同じ（R-04）。
			"""
		satisfies: ["R-03", "R-04", "R-05", "F-03"]
	}
	"D-04": {
		title: "画面の殻と状態（views/allgraph.js）"
		text: """
			- 殻：graph.js の `mount` と同じ構造（`section.gx` の中に `.gx-view > .gx-world`、`.gx-none`、`.gx-bar`（`.gx-left > .gx-next`、`.gx-tools`。crumbs なし）、`.legend`、`aside.panel`、`.gx-empty`）。`section.gx` に `data-screen="allgraph"`。styles は graph の4つ（parts・scope_tabs・panel・graph の CSS）と `/assets/views/allgraph.css`。
			- 状態：モジュールの1つの状態 `A`（範囲、目立たせる札、選び `{repo, id}`、path・docState・docRevision・token、拡大と位置、fitted、幅）と、鍵 → リポジトリの状態の `Map`：`{structure, failure, revision, ix, desc, eg（routeLayout の結果と ms）, sig, marks, rowsRedo, warnings}`。
			- 読み込み：初めの render で `ctx.repositories` の各リポジトリを `api.structure(鍵, null)` で並べて読み、届いた順に、配置を求めて描く。複数が届いたときは、リポジトリごとに `setTimeout(0)` で描画へ戻してから次を配置する。
			- 状態の決め方：HTTP の失敗 → `failed`（`overviewWarnings(null, error.message)`）。答えがあり `scopes` が空で `snapshot.status` が ok でない → `failed`（`overviewWarnings(structure, null)`）。それ以外は `ok`（`scopes` が空なら Scope なし）で、`overviewWarnings(structure, null)` を警告の行に出す。
			- 配置：ok で Scope のあるリポジトリは `routeLayout(scopes, cleanup, {mode: "nest", range, focus: null, width: bodyWidth(図の幅, 深さ), height: 図の高さ, marks})`。sig は `${revision}|${range}|${width}|${30分の動きの印の ID}|${JSON.stringify(marks)}` で、同じなら計算し直さない（R-08）。routeLayout を呼んだ回数を `window.specdockAllGraphStats = {layouts, loads}` に数える（テストと実機の確かめのため）。
			- 更新：5秒ごと（`document.hidden` でないとき、`visibilitychange` でも）に各リポジトリの `api.revision` を読み、変わったリポジトリだけ構造を読み直す。30分の動きの印の境目を過ぎたリポジトリは描き直す（graph と同じ `M.isLive`）。dispose で止める。「見た」は送らない。
			- 描画：`compose` の結果で、世界の大きさを決め、`order` の順に `section.ax-repo[data-repo=鍵][data-depth=深さ]` を世界に平らに並べる（`pos(frame)`）。中身は、見出し `.ax-head`（folder のアイコン、`owner/name`、段の札の `sd-badge` を「 › 」でつなぐ。リポジトリの構造の図への小さなリンク `/r/<鍵>/` を添える）、警告の行 `.ax-warn`（1件1行、`overviewWarnings` の text と次の1手、省略、全文は title）、`.ax-body`（body の座標に絶対配置。中に今の部品：trunks の svg、frames、boxes、chips、`svg.gx-edges`。座標はそのリポジトリの layout のまま）。`empty`・`quiet`・`loading` で高さが `REPO.line` のときは、`.ax-body` に D-03 の1行の文（高さ0のときは何も描かない）。
			- 1つのリポジトリが変わったときは、そのリポジトリの `.ax-body` の中だけ書き直せばよいが、組み立ての寸法が変わったら全体の位置を直す（実装の裁量。描き直しても見え方が同じなら可）。
			- 空のとき（F-02）：表示しているリポジトリが0なら `.gx-empty` に概況と同じ文（道具の帯も隠す）。`next` で `order` が空なら `.gx-none` に F-02 の文（道具の帯は残す）。
			"""
		satisfies: ["R-03", "R-05", "R-08", "F-01", "F-02"]
	}
	"D-05": {
		title: "道具の帯、凡例、目立たせる札、範囲の覚え"
		text: """
			- 道具の帯：拡大・縮小・100%、『収める』、『全体・いま・これから』（graph.js の RANGES と同じ文・アイコン・title）。入れ子と木の切り替えと crumbs はない。
			- 状態で目立たせる札：graph.js の HL と同じ並びと文。数は出している枠のリポジトリの、終わっていない Issue の合計（graph の renderBar と同じ数え方）。押すとすべての枠の箱に `is-hl`・`is-dim` を当てる。
			- 凡例：graph.js と同じ凡例を出す（graph.js の renderLegend を draw.js に移すか、同じ関数を呼べるようにする。graph.js の HTML は変えない）。
			- 範囲の覚え：`specdock.allgraph.v1` に `{range}`。読むときは try/catch、値が RANGES の外なら `next`。`specdock.graph.v3` は読まず書かない。
			"""
		satisfies: ["R-05", "R-06"]
	}
	"D-06": {
		title: "選び、横の欄、稼働の印とエージェントの行"
		text: """
			- 押したときの探し：`target.closest(".gx-box, .gx-fh")` と `target.closest("[data-repo]")` で（リポジトリ、ID）を決める。選びのたびに目立たせ（graph の paint と同じ規則）を、選んだリポジトリの枠の中は path で、ほかの枠の箱と枠は `is-poff` で淡くする。線の class（`edgeClass`）も選んだリポジトリだけ path を使い、ほかは path なし。
			- 横の欄：`createScopePanel` を1つ。`show` には `{ctx: repoCtx(鍵), scope, doc, docState, byId}` を渡す。`repoCtx(鍵)` は `{...ctx, repository: 鍵, data: そのリポジトリの構造, current: () => { const c = 殻の ctx.current(); return c ? {...c, repository: 鍵, data: 今覚えているそのリポジトリの構造} : null; }}`。スコープの API は `api.scope(鍵, ID, null)`。
			- 欄の `onSelect(id)` は同じリポジトリの中の選び。`extraActions` は graph と同じ『この範囲に絞る』で、押すと `ctx.navigate("/r/<鍵>/?focus=<ID>")`（別のリポジトリなので殻がページを読み込む）。ダブルクリックとスマホの2度目のタップは `ctx.navigate(scope.path)`。
			- 稼働の印：描くたびと orca-web の知らせのたびに、リポジトリごとに `paintOrcaMarks(その枠の .ax-body, ctx, そのリポジトリの構造)` を呼び、欄の `refreshOrca()` を呼ぶ。
			- エージェントの行：リポジトリごとに graph.js の `measureMarks`・`checkRows` と同じ手順（そのリポジトリの `.ax-body` の中だけを測り、`nodeMarkRows` で比べ、違えばそのリポジトリの marks を変えて配置し直し、組み立て直す。1回の知らせか描画につき、リポジトリごとに2回まで）。ResizeObserver は世界のすべての置き場を見て、1フレームに1回まとめて確かめる。
			"""
		satisfies: ["R-06", "R-03"]
	}
	"D-07": {
		title: "広さ、初めの見え方、線の検査"
		text: """
			- 拡大の下限だけは、graph.js の `max(0.02, min(0.12, fitScale))` の 0.02 を、全体を収めるのに要る倍率まで下げる（例 `max(0.002, min(0.12, fitScale))`）。実データの『全体』では世界が数万 px になり、0.02 では『収める』で収まらないため（R-07）。graph.js は変えない。
			- 初めの見え方、『収める』、ズームと移動の操作、Safari の gesture の止め、窓の大きさの変化（200ms 落ち着いてから幅が変わったときだけ組み立て直す）は、graph.js と同じ式を compose の `width`・`height` に当てる。graph.js の関数をそのまま写してよい（共有のために graph.js を変えるなら、出す HTML と動きを変えない）。
			- 390px 以下（PHONE 640 の判定は graph と同じ）では、横の欄は今の下からのシート、道具の帯は graph.css のスマホの形。
			- `window.specdockEdgeAudit(options)`：リポジトリごとに、graph の edgeAudit と同じ計算を、そのリポジトリの `.ax-body` の四角を原点にして行い、`{repos: {鍵: 結果}, total: {各数の合計}}` を返す。dispose で消す。
			- 共有の CSS が効く範囲：graph.css の部品の絶対配置などは `.gx .gx-world > .gx-box` のような子の結合子で書かれ、`.main[data-view="graph"]` と panel.css の `:is([data-view="graph"], [data-view="board"])`（`--pn-w`）は view の名前で当たる。allgraph の部品は `.gx-world > section.ax-repo > .ax-body` の中にあり、殻は `data-view="allgraph"` を付けるので、これらに当たる規則を allgraph.css に足す（`.ax-body > .gx-box` などの絶対配置と重なりの順、`.main[data-view="allgraph"]`、`[data-view="allgraph"]` の `--pn-w`）。共有の CSS のセレクターに `[data-view="allgraph"]` を足すやり方でもよいが、構造の図とボードの見え方は変えない。
			- allgraph.css：`.ax-repo`（2px の線、角の丸みを Initiative の枠と変える、背景は今の面の色の札）、`.ax-head`（folder のアイコンと名前の帯）、`.ax-warn`、`.ax-body`、深さで背景を少し変えるなら今の札だけで。新しい色の値と色の札は書かない（R-03）。寸法は compose.js の REPO と揃える。
			- 確かめ（R-07）：この PC の状態の置き場を写した一時の置き場と隔離した venv で `dashboard serve --offline --tailscale` を別のポートで立て、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じる）で 1440・1000・390 × 明・暗 × 3つの範囲を写し、edgeAudit（倍率 100% で測る）とブラウザーのエラーと横のスクロールを数える。違反が出たリポジトリは、単体の構造の図（`/r/<鍵>/`、同じ範囲、中の幅と同じ見える幅）で同じ数かを比べ、表にする。稼働の印は、常駐の orca-web の要約を読むだけで中継する試しの orca（iss-00620 と同じ作り）で確かめる。
			"""
		satisfies: ["R-07"]
	}
}

compatibility: """
	一覧の API と構造の API は変えない。リポジトリの画面、概況、人のタスクの見え方と道は変わらず、横断の画面のタブが1つ増える。保存は新しい鍵 `specdock.allgraph.v1` を足すだけ。
	PR を戻すと `/graph` とタブがなくなり、今の画面に戻る。
	"""

risks: [
	"すべてのリポジトリの配置と線を1枚で求めるので、初めの描画が遅くなりうる。リポジトリごとに覚え、届いた順に描き、間に描画へ戻す。実データでのリポジトリごとの ms を report に残す",
	"`graph.js` からの部品の取り出しで構造の図の見え方が変わりうる。開始のコミットの HTML の写しとの一致で確かめる",
	"警告を1行に省略するので、長い理由はその場で全文が読めない（title と概況で読める）",
	"深い入れ子で中の図の使える幅が狭くなる。下限 `REPO.minW` を置き、超える分は横に広がる（『収める』で収まる）",
]
