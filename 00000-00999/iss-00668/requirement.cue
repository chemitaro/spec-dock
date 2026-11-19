package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "帯の役割、worktree の見つけ方（git worktree list）、見方ごとの出し方を変える。表示と読むだけの API で、データの書き込みはなく、PR を戻せば元に戻る"
}

purpose: """
	構造の図（各リポジトリの `/r/<repo>/graph`）と『横断の構造』（`/graph`）の指揮の帯を、**`Unscoped`** の行に変える。
	(1) 統括が居る主のワークスペース（main のチェックアウト）が、誰も指揮していなくても、いつも図に出続ける。
	(2) SpecDock を正しく使わずに（work start せずに）作業している、どの Scope にも紐づかない worktree（野良）にすぐ気づける。
	Epic epic-00667 の唯一の Issue。
	"""

background: """
	正本は統括の依頼書（2026-11-19、本人と決めたこと）と、統括の答え（msg_e863b639b47f、2026-11-19：『これから』では指揮の線を引かない）。
	iss-00616（構造の図の指揮の線と帯）、iss-00617（『横断の構造』の枠ごとの帯と『ほかの場所』）、iss-00621（印の並びの記録）、iss-00646（重さ）、iss-00648（線の形）の仕様と report を土台にする。

	タスク担当が確かめた今の事実（2026-11-19、`1cfce6f96`）：
	- 帯（`views/graph/command.js` の `bandItems`）に出るのは、指揮の線の端（親か子）になったエージェントの worktree だけ。組（`commandPairs`）がないと帯も層も出ない（`graph.js` の `clearCommand`、`allgraph.js` の `A.shape = null`）。
	  誰も指揮していない main のチェックアウト、work start していない worktree のエージェント、エージェントのいない worktree は、どこにも出ない。Orca の要約（orca-web の `/api/worktrees/summary`）がないと、帯は出ない。
	- main のチェックアウトの札は、Orca の要約の `worktree.main` が真のとき「main のチェックアウト」（`bandLabel`）。
	- 構造の API（`/api/r/<repo>/structure`）は、サーバーで `git worktree list --porcelain -z` を1回読み（`dashboard_scope_details.read_structure_facts`、読みは `infra/git_cli._parse_worktree_porcelain_nul`）、`worktrees: {status, paths}` と、各 Scope の `worktrees: [{path, branch}]`（ブランチの名前が Scope を指すもの、`branch_names_scope`）を返す。各行の main・detached・bare・prunable・locked はサーバーで読めているが、API には出ていない。
	- git の一覧には、SpecDock の仕様の置き場（`spec-dock/.canonical`、ブランチ `spec-dock/canonical`、locked）の worktree も出る。読む場所（`site.catalog`）はこの worktree である。
	- worktree と Scope の対応は `core/orca_match.js` の `matchWorktrees`（パスが先、次に同じ project の中のブランチ）。
	"""

includes: [
	"構造の API に、git の worktree の一覧の各行（パス・ブランチ・HEAD・主か・detached・locked）を足す（読むだけ）",
	"両方の画面の帯を `Unscoped` の行にし、主のチェックアウト（`Primary`）と、どの Scope にも紐づかない worktree（`Unlinked`）を並べる。指揮の線の端がこの行に来ることは今と同じ",
	"エージェントのいない紐づかない worktree を薄く出し、多いときは `+N` に畳む",
	"項目を押すと、詳細の欄にブランチ・パス・エージェントと『Orca で開く』を出す。`+N` を押すと、畳んだ worktree の一覧を出す",
	"見方（全体・いま・これから）ごとの出し方。『これから』では指揮の線を引かず、指揮している項目に子の数を添える",
	"各リポジトリの図と『横断の構造』の行の項目の決め方を1か所の純粋な計算に寄せる",
]

excludes: [
	"worktree を作る・消す・prune する、work start させるなどの操作（読むだけ）",
	"ほかの画面の文言（英語への統一は将来。この Issue で決めた語だけ英語にする）",
	"Orca の要約の形、orca-web の変更",
	"本人の環境に特化した決まり（リポジトリや場所の名前で分けること）",
]

