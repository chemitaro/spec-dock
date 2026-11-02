package spec

goals: ["親を `completed` で閉じる判定を1か所にまとめ、`scope close` と `work finish` で同じにする"]
current: "`plan_close`（scope_completion_plan.py）と `_finish_rules`（canonical_work.py）が、それぞれ子孫の状態が `completed` でなければ `DESCENDANT_NOT_COMPLETED` で止める。"
target: "子孫の状態が `completed` か `not-planned` なら通し、`open` か `unknown` が1つでもあれば止める。"

design: {
	"D-01": {
		title:     "子孫の判定の部品"
		text:      "`scope_completion_plan.py` に `require_descendants_settled(statuses)` 相当の関数を1つ置く。子孫の状態が `completed`、`not-planned` 以外（`open`、`unknown`）なら `ValueError(\"DESCENDANT_NOT_COMPLETED\")`。`plan_close`（reason が completed のとき）と `canonical_work._finish_rules` の両方がこれを呼ぶ。エラーのコードと終了コードは変えない。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "文書の更新"
		text:      "`src/spec_dock/assets/spec_dock/docs/reference_cli.md` の C10 に、不採用の子孫は止めず、開いている・状態不明の子孫は `DESCENDANT_NOT_COMPLETED` で止まると書く。dogfood の写し（`spec-dock/docs/`）と `static-inventory.json` のハッシュを揃え、0.5.0 のバイトを既知の古い版に足す。SKILL.md の 'Parent completion requires completed descendants' も直す。"
		satisfies: ["R-02"]
	}
}

compatibility: "エラーのコード・終了コード・JSON の形は変えない。止まる条件が狭まるだけ（不採用の子孫を許す）。不採用の子孫を持つ親の `scope close`／`work finish` は、終了コード3から0に変わる。この変更は #513 が migration.md の 0.5.1 の節に載せる（Epic の R-09 と decisions で採用済み。worker_done で統括にも伝える）。"
