package spec

schema: "specdock/v1"

assurance: {
	level:  "strict"
	reason: "公開の契約を変える"
}

requirements: "R-01": {
	title: "設定を書き出せる"
	acceptance: ["書き出せる"]
}

failures: "F-01": title: "書き出し先があれば止まる"
