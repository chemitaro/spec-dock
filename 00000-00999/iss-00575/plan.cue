package spec

steps: {
	"S-01": {title: "最上位の切れ目、縦長、鎖、広げ直しの固定を確かめるテストを書く（Red）", realizes: ["R-01", "R-02", "R-03"], status: "done"}
	"S-02": {title: "childrenBlock の最上位で、切れ目の候補ごとに全体の倍率を計算して選ぶ。graph.js が図の領域の幅と高さを渡し、変わり終わってから並べ直す（Green）", realizes: ["R-01", "R-02", "R-03"], status: "done", after: ["S-01"]}
	"S-03": {title: "spec-dock の実データで 1440×900、1920×1080、390 の写しと、高さを変えて戻した確かめを report.md に残す", realizes: ["R-01", "R-03"], status: "done", after: ["S-02"]}
}

tests: {
	"T-01": {title: "合成の4 Initiative で、1400×760 と 1920×1080 は2つずつ2行（幅は狭めない）、幅374・高さ800は縦積み、高さなしは今までの折り返し。実データ（ブラウザー）で 1440×900 と 1920×1080 は1行に2つ以上で倍率が上がり、390 は縦積み", verifies: ["R-01"]}
	"T-02": {title: "依存でつながった Initiative の鎖が1行に残り、切れ目が鎖の中に落ちない", verifies: ["R-02"]}
	"T-03": {title: "edgeAudit の違反0（高さありを含む）、広げ直しの前後で行が同じ、ブラウザーで高さを変えて戻すと元の配置に戻りエラー0", verifies: ["R-03"]}
}
