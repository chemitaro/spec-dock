package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"文書と説明資料のタブを「1行の帯 ＋ 残りの高さを使う枠」の同じ形にする",
	"変えるのは scope_tabs.js の2つのタブの描き方と、その見た目だけ。欄の部品（panel.js）と Scope の JSON は変えない",
]

current: """
	docsTab（views/_shared/scope_tabs.js）が checkResults（誤りなしでも帯）＋ planProgress（計画の進み具合）＋ .sd-docs（DOC_INFO の札、説明資料を含む）＋ .sd-docview（iframe.sd-docframe、
	高さ min(78vh, 1100px)、欄では min(70vh, 900px)）を縦に積む。欄の .pn-body は overflow: auto なので、枠は中身をスクロールした先にある（二重のスクロール）。
	explanationTab は .sd-explainbox（.sd-explain__bar の帯 24px ＋ iframe.sd-explain）で、欄では .pn-body[data-tab="explanation"] を flex の列にして枠を伸ばしている。
	概要のタブ（summaryTab）には、すでに「計画の進み具合」（planProgress）がある。
	"""

target: """
	docsTab は [誤りの帯（誤りがあるときだけ）] ＋ .sd-framebox（.sd-framebar の1行 ＋ iframe.sd-docframe）を返す。.sd-framebar は左にセグメントの切り替え（.sd-seg）、右端に新しいタブのリンク。
	explanationTab の written も同じ .sd-framebox（左は「説明資料」の小さな名前、右端に新しいタブのリンク）＋ iframe.sd-explain を返す。
	欄では、.pn-body[data-tab="docs"] と [data-tab="explanation"] を flex の列にし、.sd-framebox を flex: 1、枠を flex: 1・min-height で伸ばす。詳しい画面では、枠の高さを画面の高さから決める。
	"""

