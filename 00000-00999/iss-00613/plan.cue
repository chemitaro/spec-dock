package spec

// 計画（Issue）。型 specdock/v1。

goal: "`GET /api/v1/repositories` が各リポジトリの `parent` と `tier` を返し、道を出さず、契約の文書に書かれている状態にする（サーバーの側だけ、画面は変えない）"

steps: {
	"S-01": {title: "T-01〜T-06 のテストを先に書き、開始のコミットで落ちる（`dashboard_nesting` がない、`parent`・`tier` がない）ことを確かめる（Red）。`tests/unit/application/test_dashboard_nesting.py`（純粋な関数）と `tests/unit/application/test_dashboard_repositories_nesting.py`（`DashboardSite` と HTTP、`tmp_path` の合成の登録簿）に置く", realizes: ["R-01", "R-02", "R-03", "F-02", "F-03", "F-05"], status: "done", session: "impl-sol"}
	"S-02": {title: "`dashboard_nesting.py`（D-01）、`DashboardSite` の `nesting` と `nested_repositories()`（D-02）、`_repositories` の `parent`・`tier`（D-03）を実装し、S-01 のテストと今のダッシュボードのテストを通す（Green）", realizes: ["R-01", "R-02", "R-03", "F-02", "F-03", "F-05"], status: "doing", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "`reference_cli.md` の契約と `static-inventory.json` の sha256（D-04）を直し、T-07 を足して通す。`make lint` と全体の `uv run pytest` を通す", realizes: ["R-03"], status: "todo", after: ["S-02"], session: "impl-sol"}
	"S-04": {title: "実機の確かめ：作業ツリーの wheel を隔離した venv に入れ、この PC の状態の置き場の写し（一時の置き場）で `dashboard serve --offline --state-root` を別のポートで立て、`/api/v1/repositories` の `parent`・`tier` が company-os の入れ子と、外の spec-dock・orca-web（最上位）になり、応答に道がないことを report.md に残す（T-08）", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "この PC の登録の形（9つ、合成の道 `/ws/company-os`、`/ws/company-os/businesses/housing-lifecycle`、`…/products/taikyohiyou_project`、`/ws/company-os/businesses/input-devices`、`…/products/{generic-mona,tenting-cradle,yubisaki}`、`/ws/tools/spec-dock`、`/ws/tools/orca-web`）で、`repository_nesting` の `parent` と `tier` が R-01・R-02 の受け入れのとおり", verifies: ["R-01", "R-02"]}
	"T-02": {title: "境界の形：`/ws/a` と `/ws/a-b` は親子にならない、同じ道の2つは親子にならない、3段で最も近い祖先、親の直下は札が空、途中 `groups/team` は `[\"groups\", \"team\"]`、`services` は `[\"サービス\"]`", verifies: ["R-01", "R-02"]}
	"T-03": {title: "チェックアウトが None（ambiguous）のリポジトリは `parent` null・札が空で、中のリポジトリの親にならない。中のリポジトリは外の出す祖先の子で、札はクローンの境界から数える", verifies: ["F-02"]}
	"T-04": {title: "隠したリポジトリ（境界にだけある）の中のリポジトリは、外の出す祖先の子で、札に隠したものの名前とその上の途中の名前（例 `businesses`）が現れない。出す祖先がなければ最上位で札が空。リポジトリの分からない行の境界も同じに効く", verifies: ["F-03"]}
	"T-05": {title: "絶対でない道（空、相対）の行は境界にも親にも使われず、そのリポジトリは最上位で札が空", verifies: ["F-05"]}
	"T-06": {title: "`tmp_path` の合成の登録簿（この PC の形、隠す印を1つ、ambiguous を1つ、分からない行を1つ）で `DashboardSite` と `GET /api/v1/repositories` を通し、(a) 各リポジトリに `parent`・`tier` があり今の7つの項目の値と並びが今と同じ、(b) 各 `parent` が null か応答の鍵、(c) 隠したリポジトリが出ず、その中のものが出す祖先の子、(d) 応答の JSON の文字列に `tmp_path` と各 `main_checkout`・カタログの道が現れない、(e) 隠す印を変えると次の要求で入れ子が変わる", verifies: ["R-01", "R-02", "R-03", "F-02", "F-03"]}
	"T-07": {title: "配る側の `reference_cli.md` の API の項目に `parent` と `tier` の説明があり、`static-inventory.json` の sha256 が内容と合う（今の目録のテストを含む）", verifies: ["R-03"]}
	"T-08": {title: "実機：この PC の登録（9つ）の写しで立てた別のポートのサーバーの `/api/v1/repositories` の `parent`・`tier` の表と、応答に `/Users/`・`/Volumes/` などの道の文字列がないことの確かめが report.md にある（道は伏せて書く）", verifies: ["R-01", "R-02", "R-03"]}
}

verification: """
	節目：`uv run pytest tests/unit/application/test_dashboard_nesting.py tests/unit/application/test_dashboard_repositories_nesting.py tests/unit/application`。最後に `make lint`、`uv run pytest`（全体、手元で）。
	実機：作業ツリーの wheel を `.workbench/iss-00613/venv` に入れ、この PC の状態の置き場から登録簿・隠す印・ダッシュボードの設定とスナップショットを `.workbench/iss-00613/state` に写し、
	`spec-dock dashboard serve --port <空いている番号> --offline --state-root <絶対の道>` で立てて `curl` で読む。常駐のダッシュボード（47800）と道具の環境には触れない。終わったらそのサーバーを止める。
	"""

rollback: "PR を戻す（サーバーのコード、配る側の文書、目録、テストだけ）。一覧の API の `parent`・`tier` がなくなり、今の応答に戻る。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の確かめがある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {}
	checkpoints_note: "なし（サーバーの小さな変更で、手順が続けて1つの実装担当に入るため。すべての手順の後、最終品質ゲートへそのまま進む）"
	final_quality_gate: {
		scope:          "開始のコミット 2c7427a97ff97bd3b7ffc463401f3cffffab36e1 から S-03 の終わりまで（S-04 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "security"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00613/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01〜S-03）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。入れ子の計算と一覧の API の拡張は Python の単体テストと HTTP のテストで確かめられる（方針の「テストで確かめられる実装」× standard）。本人の指示で Sol を使う。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		owner:      {task: "実機の確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
