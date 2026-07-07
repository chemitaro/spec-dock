---
種別: 実装計画書（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — 実装計画

## 位置づけ

この計画は、`epic-00283` の最後に実行する品質ゲート / 手動テスト / Pull Request 作成計画です。先行 Issue では PR を作成せず、`iss-00284` から `iss-00292` までを順番に完了させた後、この Issue で Epic 全体の統合確認と mergeable PR 作成を行います。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。ただし、この Issue は Epic 全体の品質ゲート、手動テスト、PR 作成、CI / review 修正、mergeable 確認を担当するため、strict 相当の追加 obligation を持ちます。execution-ready と扱うには、先行 Issue の完了証跡、manual test evidence、fresh `spec-reviewer`、issue-wide `code-reviewer`、`qa-reviewer` の三者 final gate result を `report.md` に残します。

追加のユーザー補足により、この Issue は Pull Request 作成前に ChatGPT Use / Oracle 実行まわりの個人環境絶対パス依存を解消する責務を持つ。SpecDock repo 側は Oracle 本体を同梱せず、`SPECDOCK_CHATGPT_COMMAND` を第一候補、`ORACLE_CHATGPT_COMMAND` を互換 fallback とする backend command adapter / invocation contract を実装または検証し、未設定時の fail-closed と設定時の command 解決を final gate 対象に含める。

## 実装ステップ

1. `./spec-dock/scripts/spec-dock active show` と関連 Issue の `report.md` を確認し、`iss-00284` から `iss-00292` までの完了状態を確認する。
2. `git status --short` と差分を確認し、Epic 外の混入変更がないかを確認する。
3. `./spec-dock/scripts/spec-dock validate` を実行し、SpecDock 構造が壊れていないことを確認する。
4. 実装変更の範囲に応じて、最小の関連自動テストを実行する。必要に応じて `uv run pytest tests/unit`、`uv run pytest tests/cli_runtime`、または対象テストを選ぶ。
5. PR 作成前に ChatGPT backend command adapter / invocation contract を確認し、必要なら実装する。未設定時は明確なエラーで fail し、設定時は指定 backend command を利用できることを検証する。
6. Epic の manual test matrix を実行し、preflight、safe review、diff/staging、profile validation、dogfood scenario、documentation/metrics、backend command adapter の観点を確認する。
7. 失敗、レビュー指摘、手動テストで見つかった不具合をこの Issue の `report.md` に記録し、Epic スコープ内で最小修正する。
8. 修正後に関連検証を再実行し、再検証結果を `report.md` に残す。
9. Pull Request を作成または更新し、PR URL、base/head、CI 状態、review 状態を記録する。
10. PR が mergeable でない場合は、ブロッカーを修正して再 push し、mergeable になるまで確認ループを回す。
11. Epic `report.md` に最終品質ゲート、manual test evidence、backend command adapter evidence、PR URL、mergeable status、残課題を追記する。


## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | purpose | maps to | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | 先行 Issue 完了と scope isolation を確認する | AC-001 | `iss-00284`〜`iss-00292` report、`git status --short` | 先行 Issue の完了証跡と Epic 外混入なしを説明できる | `report.md` の Closure Evidence Ledger |
| tc-002 | S02 | 構造検証と関連自動テストを実行する | AC-002 / AC-003 | `spec-dock validate`、`git diff --check`、関連 pytest | 実行結果が pass、または blocker と次アクションが明確 | `report.md` の実行証跡 |
| tc-003 | S03 | Epic manual test matrix を実行する | AC-004 | manual test evidence、失敗時の修正 / 再検証記録 | preflight / safe review / staging / profile / dogfood / docs / metrics を確認済み | `report.md` の manual test evidence |
| tc-004 | S04 | ChatGPT backend command adapter / invocation contract を検証する | AC-011 / AC-012 / AC-013 | adapter 実装または既存実装確認、未設定 fail-closed、設定時 command 解決、絶対パス非直書き確認 | PR 作成前に backend command 依存が設定差し替え可能で、未設定時は明確に fail する | `report.md` の backend adapter evidence |
| tc-005 | S05 | PR 作成、CI / review 修正、mergeable 確認を行う | AC-005 / AC-006 / AC-007 | PR URL、base/head、CI、review、mergeable status | PR が mergeable、または blocker と次アクションが明確 | `report.md` と Epic `report.md` |
| tc-006 | S90 | docs impact と report ledger を解消する | AC-008 / AC-010 | Epic / Issue report 更新、docs impact no-op または更新 | final evidence が canonical reports に残っている | `report.md` の Docs Impact / EAL |
| tc-007 | S99 | final QA / code / spec gate を閉じる | AC-009 | fresh reviewer results、再 push / 再検証結果 | P0/P1 blocker がない | `report.md` の Final Gate |

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
  - 担当: main orchestrator または dev-coder。
  - close 条件: ChatGPT backend command adapter / invocation contract を実装または確認し、未設定時の fail-closed、設定時の command 解決、個人環境絶対パス非直書きを検証する。
  - closure id: `tc-004`。
- S05:
  - 担当: main orchestrator。
  - close 条件: PR URL、base/head、CI、review、mergeable status を記録し、未解消 blocker を隠さない。
  - closure id: `tc-005`。
- S90:
  - 担当: main orchestrator。
  - close 条件: Epic / Issue report と docs impact を解消し、最終証跡を canonical reports に反映する。
  - closure id: `tc-006`。
- S99:
  - 担当: main orchestrator と fresh reviewers。
  - close 条件: fresh `spec-reviewer`、issue-wide `code-reviewer`、`qa-reviewer` がすべて pass、または blocker と次アクションが明確である。
  - closure id: `tc-007`。


## 委任契約（Delegation Contract）

| step | delegated role | input docs | allowed paths | forbidden changes | acceptance criteria | required tests or docs-only verification | reviewer focus | stop conditions | output required | report destination | amendment trigger | step gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | main orchestrator | Epic docs, `iss-00284`〜`iss-00292` reports, git status | inspect-only; `iss-00293/report.md`; Epic `report.md` summary | source edits, unrelated docs cleanup, PR creation before scope is clean | AC-001 / AC-002 | `git status --short`; prior Issue report inspection | prior closure, scope isolation | incomplete prior Issue, dirty unrelated change | prior Issue completion matrix | `iss-00293/report.md` Closure Evidence Ledger | prior Issue incomplete or scope changes | S01 closed before S02 |
| S02 | qa-reviewer / main orchestrator | final diff, repo commands, prior Issue evidence | `iss-00293/report.md`; bounded fixes in prior allowed paths only if blocker found | broad refactor, unplanned features, `.assurance.json` mutation | AC-003 | `spec-dock validate`, `git diff --check`, relevant pytest | structural validity, regression risk | failing command or test without bounded fix path | command outputs and disposition | `iss-00293/report.md` execution evidence | new failure requiring design/plan amendment | S02 closed before S03 |
| S03 | qa-reviewer / main orchestrator | Epic manual test matrix, outputs from S02 | manual evidence artifacts, `iss-00293/report.md`, Epic `report.md` | skipping required scenario, claiming unexecuted manual tests | AC-004 | manual test matrix; scenario-by-scenario evidence | preflight/safety/staging/profile/dogfood/docs/metrics coverage | missing scenario, ambiguous result | manual test evidence and defects | `iss-00293/report.md`; Epic `report.md` | new dogfood failure mode | S03 closed before S04 |
| S04 | main orchestrator / dev-coder | backend invocation contract, existing authoring-pack scripts, user supplemental requirement | `scripts/authoring-pack/**`, `tests/manual_tests/**`, `iss-00293/report.md`, Epic `report.md` | bundling Oracle/ChatGPT automation, hardcoding personal absolute paths, broad runtime promotion, `.assurance.json` mutation | AC-011 / AC-012 / AC-013 | unset-command fail-closed test, configured-command resolution test, `rg` absolute-path guard, focused pytest | portability, clear error, no local wrapper dependency | backend command cannot be configured, missing clear error, local wrapper path is required | adapter implementation/evidence and verification output | `iss-00293/report.md`; Epic `report.md` | contract requires runtime promotion outside this Epic | S04 closed before S05 |
| S05 | main orchestrator | PR branch, final diff, CI/review status | PR metadata/report updates; bounded fixes in prior allowed paths | unrelated GitHub changes, force-push/destructive actions, hiding CI/review failures | AC-005 / AC-006 / AC-007 | PR URL, base/head, CI, review, mergeable status | PR readiness, repair loop integrity | PR blocked, CI failure, review P0/P1 | PR URL and status ledger | `iss-00293/report.md`; Epic `report.md` | blocker outside Epic scope | S05 closed before S90 |
| S90 | main orchestrator / doc-writer | S01〜S05 evidence, Epic report, Issue reports | Epic `report.md`, `iss-00293/report.md`, docs only for direct contradiction | broad docs cleanup, changing earlier Issue decisions without evidence | AC-008 / AC-010 | docs/report impact inspection; `spec-dock validate` | final ledger completeness | stale or contradictory report | docs impact decision and EAL updates | `iss-00293/report.md`; Epic `report.md` | canonical docs need amendment | S90 closed before S99 |
| S99 | main orchestrator + fresh reviewers | all closure evidence, PR status, final diff | final reports; bounded fixes in previously allowed paths only | new feature work, unreviewed scope expansion, merge claim without evidence | AC-009 | fresh `spec-reviewer`, issue-wide `code-reviewer`, `qa-reviewer`; final command evidence | no P0/P1 blocker, residual risk clarity | any P0/P1 finding or stale reviewer | final gate result and completion recommendation | `iss-00293/report.md`; Epic `report.md` | reviewer requires plan/design change | Epic PR-ready only after S99 |

