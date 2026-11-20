package spec

// 計画（Epic）。型 specdock/v1。

goal: "Antigravity のエージェントが作業用の worktree で仕様を読み書きでき、ダッシュボードで種類の名前とアイコンが Claude・Codex と同じ扱いで見える版を出す。"

// この Epic の外の前提（型にない項目）。別のリポジトリの Issue なので、slices の鍵にも、
// SpecDock の依存（リポジトリをまたいで登録できない。`dependency add` は SCOPE_NOT_FOUND）にもできない。
// GitHub の API で直接つなぐと、SpecDock はそれを DEPENDENCY_FOREIGN_REPOSITORY の食い違いとして扱い、
// iss-00674 の着手の判定が不明になるので、つながない（統括の判断、2026-11-20）。
prerequisites: {
	"gh:chemitaro/orca-web#66": {
		title: "orca-web の iss-00066（epic-00065）：稼働の印と送信欄に、Antigravity と Gemini のアイコンと名前を出す"
		needed_by: ["iss-00674"]
		needed_for: "iss-00674 の実データでの確かめ（Antigravity の名前とアイコンが出ること）。作るのは待たずに始めてよい"
	}
}

slices: {
	"iss-00673": {
		covers: ["R-01", "R-02", "F-01"]
		text: """
			Antigravity でのカタログの読み書き（D-01）：実物の `agy` での確かめ、要れば `canonical status` の `tools` の Antigravity の項目と検出と1行、`docs/canonical.md`・`docs/reference_cli.md` の案内、
			要れば配るスキルの『仕様の扱い』の制限のモードの決まりと `static-inventory.json`。書く範囲：`src/spec_dock/runtime/{domain/canonical_tools.py,infra/runtime_environment.py,application/canonical_tools_check.py,application/canonical_status.py}`、`presentation` の該当部分、`src/spec_dock/assets/spec_dock/docs/`、`src/spec_dock/assets/install_root/`、`src/spec_dock/assets/static-inventory.json`、`tests/`。
			"""
		session: "owner"
	}
	"iss-00674": {
		covers: ["R-03", "F-02"]
		text: """
			ダッシュボードの種類の名前（D-02）：`src/spec_dock/assets/dashboard/views/` の5か所と新しい小さな関数、node のテスト。orca-web の iss-00066 の後の常駐の orca-web で、Antigravity のエージェントの名前を実データで確かめる。
			iss-00673 と書く範囲が重ならないので並べて進める。
			"""
		session: "owner"
	}
	"iss-00675": {
		covers: ["R-04"]
		text: """
			リリース（0.9.10）：手本は 0.9.9 の iss-00670（PR #671）。`pyproject.toml`、`uv.lock`、`spec-dock-version`、`docs/migration.md` の節、`static-inventory.json`、利用側の写し、0.9.9 からの `installation update` の統合テスト。
			iss-00673 と iss-00674 のマージの後に始める（依存 `iss-00675 → iss-00673`、`iss-00675 → iss-00674`、登録済み）。マージの後、統括がタグを付けて wheel を入れる。
			"""
		after: ["iss-00673", "iss-00674"]
		session: "owner"
	}
}

verification: """
	iss-00673：`canonical status` の `tools` の単体テスト（Antigravity の中・外、設定あり・なし・読めない）、今の Codex・Claude Code のテストがそのまま通ること、配る資産の検査、`make lint` と全テスト。実物の `agy` で確かめた結果を報告書に残す。
	iss-00674：名前の関数の node のテスト（知る種類、知らない種類、種類なし、部品なし、表なし）、今のダッシュボードのテストがそのまま通ること、`make lint` と全テスト。
	最後に統括が、両方を入れた版を出して入れ、実際の Orca の Antigravity のエージェントで、ダッシュボードの名前とアイコンと、作業用の worktree での `canonical status` を確かめる。
	"""

rollback: "各 Issue の PR を戻す。iss-00673 を戻すと Antigravity の項目と案内がなくなり、iss-00674 を戻すと種類は今どおり生の文字列で出る。"

exit: "iss-00673 と iss-00674 が閉じ、両方を入れた版が出て、この PC で Antigravity のエージェントの名前とアイコンがダッシュボードに出る。"

execution: {
	sessions: {
		plan: {task: "Epic の仕様と切り分け（この記録）", model: "Opus 5.5", effort: "medium", rationale: "統括（方針の第2節、standard の統括）が自分で書いた"}
		owner: {task: "各 Issue のタスク担当（Issue の仕様、実装担当の起動、関門、PR）", model: "Opus 5.5", effort: "medium", rationale: "方針の第2節、standard のタスク担当。実装担当は Issue の計画で選ぶ（iss-00673 はテストで確かめられる実行時の変更なので GPT-6.2 Sol / medium、文書はタスク担当が書く。iss-00674 は画面の JS なので Opus 5.5 / medium を推す）"}
	}
}