design: {
	"D-01": {
		title: "文書の選びの並び（docChoices）"
		text: """
			documentEntries（今の関数）を、説明資料（key が explanation）を除く形にし、名前を DOC_INFO から取る：spec は「仕様」、requirement・design・plan は「要件」「設計」「計画」、report は「報告」、ADR は ADR の名前（今は "ADR"。同じ名前が並ぶので adr.name のファイル名から .md を除いたものを使う）。
			各項目は {id, key, label, name, view, exists}。選べるのは view を持つ項目だけで、選びは今と同じ（wanted = env.param("doc") に合う項目、なければ最初の選べる項目）。
			DOC_INFO の2つ目の値（説明の文）は使わなくなるので消す。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "1行の帯（.sd-framebar）と、セグメントの切り替え（.sd-seg）"
		text: """
			HTML：`<div class="sd-framebox" data-frame="docs"><div class="sd-framebar"><nav class="sd-seg" aria-label="文書">…</nav><a class="sd-framebar__open" href="<view>" target="_blank" rel="noopener" aria-label="新しいタブで開く" title="新しいタブで開く">${icon("external")}</a></div><iframe class="sd-docframe" …></iframe></div>`。
			.sd-seg の項目：選べる項目は `<a ${env.paramLink("doc", id)}>`（spec で wanted がないときは今と同じく null を渡す）で、選んでいる項目に aria-current="true"。選べない項目は `<span aria-disabled="true" title="まだない">`。
			項目の title にファイル名（requirement.cue・design.cue・plan.cue など）を入れる。iframe の属性（src、sandbox、referrerpolicy、loading、title）は今のまま。
			見た目：帯は高さ 24px（height、どの幅でも）、.sd-seg は角丸 var(--ds-radius) の枠（var(--ds-border)）の中に高さ 22px の項目（字 12.5px）を並べ、選んでいる項目は var(--ds-accent-soft) の地と var(--ds-accent-strong) の字。
			新しいタブのリンクは印だけ（24×24px の当たり、印 15px）。幅が狭い（欄で .sd-seg がはみ出す）ときは、.sd-seg が横にスクロールする（min-width: 0、overflow-x: auto）。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "誤りの帯（checkResults の詰め）と、計画の進み具合を外す"
		text: """
			checkResults(check, scopeId)：status が failed なら今の render-failed の知らせ（変えない）。errors が 0 件なら "" を返す（警告だけでも出さない）。
			errors があれば `<details class="sd-checkbar" data-code="check-invalid"><summary>${icon("zap")}検査の誤り N件（警告 M件） <code>spec-dock scope check <ID></code></summary><ul class="sd-list sd-findings">…</ul></details>`。summary は1行（高さ 28px、white-space: nowrap、overflow: hidden、text-overflow: ellipsis）、地は var(--ds-danger-bg)、字は var(--ds-text)。開いたときだけ一覧が下に出る。
			docsTab から planProgress の呼び出しを除く（概要のタブの planProgress はそのまま）。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "枠に残りの高さを使わせる"
		text: """
			共有（scope_tabs.css、[data-view="scope"] と .sd-pn の両方）：`.sd-framebox { display: flex; flex-direction: column; gap: 2px; min-height: 0; }`、枠の見た目
			`:is(.sd-docframe, .sd-explain) { display: block; width: 100%; border: 1px solid var(--ds-border); border-radius: var(--ds-radius-l); background: var(--ds-bg); }`。
			枠の高さはここでは決めない。今の共有の `.sd-explain { flex: 1; min-height: 0; … }` と `.sd-docframe { height: min(78vh, 1100px); min-height: 420px; … }` はこの規則に置き換える。
			欄（panel.css）：今の `.sd-pn .pn-body[data-tab="explanation"] { …; padding: 8px 10px 10px; overflow: hidden; }`、`> .sd-explainbox { flex: 1; }`、`.sd-pn .sd-explain { height: auto; }`、
			`.sd-pn .sd-docframe { height: min(70vh, 900px); … }` を消し、次に置き換える：
			`.sd-pn .pn-body:is([data-tab="docs"], [data-tab="explanation"]) { display: flex; flex-direction: column; gap: 4px; padding: 4px 10px 10px; }`（overflow は auto のまま。誤りの帯を開いて一覧が長いときだけスクロールする）、
			`.sd-pn .sd-framebox { flex: 1; }`、`.sd-pn :is(.sd-docframe, .sd-explain) { flex: 1; min-height: 240px; height: auto; }`。
			スマホ（@container app (max-width: 640px)）：`.sd-pn .pn-body:is([data-tab="docs"], [data-tab="explanation"]) { padding: 2px 4px 4px; }`（今の `[data-tab="explanation"] { padding: 4px 6px 6px; }` と `.sd-explain__bar` の規則は消す）。
			これで、PC の欄の説明資料の枠の上端は 4 + 24 + 2 = 30px（R-05 の 32px 以内）、390×844 の全体の段では中身 688px から 688 − 2 − 24 − 2 − 4 = 656px（直す前 652px より高い）。
			詳しい画面（scope.css）：`[data-view="scope"] :is(.sd-docframe, .sd-explain) { flex: none; height: max(420px, calc(100dvh - 120px)); }`（flex: none で、高さの決まらない縦の flex の中でも height が効く。今の `.sd-explain { flex: none; height: max(480px, calc(100vh - 220px)); }` を置き換える。
			120px は上の帯（ページの見出し）と、帯の行と、間のすき間）。ページは今と同じく、画面がスクロールして枠に届く。
			今の .sd-docs、.sd-doc*、.sd-docview、.sd-explainbox、.sd-explain__bar、`:is(.sd-tabpanel, .pn-body)[data-tab="docs"] > .sd-progress` の規則は、使われなくなるので消す。
			"""
		satisfies: ["R-04", "R-05"]
	}
	"D-05": {
		title: "説明資料のタブの帯"
		text: """
			explanationTab の written は `<div class="sd-framebox" data-frame="explanation"><div class="sd-framebar"><span class="sd-framebar__name">${icon("book")}説明資料</span><a class="sd-framebar__open" …>…</a></div><iframe class="sd-explain" …></iframe></div>`。
			iframe の src、sandbox、referrerpolicy、title は今のまま。雛形・ない・読めないの知らせは今のまま。
			"""
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "知らせと描き直し"
		text: """
			catalog が ok でないとき（catalogProblem）、描けないとき（render-failed で枠なし）、選べる文書がないとき（emptyState）は、今と同じ知らせ（F-01）。
			HTML は選び（doc）と Scope の中身だけで決まり、時刻などを含めないので、描き直しで同じ文字列になり、panel.js は枠を置き換えない（F-02、今の仕組み）。
			"""
		satisfies: ["F-01", "F-02"]
	}
	"D-07": {
		title: "写しと測り（タスク担当）"
		text: """
			.workbench/iss-00589/shoot.mjs（headless Chrome、CDP、--disable-features=MacAppCodeSignClone、Browser.close）で、epic-00573 を、詳しい画面と構造の図の欄の文書・説明資料のタブ、
			1440×900、1000×800、390×844 の全体の段で撮り、枠の上端・高さ・見える高さ・欄に対する割合・中身のスクロールの有無・帯の高さを測る。
			誤りの帯（R-03）は、実データに誤りのある Scope がないとき、欄の文書のタブを開いたページで、配られた scope_tabs.js を import して checkResults と同じ HTML（誤り3件・長い文の errors を持つ check）を
			描き、切り替えの行の上に差し込んで、閉じた状態の高さを 1000×800 と 390×844 で測る（checkResults を export するか、docsTab に誤りのある details を渡して描く）。直す前は開始のコミットの venv（ポート 18589）、
			直した後は作業の木の wheel の venv（ポート 18590、--tailscale）。状態の置き場は .workbench/iss-00589/state の写し。道具の環境と常駐のダッシュボード（47800）には触れない。
			"""
		satisfies: ["R-06"]
	}
}

compatibility: "?doc=<id> の道（spec、requirement、report、adr:<path> など）は今と同じ。?doc=explanation は選べる項目にないので、最初の選べる項目（仕様）を示す。"

risks: [
	"欄の幅が狭い（380px）と、ADR が多い Scope ではセグメントがはみ出す。横のスクロールで受ける",
	"詳しい画面の 100dvh − 120px は上の帯の高さに依る。測りで確かめる",
]
