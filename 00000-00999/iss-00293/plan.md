---
種別: 実装計画書（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — 実装計画

## 位置づけ

この計画は、`epic-00283` の最後に実行する品質ゲート / 手動テスト / Pull Request 作成計画です。先行 Issue では PR を作成せず、`iss-00284` から `iss-00292` までを順番に完了させた後、この Issue で Epic 全体の統合確認と mergeable PR 作成を行います。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。ただし、この Issue は Epic 全体の品質ゲート、手動テスト、PR 作成、CI / review 修正、mergeable 確認を担当するため、strict 相当の追加 obligation を持ちます。execution-ready と扱うには、先行 Issue の完了証跡、manual test evidence、fresh `spec-reviewer` result を `report.md` に残します。

## 実装ステップ

1. `./spec-dock/scripts/spec-dock active show` と関連 Issue の `report.md` を確認し、`iss-00284` から `iss-00292` までの完了状態を確認する。
2. `git status --short` と差分を確認し、Epic 外の混入変更がないかを確認する。
3. `./spec-dock/scripts/spec-dock validate` を実行し、SpecDock 構造が壊れていないことを確認する。
4. 実装変更の範囲に応じて、最小の関連自動テストを実行する。必要に応じて `uv run pytest tests/unit`、`uv run pytest tests/cli_runtime`、または対象テストを選ぶ。
5. Epic の manual test matrix を実行し、preflight、safe review、diff/staging、profile validation、dogfood scenario、documentation/metrics の観点を確認する。
6. 失敗、レビュー指摘、手動テストで見つかった不具合をこの Issue の `report.md` に記録し、Epic スコープ内で最小修正する。
7. 修正後に関連検証を再実行し、再検証結果を `report.md` に残す。
8. Pull Request を作成または更新し、PR URL、base/head、CI 状態、review 状態を記録する。
9. PR が mergeable でない場合は、ブロッカーを修正して再 push し、mergeable になるまで確認ループを回す。
10. Epic `report.md` に最終品質ゲート、manual test evidence、PR URL、mergeable status、残課題を追記する。


## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | purpose | maps to | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | 先行 Issue 完了と scope isolation を確認する | AC-001 / AC-002 | `iss-00284`〜`iss-00292` report、`git status --short` | 先行 Issue の完了証跡と Epic 外混入なしを説明できる | `report.md` の Closure Evidence Ledger |
| tc-002 | S02 | 構造検証と関連自動テストを実行する | AC-003 | `spec-dock validate`、`git diff --check`、関連 pytest | 実行結果が pass、または blocker と次アクションが明確 | `report.md` の実行証跡 |
| tc-003 | S03 | Epic manual test matrix を実行する | AC-004 / AC-005 | manual test evidence、失敗時の修正 / 再検証記録 | preflight / safe review / staging / profile / dogfood / docs / metrics を確認済み | `report.md` の manual test evidence |
| tc-004 | S04 | PR 作成、CI / review 修正、mergeable 確認を行う | AC-006 / AC-007 | PR URL、base/head、CI、review、mergeable status | PR が mergeable、または blocker と次アクションが明確 | `report.md` と Epic `report.md` |
| tc-005 | S90 | docs impact と report ledger を解消する | AC-008 | Epic / Issue report 更新、docs impact no-op または更新 | final evidence が canonical reports に残っている | `report.md` の Docs Impact / EAL |
| tc-006 | S99 | final QA / code / spec gate を閉じる | AC-009 | fresh reviewer results、再 push / 再検証結果 | P0/P1 blocker がない | `report.md` の Final Gate |

## ステップ別実行契約

- S01:
  - 担当: main orchestrator。
  - close 条件: 先行 Issue の report と `issue finish` 状態を確認し、Epic 外の混入変更がないことを記録する。
  - closure id: `tc-001`。
- S02:
  - 担当: main orchestrator または QA worker。
  - close 条件: 構造検証、差分検査、関連自動テストの結果を report に残す。
  - closure id: `tc-002`。
