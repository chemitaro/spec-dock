package spec

design: {
	"D-01": {
		title:     "版を書く場所"
		text:      "`pyproject.toml`、`uv.lock`、提供側と dogfood の `system/spec-dock-version` を 0.9.0 にする。0.8.0 の版を固定するテストは外す。機能のコードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "migration.md の節と 0.8.0 の節の訂正"
		text:      "「## 0.8.0 への更新」の後に「## 0.9.0 への更新」を足す。内容は #574・#575・#578・#572 の report.md と `git log v0.8.0..origin/main` で確かめる。0.8.0 の節の本文は配布済みのバイトのまま直さず、0.9.0 の節の「0.8.0 の節の訂正」で、#568 の意味の変更（構造の古さは max(スナップショットの fetched_at, 確かめた checked_at)）を、欄の名前と型は同じことと合わせて書く。理由：0.8.0 のバイトは `known_old_sha256` で受け入れる配布済みの版で、履歴としてそのまま残す。直した文は次の節にあり、読み手は続けて読める。写しはバイトで一致させる。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "static-inventory.json と統合テスト"
		text:      "`migration.md` と版のファイルの行の `sha256` を今のハッシュにし、0.8.0 のバイト（タグ v0.8.0 から取り、`tests/fixtures/issue580/` に置く）を `known_old_sha256` に足す。統合テスト `tests/integration/test_issue580_release_0_9_0.py` で、版、節と写しの一致、inventory、0.8.0 の資産を持つ consumer の `installation update` を確かめる。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title:     "配布（統括）"
		text:      "R-04 はマージの後に統括が行う。この Issue の実装は扱わない。"
		satisfies: ["R-04"]
	}
}