## 具体テストケース一覧

- `tc-s01-00293-001` inspect: `iss-00284`〜`iss-00292` の completion evidence を確認する
  - 前提: 各 child Issue の `report.md`、Closure Evidence Ledger、Final Gate が読める。
  - 操作: `iss-00284`〜`iss-00292` の required closure id が pass または approved no-op であるか確認する。
  - 期待結果: prior Issue completion matrix と未完了 blocker が `iss-00293/report.md` に記録される。
  - 失敗検出: 未完了 Issue や stale report を完了済みとして最終 PR へ進める回帰を検出する。
  - 検証方法: report inspection、`git status --short`、Closure Evidence Ledger 確認。
  - 関連 closure id: `tc-001`

- `tc-s02-00293-001` command: spec-dock 構造検証を実行する
  - 前提: child Issue の修正がすべて working tree に反映されている。
  - 操作: `./spec-dock/scripts/spec-dock validate` を実行する。
  - 期待結果: command は成功し、失敗時は blocker disposition と bounded fix path が report に残る。
  - 失敗検出: 構造不整合や stale projection を見逃して PR-ready とする回帰を検出する。
  - 検証方法: command output を `iss-00293/report.md` execution evidence に記録する。
  - 関連 closure id: `tc-002`

- `tc-s02-00293-002` command: diff whitespace / patch hygiene を確認する
  - 前提: final diff が存在する。
  - 操作: `git diff --check` を実行する。
  - 期待結果: whitespace error や patch hygiene failure がない、または blocker disposition が明示される。
  - 失敗検出: trailing whitespace や malformed patch を残したまま PR を作る回帰を検出する。
  - 検証方法: command output を `iss-00293/report.md` execution evidence に記録する。
  - 関連 closure id: `tc-002`

