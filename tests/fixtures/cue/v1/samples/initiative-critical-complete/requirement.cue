package spec

schema: "specdock/v1"

assurance: {
	level:  "critical"
	reason: "利用者の記録の保存の仕組みを入れ替える"
}

requirements: {
	"R-01": {title: "記録を新しい保存先に移せる", acceptance: ["移した記録がすべて読める"]}
	"R-02": {title: "古い保存先を止められる", acceptance: ["古い保存先に書かれない"]}
}

failures: "F-01": {
	title:    "移す途中で止まったら、古い保存先を使い続ける"
	impact:   "記録が2か所に分かれる"
	recovery: "移し直す"
}
