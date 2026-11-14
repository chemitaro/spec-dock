package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル。正本はここだけ。
assurance: {
	level:  "strict"
	reason: "送信できる orca-web のチャットの iframe を、SpecDock が選んだエージェントで開く。選び違いや、別の Scope のチャットが残ると、利用者が誤った相手に送り、取り消せないことがある。送信の守りは orca-web が持つが、相手を選ぶのは SpecDock なので、失敗の条件ごとに確かめる"
}

purpose: "横の欄と詳しい画面の共有のタブに「エージェント」のタブを足し、その Scope に対応した worktree のエージェントを選んで、orca-web の詳細とチャット（`/embed/agent` の iframe）をその場で使えるようにする（epic-00526 の唯一の切り分け）。"

background: """
	親の Epic epic-00526 の plan.cue の slice `iss-00593` は、Epic の R-01〜R-08、F-01〜F-07 のすべてと、設計 D-01〜D-07 を受け持つ。この要件は、Epic の要件を Issue の受け入れの粒度に書き直し、Epic が担当に任せた判断（iframe の sandbox、一覧の形、確かめの宛先）を決めたもの。Epic の要件と食い違うときは Epic が正しく、この文書を直す。

	今の状態（2026-11-14、main `67abbe6c1`、iss-00591 の PR #596 のマージの後に確かめた事実）：

	- `views/_shared/scope_tabs.js` の `SCOPE_TABS` は説明資料、概要、依存、配下、文書、Artifact、人のタスクの7つで、どのタブもいつも出る。`pageEnv`・`panelEnv` は `{mode, ctx, scope, doc, byId, param, paramLink}`。
	- 横の欄（`views/_shared/panel.js`）は中身の HTML が前と同じなら置き換えない。詳しい画面（`views/scope.js`）は描くたびに `root.innerHTML` で全体を置き換える。
	- `core/orca.js` の `createOrca` が `ctx.orca`（`origin`、`status()`、`summary()`、`marks()`、`forScope(structure, id)`、`subscribe(fn)`）を作り、`app.js` が `ctx.orca` を画面に渡す。どの画面もまだ `ctx.orca` を使わず、知らせで描き直す口もない。一覧の API の `server.orca_web` は `{enabled, origin, port, problem}`。
	- 画面の CSP の `frame-src` には、連携が有効なとき orca-web のオリジンが足されている（iss-00591）。ほかに足すものはない。
	- 明暗は `document.documentElement.dataset.theme`（埋め込みの親が `theme` で決める）か、なければ OS の `prefers-color-scheme`。SpecDock の画面に明暗の切り替えのボタンはない。
	- orca-web の `/embed/agent` の画面（orca-web の main `1a2afed` の `web/embed/` を読んだ事実）：`theme` の問い合わせを読む。送信はボタンの押しと Enter のキーで `fetch` し、`<form>` を使わない。詳細の PR と CI のリンクは `target="_blank"`、親と子のエージェントのリンクは同じ iframe の中で開く。`window.parent` も `postMessage` も使わない。

	並んで進む iss-00592（epic-00471）も `views/_shared/panel.js`、`views/graph.js`、`views/board.js` と配る文書の `reference_cli.md` を変える。iss-00592 は印を押したときに横の欄へ `preferTab("agents")` を伝える口を作り、この Issue のキー `agents` に頼る。
	"""

includes: [
	"共有のタブの並びの2番目の「エージェント」のタブ（キー `agents`）と、タブの任意の `visible(env)`",
	"タブの中の、1行のエージェントの選び（印、種類、ブランチ）と、選んだエージェントの orca-web の iframe",
	"タブを出す条件、選びの持ち方（横の欄の中と、詳しい画面の問い合わせ）、自動の選びと、いなくなった印",
	"描き直しで iframe を読み込み直さないこと（詳しい画面の描き方を、見出し・タブの帯・中身に分ける）と、Scope を変えたときに外すこと",
	"orca-web に届かないとき、連携を切ったとき、設定が壊れたとき、埋め込みの画面の中の知らせ",
	"要約の知らせ（`ctx.orca.subscribe`）と明暗の変化での描き直し",
	"書き込みに関わらないことの静的なテストと、送信の間のネットワークの記録",
	"配る文書の、エージェントのタブの説明",
]

