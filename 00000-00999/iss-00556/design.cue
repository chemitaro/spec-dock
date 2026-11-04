package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"既定の表示で、開いた枠の中の進み具合（終わった Scope と終わった依存）を図に残す",
	"並びを活動順にし、依存の左右の段の考え方（前のものを左）を保ち、出ている終わった依存も左から右へ並べる",
	"前に保存した見せ方が新しい既定を打ち消さないようにする",
]

current: "`graph/layout.js` の `visibility` は、`showDone` か、開いているか、見える子を持つ Scope だけを出す。`DEFAULTS` は `{showDone: false, deps: \"wait\"}`。`byStageRank` は段、`rank`、番号の順で並べ、最上位は Initiative を先に `rank` の順。`graph.js` は `specdock.graph.v1` の `mode`・`showDone`・`deps`・`fold`・`legend` を読む。構造の API に最後に動いた時刻はない。"

target: "`visibility` は親が開いている終わった Scope も出す。`DEFAULTS.deps` は `\"all\"`。並びは段の中で活動順（枠は組と最近の順、箱は開いたものを推奨順、終わったものを最近の順）。見せ方は `specdock.graph.v2` に保存し、v1 からは一部だけ引き継ぐ。API の各 Scope に `active_at` がある。"

design: {
	"D-01": {
		title: "可視の判定（`graph/layout.js` の `visibility`）"
		text: """
			`visible(s) = showDone || s.state !== "done" || 見える子を持つ || context(s)`。
			`context(s)` は、親 `p = byId(s.parent_id)` があり（自分でなく）、`p.state !== "done"` か `p.id === focus` のとき真。
			- 終わった Epic の子は、親が終わっているので、開いた子孫がなければ出ない。終わった Epic は見える子がなく、今の `frameBlock` の畳んだ枠（`compact`）になり、画面の枠は配下すべての数（`tally`、完了 n/n）を示す（画面のコードは変えない）。
			- 範囲を絞った Scope の子は `context` が真になる。絞った Scope の孫より下は通常の規則に従う。
			- 親の循環は今の `seen` の守りで止まる。`index` の `kids` と `byId` を使い、親が構造にない Scope は親のない扱いにする。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "依存の線の既定（`DEFAULTS.deps = \"all\"`）"
		text: "`DEFAULTS` を `{mode: \"nest\", showDone: false, deps: \"all\", fold: true, focus: null}` にする。`pairs` は今のまま、図に出ている箱・枠・畳んだまとまりの間だけ線を作り、終わった依存は `done: true`（画面の `is-done`、薄い線）になる。`deps: \"wait\"` は今のまま終わった依存を除く。経路と線の検査（`router.js`、`routeLayout`）は変えない。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "活動順の並び（`graph/layout.js` の比べ方）"
		text: """
			`index` に、配下の要約を覚える `summary(id) -> {tier, recent}` を足す（循環は訪れた印で止める）。
			- `tier`：子があれば全子孫の状態で、なければ自分の状態で決める（親の状態はモデルが子から決めるため、親自身の状態では見ない）。作業中があれば 0、なければ着手できるがあれば 1、なければ開いたもの（止められている、不明）があれば 2、すべて終わっていれば 3。
			- `recent`：自分と配下の `active_at` の最大（ない Scope は無視。すべてなければ空。比べるときは空を最も古いとする）。
			比べ方 `byActivity(ix)(a, b)`：
			1. 組：開いた枠（`tier` 0〜2）、開いた箱、終わったもの（`tier` 3 の枠と終わった箱）の順。枠は「子を持つか、Issue でない」Scope。
			2. 開いた枠どうしは `tier`、`recent` の新しい順。開いた箱どうしは `rank`（Epic R-31）。終わったものどうしは、箱は `closed_at`（なければ `active_at`）、枠は `recent` の新しい順。
			3. 同じなら番号の小さい順。
			段：`childrenBlock` と木の `walk` は、枠ごとに段の種類を決める。終わった子を出す枠（`showDone`、親が開いている、絞った Scope。D-01 の `context` と同じ条件）では `stage.all`、それ以外（開いた子孫を持つ閉じた親）では `stage.open` を使い、どちらも値がなければ 1。終わった子を出す枠ではすべての子（開いたものと終わったもの）が出るので、`stage.all` の段は、出ている終わった依存を左から右へ並べる（片付けの候補として畳まれた子は、畳んだまとまりがその段に入る）。
			`childrenBlock` と木の `walk` は、この段の後にこの比べ方で並べる（`byStageRank` を段と `byActivity` にする）。最上位（`roots`）も `byActivity` で並べ、Initiative を先にする規則はやめる。入れ子の最上位の枠と、親のない箱（`loose`）の分け方は今のまま。
			"""
		satisfies: ["R-03", "F-01"]
	}
	"D-04": {
		title: "構造の API の `active_at`（`presentation/dashboard_api.py` の `scope_item`）"
		text: "`_active_at(scope, node)`：`scope.created_at`、`node.updated_at`（スナップショットの Issue の更新）、`scope.closed_at`、`scope.pr` の `created_at`・`merged_at`・`closed_at` のうち、`parse_timestamp` で読めるものの最大の元の文字列。読めないものは使わない。全部読めなければ `scope.created_at`。`scope_item` に `\"active_at\"` を足す（構造の API と詳しい画面の両方に出る）。"
		satisfies: ["R-04", "F-01"]
	}
	"D-05": {
		title: "見せ方の保存（`views/graph/prefs.js`、`graph.js`）"
		text: """
			DOM のない小さな部品 `views/graph/prefs.js` を足す。
			- `PREFS_KEY = "specdock.graph.v2"`、`LEGACY_KEY = "specdock.graph.v1"`。
			- `restorePrefs(current, legacy, defaults) -> {opts, legend}`：`current`（v2 を JSON として読んだ値。なければ `null`）があればそれを、なければ `legacy`（v1）から `mode`・`fold`・`legend` だけを使う。値ごとに型と範囲（`mode` は nest・tree、`deps` は all・wait・none、`showDone`・`fold`・`legend` は真偽）を確かめ、合わないものは既定にする。
			- `graph.js` の `loadPrefs` は2つのキーを読んで `restorePrefs` に渡し、`savePrefs` は v2 にだけ書く（v1 は消さない。前の版の画面に戻したときのため）。`localStorage` の例外と壊れた JSON は今のまま既定にする。
			"""
		satisfies: ["R-05", "F-02"]
	}
	"D-06": {
		title: "ボードの「終わった」の列"
		text: "`views/_shared/logic.js` の `boardColumns` は、すでに `closed_at` の新しい順、同じなら番号の大きい順に並べる。コードは変えず、node のテストで確かめる。"
		satisfies: ["R-06"]
	}
}

compatibility: "構造の API に項目を足すだけ。画面の既定の表示と並びが変わる（構造の図は、既定で、開いた親の中の終わった Scope と終わった依存の線を出し、活動順に並べる。前に保存した「終わったものも」と依存の線の選択は一度だけ既定に戻る）。この変化は、移行の注記の材料として PR の本文と統括への報告（worker_done）に書く。注記を書く版と文書（`migration.md`）は統括とリリースの Issue が決めて書き、この Issue では書かない。"
risks: [
	"終わった Scope と線が増え、経路の引き直しが収まらない組み合わせが出る。代表のデータとこのPCの実際のスナップショットの線の検査で確かめる",
	"活動順は時刻で変わるため、5秒ごとの更新で箱の位置が動くことがある。更新は `revision` が変わったときだけで、時刻は Issue と PR の変化でしか動かないので、動くのは変化があったときだけ",
]