requirements: {
	"R-01": {
		title: "構造の API が git の worktree の一覧の各行を返す"
		text: """
			`/api/r/<repo>/structure` の `worktrees` に `items` を足す。各行は `{path, branch, head, main, detached, locked}`。
			`main` は git の一覧の最初の行（主の worktree）だけ真。bare の行・prunable の行（ディレクトリがない）・仕様の置き場の worktree（読む場所 `site.catalog` と同じパス）は `items` に入れない。
			`status` と `paths` は今のまま（`paths` は今どおり全部の行）。一覧が読めないときは `status: "unreadable"`、`items: []`。
			"""
		acceptance: [
			"main・linked・detached・locked・bare・prunable・仕様の置き場を含む一覧から、bare・prunable・仕様の置き場を除いた行が、git の順で返る",
			"`main` は最初の行だけ真、detached の行は `branch: null` で `head` を持つ",
			"一覧が読めないとき `status: \"unreadable\"`・`items: []`、`paths` は今と同じ",
		]
	}
	"R-02": {
		title: "帯を Unscoped の行にし、主のチェックアウトをいつも先頭に出す"
		text: """
			帯の行を `Unscoped` と呼び、行の頭に `Unscoped` の文字（title「Worktrees not shown as a Scope box」）を出す（今の『ほかの場所』の頭の文字と同じ形）。行の先頭に、主のチェックアウトの項目をいつも出す（エージェントがいなくても、Orca がなくても、誰も指揮していなくても）。
			項目は、ブランチ名（detached なら `detached @<HEAD の先頭7文字>`）と印 `Primary` と、そこにいるエージェントの印。主のチェックアウトが Scope に紐づくブランチにいても出す（そのエージェントは今どおり Scope の印に出る）。
			印には title と aria-label で短い説明を付ける（`Primary`：「The main checkout of this repository」）。
			"""
		acceptance: [
			"組がなく、Orca の要約もないとき、構造の図と『横断の構造』の各リポジトリの枠に、主のチェックアウトの項目が `Primary` の印つきで出る",
			"統括が誰も指揮していないとき、統括のいる主のチェックアウトが `Primary` で出て、統括の印がある",
			"今の札「main のチェックアウト」は、ブランチ名と `Primary` の印に変わる",
		]
	}
	"R-03": {
		title: "どの Scope にも紐づかない worktree を Unlinked で出す"
		text: """
			git の一覧の主以外の行で、どの Scope の worktree の記録（`scopes[].worktrees[].path`、`matchWorktrees` のパスの決まり）にも当たらないものを、主の後に、ブランチ名の順で並べる。印は `Unlinked`（title・aria-label「Not linked to any Scope. Link it with `spec-dock work start`.」）。
			Orca の要約に同じパスの worktree があれば、そのエージェントの印を重ねる（要約の並び、または部品の `orderAgents`）。
			指揮の線の端になったが行の項目に当たらない worktree（Orca の要約にだけある、同じ project の別の場所の worktree、ほかのリポジトリの worktree、Scope に紐づくが描かれた祖先がない worktree）は、今どおり行の項目になる（印は付けない。ほかのリポジトリは今の札、『横断の構造』では今の『ほかの場所』）。
			"""
		acceptance: [
			"work start していない worktree にエージェントがいると、その worktree が `Unlinked` とエージェントの印で出る",
			"Scope に紐づく worktree は行に出ない（線の端になって描かれた祖先がないときだけ、今どおり印なしで出る）",
			"Orca の要約にだけあって git にない worktree の扱いが今と同じ",
		]
	}
	"R-04": {
		title: "エージェントのいない紐づかない worktree を薄く出し、多いときは +N に畳む"
		text: """
			エージェントのいない `Unlinked` の項目は、減らした不透明度で出す。そのような項目が2つ以上あるときは、すべてを1つの `+N`（N はその数）の項目に畳む。1つだけなら畳まずに薄く出す。
			`+N` を押すと、詳細の欄に、畳んだ worktree のブランチとパスの一覧を出す（行の形は変えない）。
			"""
		acceptance: [
			"エージェントのいない紐づかない worktree が1つなら薄く出る、2つ以上なら `+N` に畳まれる",
			"`+N` を押すと、詳細の欄に畳んだ worktree の一覧が出る。もう一度・閉じる・Esc で閉じる",
		]
	}
	"R-05": {
		title: "項目を押すと詳細が出て、エージェントの印を押すとチャットが開く"
		text: """
			項目（ブランチ名の部分）を押すと、詳細の欄に、印（`Primary`・`Unlinked`）、ブランチ、パス、エージェントの一覧と、Orca の要約に同じ worktree があり orca-web につながるときは『Orca で開く』を出す。
			エージェントの印を押すと、今の帯と同じく、そのエージェントのチャット（`/embed/agent`）が開き、その線が目立つ。
			"""
		acceptance: [
			"項目を押すと詳細の欄にブランチ・パス・エージェントが出て、orca-web があれば『Orca で開く』が出る",
			"エージェントの印の押しで、今と同じチャットと線の目立ちが出る",
		]
	}
	"R-06": {
		title: "見方ごとに出すものを変える"
		text: """
			全体・いま：主のチェックアウト、紐づかない worktree のすべて（R-04 の畳み方）、指揮の線の端の項目。指揮の線は今のまま。
			これから：主のチェックアウトと、**子のいるエージェントのいる**紐づかない worktree だけを出す。指揮の線は引かない（今の『これから』の、祖先の枠や帯へ落ちる線はなくなる）。
			主のチェックアウトを含め、子のいるエージェントのいる項目に、子の数（項目ごとの合計。例：`3`、title・aria-label「3 agents in progress」、1なら「1 agent in progress」、内訳は R-09）を添える。
			指揮していない紐づかない worktree、エージェントのいない worktree、指揮の線の端だけの項目は『これから』に出さない。
			見分けは、要約の `agents[].parent` からの『子がいるか』という構造の印だけで決める（名前や場所の決まりに頼らない）。
			"""
		acceptance: [
			"『これから』で、指揮している紐づかない worktree だけが子の数つきで出て、指揮の線は1本もない",
			"『これから』で、主のチェックアウトはいつも出て、指揮していれば数が付く",
			"全体・いまの指揮の線が今と同じ",
		]
	}
	"R-07": {
		title: "『横断の構造』でもリポジトリの枠ごとに同じ行を出す"
		text: """
			『横断の構造』では、各リポジトリの枠の見出しの下（iss-00617 の枠ごとの帯の場所）に、そのリポジトリの同じ行を出す。行の項目は、各リポジトリの図と同じ1つの純粋な計算で決める。
			『これから』で見せる Scope がないリポジトリは、行に指揮している項目があるときだけ、見出しと行だけの枠で出す（iss-00617 R-03 の決まりを、指揮の線の親の代わりに『子がいる項目』で決める）。全体・いまでは今どおり。
			"""
		acceptance: [
			"『横断の構造』の各リポジトリの枠に、同じ行が出る",
			"『これから』で、Scope のないリポジトリの枠は、指揮している項目があるときだけ見出しと行で出る",
		]
	}
	"R-09": {
		title: "1つの worktree は1つの項目で、そこにいるエージェントの印をすべて並べる"
		text: """
			行の項目は worktree の単位にする（今の帯と同じく、同じ worktree のエージェントを別の項目に分けない）。項目の中に、ブランチ名（`Primary`・`Unlinked` の印）と、その worktree のすべてのエージェントの印を並べる（線の端でないエージェントも）。
			並びは、今の箱の印の決まり（部品の `orderAgents`：関係のないものは左に新しい順、指揮の関係のあるものは右に上流→下流。部品がなければ要約の並び）に合わせる。
			1行に並べるのは4つまでで、それより多いときは項目の中で折り返して高さを増やす（`+N` で隠さない。箱の印と同じ考え）。行の高さは、その行のいちばん高い項目に合わせる。
			指揮の線は、項目ではなく、その中の各エージェントの印の列の、項目の上の縁から出入りする（今と同じ。箱の印と同じく、折り返した行の印も項目の上の縁に端を持つ）。
			『これから』で添える子の数（R-06）は、項目（worktree）ごとの合計にし、title と aria-label で内訳（エージェントごと：`<種類> #<並びの番号>: <数>`）を出す。
			"""
		acceptance: [
			"1つの worktree に複数のエージェント（指揮の親子を含む）がいるとき、1つの項目にすべての印が `orderAgents` の並びで出る",
			"5つ以上のエージェントがいる項目は折り返して高くなり、印が隠れない。同じ行のほかの項目と枠の帯がその高さに合う",
			"指揮の線が各エージェントの印の列から出入りし、同じ項目の中の親子は弧になる",
			"『これから』の数が項目ごとの合計で、title に内訳がある",
		]
	}
	"R-08": {
		title: "線の検査と重さが戻らない"
		text: "`specdockEdgeAudit` の違反0、`specdockCmdAudit` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、iss-00646 の台本（`epic-00615/.workbench/perf-measure.mjs`）の数が今より悪くならない。"
		acceptance: [
			"実機の 1440・390 × 明・暗で違反0、cmdAudit の数が0",
			"重さの台本の数が、開始のコミットと比べて悪くならない（誤差の範囲）",
		]
	}
}