excludes: [
	"稼働の印の置き場の描き方（iss-00592 の `paintOrcaMarks`）、欄の見出しの印と「Orca で開く」",
	"orca-web の側の変更（チャットの画面、送信の守り、`sendEnabled`、CORS と `frame-ancestors`）",
	"SpecDock のサーバーの変更（API、CSP、設定の読み）",
	"SpecDock のサーバーや画面からの書き込み（送信、トークンの取得、Orca の操作）",
	"エージェントのいない worktree へ、新しくエージェントを起こすこと",
	"company-os（nestboard）のダッシュボードへの埋め込み",
]

requirements: {
	"R-01": {
		title: "共有のタブの2番目に「エージェント」のタブがあり、決まった条件のときだけ出る"
		text: """
			`SCOPE_TABS` の説明資料の次（2番目）に、キー `agents`、名前「エージェント」のタブを足す。横の欄と詳しい画面の両方に同じタブとして出る。
			出す条件（Epic R-01、上から順に決める）：

			1. 連携を切っている（`ctx.orca.status()` が `off`）で、設定の問題（一覧の API の `server.orca_web.problem`）がない → 出さない。
			2. その Scope に SpecDock の worktree の記録がない（構造の API の `worktrees.status` が `ok` でないか、その Scope の項目の `worktrees` が空）→ 出さない。
			3. 設定の問題がある、または状態が `loading`・`unreachable`・`orca-unreachable`・`orca-starting` → 出す（中は理由の知らせ。R-06）。
			4. 状態が `ok`：対応した worktree（`ctx.orca.forScope`）のエージェントが1人以上 → 出す。0人で、その Scope の選び（R-02 の自動の選びと、いなくなった印を含む）がある → 出す（R-05 の知らせのため）。ほか → 出さない。

			数の札は、状態が `ok` で理由がないときだけ、対応した worktree のエージェントの数（0 を含む）。理由の知らせのときは札を出さない。
			タブを出さなくなったとき、そのタブを選んでいたら、今の既定のタブ（説明資料か概要）を示す。問い合わせの `tab=agents` でタブが出ない Scope を開いても、既定のタブを示す。
			埋め込みの画面でも出す条件は同じで、中は埋め込みの知らせ（R-06）になる。
			"""
		acceptance: [
			"エージェントのいる Issue を選ぶと、横の欄のタブの2番目が「エージェント」で、数の札が対応した worktree のエージェントの数と同じ",
			"同じ Issue の詳しい画面にも、2番目に同じタブがあり、数の札が同じ",
			"worktree の記録のない Scope と、エージェントのいない worktree の Scope（選びがあるときを除く）には、タブがない",
			"`orca_web.enabled` が false のとき、どの Scope にもタブがない",
			"エージェントのタブを開いたまま、そのタブが出なくなる Scope を選ぶと、既定のタブが示される",
		]
	}
	"R-02": {
		title: "タブの上に1行のエージェントの選びがあり、1人ならすぐに開き、選びは自動で別の相手に移らない"
		text: """
			タブの上の1行の帯に、対応した worktree のエージェントを並べる。各項目は、orca-web の稼働の印（`renderAgentMarks` にそのエージェントだけを渡したもの）、種類（`agentType`）、worktree のブランチを持つ。並びは `forScope` の worktree の順、その中の要約の `agents` の順。帯は1行のままで、入りきらなければ横に動かせる（折り返さない）。
			- 2人以上：小さな切り替え（押せる項目の並び）にし、選んだ項目に印（`aria-current`）を付ける。選びがなければ iframe を置かず、「エージェントを選ぶ」と示す。
			- 1人：切り替えを出さず、その1人の印、種類、ブランチを帯に示し、押さずにそのエージェントの iframe を置く。この自動の選びは、選びとして覚える。
			選びは、横の欄では欄の中（iss-00587 の選びと同じ。ページの問い合わせを変えない）、詳しい画面では問い合わせの `agent` に持つ。自動の選びと、いなくなった印は、詳しい画面では履歴を増やさずに問い合わせを書き換える。人が切り替えで選ぶと、詳しい画面では普通の移動（履歴が1つ増える）になる。
			覚えた選びは、人が切り替えで選び直すまで、ほかのエージェントに自動で移らない。人数が増えても減っても、選びは変わらない。
			"""
		acceptance: [
			"エージェントが1人の Issue でタブを開くと、押さずにそのエージェントの iframe が出て、帯に印、種類、ブランチが1行で出る",
			"エージェントが2人の Issue でタブを開くと、切り替えと「エージェントを選ぶ」が出て、押したエージェントの iframe が出る",
			"詳しい画面で選ぶと URL の問い合わせに `agent` が入り、読み込み直しても同じエージェントが選ばれている。自動の選びでは履歴が増えない",
			"横の欄で選んでも、ページの URL は変わらない",
			"1人のエージェント A の iframe が自動で開いた後、A が消えて別のエージェント B だけが残っても、B の iframe は自動で開かず、A がいなくなった知らせと切り替えが出る",
			"A の iframe を開いたまま同じ Scope に B が加わっても、A が選ばれたままである",
		]
	}
	"R-03": {
		title: "iframe は orca-web の `/embed/agent` で、帯の下の残りの高さをすべて使う"
		text: """
			選んだエージェントの、要約の `detail`（`/embed/agent?id=…`）に `&theme=<light|dark>` を足した道を、`ctx.orca.origin` の下で iframe に置く。`theme` は SpecDock の今の明暗（`data-theme`、なければ OS の明暗）で、明暗が変わったら新しい `theme` で置き直す。
			iframe は帯の下の残りの高さをすべて使い、欄の中身や詳しい画面の枠の外に二重のスクロールを作らない（iss-00589 の文書と説明資料の枠と同じ形と高さの決め方）。スマホの下から出る欄（3段のシート）では、全体の段で画面の高さの大半を使う。
			iframe の `title` に、エージェントの種類と worktree のブランチを書く。
			"""
		acceptance: [
			"1440 の横の欄で、iframe の下端が欄の中身の下端（足の帯の上）にそろい、欄の中身に縦のスクロールの棒が出ない",
			"1000 の横の欄と詳しい画面でも、iframe が帯の下の残りを使い、二重のスクロールがない",
			"390 で欄を全体の段に広げると、iframe が画面の高さの半分より多くを使う",
			"暗い明暗で開くと iframe の URL に `theme=dark` があり、明るい明暗に変えると `theme=light` で置き直される",
		]
	}
	"R-04": {
		title: "送信は orca-web の iframe の中だけで行い、SpecDock は書き込みに関わらない"
		text: """
			SpecDock の画面は、orca-web の書き込みの口（`/api/token`、`/api/send/`、`/api/open`、`/api/settings`）を呼ばず、iframe に本文、トークン、宛先を渡さない（`postMessage` を使わない）。iframe の URL に載せるのは、要約の `detail` の `id` と `theme` だけ。
			iframe の `sandbox` は、orca-web の画面の読み、送信、新しいタブのリンクが動く最小の許可にする（設計 D-03 が決め、実機で確かめる）。SpecDock の画面の CSP は変えない。
			送れるか、送った結果、結果不明の帯は、orca-web の画面がそのまま示す。SpecDock は送信の可否を上書きしたり隠したりしない。
			"""
		acceptance: [
			"確かめ専用の宛先へ iframe の中から送る間、送信の口（`/api/token`、`/api/send/`）への要求はすべて iframe の文書から出て、SpecDock の画面の文書（親）からは出ない（CDP の `Network.requestWillBeSent` の `frameId` の記録）",
			"この Issue と epic-00471 で足す画面のファイルに、書き込みの口の道と `postMessage` の文字列がない",
			"ダッシュボードの画面のコードの `postMessage` は、今ある埋め込みの知らせ（`core/embed.js` の `window.parent` への1か所）だけである",
			"iframe に `sandbox` があり、その値が設計 D-03 の値と同じ",
		]
	}
	"R-05": {
		title: "選んだ相手と違うエージェントのチャットを見せない"
		text: """
			iframe は、今示している Scope の、今対応している worktree の、選んだエージェントのものだけを置く。
			- Scope を変えたら、前の Scope の iframe を外す。
			- 状態が `ok` の要約で、選んだエージェント（自動の選びを含む）がその Scope の対応した worktree にいなくなったら、iframe を外し、「このエージェントはいなくなった」と示して切り替えに戻す。知らせは、人が切り替えで選び直すか、別の Scope に移るまで残る（同じ Scope で別のタブに移って戻っても残る）。同じ id のエージェントが後で戻っても、人が選び直すまで開かない。最後の1人がいなくなったときも、タブは知らせのために残る（R-01）。
			- 帯の各項目と iframe の `title` に worktree のブランチを出し、送る前に相手の worktree を確かめられる。
			"""
		acceptance: [
			"Scope A のチャットを開いたまま Scope B を選ぶと、A の iframe がなくなる（横の欄と詳しい画面の両方）",
			"選んだエージェントが要約から消えると、次の知らせの後に iframe がなくなり、知らせが出る",
			"選んでいたエージェントがその Scope の最後の1人で、それが消えたときも、タブが残って知らせが出る",
			"いなくなったエージェントが、後の要約で同じ id で戻っても、人が選び直すまで iframe は戻らず、知らせが残る",
			"知らせが出たまま同じ Scope の別のタブに移って戻っても、知らせが残る（横の欄と詳しい画面の両方）",
		]
	}
	"R-06": {
		title: "orca-web を使えないときは、タブの中に理由を1行で示す"
		text: """
			R-01 の条件でタブを出しているが iframe を置けないときは、iframe を置かず、理由を1つの知らせで示す（Epic R-06、D-05 の言葉）。
			- 読み込み中（`loading`）：「orca-web を読んでいる」。
			- 届かない（`unreachable`）：「orca-web（<オリジン>）に届かない」と、確かめること（orca-web が動いているか、`ORCA_WEB_READ_ORIGINS` がこの画面のオリジンを許しているか）。
			- Orca に届いていない（`orca-unreachable`）、読み始め（`orca-starting`）：orca-web の `connection.state` の言葉で示す。
			- 設定の `orca_web` の節が壊れている：その理由（`server.orca_web.problem`）と、直すファイル（`config.json`）。
			- 埋め込みの画面の中：「埋め込みの画面ではチャットを開けない」と、同じ Scope を埋め込みでなく新しいタブで開くリンク。
			状態が `ok` に戻ったら知らせを消し、前の選びのエージェントがまだいればその iframe を置く。届かない間は選びを変えない（いなくなったとは決めない）。
			"""
		acceptance: [
			"試しの orca-web を止めると、エージェントのタブの中が「orca-web（<試しのオリジン>）に届かない」の知らせになり、構造の図とボードとほかのタブは動く",
			"試しの orca-web を起動し直すと、次の読み直しの後に知らせが消え、前に選んでいたエージェントの iframe が出る",
			"埋め込みの画面（`?embed=1`）では、タブの中が埋め込みの知らせとリンクになり、iframe がない",
			"設定の `orca_web` が壊れているとき、worktree のある Scope のタブの中に、その理由と `config.json` が出る",
		]
	}
	"R-07": {
		title: "描き直しで iframe を読み込み直さない"
		text: """
			構造の描き直し、要約の 10 秒ごとの知らせ、Scope の JSON の読み直しでは、同じ Scope、同じエージェント（id、種類、ブランチ）、同じ明暗の間、iframe を作り直さず、読み込み直さない（入力欄に書きかけた本文が消えない）。同じ Scope のほかのエージェントが増えたり減ったりして帯が変わっても、選んだエージェントの iframe は残す。横の欄でも詳しい画面でも同じ。
			置き直してよいのは次のときだけ（書きかけの本文は消えうる）：明暗を変えたとき。選んだエージェントの worktree のブランチか種類が、要約で変わったとき（新しいブランチと種類を title に出す）。
			"""
		acceptance: [
			"チャットの入力欄に本文を書いたまま 60 秒待っても、本文が残り、iframe の読み込みが1回だけである（横の欄と詳しい画面の両方）",
			"チャットを開いたまま、同じ Scope にエージェントが1人加わるか、選んでいないエージェントがいなくなっても、iframe の読み込みが増えない",
			"選んだエージェントの worktree のブランチが要約で変わると、iframe の title が新しいブランチになって置き直される",
		]
	}
	"R-08": {
		title: "配る文書に、エージェントのタブの説明がある"
		text: "配る文書（`src/spec_dock/assets/spec_dock/docs/reference_cli.md`）に、エージェントのタブを出す条件、選びの持ち方、送信は orca-web の iframe の中で行われ orca-web の設定の `sendEnabled` で止められること、知らせの言葉の意味を書く。実際の IP、ユーザー名、パスは書かない（例は 127.0.0.1 と 192.0.2.x）。"
		acceptance: [
			"配る文書に、エージェントのタブの条件、送信が orca-web の iframe の中で行われ `sendEnabled` で止まること、知らせの意味の説明があり、`static-inventory.json` の sha256 が合う",
		]
	}
}

