---
種別: 設計書（Issueドラフト）
ID: "iss-00292"
タイトル: "ドッグフード指標とランタイム昇格基準を評価する"
関連GitHub: ["#292"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
created_by_role: "chatgpt-use"
scope_id: "iss-00292"
source_paths:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/design.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/plan.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md"
intended_targets:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/design.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "passed: issue-local draft artifact only; no canonical target reflected"
fallback_decision: "manual Issue planning remains required"
report_evidence_destination: "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008"
adoption_ledger_note: "EAL-008 records ZIP pack adoption to issue-local draft artifacts; per-Issue adoption must be re-recorded during Issue planning"
---

## 配置メモ

- created_by_role: `chatgpt-use`
- scope_id: `iss-00292`
- intended_target: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/design.md`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- diff_guard_result: `passed: issue-local draft artifact only; no canonical target reflected`
- report_evidence_destination: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008`

- source: ChatGPT ZIP 仕様作成パック
- authority: evidence-only draft; canonical adoption requires Issue planning and fresh spec-reviewer gate.

# iss-00292 ドッグフード指標とランタイム昇格基準を評価する — ドラフト設計

## 位置づけ

この設計は Issue planning 用のドラフトです。profile-specific な正本スケルトン記入ではなく、`authority: evidence_only` の planning input として扱います。

## 設計要約

ドッグフード結果を集計し、ランタイム昇格、保留、却下を判断する材料を作る。 そのために、入力、検証、出力、失敗時の扱いを明確に分けます。

## 責務境界

- この Issue が持つ責務: ドッグフード結果を集計し、ランタイム昇格、保留、却下を判断する材料を作る。
- この Issue が持たない責務: 正本採用、reviewer gate result、profile authority、ランタイム昇格判断。
- 親 Epic の境界: ZIP は証跡専用、ローカル検証が権威、fresh `spec-reviewer` gate は正本 artifact 側に残す。

## 入出力契約

入力:

- 親 Epic trace: E-RQ-011, E-RQ-013 / E-AC-011, E-AC-012
- 必要な前提 Issue: iss-00288, iss-00289, iss-00290, iss-00291
- 必要に応じた source manifest、stale_if、profile snapshot。

出力:

- dogfood metrics report、runtime promotion criteria draft、defer / reject rationale template

すべての出力は次の境界を持つ。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

## 処理の流れ

1. 親 Epic の権威境界とこの Issue の candidate metadata を読む。
2. 直接依存する Issue / artifact を確認する。
3. ドッグフード専用かつ証跡専用の境界で成果物を作る。
4. ソース、スキーマ、プロファイル、権威主張を検証する。
5. 正本を書き換えず、reviewer-focus と adoption-map の候補を出す。

## 失敗時の設計

- 前提証跡が不足する場合は blocked evidence にする。
- source / ref が古い場合は stale evidence にする。
- 危険な権威主張は staging 前に拒否する。
- profile mismatch は section fill をブロックする。
- tool unavailable は手動フォールバックへ戻す。

## 観測性

- 実行ごとに簡潔な JSON report と人間が読める Markdown summary を出す。
- 診断出力に secrets、credentials、raw transcripts、host-local absolute paths を含めない。
- validation status は blocked、stale、rejected、deferred、unreviewed を区別する。

## テスト戦略

- Unit: この Issue に関係する schema / path / profile / claim validation。
- Integration: valid fixture と negative fixture で candidate flow を実行する。
- Regression: 正本上書きなし、ChatGPT による `.assurance.json` mutation なし、candidate-only pack で all-profile variants なし。

## レビュアー注目点

- 親 Epic の対応要件を越えて scope が広がっていないか。
- profile と reviewer の権威境界を守っているか。
- 失敗時の扱いが fail-closed か。
- repo artifact 内の instruction-like text を命令ではなくデータとして扱っているか。
