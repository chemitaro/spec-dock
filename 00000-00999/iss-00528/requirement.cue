package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00427。plan.cue の slice `iss-00528`（covers: R-07、R-09、R-10、R-20、R-21、R-29、R-31、F-01〜F-04、F-06）を、この Issue の番号に書き直した。
// Epic の番号は「Epic R-10」のように書く。この Issue の番号は R-01 などである。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
assurance: {
	level:  "standard"
	reason: "状態の判定と公開の要約の JSON（統合ダッシュボードとエージェントが読む契約）を作る。誤りは表示と要約の誤りで、版を戻せば回復できる。"
}

purpose: "ダッシュボードの画面（#529 以降）と要約の CLI が同じものを示すように、構造のスナップショットから、状態、ボードの分け方、推奨順、片付けの候補、配下の段、前回からの変化、時間の軸の数を作る1つのモデルを作る。あわせて、その要約を版つきの JSON で返す `spec-dock dashboard summary` を出す。"

background: """
	- 親の Epic（epic-00427）の設計 D-04（状態のモデル）、D-05（要約の契約）、D-12（読めないときの扱い）、D-01 のうち `dashboard summary` を、この Issue が作る。HTTP のサーバーと画面は #529 以降。
	- 構造は epic-00424 の構造のスナップショット（`<state_root>/github/<host>/<owner>/<name>/snapshot.json`）にある。PR の欄は #537 がスナップショットの版2に足す（D-19）。#537 との形の合意は `decisions` に書いた。
	- 着手の判定は `runtime/domain/canonical_readiness.py` の `evaluate_readiness`／`evaluate_all` にあり、`dependency check` と `work start` が使う。状態はそれを写し、別に書かない（Epic R-10）。
	- 推奨順と後に続く数の決まりは、利用者が採った試作（`epic-00427/artifacts/20261103t150110z--dashboard-design-d2.html` の `recCmp` と `down`）を参考にした。正本は Epic の R-31 と R-15。
	"""

includes: [
	"領域のモデル `runtime/domain/dashboard_model.py`（純粋な関数。ファイルもネットワークも読まない）",
	"スナップショットのファイルの読み（版1と版2、PR の欄の解析、読めない・知らない版・ないの見分け）",
	"要約の JSON（`specdock.dashboard-summary/v1`）の組み立て",
	"コマンド `spec-dock dashboard summary [REPOSITORY]`（公開のコマンドが 53 → 54）と、コマンドの数を縛るテストと文書",
	"「見た」の記録の1件を、モデルから作る関数と、比べる関数（ファイルの読み書きは #529）",
]
excludes: [
	"HTTP のサーバー、API、画面、「見た」の記録のファイルの読み書きと POST の口、在りかの記録と隠す印のファイルの書き手（#529）",
	"PR の取得とスナップショットの書き手（#537）。`canonical_sync` と `SnapshotStore` の書き手は変えない",
	"構造の図の配置と依存の線の経路（#532）",
	"`dashboard serve`、`service`、`hide`、`show`、`list` のコマンド（#529、#530）",
	"版の番号、`migration.md`（#534）。`static-inventory.json` は、この Issue で変えた配布文書の行の sha256 と known_old_sha256 だけを変える（統括の決定）",
]

