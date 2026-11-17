package spec

// 設計（Issue）。型 specdock/v1。

current: "このハーネス（`tests/js/dashboard_allgraph_command_screen.mjs`）は、画面の CSS が効いた状態を与えない。`views/allgraph.js` の `whenStyled` は、CSS が効く（`.gx` が position: absolute）まで requestAnimationFrame で待ち、`performance.now()` で3000ms を過ぎると打ち切って `initialView()` と `applyT()` を呼ぶ。偽の DOM では効いた状態にならないので、描くたびに待ちの連鎖が残り、どれも実時間の3000ms（ハーネスは偽の時計の進みも `performance.now` に足す）で打ち切られる。`A.el` はモジュールの変数なので、前の run で始まった連鎖も、次の run の画面で生き返って打ち切られる。それが motion run の step 1（偽の時計を400ms 進める）の中で起きると、`applyT()` が `motion.moved()` を呼んで is-still を付け、300ms 後に外す時計は偽の時計の上に残り、`shots[1].still` が True になる。ブラウザーでは CSS がすぐ効くので、待ちは1枚目の絵で終わる。"
target:  "動きを確かめる run（motion）と、最初の見え方を前提にする run（input、iss-00655）は、画面の CSS が効いた状態で描く。最初の見え方は最初の描画で決まり、前の run から残った待ちも、その run の最初の絵で効いた状態を見て終わる。実時間の打ち切りは、これらの run の結果に関わらない。"

design: {
	"D-01": {
		title:     "ハーネスの run.styled（CSS が効いた状態）"
		text:      "兄弟のハーネス（`dashboard_allgraph_screen.mjs`、`dashboard_graph_command_screen.mjs`）と同じ決まりで、run に `styled: true` があれば、`getComputedStyle` が `.gx` に position: absolute を返す。motion と input の run に付ける。画面のコードは変えない（利用者に見える不具合ではないため。F-01 は当たらない）。"
		satisfies: ["R-02", "F-01"]
	}
	"D-02": {
		title:     "原因の記録と実機の確かめ"
		text:      "各マージで単独10回の落ちた回数を測り、計測（applyT と whenStyled の打ち切りの記録）で仕組みを確かめて report.md に表で残す。1440×900 の Chrome で、読み込み・ドラッグ・ホイール・キーの後の is-still と絵の切り替えを確かめる。"
		satisfies: ["R-01", "R-03"]
	}
}

risks: ["styled の run では、最初の見え方の置き方が、待ちの打ち切りではなく最初の描画で決まる。input run の t0 の意味（最初の見え方）は、実際のブラウザーに近づく"]
