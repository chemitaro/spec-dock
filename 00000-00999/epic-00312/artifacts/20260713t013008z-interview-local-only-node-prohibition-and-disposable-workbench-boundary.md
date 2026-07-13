---
種別: interview
ID: "20260713t013008z-interview"
タイトル: "Local-Only Node Prohibition And Disposable Workbench Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: ["init-local-00003"]
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T01:30:08Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/initiative/requirement.md"
  - "spec-dock/active/initiative/design.md"
  - "artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md"
reflected_to:
  - "requirement.md#目的Initiative-との紐づき"
  - "report.md#証跡採用台帳Evidence-Adoption-Ledger--必須"
---

# Local-Only Node Prohibition And Disposable Workbench Boundary

## 正式質問として扱う理由
- 親 Initiative の非交渉制約 `local-only は完全廃止する` と、Epic 00312 の Git-ignored local Workbench の整合は、Epic の親 trace と実施可否を左右する。
- ChatGPT 5.6 Pro と fresh `spec-reviewer` の双方が、人間による明示 disposition なしでは phase promotion できない blocker と判定した。

## 質問
- 親 Initiative の `local-only は完全廃止する` は、local-only node / identity / canonical state の廃止を意味し、非正本・非永続・消失可能な `.workbench/` は禁止対象外と明確化してよいか。

## source-grounded context
- `spec-dock/active/initiative/requirement.md` は `local-only は完全廃止する` と定めるが、対象語を node に限定する説明はない。
- Epic 00312 の clarification は Workbench を Git-ignored、local-only、disposable、non-canonical とし、durable evidence / accepted authority に使用しないと定める。
- 設計上は authority/state と scratch file の責務が異なるが、親制約の意味は product owner の判断が必要だった。

## ユーザー回答
- 回答:
  - `local-only は完全廃止する` の対象は local-only な Initiative / Epic / Issue、すなわち SpecDock node である。
  - Workbench は一時ファイルであり、永続化するものでも永続的な製品でもない。
- 回答日時: `2026-07-13`

## 採用判断
- adoption_status: `adopted`
- adoption target:
  - `requirement.md`
  - `report.md` Evidence Adoption Ledger
- 理由:
  - 親 Initiative が廃止する local-only authority と、Epic が提供する disposable scratch の責務境界が product owner により明確化された。

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - Workbench は node、identity、canonical state、durable evidence、永続製品ではないことを明記する。
- `design.md`:
  - Workbench の存在や内容から node lifecycle/state を生成しない。
- `plan.md`:
  - scanner isolation と authority boundary の検証を実装 Issue に含める。
- `ADR`:
  - 新しい永続 authority を導入しないため不要。
- 追加確認:
  - この論点については不要。special filesystem entry の意味は別の one-question interview とする。
