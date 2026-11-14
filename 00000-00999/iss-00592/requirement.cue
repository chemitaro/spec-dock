package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル。正本はここだけ。
assurance: {
	level:  "standard"
	reason: "ダッシュボードの画面に orca-web の部品（稼働の印、Orca で開くのボタン）を置くだけで、SpecDock は見るだけのまま。誤りは表示の誤りか、ボタンが出ないことにとどまり、PR を戻せば元に戻る。主な画面の見た目が変わるので、レビューと最終品質ゲートを通す"
}

purpose: "epic-00471 の第2の切り分け。iss-00591 が作った `ctx.orca`（要約の1つの読みの輪と、Scope と worktree の対応）を使い、構造の図の箱と枠、ボードの札、横の欄の見出しに orca-web の稼働の印を描き、横の欄の見出しに「Orca で開く」を置く。配る文書に連携の設定と前提を書く。"

background: """
	正本は Epic epic-00471 の requirement.cue・design.cue（D-06、D-07、D-08）と plan.cue の slice `iss-00592`（R-05〜R-09、F-01、F-03、F-06）。
	iss-00591（PR #596、main `67abbe6c1`）が、`config.json` の `orca_web`、画面の CSP、一覧の API の `server.orca_web`、構造の API の `worktrees`、`core/orca_match.js`（`matchWorktrees`、`mergedWorktree`、`orcaStatus`）、`core/orca.js`（`createOrca`。`status()`、`summary()`、`marks()`、`origin`、`subscribe(fn)`、`forScope(structure, id)`、`stop()`）を作り、`app.js` が `ctx.orca` を画面に渡している。画面に印はまだない。

	統括の決定（2026-11-14、この Issue の依頼書。`epic-00471/.workbench/owner-iss-00592.md`）：

	1. 構造の図の箱：今の箱の大きさ（`views/graph/layout.js` の `SIZE`）を変えない。箱の下の段（保証レベルや PR の小さな印の行 `.gx-marks`）の右寄せに orca-web の印の部品を置く。入りきらないときは部品の「+N」に任せる。
	2. ボードの札：札の下の段の右寄せに、同じ部品を置く。
	3. 横の欄の見出し：状態の札の行に、同じ部品（経過つき）を置き、右端に orca-web の `open-button.js`（`data-worktree` に対応した worktree）を置く。スマホ（390px 以下）では orca-web の部品が自分で出さない。
	4. 印を押したときは、その Scope の横の欄を開く（iss-00593 のエージェントのタブができたら、そのタブを開く。できる前は欄を開くだけ）。
	5. 印は、対応した worktree にエージェントがいる Scope だけに出す。いないときは何も出さず、場所も空けない。
	6. 見た目：色・状態・印・経過の表記は orca-web の部品のまま。SpecDock の中で描き直さず、新しい色を足さない。

	orca-web の部品の事実（orca-web の main `1a2afed` の `web/embed/` を読んで確かめた）：

	- `renderAgentMarks(container, worktree, {now, size, max, onSelect})` は、呼ぶたびに container の中身を `replaceChildren` で作り直す。`onSelect` がなければ印は `role="img"` の span で、押せない。作業中の弧は CSS の animation で回るので、作り直すと回り始めに戻る。
	- `buildMarks(worktree, {now, max})` は純粋な関数で、描く印の形（`{marks, overflow}`）を返す。部品から export されている。
	- `open-button.js` は `document.currentScript` の `data-*` を読み、自分の直後に iframe（既定の幅 260、`data-size="sm"` で高さ 26）を差し込む。親の幅が 390px 以下の間は iframe を隠し、読み込まない。iframe の中では、ボタンが左に寄り、右に結果の短い文が出る。
	- iss-00593（epic-00526、並んで進む）は、共有のタブの並び `SCOPE_TABS` にキー `agents` のタブを足し、対応した worktree にエージェントがいるときだけ出す（epic-00526 の design.cue）。
	"""

includes: [
	"構造の図の Issue の箱（`.gx-marks`）、Epic・Initiative の枠の見出し（`.gx-fh`）と木の表示の枠の箱（`.gx-marks`）への稼働の印",
	"ボードの札の下の段への稼働の印",
	"横の欄の見出しの状態の札の行への稼働の印と「Orca で開く」",
	"印を押したときに、その Scope を選び、横の欄を開き、エージェントのタブがあればそれを開くこと",
	"描き直しで印がちらつかず、ボタンの iframe を読み込み直さないこと",
	"配る文書（`src/spec_dock/assets/spec_dock/docs/`）への、連携の設定と前提と届かないときの見え方",
]

excludes: [
	"エージェントのタブ、詳細とチャットの iframe（iss-00593）",
	"詳しい画面（`views/scope.js`）の見出し、時間の軸、概要、人のタスクの画面、タブの中の札（子の一覧など）への印",
	"iss-00591 が作った設定、CSP、API、`core/orca.js`、`core/orca_match.js` の契約の変更",
	"orca-web の側の変更（部品、色、経過の表記、CORS の許す先）",
	"構造の図の箱の大きさ（`SIZE`）と、配置の計算の変更",
]

requirements: {
	"R-01": {
		title: "構造の図の箱と枠、ボードの札、横の欄の見出しに、orca-web の部品で稼働の印を出す"
		text: """
			対応した worktree（`ctx.orca.forScope`）が1つ以上ある Scope に、orca-web の `renderAgentMarks` で印を描く。置き場：
			- 構造の図の Issue の箱と、木の表示の枠の箱：下の段（`.gx-marks`）の右寄せ。
			- 構造の図の Epic・Initiative の枠：見出し（`.gx-fh`）の右寄せ（Epic の design.cue D-06）。
			- ボードの札：下の段（`.sd-card__meta`）の右寄せ。札にほかの下の段の印がなくても、印があれば下の段に出す。
			- 横の欄：見出しの状態の札の行（`.pn-head`）。
			対応した worktree が2つ以上なら、`mergedWorktree` で1つにまとめて描く。対応した worktree がない、または `ctx.orca.status()` が ok でないときは、置き場に何も描かず、置き場は幅も高さも取らない（下の段がほかに何もなければ、下の段も出さない）。
			印の形、色、言葉、経過は orca-web の部品のまま。SpecDock の CSS は置き場の位置（右寄せ、縮まないこと）だけを決め、印の色や形を上書きしない。
			"""
		acceptance: [
			"作業中のエージェントが1人いる Issue の、構造の図の箱、ボードの札、横の欄の見出しに、orca-web の印（種類のアイコン、緑、回る弧、経過）が出る",
			"対応した worktree のない Scope の箱と札は、空の置き場があるだけで、置き場が見た目の場所を取らず（幅、高さ、flex の gap を取らない）、見た目が今と同じ",
			"構造の図の箱の大きさ（`SIZE`）が変わらず、印が箱の幅を越えない（越える分は部品の「+N」）",
			"SpecDock の CSS に `.orca-mark` の色の指定がない",
		]
	}
	"R-02": {
		title: "印は1つの読みから描き、描き直しでちらつかない"
		text: """
			すべての置き場は `ctx.orca` の同じ要約から描く（新しい読みの輪を作らない）。
			画面の描き直し（構造の更新、横の欄の描き直し）と要約の知らせ（`ctx.orca.subscribe`）のたびに、置き場ごとに描く印の形（部品の `buildMarks` の結果）を前と比べ、変わったときだけ `renderAgentMarks` で作り直す（作業中の弧が回り始めに戻らない）。
			描き直しで置き場の要素が作り直されたときは、同じ処理の中で印を描き直す（描き直しの間に印が消えて戻ることがない）。経過は部品が `elapsedFrom` から描く。SpecDock は描くときの今の時刻（`Date.now()`）を部品に渡すだけで、経過を進める時計（タイマー）を持たない（要約の読み直しと描き直しで進む）。
			"""
		acceptance: [
			"画面に箱が多くあっても、要約の読みは1つの間隔に1回である",
			"要約が同じ間、置き場を作り直さない描き直し（要約の知らせ、横の欄の描き直し、構造の図の署名が変わらない描き直し）では、置き場の印の要素が同じもののまま（作り直されない）",
			"置き場が作り直される描き直し（ボードのページの作り直し、構造の図の箱の作り直し）では、同じ処理の中で印が描かれる",
			"構造の描き直しで箱が作り直された後も、箱の印が残っている",
			"入力待ちのエージェントの印の経過が `elapsedFrom` からの経過で、title に読める文がある（部品のまま）",
		]
	}
	"R-03": {
		title: "印を押すと、その Scope の横の欄が開き、エージェントのタブがあればそれが開く"
		text: """
			構造の図とボードの印は、部品の `onSelect` を渡さず（押せる要素にしない）、押すと、今までどおりその箱や札が選ばれて横の欄が開く。
			印の置き場の上で押したときは、さらに横の欄にキー `agents` のタブを望む（そのタブが並びにあればそれを開き、なければ今の既定のタブ。iss-00593 を待たずに作れる）。
			修飾つきの押し（新しいタブで開くなど）は、今の札の振る舞いのまま。
			"""
		acceptance: [
			"箱の印を押すと、その箱が選ばれ、横の欄が開く",
			"ボードの札の印を押すと、その札が選ばれ、横の欄が開く（詳しい画面へは移らない）",
			"共有のタブの並びにキー `agents` があるとき、印を押すとそのタブが選ばれる。ないときは今の既定のタブ",
		]
	}
	"R-04": {
		title: "横の欄の見出しに、対応した worktree を Orca で開くボタンを置き、描き直しで読み込み直さない"
		text: """
			横の欄の見出しの状態の札の行の右端（閉じるの左）に、orca-web の `open-button.js` を（幅は部品に任せ、`data-width` を付けない）、対応した worktree（`forScope` の最初）の要約の `id` を `data-worktree` に、`data-theme` を SpecDock の今の明暗（`<html data-theme>`、なければ `prefers-color-scheme`）、`data-size="sm"` にして置く。
			置き場は横の欄の描き直しで作り直さない。ねらい（Scope の ID、worktree の id、明暗）が前と同じなら何もしない。違えば置き場を空にし、置けるときだけ新しいスクリプトを置く。
			置けるのは、`ctx.orca.status()` が ok で、対応した worktree があり、埋め込みの画面（`ctx.embed`）でないときだけ。幅 390px 以下の扱いは部品に任せ、SpecDock は隠さない。
			横の欄の要素が作り直されたとき（片付けの候補の一覧の後など）は、ねらいの覚えも捨てる（Epic のレビューの P2）。
			"""
		acceptance: [
			"エージェントのいる Issue を選ぶと、横の欄の見出しに「Orca で開く」が出る",
			"幅 390px の画面では、ボタンが出ない（iframe は隠れ、読み込まれない）",
			"対応した worktree のない Scope を選ぶと、ボタンが出ない",
			"同じ Scope を選んだまま 30 秒待つ間に、ボタンの iframe の読み込みが1回だけである",
			"明暗を変えると、ボタンが新しい明暗で置き直される",
			"埋め込みの画面（`?embed=1`）では、印は出るが、ボタンは出ない",
		]
	}
	"R-05": {
		title: "配る文書に、連携の設定と前提と、届かないときの見え方を書く"
		text: "配る文書（`src/spec_dock/assets/spec_dock/docs/` の、ダッシュボードの設定を説明する文書）に、`config.json` の `orca_web` の節（書き方、既定の値、壊れたとき）、orca-web の `ORCA_WEB_READ_ORIGINS` が SpecDock のオリジンを許すこと、同じ PC で動くこと、`localhost` や MagicDNS の名前で開くと読めないこと、届かないときの見え方を書く。実際の IP は書かない（例は 127.0.0.1 と RFC 5737 の文書用の IP）。"
		acceptance: [
			"配る文書に `orca_web` の節の書き方と既定の値（enabled true、port 8791）があり、`ORCA_WEB_READ_ORIGINS` への言及と、届かないときの見え方の説明がある",
			"配る文書と、変えた静的な資産の sha256 が `static-inventory.json` と一致する",
		]
	}
}

failures: {
	"F-01": {
		title: "orca-web に届かない（止まっている、CORS で拒まれる、部品の import に失敗する）ときは、印もボタンも出さず、図とボードは今までどおり動く"
		text:  "`ctx.orca.status()` が ok でない間、置き場は空で、ボタンの置き場も空。誤りの知らせを図やボードに出さない。読めるようになれば、次の知らせで印とボタンが出る。印を描く処理の例外（部品の契約の違いなど）は置き場ごとに捕まえ、その置き場を空にして、画面の描きを止めない。"
	}
	"F-02": {
		title: "orca-web が Orca に届いていない（connection.state が connected でない）ときは、印もボタンも出さない"
		text:  "`ctx.orca.status()` が orca-unreachable か orca-starting の間は、F-01 と同じに扱う。`stale` が true でも connected なら出す（`orcaStatus` のまま）。"
	}
	"F-03": {
		title: "埋め込みの画面では、印は出すが「Orca で開く」は置かない"
		text:  "orca-web の `frame-ancestors` が祖先の画面すべてを確かめるので、埋め込み先のオリジンが許されていないと壊れた枠になるため。"
	}
	"F-04": {
		title: "連携を切っている（`ctx.orca.status()` が off）ときは、置き場があっても何も描かず、今の画面と同じに見える"
	}
}

