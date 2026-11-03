package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00427。plan.cue の slice `iss-00544`（covers: R-11、R-15、R-18）を、この Issue の番号に書き直した。
// Epic の番号は「Epic R-15」のように書く。この Issue の番号は R-01 などである。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
assurance: {
	level:  "standard"
	reason: "第3波の画面の統合の手直し。サーバーの API と画面の資源を変える"
}

purpose: "第3波（#529 骨組み、#531 ボード・詳しい画面・概況、#532 構造の図・時間の軸）の報告に残った手直しを、0.6.0 の前にまとめて行う。骨組みの格子、構造の API の保証レベルとブランチ、状態の印の置き場、「見た」の 409、線の重なりの5つ。"

background: """
	- #532 の報告：PC では `.mtabs` と知らせの帯が `display:none` になり、骨組みの格子（`grid-template-rows: 56px auto auto minmax(0,1fr)`）で `<main>` が高さ auto の2行目に入り、高さ0になる。#532 は自分の CSS に `.main[data-view="graph"|"timeline"] { grid-row: 4; }` を書いて避けた。
	- #532 は構造の API に `assurance` と `branch` を常に `null` で足し、値があるときだけ印を出す画面を作った。値の読み取りは統括の手当てとして残った。#531 の `application/dashboard_scope_details.py` は、詳しい画面の要求ごとに1つの Scope の保証レベル（`cue`、上限3秒）と `git worktree list`（上限3秒）を読む。
	- 構造の API は、画面が5秒ごとに `revision` を確かめ、変わったときだけ読み直す。横断の概況はリポジトリごとに構造の API を読む。
	- #531 の `views/_shared/parts.js`・`logic.js` と #532 の `views/graph/marks.js` は、どちらも状態の形を骨組みの `core/ui.js`（`STATES`、`stateIcon`）から取るが、アイコン（branch、merge など9つ）、種類の名前、保証レベルの段、PR の言葉、状態の言葉を別々に持つ。
	- スナップショットのないリポジトリでは、構造の API は 200 で `scopes: []` を返し、骨組みは「見た」の `POST` を送り、サーバーは 409（`DASHBOARD_NOTHING_TO_RECORD`）を返す。ブラウザーの記録に1件のエラーが出る。#529 の設計（Epic D-18）では、「見た」は記録を作るためのもので、データのないリポジトリでは記録するものがない。
	- #532 の手元の検査で、終わったものとすべての線を同時に出す既定でない組み合わせの4通り（housing-lifecycle の入れ子1、taikyohiyou_project の入れ子1・木2）に車線の重なりが残った（8回の引き直しで隙間が収まらない）。
	"""

includes: [
	"骨組みの格子の直しと、#532 の `grid-row: 4` の回避の撤去",
	"構造の API の `assurance` と `branch` を全 Scope 分読む仕組み（覚える仕組みと時間の上限つき）。詳しい画面の `scope` の同じ項目",
	"アイコン、状態の言葉、種類の名前、保証レベルの段、PR の言葉の置き場を `core/ui.js` に寄せる（見た目を変えない）",
	"スナップショットのないリポジトリで「見た」を送らない",
	"依存の線の引き直しの手直しと、線の検査のテストの代表のデータの追加",
	"PC のヘッドレスの Chrome での確かめ（5画面、PC の幅と 390px）",
]
excludes: [
	"常駐（`dashboard service`。#530）",
	"配布資産の文書、`static-inventory.json`、版の番号と `migration.md`（#534）",
	"木の表し方の経路の作り直し（下の decisions）",
	"iPhone の Safari での確かめ（#534 で利用者に頼む）",
]

