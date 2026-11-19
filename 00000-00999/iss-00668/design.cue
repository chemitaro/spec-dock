package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"git の worktree の一覧を、今のサーバーの1回の読みから API に出すだけにし、新しい git の呼び出しを足さない",
	"行の項目の決め方を1つの純粋な計算（新しい `views/graph/unscoped.js`）に寄せ、構造の図と『横断の構造』の両方がそれを呼ぶ",
	"今の帯の描画（`commandModel` の rows、`command_view.js` の層）を写さずに広げ、項目に印・数・薄さ・畳みを足す",
	"`+N` と項目の押しは詳細の欄だけを変え、行と枠の形を変えない",
	"`items` のない構造（今のテストの多く）では、行の項目を今どおり指揮の線の端だけで決める（F-01）",
]

current: """
	- サーバー：`read_structure_facts`（`runtime/application/dashboard_scope_details.py`）が `worktree_list(catalog)` の `GitWorktreeRecord`（path・head・branch・detached・bare・locked・prunable）を読み、`StructureFacts(readings, status, paths)` を返す。`dashboard_http._repository_api` が `worktrees={"status", "paths"}` を `structure_document` に渡し、そのまま JSON に出る。
	- 構造の図（`views/graph.js` の `paintCommand`）：`commandPairs(summary)` → `placeAgents` → `bandItems(pairs, places, own, orderOf)` → `commandModel({items, …})` → `CV.layersHtml`。組がなければ `clearCommand()`。`commandKey({summary, routing: V.EG, marks, ids})` が同じなら描かない。
	- 『横断の構造』（`views/allgraph.js` の `paintCommand`）：`crossPlace` が各リポジトリの行（`rows: Map<repo key, bandItems>`）と `''`（『ほかの場所』）と `keep` を作り、`bandShape` が `compose` の帯の高さと幅を決め、形が変われば `draw()` で組み立て直す（F-05 の2回の上限）。組がなければ `A.shape = null`。
	- 帯の項目の幅は `command.js` の `itemWidth`（枠・余白・札の幅・エージェントの数 × `BAND.slot`）、描画は `command_view.js` の `layersHtml`（`.gx-band-item` に `.gx-band-lab` の span と `.gx-band-agent` のボタン）。
	"""

target: """
	- API の `worktrees` に `items: [{path, branch, head, main, detached, locked}]`。
	- `views/graph/unscoped.js`（純粋な計算）が、構造・要約・組・居場所・見方から、1つのリポジトリの行の項目（`Primary`・`Unlinked`・線の端・`+N`）を返す。
	- 両方の画面は、組がなくても行を描き、『これから』では線を描かずに数を添え、項目と `+N` の押しで詳細の欄を開く。
	"""

