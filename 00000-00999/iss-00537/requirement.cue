package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "定期の同期の GitHub への問い合わせと、構造のスナップショットの形（版2）を変える。誤ると同期や構造の取得を止めるおそれがあるが、版を戻せば回復できる。"
}

purpose: "定期の同期が、各リポジトリの PR の状態を GitHub の GraphQL で取り、構造のスナップショット（C10）の版2に持つ。ダッシュボード（#528 のモデル、#531・#532 の画面）は、GitHub に問い合わせずに、PR の印（状態、CI、マージできるか）を描ける。"

background: """
	- 親は epic-00427（#427）。plan.cue の slice `iss-00537` が、Epic の D-19 を任せる。covers は R-07、R-30。
	- 構造のスナップショットは、`<state_root>/github/<host>/<owner>/<name>/snapshot.json`（版1）。書くのは `SnapshotStore`（ロックと rename）。読むのは、`dependency check`、`scope show`、`canonical status`、今のダッシュボード（`canonical_dashboard`）など。
	- 定期の同期は60秒ごとに1回、リポジトリごとに `ensure_fresh(repository, "cycle")` を呼ぶ。構造を取り直すのは、種類のラベルの ETag が変わったときか、30分を超えて古いときだけ。PR の CI や、マージできるかが変わっても、Issue の ETag は変わらない。そのため、PR は構造の取り直しとは別の間隔で取る。
	- 版2の形は、統括が #528 と合わせて決めた（2026-11-04、msg_099086f2b281 と msg_5e86801e635b）。
	"""

includes: [
	"PR の GraphQL の問い合わせと、その応答の解釈（`runtime/infra/github_structure.py`）",
	"構造のスナップショットの版2（`runtime/domain/canonical_structure.py` の `StructureSnapshot`）、その読み書き（`runtime/infra/github_snapshot.py` の `SnapshotStore`、`StructureSnapshotService`）",
	"PR を Scope に対応づける読む側の関数（`branch_names_scope` を使う）",
	"版1と版2の互換と、既存の読む側が変わらないことのテスト",
]

excludes: [
	"ダッシュボードの状態のモデル（`dashboard_model.py`、#528）、HTTP と画面（#529、#531、#532）",
	"版の番号、`migration.md`、`static-inventory.json`（0.6.0 のリリース #534）",
	"コマンド（`display`、`decision` の段階）からの PR の取得。PR は定期の同期だけが取る",
]

