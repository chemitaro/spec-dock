---
種別: 実装計画書（Issueドラフト）
ID: "iss-00289"
タイトル: "既存 Issue の選択済みプロファイル向けパックをドッグフードする"
関連GitHub: ["#289"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
created_by_role: "chatgpt-use"
scope_id: "iss-00289"
source_paths:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/design.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/plan.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md"
intended_targets:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack/plan.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "passed: issue-local draft artifact only; no canonical target reflected"
fallback_decision: "manual Issue planning remains required"
report_evidence_destination: "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008"
adoption_ledger_note: "EAL-008 records ZIP pack adoption to issue-local draft artifacts; per-Issue adoption must be re-recorded during Issue planning"
---

## 配置メモ

- created_by_role: `chatgpt-use`
- scope_id: `iss-00289`
- intended_target: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack/plan.md`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- diff_guard_result: `passed: issue-local draft artifact only; no canonical target reflected`
- report_evidence_destination: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008`

- source: ChatGPT ZIP 仕様作成パック
- authority: evidence-only draft; canonical adoption requires Issue planning and fresh spec-reviewer gate.

# iss-00289 既存 Issue の選択済みプロファイル向けパックをドッグフードする — ドラフト実装計画

## 位置づけ

この計画は Issue planning 用のドラフトです。正本の実装計画として採用するには、個別 Issue planning と fresh `spec-reviewer` gate が必要です。

## 実装ステップ

1. 親 Epic の `requirement.md` / `design.md` / `plan.md` と、この Issue の要件定義ドラフトを読む。
2. 依存関係を確認する: iss-00286, iss-00287。
3. レビュー済み Issue 要件から、local assurance が作った選択済みスケルトンだけを ChatGPT に埋めさせる流れを検証する。
4. 成果物を selected-profile ZIP fixture、profile validation report、段階的採用 dry run として作る。
5. 正本ファイルを直接変更せず、検証 report と staged artifact を出す。
6. Evidence Adoption Ledger へ採用候補を引き渡せる形に整える。

## 検証計画

- 正常系 fixture で expected output が作られることを確認する。
- negative fixture で危険な claim、stale source、profile mismatch をブロックする。
- `git status` または差分確認で正本直接上書きがないことを確認する。
- `.assurance.json` が ChatGPT 出力によって変更されていないことを確認する。

## リスク

- Issue の設計・計画を ChatGPT が正本として完了したように見せるリスクを遮断する。
- ChatGPT 出力を正本完了や reviewer pass と誤認するリスク。
- ドッグフード専用の提案が配布ランタイム契約のように読まれるリスク。

## 完了条件

- selected-profile ZIP fixture、profile validation report、段階的採用 dry run が存在する。
- 親 trace E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011 を説明できる。
- validation report が pass / fail / blocked / stale を区別する。
- 正本上書きがない。
- fresh reviewer gate が別途必要であることが report に残る。

## リレー実行 / PR 方針

- このドラフト計画単独では Pull Request を作成しない。
- 実装と検証が完了したら、この Issue の `report.md` に完了証跡を記録し、`./spec-dock/scripts/spec-dock issue finish` を実行する。
- その後、次 Issue `iss-00290` を `./spec-dock/scripts/spec-dock issue start iss-00290` で開始する。
- PR 作成、CI / review 修正、mergeable 確認は最後の `iss-00293` に集約する。

## レビュアー引き渡しメモ

- この Issue は `strict` 推奨だが、最終グレードは local assurance が決める。
- ChatGPT 出力は採用候補であり、正本ではない。
- 実装前に、このドラフトを Issue canonical `design.md` / `plan.md` へ採用するかを判断する。