requirements: {
	"R-01": {
		title: "各 Scope の状態を、着手の判定から5つに決める"
		text: """
			どの種類も `evaluate_all` の結果を写す：DONE → 終わった（`done`）、UNKNOWN → 不明（`unknown`）、DOING → 作業中（`doing`）、BLOCKED → 止められている（`blocked`）、READY → 着手できる（`ready`）。Epic と Initiative は、DONE でも UNKNOWN でもなく、開いた子孫のどれかに作業中の印があれば、作業中にする（これだけを足す）。

			各 Scope に理由を付ける。止められているときは、閉じた祖先（「親が閉じている」）、自分の依存の先、祖先から引き継いだ依存の先、Scope でない Issue を見分ける。不明のときは、構造の異常のコードを示す。（Epic R-10、F-06）
			"""
		acceptance: [
			"見本の構造（作業中の印、開いた依存、親から引き継いだ依存、Scope でない Issue への依存、閉じた Scope、閉じた異常の Scope、祖先の異常、閉じた親の下の開いた Issue、配下だけに作業中の印がある Epic）で、各 Scope の状態がこのとおりになる",
			"見本のすべての Issue で、状態が `evaluate_readiness` の結果と一致する",
			"構造の異常がある Scope は不明になり、ほかの Scope の状態は決まる",
		]
	}
	"R-02": {
		title: "ボードの列と、マージ待ちの「マージできる」「直す必要あり」を決める"
		text: "各 Scope に、ボードの列（`blocked`、`ready`、`doing`、`awaiting_merge`、`done`、`unknown`）を決める。作業中の Issue で、選んだ PR が開いていて下書きでないものを `awaiting_merge` にし、CI が失敗したか衝突のあるものを「直す必要あり」（`needs_fix`）、ほかを「マージできる」（`mergeable`）にする。状態の5つの区分は変えない。PR の状態が分からないとき（R-08）は、マージ待ちにしない。（Epic R-13、R-30）"
		acceptance: [
			"見本で、下書きでない PR が開いている作業中の Issue がマージ待ちに、下書きの PR の Issue が作業中の列に出る",
			"CI が失敗した PR と衝突した PR が「直す必要あり」に、CI が成功、実行中、なし、マージの可否が分からないものが「マージできる」に分かれる",
		]
	}
	"R-03": {
		title: "推奨順に並べ、後に続く数と待ち先の数を示す"
		text: """
			開いた Scope ごとに、後に続く数（それを直接か間接に待っている開いた Scope の数）と、まだ終わっていない待ち先の数（自分と祖先の依存の先のうち、完了で閉じていない Scope と、開いている Scope でない Issue の数）を求める。

			推奨順：マージできる → 直す必要あり → 作業中 → 着手できる → 止められている → 不明 → 終わった。マージ待ち、作業中、着手できるの中は、後に続く数の多い順、同じなら番号の小さい順。止められているの中は、待ち先の数の少ない順、次に後に続く数の多い順、番号の小さい順。不明は番号の小さい順。終わったは、閉じた時刻の新しい順。ボードの各列と、要約の一覧は、この順に並べる。（Epic R-31）
			"""
		acceptance: [
			"見本で、着手できるものの先頭に、待っている開いた Scope の数が一番多いものが来る",
			"見本で、止められているものが待ち先の数の少ない順に並ぶ",
			"親を待つ Scope と、その配下も、後に続く数に数える",
		]
	}
	"R-04": {
		title: "片付けの候補と、終わったものを隠すときに残す Scope を挙げる"
		text: "片付けの候補は、Epic R-20 の2つの種類：配下がすべて閉じたのに開いている Epic と Initiative（配下が1つ以上あるとき）と、閉じたのに開いた配下がある親。加えて、Epic R-10 のとおり、閉じた祖先のために止められている開いた Scope も挙げる。それぞれ理由を付ける。開いた子孫を持つ閉じた Scope には「隠すときも残す」の印を付ける。見るだけで、直さない。（Epic R-12、R-14、R-20）"
		acceptance: ["見本で、片付けの候補の2つの種類と、閉じた親の下の開いた Scope が、理由つきで挙がり、開いた子孫を持つ閉じた親に残す印が付く"]
	}
	"R-05": {
		title: "配下の実行の順番を段に分け、依存の道筋をたどれる"
		text: """
			親（とリポジトリの頂上）ごとに、直下の子を、子孫どうしの依存も子の間の依存に数えて、段（1、2、…）に分ける。外への依存は別に持ち、循環する子は段に入れずに別に示す。開いたものだけの段（閉じた子と、閉じた先への依存を除く）も作る。

			ある Scope の上流（前に終わるべきもの）と下流（後に続くもの）を、間接のものまで求め、直接と間接を分ける。止められている Scope の大もとの待ち先（上流の端で、止められていないもの）を求める。（Epic R-15、R-18）
			"""
		acceptance: [
			"見本の依存のとおりに、配下が段に分かれ、外への依存が別に出る",
			"見本で、止められている Scope の大もとの待ち先が、上流の端の止められていない Scope になる",
		]
	}
	"R-06": {
		title: "前回見たときと比べて、変化を見つける"
		text: "モデルから「見た」の記録の1件（各 Scope の状態と PR の段階）を作る。比べる元の記録と今のモデルを比べ、状態が変わった Scope、新しい Scope、PR の段階が変わった Scope（開いた、マージ待ちになった、直す必要が出た、マージされた、閉じた）を挙げる。題名、親子、依存だけの変化は数えない。どちらかで PR の状態が分からないときは、PR の変化を数えない。比べる元がなければ、変化はない。（Epic R-29、D-18）"
		acceptance: [
			"見本で、前回見た後に状態が変わった Scope、新しい Scope、PR が変わった Scope が挙がり、題名だけが変わった Scope は挙がらない",
			"比べる元がないときは、変化が0件になる",
		]
	}
	"R-07": {
		title: "時間の軸の、週ごとの累計と最近の動きを作る"
		text: "作成と完了の時刻から、週（月曜から、UTC）ごとに、作られた Scope と終わった Scope の累計を作る。数える種類を選べる。最近の動きとして、Scope の作成と完了、PR の開いた時刻とマージの時刻を、時刻の新しい順に並べる。（Epic R-16）"
		acceptance: ["見本の作成と完了の時刻から、週ごとの累計が正しく出る。最近の動きに Scope と PR の出来事が、時刻の新しい順に並ぶ"]
	}
	"R-08": {
		title: "構造と PR の状態をスナップショットから読み、版1も読む"
		text: """
			構造はスナップショットの版1と版2から、PR の欄（`pull_requests`、`pull_requests_error`、`pull_requests_fetched_at`）は版2から読む。PR は、そのブランチの名前が Scope を名指すとき（`branch_names_scope`）に、その Scope に対応づける。同じ Scope に複数あれば、開いているものを先に、次に作られた時刻の新しいものを選ぶ。

			PR の状態の確かさは3つ（Epic D-19）：版1か、`pull_requests_fetched_at` が null か30分を超えて古ければ「分からない」（`unknown`。PR を使わない）。取得の時刻は新しいが、最後の取得が失敗している（`pull_requests_error` がある）なら「古い」（`stale`。前回の値を使い、「分からない／古い」の印を付ける）。ほかは「新しい」（`fresh`）。GitHub に問い合わせない。（Epic R-07、R-30）
			"""
		acceptance: [
			"見本の版2のスナップショットから、PR がブランチの名前で Scope に対応づき、版1のスナップショットも読めて PR の状態が「分からない」になる",
			"30分を超えて古い取得の時刻で PR の状態が「分からない」になり、新しい取得の時刻と失敗の記録で「古い」になって前回の値が使われる",
		]
	}
	"R-09": {
		title: "構造を取得した時刻と古さと、構造の異常を示す"
		text: "モデルと要約に、構造を取得した時刻（`fetched_at`）と、30分を超えて古いか（`stale`）を持つ。構造の異常（`anomalies`）を、そのまま渡し、数を示す。（Epic R-09、F-02）"
		acceptance: ["31分前に取得したスナップショットで `stale` が真に、29分前で偽になり、異常の数が要約に出る"]
	}
	"R-10": {
		title: "要約を、版を持つ JSON（`specdock.dashboard-summary/v1`）で作る"
		text: "モデルから、`schema`、`repository`、`fetched_at`、`stale`、`counts`（種類ごと・状態ごとの数）、`completion_ratio`、`awaiting_merge`・`in_progress`・`ready`・`blocked`・`cleanup` の一覧（各要素は `id`、`number`、`kind`、`title`、`state`、`reason`。推奨順）、`anomaly_count`、`pull_requests`（PR の状態の確かさ）、`paths`（各 Scope の詳しい画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>`）、`hidden`、`server` を作る。サーバー（#529）も同じ関数で作り、内容が同じになる。（Epic R-21、D-05）"
		acceptance: [
			"見本で、要約の JSON が上の項目をすべて持ち、数と一覧がモデルと一致する",
			"同じ入力から、同じ JSON が作られる（サーバーが同じ関数を呼べる）",
		]
	}
	"R-11": {
		title: "`spec-dock dashboard summary` が、ネットワークに触れずに要約を返す"
		text: "`spec-dock dashboard summary [REPOSITORY] [--json]` は、チェックアウトの中では REPOSITORY を省ける（`origin` から決める）。外では `owner/name` か `host/owner/name` で指す。サーバーが動いていなくても、隠したリポジトリでも動く。GitHub にもサーバーにも要求を送らず、在りかの記録の `pid` が生きているかだけを見る。`--json` は `specdock.cli/v2` の封筒の `data.result` に要約を入れる（`data.kind` は `dashboard`。ほかのコマンドと同じ形）。（Epic R-21、D-01）"
		acceptance: [
			"見本のスナップショットで、チェックアウトの中と外（REPOSITORY を指定）の両方から要約が返り、GitHub への要求がない",
			"在りかの記録の `pid` が生きていれば `server` にその URL が、生きていなければ null が出る。隠す印があれば `hidden` が真になる",
			"公開のコマンドが54になり、コマンドの数を縛るテストと文書が合う",
		]
	}
}