design: {
	"D-01": {
		title: "サーバー：worktree の行を API に出す"
		text: """
			`dashboard_scope_details.py` に純粋な関数 `worktree_items(records, catalog) -> tuple[dict, ...]` を足す。records の順に、`bare` の行・`prunable` の行・パスが `catalog` と同じ行を除き、
			`{"path": str(path), "branch": branch, "head": head, "main": index == 0, "detached": detached, "locked": locked}` を返す（`main` は除く前の git の順で最初の行。最初の行が bare なら、どの行も主にならない＝F-03）。
			パスの比べは `os.path.normpath` の文字列（解決はしない。読みの側が絶対パスを返す）。
			`StructureFacts` に `items: tuple[dict, ...] = ()` を足し、`read_structure_facts` が今の1回の `lister` の結果から作る（読めないときは `()`）。
			`dashboard_http._repository_api` は `worktrees={"status", "paths", "items": list(facts.items)}` を渡す。`structure_document` は今どおり写すだけ。
			"""
		satisfies: ["R-01", "F-03"]
	}
	"D-02": {
		title: "行の項目の純粋な計算（新しい `views/graph/unscoped.js`）"
		text: """
			DOM・時計・ネットワークを持たない。`core/orca_match.js` と `graph/command.js` だけを import する。
			- `UNSCOPED = {lead: "Unscoped", leadTitle, primary: {text: "Primary", title}, unlinked: {text: "Unlinked", title}, count: (n) => 説明}`：この Issue の英語の語と説明の1か所。
			- `FOLD = 2`：エージェントのいない `Unlinked` の項目がこの数以上なら、全部を1つの `+N` に畳む（requirement の決定）。
			- `gitWorktrees(structure)`：`structure.worktrees.status === "ok"` で `items` が配列なら、`path` が文字列の行を `normPath` して返す。それ以外は `null`（F-01）。
			- `childCount(pairs)`：`Map<parent agent id, 子の id の Set の大きさ>`。`pairs` は `commandPairs(summary)` の全部（リポジトリで絞らない）。
			- `unscopedItems({structure, summary, pairs, places, own, orderOf, range})` → `[Item]`。
			  1. `git = gitWorktrees(structure)`。`linked` = `structure.scopes[].worktrees[].path` の `normPath` の集合。
			  2. 要約の worktree を `normPath(path)` で引く表（最初の1つ、F-04。要約が無効なら空、F-02）。
			  3. git があれば、主の行（`main`）を `Primary` の項目に、主以外で `linked` にない行を `Unlinked` の項目にする。項目の `worktree` は同じパスの要約の worktree（なければ `{id: null, path, branch, agents: []}`）、`agents` はその worktree の全部のエージェント（`orderOf`＝部品の `orderAgents` の並び、なければ要約の並び）の `refOf`（R-09：1つの worktree ＝ 1つの項目）。
			  4. `places` で `kind: "band"` の線の端（今の `bandItems(pairs, places, own, orderOf)`）を重ねる。端の worktree のパスが 3 の項目に当たればその項目に（エージェントは足し重ね、重複なし）、当たらなければ今の項目（印なし、今の札）として足す。git がないとき（F-01）は今の `bandItems` の結果だけで、`main` が真の項目に `Primary` の印を付ける。
			  5. 各項目の `count` = その項目の worktree のエージェントの `childCount` の和（0 なら `null`）、`countParts` = 子のいるエージェントごとの `{id, agentType, index（項目の中の並びの1始まりの番号）, n}`（title の内訳）、`idle` = エージェントが0。
			  6. 見方：`range === "next"` なら、`Primary` の項目と、`count` のある `Unlinked` の項目だけを残す（線の端だけの項目は落とす）。それ以外は全部。
			  7. 畳み：`idle` な `Unlinked` の項目が `FOLD` 以上なら、それらを外し、`{kind: "fold", key: "fold", label: "+N", folded: [{label, path}], agents: [], idle: true}` を1つ足す。
			  8. 並び：`Primary`、エージェントのいる `Unlinked`（札の順）、線の端だけの項目（今の順：自分のリポジトリ、ほかのリポジトリ）、薄い `Unlinked`、`+N`。
			- Item：`{key, kind: "worktree" | "fold", label, badge: "primary" | "unlinked" | null, own, main, worktree, path, agents: [AgentRef], idle, count, countParts, folded}`。
			- `countTitle(item)`：`"3 agents in progress — claude #1: 2, codex #2: 1"`（1なら agent。種類がなければ `agent`）。`key` は線の端と同じ（要約の worktree の `bandKeys`）、要約のない git の行は `git:<path>`。
			- `commanding(items)`：`count` のある項目があるか（『横断の構造』の keep に使う）。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-06", "R-09", "F-01", "F-02", "F-03", "F-04"]
	}
	"D-03": {
		title: "帯の模型の広げ（`views/graph/command.js`）"
		text: """
			- `bandLabel`：自分のリポジトリの main の札を「main のチェックアウト」からブランチ名に変える（`Primary` の印が代わりに示す）。detached（`branch` がなく `head` がある git の行）は `detached @<head の先頭7文字>`。ほかは今のまま。
			- 折り返し（R-09）：`BAND.perLine = 4`、`BAND.lineH = 24`。項目のエージェントの欄は `min(n, perLine)` 列 × `ceil(n / perLine)` 行。項目の高さは `BAND.h + (lines - 1) * BAND.lineH`（1行なら今の 28）。各エージェントの slot は `{x: 左 + slot × (i % perLine), y: 項目の top + lineH × floor(i / perLine), w: slot, h: BAND.h}`（1行目は今と同じ）。
			  行（row）の高さは、その行のいちばん高い項目。`bandModel` の行の `h` と `band.h` はその最大。構造の図の行（`BAND.top`）は、下の縁を今の位置（`BAND.top + BAND.h`）に保つよう、高い分だけ上に置く（graph.js が `top: BAND.top - (rowH - BAND.h)` を渡す。`bandRowHeight(items)` を export する）。
			  線の端（`fixedEnd` の band）は今どおり `{x: slot の中心, y: 項目の top}`（箱の印と同じく、折り返した行の印も項目の上の縁）。同じ項目の弧も今の `sameHop`。
			- `itemWidth(it)`：今の幅（エージェントは `min(n, perLine)` 列）に、印（`badge` があれば `labelWidth(印の文字) * 0.8 + BAND.labelGap`、小さい字）と数（`count` があれば同じ式で数の文字）を足す。`kind: "fold"` はエージェントの欄を持たない。`bandModel` は項目の `badge`・`count`・`idle`・`kind`・`folded`・`path` を写す（今の `...it` のまま）。
			- `commandModel` は rows の項目にエージェントがなくても項目を置く（今も置ける）。組が0でも rows があれば `band` を返す（今も同じ。graph.js が呼ばなかっただけ）。
			- `bandItems` は今のまま（D-02 が中で使う）。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-09"]
	}
	"D-04": {
		title: "『横断の構造』の行（`views/allgraph/command.js`）"
		text: """
			`crossPlace(pairs, {repos, summary, visible, visibleWith, orderOf, range})`：
			- `range === "next"` なら、線の組を描かない（返す `pairs` は `[]`、`places` は空）。全体・いまでは今の居場所の決め方のまま。
			- 各リポジトリの行は、そのリポジトリの `structure` と、そのリポジトリの端（今の `rows.get(key)` に入る場所）から `unscopedItems` で決める（`own` は今の `of` のそのリポジトリの worktree）。項目のないリポジトリは行を持たない。『ほかの場所』（`''`）は今のまま `bandItems`（全体・いまだけ）。
			- `keep`：見えないリポジトリで、全体・いまは今どおり（親が帯にいる）、これからは `commanding(行)` が真のもの。
			- `pairs` が0でも `crossPlace` を呼べる（行は git の一覧と要約から決まる）。
			`bandShape` は行の幅に頭の文字 `Unscoped` の幅を入れ（`bandRowWidth(items, UNSCOPED.lead)`）、行の高さを `REPO.band + bandRowHeight(items) - BAND.h` にする（R-09、`compose` の `bands[key].h` はすでに高さを受け取る）。`crossModel` は各リポジトリの行に `lead: UNSCOPED.lead` を付ける。
			"""
		satisfies: ["R-06", "R-07", "R-09"]
	}
	"D-05": {
		title: "構造の図の描き方（`views/graph.js`）"
		text: """
			`paintCommand`：
			- `pairs = range === "next" ? [] : commandPairs(summary)`（数のためには全部の組 `commandPairs(summary)` を `unscopedItems` に渡す）。
			- `placeAgents` は組があるときだけ。`own` は `ownWorktrees` か、ないとき空の集合。
			- `items = unscopedItems({...})`。項目が0なら `clearCommand()`（F-01 と同じ：構造に `items` がなく組もない）。
			- `commandModel({pairs, places, rows: [{key: "", left: BAND.left, top: BAND.top, lead: UNSCOPED.lead, items}], …})` → `drawCommand`。
			- `commandKey` に構造（`V.data`）と見方（`range`）を足す（同じ入力で描かない R-08 を保つ）。
			- 押し：`[data-cmd-wt]`（項目の札）と `[data-cmd-fold]`（`+N`）で `CV.renderWorktreePanel`、もう一度・閉じる・Esc で閉じる（今の `pressBandAgent` と同じ形）。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-05", "R-06", "R-08"]
	}
	"D-06": {
		title: "『横断の構造』の描き方（`views/allgraph.js`）"
		text: """
			`paintCommand`：組がなくても `crossPlace` を呼び（`range: A.range`）、行が1つもなければ今の『組がない』の扱い（`A.shape = null`）。`crossKey` に見方を足す。
			押しは構造の図と同じ（`[data-cmd-wt]`・`[data-cmd-fold]` → `CV.renderWorktreePanel`）。
			すべての見えるリポジトリの枠が行を持つので、枠の高さが `REPO.band` 増える（今の iss-00617 の帯の場所と高さのまま）。
			"""
		satisfies: ["R-05", "R-06", "R-07", "R-08"]
	}
	"D-07": {
		title: "描画の部品と詳細の欄（`views/graph/command_view.js`、`views/_shared/orca_marks.js`）"
		text: """
			- `layersHtml`：項目の札を `<button class="gx-band-lab" data-cmd-wt="<key>">` にし（今の span の位置と幅のまま）、`badge` があれば `<span class="gx-band-badge" data-badge="primary|unlinked" title aria-label>`、`count` があれば `<span class="gx-band-count" title aria-label>`（`countTitle`）、エージェントのボタンは模型の slot の位置（折り返しの行）に置く、`idle` なら項目に `is-idle`。`kind: "fold"` は `<button class="gx-band-lab gx-band-fold" data-cmd-fold>+N</button>` だけ。行の頭の文字に title を付ける。
			- `renderWorktreePanel(panel, {item, orca, embed, theme, hide})`：見出し（印とブランチ）、パス、エージェントの一覧（種類と、押すとチャットを開く `data-cmd-agent` のボタン）、`item.worktree.id` が文字列で orca が ok で埋め込みでないとき『Orca で開く』（`orca_marks.js` に足す `openWorktreeButton(slot, {orca, worktreeId, theme, embed, doc})`、今の `createOpenButton` と同じ script を差す）。`fold` の項目は畳んだ worktree のブランチとパスの一覧。
			- `paintCmdSel`・`paintBandMarks` は今のまま（エージェントのボタンの形は同じ）。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-05", "R-09"]
	}
	"D-08": {
		title: "見た目（`views/graph.css`）"
		text: """
			項目は高さを模型から受け取り（style の height）、エージェントのボタンは絶対の位置（模型の slot）で置く。札・印・数は1行目の高さの中にそろえる。
			`.gx-band-badge`・`.gx-band-count`：小さい字の札（今の色の変数だけ。`Primary` は `--ds-accent-soft`、`Unlinked` は警告の地の変数、数は `--ds-surface-3`）。`.gx-band-item.is-idle`：`opacity: .55`。`.gx-band-lab` のボタンは今の span と同じ字・幅（ボタンの既定の枠と地を消す）、`:focus-visible` の輪。
			幅の推定（D-03）と CSS の字の大きさを合わせる（`graph.css` の注記に書く）。線・波紋・層の z-index は変えない。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-08"]
	}
	"D-09": {
		title: "実機の確かめと移行の案内"
		text: """
			候補の wheel を隔離した venv と一時の状態の置き場に入れ、別のポートで `--tailscale`（常駐の 47800・8791 と道具の環境には触れない）。spec-dock の構造の図と『横断の構造』を 1440・390 × 明・暗で、(a)〜(d)（依頼書の受入）と (e) 1つの worktree に複数のエージェント（指揮の親子を含む）がいる場面を写し、`specdockEdgeAudit`・`specdockCmdAudit` と iss-00646 の台本を開始のコミットの wheel と比べる。
			移行の案内の文（`Unscoped`・`Primary`・`Unlinked`、薄く・`+N`、『これから』で線がなくなり数が付くこと、API の `items`）を report.md に用意する。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-06", "R-07", "R-08", "R-09"]
	}
}

compatibility: """
	API の `worktrees` に `items` を足すだけで、`status`・`paths` は変わらない。`items` を読まない古い画面はそのまま動く。
	画面：今の札「main のチェックアウト」はブランチ名と `Primary` に変わる。『これから』の指揮の線（祖先の枠や帯へ落ちる線）はなくなり、数に変わる。各リポジトリの枠と構造の図の世界の上に、いつも行が出る（構造の図の golden・『横断の構造』の枠の高さの期待が変わる）。
	"""

risks: [
	"すべての枠に行が出るので『横断の構造』の世界が縦に伸びる（1つの枠で `REPO.band`）。重さの台本で確かめる",
	"幅の推定（labelWidth）と実際の字の幅のずれで、項目がはみ出す。実機の写しで確かめ、ずれれば D-03 の係数を直す",
]
