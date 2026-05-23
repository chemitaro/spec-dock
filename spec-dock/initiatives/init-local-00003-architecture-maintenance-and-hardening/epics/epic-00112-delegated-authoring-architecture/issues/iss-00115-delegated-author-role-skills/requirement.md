---
種別: 要件定義書（Issue）
ID: "iss-00115"
タイトル: "Delegated Author Role Skills"
関連GitHub: ["#115"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# iss-00115 Delegated Author Role Skills — 要件定義（WHAT / WHY）

## 目的
- spec-dock-system-architect と spec-dock-implementation-planner の provider-first role skills を追加する。
- 親 Epic の `E-RQ-004, E-RQ-005` / `E-AC-004/E-AC-005 role-contract baseline` を、この Issue の変更範囲で閉じられる状態にする。

## 背景・現状
- 現状の挙動:
  - Epic `epic-00112` は delegated authoring を draft-only evidence として導入する方針を固定した。
  - この Issue の対象領域 `Role skills` は、まだ shipped provider assets と dogfooding consumer workspace に実装されていない。
- 現状の課題:
  - 対象 contract が未実装のままだと、後続 Issue が reviewer pass / evidence / parity を安全に前提化できない。
- 観測点:
  - docs: 対象 provider / dogfooding docs に contract が存在する。
  - tests: 必要に応じて managed asset / init-update / content assertion が更新される。
  - spec-dock: `validate` / `sync` が成功する。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`

## スコープ
- 必須:
  - 対象成果物: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md; src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md; .agents/skills mirrors; tests/test_init_update.py as needed`
  - Provider-side source of truth を先に更新し、dogfooding workspace の parity を確認する。
  - `report.md` に変更対象、検証、reviewer 結果を記録できる状態にする。
- 禁止:
  - 初期 Epic の非スコープである write-capable delegation、runtime validation、role registry、`.github/agents` / Copilot support を実装しない。
  - delegated draft を fresh `spec-reviewer` pass の代替として扱わない。
- 対象外:
  - Issue scope を超える実装コード変更。
  - GitHub issue close/update automation。

## 境界
- 常に行う:
  - 親 Epic の ownership / draft-only / provider-first contract に従う。
  - 変更した provider asset と dogfooding mirror の関係を確認する。
- 判断が必要:
  - 既存 tests に content assertion を追加するか、manual parity evidence に留めるか。
- 行わない:
  - 親 Epic の scope / non-scope を再定義しない。

## 非交渉制約
- Manual authoring path を壊さない。
- Fresh `spec-reviewer` gate を維持する。
- Provider source と dogfooding consumer を混同しない。

## 前提
- Depends on: iss-00113, iss-00114
- 親 Epic requirement/design/plan は fresh `spec-reviewer` pass 済み。

## 受け入れ条件
- AC-001:
  - アクター: maintainer / orchestrator
  - 前提: この Issue の依存 Issue が完了または reviewer-approved no-op である。
  - 操作: 対象成果物を確認する。
  - 期待結果: `spec-dock-system-architect と spec-dock-implementation-planner の provider-first role skills を追加する。` が provider-side source of truth に反映される。
  - 観測点: git diff、対象ファイル、report evidence。
- AC-002:
  - アクター: maintainer / test runner
  - 前提: 対象成果物が更新済み。
  - 操作: `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する。
  - 期待結果: 成功し、必要な parity evidence が残る。
  - 観測点: command output、report evidence。
- AC-003:
  - アクター: `spec-reviewer`
  - 前提: requirement/design/plan/report と差分が揃っている。
  - 操作: Issue final spec review を行う。
  - 期待結果: 親 Epic の該当 E-RQ/E-AC と矛盾せず `review_status: pass`。
  - 観測点: reviewer result。

## 例外・エッジケース
- EC-001:
  - 条件: 対象 host / asset path が実装時に確認できない。
  - 期待: verified implementation と偽らず、documented uncertainty / approved no-op / follow-up のいずれかで閉じる。
  - 観測点: report evidence。
- EC-002:
  - 条件: dogfooding mirror が provider source と異なる。
  - 期待: 意図した差分か drift かを report に記録し、必要なら修正する。
  - 観測点: diff evidence。

## 用語（ドメイン語彙）
- TERM-001: delegated draft evidence
  - delegated author が返す draft-only artifact。canonical authority ではない。
- TERM-002: provider-first
  - shipped source を `src/spec_dock/assets/...` で変更し、consumer workspace で検証する方針。

## 未確定事項
- なし。


## Parent Epic Role Contract Details
- `spec-dock-system-architect` required output sections:
  - Requirement Coverage
  - Existing Context Findings
  - Design Decisions
  - Alternatives Considered
  - Boundary / Contract Model
  - Dependency Analysis
  - Source of Record
  - Data Flow / Domain Model / Interface Contract
  - File / Module Change Plan
  - Migration / Compatibility / Rollback
  - Observability
  - Test Strategy
  - ADR Candidates
  - Risks
  - Requirement Clarification Requests
  - Integration Notes for Main Orchestrator
- `spec-dock-implementation-planner` required output sections:
  - Plan Summary
  - Requirement / Design Traceability
  - Milestones
  - Dependency-Derived Execution Order
  - Issue / Step Slicing
  - Test Strategy Mapping
  - Review Gates
  - Rollback / Compatibility
  - Docs Impact
  - Final Quality Gate
  - Plan Blockers
  - Integration Notes for Main Orchestrator
- Required blocker behavior:
  - `system-architect` returns Requirement Clarification Request for requirement gaps.
  - `implementation-planner` returns Plan Blocked for design gaps.
- Forbidden actions for both roles:
  - edit canonical artifacts directly
  - edit implementation code
  - close/update GitHub issues
  - run destructive commands
  - promote phases
  - claim spec-reviewer pass
  - ask the user directly for clarification instead of returning a blocker to the orchestrator
