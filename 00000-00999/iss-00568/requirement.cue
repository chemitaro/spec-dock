package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "light"
	reason: "古さの判定の入力を足すだけ。誤りは警告の出方に限られ、版を戻せば直る"
}

purpose: "構造に変化がない間も、同期が正常ならダッシュボードが古いと警告しないようにする（epic-00427 R-09 の古さの表示）。"
background: "古さは `snapshot.fetched_at` だけで判定していた。定期の同期は probe（`probe.json` の `checked_at`）で変化を確かめ、変化がなければスナップショットを取り直さないので、同期が正常でも30分で『更新されていません』と出る（2026-11-04 21:15 に利用者が確認）。"
includes: ["古さの判定と、上の帯の『N分前に取得』の時刻", "サーバー、`dashboard summary`、横断の概況の3つで同じ判定を使うこと"]
excludes: ["PR の状態の古さ（`pull_requests_fetched_at`）の判定", "同期や probe の動作そのもの"]

requirements: {
	"R-01": {
		title: "構造を最後に確かめた時刻で古さを判定する"
		text:  "古さは『最後に GitHub の構造を確かめた時刻』で判定する。その時刻は、スナップショットの `fetched_at` と、probe の `checked_at`（probe に `last_error` がないときだけ）の新しいほう。30分を超えたら古い。"
		acceptance: ["スナップショットが31分前で probe が1分前（エラーなし）なら、古くない", "スナップショットが31分前で probe も31分前なら、古い"]
	}
	"R-02": {
		title: "probe が失敗している間は古くなる"
		text:  "probe に `last_error` があるときは、その `checked_at` を使わない。同期が失敗し続けているときは、今のとおり `fetched_at` で古くなる。probe がない、読めない、`checked_at` がないときも `fetched_at` だけで判定する。"
		acceptance: ["probe が1分前でも `last_error` があり、スナップショットが31分前なら、古い", "probe.json がないか壊れていても、エラーにならず `fetched_at` で判定する"]
	}
	"R-03": {
		title: "表示と判定を同じ時刻にそろえる"
		text:  "画面の上の帯の『N分前に取得』、古さの警告の『N分前から更新されていません』、API の `snapshot.fetched_at`／`age_seconds`／`stale`、`dashboard summary` の `fetched_at`／`stale` は、R-01 の同じ時刻から作る。判定は1か所の関数にまとめ、サーバー、`dashboard summary`、横断の概況が同じものを使う。"
		acceptance: ["同じ入力で、API と `dashboard summary` の `fetched_at` と `stale` が一致する", "probe.json だけが更新されたとき、サーバーが次の要求で反映する"]
	}
	"R-04": {
		title: "PR の状態の判定と契約の形は変えない"
		text:  "PR の状態（`pull_requests.status`、`pull_requests_fetched_at`）の判定は変えない。JSON の欄の名前と型は変えず、`fetched_at` の意味だけが『構造を最後に確かめた時刻』に変わる。reference_cli.md にその意味を書く。"
		acceptance: ["PR の状態の既存のテストが変わらず通る", "reference_cli.md の `fetched_at` の説明が新しい意味になっている"]
	}
}

failures: {
	"F-01": {
		title: "probe.json の時刻が未来、または形が不正でも、止まらず `fetched_at` を使う"
	}
}

constraints: ["版の番号と migration.md は変えない（#553 が行う）", "利用者の環境とほかのリポジトリを変えない。テストは一時のディレクトリで閉じる"]
decisions: ["欄の名前は変えず、`fetched_at` の意味を変える（画面の JavaScript を変えずに済み、契約の形が保たれる）", "probe の時刻が未来のときは、`now` で頭打ちにせず使わない（時計のずれで古さを隠さない）"]
