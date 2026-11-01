package spec

// 計画（Issue）。型 specdock/v1。

goal: "雛形の README を、ルートの `.workbench/` の無視の下でもコミットできるようにする"

steps: {
	"S-01": {title: "失敗するテストを書く（Git の挙動、古いバイトからの更新、dogfood の写し）", realizes: ["R-01", "R-02", "R-03"], status: "todo"}
	"S-02": {title: "`.gitignore` に `!**/.workbench/` を足し、インベントリと dogfood の写しを更新する", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-01"]}
	"S-03": {title: "レビュー、全体のテストと lint、PR", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-02"]}
}

tests: {
	"T-01": {title: "ルートに `.workbench/` がある一時のリポジトリで、README が追跡の対象になり、ほかのファイルは無視される", verifies: ["R-01", "R-02"]}
	"T-02": {title: "0.4.2 のバイトの利用側が `installation update` で上がり、dogfood の写しが提供側と一致する", verifies: ["R-03"]}
}

verification: "`uv run pytest` と `make lint`。dogfood で `git check-ignore -v` が README を無視と判定しない。"
