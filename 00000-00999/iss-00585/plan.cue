package spec

goal: "マージできる 0.9.1 のリリースの PR（CI 合格、最終品質ゲートの closure.md あり）。"

steps: {
	"S-01": {title: "migration.md に 0.9.1 の節を足す（提供側と dogfood、タスク担当）", realizes: ["R-02"], status: "done", session: "owner"}
	"S-02": {title: "版を 0.9.1 にし、0.9.0 の版固定のテストを外す", realizes: ["R-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "static-inventory.json の2行、0.9.0 の fixture、統合テストを足す", realizes: ["R-03", "R-01", "R-02"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "wheel を隔離した venv で確かめ、配布の手順を report.md に書く（タスク担当）", realizes: ["R-01", "R-04"], status: "done", after: ["S-03"], session: "owner2"}
}

tests: {
	"T-01": {title: "版が 0.9.1 の4つの場所でそろう（統合テスト）、隔離した venv の wheel の `spec-dock --version` が 0.9.1", verifies: ["R-01"]}
	"T-02": {title: "migration.md の 0.9.1 の節が 0.9.0 の直後にあり、主な語があり、dogfood の写しと一致する（統合テスト）", verifies: ["R-02"]}
	"T-03": {title: "inventory が 0.9.0 のバイトを知り、0.9.0 の consumer が installation update で2つのファイルだけ変わって上がる（統合テスト）", verifies: ["R-03"]}
	"T-04": {title: "`git diff --stat` に範囲外のファイルがなく、タグがない。report.md に配布の手順がある", verifies: ["R-04"]}
}

verification: """
	S-03 の後：`uv run pytest tests/integration/test_issue585_release_0_9_1.py tests/integration/test_issue580_release_0_9_0.py tests/integration/test_issue536_release_0_8_0.py`。
	最後に `make lint`、`uv run pytest`（全体）。wheel：`uv build --wheel --out-dir <新しい /private/tmp の道>`、`uv venv <新しい道>`、`uv pip install --python <venv>/bin/python <wheel>`、`<venv>/bin/spec-dock --version`。道具の環境（uv tool）には入れない。
	"""

rollback: "PR を戻す（版、文書、inventory、テストだけの変更）。配布の後なら、パッケージを 0.9.0 の wheel に戻す。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に配布の手順がある。マージ、タグ、配布は統括が行う。"

gates: {
	checkpoints: {}
	checkpoints_note: "なし。手本のある機械的な変更で、最終品質ゲートで足りる"
	final_quality_gate: {
		scope:          "開始のコミット 3055648c8 から S-03 の終わりまで（S-04 は記録だけ）"
		perspectives:   ["requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "本人が統括にマージを委任した（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		owner:  {task: "仕様化と migration.md の節（S-01）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）。文書は依頼書でタスク担当が書く"}
		impl:   {task: "実装（S-02、S-03）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。テストで確かめられる機械的な変更。本人の指示（2026-11-13）で Sol を使う"}
		owner2: {task: "wheel の確かめと配布の手順の記録（S-04）", model: "opus", effort: "medium", rationale: "タスク担当。記録と確かめだけで実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
