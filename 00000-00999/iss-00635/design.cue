package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"入れ子はチェックアウトのパスの包含だけで決め、ディレクトリの名前を読まない",
	"消すだけの変更にとどめ、入れ子の親の値と、ほかの API の項目と画面は変えない",
]

current: """
	- `runtime/application/dashboard_nesting.py`：`TIER_LABELS`、`Nesting(parent, tier)`、`repository_nesting(shown, boundaries)`。`boundaries`（登録簿のすべての行のチェックアウト）は、段の札の起点（いちばん近い境界）を決めるためだけに使う。
	- `dashboard_site.py`：`_listing_nesting(entries, served, visibility)` が `boundaries` を作って渡す。`nested_repositories()` が `(SiteRepository, Nesting)` の組を返す。
	- `dashboard_http.py`：`_repositories` が `parent` と `tier` を出す。
	- `views/allgraph.js`：`headHtml` が `it.tier` を `sd-badge` で描く。`allgraph.css`：`.ax-tier` と `.ax-tier .sd-badge`。
	- `docs/reference_cli.md`（配る側と dogfood）：`tier` と段の札の決め方。
	"""

target: """
	- `repository_nesting(shown)` が鍵 → 親の鍵か None の辞書を返す。`TIER_LABELS`、`Nesting`、`boundaries` はない。
	- 一覧の API の各リポジトリは `parent` で終わる。画面の見出しは名前とリンクだけ。文書は `parent` だけを書く。
	"""