- `tc-s02-00293-003` inspect: focused pytest または docs-only no-op rationale を固定する
  - 前提: final diff に runtime / tests / docs-only の変更種別がある。
  - 操作: 実装範囲に応じた focused pytest を選ぶか、docs-only no-op rationale を記録する。
  - 期待結果: 未実行テストを実施済みと主張せず、必要な focused verification が明示される。
  - 失敗検出: docs-only 変更なのに不明な pytest pass を主張する、または runtime 変更なのに test が欠落する回帰を検出する。
  - 検証方法: command output または no-op rationale inspection。
  - 関連 closure id: `tc-002`

- `tc-s03-00293-001` manual: manual matrix の各 scenario を確認する
  - 前提: preflight、safe review、diff-staging、profile、dogfood、docs、metrics の manual matrix がある。
  - 操作: 各 scenario の pass/fail evidence、未実施理由、blocker を scenario-by-scenario に確認する。
  - 期待結果: coverage gap がある場合は明示され、実施していない manual test を pass としない。
  - 失敗検出: manual matrix の一部 scenario が空欄のまま Epic 完了扱いになる回帰を検出する。
  - 検証方法: manual evidence artifact inspection と `iss-00293/report.md` 記録。
  - 関連 closure id: `tc-003`

- `tc-s04-00293-001` command: ChatGPT backend command 未設定時に fail-closed する
  - 前提: `SPECDOCK_CHATGPT_COMMAND` と `ORACLE_CHATGPT_COMMAND` が未設定である。
  - 操作: backend command adapter / invocation contract を呼び出す。
  - 期待結果: 個人環境の wrapper path を推測せず、設定が必要であることを示す明確なエラーで失敗する。
  - 失敗検出: 未設定時に `/Users/...` などのローカル絶対パスへフォールバックする回帰を検出する。
  - 検証方法: focused pytest または adapter の dry-run / no-op command output。
  - 関連 closure id: `tc-004`

- `tc-s04-00293-002` command: 設定された backend command を解決する
  - 前提: `SPECDOCK_CHATGPT_COMMAND` または `ORACLE_CHATGPT_COMMAND` にテスト用 command が指定されている。
  - 操作: backend command adapter / invocation contract を呼び出す。
  - 期待結果: 指定された command を backend として扱い、SpecDock repo に Oracle / ChatGPT automation 本体を要求しない。
  - 失敗検出: 設定値を無視する、または個人環境 path を必須依存として扱う回帰を検出する。
  - 検証方法: focused pytest または adapter の dry-run / no-op command output。
  - 関連 closure id: `tc-004`

- `tc-s04-00293-003` inspect: 個人環境 wrapper の絶対パス非直書きを確認する
  - 前提: final diff が存在する。
  - 操作: repo 内の正式ワークフロー / スクリプト対象に対して、個人環境 wrapper path が直書きされていないことを確認する。
  - 期待結果: 既存のローカル `oracle-chatgpt` wrapper は設定例としてのみ扱われ、正式ワークフローの必須 path ではない。
  - 失敗検出: 個人環境固有の ChatGPT Use / Oracle wrapper 絶対パスを必須 path として commit する回帰を検出する。
  - 検証方法: `rg` guard と focused review。
  - 関連 closure id: `tc-004`

- `tc-s05-00293-001` pr-readiness: PR URL / base / head / CI / review / mergeable status を確認する
  - 前提: final branch に PR 作成または更新の準備がある。
  - 操作: PR URL、base/head、CI、review、mergeable status を確認し、repair loop が必要か判断する。
  - 期待結果: PR は mergeable または blocker が explicit で、実行していない CI / review を成功済みと書かない。
  - 失敗検出: PR 未作成・CI 未確認のまま mergeable と主張する回帰を検出する。
  - 検証方法: PR metadata inspection、GitHub / local report evidence。
  - 関連 closure id: `tc-005`

