package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"欄を1つの共有の部品にし、構造の図とボードの両方で使う",
	"欄のタブと詳しい画面のタブを、1つのタブの並びと同じ描き方の関数から作る（二重に作らない）",
	"説明資料を同じオリジンの sandbox の枠で埋め込み、雛形とないときを見分ける",
	"スマホのシートを3段のスワイプにし、中身のスクロールとぶつけない",
	"後のエージェントのタブを、並びに1つ足すだけで出せる",
]

current: """
	欄は構造の図だけにある（graph.js の renderPanel、graph.css の .gx .panel、幅 372px、スマホは max-height 58〜74% で動かない取っ手 .pn-grab）。
	中身は状態、道筋、種類・保証・PR・ブランチ・段・後に続く・人のタスク・変化・大もと、配下の進み具合と、「詳しく」「この範囲に絞る」「GitHub」。
	ボードの札（parts.js の card）は詳しい画面への <a data-nav> で、押すと詳しい画面へ移る。
	詳しい画面（scope.js）のタブの中身（summaryTab、depsTab、childrenTab、docsTab、artifactsTab、todosTab）は scope.js の中の関数で、
	タブの中のリンクは ctx.route.path に問い合わせ（tab、done、doc）を足した道。タブの並びは logic.js の TABS、選びは tabOf(params)（ないときは summary）。
	説明資料は Scope の JSON の details.documents の explanation の href（/r/…/files/<ID>/explanation.html）で、文書のタブから新しいタブで開くだけ。
	"""

target: """
	新しい views/_shared/scope_tabs.js が、タブの並び SCOPE_TABS と、各タブの描き方（説明資料のタブを含む）を持つ。描き方は env（下の D-03）だけを見る。
	scope.js は env を「ページ」の形で作り、タブを描く。新しい views/_shared/panel.js（と panel.css）が欄の部品で、env を「欄」の形で作る。
	構造の図とボードは、欄の部品を作り、Scope を選んだら show、閉じたら hide を呼ぶ。純粋な計算（最初のタブ、説明資料の状態、シートの段）は views/_shared/panel_logic.js に置く。
	"""

