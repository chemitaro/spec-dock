package spec

// 要件（Epic）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル。正本はここだけ。
assurance: {
	level:  "standard"
	reason: "SpecDock の画面に、別のサービス orca-web から読んだエージェントの稼働を重ねて示し、orca-web の「Orca で開く」のボタンを埋め込む。SpecDock 自身は見るだけのままで、誤りは表示の誤りか、埋め込みの不具合にとどまり、版を戻せば回復できる。"
}

purpose: "SpecDock のダッシュボード（epic-00427、epic-00573）の構造の図の箱、ボードの札、横の欄（iss-00587 の共有の欄）の見出しに、その Scope に対応する worktree にいる Orca のエージェントの稼働の印を重ねて示し、横の欄の見出しに、その worktree を Orca のアプリで開くボタンを置く（ダッシュボードの第2段階）。"

background: """
	2026-11-03 の利用者の決定（epic-00427 の requirement.cue の decisions）：

	- ダッシュボードは3つの段階で進める。第1段階（epic-00427）は SpecDock の資源だけを見る。第2段階（この Epic）は Orca と連携して、エージェントの稼働を示す。第3段階（epic-00526）は、Orca のエージェントとのチャット（ログの表示と送信）を埋め込む。
	- Orca を外から操作する機能は、SpecDock の中に作らず、独立したサービス **orca-web**（`chemitaro/orca-web`、Tailscale の中だけ）に作る。SpecDock は orca-web の画面と部品を埋め込んで使う。
	- この Epic で SpecDock は見るだけのまま（`GET` だけ）で、Orca の状態は orca-web の読む口から取る。Orca の CLI を直接呼ばない。Scope と worktree の対応は SpecDock が決める。

	2026-11-14 の本人の要望：「SpecDock の Issue に紐づく worktree にいるエージェントを、構造の図や Issue の一覧の狭い枠と、SpecDock の詳細の画面に取り込む」。
	orca-web の側の部品は完成し、本人が確かめた（orca-web の iss-00027 稼働の印、iss-00028 詳細とチャット、iss-00014 試しの画面）。部品の契約は orca-web の README の「SpecDock のダッシュボードに置く」の節にある。
	この Epic の要件は、統括の決定（2026-11-14、Orca の依頼 task_87517b448497）をそのまま写したもの。

	orca-web の部品の契約（README、2026-11-14 の main で確かめた事実）：

	- `GET /api/worktrees/summary`（`schema: "orca-web.worktree-summary/v1"`）は、エージェントが1つ以上いる worktree ごとに `id`、`path`、`branch`、`project {id, name}`、`issue`、`counts`、`agents[] {id, mark, workingMode, agentType, since, detail, elapsedFrom, elapsedBasis}` を返し、文書の上に `stale` と `connection {state, checkedAt}`（`state` は `connected`・`unreachable`・`starting`）を持つ。Orca に届かないときも 200。
	- 読み取りの CORS は `ORCA_WEB_READ_ORIGINS` のオリジンだけ（既定は SpecDock の `http://127.0.0.1:47800` と、Tailscale の IP の同じポート）。ほかのオリジンは 403。
	- 稼働の印の部品は ES Module（`/embed/agent-marks.js` と `agent-marks.css`、ほかに同じ場所の3つのファイル）で、`watchWorktreeSummary(base, {onDocument, onError})` が既定 10 秒ごとに要約を読み（画面が見えない間は読まない）、`findWorktree`、`renderAgentMarks(container, worktree, {size, max, onSelect})` で多くの箱に描ける。色は SpecDock の `--sd-*`・`--ds-*` を先に使う。
	- 「Orca で開く」は `<script src="<orca-web>/embed/open-button.js" data-worktree="<worktree の ID かパス>" data-theme data-size>` の1行で、スクリプトが自分の後ろに iframe を差し込む。親の画面の幅が 390px 以下の間は出さず、読み込まない。置ける画面は `ORCA_WEB_READ_ORIGINS` のオリジンだけ（`frame-ancestors`）。
	- orca-web は 127.0.0.1 と Tailscale の IP だけで待ち受け、Host を完全一致で確かめる（`127.0.0.1`、`localhost`、Tailscale の IP。ほかは 421）。

	SpecDock の今の状態（2026-11-14 の main `7e50ac583` で確かめた事実）：

	- ダッシュボードの構造の API の Scope の項目は、この PC の `git worktree list` のうち、ブランチ名がその Scope を名指す最初の worktree のブランチ（`branch`）だけを持つ（iss-00544）。worktree のパスは、Scope の JSON の `details.worktrees.items[] {path, branch}` にだけある（iss-00531）。
	- 画面の CSP は `script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-src 'self'` で、ほかのオリジンを読めない。
	- 利用者の設定 `$XDG_CONFIG_HOME/spec-dock/config.json`（`specdock.config/v1`）は、`todo` と `dashboard`（出すリポジトリ）の節を持つ。`dashboard` の節が壊れていると、全リポジトリが隠れる（隠す側に倒れる）。
	"""

