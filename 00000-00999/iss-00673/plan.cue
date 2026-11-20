package spec

// 計画（Issue）。型 specdock/v1。

goal: "マージできる PR（CI 合格、最終品質ゲートの closure.md あり）。Antigravity の中の linked worktree で `canonical status` が1行を示し、配る案内に Antigravity がある。"

steps: {
	"S-01": {title: "canonical.md・reference_cli.md の Antigravity の案内（提供側と dogfood）と static-inventory.json の2行（タスク担当）", realizes: ["R-02"], status: "done", session: "owner"}
	"S-02": {title: "検出（D-01）、domain の関数（D-02）、`tools.antigravity` と警告（D-03）と、そのテスト・案内の検査のテスト", realizes: ["R-01", "R-02", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "deny・ask の `*`・絶対でない規則を判定できないとし（統括の決定）、T-07・T-08 のテストを足す", realizes: ["R-01", "F-01"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "deny・ask の空の対象（`read_file()`）と括弧のない形（`write_file`）も判定できないとし（統括の決定）、T-09 のテストを足す", realizes: ["R-01"], status: "todo", after: ["S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "`ANTIGRAVITY_AGENT` ありの linked worktree で、設定のファイルがないと `configured` 偽、1行、`CANONICAL_TOOL_SETTING_MISSING`（tool antigravity）、`tools.next_step` がその1行（cli_runtime）", verifies: ["R-01"]}
	"T-02": {title: "`permissions.allow` にカタログか親の `read_file`・`write_file` の両方で `configured` 真・警告なし。片方だけ、`~`・相対・`*` の規則だけ、`allowNonWorkspaceAccess` 真だけで偽。`deny`・`ask` にカタログを覆う `read_file`・`write_file` があると null と、deny と ask を名指す next_step の `CANONICAL_TOOL_SETTING_UNKNOWN`（cli_runtime と domain の単体）", verifies: ["R-01"]}
	"T-03": {title: "JSON でない、形が違う（`permissions`・`allow`・`ask`・`deny` の型）、権限で読めない、UTF-8 でない設定と、ホームが分からないときは `configured` null と `CANONICAL_TOOL_SETTING_UNKNOWN`（Antigravity の中、cli_runtime と domain の単体）", verifies: ["R-01"]}
	"T-04": {title: "`ANTIGRAVITY_AGENT` なしでは、設定がなくても Antigravity の警告が出ず、`tools` の `status`・`next_step` と警告の列が今と同じ。main のチェックアウトでは `needed` 偽で警告なし（cli_runtime）", verifies: ["F-01", "R-01"]}
	"T-05": {title: "設定のファイルのバイトが実行の前後で同じ。今の `test_issue429_canonical_status.py` などの Codex・Claude Code のテストがそのまま通る", verifies: ["R-01"]}
	"T-06": {title: "提供側の canonical.md に Antigravity の項（`~/.gemini/antigravity-cli/settings.json`、`read_file(`、`write_file(`、`1.5.12`）があり、reference_cli.md の C45 に Antigravity があり、両方が dogfood の写しとバイトが同じ。今の資産の検査のテストが通る", verifies: ["R-02"]}
	"T-07": {title: "`deny` の `read_file(*)`、`ask` の `write_file(/some/*)` があると、`allow` に両方があっても null と `CANONICAL_TOOL_SETTING_UNKNOWN`（next_step が、空・括弧なし・`*`・絶対でないパスの deny・ask の規則を名指す）。`deny` に `*` を含まない、カタログを覆わない別のフォルダーの規則は影響しない（真のまま）。`allow` の `read_file(*)` と `write_file(*)` だけでは偽（cli_runtime と domain の単体）", verifies: ["R-01"]}
	"T-08": {title: "`ANTIGRAVITY_AGENT` なしで判定が null（壊れた設定）のとき、Antigravity の警告が出ず、`tools` の `status`・`next_step` は Codex・Claude Code の警告だけで決まる（cli_runtime）", verifies: ["F-01"]}
	"T-09": {title: "`deny` の `read_file()`、`ask` の `write_file`（括弧なし）、`deny` の `read_file(relative/path)` があると、`allow` に両方があっても null と `CANONICAL_TOOL_SETTING_UNKNOWN`。`allow` の `read_file()`・`write_file` だけでは偽（cli_runtime と domain の単体）", verifies: ["R-01"]}
}

verification: """
	S-02 の後：`uv run pytest tests/cli_runtime/test_issue429_canonical_status.py tests/unit/infra/test_runtime_environment.py` と、新しいテストのファイル、資産の検査のテスト（`uv run pytest tests/unit/infra -k inventory` など、実装担当が名前を確かめる）。
	最後に `make lint`、`uv run pytest`（全体）。
	"""

rollback: "PR を戻す。Antigravity の項目と案内がなくなるだけで、Codex・Claude Code の動きは変わらない。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に実物での確かめがある。マージ、`work finish`、版の公開は統括が行う。"

gates: {
	checkpoints: {}
	checkpoints_note: "なし。実装の手順は1つで、最終品質ゲートで足りる"
	final_quality_gate: {
		scope:          "この Issue の変更：開始のコミット 83b8ee95f から S-04 の終わりまで。origin/main を取り込んだ後は、取り込んだ main（6de140261）を開始のコミットとする（iss-00673-fqg-1 は S-02 で合格、fqg-2 は S-03 で全車線が通ったが取り込みの前、fqg-3 は S-04 の決定で止めた。S-04 の後に新しいキャンペーン iss-00673-fqg-4 でやり直す）"
		perspectives:   ["requirements-closure", "test-adequacy", "compatibility"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "chatgpt"
		second_opinion_note: "依頼書の指示で、2人目は ChatGPT Use の系列（chatgpt-final-quality-gate-strict）を先に使う。取れなければ方針どおり（standard は2人目なし）にし、逸脱として記録する"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "本人が統括にマージを委任した（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		owner: {task: "仕様化と案内の文書（S-01）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）。文書は依頼書と方針の第2節でタスク担当が書く（同じセッションの例外：文書を書く手順）"}
		impl: {task: "実行時の Python とテスト（S-02）", provider: "codex", model: "gpt-6.2-sol", effort: "medium", rationale: "方針の第2節、standard のテストで確かめられる実装。依頼書も GPT-6.2 Sol / medium を推す。Sol で失敗や見落としが記録されたときだけ GPT-6.2 Astra / high に上げる。確認の画面や chat-scratch の symlink の拒否で止まったら、worker-stop して Claude Opus 5.5 / medium に切り替える（統括が了承済み）"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
