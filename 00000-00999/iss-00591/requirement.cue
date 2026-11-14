package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードのサーバーが返す項目と CSP に orca-web の場所を足し、画面の側で orca-web の要約を読んで Scope に対応させる。書き込みはなく、誤りは印の出し間違いか出ないことにとどまり、PR を戻せば元に戻る。ただし対応の誤りは後のエージェントのタブ（epic-00526）の相手の選びに及ぶので、レビューと最終品質ゲートを通す"
}

purpose: "ダッシュボードの画面が orca-web の場所を知り、その要約を1つの輪で読み、SpecDock の worktree の記録と突き合わせて Scope ごとの worktree を決められるようにする（epic-00471 の第1の切り分け。画面に印はまだ描かない）。"

background: """
	親の Epic epic-00471 の plan.cue の slice `iss-00591` は、Epic の R-01〜R-04、F-02、F-04、F-05 と、設計 D-01〜D-05 を受け持つ。
	印とボタンの描き（Epic の R-05〜R-09、D-06〜D-08）は iss-00592 が、エージェントのタブは epic-00526 の iss-00593 が、この Issue の対応と状態を使って作る。

	2026-11-14 に開始のコミット `89f51588a` で確かめた事実：

	- 構造の API の Scope の項目は `branch`（この PC の `git worktree list` のうち、ブランチ名がその Scope を名指す最初の worktree のブランチ）だけを持つ（`application/dashboard_scope_details.py` の `read_structure_facts`、`presentation/dashboard_api.py` の `scope_item`）。
	- 構造の revision（`application/dashboard_site.py` の `_revision`）の材料に worktree の変化は入っていない。画面は revision が変わったときだけ構造を読み直す（Epic の spec-review の P2 の引き継ぎ）。
	- 画面の CSP は `application/dashboard_http.py` の固定の `_SHELL_CSP`。リポジトリの一覧の API の `server` は要求の Host を使わずに作る。
	- 利用者の設定 `config.json` の読み（`domain/dashboard_visibility.py` の `parse_user_dashboard`）は、知らない最上位の鍵を無視する。ファイルが JSON でない、`schema` が違うときは、`dashboard` の節が invalid になる。
	- 常駐の orca-web（127.0.0.1:8791）の要約では、spec-dock の main のチェックアウトと、linked worktree（iss-00591、iss-00594）が同じ `project.id` を持つ。`path` が null の worktree もある。
	"""

includes: [
	"`config.json` の最上位の節 `orca_web` の読み、orca-web のオリジンの決め方、画面の CSP、リポジトリの一覧の API の `server.orca_web`、`spec-dock dashboard list` の `config_problems`",
	"構造の API の、Scope ごとの worktree の記録と、文書の上の worktree のパスの一覧。worktree の変化で構造の revision が変わること",
	"画面の `core/orca_match.js`（対応と状態の純粋な計算）と `core/orca.js`（部品の import、1つの読みの輪、試し直し、知らせ、Scope ごとの worktree）と、シェル（`app.js`）がそれを1つ作って画面に `ctx.orca` で渡すこと",
	"Python と node のテスト。常駐の orca-web を読むだけの、実データの対応の確かめ",
]

excludes: [
	"構造の図、ボード、横の欄への印と「Orca で開く」（iss-00592）。配る文書（iss-00592、Epic の R-09）",
	"エージェントのタブ（epic-00526）。`server.orca_web.problem` の画面での見え方（epic-00526）",
	"orca-web の側の変更と、常駐の orca-web・常駐のダッシュボードの設定の変更",
	"SpecDock のサーバーが orca-web や Orca を読むこと",
]

