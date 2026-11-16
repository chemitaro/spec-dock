package spec

// 計画（Issue）。型 specdock/v1。

goal: "`/graph` に、表示しているすべてのリポジトリの構造の図を会社の入れ子のリポジトリの枠で1枚に描く『横断の構造』を足す（既定は『これから』）。構造の図の見え方は変えない"

steps: {
	"S-01": {title: "compose.js（D-03）の node のテスト（T-01・T-02。この PC の登録の形の合成の9つ、名前だけの入力、next の出し入れ、帯、F-03）を先に書いて落ちることを確かめ、compose.js を書いて通す", realizes: ["R-03", "R-04", "R-05", "F-03"], status: "todo", session: "impl-sol"}
	"S-02": {title: "D-01（parseRoute・allGraphPath・ALL_TABS・VIEWS の口・title・interceptLinks・サーバーの _get・reference_cli.md）のテスト（T-03）を先に書いて落ちることを確かめ、実装して通す。VIEWS の allgraph は、S-04 まで最小の画面（空の render と dispose）でよい", realizes: ["R-01"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "開始のコミット 7f7dd2b1d の graph.js で偽の DOM の HTML の写し（T-04）を作ってテストの資料に残し、D-02 の draw.js を取り出し、写しとの一致と、調べる場所を移したソースの文字列のテストと、構造の図の既存のテストを通す", realizes: ["R-02"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "allgraph.js・allgraph.css（D-04〜D-07）を、偽の DOM のテスト（T-05〜T-07）を先に書いて落ちることを確かめてから書き、通す", realizes: ["R-03", "R-05", "R-06", "R-07", "R-08", "F-01", "F-02"], status: "todo", after: ["S-03"], session: "impl-claude"}
	"S-05": {title: "static-inventory.json の sha256 を直し（変われば）、make lint と全体の uv run pytest を通す", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-04"], session: "impl-claude"}
	"S-06": {title: "D-07 の実機の写し（T-08）を取り、report.md に残し、本人が見る試しの URL を tailnet で立てる", realizes: ["R-03", "R-05", "R-06", "R-07"], status: "todo", after: ["S-05"], session: "owner"}
}

tests: {
	"T-01": {title: "compose の入れ子：この PC の登録の形の合成の9つ（company-os・housing-lifecycle・taikyohiyou_project・input-devices・generic-mona・tenting-cradle・yubisaki・spec-dock・orca-web、parent と tier は iss-00613 の形）で、親の枠が子の枠を幾何で含み、spec-dock と orca-web が company-os の外、子が親の body と兄弟と重ならず body の下、最上位と棚が幅で折り返し、出力の order が深さ優先で親が先、bodyWidth の式と下限、parent が一覧にない・循環のときは最上位で一度だけ（F-03）", verifies: ["R-03", "F-03"]}
	"T-02": {title: "compose の出し入れと帯：next で shown 0・warns 0・子なしは出さず、見える子を持つ親は、中身が高さ0（body.kind は Scope 0 なら empty、Scope があれば quiet）の入れ物として出し、孫だけが見えるときも祖先を出す。loading・failed・alerts のある ok は出し、info の警告（warns だけ）では出さない。all・now ではすべて出し、Scope 0 は kind empty、Scope があり shown 0 は kind quiet（REPO.line）。棚は bodyWidth で折り返し、入れ物の親（body の高さ0）の子も横に並ぶ。bands を渡さないときと全部0のときの出力が同じ、ある枠に h を渡すとその枠の band の四角と body の y と枠の高さが h 増え、重なりがないまま", verifies: ["R-04", "R-05"]}
	"T-03": {title: "道とタブ：parseRoute の /graph・/graph?embed=1・/graph/x（今どおり overview）、ALL_TABS の3つの順と embed の href、/r/… の TABS が4つのまま、title() の『横断の構造 · すべてのリポジトリ · SpecDock』（app.js のソースの検査でよい）、interceptLinks が /graph を殻の道とする、HTTP の GET /graph と /graph/ が殻の 200、/graph/x が 404、reference_cli.md の画面の道に /graph と /todos", verifies: ["R-01"]}
	"T-04": {title: "構造の図の見え方：開始のコミットの graph.js の偽の DOM の HTML の写し（入れ子・木 × 全体・いま・これから、focus、片付けの候補、選びと path、状態の札、稼働の印の行の寸法）と、取り出した後の graph.js の HTML が同じ。調べる場所を draw.js に移したソースの文字列のテストの文字列と数が開始のコミットと同じ。graph の node の配置・線・範囲・道具の帯のテストが変えずに通る", verifies: ["R-02"]}
	"T-05": {title: "偽の DOM の allgraph：合成の9つのリポジトリ（stub の api）で、既定が next、範囲の切り替えが specdock.allgraph.v1 にだけ書く（specdock.graph.v3 は変わらない、壊れた値で next、保存した all を新しい描画で読み戻す）、ax-repo の並びと data-depth、見出しの owner/name と段の札（›）、next で見えないリポジトリの枠がなく入れ物の親があり、all・now ですべての枠、1つのリポジトリの枠の箱の ID の集まりが同じ構造の routeLayout と同じ、失敗したリポジトリの枠に overviewWarnings の文と次の1手、F-02 の2つの知らせ、allgraph.css に色の値と色の札がなく、`.ax-body > .gx-box` 等の絶対配置・`.main[data-view=\"allgraph\"]`・allgraph の `--pn-w` の規則がある", verifies: ["R-03", "R-05", "F-01", "F-02"]}
	"T-06": {title: "偽の DOM の allgraph の選び：2つのリポジトリにある同じ ID の箱の一方を押すと、api.scope がそのリポジトリの鍵で呼ばれ、もう一方の箱は is-sel でなく、欄の『詳しい画面』の href が /r/<その鍵>/scopes/<ID>（embed で embed=1）、欄の current() がそのリポジトリと構造を返す。状態の札の数がすべての出している枠の合計。稼働の印（orca-web の要約の合成）が対応した worktree のあるリポジトリの箱にだけ描かれる", verifies: ["R-06"]}
	"T-07": {title: "偽の DOM の allgraph の更新：版が変わらない更新を3回しても specdockAllGraphStats.layouts が増えず、1つのリポジトリの版を変えるとそのリポジトリの構造だけが読み直されて layouts が1つだけ増える。markSeen を呼ばない。エージェントの行の寸法が変わったリポジトリだけ配置し直す（リポジトリごとに2回まで）", verifies: ["R-06", "R-08"]}
	"T-08": {title: "実機：この PC の9つの登録の写しで、company-os の下の事業・プロダクトの入れ子と外の spec-dock・orca-web が1枚に出る、全体・いま・これからで枠の出入りが正しい、箱を押すと横の欄が開き『詳しい画面』がそのリポジトリへ移る、稼働の印が出る、を 1440・1000・390 × 明・暗で写し、edgeAudit の total の違反0、ブラウザーのエラー0、横のスクロールなし、『収める』の後にすべての枠が図の領域に収まる、リポジトリごとの配置の ms", verifies: ["R-01", "R-03", "R-05", "R-06", "R-07"]}
}

verification: """
	節目（実装担当が各手順の後）：`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-07（T-08）。
	"""

rollback: "PR を戻す（dashboard の静的な資産、サーバーの殻の道1つ、契約の文書の1行、テストだけ）。API・保存・モデルは変わらない。保存の `specdock.allgraph.v1` は残っても害がない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": "なし（S-02 の後は、タスク担当が S-01・S-02 のテストの合格と HEAD を確かめてから impl-claude を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 7f7dd2b1d から S-05 の終わりまで（S-06 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00614/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01〜S-02、compose.js と道・タブ・サーバーの殻の道、その node と HTTP のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。枠の組み立てと『これから』の出し入れは DOM のない純粋な計算で node のテストで確かめられ、道とサーバーも単体のテストで確かめられる（方針の「テストで確かめられる実装」× standard、本人の指示で Sol）。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-03〜S-05、draw.js の取り出し、画面・CSS・偽の DOM のテスト、全体の検証）", model: "opus", effort: "medium", rationale: "claude。画面は実機の DOM と見た目の判断を含む（依頼書の指定：画面は Claude Opus 5.5 / medium）"}
		owner:         {task: "実機の写しと試しの URL（S-06）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-05", model: "opus", effort: "medium"}
	}
}
