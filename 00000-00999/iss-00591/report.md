---
種別: レポート（Issue）
ID: "iss-00591"
関連GitHub: ["#591"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- round-1（spec-reviewer opus / high）：合格（P0 0・P1 0・P2 2・P3 2）。`.workbench/spec-review/iss-00591/round-1.json`、検査 `round-1.check.json`（valid、pass）。P2（別のポートでは部品の import も CORS で 403 になり D-06 の確かめが書いたとおりに取れない、port の一致が config_problems に出ない）と P3 2 を直し、`review-response.md` に対応を記録。
- round-2（同じレビュアー）：**合格**。P0〜P3 なし。`round-2.json`、検査 `round-2.check.json`（valid、pass）。
- 合格した文書の sha256：requirement.cue `ca98d0d4409f4c0130b3c1ecfd1f5d217a486d45c0e537907c675e5263eddbc1`、design.cue `ad630886b2d0ef6da2b17362d6c110d80bd5f7b4f2b7e40d3095c836c708b6f5`、plan.cue `755294cfe08b5ac4916464198b62da667c711edb94c8c2b03947196e625e3e24`。開始のコミット `89f51588a`（clean）。
- 結果の場所：この Issue の worktree の `.workbench/spec-review/iss-00591/`。
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `89f51588a..b7dd1c765`、観点 functional-correctness・requirements-closure・test-adequacy・security-baseline）：**合格**（attempt 1）。P0〜P3 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3844 passed / 7 skipped）。closure は worktree の `.workbench/final-quality-gate/iss-00591-fqg-1/closure.md`。
- 注：plan.cue は合格の後、手順の status だけを done に書き換えている（中身は合格のまま）。

## 実装の記録

実装担当 impl（Codex gpt-6.1-sol / medium、dispatch `ctx_c24c12977822`、launch.effective codex・gpt-6.1-sol・medium）。記録の詳細は worktree の `.workbench/implement/iss-00591/{start.md,steps.md}`。

- 開始のコミット `89f51588a` の基準：`make lint` 合格、`uv run pytest` 3801 passed / 7 skipped。
- S-01（`1abe9062f`）：`domain/orca_web.py`、`read_user_orca_web`、`DashboardSite.orca_web()` と節の誤りの `config_problems`、`shell_csp`・`_orca`・画面の CSP・一覧の API の `server.orca_web`。T-01〜T-03。
- S-02（`7de3a6eb3`）：`StructureFacts(readings, worktrees_status, paths)`、構造の API の `worktrees`（文書の上と各 Scope）、`scope_facts` の worktrees、`infra/worktree_signature.py` と revision。T-04、T-05（本物の git）。
- S-03（`4dfcf9167`）：`core/orca_match.js`。T-06〜T-08。git-autocommit が英語の文を作ったので、未 push のコミットの文だけを日本語にする amend をタスク担当が認可した（ツリーと親は同じ）。
- S-04（`c3ddadc74`）：`core/orca.js` と `app.js` の組み込み。T-09、T-10。
- D-01 の追補（`b7dd1c765`）：有効な origin の `problem` を必ず null にする（純粋な関数の出力の契約）。
- 終わり：`make lint` 合格、`uv run pytest` 3844 passed / 7 skipped。

## 実データの確かめ（S-05、タスク担当）

HEAD `b7dd1c765` の `git archive` から作った wheel（spec-dock 0.9.1）を隔離した venv に入れ、道具の環境の状態の置き場の写し（サーバーの記録とログを除く）で、ポート 18591、`--tailscale` で `dashboard serve` を立てた（記録は worktree の `.workbench/iss-00591/`）。常駐の orca-web（127.0.0.1:8791）と常駐のダッシュボード（47800）の設定には触れていない。

- 一覧の API の `server.orca_web`：`{enabled: true, origin: "http://127.0.0.1:8791", port: 8791, problem: null}`。画面の CSP の script-src・style-src・connect-src・frame-src の末尾に `http://127.0.0.1:8791` だけが足され、`frame-ancestors 'self'` は今のまま。
- node の上の本物の部品（`match.mjs`）：配った `core/orca.js` を、常駐の orca-web の `/embed/` の部品（agent-marks.js、agent-marks-icons.js、agent-marks-view.js、elapsed.js）と要約で動かした。状態 ok、connection connected、要約の worktree 53。CSS 1回、import 1回。
  - spec-dock：構造の worktree の記録 ok（パス 5）。対応 1 Scope・1 worktree：iss-00591 ← この Issue の worktree（ブランチ `chemitaro/iss-00591`、エージェント 4）。main のチェックアウト（ブランチ main）はどの Scope にも対応しない。要約に残っていた iss-00594 は、確かめの時点で worktree が片付けられ、構造にも要約にも出なかった。
  - housing-lifecycle：9 Scope・9 worktree（iss-00296、00399、00400、00407、00409、00412、00415、00417、00419）。Scope を名指さないブランチ（`chemitaro/i418-domain-design`、`chemitaro/seabiscuit`）は対応しない。
  - tenting-cradle：1 Scope・1 worktree（iss-00025）。company-os、input-devices、yubisaki、orca-web：0（エージェントは main のチェックアウトだけ）。
  - 合計：**11 Scope・11 worktree**。
- ブラウザー（headless Chrome、`browser.mjs`、CDP）：試しの画面（オリジン 18591。orca-web の `ORCA_WEB_READ_ORIGINS` にない）で、`agent-marks.css` は 200、`agent-marks.js` は CORS で拒まれ（同じ Origin の curl で 403）、約 10 秒後に `agent-marks.js?r=1` が試され同じく拒まれた。要約の GET は出なかった。構造の図（23 の箱）とボードは描かれ、ページの例外はない（コンソールの誤りは CORS の拒否の記録だけ）。

## 逸脱と判断

- 仕様のレビューの P2 を受けて、S-05 の確かめのやり方を直した（別のポートでは部品の import も orca-web の CORS で拒まれるため、本物の部品と要約での `core/orca.js` の確かめは node の上で行った）。ブラウザーから本物の要約を読む確かめは、47800 の常駐のダッシュボードを新しい版にした後の Epic の確かめに残る。
- S-03 のコミットの文の amend（未 push、文だけ。タスク担当が認可）。
- 実装担当の値は計画どおり（Codex gpt-6.1-sol / medium）。逸脱なし。

## Outcome

PR #596（https://github.com/chemitaro/spec-dock/pull/596、head `b7dd1c765d922a847b26103d0486290d9b7d8bd8`）。CI：observable_ci PASS、merge_readiness READY（2026-11-14T10:56Z、worktree の `.workbench/coding-task/iss-00591/ci2.json`）。マージは統括が行う。

## Verification

## Residual Risks / Follow-ups

- iss-00592：印と「Orca で開く」の描き、配る文書（`orca_web` の節、`ORCA_WEB_READ_ORIGINS` の前提、localhost や MagicDNS の名前では読めないこと）。
- `.git` が dir でない main のチェックアウトでは worktree の署名が None で、worktree の変化だけでは revision が変わらない（design.cue の risks）。
