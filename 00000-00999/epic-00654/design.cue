package spec

// 設計（Epic）。型 specdock/v1。

design: {
	"D-01": {
		title:     "入力の決まりの1つのモジュール"
		text:      "wheel の見分けと写し、キーの写し、横取りしない場面、つなぎを `views/graph/view_input.js` に置き、両方の画面が使う。詳細は iss-00655 の design.cue（D-01〜D-05）。"
		satisfies: ["R-01", "R-02", "R-03", "R-04"]
	}
}
