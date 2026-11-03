package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"判定はモデルに任せ、画面は API の値を並べて描くだけにする",
	"配置と経路の計算を DOM から切り離し、同じ関数をブラウザーと node のテストで走らせる",
	"骨組みの差し込み口の約束（`render(root, ctx)`、`dispose()`）だけを使い、ほかの画面と骨組みに触れない",
]
current: "`views/graph.js` と `views/timeline.js` は、骨組み（#529）の空の枠。構造の API は Scope ごとの状態、理由、PR、変化、後に続く数、待ちの数、片付けの候補、週の累計、最近の動きを返すが、依存の先、段、推奨順の位置を返さない。"
target:  "構造の図と時間の軸が、試作 d2 の見た目と振る舞いで動き、依存の線が検査で0件になる。"

design: {
	"D-01": {
		title: "構造の API に足す項目（`presentation/dashboard_api.py`）"
		text: """
			`structure` の各 Scope（`scope_item`）に足す。`scopes/<ID>` の `scope` にも同じく入る。

			- `blocked_by`：その Scope が宣言した待ち先のうち、このリポジトリの Scope の ID の配列（番号の順）。リポジトリの外の Issue は入れない。
			- `stage`：`{"all": n|null, "open": n|null}`。親の子（親がなければ最上位の Scope）の中での段。`all` はモデルの `child_stages(model, parent)`、`open` は `child_stages(model, parent, open_only=True)` の段の番号（1始まり）。循環で段がない、または `open` で閉じている Scope は `null`。
			- `rank`：モデルの推奨順（`recommended_key`）で全 Scope を並べたときの位置（0始まり）。画面は同じ段の中をこの順に並べる。
			- `assurance`、`branch`：今は常に `null`（統括が後で値を入れる。形は文字列。`assurance` は `light`／`standard`／`strict`／`critical`、`branch` はこのPCの worktree のブランチの名前）。

			`structure` の `timeline` に `weeks_by_kind: {"initiative": [...], "epic": [...], "issue": [...]}` を足す（各要素は `weeks` と同じ `{week_start, created, closed}`。モデルの `weekly_totals(model, now=now, kinds=(種類,))`）。既存の項目は変えない。
			"""
		satisfies: ["R-01", "R-05", "R-11"]
	}
	"D-02": {
		title: "経路の計算と検査（`views/graph/router.js`）"
		text: """
			試作の `ROUTER` を、DOM を知らない ES モジュールに移す。`export const C`、`route(G)`、`svg(G, routes, classes)`、`audit(routes, obs, opts)`。

			- 入力 `G = {obs: [{x1, y1, x2, y2, p1, p2, key, lane?}], frames: [{x1, y1, x2, y2, cls}], edges: [{a, z}], bounds}`。`edges` は `obs` の番号で、`a` の右の辺から `z` の左の辺へ。
			- 手順：出入りの位置の割り振り（間隔10px）、障害物を4px ふくらませた疎な直交の格子、向きを状態に持つ A*（長さ、曲がり40、枠の出入り30、共有と交差の罰則）、同じ向きの線分を8px の車線に分ける寄せ（3回）、角の半径7px と交差の切れ目の描画。足りない車線の幅は `widen: [{axis, oa, ob, amount}]` で返す。
			- 試作から足すもの：`obs` の `lane: "v"` は、縦の線分だけを塞ぐ障害物（木の親子の線）。横に横切れる。`audit` は、それに沿う縦の線分を `trunkOverlaps` に数える。
			- `audit` は試作と同じく `boxHits`、`ownHits`、`overlaps`、`diagonal`、`portShare`、`failed` を数える（`lane` の障害物は箱の当たりに数えない）。
			"""
		satisfies: ["R-02", "F-02"]
	}
	"D-03": {
		title: "配置の計算（`views/graph/layout.js`）"
		text: """
			API の Scope の一覧と、表し方の選択（`mode: "nest"|"tree"`、`showDone`、`deps: "all"|"wait"|"none"`、`fold`、`focus`）から、箱、枠、まとまり、親子の線の座標と、線を引く依存の組を返す純粋な関数。`layout(scopes, cleanup, opts, gaps)`。

			- 見せる Scope：`showDone` か、終わっていないか、見せる子を持つもの。`focus` があれば、その Scope と子孫だけ。
			- 入れ子：子を持つ Scope を枠、子のない Issue を箱にする。枠の中は、子の段（`showDone` なら `stage.all`、でなければ `stage.open`。`null` は1段目）の列に分け、同じ段の中は `rank` の順に上から並べる。段が1つなら折り返す行（幅 1240px まで）にする。段が6つを超えたら、6列ごとに次の行に折り返す。最上位は、枠を推奨順に縦に重ね、親のない Issue をその後の行に並べる。
			- 木：見せる Scope を、親の後に子を推奨順に並べた字下げの一覧にする（1段32px）。すべて同じ大きさの箱。親子の線は、親の箱の左下から子の左の辺へ。
			- 片付けの候補（`fold` のとき）：同じ入れ物の同じ列の候補を、1つのまとまりにする。まとまりの中の Scope への依存は、まとまりにつなぐ。
			- 依存の組：各 Scope の `blocked_by` の先と自分を、見えている箱、枠、まとまりに写す。同じ組は1本にまとめる。親子の間（片方がもう片方を含む）と、同じまとまりの中は線にしない。`deps` が `wait` なら、待ち先が開いている依存だけ。
			- 寸法：箱 178×88、枠の見出し22、要点の行18、枠の中の余白、列の間44、行の間12、最上位の間28、上の余白は操作の帯の高さ（D-05）。隙間は `gaps[キー]` だけ広げられる。
			- `widen` を隙間のキーに写す `gapFor(axis, a, b)`：2つの障害物の共通の入れ物が、その向きに並べる入れ物なら、その隙間のキーを返す。
			- `G` を作る `graphInput(layout)` と、隙間を広げて最大8回引き直す `routeLayout(scopes, cleanup, opts)` も、このモジュールに置く（DOM なし）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-13", "F-02"]
	}
	"D-04": {
		title: "図の画面（`views/graph.js`、`views/graph.css`、`views/graph/marks.js`）"
		text: """
			- `render(root, ctx)`：最初に骨組みの DOM（図の領域、世界、線の SVG、操作の帯、凡例、要点の欄）を作る。データ（`revision`）、表し方、`focus` が変わったときだけ、D-03 で配置して描き直し、見る位置と倍率と選択を保つ。`dispose()` で文書への登録（`gesturestart` など、`keydown`）を外す。
			- 箱と枠と印は `marks.js` の部品で描く。状態の記号は `core/ui.js` の `stateIcon`。PR の印は `pr.state`、`pr.is_draft`、`pr.checks`、`pr.mergeable` から。
			- 状態の印（`hl`）：Issue の箱の `lane`／`merge` で数え、押すとその箱に `is-hl`、ほかに `is-dim`。選択と状態の印は、後の操作が前の操作を消す。
			- 選択：`api.scope(repository, ID, baseline なし)` を読み、`upstream`、`downstream`、`root_waits` から箱と線の見え方を決める。線は、組 `[待ち先, 待つもの]` のどれかが、選んだ Scope と直接の上流・下流を結べば強く、両端が関係する Scope（選んだもの、その祖先、上流、下流）なら弱く、ほかは淡く。読んでいる間に別の操作があったら結果を捨てる。読めなければ選んだ箱だけを際立たせる。
			- 要点の欄：状態の札（言葉つき）、マージ待ちの札、ID と番号と種類、題名、理由の文、親の道筋（押すとその親を選ぶ）、種類・保証・PR・ブランチ・段・変化の表、枠なら配下の進み具合、「詳しく」（`ctx.navigate`）、GitHub のリンク、枠なら「この範囲に絞る」。片付けの候補のまとまりを押したときは、候補の一覧と理由。
			- 範囲の絞り込みは `ctx.navigate(?focus=ID)`。絞っているときは、帯に道筋と「全体へ戻る」。
			- 操作：D-05。PC のダブルクリックで `ctx.navigate(scope の path)`。幅 640px 以下では、同じ箱の2回目のタップで移る。
			- 線の検査：`edgeAudit()` を書き出し、今の DOM の矩形で `audit` を走らせる（ブラウザーでの確かめ用。`window.specdockEdgeAudit` にも置く）。
			"""
		satisfies: ["R-01", "R-03", "R-04", "R-06", "R-07", "R-09", "R-10", "R-12", "F-01", "F-02"]
	}
	"D-05": {
		title: "拡大・縮小・移動と指の操作"
		text: """
			- 図の領域に `touch-action: none`。Pointer Events で、1本はドラッグ（6px を超えたら移動。押した箱を選ばない）、2本は2点の間の距離の比で拡大・縮小し、中点の移動で動かす。倍率は 0.12〜2。
			- `document` に `gesturestart`、`gesturechange`、`gestureend` を `passive: false` で登録し、`preventDefault` する（画面を離れるときに外す）。
			- ホイール：Ctrl か Command つきは拡大・縮小、なしは移動。道具：縮小、倍率（押すと100%）、拡大、全体を収める。
			- 操作の帯の高さを測り、開いたときと全体を収めるときの上の位置を、帯の下端より下にする。
			"""
		satisfies: ["R-08"]
	}
	"D-06": {
		title: "時間の軸（`views/timeline.js`、`views/timeline.css`、`views/timeline/series.js`）"
		text: """
			- `series.js`：`mergeWeeks(weeksByKind, kinds)`（選んだ種類の週の累計を、週の始まりで合わせて足す。ある種類の最初の週より前は0、最後の週より後は最後の値）、`groupEvents(events, scopes)`（日ごとに分け、題名を引く）。純粋な関数。
			- 画面：4つの数、種類の選択（Initiative、Epic、Issue。既定はすべて）、累計の図（SVG。点を指すと縦の線とその週の数）、最近の動き（日ごとの見出し、出来事の記号と文、時刻。押すと詳しい画面）。PR の出来事の番号は PR の番号。
			- 構造がないときは理由の文だけを出す。
			"""
		satisfies: ["R-11", "R-12", "F-01"]
	}
	"D-07": {
		title: "線の検査と純粋な関数のテスト"
		text: """
			- `tests/unit/presentation/test_dashboard_graph_js.py` が、見本の構造から `structure_document` の JSON を作り、node で `tests/js/dashboard_graph_check.mjs` を走らせ、結果の JSON を確かめる。
			- 見本：`tests/fixtures/issue532/spec-dock-snapshot.json`（spec-dock の構造のスナップショット、2026-11-04）と、生成した250件の構造（Initiative 2、Epic 18、Issue 230、依存あり）。
			- 組み合わせ：表し方（入れ子、木）× 終わったもの（隠す、出す）× 線（すべて、待っているもの）× 片付けの候補（畳む、開く）と、各 Epic への絞り込み。すべてで `audit` の6つの数と `trunkOverlaps` が0。
			- node がないとき：環境変数 `CI` があれば失敗、なければ理由つきで skip。
			"""
		satisfies: ["R-02", "R-05", "R-11"]
	}
}

compatibility: "構造の API に項目を足すだけで、既存の項目は変えない（API の形は契約ではない。iss-00529 D-06）。骨組み、ほかの画面、配布資産の文書、`static-inventory.json` は変えない。"
risks: [
	"箱の高さを固定するので、題名が長いと2行で切れる。全文は要点の欄と `title` の吹き出しで読める。",
	"Safari の実機での指の操作は、この Issue では確かめない（#534 で利用者に頼む）。",
	"保証レベルとブランチは、統括が値を入れるまで出ない。",
]
