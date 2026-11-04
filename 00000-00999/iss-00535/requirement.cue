package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "CUE と Markdown の文書、報告、ADR を描き、資料と同じ切り離しで配る。誤ると文書のスクリプトが画面に触れるおそれがあるが、書き込みはなく、版を戻せば回復できる。"
}

purpose: "ダッシュボードの Scope の詳しい画面で、要件・設計・計画・報告・ADR を、その場で描いて読めるようにし、CUE の Issue の計画の進み具合を示す（epic-00427 の段階2、D-11）。あわせて、前面の `serve` が古い版で動き続けているとき、上の帯で起動し直しを促す（#530 の残り）。"

background: "0.6.0 の詳しい画面の「文書」のタブは、文書があるかどうかと説明資料へのリンクだけを示し、ほかは「文書の画面は 0.7.0」と書いていた。描画の入口（`render_scope_html`、`spec-dock scope render`、epic-00425 の K5）とデザインシステムは既にあり、サーバーは `/ds/` と `/vendor/` を配っている。#530 は API の `server.restart_required` を出したが、画面はまだそれを示さない。"

includes: [
	"CUE の Scope の要件・設計・計画を、その場で描いたページとして配り、詳しい画面の中で読ませる（Epic R-19）",
	"`scope check` の誤りと警告、描画の失敗の理由と次の1手を詳しい画面に示す（Epic R-19、F-10）",
	"Markdown の Scope の `requirement.md`・`design.md`・`plan.md`、どの Scope の `report.md` と ADR も、デザインシステムの薄いページに包んで読ませる（Epic R-25）",
	"CUE の Scope の `plan.cue` の手順の進み具合を、詳しい画面に帯と数で示す（Epic R-26）",
	"API の `server.restart_required` が true のとき、上の帯で前面の `serve` の起動し直しを促す（#530 の残り）",
]

excludes: [
	"構造の図とボードの補足の1行への進み具合の表示（Epic R-26 の「示せる」。構造の API で全 Scope の `cue` を動かすことになるので、この Issue では入れない）",
	"Artifact の Markdown のうち ADR でないものの描画（今のとおり、資料として新しいタブで開く）",
	"版の番号と `migration.md` の変更（0.7.0 のリリースの #536 が行う）",
]

requirements: {
	"R-01": {
		title: "CUE の Scope の要件・設計・計画を、正本の CUE からその場で描いて、詳しい画面の中で読める"
		text:  "サーバーは `GET /r/<host>/<owner>/<name>/scopes/<ID>/doc` で、カタログの Scope のディレクトリの3つの CUE のファイルを、`render_scope_html` と同じ描画で HTML にして返す。デザインシステムは `/ds/`、図の部品は `/vendor/` から読むので、インターネットにつながらなくても描ける。前もって作ったファイルは使わない。詳しい画面の「文書」のタブは、そのページを枠の中に示し、新しいタブでも開ける。説明資料（`explanation.html`）へのリンクは今のとおり示す。（Epic R-19）"
		acceptance: [
			"見本の CUE の Scope の詳しい画面の「文書」のタブに、その場で描いた要件・設計・計画のページが枠の中に出て、`explanation.html` へのリンクがある",
			"そのページの応答は、`/ds/` と `/vendor/` のほかに外の場所を読まない（HTML に `https://` の読み込みがなく、`ds-vendor-base` が `/vendor/`）",
		]
	}
	"R-02": {
		title: "CUE の Scope の検査の結果（誤りと警告）を、詳しい画面に示す"
		text:  "Scope の API の `details.check` に、`scope check` と同じ検査（`check_scope_documents`）の結果（`status`、誤りと警告のコード・文・ファイル、次の1手）を持たせ、「文書」のタブに数と一覧で示す。誤りがなければ、そのことを示す。（Epic R-19）"
		acceptance: ["誤り（つながりの指摘など）と警告（説明資料が雛形のまま）のある見本の Scope で、詳しい画面にその数とコードが出る。誤りのない Scope では「誤りなし」が出る"]
	}
	"R-03": {
		title: "Markdown の文書（Markdown の Scope の要件・設計・計画、報告、ADR）を、画面の中で読めるように描く"
		text:  "サーバーは `GET /r/<host>/<owner>/<name>/scopes/<ID>/doc/<道>` で、Markdown の Scope の `requirement.md`、`design.md`、`plan.md`、どの Scope の `report.md`、`artifacts/` と `discussions/` の ADR（名前に `adr-` を含む `.md`）を、`wrap_page` のデザインシステムの薄いページに包んで返す。ほかの道は断る。「文書」のタブは、選んだ文書を枠の中に示す。（Epic R-25）"
		acceptance: ["見本の Markdown の Scope で要件・設計・計画が、CUE の Scope でも報告と ADR が、「文書」のタブの枠の中で読める。インターネットにつながらなくても描ける"]
	}
	"R-04": {
		title: "CUE の Scope の計画の進み具合を示す"
		text:  "CUE の Scope の評価の `steps` の `status`（todo、doing、done、dropped）を数え、Scope の API の `details.progress` に、`dropped` を除いた全体の数、終わった数、作業中と未着手の数、作業中の手順（番号と題名）を持たせる。詳しい画面の「概要」と「文書」のタブに、帯と数で示す。手順がない、または評価が通らないときは示さない。（Epic R-26）"
		acceptance: ["見本の `plan.cue`（todo、doing、done、dropped を含む）で、詳しい画面の計画の進み具合の数（終わった／全体、作業中の手順）が正しく出る"]
	}
	"R-05": {
		title: "前面の `serve` が古い版で動いているとき、上の帯で起動し直しを促す"
		text:  "画面は `/api/v1/repositories` を開いたときと60秒ごとに読み、`server.restart_required` が true なら、知らせの帯に「SpecDock が `<installed_version>` に更新された。前面の `serve` を起動し直すと新しい版になる」と次の1手（`spec-dock dashboard serve`）を示す。横断の概況とリポジトリの画面のどちらにも出す。（#530 の残り、Epic R-28）"
		acceptance: ["`restart_required: true` を返すサーバーで、横断の概況とリポジトリの画面の上の帯に、起動し直しの知らせと入っている版が出る。false なら出ない"]
	}
}