requirements: {
	"R-01": {
		title: "orca-web の場所は、画面を開いた Host の名前と同じ名前の 8791 を既定とし、`config.json` の `orca_web` で切るかポートを変えられる"
		text: """
			Epic の R-01。オリジンは `http://<要求の Host のホスト名>:<port>`。`port` の既定は 8791。ホスト名は、ダッシュボードのサーバーが許した Host の名前だけを使う（許していない Host は今と同じく 421）。
			`config.json` の最上位の節 `orca_web: {enabled?: true|false, port?: 1〜65535 の整数}`。設定を変えると、サーバーを起動し直さずに次の要求から効く。
			リポジトリの一覧の API（`/api/v1/repositories`）の `server.orca_web` に `{enabled, origin, port, problem}` を返す。画面はこの値だけで orca-web の場所を知る。
			"""
		acceptance: [
			"設定がないとき、Host `127.0.0.1:<ダッシュボードのポート>` の一覧の API の `server.orca_web` が `{enabled: true, origin: \"http://127.0.0.1:8791\", port: 8791, problem: null}` で、許した別の Host（文書用の IP の例 192.0.2.10）ではその名前の 8791 になる",
			"`orca_web.port` を 9001 に書き換えると、サーバーを起動し直さずに、次の一覧の API の origin が `:9001` になる",
			"`orca_web.enabled` が false のとき、`server.orca_web` は `{enabled: false, origin: null, …}` である",
		]
	}
	"R-02": {
		title: "画面の CSP は、連携が有効なときだけ、その orca-web のオリジンを4つの指示に足す"
		text: """
			Epic の R-02。有効なとき、画面の HTML の CSP の `script-src`、`style-src`、`connect-src`、`frame-src` の値の末尾に、R-01 のオリジンを1つ足す。ほかのオリジンは足さない。
			無効なときは今と同じ文字列。JSON の口と /files/ の資料の CSP、`frame-ancestors` は変えない。
			"""
		acceptance: [
			"有効なとき、画面の CSP の4つの指示に、そのオリジンだけが足され、ほかの指示は今と同じ",
			"`enabled: false` のとき、画面の CSP は開始のコミットと同じ文字列である",
			"JSON の口と /files/ の CSP は開始のコミットと同じである",
		]
	}
	"R-03": {
		title: "構造の API は、Scope ごとの worktree の記録と、クローンの worktree のパスの一覧を返し、worktree の変化で revision が変わる"
		text: """
			Epic の R-03。各 Scope の項目に `worktrees: [{path, branch}]`（`git worktree list` のうち、ブランチ名がその Scope を名指すすべて、一覧の順）を足す。今の `branch` はその最初のブランチのまま。
			文書の上に `worktrees: {status: "ok" | "unreadable", paths: [クローンのすべての worktree のパス]}` を足す（main のチェックアウト、linked worktree、カタログの worktree を含む）。
			worktree の追加、削除、移動、ブランチの切り替えで、構造の revision が変わる（画面の5秒ごとの revision の読みで、構造が読み直される。Epic の spec-review の P2）。サーバーは orca-web を読まない。
			"""
		acceptance: [
			"`chemitaro/iss-00591` のブランチの worktree があるクローンで、構造の API の iss-00591 の項目の `worktrees` に、そのパスとブランチが入る",
			"文書の上の `worktrees.paths` に、main のチェックアウトのパスと、linked worktree のパスが入る",
			"linked worktree を足すか、そのブランチを切り替えると、次の revision の API の値が変わる",
		]
	}
	"R-04": {
		title: "Scope と orca-web の worktree の対応は、パスの一致か、同じリポジトリのブランチ名の一致で決める"
		text: """
			Epic の R-04 と D-04。純粋な関数 `matchWorktrees(structure, summary)` が決める。

			1. パスの一致：要約の worktree の `path` が、ある Scope の worktree の記録の `path` と、末尾の `/` を除いて完全に一致する。
			2. 同じリポジトリのブランチ名の一致：1 で対応しなかった要約の worktree は、その `project.id` が「パスが `structure.worktrees.paths` のどれかと一致した要約の worktree」の `project.id` の集合にあり、かつ `branch` が、ある Scope の worktree の記録の `branch` と完全に一致するときだけ、その Scope に対応する。

			要約の `issue`、`project.name`、`id` は比べない。1つの要約の worktree は多くても1つの Scope に入る。親の Scope は、自分のブランチの worktree が対応したときだけ worktree を持ち、配下を合算しない。
			"""
		acceptance: [
			"パスが一致する worktree は、その Scope に対応する（末尾の `/` の有無を問わない）",
			"パスが違い、同じリポジトリの手がかりがあり、ブランチが一致する worktree は、その Scope に対応する",
			"同じブランチ名でも、project.id が手がかりにない worktree は対応しない。手がかりがないときも対応しない",
			"`issue` だけが Scope の ID と一致する worktree は対応しない",
			"Epic は、配下の Issue に worktree が対応しても、自分の worktree がなければ空である",
		]
	}
	"R-05": {
		title: "画面は orca-web の要約を1つの輪で読み、状態と Scope ごとの worktree を、描く側に知らせる"
		text: """
			Epic の D-05。シェル（`app.js`）がリポジトリの一覧の API の `server.orca_web` を受けて `core/orca.js` の部品を1つ作り、画面に `ctx.orca` で渡す（画面はまだ使わない）。
			有効なとき、orca-web の `agent-marks.css` を1回足し、`agent-marks.js` を import し、`watchWorktreeSummary` を1つだけ動かす。import に失敗したら 10 秒後に問い合わせの文字列を変えて import し直す。
			状態（off、loading、unreachable、orca-unreachable、orca-starting、ok）と、ok のときの最後の要約と、Scope ごとの worktree（R-04）を返し、要約か状態が変わるたびに知らせる。
			SpecDock の画面の JavaScript が orca-web に送るのは、要約の GET と、部品の import と CSS だけ。
			"""
		acceptance: [
			"有効な設定で作ると、部品の import は1回、要約の読みの輪は1つで、読めた要約で状態が ok になり、知らせが呼ばれる",
			"import が失敗すると状態が unreachable になり、次の試しが `?r=1` を付けた URL で行われ、成功すると読みの輪が始まる",
			"読みが失敗すると、前の要約を捨てて unreachable になり、`forScope` が空の並びを返す",
			"`connection.state` が unreachable なら orca-unreachable、starting なら orca-starting、connected なら `stale` が true でも ok である",
		]
	}
	"R-06": {
		title: "常駐の orca-web の実データで、Scope と worktree の対応を確かめて記録する"
		text: """
			隔離した venv と一時の状態の置き場で、別のポートの SpecDock（`--tailscale`）を立て、その構造の API を、node の上で本物の orca-web の部品と常駐の orca-web の要約（読むだけ）で動かした `core/orca.js` に渡して、対応した Scope と worktree の数を report.md に残す。
			ブラウザーの画面からは、orca-web の `ORCA_WEB_READ_ORIGINS` が別のポートを許さないので、部品の import が 403 で拒まれて unreachable になり、図とボードが今までどおり動くことを確かめる（常駐の設定は変えない）。
			"""
		acceptance: [
			"report.md に、試しの SpecDock の版とポート、要約の worktree の数、`core/orca.js` の状態が ok になったこと、対応した Scope と worktree の数と ID（この Issue の worktree が iss-00591 に対応すること）がある",
			"report.md に、試しの画面のオリジンからの部品の import が 403 で拒まれ、`?r=1` で試し直され、要約の GET が出ず、図とボードが今までどおり描かれたことの記録がある",
		]
	}
}