failures: {
	"F-01": {
		title:    "orca-web に届かない、部品を読めない、要約の形が違うときは、iframe を置かず理由を示し、ほかのタブと図とボードは動く"
		impact:   "チャットを使えない。会話や送信が SpecDock の側に残ることはない"
		recovery: "orca-web を起動するか、`ORCA_WEB_READ_ORIGINS` に SpecDock のオリジンを足す。次の読み直し（10 秒）で知らせが消え、前の選びの iframe が出る"
	}
	"F-02": {
		title:    "選んだエージェント（自動の選びを含む）が要約で対応した worktree にいなくなったら、iframe を外して知らせ、ほかのエージェントへ自動で移らず、同じ id が戻っても人が選び直すまで開かない"
		impact:   "外さないか、残った別のエージェントへ自動で移ると、利用者が前の相手のつもりで別のセッションに送るおそれがある"
		recovery: "切り替えで選び直す。書きかけの本文は失われる"
	}
	"F-03": {
		title:    "Scope を変えたときは、前の Scope の iframe を残さない"
		impact:   "残すと、欄が別の Scope を示しているのに、前の Scope のエージェントに送るおそれがある"
		recovery: "前の Scope を選び直せば、同じ選びのチャットに戻る（詳しい画面は問い合わせで、横の欄は1人なら自動の選びで）。書きかけの本文は失われる"
	}
	"F-04": {
		title:    "SpecDock の側で worktree の記録を読めない、対応が決まらないときは、エージェントを推し量って出さない"
		impact:   "その Scope のタブが出ない。要約の `issue` や名前の一致で、別のリポジトリや別の Scope のエージェントを出すことはない"
		recovery: "`git worktree list` が読めるようにする（カタログのリンク、Git の状態）。次の構造の読み直しで対応する"
	}
	"F-05": {
		title:    "埋め込みの画面の中では、iframe を置かず、SpecDock を直接開く道を示す"
		impact:   "埋め込み先のオリジンを orca-web の `frame-ancestors` が許さないので、置いても枠が拒まれる"
		recovery: "知らせのリンクで SpecDock のダッシュボードを直接開く"
	}
	"F-06": {
		title:    "orca-web の送信が止まっている（`sendEnabled` が false）ときも、SpecDock は何もしない"
		impact:   "チャットは読めるが送れない。理由は orca-web の画面が入力欄の下に示す"
		recovery: "orca-web の設定のファイルに `\"sendEnabled\": true` を手で書く（orca-web の README）。SpecDock の側の操作はない"
	}
	"F-07": {
		title:    "連携を切っている、設定の `orca_web` の節が壊れているときは、タブを出さないか壊れた理由を示し、orca-web に何も要求しない"
		impact:   "チャットを使えない"
		recovery: "`config.json` の `orca_web` の節を直す。サーバーを起動し直さずに、次に開いた画面から効く"
	}
}

