---
type: research
source: chatgpt-5.5-pro
created_at: 2026-05-23T13:14:06+09:00
epic: epic-00112
topic: integrated best practice for delegated authoring
chatgpt_thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a11a4a5-3ebc-83a5-b653-64cd14e87feb
status: current
---

# ChatGPT 5.5 Pro 統合調査: delegated authoring のベストプラクティス

## 依頼内容

draft canonical authoring、depth=2 specialist delegation、main orchestrator final ownership を組み合わせた場合のベストプラクティスを分析した。

## 回答の要点

採用すべき構成は次の通り。

- `requirement.md`: main orchestrator が責任を持つ。
- `design.md`: `system-architect` が actual artifact の draft を作成・更新する。
- `plan.md`: `implementation-planner` が actual artifact の draft を作成・更新する。
- child specialist: depth=2 で read-only evidence/report producer として使う。
- final review / final promotion: main orchestrator が所有する。

## 推奨 metadata

- `status`
- `governance_owner`
- `draft_author`
- `promotion_authority`
- `source_requirement_revision`
- `source_design_revision`
- `evidence_index`
- `open_questions`

## 推奨 regression tests

- child specialist が `design.md` / `plan.md` を変更しようとすると fail。
- `system-architect` が design を approved に promotion しようとすると fail。
- `implementation-planner` が plan を approved に promotion しようとすると fail。
- draft design に依存した approved plan は fail。
- final review missing は fail。
- non-trivial design で evidence index missing は fail。

## 判断

統合ベストプラクティスとしては、専門 author に draft artifact 作成権限を与える。ただし、承認、promotion、実装開始可否の判断は main orchestrator と workflow gate が保持する。