failures: {
	"F-01": {
		title: "要約の形が違う（null、schema が違う、worktrees が並びでない）ときは、読めないときと同じに扱い、どの Scope にも対応させない"
		text:  "Epic の F-02。`matchWorktrees` は `status: \"invalid\"` と空の対応を返し、`orcaStatus` は unreachable を返す。要約の worktree の `path` や `branch` や `project` が null か文字列でないときは、その項目を比べに使わない。"
	}
	"F-02": {
		title: "連携を切っている（enabled が false）か、`orca_web` の節が読めないときは、orca-web に何も要求せず、CSP も今のまま。ほかの節の読みに影響させない"
		text: """
			Epic の F-04。節の形や値が違う、`port` がダッシュボード自身のポートと同じ、ファイルが読めない・JSON でない・`schema` が違うときは、`enabled: false` と同じに扱い、`problem` に理由を持つ。
			節だけの誤りは `spec-dock dashboard list` の `config_problems`（層は user、パスは `config.json`）に1行で出す。ファイルそのものの誤りは、今の `dashboard` の節の誤りとして既に出るので、重ねて出さない。
			`orca_web` の節の誤りで、`dashboard` と `todo` の節の読みと、リポジトリの出し入れは変わらない。
			"""
	}
	"F-03": {
		title: "SpecDock の側で worktree の記録を読めない（`git worktree list` の失敗、カタログがない）ときは、どの Scope にも対応させない"
		text:  "Epic の F-05。構造の `worktrees.status` が unreadable なら、`matchWorktrees` は `status: \"no-records\"` と空の対応を返す。要約の `issue` や名前から推し量らない。"
	}
}

