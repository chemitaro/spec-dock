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
		text:      "`pyproject.toml`、`uv.lock`、提供側と dogfood の `system/spec-dock-version` を 0.5.1 にする。版を固定するテストの値も合わせる。過去の版を述べる文と 0.5.0 のバイトの fixture は変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "migration.md の節"
		text:      "提供側 `docs/migration.md` に「## 0.5.1 への更新」を足す。#506〜#511 と #520 の要点を各 PR の report とコードで確かめて書き、`installation update` の手順と契約の変更を述べる。dogfood の写しはバイトで一致させる。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json"
		text:      "変えた `migration.md` と版のファイルの今のハッシュを入れ、0.5.0 のバイトを `known_old_sha256` に足す。#509・#520 が足した古い版は重ねない。0.5.0 のバイトは fixture に置き、統合テストで 0.5.0 の資産を持つリポジトリが `installation update` で 0.5.1 に上がることを確かめる。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title:     "配布と古い記述の直し（統括）"
		text:      "R-04・R-05 はマージの後に統括が行う。この Issue の実装は扱わない。"
		satisfies: ["R-04", "R-05"]
	}
}

// 移行・互換性、リスク（任意）。
// compatibility: "..."
// risks: ["..."]
