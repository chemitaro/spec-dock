---
種別: 実装計画書（Issue）
ID: "<ISS_ID>"
タイトル: "<ISS_TITLE>"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md", "design.md"]
親: ["<EPIC_ID>", "<INIT_ID>"]
---

# <ISS_ID> <ISS_TITLE> — 実装計画（Execution Contract）

> このテンプレートは最小 scaffold です。プロジェクトの目的、作業内容、人間の理解しやすさ、エージェントの実行可能性に合わせて、項目は追加・削除・統合・並べ替えてよい。実行 policy は `workflow_issue.md`、Issue plan の書き方は `phase_plan_issue.md` を正本にする。

## この計画で満たす要件ID
- AC:
  - ...
- EC:
  - ...
- 制約:
  - ...

## マイルストーン一覧
- M1:
  - 対象:
  - exit:
- M2:
  - ...

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `Module Dependency Diagram`
  - `design.md` の `ディレクトリ / ファイル変更計画`
- sequencing rule:
  - upstream / prerequisite / lower-dependency slice から先に step を組む
  - downstream / dependent slice は前提が固まってから置く
- step ordering notes:
  - どの step が何に依存するかを短く書く
- step dependency summary:
  - S01:
    - depends on:
    - unblocks:
    - target files:

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
  - depends on:
  - unblocks:
  - target files:
  - closes:
  - review gate:
- S02:
  - ...

## 要件 ↔ ステップ対応
- AC-001 -> S01
- EC-001 -> S02

## Spec-Locked Closure Index（仕様固定クロージャ索引）

> これは Issue 全体のテストケース一覧ではなく、エージェントが仕様を縮小解釈・後付けテスト・過剰実装しないための coverage ledger です。実際の test contract と close 条件は各 step の `step closure contract` に置く。private method、実装アルゴリズム、mock 構造、assert 細部は原則固定しない。

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | <behavior> | acceptance | AC-001 | ... | ... | spec drift | yes | red-required | report step closure |
| tc-002 | S01 | <behavior> | negative | EC-001 | ... | ... | silent failure | yes | covered-existing | report step closure |

- optional detail columns when needed:
  - fixture notes:
  - golden output:
  - manual verification:
  - property domain:
  - non-goals:
- evidence level values:
  - red-required:
  - covered-existing:
  - inspect-only:
  - manual-required:
- detail policy:
  - 通常 Issue は step / behavior slice ごとに 1〜3 件程度の検証契約を書く。
  - 中央 index は重複するテストケース表にせず、仕様ロック、担当 step、required、evidence level、closure evidence だけを追う。
  - public CLI behavior、shipped scaffold / runtime contract、template / system docs の互換性、installer / update / migration、filesystem / GitHub / active store、negative path、既存 regression、複数 Agent 並列実装の領域では詳細化する。

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing: each implementation step before commit
  - reviewer: code-reviewer
  - pass condition: review_status: pass
  - scope: step diff, tests, docs/report updates, and spec impact for the current step
- QG1 QA review:
  - timing: S99 final quality gate
  - reviewer: qa-reviewer
  - scope: test adequacy and integration test need for the whole issue
- SG1 spec review:
  - timing: S90 docs impact resolution and S99 final quality gate
  - reviewer: spec-reviewer
  - scope: requirement / design / plan / report / docs alignment and requirement fulfillment

## 実行ルール（全ステップ共通）
- 実行 policy、approval cadence、completion contract は `workflow_issue.md` を正本にする。
- step / block / behavior slice の書き方は `phase_plan_issue.md` を正本にする。
- plan 本文には、この Issue 固有の順序、依存、検証、review / QA gate だけを書く。
- 各 implementation step は commit 単位として設計し、`code-reviewer gate` を pass してから `commit gate` で閉じる。
- `approved-no-op` は差分なしの場合だけ許可し、理由、確認対象、差分なし確認コマンドを report に残す。

