---
種別: research
ID: "20260627t112517z-research"
タイトル: "guidance issue-execution step selection regression analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連: []
authority: "synthesized"
derived_from:
  - "local command: ./spec-dock/scripts/spec-dock guidance issue-execution"
  - "deep-consultant: 019f08cc-4816-7602-9e4a-8fe043bbbd13"
reflected_to: []
---

# 20260627t112517z-research guidance issue-execution step selection regression analysis

## 位置づけ
- この artifact は `iss-00241` の PR 作成後に発見された `guidance issue-execution` step selection regression の source-grounded research evidence である。
- canonical authority ではない。修正として採用する場合は、`report.md` の Decision / Evidence Adoption Ledger と実装・テストに反映する。
- deep-consultant `019f08cc-4816-7602-9e4a-8fe043bbbd13` の read-only 分析と、main orchestrator の local source inspection を統合した。

## 調査目的 (必須)
- `./spec-dock/scripts/spec-dock guidance issue-execution` が、`report.md` 上では S01〜S99 の完了証跡があるにもかかわらず `selected_step: S01` を返し続ける根本原因を特定する。
- この不具合が `iss-00241` の追加修正範囲か、別 Issue に切り出すべきかを判断する。
- 修正時に採るべき最小かつ堅牢な設計方針と regression tests を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `spec-dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - `tests/cli_runtime/test_workflow.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock guidance issue-execution` を実行し、現在の `selected_step` を確認した。
  - active issue の `plan.md` / `report.md` に S01〜S99 の step と完了証跡が存在するか確認した。
  - provider source と dogfooding mirror の `context_packets.py` を `diff -u` で比較した。
  - `_select_step()` / `_completed_step_ids()` / `_block_has_completed_step*()` の完了判定を読んだ。
  - 既存 tests がどの report 形式を期待しているか確認した。
  - deep-consultant に read-only 分析を依頼し、独立見解を得た。
- 実験条件:
  - repo: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
  - branch: `iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps`
  - active issue: `iss-00241`
  - latest observed head: `5affb8cc178105356e67cb191e409617446ce51c`

## facts / 観測できた事実 (必須)
- `guidance issue-execution` の実行結果は `state: ready` / `next_action: execution-ready` / `selected_step: S01` である。
- active `report.md` には S01〜S04、S90、S99 の Step Contract Closure、Reviewer Gate Status、Step Commit Gate が記録されている。
- active `report.md` の Step Commit Gate では S01〜S99 が `committed` として記録されている。
- active `plan.md` には S01〜S04、S90、S99 が実装 / docs / final quality gate step として定義されている。
- provider source の `_completed_step_ids()` は `### セッションログ（...）` block を探し、その block 内の completion table を完了判定の主要入力にしている。
- dogfooding mirror の `_completed_step_ids()` も `### セッションログ（...）` block だけを走査する。
- 今回の active `report.md` の主要完了台帳は `### Step Contract Closure`、`### Reviewer Gate Status`、`### Step Commit Gate` として session block 外にある。
- `Reviewer Gate Status` の step cell は `S01 code review` のような複合ラベルであり、単純な first-cell equals `S01` 前提では読めない。
- provider source と dogfooding mirror の `context_packets.py` は一致していない。step heading regex、S90/S99 skip、completion gate 判定、runtime evidence 判定に差分がある。
- 実際に `./spec-dock/scripts/spec-dock ...` で動くのは dogfooding mirror 側である一方、shipped implementation source of truth は provider 側 `src/spec_dock/assets/spec_dock/...` である。
- 既存 `tests/cli_runtime/test_workflow_context_routing.py` は、セッションログ内の `#### ステップ契約の完了証跡` だけで S01 を skip して S02 を選ぶ fixture を持つ。一方、今回の active report と同じ global gate ledger 形式の regression はない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 根本原因は、step completion parser が canonical report の実際の完了台帳形式を十分に読めないことである。
  - `guidance issue-execution` は step-by-step operation authority として使われる想定だったが、現状では完了済み step を S01 と誤選択するため、その運用は成立していない。
  - これは `iss-00241` の S99 manual validation が主張した guidance / Issue execution behavior coverage を直接崩すため、同 Issue 内で修正するのが妥当である。
  - provider / dogfooding mirror drift は、今回の問題の検出・修正を難しくしている副次原因である。修正時は provider first で直し、dogfooding mirror を同期する必要がある。
- 推測の根拠:
  - `guidance issue-execution` の stdout と `spec-dock/.agent/context-packets/current-context-packets.json` は、どちらも `selected_step.id == S01` を示している。
  - `report.md` の Step Commit Gate には S01〜S99 の `committed` が存在するため、完了証跡そのものが欠落しているわけではない。
  - `_completed_step_ids()` は session block を起点にしており、global `### Step Commit Gate` section を completion source として直接走査していない。
  - deep-consultant も同じ根本原因と修正方向を指摘した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 修正後に `guidance issue-execution` が全 step completed をどの state / next_action として表現すべきかの最終仕様。
  - `workflow_issue.md` へ「全 step 完了時の guidance 表示」を明示する必要があるか。
  - issue finish 前 / PR merge-prepared 後の状態を `guidance issue-execution` がどこまで案内すべきか。
