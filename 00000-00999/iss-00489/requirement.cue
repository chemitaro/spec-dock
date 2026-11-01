package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
assurance: {
	level:  "standard"
	reason: "scope check の誤りの表示、配布する CUE の雛形、scope render の引数を変える。利用者の見る出力と配布資産の変更で、ほかのリポジトリにも届くが、データは書き換えず、PR と版を戻せば元に戻る。"
}

purpose: "CUE の仕様を書く人が、`scope check` の誤りから直し方をすぐ読み取れ、`scope render` の HTML を別の PC に渡しても読めるようにする。"

background: """
	epic-00425 の I-7（iss-00487）で、初めて CUE の仕様で Issue を回した。その試しの `report.md` の「改善の提案（優先度つき）」の5つを実装する。

	1. （高）`plan.cue` の `status: "doin"` で、`CUE_INVALID` が2件出る。1件目は既定値 `todo` との「conflicting values」で紛らわしく、2件目の「out of bound」が本当の手がかり。
	2. （中）`SPEC_FINDINGS` の `hint` は日本語だが、`CUE_INVALID` の `hint` だけ英語。
	3. （中）雛形の手順の例で、`status` を `title` と `realizes` のすぐ後に書く並びを示す。
	4. （低）light では、テストが1つもなくても何も言われない。
	5. （低）`scope render` の HTML は、デザインシステムを `file://` の絶対の道筋で読むので、別の PC ではスタイルが外れる。
	"""

includes: [
	"`scope check` の `CUE_INVALID` の組み立て（`src/spec_dock/runtime/application/scope_check.py`）",
	"配布する CUE の雛形 `templates/cue/issue/plan.cue` と dogfood の写し、`static-inventory.json`",
	"`scope render` の引数と、描画の入口（契約 K5）への既定値つきのキーワード引数",
	"`cue.md`、`reference_cli.md` の該当の記述と、その dogfood の写し、目録のハッシュ",
]

excludes: [
	"型（`specdock/v1`）の変更",
	"`.md` の雛形（`spec-dock/templates/<種類>/`）の変更（epic-00424 の I-13）",
	"#487 の FQG-001（`-yy`）",
	"`CUE_INVALID` 以外のコード（`EXPLANATION_*`、`SCOPE_DOCUMENT_MISSING` など）の `hint` の言語",
	"`cue` が出す誤りの文そのもの（`cue_message`、`message` の中の CUE の原文）",
]

