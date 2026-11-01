package spec

goal: "README に I-12 の穴を書き、テストで語を縛る"

steps: {
	"S-01": {title: "README の語を縛るテストを足し、失敗を確かめる（Red）", realizes: ["R-01", "R-02"], status: "done"}
	"S-02": {title: "「戻し方」に、ツリーの外のリンクの小節を書く", realizes: ["R-01"], status: "done", after: ["S-01"]}
	"S-03": {title: "共通の決まりに、3つの注意を書く", realizes: ["R-02"], status: "done", after: ["S-01"]}
}

tests: {
	"T-01": {title: "README に、ツリーの外のリンクを手で戻す説明の語がある", verifies: ["R-01"]}
	"T-02": {title: "README に、0件の verify、500件の上限の待ち、往復のリンクの変化の語がある", verifies: ["R-02"]}
}