- 確認できない理由:
  - 現行 runtime には `all_steps_completed` などの明示 state がまだなく、仕様決定と実装が必要である。
  - PR merge-preparer skill は open PR 段階で `issue finish` を禁止しており、final delivery と issue lifecycle close の境界を runtime guidance にどう出すかは設計判断が必要である。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 全 step 完了後、active issue がまだ PR open の場合に `guidance issue-execution` は `all-steps-completed-pr-open` のように PR 観測 / human merge を案内すべきか。
  - `issue finish` 可能な条件を runtime guidance に含めるか、引き続き workflow skill / PR merge-preparer 側に委ねるか。
- pressure-test question として切り出すべき候補:
  - 完了 step の判定は Step Contract Closure + Reviewer Gate Status + Step Commit Gate の conjunction を必須にするべきか。
  - reviewer gate row が `S01 code review` / `S99 final QA review` など複合ラベルの場合、first cell から step id を抽出してよいか。
- 質問せずに解決できた候補:
  - この不具合を `iss-00241` 内で直すべきかどうか: Issue の目的と S99 manual validation scope に直結するため、この Issue 内で修正するのが妥当。
  - provider と dogfooding mirror のどちらを source of truth とするか: repo guidelines により provider 側 `src/spec_dock/assets/spec_dock/...` を先に修正し、dogfooding mirror を同期する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `issue_wide_default`
  - `workflow-plan-unselectable`
  - `all steps completed`
- 既存 docs / code / tests / discussions での使われ方:
  - 現行 code では selectable step がない場合に `issue_wide_default` が返り、`workflow.py` で `workflow-plan-unselectable` に変換される。
  - しかし selectable step がない理由には「plan が不備で step を抽出できない」と「全 step が完了済みで次に実装 step がない」の 2 種類がある。
  - 現行実装はこの 2 つを区別していない。
- 判断が必要な理由:
  - 全 step 完了時に plan 修正を促すと、実際には完了済みなのに agent が誤った修正作業へ誘導される。
  - `guidance` を step-by-step operational authority とするなら、全完了状態は明示的に別 state / reason_code として表現する必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Step Contract Closure は `pass`、Reviewer Gate Status は `failed`、Step Commit Gate は `committed` の場合。
  - Step Contract Closure は `pass`、Reviewer Gate Status は `passed`、Step Commit Gate は `pending` の場合。
  - Reviewer Gate Status の first cell が `S01 code review` のような複合ラベルの場合。
  - S90 / S99 の見出しが `### ドキュメント影響の解消ステップ S90` / `### 最終品質ゲートステップ S99` のように `実装ステップ Sxx` ではない場合。
  - 全 step が完了している場合。
  - report に session-local gate と global gate の両方があり、片方が stale な場合。
- その edge case が requirement / design / plan に与える影響:
  - step completion parser は `pass` 断片だけで false pass してはいけない。
  - completion 判定は少なくとも Step Contract Closure / Reviewer Gate Status / Step Commit Gate の 3 gate を統合して見る必要がある。
  - row label から step id を抽出できるようにしつつ、`failed` / `blocked` / `denied` / `unavailable` / `stale` / `provisional` / `pending` を未完了として扱う必要がある。
  - S90 / S99 も plan 上の selectable step として扱える必要がある。
  - 全 step 完了時は S01 に戻らず、別の completion state を返す必要がある。

## implications / 判断への含意 (必須)
- `iss-00241` の追加修正として扱うべきである。別 Issue へ defer すると、`guidance issue-execution` を使う step-by-step operation の成立性をこの Issue で閉じたとは言えない。
- 修正は provider source `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py` を正本として行い、dogfooding mirror `spec-dock/scripts/spec_dock_runtime/application/context_packets.py` を同期する。
- regression tests は `tests/cli_runtime/test_workflow_context_routing.py` に追加するのが最も自然である。理由は、現在の `guidance issue-execution` の selected step / context packet projection を E2E に近い形で検証しているため。
- `tests/unit/infra/test_init_update.py` の provider / dogfooding parity 検査も必要に応じて更新し、runtime drift を検知できるようにする。
- 最小修正でも global gate section scan は必要である。ただし推奨は、見出し階層に依存しすぎない小さな section-aware parser とし、row label から step id を抽出し、3 gate conjunction で完了判定する方針である。

## リスク/制約 (任意)
- Markdown report parser を過度に汎用化すると実装が膨らむため、新依存や大きな Markdown AST parser は導入しない。
- 一方で first-cell exact match / session-only scan のままでは再発するため、section heading と table row を少し堅牢に読む必要がある。
- 全 step 完了時の runtime output は、既存 `issue_wide_default` と混ぜると誤誘導になる。明示 state / reason_code の追加が望ましい。

## 反映先 (任意)
- reflected_to:
  - `spec-dock/active/issue/report.md` の Decision / Evidence Adoption Ledger
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `spec-dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - 必要に応じて `tests/unit/infra/test_init_update.py`

## 参考（References） (任意)
- local command result: `./spec-dock/scripts/spec-dock guidance issue-execution` -> `selected_step: S01`
- deep-consultant `019f08cc-4816-7602-9e4a-8fe043bbbd13`: root cause and recommended repair analysis
- active issue `plan.md`: S01〜S04 / S90 / S99 step definitions
- active issue `report.md`: Step Contract Closure / Reviewer Gate Status / Step Commit Gate