failures: {
	"F-01": {
		title: "スナップショットがない"
		text:  "`dashboard summary` は `DASHBOARD_SNAPSHOT_MISSING`（終了コード3）で止まり、次の1手（`spec-dock canonical link`、`spec-dock canonical status`）を示す。（Epic F-01）"
	}
	"F-02": {
		title: "スナップショットが30分を超えて古い"
		text:  "要約を返し、`stale` を真にする。（Epic F-02）"
	}
	"F-03": {
		title: "スナップショットが知らない版"
		text:  "読まずに `DASHBOARD_SNAPSHOT_UNSUPPORTED`（終了コード3）で止まり、SpecDock の更新を示す。読み手は、この見分けを返す。（Epic F-03）"
	}
	"F-04": {
		title: "スナップショットが読めない（壊れている、別のリポジトリのもの）"
		text:  "`DASHBOARD_SNAPSHOT_UNREADABLE`（終了コード3）で止まり、`spec-dock canonical status` と次の同期を示す。最後に読めた内容で続けるのは、記憶を持つサーバーの側（#529）。（Epic F-04）"
	}
	"F-05": {
		title: "構造の異常（親の欠け、依存の循環、種類の決まらない Issue）"
		text:  "その Scope を不明として示し、ほかの表示は続ける。段の計算では、循環する子を段に入れずに別に示す。（Epic F-06）"
	}
	"F-06": {
		title: "在りかの記録や隠す印のファイルが、ない、壊れている"
		text:  "要約は止まらない。在りかの記録が読めなければ `server` を null に、隠す印が読めなければ `hidden` を偽にする。"
	}
}