- `tc-s90-00293-001` inspect: Epic / Issue reports の最終整合を確認する
  - 前提: final gate の command evidence、manual matrix、PR status がある。
  - 操作: Epic report、`iss-00293/report.md`、child Issue reports に stale ledger や矛盾がないか確認する。
  - 期待結果: final reports are coherent で、docs impact は update または approved no-op として記録される。
  - 失敗検出: 過去の candidate / draft / blocked 状態が現状と矛盾して残る回帰を検出する。
  - 検証方法: docs-only inspection と `rg`。
  - 関連 closure id: `tc-006`

- `tc-s99-00293-001` final-gate: fresh reviewer results と closure ids を確認する
  - 前提: S01〜S05 と S90 が closed または approved no-op である。
  - 操作: fresh `spec-reviewer`、issue-wide `code-reviewer`、`qa-reviewer` をすべて実行し、結果と closure id の状態を確認する。
  - 期待結果: P0/P1 blocker がなく、残る場合は次アクションが explicit である。
  - 失敗検出: stale reviewer result、未確認 closure、未解決 P0/P1 を残して completion-ready とする回帰を検出する。
  - 検証方法: final gate ledger と reviewer result の report 記録。
  - 関連 closure id: `tc-007`

### S90 ドキュメント影響解消

- 最終品質ゲートで変わった仕様、計画、運用方針は Epic / Issue report に反映する。
- 仕様変更を伴う場合は、該当 Issue の requirement / design / plan へ戻って再レビューする。
- PR 作成や CI / review 状態を、実行していない場合に実施済みとして記録しない。

### S99 最終品質ゲート

- 前提: S01〜S05 と S90 が closed または approved no-op である。
- 必須確認: fresh `spec-reviewer`、issue-wide `code-reviewer`、`qa-reviewer`、CI / review / mergeable 状態。
- P0/P1 finding はこの Issue 内で最小修正し、再検証、再 push、再レビュー結果を記録する。

## Final Exit Contract

- 先行 Issue の完了証跡が揃っている。
- Spec-Locked Closure Index の required closure id が `pass` または valid approved-no-op として `report.md` に記録されている。
- manual test evidence、PR URL、CI / review / mergeable status が canonical reports に残っている。
- ChatGPT backend command adapter / invocation contract の未設定 fail-closed、設定時 command 解決、個人環境絶対パス非直書きの証跡が残っている。
- Epic `report.md` が最終品質ゲート結果と残リスクを反映している。
- P0/P1 blocker がない、または未解決 blocker と次アクションが明確である。

## リレー実行 / PR 方針

- この Issue は、この Epic で Pull Request を作成または更新する唯一の Issue である。
- `iss-00292` の完了後に `./spec-dock/scripts/spec-dock issue start iss-00293` で開始する。
- 先行 Issue では PR を作成しない。各 Issue の完了証跡は `report.md` と `issue finish` に集約する。
- PR 作成後に CI、レビュー、手動テストで不具合が見つかった場合、この Issue の作業として修正、再検証、再 push を行う。
- PR 作成前に ChatGPT backend command adapter / invocation contract の検証を完了する。
- mergeable にならない場合は、残ブロッカー、再現条件、次アクションを明記する。

## 検証計画

- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`
- 実装範囲に応じた関連 pytest。
- Epic manual test matrix。
- ChatGPT backend command adapter / invocation contract の focused verification。
- GitHub PR の CI / review / mergeable 状態確認。

## 完了条件

- 先行 Issue すべての完了証跡が確認されている。
- `spec-dock validate` と必要な関連テストの結果が記録されている。
- manual test evidence が作成されている。
- ChatGPT backend command adapter / invocation contract が設定差し替え可能で、未設定時に明確に fail することが確認されている。
- PR が作成または更新され、GitHub に push 済みである。
- P0/P1 相当の品質ゲート不具合とレビュー指摘が解消されている。
- PR が mergeable である、または未解決ブロッカーと次アクションが明確である。
- Epic `report.md` とこの Issue `report.md` に最終証跡が残っている。
