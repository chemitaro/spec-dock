package spec

current: "設定を書き出す方法がない"
target:  "`export` のコマンドが、設定を JSON に書き出す"

design: {
	"D-01": {
		title: "書き出しの部品"
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "書き出し先の確かめ"
		satisfies: ["F-01"]
	}
}

risks: ["JSON の形を後から変えにくい"]
