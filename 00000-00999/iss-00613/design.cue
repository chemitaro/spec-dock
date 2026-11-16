package spec

// 設計（Issue）。型 specdock/v1。Epic epic-00612 の D-01、D-02 を、この Issue の粒度に下ろす。

goals: [
	"入れ子（親と段の札）は、純粋な関数1か所で決める",
	"一覧の API は項目を足すだけにし、今の項目・並び・版を変えない",
	"道をブラウザーに出さない",
]

current: """
	- `DashboardSite._refresh_listing`（`runtime/application/dashboard_site.py`）が、登録簿の行 `entries`、出すもの `served`（鍵 → `SiteRepository`、1つのクローンなら `checkout` が登録の `main_checkout`、2つなら None で `problem` が `ambiguous`）、`visibility`（隠す印と設定）を `_Listing` に覚える。署名が同じなら読み直さない。
	- `DashboardSite.repositories()` は、隠していない `served` を鍵の順に返す。
	- `DashboardHttp._repositories`（`runtime/application/dashboard_http.py`）が、それを `repository`、`host`、`owner`、`name`、`path`、`api`、`problem` の7つで返す。
	"""

target: """
	- 新しい `runtime/application/dashboard_nesting.py` の `repository_nesting` が、出すリポジトリと境界の道から、鍵ごとの `Nesting(parent, tier)` を返す。
	- `_Listing` が `nesting` を覚え、`DashboardSite.nested_repositories()` が（`SiteRepository`、`Nesting`）の組を鍵の順に返す。
	- `_repositories` が、各リポジトリの末尾に `parent` と `tier` を足す。
	"""

design: {
	"D-01": {
		title: "入れ子と段の札を決める純粋な関数"
		text: """
			`runtime/application/dashboard_nesting.py`（新しい。ファイル・ネットワーク・時刻・`os.path` の解決に触れない）：

			```python
			TIER_LABELS: Mapping[str, str] = {"businesses": "事業", "products": "プロダクト", "services": "サービス"}

			@dataclass(frozen=True)
			class Nesting:
			    parent: str | None
			    tier: tuple[str, ...]

			def repository_nesting(
			    shown: Sequence[tuple[str, str | None]], boundaries: Sequence[str]
			) -> dict[str, Nesting]: ...
			```

			- `shown`：出すリポジトリの（鍵、正規化した main のチェックアウトか None）を一覧の並びで。`boundaries`：登録簿のすべての行の、正規化した `main_checkout`（隠したもの、リポジトリの分からない行、ambiguous の各クローンを含む。重なってよい）。
			- 道は `PurePosixPath` の `parts` で比べる。絶対の道でない値（空を含む）は、`shown` では None と同じに、`boundaries` では無いものとして扱う（F-05）。
			- 「P が C を中に持つ」は、`P.parts` が `C.parts` の真の頭（`len(P.parts) < len(C.parts)` かつ頭が一致）であること。文字の頭ではない（R-01 の2つ目）。同じ道は中に持たない。
			- 親：チェックアウトが None でない `shown` のうち、子のチェックアウトを中に持つ、`parts` のいちばん長いもの（R-01）。チェックアウトが None のリポジトリは親にならず、自身の `parent` は None（F-02）。同じ長さの候補は起こらない（同じ道の2つのリポジトリなら、どちらも中に持たない）。
			- 段の札：親が None なら空。親があれば、子のチェックアウトを中に持つ境界（`boundaries` と `shown` のチェックアウト）のうち `parts` のいちばん長いもの N から子までの部分 `C.parts[len(N.parts):-1]` を、`TIER_LABELS` で写し（ないものはそのまま）、タプルにする（R-02）。N は親と同じか、親より深い（隠したもの、分からない行、ambiguous のクローン）。だから、隠したものの名前とその上の途中の名前は札に現れない（F-03）。
			- 返す辞書の鍵は `shown` の鍵のすべて。
			"""
		satisfies: ["R-01", "R-02", "F-02", "F-03", "F-05"]
	}
	"D-02": {
		title: "`DashboardSite` の一覧での計算と覚え"
		text: """
			- `_Listing` に `nesting: dict[str, Nesting]`（既定は空の辞書）を足す。
			- `_refresh_listing` で、`visibility` を決めた後に、`shown`＝鍵の順の `served` のうち `visibility[key].hidden` でないものの（鍵、`site.checkout` があり絶対なら `os.path.realpath(site.checkout)`、なければ None）と、`boundaries`＝`entries` の `main_checkout` のうち絶対の道のものの `os.path.realpath` を作り、`repository_nesting` を呼んで `_Listing` に入れる。正規化はこの時の1回だけ（署名が同じ要求では読み直さない）。
			- 新しい `nested_repositories() -> tuple[tuple[SiteRepository, Nesting], ...]` を、`repositories()` と同じ1つの鍵の内側で、同じ並び（鍵の順、隠していないもの）で返す。`repositories()` は変えない。
			- 隠す印が読めないとき（すべて隠す、fail closed）は、出すものがないので空。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-02", "F-03", "F-05"]
	}
	"D-03": {
		title: "一覧の API に `parent` と `tier` を足す"
		text: """
			`DashboardHttp._repositories` を `self.site.nested_repositories()` から組み、各リポジトリの今の7つの項目の後ろに `"parent": nesting.parent`、`"tier": list(nesting.tier)` を足す。今の項目の値、並び、`schema`、`unknown_count`、`marks_unreadable`、`server` は変えない。
			`parent` は同じ読みの `shown` の鍵だけを指すので、同じ応答の `repositories` にある（R-03 の2つ目）。道とカタログの文字列は応答に入れない。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "契約の文書と静的な資産の目録"
		text: """
			`src/spec_dock/assets/spec_dock/docs/reference_cli.md` の「ダッシュボードのサーバーの契約」の **API** の項目に、次を足す：`GET /api/v1/repositories` の各リポジトリの `parent`（出す親のリポジトリの鍵か `null`）と `tier`（段の札の配列）、決め方（登録された main のチェックアウトの道のいちばん近い出す祖先。段の札は、いちばん近い登録された行のチェックアウトから子までの途中のディレクトリの名前で、`businesses`→事業、`products`→プロダクト、`services`→サービス、ほかはそのまま。隠したものは親にならず、その中のものは外の出す祖先の子。クローンが2つのものと絶対でない道の行は最上位で親にならない）、チェックアウトとカタログの道は返さないこと。
			`src/spec_dock/assets/static-inventory.json` の `spec-dock/docs/reference_cli.md` の `sha256` を新しい内容に合わせ、今の値を `known_old_sha256` に足す（今のリポジトリの決まり。目録のテストが確かめる）。dogfood の写し `spec-dock/docs/reference_cli.md` は変えない。
			"""
		satisfies: ["R-03"]
	}
}

compatibility: """
	一覧の API は項目を2つ足すだけで、版は変えない。今の画面は未知の項目を読まないので見え方は変わらない。
	PR を戻すと `parent`・`tier` がなくなり、今の応答に戻る。
	"""

risks: [
	"大文字と小文字を区別しないファイルシステムで、登録の道の大文字が違うと、親子を見落としうる。realpath で揃え、それでも違うものは最上位に並ぶ（表示が平らになるだけで、誤った親にはならない）",
	"登録の後にチェックアウトが消えても、realpath は道を返す（ある部分だけ解決する）。入れ子は登録の道で決まるので、表示は登録どおり",
]
