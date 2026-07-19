---
種別: research
ID: "20260719t135413z-07-research"
タイトル: "Source Branch Baselineと完全置換整合性"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "application safety evidence"
derived_from:
  - "GitHub branch codex/init-00322-chatgpt56-planning-pack-adoption"
reflected_to:
  - "FILE-OPERATIONS.md"
  - "CODEX-APPLY-PROMPT.md"
---

# Source Branch Baselineと完全置換整合性

## Target

```text
Repository: chemitaro/spec-dock
Branch: codex/init-00322-chatgpt56-planning-pack-adoption
Initiative: init-00322
Path: spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture
```

## Observed baseline blobs

```text
requirement.md: d32ff622b18fb6c2aa089dbeef7817248e4cda8e
design.md:      e4020dd7793a07eead7ab10f658df3d5c449ab78
plan.md:        0cba18cda20f70000140bb5c0fe956d786894eba
report.md:      6d9ae97d09b62c96d005fb44cf897cc225cae530
```

## Integrity rule

本パッケージの三文書は、baseline文書とArchitecture-Aware Execution Brief要件を統合した完全な置換物である。差分説明、旧文書を併存させる前提、旧設計を別途参照しないと成立しない本文を含めない。

Codexは適用前に現在blobを確認する。baselineと異なる場合は、別変更が入った可能性があるため上書きせず停止する。

## Merge coverage

完全置換文書は、baselineの次を保持・統合する。

- Initiative identity、Goal、Why now、Human Gate。
- Actor responsibility、Git ownership、Oracle／GitHub binding。
- Integrated Planning、Review Protocol、Repair Batch、Executor、Delivery Topology、Cutover。
- 7 Epicの責任境界と依存DAG。
- 既存REQ-001〜REQ-019、NFR-001〜006、AC-001〜AC-018、M-001〜M-008、R-001〜R-009。

加えて、Architecture-Aware Execution Briefについて、REQ-020〜REQ-025、NFR-007、AC-019〜AC-025、M-009〜M-013、R-010〜R-015を統合する。
