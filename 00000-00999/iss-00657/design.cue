package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"点の組の間・形・速さ・刻みを `MOTION` の数だけで決め、CSS はその写しにする（一緒に直す1か所）",
	"iss-00646 の描き方（線ごとの SVG、切り替えの絵、止める仕組み）の形を変えず、枚数と中の点の線だけを変える",
	"止まった1枚の絵に、向きの分かる組の形を持たせ、減らす設定でも向きを示す",
]

current: """
	（`92e26aff7`。iss-00648 のマージの後に、実装の前に読み直す）
	- `views/graph/command_motion.js`：`MOTION = {phases: 4, step: 2, tick: 0.05, pad: 4}`。`phaseDelay(i) = −(((phases − i) mod phases) · tick)`、`phaseOffset(i) = −step · i`。
	  `bodyHtml(link)` は `flow` の線に、光の下地だけの止めた SVG と、`phases` 枚の `<svg class="cl-svg cl-ph" data-ph="i" style="…;animation-delay:…s">` に `<path class="cl-line" d style="stroke-dashoffset:<off>px"/>` を1本ずつ置く。`endsHtml(link)` は `stubs` に同じ切り替えを付ける（iss-00648 の後は `stubs` が空で、切り替えの絵がない）。
	- `graph.css` の8節：`.gx .cl[data-state="flow"] :is(.cl-line, .cl-stub) { stroke-dasharray: 0.1 7.9; }`、`.gx .cl-ph { animation: sd-cmd-phase .2s steps(1, end) infinite; }`、`@keyframes sd-cmd-phase { 0% { opacity: 1; } 25% { opacity: 0; } 100% { opacity: 0; } }`、
	  `.gx .cr > i { …; animation: sd-cmd-ripple 2.4s ease-out infinite; }`、`.gx .cr .cr-b { animation-delay: 1.2s; }`、`.gx .cl.is-cmd-hl .cl-line { stroke-width: 3; }`、減らす設定の規則。
	- テスト：`tests/js/dashboard_graph_command_motion.mjs`（`MOTION`、遅延、ずれ、0〜0.4秒の見える枚）と `tests/unit/presentation/test_dashboard_graph_command_motion.py`、CSS と画面の検査（`tests/unit/presentation/test_dashboard_graph_command_screen.py` ほか、`4`・`0.05`・`.2s`・`7.9`・`2.4s` を固定している所）。
	"""

target: """
	- `MOTION = {phases: 12, step: 2, tick: 0.1, gap: 24, tail: 6, pad: 4}`。切り替えの絵の各々に、頭と尾の2本の点の線。
	- `graph.css`：組の間 24 の点、頭と尾の太さと不透明度、1.2秒の切り替え、3.6秒の波紋。
	- 止める仕組み、層の並び、端の層（iss-00648 の矢じりと縁）は変えない。
	"""

