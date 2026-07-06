---
種別: 実装計画書（Issueドラフト）
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
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/plan.md"
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
- intended_target: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/plan.md`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- diff_guard_result: `passed: issue-local draft artifact only; no canonical target reflected`
- report_evidence_destination: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008`

- source: ChatGPT ZIP 仕様作成パック
- authority: evidence-only draft; canonical adoption requires Issue planning and fresh spec-reviewer gate.

# iss-00292 ドッグフード指標とランタイム昇格基準を評価する — ドラフト実装計画

## 位置づけ

この計画は Issue planning 用のドラフトです。正本の実装計画として採用するには、個別 Issue planning と fresh `spec-reviewer` gate が必要です。

## 実装ステップ

1. 親 Epic の `requirement.md` / `design.md` / `plan.md` と、この Issue の要件定義ドラフトを読む。
2. 依存関係を確認する: iss-00288, iss-00289, iss-00290, iss-00291。
3. ドッグフード結果を集計し、ランタイム昇格、保留、却下を判断する材料を作る。
4. 成果物を dogfood metrics report、runtime promotion criteria draft、defer / reject rationale template として作る。
5. 正本ファイルを直接変更せず、検証 report と staged artifact を出す。
6. Evidence Adoption Ledger へ採用候補を引き渡せる形に整える。

## 検証計画

- 正常系 fixture で expected output が作られることを確認する。
- negative fixture で危険な claim、stale source、profile mismatch をブロックする。
- `git status` または差分確認で正本直接上書きがないことを確認する。
- `.assurance.json` が ChatGPT 出力によって変更されていないことを確認する。

## リスク

- 十分な証跡がないまま配布ランタイムへ昇格してしまうリスクを下げる。
- ChatGPT 出力を正本完了や reviewer pass と誤認するリスク。
- ドッグフード専用の提案が配布ランタイム契約のように読まれるリスク。

## 完了条件

- dogfood metrics report、runtime promotion criteria draft、defer / reject rationale template が存在する。
- 親 trace E-RQ-011, E-RQ-013 / E-AC-011, E-AC-012 を説明できる。
- validation report が pass / fail / blocked / stale を区別する。
- 正本上書きがない。
- fresh reviewer gate が別途必要であることが report に残る。

## レビュアー引き渡しメモ

- この Issue は `standard` 推奨だが、最終グレードは local assurance が決める。
- ChatGPT 出力は採用候補であり、正本ではない。
- 実装前に、このドラフトを Issue canonical `design.md` / `plan.md` へ採用するかを判断する。
