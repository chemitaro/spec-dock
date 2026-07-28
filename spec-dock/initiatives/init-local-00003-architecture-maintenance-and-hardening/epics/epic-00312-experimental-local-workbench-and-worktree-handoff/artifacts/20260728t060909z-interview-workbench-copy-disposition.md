---
種別: interview
ID: "20260728t060909z-interview"
タイトル: "workbench copyの今後の扱い"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00312"]
関連:
  - "20260728t054338z-research"
  - "20260728t054625z-interview"
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-28T06:09:09Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "2026-07-28 user clarification"
reflected_to:
  - "20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md"
---

# workbench copyの今後の扱い

## 正式質問として扱う理由

現行 Epic の主要成果である `workbench copy` は、今回確定しつつある理想状態では標準workflowに不要となる。

扱いによって次が変わる。

- `requirement.md`: scope/non-scope
- `design.md`: workbench application/infraの存廃
- `plan.md`: remove / deprecate / optional helperへの再配置
- public CLI/docs/tests: compatibility surface

## 質問

現在の `workbench copy` commandを今後どう扱いますか。

### Option A — 今回削除する（Codex推奨）

- public CLI、parser、application、infra、presentation、docs、専用testsを削除する。
- Workbench contentsはbranch/worktree間で受け渡さない。
- 必要なfileはArtifact importで永続化する。
- product versionは現在`0.2.3`で、command自身もexperimentalとして公開されている。

### Option B — deprecatedにして後続releaseで削除する

- commandは一時的に動作させる。
- help/docsでdeprecated warningを表示する。
- removal deadlineを決める。
- backward compatibilityは高いが、不要なimplementationとtestsを一定期間維持する。

### Option C — optional補助機能として残す

- headline workflowからは外す。
- 利用者が明示した場合だけone-shot copyできる。
- Workbench lifecycleには含めない。
- ただし、誤った概念のcommand surfaceと保守負担が残る。

回答では、A / B / C、または修正版を指定してほしい。

## source-grounded context

確認済み:

- current Epic requirement/design/planは`workbench copy`を主要capabilityとしている
- current public guide/referenceにcommandが記載されている
- parser/application/infra/presentationとfocused testsが実装済み
- commandはexperimental/non-canonical/one-shotと明示されている
- package versionは`0.2.3`
- product ownerはWorkbenchを移動・受け渡すものではなく、contentsはworktree終了時に破棄されるものと整理した
- 残す必要があるfileはgeneric Artifact importで保存できるtarget stateになった

local contextで解決できたこと:

- tracked shellによりdirectoryそのものをcopyする必要はない
- contentsはworktree-localでよい
- durable handoffはArtifact importが担う

人間判断が必要な理由:

- experimental commandでも既存利用者がいる可能性はあり、即時削除かcompatibility windowかはproduct policyの判断になる

## Codexの分析

判断軸:

- target stateの単純さ
- backward compatibility
- implementation/test/docs保守負担
- 利用者が誤ったworkflowを選ぶリスク

tradeoff:

- Option Aは最も単純でtarget stateと一致するが、既存callerを直ちに壊す
- Option Bは移行猶予を与えるが、一時的に二つのworkflowが併存する
- Option Cは互換性を維持するが、誤った中心概念が残る

## Codexの推奨案

Option Aを推奨する。

理由:

- commandはexperimentalで、versionも0.xである
- Workbench contents handoffはproduct ownerが不要と明示した
- generic Artifact importが必要なfileの保存経路を提供する
- 不要なcopy semantics、symlink/collision behavior、linked-worktree resolutionを維持しなくてよい

## ユーザー回答

- answer capture:
  - 2026-07-28 chat回答
- 回答:
  - Option Cを採用し、`workbench copy`を補助機能として残す。
  - Workbench contentsはGit管理外なので、linked worktree作成時には新しいworktreeへ移らない。
  - 元のworktreeのWorkbench contentsが必要な場合に限り、手動でtarget worktreeへcopyする必要がある。
  - `workbench copy`はworktree作成時に自動実行しない。
  - 利用者が必要に応じて明示的に実行する。
- 回答日時:
  - 2026-07-28

## 追加確認の要否

- 追加確認が必要か: no
- 次のquestion candidate:
  - none。tracked marker選択はdesignでsource-groundedに決める。

## 採用判断

- adoption_status: adopted
- adoption target:
  - target-state research
  - future `requirement.md`
  - future `design.md`
  - future `plan.md`
  - future `report.md` Evidence Adoption Ledger
- 理由:
  - product ownerがOption Cとmanual-onlyの理由を明示した
- `report.md`反映要否:
  - yes when canonical authoring begins

## requirement / design / plan / ADRへの含意

- `requirement.md`:
  - `workbench copy`をoptional manual helperとして残す
  - worktree create時に自動実行しない
  - sync、watch、copy-backを行わない
- `design.md`:
  - current worktreeをsource、明示target linked worktreeをdestinationとするone-shot copyを維持する
  - tracked shellの存在とGit管理外contentsのcopyを分離する
- `plan.md`:
  - copy implementation/testsは維持する
  - docs上の位置づけをheadline lifecycleからoptional helperへ変更する
- `ADR`:
  - 現時点では不要
- reflected_to:
  - target-state researchへ反映済み