constraints: [
	"SpecDock のサーバーと API は変えない（iss-00591 のまま）。画面の JavaScript が orca-web に送るのは、iss-00591 の要約の読みと部品の import と CSS、この Issue の `open-button.js` の読み込みとその iframe だけ",
	"印、色、経過の表記、ボタンは orca-web の部品をそのまま使う。SpecDock の CSS は置き場の位置だけを決める",
	"構造の図の箱の大きさ（`SIZE`）と配置の計算を変えない",
	"公開のリポジトリ（コード、テスト、文書、仕様、report）に実際の Tailscale の IP、ユーザー名、ホームのパスを書かない。写しの中に写るものは、写しを report に貼る前に確かめる",
	"新しい依存（Python、JavaScript）を足さない",
]

decisions: [
	"2026-11-14、統括の決定（依頼書）：置き場は、箱と札は下の段の右寄せ、横の欄は状態の札の行に印と、右端に open-button.js。印を押すとその Scope の横の欄を開き、エージェントのタブがあればそれを開く。印のない Scope は場所も空けない（background の 1〜6）",
	"2026-11-14、タスク担当の判断：Epic・Initiative の枠の印は、Epic の design.cue D-06 のとおり見出し（`.gx-fh`）の右寄せに置く（統括の決定の「箱の下の段」は Issue の箱と木の表示の枠の箱に当てる）。枠の下の段（`.gx-fm`）は配下の進み具合の行で、その枠の自分の worktree の印と混ぜないため",
	"2026-11-14、タスク担当の判断：作り直しを避ける比べには、orca-web の部品が export する `buildMarks` の結果を使う（SpecDock で印の形を作らず、部品の決め方のまま比べるため）",
	"2026-11-14、タスク担当の判断：エージェントのタブを望む口は、横の欄に `preferTab(key)`（並びにあれば選ぶ。人が選んだタブとして覚える）を足す形にする。iss-00593 の `agents` のキーに依存するが、タブがなければ何も変えない",
	"2026-11-14、タスク担当の判断：横の欄の見出しは、描くたびに見出しの HTML が前と同じなら書き換えない（印の置き場が作り直されず、回る弧が回り始めに戻らないため）",
	"2026-11-14、依頼書の指示：配る文書（R-05）はタスク担当が書く",
	"2026-11-14、タスク担当の判断（Epic の design.cue D-06 の「SpecDock は時刻を渡さない」からの変更）：部品の `buildMarks` は `now` がないと経過を null にするので、比べの鍵と描きをそろえるため、描くときの `Date.now()` の1つの値を `buildMarks` と `renderAgentMarks` の両方に渡す。働きは部品の既定（`Date.now()`）と同じで、SpecDock は時計（タイマー）を持たない",
	"2026-11-14、統括の連絡（orca-web の iss-00035 で「Orca で開く」を小さなボタンに作り直す）：横の欄の見出しでは data-size=sm で右端に置き、幅は部品に任せ（data-width を付けない）、見出しの行はボタンの高さ 24px に合わせる",
]
