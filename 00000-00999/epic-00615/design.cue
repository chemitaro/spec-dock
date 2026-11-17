package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"親を id に解くのは orca-web の1か所、線の端（印の位置）を決めるのは SpecDock の配置の計算の1か所にする（DOM を正本にしない）",
	"稼働の印の並びは orca-web の部品の `buildMarks` の1か所で決め、SpecDock は押した印の対応と印の位置を、その並びから求める",
	"線の計算は純粋な関数1つにまとめ、リポジトリの構造の図と『横断の構造』の両方が同じ関数を使う",
	"組がないときは、今の図の HTML と見え方を変えない",
]

current: """
	- orca-web の要約（`GET /api/worktrees/summary`、`orca-web.worktree-summary/v1`）は、エージェントが1人以上いる worktree ごとに `id`、`path`、`branch`、`project {id, name}`、`issue`、`counts`、`agents[]`（`id`、`mark`、`workingMode`、`agentType`、`since`、`detail`（`/embed/agent?id=…`）など）を返す。親の項目と main の印はない。orca-web の状態の文書の各エージェントは `paneKey` と `parentPaneKey`、各 worktree は `isMainWorktree` を持つ。
	- SpecDock の画面は、殻の1つの読み手（`core/orca.js` の `createOrca`）で orca-web の部品（`/embed/agent-marks.js`）を読み、その `watchWorktreeSummary` で要約を 10 秒ごとに受ける。`orca.summary()` が今の要約、`orca.subscribe` が知らせ。Scope と worktree の対応は `core/orca_match.js` の `matchWorktrees`（構造の `worktrees.paths` と各 Scope の `worktrees[]` のパスとブランチ）。
	- 構造の図（`views/graph.js`）は、`layout.js` の座標で、世界（`.gx-world`、`translate(tx, ty) scale(s)`）の中に、木の線の SVG（`.gx-tree`）→ 枠 → 箱 → 塊 → 依存の線の SVG（`.gx-edges`）の順に置く。稼働の印は `_shared/orca_marks.js` の `paintOrcaMarks` が、箱と枠の印の置き場（`[data-orca-scope]`）に orca-web の `renderAgentMarks` で描く。印は `max` を超えると `+N` に畳まれる。
	- 横の欄は `_shared/panel.js` の `createScopePanel`。片付けの候補の一覧は、同じ欄（aside）を Scope 以外の中身に使っている前例。エージェントのタブ（`_shared/agents_tab.js`）は、orca-web の `/embed/agent` を決まった sandbox の iframe で開く（`agentFrame`、`AGENT_SANDBOX`）。
	- iss-00614（epic-00612）は、箱・枠・塊・線の HTML を `views/graph/draw.js` に取り出し、『横断の構造』（`views/allgraph.js`、組み立ては `views/allgraph/compose.js`）を作る。リポジトリの枠ごとに、中の構造の図の原点 `body {x, y}` がある。
	- 改訂の時点（2026-11-17）の事実：
	  - orca-web の部品は `buildMarks(worktree, {now, max})`（`web/embed/agent-marks-view.js`、書き出し済み）で並びを決め、`renderAgentMarks` がその順に `.orca-mark` を描く（先頭から上限 − 1 人、残りは `.orca-mark--more` の『+N』）。並びは状態の重さ（`ORDER`）の順、同じなら要約の順。各印の view は `id` と `detail` を持つ。`onSelect` を渡すと印がボタンになる。印の要素に `data-agent-id` はまだない（iss-00043 が足す）。
	  - orca-web の状態の各エージェントは `stateStartedAt`（今の状態になった時刻）を持ち、要約の `elapsedFrom` はそこから来る。エージェントの開始の時刻の項目はない。
	  - SpecDock の `paintOrcaMarks` は、置き場ごとに `buildMarks` の結果から鍵（`marksKey`）を作り、変わったときだけ `renderAgentMarks` を呼ぶ。
	  - 印を押したときは、構造の図（`graph.js` の `.sd-orca` の押し）、ボード（`board.js` の `onCardClick`）、横の欄の見出し（`panel.js` の `.sd-orca`）のどれも、Scope を選んで `preferTab("agents")` を呼ぶだけで、押したエージェントを渡さない。エージェントのタブは、欄の選び（`param("agent")`）か、そのページの記憶（`mem.last`）でエージェントを選ぶ（`agents_tab.js` の `agentsState`）。
	  - worktree の印 `M.wtMark(branch)` は、Issue の箱（`boxHtml` の箱の枝）にだけ出る。入れ子の枠の見出し（`frameHtml`）と木の枠の箱にはない。構造の API の `branch` は Scope の種類を問わず、ブランチの最後の区切りが Scope の ID のもの（`branch_names_scope`）。
	  - ボードの札の稼働の印は、札の情報の行（`parts.js` の `meta`）に、ほかの印と並んで置かれる（上限 4）。
	  - iss-00620（epic-00573、進行中）は、構造の図の箱と枠の印を上限なしにし、ほかの印の下の専用の行 `.gx-agents`（Issue の箱・木の枠の箱は `.gx-marks` の下、入れ子の枠は `.gx-fh` の最後の子として題名の行の下。中が空なら隠れる）に左から詰めて折り返し、印の測った幅（`{items, gap}`）と行の規則（`markRows`・`nodeMarkRows`、`MARK_ROW`、`MARK_INSET`）で、配置が箱・枠を縦に伸ばす。印の行の数が変わったときだけ配置をやり直す（iss-00620 R-06）。
	  - 配置の箱の間の余白（`layout.js` の `BASE`）：同じ段の中の行の間 12px、包みの行と列の間 14px、段（列）の間 44px、木の行の間 14px。
	"""

target: """
	- orca-web：要約の各エージェントに `parent`、各 worktree に `main`、印の要素に `data-agent-id`（iss-00043、orca-web のリポジトリ）。
	- orca-web（iss-00043）：あわせて、要約の各エージェントに `startedAt` を足し、`buildMarks` の並びを指揮の関係の順（R-14）にする。
	- SpecDock：枠の worktree の印、押した印のエージェントを開く口、ボードの札の専用の行（iss-00621）。純粋な計算 `views/graph/command.js`（つながり・居場所・帯・印の位置・端と曲線と弧）、構造の図の指揮の層と帯（iss-00616）、『横断の構造』への適用（iss-00617）。
	"""

design: {
	"D-01": {
		title: "前提の契約：orca-web の要約の追加の項目（iss-00043 が持つ）"
		text: """
			SpecDock が読むと決める形（版 `orca-web.worktree-summary/v1` のまま、項目を足すだけ）：

			```jsonc
			worktrees[]: {
			  main: true | false | null,          // Orca の isMainWorktree。分からなければ null
			  agents[]: {
			    parent: null                       // 親がない（Orca が親を出していない）
			          | {id: string | null,        // 親のエージェントの id（同じ id の空間）。見えなければ null
			             worktreeId: string | null},// 親のいる worktree（同じ要約の worktrees[].id）
			    startedAt: string | null           // 並び（R-14）の『新しい』の時刻（ISO 8601）。下の決め方
			  }
			}
			```

			- orca-web は、子の `parentPaneKey` と同じ `paneKey` を持つエージェントを親とし、その `id` と `worktreeId` を返す（構造化 Chat の id の合併の後の id）。`parentPaneKey` があるのに親が見つからなければ `{id: null, worktreeId: null}`。
			- 印の要素（`renderAgentMarks` が描く各エージェントの要素）に `data-agent-id`（エージェントの id）を足す。`+N` に畳まれたエージェントには要素がない。
			- `startedAt`：Orca がそのエージェント（pane・タブ）の開始の時刻を出していればそれ。なければ、orca-web がそのエージェントの id を初めて見たときの `stateStartedAt`（orca-web の中で覚え、状態が変わっても動かさない。orca-web を立て直すと、その時の値から覚え直す）。どちらもなければ null。どの Orca の項目が開始の時刻に当たるかは iss-00043 の設計で、Orca の実物で確かめて決める。
			- `buildMarks` の並び（R-14）：同じ worktree の `agents` について、
			  1. 関係あり ＝ その worktree の中に、`parent.id` がその id を指す子がいるか、自分の `parent.id` が同じ worktree の別のエージェントを指すもの。ほかは関係なし。
			  2. 関係なしを `startedAt` の新しい順（null は最後）、同じなら id の順に並べる。
			  3. 関係ありを、その worktree の中に親のいないもの（根）から深さ優先でたどる（親 → 子 → 孫）。根どうしと兄弟は `startedAt` の新しい順（null は最後）、同じなら id の順。輪（親子が輪になる）は、たどった順で1回ずつ出し、残りを関係なしの規則で後ろに足す。
			  4. 関係なし → 関係ありの順に並べ、上限を越えれば、今どおり先頭から上限 − 1 人と『+N』。
			  `parent` や `startedAt` がない（古い orca-web の要約）なら、全員を関係なしとし、`startedAt` の代わりに要約の順で並べる。`ORDER`（状態の重さの順）は並びに使わない。
			- SpecDock は、項目がない（古い orca-web）、形が違う、を F-01・F-03 として受け、要約の版を見て止まらない（版は変わらない）。SpecDock は印を並べ替えず、`buildMarks` の並びをそのまま使う（D-09）。

			この Epic の SpecDock の Issue は、この形を合成の要約で確かめて先に進められる。実データでの確かめは、iss-00043 が main に入った後に行う。
			"""
		satisfies: ["R-01", "R-14", "F-01"]
	}
	"D-02": {
		title: "指揮の線の純粋な計算（views/graph/command.js）"
		text: """
			DOM・ネットワーク・時計に触れないモジュール。入力と出力（名前は Issue の設計で決めてよいが、役割は次のとおり）：

			1. `commandPairs(summary)` → 組の並び `[{parent: AgentRef, child: AgentRef}]`。`AgentRef` は `{id, mark, workingMode, agentType, detail, worktree}`（worktree は要約の worktree の写し）。
			   - 要約の全エージェントを id で引く表を作り、各子の `parent.id` が表にあり、自分でなければ組にする（R-01、F-02、F-03）。`parent` の形が違えば飛ばす。同じ（親, 子）は1組。並びは子の id の順。
			   - `orca.status()` が ok でないか、要約が無効なら空（F-01）。
			2. `placeAgents(pairs, {structure, nodes, groups, ix, isOwnWorktree})` → 各端の居場所 `{kind: "mark", node, agent} | {kind: "group", id} | {kind: "frame", id} | {kind: "band", item, agent}`（R-02）。
			   - worktree → Scope は今の `matchWorktrees` と同じ対応（逆の索引を足す。Scope の種類を問わない）。Scope が `nodes` にあれば、その箱・枠の、そのエージェントの印（`mark`）。畳んだ塊（`groups` の members）に入っていればその塊（`group`）、なければ `ix.ancestors` をたどって最初に `nodes` にある祖先の枠（`frame`。その枠の印ではなく枠の縁）。どれもなければ帯。
			   - 帯の項目は worktree ごと：`{key: worktree.id, label, own: bool, agents: [AgentRef]}`。項目の中の `agents` は、その worktree の `buildMarks` の並び（D-01）から、帯に出すものだけを取り出した順（描く側が並びを渡す）。札は、このリポジトリの worktree（`matchWorktrees` と同じ判定：構造の `worktrees.paths` にパスがある、または同じ project）なら `main === true` で「main のチェックアウト」、ほかはブランチ名。ほかのリポジトリなら「<project.name> · <branch>」。項目が null のときは F-04 の札。並びは、このリポジトリの main のチェックアウト → このリポジトリのほか（ブランチ名の順）→ ほかのリポジトリ（札の順）。帯に出すのは、組の端だけ（R-03）。
			3. `commandModel({pairs, places, layout, marks, edges, band})` → `{band: {h, items: [{key, label, x, y, w, h, agents: [{id, x, y, w, h}]}]}, links: [{parent, child, state, kind, d, from, to, stubs, mark}], ripples: [{agent, x, y}], audit, width, height}`。
			   - `marks`：iss-00620 が測った箱・枠ごとの印の幅 `{items, gap}` に、iss-00621 が足す `ids`（各印のエージェントの id、描いた順。D-09）を加えたもの（Scope の id → 値）。`edges`：routeLayout の依存の線の道（弧の検査に使う）。
			   - 帯の寸法：1行、項目は札＋印の数で幅を決め、左から並べる（折り返さない。R-03）。帯の高さは項目が1つ以上で定数 `BAND.h`、なければ0。全体の座標＝配置の座標＋(0, 帯の高さ)。`width` は配置の幅と帯の幅の大きいほう。
			   - 端（R-04）：`mark` なら、D-10 の `markSpots` が返すそのエージェントの印の矩形。帯なら、その項目の中のそのエージェントの印の矩形。`group`・`frame` なら、その塊・枠の上の縁の中央（同じ端から出る線は、一定の間隔でずらす。枠が相手の端を中に含むときも上の縁）。印の位置が分からなければ F-05（上の縁の中央）。
			   - 出口と道（iss-00648 が置き換えた）：どの端も、印の中央の真上の、箱・入れ子の枠・帯の項目の上の縁（印のない端は上の縁の中央）から上へ出て、上から入る。箱の中には線を引かない（`stubs` は空）。道（`kind: "curve"`）は、上にふくらむ三次ベジェの弧（ホップ）で、高さは両端の水平の距離と高さの差から下限と上限の間で決める（数と式は iss-00648 の設計の `HOP`・`hop`）。相手が箱の上にあるときは、弧が箱の後ろ（線の本体の層は箱の下）を通る。子の端に下向きの矢じり、印のある子は印の縁を指揮の色にする（`mark`）。
			   - 両端が同じ箱・枠（`mark` の `node` が同じ）か帯の同じ項目なら、D-10 の弧（`kind: "arc"`）。両端が同じ塊か同じ祖先の枠（どちらにも印がない）なら、線を作らない（R-04）。
			   - `ripples`：組の親の印（帯なら帯の印）ごとに1つ、その印の中央（端の層に描く）。
			   - `state`：子の `mark` が working なら `flow`、done なら `done`、そのほか（waiting、blocked、sleeping、unknown）は `wait`（R-05）。
			   - `audit`：D-10 の `cmdAudit`（弧と箱・枠・塊の重なり、弧と依存の線の平行な重なり、浅くした弧の数）。
			4. 鍵：（要約の文書、配置の結果、印の測った幅と並び、帯の寸法の定数）が同じなら、前の結果を返す（R-09）。

			   - リポジトリの構造の図では、両端ともほかのリポジトリにいる組を落とす（R-02。`isOwnWorktree` で判定）。『横断の構造』（D-06）では落とさない。

			node のテスト：報告書の実データの形の合成の入力（5組、別のリポジトリの統括、同じ worktree の親子、main のチェックアウトの中の親子）、両端ともほかのリポジトリの組、Epic の worktree の統括 → 枠の中の Issue の子、隠れた同じ Epic の中の Issue の子（枠の上の縁、iss-00648）、同じ行・違う行の同じ箱の親子、帯の項目の中の並び（`buildMarks` の並びの部分の列）、隠れた Issue、畳んだ塊、印の位置が分からない（F-05）、親が見えない、形の違う親、自分を指す、輪、`main` がない、`branch` が null、`project` が null、構造の worktree の一覧が読めない（F-01）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-09", "F-01", "F-02", "F-03", "F-04", "F-05"]
	}
	"D-03": {
		title: "構造の図の指揮の層と帯（描画）"
		text: """
			- 世界の中の並び：木の線 → 枠 → **指揮の層**（`<div class="gx-cmd" aria-hidden="true">`、線ごとの小さな SVG の線の本体と下地の光。iss-00646）→ 箱 → 塊 → **指揮の端の層**（`<div class="gx-cmd-top" aria-hidden="true">`、子の端の矢じり・受けた印の縁・波紋。帯の印の縁と帯の親の波紋は帯の層の入れ物 `.gx-band-cr`。iss-00648）→ 依存の線。どちらの層も `pointer-events: none`、`overflow: visible`。帯（`<div class="gx-band">`）は世界のいちばん上（y が 0 から帯の高さ）。組がなければ、2つの層と帯の要素を置かない（R-03 の3つ目、制約の4つ目）。
			- 配置の座標を帯の高さだけ下げる。今の `layout` の座標で置く枠・箱・塊・依存の線は、それらを包む1つの入れ物を帯の高さだけ下げるか、同じ量を足して置く（どちらかは Issue で決める。依存の線と edgeAudit の座標の測り方は変えない）。世界の幅と高さ、初めの見え方と『収める』の外接の四角に帯を含める（R-08）。
			- 帯が出たり消えたりして帯の高さが変わったら、見る位置 `ty` を、変わった高さ × 倍率だけ補い、箱が画面の上で動かないようにする（R-09）。
			- 帯の項目：札（文字）と、各エージェントの印。印は orca-web の `renderAgentMarks` に、そのエージェント1人だけの worktree を渡して描く。各エージェントを `<button type="button" data-cmd-agent="<id>">` で包み、押せてキーボードで選べる（R-07）。
			- 線：各組に、下地の光の道（太く薄い）と本体の道の2本（弧も同じ）。`data-state` で `flow`・`wait`・`done` を分ける。箱の中には線を引かず、子の端の矢じりと受けた印の縁を、同じ `data-state` で端の層（帯の印の縁は帯の層の入れ物 `.gx-band-cr`）に描く（iss-00648）。親の印の中央に波紋（HTML の輪を2つ、ずらして広げる。iss-00646）。同じ親の波紋は1か所に1つ。
			- 稼働の印を描く今の関数（`paintOrca`）の中で、印を描き、iss-00620 の測り（`checkRows`）が済んだ後に、線と帯を描き直す。鍵が同じなら何もしない（R-09）。iss-00620 の測りで配置をやり直すときは、その後の描き直しで線も描き直す。
			"""
		satisfies: ["R-03", "R-04", "R-05", "R-08", "R-09", "F-05"]
	}
	"D-04": {
		title: "指揮の色、動き、凡例"
		text: """
			- 色の札：`--sd-cmd`（線の本体）と `--sd-cmd-glow`（下地の光）を、`app.css` の明るいテーマ（`:root`）、暗いテーマ（`prefers-color-scheme: dark` の中）、明示の暗いテーマ（`[data-theme="dark"]`）の3か所に定める。色相は 54〜58°（`--sd-blocked` の明 約39°・暗 約43.4° より10°以上、黄の側）。明るいテーマは、図の背景（`--ds-bg-2`）と 3:1 以上の濃い黄（#a89200 は約 2.9:1 で足りないので、それより濃い黄）に、太く薄い光（同じ色相の明るい黄の半透明）を下に重ねる。暗いテーマは明るいレモン（例 #ffec4d の近く）。値は Issue で、図の背景とのコントラストと色相の差を計算して決める（R-06）。
			- 動き（`graph.css`、iss-00646 が置き換えた）：`flow` は丸い点の破線（`stroke-linecap: round`、`stroke-dasharray`）を、点を 2px ずつずらした止めた絵4枚にして、合成スレッドで動く `opacity` の切り替え（0.05秒ごと）で見せ、どの線も一様に 40px/秒で流す。線は線ごとの外接の四角の小さな SVG に描く。`wait` は止まった点線。`done` は薄い（opacity を下げた）動かない線。波紋は HTML の輪の `transform: scale` と `opacity` で 2.4 秒ごとに2つの輪をずらして出す。図を動かす間・画面の外・裏では止める（R-05。詳細は iss-00646 の設計）。
			- 減らす設定：`@media (prefers-reduced-motion: reduce)` で、指揮の層のアニメーションを止め（`animation: none`）、波紋の2つ目の輪を隠して、1つの輪を動かさずに出す。今の全体の規則（`app.css` の時間を 0.01ms にする規則）だけに頼らない（それでは最後の形が残るとは限らないため）（R-05）。
			- 凡例：構造の図の凡例（`renderLegend`）の『そのほか』に、指揮の線の見本と波紋の見本で「指揮（親 → 子）」の行を足す。『横断の構造』の凡例も同じ行を持つ（R-06）。
			"""
		satisfies: ["R-05", "R-06"]
	}
	"D-05": {
		title: "印を押したときの線の目立たせと、帯のエージェントの詳細の欄のチャット"
		text: """
			- 選びの状態は、Scope の選び（`V.sel`）と別に、指揮の選び（選んだエージェントの id）を1つ持つ。
			  - 帯のエージェントを押すと、Scope の選びを解いて指揮の選びにし、下の詳細の欄を開く。
			  - 箱・枠の見出しの稼働の印を押すと、D-09 で押したエージェントを求め、その Scope を選び（横の欄のエージェントのタブでそのエージェントを選ぶ）、同時に指揮の選びをそのエージェントにする。結べなかった（F-06）ときは、指揮の選びを解く。
			  - もう一度押す（帯）、欄を閉じる、Esc、図の空いたところ、別の箱を印でないところで選ぶ、で指揮の選びを解く（R-07）。
			- 目立たせ：指揮の層に `has-cmd-sel`、そのエージェントが親か子の線に `is-cmd-hl`、ほかの線に `is-cmd-off`。帯の項目の押したボタンに `aria-pressed="true"`。
			- 詳細の欄：片付けの候補の一覧と同じように、構造の図の横の欄（aside）を、Scope の欄を隠してエージェントの中身に使う。見出しに印・種類・札、閉じるボタン。中身はエージェントのタブと同じ `agentFrame(origin, agent, theme)` と `AGENT_SANDBOX` の iframe（要約の `detail` の `/embed/agent?id=…`）。スマホでは今の下からのシート。欄の中身とページの URL は変えない（覚えない）。
			- 押した後に、そのエージェントが要約から消えたら、指揮の選びを解く。帯のエージェントの詳細の欄なら、欄も閉じる（Scope の欄は、エージェントのタブの今の『いなくなった』の扱いのまま）。
			"""
		satisfies: ["R-07"]
	}
	"D-06": {
		title: "『横断の構造』への適用"
		text: """
			iss-00614 の `compose` と `allgraph.js` に足す（その Issue の後の実際の形に合わせる）。

			- リポジトリごとの対応：要約の各 worktree を、そのパスかブランチ・project で対応するリポジトリ（各リポジトリの構造の `worktrees.paths` と `matchWorktrees`）に割り当てる。どれにも当たらなければ「ほかの場所」。
			- 居場所：`placeAgents` を、そのエージェントのリポジトリの構造・配置で呼ぶ。帯に決まったものは、そのリポジトリの枠の帯へ（札はそのリポジトリの中の札）。「ほかの場所」のものは、全体の帯「ほかの場所」へ（札は「<project.name> · <branch>」）（R-10）。
			- 組み立て：`compose` の `sizes` に各リポジトリの帯の高さ `band` を足し、見出しと body の間に入れる。全体のいちばん上に、「ほかの場所」の帯の高さを足す。『これから』で、`shown` が0で子の枠も出ないリポジトリでも、そのリポジトリの帯に**組の親**がいれば、見出しと帯だけの入れ物として出す（R-11。epic-00612 R-06 のただ1つの例外）。帯に子だけがいるときは枠を出さず、その子を全体の帯「ほかの場所」に置く。親がいなくなれば、今の規則どおり出さない。
			- 端の座標：全体の世界の座標＝そのリポジトリの body の原点＋そのリポジトリの配置の座標（帯は、その枠の帯の位置）。リポジトリをまたぐ組も、全体の世界の1枚の指揮の層に描く。
			- 重なり：リポジトリの枠（section）は重なりの文脈を作らないようにし、z-index で、枠（リポジトリと Initiative）→ 指揮の層 → 箱 → 依存の線の順にする。
			- 帯の高さが変わったら、そのリポジトリより後ろの枠の位置が変わるので、`compose` を計算し直す（各リポジトリの中の配置は計算し直さない）。見る位置の補い（D-03）は、画面のいちばん上に見えているリポジトリの枠を基準にし、その枠とその中の箱が画面の上で動かないようにする。それより下の枠は動いてよい（R-10）。
			- 組は全部出す（両端ともほかのリポジトリの組も、どちらかの枠か「ほかの場所」に端がある）。
			- 印の位置（D-10 の `markSpots`）は、各リポジトリの配置と、そのリポジトリの枠の中で測った印の幅と並び（iss-00614 の後の形で、iss-00620 の測りがリポジトリごとにどう持たれるか）で求め、全体の世界の座標に直す。同じ箱の弧（D-10）も同じ。
			- 選び・色・動き・凡例は D-03〜D-05 と同じ部品を使う。印を押したときの横の欄の動き（R-13）は iss-00621 が作る。
			"""
		satisfies: ["R-10", "R-11"]
	}
	"D-07": {
		title: "確かめのしかた"
		text: """
			- 純粋な計算：node のテスト（D-02 の場合）。
			- 画面：合成の要約を返す試しの orca-web の口（部品は orca-web の配る `agent-marks.js` の写しか、iss-00043 の後の本物）と、この PC の状態の置き場の写しで、`dashboard serve --offline --state-root` を別のポートで立て、headless Chrome で 1440・1000・390 × 明・暗の写しを撮り、edgeAudit の違反、ブラウザーのエラー、層の並び、`pointer-events`、減らす設定の見え方を数える。常駐のダッシュボードと Orca には触れない（epic-00612 D-07 と同じ）。合成の値と写しは Workbench に置き、公開のリポジトリに実際のパスを入れない。
			- 実データ：iss-00043 が main に入り、手元の orca-web が新しい要約を返すようになった後に、手元の Orca の実際の親子で、線と帯が出ることを確かめる（各 SpecDock の Issue の最後、と統括の最後の確かめ）。
			- Epic の worktree の実例（iss-00621・iss-00616）：統括が用意する試しの送り先（作業中の Epic の worktree にエージェントがいる状態）で、枠の見出しの worktree の印と稼働の印（R-12）、その印を押したときのチャット（R-13）、その Epic のエージェントから枠の中の Issue の箱の印への線（R-04）を写す。
			- 印の位置の検査：実機で、`markSpots` の矩形と、描いた `.orca-mark` の箱の中の offset（`offsetLeft`・`offsetTop` を箱の要素まで足したもの。拡大の影響を受けない）との差が 1px 以内であることを数える（R-04 の3つ目。検査の関数は iss-00616 が足し、写しの確かめだけに使う）。
			"""
		satisfies: ["R-08", "R-10", "R-12", "R-13"]
	}
	"D-08": {
		title: "Epic・Initiative の枠の worktree の印と、ボードの札の専用の行（iss-00621）"
		text: """
			- 入れ子の枠の見出し（`frameHtml` の `.gx-fh`）：題名（`.gx-fttl`）の後、稼働の印の専用の行（iss-00620 の `.gx-agents`、`.gx-fh` の最後の子）の前に `M.wtMark(s.state === "doing" ? s.branch : null)` を置き、見出しの行（状態の印・Initiative の印・ID・題名）に並べる。稼働の印の専用の行には入れない。iss-00620 の行の数は稼働の印の幅（`{items, gap}`）と枠の中の幅だけで決まり、見出しの行の幅を数えないので、worktree の印を足しても行の数と配置は変わらない（題名は今のとおり縮む）。
			- 木の枠の箱（`boxHtml` の `frame` の枝）：Issue の箱と同じ位置（保証レベル・片付けの候補の後、人のタスクの前）に `M.wtMark(...)` を足す。
			- 『横断の構造』は、iss-00614 が取り出した `views/graph/draw.js` の同じ部品を通るので、同じ変更で出る（iss-00621 は iss-00614 の後に作る）。
			- 読み上げ：枠の見出しの aria-label は今のまま（worktree の印は自分の aria-label「worktree <branch>」を持つ）。
			- ボードの札（`parts.js` の札の `meta`）：orca-web とつながっているとき（今 `orcaSlot` を足している条件）、稼働の印の置き場（`orcaSlot(scope.id, 4)`）を `meta` の行から外し、その下の専用の行の要素（例 `<div class="sd-card-agents">`）に包んで置く。中に `.orca-mark` がなければ、iss-00620 と同じく `:not(:has(.orca-mark))` で `display: none` にし、高さを取らない。orca-web とつながっていないときは、今どおり置き場も行も出さない。上限 4 と『+N』、札の幅、ボードの並び順は変えない。色は足さない（デザインシステムの変数だけ）。
			"""
		satisfies: ["R-12", "R-15"]
	}
	"D-09": {
		title: "押した印のエージェントを求め、横の欄のエージェントのタブをそのエージェントで開く（iss-00621）"
		text: """
			- 描いた並びの記録：`paintOrcaMarks` は、置き場ごとに、描くときに使った `buildMarks` の結果の `marks[].id`（描いた順）を記録する（置き場の要素への WeakMap か `data-orca-ids`。どちらかは Issue で決める）。部品の `renderAgentMarks` は同じ `buildMarks` の順に `.orca-mark` を描くので、記録の i 番目と、置き場の中の i 番目の `.orca-mark`（`--more` を除く）が同じエージェントになる。
			- 押した印のエージェント `markAgentAt(slot, target)`（`_shared/orca_marks.js`）：押した要素の最も近い `.orca-mark` を取り、`--more` なら null。`data-agent-id` があればそれ（iss-00043 の後）。なければ、置き場の中の `.orca-mark`（`--more` を除く）の何番目かを数え、記録のその番目の id。記録がない、数が違う、なら null（F-06）。
			- 横の欄の口：`createScopePanel` の戻り値に `openAgent(agentId)` を足す。中で、エージェントのタブを選び（`preferTab("agents")` と同じ）、欄の選び（`params` の `agent`）を `agentId` にし、エージェントの記憶をその人の選びにする（`forgetGone(mem, agentId)` と同じ意味。エージェントのタブで項目を押したときと同じ）。`agentId` が null なら、今の `preferTab("agents")` だけ。
			- 呼ぶところ：構造の図（`graph.js` の `.sd-orca` の押し：`select(id)` の後に `V.pn?.openAgent(markAgentAt(...))`）、ボード（`board.js` の `onCardClick`）、横の欄の見出し（`panel.js` の `.sd-orca`）、『横断の構造』（iss-00614 の後の `allgraph.js` の同じ押し）。帯のエージェント（iss-00616）は Scope がないので D-05 の詳細の欄。
			- スマホ：今の押しの扱い（iss-00602 の二度目の指）を変えず、印を押したときに `openAgent` を呼ぶ。
			- 部品の `onSelect` は使わない（印がボタンになり、箱の `role="button"` の中にボタンが入れ子になる）。印の要素は今のまま絵（`role="img"`）。
			- この口と記録を、iss-00616 の印の位置（D-10 の `ids`）も使う。
			"""
		satisfies: ["R-13", "R-14", "F-06"]
	}
	"D-10": {
		title: "印の位置（markSpots）と、同じ箱の弧（iss-00616）"
		text: """
			- `markSpots(node, m)`（`views/graph/layout.js`、iss-00620 の `markRows` の隣。DOM なし）：layout の node（box・tframe・frame）と、測った `m = {items, gap, ids}` から、各印の矩形 `[{id, x, y, w, h}]`（node の左上からの座標）を返す。
			  - 詰め方は、iss-00620 の `markRows` と同じ左から詰める規則を、同じ詰め（各印の行と x）から求める（規則を2か所に写さない。`markRows` の内部の詰めを関数に分けて共有し、行の数と各印の位置の両方をそこから出す）。
			  - 行の位置：箱では、専用の行は箱の最後の行（箱の下の内側の縁から数える）。入れ子の枠では、見出しの中の題名の行の下（枠の上の縁から数える）。`MARK_ROW`、印の高さ（部品の sm の 16px）、箱の内側の余白は、iss-00620 が layout.js に置く CSS の写しの定数（`MARK_ROW`・`MARK_INSET` と同じ所）を使う。足す定数（印の高さ、専用の行の位置など）は同じ所に置き、`graph.css` とコメントで互いを指す。
			  - 印の位置が分からない（`m` がない、`ids` の数と `items` の数が違う）なら null（F-05）。
			- 同じ箱の弧（R-04、iss-00648 が置き換えた）：両端の印の矩形 A（親）と B（子）が同じ node（帯なら同じ項目）にあるとき、その上の縁の、A と B の中央の真上の2点（12px より近ければ 12px 離す）から上へ出て戻る、上にふくらむ三次ベジェの弧にする。高さは 18px。上の余白（縁から、弧の幅の範囲で向かい合ういちばん近い箱・枠・塊・帯の項目の縁、入れ子の枠の内側の縁まで）から 3px を引いた値が 18 より小さければ、その値（8px 以上）に下げ、`cmdAudit.crowded` に数える。弧の頂点が依存の線の水平な区間と平行に重ならないよう、高さを上限から 8px まで下げながら、頂点（弧の幅の中央の半分）が横の区間から 3px 以上離れる最も高い値を選び、どの高さでも離れなければ上限で描いて `cmdAudit.edgeOverlaps` に数える（脚が縦に横切るのは数えない）。数と式は iss-00648 の設計の `HOP`・`sameHop`。
			- 配置（余白）は広げない（R-09。要約の変化で配置をやり直さない）。今の配置の行の間の余白（14px）では、弧は 11px に下がる。
			- `cmdAudit`：`{boxOverlaps, edgeOverlaps, crowded}`。`boxOverlaps` は弧（ふくらみの外接の四角）が、自分の箱以外の箱・枠（自分を入れる祖先の枠の内側を除く）・塊と重なる数。`edgeOverlaps` は弧の頂点付近が依存の線の横の区間と ±3px 以内に平行に重なる数（iss-00648）。合成の入力の受け入れでは、`boxOverlaps` と `edgeOverlaps` が0。実機の写しでも数えて report.md に残す。
			"""
		satisfies: ["R-04", "F-05"]
	}
}

compatibility: """
	orca-web の要約は項目を足すだけ（版を変えない）で、古い SpecDock はそれを読まない。SpecDock は古い orca-web（項目がない）では線と帯を出さない（F-01）。
	組がないとき、構造の図と『横断の構造』の HTML と見え方は今のまま。PR を戻すと、線と帯と色の札がなくなる。保存（localStorage）は足さない。
	"""

risks: [
	"`parentPaneKey` は Orca の CLI の行の項目で、公開の契約として文書になっていない。Orca の版で形が変わりうる。orca-web の読む口の1か所で吸収し、SpecDock は要約の `parent` だけを読む",
	"帯を足すと、構造の図の座標の原点が帯の高さだけずれる。依存の線、edgeAudit、選んだ箱を欄の上に保つ動き（`keepAbovePanel`）、初めの見え方が、ずれを数え損ねうる。組のあるときとないときの両方で、今のテストと写しで確かめる",
	"明るいテーマで、黄の線が白地と、止められている箱（琥珀の塗りと枠）の近くで見えにくい・紛らわしい。コントラストを計算で確かめ、写しで本人の確かめを受ける",
	"『横断の構造』は iss-00614 の形に足すので、その Issue の実装で名前や寸法が設計（epic-00612 D-04〜D-07）から変わっていれば、iss-00617 の設計を実際の形に合わせる",
	"iss-00614 の『新しい色を足さない』を確かめるテストがあれば、指揮の色の札だけを許すように、iss-00616 で確かめる中身を明示して直す（ほかの新しい色は今までどおり禁じる）",
]