requirements: {
	"R-01": {
		title: "どの画面でも、PC と 390px で `<main>` が上の帯の下の残りの高さを占める"
		text: """
			骨組みの格子で、上の帯、画面の切り替え（390px だけ）、知らせの帯、`<main>` の各行を固定する。画面の切り替えや知らせの帯が出ないときも、`<main>` は最後の行（残りの高さ）に入る。#532 の構造の図と時間の軸の CSS にある `grid-row: 4` の回避を外す。（Epic R-15、R-18 の画面の土台）
			"""
		acceptance: [
			"PC（1440×900）と 390px の幅で、構造の図、ボード、時間の軸、詳しい画面、横断の概況の5画面の `<main>` の高さが、窓の高さから上の帯（390px では画面の切り替えも）と知らせの帯を引いた値に等しい（ヘッドレスの Chrome で測る）",
			"`views/graph.css` と `views/timeline.css` に `grid-row` がない",
		]
	}
	"R-02": {
		title: "構造の API の各 Scope の `assurance` と `branch` に値が入る"
		text: """
			- `assurance`：その Scope の `requirement.cue` の `assurance.level`（`light`、`standard`、`strict`、`critical`）。CUE の Scope でない、読めない、カタログがないときは `null`。
			- `branch`：このPCの worktree のうち、ブランチ名がその Scope を指すもの（詳しい画面の `details.worktrees` と同じ判定）のブランチ名。複数あれば `git worktree list` の順の最初。なければ、または読めなければ `null`。
			- 詳しい画面（`scopes/<ID>`）の `scope` の同じ2つの項目も、`details` と同じ値にする。
			（Epic R-15、R-18）
			"""
		acceptance: [
			"CUE の Scope と Markdown の Scope と worktree のあるカタログで、構造の API の CUE の Scope に保証レベルが、worktree のある Scope にブランチ名が入り、ほかは `null`",
			"詳しい画面の `scope.assurance` と `scope.branch` が、`details.assurance.level` と `details.worktrees` の最初のブランチに一致する",
		]
	}
	"R-03": {
		title: "保証レベルとブランチの読み取りは、5秒ごとの更新と概況に耐える"
		text: """
			- `git worktree list` は、構造の API の要求ごとに1回だけ走らせる（Scope ごとには走らせない）。
			- 保証レベルは、`requirement.cue` の更新時刻と大きさで覚え、変わっていなければ `cue` を走らせない。覚える範囲はリポジトリ（カタログ）ごとで、その要求で見なかった Scope の分は捨てる。
			- 外の処理（`cue` と `git worktree list`）は、1つの要求の中で合わせて3秒を上限にする。
			"""
		acceptance: [
			"同じカタログで構造の API を2回読むと、2回目は `cue` を1度も走らせず、`git worktree list` は各要求で1回ずつ走る",
			"1つの `requirement.cue` を書き換えると、次の要求でその Scope だけを読み直す",
		]
	}
	"R-04": {
		title: "状態の印と小さな印の部品の置き場が、骨組みの `core/ui.js` の1つになる"
		text: """
			アイコンの形、状態の言葉（`STATES` の label）、種類の名前、保証レベルの段、PR の状態の言葉を `core/ui.js` に置き、`views/_shared/parts.js`・`logic.js` と `views/graph/marks.js` はそこから取る。同じ値を2か所に書かない。印の HTML（クラス名、構造、言葉）は変えない。（Epic R-11）
			"""
		acceptance: [
			"`parts.js`、`logic.js`、`marks.js` に、アイコンの SVG の形、状態の言葉の表、種類の名前の表、保証レベルの段の表、PR の状態の言葉の表の定義がない",
			"直す前と後で、`parts.js` と `marks.js` の印の関数が同じ入力に同じ HTML を返す（node のテスト）",
			"構造の図の箱の worktree の印は、`branch` があり状態が作業中の箱だけに出る（decisions）",
		]
	}
	"R-05": {
		title: "スナップショットのないリポジトリで、画面は「見た」を送らず、エラーを出さない"
		text: "構造の API がモデルを持たない（`snapshot.fetched_at` が `null`）とき、骨組みは「見た」の `POST` を送らない。送ったときに 409 などで断られても、画面は例外を出さずに続ける。サーバーの 409 の振る舞いは変えない。（Epic D-18）"
		acceptance: [
			"スナップショットのないリポジトリを開いても、ブラウザーの記録にエラーがなく、「見た」の `POST` が送られない（ヘッドレスの Chrome）",
			"スナップショットのあるリポジトリでは、開いたときに「見た」が1回送られる（今までどおり）",
		]
	}
	"R-06": {
		title: "依存の線の引き直しが収まらないときも、重なりの最も少ない回を描く"
		text: """
			配置と経路の引き直しの回数の上限を8回から10回にし、上限まで収まらないときは、最後の回でなく、線の検査（`audit`）の問題の数が最も少ない回（同じなら早い回）を返す。直したことを示す見本を、線の検査のテストの代表のデータに足す。直せない組み合わせは、理由を report.md に書く。（Epic R-15）
			"""
		acceptance: [
			"線の検査のテストで、spec-dock の構造、250件の見本（種 532）に加え、8回で最後の回を返すと車線が重なる250件の見本2つ（種 15、18）の、すべての表し方で問題が0件",
			"250件の見本（種 532）の配置と経路が1秒以内（今までどおり）",
		]
	}
}

failures: {
	"F-01": {
		title: "保証レベルやブランチを読めないときも、構造の API は応え、その項目だけ `null` にする"
		text: "`cue` がない・失敗する・遅い、`requirement.cue` が壊れている、`git worktree list` が失敗する、カタログがない・決まらない（クローンが2つ）ときも、構造の API は 200 で応え、読めなかった Scope の `assurance` か、すべての `branch` だけを `null` にする。"
	}
	"F-02": {
		title: "3秒の上限に達したら、残りの保証レベルは読まずに `null` で返し、次の要求で読み直す"
		text: "上限に達した後の Scope の保証レベルは `null` で返し、覚えない。次の要求では、覚えた分を使い、残りから読む。"
	}
}

constraints: [
	"編集してよい範囲：`src/spec_dock/assets/dashboard/**`、`src/spec_dock/runtime/application/dashboard_*.py`、`runtime/presentation/dashboard_api.py`、`tests/`、この Scope のディレクトリ",
	"構造の API の形（`specdock.dashboard/v1` の `structure`、`scopes/<ID>`）は画面のためで、公開の契約ではない（#529 の決定）。項目の意味は変えず、値を入れるだけ",
	"手元の私的なリポジトリの構造はテストに入れない（#532 と同じ）",
]

decisions: [
	"`branch` は Scope の状態に関わらず、このPCの worktree の事実として返す。構造の図の箱の worktree の印は、Epic R-15 の「作業中なら」に従い、状態が作業中の箱だけに出す",
	"線の重なりのうち、木の表し方で線が多いもの（taikyohiyou_project の線284本）は直さない。木では全 Scope が字下げの1列に並び、長い縦の線が狭い字下げの通り道を取り合う。広げられる隙間は字下げ1つだけで、広げても深さの違う箱どうしの間は少ししか広がらない。直すには、木の線の通り道を別に設けるなど経路の作り方を変える必要があり、この Issue の範囲を超える",
	"寄せが残す数 px の凸を消す処理も試したが、別の組み合わせで重なりが増えたので採らなかった",
]