design: {
	"D-01": {
		title: "動きの数と点の線（command_motion.js）"
		text: """
			- `MOTION = {phases: 12, step: 2, tick: 0.1, gap: 24, tail: 6, pad: 4}`：切り替えの枚数、1枚ごとのずらし px、1枚を見せる秒、組の間 px（点の線の周期）、尾の頭からの後ろへの距離 px、外接の四角の余白 px。`phases · step = gap`（1周で組が1つ分進む）を保つ。速さ `step / tick` = 20px/秒、1周 `phases · tick` = 1.2秒。
			- `phaseDelay(i)`・`phaseOffset(i)` の式は今のまま（数だけが変わる。遅延 0、−1.1、−1.0、…、−0.1秒。ずらし 0、−2、…、−22px）。浮動小数の誤差を除くため、遅延は今のとおりミリ秒で丸める。
			- 切り替えの絵の中身 `dotsHtml(d, off)`（新しく `export`、純粋）：同じ道 `d` の点の線を2本、`<path class="cl-line cl-hd" d style="stroke-dashoffset:<off>px"/>` と `<path class="cl-line cl-tl" d style="stroke-dashoffset:<off + tail>px"/>`。点は道の距離 `k·gap − offset` に来るので、尾のずらしを `+tail` にすると尾は頭の `tail` px 後ろ（親の側）に来る。`off + tail` も `−0` を `0` に直す。
			- `bodyHtml(link)`：`flow` の線の切り替えの絵の中身を `dotsHtml(link.d, phaseOffset(i))` にする。ほかの形（止めた SVG、`g` の属性、四角、`wait`・`done`）は今のまま。
			- `endsHtml(link)`：今のまま（iss-00648 の後は `stubs` が空で切り替えの絵がない。`stubs` があるときの切り替えは今の1本の `cl-stub` のまま残し、組にしない。端の層の `stubs` は iss-00648 でなくなる）。iss-00648 のマージの後の形が設計と違えば、実装の前に統括に知らせる。
			- 四角の余白 `pad` 4 は、頭の点の半径（選んだ線で 2.25）と光の下地の半分（3）より大きいので変えない。
			"""
		satisfies: ["R-01", "R-02", "R-04", "R-05", "F-01"]
	}
	"D-02": {
		title: "CSS（graph.css の8節）"
		text: """
			- 点の線：`.gx .cl[data-state="flow"] :is(.cl-line, .cl-stub) { stroke-dasharray: 0.1 23.9; }`（周期 `gap` 24）。`wait` は今の `0.1 7.9` のまま（止まった点線は流れる線と区別する）。
			- 組：`.gx .cl-hd { stroke-width: 3.5; }`、`.gx .cl-tl { stroke-width: 2; opacity: .45; }`、選んだ線：`.gx .cl.is-cmd-hl .cl-hd { stroke-width: 4.5; }`・`.gx .cl.is-cmd-hl .cl-tl { stroke-width: 3; }`（今の `.gx .cl.is-cmd-hl .cl-line { stroke-width: 3; }` の後に置き、詳しさを同じかそれ以上にして勝たせる）。色と丸い端は今の `.cl-line` の規則のまま。
			- 切り替え：`.gx .cl-ph { animation: sd-cmd-phase 1.2s steps(1, end) infinite; }`、`@keyframes sd-cmd-phase { 0% { opacity: 1; } 8.334% { opacity: 0; } 100% { opacity: 0; } }`。1/12 = 8.3333…% を少し上に丸め、隣の絵と見える区間が隙間なく（重なりは 1.2秒の 0.0007% ＝ 約 8µs で、どのコマにも出ない）つながるようにする。
			- 波紋：`.gx .cr > i { …; animation: sd-cmd-ripple 3.6s ease-out infinite; }`、`.gx .cr .cr-b { animation-delay: 1.8s; }`。keyframes と大きさは今のまま。
			- 止める規則・減らす設定・層の規則は今のまま（減らす設定は `data-ph="0"` の1枚を見せ、その中の頭と尾が向きを示す）。
			- 8節の先頭の注記と、点の規則の上の注記（今の『点の1周は 8px…40px/秒』）を、新しい数（組の間 24px、頭と尾、12枚 × 0.1秒、20px/秒。`MOTION` の写しで一緒に直す）に書き換える。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-05"]
	}
	"D-03": {
		title: "テスト"
		text: """
			- node（`tests/js/dashboard_graph_command_motion.mjs`）：時刻の表を `phases · tick` の2周（0〜2.4秒、0.01秒刻み）にし、見える区間を keyframes の写し（1周の 1/phases）から計算する。`dotsHtml` の出力を返す。
			- Python（`test_dashboard_graph_command_motion.py`）：`MOTION` の値、遅延と ずらし の12個、どの時刻も見える絵がちょうど1枚で、ずらしが 0.1秒ごとに −2 ずつ進み 1.2秒で戻ること、`bodyHtml` の `flow` の線が止めた SVG 1つと切り替えの SVG 12個で、各々に `cl-hd` と `cl-tl` の2本があり尾のずらしが頭 +6 であること、属性のエスケープ。
			- CSS の静的な検査（今の iss-00646 の検査を直す）：`0.1 23.9`、`sd-cmd-phase 1.2s steps(1, end)`、keyframes（opacity だけ、8.334%）、頭と尾の太さと不透明度、選んだ線の規則、`sd-cmd-ripple 3.6s ease-out`、`1.8s`。`MOTION` と CSS の写しの数が合うことを、CSS から数を読んで比べる（`phases · tick` と 1周の秒、`gap` と dasharray の和、`1/phases` と keyframes の割合）。
			- 画面（偽の DOM）：流れる線1本で、本体の層の SVG が 13（止めた1 ＋ 切り替え12）、`motion.phases` が 12。今のほかの期待は変えない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05"]
	}
	"D-04": {
		title: "測りと実機の確かめ"
		text: """
			iss-00646 の D-06 と同じ試しのサーバー（隔離した venv、状態の置き場の写し、別のポート、`--tailscale`、orca-web を GET で読むだけの中継）と headless Chrome（`--disable-features=MacAppCodeSignClone`、閉じるときは CDP の `Browser.close`）で：

			- 前（iss-00648 のマージの後の `origin/main`）と後のサーバーを並べ、同じ台本で、横断の構造と spec-dock の構造の図の動きありと減らす設定の TaskDuration を交互に3回ずつ測る。流れる線と切り替えの絵の数も書く。
			- 連続の写し：1440×900 で、流れる線の周りを、`document.getAnimations()` の `currentTime` をそろえて 0.1秒ずつ進めた 12枚（前は 0.05秒ずつ 4枚と、0.1秒ずつの 10枚）を、前と後で並べた絵にする。明・暗、減らす設定の1枚も。
			- `specdockEdgeAudit()`、`specdockCmdAudit()`（`boxOverlaps`・`edgeOverlaps`・`heads`・`spotDrift`・`motion`）、ブラウザーのエラー。
			- 流れる線が足りないときは、統括に試しのエージェントを頼む。
			"""
		satisfies: ["R-01", "R-02", "R-04", "R-05"]
	}
	"D-05": {
		title: "Epic epic-00615 の文書"
		text: """
			- requirement.cue：R-05 の text の『点を 2px ずつずらした止めた絵4枚…一様に 40px/秒』を『組の間 24px の大小2つの点の組を、2px ずつずらした止めた絵12枚の切り替え（0.1秒ごと）で一様に 20px/秒で流す（iss-00657）』に書き換える。波紋の時間を足す。decisions に、この Issue の決定の1行を足す（前の行は消さない）。
			- design.cue：D-04 の動きの行を同じ内容に書き換え、詳細は iss-00646 と iss-00657 の設計を指す。番号と `satisfies` は変えない。
			- 書き換えたら `spec-dock scope check epic-00615` を通す。
			"""
		satisfies: ["R-02"]
	}
}

compatibility: "表示だけの変更。モデル、API、層の class と並び、`specdockCmdAudit` の項目は同じ。切り替えの絵の数（4 → 12）と中の点の線の数（1 → 2）、点と波紋の時間が変わるので、それを固定している今のテストの期待を直す。"

risks: [
	"合成スレッドのレイヤーが、流れる線1本につき 5 から 13 に増える。GPU のメモリと合成の仕事が増える。TaskDuration（主スレッド）で受入を確かめ、超えたら枚数（例えば 0.12秒 × 10枚 × 2.4px）を見直すか統括に問う。",
	"keyframes の 8.334% は 1/12 の丸め。隣の絵と約 8µs 重なるが、どのコマにも出ない。隙間（両方が消える時間）にはしない。",
	"組の間を広げると、短い線（24px 未満）では、点が見えない時間がある（F-01。光の下地は見える）。",
]
