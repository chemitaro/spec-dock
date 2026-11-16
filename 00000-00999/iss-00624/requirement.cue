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
	reason: "テストだけを直し、製品の動きは変えない"
}

purpose:    "全体の `uv run pytest` で `tests/integration/test_issue413_native_lock.py` が、変更と関係なく時々落ちるのをなくす"
background: """
	iss-00611・iss-00620 の最終品質ゲートで、`test_terminated_owner_releases_native_start_lock_without_pid_recovery` が1回目に落ち、同じコミットのやり直しで通った（それぞれの report.md）。
	原因（タスク担当が 2026-11-17 に確かめた）：fixture の `git commit --allow-empty`（git 2.56.0）は、書いた後に `git maintenance run --auto --quiet --detach` を起こす（`GIT_TRACE=1` で観測）。切り離された子は、親の commit が返った後に `.git/objects/maintenance.lock` を作って消す。テストの `_snapshot()` は `.git` を `rglob` で走査し、各項目を `lstat` と `read_bytes` で読むので、走査の途中でロックが消えると `FileNotFoundError`、走査の前後でロックの有無が違うと、スナップショットの比較の不一致で落ちる。同じ環境（HOME は一時、`GIT_CONFIG_GLOBAL=/dev/null`）で commit の後 0.5 秒にロックが見えたのは 40 回中 1 回で、`maintenance.auto=false`・`gc.auto=0` を環境で与えると 40 回中 0 回だった。
	製品の `StartLock`（`src/spec_dock/runtime/infra/start_lock.py`）は git を起動せず、`.git` に何も書かない（flock だけ）。揺れはテストの隔離の不足で、製品の不具合ではない。
	"""

includes: ["`tests/integration/test_issue413_native_lock.py` の git の環境に、自動の maintenance と gc を止める設定を入れる"]
excludes: ["製品のコード（`src/spec_dock/`）の変更", "他のテストファイルの同じ形の見直し（このファイルだけ）", "テストの削除・skip・アサーションを緩めること"]

requirements: {
	"R-01": {
		title: "テストの fixture の git が、切り離した自動の maintenance を起こさない"
		text:  "`_environment()` が返す環境で起動するすべての git（init、commit、worktree add、clone、rev-parse）で、`maintenance.auto=false` と `gc.auto=0` が効く。設定はグローバルやシステムの git の設定に書かず、プロセスの環境（`GIT_CONFIG_COUNT`・`GIT_CONFIG_KEY_<n>`・`GIT_CONFIG_VALUE_<n>`）で与える"
		acceptance: [
			"`_environment()` の環境で `git config --get maintenance.auto` が `false`、`git config --get gc.auto` が `0` を返す（テストで確かめる）",
			"その環境で `GIT_TRACE=1` を付けた `git commit --allow-empty` の出力に `maintenance run` が出ない（テストで確かめる）",
		]
	}
	"R-02": {
		title: "native lock のテストが揺れない"
		text:  "3つのテストの主張（`.git` のスナップショットが前後で同じこと、ロックの busy・取得・識別）を変えずに、何度走らせても通る"
		acceptance: [
			"`uv run pytest tests/integration/test_issue413_native_lock.py` を単独で50回続けて走らせ、すべて通る（report.md に回数と結果）",
			"全体の `uv run pytest` を2回走らせ、どちらも失敗0（report.md に件数）",
			"`_snapshot()` とアサーションは緩めない（差分で確かめる）",
		]
	}
}

failures: {
	"F-01": {
		title: "利用者の git の設定が `GIT_CONFIG_COUNT` を使っていても、テストは利用者の環境に頼らない"
		text:  "`_environment()` は PATH 以外の環境を引き継がないので、外の `GIT_CONFIG_*` は入らない。テストの設定だけが効く"
	}
}

constraints: ["書いてよいのは `tests/` とこの Scope のディレクトリだけ（依頼書）", "製品の不具合は見つからなかったので `src/spec_dock/` は変えない"]
decisions: ["原因はテストの隔離の不足で、製品は直さない（タスク担当、2026-11-17、上の観測による）", "設定は `git config --local` ではなく環境で与える。最初の commit より前から効き、clone 先と linked worktree にも同じく効くため（タスク担当）"]