includes: [
	"orca-web の場所（画面を開いたホスト名と同じ名前の、既定 8791 のポート）を決める設定と、その場所だけを許す CSP",
	"構造の API が、Scope ごとの worktree の記録（パスとブランチのすべて）と、リポジトリの worktree のパスの一覧を返すこと",
	"画面が orca-web の要約を直接読み、SpecDock の worktree の記録と突き合わせて、Scope ごとの worktree を決める計算",
	"構造の図の箱と枠、ボードの札、横の欄の見出しへの稼働の印（orca-web の部品）",
	"横の欄の見出しへの「Orca で開く」のボタン（orca-web の部品）",
	"orca-web に届かないとき、連携を切ったとき、埋め込みの画面の中での振る舞い",
	"配る文書（spec-dock/docs/）への、連携の設定と前提の説明",
]

excludes: [
	"エージェントのタブ、詳細とチャットの iframe、送信（epic-00526）",
	"詳しい画面（views/scope.js）の見出しへの印とボタン（エージェントのタブは epic-00526 が共有のタブに足す）",
	"時間の軸、概要、人のタスクの画面への印",
	"orca-web の側の変更（部品、色、経過の表記、CORS の許す先）",
	"SpecDock のサーバーが orca-web や Orca を読むこと、書くこと",
	"オーケストレーションの連絡（統括と worker）を図の上に線で示すこと（2026-10-30 の構想。この Epic では扱わない）",
]