constraints: [
	"SpecDock のサーバーは変えない（見るだけ。書く口を足さない）。画面も orca-web の書き込みの口を呼ばない",
	"帯の印と iframe の中身は orca-web の部品と画面をそのまま使い、SpecDock の中で描き直さず、新しい色を足さない",
	"orca-web の場所、要約、対応、状態は iss-00591 の `core/orca.js`・`core/orca_match.js` を使い、別に読まない",
	"公開のリポジトリ（コード、テスト、文書、仕様）に、実際の Tailscale の IP、ユーザー名、利用者の絶対パスを書かない",
	"新しい依存を足さない",
	"実機の確かめは、試しの SpecDock（隔離した venv、一時の状態の置き場、別のポート、`--tailscale`）と試しの orca-web（orca-web の main のチェックアウトの `dist/`、別のポート、試し専用の設定のファイル）の組で行う。常駐のダッシュボード（47800）と常駐の orca-web（8791）の設定と設定のファイルに触れない",
	"送ってよい宛先は、統括が用意した spec-dock の確かめ専用の worktree `iss-00593-send-test`（ブランチ `chemitaro/iss-00593-send-test`）のエージェントと、orca-web の worktree `send-test` の2つのエージェントだけ。業務中のエージェント（この Issue の worktree のエージェント、統括、ほかの worker）には送らない",
]

