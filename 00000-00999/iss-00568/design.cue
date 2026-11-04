package spec

// 設計（Issue）。型 specdock/v1。
goals: ["古さの判定を1か所の関数にまとめ、3つの読み手が同じ時刻を使う"]
current: "`build_model` が `snapshot.fetched_at` だけで `stale` を決め、サーバーの revision と API の通知も同じ値を使う。probe.json は読まない。"
target:  "`read_snapshot_file` が probe.json も読み、`confirmed_at()` が確かめた時刻を決め、`build_model(..., confirmed_at=)` がそれで `fetched_at`／`stale` を作る。"

design: {
	"D-01": {
		title:     "確かめた時刻の関数（domain/dashboard_snapshot.py）"
		text:      "`structure_confirmed_at(fetched_at, probe_checked_at, probe_failed, now)`：`probe_failed` でない `probe_checked_at` が `fetched_at` より新しく、`now` より未来でないときそれを返し、そうでなければ `fetched_at`。純関数で、時刻の形が不正なら `fetched_at`。"
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-02": {
		title:     "probe の読み取り（infra/dashboard_files.py）"
		text:      "`SnapshotRead` に `probe_checked_at` と `probe_failed` を足す。`read_snapshot_file` が同じ場所の `probe.json` を読む（読み取りだけ。ないか壊れていれば None と False）。"
		satisfies: ["R-02", "F-01"]
	}
	"D-03": {
		title:     "モデルと3つの読み手"
		text:      "`build_model` に `confirmed_at` を足し、`DashboardModel.fetched_at`／`stale` をそれで作る。`dashboard_summary`、`dashboard_site` が `SnapshotRead` から渡す。`dashboard_site` のキャッシュの署名と revision に probe.json を加え、API は model の値をそのまま使うので、画面の帯と警告も同じ時刻になる。"
		satisfies: ["R-03", "R-04"]
	}
	"D-04": {
		title:     "文書"
		text:      "reference_cli.md（と dogfood の写し、static-inventory.json の該当行）で、`fetched_at`／`stale` の意味を書き換える。"
		satisfies: ["R-04"]
	}
}

compatibility: "欄の名前と型は同じ。`fetched_at` が新しくなるだけで、読み手が古さを `stale` で見ている限り影響は誤警告が減ることだけ。"
risks: ["probe.json の読み取りの失敗が画面を止めないこと（D-02 で None に倒す）", "署名に probe を加え忘れると反映が遅れる（テストで確かめる）"]