failures: {
	"F-01": {title: "git の一覧が読めない、または API に `items` がないとき（古いサーバー・試しの構造）は、行の項目を今どおり指揮の線の端だけで決め、主の印は Orca の要約の `main` で付ける"}
	"F-02": {title: "Orca の要約がない・壊れているときは、git の一覧だけで行を出す（エージェントの印・数・『Orca で開く』はない）"}
	"F-03": {title: "主の worktree が bare（チェックアウトがない）ときは、`Primary` の項目を出さない"}
	"F-04": {title: "パスの末尾の `/` の違いは同じ worktree とみなす（`normPath`）。同じパスの要約の worktree が2つあれば最初を使う"}
}

constraints: [
	"サーバーは git を読むだけ（worktree の一覧は今の1回の読みを使い、新しい git の呼び出しを足さない）",
	"項目の決め方は DOM・時計・ネットワークのない純粋な計算にし、node のテストで確かめる",
	"本人の環境に特化した名前（company-os・businesses・products など）を決まりに入れない",
	"英語にするのは、この Issue で決めた語（`Unscoped`・`Primary`・`Unlinked`、印の説明、子の数の説明）だけ",
]

decisions: [
	"2026-11-19 本人と統括（依頼書）：行の名前 `Unscoped`、印 `Primary`・`Unlinked`、並べるもの、git worktree list を土台にする、薄く・畳む、見方ごとの出し方、横断の構造でも枠ごと、環境に特化しない",
	"2026-11-19 統括（msg_e863b639b47f）：『これから』では指揮の線を引かない。Primary を含め、子のいる項目に子の数を添える。今の『これから』の祖先の枠へ落ちる線がなくなることを、決定と移行の案内に書く。全体・いまの線は今のまま",
	"2026-11-19 本人と統括（msg_19e324e8a034）：行の項目は worktree の単位。項目の中にすべてのエージェントの印を箱の印の並び（orderAgents）で並べ、多いときは折り返して高さを増やす（+N で隠さない）。指揮の線は各エージェントの印から出入りする。『これから』の数は項目ごとの合計で、title に内訳。受入に、1つの worktree に複数のエージェント（指揮の親子を含む）がいる場面の実機の写しを足す",
	"2026-11-19 タスク担当：1行に並べるエージェントの印は4つまで（4 × 52px で項目が 390 の幅の半分ほどに収まり、主と働いている項目が並ぶ）。それより多いと折り返す。`+N` に畳むのは、エージェントのいない worktree（R-04）だけで、エージェントは畳まない",
	"2026-11-19 タスク担当：畳む目安は『エージェントのいない紐づかない worktree が2つ以上なら全部を +N』。エージェントのいない worktree は片付けの候補で、押して見る以外の働きがない。1つなら薄く見せても行が長くならず、2つ以上は 390 の幅で主と働いている項目を押し出すので、全部を1つにまとめる（どれを見せるかの選び方を持ち込まない）",
	"2026-11-19 タスク担当：`+N` を押すと行を広げず、詳細の欄に一覧を出す。行の形が変わらないので、枠の組み立て直し（iss-00617 F-05）と線の動きが起きない",
	"2026-11-19 タスク担当：bare・prunable・仕様の置き場の worktree は API の `items` に入れない（開けるチェックアウトがない、または SpecDock の内部の worktree で作業の場所ではない）。仕様の置き場は読む場所と同じパスという構造の印で見分ける",
	"2026-11-19 タスク担当：行の名前は、今の『ほかの場所』と同じ行の頭の文字（lead）で `Unscoped` と出す（行が何かを画面だけで分かるようにする）。『ほかの場所』の頭の文字は今のまま",
]

questions: []
