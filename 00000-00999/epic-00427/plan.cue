package spec

// 計画（Epic）。型 specdock/v1。
// 依存は GitHub に登録済み（2026-11-03）。after はそれと同じ。

goal: "利用者ごとに1つのサーバーで、全リポジトリの仕様の構造（段階1、0.6.0）と文書（段階2、0.7.0）を見せるダッシュボードを出し、company-os に埋め込めるようにし、今の Markdown と PlantUML のダッシュボードを撤去する。"

slices: {
	"iss-00527": {
		covers:  ["F-13"]
		text:    "第1波。試作：起点の違う iframe の中で、iPhone の Safari と PC のブラウザーが、構造の図の指の操作（つまむ、移動、ダブルタップ）、`frame-ancestors` の決まり、`sandbox` の資料の切り離しと `/ds/` の読み込み、戻るの履歴（D-15）、写す機能の代わり（D-17）をどう扱うかを確かめる。製品のコードは出さず、結果を report.md に書き、設計（D-08、D-09、D-15、D-17）を直す材料にする。iPhone の実機の確かめは利用者に頼む。"
		session: "light"
	}
	"iss-00528": {
		covers:  ["R-07", "R-09", "R-10", "R-20", "R-21", "F-01", "F-02", "F-03", "F-04", "F-06"]
		text:    "第1波。D-04 の状態のモデル、D-05 の要約、D-12 の読めないときの扱いと、`dashboard summary`（D-01 の一部）。HTTP は作らない。#527 と並べる。"
		session: "std"
	}
	"iss-00529": {
		covers:  ["R-01", "R-02", "R-03", "R-04", "R-05", "R-08", "R-22", "R-27", "F-07", "F-08", "F-09", "F-12"]
		text:    "第2波。D-02 のサーバー、D-03 の道筋と API、D-06 の在りかの記録、D-09 の切り離しと枠の決まり、D-13 の `hide`／`show`／`list`、D-15 の埋め込みの表示と postMessage の約束（サーバーの側と、確かめ用の空の画面）。画面そのものは #531・#532。"
		after:   ["iss-00528"]
		session: "std"
	}
	"iss-00530": {
		covers:  ["R-28"]
		text:    "第3波。D-14 の常駐（`dashboard service install`／`status`／`uninstall`）と、版の更新の後の起動し直し。#531・#532・#533 と並べる。"
		after:   ["iss-00529"]
		session: "std"
	}
	"iss-00531": {
		covers:  ["R-06", "R-11", "R-12", "R-13", "R-14", "R-17", "R-18", "R-24", "R-29", "F-05"]
		text:    "第3波。D-07 の画面の作り、D-08 のボード・一覧・詳しい画面・検索、D-16 の横断の概況、D-17 の写せるコマンド。#527 の試作の結果を取り込む。#532 と並べる（画面のモジュールを分けてぶつからないようにする）。"
		after:   ["iss-00529", "iss-00527"]
		session: "std"
	}
	"iss-00532": {
		covers:  ["R-15", "R-16", "F-11"]
		text:    "第3波。D-08 の構造の図（ホーム）と時間の軸。#527 の試作の指の操作の結果を取り込む。#531 と並べる。"
		after:   ["iss-00529", "iss-00527"]
		session: "std"
	}
	"iss-00533": {
		covers:  ["R-23"]
		text:    "第3波。D-10 の撤去。#530〜#532 と並べる（直す場所が重ならない）。"
		after:   ["iss-00529"]
		session: "std"
	}
	"iss-00534": {
		covers:  ["R-23"]
		text:    "第4波。0.6.0 を出し、5つのリポジトリに配る。`migration.md` の「0.6.0 への更新」（コマンドが8つ増える、`canonical status` の `dashboard` の項目が消える、残った5つのファイルを消してよい）。マージの後の導入と配布は統括が行い、利用者の PC で `dashboard serve` と iPhone からの表示を確かめる。"
		after:   ["iss-00530", "iss-00531", "iss-00532", "iss-00533"]
		session: "light"
	}
	"iss-00535": {
		covers:  ["R-19", "R-25", "R-26", "F-10"]
		text:    "第5波（段階2）。D-11 の文書の描画と計画の進み具合。"
		after:   ["iss-00534"]
		session: "std"
	}
	"iss-00536": {
		covers:  ["R-19", "R-25", "R-26"]
		text:    "第6波（段階2）。0.7.0 を出し、5つのリポジトリに配る。"
		after:   ["iss-00535"]
		session: "light"
	}
}

verification: "各 Issue の PR で `make lint` と `uv run pytest`（全体）と CI を通す。standard の Issue は、仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通す。light の Issue は、仕様のレビュー opus/medium、コードのレビュー sonnet/high、最終品質ゲート opus/high（1人）。画面の Issue（#531、#532）は、PC のブラウザーでの確かめを報告に残し、iPhone の Safari の確かめは利用者に頼む。0.6.0 と 0.7.0 の配布の後、5つのリポジトリで `canonical status` と、`dashboard serve` での各リポジトリの表示を確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。配った後なら、常駐を入れていれば `dashboard service uninstall` を先に行い、パッケージを前の版に戻し、各リポジトリの配布の PR を `git revert` する。"
exit: "#527〜#536 が閉じ、5つのリポジトリが 0.7.0 で、利用者の PC と iPhone から全リポジトリのダッシュボードが開け、company-os の試しの親の画面に埋め込めることを確かめ、この Epic の report.md に結果をまとめた。"

execution: {
	sessions: {
		coord: {task: "統括（計画、配布、利用者への報告）", model: "opus", effort: "high", rationale: "policy §5 統括役"}
		std: {task: "standard の Issue の実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装"}
		light: {task: "light の Issue の実装（Orca の worker）", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装"}
	}
	reviews: {
		"std-spec": {role: "standard の Issue の仕様のレビュー", after: "iss-00528", model: "opus", effort: "high"}
		"std-code": {role: "standard の Issue のコードのレビュー", after: "iss-00528", model: "opus", effort: "high"}
		"std-gate": {role: "standard の Issue の最終品質ゲート", after: "iss-00528", model: "opus", effort: "high"}
		"light-spec": {role: "light の Issue の仕様のレビュー", after: "iss-00527", model: "opus", effort: "medium"}
		"light-code": {role: "light の Issue のコードのレビュー", after: "iss-00534", model: "sonnet", effort: "high"}
		"light-gate": {role: "light の Issue の最終品質ゲート", after: "iss-00534", model: "opus", effort: "high"}
	}
}
