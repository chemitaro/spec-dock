package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"ダッシュボードが GitHub に問い合わせずに PR の印を描けるように、PR の状態を構造のスナップショットに持つ",
	"PR の取得の失敗とレート制限が、構造の取得と同期のほかの処理に及ばないようにする",
	"版1と版2の間で、どちらの版の SpecDock も止まらず、既存の読む側の結果を変えない",
]

current: "スナップショットは版1で、Issue の構造だけを持つ。PR の状態はどこにもない。"
target:  "スナップショットは版2で、定期の同期が2分に1回まで、PR の状態を足して書く。読む側は `pull_requests_by_scope` で Scope ごとの PR を得る。"

design: {
	"D-01": {
		title: "領域のモデル：`PullRequest`、`PullRequestsError` と、`StructureSnapshot` の3つの欄"
		text: """
			`runtime/domain/canonical_structure.py` に置く。

			- `SNAPSHOT_VERSION = 2`。読める版は1と2（`READABLE_SNAPSHOT_VERSIONS`）。
			- `PullRequest`（凍結の dataclass）：`number`、`state`（`open`|`closed`|`merged`）、`is_draft`、`head_ref_name`、`mergeable`（`mergeable`|`conflicting`|`unknown`）、`checks`（`success`|`failure`|`pending`|`none`）、`created_at`、`merged_at`、`closed_at`、`url`。
			- `PullRequestsError`：`code`、`message`、`at`。
			- `StructureSnapshot` に、`pull_requests: Mapping[int, PullRequest]`（既定は空）、`pull_requests_fetched_at: str | None`（既定 `None`）、`pull_requests_error: PullRequestsError | None`（既定 `None`）を足す。既定値があるので、今の作り手（`build_snapshot`、テストの見本）は変えずに済む。
			- `to_json` は版2で、3つの鍵を書く。`pull_requests` の鍵は番号の文字列で、番号の順。
			- `from_json`：版1は今の鍵の組だけを受け、3つの欄を既定値にする。版2は今の鍵の組に3つを足した組だけを受ける。PR の各値は許す値の組で調べ、形が違えば `SnapshotFormatError`（読む側は「ない」）。
			- 引き継ぎ：`_apply`（書き込みの反映）と `merge_refresh`（構造の取り直し）は、もとのスナップショットの3つの欄を、結果に `replace` で引き継ぐ。`merge_refresh` は、取り直したもの（PR を持たない）でなく、今のスナップショットの PR を引き継ぐ。
			- 純粋な関数：`with_pull_requests(snapshot, items, fetched_at)`（置き換え、`pull_requests_error` を `None` に）、`with_pull_requests_error(snapshot, error)`（PR と `fetched_at` を残す）。
			"""
		satisfies: ["R-01", "R-02", "R-04", "R-06"]
	}
	"D-02": {
		title: "Scope との対応：`pull_requests_by_scope`"
		text: """
			`runtime/domain/canonical_structure.py` の純粋な関数 `pull_requests_by_scope(snapshot) -> Mapping[str, PullRequest]`。

			- 各 PR の `head_ref_name` の最後の区切り（`/` の後）から、`(init|epic|iss)-<番号>` で始まり、その後が終わりか `-` のものを候補の ID にし、`snapshot.find(ID)` がある Scope で、`branch_names_scope(head_ref_name, ID)` が真のときだけ対応づける（規則は `branch_names_scope` が正本）。
			- 同じ Scope に複数あれば、`state == "open"` を先に、次に `created_at` の新しいもの、同じなら番号の大きいものを選ぶ。
			- #528 は当面、自分の領域で2つの鍵を解析する（統括の決定 (4)）。後にマージするほうが、この関数に寄せて重複を消す。
			"""
		satisfies: ["R-05"]
	}
	"D-03": {
		title: "GraphQL の問い合わせ：`GithubStructureClient.fetch_pull_requests`"
		text: """
			`runtime/infra/github_structure.py` に `PULL_REQUESTS_QUERY` を置く。

			```graphql
			query($owner: String!, $name: String!) {
			  rateLimit { cost remaining resetAt }
			  repository(owner: $owner, name: $name) {
			    open: pullRequests(first: 100, states: [OPEN], orderBy: {field: UPDATED_AT, direction: DESC}) { nodes { ...pr } }
			    closed: pullRequests(first: 50, states: [CLOSED, MERGED], orderBy: {field: UPDATED_AT, direction: DESC}) { nodes { ...pr } }
			  }
			}
			fragment pr on PullRequest {
			  number state isDraft headRefName mergeable createdAt mergedAt closedAt url
			  commits(last: 1) { nodes { commit { statusCheckRollup { state } } } }
			}
			```

			- 応答の値を D-01 の値に写す（R-02）。知らない値や形の違いは `GITHUB_RESPONSE_INVALID`。同じ番号が2回あれば `GITHUB_RESPONSE_INVALID`。
			- レート制限を待たない：`GithubApi.request` と `GithubStructureClient.graphql` に `wait_rate_limit: bool = True` を足し、PR の問い合わせだけ `False` で呼ぶ。`False` のときは、HTTP のレート制限と GraphQL の `RATE_LIMITED` を、待たずに `GITHUB_RATE_LIMITED` にする。5xx の再試行（読むための既存の扱い）は変えない。ほかの呼び手の既定は変わらない。
			"""
		satisfies: ["R-01", "R-02", "R-04"]
	}
	"D-04": {
		title: "保存と同期：`SnapshotStore` と `StructureSnapshotService`"
		text: """
			`runtime/infra/github_snapshot.py`。

			- `PULL_REQUEST_INTERVAL = timedelta(minutes=2)`。
			- 試みの時刻：成功は `pull_requests_fetched_at`、失敗は `pull_requests_error.at`。どちらも応答を受けた時刻（`clock.now()`）。スナップショットの最後の試みの時刻は、この2つの新しいほう。
			- `SnapshotStore.commit_pull_requests(items, fetched_at)`：ロックの中で読み直し、スナップショットがなければ何もしない。今の最後の試みの時刻が `fetched_at` より新しければ残す（F-04）。ほかは `with_pull_requests` で書く。
			- `SnapshotStore.record_pull_requests_error(error)`：ロックの中で読み直し、スナップショットがなければ何もしない。今の最後の試みの時刻が `error.at` より新しければ残す。ほかは `with_pull_requests_error` で書く。
			- `StructureSnapshotService.ensure_fresh("cycle")`：構造の処理の後、構造の処理が失敗せず（`probe != "failed"`）、スナップショットがあるとき、`refresh_pull_requests()` を呼ぶ。返す `FreshSnapshot` の `snapshot` は PR を書いた後のもの。足した欄 `pull_requests`（`fetched`|`failed`|`skipped`）を持つ。`display`、`decision`、`refresh()` は呼ばない（R-03）。
			- `refresh_pull_requests()`：`pull_requests_fetched_at` から `PULL_REQUEST_INTERVAL` 以内なら `skipped`。`pull_requests_error.code` が `GITHUB_RATE_LIMITED` で、`pull_requests_error.at` から `PULL_REQUEST_INTERVAL` 以内でも `skipped`。ほかは問い合わせ、成功なら `commit_pull_requests`、`GithubStructureError` なら `record_pull_requests_error`（`code`、`message`、`at`）で `failed`。例外は外へ出さない（R-04）。
			- 同期の側（`canonical_sync.refresh_structures`）は、`ensure_fresh(..., "cycle")` を今までどおり呼ぶだけで、変えない。
			"""
		satisfies: ["R-01", "R-03", "R-04"]
	}
	"D-05": {
		title: "版の移りと互換"
		text: """
			| 場面 | 振る舞い |
			|---|---|
			| 新しい版が版1のファイルを読む | 構造を読み、PR は「まだ取っていない」（`{}`、`null`、`null`）。次に書くときに版2になる。構造の取り直しは起きない |
			| 新しい版の同期の最初の周期（版1のファイル） | 構造の処理は今までどおり（ETag が同じなら取り直さない）。PR を取り、版2で書く |
			| 古い版（版1だけを読む）が版2のファイルを読む | `from_json` が知らない版として「ない」を返し、`ensure_fresh` が取り直して版1で書く（版1の鍵の組を厳しく調べるので、版2の鍵を誤って読まない） |
			| 古い版が書き戻した版1を、新しい版が読む | 読める。PR は「まだ取っていない」になり、次の同期の周期で取り直す（前回の試みの時刻もないので、間隔を待たない） |
			| 版3以上、0、文字列、鍵の組と版が合わない | 今までどおり「ない」 |

			- 既存の読む側（`dependency check`、`scope show`、`canonical status`、今のダッシュボード）は、`StructureSnapshot` の今の欄だけを使う。PR の欄は足すだけなので結果は変わらない。今のダッシュボードの `input_hash` は `issues`、`external`、`anomalies` だけを数えるので、PR の変化でファイルを書き直さない。
			- 費用：PR の問い合わせはおよそ3点（開いた PR 100件と、その最後のコミット 100件、閉じた PR 50件と、その最後のコミット 50件。合わせて300件÷100）。成功の後は2分に1回なので、1リポジトリでおよそ90点/時（失敗が続くと、レート制限のほかは60秒の周期ごとに1回試みる）、5リポジトリでおよそ450点/時（1時間の上限5000点の1割に満たない）。1回の同期の時間は、2分に1回、`gh` の呼び出し1回（およそ1秒）だけ増える。
			"""
		satisfies: ["R-03", "R-06"]
	}
}