## 実装ステップ

### S01 — <observable behavior>
- observable behavior:
  - ...
- design refs:
  - ...
- depends on:
  - ...
- unblocks:
  - ...
- target files:
  - ...
- test bundle:
  - closure ids:
    - tc-001
  - test ids:
    - same as closure ids unless a project explicitly documents separate aliases
  - evidence level:
    - red-required / covered-existing / inspect-only / manual-required
  - acceptance:
  - characterization:
  - property / invariant:
  - regression:
  - negative:
- pre-implementation evidence:
  - expected red / characterization pass / test sensitivity evidence:
- report draft update before review:
  - verification / closure / review intent evidence to include in the step diff:
- notes:
  - ...

#### step closure contract
- closure ids:
  - tc-001
- close when:
  - ...
- verification evidence:
  - targeted command / manual evidence / inspection evidence:
- report evidence:
  - Step Contract Closure:
  - Test Contract Closure:
  - Closure Coverage:
- residual risk:
  - ...

#### behavior slice execution
- implementation batch:
  - allowed scope:
  - forbidden scope:
- verification:
  - targeted command:
  - related / full command:
- refactor / tidy:
  - purpose:
  - guardrail:

#### step gate
- delegation decision:
  - delegated / approved-local-execution / degraded mode:
  - required reason / no delegation rationale:
- report draft update:
  - update before code-reviewer so the evidence is reviewed and committed with the step:
- code-reviewer gate:
  - reviewer: code-reviewer
  - review scope:
  - pass condition: review_status: pass
  - re-review rule: fix findings and re-run until pass
- expected verification:
  - ...
- commit gate:
  - closure state: committed / approved-no-op
  - commit scope:
  - commit message intent:
  - post-commit clean check:
- no-op gate:
  - allowed only when:
  - diff check command:
  - checked contracts / files:
  - read-only confirmation evidence:
  - rationale:
- post-commit report evidence:
  - commit hash / final ledger reference:
  - clean check result:

### Sxx — <next observable behavior>
- ...

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / templates / README / workflow / skill / migration notes / none
- 対応:
  - ...
- doc update owner:
  - doc-writer when updates are required
- spec/doc review:
  - reviewer: spec-reviewer
  - pass condition: docs align with requirement / design / plan and no required docs impact remains unresolved

### S99 — final quality gate
- branch diff scope:
  - ...
- required validation:
  - ...
- final QA gate:
  - reviewer: qa-reviewer
  - scope: test adequacy and integration test need for the whole issue
  - pass condition: reviewer pass; add integration tests first if required
  - re-review rule: fix findings and re-run qa-reviewer until pass
- final code review gate:
  - reviewer: code-reviewer
  - scope: issue-wide integrated diff, structure, responsibility boundaries, regression risk, maintainability
  - pass condition: review_status: pass
  - re-review rule: fix findings and re-run code-reviewer until pass
- final spec review gate:
  - reviewer: spec-reviewer
  - scope: requirement / design / plan / report / implementation / tests / docs alignment
  - pass condition: reviewer pass
  - re-review rule: fix findings and re-run spec-reviewer until pass
- final commit gate:
  - commit scope:
  - final report ledger before commit:
  - post-commit external evidence destination:

## 未確定事項
- Q-001:
  - 質問:
  - 選択肢:
    - A:
      - ...
    - B:
      - ...
  - 推奨案:
    - ...
  - 影響範囲:
    - ...

## final exit contract
- AC/EC 達成:
  - ...
- docs impact resolved:
  - ...
- all implementation steps closed:
  - committed / approved-no-op:
- final quality gate passed:
  - qa-reviewer:
  - issue-wide code-reviewer:
  - spec-reviewer:
- final commit completed:
  - ...
- required closure ids closed:
  - Step Contract Closure:
  - Test Contract Closure:
  - Closure Coverage:
- final clean state:
  - no unintended staged / unstaged changes:
