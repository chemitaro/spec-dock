---
種別: レポート（Issue）
ID: "iss-00537"
関連GitHub: ["#537", "#427"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 定期の同期（`ensure_fresh(..., "cycle")`）が、構造の処理の後に、PR の状態を GraphQL の1回の問い合わせで取り、構造のスナップショットに書くようにした。開いている PR は100件まで、閉じたかマージされた PR は50件までで、どちらも更新の新しい順。費用はおよそ3点。前回の成功から2分を超えたときだけ取る。レート制限で失敗したときは、その時刻からも2分待つ。
- スナップショットの版を2にした。`pull_requests`、`pull_requests_fetched_at`、`pull_requests_error` を足した。形は統括と #528 で決めたもの（msg_099086f2b281、msg_5e86801e635b）。
- 新しい版は版1のファイルも読む。そのとき PR の欄は空で、`fetched_at` は `null` になる。書くときは版2で書く。古い版は版2を「ない」として取り直し、版1で書き戻す。そのファイルも新しい版は読める。
- PR の問い合わせだけが失敗したときは、構造の結果を書き、PR は前回の値を残し、`pull_requests_error` に理由を書く。レート制限は待たずに失敗にする（`GithubApi.request` と `graphql` に `wait_rate_limit=False` を足した）。
- 読む側の関数 `pull_requests_by_scope(snapshot)` を足した。`branch_names_scope` で Scope を求め、開いている PR を先に、次に `created_at` の新しいものを選ぶ。コマンドの段階（`display`、`decision`、`refresh`）は PR を取らない。
- コミット：`36e368fa3`（本体）、`b8a3812d8`（コードのレビューの P3。GraphQL が断ったときの説明の文言）。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：round 1 は合格（P2 が1件、P3 が1件）。P2 は間隔の起点を統括の決定に合わせる指摘、P3 は新旧の比べ方の指摘で、仕様を直した。round 2 も合格（P3 が1件）。P3 は互換の注記の書き方で、直した。
- コードのレビュー（code-reviewer opus/high、Standards と Spec の2人）：どちらも合格。Standards の P3 が1件で、`b8a3812d8` で直した。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人。campaign `iss-00537-1`）：`b8a3812d8` で合格。レビューは P0〜P3 がすべて0件で、観点も網羅した。`make lint` は exit 0。`uv run pytest` は exit 0（3340 passed、7 skipped）。証拠はリポジトリの `.workbench/final-quality-gate/iss-00537-1/closure.md`。
- 既存の読む側：版1と版2で、`dependency check` の JSON の結果が一致した。PR が変わっても、今のダッシュボードの `input_hash` は変わらない。どちらもテストで確かめた（`tests/cli_runtime/test_issue537_pull_request_snapshot.py`、`tests/unit/domain/test_canonical_dashboard.py`）。

## 0.6.0 の移行の注記に要る契約の変更

- 構造のスナップショット（`<state_root>/github/<host>/<owner>/<name>/snapshot.json`）が版2になり、`pull_requests`、`pull_requests_fetched_at`、`pull_requests_error` を持つ。新しい版は版1を読める。前の版に戻すと、前の版は版2を「ない」として、構造を一度だけ取り直す。
- 定期の同期の GitHub への要求が増える。PR の GraphQL の問い合わせ（およそ3点）が、リポジトリごとに次の頻度で加わる。成功の後は2分に1回、レート制限の後も2分に1回、ほかの失敗が続くときは周期（60秒）ごとに1回。公開のコマンドの出力は変えない。

## Residual Risks / Follow-ups

- 読む側の約束（#528）：`pull_requests_fetched_at` が `null` か、30分を超えて古いか、`pull_requests_error` があるときは、PR の状態を「分からない」とする。版1のファイルは「知らない版」でなく「PR が分からない」として扱う。
- PR の取得が成功するたびに `snapshot.json` を書き直す（2分に1回）。ファイルの時刻を見る読む側（#529 の自動の更新）は、そのたびに読み直す。
- `pull_requests_by_scope` は、この Issue の領域の関数である。#528 が自分の領域で2つの鍵を解析しているなら、後にマージするほうが重複を消す（統括の決定 (4)）。
