package spec

// 設計（Issue）。型 specdock/v1。
// コードの場所は 2026-11-04 の main（24f291f9c）で確かめた。

goals: [
	"画面（#529 以降）と要約の CLI が、同じ1つのモデルから作られ、食い違わない",
	"状態の判定を `evaluate_all` に任せ、ダッシュボードの側では足すもの（子孫の作業中、ボードの列、推奨順）だけを書く",
	"モデルを純粋な関数にし、ファイルの読みと CLI を薄い層に分ける（#529 のサーバーが同じ部品を呼べる）",
]

current: """
	- 着手の判定は `runtime/domain/canonical_readiness.py`（`evaluate_readiness`、`evaluate_all`、`ScopeReadiness`、`CanonicalBlocker` の `role` は self／ancestor／prerequisite／external）。
	- 構造のスナップショットは `runtime/domain/canonical_structure.py` の `StructureSnapshot`（版1。`from_json` は鍵が完全に一致する版1だけを受ける）。`SnapshotStore.load()` は、読めない・知らない版を「ない」と返し、見分けない。
	- 状態の置き場は `runtime/infra/state_root.resolve_state_root()`。チェックアウトのリポジトリは `github_structure.repository_for_checkout`（`origin` から。ネットワークなし）。
	- コマンドの一覧は `runtime/cli/catalog.py`（`LEAF_PATHS`、`LEAF_ARGUMENTS`、`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_READS_BY_ROOT` など）と `commands/canonical_dispatch.py`（`CANONICAL_HANDLERS`、`REPOSITORY_INDEPENDENT_HANDLERS`）。公開のコマンドは53。
	"""

target: """
	- `runtime/domain/dashboard_snapshot.py`：スナップショットの文書の版の見分けと、PR の欄の解析。
	- `runtime/domain/dashboard_model.py`：モデル（状態、列、推奨順、片付けの候補、段、道筋、変化、時間の軸、古さ）。
	- `runtime/infra/dashboard_files.py`：スナップショット、隠す印、在りかの記録の読み（書かない）。
	- `runtime/presentation/dashboard_summary.py`：要約の JSON。
	- `runtime/application/dashboard_summary.py`：`dashboard summary` の処理。公開のコマンドは54。
	"""

