---
kind: disc
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T07:03:22Z
created_by: orchestrator
status: proposed
authority: proposed
adoption_status: adopted
derived_from:
  - requirement.md
  - design.md
  - plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan_issue.md
  - .agents/skills/spec-dock-issue-execution/SKILL.md
  - .agents/skills/spec-driven-tdd-workflow/SKILL.md
reflected_to:
  - requirement.md
  - design.md
  - plan.md
  - report.md
---

# issue planning / execution split deep consultant analysis

## 位置づけ

この文書は、`spec-dock-issue-execution` が Issue の仕様作成フェーズと実装フェーズの両方を入口として持っているように見える問題について、deep consultant の分析を issue-local evidence として整理した記録である。

実装はまだ行わない。この文書は requirement / design / plan を再更新するための synthesis / proposal である。

## 結論

`spec-dock-issue-planning` と `spec-dock-issue-execution` は分けるべきである。

今回 issue に含める粒度は、次に限定するのが妥当である。

- skill interface の分離
- workflow authority の分離
- tests
- dogfooding mirror

今回 issue では、runtime CLI command の新設、lifecycle state machine の大改造、既存 artifact の自動 migration、PR / finish lifecycle の再設計までは含めない。

## 現状調査

文書レベルでは、authoring と execution は既に一部分離されている。

- `workflow_spec_authoring.md` は、`requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` を定義している。
- `authoring/issue-plan.md` は、Issue plan の field semantics / executable step schema を扱い、lifecycle / execution / completion policy を `workflow_issue.md` へ送っている。
- `phase_plan_issue.md` も、Issue plan の作成哲学と review checklist を扱い、execution policy は `workflow_issue.md` に分離している。

一方で、user-facing / agent-facing interface では混線している。

- `spec-driven-tdd-workflow` は Issue planning 用の leaf skill を持たず、Issue 作業を `spec-dock-issue-execution` へ流しやすい。
- `workflow_issue.md` は、仕様 authoring、execution contract、PR delivery、merge preparation、`issue finish` を同じ文書内に持つ。
- `spec-dock-issue-execution` は execution reminder としては妥当だが、唯一の Issue leaf skill であるため、Issue planning の入口として誤用されやすい。

## 問題分析

### premature implementation

`workflow_issue.md` が `issue start`、plan execution、PR delivery、merge-prepared、`issue finish` まで同じ文書に持つため、要件 / 設計 / 計画の review pass 前に実装へ進む誤読が起きやすい。

今回の会話でも、仕様作成と実装計画を同時に進めかけたため、ユーザーから workflow の順序を明示的に修正された。

### review gate bypass

grill 型 workflow で質問回答や discussion evidence が積み上がると、それ自体を reviewer pass の代替のように扱う危険がある。

しかし spec-dock の authority は、discussion evidence ではなく、canonical docs と fresh `spec-reviewer` pass にある。

### context bloat

planning 中に PR delivery、merge preparation、commit gate、final QA / code / spec review まで読むと、grill 型の「一問ずつ曖昧さを潰す」集中が落ちる。

planning skill は authoring gate と question / research / synthesis に集中し、execution skill は approved plan の実行と delivery に集中する方がよい。

### specialist boundary の誤解

`spec-dock-system-architect` / `spec-dock-implementation-planner` は canonical editor ではなく、discussion draft / analysis producer である。

Issue planning skill がない場合、これらの specialist が canonical docs を直接完成させる skill と誤解されやすい。

## 理想状態

### `spec-dock-issue-planning`

責務:

- Issue の `requirement.md` / `design.md` / `plan.md` 作成・更新を扱う。
- grill 型 clarification、正式 `interview.md`、`research.md`、`disc.md`、Evidence Adoption Ledger、Spec Authoring Gate を使う。
- 各 phase で fresh `spec-reviewer pass` を必須にする。
- `system-architect` / `implementation-planner` を draft evidence producer として使える。
- canonical 反映、user dialogue、phase promotion は orchestrator が所有する。

禁止:

- 実装 edits。
- PR 作成。
- merge-prepared claim。
- `issue finish`。
- reviewer pass 前の implementation readiness claim。

### `spec-dock-issue-execution`

責務:

- reviewer-pass 済み `requirement.md` / `design.md` / `plan.md` と、`report.md` の Spec Authoring Gate evidence を前提にする。
- `plan.md` を executable command queue として実行する。
- Red / Green / Refactor evidence、worker evidence、reviewer gate、commit / no-op evidence を `report.md` に残す。
- PR delivery、merge preparation、`issue finish` へ進む。

停止条件:

- requirement / design / plan の不足。
- stale / failed / missing reviewer pass。
- grill discussion evidence だけで canonical authority が成立しているように見える場合。
- 実装中に新しい仕様判断が見つかり、plan amendment / re-review が必要な場合。

## workflow docs の望ましい分離

- `workflow_spec_authoring.md`
  - Initiative / Epic / Issue 共通の phase promotion gate。
- `workflow_issue_planning.md`
  - Issue 固有の planning / grill / canonical docs authoring。
- `authoring/issue-plan.md`
  - Issue plan の field semantics。
- `phase_plan_issue.md`
  - Issue plan の作成哲学・review checklist。
- `workflow_issue_execution.md`
  - approved plan execution、report evidence、review loop、PR、finish。
- `workflow_issue.md`
  - 互換用 umbrella。planning / execution への routing と lifecycle command の概要だけを置く。

## 要件への追加提案

### 必須

- Issue の planning interface と execution interface を分離する。
- `spec-dock-issue-planning` は、Issue の requirement / design / plan authoring と fresh reviewer pass までを扱う。
- `spec-dock-issue-execution` は、approved plan の実装、検証、PR delivery、merge preparation、issue finish を扱う。
- execution 中に requirement / design / plan の不足が見つかった場合、実装を続行せず planning phase に戻す。

### 禁止

- `spec-dock-issue-execution` を requirement / design / plan authoring の入口として使うこと。
- grill discussion evidence を `spec-reviewer pass` の代替として扱うこと。
- planning skill が実装、PR 作成、merge-prepared、issue finish を claim すること。

### 対象外

- runtime CLI command の分割。
- lifecycle state machine の大改造。
- 既存 artifact の自動 migration。
- PR / finish lifecycle の再設計。

## 設計への追加提案

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` を追加する。
- dogfooding mirror として `.agents/skills/spec-dock-issue-planning/SKILL.md` を同期対象にする。
- `spec-driven-tdd-workflow` に `spec-dock-issue-planning` route を追加する。
- `spec-dock-issue-execution` は execution-only と明記し、planning request は `spec-dock-issue-planning` へ route する。
- `workflow_issue.md` を umbrella 化し、planning / execution の境界を先頭で明記する。
- 可能なら provider-side docs に `workflow_issue_planning.md` / `workflow_issue_execution.md` を追加する。
- `system-architect` / `implementation-planner` は issue planning の補助に使えるが、canonical edit / phase promotion / implementation readiness claim は不可と明記する。

## 実装計画への追加提案

- S04 を分割または増強する。
  - S04a: issue planning skill / routing / workflow authority split
  - S04b: existing grill docs / templates / report adoption guidance
- S05 に tests を追加する。
  - 新 skill が install / update で配布される。
  - hub skill が issue planning と issue execution を別 route として含む。
  - execution skill が planning authoring を入口にしない。
- S06 に dogfooding mirror を追加する。
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `spec-dock/docs/workflow_issue_planning.md`
  - `spec-dock/docs/workflow_issue_execution.md`
  - umbrella 化した `spec-dock/docs/workflow_issue.md`

## tradeoff と対策

### tradeoff

- skill 数が増える。
- `implementation-planner` と `issue-planning` の名前が紛らわしい。
- docs split により参照更新漏れが起きる。
- 既存 agent が `spec-dock-issue-execution` を Issue 作業全般の入口として覚えている可能性がある。

### 対策

- skill は短くし、正本を docs に置く。
- `implementation-planner` は delegated draft producer、`issue-planning` は orchestrator-facing canonical authoring workflow と明記する。
- `workflow_issue.md` は互換用 umbrella として残し、旧参照を壊さない。
- execution skill に「planning request は `spec-dock-issue-planning` へ route」と明記する。

## 採用判断案

採用を推奨する。

ただし今回 issue に含めるのは、interface split、docs authority split、tests、dogfooding mirror までに限定する。

runtime command 追加、lifecycle state machine 変更、既存 artifact migration、PR / finish lifecycle 再設計は今回の scope 外とする。