constraints: [
	"SpecDock のサーバーは見るだけのまま（GET と今の「見た」の POST だけ）。サーバーは orca-web と Orca を読まず、Orca の CLI を呼ばない",
	"構造の API とリポジトリの一覧の API は項目を足すだけで、`API_SCHEMA` は変えない",
	"公開のリポジトリ（コード、テスト、文書、仕様）に実際の Tailscale の IP、ユーザー名、利用者の PC のパスを書かない。例は 127.0.0.1 と、文書用の IP（RFC 5737 の 192.0.2.x）にする。report.md の実機の記録は Scope のディレクトリ（Git で扱わない）に置き、その中でもユーザー名を含む絶対パスは書かない",
	"新しい依存（Python、JavaScript）を足さない",
	"常駐の orca-web と常駐のダッシュボード（47800）と道具の環境の spec-dock に触れない（読むだけ）",
]

decisions: [
	"2026-11-14、親の Epic の decisions：設定は `config.json` の最上位の節 `orca_web`、ホスト名は変えられない、同じリポジトリは要約の中でパスが一致した worktree の `project.id` で決める",
	"2026-11-14、タスク担当の判断（Epic の spec-review の P2 の1つ目）：worktree の変化を構造の revision に入れる。`git worktree list` を5秒ごとに呼ばず、main のチェックアウトの `.git` の `HEAD` と `worktrees/` の項目のファイルの時刻と大きさから作る署名を使う（D-03）",
	"2026-11-14、タスク担当の判断（Epic の spec-review の P2 の3つ目）：実データの確かめの例は、マージで片付けられた iss-00589 ではなく、この Issue の worktree（iss-00591）を使う",
	"2026-11-14、タスク担当の判断：ファイルそのものが壊れているとき、`orca_web` は無効にし、`config_problems` には今の `dashboard` の行だけを出す（同じファイルの同じ理由を2行にしない）",
	"2026-11-14、タスク担当の判断（Epic の D-02 の config_problems の具体化）：`port` がダッシュボード自身のポートと同じ誤りは、要求を受けたサーバーだけが知る（`dashboard list` はサーバーなしでも動き、DashboardSite はポートを持たない）ので、`server.orca_web.problem` にだけ出し、`config_problems` には出さない。`config_problems` に出すのは、ファイルだけで決まる節の形と値の誤り",
	"2026-11-14、タスク担当の判断（仕様のレビューの P2）：orca-web は部品のファイルも読み取りの CORS で配るので、別のポートの試しの画面からは import が 403 になる。本物の部品と要約での `core/orca.js` の確かめは node の上で行い、ブラウザーでは拒まれる側の振る舞いを確かめる",
	"2026-11-14、本人の指示（依頼書）：サーバー側と純粋な計算の実装は Codex GPT-6.1 Sol / medium",
]
