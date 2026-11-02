package spec

// 計画（Epic）。型 specdock/v1。

goal: "canonical の処理の不足を直した 0.5.1 を5つのリポジトリに配り、移行の控えを片付ける。"

slices: {
	"iss-00508": {
		covers:  ["R-03", "F-01"]
		text:    "第1波。利用者のファイルを許可なく消すおそれがあるので、最初に直す。"
		session: "std"
	}
	"iss-00509": {
		covers:  ["R-04"]
		text:    "第1波。#508 と並べる（直す場所が重ならない）。"
		session: "light"
	}
	"iss-00510": {
		covers:  ["R-05"]
		text:    "第1波。#508 と並べる（直す場所が重ならない）。"
		session: "light"
	}
	"iss-00506": {
		covers:  ["R-01", "F-01"]
		text:    "第2波。#507 と並べる。"
		after:   ["iss-00508"]
		session: "std"
	}
	"iss-00507": {
		covers:  ["R-02", "F-01"]
		text:    "第2波。#506 と並べる。ぶつかったら、後にマージするほうが main を取り込む。"
		after:   ["iss-00508"]
		session: "std"
	}
	"iss-00520": {
		covers:  ["R-09"]
		text:    "第2波。#506 と #507 と並べる。#506 も `scope close` を直すので、ぶつかったら後にマージするほうが main を取り込む。"
		after:   ["iss-00508"]
		session: "light"
	}
	"iss-00511": {
		covers:  ["R-06"]
		text:    "第3波。ほかの直しが変えた文書も含めて整えるので、#506、#507、#509、#510、#520 の後に行う。"
		after:   ["iss-00506", "iss-00507", "iss-00509", "iss-00510", "iss-00520"]
		session: "light"
	}
	"iss-00513": {
		covers:  ["R-07", "F-02"]
		text:    "第4波。版を 0.5.1 にする PR は担当が作る。マージの後の導入と4つのリポジトリへの配布は統括が行う。"
		after:   ["iss-00511"]
		session: "light"
	}
	"iss-00514": {
		covers:  ["R-08", "F-03"]
		text:    "第5波。0.5.1 を配ってから1〜2週間の通常の利用の後、統括が一覧を作り、利用者の許可の後に片付ける。"
		after:   ["iss-00513"]
		session: "coord"
	}
}

verification: "各 Issue の PR で `make lint` と `uv run pytest`（全体）と CI を通す。standard の Issue は、仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通す。light の Issue は、仕様のレビュー opus/medium、コードのレビュー sonnet/high、最終品質ゲート opus/high（1人）。配布の後、5つのリポジトリで `canonical status` と検査のワークフローを確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。配った後なら、パッケージを 0.5.0 に戻し、各リポジトリの配布の PR を `git revert` する。片付け（#514）は戻せないので、利用者の許可を条件にする。"
exit: "#506〜#511、#513、#514、#520 が閉じ、epic-00424 を閉じ、5つのリポジトリが 0.5.1 で `canonical status` が ok、控えの扱いが #514 の report.md に記録され、この Epic の report.md に結果をまとめた。"

execution: {
	sessions: {
		coord: {task: "統括（計画、配布、片付け、利用者への報告）", model: "opus", effort: "high", rationale: "policy §5 統括役"}
		std: {task: "standard の Issue の実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装"}
		light: {task: "light の Issue の実装（Orca の worker）", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装"}
	}
	reviews: {
		"std-spec": {role: "standard の Issue の仕様のレビュー", after: "iss-00508", model: "opus", effort: "high"}
		"std-code": {role: "standard の Issue のコードのレビュー", after: "iss-00508", model: "opus", effort: "high"}
		"std-gate": {role: "standard の Issue の最終品質ゲート", after: "iss-00508", model: "opus", effort: "high"}
		"light-spec": {role: "light の Issue の仕様のレビュー", after: "iss-00509", model: "opus", effort: "medium"}
		"light-code": {role: "light の Issue のコードのレビュー", after: "iss-00509", model: "sonnet", effort: "high"}
		"light-gate": {role: "light の Issue の最終品質ゲート", after: "iss-00509", model: "opus", effort: "high"}
	}
}
