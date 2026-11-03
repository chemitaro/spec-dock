package spec

design: {
	"D-01": {
		title: "試しの仕組み（1ファイル）"
		text: "起点の違う2つの手元のサーバーを1つの Python ファイルで立てる。親（company-os の代わり）はポート A、子（SpecDock の代わり）はポート B。子は D-09 の見出しを付けて、構造の図の試し、`/files/`（sandbox の資料）、`/ds/`（CORS）を配り、D-15 の約束を実装した最小の部分を持つ。ファイルは `artifacts/` に置く。"
		satisfies: ["R-01", "R-02", "R-03"]
	}
	"D-02": {
		title: "PC での確かめ"
		text: "ヘッドレスの Chrome を CDP で操り（`--disable-features=MacAppCodeSignClone`、終了は `Browser.close`）、iPhone の幅、触る操作の模擬、見出しと postMessage の観測を行う。Safari は手に入れば safaridriver か手で確かめる。結果は項目ごとに記録する。"
		satisfies: ["R-01", "R-02", "R-03"]
	}
	"D-03": {
		title: "report.md と iPhone の手順"
		text: "項目ごとの結果表（PC Chrome、PC Safari、iPhone は利用者の確かめ待ち）、設計への直しの提案、利用者が iPhone で開くだけで確かめるチェックリスト、Tailscale の IP の起動のしかた。"
		satisfies: ["R-04"]
	}
	"D-04": {
		title: "後始末"
		text: "試しのサーバーと Chrome を止め、一時のディレクトリを消す。Tailscale の IP で待ち受ける常駐はしない。"
		satisfies: ["F-01"]
	}
}
