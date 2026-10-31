package spec

// 設計（Issue）。型 specdock/v1。light では任意だが、help の作りだけ短く書く。

current: "`parse_vnext` は、共通の引数を argparse に渡す前に取り除く。葉の parser は葉の引数だけを持つので、`--help` の一覧に共通の引数が出ない。"
target:  "葉の parser に「common options」の組を足し、その葉で受け付ける共通の引数を表示だけの項目として持つ。解析の経路は変えない。"

design: {
	"D-01": {
		title: "葉の parser の表示だけの共通の引数"
		text: """
			`build_vnext_parser` が、葉ごとに `add_argument_group("common options")` を足し、`_COMMON_SWITCHES` と `_COMMON_VALUES` から、その葉で受け付けるものだけを `default=argparse.SUPPRESS` で足す。
			受け付けるかの判定は、`parse_vnext` の拒む規則（`MUTATING_LEAF_PATHS`、`_NO_PLAN_LEAVES`、`canonical sync`/`resume` の `--offline`、`--lock-timeout` の葉）と同じ1つの関数にまとめ、解析と表示が食い違わないようにする。
			`parse_vnext` は共通の引数を先に取り除くので、足した項目は解析では値を作らない（`--` の後の語は位置の引数のまま）。
			"""
		satisfies: ["R-03", "F-01"]
	}
	"D-02": {
		title:     "ガイドとテスト"
		text:      "ガイドの相互リンクと `cue.md` の文を直し、`test_issue477_authoring_docs.py` に、`cue.md` 単独の表のテストと、リンクのテストを足す。"
		satisfies: ["R-01", "R-02", "R-04"]
	}
}

compatibility: "help の文字列だけが変わる。`--json` の help の `data.text` も同じく長くなる。解析の結果と終了コードは変わらない。"

risks: ["使い方の行（usage）が長くなる。正確さを優先する"]
