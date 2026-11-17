package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"知らせの振り分けを、DOM のない純粋な部品にして node で確かめる",
	"知らせの文は今の `overviewWarnings` の1か所のままにし、種類（kind）と値（detail）を足すだけにする",
	"compose.js（枠の配置）は変えず、入力の warns・alerts を枠に残る知らせだけで数える",
]

current: """
	- `_shared/logic.js` の `overviewWarnings(structure, failure)` は `[{level, text, next}]` を返す。種類は文でしか分からない。
	- allgraph.js：`r.warnings = overviewWarnings(...)`。`sizes()` が `warns = r.warnings.length`、`alerts = level が info でない数` を compose に渡し、
	  `frameHtml` が `warnHtml(r.warnings)` を枠の見出しの下（`.ax-warn`、1行 24px）に描く。
	- 上の帯は `.gx-bar` > `.gx-left` > `.gx-next`（状態のチップ）と `.gx-tools`。最初の表示の上端は `barBottom()`（`.gx-next` と PC の `.gx-tools` の下端）+ 8。
	"""

target: """
	- `overviewWarnings` の各知らせに `kind`（と種類ごとの `detail`）が付く。
	- 新しい `views/allgraph/notices.js` の `splitNotices` が、知らせを上のまとめの行と、枠に残る知らせに分ける。
	- allgraph.js は枠に残る知らせだけを `warnHtml` と `sizes()` に使い、まとめの行を `.gx-left` の `.ax-sum` に描き、`barBottom()` がそれを含む。
	"""

design: {
	"D-01": {
		title: "知らせの種類と値（_shared/logic.js）"
		text: """
			`overviewWarnings` の返す各知らせに `kind` を足す（文・level・next と並びは変えない）。

			| kind | 今の文 | detail |
			|---|---|---|
			| `failure` | このリポジトリを読めませんでした（…）。 | なし |
			| `snapshot-missing` | 構造のスナップショットがありません。 | なし |
			| `snapshot-unsupported` | 構造のスナップショットが知らない版です。… | なし |
			| `snapshot-unreadable` | 構造のスナップショットが読めません（…）。 | `agoText(age)`（なければなし） |
			| `stale` | N前から更新されていません（…）。 | `agoText(age)`（なければなし） |
			| `anomalies` | 構造の異常が N件あります。 | `N件` |
			| `pr-unknown` | PR の状態が分かりません。 | なし |
			| `ambiguous` | REPOSITORY_AMBIGUOUS の文 | なし |
			"""
		satisfies: ["R-01", "R-02", "R-05"]
	}
	"D-02": {
		title: "知らせの振り分け（新しい views/allgraph/notices.js、純粋）"
		text: """
			```js
			/** The kinds the page's summary takes (the rest stay in their frame), in the summary's order within a level. */
			export const SHARED = { "snapshot-missing": "構造のスナップショットがありません", "snapshot-unsupported": "構造のスナップショットが知らない版です（SpecDock を更新してください）",
			  "snapshot-unreadable": "構造のスナップショットが読めません", stale: "構造が更新されていません", anomalies: "構造の異常があります", "pr-unknown": "PR の状態が分かりません" };
			/**
			 * @param repos   [{repository, owner, name, failed, warnings}] in the list's order (warnings: overviewWarnings' result, or null while loading;
			 *                failed: the screen cannot draw its graph, so every warning is its reason and stays in its frame)
			 * @returns {summary: [{kind, level, text, next, repos: [{repository, label, detail}]}], own: Map(repository → warnings kept in its frame)}
			 */
			export function splitNotices(repos)
			```

			- failed のリポジトリは、知らせのすべてを own へ（まとめに出ない）。ほかのリポジトリでは、種類が SHARED にある知らせはまとめへ、ほか（failure、ambiguous、kind のない知らせ）は own へ。warnings が null のリポジトリは数えない（F-01）。
			- まとめの行は種類ごとに1つ。`text` は SHARED の見出し、`level` は種類の最初の知らせの level、`next` は最初に出た知らせの next（同じ種類は同じ next）。
			- `repos` は一覧の順。`label` は name（なければ repository）。同じ name の別の repository が一覧（読み込み中を含む）にあれば `owner/name`。`detail` は知らせの detail。
			- 行の順：level（error、warning、info）の順、同じ level では SHARED の順。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-03": {
		title: "まとめの行を描き、枠には残る知らせだけを使う（allgraph.js・allgraph.css）"
		text: """
			- mount：`.gx-left` の `.gx-next` の後に `<ul class="ax-sum" hidden></ul>` を置き、`A.el.sum` にする。
			- `notices()`：`splitNotices(items().map(it => ({...it, failed: R.get(key)?.status === "failed", warnings: !R.get(key) || R.get(key).status === "loading" ? null : R.get(key).warnings})))`。
			- `sizes()` の warns・alerts は `own.get(key)` で数える。`frameHtml` の `warnHtml` も `own.get(key)`。
			- `renderSum(summary)`（`renderBar` から呼ぶ）：各行 `<li data-level data-kind title="全文">印 <span class="ax-text"><b>見出し</b>：名前（detail）、…<span class="ax-next">次の1手：<code>…</code></span></span></li>`。
			  全文の title は「見出し：名前（detail）、… 次の1手：…」。summary が空なら hidden。
			- `barBottom()` は `.gx-next` に続けて `.ax-sum`（hidden でないとき）の下端も見る（R-03）。
			- allgraph.css：`.gx .ax-sum` は 0 余白・list なし・縦に並べる（flex column、gap 4px、align-items flex-start）・`pointer-events: none`（`.gx-bar > *` の auto を打ち消す。行の外ではドラッグ・拡大が図に届く）。
			  `li` は `pointer-events: auto`（title を見る）・`width: fit-content`・`max-width: 100%` で、`.ax-warn li` と同じ1行の作り（高さ 24px、nowrap、省略、12px、level の色）に、背景 `var(--ds-surface)`・縁 `1px solid var(--ds-border)`・角 `var(--ds-radius)` を足す（新しい色なし）。
			  スマホ（.gx-left が absolute の幅）でも同じ1行ずつの省略。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01"]
	}
	"D-04": {
		title: "実機の確かめ"
		text: """
			隔離した venv（この worktree の wheel）と一時の状態の置き場（この PC の状態の置き場の写し）、別のポートで `dashboard serve --offline --tailscale`。
			稼働の印は、iss-00627 と同じく `XDG_CONFIG_HOME` の試しの設定（`orca_web.port` を別のポート）と、試しの orca の中継（iss-00614 の relay_orca.py の写し：GET だけで常駐の orca-web を中継し CORS の頭を足す）で出す。
			測りは、各リポジトリの枠に稼働の印（`.orca-mark`）が描かれ、数が2回続けて同じになってから行い、印の数を表に残す（印が0の組は、その旨を書く）。
			headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で、R-04 の18組の edgeAudit・縮めた枠のはみ出し、まとめの行の数と枠の知らせの行の数、
			1440・390 × 明暗の写し（直す前と後）を report.md に残す。
			"""
		satisfies: ["R-03", "R-04"]
	}
}

compatibility: "API・保存・モデルは変わらない。overviewWarnings の項目を足すだけで、ほかの画面の表示は同じ。"

risks: [
	"まとめの行が増えると上の帯が高くなり、スマホでは図の見える高さが減る（種類は最大6、ふつうは1〜2行）",
]
