package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"押した印とエージェントの対応を、部品の `data-agent-id` の有無に関わらず1つの関数で求める",
	"横の欄に、エージェントのタブを指定のエージェントで開く口を1つ足し、4つの画面がそれを呼ぶ",
	"枠の worktree の印とボードの札の専用の行は、今の部品（`wtMark`・`orcaSlot`）の置き場を変えるだけにする",
]

current: """
	- `views/_shared/orca_marks.js` の `paintOrcaMarks(root, ctx, structure)` は、置き場（`[data-orca-scope]`）ごとに `module.buildMarks(worktree, {now, max})` の結果を `marksKey` で比べ、違えば `module.renderAgentMarks(slot, worktree, {size: "sm", max, now})` で描く。描いた並びは覚えていない。
	- 印を押したとき：`views/graph.js` の押し（`.sd-orca` のとき `select(id)` の後に `V.pn?.preferTab("agents")`）、`views/allgraph.js` の同じ押し、`views/board.js` の `onCardClick`、`views/_shared/panel.js` の aside の押し（`preferTab("agents")`）。エージェントのタブの選びは、欄の `params` の `agent`、なければエージェントの記憶（`agents_tab.js` の `mem.last`）。
	- `views/graph/draw.js` の `frameHtml` の見出しは、状態の印・Initiative の印・ID・題名・稼働の印の専用の行（`.gx-agents`）。`boxHtml` の木の表示の枠（`frame`）の `.gx-marks` に worktree の印はない。
	- `views/_shared/parts.js` の `card(scope, ctx, {orca: true})` は、`meta`（`.sd-card__meta`）の最後に `orcaSlot(scope.id, 4)` を入れる。CSS（`parts.css`）は、`meta` の中身が空の置き場だけなら `meta` を隠す。
	"""

target: """
	稼働の印の置き場ごとに描いた並びを覚え、押した要素からエージェントの id を求め、横の欄の `openAgent(id)` がそのエージェントでエージェントのタブを開く。
	枠の見出しと木の枠の箱に worktree の印があり、ボードの札の稼働の印は専用の行にある。
	"""

