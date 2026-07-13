---
種別: interview
ID: "20260713t031557z-interview"
タイトル: "ChatGPT Output Prefix Coexistence Without Reservation"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: ["epic-00259"]
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T03:15:57Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260713t023439z-decision-candidate-chatgpt-output-artifact-import-contract.md"
  - "artifacts/20260713t031057z-research-chatgpt-5-6-pro-artifact-import-integration-analysis.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
  - "artifacts/20260713t031808z-adr-template-free-artifact-import-and-blank-filename-coexistence.md"
---

# ChatGPT Output Prefix Coexistence Without Reservation

## 質問
- `chatgpt-output` をtyped Artifact tokenとして追加すると従来blank slug `chatgpt-output-*` とfilename grammarが重なるため、blank側で予約prefixとして禁止してよいか。

## ユーザー回答
- 回答:
  - 予約する必要はない。
  - `artifact import`でChatGPT outputを作成できることと、blank Artifactのfilename/slugとしてChatGPT outputを使うことは両方存在してよい。
  - Blank Artifact側で`chatgpt-output-*`を禁止する必要はない。
- 回答日時: `2026-07-13`

## 採用含意
- New blank-prefix reservationは導入しない。
- Existing blank Artifact input compatibilityを維持する。
- Filenameだけをimport provenance、authority、creation routeの一意な識別子として扱わない。
- Imported outputのsource path/hash/capture boundary/adoption statusはcommand resultとEALで管理し、本文へfrontmatter/sidecarを追加しない。
- Typed recognitionとblank grammarが衝突する場合、parser/catalogを複雑化してcreation originを推測せず、import commandのeligibilityとdestination namingを分離する案を優先して再設計する。

## Adoption status
- 現時点: `unreviewed`
- 次アクション:
  - GPT-5.6 Pro follow-upで既存Artifact ADR/parser/validatorとの最小整合案を比較する。
  - EAL disposition後、requirement→design→planの順でcanonical refreshする。
