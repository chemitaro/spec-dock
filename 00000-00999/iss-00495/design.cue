package spec

// 設計（Issue）。型 specdock/v1。

goals:   ["I-12 で見つけた移行スクリプトの穴を、README だけに書く（コードは直さない）"]
current: "README の「戻し方」と共通の決まりに、ツリーの外のリンク、Scope が0件の verify、書き込みの上限の待ち、往復のリンクの変化が書かれていない"
target:  "これらが README に書かれ、テストが要る語の存在を確かめる"

design: {
	"D-01": {
		title:     "「戻し方」へのツリーの外のリンクの節"
		text:      "「戻し方」に小節「ツリーの外のリンク」を足す。`migrate.py` が書き換えるのは仕様のツリーの中のリンクだけであること、切り替え前のコミットの `.meta.json` から新旧のパスの対応を作って手で直した実績（#20、#240、#2228）、`export-legacy` の後も同じく手で戻すことを書く。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "共通の決まりへの3つの注意"
		text:      "「共通の決まり」の終了コードの後に、Scope が0件の `verify`（exit 2、異常ではない）、`WRITES_PER_HOUR`（500件、表示なしに最大1時間待つ）、往復で前から切れたリンクの書き方が変わること（開く先はどちらも存在しない）を箇条書きで足す。あわせて、「入れ子への戻し方」の「字面が元に戻らないのは…3種類だけ」の文に、前から切れたリンクは書き方が変わりうる旨を一言足し、README の中で記述が食い違わないようにする。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "README の語を縛るテスト"
		text:      "既存の README のテスト（`tests/integration/migration/test_migrate_plan.py`）に近い形で、要る語（`WRITES_PER_HOUR`、`no commit with schema-3 metadata was found`、ツリーの外のリンク、前から切れたリンク）が README にあることを確かめるテストを足す。"
		satisfies: ["R-01", "R-02"]
	}
}

compatibility: "README とテストだけの変更で、実行時の動きは変わらない"
