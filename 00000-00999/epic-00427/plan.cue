package spec

// 計画（Epic）。型 specdock/v1。
// 依存は GitHub に登録済み（2026-11-03）。after はそれと同じ。

goal: "利用者ごとに1つのサーバーで、全リポジトリの仕様の構造（段階1、0.6.0）と文書（段階2、0.7.0）を見せるダッシュボードを出し、company-os に埋め込めるようにし、今の Markdown と PlantUML のダッシュボードを撤去する。"

slices: {
	"iss-00527": {
		covers:  ["F-13"]
		text:    "第1波。試作：起点の違う iframe の中で、iPhone の Safari と PC のブラウザーが、構造の図の指の操作（つまむ、移動、タップ）、`frame-ancestors` の決まり、`sandbox` の資料の切り離しと `/ds/` の読み込み、postMessage の始まりの挨拶と戻るの履歴（D-15）をどう扱うかを確かめる。製品のコードは出さず、結果を report.md に書き、設計（D-08、D-09、D-15）を直す材料にする。逃げ道（普通のリンク）の実装は #531。iPhone の実機の確かめは利用者に頼む。"
		session: "light"
	}
	"iss-00528": {
		covers:  ["R-07", "R-09", "R-10", "R-20", "R-21", "R-29", "R-31", "F-01", "F-02", "F-03", "F-04", "F-06"]
		text:    "第1波。D-04 の状態のモデル（ボードの分け方、変化の比べ方を含む。PR の欄は #537 の形を先に決めて受ける）、D-05 の要約、D-12 の読めないときの扱いと、`dashboard summary`（D-01 の一部）。HTTP は作らない。R-21 の受け入れのうち CLI の側と、R-29 の比べ方を確かめる。#527・#537 と並べる。"
		session: "std"
	}
	"iss-00537": {
		covers:  ["R-07", "R-30"]
		text:    "第1波。D-19 の PR の状態の取得（定期の同期の GraphQL、構造のスナップショットの版2、Scope との対応、失敗の扱い）。スナップショットの形は #528 と最初に合わせる。#527・#528 と並べる。"
		session: "std"
	}
	"iss-00529": {
		covers:  ["R-01", "R-02", "R-03", "R-04", "R-05", "R-08", "R-09", "R-21", "R-22", "R-27", "R-29", "F-01", "F-02", "F-04", "F-07", "F-08", "F-09", "F-12"]
		text:    "第2波。D-02 のサーバー、D-03 の道筋と API、D-06 の在りかの記録、D-09 の切り離しと枠の決まり、D-13 の `hide`／`show`／`list`、D-18 の「見た」の口、D-15 の埋め込みの約束（#527 の提案：資料の道も同じ `frame-ancestors` を持つこと、CORS は `/ds/` と `/vendor/` だけで API には付けないことをテストで確かめる）、D-12 のサーバーの側（リポジトリごとに最後に読めたモデルを覚え、読めないときも画面を開いて、古さ・読めないこと・次の1手を上の帯に示す）。あわせて、画面の骨組み（上の帯、リポジトリの切り替え、画面の切り替えの枠、`?embed=1`、postMessage の受け渡し、5秒ごとの自動の更新、「見た」の送信）を作り、R-03・R-08・R-22 と、R-09 の上の帯の表示、F-01・F-02・F-04 をこの Issue で確かめる。中の3つの画面は #531・#532 が作る。見た目は利用者が選んだデザイン案に従う。"
		after:   ["iss-00528"]
		session: "std"
	}
	"iss-00530": {
		covers:  ["R-28"]
		text:    "第3波。D-14 の常駐（`dashboard service install`／`status`／`uninstall`、前面の `serve` との共存、版の更新の後の起動し直し）。#531・#532・#533 と並べる。コマンドの数を縛る文書（`reference_cli.md` など）は #533 と重なるので、後にマージするほうが main を取り込む。"
		after:   ["iss-00529"]
		session: "std"
	}
	"iss-00531": {
		covers:  ["R-06", "R-09", "R-11", "R-12", "R-13", "R-14", "R-17", "R-18", "R-24", "R-29", "R-30", "R-31", "F-05", "F-13"]
		text:    "第3波。D-07 の画面の作り、D-08 の状態のボード（マージ待ちの列、片付けの候補の印）・詳しい画面（タブ）・検索、D-16 の横断の概況（取得が古いときの警告の帯、R-09）、PR の状態が分からないときの表示（R-30）、変化の印、どの画面も普通のリンクで開ける逃げ道。#527 の試作の結果と、利用者が選んだデザイン案を取り込む。#532 と並べる（画面のモジュールを分けてぶつからないようにする）。"
		after:   ["iss-00529", "iss-00527", "iss-00537"]
		session: "std"
	}
	"iss-00532": {
		covers:  ["R-06", "R-11", "R-15", "R-16", "R-29", "R-31", "F-11"]
		text:    "第3波。D-08 の構造の図（ホーム。状態をアイコンと図形で示す）と時間の軸（PR の出来事を含む）、図の変化の印。#527 の試作の指の操作の結果と、利用者が選んだデザイン案を取り込む。採用した試作には2本指のつまみと `gesturestart` の抑止がないので、#527 の `embed-lab.py` の図を参考に足し、「2本指のつまみで図だけが拡大し、ページ全体は拡大しない」を受け入れの条件にする。図の上の操作の帯の下に、箱が隠れない余白を取る（#527 の提案 P-5、P-6）。#531 と並べる。"
		after:   ["iss-00529", "iss-00527", "iss-00537"]
		session: "std"
	}
	"iss-00533": {
		covers:  ["R-23"]
		text:    "第3波。D-10 の撤去。#530〜#532 と並べる。`reference_cli.md` と `cli-redesign-guide.html` は #530 と重なるので、後にマージするほうが main を取り込む。"
		after:   ["iss-00529"]
		session: "std"
	}
	"iss-00544": {
		covers:  ["R-11", "R-15", "R-18"]
		text:    "第3波の後の手直し（2026-11-04 統括が追加）。#531・#532 の報告の残り：骨組みの格子で PC の `<main>` が高さ0になる件を骨組みで直す（#532 の `grid-row: 4` の回避を外す）、構造の API の `assurance`・`branch`（#532 が null で足した項目）を全 Scope 分読む（#531 の `dashboard_scope_details.py` の読み取りを一覧に広げ、時間の上限と失敗の扱いを保つ）、`views/_shared/parts.js` と `views/graph/marks.js` の状態の印の重複を1つに寄せる、スナップショットのないリポジトリでの「見た」の 409 の扱い、手元のデータの既定でない組み合わせで残る線の重なり（4/171 通り）を調べて直せる分を直す。"
		after:   ["iss-00531", "iss-00532"]
		session: "std"
	}
	"iss-00534": {
		covers:  ["R-23"]
		text:    "第4波。0.6.0 を出し、5つのリポジトリに配る。`migration.md` の「0.6.0 への更新」（コマンドが8つ増える、`canonical status` の `dashboard` の項目が消える、残った5つのファイルを消してよい、構造のスナップショットが版2になる）。マージの後の導入と配布は統括が行い、利用者の PC で `dashboard serve` と iPhone からの表示を確かめる。"
		after:   ["iss-00530", "iss-00531", "iss-00532", "iss-00533", "iss-00544"]
		session: "light"
	}
	"iss-00552": {
		covers:  ["R-01"]
		text:    "2026-11-04 利用者の要望で統括が追加。ダッシュボードに出すかどうかを、コマンド（`dashboard hide`／`show`）だけでなく、設定のファイルで決められるようにする。設定は epic-00547 の3段（初めの値 < 利用者の設定 `$XDG_CONFIG_HOME/spec-dock/config.json` < リポジトリの設定）と同じ仕組みに乗せ、その設計が決まってから着手する。`hide`／`show` との優先の関係を決める。設定の仕組みは #549（PR #558）で入った（`specdock.config/v1`）。"
		after:   ["iss-00534"]
		session: "std"
	}
	"iss-00556": {
		covers:  ["R-15", "R-31"]
		text:    "2026-11-04 利用者の 0.6.0 の確かめから統括が追加。構造の図の既定の表示を「全体の計画が見え続ける」形に直す。(1) 終わった Scope は、親が開いていれば出す（進行中の Epic の終わった Issue、開いた Initiative の終わった Epic）。終わった Epic は畳んだ枠（完了 n/n）だけにし、その中（孫）は出さない。親も終わったものは出さない。「終わったものも全部」の切り替えは残す。(2) 図に出ている箱どうしなら、終わった依存の矢印も既定で薄く出す（待っている依存は今のとおり目立たせる）。(3) 並びを番号順でなく活動順にする：枠（Initiative・Epic）は作業中を含む → 着手できるを含む → 止められているだけ → 終わったものだけ、同じ組の中は最近動いた順。枠の中の箱は、開いているものを R-31 の推奨順で上に、終わったものを下に（最近終わった順）。依存の左右の段は今のまま。ボードの「終わった」の列も最近終わった順にそろえる。(4) 枠や箱を一定の幅で折り返さず、右へ広げる（画面は横に動かして見る。利用者の判断、2026-11-04）。edgeAudit の違反0を保つ。"
		after:   ["iss-00534"]
		session: "std"
	}
	"iss-00535": {
		covers:  ["R-19", "R-25", "R-26", "F-10"]
		text:    "第5波（段階2）。D-11 の文書の描画と計画の進み具合。あわせて、#530 の残り：API の `server.restart_required` が true のとき、画面の上の帯で前面の `serve` の起動し直しを促す。"
		after:   ["iss-00534"]
		session: "std"
	}
	"iss-00536": {
		covers:  ["R-19", "R-25", "R-26"]
		text:    "第6波（段階2）。0.7.0 を出し、5つのリポジトリに配る。"
		after:   ["iss-00535"]
		session: "light"
	}
}

