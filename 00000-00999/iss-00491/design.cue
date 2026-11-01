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
	"D-01": {title: "版の置き場をそろえる", text: "pyproject.toml、uv.lock、system/spec-dock-version（提供側と dogfood）、版を固定したテストを 0.4.1 にする。", satisfies: ["R-01"]}
	"D-02": {title: "migration.md の節", text: "「## 0.4.1 への更新」を足し、dogfood の写しを同じ内容にする。", satisfies: ["R-02"]}
	"D-03": {title: "在庫の既知の古い版", text: "変わる配布資産（版のファイル、migration.md）の 0.4.0 のハッシュを known_old_sha256 に足し、更新のテストで確かめる。", satisfies: ["R-03"]}
	"D-04": {title: "README の直し", text: "scripts/migrate-to-canonical/README.md の撤去の版を 0.5.0 にする。", satisfies: ["R-04"]}
}

// 移行・互換性、リスク（任意）。
// compatibility: "..."
// risks: ["..."]
