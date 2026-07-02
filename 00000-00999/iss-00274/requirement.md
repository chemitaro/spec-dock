---
種別: 要件定義書（Issue）
ID: "iss-00274"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow"
関連GitHub: ["#274"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270", "init-local-00003"]
---

# iss-00274 Epic execution handoff と Issue readiness workflow 更新 — Issue 要件定義

## 文書の位置づけ
- この文書は `epic-00270` 配下の正規 Issue 要件定義である。
- Canonical `design.md` と `plan.md` は、Issue Start 後に assurance classify / assurance compose / fresh reviewer gate を通して正規化するまで `awaiting-assurance-compose` placeholder とする。
- Issue Start 前の設計・計画 seed は、Issue-local `draft-design` / `draft-plan` artifact として保持し、canonical authority ではなく handoff evidence として扱う。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00275` へバトンを渡す。

## Pre-start draft handoff
- draft-design artifact: `artifacts/20260702t081006z-draft-design-epic-execution-readiness-workflow-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081007z-draft-plan-epic-execution-readiness-workflow-pre-start-seed.md`
- artifact authority: evidence only
- canonical adoption: `issue start` 後に Issue Planning EAL で adopted / partially_adopted / rejected / stale / blocked を判断する。
- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 目的
Epic execution coordinator が、reviewer-gated Epic planning outputs と downstream Issue handoff package を消費し、Issue start / execution へ進める前に structural readiness を確認できるように、Epic execution skill / workflow guidance を更新する。

## 背景
- Epic planning が改善されても、Epic execution が handoff package を読まずに Issue execution へ進むと、Issue ごとの計画が親境界や evidence flow から外れる。
- ユーザー決定により、handoff inspection は Option B とし、machine-checkable な構造欠落は blocking、意味的品質は reviewer finding として扱う。
- Epic execution は semantic reviewer ではなく coordinator / structural gate である必要がある。

## 親スコープから継承する要件
- `E-RQ-010`: Issue-local draft artifact boundary and grade-aware role policy
- `E-AC-008`: pre-start Issue draft migration readiness
- `E-RQ-006`: Epic-to-Issue slicing and handoff
- `E-RQ-007`: handoff inspection and execution readiness
- `E-RQ-009`: Japanese-first spec and artifact authoring
- `E-AC-004`: Epic execution handoff readiness
- `E-AC-007`: Japanese-first authoring readiness

## 親設計から継承する判断
- `D-005`: flexible six-Issue baseline。
- `D-006`: Option B handoff inspection。
- `D-008`: Japanese-first spec authoring。

## 対象
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
- 必要な `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- 必要な `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 必要な phase / authoring docs
- 振る舞い変更が必要な場合の runtime guidance / tests

## 対象外
- Epic execution を semantic spec reviewer にすること。
- Issue planning、Issue execution、dependency checks、fresh reviewer gates を bypass すること。
- Issueごとの PR 作成を通常フローに入れること。
- GitHub mutation、PR merge、Issue close automation。
- runtime command validation の大規模追加。必要性が出た場合は plan amendment を行う。

## 受け入れ条件
- `I274-AC-001`: Epic execution skill / docs が、Epic requirement / design / plan / report と Issue handoff package を execution input として読むよう誘導する。
- `I274-AC-002`: missing canonical docs、missing / stale reviewer pass、missing Issue readiness contract、missing executable plan structure、missing delegation contract、missing verification、missing reviewer focus、unresolved blocking report entries を structural blocker として扱う。
- `I274-AC-003`: acceptance criteria や test strategy の弱さなど、構造はあるが意味的十分性が疑わしいものは reviewer finding として扱い、coordinator が semantic reviewer を置き換えない。
- `I274-AC-004`: raw artifact を canonical authority と扱う、または decision-only Issue を execution-ready と扱う導線を禁止する。
- `I274-AC-005`: Issueごとの PR 作成を通常フローにせず、final PR delivery は `iss-00276` に集約することを明示する。
- `I274-AC-006`: 日本語運用では、execution / readiness 中に作成・更新する docs / report / artifacts の本文を日本語ファーストにする guidance を含む。
- `I274-AC-007`: `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` を pre-start Issue handoff artifact の統一 primitive として workflow / skills / 必要な runtime behavior に反映する。
- `I274-AC-008`: actor / specialist / depth 別 draft command を導入せず、`assurance compose` は canonical compose 専用として扱う。
- `I274-AC-009`: handoff-ready と execution-ready を分離し、Issue grade 別の specialist obligation を readiness evidence gate に反映する。

## 例外条件 / 失敗条件
- `I274-EC-001`: readiness check が `spec-reviewer` の代替として振る舞ってはならない。
- `I274-EC-002`: structural blocker がある Issue を実行可能として扱ってはならない。
- `I274-EC-003`: reviewer finding をすべて blocking にして、ユーザー認知負荷や無駄な停止を増やしてはならない。
- `I274-EC-004`: PR merge や credentialed GitHub mutation をこの Issue に含めてはならない。

## バトン / 依存
- 前提:
  - `iss-00272` の Epic handoff package。
  - `iss-00273` の scope-layering reference / planning guidance。
- 後続:
  - `iss-00275` は、この Issue の structural blocker / reviewer finding 分離を smoke checks の対象にする。
  - `iss-00276` は、最終実行時にこの readiness workflow を通って全Issue完了を確認する。

## 検証期待
- skill / workflow docs の差分点検。
- 必要な場合の focused runtime / CLI tests。
- Epic execution read-through の manual evidence。
- `./spec-dock/scripts/spec-dock validate`。

## 実行開始時の確認事項
- 前段の reference / template wording を確認する。
- runtime behavior change が本当に必要か、docs / skill guidance で足りるかを最初に判定する。