verification: "画面の見た目は、利用者が4つのデザイン案から選んだ案D と、それを直した試作（2026-11-04 の決定。`artifacts/20261103t150110z--dashboard-design-d2.html`）に従う。#532 は試作の線の検査（`edgeAudit`）をテストに持ち込む。各 Issue の PR で `make lint` と `uv run pytest`（全体）と CI を通す。standard の Issue は、仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通す。light の Issue は、仕様のレビュー opus/medium、コードのレビュー sonnet/high、最終品質ゲート opus/high（1人）。画面の Issue（#531、#532）は、PC のブラウザーでの確かめを報告に残し、iPhone の Safari の確かめは利用者に頼む。0.6.0 と 0.7.0 の配布の後、5つのリポジトリで `canonical status` と、`dashboard serve` での各リポジトリの表示を確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。配った後なら、常駐を入れていれば `dashboard service uninstall` を先に行い、パッケージを前の版に戻し、各リポジトリの配布の PR を `git revert` する。"
exit: "#527〜#537 が閉じ、5つのリポジトリが 0.7.0 で、利用者の PC と iPhone から全リポジトリのダッシュボードが開け、company-os の試しの親の画面に埋め込めることを確かめ、この Epic の report.md に結果をまとめた。"

execution: {
	sessions: {
		coord: {task: "統括（計画、配布、利用者への報告）", model: "opus", effort: "high", rationale: "policy §5 統括役"}
		std: {task: "standard の Issue の実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装"}
		light: {task: "light の Issue の実装（Orca の worker）", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装"}
	}
	reviews: {
		"std-spec": {role: "standard の Issue の仕様のレビュー", after: "iss-00528", model: "opus", effort: "high"}
		"std-code": {role: "standard の Issue のコードのレビュー", after: "iss-00528", model: "opus", effort: "high"}
		"std-gate": {role: "standard の Issue の最終品質ゲート", after: "iss-00528", model: "opus", effort: "high"}
		"light-spec": {role: "light の Issue の仕様のレビュー", after: "iss-00527", model: "opus", effort: "medium"}
		"light-code": {role: "light の Issue のコードのレビュー", after: "iss-00534", model: "sonnet", effort: "high"}
		"light-gate": {role: "light の Issue の最終品質ゲート", after: "iss-00534", model: "opus", effort: "high"}
	}
}
