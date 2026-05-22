---
種別: disc
ID: "20260522t120437z-02-disc"
タイトル: "Epic slicing recommendation for delegated authoring"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-22"
親: ["epic-00112"]
関連: ["GitHub #112"]
authority: "synthesized"
derived_from:
  - "20260522t120437z-research-delegated-authoring-source-architecture-report.md"
  - "20260522t120437z-01-research-consultant-analysis-delegated-authoring-rollout.md"
reflected_to:
  - "epic-00112 requirement/design/plan authoring"
---

# Epic slicing recommendation for delegated authoring

## 目的

`epic-00112-delegated-authoring-architecture` の spec authoring に入る前に、ユーザー提供レポート、consultant 分析、deep-consultant 分析を統合し、初期 Epic の進め方を整理する。

## 合意できる結論

- この変更は **単独 issue ではなく Epic として扱う**。
- 初期導入は **draft-only delegation** に限定する。
- Main orchestrator は canonical artifacts、user dialogue、phase promotion、report evidence を所有し続ける。
- `system-architect` は design draft の一次作成者として扱うが、requirement を変更しない。
- `implementation-planner` は plan draft の一次作成者として扱うが、design decision を追加しない。
- fresh `spec-reviewer` pass は現行通り phase promotion の必須条件にする。
- scoped write-capable delegation、role registry、runtime validation は初期 Epic の必須範囲から外す。

## 推奨 issue 分割

### Issue 1: delegated authoring policy foundation

目的:
- `workflow_spec_authoring.md` に artifact ownership と draft-only authoring delegation の正本契約を追加する。

成果物:
- Orchestrator ownership contract
- Delegated author boundaries
- Requirement Clarification Request / Plan Blocked の扱い
- Consent / forbidden actions / reviewer freshness の基本方針

検証:
- `spec-reviewer` が phase gate と矛盾しないと判断できること。
- `./spec-dock/scripts/spec-dock validate` が通ること。

### Issue 2: role skill assets

目的:
- `spec-dock-system-architect` と `spec-dock-implementation-planner` の shipped role skill を追加する。

成果物:
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
- 必要な managed asset parity tests

検証:
- init / update 後に skill assets が consumer repo へ配布されること。
- provider asset と dogfooding consumer の差分が意図通りであること。

### Issue 3: host callable role integration

目的:
- Codex / Copilot などから named role として呼べる入口を整える。

成果物候補:
- `.codex/agents/system-architect.toml`
- `.codex/agents/implementation-planner.toml`
- 必要なら `.github/agents/*.agent.md`

検証:
- host adapter / agent definition が skill と矛盾しないこと。
- draft-only の hard boundary が host-facing instructions にも残ること。

未決:
- GitHub Copilot agent を初期 Epic に含めるか。

### Issue 4: phase gate and report evidence integration

目的:
- design / plan phase playbook と report evidence に delegated authoring gate を埋め込む。

成果物:
- `phase_design.md` の Delegated Design Authoring Gate
- `phase_plan.md` / `phase_plan_issue.md` の Delegated Plan Authoring Gate
- `report.md` template / evidence contract の Design Authoring Delegation / Plan Authoring Delegation

検証:
- reviewer freshness と report evidence が conflict しないこと。
- delegated draft が reviewer pass の代替ではないことが明示されること。

### Issue 5: dogfooding parity and validation

目的:
- 初期導入後、dogfooding workspace で draft-only delegated authoring を実際に試す。

成果物:
- provider / consumer parity evidence
- `validate` / `sync` evidence
- 小さな authoring task での draft -> integration -> fresh reviewer pass の記録

検証:
- dogfooding workspace で provider source と consumer generated workspace を混同しないこと。
- reviewer pass と report evidence が揃うこと。

## 初期 Epic の非スコープ

- delegated agent による canonical `requirement.md` / `design.md` / `plan.md` の直接編集
- scoped write-capable delegation の正式導入
- role registry の runtime 実装
- path allowlist / write guard の runtime validation
- external publishing や GitHub issue close/update の委任
- 実装コード変更を伴う agent orchestration runtime の大規模変更

## ユーザー確認が必要な点

1. 初期 Epic に `.codex/agents` まで含めるか。
2. 初期 Epic に `.github/agents` まで含めるか。
3. delegated authoring consent を Initiative / Epic / Issue 共通にするか、まず Issue scope 中心にするか。
4. draft output を chat result のみで扱うか、`discussions/` に保存する structured draft artifact を標準にするか。
5. scoped write-capable delegation へ進む判定基準を、dogfooding pass 何件にするか。

## 推奨する次アクション

1. この discussion を Epic requirement の input として扱う。
2. Epic requirement では、初期スコープを draft-only delegated authoring に限定する。
3. Epic design では、provider-first / consumer dogfooding parity、phase gate、report evidence、role skill boundaries を中心に設計する。
4. Epic plan では、上記 5 issue を依存順に並べ、Issue 1 から順に authoring / reviewer pass へ進める。