failures: {
	"F-01": {
		title: "CUE の Scope の描画に失敗する（評価の誤り、`cue` がない、時間切れ）"
		text:  "その Scope の「文書」のタブに、検査の結果と次の1手（`cue` を入れる、`spec-dock scope check <ID>`）を示し、ほかの表示（概要、依存、配下、Artifact、ほかの Scope）は続ける。評価の誤りのときは、描画の入口が検査の結果だけのページを返す。`cue` がないか時間切れのときは、そのことと次の1手だけを載せた薄いページを返す。（Epic F-10）"
		impact: "文書が読めないが、構造の表示は変わらない"
		recovery: "`cue` v0.17.1 以上を入れるか、`spec-dock scope check <ID>` の示すとおりに直すと、次の要求で描ける"
	}
	"F-02": {
		title: "文書のスクリプトや Markdown の中身が、画面と API に触れない"
		text:  "文書の応答は、資料と同じ `Content-Security-Policy: sandbox allow-scripts allow-popups; frame-ancestors <埋め込みの許可>` を持ち（`allow-same-origin` なし）、画面の枠も同じ `sandbox` の属性を持つ。リンク、ディレクトリ、決まった名前でないファイルは、データを含まない 404 で、`..` や空の道の区切りは共通の道の分解が 400 で断る。"
		impact: "誤ると、文書に書かれたスクリプトが画面や API を読めるおそれがある"
		recovery: "版を戻す。書き込みはないので、データは壊れない"
	}
	"F-03": {
		title: "カタログがない、2つある、Scope のディレクトリがない、文書がない"
		text:  "文書の道は、資料と同じ扱い（あいまいなら 409、ほかは 404）で断る。詳しい画面は、今のとおりカタログの問題と次の1手を示す。"
	}
}

constraints: [
	"ダッシュボードは何も書かない（キャッシュはサーバーのメモリの中だけ）。GitHub に要求を送らない",
	"`cue` はリポジトリの型（`spec-dock/cue/`）を、登録簿の main のチェックアウトから読む。分からなければリポジトリの型なしで描く",
	"画面の JSON（`scopes/<ID>`）は契約にしない（reference_cli.md）。文書の道は画面の道として文書に書く",
]

decisions: [
	"2026-11-04（実装の担当の判断）：CUE の Scope の検査と描画の結果は、Scope ごとに、3つの CUE のファイルと説明資料とリポジトリの型の時刻と大きさで覚え、Scope の API と文書の道で共有する（D-11 の「3つの CUE のファイルの時刻で結果を覚えておく」に、描画に効くほかのファイルを足した）",
	"2026-11-04（実装の担当の判断）：ADR は、Artifact の決まり（`adr` の型の名前）に合わせ、`artifacts/` と `discussions/` の直下の、名前に `adr-` を含む `.md` とする。題名に `adr-` を含むほかの Artifact も拾うことがあるが、読むだけで害はないので受け入れる（仕様のレビュー P3）",
]
