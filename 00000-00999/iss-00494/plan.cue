package spec

goal: "見本と案内に費用と合わせ方を書き、既存のテストと配布資産の整合を保つ"

steps: {
	"S-01": {title: "文書テストを先に書く（Red）", realizes: ["R-01"], status: "todo"}
	"S-02": {title: "見本に注記を足し、canonical.md に節を足す。dogfood の写しも直す", realizes: ["R-01"], status: "todo", after: ["S-01"]}
	"S-03": {title: "static-inventory.json のハッシュと known_old_sha256 を更新する", realizes: ["R-01"], status: "todo", after: ["S-02"]}
}

tests: {
	"T-01": {title: "見本と canonical.md が費用、変えてよいこと、pre-push の形の語を含み、WORKFLOW_BRANCH_LINE が1行のまま残る", verifies: ["R-01"]}
}

verification: "make lint と uv run pytest（全体）が通る。"
