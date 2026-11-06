package spec

schema: "specdock/v1"

assurance: {
	level:  "light"
	reason: "テストの測り方と、ダッシュボードの小さな見た目の直し。ユーザーの保存データも公開の契約も変えず、PR を戻せば元に戻る"
}

purpose: "負荷が高い PC でも落ちないテストにし、ダッシュボードの細かい見た目の不具合 4 件を直す"

background: """
	親は epic-00080（小さな不具合の直し）。統括が 2026-11-05 に、負荷の高い PC で `test_the_250_scope_structure_routes_within_a_second`（上限 1000ms。負荷 40〜128 で 1379〜2060ms）と
	`test_issue440_g3_worktree_bootstrap` の 0.1 秒の timeout のテストが main でも落ちることと、ブラウザーで見たダッシュボードの見た目の不具合 4 件を見つけた。CI では通る。
	作業メモの 2（`migration.md` の食い違い）はこの Issue では直さない（次の版 0.9.0 のリリースの Issue が新しい節で正す）。
	"""

includes: [
	"時間を見る 2 つのテストを、負荷に強い測り方にする",
	"`/favicon.ico` の 404、Scope が 0 件の札、390px の図の枠の線",
]

excludes: [
	"`migration.md` と版の番号（0.9.0 のリリースの Issue が行う）",
	"配線の経路探索そのものの速さの改善",
]

requirements: {
	"R-01": {
		title: "構造の図の経路探索の時間のテストが、負荷に強い"
		text:  "性能の退行を見張る意味は残したまま、PC の負荷で時間が伸びても落ちない。上限をただ大きくしない。"
		acceptance: [
			"時間は node の CPU 時間（user+system）で測り、3 回のうちの最小を採る。上限 1000ms は変えない",
			"`yes > /dev/null` を CPU の数の 4 倍走らせた状態でも、`test_the_250_scope_structure_routes_within_a_second` が通る",
		]
	}
	"R-02": {
		title: "bootstrap の timeout のテストが、負荷に強い"
		text:  "timeout は Git の事前確認も含めて数える。0.1 秒では、負荷が高いと hook が始まる前に切れて `started` が偽になる。"
		acceptance: [
			"timeout を 1.0 秒にし、hook はそれより長く（2 秒）動くようにする。確かめる内容（部分の効果が残る、子のプロセスの群れが止まる）は変えない",
			"負荷をかけた状態でも `tests/cli_runtime/test_issue440_g3_worktree_bootstrap.py` が通る",
		]
	}
	"R-03": {
		title: "ダッシュボードが `/favicon.ico` の 404 を出さない"
		acceptance: [
			"`GET /favicon.ico` が 200 で SpecDock の印の SVG を返す",
			"ダッシュボードのページが `<link rel=\"icon\">` で同じ印を指し、ブラウザーの通信に 404 が出ない",
		]
	}
	"R-04": {
		title: "Scope が 0 件のリポジトリの札に、「Scope がない」と示す"
		acceptance: ["横断の概況で、Scope が 0 件のリポジトリの札に「Scope はまだありません」と出る（見出しだけで空にならない）"]
	}
	"R-05": {
		title: "390px の幅で、状態の札の帯の下に図の枠の線が見えない"
		acceptance: ["390px の幅の構造の図で、状態の札の帯の下は帯の背景で隠れ、図の領域は帯の下から始まる"]
	}
}

failures: {
	"F-01": {
		title: "上限を緩めただけで、性能の退行を見逃す"
		text:  "CPU 時間と最小値で負荷の影響を除き、上限は 1000ms のままにする。"
	}
}

decisions: [
	"(c) 文書の画面の目次の背景が切れる、は不具合ではなかった。統括の 2026-11-05 の写しは、ページ全体を 1 枚に撮る方法（captureBeyondViewport）で、sticky の目次が画面の高さ分しか写らなかった見かけだった。main（0.8.0）でも切れておらず、変更しない（統括の確認、2026-11-06）。",
]
