package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

schema: "specdock/v1"

assurance: {
	level:  "light"
	reason: "画面の CSS と1か所の属性の小さな不具合の修正"
}

purpose:    "構造の図（と『横断の構造』）の指揮の帯の印から開くチャットを、Scope の欄のエージェントのタブと同じく、欄の本文の高さいっぱいに出す"
background: """
	本人の指摘（2026-11-17）：「main のチェックアウト」の帯のエージェントの印を押すと、右の欄にチャットが出るが、枠が欄の上の方に小さく出るだけで、欄の残りが空く。
	原因（タスク担当が確かめた）：帯の欄は `views/graph/command_view.js` の `renderAgentPanel` が `<div class="pn-body">` にじかに `iframe.sd-agent` を入れ、`data-tab` を付けない。
	`views/_shared/panel.css` の本文を縦の flex にする規則は `.pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"])` にだけ効くため、`.sd-agent` の `flex: 1` が効かず、iframe は既定の高さ（約 150px）のままになる。
	構造の図と『横断の構造』の両方が同じ `CV.renderAgentPanel` を使う。
	"""

includes: ["構造の図と『横断の構造』の帯の欄（同じ関数）", "回帰のテスト"]
excludes: ["Scope の欄のエージェントのタブ", "欄の部品（panel.js）の作り", "orca-web の埋め込みの中身"]

requirements: {
	"R-01": {
		title: "帯の欄のチャットの枠が、欄の本文の高さいっぱいに広がる"
		text:  "チャットを開けるとき、欄の本文はエージェントのタブと同じ縦の flex の規則に乗り、iframe が見出しの下から欄の下まで広がる。余白・角丸・縁取りはエージェントのタブと同じ。PC（右の欄）と狭い画面（下からの欄）の両方。"
		acceptance: [
			"1440×900 と 390×844 で、帯の印を押したときの iframe の高さが、欄の本文の高さから本文の上下の余白を引いた値とほぼ同じ（差 2px 以内）",
			"帯の欄の本文に `data-tab=\"agents\"` が付き、panel.css の縦の flex の規則（PC と狭い画面）に乗る（静的と偽の DOM のテスト）",
		]
	}
	"R-02": {
		title: "ほかの動きを変えない"
		text:  "「チャットを開けません。」の表示（余白も含む）、同じエージェントで開き直したときに読み込み直さない動き（iss-00616 D-04）、欄の引っぱりでの大きさ変え、狭い画面の下からの欄の形、線の検査を変えない。"
		acceptance: [
			"チャットを開けないとき、本文に `data-tab` が付かず、HTML が今と同じ",
			"今の構造の図と『横断の構造』の指揮の画面のテストが通る（iframe が同じ要素のまま）",
			"実機で `specdockEdgeAudit` の違反0、`specdockCmdAudit` の boxOverlaps・edgeOverlaps 0",
		]
	}
}

failures: {
	"F-01": {
		title: "チャットの入口がないとき（detail がない・orca の origin がない）は、今の「チャットを開けません。」の表示のまま"
	}
}

constraints: [
	"直し方は既存の決まり（本文の `data-tab=\"agents\"`）に乗せる。帯の欄だけの CSS は足さない",
	"書いてよいのは src/spec_dock/assets/dashboard/、tests/、static-inventory.json、この Scope",
	"本人の環境に特化した決まりを入れない",
]

decisions: [
	"統括の決定（依頼書、2026-11-17）：エージェントのタブと同じ形にし、既存の決まりに乗せる。開けない表示・D-04・引っぱり・狭い画面の形は変えない。『横断の構造』も同じく直す",
	"タスク担当の判断：`data-tab=\"agents\"` はチャットの枠を出すときだけ付ける（開けない表示の余白を変えないため）",
]
