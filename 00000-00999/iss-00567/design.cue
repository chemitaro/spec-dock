package spec

// 設計（Issue）。型 specdock/v1。

// 設計目標、今の状態と、この Issue の後の状態（任意）。
// goals: ["..."]
// current: "..."
// target:  "..."

// 設計の単位（責務、interface、data など）。番号（D-01、…）をキーにする。
// title と satisfies（満たす要件・失敗の条件の番号）が必須。
// standard 以上では、すべての要件に、それを満たす設計が要る。
design: {
	"D-01": {
		title:     "例とコメントだけを直す"
		text:      "cue.md（実行の割り当ての節と全体の例）と Issue の plan.cue 雛形のコメントを直す。execution の型と検査は変えない。dogfood の写しと static-inventory.json の sha256 を合わせる。"
		satisfies: ["R-01", "R-02"]
	}
}

// 移行・互換性、リスク（任意）。
compatibility: "型と検査は変わらない。既存の計画は影響を受けない。配布資産の文書と雛形の内容が変わるので、前の sha256 を known_old_sha256 に足す。"
// risks: ["..."]