design: {
	"D-01": {
		title: "状態と理由：`evaluate_all` の写し"
		text: """
			`build_model(snapshot, pull_requests, *, now)` が `DashboardModel` を返す。各 Scope の `ScopeModel` は、`id`、`number`、`kind`、`title`、`parent_id`、`children`（ID、番号の順）、`state`、`reason`（`ScopeReason(code, text, numbers)`）、`readiness`（写した `ScopeReadiness`）、`pr`、`lane`、`merge`、`downstream`、`waits`、`keep_visible`、`created_at`、`closed_at`、`url` を持つ。

			- 状態：`evaluate_all(snapshot)` の DONE／UNKNOWN／DOING／BLOCKED／READY を `done`／`unknown`／`doing`／`blocked`／`ready` に写す。Epic と Initiative は、BLOCKED か READY のときに、開いた子孫に `in_progress` があれば `doing` にする。
			- 理由のコード：`closed`（終わった）、異常のコード（不明。`readiness.unknown` の最初のもの）、`in_progress`、`descendant_in_progress`、`pr_mergeable`、`pr_needs_fix`、`parent_closed`（role が ancestor）、`waiting`（自分の依存の先）、`inherited_waiting`（祖先が宣言した依存の先）、`waiting_external`（Scope でない Issue）、`no_waits`。止められているときは、閉じた祖先 → 自分の依存 → 引き継いだ依存の順に、最初に当たるものを主な理由にし、`numbers` に待ち先の番号を入れる。`text` は画面に出す日本語の短い文。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "ボードの列と、マージ待ちの分け方"
		text: "`lane` は、状態が `doing` で種類が Issue で、PR の確かさが `unknown` でなく、選んだ PR の `state` が `open` で `is_draft` が偽のときに `awaiting_merge`、ほかは状態と同じ名前。`awaiting_merge` のとき、`merge` は `checks == failure` か `mergeable == conflicting` なら `needs_fix`、ほかは `mergeable`。理由のコードも `pr_needs_fix`／`pr_mergeable` にする。状態そのものは `doing` のまま。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "推奨順：後に続く数と待ち先の数"
		text: """
			- 待つ関係：Scope y が x を待つのは、y か y の祖先の `blocked_by` に x があるとき。
			- 後に続く数（`downstream`）：開いた x について、x と x の開いた祖先から始め、それを `blocking` する Scope と、その子孫（開いたもの）を「後に続く」に入れ、入れたものと、その開いた祖先から、同じように広げる。最後に x と x の祖先を除いた数。閉じた Scope は0。試作の `down` と同じ。
			- 待ち先の数（`waits`）：`readiness.blockers` のうち role が prerequisite か external のものの、番号の重なりを除いた数。
			- 並べ方 `recommended_key(scope)`：分類（マージできる0、直す必要あり1、作業中2、着手できる3、止められている4、不明5、終わった6）、次に分類ごとの鍵（0〜3：後に続く数の多い順、番号の小さい順。4：待ち先の少ない順、後に続く数の多い順、番号の小さい順。5：番号の小さい順。6：閉じた時刻の新しい順、番号の小さい順）。`model.ordered(ids)` がこの順に並べ、ボードの列と要約の一覧はこれを使う。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "片付けの候補と、残す印"
		text: "`model.cleanup` は `CleanupCandidate(scope_id, code, text)` の推奨順の列。`all_descendants_closed`：開いた Epic と Initiative で、子孫が1つ以上あり、すべて閉じている。`closed_with_open_descendants`：閉じた Scope で、開いた子孫がある（この Scope の `keep_visible` を真にする）。`open_under_closed_parent`：理由が `parent_closed` の止められている Scope（Epic R-10）。子孫は、スナップショットの親子のうち Scope の番号だけをたどる。"
		satisfies: ["R-04"]
	}
	"D-05": {
		title: "配下の段と依存の道筋"
		text: """
			- `child_stages(model, parent_id, *, open_only)`：`parent_id` が None なら親のない Scope を、ほかはその直下の子を並べる。子 a が子 b を待つのは、a の部分木のどれかの `blocked_by` が b の部分木の番号を指すとき（a ≠ b）。部分木の外を指すものは `external`（子の ID と番号）に入れる。最長の道で段を決め、循環に入る子は段に入れず `cyclic` に入れる。`open_only` では閉じた子と、閉じた先への依存を除く。各段の中は推奨順。返り値は `ChildStages(stages, external, cyclic)`。
			- `downstream_ids(model, id, *, open_only=True)`：D-03 の後に続く数と同じ広げ方（x と x の祖先を待つもの、その子孫、それらの祖先を待つもの）で求めた集合を返す。`open_only` のときの大きさは `downstream` と一致する。直接は、x 自身の番号を `blocked_by` に持つ Scope、ほかは間接。
			- `upstream(model, id, *, open_only=False)`：直接は自分の `blocked_by` の先（Scope だけ）。間接は、祖先から引き継いだ依存の先と、たどり着いたものの子孫とその依存の先（自分と祖先の分）を、再帰に集めたもの。
			- `root_waits(model, id)`：止められている Scope の上流の端（開いた依存の先を自分と祖先に持たず、開いた子孫も持たない開いた Scope）のうち、止められていないものと、上流がたどる開いている Scope でない Issue の番号。
			"""
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "「見た」の記録の1件と、比べ方"
		text: """
			- `seen_scopes(model) -> {ID: SeenScope(state, pr)}`：`pr` は PR の段階 `none`、`draft`、`open`、`needs_fix`、`merged`、`closed` のどれか、PR の状態が分からないときは null。`open` と `needs_fix` は、開いた下書きでない PR を `merge` と同じ決まりで分けたもの。#529 は、これを D-18 の形（`{ID: {state, pr}}`）で書く。
			- `compare_seen(model, baseline) -> {ID: ScopeChange(kinds, state_before, pr_before)}`：`baseline` が None なら空。基の記録にない Scope は `new`。状態が違えば `state`。PR の段階が両方とも null でなく、違えば `pr`。`ScopeChange.kinds` はこの3つの部分集合。
			- ファイルの読み書きと `seen_id` の管理は #529。
			"""
		satisfies: ["R-06"]
	}
	"D-07": {
		title: "時間の軸"
		text: "`weekly_totals(model, *, kinds, now)`：最初の `created_at` の週の月曜（UTC）から `now` の週まで、各週の終わりまでに作られた数と閉じた数の累計 `WeekTotal(week_start, created, closed)`。`recent_events(model, *, limit)`：Scope の `created`／`closed`、PR の `pr_opened`（`created_at`）／`pr_merged`（`merged_at`）を `TimelineEvent(at, kind, scope_id, number)` にし、時刻の新しい順、同じなら番号の順。PR の出来事は対応づいた Scope があり、PR の状態が分からないとき以外に入れる。"
		satisfies: ["R-07"]
	}
	"D-08": {
		title: "スナップショットの文書の読み（版1と版2、PR の欄）"
		text: """
			`runtime/domain/dashboard_snapshot.py`（#537 のマージの後、#537 の部品に寄せた）：

			- `parse_snapshot_document(payload, *, repository) -> ParsedSnapshot(snapshot, pull_requests)`。`version` が整数でなければ `SnapshotUnreadable`、整数で `READABLE_SNAPSHOT_VERSIONS`（1と2）になければ `SnapshotUnsupported`。解析は `StructureSnapshot.from_json`（#537 が版1と版2を読み、PR の欄 `pull_requests`、`pull_requests_fetched_at`、`pull_requests_error` を持つ）に任せ、`SnapshotFormatError` と別のリポジトリのものは `SnapshotUnreadable`。
			- PR の形は `canonical_structure.PullRequest`、`PullRequestsError`。`PullRequestInfo.of(snapshot)` は `fetched_at`、`error`、`items` と、Scope ごとの PR `by_scope`（`canonical_structure.pull_requests_by_scope`。`branch_names_scope` で対応づけ、open を先、次に `created_at` の新しい順、次に番号の大きい順）を持つ。
			- `status(now)` は、`pull_requests_fetched_at` が null（版1を含む）か、`now - fetched_at` が30分を超えていれば `unknown`、それ以外で `pull_requests_error` があれば `stale`、ほかは `fresh`（Epic D-19）。
			- `build_model(snapshot, *, now)` は、PR をスナップショットから取る。
			"""
		satisfies: ["R-08"]
	}
	"D-09": {
		title: "取得の時刻、古さ、異常"
		text: "`DashboardModel` は `repository`、`fetched_at`、`stale`（`now - fetched_at > 30分`。`github_snapshot.MAX_AGE[\"display\"]` を使う）、`anomalies`（スナップショットのまま）、`pull_requests`（`PullRequestInfo`）を持つ。"
		satisfies: ["R-09"]
	}
	"D-10": {
		title: "要約の JSON（`specdock.dashboard-summary/v1`）"
		text: """
			`presentation/dashboard_summary.py` の `summary_document(model, *, hidden, server) -> dict`。#529 のサーバーも呼ぶ。

			```json
			{"schema": "specdock.dashboard-summary/v1",
			 "repository": "github.com/<owner>/<name>",
			 "fetched_at": "…Z", "stale": false,
			 "counts": {"total": 0, "by_state": {"done":0,"doing":0,"blocked":0,"ready":0,"unknown":0},
			            "by_kind": {"initiative": {"total":0,"done":0,…}, "epic": {…}, "issue": {…}}},
			 "completion_ratio": 0.5,
			 "awaiting_merge": [{"id","number","kind","title","state","reason","merge"}],
			 "in_progress": […], "ready": […], "blocked": […],
			 "cleanup": [{"id","number","kind","title","state","reason"}],
			 "anomaly_count": 0,
			 "pull_requests": {"status": "fresh|stale|unknown", "fetched_at": null, "error": null},
			 "paths": {"<ID>": "/r/github.com/<owner>/<name>/scopes/<ID>"},
			 "hidden": false, "server": null}
			```

			- `completion_ratio` は終わった数／全体の数（全体が0なら null）。`by_state` はボードの列でなく状態の5つで数える。
			- `in_progress` は列が `doing` のもの（マージ待ちを除く）、`awaiting_merge` には `merge` を足す。一覧はすべての種類を含み、推奨順。`reason` は、`cleanup` では片付けの候補の理由（`CleanupCandidate.text`）で、要素に `cleanup`（候補のコード）を足す。ほかの一覧では Scope の理由（`ScopeReason.text`）。
			- 項目を足すのは版を変えずにでき、消すか意味を変えるときは版を上げる。配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-10"]
	}
	"D-11": {
		title: "コマンド `dashboard summary` と、読むファイル"
		text: """
			- 一覧：`LEAF_PATHS` に `dashboard summary` を足し（53 → 54）、引数は `repository`（省略可）。`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_READS_BY_ROOT`、`_DOES_NOT_BY_ROOT`、`_JSON_DATA_BY_ROOT` に `dashboard` を足す。読むだけのコマンド（`MUTATING_LEAF_PATHS` に入れない）。
			- 経路：REPOSITORY を指定したときは `REPOSITORY_INDEPENDENT_HANDLERS` で、チェックアウトなしに処理する。省いたときは `CANONICAL_HANDLERS` で、`repository_for_checkout(context.root)` から決める（ネットワークなし）。REPOSITORY が `owner/name`、`github.com/owner/name` でなければ `DASHBOARD_REPOSITORY_INVALID`（終了コード2）。
			- `runtime/infra/dashboard_files.py`：`read_snapshot_file(state_root, repository)`（`<state_root>/github/<host>/<owner>/<name>/snapshot.json` を自分で読み、`missing`／`unreadable`／`unsupported`／読めた文書を返す）。`read_hidden(state_root, key)`（`<state_root>/dashboard/repositories.json` の `specdock.dashboard-repositories/v1`、`repositories` の鍵 `host/owner/name` があれば真。ない・壊れているは偽）。`read_server_url(state_root)`（`<state_root>/dashboard/server.json` の `specdock.dashboard-server/v1` の `pid` に `os.kill(pid, 0)` で生きているかだけを見て、生きていれば `urls.local`、ほかは null。要求は送らない）。どれも書かない。
			- 失敗：F-01 `DASHBOARD_SNAPSHOT_MISSING`、F-03 `DASHBOARD_SNAPSHOT_UNSUPPORTED`、F-04 `DASHBOARD_SNAPSHOT_UNREADABLE`（どれも終了コード3、`recovery` に次の1手）。
			- 出力：`--json` は封筒の `data.result` に要約（`FamilyData("dashboard", summary)`。`data.kind` は `dashboard`）。文字の出力は、取得の時刻、古さ、状態ごとの数、各一覧の先頭の数件。
			- 文書：`reference_cli.md`（提供側と dogfood の写し）にコマンドの行と要約の契約を足し、README と `cli-redesign-guide.html` の数を54にする。`static-inventory.json` は、変えた配布文書の行の sha256 を更新し、前の sha256 を known_old_sha256 に足す（統括の決定。版の番号と `migration.md` は変えない）。
			"""
		satisfies: ["R-11"]
	}
	"D-12": {
		title: "読めないときの扱い"
		text: "`read_snapshot_file` が `missing`、`unsupported`、`unreadable` を見分けて返し、CLI はそれぞれの失敗のコードで止まる。異常のある Scope は D-01 で不明になり、段の計算は循環を `cyclic` に分ける。在りかの記録と隠す印は、読めなくても要約を止めない。"
		satisfies: ["R-08", "R-09", "R-11"]
	}
}

compatibility: """
	- 0.6.0 の移行の注記に要るもの：公開のコマンドが1つ増える（`dashboard summary`。Epic 全体では8つ）。新しい公開の契約 `specdock.dashboard-summary/v1`（`reference_cli.md` に書く）。ほかのコマンドの契約は変えない。
	- スナップショットの書き手と既存の読み手は変えない。版2の文書を読むのは、ダッシュボードの読み手だけ。
	- 戻すときは PR を revert する。状態の置き場には何も書かないので、残るものはない。
	"""

risks: [
		"コマンドの数（53 → 54）を縛るテストと文書が、#530 と #533 でも変わる。後にマージするほうが main を取り込む",
	"後に続く数の計算は、Scope の数 n に対して最悪 n² 程度。250件で十分に速いことをテストで確かめる",
]
