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
		title:     "版を書く場所"
		text:      "`pyproject.toml`、`uv.lock`、提供側と dogfood の `system/spec-dock-version` を 0.7.0 にする。0.6.0 の版を固定するテストは、0.7.0 のテストに置き換える。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "migration.md の節"
		text:      "提供側 `docs/migration.md` の「## 0.6.0 への更新」の後に「## 0.7.0 への更新」を足す。内容は各 Issue の report.md（#549・#550・#551・#552・#556）と `reference_cli.md` で確かめて書く。dogfood の写しはバイトで一致させる。`git log v0.6.0..HEAD` で、リリースの時点で main に入っているものだけを書く。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json と統合テスト"
		text:      "`migration.md` と版のファイルの今のハッシュを入れ、0.6.0 のバイト（タグ v0.6.0 から取り、fixture に置く）を `known_old_sha256` に足す。ほかの変わった配布資産（スキル、README、guide、canonical、cli-redesign-guide、reference_cli）は前の Issue がすでに入れている。統合テストで、0.6.0 の資産を持つリポジトリが `installation update` で 0.7.0 に上がることを確かめる。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title:     "配布（統括）"
		text:      "R-04 はマージの後に統括が行う。この Issue の実装は扱わない。"
		satisfies: ["R-04"]
	}
}

// 移行・互換性、リスク（任意）。
// compatibility: "..."
// risks: ["..."]
