---
種別: レポート（Issue）
ID: "iss-00635"
関連GitHub: ["#635"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 一覧の API（`GET /api/v1/repositories`）から `tier` を消し、各リポジトリは `repository`〜`problem` と `parent` だけを返す。読み替えの表 `TIER_LABELS`、`Nesting`、札のための `boundaries` の入力を消し、`repository_nesting(shown)` は鍵 → 親の鍵か None を返す（親の決め方は変えていない）。
- 『横断の構造』の枠の見出しは、folder のアイコン、`owner/name`、構造の図へのリンクだけ。`.ax-tier` の規則を CSS から消した。`REPO.headW`（280）は名前とリンクの最小の幅なので変えていない（requirement の decisions）。札の入れ物と間（gap）がなくなった分は名前が使う。
- 契約の文書 `reference_cli.md`（配る側と dogfood、同じバイト）から段の札の記述を消し、「0.9.5 だけで配った`tier`は、使う者がなく、0.9.6 で消しました（版の規則の例外）。」を足した（統括の決定 A、2026-11-17）。目録の sha256 を `9375d7fd…` にし、前の値 `bd8b72af…` を `known_old_sha256` に足した。
- Epic epic-00612 の仕様（R-02 を「名前に意味を持たせず、パスの包含だけ」に、R-03・R-05・F-02・F-03・D-01・D-02・D-05・compatibility・slices・exit）を、札をなくしたことに合わせて直した。
- コミット：`cca43a4ed`（Red：サーバーと文書のテスト）、`5265a5bfb`（Green：サーバー・文書・目録）、`1b480b498`（Red：画面のテスト）、`73d7e06c6`（Green：画面）。

### 環境に特化した決まりの調べ（R-04、D-06）

`src/spec_dock`（vendor を除く）で `company`・`business`・`product`・`service`・`事業`・`プロダクト`・`サービス`・`会社`・本人のリポジトリの名前（`housing`・`input-devices`・`yubisaki`・`taikyo`・`orca-web`）を探した。

| 見つけたもの | 種類 | 扱い |
|---|---|---|
| `runtime/application/dashboard_nesting.py` の `TIER_LABELS`（businesses→事業、products→プロダクト、services→サービス）と、途中のディレクトリの名前を札にする処理 | 決まり（名前の読み替え） | 外した（D-01）。T-05 で runtime の .py にこれらの語がないことを確かめる |
| `views/allgraph.js`・`views/allgraph/compose.js` の先頭のコメント「nested as the company is (company-os → business → product …)」 | コメント（決まりと誤読されうる） | 「main のチェックアウトのパスの包含で入れ子にする」の一般の言い方に直した |
| `docs/canonical.md` の設定の例のパス（`/path/to/taikyohiyou_project/...`、`housing-lifecycle`、`input-devices`、`company-os`） | 文書の例（決まりではない） | 残した。後続の候補（下の Follow-ups）。変えると配る資産と目録が増え、版上げの Issue と重なる |
| `runtime/domain/orca_web.py` と画面の orca-web の印・設定の節 `orca_web` | 連携する製品の名前（機能の名前） | 残した。ディレクトリやリポジトリの名前で分かれる決まりではない |
| 英語の一般の語（`business commands`、`product direction`、`ds.css "D: business"` など） | 一般の語 | 関係ない |

ほかに、名前やディレクトリの名前で分かれる処理は見つからなかった。

## Verification

- 仕様のレビュー（spec-reviewer opus / high）：1回目は fail（P1：v1 のまま `tier` を消すと契約の版の規則に反する）。統括に問い（msg_0343f6514fea）、A（v1 のまま、例外を1文で明記）に決まり反映した。2回目は pass（P0・P1 0、P3 2件は直した）。記録は `.workbench/spec-review/iss-00635/`。
- 節目のテスト：`uv run pytest tests/unit/application tests/unit/infra/test_issue613_repository_nesting_docs.py` 306 passed（S-01 の後）。`tests/unit/presentation/test_dashboard_allgraph_screen.py`・`test_dashboard_allgraph_compose.py` 35 passed（S-02 の後）。どちらも先にテストを直して落ちることを確かめた（Red：24 failed、2 failed）。
- 最終品質ゲート（quality-gate-reviewer opus / medium、試行1回）：`73d7e06c6` で pass（P0〜P3 0、coverage complete）。`make lint` exit 0、`uv run pytest` exit 0（4083 passed, 7 skipped）。記録は [closure.md](artifacts/20261117t030937z--closure.md)。
- 外の利用者：orca-web の main のチェックアウト `27b01fe` で、`spec-dock/` と `node_modules` を除き、語 `tier` も `specdock.dashboard/v` も検索が0件。

### 実機（T-06）

- `73d7e06c6` を `git archive` から wheel にし、隔離した venv、iss-00629 の状態の置き場の写し（9つの登録）、試しの `XDG_CONFIG_HOME`（orca_web は切る）で、`spec-dock dashboard serve --offline --tailscale --port 18635` を立てた。常駐の 47800・8791、道具の環境、ほかの Issue の試しのポートには触れていない（最初の1回は既定の設定で、ブラウザーが常駐の orca-web の `embed/agent-marks.js` を GET して CORS で止められたので、orca_web を切って取り直した）。
- 一覧の API（[api.json](artifacts/20261117t023505z-01--api.json)）：9つのリポジトリの項目は `repository`〜`problem` と `parent` で、`tier` はない。応答に `/Users/`・`/Volumes/` の文字列はない。親は、今の main の試しのサーバー（18629、iss-00629 の wheel）と9つとも同じ（company-os → housing-lifecycle → taikyohiyou_project、company-os → input-devices → generic-mona・tenting-cradle・yubisaki、spec-dock・orca-web は最上位）。18629 の `tier` は ［事業］・［プロダクト］ だった。
- 画面（headless Chrome、1440・390 × 明・暗 × 『これから』・『全体』の8組、[result.json](artifacts/20261117t023505z--result.json)）：8組すべてで、9つの枠の見出しの子は `ax-icon`・`ax-name`・`ax-link` だけで、`sd-badge`・`ax-tier` は0。入れ子（子の枠が親の枠の中、spec-dock・orca-web は company-os の外）が成り立つ。ブラウザーのエラー0、ページの横のスクロールなし。
- 写し（最初の表示）：[1440 明 これから](artifacts/20261117t023503z--allgraph-1440-light-next.png)、[1440 暗 これから](artifacts/20261117t023504z--allgraph-1440-dark-next.png)、[390 明 これから](artifacts/20261117t023504z-01--allgraph-390-light-next.png)、[390 暗 これから](artifacts/20261117t023504z-02--allgraph-390-dark-next.png)。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18635 番の `/graph`（`73d7e06c6` の wheel、orca-web の印は切ってある。URL は統括への報告で伝える）。止め方：`kill $(lsof -tnP -iTCP:18635 -sTCP:LISTEN)`。

### 逸脱

- codex-symlink-refusal：plan の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_7050ca89b1fa、launch.effective codex / gpt-6.1-sol / medium）は、Orca の chat-scratch の writable root の symlink による拒否で、ファイルを変えずに止まった（outcome failed）。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium に切り替えた。変更が小さいため、別の実装担当のセッションは起動せず、タスク担当（このセッション、Opus 5.5 / medium）が S-01 と S-02 を実装した。独立したレビューは最終品質ゲートの quality-gate-reviewer が行う。

## Residual Risks / Follow-ups

- `docs/canonical.md` の設定の例のパスに、本人のリポジトリの名前（taikyohiyou_project、housing-lifecycle、input-devices、company-os）が入っている。決まりではないが、普遍的な例（`/path/to/repo-a/...`）に直す後続の候補。配る資産の変更なので、版上げと合わせて行うのがよい。
- `migration.md` の 0.9.6 の節（`tier` を消したことと戻し方）は、iss-00634 が書く。
- 0.9.5 の `tier` を読む外の利用者が今後現れることはない（項目がない）。
