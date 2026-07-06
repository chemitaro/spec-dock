---
種別: 実装計画書（Issue）
ID: "iss-00291"
タイトル: "仕様作成パックのワークフローと採用台帳例を文書化する"
関連GitHub: ["#291"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00291 仕様作成パックのワークフローと採用台帳例を文書化する — 実装計画

## 位置づけ

この `plan.md` は、この Issue の canonical implementation plan です。ChatGPT ZIP 仕様作成パック由来の draft artifact は evidence-only handoff として保持し、main orchestrator が採否判断した内容だけをこの文書に再記述しています。execution-ready と扱うには、この計画への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。この Issue は文書化と採用台帳例に限定し、配布ランタイムや正本採用自動化を行わないため、追加 obligation は standard とします。execution-ready と扱うには、fresh `spec-reviewer` result を `report.md` に残します。

## 実装ステップ

1. 親 Epic の `requirement.md` / `design.md` / `plan.md` と、この Issue の要件定義を読む。
2. 依存関係を確認する: iss-00284, iss-00285, iss-00286。
3. ドッグフード専用ワークフロー、プロンプト規約、権威境界、EAL 例、手動フォールバックを日本語ファーストで文書化する。
4. 成果物を 日本語 README、プロンプト規約案、EAL 例、手動フォールバック notes として作る。
5. 正本ファイルを直接変更せず、検証 report と staged artifact を出す。
6. Evidence Adoption Ledger へ採用候補を引き渡せる形に整える。

## 検証計画

- 正常系 fixture で expected output が作られることを確認する。
- negative fixture で危険な claim、stale source、profile mismatch をブロックする。
- `git status` または差分確認で正本直接上書きがないことを確認する。
- `.assurance.json` が ChatGPT 出力によって変更されていないことを確認する。


## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | purpose | maps to | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | 親 Epic trace と依存 Issue output を確認する | 親 E-RQ / E-AC、依存関係 | 親 docs / 依存 Issue report の確認メモ | 対応する親 trace と依存 output を説明できる | Issue `report.md` の Closure Evidence Ledger |
| tc-002 | S02 | Issue 固有成果物を実装または作成する | Issue AC-001〜AC-004 | 変更差分、生成 artifact、または no-op rationale | 成果物が存在し、正本直接上書きがない | Issue `report.md` の実行証跡 / EAL |
| tc-003 | S03 | 正常系 / negative fixture / safety boundary を検証する | Issue AC-005〜AC-006 | validation report、fixture 結果、`.assurance.json` 差分確認 | pass / blocked / stale / rejected / deferred を区別できる | Issue `report.md` の Closure Evidence Ledger |
| tc-004 | S90 | docs impact と adoption ledger を解消する | docs / report integrity | docs impact 判断、EAL 更新、Closure Delta 有無 | 関連 docs / report の更新または no-op 理由が記録されている | Issue `report.md` の Docs Impact / EAL |
| tc-005 | S99 | final QA / code / spec gate を閉じる | all AC / EC | `spec-dock validate`、関連テスト、fresh reviewer result | P0/P1 blocker がなく、残リスクと次アクションが明確 | Issue `report.md` の Final Gate / Closure Evidence Ledger |

## ステップ別実行契約

- S01:
  - 担当: main orchestrator または委任 worker。
  - close 条件: 親 Epic trace、依存 Issue、local `authorized_profile` を確認し、ChatGPT 推奨で `.assurance.json` を変更していないことを記録する。
  - closure id: `tc-001`。
- S02:
  - 担当: 実装 worker。
  - close 条件: この Issue 固有の成果物を作り、ChatGPT / ZIP / staged artifact が正本を直接上書きしていないことを確認する。
  - closure id: `tc-002`。
- S03:
  - 担当: QA / 実装 worker。
  - close 条件: 正常系 fixture と negative fixture を実行し、validation status を区別して report に残す。
  - closure id: `tc-003`。
- S90:
  - 担当: main orchestrator。
  - close 条件: docs impact、EAL、Spec Authoring Gate、Closure Delta を更新または no-op として記録する。
  - closure id: `tc-004`。
- S99:
  - 担当: main orchestrator と fresh reviewer。
  - close 条件: `spec-dock validate`、必要な関連テスト、fresh `spec-reviewer` result を揃え、P0/P1 blocker を残さない。
  - closure id: `tc-005`。


## 委任契約（Delegation Contract）

| step | delegated role | input docs | allowed paths | forbidden changes | acceptance criteria | required tests or docs-only verification | reviewer focus | stop conditions | output required | report destination | amendment trigger | step gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | main orchestrator / implementation-planner | Epic docs, this Issue `requirement.md` / `design.md` / `plan.md`, `.assurance.json` | inspect-only; this Issue `report.md` for evidence | `.assurance.json` mutation, source/runtime edits, PR creation | parent trace and dependency outputs are understood | docs-only inspection; no command required beyond optional `spec-dock validate` | scope, dependency, local assurance consistency | missing dependency evidence, stale profile, unclear parent trace | S01 evidence row and blocker/no-blocker note | Issue `report.md` Closure Evidence Ledger | parent trace or allowed paths differ from plan | S01 closed before S02 |
| S02 | dev-coder or doc-writer matching touched surface | this Issue `requirement.md`, `design.md`, S01 evidence | `scripts/authoring-pack/README.md`, `spec-dock/docs/**` は直接文書化が必要な場合のみ, this Issue `artifacts/**`, this Issue `report.md` | unrelated initiatives, unrelated Issue docs, `.assurance.json`, direct canonical overwrite by generated ZIP, PR/CI operations | Issue AC-001〜AC-004 and issue-specific deliverables | focused unit/integration/docs-only check selected before edit; `git diff --check` | implementation scope, no authority-boundary regression | outside allowed paths, public contract expansion not in requirement, unsafe ZIP/adoption claim | changed files, generated/staged artifacts, verification result, residual risks | Issue `report.md` execution evidence / EAL | new public command, new persistence, or scope wider than AC | S02 reviewer-ready before S03 |
| S03 | qa-reviewer or dev-coder | S02 output, fixtures, validation report contract | `tests/**`, this Issue `artifacts/**`, this Issue `report.md`; source fixes only if failing test reveals in-scope defect | unrelated refactor, broad fixture rewrite, `.assurance.json` mutation, self-review pass claim | Issue AC-005〜AC-006 and negative fixtures are covered | normal fixture, negative fixture, `spec-dock validate`, `git diff --check`, focused pytest or documented no-op | fail-closed behavior, validation status taxonomy, no canonical overwrite | missing negative fixture, ambiguous validation status, test requires broader design | test output, blocked/stale/rejected/deferred evidence, defect notes | Issue `report.md` Closure Evidence Ledger | new failure mode not covered by design | S03 closed before S90 |
| S90 | main orchestrator / doc-writer | S01〜S03 evidence, Epic docs, workflow docs if touched | this Issue docs/report, Epic report; `spec-dock/docs/**` only for direct contradiction | broad docs cleanup, template changes unrelated to this Issue, historical ledger deletion | docs impact and adoption ledger are resolved | docs-only inspection; `rg` for direct contradictions; `spec-dock validate` | report consistency, EAL/SID/closure integrity | unresolved contradiction or required docs update | docs impact decision, EAL/SID updates or no-op rationale | Issue `report.md`, Epic `report.md` when needed | docs impact changes canonical workflow | S90 closed before S99 |
| S99 | main orchestrator + fresh reviewers | all closure evidence, final diff, reviewer results | this Issue `report.md`, Epic report for summary; bounded fixes only in previously allowed paths | new behavior implementation, PR creation, unrelated cleanup | all required closure ids pass or approved no-op | `spec-dock validate`, `git diff --check`, focused tests from S02/S03, fresh `spec-reviewer` result | final readiness, P0/P1 blocker absence, residual risk clarity | any P0/P1 finding, stale reviewer, missing closure evidence | final gate result, reviewer status, remaining risks | Issue `report.md` Final Gate / Closure Evidence Ledger | reviewer requires plan/design change | Issue completion-ready only after S99 |

## 具体テストケース一覧

- `tc-s01-00291-001` inspect: 文書化対象と runtime 非主張を確認する
  - 前提: `iss-00284`〜`iss-00290` の成果物・validation report・dogfood evidence が読める。
  - 操作: README、プロンプト規約、EAL 例、手動フォールバック notes の入力範囲を確認する。
  - 期待結果: 文書は現時点の dogfood / planned workflow を説明し、配布 runtime command が利用可能だと主張しない。
  - 失敗検出: 未実装ランタイム機能を利用可能な手順として書く回帰を検出する。
  - 検証方法: docs-only inspection と Issue `report.md` Closure Evidence Ledger。
  - 関連 closure id: `tc-001`

- `tc-s02-00291-001` acceptance: 日本語 README に利用手順と境界を書く
  - 前提: workflow の正本 docs と Epic / Issue reports がある。
  - 操作: 日本語 README に preflight、safe review、staging、local adoption、reviewer gate、manual fallback の流れを書く。
  - 期待結果: 日本語話者が ChatGPT output を evidence-only として扱う手順を読める。
  - 失敗検出: ChatGPT output を正本昇格済み、または reviewer pass の代替として扱う記述を検出する。
  - 検証方法: docs diff inspection と `rg` による禁止 claim 確認。
  - 関連 closure id: `tc-002`

- `tc-s02-00291-002` acceptance: プロンプト規約で repo instruction-like text を data として扱う
  - 前提: ChatGPT に渡す prompt pack の禁止 claim と source manifest のルールがある。
  - 操作: プロンプト規約案に、repo 内の instruction-like text は source data として扱い、local authority を上書きしない旨を書く。
  - 期待結果: prompt pack が host instructions、reviewer gate、`.assurance.json` authority を侵食しない。
  - 失敗検出: source 文書内の命令文を ChatGPT が実行権限として解釈する余地を検出する。
  - 検証方法: docs-only inspection、prompt rules artifact inspection。
  - 関連 closure id: `tc-002`

- `tc-s03-00291-001` acceptance: EAL 例が採用状態を区別する
  - 前提: adopted、partially_adopted、rejected、stale、deferred、blocked の例が必要である。
  - 操作: EAL 例を作成し、各 status の意味、必要 evidence、次アクションを分けて書く。
  - 期待結果: reviewer は ChatGPT ZIP output と canonical adoption の差を EAL 例から判断できる。
  - 失敗検出: rejected / stale / blocked を adopted と同じように扱う ledger 例を検出する。
  - 検証方法: EAL example inspection と Issue `report.md` Closure Evidence Ledger。
  - 関連 closure id: `tc-003`

- `tc-s03-00291-002` acceptance: 手動フォールバック notes を用意する
  - 前提: ChatGPT / ZIP generation / GitHub connector が利用不能な場合がある。
  - 操作: 手動 authoring path、blocked / skipped evidence、再開条件を notes に書く。
  - 期待結果: automation が使えない場合でも、local authoring と reviewer gate へ戻れる。
  - 失敗検出: ChatGPT が使えないと Issue planning が停止する手順を検出する。
  - 検証方法: docs-only inspection。
  - 関連 closure id: `tc-003`

- `tc-s90-00291-001` inspect: 文書間の直接矛盾を確認する
  - 前提: README、prompt rules、EAL examples、fallback notes が作成済みである。
  - 操作: workflow docs、Epic docs、Issue docs と直接矛盾がないか確認する。
  - 期待結果: update または approved no-op rationale が記録される。
  - 失敗検出: docs 間で authority boundary や reviewer gate の説明が食い違う回帰を検出する。
  - 検証方法: docs-only inspection と `rg`。
  - 関連 closure id: `tc-004`

- `tc-s99-00291-001` final-gate: docs 検証と fresh reviewer を通す
  - 前提: S01〜S03 と S90 が closed または approved no-op である。
  - 操作: `./spec-dock/scripts/spec-dock validate`、`git diff --check`、docs inspection、fresh `spec-reviewer` result を確認する。
  - 期待結果: P0/P1 blocker がなく、残リスクまたは次アクションが Issue `report.md` Final Gate に記録される。
  - 失敗検出: docs-only verification を未実施のまま完了扱いする回帰を検出する。
  - 検証方法: command output、docs inspection evidence、reviewer result の report 記録。
  - 関連 closure id: `tc-005`

### S90 ドキュメント影響解消

- この Issue の実装が workflow docs、template、README、Epic docs、Issue docs に影響する場合だけ更新する。
- 更新しない場合も、直接矛盾がないことを `report.md` に no-op rationale として残す。
- ChatGPT output、ZIP、staged artifact、reviewer-focus は正本昇格や reviewer pass の代替として記述しない。

### S99 最終品質ゲート

- 前提: S01〜S03 と S90 が closed または approved no-op である。
- 必須確認: `./spec-dock/scripts/spec-dock validate`、`git diff --check`、Issue 固有検証、fresh `spec-reviewer` result。
- reviewer 指摘が出た場合は、bounded fix を行い、Closure Delta と再検証結果を report に残す。

## Final Exit Contract

- Spec-Locked Closure Index の required closure id が `pass` または valid approved-no-op として `report.md` に記録されている。
- `.assurance.json` / `authorized_profile` は ChatGPT 推奨では変更されていない。
- ChatGPT output / ZIP / staged artifact は evidence-only であり、正本直接上書きや self-review pass claim がない。
- S90 docs impact が解消されている。
- S99 final QA / spec reviewer が fresh pass である、または blocker と次アクションが明確である。

## リスク

- ユーザーが provider detail や ChatGPT 出力を正本と誤認するリスクを下げる。
- ChatGPT 出力を正本完了や reviewer pass と誤認するリスク。
- ドッグフード専用の提案が配布ランタイム契約のように読まれるリスク。

## 完了条件

- 日本語 README、プロンプト規約案、EAL 例、手動フォールバック notes が存在する。
- 親 trace E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012 を説明できる。
- validation report が pass / fail / blocked / stale を区別する。
- 正本上書きがない。
- fresh reviewer gate result と closure evidence が report に残る。

## レビュアー引き渡しメモ

- この Issue は `standard` 推奨だが、最終グレードは local assurance が決める。
- ChatGPT 出力は採用候補であり、正本ではない。
- 実装前に、Issue-local draft artifacts は採用済み証跡として確認し、追加変更が必要な場合は Closure Delta と fresh reviewer evidence を残す。
