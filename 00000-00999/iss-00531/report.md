---
種別: レポート（Issue）
ID: "iss-00531"
関連GitHub: ["#531"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

骨組み（#529）の差し込み口に、状態のボード、Scope の詳しい画面、横断の概況、上の帯の検索を入れた。判定は #528 のモデルをそのまま使い、画面はサーバーの JSON（`lane`、`merge`、新しく足した `rank` など）を写すだけにした。詳しい画面のために、カタログの文書と Artifact、保証レベル、このPCの worktree を読む部品を足した（何も書かない）。

## Outcome

- 画面（`src/spec_dock/assets/dashboard/views/`）
  - `board.js`、`board.css`：列 止められている → 着手できる → 作業中 → マージ待ち（マージできる／直す必要あり）→（終わった）。列の中は `rank`（推奨順）。不明の帯、開いた配下を持つ閉じた親の帯、上の数の帯、片付けの候補の `<dialog>`、種類・親ごと・終わったものの切り替え（問い合わせ `kind`、`group`、`done`）、凡例、PR が分からないときの帯。
  - `scope.js`、`scope.css`：見出し（種類、ID、番号、題名、状態、理由、マージ待ちの段、変化、親の道筋、保証レベル、GitHub、PR、このPCのブランチ）と5つのタブ（問い合わせ `tab`）。依存のタブは自分の依存と引き継いだ依存を分け、大もとの待ち先に印を付け、間接の大もとの待ち先を別に並べる。配下のタブは開いたものだけの段。文書と Artifact のタブは、カタログがないときに次の1手を示す。
  - `overview.js`、`overview.css`：リポジトリごとの札（マージ待ち・作業中・着手できるの題名、数、片付けの候補、変化、取得の時刻）と警告の帯（ない、読めない、知らない版、30分を超えて古い、異常、PR が分からない、2つのクローン、API の失敗）。「見た」は送らない。
- 共有の部品（#532 と名前が重ならないよう `views/_shared/` に置いた。統括が後で整理する）
  - `views/_shared/logic.js`：DOM を使わない関数（列の振り分け、数、問い合わせの切り替え、検索の一致、変化と PR の言葉、概況の警告、日付）。
  - `views/_shared/parts.js`、`parts.css`：札、PR の印、保証レベルの印、後に続くの印、変化の印、進み具合の帯、凡例、逃げ道のリンク（`newTabLink`）、骨組みにないアイコン。CSS は3つの画面の `[data-view=…]` の下に限った。
  - `views/_shared/search.js`、`search.css`：上の帯の検索。骨組みの `app.js` に import と `mountSearch` の1行を足した（統括が許した）。5秒ごとの上の帯の描き直しは `MutationObserver` で見張って付け直す。CSS は `search.js` が自分で読み込む（#532 の画面がホームでも効く）。
  - 状態の形は骨組みの `core/ui.js` の `STATES`、`stateIcon`、`chip` を使い、新しく作っていない。
- サーバー
  - `runtime/presentation/dashboard_api.py`：構造と Scope の JSON に `rank`、`in_progress` を、Scope の JSON に `dependencies`（`waits_for`、`waited_by`）、`open_child_stages`、`details` を足した。
  - `runtime/application/dashboard_scope_details.py`（新規）：カタログの文書と Artifact、`requirement.cue` の保証レベル（`cue`、上限3秒）、`git worktree list`（上限3秒）。どれも失敗はその欄だけを「読めない」にする。
  - `runtime/application/dashboard_http.py`：`scopes/<ID>` の分岐の1か所で `read_scope_details` を渡す（統括が許した）。構造にない ID は読み取りを走らせずに 404。
  - `runtime/infra/dashboard_server.py`（#529 の不具合の直し、統括が許した）：待ち受けの待ち行列が標準の 5 のままで、画面が十数個のモジュールを同時に読むと macOS で接続が切られ（64本の同時の要求で 11〜19本が `Connection reset`）、Chrome でボードを開くと `search.js` などが切られて画面全体が出ないことが実際に起きた。`_Listener.request_queue_size = 128` を足し、`tests/cli_runtime/test_issue531_dashboard_concurrency.py` で確かめる（直した後は 64本×3回がすべて 200）。
- 作業者の判断：列の並びはサーバーの `rank` で決める。概況は要約の API でなく構造の API を読む（要約はない・読めないときに 503 で中身を返さないため）。

### 0.6.0 の移行の注記（#534）に要る契約の変更

- 公開の契約の変更はない。コマンドの数、`static-inventory.json`、配布資産の文書、状態の置き場のファイルは変えていない。
- 画面のための JSON（契約にしていない `specdock.dashboard/v1` の `structure`、`scopes/<ID>`）に項目を足しただけ（`rank`、`in_progress`、`dependencies`、`open_child_stages`、`details`）。消した項目と意味を変えた項目はない。
- 画面の道の問い合わせに `kind`、`group`、`done`、`tab` を足した（開き直しの印で、契約にはしない）。`/r/…/scopes/<ID>` と `?embed=1` の形は変えていない。
- 詳しい画面を開くと、サーバーがカタログで `cue export` と `git worktree list` を読む（どちらも上限3秒、読むだけ）。
- サーバーの待ち受けの待ち行列を 128 にした（振る舞いの変更は、同時の接続が切られなくなることだけ）。

## Verification

- `spec-dock scope check iss-00531`：誤り 0、警告 0。
- 仕様のレビュー（spec-reviewer opus/high）：1回目 pass（P0・P1 なし、P2 3件、P3 4件）。P2・P3 を仕様に反映して2回目 pass（P2 なし、P3 1件。`#search-slot` の「親の header」という書き方。実装は `closest("header")` で正しく扱う）。記録は `.workbench/spec-review/iss-00531/`。
- コードのレビュー（code-reviewer opus/high、standards と spec の2人）：1回目（36e367ca5）両方 pass（P0・P1 なし）。P2 5件（検索の閉じ方2件、矢印の選択、間接の大もとの待ち先、この報告の証拠）をすべて扱った（146cb7489 と、この report.md と Artifact）。2回目（146cb7489）spec は指摘なし、standards は P2 1件（フォーカスを戻すときの `focus` イベントが選択を先頭へ戻す）。4a2e84c83 で直し、3回目（4a2e84c83）standards も指摘なしで pass。記録は `.workbench/code-review/iss-00531/`。その後のサーバーの1行（410a06a80）は最終品質ゲートで見る。
- 新しいテスト：`tests/unit/application/test_dashboard_scope_details.py`（`rank`、`dependencies`、`open_child_stages`、カタログの状態、文書、Artifact、保証レベル、worktree、失敗をその欄に閉じること、知らない ID で読まないこと、何も書かないこと、本物の `git worktree`）、`tests/unit/infra/test_dashboard_screens_js.py`（差し込み口の形、外の URL を読まない、利用者の文字を `esc` で逃がす、`app.js` の追加が1行、CSS が3つの画面の下に限られる。`node` があるときは `logic.js` と `parts.js` を実際に動かす）。
- PC のブラウザー（ヘッドレスの Chrome、CDP、`--disable-features=MacAppCodeSignClone`、`Browser.close` で終了）。サーバーは一時のディレクトリの状態の置き場（`XDG_STATE_HOME=/private/tmp/iss531-state.*`）で `dashboard serve --port 18531` で立て、利用者の `~/.local/state/spec-dock/` は使っていない。見本は5つのリポジトリ（PR と変化と片付けの候補のある o/r、3時間古く PR の分からない o/s、スナップショットのない o/m、異常のある o/a、250件の o/big）。仕組みと結果は Artifact：[check.mjs](artifacts/20261103t194354z-04--check.mjs)、[setup.py](artifacts/20261103t194355z--setup.py)、[結果（410a06a80、最新）](artifacts/20261103t194354z-05--result-410a06a80.json)、[結果（146cb7489）](artifacts/20261103t193600z-03--result-146cb7489.json)。下の数は 410a06a80 の実行のもの（画面の写しの一部は 146cb7489 の実行。画面は同じ）。
  - 横断の概況：5枚の札。o/s に「3時間前から更新されていません」の帯、o/m に「スナップショットがありません」と次の1手、o/a と o/r に異常の帯、PR の分からないリポジトリに「PR の状態が分かりません」。o/r の札の変化の数 3。概況を開く前後で `seen.json` の o/r の記録は 1 → 1（増えない）。検索の欄は出ない。凡例あり。[PC](artifacts/20261103t193558z--01-overview-pc.png)、[390px・暗い](artifacts/20261103t193559z-03--10-phone-dark-overview.png)。
  - ボード：列が 止められている、着手できる、作業中、マージ待ち の順。着手できるの先頭が後に続く4件の iss-00003。マージ待ちは「マージできる」1件（#7）、「直す必要あり」2件（CI 失敗の #8、衝突の #10）。下書きの PR の #9 は作業中の列。不明の帯（iss-00018）、開いた配下を持つ閉じた親の帯（epic-00014）。変化の印 3件（新しい、状態が変わった（止められている → 着手できる）、PR が変わった（前は開いた PR））。片付けの候補 3件が理由つきの一覧で開き、閉じられる。`kind=epic` の切り替えが同じページの中で URL に残り、`group=1&done=1` を開き直すと終わった列と親の見出しが出る。[PC](artifacts/20261103t193558z-01--02-board-pc.png)、[片付けの候補](artifacts/20261103t193558z-02--03-board-cleanup-pc.png)、[PC・暗い](artifacts/20261103t193559z-02--10-pc-dark-board.png)、[390px](artifacts/20261103t193559z-05--10-phone-light-board.png)、[390px・暗い・片付けの候補](artifacts/20261103t193600z-01--12-phone-dark-cleanup.png)。
  - 250件の構造（o/big）：ボードの札が、移動の始めから 76ms で出た（2秒以内）。
  - 詳しい画面：見出しに親の道筋、保証レベル、GitHub、PR #40、このPCのブランチ `chemitaro/iss-00007`。依存のタブで、iss-00013 の待ち先 #3 と #90（Scope でない Issue）が「epic-00012 から引き継いだ」と「大もと」の札つきで出る。iss-00022（Epic を待つ）では、間接の大もとの待ち先 iss-00021 が別に出る。配下のタブで epic-00002 が段1〜3 に分かれ、終わった1件を隠す。文書のタブで要件・設計・説明資料があり、説明資料は新しいタブで開くリンク。保証レベル standard（`cue` で読んだ）。Artifact のタブで2件（名前の `<b>` は逃がされ、リンクは新しいタブ）。カタログに Scope のない iss-00005 は、そのことと次の1手。構造にない iss-00099 は「構造にありません」。タブつきの URL を新しいタブで開くと同じタブが出て、タブの切り替えは履歴に積まれ、戻るで戻る。PR の分からない o/s では、PR の欄が「分からない」。[概要](artifacts/20261103t193558z-03--04-scope-summary-pc.png)、[依存](artifacts/20261103t193558z-04--05-scope-deps-pc.png)、[配下](artifacts/20261103t193559z--06-scope-children-pc.png)、[390px・暗い](artifacts/20261103t193559z-04--10-phone-dark-scope.png)。
  - 検索：構造の図（ホーム、#532 の差し込み口）でも上の帯に欄が出る。`iss-8` で iss-00008、題名の `failing` でも出て、Enter で詳しい画面へ移り欄が空になる。入力したまま6.5秒待つ（骨組みが上の帯を描き直す）と、欄、値、フォーカス、開いた候補が残る。矢印で選んだ候補は描き直しの後も選ばれたまま（CDP のフォーカスの模擬を有効にし、`focus` イベントが起きる経路で確かめた）。外を押すと候補が閉じ、描き直しの後も閉じたまま（値は残る）。390px では虫めがねのボタンから開ける。[PC](artifacts/20261103t193559z-01--09-search-pc.png)、[390px](artifacts/20261103t193600z--11-phone-light-search.png)。
  - 埋め込みの逃げ道：`?embed=1` のボード、詳しい画面、概況に、`embed=1` を外した同じ道を新しいタブで開くリンクが出る。札のリンクは `embed=1` を引き継ぐ。埋め込みでないときはリンクが出ない。
  - 幅と明るさ：PC（1440px）と 390px、明るい表示と暗い表示の4通りで、概況、ボード、終わったものを含めたボード、詳しい画面の概要・依存・配下・文書・Artifact の8画面（32通り）すべてで、`scrollWidth` が画面の幅を超えない。
  - JavaScript のエラー：例外と `console.error` はなし。記録された読み込みの失敗は、構造にない ID の Scope の API の 404 と、スナップショットのない o/m の「見た」の 409 の2件だけ（どちらも意図した応答）。直す前の実行で出ていた `ERR_CONNECTION_RESET`（`parts.js`、`search.js`）は、待ち行列の直し（410a06a80）の後は出ない。
  - 追加の画面の写し（410a06a80）：[ボード](artifacts/20261103t194353z--02-board-pc-410a06a80.png)、[依存](artifacts/20261103t194354z--05-scope-deps-pc-410a06a80.png)、[検索](artifacts/20261103t194354z-01--09-search-pc-410a06a80.png)、[PC・暗い・詳しい画面](artifacts/20261103t194354z-02--10-pc-dark-scope-410a06a80.png)、[390px・暗い・ボード](artifacts/20261103t194354z-03--10-phone-dark-board-410a06a80.png)。
- 後始末：試しのサーバーと Chrome を止めた。一時の状態の置き場（`/private/tmp/iss531-state.*`）は統括の指示で消さずに残し、統括がまとめて片付ける。

## Final Quality Gate

- 合格のコミット：`410a06a8019ee1154ee07400589f21c4ece6783e`（作業ツリーは clean、試行1回）。記録は `.workbench/final-quality-gate/iss-00531-g1/`（`campaign.json`、`closure.md`、`attempts/01/`）。
- レビューの側：quality-gate-reviewer（opus/high、1人）。観点は functional-correctness、requirements-closure、test-adequacy。pass（P0 0、P1 0、P2 0、P3 1、網羅は完全）。
- テストの側：`make lint` 終了コード0（ruff check、ruff format check、mypy すべて pass）、`uv run pytest` 終了コード0（3470 passed、7 skipped、27分03秒）。どちらも同じコミット。
- P3（情報。直さない）：詳しい画面の保証レベルの欄の括弧の中の理由が、状態と食い違うことがある（2つのクローンのときに「カタログにこの Scope がない」、`requirement.*` のないディレクトリで「Markdown の Scope」）。値（分からない／なし）とほかの表示は正しい。
- 手前の全体のテスト：36e367ca5 で裏で流した全体のテストは、その後にコードを直したので途中で止めた（結果は使っていない）。

## Pull Request

（PR を作った後に書く）

## Residual Risks / Follow-ups

- iPhone の Safari での表示（390px の実機、ダイアログ、検索の欄）は確かめていない。#534 で利用者に頼む。PC の Safari も未実施。
- #532 と同じ見た目の部品（PR の印、凡例など）を `views/_shared/` に別に持つ。統括が後で1つにまとめる。#532 の画面（構造の図、時間の軸）には `parts.css` が読み込まれないので、#531 の部品を使うときは `styles` に足す必要がある。
- `node` のない環境では、JavaScript の単体のテスト（5件）が飛ぶ。静的な検査（5件）とブラウザーの確かめで補う。
- 詳しい画面を開くたびに `cue` と `git worktree list` が走る（上限3秒）。カタログが大きいリポジトリで遅くなれば、結果を覚える仕組みを足す。
