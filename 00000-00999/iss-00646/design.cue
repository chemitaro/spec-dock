package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"点の流れと波紋を、合成スレッドで動く opacity・transform の CSS アニメーションだけにし、主スレッドの毎コマの仕事をなくす",
	"線ごとに外接の四角の SVG に分け、描き直しとレイヤーの範囲を小さくする",
	"止める仕組み（図を動かす間・画面の外・裏）を、両方の画面で同じ1つの部品にする",
	"線の道と模型（commandModel・crossModel）は変えず、描き方（HTML と CSS）だけを変える",
]

current: """
	- `views/graph/command_view.js` の `layersHtml(model, {width, height})` が、`.gx-cmd`（世界と同じ大きさの `<svg>`。link ごとに `<g class="cl">` の中に `cl-glow` と `cl-line`（`style="--cl-len:<len>px"`））、
	  `.gx-cmd-top`（同じ大きさの `<svg>`。link ごとの `<g class="cl">` に `cl-stub` と `cl-dot`、帯の外の波紋 `<g class="cr" data-agent>` に円 `cr-a`・`cr-b`）、
	  `.gx-band`（帯の項目と、帯の中の波紋の `<svg class="gx-band-cr" width="1" height="1">`）の HTML を返す。`graph.js` と `allgraph.js` の `drawCommand` がこれを世界に置く。
	- `graph.css` の8節：`.gx .cl[data-state="flow"] :is(.cl-line, .cl-stub) { stroke-dasharray: 0.1 7.9; animation: sd-cmd-flow 2.5s linear infinite; }`、`@keyframes sd-cmd-flow`（`stroke-dashoffset` 0 → −`--cl-len`）、
	  `.gx .cr circle { …; transform-box: fill-box; transform-origin: center; animation: sd-cmd-ripple 2.4s ease-out infinite; }`、`.gx .cr .cr-b { animation-delay: 1.2s; }`、減らす設定の規則。
	- `CV.paintCmdSel(world, model, sel)` は `.gx-cmd, .gx-cmd-top, .gx-band-cr` に `has-cmd-sel`、`.gx-cmd .cl, .gx-cmd-top .cl` と `.gx-cmd-top .cr, .gx-band-cr .cr` に `is-cmd-hl`・`is-cmd-off` を付ける。
	- 両方の画面の `applyT()` が世界の `transform` を書く。図を動かす操作はすべてここを通る。
	"""

target: """
	- 新しい `views/graph/command_motion.js`（純粋な関数）：道の外接の四角、切り替えの定数と遅れ、link ごとの本体・端の HTML、波紋の HTML。
	- `command_view.js`：`layersHtml` がそれを使って入れ物の `div` に並べる。止める仕組み `createMotion(view)`（DOM の部品）。
	- `graph.js`・`allgraph.js`：`createMotion` を持ち、`applyT()` で `moved()`、層を描いたら `watch(world)`、消したら `watch(null)`、画面を離れたら `stop()`。`specdockCmdAudit()` に `motion`。
	- `graph.css`：点の切り替え・波紋の輪・止める印・減らす設定の規則。
	"""