requirements: {
	"R-01": {
		title: "既定値のある列挙の誤りが、許す値を示す1件の `CUE_INVALID` にまとまる"
		text: """
			1つの項目の選言（`*既定値 | 制約`）がすべて外れたとき、同じ項目についての「conflicting values」（既定値などの値との衝突）の行を、ほかの理由の行（out of bound など）にまとめ、診断を1件にする。
			まとめた行は失わず、その診断の `details.cue_related` に CUE の原文のまま残す。`cue_output` も今のまま全文を持つ。
			`status` に限らず、同じ形のどの項目にも効く（項目の名前で決め打ちしない）。選言の枝がすべて「conflicting values」のとき（制約のない列挙）は、今のまま。
			"""
		acceptance: [
			"`plan.cue` の手順に `status: \"doin\"` と書くと、`CUE_INVALID` がちょうど1件で、その `cue_message` が out of bound を含み、`details.cue_related` に `conflicting values \"todo\" and \"doin\"` がある",
			"リポジトリの型が足した、`*\"a\" | (string & =~\"^(a|b)$\")` の形のほかの項目でも、同じく1件になる",
			"選言でない項目の誤り（必須の項目がない など）の件数と中身は変わらない",
		]
	}
	"R-02": {
		title: "`CUE_INVALID` の `hint` が日本語で、直す項目とファイルを名指す"
		text:  "評価の誤り、型だけが場所を示す誤り（Scope の文書に書く）、`schema` の誤り（`requirement.cue` に書く）の3つの `hint` を日本語にする。`message` と `cue_message` は変えない。"
		acceptance: [
			"どの `CUE_INVALID` の `hint` にも、ひらがなかカタカナがあり、英語の文（`Fix `、`Write `、`do not edit` など）がない",
			"型だけが場所を示す誤りの `hint` が、項目の道筋と Scope の文書を名指し、型を直さないことを日本語で書く",
		]
	}
	"R-03": {
		title: "Issue の雛形 `plan.cue` の手順の例が、1手順1行で `title`、`realizes`、`status` の順に書く形を示す"
		text: """
			配布する雛形 `src/spec_dock/assets/spec_dock/templates/cue/issue/plan.cue` の手順の例を、`"S-01": {title: "…", realizes: ["R-01"], status: "todo", after: [...], session: "…"}` の1行の形にし、`status` を `title` と `realizes` のすぐ後に書く理由（一括で書き換えやすく、同じ手順に `status` が2つ入る誤りを防ぐ）をコメントに書く。
			dogfood の写し `spec-dock/templates/cue/issue/plan.cue` と、`static-inventory.json` の `sha256` と `known_old_sha256`（今の中身）を同じ変更で直す。
			Epic と Initiative の計画は手順（`steps`）と `status` を持たない（型が `slices` だけを許す）ので、変えない。
			"""
		acceptance: [
			"配布する雛形の手順の例の行で、`title:`、`realizes:`、`status:` がこの順に並ぶ",
			"雛形から作った Scope の `plan.cue` で、例のコメントを外すと `scope check` が誤りなく通る",
			"dogfood の写しが配布する雛形とバイトで一致し、目録の `sha256` が合い、`known_old_sha256` に今の版のハッシュがある",
			"今の版の雛形を持つ利用側で `installation update` を実行すると、新しい版に置き換わる",
		]
	}
	"R-04": {
		title: "light の Issue でテストが1つもないとき、`scope check` が警告で知らせる"
		text: """
			警告のコード `SPEC_NO_TESTS` を足す。検査の結果の形（契約 K3：誤りと警告）は変えず、今の警告の並びに1件足すだけにする。警告だけなら検査は成功のまま。
			出す条件は、Issue で、評価が通り、保証レベルが light で、`tests` が空のとき。standard 以上では規則 `requirement-without-test` が誤りとして示すので、出さない。
			"""
		acceptance: [
			"light の Issue で `tests` が空なら、`scope check` が成功し、警告に `SPEC_NO_TESTS` が1件ある",
			"light でテストが1つでもあるとき、standard 以上のとき、Epic と Initiative のときは、`SPEC_NO_TESTS` が出ない",
			"`cue.md` の結果のコードの表に `SPEC_NO_TESTS` の行がある",
		]
	}
	"R-05": {
		title: "`scope render --design-system inline` で、デザインシステムを埋め込んだ、別の PC でも崩れない HTML を出せる"
		text: """
			`scope render` に `--design-system <file|inline>` を足す。既定は `file` で、今のまま（そのチェックアウトの `spec-dock/design-system/` の `file:` の URL）。
			`inline` は、`ds.css`、`ds.js`、`vendor/marked.umd.js` を HTML の中に埋め込み、外のファイルの道筋を持たない。図の部品は今のまま CDN から読む。
			描画の入口 `render_scope_html`（契約 K5）は、既定値つきのキーワード引数 `embed_design_system: Path | None = None` を足すだけにし、今の引数の意味を変えない。
			"""
		acceptance: [
			"引数なしの `scope render` と、新しい引数を渡さない `render_scope_html` の HTML が、今と同じ",
			"`--design-system inline` の HTML が、`file:` の道筋と `ds.css`/`ds.js` へのリンクを持たず、3つのファイルの中身を持つ",
			"埋め込んだ HTML を、デザインシステムのない場所に置いてブラウザーで開くと、本文が描かれる",
		]
	}
}

failures: {
	"F-01": {
		title: "`--design-system inline` で、チェックアウトにデザインシステムがなければ、HTML を出さずに止まる"
		text:  "埋め込めないのに崩れた HTML を出さない。`DESIGN_SYSTEM_MISSING` を誤りとして、終了コード3で止まり、`spec-dock installation update` を示す。`file` の既定は今のまま警告で続ける。"
	}
	"F-02": {
		title: "Markdown の Scope と、今の検査と描画の回帰を壊さない"
		text:  "今の回帰テストを、意図を弱める形で変えない。`make lint` と `uv run pytest`（全体）が通る。"
	}
}

constraints: [
	"契約 K3（検査の結果の形）と K5（描画の入口）を変えない。K5 には既定値つきのキーワード引数を足すだけ",
	"テストは外のネットワークを使わない",
]

decisions: [
	"提案3の「3つの種類すべて」は、Epic と Initiative の計画に手順と `status` がない（型が許さない）ので、Issue の雛形だけを変える",
	"提案4は、K3 の形を変えない警告（`SPEC_NO_TESTS`）で実装する",
	"提案5は、埋め込み（`inline`）だけを足す。標準出力に出すので、出力の場所からの相対の道筋は決められない",
]