design: {
	"D-01": {
		title: "入れ子の純粋な関数を、親だけを返す形にする"
		text: """
			`dashboard_nesting.py`：`TIER_LABELS`、`Nesting`、`_Parts` の札のための計算（`walls`、`between`）を消し、`repository_nesting(shown: Sequence[tuple[str, str | None]]) -> dict[str, str | None]` にする。
			親の決め方は今と同じ：子のチェックアウトを、部分で比べて真に含む、出すリポジトリのチェックアウトのうち、いちばん長いもの（同じ長さなら先に出したもの）。子か親のチェックアウトがない（None、空、絶対でない）ものは親にならず、親を持たない。
			モジュールの文書の文を「入れ子（親）」に直す。
			`dashboard_site.py`：`_Listing.nesting` を `dict[str, str | None]`（親）にし、`_listing_nesting` は `boundaries` を作らず `repository_nesting(shown)` を呼ぶ。`nested_repositories()` は `(SiteRepository, 親の鍵か None)` の組を返す（名前はそのまま、文書の文から tier を消す）。`entries` の引数は `boundaries` のためだけなので外し、呼ぶ側（`_refresh_listing` の中）も合わせる。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "一覧の API から `tier` を消す"
		text: "`dashboard_http.py` の `_repositories` から `\"tier\": ...` の行を消し、`\"parent\": parent` にする。ほかの項目と並びは変えない。"
		satisfies: ["R-01"]
	}
	"D-03": {
		title: "横断の構造の見出しから札を消す"
		text: """
			`views/allgraph.js` の `headHtml`：`tier` の変数と `ax-tier` の span を消す（入力の `it.tier` は読まない）。先頭のコメントの「the frames nested as the company is (company-os → business → product …; the list API's parent and tier)」を、チェックアウトのパスの入れ子（the list API's parent）の一般の言い方にする。
			`views/allgraph/compose.js` の先頭のコメントの同じ言い方も直す。`views/index.js` のコメントの「with parent and tier」を「with parent」にする。
			`allgraph.css`：`.gx .ax-tier` と `.gx .ax-tier .sd-badge` の規則と、その前のコメントを消す。`REPO.headW` と `.ax-head` の寸法は変えない（requirement の decisions）。
			"""
		satisfies: ["R-02", "F-01"]
	}
	"D-04": {
		title: "契約の文書と目録"
		text: """
			配る側 `src/spec_dock/assets/spec_dock/docs/reference_cli.md` の API の行を、`…の後ろに、入れ子の親\\`parent\\`（…）があります。親は、…いちばん近い出すリポジトリです。隠したリポジトリは親にならず、…（なければ最上位）になります。クローンが2つのものと、\\`main_checkout\\`が絶対の道でない行のリポジトリは、最上位になり、親にもなりません。チェックアウトとカタログの道は返しません。` にする（段の札の文と「で札が空」を消す。親の文は今の言い方を保つ）。その後ろに「0.9.5 だけで配った`tier`は、使う者がなく、0.9.6 で消しました（版の規則の例外）。」の1文を足す。冒頭の版の規則の文は変えない。
			`static-inventory.json` の `spec-dock/docs/reference_cli.md` の `sha256` を新しい値にし、今の値 `bd8b72aff0b0…` を `known_old_sha256` の最後に足す。dogfood の写し `spec-dock/docs/reference_cli.md` に同じバイトを写す。
			"""
		satisfies: ["R-03"]
	}
	"D-05": {
		title: "テストの更新"
		text: """
			- `tests/unit/application/test_dashboard_nesting.py`：`TIER_LABELS` と札の値の確かめを消し、親の確かめ（この PC の形、名前の頭が同じだけのもの、同じ道、隠したもの、クローンが2つのもの、絶対でない道）を新しい戻り値で残す。名前に依らないことの確かめ（`businesses/x/products/y` と `groups/x/team/y` で同じ形の親）を足す。
			- `tests/unit/application/test_dashboard_repositories_nesting.py`：項目の並びを `[*FIELDS, "parent"]` にし、`tier` がないことを確かめる。親の値の確かめは残す。
			- `tests/unit/presentation/test_dashboard_allgraph_screen.py`：札の確かめ（`["プロダクト", "groups"]`）を、`tier` を持つ入力でも見出しに `sd-badge`・`ax-tier` がなく名前とリンクがある確かめに替える。FQG-001 の `.ax-tier .sd-badge` の規則のテストは、`allgraph.css` に `ax-tier` がなく、`allgraph.js` に `ax-tier` と語 `tier` がない確かめに替える。入力の合成から `tier` を外すかどうかは、F-01 を確かめる1つを除いて外す。
			- `tests/unit/presentation/test_dashboard_allgraph_compose.py`：入力の `tier` を外す（compose は読まない）。
			- `tests/unit/infra/test_issue613_repository_nesting_docs.py`：`tier` の記述があることの確かめを、段の札の記述がないことと、`parent` の記述と版の規則の例外の1文があることの確かめに替え、dogfood の写しが同じバイトであることを確かめる（名前は変えず、文書の文をこの Issue に合わせる）。
			- `src/spec_dock/runtime/` に読み替えの語がないことの静的な確かめ（R-01 の4つ目）を足す。
			- `tests/integration/test_issue623_release_0_9_5.py`：0.9.5 の migration.md の節は残すので変えない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01"]
	}
	"D-06": {
		title: "環境に特化した決まりの調べ"
		text: """
			`rg -i` で `company`・`business`・`product`・`service`・`事業`・`プロダクト`・`サービス`・`会社`・本人のリポジトリの名前（`housing`・`input-devices`・`yubisaki`・`taikyo`・`orca-web`）を `src/spec_dock`（vendor を除く）で探し、分岐・読み替え・例を分けて report.md の表にする。2026-11-17 の下調べで見つかったもの：`TIER_LABELS`（外す、D-01）、`allgraph.js`・`compose.js` のコメントの company-os の言い方（直す、D-03）、`docs/canonical.md` の設定の例のパス（例なので残し、後続の候補にする）、`orca_web` の設定の節（orca-web との連携の機能の名前で、ディレクトリの名前の決まりではないので残す）、英語の business の一般の語（関係ない）。
			"""
		satisfies: ["R-04"]
	}
}

compatibility: """
	一覧の API から `tier` がなくなる（0.9.5 で足した項目）。契約の版は `specdock.dashboard/v1` のままにし、版の規則の例外として reference_cli.md に1文で明記する（requirement の decisions、統括 2026-11-17）。SpecDock の画面は同じパッケージで配るので組み合わせの問題はない。外の利用者 orca-web は `tier` を読んでいない（requirement の background）。移行の記録は 0.9.6 の版上げの Issue（iss-00634）が migration.md の新しい節に書く。
	"""

risks: [
	"`tier` を読む外の利用者がいれば、項目がなくなる。今の唯一の外の利用者 orca-web は読んでいないことを確かめた。",
]