- S03:
  - 担当: main orchestrator / QA worker。
  - close 条件: Epic manual test matrix を実行し、失敗時は最小修正と再検証を記録する。
  - closure id: `tc-003`。
- S04:
  - 担当: main orchestrator。
  - close 条件: PR URL、base/head、CI、review、mergeable status を記録し、未解消 blocker を隠さない。
  - closure id: `tc-004`。
- S90:
  - 担当: main orchestrator。
  - close 条件: Epic / Issue report と docs impact を解消し、最終証跡を canonical reports に反映する。
  - closure id: `tc-005`。
- S99:
  - 担当: main orchestrator と fresh reviewers。
  - close 条件: final QA / code / spec reviewer が fresh pass、または blocker と次アクションが明確である。
  - closure id: `tc-006`。


## 委任契約（Delegation Contract）

| step | delegated role | input docs | allowed paths | forbidden changes | acceptance criteria | required tests or docs-only verification | reviewer focus | stop conditions | output required | report destination | amendment trigger | step gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | main orchestrator | Epic docs, `iss-00284`〜`iss-00292` reports, git status | inspect-only; `iss-00293/report.md`; Epic `report.md` summary | source edits, unrelated docs cleanup, PR creation before scope is clean | AC-001 / AC-002 | `git status --short`; prior Issue report inspection | prior closure, scope isolation | incomplete prior Issue, dirty unrelated change | prior Issue completion matrix | `iss-00293/report.md` Closure Evidence Ledger | prior Issue incomplete or scope changes | S01 closed before S02 |
| S02 | qa-reviewer / main orchestrator | final diff, repo commands, prior Issue evidence | `iss-00293/report.md`; bounded fixes in prior allowed paths only if blocker found | broad refactor, unplanned features, `.assurance.json` mutation | AC-003 | `spec-dock validate`, `git diff --check`, relevant pytest | structural validity, regression risk | failing command or test without bounded fix path | command outputs and disposition | `iss-00293/report.md` execution evidence | new failure requiring design/plan amendment | S02 closed before S03 |
| S03 | qa-reviewer / main orchestrator | Epic manual test matrix, outputs from S02 | manual evidence artifacts, `iss-00293/report.md`, Epic `report.md` | skipping required scenario, claiming unexecuted manual tests | AC-004 / AC-005 | manual test matrix; scenario-by-scenario evidence | preflight/safety/staging/profile/dogfood/docs/metrics coverage | missing scenario, ambiguous result | manual test evidence and defects | `iss-00293/report.md`; Epic `report.md` | new dogfood failure mode | S03 closed before S04 |
| S04 | main orchestrator | PR branch, final diff, CI/review status | PR metadata/report updates; bounded fixes in prior allowed paths | unrelated GitHub changes, force-push/destructive actions, hiding CI/review failures | AC-006 / AC-007 | PR URL, base/head, CI, review, mergeable status | PR readiness, repair loop integrity | PR blocked, CI failure, review P0/P1 | PR URL and status ledger | `iss-00293/report.md`; Epic `report.md` | blocker outside Epic scope | S04 closed before S90 |
| S90 | main orchestrator / doc-writer | S01〜S04 evidence, Epic report, Issue reports | Epic `report.md`, `iss-00293/report.md`, docs only for direct contradiction | broad docs cleanup, changing earlier Issue decisions without evidence | AC-008 | docs/report impact inspection; `spec-dock validate` | final ledger completeness | stale or contradictory report | docs impact decision and EAL updates | `iss-00293/report.md`; Epic `report.md` | canonical docs need amendment | S90 closed before S99 |
| S99 | main orchestrator + fresh reviewers | all closure evidence, PR status, final diff | final reports; bounded fixes in previously allowed paths only | new feature work, unreviewed scope expansion, merge claim without evidence | AC-009 | fresh spec/code/QA review as needed; final command evidence | no P0/P1 blocker, residual risk clarity | any P0/P1 finding or stale reviewer | final gate result and completion recommendation | `iss-00293/report.md`; Epic `report.md` | reviewer requires plan/design change | Epic PR-ready only after S99 |

