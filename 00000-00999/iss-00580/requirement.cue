package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "全リポジトリへ配る版を作る。誤りは次の版で直せるが、7つのリポジトリの検査と画面に広く効く"
}

purpose:    "SpecDock 0.9.0（ダッシュボードの状態の色と形 #574、Initiative の横並び #575、構造の図の隙間の直し #578、細かい直し #572）を出す。"
background: "0.8.0 の後に #572・#574・#575・#578 が main に入った。手順は #536（0.8.0）と同じ。マージの後のタグ、導入、配布は統括が行う。0.8.0 の節は #568 の意味の変更を「足すものだけ」と書いていて食い違うので、0.9.0 の節で正す。"
excludes: ["機能のコードの変更", "タグの作成、パッケージの導入、配布（統括）"]

requirements: {
	"R-01": {
		title: "版が 0.9.0 になる"
		text:  "`pyproject.toml`、`uv.lock`、`system/spec-dock-version`（提供側と dogfood の写し）が 0.9.0 になる。"
		acceptance: ["4つの場所の版がすべて 0.9.0 で、統合テストが確かめる"]
	}
	"R-02": {
		title: "migration.md が 0.9.0 の変更を説明し、0.8.0 の節の食い違いを正す"
		text:  "提供側と dogfood の `migration.md`（バイト一致）に「## 0.9.0 への更新」の節が「## 0.8.0 への更新」の直後にある。マージ済みの #574・#575・#578・#572 と常駐の自動の起動し直しを述べ、「0.8.0 の節の訂正」で #568 の意味の変更を正しく説明する。"
		acceptance: [
			"節の見出しの順と、主な語（progress、revision、frameExits、/favicon.ico、max(fetched_at、checked_at) の説明、自動で起動し直）が節にある",
			"提供側と dogfood の写しがバイトで一致する",
			"`git log v0.8.0..origin/main` でマージ済みでないものは書かれていない",
		]
	}
	"R-03": {
		title: "0.8.0 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` の `migration.md` と版のファイルの行が今のハッシュと、0.8.0 のバイト（タグ v0.8.0）を既知の古い版として持つ。ほかの行は変えない。"
		acceptance: [
			"0.8.0 のバイトの fixture から作った consumer が `installation update` で2つのファイルだけ変わって成功する",
			"ほかの行のハッシュと既知の古い版は変わらない",
		]
	}
	"R-04": {
		title: "タグ・導入・配布は統括が行う"
		text:  "マージの後のタグ、パッケージの導入、配布は、この Issue の PR では行わない。"
		acceptance: ["PR にタグも機能のコードの変更もない"]
	}
}

failures: {}
