package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル。正本はここだけ。
assurance: {
	level:  "light"
	reason: "ガイドの相互リンク、ガイドの表をテストで縛ること、個別のコマンドの --help の表示だけを直す。データを書き換えず、PR を戻せば元に戻る。"
}

purpose: "CUE の Scope を書く人とエージェントが、ガイドと葉のコマンドの `--help` だけで、説明資料のガイドと共通の引数にたどり着ける。"

background: """
	epic-00425 の I-6（iss-00477）のレビューで、次の3つが積み残された。

	- 配布するガイド `issue-plan.md` と `scope-layering.md` は `cue.md` にだけリンクし、説明資料のガイド `explanation.md` にリンクしない（`overview.md` は両方へつなぐ）。
	- `cue.md` の「検査と表示」の誤りのコードの表は、`canonical.md` の表との和集合でしかテストに縛られていない。`cue.md` の行が増えても減っても、テストが気づかない。
	- 葉のコマンド（例 `spec-dock scope create issue --help`）の一覧に、共通の引数（`--json`、`--offline`、`--timeout` など）が出ない。`cue.md` は「葉の `--help` の一覧には出ませんが、使えます」と補っている。

	この Issue は、spec-dock で初めて CUE の仕様で始めから終わりまで回す Issue でもある（epic-00425 の R-J1、AC-14）。
	"""

includes: [
	"配布するガイド（`src/spec_dock/assets/spec_dock/docs/authoring/`）と、その dogfood の写し（`spec-dock/docs/authoring/`）、`static-inventory.json` のハッシュ",
	"`cue.md` の「検査と表示」の表を縛るテスト",
	"葉のコマンドの `--help` の表示（`src/spec_dock/runtime/cli/options.py`）",
	"`report.md` の「CUE の仕様の試し」の記録",
]

excludes: [
	"空の CUE の文書が検査に通ること（設計どおり。気づいたことは試しの記録に書く）",
	"`.md` の雛形の削除（epic-00424 の I-13）",
	"型（`specdock/v1`）と CUE の雛形の変更（直したい点は提案として記録する）",
	"共通の引数の受け付け方（意味、既定値、位置、どの葉で受け付けるか）の変更",
]

requirements: {
	"R-01": {
		title: "`issue-plan.md` と `scope-layering.md` の CUE の節が、`cue.md` と `explanation.md` の両方へリンクする"
		text:  "配布するガイドと dogfood の写しの両方を直し、`static-inventory.json` の `sha256` を新しい中身に、`known_old_sha256` に今の中身を足す。"
		acceptance: [
			"両方のガイドの「保証レベル（CUE の Scope）」の節に `(cue.md)` と `(explanation.md)` がある",
			"dogfood の写しが配布するガイドとバイトで一致し、目録のハッシュが合う",
		]
	}
	"R-02": {
		title: "`cue.md` の「検査と表示」の誤りのコードの表が、検査の返すコードと一対一に合うことを、`cue.md` 単独でテストが確かめる"
		text:  "検査の返すコードは、`scope_check` と `canonical_scope_check` の公開のコード。表の行が多くても少なくても失敗する。止まるコードの終了コードも、実装と合うことを確かめる。"
		acceptance: [
			"表の行のコードの集合が、検査のコードの集合と等しいことをテストが確かめる",
			"`cue` の道具の失敗のコードの「止まる（N）」が、実装の終了コードと合うことをテストが確かめる",
		]
	}
	"R-03": {
		title: "葉のコマンドの `--help` の一覧に、その葉で受け付ける共通の引数が出る"
		text: """
			共通の引数は、`--json`、`--non-interactive`、`--dry-run`、`--offline`、`--project`、`--expect-current`、`--expect-backend`、`--timeout`、`--color`、変更するコマンドだけの `--yes`/`-y`、`work start` と `branch switch` だけの `--lock-timeout`。
			受け付けない葉（`--dry-run` を拒む `canonical sync` など、`--offline` を拒む `canonical sync`/`canonical resume`）には出さない。
			"""
		acceptance: [
			"`spec-dock scope create issue --help` の一覧に `--json`、`--offline`、`--timeout`、`--yes`、`--dry-run` が出る",
			"どの葉でも、一覧に出る共通の引数が、実際に解析で受け付けられる",
			"読むだけの葉（`scope check` など）に `--yes` が出ない",
		]
	}
	"R-04": {
		title: "`cue.md` の「検査と表示」の共通の引数の説明が、直した後の `--help` の実態に合う"
		acceptance: ["「葉の `--help` の一覧には出ません」という文が消え、一覧に出ることを書く"]
	}
	"R-05": {
		title: "`report.md` に「CUE の仕様の試し」の記録がある"
		text:  "書きやすかったこと、書きにくかったこと、`scope check` と `scope render` の使い勝手、型・雛形・ガイドへの提案（優先度つき）、手間の目安。"
	}
}

failures: {
	"F-01": {
		title:  "共通の引数を help に出しても、引数の受け付け方（意味、既定値、位置、拒む組み合わせ）は変わらない"
		impact: "help の表示のために parser に足した項目が解析に効くと、既存のコマンドの動きが変わる"
	}
	"F-02": {
		title: "Markdown の Scope の回帰と、既存の help とコマンドの補完のテストを壊さない"
	}
}

constraints: [
	"型（`specdock/v1`）と雛形（`spec-dock/templates/`）は変えない",
	"Epic の文書とほかの Scope は変えない",
]

decisions: [
	"共通の引数は、解析の前に取り除く今の作りのまま、葉の parser には表示だけの項目（`default=SUPPRESS`）として「common options」の組に足す",
]