constraints: [
	"ダッシュボードとその CLI は GitHub に要求を送らない（Epic の制約）",
	"状態の判定を別に書かない。`evaluate_readiness`／`evaluate_all` を写す",
	"同期（`canonical_sync`）とスナップショットの書き手は変えない（#537 の範囲）",
	"版の番号と `migration.md` は変えない（#534）。`static-inventory.json` は、変えた配布文書の行の sha256 と known_old_sha256 だけを更新する",
]

decisions: [
	"2026-11-04（統括、#537 と合意）：スナップショットの版2の PR の欄は `pull_requests: {\"<番号>\": {number, state: open|closed|merged, is_draft, head_ref_name, mergeable: mergeable|conflicting|unknown, checks: success|failure|pending|none, created_at, merged_at|null, closed_at|null, url}}` と `pull_requests_error: null|{code, message, at}`。鍵は snake_case、値は小文字、時刻は UTC の Z 形式。Scope との対応はスナップショットに持たず、読む側が `branch_names_scope` で求める（open を先、次に created_at の新しい順）",
	"2026-11-04（統括、#537 から）：版2に `pull_requests_fetched_at: null|\"<UTC Z>\"` がある。null か版1なら PR の状態は分からない。`pull_requests` が {} で取得の時刻が新しければ PR は0件。`pull_requests_error` があっても前回の値を表示に使ってよいが、「分からない／古い」の印を付ける。30分を超えて古いときは「分からない」とする（Epic D-19）",
	"2026-11-04（統括）：当面、#528 は自分の領域で PR の欄を解析する。後にマージするほうが、もう一方の部品に寄せて重複を消す",
	"2026-11-04（この Issue の判断）：`dashboard summary` は、リポジトリごとのファイル（スナップショット、隠す印、在りかの記録）だけを読み、クローンの選択に関わらないので、同じリポジトリのクローンが2つ登録されていても曖昧にしない（`DASHBOARD_REPOSITORY_AMBIGUOUS` は、クローンを選ぶ必要のある #529 のコマンドに残す）",
	"2026-11-04（この Issue の判断）：Epic と Initiative を作業中にする子孫の作業中の印は、開いた子孫のものだけを数える（閉じた Scope に残った印で作業中にしない）",
	"2026-11-04（この Issue の判断）：片付けの候補には、Epic R-20 の「閉じたのに開いた配下がある親」として閉じた親そのものを挙げ、Epic R-10 のとおり、閉じた祖先のために止められている開いた Scope も挙げる（試作は開いた子の側だけを挙げていた）",
	"2026-11-04（統括）：コマンドの一覧の配布文書を変えるので、`static-inventory.json` の、その文書の行の sha256 を更新し、前の sha256 を known_old_sha256 に足す。版の番号、`migration.md`、ほかの行は変えない。#530・#533 と重なったら、後にマージするほうが取り込み直す",
]