requirements: {
	"R-01": {
		title: "定期の同期が、PR の状態を1回の GraphQL の問い合わせで取り、スナップショットに書く"
		text: """
			定期の同期の各リポジトリの処理（`ensure_fresh` の `cycle` の段階）で、構造の処理の後に、PR を取る。1回の GraphQL の問い合わせで、開いている PR を最大100件、閉じたかマージされた PR を最大50件、どちらも更新の新しい順に取る（ページは足さない）。取るのは `number`、`state`、`isDraft`、`headRefName`、`mergeable`、最後のコミットの `statusCheckRollup.state`、`createdAt`、`mergedAt`、`closedAt`、`url`。結果は、スナップショットの `pull_requests` に、前回の値と置き換えて書く。
			"""
		acceptance: [
			"見本の GitHub の応答（gh の stub）から、同期の1回で、スナップショットの `pull_requests` に、決めた形（R-02）の PR が入る",
			"同期の1回の PR の問い合わせは GraphQL の1回で、開いている PR の `first: 100` と、閉じた PR の `first: 50` を含む",
		]
	}
	"R-02": {
		title: "版2の形：`pull_requests`、`pull_requests_fetched_at`、`pull_requests_error`"
		text: """
			スナップショットの `version` を2にし、版1の鍵に3つの鍵を足す。

			- `pull_requests`：`{"<番号>": {number, state, is_draft, head_ref_name, mergeable, checks, created_at, merged_at, closed_at, url}}`。`state` は `open`、`closed`、`merged`。`mergeable` は `mergeable`、`conflicting`、`unknown`。`checks` は `success`、`failure`、`pending`、`none`（`SUCCESS`→`success`、`FAILURE` と `ERROR`→`failure`、`PENDING` と `EXPECTED`→`pending`、rollup がない→`none`）。時刻は UTC の `Z` の形で、`merged_at` と `closed_at` はないとき `null`。
			- `pull_requests_fetched_at`：最後に PR を取れた時刻。一度も取れていなければ `null`。
			- `pull_requests_error`：最後の PR の取得が失敗したとき `{code, message, at}`、成功したら `null`。

			読む側の約束（#528 と共通）：`pull_requests_fetched_at` が `null` か、30分を超えて古いか、`pull_requests_error` が `null` でないときは、PR の状態を「分からない」とする。
			"""
		acceptance: [
			"書いたスナップショットの JSON が `version: 2` で、3つの鍵が上の形と値を持つ。CI の5つの写し方と、rollup がないときの `none` が単体のテストで確かめられる",
			"構造を取り直しただけで、まだ PR を取っていないスナップショットは、`pull_requests: {}`、`pull_requests_fetched_at: null`、`pull_requests_error: null` になる",
		]
	}
	"R-03": {
		title: "PR の取得は、前回の取得から2分を超えたときだけ行い、コマンドからは行わない"
		text: "同期の周期（60秒）ごとに PR を取ると費用が大きいので、前回の成功（`pull_requests_fetched_at`）から2分を超えたときだけ取る（Epic の D-19）。ただし、前回の試みがレート制限（`pull_requests_error.code` が `GITHUB_RATE_LIMITED`）で失敗したときは、その時刻（`pull_requests_error.at`）からも2分を超えるまで試みない（制限の中で問い合わせを重ねると、GitHub が制限を延ばすため）。ほかの失敗の後は、次の周期で試みる。コマンドが使う `display` と `decision` の段階（`dependency check`、`scope show` など）と `refresh`（`--source github`）は、PR を取らない（Epic の制約：GitHub への要求は定期の同期にだけ任せる）。"
		acceptance: [
			"前回の成功から2分以内の同期の周期では PR の問い合わせが出ず、2分を超えた周期では出る。レート制限の失敗の後は2分、ほかの失敗の後は次の周期で出る",
			"`display` と `decision` の段階と `refresh` では、PR の問い合わせが出ない",
		]
	}
	"R-04": {
		title: "PR の取得だけが失敗しても、構造の取得は続き、前回の PR の値を残して理由を書く"
		text: "PR の問い合わせが失敗したとき（届かない、断られた、応答の形が違う、レート制限）、構造の取得の結果はそのまま書き、`pull_requests` と `pull_requests_fetched_at` は前回の値のまま残し、`pull_requests_error` に理由のコードと説明と時刻を書く。レート制限のときは待たずに失敗にする（構造の処理と、同期のほかのリポジトリを遅らせない）。次に成功したら `pull_requests_error` を `null` に戻す。"
		acceptance: [
			"PR の問い合わせが失敗する見本で、構造の取得の結果（`fetched_at`、`issues`）は新しくなり、`pull_requests` と `pull_requests_fetched_at` は前回の値のまま、`pull_requests_error` にコードと時刻が入る。同期の1回の結果は失敗にならない",
			"GraphQL のレート制限の見本で、待ち（`sleep`）をせずに `pull_requests_error.code` が `GITHUB_RATE_LIMITED` になる",
			"失敗の後に成功すると、`pull_requests_error` が `null` に戻る",
		]
	}
	"R-05": {
		title: "読む側が、PR を Scope に対応づける"
		text: "Scope との対応はスナップショットに持たない。読む側の関数 `pull_requests_by_scope(snapshot)` が、`head_ref_name` を `branch_names_scope` で、スナップショットにある Scope に対応づける（`iss-00537`、`chemitaro/iss-00537`、`iss-00537-xxx` など）。同じ Scope に複数の PR があれば、開いているものを先に、次に `created_at` の新しいものを選ぶ。"
		acceptance: [
			"見本で、`<ID>`、`<名前>/<ID>`、`<ID>-<語>` のブランチの PR が、その Scope に対応づき、Scope を名指さないブランチと、スナップショットにない ID のブランチは対応づかない",
			"同じ Scope に、閉じた新しい PR と開いた古い PR があるとき、開いた PR が選ばれる。両方開いていれば、新しいほうが選ばれる",
		]
	}
	"R-06": {
		title: "版1から版2へ移り、既存の読む側は変わらない"
		text: """
			- 新しい版は、版1のファイルも読む（PR の欄は空、`pull_requests_fetched_at` は `null`）。書くときは版2で書く。更新の直後に構造をすべて取り直さずに済み、GitHub に届かないときもコマンドが動く。
			- 版2を知らない古い SpecDock は、版2を「ない」とし、取り直して版1で書き戻す。そのファイルも、新しい版は読める。
			- 知らない版（3以上、0、文字列）と、版と鍵の組が合わない文書は、今までどおり「ない」とする。
			- `dependency check`、`scope show`、`canonical status`、今のダッシュボード（`input_hash`）は、版2でも同じ結果を返す。PR の変化だけでは、今のダッシュボードのファイルを書き直さない。
			"""
		acceptance: [
			"版1のファイルを `SnapshotStore.load()` が読み、構造が同じで PR が「まだ取っていない」の値になる。それを書き戻すと版2になる",
			"版2のファイルを、版1だけを読む古い読み手（今の版1の検査を写した関数）が「ない」とする。古い版が書き戻した版1のファイルを、新しい版が読める",
			"版1と版2の同じ構造のスナップショットで、`dependency check` の JSON の結果と今のダッシュボードの `input_hash` が一致する",
		]
	}
}

