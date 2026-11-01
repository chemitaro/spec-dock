package spec

// 設計（Issue）。型 specdock/v1。

current: """
	`scope_check._shape_errors` は、`cue` の誤りから派生の誤り（`_` で始まる項目、組み込み関数、`N errors in empty disjunction` の見出し）を除き、残りを項目と文で重複を除いて、1件ずつ `CUE_INVALID` にする。`hint` は英語の固定の文。
	`scope render` は、`file:` の URL を `design_system_base` に渡し、`wrap_page` が `ds.css` と `ds.js` へのリンクを書く。
	"""
target: "同じ項目の選言の誤りを1件にまとめ、`CUE_INVALID` の `hint` を日本語にし、light でテストのない Issue に警告を出し、`scope render` でデザインシステムを埋め込めるようにする。"

design: {
	"D-01": {
		title: "同じ項目の選言の誤りをまとめる"
		text: """
			`_shape_errors` で、派生の誤りを除く前に、見出し `N errors in empty disjunction` のある項目の道筋を集める。
			その項目の誤りのうち、`conflicting values` で始まるものと、そうでないもの（out of bound、mismatched types など）が両方あれば、`conflicting values` の誤りを診断にせず、残す誤りの `details.cue_related`（CUE の原文の並び）に入れる。
			残す誤りが複数あれば、最初の1件に入れる。そうでない項目の診断には、`cue_related` を足さない（今と同じ形）。項目の名前で決め打ちしないので、リポジトリの型が足した同じ形の項目にも効く。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "`CUE_INVALID` の日本語の `hint`"
		text: """
			`_shape_error` の2つの `hint` と、`_SCHEMA_STEP` を日本語にする。
			- 評価の誤り：「<ファイル> の <項目> を、仕様の型に合うように直す。誤りの原文は cue_message と positions にある。」
			- 型だけが場所を示す誤り：「Scope の CUE の文書（<Scope>/*.cue）に <項目> を書くか直して、仕様の型に合わせる。SpecDock の型（<ファイル>）は直さない（誤りの原文は cue_message にある）。」
			- `schema`：「requirement.cue に schema: \"specdock/v1\" を書く（型の版は、このファイルだけから読む）。」
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "Issue の雛形の手順の例"
		text:  "手順の例を1行の形にし、`status` を `title` と `realizes` のすぐ後に書く理由をコメントに書く。テストの例も1行の形にそろえる。目録の `sha256` を新しい中身に、`known_old_sha256` に今の中身（`08b4c2fd…`）を足す。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "警告 `SPEC_NO_TESTS`"
		text: """
			`check_scope_documents` で、評価が通り、`kind == "issue"`、保証レベルが light、`evaluation["tests"]` が空のとき、警告 `SPEC_NO_TESTS` を `warnings` に足す（説明資料の警告の前）。
			`details` は `file`（`<Scope>/plan.cue`）と日本語の `hint`。`ScopeCheckReport` の形は変えない。`cue.md` の表と、表を縛るテストのコードの集合に足す。
			"""
		satisfies: ["R-04"]
	}
	"D-05": {
		title: "デザインシステムの埋め込み"
		text: """
			`wrap_page` に `embedded: EmbeddedDesignSystem | None = None` を足す。あれば、`ds.css` を `<style>` に、`marked.umd.js` と `ds.js` を、この順に `data:text/javascript;base64,` の `<script src>` で書く（`</script>` を含む中身を、書き換えずに安全に埋め込める）。`marked` が先に読まれるので、`ds.js` は `vendor/` を読みに行かない。
			`render_scope` と `render_scope_html` に `embed_design_system: Path | None = None` を足す。あれば、そのディレクトリから3つのファイルを読み、`wrap_page` に渡す。読めなければ `CanonicalCommandError(DESIGN_SYSTEM_MISSING, exit_code=3)` で止まる。
			`scope render` の葉に `--design-system`（`file`、`inline`、既定 `file`）を足す。`inline` ならチェックアウトの `spec-dock/design-system/` を渡し、`--json` の `design_system_base` は `null`、`design_system` は `inline` を返す。
			"""
		satisfies: ["R-05", "F-01"]
	}
	"D-06": {
		title: "ガイドと参照"
		text:  "`cue.md` に `SPEC_NO_TESTS` の行と `--design-system inline` を、`reference_cli.md` の `scope render` に引数を書き、dogfood の写しと目録を直す。"
		satisfies: ["R-04", "R-05"]
	}
	"D-07": {
		title: "回帰の確かめ"
		text:  "今の回帰テストを保ち、件数が変わる `status: \"nope\"` のテストだけを、新しい件数（1件）と `cue_related` を確かめる形に書き換える（意図は強める）。"
		satisfies: ["F-02"]
	}
}

compatibility: "`CUE_INVALID` の件数が減る場合と、`hint` の言語が変わる。`details` に `cue_related` が足されることがある（足すだけ）。警告に `SPEC_NO_TESTS` が足されることがある。`scope render` の既定と `render_scope_html` の既定の出力は変わらない。"

risks: [
	"埋め込んだ HTML は約 400KB になる。既定ではないので、選んだときだけ",
	"`cue` の誤りの文の形が将来変わると、まとめが効かなくなる（そのときは今と同じ2件に戻るだけで、誤りは失われない）",
]