design: {
	"D-01": {
		title: "描き方の純粋な計算（新しい graph/command_motion.js）"
		text: """
			DOM を使わない ES module。node のテストで確かめる。

			- `MOTION = {phases: 4, step: 2, tick: 0.05, pad: 4}`（切り替えの枚数、1枚ごとのずらし px、1枚を見せる秒、外接の四角の余白 px）。点の速さは `step / tick` = 40px/秒、1周 `phases · tick` = 0.2秒（= 点の周期 8px を `step` で割った枚数 × tick）。
			- `boxOf(ds, pad = MOTION.pad, dots = [])` → `{x, y, w, h}`：道の文字列 `ds`（`M x y C x y x y x y` と `M x y L x y …` の形。数を2つずつ点として読む）と点 `dots`（`{x, y, r}`、半径の分だけ広げる）のすべての点の最小・最大に `pad` を足し、`x`・`y` は切り捨て、右端・下端は切り上げた整数の四角。三次ベジェは制御点の凸包の中にあるので、この四角は道を必ず含む。点が1つもなければ `null`。
			- `phaseDelay(i)` → 秒：`−(((phases − i) mod phases) · tick)`。i 枚目は、時刻 t の `t mod 0.2` が `[0.05·i, 0.05·(i+1))` のときに見える（切り替えの keyframes は 0〜25% で不透明度 1、25〜100% で 0、`steps(1, end)`）。
			- `phaseOffset(i)` → px：`−step · i`（ずらし 0、−2、−4、−6。負のずらしで点は道の向き、つまり親から子へ進む）。
			- `svgOpen(box, cls, extra)`：`<svg class="<cls>" style="left:<x>px;top:<y>px<extra>" width="<w>" height="<h>" viewBox="<x> <y> <w> <h>" aria-hidden="true">`。
			- `bodyHtml(link)`：本体の層の HTML。`<svg class="cl-svg">` の中に `<g class="cl" data-id data-parent data-child data-state>` と `cl-glow`（どの状態も）と、`flow` でなければ `cl-line`。`flow` なら続けて4つの `<svg class="cl-svg cl-ph" data-ph="i" style="…;animation-delay:<phaseDelay(i)>s">` に、同じ `g` の属性と `<path class="cl-line" d style="stroke-dashoffset:<phaseOffset(i)>px"/>`。四角は `boxOf([d])`。
			- `endsHtml(link)`：端の層の HTML。`<svg class="cl-svg">` の中に `<g class="cl" data-id data-state>` と、`flow` でなければ stubs（`cl-stub`）と、端の点 `<circle class="cl-dot" cx cy r="2.5"/>`。`flow` で stubs があれば、続けて4つの `cl-ph` の SVG に、ずらしを付けた stubs。四角は `boxOf(stubs, pad, [{x: to.x, y: to.y, r: 2.5}])`。
			- `rippleHtml(r)`：`<span class="cr" data-agent="<agent>" style="left:<x>px;top:<y>px"><i class="cr-a"></i><i class="cr-b"></i></span>`（中心の座標。輪の大きさは CSS）。
			- 属性の値は今と同じく `esc` で守る（`marks.js` の `esc` を使う）。`--cl-len` は使わなくなるので書かない。
			"""
		satisfies: ["R-01", "R-02", "R-05"]
	}
	"D-02": {
		title: "層の HTML（command_view.js の layersHtml）"
		text: """
			`layersHtml(model)`（`{width, height}` は受け取っても使わない）が返す `{cmd, top, band}`：

			- `cmd`：`<div class="gx-cmd" aria-hidden="true">` ＋ link ごとの `bodyHtml` ＋ `</div>`。
			- `top`：`<div class="gx-cmd-top" aria-hidden="true">` ＋ link ごとの `endsHtml` ＋ 帯の外の波紋の `rippleHtml` ＋ `</div>`。
			- `band`：今の帯の HTML のまま、帯の中の波紋の入れ物だけを `<div class="gx-band-cr" aria-hidden="true">` ＋ `rippleHtml` ＋ `</div>` にする。
			層の並び（`.gx-cmd` を最後の枠の後、`.gx-cmd-top` を依存の線の前、`.gx-band` を最後）と `removeLayers`・`LAYERS` は今のまま。`paintCmdSel` は選択子を変えずに、同じ `data-id` のすべての `g.cl`（本体・4枚・端）と `.cr` に class を付ける。
			"""
		satisfies: ["R-02", "R-05"]
	}
	"D-03": {
		title: "止める仕組み（command_view.js の createMotion）"
		text: """
			`createMotion(view, {quiet = 300} = {})` → `{moved(), watch(world), stop(), state()}`。両方の画面が1つずつ持つ。

			- `moved()`：`view` に class `is-still` を付け（付いていなければ）、前の時計を消して `quiet` ms の時計を置く。時計が来たら、ページが裏でなければ `is-still` を外す。
			- 裏：`document` の `visibilitychange` で、`hidden` なら `is-still` を付け、表に戻ったら、時計が残っていなければ外す。
			- `watch(world)`：前の IntersectionObserver を切り、`world` があれば、`root: view`・`threshold: 0` の IntersectionObserver で `world` の中の `.cl-ph` と `.cr` を見張る。知らせのたびに、重ならないものに class `is-off` を付け、重なるものから外す。`IntersectionObserver` がなければ見張らない（F-01）。
			- `stop()`：見張りを切り、時計を消し、`visibilitychange` の聞き手を外し、`is-still` を外す（F-02）。
			- `state()` → `{phases, ripples, off, still}`：見張っている切り替えの絵と波紋の数、`is-off` の数、`is-still` の有無（`specdockCmdAudit` の `motion`）。
			止めるのは CSS（D-05）。この部品は class を付け外しするだけで、アニメーションを JS で動かさない。
			"""
		satisfies: ["R-03", "R-04", "F-01", "F-02"]
	}
	"D-04": {
		title: "両方の画面のつなぎ（graph.js・allgraph.js）"
		text: """
			- 画面を開くとき（`mount` で `V.el`・`A.el` を作った後）に `createMotion(view)`、離れるとき（今の後始末）に `stop()`。
			- `applyT()` の最後に `moved()`。
			- `drawCommand` の最後に `watch(world)`、`clearCommand` で `watch(null)`。
			- `cmdAudit()`（両方の画面の `window.specdockCmdAudit`）の戻りに `motion: state()` を足す（ほかの項目は今と同じ）。
			"""
		satisfies: ["R-03", "R-04", "F-02"]
	}
	"D-05": {
		title: "CSS（graph.css の8節）"
		text: """
			- 層の入れ物：今の `.gx .gx-world > .gx-cmd, .gx .gx-world > .gx-cmd-top`（position absolute、left 0、top 0、overflow visible、pointer-events none）と z-index 1・3 はそのまま。足す：`.gx .cl-svg { position: absolute; overflow: visible; }`。
			- 点：`.gx .cl[data-state="flow"] :is(.cl-line, .cl-stub)` は `stroke-dasharray: 0.1 7.9` だけ（アニメーションを外す）。`wait`・`done` は今のまま。`@keyframes sd-cmd-flow` を消す。
			  `.gx .cl-ph { animation: sd-cmd-phase .2s steps(1, end) infinite; }`、`@keyframes sd-cmd-phase { 0% { opacity: 1; } 25% { opacity: 0; } 100% { opacity: 0; } }`（4枚 × 0.05秒、MOTION の写し。一緒に直す）。
			- 波紋：`.gx .cr { position: absolute; width: 15.5px; height: 15.5px; margin: -7.75px 0 0 -7.75px; }`、
			  `.gx .cr > i { position: absolute; inset: 0; box-sizing: border-box; border: 1.5px solid var(--sd-cmd); border-radius: 50%; animation: sd-cmd-ripple 2.4s ease-out infinite; }`（今の半径 7・縁 1.5 の円と同じ外径 15.5・内径 12.5）、`.gx .cr .cr-b { animation-delay: 1.2s; }`、`@keyframes sd-cmd-ripple` は今のまま（`transform: scale(.4) → scale(2.2)`、`opacity: .9 → 0`）。
			- 止める：`.gx .gx-view.is-still :is(.cl-ph, .cr > i), .gx .cl-ph.is-off, .gx .cr.is-off > i { animation-play-state: paused; }`。
			- 減らす設定（今の `@media (prefers-reduced-motion: reduce)` の中）：`.gx .cl-ph { animation: none; opacity: 0; }`、`.gx .cl-ph[data-ph="0"] { opacity: 1; }`、`.gx .cr > i { animation: none; transform: scale(1.4); opacity: .6; }`、`.gx .cr-b { display: none; }`。
			- 指揮の選び：`.gx .has-cmd-sel .cl.is-cmd-off, .gx .has-cmd-sel .cr.is-cmd-off { opacity: .15; }`・`.gx .cl.is-cmd-hl .cl-line { stroke-width: 3; }` は今のまま。
			- 色は `--sd-cmd`・`--sd-cmd-glow` と今の変数だけ。`<animate`・`animateMotion`・canvas・`blur(` を使わない（今の検査）。
			"""
		satisfies: ["R-01", "R-03", "R-04", "R-05"]
	}
	"D-06": {
		title: "測りと実機の確かめ"
		text: """
			試しのサーバー（この worktree の候補を隔離した venv に入れ、状態の置き場の写しと別のポート、`--tailscale`）と headless Chrome（`--disable-features=MacAppCodeSignClone`、閉じるときは CDP の `Browser.close`）で：

			- 統括の台本 `perf-measure.mjs` と同じ条件（1440×900、deviceScaleFactor 2、読み込みの15秒後から10秒の TaskDuration）で、横断の構造と spec-dock の構造の図を、直す前（`2fa809271` 相当のサーバー）と後で、それぞれ動きありと減らす設定で測る。線が画面に入っている場合（単体の図の初めの見え方）と、入っていない場合（横断の初めの見え方）を区別して書く。
			- ドラッグ：CDP の `Input.dispatchMouseEvent` で約4秒動かす間の、50ms を超える長いタスクの数と最長、1秒あたりのコマの数、TaskDuration。
			- `specdockEdgeAudit()` の違反0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、`spotDrift` ≤ 0.4、`motion` の数え。
			- 写し：両方の画面、1440 × 明・暗で、線・点・波紋の拡大を、直す前と後で並べる。点の流れは、0.05秒ずつずらした写しで向きを確かめる。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-05"]
	}
}

compatibility: """
	組がないときの世界の HTML は今と同じ（層を置かない）。線の道と模型、`specdockCmdAudit` の今の項目、層の class と重なりの順は今と同じで、`motion` の項目が足される。
	層の中の HTML（SVG の数と形、波紋の要素）は変わるので、それを固定している今のテスト（iss-00616・iss-00617 の画面と CSS の検査）は、この設計に合わせて直す。
	"""

risks: [
	"合成スレッドのレイヤーが線ごとに5つ（本体1、切り替え4）と端の層に増える。線が多いとき GPU のメモリが増える（今の線は10本ほどで、試作で問題は見えない）。",
	"切り替えの4枚は同じ道を重ねるので、どの時刻も1枚だけが見えることを、keyframes と遅れの計算（D-01）で保つ。ずれると点が二重に見える。",
	"点の速さが線の長さによらず一様（40px/秒）になる。統括が決めた（『指令が流れている』感じを保つため 20px/秒ではなく 40px/秒）。",
]
