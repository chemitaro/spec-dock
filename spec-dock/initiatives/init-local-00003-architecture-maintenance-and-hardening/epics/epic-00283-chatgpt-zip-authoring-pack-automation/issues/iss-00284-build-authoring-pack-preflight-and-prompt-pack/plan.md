---
種別: 実装計画書（Issue）
ID: "iss-00284"
タイトル: "仕様作成パックの事前確認とプロンプトパックを作る"
関連GitHub: ["#284"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00284 仕様作成パックの事前確認とプロンプトパックを作る — 実装計画

## 位置づけ

この `plan.md` は、この Issue の canonical implementation plan です。ChatGPT ZIP 仕様作成パック由来の draft artifact は evidence-only handoff として保持し、main orchestrator が採否判断した内容だけをこの文書に再記述しています。execution-ready と扱うには、この計画への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。ただし、この Issue は branch / ref / source / stale_if を固定する制御プレーン入口であるため、strict 相当の追加 obligation を持ちます。execution-ready と扱うには、manual fallback evidence、failure-mode record、fresh `spec-reviewer` result を `report.md` に残します。

## 実装ステップ

1. 親 Epic の `requirement.md` / `design.md` / `plan.md` と、この Issue の要件定義を読む。
2. 依存関係を確認する: なし。
3. repo / ref / source_paths / stale_if / denylist / profile snapshot を固定し、ChatGPT に渡すプロンプトパックを作る。
4. 成果物を 事前確認 JSON スキーマ案、プロンプトパック案、ソース一覧 fixture、stale_if fixture として作る。
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
| S02 | dev-coder or doc-writer matching touched surface | this Issue `requirement.md`, `design.md`, S01 evidence | `src/spec_dock/**`, `tests/**`, this Issue `artifacts/**`, this Issue `report.md` | unrelated initiatives, unrelated Issue docs, `.assurance.json`, direct canonical overwrite by generated ZIP, PR/CI operations | Issue AC-001〜AC-004 and issue-specific deliverables | focused unit/integration/docs-only check selected before edit; `git diff --check` | implementation scope, no authority-boundary regression | outside allowed paths, public contract expansion not in requirement, unsafe ZIP/adoption claim | changed files, generated/staged artifacts, verification result, residual risks | Issue `report.md` execution evidence / EAL | new public command, new persistence, or scope wider than AC | S02 reviewer-ready before S03 |
| S03 | qa-reviewer or dev-coder | S02 output, fixtures, validation report contract | `tests/**`, this Issue `artifacts/**`, this Issue `report.md`; source fixes only if failing test reveals in-scope defect | unrelated refactor, broad fixture rewrite, `.assurance.json` mutation, self-review pass claim | Issue AC-005〜AC-006 and negative fixtures are covered | normal fixture, negative fixture, `spec-dock validate`, `git diff --check`, focused pytest or documented no-op | fail-closed behavior, validation status taxonomy, no canonical overwrite | missing negative fixture, ambiguous validation status, test requires broader design | test output, blocked/stale/rejected/deferred evidence, defect notes | Issue `report.md` Closure Evidence Ledger | new failure mode not covered by design | S03 closed before S90 |
| S90 | main orchestrator / doc-writer | S01〜S03 evidence, Epic docs, workflow docs if touched | this Issue docs/report, Epic report; `spec-dock/docs/**` only for direct contradiction | broad docs cleanup, template changes unrelated to this Issue, historical ledger deletion | docs impact and adoption ledger are resolved | docs-only inspection; `rg` for direct contradictions; `spec-dock validate` | report consistency, EAL/SID/closure integrity | unresolved contradiction or required docs update | docs impact decision, EAL/SID updates or no-op rationale | Issue `report.md`, Epic `report.md` when needed | docs impact changes canonical workflow | S90 closed before S99 |
| S99 | main orchestrator + fresh reviewers | all closure evidence, final diff, reviewer results | this Issue `report.md`, Epic report for summary; bounded fixes only in previously allowed paths | new behavior implementation, PR creation, unrelated cleanup | all required closure ids pass or approved no-op | `spec-dock validate`, `git diff --check`, focused tests from S02/S03, fresh `spec-reviewer` result | final readiness, P0/P1 blocker absence, residual risk clarity | any P0/P1 finding, stale reviewer, missing closure evidence | final gate result, reviewer status, remaining risks | Issue `report.md` Final Gate / Closure Evidence Ledger | reviewer requires plan/design change | Issue completion-ready only after S99 |

## 具体テストケース一覧

| test id | step | kind | concrete case | expected result | evidence path |
|---|---|---|---|---|---|
| tc-001-a | S01 | inspect | 親 Epic trace、依存 Issue、local assurance を確認する | parent trace / dependency / `authorized_profile` が report に記録される | Issue `report.md` Closure Evidence Ledger |
| tc-002-a | S02 | implementation/docs | Issue 固有成果物を作成し、generated ZIP / staged artifact が正本を直接上書きしないことを確認する | deliverable と no-overwrite evidence が残る | Issue `report.md`; staged artifact path |
| tc-003-a | S03 | normal fixture | 正常系 fixture を実行する、または docs-only Issue では expected artifact inspection を行う | validation status が pass として記録される | validation report / Issue `report.md` |
| tc-003-b | S03 | negative fixture | stale source、profile mismatch、unsafe authority claim、または Issue 固有の拒否条件を検証する | blocked / stale / rejected / deferred のいずれかで fail-closed になる | validation report / Issue `report.md` |
| tc-004-a | S90 | docs impact | docs / report / EAL / SID に直接矛盾がないか確認する | update または approved no-op rationale が記録される | Issue `report.md`; Epic `report.md` when touched |
| tc-005-a | S99 | final gate | `spec-dock validate`、`git diff --check`、focused tests、fresh `spec-reviewer` を確認する | P0/P1 blocker がない、または blocker と次アクションが明確 | Issue `report.md` Final Gate |

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

- branch / ref / source provenance が曖昧なまま ZIP 生成へ進むリスクを遮断する。
- ChatGPT 出力を正本完了や reviewer pass と誤認するリスク。
- ドッグフード専用の提案が配布ランタイム契約のように読まれるリスク。

## 完了条件

- 事前確認 JSON スキーマ案、プロンプトパック案、ソース一覧 fixture、stale_if fixture が存在する。
- 親 trace E-RQ-001, E-RQ-002, E-RQ-003 / E-AC-001 を説明できる。
- validation report が pass / fail / blocked / stale を区別する。
- 正本上書きがない。
- fresh reviewer gate result と closure evidence が report に残る。

## レビュアー引き渡しメモ

- この Issue は `strict` 推奨だが、最終グレードは local assurance が決める。
- ChatGPT 出力は採用候補であり、正本ではない。
- 実装前に、Issue-local draft artifacts は採用済み証跡として確認し、追加変更が必要な場合は Closure Delta と fresh reviewer evidence を残す。
