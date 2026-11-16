package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"親を id に解くのは orca-web の1か所、線の端を決めるのは SpecDock の配置の計算の1か所にする（DOM を正本にしない）",
	"線の計算は純粋な関数1つにまとめ、リポジトリの構造の図と『横断の構造』の両方が同じ関数を使う",
	"組がないときは、今の図の HTML と見え方を変えない",
]

current: """
	- orca-web の要約（`GET /api/worktrees/summary`、`orca-web.worktree-summary/v1`）は、エージェントが1人以上いる worktree ごとに `id`、`path`、`branch`、`project {id, name}`、`issue`、`counts`、`agents[]`（`id`、`mark`、`workingMode`、`agentType`、`since`、`detail`（`/embed/agent?id=…`）など）を返す。親の項目と main の印はない。orca-web の状態の文書の各エージェントは `paneKey` と `parentPaneKey`、各 worktree は `isMainWorktree` を持つ。
	- SpecDock の画面は、殻の1つの読み手（`core/orca.js` の `createOrca`）で orca-web の部品（`/embed/agent-marks.js`）を読み、その `watchWorktreeSummary` で要約を 10 秒ごとに受ける。`orca.summary()` が今の要約、`orca.subscribe` が知らせ。Scope と worktree の対応は `core/orca_match.js` の `matchWorktrees`（構造の `worktrees.paths` と各 Scope の `worktrees[]` のパスとブランチ）。
	- 構造の図（`views/graph.js`）は、`layout.js` の座標で、世界（`.gx-world`、`translate(tx, ty) scale(s)`）の中に、木の線の SVG（`.gx-tree`）→ 枠 → 箱 → 塊 → 依存の線の SVG（`.gx-edges`）の順に置く。稼働の印は `_shared/orca_marks.js` の `paintOrcaMarks` が、箱と枠の印の置き場（`[data-orca-scope]`）に orca-web の `renderAgentMarks` で描く。印は `max` を超えると `+N` に畳まれる。
	- 横の欄は `_shared/panel.js` の `createScopePanel`。片付けの候補の一覧は、同じ欄（aside）を Scope 以外の中身に使っている前例。エージェントのタブ（`_shared/agents_tab.js`）は、orca-web の `/embed/agent` を決まった sandbox の iframe で開く（`agentFrame`、`AGENT_SANDBOX`）。
	- iss-00614（epic-00612）は、箱・枠・塊・線の HTML を `views/graph/draw.js` に取り出し、『横断の構造』（`views/allgraph.js`、組み立ては `views/allgraph/compose.js`）を作る。リポジトリの枠ごとに、中の構造の図の原点 `body {x, y}` がある。
	"""

target: """
	- orca-web：要約の各エージェントに `parent`、各 worktree に `main`、印の要素に `data-agent-id`（iss-00043、orca-web のリポジトリ）。
	- SpecDock：純粋な計算 `views/graph/command.js`（つながり・居場所・帯・端と曲線）、構造の図の指揮の層と帯（iss-00616）、『横断の構造』への適用（iss-00617）。
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
			             worktreeId: string | null} // 親のいる worktree（同じ要約の worktrees[].id）
			  }
			}
			```

			- orca-web は、子の `parentPaneKey` と同じ `paneKey` を持つエージェントを親とし、その `id` と `worktreeId` を返す（構造化 Chat の id の合併の後の id）。`parentPaneKey` があるのに親が見つからなければ `{id: null, worktreeId: null}`。
			- 印の要素（`renderAgentMarks` が描く各エージェントの要素）に `data-agent-id`（エージェントの id）を足す。`+N` に畳まれたエージェントには要素がない。
			- SpecDock は、項目がない（古い orca-web）、形が違う、を F-01・F-03 として受け、要約の版を見て止まらない（版は変わらない）。

			この Epic の SpecDock の Issue は、この形を合成の要約で確かめて先に進められる。実データでの確かめは、iss-00043 が main に入った後に行う。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "指揮の線の純粋な計算（views/graph/command.js）"
		text: """
			DOM・ネットワーク・時計に触れないモジュール。入力と出力（名前は Issue の設計で決めてよいが、役割は次のとおり）：

			1. `commandPairs(summary)` → 組の並び `[{parent: AgentRef, child: AgentRef}]`。`AgentRef` は `{id, mark, workingMode, agentType, detail, worktree}`（worktree は要約の worktree の写し）。
			   - 要約の全エージェントを id で引く表を作り、各子の `parent.id` が表にあり、自分でなければ組にする（R-01、F-02、F-03）。`parent` の形が違えば飛ばす。同じ（親, 子）は1組。並びは子の id の順。
			   - `orca.status()` が ok でないか、要約が無効なら空（F-01）。
			2. `placeAgents(pairs, {structure, nodes, groups, ix, isOwnWorktree})` → 各端の居場所 `{kind: "node", id} | {kind: "group", id} | {kind: "band", item}`（R-02）。
			   - worktree → Scope は今の `matchWorktrees` と同じ対応（逆の索引を足す）。Scope が `nodes` にあればその箱・枠、畳んだ塊（`groups` の members）に入っていればその塊、なければ `ix.ancestors` をたどって最初に `nodes` にある祖先の枠。どれもなければ帯。
			   - 帯の項目は worktree ごと：`{key: worktree.id, label, own: bool, agents: [AgentRef]}`。札は、このリポジトリの worktree（`matchWorktrees` と同じ判定：構造の `worktrees.paths` にパスがある、または同じ project）なら `main === true` で「main のチェックアウト」、ほかはブランチ名。ほかのリポジトリなら「<project.name> · <branch>」。項目が null のときは F-04 の札。並びは、このリポジトリの main のチェックアウト → このリポジトリのほか（ブランチ名の順）→ ほかのリポジトリ（札の順）。帯に出すのは、組の端だけ（R-03）。
			3. `commandModel({pairs, places, layout, band})` → `{band: {h, items: [{key, label, x, y, w, h, agents: [{id, x, y}]}]}, links: [{parent, child, state, d, from, to}], rings: [{nodeId, agentId}], width, height}`。
			   - 帯の寸法：1行、項目は札＋印の数で幅を決め、左から並べる（折り返さない。R-03）。帯の高さは項目が1つ以上で定数 `BAND.h`、なければ0。全体の座標＝配置の座標＋(0, 帯の高さ)。`width` は配置の幅と帯の幅の大きいほう。
			   - 端：箱・枠・塊の矩形（`layout` の座標＋帯の高さ）の上の辺。帯の項目なら、その項目の中のそのエージェントの印の下の辺。同じ端から出る線は、出口の x を一定の間隔でずらす。
			   - 道：`M from C c1 c2 to` の三次ベジェで、制御点は両端の上に、両端の縦の差に応じた高さだけ持ち上げる（上にふくらむ弧）。
			   - 両端が同じ居場所なら線を作らず、`rings` に（その箱、親の id）を足す（R-04）。
			   - `state`：子の `mark` が working なら `flow`、done なら `done`、そのほか（waiting、blocked、sleeping、unknown）は `wait`（R-05）。
			4. 鍵：（要約の文書、配置の結果、帯の寸法の定数）が同じなら、前の結果を返す（R-09）。

			node のテスト：報告書の実データの形の合成の入力（5組、別のリポジトリの統括、同じ worktree の親子）、隠れた Issue、畳んだ塊、親が見えない、形の違う親、自分を指す、輪、`main` がない、`branch` が null、`project` が null。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-09", "F-01", "F-02", "F-03", "F-04"]
	}
	"D-03": {
		title: "構造の図の指揮の層と帯（描画）"
		text: """
			- 世界の中の並び：木の線 → 枠 → **指揮の層**（`<svg class="gx-cmd" aria-hidden="true">`、`pointer-events: none`、`overflow: visible`）→ 箱 → 塊 → 依存の線。帯（`<div class="gx-band">`）は世界のいちばん上（y が 0 から帯の高さ）。組がなければ、層と帯の要素を置かない（R-03 の3つ目、制約の4つ目）。
			- 配置の座標を帯の高さだけ下げる。今の `layout` の座標で置く枠・箱・塊・依存の線は、それらを包む1つの入れ物を帯の高さだけ下げるか、同じ量を足して置く（どちらかは Issue で決める。依存の線と edgeAudit の座標の測り方は変えない）。世界の幅と高さ、初めの見え方と『収める』の外接の四角に帯を含める（R-08）。
			- 帯が出たり消えたりして帯の高さが変わったら、見る位置 `ty` を、変わった高さ × 倍率だけ補い、箱が画面の上で動かないようにする（R-09）。
			- 帯の項目：札（文字）と、各エージェントの印。印は orca-web の `renderAgentMarks` に、そのエージェント1人だけの worktree を渡して描く。各エージェントを `<button type="button" data-cmd-agent="<id>">` で包み、押せてキーボードで選べる（R-07）。
			- 線：各組に、下地の光の道（太く薄い）と本体の道の2本。`data-state` で `flow`・`wait`・`done` を分ける。親の端に波紋（円を2つ、ずらして広げる）。同じ親の波紋は1か所に1つ。
			- 電波の輪：`rings` の箱の印の置き場で、`data-agent-id` がその親の印の要素に、小さな輪の印（CSS の擬似要素か小さな SVG）を付ける。要素がなければ（`+N` に畳まれた）、その置き場に付ける（R-04）。
			- 稼働の印を描く今の関数（`paintOrca`）の中で、線と帯を描き直す。鍵が同じなら何もしない（R-09）。
			"""
		satisfies: ["R-03", "R-04", "R-05", "R-08", "R-09"]
	}
	"D-04": {
		title: "指揮の色、動き、凡例"
		text: """
			- 色の札：`--sd-cmd`（線の本体）と `--sd-cmd-glow`（下地の光）を、`app.css` の明るいテーマ（`:root`）、暗いテーマ（`prefers-color-scheme: dark` の中）、明示の暗いテーマ（`[data-theme="dark"]`）の3か所に定める。色相は 50〜58°（`--sd-blocked` の明 39°・暗 43° より10°以上、黄の側）。明るいテーマは、白地で 3:1 以上の濃い黄（例 #a89200 の近く）に、太く薄い光（同じ色相の明るい黄の半透明）を下に重ねる。暗いテーマは明るいレモン（例 #ffec4d の近く）。値は Issue で、背景とのコントラストを計算して決める（R-06）。
			- 動き（`graph.css`）：`flow` は丸い点の破線（`stroke-linecap: round`、`stroke-dasharray`）の `stroke-dashoffset` を、端から端まで 2〜3 秒で流す。`wait` は止まった点線。`done` は薄い（opacity を下げた）動かない線。波紋は `transform: scale` と `opacity` で 2.4 秒ごとに2つの輪をずらして出す（R-05）。
			- 減らす設定：`@media (prefers-reduced-motion: reduce)` で、指揮の層のアニメーションを止め（`animation: none`）、波紋の2つ目の輪を隠して、1つの輪を動かさずに出す。今の全体の規則（`app.css` の時間を 0.01ms にする規則）だけに頼らない（それでは最後の形が残るとは限らないため）（R-05）。
			- 凡例：構造の図の凡例（`renderLegend`）の『そのほか』に、指揮の線の見本と波紋の見本で「指揮（親 → 子）」の行を足す。『横断の構造』の凡例も同じ行を持つ（R-06）。
			"""
		satisfies: ["R-05", "R-06"]
	}
	"D-05": {
		title: "帯のエージェントの選びと、詳細の欄のチャット"
		text: """
			- 選びの状態は、Scope の選び（`V.sel`）と別に、指揮の選び（選んだエージェントの id）を1つ持つ。どちらか一方だけ。帯のエージェントを押すと、Scope の選びを解いて指揮の選びにする。もう一度押すか、欄を閉じる、Esc、図の空いたところ、箱を選ぶ、で解く（R-07）。
			- 目立たせ：指揮の層に `has-cmd-sel`、そのエージェントが親か子の線に `is-cmd-hl`、ほかの線に `is-cmd-off`。帯の項目の押したボタンに `aria-pressed="true"`。
			- 詳細の欄：片付けの候補の一覧と同じように、構造の図の横の欄（aside）を、Scope の欄を隠してエージェントの中身に使う。見出しに印・種類・札、閉じるボタン。中身はエージェントのタブと同じ `agentFrame(origin, agent, theme)` と `AGENT_SANDBOX` の iframe（要約の `detail` の `/embed/agent?id=…`）。スマホでは今の下からのシート。欄の中身とページの URL は変えない（覚えない）。
			- 押した後に、そのエージェントが要約から消えたら、指揮の選びを解き、欄を閉じる。
			"""
		satisfies: ["R-07"]
	}
	"D-06": {
		title: "『横断の構造』への適用"
		text: """
			iss-00614 の `compose` と `allgraph.js` に足す（その Issue の後の実際の形に合わせる）。

			- リポジトリごとの対応：要約の各 worktree を、そのパスかブランチ・project で対応するリポジトリ（各リポジトリの構造の `worktrees.paths` と `matchWorktrees`）に割り当てる。どれにも当たらなければ「ほかの場所」。
			- 居場所：`placeAgents` を、そのエージェントのリポジトリの構造・配置で呼ぶ。帯に決まったものは、そのリポジトリの枠の帯へ（札はそのリポジトリの中の札）。「ほかの場所」のものは、全体の帯「ほかの場所」へ（札は「<project.name> · <branch>」）（R-10）。
			- 組み立て：`compose` の `sizes` に各リポジトリの帯の高さ `band` を足し、見出しと body の間に入れる。全体のいちばん上に、「ほかの場所」の帯の高さを足す。『これから』で、`shown` が0で子の枠も出ないリポジトリでも、`band > 0` なら、見出しと帯だけの入れ物として出す（R-11。epic-00612 R-06 のただ1つの例外）。帯がなくなれば、今の規則どおり出さない。
			- 端の座標：全体の世界の座標＝そのリポジトリの body の原点＋そのリポジトリの配置の座標（帯は、その枠の帯の位置）。リポジトリをまたぐ組も、全体の世界の1枚の指揮の層に描く。
			- 重なり：リポジトリの枠（section）は重なりの文脈を作らないようにし、z-index で、枠（リポジトリと Initiative）→ 指揮の層 → 箱 → 依存の線の順にする。
			- 帯の高さが変わったら、そのリポジトリより後ろの枠の位置が変わるので、`compose` を計算し直す（各リポジトリの中の配置は計算し直さない）。見る位置の補い（D-03）は、画面のいちばん上の見えている枠を基準にする。
			- 選び・色・動き・凡例は D-03〜D-05 と同じ部品を使う。
			"""
		satisfies: ["R-10", "R-11"]
	}
	"D-07": {
		title: "確かめのしかた"
		text: """
			- 純粋な計算：node のテスト（D-02 の場合）。
			- 画面：合成の要約を返す試しの orca-web の口（部品は orca-web の配る `agent-marks.js` の写しか、iss-00043 の後の本物）と、この PC の状態の置き場の写しで、`dashboard serve --offline --state-root` を別のポートで立て、headless Chrome で 1440・1000・390 × 明・暗の写しを撮り、edgeAudit の違反、ブラウザーのエラー、層の並び、`pointer-events`、減らす設定の見え方を数える。常駐のダッシュボードと Orca には触れない（epic-00612 D-07 と同じ）。合成の値と写しは Workbench に置き、公開のリポジトリに実際のパスを入れない。
			- 実データ：iss-00043 が main に入り、手元の orca-web が新しい要約を返すようになった後に、手元の Orca の実際の親子で、線と帯が出ることを確かめる（各 SpecDock の Issue の最後、と統括の最後の確かめ）。
			"""
		satisfies: ["R-08", "R-10"]
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
