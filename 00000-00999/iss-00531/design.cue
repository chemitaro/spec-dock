package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"判定はサーバー（#528 のモデル）に1つだけ置き、画面はその JSON を写すだけにする",
	"骨組み（#529）と #532 の画面に触れず、差し込み口の3つの画面と `views/_shared/` だけで作る",
	"詳しい画面の読み取り（カタログ、cue、git）は時間の上限つきで、失敗してもその欄だけを「読めない」にする",
]

current: "#529 の骨組みの差し込み口（`views/board.js`、`scope.js`、`overview.js`）は空の札を出すだけで、検索の枠 `#search-slot` は空。構造の JSON は Scope ごとの状態、`lane`、`merge`、`downstream`、`waits`、`pr`、`change` を持つが、推奨順の順位を持たない。Scope の JSON は `upstream`、`downstream`、`root_waits`、`child_stages` を持つが、引き継いだ依存、Scope でない Issue への依存、文書、Artifact、保証レベル、worktree を持たない。"

target: "ボード、詳しい画面、横断の概況、検索が動き、PC と幅 390px、明るい表示と暗い表示で崩れない。サーバーの JSON は、画面に要る項目（`rank`、`dependencies`、`details`）を持つ。"

design: {
	"D-01": {
		title: "構造の JSON に推奨順の順位 `rank` を足す"
		text: """
			`presentation/dashboard_api.py` の `structure_document` で、モデルの `ordered`（`recommended_key` の順）で全 Scope の順位（0 から）を求め、`scope_item` の `rank` に入れる。ボード、横断の概況、検索の候補、詳しい画面の段の中は、この `rank` で並べる。`scope_document` の `scope` にも同じ `rank` を入れる。

			また、構造の JSON の各 Scope に `in_progress`（スナップショットの作業中の印）を足す。ボードの札は使わないが、概要のタブで「このPCの worktree がない作業中」を見分けるのに使う。
			"""
		satisfies: ["R-01", "R-02", "R-12"]
	}
	"D-02": {
		title: "Scope の JSON に依存の内訳 `dependencies` を足す"
		text: """
			`scope_document` に `dependencies: {waits_for, waited_by}` を足す。

			- `waits_for`：その Scope と祖先のスナップショットの `blocked_by` を、自分の分を先に、祖先は近い順に集める。各項目は `{number, scope_id, title, state, declared_by, inherited, external, open}`。`scope_id` は Scope なら ID、Scope でない Issue なら null（`external: true`、`state` は `open` か `done`、題名はスナップショットの `external` から）。`state` は Scope ならモデルの状態。同じ番号は最初の1回だけ。
			- `waited_by`：スナップショットの `blocked_by` にこの Scope の番号を持つ Scope の ID（直接に待つもの）。間接のものは既存の `downstream`（直接と間接）を使う。

			判定は足さず、スナップショットの依存の記録を写すだけにする。止められている理由と大もとの待ち先は、既存の `scope.reason` と `root_waits` を使う。
			"""
		satisfies: ["R-07", "R-08"]
	}
	"D-03": {
		title: "詳しい画面の読み取り `application/dashboard_scope_details.py`"
		text: """
			新しいモジュールに `read_scope_details(site, scope_id, *, timeout=3.0, assurance_reader=read_assurance, worktree_lister=worktree_list) -> dict` を置く。何も書かない。

			- カタログ：`site.catalog` が None（2つのクローン）なら `catalog: "ambiguous"`、そのディレクトリがなければ `missing`、Scope のディレクトリ（`scope_relative(ID)`）がなければ `scope_missing`、あれば `ok`。`ok` でないときは次の1手（`spec-dock canonical link`、`spec-dock canonical status`、2つのクローンなら `spec-dock dashboard list`）を `next_steps` に入れる。
			- 文書：`requirement`、`design`、`plan`（`.cue` か、なければ昔の `.md`）、`explanation.html`、`report.md` のそれぞれについて、通常のファイルとしてあるか（リンクは辿らない）と名前。説明資料は `href`（`/r/<repo>/files/<ID>/explanation.html`）を持つ。
			- Artifact：`artifacts/` の直下の通常のファイル（リンクと、名前が `.` で始まるものを除く）を名前の順に、`{name, size, modified_at, html, href}`。`href` は `/r/<repo>/files/<ID>/artifacts/<名前を URL の形に逃がしたもの>`。300件で打ち切り、`truncated` を立てる。
			- 保証レベル：`requirement.cue` があるときだけ、`scope_check.read_assurance`（時間の上限つき）で読み、`{level, source: "cue"|"unreadable"|"unset", problem}`。
			- worktree：カタログで `git worktree list --porcelain -z`（時間の上限つき）を読み、ブランチが Scope を名指す（`branch_names_scope`）ものの `{path, branch}` を返す（`worktrees: {status: "ok"|"unreadable", items}`）。カタログがなければ `unreadable`。
			- どの部分も、例外（`OSError`、時間切れ、git と cue の失敗）を、その部分の `unreadable` にして続ける。
			"""
		satisfies: ["R-07", "R-08", "R-09"]
	}
	"D-04": {
		title: "`dashboard_http.py` の1か所と、`scope_document` の `details`"
		text: "`_repository_api` の `scopes/<ID>` の分岐で、`scope_document(view, ID, baseline=…, details=read_scope_details(site, ID))` と渡す。`scope_document` は引数 `details`（既定 None）を受け、`details` の項目にそのまま入れる。構造に ID がないときは、読み取りを走らせずに 404 を返す（今のまま）。"
		satisfies: ["R-07", "R-08", "R-09"]
	}
	"D-05": {
		title: "共有の部品 `views/_shared/parts.js` と `parts.css`"
		text: """
			ボード、詳しい画面、横断の概況が共通に使う、文字列を返す小さな関数を置く。どれも利用者の文字を `esc` で逃がす。

			- 足りないアイコン（`branch`、`merge`、`prClosed`、`chevronRight`、`chevronLeft`、`x`、`box`、`down`、`arrowRight`、`arrowDown`、`file`、`book`、`target`、`calendar`）と、それを描く `icon(name)`（`core/ui.js` の `ic` と同じ描き方）。
			- `prMark(pr, {words})`：PR の状態（下書き、開いている、マージ済み、閉じた）、CI（成功、失敗、実行中、なし）、マージできるか（できる、衝突、分からない）をアイコンと言葉で。`mergeBadge(scope)`：マージ待ちの段。
			- `assuranceMark(level)`、`downMark(n)`（後に続く N）、`changeBadge(change)`（新しい／状態が変わった（前の状態）／PR が変わった）、`kindLabel(kind)`、`progressBar(counts)`、`stateCounts(scopes)`。
			- `card(scope, ctx, {parent})`：ボードと詳しい画面の札。`<a data-nav href=ctx.href(scope.path)>` で、押すと詳しい画面へ移る（普通のリンクなので、新しいタブでも開ける）。
			- `newTabLink(ctx)`：埋め込みのときだけ、`embed=1` を外した今の道を `target=_blank` で開くリンク（R-14）。
			- `legend()`：状態の形と言葉、PR の印、変化の印、後に続く印の凡例（`<details>`）。
			- `fmtDay(iso)`、`fmtDateTime(iso)`。

			CSS（`parts.css`）は、`:is([data-view="board"],[data-view="scope"],[data-view="overview"])` の下に書き、#532 の画面へ漏らさない。各画面の `styles` に `parts.css` と自分の CSS を並べる。
			"""
		satisfies: ["R-04", "R-05", "R-14", "R-15"]
	}
	"D-06": {
		title: "状態のボード `views/board.js`"
		text: """
			`render(root, ctx)` は `ctx.data.scopes` から作る。

			- 表示の切り替えは問い合わせの文字列：`kind`（`initiative`、`epic`、`issue`。なしはすべて）、`group=1`（親ごと）、`done=1`（終わったものを含める）。押すと `ctx.navigate` で URL を置き換え、骨組みが `render` を呼び直す。
			- 列：`blocked`、`ready`、`doing`、`awaiting_merge`、（`done`）。各 Scope の `lane` で振り分け、`rank` の昇順に並べる。`unknown` は列に入れず、上の注意の帯に一覧にする。`awaiting_merge` の列は `merge` で `mergeable`（先）と `needs_fix` の段に分ける。終わった列は新しい順の30件までにし、残りの数を書く。
			- 親ごとのまとめでは、列の中を親で分け、見出しに親の状態の印と ID と題名を出す（閉じた親も見出しには出る。開いた配下を見失わない。Epic R-12）。親の並びは、その親の中で一番 `rank` の小さい札の順。
			- 上の数の帯：止められている、着手できる、作業中、マージ待ち（直す・できるの内訳）、不明（あれば）の数（Issue だけを数える）と、終わった割合（全 Scope の終わった数／全体）。右に「片付けの候補 N」のボタン。押すと `<dialog>` で一覧（Scope、理由、GitHub へのリンク、詳しい画面へのリンク）を開く。
			- PR の状態：`pull_requests.status` が `unknown` なら、上に「PR の状態が分からない」の帯を出し、マージ待ちの列の中に理由を書く。`stale` なら帯に「前回の値」と書く。
			- 凡例と、列の並びの説明（推奨順）を置く。埋め込みのときは `newTabLink`。
			- 構造がない（`ctx.data` が null か `snapshot.status` が `missing`／`unsupported` で Scope が0件）ときは、空の案内だけを出す（通知の帯は骨組みが出す）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-14", "R-15"]
	}
	"D-07": {
		title: "Scope の詳しい画面 `views/scope.js`"
		text: """
			`ctx.scope`（`scopes/<ID>` の JSON）と `ctx.data`（構造）から作る。

			- `ctx.scope` が null で、構造にその ID がなければ「構造にない」とボードへのリンク（F-02）。構造にはあるのに Scope の JSON が読めないときは「読めない」。
			- 見出し：種類、ID、番号、題名、状態の札（`chip`）、理由、マージ待ちの段、変化の印、右の欄に親の道筋（構造の `parent_id` を辿る。各段は詳しい画面へのリンク）、保証レベル（`details.assurance`）、GitHub の Issue、PR（印とリンク）、このPCのブランチ。
			- タブ（問い合わせ `tab`＝`summary`、`deps`、`children`、`docs`、`artifacts`。既定 `summary`）。押すと `ctx.navigate` で URL を置き換える。配下のない Issue でも配下のタブは出し、「配下はない」と書く。
			- 概要：状態の説明の帯、配下の進み具合（子孫でなく直下の配下の状態ごとの数）、記録（作成と完了の日、このPCの worktree とブランチ、PR、変化）。worktree が読めないときは「分からない」、ないときは「このPCにはない（ほかのPCは分からない）」。
			- 依存：待っているもの（`dependencies.waits_for` を、自分の分と引き継いだ分（宣言した祖先の ID つき）に分け、Scope でない Issue は GitHub のリンク）と、大もとの待ち先の印（`root_waits`）、待たれているもの（`waited_by` を直接、`downstream.indirect` の数を間接）。
			- 配下：`child_stages.stages` を段1 → 段2 → … に並べ、各段の中は `rank` の順。終わったものを隠す（問い合わせ `done=1` で含める）ときは、終わった配下を数だけにする（`keep_visible` は残す）。`external`（外への依存）と `cyclic`（循環）を別に示す。
			- 文書と Artifact：`details.catalog` が `ok` でなければ、そのことと次の1手。文書は5つの札（あるかないか、説明資料は新しいタブで開くリンク）。Artifact は表（名前、形式、大きさ、日時、新しいタブで開くリンク。HTML はサーバーが切り離して配る）。
			"""
		satisfies: ["R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "R-11", "R-14", "R-15"]
	}
	"D-08": {
		title: "横断の概況 `views/overview.js`"
		text: """
			`render` は、`ctx.repositories` の各リポジトリの構造（`core/api.js` の `structure`、baseline なし）を並べて読み、札を描く。読み込みの間は札の枠だけを出し、読めたものから描く。60秒ごとに読み直し、`dispose` で止める。「見た」は送らない（骨組みも概況では送らない）。

			- 札：名前、取得の時刻（「N分前」）、マージ待ち・作業中・着手できる Issue の題名を `rank` の順に3件ずつ（残りの数）、状態ごとの数とマージ待ちの数、終わった数／全体、止められている数、片付けの候補の数、変化の数。札全体がそのリポジトリのホームへのリンク（`ctx.href(item.path)`。別のリポジトリなので骨組みはページを読み直す）。
			- 警告の帯：構造の JSON の `snapshot.status`（`missing`、`unreadable`、`unsupported`）と `notices` の `SNAPSHOT_STALE`、`STRUCTURE_ANOMALIES`、`PULL_REQUESTS_UNKNOWN`、`REPOSITORY_AMBIGUOUS` から、理由と経過（「3時間前から更新されていない」）と次の1手を札の上に出す。API が失敗したら（404、500、通信の失敗）、その札にだけ「読めない」の帯を出す。
			- 埋め込みのときは `newTabLink`。
			"""
		satisfies: ["R-04", "R-05", "R-12", "R-13", "R-14", "R-15"]
	}
	"D-09": {
		title: "検索 `views/_shared/search.js` と、骨組みの1行"
		text: """
			`mountSearch(slot, {route, data, navigate, href})` を骨組みの `render()` の `renderTop` の直後に1回呼ぶ（`app.js` に import と1行）。

			- 部品（入力欄と候補の一覧、スマートフォンの虫めがねのボタン）はモジュールの中で1回だけ作り、呼ばれるたびに新しい `#search-slot` へ移す。入力中に骨組みが上の帯を描き直しても、入力の値、カーソル、開いた候補を保つ（移す前にフォーカスを覚え、移した後に戻す）。
			- リポジトリがない（概況）か、構造がないときは何も出さない。
			- 一致：ID（大文字小文字を区別しない。`iss-531` のような0埋めなしも、数字を5桁にそろえて比べる）、番号（`531`、`#531`）、題名の部分一致。完全に一致する ID と番号を先に、ほかは `rank` の順で8件まで。終わったものも出す（状態の印で分かる）。
			- 上下の矢印で選び、Enter か押すと `navigate(scope.path)` で詳しい画面へ移り、欄を空にする。Escape で閉じる。`role="combobox"` と `listbox` を持つ。
			- 幅 640px 以下では、虫めがねのボタンだけを出し、押すと上の帯の下に欄を開く。
			"""
		satisfies: ["R-10", "R-11", "R-15"]
	}
}

compatibility: """
	- 構造と Scope の JSON は画面のためのもので、公開の契約にしていない（#529 D-06）。足すだけで、消す項目と意味を変える項目はない。
	- 画面の道（`/r/…/scopes/<ID>`、`?embed=1`）の形は変えない。問い合わせの文字列に `tab`、`kind`、`group`、`done` を足す（開き直しの印で、契約にはしない）。
	- 配布資産（`static-inventory.json`）は変えない（画面は wheel にだけ入る）。
	"""

risks: [
	"詳しい画面を開くたびに `cue` と `git worktree list` が走る。上限3秒と、読み取りの失敗を欄だけに閉じることで、画面が止まらないようにする",
	"#532 と同じ見た目の部品（PR の印など）を別に持つので、見た目がずれることがある。統括が後で1つにまとめる",
	"JavaScript の単体のテストは、`node` がない環境では飛ばす（CI の Linux には `node` がある）。画面の振る舞いはヘッドレスの Chrome の確かめで補う",
]
