package spec

schema: "specdock/v1"

assurance: {
	level:  "strict"
	reason: "公開の CLI の契約を変える"
}

purpose:    "設定を書き出せる"
background: "利用者が、設定を別の PC に移したい"
includes: ["書き出しのコマンド"]
excludes: ["読み込み"]

requirements: "R-01": {
	title: "設定を JSON に書き出せる"
	acceptance: ["書き出した JSON を、そのまま読み込める"]
}

failures: "F-01": {
	title:    "書き出し先がすでにあるときは、何も書かずに止まる"
	impact:   "利用者のファイルを上書きしない"
	recovery: "別の場所を指定して、もう一度実行する"
}

constraints: ["Python 3.10 以上"]
