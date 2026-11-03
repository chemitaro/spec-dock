---
種別: レポート（Issue）
ID: "iss-00528"
関連GitHub: ["#528"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードの状態のモデル（Epic D-04）、要約の JSON `specdock.dashboard-summary/v1`（D-05）、読めないときの扱い（D-12）と、コマンド `spec-dock dashboard summary [REPOSITORY]`（D-01 の一部）を作った。HTTP のサーバーと画面は作っていない（#529 以降）。

- `runtime/domain/dashboard_snapshot.py`：スナップショットの文書の版1・版2の読み、PR の欄の解析、PR の確かさ（`fresh`／`stale`／`unknown`）、`branch_names_scope` による Scope への対応づけ。
- `runtime/domain/dashboard_model.py`：`evaluate_all` を写した5つの状態と理由、ボードの列とマージ待ちの「マージできる／直す必要あり」、後に続く数・待ち先の数・推奨順（R-31）、片付けの候補（3種類）と残す印、配下の段・上流・下流・大もとの待ち先、「見た」の記録の1件と比べ方、週ごとの累計と最近の動き、取得の古さ。
- `runtime/infra/dashboard_files.py`：スナップショット（ない／読めない／知らない版の見分け）、隠す印、在りかの記録（`pid` が生きているかだけ）の読み。書かない。
- `runtime/presentation/dashboard_summary.py`、`runtime/application/dashboard_summary.py`、CLI の一覧と経路。公開のコマンドは 53 → 54。
- 文書：`reference_cli.md`（C54 の行と要約の契約の節）、`docs/README.md`、`cli-redesign-guide.html`、ルートの README（提供側と dogfood の写し）。`static-inventory.json` は、変えた3文書の行の sha256 を更新し、前の sha256 を `known_old_sha256` に足した（統括の決定 A）。

コミット：`b33e97758`（実装）、`e68a885cc`（コードのレビューの指摘の修正）、`e98f0ced2`（#537 を含む main の取り込み）、`c3d2ce374`（PR の解析を #537 の部品に寄せた）。PR：https://github.com/chemitaro/spec-dock/pull/539（最終の head `c3d2ce374`）。

### 仮の判断・合意（PR の本文にも書く）

- D-19 の PR の欄の形は、統括を介して #537 と合意した（requirement.cue の decisions）。#537 が先にマージされた（c2dc91826）ので、main を取り込み、PR の解析と Scope への対応づけを #537 の部品（`StructureSnapshot` の版2、`pull_requests_by_scope`）に寄せて重複を消した。`build_model(snapshot, *, now)` は PR をスナップショットから取る。
- PR の確かさ：版1、未取得、30分を超えた取得は `unknown`（PR を使わない）、取得の時刻が新しく `pull_requests_error` があれば `stale`（前回の値を使い印を付ける）。
- 片付けの候補に、Epic R-10 に合わせて「閉じた祖先のために止められている開いた Scope」（`open_under_closed_parent`）も挙げた。
- `dashboard summary` はリポジトリごとのファイルだけを読むので、同じリポジトリのクローンが2つ登録されていても曖昧にしない。REPOSITORY を指定したときは、チェックアウト（版3の宣言を含む）に関わらず動く。
- `--json` の要約は、ほかのコマンドと同じく `data.result` に入る（`data.kind` は `dashboard`）。

## Verification

- `spec-dock scope check iss-00528`：誤り0、警告0。
- 仕様のレビュー（spec-reviewer opus/high）：第1回 P1 1・P2 3・P3 3（`.workbench/spec-review/iss-00528/round-1.json`）を直し、第2回で pass（P0 0・P1 0、P3 2。`round-2.json`、`round-2.check.json`）。P3 の2件も直した。
- コードのレビュー（code-reviewer opus/high、規約と仕様の2人、`b33e97758`）：規約 P1 1（コマンドの数を縛る既存テスト3件の未更新）、仕様 P2 1（最近の動きが選んだ1件の PR しか入れない）。どちらも `e68a885cc` で直した（`.workbench/code-review/iss-00528/`）。
- #537 の取り込みと寄せた後の範囲のコードのレビュー（code-reviewer opus/high、`e68a885cc..c3d2ce374`）：pass、指摘なし（`.workbench/code-review/iss-00528/round-2-both.json`）。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）：
  - キャンペーン `iss-00528-fqg1`（`e68a885cc`、#537 の取り込みの前）：合格（レビューの P3 1件。lint 0、pytest 0 で 3344 passed、7 skipped）。
  - キャンペーン `iss-00528-fqg2`（**最終の `c3d2ce374`**）：合格。レビューは pass、網羅は完全、P0〜P3 0。`make lint` は終了コード0（ruff check、ruff format check、mypy が pass）。`uv run pytest` は終了コード0（3396 passed、7 skipped、1493.68秒。2回目）。1回目では `tests/integration/test_issue440_g3_git_boundary.py::test_signalled_checkout_is_observed_without_claiming_failure_certainty[signal]` が1件落ちた。`--timeout 1` の中で `git rev-parse` が時間切れになったもので、ほかのレビューと並べて走らせた負荷の下で起きた。この変更とは関係なく、単独では3回とも通るので、同じコミットで再実行した。
  - 証拠：`.workbench/final-quality-gate/iss-00528-fqg2/closure.md`（`fqg1` も残す）。
- CI（PR #539、`c3d2ce374`）：Provider CI、SpecDock check、Commit identity が成功。GitHub はマージできる状態（OPEN、下書きでない、MERGEABLE、CLEAN）と示した（2026-11-03T17:03Z 時点の観測）。
- 手元の本物のスナップショット（spec-dock、308件）で `spec-dock dashboard summary` が 0.23 秒で返り、片付けの候補などが出ることを確かめた（読むだけ）。

## Residual Risks / Follow-ups

- #530・#533 も `reference_cli.md`、`cli-redesign-guide.html`、`static-inventory.json` の同じ行を変える。後にマージするほうが取り込み直す。
- 0.6.0 の移行の注記（#534）に要る契約の変更：公開のコマンドに `dashboard summary` が増える（53 → 54）。新しい公開の契約 `specdock.dashboard-summary/v1`（`reference_cli.md` に記載）。ほかのコマンドの契約は変えていない。
- `spec-dock work finish` は、マージの後に統括が行う。