## 具体テストケース一覧

| test id | step | kind | concrete case | expected result | evidence path |
|---|---|---|---|---|---|
| tc-001-a | S01 | inspect | `iss-00284`〜`iss-00292` の completion/report evidence と `git status --short` を確認する | prior issue completion and scope isolation are recorded | `iss-00293/report.md` Closure Evidence Ledger |
| tc-002-a | S02 | command | `./spec-dock/scripts/spec-dock validate` と `git diff --check` を実行する | both pass or blocker disposition is recorded | `iss-00293/report.md` execution evidence |
| tc-002-b | S02 | focused test | 実装範囲に応じた pytest を選択して実行、または docs-only no-op rationale を残す | pass or explicit blocker | `iss-00293/report.md` execution evidence |
| tc-003-a | S03 | manual matrix | preflight / safe review / diff-staging / profile / dogfood / docs / metrics の manual matrix を確認する | each scenario has pass/fail evidence | manual test evidence artifact; `iss-00293/report.md` |
| tc-004-a | S04 | PR readiness | PR URL、base/head、CI、review、mergeable status を確認する | PR is mergeable or blocker is explicit | `iss-00293/report.md`; Epic `report.md` |
| tc-005-a | S90 | docs impact | Epic / Issue reports と docs impact を確認する | final reports are coherent and no stale ledger remains | `iss-00293/report.md`; Epic `report.md` |
| tc-006-a | S99 | final gate | fresh reviewer results and closure ids are checked | P0/P1 blocker absent or next action explicit | final gate ledger |

### S90 ドキュメント影響解消

- 最終品質ゲートで変わった仕様、計画、運用方針は Epic / Issue report に反映する。
- 仕様変更を伴う場合は、該当 Issue の requirement / design / plan へ戻って再レビューする。
- PR 作成や CI / review 状態を、実行していない場合に実施済みとして記録しない。

### S99 最終品質ゲート

- 前提: S01〜S04 と S90 が closed または approved no-op である。
- 必須確認: fresh `spec-reviewer`、必要に応じた code / QA reviewer、CI / review / mergeable 状態。
- P0/P1 finding はこの Issue 内で最小修正し、再検証、再 push、再レビュー結果を記録する。

## Final Exit Contract

- 先行 Issue の完了証跡が揃っている。
- Spec-Locked Closure Index の required closure id が `pass` または valid approved-no-op として `report.md` に記録されている。
- manual test evidence、PR URL、CI / review / mergeable status が canonical reports に残っている。
- Epic `report.md` が最終品質ゲート結果と残リスクを反映している。
- P0/P1 blocker がない、または未解決 blocker と次アクションが明確である。

## リレー実行 / PR 方針

- この Issue は、この Epic で Pull Request を作成または更新する唯一の Issue である。
- `iss-00292` の完了後に `./spec-dock/scripts/spec-dock issue start iss-00293` で開始する。
- 先行 Issue では PR を作成しない。各 Issue の完了証跡は `report.md` と `issue finish` に集約する。
- PR 作成後に CI、レビュー、手動テストで不具合が見つかった場合、この Issue の作業として修正、再検証、再 push を行う。
- mergeable にならない場合は、残ブロッカー、再現条件、次アクションを明記する。

## 検証計画

- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`
- 実装範囲に応じた関連 pytest。
- Epic manual test matrix。
- GitHub PR の CI / review / mergeable 状態確認。

## 完了条件

- 先行 Issue すべての完了証跡が確認されている。
- `spec-dock validate` と必要な関連テストの結果が記録されている。
- manual test evidence が作成されている。
- PR が作成または更新され、GitHub に push 済みである。
- P0/P1 相当の品質ゲート不具合とレビュー指摘が解消されている。
- PR が mergeable である、または未解決ブロッカーと次アクションが明確である。
- Epic `report.md` とこの Issue `report.md` に最終証跡が残っている。
