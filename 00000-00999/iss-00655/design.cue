package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"見分けとキーの写しを、DOM のない純粋な関数にして node で表のテストをする",
	"両方の画面のつなぎを、1つの bind の関数と、各画面の4つの口（pan・zoomAt・zoomCenter・fit）にする",
	"今の口（`applyT`）を通すので、iss-00646 の止める扱いと横断の構造の `A.moved` は変えずに保つ",
]

current: "両方の画面が、wheel の処理（ctrl・meta で拡大、なければ動かす）を写して持ち、矢印キー・`+`・`-`・`0` を扱わない。"
target:  "新しい `views/graph/view_input.js` が見分け・写し・つなぎを持ち、両方の画面の `bindView` は、その `bindViewInput` を呼ぶ。今の wheel の処理は消す。"

design: {
	"D-01": {
		title: "wheel の見分け（純粋な関数 `wheelKind(e)`）"
		text: """
			新しい `src/spec_dock/assets/dashboard/views/graph/view_input.js`。DOM を読まない。`e` は wheel のイベント（または同じ名前の値を持つただの物）。上から順に決める：
			1. `ctrlKey` か `metaKey` → `"pinch"`（トラックパッドのピンチ。Windows の Ctrl＋ホイールも同じ扱いで、今と同じ）。
			2. `shiftKey` → `"hpan"`（横に動かす）。
			3. `deltaMode`（必ず `wheelDeltaY` より先に読む。Firefox の決まり）が 1 か 2 で、`deltaX` が 0 → `"wheel"`（マウスのホイール。確か）。`deltaX` が 0 でなければ（Firefox のチルト・横のホイール）→ `"pan"`（今と同じく横に動く。量は D-02 で画素に直す）。
			4. `deltaX` が 0 で、`wheelDeltaY` が数で 0 でなく、`wheelDeltaY % 120 === 0` → `"wheel?"`（マウスのホイールらしい。弱い）。
			5. それ以外 → `"pan"`（見分けられない値を含む。F-01）。

			代表の値の表（テストの表。値は、ブラウザーの決まり（Firefox の行の単位、Chromium・WebKit のマウスのホイールの1刻み = `wheelDelta` 120、トラックパッドは画素の `deltaY` と、その −3倍の `wheelDeltaY`）から作った合成の値で、実機で測ったものではない。実機の Chrome では CDP の値を S-04 で測って report.md に書く）：
			| 場面 | 値 | 種類 |
			|---|---|---|
			| Chrome macOS・Windows、マウスのホイール | deltaMode 0、deltaY ±100（Windows）・±4〜±40（macOS の加速）、deltaX 0、wheelDeltaY ∓120・∓240 | wheel? |
			| Safari macOS、マウスのホイール | deltaMode 0、deltaY ±4、deltaX 0、wheelDeltaY ∓120 | wheel? |
			| Firefox macOS・Windows、マウスのホイール | deltaMode 1、deltaY ±1・±3、deltaX 0 | wheel |
			| Firefox、チルト・横のホイール | deltaMode 1、deltaY 0、deltaX ±1・±3 | pan |
			| Chrome・Safari macOS、トラックパッドの2本指 | deltaMode 0、deltaY 2.5・−7・12、deltaX 0〜±3、wheelDeltaY = −3·deltaY（−7.5・21・−36） | pan |
			| Chrome Windows、高精度タッチパッド | deltaMode 0、deltaY 小さな数、wheelDeltaY 120 の倍数でない | pan |
			| Firefox macOS、トラックパッド | deltaMode 0、wheelDeltaY なし（読まない値）か 120 の倍数でない | pan |
			| ピンチ（どれも） | ctrlKey true、deltaY ±1〜±10 | pinch |
			| Shift＋マウスのホイール（Chrome は deltaX に移す、Firefox は deltaMode 1 の deltaY） | shiftKey true | hpan |
			| 値がない（偽のイベント、今のテスト） | deltaMode・wheelDeltaY なし | pan |
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01"]
	}
	"D-02": {
		title: "wheel の写し（純粋な関数 `wheelAction(e, last, now, page)`）"
		text: """
			`last` は前の写しの `{kind, at}`（初めは null）、`now` は時刻（ms）、`page` は横の1ページの画素（図の面の幅）。返り値は `{act, kind, at}` で、`act` は次のどれか：
			- `{type: "zoom", f, x: e.clientX, y: e.clientY}`：`kind` が `pinch` なら `f = exp(−deltaY·0.01)`（今と同じ）。`wheel`・`wheel?` なら、刻み数 `n = min(WHEEL.maxSteps, max(1, round(|wheelDeltaY| / 120)))`（`wheelDeltaY` がないか `deltaMode` が 0 でないときは 1）、`f = WHEEL.step ^ (deltaY < 0 ? n : −n)`。`deltaY` が 0 なら `act` は null。`WHEEL = {step: 1.15, maxSteps: 2, stick: 200}`。
			- `{type: "pan", dx, dy}`：`pan` は `dx = −deltaX·u`、`dy = −deltaY·u`（今と同じ向き。`deltaMode` 0 では今と同じ量）。`hpan` は、`deltaX` が 0 でなければ `dx = −deltaX·u`、0 なら `dx = −deltaY·u`、`dy = 0`。`u` は `deltaMode` 0 で 1、1 で 16、2 で `page`。
			続きの扱い：`kind` が `wheel?`（弱い）で、`last.kind` が `pan` で、`now − last.at < WHEEL.stick` なら、`kind` を `pan` にする（トラックパッドの連続した動きの途中）。`wheel`・`pinch`・`hpan` は続きで変えない。返す `kind` は変えた後の値で、呼ぶ側はそれを次の `last` にする。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01"]
	}
	"D-03": {
		title: "キーの写し（純粋な関数 `keyAction(e)`）と、横取りしない場面（`ownsKey(e, view)`）"
		text: """
			`keyAction(e)`：`ctrlKey`・`metaKey`・`altKey`・`isComposing`・`defaultPrevented` のどれかがあれば null。`e.key` で：
			- `ArrowLeft` → `{type: "pan", dx: +d, dy: 0}`、`ArrowRight` → `dx: −d`、`ArrowUp` → `dy: +d`、`ArrowDown` → `dy: −d`。`d = KEYS.pan · (shiftKey ? KEYS.fast : 1)`、`KEYS = {pan: 80, fast: 4, zin: 1.25, zout: 0.8}`（世界の移動量。図の右を見る → は世界を左へ）。
			- `+`・`=` → `{type: "zoom", f: KEYS.zin}`、`-` → `{type: "zoom", f: KEYS.zout}`（中央で。ボタンと同じ倍率）、`0` → `{type: "fit"}`。テンキーも `e.key` が同じなので同じ。
			- ほか → null。

			`ownsKey(e, view)`：`e.target` を見る。DOM の `closest` だけを使う（偽の DOM で試せる）。
			- `target` がないか、`target.contains(view)`（`body`・`html`、画面の入れ物の `main#view`（`tabindex="-1"`。app.js の移動のたびに `focus()` される）など、図の面を包む要素）→ true（図の画面そのものにフォーカスがある）。
			- `target.closest("input, textarea, select, button, a[href], summary, iframe, [contenteditable]:not([contenteditable='false'])")` があれば false。
			- `view.contains(target)` なら true（図の面、中の箱・枠の見出し・帯のエージェント）。それ以外は false（欄・道具の棒など、図の面の外）。
			"""
		satisfies: ["R-04", "R-05"]
	}
	"D-04": {
		title: "つなぎ（`bindViewInput(view, ops)`）"
		text: """
			`ops = {active(), pan(dx, dy), zoomAt(f, x, y), zoomCenter(f), fit()}`。`x`・`y` は図の面の中の座標。
			- `view` の wheel（`passive: false`）：`preventDefault` し、`wheelAction(e, last, performance.now(), view.clientWidth)` の `act` を呼ぶ（`zoom` は `zoomAt(f, e.clientX − rect.left, e.clientY − rect.top)`、`pan` は `pan(dx, dy)`）。`last` を更新する。
			- `document` の keydown：`ops.active()` が false（画面が隠れている、画面がない）か、`ownsKey` が false なら何もしない。`keyAction(e)` が null なら何もしない。そうでなければ `preventDefault` し、`pan`・`zoomCenter(f)`・`fit()` を呼ぶ。
			- 返り値 `{dispose()}` は2つの見張りを外す。
			両方の画面の `bindView` は、今の wheel の見張りを消して `bindViewInput` を呼び、`dispose` でそれを外す。各画面の口：
			- graph.js：`pan(dx, dy)` は `V.tx += dx; V.ty += dy; applyT()`、`zoomAt`・`zoomCenter`・`fit` は今の関数。`active()` は `!!V.el && !V.el.view.hidden`。
			- allgraph.js：`pan` は `A.moved = true; A.tx += dx; A.ty += dy; applyT()`、ほかは今の関数（`A.moved` を付ける）。`active()` は `!!A.el && !A.el.view.hidden`。
			どれも `applyT()` を通るので、`motion.moved()`（iss-00646、`is-still`）が今と同じに呼ばれる。今の `onKey`（Escape・Enter・Space）はそのまま。
			"""
		satisfies: ["R-01", "R-04", "R-05", "R-06", "F-02"]
	}
	"D-05": {
		title: "操作の説明"
		text: """
			`.gx-view` の `aria-label` を、両方の画面で次にする（頭の名前は今のまま）：
			`構造の図。ドラッグ・2本指・矢印キーで移動、ホイール・ピンチ・+ と - で拡大・縮小、0 で全体`（横断は `横断の構造。…`）。
			"""
		satisfies: ["R-07"]
	}
	"D-06": {
		title: "実機の確かめ"
		text: """
			この worktree を隔離した venv に入れ、一時の状態の置き場で別のポート（18655）、`--tailscale` で立てる（常駐の 47800・8791 の設定、道具の環境には触れない）。headless でない Chrome を `--disable-features=MacAppCodeSignClone` で 1440×900 に開き、CDP で：
			- 両方の画面で、`Input.dispatchMouseEvent`（`mouseWheel`、deltaY −120・+120）の前と後の拡大率（`.zoomval`）と、カーソルの下の世界の点のずれ。そのとき届いた wheel の値（`deltaMode`・`deltaY`・`wheelDeltaY`）を記録する。
			- 小さな deltaX・deltaY の `mouseWheel`（例 deltaX 3、deltaY 7）：拡大率が変わらず、世界が動く（届いた値も記録）。CDP の値が `wheelDeltaY` 120 の倍数になって見分けの表と違えば、その事実を記録し、統括に問う。
			- `Input.dispatchKeyEvent` で → ↓ ← ↑、Shift+→、`+`、`-`、`0`：世界の transform と拡大率の前と後。
			- 両方の画面で `specdockEdgeAudit()` の違反0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、ブラウザーのエラー0。
			- 前と後の写し（`.workbench/iss-00655/shots/`）。閉じるのは CDP の `Browser.close`。
			"""
		satisfies: ["R-01", "R-02", "R-04", "F-02"]
	}
}

compatibility: "マウスのホイールは、動かすから拡大・縮小に変わる（本人の要望）。トラックパッド、ドラッグ、タッチ、ボタンは今のまま。API・保存は変わらない。PR を戻せば今の動きに戻る。"

risks: [
	"ブラウザー・OS・マウスの設定（加速、高精度のホイール）によっては、マウスのホイールが `wheelDeltaY` 120 の倍数にならず、動かすに倒れる（F-01 の側。今と同じ動き）。そのときは Ctrl＋ホイール・+ と - で拡大・縮小できる",
	"トラックパッドの動きの初めの1つがたまたま `wheelDeltaY` 120 の倍数（deltaY ±40）で deltaX 0 だと、1刻みだけ拡大・縮小する。続きの扱いで、動きの途中では起きない",
	"代表の値の表は、ブラウザーの決まりから作った合成の値で、本人の機械で測ったものではない。実機の Chrome の値は S-04 で記録する",
]
