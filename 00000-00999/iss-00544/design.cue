package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"骨組みの格子を、出ない行があっても崩れない形にする",
	"構造の API の保証レベルとブランチを、要求ごとに重い処理を走らせずに埋める",
	"印の部品の値を1か所に置き、画面ごとの写しをなくす",
]

current: "`<main>` は格子の自動の配置で行が決まり、PC では2行目（高さ auto）に入る。構造の API の `assurance`・`branch` は常に `null`。印の値は `core/ui.js`、`views/_shared/{parts,logic}.js`、`views/graph/marks.js` に分かれる。骨組みはスナップショットのないリポジトリにも「見た」を送る。経路の引き直しは8回で、最後の回を返す。"

target: "格子の各行を明示し、構造の API は覚える仕組みつきの読み取りで値を埋め、印の値は `core/ui.js` だけが持ち、骨組みはモデルがあるときだけ「見た」を送り、経路の引き直しは問題の最も少ない回を返す。"

design: {
	"D-01": {
		title: "骨組みの格子の行を明示する"
		text: """
			`app.css` で `.top { grid-row: 1 }`、`.mtabs { grid-row: 2 }`、`.notices { grid-row: 3 }`、`.main { grid-row: 4 }` を指定する。出ない行は高さ auto で0になり、`<main>` は常に4行目（`minmax(0, 1fr)`）に入る。`views/graph.css` と `views/timeline.css` の `grid-row: 4` を消す（graph の `position: relative; overflow: hidden` は残す）。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "構造の一覧の読み取り `read_structure_facts`（`application/dashboard_scope_details.py`）"
		text: """
			- `StructureFactsCache`：カタログのパスごとに `{Scope ID: (requirement.cue の st_mtime_ns, st_size, level)}` を持つ。サーバーの1つの `DashboardHttp` が1つ持つ（プロセスの間だけ。ファイルに書かない）。
			- `read_structure_facts(site, scope_ids, cache, *, timeout=3.0, clock, assurance_reader, worktree_lister, cue_locator) -> {ID: {"assurance": str|None, "branch": str|None}}`。
			  1. 締め切り = 今 + timeout。カタログが `None` か、ディレクトリでなければ、全 Scope を `null` で返す（覚えたものも捨てない）。
			  2. `git worktree list` を1回（上限は締め切りまでの残り）。失敗すれば全 `branch` を `null`。成功すれば、各 Scope について `branch_names_scope` が真の最初のブランチ。
			  3. 各 Scope の `<カタログ>/<区切り>/<ID>/requirement.cue` を `lstat`。通常のファイルでなければ `null`（Markdown の Scope など）。覚えた (時刻, 大きさ) が同じなら、覚えた値。違えば、締め切りの前なら `read_assurance(directory, timeout=残り, tool=…)` で読む。読めた値（`light` など）か、読めなかったときの `null` を覚える（壊れたファイルを毎回読み直さないため。時刻か大きさが変われば読み直す）。締め切りの後は `null` を返し、覚えない（F-02）。例外は、その Scope の `null` にする（F-01）。
			  4. `cue` の在りか（`locate_cue`）は、読む必要のある Scope が出たときに1回だけ探す。見つからなければ、残りの読み直しは `null`（覚えない）。
			  5. その要求で見なかった Scope の分を、覚えたものから捨てる。
			- `DashboardHttp._repository_api` の `structure` で `read_structure_facts` を呼び、`structure_document(..., facts=…)` に渡す。`scopes/<ID>` では、今までの `read_scope_details` の結果から、その Scope の `assurance`（`details.assurance.level`）と `branch`（`details.worktrees.items` の最初）を作って渡す。
			"""
		satisfies: ["R-02", "R-03", "F-01", "F-02"]
	}
	"D-03": {
		title: "`presentation/dashboard_api.py` の `facts`"
		text: "`structure_document(view, *, now, baseline, latest, facts=None)` と `scope_document(..., facts=None)`。`scope_item` は `facts.get(ID)` の `assurance` と `branch` を入れ、なければ `null`。既定の `None` では今までどおり `null`。"
		satisfies: ["R-02"]
	}
	"D-04": {
		title: "印の値の置き場を `core/ui.js` に寄せる"
		text: """
			- `core/ui.js` に足す：`ICONS` に、`parts.js` の `MORE_ICONS` と `marks.js` の `GRAPH_ICONS` の和（同じ名前は同じ形なので1つに）。`KIND_LABEL`、`ASSURANCE_LEVELS`（`{light: 1, …}`）、`PR_STATE_WORDS`、`STATE_WORDS`（`STATES` の label から作る）。
			- `parts.js`：`MORE_ICONS` を消し、`icon` は `ic` の別名にする。`LEVELS` を `ASSURANCE_LEVELS` に。
			- `logic.js`：`KIND_LABEL`、`STATE_WORDS`、`PR_STATE_WORDS` を `core/ui.js` から読み直して書き出す（今の import 先を変えない）。
			- `marks.js`：`GRAPH_ICONS` を消し、`ic` は `core/ui.js` の `ic`。`KIND`、`AS`、`PRW` を `core/ui.js` の値に。
			- `logic.js` は DOM を使わないまま（`core/ui.js` も DOM を使わない）。
			- 見た目：印の HTML の文字列は変えない（R-04 のテスト）。構造の図の箱の worktree の印だけ、状態が作業中の箱に限る（requirement の decisions）。
			"""
		satisfies: ["R-04"]
	}
	"D-05": {
		title: "「見た」はモデルがあるときだけ送る"
		text: "`app.js` の `boot` で、`state.data?.snapshot?.fetched_at` があるときだけ `api.markSeen` を呼ぶ。比べる元（`baseline`）の受け取りは今までどおり。`api.markSeen` は断られても例外を出さない（今の `response.ok ? … : null` を保ち、`fetch` の失敗も `null`）。"
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "経路の引き直しは、問題の最も少ない回を返す（`views/graph/layout.js` の `routeLayout`）"
		text: """
			- `ROUNDS = 10`（試作の8回から。線284本の構造で9回が要った）。
			- 各回で、収まった（広げる隙間も高くする辺もない）ならその回を返す。収まらなければ、`router.js` の `audit` で問題の数（箱への当たり、自分の箱、車線の重なり、斜め、出入りの衝突、親子の線に沿う重なり、経路の失敗の和）を数え、最も少ない回（同じなら早い回）を覚え、上限で止まったらその回を返す。隙間を広げると別の通り道が混み、回を重ねると、一度は0件だった配置が崩れることがあるため。
			- 返す形に `problems` を足す（ほかの項目は今までどおり。`iters` は回した数）。
			- 線の検査のテストの代表のデータに `generated(250, seed=15)` と `generated(250, seed=18)` を足す（直す前の8回・最後の回では車線が重なる）。
			"""
		satisfies: ["R-06"]
	}
}

compatibility: "構造の API の `assurance` と `branch` に値が入る（項目と意味は #532 のまま）。画面の道、コマンド、状態の置き場、配布資産の文書は変えない。0.6.0 の移行の注記には「構造の図とボードに保証レベルとブランチの印が出るようになった」とだけ書けばよい。"

risks: [
	"CUE の Scope が多いカタログでは、サーバーを立てた後の最初の構造の要求で `cue` を Scope の数だけ走らせる（spec-dock では35件、1件 約10ms）。3秒の上限で切り、残りは次の要求で読む",
	"経路の引き直しが最大10回になり、収まらない構造では各回で検査を数えるため、線の多い構造（284本）で配置と経路に約2.3秒かかる",
]
