package spec

steps: {
	"S-01": {title: "最上位の Initiative が横に並ぶことを確かめるテストを書く（Red）", realizes: ["R-01", "R-02", "R-03"], status: "done"}
	"S-02": {title: "childrenBlock で最上位の Initiative を残りの幅で作り直して並べる（Green）", realizes: ["R-01", "R-02", "R-03"], status: "done", after: ["S-01"]}
	"S-03": {title: "spec-dock の実データで 1440、1000、390 の写しを report.md に残す", realizes: ["R-01"], status: "done", after: ["S-02"]}
}

tests: {
	"T-01": {title: "幅1400で Initiative が同じ行に並び、幅374で縦に積まれる", verifies: ["R-01"]}
	"T-02": {title: "依存でつながった Initiative の鎖が1行に残る", verifies: ["R-02"]}
	"T-03": {title: "edgeAudit の違反が0で、広げ直しの前後で割り当てた幅と行が同じ", verifies: ["R-03"]}
}
