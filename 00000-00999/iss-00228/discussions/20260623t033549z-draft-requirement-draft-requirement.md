---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00228"
タイトル: "Compile State Aware Workflow Runbooks And Fixed Skill Kernels"
関連GitHub: ["#228"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00228 Draft Requirement

## 目的
- Agent が状態を推測せず、runtime の `workflow status / next` から current Runbook を取得できるようにする。
- Planning / Execution Skill を fixed kernel 化し、Issue 切替で tracked Skill 差分を発生させない。

## スコープ
- 必須:
  - Workflow State Resolver。
  - Runbook schema / compiler / atomic generated store。
  - no-active / requirement-capture / classification-required state。
  - Markdown / JSON output。
  - fixed planning / execution skill kernel。
  - generated state ignored path。
- 禁止:
  - Profile-aware artifact composition。
  - Step worker routing。
  - PR review。

## Trace
- closes: E-RQ-001, E-RQ-004, E-RQ-005, E-AC-001, E-AC-004, E-AC-005。

## 受け入れ条件
- AC-001: Active Issue なしでは `issue start <target>` または target 入力要求だけを返す。
- AC-002: `lite_candidate` は Runbook obligation を減らさず、`authorized_profile` だけを execution authority とする。
- AC-003: Issue 切替や classification により `.agents/skills/**` に tracked diff が出ない。
- AC-004: Runbook は未選択 Profile の完全手順を含まない。

## 依存
- Upstream: iss-00227。
- Downstream: iss-00229, iss-00233。

## 静的解析前提
- CLI / presentation output code は typed data contract を使い、stringly-typed ad hoc branching を増やさない。