requirements: {
	"R-01": {
		title: "orca-web の場所は、画面を開いたホスト名と同じ名前の 8791 を既定とし、利用者の設定で変えられる"
		text: """
			画面が読む orca-web のオリジンは `http://<画面を開いたときの Host のホスト名>:<ポート>` で、ポートの既定は 8791。
			127.0.0.1 で開けば `http://127.0.0.1:8791`、Tailscale の IP で開けばその IP の 8791 になる。ホスト名は、ダッシュボードのサーバーが許した Host の名前だけを使う。
			利用者の設定 `config.json` の新しい最上位の節 `orca_web`（`{"enabled": true か false, "port": 1〜65535 の整数}`、どちらも省ける）で、連携を切るか、ポートを変えられる。
			設定を変えると、サーバーを起動し直さずに次の要求から効く（今の設定の読み直しと同じ）。公開のリポジトリ（コード、テスト、文書）に実際の IP を書かない。
			"""
		acceptance: [
			"設定がないとき、`http://127.0.0.1:47800/` で開いた画面は `http://127.0.0.1:8791` を、別の許した Host 名で開いた画面はその名前の 8791 を orca-web として使う（テストは 127.0.0.1 と、文書用の IP の例で確かめる）",
			"`orca_web.port` を変えると、起動し直さずに、次に開いた画面がそのポートを使う",
			"`orca_web.enabled` が false のとき、画面は orca-web に何も要求しない",
		]
	}
	"R-02": {
		title: "画面の CSP は、連携が有効なときだけ、その orca-web のオリジンを読み込みと iframe に許す"
		text: """
			画面の HTML の CSP は、連携が有効なとき、R-01 のオリジンを `script-src`、`style-src`、`connect-src`、`frame-src` に足す。ほかのオリジンは足さない。
			連携を切っているときは、今の CSP と同じ文字列のまま。JSON の口と、/files/ の資料の CSP は変えない。
			"""
		acceptance: [
			"有効なとき、画面の CSP の4つの指示に、そのオリジン（Host の名前とポート）だけが足されている",
			"`enabled: false` のとき、画面の CSP は今と同じ文字列である",
			"許していない Host 名の要求は、今と同じく 421 で、CSP にその名前が入ることはない",
		]
	}
	"R-03": {
		title: "構造の API は、Scope ごとの worktree の記録と、リポジトリの worktree のパスの一覧を返す"
		text: """
			構造の API の各 Scope の項目に、この PC の `git worktree list` のうち、ブランチ名がその Scope を名指す worktree のすべてを `{path, branch}` の並び（一覧の順）で足す。
			文書の上には、そのクローンの worktree のすべてのパス（main のチェックアウト、linked worktree、カタログの worktree を含む）を足す。
			今の `branch` の項目は変えずに残す。`git worktree list` を読めないときは、並びを空にし、読めないことを示す値を持つ（画面は対応を作らない）。サーバーは orca-web を読まない。
			"""
		acceptance: [
			"`chemitaro/iss-00589` の worktree があると、iss-00589 の項目に、そのパスとブランチが入る",
			"リポジトリの worktree のパスの一覧に、main のチェックアウトのパスが入る",
			"`git worktree list` が失敗すると、並びは空で、読めないことを示す値が入り、ほかの項目は今と同じ",
		]
	}
	"R-04": {
		title: "Scope と orca-web の worktree の対応は、SpecDock の記録との突き合わせで決める"
		text: """
			画面は orca-web の要約の worktree を、次の順で Scope に対応させる。

			1. パスの一致：要約の worktree の `path` が、ある Scope の worktree の記録の `path` と、末尾の `/` を除いて一致する。
			2. 同じリポジトリのブランチ名の一致：1 で対応しなかった要約の worktree は、その `project.id` が「このリポジトリの worktree のパスの一覧のどれかとパスが一致した要約の worktree」の `project.id` と同じで、かつ `branch` が、ある Scope の worktree の記録の `branch` と完全に一致するときだけ、その Scope に対応する。この「同じリポジトリ」の手がかりが要約の中にないときは、2 では対応させない。

			要約の `issue` は使わない（参考に留める）。どの Scope にも対応しない要約の worktree は、どこにも出さない。
			1つの要約の worktree は、多くても1つの Scope に対応する。1つの Scope に2つ以上の worktree が対応したら、そのすべてのエージェントをその Scope のものとする。
			親の Scope（Epic、Initiative）は、自分のブランチの worktree が対応したときだけエージェントを持ち、配下のエージェントを合算しない。
			"""
		acceptance: [
			"パスが一致する worktree は、その Scope に対応する",
			"パスが違い、同じリポジトリの手がかりがあり、ブランチが一致する worktree は、その Scope に対応する",
			"同じブランチ名でも、別のリポジトリ（project.id が違う）の worktree は対応しない。手がかりがないときも対応しない",
			"`issue` だけが Scope の ID と一致する worktree は対応しない",
			"Epic は、配下の Issue にエージェントがいても、自分の worktree がなければエージェントを持たない",
		]
	}
	"R-05": {
		title: "構造の図の箱と枠、ボードの札、横の欄の見出しに、orca-web の部品で稼働の印を出す"
		text: """
			対応した worktree にエージェントがいる Scope の、構造の図の箱（Issue）と枠の見出しまたは箱（Epic、Initiative）、ボードの札、横の欄の見出しに、orca-web の `renderAgentMarks` で稼働の印を描く。
			部品は orca-web から import し、SpecDock の中で印の形、色、言葉を作り直さない（色と状態の対応、監視中の脈の線、作業中の回る弧、経過の表記は orca-web の部品のまま）。
			要約は画面全体で1つの読みの輪（`watchWorktreeSummary`）で読み、同じ文書から全部の印を描く。図とボードの印は押せない（印に `onSelect` を渡さない。押すと今までどおり箱や札が選ばれる）。
			"""
		acceptance: [
			"作業中のエージェントが1人いる Issue の箱に、orca-web の印（種類のアイコン、緑、回る弧、経過）が出る",
			"同じ Issue のボードの札と、横の欄の見出しにも、同じ印が出る",
			"画面に箱が多くあっても、要約の読みは1つの間隔に1回である",
			"箱の印を押すと、今までどおりその箱が選ばれ、横の欄が開く",
		]
	}
	"R-06": {
		title: "印の経過で、作業を終えてからの待ち時間を示す"
		text: "印の経過（now、5m、3h、2d）は orca-web の `elapsedFrom` を起点に、orca-web の部品が描く。完了（done）や入力待ち（waiting）のエージェントの経過が、作業を終えてからの待ち時間になる。SpecDock は別の時刻を出さない。"
		acceptance: [
			"入力待ちのエージェントの印の経過が、その状態になった時刻（`elapsedFrom`）からの経過で、title に読める文がある",
		]
	}
	"R-07": {
		title: "横の欄の見出しに、対応した worktree を Orca で開くボタンを置く"
		text: """
			横の欄の見出しに、orca-web の `open-button.js` を、対応した worktree の要約の `id` を `data-worktree` にして置く（`data-theme` は SpecDock の今の明暗、`data-size` は sm）。
			対応した worktree が2つ以上なら、SpecDock の worktree の記録の順で最初のものを使う。対応した worktree がなければ置かない。
			画面の幅が 390px 以下では、orca-web の部品が自分で出さない（SpecDock は隠さない）。
			"""
		acceptance: [
			"エージェントのいる Issue を選ぶと、横の欄の見出しに「Orca で開く」のボタンが出て、押すとその worktree が Orca で前面に出る",
			"幅 390px の画面では、ボタンが出ない",
			"対応した worktree のない Scope を選ぶと、ボタンが出ない",
		]
	}
	"R-08": {
		title: "画面の描き直しで、印がちらつかず、ボタンの iframe を読み込み直さない"
		text: """
			構造の5秒ごとの描き直しと、要約の読み直しのたびに、印は最後に読めた要約から描き直す（描き直しの間に印が消えて戻ることがない）。
			横の欄の「Orca で開く」の iframe は、同じ Scope、同じ worktree、同じ明暗の間は作り直さない。Scope か worktree か明暗が変わったときだけ置き直す。
			"""
		acceptance: [
			"同じ Scope を選んだまま 30 秒待つ間に、ボタンの iframe の読み込みが1回だけである",
			"構造の描き直しの後も、箱の印が残っている",
		]
	}
	"R-09": {
		title: "配る文書に、連携の設定と前提を書く"
		text: "配る文書（`src/spec_dock/assets/spec_dock/docs/` の該当する文書）に、orca-web との連携の前提（orca-web の `ORCA_WEB_READ_ORIGINS` が SpecDock のオリジンを許すこと、同じ PC で動くこと）、`config.json` の `orca_web` の節、届かないときの見え方を書く。実際の IP は書かない。"
		acceptance: [
			"配る文書に `orca_web` の節の書き方と既定の値があり、`ORCA_WEB_READ_ORIGINS` への言及がある",
		]
	}
}

