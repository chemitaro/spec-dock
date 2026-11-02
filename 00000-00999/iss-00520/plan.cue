package spec

goal: "不採用の子孫があっても親を completed で閉じられるようにする。"

steps: {
	"S-01": {title: "テストを先に書く（Red）。旧判定を固定する既存テスト（test_issue440_g2_scope_change.py の not_planned の子孫の2ケース）は、新しい判定に書き換える", realizes: ["R-01", "R-02"], status: "todo"}
	"S-02": {title: "判定を1つの関数にまとめ、plan_close と _finish_rules から呼ぶ", realizes: ["R-01"], status: "todo", after: ["S-01"]}
	"S-03": {title: "reference_cli.md、SKILL.md、写し、static-inventory を直す", realizes: ["R-02"], status: "todo", after: ["S-02"]}
}

tests: {
	"T-01": {title: "scope close: 不採用の子孫だけなら親を閉じられ、開いた子孫・状態不明の子孫があれば DESCENDANT_NOT_COMPLETED で止まる", verifies: ["R-01"]}
	"T-02": {title: "work finish: 同じ判定になる", verifies: ["R-01"]}
	"T-03": {title: "配布文書のハッシュと古い版（0.5.0）の登録が一致する", verifies: ["R-02"]}
}

verification: "uv run pytest（全体）と make lint。"