design: {
	"D-01": {
		title:     "Scope の JSON：説明資料が雛形のままかを示す skeleton"
		satisfies: ["R-03", "F-03"]
		text: """
			dashboard_scope_details.py の _documents で、key が explanation の項目に skeleton を足す：ファイルがあり、普通のファイルとして先頭の 256KiB を読めて、
			domain/explanation_shape.py の SKELETON_MARKER を含めば true、含まなければ false、ない・読めないときは null。ほかの文書の項目には skeleton を足さない。
			読むのは普通のファイルだけ（リンクはたどらない。今の _regular と同じ）。presentation/dashboard_api.py は details をそのまま写すので変えない（確かめる）。
			API_SCHEMA は変えない（項目の追加だけ）。
			"""
	}
	"D-02": {
		title:     "純粋な計算：views/_shared/panel_logic.js"
		satisfies: ["R-02", "R-03", "R-04", "R-07"]
		text: """
			DOM を触らない関数だけを置き、node のテストで確かめる。
			- explanationState(details)：details がないか catalog が ok でなければ "unreadable"。documents の explanation がない・exists が false なら "missing"。
			  skeleton が true なら "skeleton"。ほか（false か null）は "written"。
			- defaultTab(details)：explanationState が "written" なら "explanation"、ほかは "summary"。
			- pickTab(wanted, keys, details)：wanted が keys にあればそれ、ほかは defaultTab(details)。詳しい画面は wanted に問い合わせの tab を、欄は利用者が選んだタブ（なければ null）を渡す。
			- sheetHeights(viewHeight)：{peek: 120, half: round(viewHeight × 0.58), full: viewHeight}。
			- settleSheet({height, velocity, heights})：離したときの段。velocity は px/ms で上向きが正（シートが高くなる向き）。
			  height が heights.peek − 48 より低ければ "closed"。|velocity| が 0.5 以上なら、その向きで、いまの高さの次の段（上向きは height より高い一番低い段、下向きは height より低い一番高い段。なければ端の段）。
			  ほかは一番近い段。段は "peek"、"half"、"full"。
			- nextOnTap(snap)："full" なら "half"、ほかは "full"。
			"""
	}
	"D-03": {
		title:     "タブの中身の共有：views/_shared/scope_tabs.js と env"
		satisfies: ["R-02", "R-04", "R-09"]
		text: """
			scope.js の summaryTab、depsTab、childrenTab、docsTab、artifactsTab、todosTab と、その下請け（section、planProgress、catalogProblem、documentEntries、checkResults、link、idleBadge は使う側に応じて）を
			scope_tabs.js に移し、中身の HTML は変えない。違いは env で受ける：
			- env.ctx：シェルの ctx（data、href、navigate、repository、route、embed）。
			- env.scope、env.doc（scopes/<ID> の JSON）、env.byId。
			- env.param(name)：タブの中の選び（done、doc）。ページは ctx.route.params、欄は欄が持つ Map。
			- env.paramLink(name, value)：<a> の属性の文字列。ページは `data-nav href="<ctx.href(withParam(ctx.route.path, name, value))>"`（今と同じ道）。
			  欄は `href="<詳しい画面の道に name=value と tab を足したもの>" data-pn-param="<name>" data-pn-value="<value または空>"`（修飾キーのクリックは詳しい画面を新しいタブで開ける）。
			- env.mode："page" か "panel"。
			Scope へのリンク（link）は data-id を持つ（札の card は今も data-id を持つ）。
			SCOPE_TABS は [{key, label, count(env) → 数か null, render(env) → HTML}] の並びで、
			explanation（説明資料）、summary（概要）、deps（依存）、children（配下）、docs（文書）、artifacts（Artifact）、todos（人のタスク）の順。
			logic.js の TABS は SCOPE_TABS のキーと名前を写す形にするか、SCOPE_TABS に置き換え、tabOf は panel_logic.js の pickTab を使う形に改める（呼ぶ側は scope.js とテストだけ）。
			後のエージェントのタブは、SCOPE_TABS に1つ足すだけで、欄と詳しい画面に出る（R-09）。
			"""
	}
	"D-04": {
		title:     "説明資料のタブ"
		satisfies: ["R-03", "F-03"]
		text: """
			render(env) は explanationState(env.doc.details) で分ける。
			- written：上に細い帯（「説明資料」と「新しいタブで開く」のリンク、href は documents の explanation の href）、その下に
			  <iframe class="sd-explain" src="<href>" sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer" title="説明資料：<ID>">。
			  タブの中身の箱は縦の flex にし、枠は残りの高さをすべて使う（flex: 1、min-height: 0）。ページでは枠の高さを max(480px, 画面の高さ − 見出しの分) 程度にする（scope.css）。
			- skeleton：知らせ（data-code="explanation-skeleton"）「説明資料は雛形のまま（まだ書かれていない）」、書き方 spec-dock/docs/authoring/explanation.md、雛形を新しいタブで開くリンク。
			- missing：知らせ（data-code="explanation-missing"）「説明資料はまだない」と書き方。
			- unreadable：文書のタブと同じ catalogProblem。
			count は null（数を出さない）。
			"""
	}
	"D-05": {
		title:     "欄の部品：views/_shared/panel.js と panel.css"
		satisfies: ["R-01", "R-02", "R-05", "R-06", "R-08", "F-01", "F-04"]
		text: """
			createScopePanel(aside, {onSelect(id), onClose(), extraActions(scope) → HTML}) が {show(state), hide(), isOpen(), element, snap} を返す。
			show({ctx, scope, doc, byId}) は、scope（構造の JSON の項目）と doc（詳しい JSON、まだないか読めないなら null）で欄を描く。
			- 見出し：状態の札（stateChip、motion: true）、マージの印、閉じる。ID・番号・種類、題名、理由（pn-why）、動きなし、親の道筋（押すと onSelect）。今の graph の見出しを移す。
			- タブの帯：SCOPE_TABS のボタン（role=tab、aria-selected）。選んだタブは部品が持ち、利用者が押したものを保つ（R-02）。初めは pickTab(null, …)。
			- 中身：doc があれば選んだタブの render(env)。doc がまだなら「読み込み中」、読めないなら F-01 の知らせ。
			- 下の帯：「詳しい画面」（<a data-nav href="ctx.href(<詳しい画面の道>?tab=<タブ>)">）、「新しいタブで開く」（target=_blank、embed のない道）、extraActions（図の「この範囲に絞る」）、GitHub。
			描き直しは、見出し・タブの帯・下の帯を毎回作り直し、中身は「Scope の ID、タブ、doc、タブの中の選び」のどれかが変わったときだけ作り直す。
			説明資料の枠は、作り直しても src が同じなら前の iframe 要素を移して使う（R-08）。中身のスクロールの位置は、同じ Scope・同じタブの作り直しで戻す。
			欄の中のクリック：data-pn-param のリンクは欄の Map を変えて描き直す（修飾キーのときは何もしない＝普通に開く）。data-id を持つリンク（札、link）は、構造にある Scope なら onSelect(id)。
			ほかのリンクは今までどおり（data-nav はシェルが同じページの中で移す）。
			panel.css は欄の見た目（今の .gx .panel の見た目を .sd-pn に移す）と、PC の幅 --pn-w: clamp(380px, 44cqw, 720px)（container app）を持つ。
			"""
	}
	"D-06": {
		title:     "構造の図：共有の欄を使う"
		satisfies: ["R-01", "R-05", "R-08", "F-02", "F-04"]
		text: """
			graph.js の renderPanel の Scope の部分を、createScopePanel の show に置き換える。片付けの候補の一覧（V.cleanup）は今の描き方のまま同じ aside に描く（欄の部品は hide してから描く）。
			select(id) は今のまま api.scope を読み、V.path.doc を欄に渡す（読めなければ doc は null で F-01）。token で古い答えを捨てる（今と同じ、F-04）。
			revision が変わった描き直しで、選んだ Scope の api.scope を読み直す。選んだ Scope が構造にないなら select(null)（今と同じ、F-02）。
			欄が開いている PC では、.gx に data-panel="open" を付け、上の帯（.gx-bar）の right を var(--pn-w) + 20px にして、道具が欄の左に折り返す。
			centerOn の右へのずらしは、固定の 190 ではなく、欄の幅の半分。スマホの keepAbovePanel は、シートのいまの高さを使う。
			図の Esc、Enter、スマホの2度目のタップで詳しい画面へ、は今のまま。
			"""
	}
	"D-07": {
		title:     "ボード：共有の欄を使う"
		satisfies: ["R-01", "R-05", "F-02", "F-04"]
		text: """
			board.js は、欄の aside を .sd-page の外（root の直下）に1つ持ち、5秒の描き直しでも作り直さない（root.innerHTML で消さない形にする。ページの中身は子の要素に描く）。
			root のクリックで、修飾キーなしの左クリックの a.sd-card[data-id] は preventDefault して選ぶ（シェルの interceptLinks は defaultPrevented を見て何もしない）。
			選ぶと api.scope を読み、token で古い答えを捨て、欄に渡す。Esc で閉じる。dispose で選びと欄を片付ける。
			欄が開いている PC では、ボードの root に data-panel="open" を付け、.sd-page の右に var(--pn-w) + 20px の余白を足して、列が欄の左に収まる。
			選んだ札には aria-current="true" と、目に見える枠を付ける。
			"""
	}
	"D-08": {
		title:     "スマホの3段のシート"
		satisfies: ["R-07", "R-08"]
		text: """
			640px 以下では、欄は position: fixed で画面の下に付き、高さを --pn-h（px）で持つ。段は panel_logic.js の sheetHeights(innerHeight)。全体のときは上の角を丸めない。
			取っ手（.pn-grab、<button aria-label="欄の高さを変える">）と見出しの帯（.pn-head と題名の行）が、pointerdown で引きずりを始める（ボタンやリンクの上は除く、6px 動いてから）。
			setPointerCapture で指を追い、引きずりの間は transition を外し、枠には pointer-events: none を付ける。離したら settleSheet で段を決め、"closed" なら onClose。
			取っ手のタップは nextOnTap。中身（.pn-body）は overflow: auto と overscroll-behavior: contain で、シートを動かさない。touch-action は、取っ手と見出しの帯だけ none。
			別の Scope を選んでも段を保ち、最小のときは通常にする。resize で sheetHeights を計算し直し、同じ段に合わせる。
			PC の幅になったら、--pn-h と段を使わない。reduced motion では transition を外す。
			"""
	}
}

compatibility: """
	Scope の JSON は項目の追加だけ。詳しい画面の URL（/r/…/scopes/<ID>、?tab=deps など）は同じタブを開く。tab のない URL は、説明資料が書かれていれば説明資料のタブを開く（今までは概要）。
	埋め込みの契約（specdock.embed/v1）は変えない。
	"""

risks: [
	"説明資料の枠は、シェルの明るさの切り替え（埋め込みの theme）に従わず、OS の設定に従う（説明資料の側の仕組み。今の新しいタブと同じ）",
	"ボードの描き直しの形を変えるので、片付けの候補のダイアログと、スクロールの位置の保ち方を壊さないようにする",
	"欄の幅が広がるので、1000px の構造の図は見える幅が狭くなる（図の配置は欄で変えない。今と同じ）",
]
