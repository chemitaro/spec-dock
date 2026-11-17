package spec

// 設計（Epic）。型 specdock/v1。

design: {
	"D-01": {
		title:     "状態の色の札と印の一元の置き場"
		text:      "`app.css` の `--sd-<状態>` の札だけが色を持ち、`core/ui.js` の STATES と stateIcon が形を持つ。ほかの画面はそれを使う。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "plan.cue の進み具合の読み取りと覚え方"
		text:      "`application/dashboard_progress.py` が作業中の Issue の plan.cue を `cue export -e steps` で読み、時刻と大きさで覚える。構造と詳しい画面の API の各 Scope に `progress` を足す（画面用、非契約）。読めないときは null。"
		satisfies: ["R-02", "F-01"]
	}
	"D-03": {
		title:     "最上位の棚詰め"
		text:      "`views/graph/layout.js` の childrenBlock が、行の切れ目の候補をすべて試し、倍率 = min(見える幅/全体の幅, 見える高さ/全体の高さ) が最大の切れ目を採る。graph.js が図の領域の幅と高さを渡す。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title:     "配線の寄せと広げを通り道ごとに見積もる"
		text:      "`views/graph/router.js` の nudgePass が、線分ごとに自分の通り道の中の鎖だけで広げの量と組を求める。線の多い入口の辺は 8px おき。寄せの範囲を線分を含むいちばん内側の枠に限り、検査に frameExits を足す。"
		satisfies: ["R-04"]
	}
	"D-05": {
		title:     "0.9.0 のリリースと配布"
		text:      "版の番号、migration.md の「0.9.0 への更新」（0.8.0 の節の訂正を含む）、static-inventory の既知の古い版、0.8.0 からの更新の統合テスト。タグの後に統括が導入と配布を行う。"
		satisfies: ["R-05"]
	}
	"D-06": {
		title:     "欄の見出しの1行目と、足すときだけの帯"
		text:      "`views/_shared/panel.js` の見出しを、祖先のパンくずと今の ID・番号・種類の行（右に状態の札・エージェントの印・Orca で開く・閉じる）と題名にする。帯は `panel_logic.js` の `headerBand` が、理由が状態の名前のほかに何かを足すときと動きなしがあるときだけ返す。枠を新しいタブで開く印は SCOPE_TABS の `open` でタブの行の右端に置く（詳細は iss-00656 の design.cue）。"
		satisfies: ["R-06"]
	}
}

compatibility: "公開の CLI と JSON の契約は変わらない。API に非契約の `progress` が足され、`revision` が作業中の Issue の plan.cue の書き換えでも変わる。"
