package spec

// 設計（Issue）。型 specdock/v1。

goals: ["雛形の README だけを、ルートの `.workbench/` の無視があっても追跡の対象にする", "配布資産の更新の経路を壊さない"]
current: "`spec-dock/.gitignore` は `**/.workbench/*` と `!**/.workbench/README.md` を持つ。しかしルートの `.gitignore` の `.workbench/` はディレクトリそのものを無視し、Git はその下へ降りないので、`!` の行が効かない。"
target:  "`spec-dock/.gitignore` が `!**/.workbench/` を `**/.workbench/*` より前に持つ。深い階層の `.gitignore` は浅いものに勝つので、ディレクトリが戻り、`*` と `!README.md` の組が従来どおり働く。"

design: {
	"D-01": {
		title:     "`spec-dock/.gitignore` にディレクトリを戻す行を足す"
		text:      "配布資産 `src/spec_dock/assets/spec_dock/.gitignore` の `**/.workbench/*` の前に `!**/.workbench/` を足す。一時のリポジトリ（ルートに `.workbench/`）で `git check-ignore -v` と `git add -n` を使い、README が対象になり、`note.md` が無視されることを確かめた。"
		satisfies: ["R-01", "R-02"]
	}
	"D-02": {
		title:     "配布資産の更新の経路"
		text:      "`static-inventory.json` の `spec-dock/.gitignore` の `sha256` を新しい版にし、0.4.2 のバイト（sha256 `b28e6f2…`）を `known_old_sha256` に足す。0.4.2 のバイトは `tests/fixtures/issue497/` に置く。dogfood の `spec-dock/.gitignore` を同じ内容にする。"
		satisfies: ["R-03"]
	}
}

compatibility: "`spec-dock/` の下の雛形以外の `.workbench/README.md` も同じ規則で追跡の対象になる（従来の意図どおり）。利用側の見た目の変化は、`.workbench/` の無視の下でも雛形の README が追跡の対象になることだけ。バイトが変わるので `installation update` が更新を提案する。版は上げず、0.5.0 の「更新」の節に書く内容は report.md に残す。"
risks: [
	"採らなかった案：置き場の名前を変える案は、`scope create` の雛形の写し方と既存の利用側の README に響く。`installation update` の警告は、利用者が `git add -f` する手間を残し、問題の原因を直さない。",
	"`!**/.workbench/` は `spec-dock/` の下のすべての `.workbench/` を戻すが、中身は `**/.workbench/*` で無視されたままなので、README 以外は追跡されない。",
]
