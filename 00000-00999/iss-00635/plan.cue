package spec

// 計画（Issue）。型 specdock/v1。

goal: "一覧の API と『横断の構造』の見出しから段の札をなくし、チェックアウトのパスの包含による入れ子だけで、どの置き方のリポジトリでも同じに見せる"

steps: {
	"S-01": {title: "D-05 のサーバーと文書のテスト（T-01・T-02・T-04・T-05）を先に直して落ちることを確かめ、D-01・D-02・D-04 を実装して通す（dashboard_nesting.py・dashboard_site.py・dashboard_http.py、reference_cli.md の配る側と dogfood、static-inventory.json）", realizes: ["R-01", "R-03"], status: "todo", session: "impl-sol"}
	"S-02": {title: "D-05 の画面のテスト（T-03）を先に直して落ちることを確かめ、D-03 を実装して通す（allgraph.js・allgraph.css・compose.js と index.js のコメント）。make lint と全体の uv run pytest を通す", realizes: ["R-02", "F-01"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "D-06 の調べの表と、実機の確かめ（T-06）を report.md に残し、本人が見る試しの URL を tailnet で立てる", realizes: ["R-02", "R-04"], status: "todo", after: ["S-02"], session: "owner"}
}

tests: {
	"T-01": {title: "純粋な関数（test_dashboard_nesting.py）：この PC の登録の形の9つの親が今と同じ、名前の頭が同じだけのもの・同じ道・隠したもの・クローンが2つのもの・絶対でない道の親が今と同じ、`businesses/b/products/p` と `groups/b/team/p` で親の形が同じ。`TIER_LABELS` と `Nesting` を import できない", verifies: ["R-01"]}
	"T-02": {title: "一覧の API（test_dashboard_repositories_nesting.py）：各リポジトリの項目が `[*FIELDS, \"parent\"]` の順で `tier` がなく、親の値が今と同じ。隠したもの・ambiguous・分からない行の扱いと、道を返さないことが今と同じ", verifies: ["R-01"]}
	"T-03": {title: "画面（偽の DOM、test_dashboard_allgraph_screen.py）：`tier` を持つ入力でも、どの枠の見出しにも `sd-badge`・`ax-tier` がなく、`owner/name` とリンクがある。`allgraph.css`・`allgraph.js` に `ax-tier` がない。compose の入れ子のテストが通る", verifies: ["R-02", "F-01"]}
	"T-04": {title: "文書（test_issue613_repository_nesting_docs.py）：配る側と dogfood の reference_cli.md が同じバイトで、API の行に `parent` の決め方があり、`tier`・`段の札`・`businesses` がない。目録の sha256 が内容と合い、前の値が known_old_sha256 にある", verifies: ["R-03"]}
	"T-05": {title: "静的な確かめ：`src/spec_dock/runtime/` の .py に `TIER_LABELS`・`事業`・`プロダクト`・`サービス`・`businesses`・`products` の文字列がない", verifies: ["R-01"]}
	"T-06": {title: "実機：作業ツリーの wheel を隔離した venv に入れ、この PC の状態の置き場の写し（一時の置き場）で別のポート・`--tailscale` で立て、`/api/v1/repositories` に `tier` がなく `parent` が今と同じこと、`/graph` の 1440・390 × 明・暗の写しで見出しに札がなく入れ子が今どおりであることを report.md と artifacts に残す。調べの表（D-06）も report.md に書く", verifies: ["R-01", "R-02", "R-04"]}
}

verification: """
	節目：実装担当が各手順の後に `uv run pytest tests/unit/application/test_dashboard_nesting.py tests/unit/application/test_dashboard_repositories_nesting.py tests/unit/infra/test_issue613_repository_nesting_docs.py tests/unit/presentation/test_dashboard_allgraph_screen.py tests/unit/presentation/test_dashboard_allgraph_compose.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は T-06。
	"""

rollback: "PR を戻す（サーバーのコード、画面の静的な資産、配る側の文書と目録、dogfood の写し、テスト）。一覧の API に `tier` が戻り、見出しに札が戻る。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に調べの表、実機の写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 のテストの合格と HEAD を確かめてから impl-claude を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミットから S-02 の終わりまで（S-03 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00635/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が依頼書で指定（Opus 5.5 / medium）"}
		"impl-sol":    {task: "実装（S-01、サーバー・文書・目録とそのテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。テストで確かめられる部分（依頼書の指定で Sol）。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02、画面と偽の DOM のテスト、全体の検証）", model: "opus", effort: "medium", rationale: "claude。画面（依頼書の指定：画面は Claude Opus 5.5 / medium）"}
		owner:         {task: "調べの表、実機の確かめと試しの URL（S-03）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		// 仕様のレビュー（spec-reviewer opus / high）は S-01 の前に行う。after は手順の後しか指せないので、ここには書かず report.md に記録する
		gate: {role: "最終品質ゲート", after: "S-02", model: "opus", effort: "medium"}
	}
}