design: {
	"D-01": {
		title: "描いた並びの記録と、押した印のエージェント（`orca_marks.js`）"
		text: """
			- 記録：モジュールの中の `WeakMap`（`shown`、置き場の要素 → id の配列）。`paintOrcaMarks` は、置き場を描いたとき（`renderAgentMarks` の後）に `built.marks.map((m) => m.id ?? null)` を記録する。key が空で置き場を空にしたときは空の配列、catch で空にしたときは `shown.delete(slot)`（F-02）。key が同じで描き直さないときは、記録を触らない（同じ key は同じ `buildMarks` の結果なので、id の並びも同じ）。
			  部品の `renderAgentMarks` は中で同じ引数（`now`・`max`）で `buildMarks` を呼び、その `marks` の順に `.orca-mark` を描き、最後に『+N』（`.orca-mark--more`）を足すので、記録の i 番目と、置き場の中の i 番目の `.orca-mark:not(.orca-mark--more)` が同じエージェントになる。
			- `export function markAgentAt(slot, target)`：`const mark = target?.closest?.(".orca-mark")`。`mark` がない、`slot` の中でない（`slot.contains(mark)` が偽）、`mark.classList.contains("orca-mark--more")`、のどれかなら null。
			  `mark.getAttribute("data-agent-id")` が空でない文字列ならそれ。なければ `const marks = [...slot.querySelectorAll(".orca-mark:not(.orca-mark--more)")]`、`const ids = shown.get(slot)`。`ids` がない、`ids.length !== marks.length`、`marks.indexOf(mark) < 0` なら null。そうでなければ `ids[i]`（null もそのまま返す）（F-01）。
			- `export function markIds(slot)`：記録の写し（配列の複製）か null を返す。iss-00616 の印の位置（Epic の D-02 の `marks` の `ids`、D-10 の `markSpots`）は、graph.js の測り（`{Scope id: {items, gap}}`）に、この関数で置き場ごとの `ids` を足して使う（測りへの足しは iss-00616 が行う。この Issue は口だけを作る）。
			- SpecDock の側に並べ替えのコードを置かない（R-03）。`marksKey` と置き場の HTML（`orcaSlot`）は今のまま。
			"""
		satisfies: ["R-03", "R-04", "F-01", "F-02"]
	}
	"D-02": {
		title: "横の欄の `openAgent(agentId)`（`panel.js`）"
		text: """
			`createScopePanel` の戻り値に `openAgent(agentId)` を足す（`preferTab` は残す）。中身：
			1. `userTab = "agents"`（`preferTab("agents")` と同じ選び）。
			2. `agentId` が空でない文字列で、`current` がある（欄が Scope を見せている）とき：`params.set("agent", agentId)`、`memoryFor(mem, current.scope.id)` の後に `forgetGone(mem, agentId)`（エージェントのタブの帯の項目を押したときと同じ意味：その Scope の失いの記録を忘れ、選びと最後の置きをその人にする）。
			3. `current` があれば `draw()`。
			`agentId` が null（F-01、『+N』）なら 1 と 3 だけで、今の `preferTab("agents")` と同じ。`memoryFor`・`forgetGone`・`mem` は `agents_logic.js`・`agents_tab.js` の今の関数を使う。
			呼ぶ側は、Scope を選ぶ（`select`。欄の `show` を同じ流れの中で呼ぶ）**後**に `openAgent` を呼ぶ。`show` は Scope が変われば `params` を空にするので、前に呼ぶと選びが消える。graph・allgraph・board の `select` は、await の前に欄を描く（`renderPanel`・`drawPanel` → `pn.show`）ので、`select(id)` の直後に呼べばよい。
			エージェントのタブを見せない欄（`visibleTabs` に agents がない）では、今の `preferTab` と同じく描きの中の `pickTab` に任せる（新しい扱いを足さない）。
			"""
		satisfies: ["R-02", "F-01"]
	}
	"D-03": {
		title: "4つの画面の印の押し"
		text: """
			押した置き場は `target.closest(".sd-orca")`、エージェントは `markAgentAt(slot, target)`（D-01）。`preferTab("agents")` の呼びを `openAgent(...)` に置き換える。ほかの流れは変えない。
			- 構造の図（`graph.js` の押し）：`if (V.sel !== id) select(id); V.pn?.openAgent(markAgentAt(slot, target));`。箱（`.gx-box`）も枠の見出し（`.gx-fh`）も同じ押しを通る。スマホの二度目の指（iss-00602）の扱いは、印の押しの後にあるので変わらない。
			- 『横断の構造』（`allgraph.js` の押し）：`if (!same) select(hit.repo, hit.id); A.pn?.openAgent(markAgentAt(slot, target));`。
			- ボード（`board.js` の `onCardClick`）：`select(anchor.dataset.id)` の後、`const slot = event.target.closest(".sd-orca"); if (slot) B.pn?.openAgent(markAgentAt(slot, event.target));`。
			- 横の欄の見出し（`panel.js` の aside の押し）：`const slot = t.closest(".sd-orca"); if (slot) { openAgent(markAgentAt(slot, t)); return; }`。欄の中の帯（`.sd-agentpick__mark`）は `.sd-orca` ではないので、今どおり帯の項目の押しになる。
			"""
		satisfies: ["R-02"]
	}
	"D-04": {
		title: "枠の worktree の印（`draw.js`・`graph.css`）"
		text: """
			- `frameHtml` の見出し：題名（`.gx-fttl`）の後、`.gx-agents` の前に `M.wtMark(s.state === "doing" ? s.branch : null)` を置く。`wtMark` は branch が空なら空の文字列を返すので、作業中でない・branch のない枠の HTML は今と同じ（R-01）。
			- `boxHtml` の木の表示の枠（`frame` の枝）の `.gx-marks`：Issue の箱と同じ位置（保証レベル・片付けの候補の後、人のタスクの前）に同じ `M.wtMark(...)` を足す。
			- 見出しの行：配置の規則の `.gx .gx-fttl { max-width: none; flex: 1; }`（基準 0）で題名だけが縮むので、`.gx-fh` が `flex-wrap: wrap` になる稼働の印のある見出しでも、worktree の印は題名の行に残る（Epic の round-3 の申し送り）。足りなければ `.gx .gx-fh > .wt { flex: none; }` を足す。縮めた枠（`is-compact`）の題名は2行まで折り返し、その高さは iss-00627 の測り直し（`compactNeeds`）が測るので、配置の見込みの式は変えない。
			- 『横断の構造』は `draw.js` の同じ部品を通る。見出しの aria-label は今のまま。
			"""
		satisfies: ["R-01"]
	}
	"D-05": {
		title: "ボードの札の専用の行（`parts.js`・`parts.css`）"
		text: """
			- `card`：`if (orca) meta.push(orcaSlot(scope.id, 4))` をやめ、`meta` の行の後（`parentLine` の前）に、`orca` のときだけ `<span class="sd-card__agents">${orcaSlot(scope.id, 4)}</span>` を置く（札は `<a>` なので `span`）。`orca` でない札の HTML は今と同じ。
			- `parts.css`：`.sd-card__agents { display: flex; margin-top: 4px; min-width: 0; }`、`.sd-card__agents:not(:has(.orca-mark)) { display: none; }`、`.sd-card__agents > .sd-orca { margin-left: 0; }`（今の `.sd-orca` の行の終わりの寄せを打ち消す。値は今の規則を読んで決める）。
			  `.sd-card__meta` の、空の置き場だけのときに隠す規則は、置き場が `meta` から外れて要らなくなるので、`orca` でない札と同じ形（`meta` があるときだけ行を出す）で足りる。規則を消すか残すかは、HTML が今と同じことを優先して実装で決める。
			- 色・上限・並び順は変えない。
			"""
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "確かめのしかた"
		text: """
			- node のテスト：`markAgentAt` と記録（`tests/unit/infra/test_dashboard_orca_marks_js.py` の偽の DOM）、`openAgent`（`tests/unit/infra/test_dashboard_orca_views_js.py` の `run_panel`）、`frameHtml`・`boxHtml` と `card` の HTML（同じファイルか近いもの）、画面の押しの静的な検査。
			- 実機（Epic の D-07）：隔離した venv に、この branch の wheel を入れ、一時の状態の置き場（この PC の状態の置き場の写し）で `dashboard serve` を別のポートに `--tailscale` で立てる。orca-web は手元のもの（iss-00043 の後の部品）を読む（その設定は変えない）。
			  統括が用意する試しの送り先（作業中の Epic の worktree に2人以上のエージェント。置けるなら指揮の親子の組を含む）で、枠の見出しの worktree の印と稼働の印、2つ目の印を押したときのチャット、ボードの札の専用の行、横の欄の見出しと『横断の構造』の押しを、1440・390 × 明・暗で写し、edgeAudit の違反0、ブラウザーのエラー0を数える。エージェントには何も送らない。
			- headless Chrome は `--disable-features=MacAppCodeSignClone` で起動し、CDP の `Browser.close` で閉じる。写しと道具は Issue の `.workbench/` に置く。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-05"]
	}
}

compatibility: "API・保存・モデルは変わらない。置き場の HTML（`orcaSlot`）、`marksKey`、`preferTab` は今のまま。iss-00616 は D-01 の `markIds`（置き場ごとの ids）と `markAgentAt`、D-02 の `openAgent` を使う（Epic の D-02・D-09・D-10）。"

risks: [
	"orca-web の部品が `.orca-mark` の描く順を `buildMarks` の順から変えると、`data-agent-id` のない印で取り違える。今の部品は `data-agent-id` を出す（iss-00043）ので、その値を先に使い、記録は古い部品のための予備にする",
	"枠の見出しで題名がさらに縮む。縮めた枠の題名が2行になる枠が増えるが、iss-00627 の測り直しが高さを合わせる",
]
