---
種別: 議論メモ（Issue）
ID: "disc-clarification-workflow-naming"
タイトル: "docs-aware clarification workflow の命名判断"
状態: "resolved"
作成者: "Codex"
最終更新: "2026-05-29"
親: ["iss-00134", "epic-00067", "init-local-00003"]
authority: "synthesized"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "consultant:naming-proposal"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# docs-aware clarification workflow の命名判断

## 位置づけ

この文書は、iss-00134 で追加する workflow / skill の外向き名称を決定した議論メモである。

初期案では Matt Pocock 氏の既存パターンに由来する `grill` を workflow / skill 名へ含めていた。しかし、初見のメンバーやエージェントにとって `grill` は意味が直感的ではなく、詰問や圧迫的な比喩にも読める。そのため、恒久的な spec-dock の概念名としては採用しない。

## 命名候補

| 候補 | 評価 |
|---|---|
| `workflow_clarification.md` / `spec-dock-clarification` | 最推奨。短く、曖昧さ解消、質問、文書化、意思決定の昇華という中核を素直に表す。 |
| `workflow_spec_clarification.md` / `spec-dock-spec-clarification` | spec-dock らしさはあるが、`spec-dock-spec-*` が重複気味でやや重い。 |
| `workflow_docs_clarification.md` / `spec-dock-docs-clarification` | docs-aware 性は伝わるが、文書を読むだけの workflow に狭く見える可能性がある。 |
| `workflow_guided_clarification.md` / `spec-dock-guided-clarification` | 一問一答の導線は伝わるが、docs-aware 性や正規ドキュメントへの昇華が名前だけでは弱い。 |
| `workflow_context_inquiry.md` / `spec-dock-context-inquiry` | 質問ワークフロー感はあるが、仕様を明確化して成果物へ反映する目的が弱い。 |

## 採用判断

採用する名称:

- workflow file: `workflow_clarification.md`
- skill name: `spec-dock-clarification`
- 日本語表示名: `仕様明確化ワークフロー`
- 説明文: `既存ドキュメントとコードを根拠に、曖昧さを一問一答で解消し、合意内容を spec-dock の成果物へ昇華するワークフロー`

判断理由:

- `clarification` は「曖昧さを明確にする」という機能の中心を直接表す。
- issue / epic / initiative、局所論点、要件定義、設計、計画のいずれにも適用でき、範囲が狭すぎない。
- `docs-aware` は workflow 本文と説明文で明示し、ファイル名と skill 名は短く保てる。
- `grill` のような内輪語、比喩、Matt Pocock 文脈への依存を避けられる。
- Issue planning / execution split へ名前が引っ張られず、主目的が clarification workflow であることを保てる。

## 由来の扱い

Matt Pocock 氏の既存パターンは、この issue の着想源として `discussions/` と issue 背景に残す。一方で、恒久的な workflow file、skill name、ユーザー導線、PR title、主要 closure evidence の主語には `grill` を使わない。

設計上の扱い:

- 由来: Matt Pocock 由来の pattern として issue-local evidence に残す。
- 外向き名称: `docs-aware clarification workflow` / `workflow_clarification.md` / `spec-dock-clarification` に統一する。
- 禁止例: `clarification-interview.md` などの専用 template variant と、旧称由来の `grill-*` variant は追加しない。

## 反映方針

- `requirement.md`、`design.md`、`plan.md`、`report.md` の外向き名称を `docs-aware clarification workflow` に統一する。
- planned workflow file は `workflow_clarification.md` とする。
- planned installed skill は `spec-dock-clarification/SKILL.md` とする。
- `grill` は historical discussion path、source snapshot、由来説明以外の恒久導線から外す。