compatibility: """
	0.6.0 の移行の注記に要る契約の変更：構造のスナップショット（`<state_root>/github/<host>/<owner>/<name>/snapshot.json`、SpecDock だけが読むユーザーごとのファイル）が版2になり、`pull_requests`、`pull_requests_fetched_at`、`pull_requests_error` を持つ。新しい版は版1を読める。前の版に戻すと、前の版は版2を「ない」として一度取り直す（構造の GraphQL の1回分）。定期の同期の GitHub への要求は、PR の GraphQL の問い合わせ（およそ3点）が、リポジトリごとに、成功の後は2分に1回、レート制限の後は2分に1回、ほかの失敗が続くときは同期の周期（60秒）ごとに1回増える。公開のコマンドの出力は変えない。
	"""

risks: [
	"GitHub が `mergeable` を計算し終えていないと `UNKNOWN` を返す。読む側は、それを「マージできる」に入れる（Epic の D-04）",
	"利用者のほかの `gh` の使い方と、同じ1時間に5000点を分ける。PR の問い合わせは成功の後とレート制限の後は2分に1回に抑え、レート制限では待たずに諦める。ほかの失敗が続くと60秒ごとに試みる（失敗の問い合わせの多くは点を使わない）",
	"PR の取得の成功のたびに `snapshot.json` を書き直す（2分に1回）。ファイルの時刻を見る読む側（#529 の自動の更新）は、そのたびに読み直す",
	"`head_ref_name` が別のフォークの同じ名前のブランチでも対応づく。SpecDock のブランチの規則（Scope の ID）に従う名前なので、受け入れる",
]
