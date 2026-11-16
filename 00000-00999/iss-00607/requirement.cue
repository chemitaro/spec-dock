package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの構造の図の表示とブラウザーの保存だけを変え、データや操作には触れない。PR を戻せば元に戻る"
}

purpose: """
	構造の図（ホーム）の道具の帯から、依存の線の切り替え「待っている線｜すべての線｜線なし」をなくし、
	依存の線を常に「すべての線」の描き方で出す。見せる範囲は「全体・いま・これから」（iss-00603）で変えられるので、線の範囲の切り替えは要らない。
	"""

background: """
	iss-00556 で依存の線の既定を「すべての線」（終わった依存は薄く、待っている依存は目立つ）にし、iss-00603 で見せる範囲を1つの切り替えにまとめた。
	本人（2026-11-16）は、線の3つのボタンは要らないので削除し、「すべての線」を常にすることを求めた。
	統括の決定（依頼書、2026-11-16）：3つのボタンを消す。見えない相手との線は今どおり描かない。選んだ箱の線の強調と凡例は変えない。
	保存から deps をなくし、前の deps（wait・none）は読まずに捨てる。鍵の版は iss-00603 の v3 にならい仕様で決める。URL やほかの画面の deps の指定も見ない。
	色・字体はデザインシステムのまま。390px で道具の帯が今より詰まって収まることを確かめる。
	"""

includes: [
	"`views/graph.js` の道具の帯（線の切り替えの3つのボタン）とクリックの扱い、保存（`savePrefs`）",
	"`views/graph/layout.js` の依存の線（`pairs`）と DEFAULTS・options の `deps`",
	"`views/graph/prefs.js` の保存の形（`deps` をなくす）",
	"テスト（`tests/js/dashboard_graph_check.mjs`、`tests/js/dashboard_graph_toolbar.mjs`、`tests/unit/presentation/test_dashboard_graph_{js,range,toolbar}.py` ほか、`tests/fixtures/issue603/` の digest の扱い）",
]

excludes: [
	"見せる範囲（全体・いま・これから）、入れ子・木、拡大縮小、収める、状態の札の帯の動き",
	"箱を選んだときの線の強調（直接・間接・関係ない）と凡例の文",
	"線の色・太さ・薄さの見た目（今の「すべての線」の描き方のまま）",
	"構造の API とモデル、ほかの画面（ボード・時系列・Scope）",
	"配布の手引き・リリースノート（リリースの Issue で書く）",
]

requirements: {
	"R-01": {
		title: "道具の帯に依存の線の切り替えがない"
		text:  "「待っている線」「すべての線」「線なし」の3つのボタンと、それをまとめる role=group aria-label「依存の線」を、入れ子と木、すべての見せる範囲で出さない。ほかの道具（拡大縮小、収める、入れ子/木、見せる範囲）は今のままの順で残る。"
		acceptance: [
			"道具の帯の HTML に `data-act=\"deps\"`、aria-label「依存の線」、「待っている線」「すべての線」「線なし」の文字がない（入れ子・木 × 全体・いま・これから）",
			"道具の帯に 縮小・100%・拡大、収める、入れ子/木、見せる範囲の3つのボタンが今の順で残る",
		]
	}
	"R-02": {
		title: "依存の線は常にすべての線の描き方で出る"
		text: """
			図に出ている箱・枠・畳んだ塊どうしの依存は、終わった依存（待つ相手が終わった）も薄い線（is-done）で、待っている依存は目立つ線で、常に出る。
			layout に `deps` を渡しても結果は変わらない（wait・none の働きはない）。
			見せる範囲で見えない相手との線、これからで端が終わった Scope の線は、今どおり描かない。
			"""
		acceptance: [
			"全体・いまの layout（入れ子・木、幅 既定・374、配線の前後）が、iss-00603 で記録した直す前の digest（`tests/fixtures/issue603/layout-before.json` の deps all の組）と同じ。これからの線の既存のテストが通る",
			"layout に deps wait・none を渡しても、deps を渡さないときと同じ nodes・groups・edges になる",
			"終わった依存の線が is-done で出る（全体・いま）",
		]
	}
	"R-03": {
		title: "選んだ箱の線の強調と凡例は今のまま"
		text:  "箱を選んだときの直接・間接・関係ないの線の描き分けと、凡例の「待っている依存」「終わった依存」「直接の依存」「間接」の説明は変えない。"
		acceptance: [
			"凡例の HTML が直す前と同じ",
			"選んだ箱の線の強調のテスト（既存）が通る",
		]
	}
	"R-04": {
		title: "保存に deps がなく、前の deps は捨てる"
		text: """
			保存の鍵は `specdock.graph.v3` のまま（鍵の版は上げない。iss-00603 は項目の意味が変わったので版を上げたが、今回は項目を1つ捨てるだけで、残る mode・range・legend の意味は変わらないため）。
			書く値は `{mode, range, legend}` の3つの鍵だけ。版3の値に deps があっても読まず、次に書くときに消える。
			版2からの移し替え（mode・legend、showDone から range）と版1からの移し替え（mode・legend）は今のままで、deps は読まない。
			"""
		acceptance: [
			"範囲や表し方を押したあと、`specdock.graph.v3` に `{mode, range, legend}` の3つの鍵だけが書かれる",
			"restorePrefs の返す opts に deps がない（版3・版2・版1・壊れた値・なし）",
			"prefs.js と graph.js に deps の字がない",
		]
	}
	"R-05": {
		title: "実データで道具の帯と線が正しく見える"
		text:  "spec-dock と housing-lifecycle の実データで、道具の帯（1440・390、明暗）と線を、直す前と後で写す。色・字体はデザインシステムのままで、390px の道具の帯は直す前より短く（縦に詰まって）収まる。"
		acceptance: [
			"report.md に、直す前と後の写し（2つのリポジトリ × 1440・390 × 明暗）、道具の帯の大きさ（390px で直す前より短い）、edgeAudit の違反0、ブラウザーのエラー0がある",
			"graph.css に新しい色・字体の値がない",
		]
	}
}

failures: {
	"F-01": {
		title: "前に deps wait・none を保存した人も、線がすべて出る"
		text:  "版3・版2に deps wait・none が保存されていても、読み込んだ後の図は deps all と同じ線で描かれ、エラーは出ない。"
	}
}

constraints: [
	"URL とほかの画面には、もともと deps の指定がない（`core/route.js` は embed と画面の道だけ、graph.js の URL は focus だけ。2026-11-16 に確かめた）。見ないことは、graph.js が URL から deps を読まないことで満たす",
	"ダッシュボードの資産は static-inventory.json に載っていない（iss-00603 の記録）。sha256 が載る資産を変えるときだけ更新する",
]

decisions: [
	"3つのボタンを消し、すべての線を常にする（本人、2026-11-16。依頼書）",
	"見えない相手との線は描かない。選んだ箱の強調と凡例は変えない。保存から deps をなくし前の値は捨てる（統括、2026-11-16。依頼書）",
	"保存の鍵は v3 のまま（タスク担当、2026-11-16。依頼書の「仕様で決める」に基づく。理由は R-04）",
]