failures: {
	"F-01": {
		title: "PR の問い合わせが届かない、断られる、応答の形が違う"
		text:  "構造の結果は書き、PR は前回の値を残し、`pull_requests_error` に理由を書く（R-04）。同期の結果のコードは変えない。"
	}
	"F-02": {
		title: "GitHub のレート制限"
		text:  "待たずに `GITHUB_RATE_LIMITED` を `pull_requests_error` に書く。次の試みは、その失敗から2分を超えてから（R-03）。構造の処理が同じ周期でレート制限に当たったときは、PR を試みない。"
	}
	"F-03": {
		title: "構造のスナップショットがない、または構造の処理が失敗した"
		text:  "PR を書く先がないか、GitHub に届かないので、その周期では PR を試みない。"
	}
	"F-04": {
		title: "同時の書き手（別のプロセスの同期、コマンドの書き込みの反映、構造の取り直し）"
		text:  "PR の欄は、ロックの中で読み直したスナップショットに書く。より新しい PR の結果（成功か失敗）を、それより古い試みの結果で上書きしない。比べる時刻は、成功は `pull_requests_fetched_at`、失敗は `pull_requests_error.at` で、どちらも応答を受けた時刻とする。構造の取り直しと書き込みの反映は、PR の3つの鍵を引き継ぐ。"
	}
	"F-05": {
		title: "開いている PR が100件を超える、閉じた PR が50件を超える"
		text:  "更新の新しい順に上限まで持ち、それより古いものは持たない（取りこぼした PR の Scope は、PR がないものとして描かれる）。ページを足さず、費用を一定に保つ。"
	}
}

constraints: [
	"GitHub への要求は、定期の同期にだけ任せる。ダッシュボードとその CLI、ほかのコマンドは、PR を問い合わせない（Epic の制約）",
	"テストは一時のディレクトリと gh の stub で閉じる。本物の GitHub に要求しない",
	"版の番号、`migration.md`、`static-inventory.json` は変えない（#534）。PR の本文に、0.6.0 の移行の注記に要る契約の変更を書く",
	"ダッシュボードのモデル（`dashboard_model.py`）は作らない（#528）",
]

decisions: [
	"2026-11-04（統括、#528 と共通）：版2の `pull_requests` の形、値の写し方、`pull_requests_error` の形、Scope との対応を読む側で求めること（msg_099086f2b281）",
	"2026-11-04（統括）：`pull_requests_fetched_at` を足す。`null` は一度も取れていない。PR の取得は前回から2分を超えたときだけ。レート制限は待たない。新しい版は版1も読み、版2で書く（msg_5e86801e635b）",
	"2026-11-04（担当の判断）：2分は前回の成功から数える（統括の決定）。レート制限の失敗の後だけは、その時刻からも2分待つ（制限の中の問い合わせの繰り返しを避ける）",
	"2026-11-04（担当の判断）：閉じた PR にも、開いた PR と同じ欄（CI、マージできるか）を取る。問い合わせを1つの形に保ち、費用の差は小さい（およそ3点と2.5点）",
]