decisions: [
	"2026-11-14、統括の決定（依頼書）：タブは共有のタブの説明資料の次（2番目）。対応した worktree にエージェントがいるときだけ出す（届かないときは worktree のある Scope にだけ出して理由を1行で示す）。中は上に1行のエージェントの選び（稼働の印つきの小さな切り替え。1人なら選びを出さずにすぐ開く）、その下に `/embed/agent?id=…&theme=…` の iframe が残りの高さをすべて使う（スマホのシートの全体の段でも）。明暗は今の明暗を `theme` で渡し、切り替えに追従する。送信は iframe の中だけ。sandbox と CSP は orca-web の送信の守りが働く最小の許可にし、理由を設計に書く",
	"2026-11-14、統括の決定（依頼書）：実装担当は、画面と一体の部分を Claude Opus 5.5 / high、テストで確かめられる純粋な計算を Codex GPT-6.1 Sol / medium",
	"2026-11-14、統括の決定（msg_baf8fde71131）：送信の確かめは案B。統括が用意した spec-dock の確かめ専用の worktree `iss-00593-send-test`（ブランチ `chemitaro/iss-00593-send-test`、Claude Haiku、届いた文に従わず受け取りの文字数だけ答える依頼）のエージェントにだけ送る。この worktree の片付けは統括が行う",
	"2026-11-14、統括の知らせ（msg_7993f0b4b433）：本人の了承で、常駐の orca-web の `sendEnabled` は true になった。確かめは依頼書のまま試しの組で行い、常駐の設定のファイルには触れない。試しの orca-web は試し専用の設定のファイルで `sendEnabled` を true にする",
	"2026-11-14、タスク担当の判断：1人のときの帯は、切り替えにせず印・種類・ブランチの1行の見出しにする（統括の「選びを出さない」と、Epic R-05 の「送る前に相手の worktree を確かめられる」の両立）",
	"2026-11-14、タスク担当の判断：エージェントの多い worktree は、帯を折り返さず横に動かせる1行にする（Epic の risks の「10人を超える場合」への答え。iframe の高さを一定に保つ）",
]

questions: []
