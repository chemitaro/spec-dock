---
種別: 要件定義書（Issueドラフト）
ID: "iss-00286"
タイトル: "仕様作成パックの差分表示と段階配置を実装する"
関連GitHub: ["#286"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
created_by_role: "chatgpt-use"
scope_id: "iss-00286"
source_paths:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/design.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/plan.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md"
intended_targets:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering/requirement.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "passed: issue-local draft artifact only; no canonical target reflected"
fallback_decision: "manual Issue planning remains required"
report_evidence_destination: "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008"
adoption_ledger_note: "EAL-008 records ZIP pack adoption to issue-local draft artifacts; per-Issue adoption must be re-recorded during Issue planning"
---

## 配置メモ

- created_by_role: `chatgpt-use`
- scope_id: `iss-00286`
- intended_target: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering/requirement.md`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- diff_guard_result: `passed: issue-local draft artifact only; no canonical target reflected`
- report_evidence_destination: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md#EAL-008`

- source: ChatGPT ZIP 仕様作成パック
- authority: evidence-only draft; canonical adoption requires Issue planning and fresh spec-reviewer gate.

# iss-00286 仕様作成パックの差分表示と段階配置を実装する — ドラフト

## 位置づけ

この文書は `epic-00283` から切り出した Issue の要件定義ドラフトです。fresh `spec-reviewer` 前の planning input であり、`authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` の範囲で扱います。

## 目的

valid ZIP を正本へ直接書かず、ドライラン差分とサニタイズ済み段階配置 artifact に変換する。

## 親 Epic への対応

- 対応要件: E-RQ-006, E-RQ-007
- 対応受け入れ条件: E-AC-008, E-AC-009
- 推奨グレード: `strict`
- 実施単位: T2 差分 / 段階配置

## 範囲

- valid ZIP を正本へ直接書かず、ドライラン差分とサニタイズ済み段階配置 artifact に変換する。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: ドライラン差分レポート、段階配置 renderer、adoption-map 引き渡し確認。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- iss-00285

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

ZIP 内容が正本ファイルを直接上書きするリスクを遮断する。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義ドラフトを確認する。
- 期待結果: E-RQ-006, E-RQ-007 / E-AC-008, E-AC-009 へ trace できる。
- 観測点: candidate metadata、Epic report の採用台帳。

### AC-002: 権威境界が明示される

- 前提: ChatGPT ZIP 由来のドラフトを読む。
- 操作: scope、non-scope、profile fields を確認する。
- 期待結果: `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` が保たれる。
- 観測点: Markdown frontmatter、`profile.json`、検証 report。

### AC-003: ローカル検証が必須条件として残る

- 前提: candidate output が有用そうに見える。
- 操作: local validation と fresh reviewer gate の必要性を確認する。
- 期待結果: local validation / canonical rewrite / reviewer gate なしに downstream work を開始可能とは扱わない。
- 観測点: report evidence gate proposal。

### AC-004: 成果物を独立にレビューできる

- 前提: candidate deliverable が作られた。
- 操作: reviewer-focus と validation report を読む。
- 期待結果: reviewer が local adoption 可否を判断する観測点を持つ。
- 観測点: candidate report evidence。

### AC-005: 正本を直接上書きしない

- 前提: この Issue の成果物または fixture が存在する。
- 操作: valid ZIP fixture を stage する。
- 期待結果: canonical `requirement.md` / `design.md` / `plan.md` は直接変更されず、dry-run diff と staged artifact だけが出る。
- 観測点: validation report、staged artifact、または Issue report。

### AC-006: adoption-map を EAL 候補へ変換できる

- 前提: この Issue の成果物または fixture が存在する。
- 操作: adoption-map を含む fixture を処理する。
- 期待結果: claim ごとの adopted / rejected / stale / blocked 候補を report へ引き渡せる。
- 観測点: validation report、staged artifact、または Issue report。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