failures: {
	"F-01": {
		title: "orca-web に届かないとき（止まっている、CORS で拒まれる、部品の import に失敗する）は、印もボタンも出さず、図とボードは今までどおり動く"
		text:  "読みと import の失敗は画面の操作を止めず、誤りの知らせも図やボードに出さない。次の読みの間隔で試し直し、読めたら印が出る。import に失敗したら、次の試しでは別の問い合わせの文字列を付けて読み直す（ブラウザーが失敗を覚えていても試し直せるように）。"
	}
	"F-02": {
		title: "要約の形が違う（schema が違う、worktrees が並びでない）ときは、届かないときと同じに扱う"
	}
	"F-03": {
		title: "orca-web が Orca に届いていない（connection.state が connected でない）ときは、印もボタンも出さない"
		text:  "`stale` が true でも connected なら印を出す（一部の取得元の古さで全部を消さない）。"
	}
	"F-04": {
		title: "連携を切っている（enabled が false）か、設定の orca_web の節が読めないときは、orca-web に何も要求せず、CSP も今のまま"
		text:  "`orca_web` の節が壊れていても、ほかの節（`dashboard`、`todo`）の読みに影響させない。壊れていることは、リポジトリの一覧の API と `spec-dock dashboard list` の設定の問題（`config_problems`）に示す。"
	}
	"F-05": {
		title: "SpecDock の側で worktree の記録を読めないときは、どの Scope にも対応させない"
		text:  "要約の `issue` や名前から推し量らない。"
	}
	"F-06": {
		title: "ダッシュボードが別の画面に埋め込まれている（embed）ときは、印は出すが「Orca で開く」は置かない"
		text:  "orca-web の `frame-ancestors` は祖先のすべての画面を確かめるので、埋め込み先（company-os など）のオリジンが許されていなければボタンが描けない。壊れた枠を見せないために置かない。"
	}
}

