package spec

// 設計（Issue）。型 specdock/v1。

current: "`_environment()` は HOME を一時のディレクトリにし、`GIT_CONFIG_NOSYSTEM=1`・`GIT_CONFIG_GLOBAL=/dev/null` でグローバルとシステムの設定を切るが、git の既定の `maintenance.auto=true`（自動で切り離して走る）は残る"
target:  "`_environment()` が、自動の maintenance と gc を止める設定を環境で加える。テストの主張は変わらない"

design: {
	"D-01": {
		title: "`_environment()` に git の設定を環境で足す"
		text: """
			`_environment()` の `environment.update` に `GIT_CONFIG_COUNT=2`、`GIT_CONFIG_KEY_0=maintenance.auto`・`GIT_CONFIG_VALUE_0=false`、`GIT_CONFIG_KEY_1=gc.auto`・`GIT_CONFIG_VALUE_1=0` を足す。同じ環境が holder と probe の Python にも渡るが、それらは git を起動しないので影響はない。
			退けた案：(a) `_snapshot()` で消えたファイルを許す（ロックが走査の前後のどちらかだけにあると比較が不一致になり、主張も弱まる）。(b) commit に `-c` を付ける（clone と worktree add に付け忘れが残る）。(c) 走査の前に maintenance の終わりを待つ（終わりを知る確かな手段がなく、遅くなる）。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-02": {
		title: "設定が効くことの回帰テスト"
		text:  "同じファイルに、`_environment(tmp_path)` で `git config --get` の値と、一時のリポジトリで `GIT_TRACE=1` を付けた commit の stderr に `maintenance run` が出ないことを確かめるテストを足す（観測の継ぎ目）"
		satisfies: ["R-01"]
	}
}

risks: ["git の将来の版で自動の仕事の設定名が変わると、また揺れうる（D-02 のテストが `maintenance run` の起動を見張る）"]