constraints: [
	"SpecDock のサーバーは見るだけのまま（GET だけ。今の「見た」の記録の POST のほかに書く口を足さない）。サーバーは orca-web と Orca を読まず、Orca の CLI を呼ばない",
	"印、色、経過の表記、ボタンは orca-web の部品をそのまま使う。SpecDock の app.css で印の色を上書きしない（orca-web の部品が SpecDock の変数を先に使う）",
	"公開のリポジトリ（コード、テスト、文書、仕様）に実際の Tailscale の IP を書かない。例は 127.0.0.1 と、文書用の IP（RFC 5737 の 192.0.2.x など）にする",
	"新しい依存（Python、JavaScript）を足さない",
]

decisions: [
	"2026-11-03（epic-00427 のデザインの決定から）：構造の図とボードに、作業中の worktree の最後の更新の時刻は出さない。代わりに、Orca のエージェントが作業を終えてからの待ち時間を、印の経過（now・5m・3h・2d）で示す（R-06）。起点は orca-web の要約の `elapsedFrom`（`since` があればその状態になった時刻）で、orca-web の部品が描く（2026-11-14、統括の決定8）",
	"2026-11-14、統括の決定1：SpecDock のブラウザーの画面が orca-web を直接読む（読み取りの CORS）。SpecDock のサーバーは orca-web を代わりに読まない。orca-web の場所は、画面を開いたホスト名と同じ名前の 8791 を既定とし、設定で変えられる形を設計で決める",
	"2026-11-14、統括の決定2：Scope と worktree の対応は SpecDock が決める。パスが一致すればそれ、なければ同じリポジトリのブランチ名の一致。要約の `issue` は参考に留める。対応しない worktree は出さない。親の Scope は、自分に対応する worktree があるときだけ印を出し、配下を合算しない",
	"2026-11-14、統括の決定3・4・6：印は構造の図の箱、ボードの札、横の欄の見出しに、orca-web の部品で出す。横の欄の見出しに open-button.js を置く。スマホ（390px 以下）では orca-web の部品が自分で出さない。orca-web に届かないときは、印は出さず、図やボードを止めない",
	"2026-11-14、設計の担当の判断（統括の決定1の「設定で変えられる形」の具体化）：設定は `config.json` の最上位の新しい節 `orca_web`（`enabled`、`port`）に置く。ホスト名は変えられない（orca-web は同じ PC で 127.0.0.1 と Tailscale の IP だけで待ち受け、SpecDock の画面と同じ名前で読むため）。`dashboard` の節に入れないのは、誤りが全リポジトリを隠す側に倒れないようにするため",
	"2026-11-14、設計の担当の判断（統括の決定2の「同じリポジトリ」の具体化）：同じリポジトリは、要約の中で、このリポジトリの worktree のパスとパスが一致した worktree の `project.id` で決める。手がかりがなければブランチ名だけでは対応させない（別のリポジトリに同じブランチ名があるため。例：orca-web と spec-dock の両方に iss-00014 がある）",
]
